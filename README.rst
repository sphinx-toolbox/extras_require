================
extras_require
================

.. start short_desc

**Display a warning at the top of module documentation that it has additional requirements.**

.. end short_desc

.. start shields

.. list-table::
	:stub-columns: 1
	:widths: 10 90

	* - Docs
	  - |docs| |docs_check|
	* - Tests
	  - |actions_linux| |actions_windows| |actions_macos| |coveralls|
	* - PyPI
	  - |pypi-version| |supported-versions| |supported-implementations| |wheel|
	* - Anaconda
	  - |conda-version| |conda-platform|
	* - Activity
	  - |commits-latest| |commits-since| |maintained| |pypi-downloads|
	* - QA
	  - |codefactor| |actions_flake8| |actions_mypy|
	* - Other
	  - |license| |language| |requires|

.. |docs| image:: https://img.shields.io/readthedocs/extras-require/latest?logo=read-the-docs
	:target: https://extras-require.readthedocs.io/en/latest
	:alt: Documentation Build Status

.. |docs_check| image:: https://github.com/sphinx-toolbox/extras_require/workflows/Docs%20Check/badge.svg
	:target: https://github.com/sphinx-toolbox/extras_require/actions?query=workflow%3A%22Docs+Check%22
	:alt: Docs Check Status

.. |actions_linux| image:: https://github.com/sphinx-toolbox/extras_require/workflows/Linux/badge.svg
	:target: https://github.com/sphinx-toolbox/extras_require/actions?query=workflow%3A%22Linux%22
	:alt: Linux Test Status

.. |actions_windows| image:: https://github.com/sphinx-toolbox/extras_require/workflows/Windows/badge.svg
	:target: https://github.com/sphinx-toolbox/extras_require/actions?query=workflow%3A%22Windows%22
	:alt: Windows Test Status

.. |actions_macos| image:: https://github.com/sphinx-toolbox/extras_require/workflows/macOS/badge.svg
	:target: https://github.com/sphinx-toolbox/extras_require/actions?query=workflow%3A%22macOS%22
	:alt: macOS Test Status

.. |actions_flake8| image:: https://github.com/sphinx-toolbox/extras_require/workflows/Flake8/badge.svg
	:target: https://github.com/sphinx-toolbox/extras_require/actions?query=workflow%3A%22Flake8%22
	:alt: Flake8 Status

.. |actions_mypy| image:: https://github.com/sphinx-toolbox/extras_require/workflows/mypy/badge.svg
	:target: https://github.com/sphinx-toolbox/extras_require/actions?query=workflow%3A%22mypy%22
	:alt: mypy status

.. |requires| image:: https://dependency-dash.repo-helper.uk/github/sphinx-toolbox/extras_require/badge.svg
	:target: https://dependency-dash.repo-helper.uk/github/sphinx-toolbox/extras_require/
	:alt: Requirements Status

.. |coveralls| image:: https://img.shields.io/coveralls/github/sphinx-toolbox/extras_require/master?logo=coveralls
	:target: https://coveralls.io/github/sphinx-toolbox/extras_require?branch=master
	:alt: Coverage

.. |codefactor| image:: https://img.shields.io/codefactor/grade/github/sphinx-toolbox/extras_require?logo=codefactor
	:target: https://www.codefactor.io/repository/github/sphinx-toolbox/extras_require
	:alt: CodeFactor Grade

.. |pypi-version| image:: https://img.shields.io/pypi/v/extras_require
	:target: https://pypi.org/project/extras_require/
	:alt: PyPI - Package Version

.. |supported-versions| image:: https://img.shields.io/pypi/pyversions/extras_require?logo=python&logoColor=white
	:target: https://pypi.org/project/extras_require/
	:alt: PyPI - Supported Python Versions

.. |supported-implementations| image:: https://img.shields.io/pypi/implementation/extras_require
	:target: https://pypi.org/project/extras_require/
	:alt: PyPI - Supported Implementations

.. |wheel| image:: https://img.shields.io/pypi/wheel/extras_require
	:target: https://pypi.org/project/extras_require/
	:alt: PyPI - Wheel

.. |conda-version| image:: https://img.shields.io/conda/v/domdfcoding/extras_require?logo=anaconda
	:target: https://anaconda.org/domdfcoding/extras_require
	:alt: Conda - Package Version

