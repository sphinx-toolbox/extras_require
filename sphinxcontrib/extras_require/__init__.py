#!/usr/bin/env python3
"""
sphinxcontrib.extras_require
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A Sphinx directive to specify that a module has extra requirements, and show how to install them
Display a warning at the top of module documentation that it has additional requirements.

:copyright: Copyright (c) 2020 by Dominic Davis-Foster <dominic@davis-foster.co.uk>
:license: BSD, see LICENSE for details.
"""

__author__ = "Dominic Davis-Foster"
__copyright__ = "2020 Dominic Davis-Foster"

__license__ = "BSD"
__version__ = "0.1.1"
__email__ = "dominic@davis-foster.co.uk"

# stdlib
from typing import Any, Dict

# 3rd party
from sphinx.application import Sphinx

# this package
from sphinxcontrib.extras_require.directive import ExtrasRequireDirective
from sphinxcontrib.extras_require.sources import sources

# For type hinting install docutils-stubs


def purge_extras_requires(app: Sphinx, env, docname) -> None:
	if not hasattr(env, 'all_extras_requires'):
		return

	env.all_extras_requires = [
			extras_require for extras_require in env.all_extras_requires if extras_require['docname'] != docname
			]


def setup(app: Sphinx) -> Dict[str, Any]:
	"""
	Setup Sphinx Extension

	:param app:

	:return:
	"""

	# Location of package source directory relative to documentation source directory
	app.add_config_value('package_root', None, 'html')

	app.add_directive('extras-require', ExtrasRequireDirective)
	app.connect('env-purge-doc', purge_extras_requires)

	return {
			'version': __version__,
			'parallel_read_safe': True,
			'parallel_write_safe': True,
			}
