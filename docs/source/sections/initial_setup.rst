.. _installation:

Installation
============

To use pyshell, first install it using pip:

.. code-block:: console

	$ pip install https://github.com/volitank/pyshell/releases/download/v1.0.0.a1/pyshell-1.0.0a1-py3-none-any.whl
 
or

.. code-block:: console
 
	$ pip install https://github.com/volitank/pyshell/releases/download/v1.0.0.a1/pyshell-1.0.0a1.tar.gz

To install the directly from the source code you can use 

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