.. |conda-platform| image:: https://img.shields.io/conda/pn/domdfcoding/extras_require?label=conda%7Cplatform
	:target: https://anaconda.org/domdfcoding/extras_require
	:alt: Conda - Platform

.. |license| image:: https://img.shields.io/github/license/sphinx-toolbox/extras_require
	:target: https://github.com/sphinx-toolbox/extras_require/blob/master/LICENSE
	:alt: License

.. |language| image:: https://img.shields.io/github/languages/top/sphinx-toolbox/extras_require
	:alt: GitHub top language

.. |commits-since| image:: https://img.shields.io/github/commits-since/sphinx-toolbox/extras_require/v0.5.0
	:target: https://github.com/sphinx-toolbox/extras_require/pulse
	:alt: GitHub commits since tagged version

.. |commits-latest| image:: https://img.shields.io/github/last-commit/sphinx-toolbox/extras_require
	:target: https://github.com/sphinx-toolbox/extras_require/commit/master
	:alt: GitHub last commit

.. |maintained| image:: https://img.shields.io/maintenance/yes/2023
	:alt: Maintenance

.. |pypi-downloads| image:: https://img.shields.io/pypi/dm/extras_require
	:target: https://pypi.org/project/extras_require/
	:alt: PyPI - Downloads

.. end shields


Overview
--------

This extension assumes you have a repository laid out like this:

::

	.
	├── chemistry_tools
	│   ├── __init__.py
	│   ├── formulae
	│   │   ├── __init__.py
	│   │   ├── compound.py
	│   │   ├── formula.py
	│   │   ├── parser.py
	│   │   └── requirements.txt
	│   ├── constants.py
	│   └── utils.py
	├── doc-source
	│   ├── api
	│   │   ├── chemistry_tools.rst
	│   │   ├── elements.rst
	│   │   ├── formulae.rst
	│   │   └── pubchem.rst
	│   ├── conf.py
	│   ├── index.rst
	│   └── requirements.txt
	├── LICENSE
	├── README.rst
	├── requirements.txt
	├── setup.py
	└── tox.ini

The file ``./chemistry_tools/formulae/requirements.txt`` contains the additional requirements to run the ``formulae`` subpackage. These would be defined in ``setup.py`` like this:

.. code-block:: python

	setup(
			extras_require={
					"formulae": [
							"mathematical>=0.1.7",
							"pandas>=1.0.1",
							"pyparsing>=2.2.0",
							"tabulate>=0.8.3",
							"cawdrey>=0.1.2",
							"quantities>=0.12.4",
							],
					}
			)

A message can be displayed in the documentation to indicate that the subpackage has these additional requirements that must be installed.

For instance, this:

.. code-block:: rest

	.. extras-require:: formulae
		:file: formulae/requirements.txt

will produce this:

.. image:: doc-source/example.png

The path given in ``:file:`` is relative to the ``package_root`` variable given in ``conf.py``, which in turn is relative to the parent directory of the sphinx documentation.

I.e, this line:

.. code-block:: python

	package_root = "chemistry_tools"

points to ``./chemistry_tools``, and therefore ``:file: formulae/requirements.txt`` points to ``./chemistry_tools/formulae/requirements.txt``.

Requirements can also be specified in ``pyproject.toml`` (using the option ``:pyproject:``), ``setup.cfg`` (using the option ``:setup.cfg::``), or by typing in the requirements manually, one per line.

The ``:scope:`` option can be used to specify a different scope for additional requirements, such as ``package``, ``module``, ``class`` or ``function``. Any string value can be supplied here.

Installation
--------------

.. start installation

``extras_require`` can be installed from PyPI or Anaconda.

To install with ``pip``:

.. code-block:: bash

	$ python -m pip install extras_require

To install with ``conda``:

	* First add the required channels

	.. code-block:: bash

		$ conda config --add channels https://conda.anaconda.org/conda-forge
		$ conda config --add channels https://conda.anaconda.org/domdfcoding

	* Then install

	.. code-block:: bash

		$ conda install extras_require

.. end installation

Enable ``extras_require`` by adding "sphinxcontrib.extras_require" to the ``extensions`` variable in ``conf.py``:

.. code-block:: python

	extensions = [
		...
		"sphinxcontrib.extras_require",
		]

For more information see https://www.sphinx-doc.org/en/master/usage/extensions/index.html#third-party-extensions .


Links
-----

- Source: https://github.com/sphinx-toolbox/extras-require
- Bugs: https://github.com/sphinx-toolbox/extras-require/issues
