#!/usr/bin/env python3
#
#  __init__.py
"""
The :rst:dir:`extras-require` directive.
"""
#
#  Copyright © 2020-2021 Dominic Davis-Foster <dominic@davis-foster.co.uk>
#
#  Redistribution and use in source and binary forms, with or without modification,
#  are permitted provided that the following conditions are met:
#
#      * Redistributions of source code must retain the above copyright notice,
#        this list of conditions and the following disclaimer.
#      * Redistributions in binary form must reproduce the above copyright notice,
#        this list of conditions and the following disclaimer in the documentation
#        and/or other materials provided with the distribution.
#
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
#  "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
#  LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
#  A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER
#  OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
#  EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
#  PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
#  PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
#  LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
#  NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
#  SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

# stdlib
from typing import Any, Dict, Iterable, List, Union

# 3rd party
import docutils
from docutils import nodes
from docutils.statemachine import ViewList
from domdf_python_tools.paths import PathPlus
from domdf_python_tools.stringlist import StringList
from domdf_python_tools.words import Plural
from packaging.requirements import InvalidRequirement
from shippinglabel.requirements import ComparableRequirement
from sphinx.environment import BuildEnvironment
from sphinx.util.docutils import SphinxDirective

# this package
from sphinxcontrib.extras_require.purger import extras_require_purger
from sphinxcontrib.extras_require.sources import sources

__all__ = ["ExtrasRequireDirective", "validate_requirements", "make_node_content", "get_requirements"]

_requirement = Plural("requirement", "requirements")


class ExtrasRequireDirective(SphinxDirective):
	"""
	Directive to show a notice to users that a module, class or function has additional requirements.
	"""

	has_content: bool = True

	#: One argument is required, the name of the extra (e.g. "testing", "docs")
	required_arguments: int = 1

	option_spec = {source[0]: source[2] for source in sources}
	option_spec["scope"] = str

	def _problematic(self, message: str) -> List[docutils.nodes.Node]:  # docutils.nodes.Node
		"""
		Reports an error while processing the directive.

		:param message:
		"""

		msg = self.state.reporter.warning(message, line=self.lineno)
		prob_node = docutils.nodes.problematic(self.block_text, self.block_text, msg)
		return [prob_node]

	def run(self) -> List[nodes.Node]:
		"""
		Create the extras_require node.
		"""

		extra: str = self.arguments[0]

		targetid = f'extras_require-{self.env.new_serialno("extras_require"):d}'
		targetnode = nodes.target('', '', ids=[targetid])

		valid_requirements = get_requirements(
				env=self.env,
				extra=extra,
				options=self.options,
				content=self.content,
				)

		if not valid_requirements:
			return self._problematic("No requirements specified! No notice will be shown in the documentation.")

		scope = self.options.get("scope", "module")

		pypi_name = self.env.config.pypi_name or self.env.config.project
		content = make_node_content(valid_requirements, pypi_name, extra, scope=scope)
		view = ViewList(content.split('\n'))

		extras_require_node = nodes.attention(rawsource=content)
		self.state.nested_parse(view, self.content_offset, extras_require_node)  # type: ignore[arg-type]

		extras_require_purger.add_node(self.env, extras_require_node, targetnode, self.lineno)

		return [targetnode, extras_require_node]


def validate_requirements(requirements_list: List[str]) -> List[str]:
	"""
	Validate a list of :pep:`508` requirements and format them consistently.

	:param requirements_list: List of :pep:`508` requirements.

	:return: List of :pep:`508` requirements with consistent formatting.
	"""

	valid_requirements = []

	for req in requirements_list:
		if req:
			try:
				valid_requirements.append(ComparableRequirement(req))
			except (InvalidRequirement, DeprecationWarning) as e:
				# Deprecation warning due to LegacyVersion or LegacySpecifier
				raise ValueError(f"Invalid requirement '{req}': {str(e)}") from None

	valid_requirements.sort()

	return [str(x) for x in valid_requirements]


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
	:param extra: The name of the "extra".
	:param scope: The scope of the additional requirements, e.g. ``"module"``, ``"package"``.

	:return: The content of an extras_require node.
	"""

	content = StringList(convert_indents=True)
	content.indent_type = ' ' * 4
	content.append(f"This {scope} has the following additional {_requirement(len(requirements))}:")
	content.blankline(ensure_single=True)

	with content.with_indent_size(content.indent_size + 1):
		content.append(".. code-block:: text")
		content.blankline(ensure_single=True)

		with content.with_indent_size(content.indent_size + 1):
			content.extend(requirements)

	content.blankline(ensure_single=True)

	if len(requirements) > 1:
		content.append("These can be installed as follows:")
	else:
		content.append("This can be installed as follows:")

	content.blankline(ensure_single=True)

	with content.with_indent_size(content.indent_size + 1):
		content.append(".. prompt:: bash")
		content.blankline(ensure_single=True)

		with content.with_indent_size(content.indent_size + 1):
			content.append(f"python -m pip install {package_name}[{extra}]")

	content.blankline(ensure_single=True)
	content.blankline()

	return str(content)


def get_requirements(
		env: BuildEnvironment,
		extra: str,
		options: Dict[str, Any],
		content: Union[Iterable, ViewList],
		) -> List[str]:
	"""
	Get the requirements for the extras_require node.

	:param env:
	:param extra:
	:param options:
	:param content:
	"""

	n_sources = 0

	if list(content):
		n_sources += 1

	for source in sources:
		if (source[0] in options) and options[source[0]]:
			n_sources += 1

	if n_sources > 1:
		raise ValueError("Please specify only one source for the extra requirements")
	elif n_sources == 0:
		raise ValueError(f"Please specify a source for the extra requirements {extra}")

	if env.config.package_root is None:
		raise ValueError("Please provide a value for 'package_root' in conf.py")

	src_dir = PathPlus(env.srcdir)
	package_root = src_dir.parent / env.config.package_root

	requirements: List[str]

	for option_name, getter_function, validator_function in sources:
		if option_name in options:
			requirements = getter_function(package_root, options, env, extra)
			break
	else:
		requirements = list(content)

	valid_requirements = validate_requirements(requirements)

	return valid_requirements
