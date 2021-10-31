.. _installation:

Installation
============

To use pyshell, first install it using pip:

.. code-block:: console

   $ pip install pyshell

.. _initialization:

Initialization
--------------

Now that it's installed you can import and initialize:

.. code-block:: python

	from pyshell import pyshell

	shell = pyshell(logfile='/tmp/shell.log', shell='/bin/bash')
	shell.echo('Hello', 'World')
	
.. seealso:: :ref:`pyshell_arguments`