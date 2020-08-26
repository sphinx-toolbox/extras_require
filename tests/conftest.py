"""
	pytest config for sphinxcontrib/extras_require/tests
	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

	:copyright: Copyright 2020 by Dominic Davis-Foster <dominic@davis-foster.co.uk>
	:license: BSD, see LICENSE for details.
"""

# 3rd party
import pytest
from bs4 import BeautifulSoup  # type: ignore
from domdf_python_tools.paths import PathPlus
from sphinx.testing.path import path

pytest_plugins = "sphinx.testing.fixtures"


@pytest.fixture(scope="session")
def rootdir():
	rdir = PathPlus(__file__).parent.absolute() / "doc-test"
	(rdir / "test-root").maybe_make(parents=True)
	return path(rdir)


@pytest.fixture()
def the_app(app):
	fake_repo_root = PathPlus(app.env.srcdir).parent

	PathPlus(fake_repo_root / "__pkginfo__.py").write_text(
			"""\
extras_require = {
		'extra_b': [
				"flask >=1.1.2",
				"click < 7.1.2",
				"sphinx ==3.0.3",
				]
		}
"""
			)

	PathPlus(fake_repo_root / "pyproject.toml").write_text(
			"""\
[tool.flit.metadata]
author = "Joe Bloggs"
module = "FooBar"


[tool.flit.metadata.requires-extra]
test = [
	"pytest >=2.7.3",
	"pytest-cov",
]
doc = ["sphinx"]
"""
			)

	(fake_repo_root / "setup.cfg").write_text("""\
[options.extras_require]
extra_c = faker; pytest; tox
""")

	subpackage = fake_repo_root / "dummy_package" / "subpackage"
	if not subpackage.is_dir():
		subpackage.mkdir(parents=True)

	(subpackage / "requirements.txt").write_text(
			"""\
# a comment
numpy>=1.18.4
scipy==1.4.1
# Old scipy version
# scipy==1.3.0
pandas>=0.25.0, !=1.0.0
"""
			)

	(fake_repo_root / "dummy_package" / "empty_requirements.txt"
		).write_text("""\
# a comment
# numpy>=1.18.4
# scipy==1.4.1
# pandas>=0.25.0, !=1.0.0
""")

	return app


@pytest.fixture()
def content(the_app):
	the_app.build(force_all=True)
	yield the_app


@pytest.fixture()
def page(content, request) -> BeautifulSoup:
	pagename = request.param
	c = (content.outdir / pagename).read_text()

	yield BeautifulSoup(c, "html5lib")
