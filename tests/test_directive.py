# Some text strings from https://github.com/pypa/packaging/blob/master/tests/test_requirements.py
# stdlib
from typing import List

# 3rd party
import pytest
from bs4 import BeautifulSoup  # type: ignore
from bs4.element import Tag  # type: ignore
from pytest_regressions.file_regression import FileRegressionFixture  # type: ignore

# this package
from sphinxcontrib.extras_require.directive import get_requirements, make_node_content, validate_requirements

from sphinx_toolbox.testing import check_html_regression


@pytest.mark.parametrize(
		"requirements, valid_requirements",
		[
				pytest.param(
						['name[bar]>=3; python_version == "2.7"'],
						['name[bar]>=3; python_version == "2.7"'],
						id="string_specifier_marker",
						),
				pytest.param(["name@ http://foo.com"], ["name@ http://foo.com"], id="string_url"),
				pytest.param(
						['name@ http://foo.com ; extra == "feature"'],
						['name@ http://foo.com ; extra == "feature"'],
						id="string_url_with_marker",
						),
				pytest.param(["foo-bar.quux_baz"], ["foo-bar.quux_baz"], id="name_with_other_characters"),
				pytest.param(["name>=3"], ["name>=3"], id="name_with_version"),
				pytest.param(["name==1.0.org1"], ["name==1.0.org1"], id="with_legacy_version"),
				pytest.param(
						["name>=1.x.y;python_version=='2.6'"],
						['name>=1.x.y; python_version == "2.6"'],
						id="with_legacy_version_and_marker",
						),
				pytest.param(["name (==4)"], ["name==4"], id="version_with_parens_and_whitespace"),
				pytest.param(["name>=3,<2"], ["name<2,>=3"], id="name_with_multiple_versions"),
				pytest.param(["name >=2, <3"], ["name<3,>=2"], id="name_with_multiple_versions_and_whitespace"),
				pytest.param(["foobar [quux,bar]"], ["foobar[bar,quux]"], id="extras"),
				pytest.param(["foo[]"], ["foo"], id="empty_extras"),
				pytest.param(["foo @ http://example.com"], ["foo@ http://example.com"], id="url"),
				pytest.param(
						["foo @ http://example.com ; os_name=='a'"],
						['foo@ http://example.com ; os_name == "a"'],
						id="url_and_marker",
						),
				pytest.param(["name @ file:///absolute/path"], ["name@ file:///absolute/path"], id="file_url"),
				pytest.param(
						["name [fred, bar] @ http://foo.com ; python_version=='2.7'"],
						['name[bar,fred]@ http://foo.com ; python_version == "2.7"'],
						id="extras_and_url_and_marker",
						),
				pytest.param(
						["foo @ https://example.com/name;v=1.1/?query=foo&bar=baz#blah ; python_version=='3.4'"],
						['foo@ https://example.com/name;v=1.1/?query=foo&bar=baz#blah ; python_version == "3.4"'],
						id="complex_url_and_marker",
						),
				pytest.param(
						["name[strange, quux];python_version<'2.7' and "
							"platform_version=='2'"],
						['name[quux,strange]; python_version < "2.7" and platform_version == "2"'],
						id="multiple_markers",
						),
				pytest.param(
						["name; os_name=='a' and os_name=='b' or os_name=='c'"],
						['name; os_name == "a" and os_name == "b" or os_name == "c"'],
						id="multiple_comparsion_markers",
						),
				pytest.param(["pygame"], ["pygame"], id="pygame"),
				pytest.param(["six"], ["six"], id="six"),
				pytest.param(["urllib3"], ["urllib3"], id="urllib3"),
				pytest.param(["setuptools"], ["setuptools"], id="setuptools"),
				pytest.param(["docutils"], ["docutils"], id="docutils"),
				pytest.param(["pip"], ["pip"], id="pip"),
				pytest.param(["wheel"], ["wheel"], id="wheel"),
				pytest.param(["pytz"], ["pytz"], id="pytz"),
				pytest.param(["certifi"], ["certifi"], id="certifi"),
				pytest.param(["numpy"], ["numpy"], id="numpy"),
				pytest.param(["pygame     >=1.2.3"], ["pygame>=1.2.3"], id=">= and excess space"),
				pytest.param(["six<1.2.3"], ["six<1.2.3"], id="<"),
				pytest.param(["urllib3>1.2.4, !=1.2.6"], ["urllib3!=1.2.6,>1.2.4"], id="> and !="),
				pytest.param(["setuptools   ==32.2"], ["setuptools==32.2"], id="== and excess space"),
				pytest.param(["docutils", "pip", "wheel"], ["docutils", "pip", "wheel"], id="three requirements"),
				pytest.param(
						["pytz<1.2", "certifi>0.1,!=2.0.1,<3.0", "numpy; platform_system!='Darwin'"],
						["certifi!=2.0.1,<3.0,>0.1", 'numpy; platform_system != "Darwin"', "pytz<1.2"],
						id="complex requirements",
						),
				]
		)
