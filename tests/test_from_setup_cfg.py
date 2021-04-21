# stdlib
import pathlib
from typing import List

# 3rd party
import pytest
from domdf_python_tools.paths import PathPlus

# this package
from sphinxcontrib.extras_require.sources import requirements_from_setup_cfg


class MockBuildEnvironment:

	def __init__(self, tmpdir: pathlib.Path):
		self.srcdir = tmpdir / "docs"


@pytest.mark.parametrize(
		"setup, extra, expects",
		[
				("extra_c = faker; pytest; tox", "extra_c", ["faker", "pytest", "tox"]),
				(
						"""\
extra_c =
    faker
    pytest
    tox; python<=3.6
""",
						"extra_c", ["faker", "pytest", "tox; python<=3.6"]
						),
				]
		)
def test_from_setup_cfg(
		tmp_pathplus: PathPlus,
		setup: str,
		extra: str,
		expects: List[str],
		):
	setup_cfg_file = tmp_pathplus / "setup.cfg"
	setup_cfg_file.write_text(f"""\
[options.extras_require]
{setup}""")

	assert requirements_from_setup_cfg(
			package_root=PathPlus(),
			options={},
			env=MockBuildEnvironment(tmp_pathplus),
			extra=extra,
			) == expects


@pytest.mark.parametrize(
		"setup, extra, expects",
		[
				("extra_c = faker; pytest; tox", "extra", ["faker", "pytest", "tox"]),
				(
						"""\
extra_c =
    faker
    pytest
    tox; python<=3.6
""",
						"test", ["faker", "pytest", "tox; python<=3.6"]
						),
				]
		)
def test_from_setup_cfg_errors(
		tmp_pathplus: PathPlus,
		setup: str,
		extra: str,
		expects: List[str],
		):
	setup_cfg_file = tmp_pathplus / "setup.cfg"
	setup_cfg_file.write_text(f"""\
[options.extras_require]
{setup}""")

	with pytest.raises(ValueError, match=f"'{extra}' not found in '\\[options.extras_require\\]'"):
		requirements_from_setup_cfg(
				package_root=PathPlus(),
				options={},
				env=MockBuildEnvironment(tmp_pathplus),
				extra=extra,
				)


def test_from_setup_cfg_missing_section(tmp_pathplus: PathPlus):
	setup_cfg_file = tmp_pathplus / "setup.cfg"
	setup_cfg_file.write_text(f"""\
[metadata]
name = FooBar
author = Joe Bloggs
""")

	with pytest.raises(ValueError, match="'options.extras_require' section not found in 'setup.cfg"):
		requirements_from_setup_cfg(
				package_root=PathPlus(),
				options={},
				env=MockBuildEnvironment(tmp_pathplus),
				extra="docs",
				)
