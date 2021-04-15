=================
Configuration
=================

.. confval:: package_root
	:type: :class:`str`
	:required: True

	 Location of package source directory relative to documentation source directory.

	For example,

	.. code-block:: python

		package_root = "chemistry_tools"

	points to ``./chemistry_tools``.


.. confval:: pypi_name
	:type: :class:`str`
	:required: False

	 The name of the package on PyPI.

	This is the name provided to ``pip install``.
	Defaults to the name of the project in the `Sphinx configuration`_.

	.. _Sphinx configuration: https://www.sphinx-doc.org/en/master/usage/configuration.html#confval-project

	.. versionadded:: 0.4.0
