import pytest
import tempfile
import pathlib

from sphinxcontrib.extras_require.sources import requirements_from_flit


class MockBuildEnvironment:

	def __init__(self, tmpdir):
		self.srcdir = tmpdir / "docs"


@pytest.mark.parametrize(
		"toml, extra, expects",
		[
				(
						"""\
extra_c = [
    "faker",
    "pytest",
    "tox; python<=3.6",
]
""",
						"extra_c", ["faker", "pytest", "tox; python<=3.6"]
						),
				(
						"""\
test = [
    "pytest >=2.7.3",
    "pytest-cov",
]
doc = ["sphinx"]
""",
						"test", ["pytest >=2.7.3", "pytest-cov"]
						),
				]
		)
def test_from_flit(toml, extra, expects):
	with tempfile.TemporaryDirectory() as tmpdir:
		tmpdir_p = pathlib.Path(tmpdir)
		pyproject_file = tmpdir_p / "pyproject.toml"
		pyproject_file.write_text(
				f"""\
[tool.flit.metadata]
author = "Joe Bloggs"
module = "FooBar"


[tool.flit.metadata.requires-extra]
{toml}"""
				)

		assert requirements_from_flit(
				package_root=None,
				options={},
				env=MockBuildEnvironment(tmpdir_p),
				extra=extra,
				) == expects


@pytest.mark.parametrize(
		"toml, extra, expects",
		[
				(
						"""\
extra_c = [
    "faker",
    "pytest",
    "tox; python<=3.6",
]
""",
						"extra", ["faker", "pytest", "tox; python<=3.6"]
						),
				(
						"""\
test = [
    "pytest >=2.7.3",
    "pytest-cov",
]
doc = ["sphinx"]
""",
						"testing", ["pytest >=2.7.3", "pytest-cov"]
						),
				]
		)
def test_from_flit_errors(toml, extra, expects):
	with tempfile.TemporaryDirectory() as tmpdir:
		tmpdir_p = pathlib.Path(tmpdir)
		pyproject_file = tmpdir_p / "pyproject.toml"
		pyproject_file.write_text(
				f"""\
[tool.flit.metadata]
author = "Joe Bloggs"
module = "FooBar"


[tool.flit.metadata.requires-extra]
{toml}"""
				)

		with pytest.raises(ValueError, match=f"'{extra}' not found in '\\[tool.flit.metadata.requires-extra\\]"):
			requirements_from_flit(
					package_root=None,
					options={},
					env=MockBuildEnvironment(tmpdir_p),
					extra=extra,
					)
