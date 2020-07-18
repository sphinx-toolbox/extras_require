import pytest
import tempfile
import pathlib

from sphinxcontrib.extras_require.sources import requirements_from_setup_cfg


class MockBuildEnvironment:

	def __init__(self, tmpdir):
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
def test_from_setup_cfg(setup, extra, expects):
	with tempfile.TemporaryDirectory() as tmpdir:
		tmpdir_p = pathlib.Path(tmpdir)
		setup_cfg_file = tmpdir_p / "setup.cfg"
		setup_cfg_file.write_text(f"""\
[options.extras_require]
{setup}""")

		assert requirements_from_setup_cfg(
				package_root=None,
				options={},
				env=MockBuildEnvironment(tmpdir_p),
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
						"testing", ["faker", "pytest", "tox; python<=3.6"]
						),
				]
		)
def test_from_setup_cfg_errors(setup, extra, expects):
	with tempfile.TemporaryDirectory() as tmpdir:
		tmpdir_p = pathlib.Path(tmpdir)
		setup_cfg_file = tmpdir_p / "setup.cfg"
		setup_cfg_file.write_text(f"""\
[options.extras_require]
{setup}""")

		with pytest.raises(ValueError, match=f"'{extra}' not found in '\\[options.extras_require\\]'"):
			requirements_from_setup_cfg(
					package_root=None,
					options={},
					env=MockBuildEnvironment(tmpdir_p),
					extra=extra,
					)


def test_from_setup_cfg_missing_section():
	with tempfile.TemporaryDirectory() as tmpdir:
		tmpdir_p = pathlib.Path(tmpdir)
		setup_cfg_file = tmpdir_p / "setup.cfg"
		setup_cfg_file.write_text(f"""\
[metadata]
name = FooBar
author = Joe Bloggs
""")

		with pytest.raises(ValueError, match="'options.extras_require' section not found in 'setup.cfg"):
			requirements_from_setup_cfg(
					package_root=None,
					options={},
					env=MockBuildEnvironment(tmpdir_p),
					extra="docs",
					)
