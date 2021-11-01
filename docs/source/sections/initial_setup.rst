.. _installation:

Installation
============

To use pyshell, first install it using pip:

You can install a specific release by running

.. code-block:: console
 
	$ pip install https://github.com/volitank/pyshell/releases/download/v1.0.0a2/pyshell-1.0.0a2.tar.gz

While we're still in early development stages it is preferred that you run directly from the git

.. code-block:: console
 
	$ pip install https://github.com/volitank/pyshell/archive/refs/heads/main.tar.gz

.. _initialization:

Initialization
--------------

Now that it's installed you can import and initialize:

.. code-block:: python

	from pyshell import pyshell

	shell = pyshell(logfile='/tmp/shell.log', shell='/bin/bash')
	shell.echo('Hello', 'World')
	
.. seealso:: :ref:`pyshell_arguments`