def test_validate_requirements(requirements, valid_requirements):
	assert validate_requirements(requirements) == valid_requirements


@pytest.mark.parametrize(
		"requirements",
		[
				pytest.param(["foo!"], id="invalid_name"),
				pytest.param(["foo @ http://example.com; os_name=='a'"]),
				pytest.param(["name @ gopher:/foo/com"], id="invalid URL"),
				pytest.param(["name @ file:."], id="invalid file URL (1)"),
				pytest.param(["name @ file:/."], id="invalud file URL (2)"),
				pytest.param(["name; foobar=='x'"], id="invalid_marker"),
				["pygame     ?=1.2.3"],
				["six**1.2.3"],
				["urllib3;1.2.4, <*1.2.6"],
				]
		)
def test_validate_requirements_invalid(requirements):
	with pytest.raises(ValueError, match="Invalid requirement"):
		validate_requirements(requirements)


class Test_make_node_content:

	@pytest.mark.parametrize("scope", ["module", "class", "package", "function", "library", "plugin"])
	def test_scopes(self, scope):
		assert make_node_content(["foo"], "my_package", "the_extra", scope) == f"""\
This {scope} has the following additional requirement:

    .. code-block:: text

        foo

These can be installed as follows:

    .. prompt:: bash

        python -m pip install my_package[the_extra]

"""

	@pytest.mark.parametrize(
			"requirements, plural",
			[
					pytest.param(["pip", "wheel", "setuptools"], "s", id="3 requirements"),
					pytest.param(["numpy", "scipy"], "s", id="2 requirements"),
					pytest.param(["sphinx"], '', id="1 requirement"),
					]
			)
	def test_plural(self, requirements, plural):
		assert make_node_content(requirements, "my_package", "the_extra").splitlines()[0] == f"""\
This module has the following additional requirement{plural}:"""


def test(the_app):
	# app is a Sphinx application object for default sphinx project (`tests/doc-test/test-root`).
	the_app.build()


def _do_test_directive(page, requirements: List[str], extra: str, file_regression: FileRegressionFixture):

	div_count = 0

	for div in page.findAll("div"):
		if not div.get("id", '').startswith("extras_require"):
			continue

		assert div.findAll("p")[0].contents == ["Attention"]
		assert div.findAll("p")[0]["class"] == ["admonition-title"]
		assert div.findAll("p")[1].contents == ["This module has the following additional requirements:"]

		assert div.div["class"] == ["highlight-text", "notranslate"]
		assert div.div.div["class"] == ["highlight"]
		assert div.div.div.pre.contents[1:] == ["\n".join(requirements) + "\n"]

		assert div.findAll("p")[2].contents == ["These can be installed as follows:"]

		assert div.blockquote.div.div["class"] == ["highlight-default", "notranslate"]
		assert div.blockquote.div.div.div["class"] == ["highlight"]

		expected_instructions = [
				Tag(name="span"),
				"$ python -m pip install Python",
				Tag(name="span", attrs={"class": ["o"]}),
				extra,
				Tag(name="span", attrs={"class": ["o"]}),
				'\n'
				]
		expected_instructions[2].string = "["
		expected_instructions[4].string = "]"

		assert div.blockquote.div.div.div.pre.contents == expected_instructions

		div_count += 1

	assert div_count == 1

	check_html_regression(page, file_regression)


@pytest.mark.parametrize("page", [
		"flit_demo.html",
		"scopes_demo.html",
		"setup_cfg_demo.html",
		"requirements_file_demo.html",
		"pkginfo_demo.html",
		"manual_demo.html",
		], indirect=True)
def test_output(page: BeautifulSoup, file_regression: FileRegressionFixture):

	check_html_regression(page, file_regression)


@pytest.mark.parametrize("page", ["no_requirements_demo.html"], indirect=True)
def test_no_requirements_demo(page: BeautifulSoup, file_regression: FileRegressionFixture):
	# Make sure the page title is what you expect
	title = page.find("h1").contents[0].strip()
	assert "No Requirements Demo" == title

	# Now test the directive
	for div in page.findAll("div"):
		assert not div.get("id", '').startswith("extras_require")

	check_html_regression(page, file_regression)


@pytest.mark.parametrize(
		"options, content",
		[
				(
						{"__pkginfo__": True, "setup.cfg": True},
						["pytest"],
						),
				(
						{"setup.cfg": True},
						["pytest"],
						),
				(
						{"flit": True, "setup.cfg": True},
						[],
						),
				]
		)
def test_directive_multiple_sources(options, content):
	with pytest.raises(ValueError, match="Please specify only one source for the extra requirements"):
		get_requirements(
				env=None,
				extra="foo",
				options=options,
				content=content,
				)


@pytest.mark.parametrize(
		"options, content", [
				({}, []),
				({"setup_cfg": True}, []),
				({"pkginfo": True}, []),
				({"flit": False}, []),
				]
		)
def test_directive_no_sources(options, content):
	with pytest.raises(ValueError, match="Please specify a source for the extra requirements"):
		get_requirements(
				env=None,
				extra="foo",
				options=options,
				content=content,
				)
