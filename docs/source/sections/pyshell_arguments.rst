.. _pyshell_arguments:

Pyshell Arguments
=================

Defaults
--------

.. code-block:: python

	input=None, capture_output=False, check=False,
	logfile=None, timeout=None, alias: dict=None, **kwargs):

Most of pyshell's arguments are much like subprocess.run.
We actually use a slightly modified version of subprocess.run

input
-----

With pyshell input can be either a string or bytes, and there is no need to specify ``text=True`` as with subprocess

.. code-block:: python

	shell = pyshell(input='this will go to stdin')

capture_output
--------------

This option works exactly like the one in subprocess. It essentially sets stdout and stderr to PIPE

check
-----

Another option we have that works just like subprocess. If set to True it will throw an exception on a bad exit code

.. code-block:: python

	shell = pyshell(capture_output=False, check=True)

logfile
-------

This is our first totally new option. Setting this will change stdout and stderr to a file. This cannot be used with **capture_output**. This should be a file in string or PathLike format. 


.. code-block:: python

	shell = pyshell(logfile='/tmp/pyshell.log')

timeout
-------

Sets the timeout, in seconds, that we will wait on a child process.

.. code-block:: python

	shell = pyshell(timeout=10)

alias
-----

This one is probably one of my favorite additions. To set this it is simple a dict with Key=command Value=alias.

.. code-block:: python

	alias = {
	'ls': ['ls', '-lah', '--color'],
	'echo': ['printf']
	}
	shell = pyshell(alias=alias)

You can also change them on the fly with ``shell.setAlias(ls, ['-lah'])``

.. _pyshell_arguments_shell:

shell
-----

While this is technically a kwarg we do run with a patched Popen that allows you to set the shell for ``shell=`` rather than True and setting ``executable=``. Another change that I've made is that you can pass a list for ``shell=`` if you want your executable to have more options than just ``-c``

.. code-block:: python

	shell = pyshell(shell='/bin/dash') # Sets shell=True and executable='/bin/dash'
	shell = pyshell(shell=['/bin/bash', '-O', 'extglob']) # Same as above yet we will have extglob for bash

All other ``**kwargs`` are passed directly to Popen. If you're interested check out their documentation for more options.

override
--------

Any settings whether initialized or not can be overrode while running your commands. Any option other than the defaults will override, to override to the default we have a special constant.

.. code-block:: python

	shell = pyshell(shell='/bin/dash', logfile='/tmp/pyshell.log')
	shell.echo('Hello', 'World', logfile=DEFAULT) # This will run this command with the logfile set to the default of None
	shell.echo('Hello', 'World', shell='/bin/bash') # This will change our shell to bash for this command only
