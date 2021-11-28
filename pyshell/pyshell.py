# This file is part of pyshell

# pyshell is a Linux subprocess module.
# Copyright (C) 2021 Volitank

# pyshell is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# pyshell is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.tures

# You should have received a copy of the GNU General Public License
# along with pyshell.  If not, see <https://www.gnu.org/licenses/>.

import os
import sys
import builtins
import shutil
from pathlib import Path
from copy import deepcopy
from inspect import getouterframes, currentframe
from subprocess import (
	Popen, CalledProcessError, TimeoutExpired, 
	SubprocessError, CompletedProcess, _USE_POSIX_SPAWN)
from pexpect import spawn

try:
    import msvcrt
    import _winapi
    _mswindows = True
except ModuleNotFoundError:
    _mswindows = False
    import _posixsubprocess
    import select
    import selectors

class pyshellPopen(Popen):
	# we are overriding execute child so we can pass a list into the shell for extglob.
	def _execute_child(self, args, executable, preexec_fn, close_fds,
						pass_fds, cwd, env,
						startupinfo, creationflags, shell,
						p2cread, p2cwrite,
						c2pread, c2pwrite,
						errread, errwrite,
						restore_signals,
						gid, gids, uid, umask,
						start_new_session):
		"""Execute program (POSIX version)"""

		if isinstance(args, (str, bytes)):
			args = [args]
		elif isinstance(args, os.PathLike):
			if shell:
				raise TypeError('path-like args is not allowed when '
								'shell is true')
			args = [args]
		else:
			args = list(args)

		if shell:
			# On Android the default shell is at '/system/bin/sh'.
			unix_shell = ('/system/bin/sh' if
						hasattr(sys, 'getandroidapilevel') else '/bin/sh')
			args = [unix_shell, "-c"] + args

			if executable:
				## Pyshell Patch ##
				# Patching this part of the method so that we will be
				# able to pass more arguments easily such as below
				# shell=['/bin/bash', '-O', 'extglob']
				if isinstance(executable, list):
					del args[0]
					args = executable + args
					executable = args[0]
				else:
					args[0] = executable

		if executable is None:
			executable = args[0]

		sys.audit("subprocess.Popen", executable, args, cwd, env)
		
		if (_USE_POSIX_SPAWN
				and os.path.dirname(executable)
				and preexec_fn is None
				and not close_fds
				and not pass_fds
				and cwd is None
				and (p2cread == -1 or p2cread > 2)
				and (c2pwrite == -1 or c2pwrite > 2)
				and (errwrite == -1 or errwrite > 2)
				and not start_new_session
				and gid is None
				and gids is None
				and uid is None
				and umask < 0):
			self._posix_spawn(args, executable, env, restore_signals,
								p2cread, p2cwrite,
								c2pread, c2pwrite,
								errread, errwrite)
			return

		orig_executable = executable

		# For transferring possible exec failure from child to parent.
		# Data format: "exception name:hex errno:description"
		# Pickle is not used; it is complex and involves memory allocation.
		errpipe_read, errpipe_write = os.pipe()
		# errpipe_write must not be in the standard io 0, 1, or 2 fd range.
		low_fds_to_close = []
		while errpipe_write < 3:
			low_fds_to_close.append(errpipe_write)
			errpipe_write = os.dup(errpipe_write)
		for low_fd in low_fds_to_close:
			os.close(low_fd)
		try:
			try:
				# We must avoid complex work that could involve
				# malloc or free in the child process to avoid
				# potential deadlocks, thus we do all this here.
				# and pass it to fork_exec()

				if env is not None:
					env_list = []
					for k, v in env.items():
						k = os.fsencode(k)
						if b'=' in k:
							raise ValueError("illegal environment variable name")
						env_list.append(k + b'=' + os.fsencode(v))
				else:
					env_list = None  # Use execv instead of execve.
				executable = os.fsencode(executable)
				if os.path.dirname(executable):
					executable_list = (executable,)
				else:
					# This matches the behavior of os._execvpe().
					executable_list = tuple(
						os.path.join(os.fsencode(dir), executable)
						for dir in os.get_exec_path(env))
				fds_to_keep = set(pass_fds)
				fds_to_keep.add(errpipe_write)

				self.pid = _posixsubprocess.fork_exec(
						args, executable_list,
						close_fds, tuple(sorted(map(int, fds_to_keep))),
						cwd, env_list,
						p2cread, p2cwrite, c2pread, c2pwrite,
						errread, errwrite,
						errpipe_read, errpipe_write,
						restore_signals, start_new_session,
						gid, gids, uid, umask,
						preexec_fn)
				self._child_created = True
			finally:
				# be sure the FD is closed no matter what
				os.close(errpipe_write)

			self._close_pipe_fds(p2cread, p2cwrite,
									c2pread, c2pwrite,
									errread, errwrite)

			# Wait for exec to fail or succeed; possibly raising an
			# exception (limited in size)
			errpipe_data = bytearray()
			while True:
				part = os.read(errpipe_read, 50000)
				errpipe_data += part
				if not part or len(errpipe_data) > 50000:
					break
		finally:
			# be sure the FD is closed no matter what
			os.close(errpipe_read)

		if errpipe_data:
			try:
				pid, sts = os.waitpid(self.pid, 0)
				if pid == self.pid:
					self._handle_exitstatus(sts)
				else:
					self.returncode = sys.maxsize
			except ChildProcessError:
				pass

			try:
				exception_name, hex_errno, err_msg = (
						errpipe_data.split(b':', 2))
				# The encoding here should match the encoding
				# written in by the subprocess implementations
				# like _posixsubprocess
				err_msg = err_msg.decode()
			except ValueError:
				exception_name = b'SubprocessError'
				hex_errno = b'0'
				err_msg = 'Bad exception data from child: {!r}'.format(
								bytes(errpipe_data))
			child_exception_type = getattr(
					builtins, exception_name.decode('ascii'),
					SubprocessError)
			if issubclass(child_exception_type, OSError) and hex_errno:
				errno_num = int(hex_errno, 16)
				child_exec_never_called = (err_msg == "noexec")
				if child_exec_never_called:
					err_msg = ""
					# The error must be from chdir(cwd).
					err_filename = cwd
				else:
					err_filename = orig_executable
				if errno_num != 0:
					err_msg = os.strerror(errno_num)
				raise child_exception_type(errno_num, err_msg, err_filename)
			raise child_exception_type(err_msg)

