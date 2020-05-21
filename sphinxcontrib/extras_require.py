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
__version__ = "0.0.2"
__email__ = "dominic@davis-foster.co.uk"


# stdlib
import mimetypes
import pathlib
import textwrap
from typing import Any, Dict

# 3rd party
from docutils import nodes
from docutils.parsers.rst import directives
from docutils.statemachine import ViewList
from sphinx.application import Sphinx
from sphinx.util.docutils import SphinxDirective


class ExtrasRequireDirective(SphinxDirective):
	# this enables content in the directive
	has_content = True
	option_spec = {
			'file': directives.unchanged_required,
			'extra': directives.unchanged_required,
			}

	def run(self):
		targetid = f'extras_require-{self.env.new_serialno("extras_require"):d}'
		targetnode = nodes.target('', '', ids=[targetid])

		src_dir = pathlib.Path(self.env.srcdir)
		package_root = src_dir.parent / self.env.config.package_root
		requirements_file = package_root / self.options["file"]

		assert mimetypes.guess_type(str(requirements_file))[0].startswith("text/")

		requirements = requirements_file.read_text()

		content = f"""\
This module has the following additional requirements:

::

{textwrap.indent(requirements, "    ")}

These can be installed as follows:

	.. code-block:: bash

		$ python -m pip install {self.env.config.project}[{self.options["extra"]}]

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
			extras_require for extras_require in env.all_extras_requires
			if extras_require['docname'] != docname
			]


def setup(app: Sphinx) -> Dict[str, Any]:

	# Location of package source directory relative to documentation source directory
	app.add_config_value('package_root', None, 'html')

	app.add_directive('extras-require', ExtrasRequireDirective)
	app.connect('env-purge-doc', purge_extras_requires)

	return {
			'version': __version__,
			'parallel_read_safe': True,
			'parallel_write_safe': True,
			}
