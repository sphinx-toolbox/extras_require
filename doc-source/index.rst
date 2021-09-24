================
extras_require
================

.. start short_desc

.. documentation-summary::
	:meta:

.. end short_desc

.. start shields

.. only:: html

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

	.. |docs| rtfd-shield::
		:project: extras_require
		:alt: Documentation Build Status

	.. |docs_check| actions-shield::
		:workflow: Docs Check
		:alt: Docs Check Status

	.. |actions_linux| actions-shield::
		:workflow: Linux
		:alt: Linux Test Status

	.. |actions_windows| actions-shield::
		:workflow: Windows
		:alt: Windows Test Status

	.. |actions_macos| actions-shield::
		:workflow: macOS
		:alt: macOS Test Status

	.. |actions_flake8| actions-shield::
		:workflow: Flake8
		:alt: Flake8 Status

	.. |actions_mypy| actions-shield::
		:workflow: mypy
		:alt: mypy status

	.. |requires| image:: https://dependency-dash.herokuapp.com/github/sphinx-toolbox/extras_require/badge.svg
		:target: https://dependency-dash.herokuapp.com/github/sphinx-toolbox/extras_require/
		:alt: Requirements Status

	.. |coveralls| coveralls-shield::
		:alt: Coverage

	.. |codefactor| codefactor-shield::
		:alt: CodeFactor Grade

	.. |pypi-version| pypi-shield::
		:project: extras_require
		:version:
		:alt: PyPI - Package Version

	.. |supported-versions| pypi-shield::
		:project: extras_require
		:py-versions:
		:alt: PyPI - Supported Python Versions

	.. |supported-implementations| pypi-shield::
		:project: extras_require
		:implementations:
		:alt: PyPI - Supported Implementations

	.. |wheel| pypi-shield::
		:project: extras_require
		:wheel:
		:alt: PyPI - Wheel

	.. |conda-version| image:: https://img.shields.io/conda/v/domdfcoding/extras_require?logo=anaconda
		:target: https://anaconda.org/domdfcoding/extras_require
		:alt: Conda - Package Version

	.. |conda-platform| image:: https://img.shields.io/conda/pn/domdfcoding/extras_require?label=conda%7Cplatform
		:target: https://anaconda.org/domdfcoding/extras_require
		:alt: Conda - Platform

	.. |license| github-shield::
		:license:
		:alt: License

	.. |language| github-shield::
		:top-language:
		:alt: GitHub top language

	.. |commits-since| github-shield::
		:commits-since: v0.4.0
		:alt: GitHub commits since tagged version

	.. |commits-latest| github-shield::
		:last-commit:
		:alt: GitHub last commit

	.. |maintained| maintained-shield:: 2021
		:alt: Maintenance

	.. |pypi-downloads| pypi-shield::
		:project: extras_require
		:downloads: month
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

.. latex:clearpage::

For instance, this:

.. code-block:: rest

	.. extras-require:: formulae
		:file: formulae/requirements.txt

will produce this:

.. extras-require:: formulae

	mathematical>=0.1.7
	pandas>=1.0.1
	pyparsing>=2.2.0
	tabulate>=0.8.3
	cawdrey>=0.1.2
	quantities>=0.12.4


The path given in ``:file:`` is relative to the ``package_root`` variable given in ``conf.py``, which in turn is relative to the parent directory of the sphinx documentation. For example, this line:.

.. code-block:: python

	package_root = "chemistry_tools"

points to ``./chemistry_tools``, and therefore ``:file: formulae/requirements.txt`` points to ``./chemistry_tools/formulae/requirements.txt``.

Requirements can also be specified in ``pyproject.toml`` (using the option ``:pyproject:``), ``setup.cfg`` (using the option ``:setup.cfg::``), or by typing in the requirements manually, one per line.

The ``:scope:`` option can be used to specify a different scope for additional requirements, such as ``package``, ``module``, ``class`` or ``function``. Any string value can be supplied here.


.. toctree::
	:hidden:

	Home<self>

Contents
-----------

.. phantom-section::

.. toctree::
	:maxdepth: 3
	:caption: Usage

	usage/installation
	usage/configuration
	usage/directive

.. toctree::
	:maxdepth: 3
	:caption: API Reference
	:glob:

	api/extras_require
	api/directive
	api/sources


.. sidebar-links::
	:caption: Links
	:github:
	:pypi: extras_require

	Contributing Guide <https://contributing-to-sphinx-toolbox.readthedocs.io/en/latest/>
	Source
	license

.. start links

.. only:: html

	View the :ref:`Function Index <genindex>` or browse the `Source Code <_modules/index.html>`__.

	:github:repo:`Browse the GitHub Repository <sphinx-toolbox/extras_require>`

.. end links
