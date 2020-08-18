#!/usr/bin/env python3
"""
Supported sources for the requirements are implemented here.

:copyright: Copyright (c) 2020 by Dominic Davis-Foster <dominic@davis-foster.co.uk>
:license: BSD, see LICENSE for details.
"""

# stdlib
import importlib.util
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


def requirements_from_file(
		package_root: pathlib.Path,
		options: Dict,
		env: sphinx.environment.BuildEnvironment,
		extra: str,
		) -> List[str]:
	"""
	Load requirements from the specified file.

	:param package_root: The path to the package root
	:type package_root:
	:param options:
	:type options: dict
	:param env:
	:param extra: The name of the "extra" that the requirements are for
	:type extra: str

	:return: List of requirements
	"""

	requirements_file = package_root / options["file"]

	if not requirements_file.is_file():
		raise FileNotFoundError(f"Cannot find requirements file '{requirements_file}'")

	mime_type = mimetypes.guess_type(str(requirements_file))[0]
	if not mime_type or not mime_type.startswith("text/"):
		raise ValueError(f"'{requirements_file}' is not a text file.")

	requirements = [x for x in requirements_file.read_text().split("\n") if x and not x.startswith("#")]

	return requirements


def requirements_from___pkginfo__(
		package_root: pathlib.Path,
		options: Dict,
		env: sphinx.environment.BuildEnvironment,
		extra: str,
		) -> List[str]:
	"""
	Load requirements from a __pkginfo__.py file in the root of the repository.

	:param package_root: The path to the package root
	:type package_root:
	:param options:
	:type options: dict
	:param env:
	:param extra: The name of the "extra" that the requirements are for
	:type extra: str

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


def requirements_from_setup_cfg(
		package_root: pathlib.Path,
		options: Dict,
		env: sphinx.environment.BuildEnvironment,
		extra: str,
		) -> List[str]:
	"""
	Load requirements from a setup.cfg file in the root of the repository.

	:param package_root: The path to the package root
	:type package_root:
	:param options:
	:type options: dict
	:param env:
	:param extra: The name of the "extra" that the requirements are for
	:type extra: str

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


def requirements_from_flit(
		package_root: pathlib.Path,
		options: Dict,
		env: sphinx.environment.BuildEnvironment,
		extra: str,
		) -> List[str]:
	"""
	Load requirements from the [tool.flit.metadata.requires-extra] section of
	a pyproject.toml file in the root of the repository.

	:param package_root: The path to the package root.
	:type package_root:
	:param options:
	:type options: dict
	:param env:
	:param extra: The name of the "extra" that the requirements are for
	:type extra: str

	:return: List of requirements
	"""

	pyproject_file = PathPlus(env.srcdir).parent / "pyproject.toml"

	if not pyproject_file.is_file():
		raise FileNotFoundError(f"Cannot find pyproject.toml in '{pyproject_file.parent}'")

	flit_extras = read_flit_config(pyproject_file).reqs_by_extra

	if extra in flit_extras:
		return flit_extras[extra]
	else:
		raise ValueError(f"'{extra}' not found in '[tool.flit.metadata.requires-extra]'")


def flag(argument: Any) -> bool:
	"""
	Check for a valid flag option (no argument) and return ``True``.

	Raise ``ValueError`` if an argument is given.
	"""

	if argument and argument.strip():
		raise ValueError(f'No argument is allowed; "{argument}" supplied')
	else:
		return True


sources: List[Tuple[str, Callable, Callable]] = [
		# (option_name, getter_function, validator_function),
		("__pkginfo__", requirements_from___pkginfo__, flag),
		("file", requirements_from_file, directives.unchanged),
		("setup.cfg", requirements_from_setup_cfg, flag),
		("flit", requirements_from_flit, flag),
		]
