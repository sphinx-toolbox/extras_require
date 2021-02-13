# stdlib
import pathlib
import tempfile

# 3rd party
import pytest
from domdf_python_tools.paths import PathPlus

# this package
from sphinxcontrib.extras_require.sources import requirements_from_pyproject


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
    'tox; python_version <= "3.6"',
]
""",
						"extra_c", ["faker", "pytest", 'tox; python_version <= "3.6"']
						),
				(
						"""\
test = [
    "pytest >=2.7.3",
    "pytest-cov",
]
doc = ["sphinx"]
""",
						"test", ["pytest>=2.7.3", "pytest-cov"]
						),
				]
		)
def test_from_pyproject(toml, extra, expects):
	with tempfile.TemporaryDirectory() as tmpdir:
		tmpdir_p = pathlib.Path(tmpdir)
		pyproject_file = tmpdir_p / "pyproject.toml"
		pyproject_file.write_text(f"""\
[project.optional-dependencies]
{toml}""")

		assert requirements_from_pyproject(
				package_root=pathlib.Path('.'),
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
def test_from_pyproject_errors(toml, extra, expects):
	with tempfile.TemporaryDirectory() as tmpdir:
		tmpdir_p = PathPlus(tmpdir)
		pyproject_file = tmpdir_p / "pyproject.toml"
		pyproject_file.write_text(f"""\
[project.optional-dependencies]
{toml}""")

		with pytest.raises(ValueError, match=f"'{extra}' not found in '\\[project.optional-dependencies\\]"):
			requirements_from_pyproject(
					package_root=pathlib.Path('.'),
					options={},
					env=MockBuildEnvironment(tmpdir_p),
					extra=extra,
					)

		with pytest.raises(FileNotFoundError, match=f"Cannot find pyproject.toml in"):
			requirements_from_pyproject(
					package_root=pathlib.Path('.'),
					options={},
					env=MockBuildEnvironment(pathlib.Path("/home/user/demo")),
					extra=extra,
					)
