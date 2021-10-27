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

##TODO
# Right now we wrap around the current subprocess run function.
# I will likely merge them do I'm not wrapping a wrapper dawg.
#
# Add more functions. This is barely useful right now outside of proof of concept

from subprocess import run

PIPE = -1
STDOUT = -2
DEVNULL = -3

class pyshell():

	def __init__(	self,
					capture_output: bool=False, check: bool=False,
					stdin=None, stdout=None, stderr=None,
					# Supply an unopened file. Such at '/tmp/logfile.txt'. We will open, append, and close for you.
					# If you want to redirect stderr to the log as well pass stderr=STDOUT
					logfile=None,
					shell: bool=False, text: bool=False, input: bool=False,
					#TODO add an input option for individual functions. Right now it is just the object and run
					**kwargs):

		"""Subprocess as an object, for Linux.

		Initialize with certain options and use them through the life of your object.
		Most of these are exactly the same you're use too with subprocess.run.
		Outlined below are new features

		Arguments:
			logfile: logfile='/tmp/pyshell.log' expects an unopen file. We will open for you.
			aliasing: You can alias commands like so sh = pybash(ls_alias=['ls', '-lah', '--color'])

		anytime you run sh.ls() you will actually run 'ls -lah --color'. This works for all functions except run

			input: can be either str or bytes. It will figure it out and switch text for you.
			shell: if you specify True it will use '/bin/bash'. You can also pass the shell instead of True, it's fine. shell='/bin/dash'

		The run function can override things that are defined in the object. If you just need one off command to work differently the use it.

		Example to mount readonly::

		dash = pyshell(ls_alias=['ls', '-lah', '--color'], shell='/bin/dash')
		dash.echo("hello this should be working")
		dash.run(["lsblk"], shell=False)
		"""

		self.stdin = stdin
		self.stdout = stdout
		self.stderr = stderr
		self.capture_output = capture_output
		self.check = check
		self.kwargs = kwargs
		self.logfile = logfile
		self.shell = shell
		self.text = text
		self.input = input

	# You can call run directly and override any thing that you've initialized with
	def run(self,	command_list, shell=None,
					stdin=None, stdout=None, stderr=None, logfile=None,
					check: bool=False, capture_output: bool=False,
					text=None, input=None,
					**kwargs):
		""" Our main function that executes all of our commands. 

		You can use this to override settings in your pybash instance
		"""
		# Define selfs
		_stdin = self.stdin
		_stdout = self.stdout
		_stderr = self.stderr
		_check = self.check
		_capture = self.capture_output
		_text = self.text
		_input = self.input

		# We need to convert our input if we're using the shell
		if self.shell and shell is None:

			rcommand = []
			# We need to make sure our strings are exactly how we want them for the shell
			for arg in command_list:
				rcommand.append(repr(arg).strip('\''))
				command_list = [' '.join((arg) for arg in rcommand)]

		# Our special settings for shell.
		if self.shell:
			_shell = True
			if self.shell is True:
				_exec = '/bin/bash'
			else:
				_exec = self.shell
		else:
			_shell = False
			_exec = None

		# Override object with shell=False
		# Handle overrides last
		if shell is not None:
			_shell = True
			if shell is False:
				_shell = False
				_exec = None
			elif shell is True:
				_exec = '/bin/bash'
			else:
				_exec = shell

		if stdout:
			_stdin = stdin
		if stdout:
			_stdout = stdout
		if stdout:
			_stderr = stderr

		if check:
			_check = check
		if capture_output:
			_capture = capture_output

		if text:
			_text = text
		if input:
			_input = input

		# Do a quick check on the input and set text to yes or no depending.
		# Not sure how this could bite us but we'll see
		
		if input or self.input:
			if isinstance(_input, str):
				_text = True
			if isinstance(_input, bytes):
				_text = False

		# You can disable a defined logfile setting logfile to false
		if self.logfile and logfile is None:
			with open(self.logfile, 'a') as logfile:
				_stdout = logfile
				self.process = run(command_list, 
								check=_check,
								capture_output=_capture,
								stdin=_stdin,
								stdout=_stdout,
								stderr=_stderr,
								shell=_shell,
								text=_text,
								input=_input,
								executable=_exec
								)
		else:
			self.process = run(command_list, 
							check=_check,
							capture_output=_capture,
							stdin=_stdin,
							stdout=_stdout,
							stderr=_stderr,
							shell=_shell,
							text=_text,
							input=_input,
							executable=_exec
							)

	def echo(self, *args, input=None):
		"""Uses the echo command

		alias with pybash(echo_alias=['echo', 'e'])
		"""
		commands = []
		# Check kwargs to see if an alias was set
		if self.kwargs.get('echo_alias'):
			#If there was then append the args first
			for arg in self.kwargs.get('echo_alias'):
				commands.append(arg)
		else:
			commands = ['echo']

		for arg in args:
			commands.append(arg)

		self.run(commands, input=input)
		return self.process

	def ls(self, *args, input=None):
		"""ls 'lists' files and directories

		alias with pyshell(ls_alias=['ls', '-lah', '--color'])
		"""
		commands = []
		# Check kwargs to see if an alias was set
		if self.kwargs.get('ls_alias'):
			#If there was then append the args first
			for arg in self.kwargs.get('ls_alias'):
				commands.append(arg)
		else:
			commands = ['ls']

		# Now we add our method arguments
		for arg in args:
			commands.append(arg)

		self.run(commands, input=input)
		return self.process

	def cat(self, *args, input=None):
		"""Concatenates files.

		alias with pyshell(cat_alias=['cat', '"I've never used a cat switch in my entire life"'])
		"""
		commands = []
		# Check kwargs to see if an alias was set
		if self.kwargs.get('cat_alias'):
			#If there was then append the args first
			for arg in self.kwargs.get('cat_alias'):
				commands.append(arg)
		else:
			commands = ['cat']

		# Now we add our method arguments
		for arg in args:
			commands.append(arg)

		self.run(commands, input=input)
		return self.process

	def grep(self, *args, input=None):
		"""grep files.

		alias with pyshell(grep_alias=['grep', '--color'])
		"""
		commands = []
		# Check kwargs to see if an alias was set
		if self.kwargs.get('grep_alias'):
			#If there was then append the args first
			for arg in self.kwargs.get('grep_alias'):
				commands.append(arg)
		else:
			commands = ['grep']

		# Now we add our method arguments
		for arg in args:
			commands.append(arg)

		self.run(commands, input=input)
		return self.process
