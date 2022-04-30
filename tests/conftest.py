# stdlib
import sys
from typing import Any, Iterator

# 3rd party
import pytest
from bs4 import BeautifulSoup  # type: ignore[import]
from domdf_python_tools.paths import PathPlus

if sys.version_info >= (3, 10):
	# stdlib
	import types
	types.Union = types.UnionType

# 3rd party
from sphinx.application import Sphinx
from sphinx.testing.path import path

pytest_plugins = ("coincidence", "sphinx.testing.fixtures", "sphinx_toolbox.testing")


@pytest.fixture(scope="session")
def rootdir() -> path:
	rdir = PathPlus(__file__).parent.absolute() / "doc-test"
	(rdir / "test-root").maybe_make(parents=True)
	return path(rdir)


@pytest.fixture()
def the_app(app: Sphinx) -> Sphinx:
	fake_repo_root = PathPlus(app.env.srcdir).parent  # type: ignore[union-attr]

	PathPlus(fake_repo_root / "__pkginfo__.py").write_lines([
			"extras_require = {",
			"\t\t'extra_b': [",
			'\t\t\t\t"flask >=1.1.2",',
			'\t\t\t\t"click < 7.1.2",',
			'\t\t\t\t"sphinx ==3.0.3",',
			"\t\t\t\t]",
			"\t\t}",
			])

	PathPlus(fake_repo_root / "pyproject.toml").write_lines([
			"[tool.flit.metadata]",
			'author = "Joe Bloggs"',
			'module = "FooBar"',
			'',
			"[tool.flit.metadata.requires-extra]",
			"test = [",
			'\t"pytest >=2.7.3",',
			'\t"pytest-cov",',
			']',
			'doc = ["sphinx"]',
			'',
			"[project.optional-dependencies]",
			"test = [",
			'\t"pytest >=2.7.3",',
			'\t"pytest-cov",',
			']',
			'doc = ["sphinx"]',
			])

	(fake_repo_root / "setup.cfg").write_lines([
			"[options.extras_require]",
			"extra_c = faker; pytest; tox",
			])

	subpackage = fake_repo_root / "dummy_package" / "subpackage"
	if not subpackage.is_dir():
		subpackage.mkdir(parents=True)

	(subpackage / "requirements.txt").write_lines([
			"# a comment",
			"numpy>=1.18.4",
			"scipy==1.4.1",
			"# Old scipy version",
			"# scipy==1.3.0",
			"pandas>=0.25.0, !=1.0.0",
			])

	(fake_repo_root / "dummy_package" / "empty_requirements.txt").write_lines([
			"# a comment",
			"# numpy>=1.18.4",
			"# scipy==1.4.1",
			"# pandas>=0.25.0, !=1.0.0",
			])

	return app


@pytest.fixture()
def content(the_app: Sphinx) -> Iterator[Sphinx]:
	the_app.build(force_all=True)
	yield the_app


@pytest.fixture()
def page(content: Any, request: Any) -> Iterator[BeautifulSoup]:
	pagename = request.param
	c = (content.outdir / pagename).read_text()

	yield BeautifulSoup(c, "html5lib")
