#!/usr/bin/env python3
#
#  __init__.py
"""
Supported sources for the requirements are implemented here.
"""
#
#  Copyright © 2020 Dominic Davis-Foster <dominic@davis-foster.co.uk>
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
from typing import Any, Callable, Dict, List, Tuple

# 3rd party
import sphinx.environment
from docutils.parsers.rst import directives
from domdf_python_tools.paths import PathPlus
from setuptools.config import read_configuration  # type: ignore

# this package
from sphinxcontrib.extras_require.flit_config import read_flit_config

__all__ = [
		"requirements_from_file",
		"requirements_from___pkginfo__",
		"requirements_from_setup_cfg",
		"requirements_from_flit",
		"flag",
		"sources",
		"Sources",
		]


class Sources(List[Tuple[str, Callable, Callable]]):
	"""
	Class to store functions that provide requirements sources.

	The syntax of each entry is:

	``(option_name, getter_function, validator_function)``

	* a string to use in the directive to specify the source to use,
	* the function that returns the list of additional requirements,
	* a function to validate the option value provided by the user.
	"""

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

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


def flag(argument: Any) -> bool:
	"""
	Check for a valid flag option (no argument) and return :py:obj:`True`.

	:raises: :exc:`ValueError` if an argument is given.
	"""

	if argument and argument.strip():
		raise ValueError(f'No argument is allowed; "{argument}" supplied')
	else:
		return True


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

	requirements = [x for x in requirements_file.read_text().split('\n') if x and not x.startswith('#')]

	return requirements


@sources.register("__pkginfo__", flag)
def requirements_from___pkginfo__(
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
				spec.loader.exec_module(__pkginfo__)  # type: ignore
				requirements = __pkginfo__.extras_require[extra]  # type: ignore
				return requirements
				# TODO: handle extra not found

	except ValueError:
		pass

	raise ImportError("Could not import __pkginfo__.py")


@sources.register("setup.cfg", flag)
def requirements_from_setup_cfg(
		package_root: pathlib.Path,
		options: Dict,
		env: sphinx.environment.BuildEnvironment,
		extra: str,
		) -> List[str]:
	"""
	Load requirements from a ``setup.cfg`` file in the root of the repository.

	:param package_root: The path to the package root
	:param options:
	:param env:
	:param extra: The name of the "extra" that the requirements are for

	:return: List of requirements
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
	a pyproject.toml file in the root of the repository.

	:param package_root: The path to the package root
	:param options:
	:param env:
	:param extra: The name of the "extra" that the requirements are for

	:return: List of requirements
	"""  # noqa D400

	pyproject_file = PathPlus(env.srcdir).parent / "pyproject.toml"

	if not pyproject_file.is_file():
		raise FileNotFoundError(f"Cannot find pyproject.toml in '{pyproject_file.parent}'")

	flit_extras = read_flit_config(pyproject_file).reqs_by_extra

	if extra in flit_extras:
		return flit_extras[extra]
	else:
		raise ValueError(f"'{extra}' not found in '[tool.flit.metadata.requires-extra]'")