class pyshell(object):

	def __init__(	self,
					input=None, capture_output=False, check=False,
					logfile=None, timeout=None, alias: dict={},
					expect=False, popen=False, **kwargs):
		"""Subprocess as an object, for Linux.

		Initialize with certain options and use them through the life of your object.
		Most of these are exactly the same you're use too with subprocess.run.
		Outlined below are new features

		Arguments:
			logfile: logfile='/tmp/pyshell.log' expects an unopen file. We will open for you.
			aliasing: You can alias commands like so sh = pyshell(alias={'ls': ['ls', '-lah', '--color']})

		anytime you run sh.ls() you will actually run 'ls -lah --color'. This works for all commands as it does it by name

			input: can be either str or bytes. It will figure it out and switch text for you.
			shell: if you specify True it will use '/bin/bash'. You can also pass the shell instead of True, it's fine. shell='/bin/dash'

		The run function can override things that are defined in the object. If you just need one off command to work differently the use it.

		Example::

		dash = pyshell(alias = {'ls': ['ls', '-lah', '--color']}, shell='/bin/dash')
		dash.echo("hello this should be working")
		dash.run(["lsblk"], shell=False)
		"""
		# These are not passed directly to Popen
		self._input = input
		self._capture_output = capture_output
		self._check = check
		self._logfile = logfile
		self._timeout = timeout
		self._popen = popen
		self._expect = expect
		# Arguments that will be passed to Popen
		self.kwargs = kwargs
		self._list = []

		# Define all the available shell commands
		# Might end up removing some of these in the future as they aren't used
		# But for now they aren't causing any harm
		(self.programs_tuple,
		self.dot_file_tuple, 
		self.dash_file_tuple, 
		self.underscore_file_tuple, 
		self.hybrid_file_tuple) = self.Parse_Path_Programs()

		self.PIPE = -1
		self.STDOUT = -2
		self.DEVNULL = -3
		self.DEFAULT = -4

		# If alias was defined and is not a dict throw an error
		if alias is not None:
			if not isinstance(alias, dict):
				raise TypeError(f"expected dict but got {type(alias).__name__} instead")
		self._alias = alias

	def __getattr__(self, attr: str):
		# We need to do some check against what was called. So we get our call. 
		call = getouterframes(currentframe())[1].code_context[0]
		try:
			# Now we're going to try to index it at a (). If this fails due to ValueError
			# Then it means the command wasn't called. Ex: pyshell.mkfs.ext4 instead of pyshell.mkfs.ext4().
			# We HAVE to catch and clear the list if this happens Or else commands could build in the store and
			# You might call something later you don't really want to.
			call = call[:call.index('(')].split('.')
			self._list.append(attr)
			return self
		except ValueError:
			self._list.clear()
		return self

	def __call__(self, *args,
				input=None, capture_output=False, check=False,
				logfile=None, timeout=None, expect=False, popen=False, **kwargs):
		# If someone sent us a list we should handle it
		if len(args) == 1:
			if isinstance(*args, list):
				args = tuple(*args)
		# Once called we send our list and Arguments to the call parser
		# Which will return our command (name), and then our args
		name, args = self.__parse_caller_commands(self._list, *args)
		# DEV echo
		#commands = ['echo', name]
		commands = [name]
		# Check kwargs to see if an alias was set
		# If it was set our commands to that
		
		if self._alias is not None:
			if self._alias.get(name):
				commands = deepcopy(self._alias.get(name))

		# Now that possible aliases are set, we can append our arguments
		for arg in args:
			commands.append(arg)

		self._list.clear()
		# This block says to error if we're not using the shell and we can't find the command.
		# But if we're using the shell then send it anyway. I'm not sure why I did this.
		# Maybe we should just send it no matter what?

		if kwargs.get('shell') or self.kwargs.get('shell'):
			if expect:
				print("You can't use shell and expect")

		if input is None:
			input = self._input
		if input is self.DEFAULT:
			input = None

		if capture_output is False:
			capture_output = self._capture_output
		if capture_output is self.DEFAULT:
			capture_output = False

		if check is False:
			check = self._check
		if check is self.DEFAULT:
			check = False

		if logfile is None:
			logfile = self._logfile
		if logfile is self.DEFAULT:
			logfile = None

		if timeout is None:
			timeout = self._timeout
		if timeout is self.DEFAULT:
			timeout = None

		if expect is False:
			expect = self._expect
		if expect is self.DEFAULT:
			expect = False

		if popen is False:
			popen = self._popen
		if popen is self.DEFAULT:
			popen = False

		if popen and expect:
			raise ValueError('expect and popen may not be used together.')

		if kwargs.get('shell') is None:
			kwargs['shell'] = self.kwargs.get('shell')

		# Update all arguments with the initialized choices.
		for Key, Value in self.kwargs.items():
			# Except for any choices explicitly Defaulted
			if kwargs.get(Key) != self.DEFAULT:
				# Make sure we Don't add our aliases. Popen can't use them
				if 'alias' not in Key:
					if Key != 'shell':
						kwargs[Key] = Value

		# Start real argument handling
		if input is not None:
			if kwargs.get('stdin') is not None:
				raise ValueError('stdin and input arguments may not both be used.')
			kwargs['stdin'] = self.PIPE

		if capture_output:
			if logfile is not None:
				raise ValueError('logfile will not work with capture_output')
			if kwargs.get('stdout') is not None or kwargs.get('stderr') is not None:
				raise ValueError('stdout and stderr arguments may not be used '
								'with capture_output.')
			kwargs['stdout'] = self.PIPE
			kwargs['stderr'] = self.PIPE

		if input:
			if isinstance(input, str):
				kwargs['text'] = True
			if isinstance(input, bytes):
				kwargs['text'] = False

		if not capture_output:
			if logfile:
				# Open our file. This makes it easier on the user. Just give us a filename
				logfile = open(logfile, 'a')
				kwargs['stdout'] = logfile
				kwargs['stderr'] = self.STDOUT

		# before we pass kwargs we need to remove anything remaining which was defaulted.	
		for Key, Value in kwargs.copy().items():
			if kwargs.get(Key) == self.DEFAULT:
				del kwargs[Key]

		if kwargs.get('shell') is not None:
			if kwargs.get('shell') is True:
				kwargs['executable'] = '/bin/bash'
				kwargs['shell'] = True
			elif kwargs.get('shell') is False:
				kwargs['shell'] = None
				kwargs['executable'] = None
			else:
				kwargs['executable'] = kwargs.get('shell')
				kwargs['shell'] = True

			# We need to make sure our strings are exactly how we want them for the shell
			# All of these different ways you can do this simple command will convert it exactly.
			# It is repr as well so if you send \n, the shell will get \n. You don't have to escape
			# dash = pyshell(shell='/bin/dash')
			# 
			# dash.echo('$0') ## dash.run(["echo", "$0"]) ## dash.run("echo", "$0") ## dash.run("echo $0")
			# Final output ['echo $0']
			rcommand = []
			if len(commands) == 1:
				commands = commands[0]

			if isinstance(commands, str):
				commands = (commands,)
			
			for arg in commands:
				rcommand.append(repr(arg).strip('\''))
			commands = [' '.join((arg) for arg in rcommand)]

		if kwargs.get('shell') is None and self.kwargs.get('shell') is None:
			if shutil.which(name) is not None or self._alias.get(name) is not None:
				if expect:
					return spawn(" ".join(com for com in commands))
				elif popen:
					return pyshellPopen(commands, **kwargs)
				else:
					self.run(	commands,
								input=input, capture_output=capture_output, check=check,
								logfile=logfile, timeout=timeout, **kwargs)

					return self.process
			else:
				raise CommandNotFound(f'command {name} does not exist')
		else:
			self.run(	commands,
						input=input, capture_output=capture_output, check=check,
						logfile=logfile, timeout=timeout, **kwargs)

			return self.process
		
	def run(self, *popenargs,
			input=None, capture_output=False, check=False,
			logfile=None, timeout=None, **kwargs):
		"""Run command with arguments and return a CompletedProcess instance.

		The returned instance will have attributes args, returncode, stdout and
		stderr. By default, stdout and stderr are not captured, and those attributes
		will be None. Pass stdout=PIPE and/or stderr=PIPE in order to capture them.

		If check is True and the exit code was non-zero, it raises a
		CalledProcessError. The CalledProcessError object will have the return code
		in the returncode attribute, and output & stderr attributes if those streams
		were captured.

		If timeout is given, and the process takes too long, a TimeoutExpired
		exception will be raised.

		There is an optional argument "input", allowing you to
		pass bytes or a string to the subprocess's stdin.  If you use this argument
		you may not also use the Popen constructor's "stdin" argument, as
		it will be used internally.

		pyshell run has a couple of customizations over the original run.

		1. pyshell will check if you pass a string or bytes for input=
		you do not need to specify text=True or false 
		(unless you are not sending input and want the output in text/bytes specifically)

		2. When specifying shell=True it will use '/bin/bash' by default instead of sh.
		You can change this without specifying executable, just pass shell='/bin/sh'
		Additionally you can pass a list to shell if you want more options.
		shell=['/bin/bash', '-O', 'extglob'] if you want to add extglob

		3. When using shell= you do not need to escape characters.
		What you have in quotes will be passed exact and the shell will expand.

		The other arguments are the same as for the Popen constructor.
		"""
		try:
			# Using our patched Popen for some special goodies.
			with pyshellPopen(*popenargs, **kwargs) as process:
				try:
					stdout, stderr = process.communicate(input, timeout=timeout)
				except TimeoutExpired as exc:
					process.kill()
					if _mswindows:
						# Windows accumulates the output in a single blocking
						# read() call run on child threads, with the timeout
						# being done in a join() on those threads.  communicate()
						# _after_ kill() is required to collect that and add it
						# to the exception.
						exc.stdout, exc.stderr = process.communicate()
					else:
						# POSIX _communicate already populated the output so
						# far into the TimeoutExpired exception.
						process.wait()
					raise
				except:  # Including KeyboardInterrupt, communicate handled that.
					process.kill()
					# We don't call process.wait() as .__exit__ does that for us.
					raise
				retcode = process.poll()
				if check and retcode:
					raise CalledProcessError(retcode, process.args,
											output=stdout, stderr=stderr)
			self.process = CompletedProcess(process.args, retcode, stdout, stderr)
			return self.process
		# Wrap everything in a try finally so we make sure we close our file if it exists.	
		finally:
			if logfile:
				logfile.close()

	def setAlias(self, command: str, alias: list):
		"""Sets a command alias
		
		Arguments:
			command: The command you want to alias. Such as 'echo' or 'mkfs.ext4'
			alias: a list containing your alias ['echo', '-e']
		"""
		# If our alias is not a dict we assume it's none and then create a bare one.
		if not isinstance(self._alias, dict):
			self._alias = {}
		# If the alias is not in a list format then we will raise an exception
		if not isinstance(alias, list):
			raise TypeError(f"expected list but got {type(alias).__name__} instead")
		self._alias.update({command:alias})

	@staticmethod
	def Parse_Path_Programs():
		# Might end up removing some of these in the future as they aren't used
		# But for now they aren't causing any harm
		#
		# Get Users Path
		env = os.environ.get('PATH').split(':')
		# Make a set to store Items since it's unique
		files_set = set()
		# Iterate through the environment globing up the whole town
		for path in env:
			for file in Path(path).glob('*'):
				if file.is_file():
					files_set.add(file.name)
		# Convert the set to a list		
		files = list(files_set)
		files.sort()
		# Make a new list because we need to run each program
		# Through which to make sure they're executable
		programs_list = []
		for path in files:
			prog = shutil.which(path)
			if prog is not None:
				prog = Path(prog)
				programs_list.append(prog)
		programs_list = tuple(programs_list)
		
		programs_tuple = []
		for path in programs_list:
			programs_tuple.append(path.name)
		programs_tuple = tuple(programs_tuple)

		dot_file_list = []
		# Make a list of dot.files
		for path in programs_list:
			if '.' in path.name:
				dot_file_list.append(path.name)
		dot_file_tuple = tuple(dot_file_list)

		underscore_file_list = []
		# Make a list of underscore_files
		for path in programs_list:
			if '_' in path.name:
				if '-' not in path.name:
					underscore_file_list.append(path.name)
		underscore_file_tuple = tuple(underscore_file_list)

		dash_file_list = []
		# Make a list of dash-files
		for path in programs_list:
			if '-' in path.name:
				if '_' not in path.name:
					dash_file_list.append(path.name)
		dash_file_tuple = tuple(dash_file_list)

		hybrid_file_list = []
		# Make a hybrid_file-list
		for path in programs_list:
			if '-' in path.name:
				if '_' in path.name:
					hybrid_file_list.append(path.name)
		hybrid_file_tuple = tuple(hybrid_file_list)

		return programs_tuple, dot_file_tuple, dash_file_tuple, underscore_file_tuple, hybrid_file_tuple

	def __parse_caller_commands(self, command_list: list, *args):
		# If our list is only one then we can just drop and use that as a command
		if len(command_list) >1:

			convert_list = []
			for command in command_list:
				convert_list.append(command.replace('_','-'))

			# Make a copy of our list and reverse it
			command_list = convert_list
			reverse_list = command_list.copy()
			reverse_list.reverse()

			name = ''
			# Iterate through and build our first name
			# This will be all attributes combined
			for command in command_list:
				name = name+'.'+command
			name = name.lstrip('.')	
			num = len(reverse_list)
			# Iterate through the reverse list stripping our command down 1 by 1
			# And then checking it against the programs tuple
			for command in reverse_list:
				num = num -1
				# All this replacing was here before I did a full convert list. It doesn't hurt anything so I'll keep it in
				# Possible that it comes in handy later if we don't want full conversion, and only want conversion on matched programs
				# Maybe make a switch to disable argument conversion? - is more common in linux commands anyway
				name = name.rstrip(command.replace('_','-')).rstrip('.').replace('_','-')
				if name in self.programs_tuple:
					break

			# We kept track of our place in the list so that we can use the rest of our list as arguments
			for number in range(0, num):
				del command_list[0]
			return name, tuple(command_list)+tuple(args)

		else:
			# Our list is only 1 or zero. If it's one easy just assume that's our command
			if command_list:
				name = command_list.pop(0).replace('_','-')
				
				return name, tuple(command_list)+tuple(args)
			else:
				# empty list means pyshell was called directly
				# We should see if there are any arguments and handle them
				args = list(args)
				if args:
					# We pop the first arg as the name so pyshell('echo', 'hello'), echo becomes our name
					name = args.pop(0)
					return name, tuple(command_list)+tuple(args)
				else:
					raise PyshellError(f"No arguments were passed")

class PyshellError(Exception): pass

class CommandNotFound(OSError): pass

	
