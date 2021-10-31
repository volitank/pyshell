.. _passing_arguments:

Passing Arguments
=================

When passing multiple arguments to a command, each argument *must* be a separate
string:

.. code-block:: python

	shell = pyshell()
	shell.tar("cvf", "/tmp/test.tar", "/my/home/directory/")

This *will not work*:

.. code-block:: python

	shell.tar("cvf /tmp/test.tar /my/home/directory")

If you're using the ``shell='/bin/bash'`` Both of these will work. This is because pyshell does some special magic behind the scenes so the shell gets exactly what you told it. This feature is almost certainly to be buggy, example with output in comments:

.. code-block:: python

	dash = pyshell(shell='/bin/dash')

	dash.echo('shell is $0')
	# shell is /bin/dash

	dash.echo('shell', 'is' ,'$0')
	# shell is /bin/dash

	dash.run(["echo", "shell", "is", "$0"], shell='/bin/bash')
	# shell is /bin/bash ## Notice we can change the shell one time on the fly and not effect the instance

	dash.run(["echo shell is $0"])
	# shell is /bin/dash

	dash("echo", "shell", "is", "$0")
	# shell is /bin/dash

	dash("echo shell is $0")
	# shell is /bin/dash

	dash("echo", "shell", "is", "$0", shell=DEFAULT)
	# shell is $0 ## We can override back to no shell using the DEFAULT switch.

	dash("echo shell is $0", shell=DEFAULT)
	# FileNotFoundError: [Errno 2] No such file or directory: 'echo shell is $0'
	# This one doesn't work because with out a shell it tries to use that string as a command

The only difference between using our run function and calling the class directly is with run you must use a list, as seen above. If something isn't working by calling the class then you can try to call run directly, it *should* work with run.

.. seealso:: Pyshell Arguments section on the :ref:`pyshell_arguments_shell`

Dashes
------

For commands with dashes we use underscores instead. All underscores in the caller will be converted to dashes. Anything in the args section will not. Below is an example of different ways to run commands and their outputs in comments below so you can get an idea as how it works.

.. code-block:: python

	shell = pyshell()
	shell.echo.test_echo()
	# test-echo

	shell.echo("test_echo")
	# test_echo

	shell.run(["echo_test"])
	# FileNotFoundError: [Errno 2] No such file or directory: 'echo_test'

	shell("echo_test")
	# pyshell.pyshell.CommandNotFound: command echo_test does not exist

	shell.echo_test()
	# pyshell.pyshell.CommandNotFound: command echo-test does not exist

Equivalents
-----------

There are many ways to go about running commands in pyshell. For example all commands below are equal.

.. code-block:: python

	shell = pyshell()
	shell.mkfs.ext4('/dev/sdb1')
	shell.run(['mkfs.ext4', '/dev/sdb1'])
	shell('mkfs.ext4', '/dev/sdb1')

When initialized we build a tuple of program names that you can use. If you do something like ``shell.mkfs.ext4.hello`` we take ``mkfs.ext4.hello`` and test it against that tuple. If nothing is found we try ``mkfs.ext4``, and then ``mkfs``. if something matches we stop, use that as the command and then the rest as arguments. This is how we are able to accommodate some commands. 