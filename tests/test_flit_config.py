# stdlib
import tempfile

# 3rd party
import pytest
from domdf_python_tools.paths import PathPlus

# this package
from sphinxcontrib.extras_require.flit_config import ConfigError, read_flit_config


@pytest.mark.parametrize(
		"toml, missing",
		[
				(
						"""\
[tool.flit.metadata]
module = "FooBar"


[tool.flit.metadata.requires-extra]
test = [
	"pytest >=2.7.3",
	"pytest-cov",
]
doc = ["sphinx"]
""",
						"author"
						),
				(
						"""\
[tool.flit.metadata]
author = "Joe Bloggs"


[tool.flit.metadata.requires-extra]
test = [
	"pytest >=2.7.3",
	"pytest-cov",
]
doc = ["sphinx"]
""",
						"module"
						),
				]
		)
def test_missing_metadata(toml, missing):
	with tempfile.TemporaryDirectory() as tmpdir:
		tmpdir_p = PathPlus(tmpdir)

		(tmpdir_p / "pyproject.toml").write_text(toml)

		with pytest.raises(ConfigError, match=f"Required fields missing: {missing}"):
			read_flit_config(tmpdir_p / "pyproject.toml")


@pytest.mark.parametrize(
		"toml",
		[
				"""\
[tool.flit.metadata]
author = 1234
module = "FooBar"


[tool.flit.metadata.requires-extra]
test = [
	"pytest >=2.7.3",
	"pytest-cov",
]
doc = ["sphinx"]
""",
				]
		)
def test_wrong_types_str(toml):
	with tempfile.TemporaryDirectory() as tmpdir:
		tmpdir_p = PathPlus(tmpdir)

		(tmpdir_p / "pyproject.toml").write_text(toml)

		with pytest.raises(ConfigError, match=f"Expected a string for .* field, found"):
			read_flit_config(tmpdir_p / "pyproject.toml")


@pytest.mark.parametrize(
		"toml",
		[
				"""\
[tool.flit.metadata]
author = "Joe Bloggs"
module = "FooBar"
foo = 1234


[tool.flit.metadata.requires-extra]
test = [
	"pytest >=2.7.3",
	"pytest-cov",
]
doc = ["sphinx"]
""",
				"""\
[tool.flit.metadata]
author = "Joe Bloggs"
module = "FooBar"
dev-requres = "pytest; pytest-cov"
""",
				]
		)
def test_unknown_meta_key(toml):
	with tempfile.TemporaryDirectory() as tmpdir:
		tmpdir_p = PathPlus(tmpdir)

		(tmpdir_p / "pyproject.toml").write_text(toml)

		with pytest.raises(ConfigError, match=f"Unrecognised metadata key"):
			read_flit_config(tmpdir_p / "pyproject.toml")


def test_wrong_type_extras():
	with tempfile.TemporaryDirectory() as tmpdir:
		tmpdir_p = PathPlus(tmpdir)

		(tmpdir_p / "pyproject.toml").write_text(
				"""\
[tool.flit.metadata]
author = "Joe Bloggs"
module = "FooBar"


[tool.flit.metadata.requires-extra]
foo=123
bar=456
"""
				)

		with pytest.raises(ConfigError, match=f"Expected a dict of lists for requires-extra field"):
			read_flit_config(tmpdir_p / "pyproject.toml")

	with tempfile.TemporaryDirectory() as tmpdir:
		tmpdir_p = PathPlus(tmpdir)

		(tmpdir_p / "pyproject.toml").write_text(
				"""\
[tool.flit.metadata]
author = "Joe Bloggs"
module = "FooBar"


[tool.flit.metadata.requires-extra]
test = [
	1234,
	5678,
]
"""
				)

		with pytest.raises(ConfigError, match="Expected a string list for requires-extra"):
			read_flit_config(tmpdir_p / "pyproject.toml")


def test_bad_config():
	with tempfile.TemporaryDirectory() as tmpdir:
		tmpdir_p = PathPlus(tmpdir)

		(tmpdir_p / "pyproject.toml").write_text(
				"""\
[tool.poetry]
classifiers = [
    "Topic :: Software Development :: Build Tools",
    "Topic :: Software Development :: Libraries :: Python Modules"
]
"""
				)

		with pytest.raises(ConfigError, match="TOML file missing \\[tool.flit\\] table."):
			read_flit_config(tmpdir_p / "pyproject.toml")

	with tempfile.TemporaryDirectory() as tmpdir:
		tmpdir_p = PathPlus(tmpdir)

		(tmpdir_p / "pyproject.toml").write_text(
				"""\
[tool.flit.metadata]
author = "Joe Bloggs"
module = "FooBar"


[tool.flit.foo]
test = [
	1234,
	5678,
]
"""
				)

		with pytest.raises(ConfigError, match="Unknown sections"):
			read_flit_config(tmpdir_p / "pyproject.toml")

	with tempfile.TemporaryDirectory() as tmpdir:
		tmpdir_p = PathPlus(tmpdir)

		(tmpdir_p / "pyproject.toml").write_text("""\
[tool.flit.scripts]
flit = "flit:main"
""")

		with pytest.raises(ConfigError, match="\\[tool.flit.metadata\\] section is required"):
			read_flit_config(tmpdir_p / "pyproject.toml")


def test_dev_requires():
	with tempfile.TemporaryDirectory() as tmpdir:
		tmpdir_p = PathPlus(tmpdir)

		(tmpdir_p / "pyproject.toml").write_text(
				"""\
[tool.flit.metadata]
author = "Joe Bloggs"
module = "FooBar"
dev-requires = "pytest >=2.7.3; pytest-cov"


[tool.flit.metadata.requires-extra]
dev = [
    "pytest >=2.7.3",
	"pytest-cov",
	]
"""
				)

		with pytest.raises(
				ConfigError, match="dev-requires occurs together with its replacement requires-extra.dev."
				):
			read_flit_config(tmpdir_p / "pyproject.toml")

	with tempfile.TemporaryDirectory() as tmpdir:
		tmpdir_p = PathPlus(tmpdir)

		(tmpdir_p / "pyproject.toml").write_text(
				"""\
[tool.flit.metadata]
author = "Joe Bloggs"
module = "FooBar"
dev-requires = "pytest >=2.7.3; pytest-cov"
"""
				)

		extras = read_flit_config(tmpdir_p / "pyproject.toml").reqs_by_extra
		assert "dev" in extras
		assert extras["dev"] == "pytest >=2.7.3; pytest-cov"


@pytest.mark.parametrize("identifier", ["--???foo", "12--", "repo-helper", "py.test"])
def test_invalid_identifier(identifier):
	with tempfile.TemporaryDirectory() as tmpdir:
		tmpdir_p = PathPlus(tmpdir)

		(tmpdir_p / "pyproject.toml").write_text(
				f"""\
[tool.flit.metadata]
author = "Joe Bloggs"
module = "{identifier}"


[tool.flit.metadata.requires-extra]
test = [
	"pytest >=2.7.3",
	"pytest-cov",
]
doc = ["sphinx"]
""",
				)

		with pytest.raises(ConfigError, match=f"Module name .* is not a valid identifier"):
			read_flit_config(tmpdir_p / "pyproject.toml")
