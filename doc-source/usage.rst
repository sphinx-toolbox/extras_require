============
Usage
============

Enable ``extras_require`` by adding "sphinxcontrib.extras_require" to the ``extensions`` variable in ``conf.py``:

.. code-block:: python

	extensions = [
		...
		"sphinxcontrib.extras_require",
		]

For more information see https://www.sphinx-doc.org/en/master/usage/extensions/index.html#third-party-extensions .

|

This extension provides a single directive, ``.. extras-require::``. The requirements can be specified in several ways:

* The ``:file:`` option, which takes a path to a :pep:`508` ``requirements.txt`` file. The path is relative to the ``package_root`` variable given in ``conf.py``, which in turn is relative to the parent directory of the sphinx documentation.

* The ``:__pkginfo__:`` option, which takes no arguments. This looks in the parent directory of the sphinx documentation for a file named ``__pkginfo__.py``. The requirements are imported as the variable ``extras_require``, which must be a dictionary mapping extras to a list of requirements. e.g.

	.. code-block:: python

		extras_require = {
			'extra_b': [
					"flask >=1.1.2",
					"click < 7.1.2",
					"sphinx ==3.0.3",
					]
			}

	The requirements can be generated programmatically in the ``__pkginfo__.py`` file during the import process.

* The ``:setup.cfg:`` option, which takes no arguments. This looks in the parent directory of the sphinx documentation for a file named ``setup.cfg``. This file must be readable by Python's :mod:`configparser` module, and contain the section ``[options.extras_require]``. e.g.

	.. code-block:: ini

		[options.extras_require]
		extra_c = faker; pytest; tox

	See https://setuptools.readthedocs.io/en/latest/setuptools.html#configuring-setup-using-setup-cfg-files for more information on ``setup.cfg``.

* Typing the list of :pep:`508` requirements manually. Each requirement must be on its own line, and there must be a blank line between the directive and the list of requirements. e.g.

	.. code-block:: rest

		.. extras-require::

			pytz >=2019.1

Only one of the above options can be used in each directive.

The ``:scope:`` option can be used to specify a different scope for additional requirements, such as package, module, class or function. Any string value can be supplied here.
