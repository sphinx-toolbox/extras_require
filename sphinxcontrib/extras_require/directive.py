#!/usr/bin/env python3
"""
The "extras_require" directive.

:copyright: Copyright (c) 2020 by Dominic Davis-Foster <dominic@davis-foster.co.uk>
:license: BSD, see LICENSE for details.
"""

# stdlib
import pathlib
import textwrap
import warnings
from typing import List

# 3rd party
from docutils import nodes
from docutils.statemachine import ViewList
from packaging.requirements import InvalidRequirement, Requirement
from sphinx.util.docutils import SphinxDirective

# this package
from sphinxcontrib.extras_require.sources import sources


class ExtrasRequireDirective(SphinxDirective):
	"""
	Directive to show a notice to users that a module, class or	function has additional requirements.
	"""

	has_content: bool = True
	required_arguments: int = 1
	option_spec = {source[0]: source[2] for source in sources}  # type: ignore
	option_spec["scope"] = str

	def run(self) -> List[nodes.Node]:
		"""
		Create the extras_require node.

		:return:
		"""

		extra: str = self.arguments[0]

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

		requirements: List[str]

		for option_name, getter_function, validator_function in sources:
			if option_name in self.options:
				requirements = getter_function(package_root, self.options, self.env, extra)
				break
		else:
			if self.content:
				requirements = list(self.content)
			else:
				raise ValueError("Please specify a source for the extra requirements")

		if not requirements:
			warnings.warn("No requirements specified! No notice will be shown in the documentation.")
			return [targetnode]

		valid_requirements = validate_requirements(requirements)

		content = make_node_content(valid_requirements, self.env.config.project, extra, scope=scope)
		view = ViewList(content.split("\n"))

		extras_require_node = nodes.attention(rawsource=content)
		self.state.nested_parse(view, self.content_offset, extras_require_node)  # type: ignore

		if not hasattr(self.env, "all_extras_requires"):
			self.env.all_extras_requires = []  # type: ignore

		self.env.all_extras_requires.append({  # type: ignore
			"docname": self.env.docname,
			"lineno": self.lineno,
			"extras_require": extras_require_node.deepcopy(),
			"target": targetnode,
			})

		return [targetnode, extras_require_node]


def validate_requirements(requirements_list: List[str]) -> List[str]:
	"""
	Validate a list of :pep:`508` requirements and format them consistently.

	:param requirements_list: List of :pep:`508` requirements.

	:return: List of :pep:`508` requirements with consistent formatting.

	:raises: Value error if one of the requirements is invalid, or if no requirements are supplied (i.e. an empty list).
	"""

	valid_requirements = []

	for req in requirements_list:
		if req:
			try:
				valid_requirements.append(str(Requirement(req)))
			except InvalidRequirement as e:
				raise ValueError(f"Invalid requirement '{req}': {str(e)}") from None

	if not valid_requirements:
		raise ValueError("Please supply at least one requirement.")

	return valid_requirements


def make_node_content(
		requirements: List[str],
		package_name: str,
		extra: str,
		scope: str = "module",
		) -> str:
	"""
	Create the content of an extras_require node.

	:param requirements: List of additional :pep:`508` requirements.
	:param package_name: The name of the module/package on PyPI.
	:type package_name: str
	:param extra: The name of the "extra".
	:type extra: str
	:param scope: The scope of the additional requirements, e.g. ``"module"``, ``"package"``.
	:type scope: str

	:return: The content of an extras_require node.
	:rtype:
	"""

	requirements_string = textwrap.indent("\n".join(requirements), "    ")

	content = f"""\
This {scope} has the following additional requirement{'s' if len(requirements) > 1 else ''}:

.. code-block:: text

{requirements_string}

These can be installed as follows:

	.. code-block:: bash

		$ python -m pip install {package_name}[{extra}]

"""

	content = content.replace("\t", "    ")

	return content
