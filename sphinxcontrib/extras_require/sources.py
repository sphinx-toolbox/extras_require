#!/usr/bin/env python3
#
#  sources.py
"""
Supported sources for the requirements are implemented here.

.. TODO:: From .dist-info

**Data:**

.. autosummary::

	~sphinxcontrib.extras_require.sources.sources

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
import importlib.util
import inspect
import mimetypes
import pathlib
from typing import Callable, Dict, List, Tuple

# 3rd party
import sphinx.environment
from docutils.parsers.rst import directives
from domdf_python_tools.paths import PathPlus
from setuptools.config import read_configuration  # type: ignore[import]
from shippinglabel import normalize_keep_dot
from shippinglabel.requirements import combine_requirements, parse_pyproject_extras, read_requirements
from sphinx_toolbox.utils import flag

__all__ = [
		"requirements_from_file",
		"requirements_from_pkginfo",
		"requirements_from_setup_cfg",
		"requirements_from_flit",
		"requirements_from_pyproject",
		"sources",
		"Sources",
		]


class Sources(List[Tuple[str, Callable, Callable]]):
	"""
	Class to store functions that provide requirements sources.

	The syntax of each entry is::

		(option_name, getter_function, validator_function)

	* a string to use in the directive to specify the source to use,
	* the function that returns the list of additional requirements,
	* a function to validate the option value provided by the user.

	.. latex:clearpage::
	"""

	_args = ["package_root", "options", "env", "extra"]
	_directive_name = "extras_require"

	def register(
			self,
			option_name: str,
			validator: Callable = directives.unchanged,
			) -> Callable:
		"""
		Decorator to register a function.

		The function must have the following signature:

		.. code-block:: python

			def function(
				package_root: pathlib.Path,
				options: Dict,
				env: sphinx.environment.BuildEnvironment,
				extra: str,
				) -> List[str]: ...

		:param option_name: A string to use in the directive to specify the source to use.
		:param validator: A function to validate the option value provided by the user.

		:return: The registered function.

		:raises: :exc:`SyntaxError` if the decorated function does not take the correct arguments.
		"""

		def _decorator(function: Callable) -> Callable:
			signature = inspect.signature(function)

			if list(signature.parameters.keys()) != self._args:
				raise SyntaxError(
						"The decorated function must take only the following arguments: "
						"'package_root', 'options', 'env', and 'extra'"
						)

			self.append((option_name, function, validator))

			setattr(function, f"_{self._directive_name}_registered", True)

			return function

		return _decorator


#: Instance of :class:`~.Sources`.
sources = Sources()


@sources.register("file", directives.unchanged)
def requirements_from_file(
		package_root: pathlib.Path,
		options: Dict,
		env: sphinx.environment.BuildEnvironment,
		extra: str,
		) -> List[str]:
	"""
	Load requirements from the specified file.

	:param package_root: The path to the package root
	:param options:
	:param env:
	:param extra: The name of the "extra" that the requirements are for

	:return: List of requirements
	"""

	requirements_file = package_root / options["file"]

	if not requirements_file.is_file():
		raise FileNotFoundError(f"Cannot find requirements file '{requirements_file}'")

	mime_type = mimetypes.guess_type(str(requirements_file))[0]
	if not mime_type or not mime_type.startswith("text/"):
		raise ValueError(f"'{requirements_file}' is not a text file.")

	requirements, comments = read_requirements(
		requirements_file,
		normalize_func=normalize_keep_dot,
		)

	return list(map(str, sorted(combine_requirements(requirements))))


@sources.register("__pkginfo__", flag)
def requirements_from_pkginfo(
		package_root: pathlib.Path,
		options: Dict,
		env: sphinx.environment.BuildEnvironment,
		extra: str,
		) -> List[str]:
	"""
	Load requirements from a ``__pkginfo__.py`` file in the root of the repository.

	:param package_root: The path to the package root
	:param options:
	:param env:
	:param extra: The name of the "extra" that the requirements are for

	:return: List of requirements
	"""

	__pkginfo___file = PathPlus(env.srcdir).parent / "__pkginfo__.py"

	if not __pkginfo___file.is_file():
		raise FileNotFoundError(f"Cannot find __pkginfo__.py in '{__pkginfo___file.parent}'")

	try:
		spec = importlib.util.spec_from_file_location("__pkginfo__", str(__pkginfo___file))

		if spec is not None:
			__pkginfo__ = importlib.util.module_from_spec(spec)

			if spec.loader:
				spec.loader.exec_module(__pkginfo__)
				requirements = __pkginfo__.extras_require[extra]
				return requirements
				# TODO: handle extra not found

	except ValueError:
		pass

	raise ImportError("Could not import __pkginfo__.py")


requirements_from___pkginfo__ = requirements_from_pkginfo


@sources.register("setup.cfg", flag)
def requirements_from_setup_cfg(
		package_root: pathlib.Path,
		options: Dict,
		env: sphinx.environment.BuildEnvironment,
		extra: str,
		) -> List[str]:
	"""
	Load requirements from a ``setup.cfg`` file in the root of the repository.

	:param package_root: The path to the package root.
	:param options:
	:param env:
	:param extra: The name of the "extra" that the requirements are for.

	:return: List of requirements.
	"""

	setup_cfg_file = PathPlus(env.srcdir).parent / "setup.cfg"
	assert setup_cfg_file.is_file()

	setup_cfg = read_configuration(setup_cfg_file)

	if "options" in setup_cfg and "extras_require" in setup_cfg["options"]:
		if extra in setup_cfg["options"]["extras_require"]:
			return setup_cfg["options"]["extras_require"][extra]
		else:
			raise ValueError(f"'{extra}' not found in '[options.extras_require]'")
	else:
		raise ValueError("'options.extras_require' section not found in 'setup.cfg")


@sources.register("flit", flag)
def requirements_from_flit(
		package_root: pathlib.Path,
		options: Dict,
		env: sphinx.environment.BuildEnvironment,
		extra: str,
		) -> List[str]:
	"""
	Load requirements from the ``[tool.flit.metadata.requires-extra]`` section of
	a ``pyproject.toml`` file in the root of the repository.

	:param package_root: The path to the package root.
	:param options:
	:param env:
	:param extra: The name of the "extra" that the requirements are for.

	:return: List of requirements.
	"""  # noqa D400

	pyproject_file = PathPlus(env.srcdir).parent / "pyproject.toml"

	if not pyproject_file.is_file():
		raise FileNotFoundError(f"Cannot find pyproject.toml in '{pyproject_file.parent}'")

	flit_extras = parse_pyproject_extras(pyproject_file, flavour="flit", normalize_func=normalize_keep_dot)

	if extra not in flit_extras:
		raise ValueError(f"'{extra}' not found in '[tool.flit.metadata.requires-extra]'")

	requirements = flit_extras[extra]

	return list(map(str, sorted(combine_requirements(requirements))))


@sources.register("pyproject", flag)
def requirements_from_pyproject(
		package_root: pathlib.Path,
		options: Dict,
		env: sphinx.environment.BuildEnvironment,
		extra: str,
		) -> List[str]:
	"""
	Load requirements from the ``[project.optional-dependencies]`` section of
	a ``pyproject.toml`` file in the root of the repository.

	.. seealso:: :pep:`621` -- Storing project metadata in pyproject.toml

	.. versionadded:: 0.3.0

	:param package_root: The path to the package root.
	:param options:
	:param env:
	:param extra: The name of the "extra" that the requirements are for.

	:return: List of requirements.
	"""  # noqa D400

	pyproject_file = PathPlus(env.srcdir).parent / "pyproject.toml"

	if not pyproject_file.is_file():
		raise FileNotFoundError(f"Cannot find pyproject.toml in '{pyproject_file.parent}'")

	flit_extras = parse_pyproject_extras(pyproject_file, flavour="pep621", normalize_func=normalize_keep_dot)

	if extra not in flit_extras:
		raise ValueError(f"'{extra}' not found in '[project.optional-dependencies]'")

	requirements = flit_extras[extra]

	return list(map(str, sorted(combine_requirements(requirements))))
