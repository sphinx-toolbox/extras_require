#!/usr/bin/env python3
# -*- coding: utf-8 -*-
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
__version__ = "0.1.0"
__email__ = "dominic@davis-foster.co.uk"

# stdlib
import configparser
import importlib.util
import mimetypes
import pathlib
import textwrap
import warnings
from typing import Any, Dict

# 3rd party
from docutils import nodes
from docutils.parsers.rst import directives
from docutils.statemachine import ViewList
from sphinx.application import Sphinx
from sphinx.util.docutils import SphinxDirective


def requirements_from_file(package_root, options, env, extra):
	"""
	Load requirements from the specified file.

	:param package_root: The path to the package root
	:type package_root:
	:param options:
	:type options: dict
	:param env:
	:type env: sphinx.environment.BuildEnvironment
	:param extra: The name of the "extra" that the requirements are for
	:type extra: str

	:return: List of requirements
	:rtype: List[str]
	"""

	requirements_file = package_root / options["file"]

	assert requirements_file.is_file()
	assert mimetypes.guess_type(str(requirements_file))[0].startswith("text/")

	requirements = requirements_file.read_text().split("\n")

	return requirements


def requirements_from___pkginfo__(package_root, options, env, extra):
	"""
	Load requirements from a __pkginfo__.py file in the root of the repository.

	:param package_root: The path to the package root
	:type package_root:
	:param options:
	:type options: dict
	:param env:
	:type env: sphinx.environment.BuildEnvironment
	:param extra: The name of the "extra" that the requirements are for
	:type extra: str

	:return: List of requirements
	:rtype: List[str]
	"""

	__pkginfo___file = pathlib.Path(env.srcdir).parent / "__pkginfo__.py"
	assert __pkginfo___file.is_file()
	assert mimetypes.guess_type(str(__pkginfo___file))[0].startswith("text/")

	spec = importlib.util.spec_from_file_location("__pkginfo__", str(__pkginfo___file))
	__pkginfo__ = importlib.util.module_from_spec(spec)
	spec.loader.exec_module(__pkginfo__)
	requirements = __pkginfo__.extras_require[extra]

	return requirements


def requirements_from_setup_cfg(package_root, options, env, extra):
	"""
	Load requirements from a setup.cfg file in the root of the repository.

	:param package_root: The path to the package root
	:type package_root:
	:param options:
	:type options: dict
	:param env:
	:type env: sphinx.environment.BuildEnvironment
	:param extra: The name of the "extra" that the requirements are for
	:type extra: str

	:return: List of requirements
	:rtype: List[str]
	"""

	setup_cfg_file = pathlib.Path(env.srcdir).parent / "setup.cfg"
	assert setup_cfg_file.is_file()

	setup_cfg = configparser.ConfigParser()
	setup_cfg.read(setup_cfg_file)

	if "options.extras_require" in setup_cfg:
		raw_requirements = dict(setup_cfg["options.extras_require"])[extra]
		requirements = [x.strip() for x in raw_requirements.split(";")]
		return requirements
	else:
		raise ValueError("'options.extras_require' section not found in 'setup.cfg")


sources = [
		# (option_name, getter_function, validator_function),
		("__pkginfo__", requirements_from___pkginfo__, bool),
		("file", requirements_from_file, directives.unchanged),
		("setup.cfg", requirements_from_setup_cfg, bool),
		]


class ExtrasRequireDirective(SphinxDirective):
	"""
	Directive to show a notice to users that a module, class or
	function has additional requirements.
	"""

	has_content = True
	required_arguments = 1
	option_spec = {source[0]: source[2] for source in sources}
	option_spec["scope"] = str

	def run(self):

		extra = self.arguments[0]

		if all(source[0] in self.options for source in sources) and self.content:
			raise ValueError("Please specify only one source for the extra requirements")

		if "scope" in self.options:
			scope = self.options["scope"]
		else:
			scope = "module"

		targetid = f'extras_require-{self.env.new_serialno("extras_require"):d}'
		targetnode = nodes.target('', '', ids=[targetid])

		src_dir = pathlib.Path(self.env.srcdir)
		package_root = src_dir.parent / self.env.config.package_root

		for option_name, getter_function, validator_function in sources:
			if option_name in self.options:
				requirements = getter_function(package_root, self.options, self.env, extra)
				break
		else:
			if self.content:
				requirements = self.content
			else:
				raise ValueError("Please specify a source for the extra requirements")

		if not requirements:
			warnings.warn("No requirements specified! No notice will be shown in the documentation.")
			return [targetnode]

		requirements = "\n".join(requirements)

		content = f"""\
This {scope} has the following additional requirements:

::

{textwrap.indent(requirements, "    ")}

These can be installed as follows:

	.. code-block:: bash

		$ python -m pip install {self.env.config.project}[{extra}]

"""
		content = content.replace("\t", "    ")
		view = ViewList(content.split("\n"))

		extras_require_node = nodes.attention(rawsource=content)
		self.state.nested_parse(view, self.content_offset, extras_require_node)

		if not hasattr(self.env, 'all_extras_requires'):
			self.env.all_extras_requires = []

		self.env.all_extras_requires.append({
				'docname': self.env.docname,
				'lineno': self.lineno,
				'extras_require': extras_require_node.deepcopy(),
				'target': targetnode,
				})

		return [targetnode, extras_require_node]


def purge_extras_requires(app, env, docname):
	if not hasattr(env, 'all_extras_requires'):
		return

	env.all_extras_requires = [
			extras_require for extras_require in env.all_extras_requires if extras_require['docname'] != docname
			]


def setup(app: Sphinx) -> Dict[str, Any]:
	"""
	Setup Sphinx Extension

	:param app:
	:type app: Sphinx

	:return:
	:rtype: dict
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
