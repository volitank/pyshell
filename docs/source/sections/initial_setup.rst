.. _installation:

Installation
============

To use pyshell, first install it using pip:

You can install the latest release

.. code-block:: console
 
	$ pip install pyshell

You can install directly from GitHub

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