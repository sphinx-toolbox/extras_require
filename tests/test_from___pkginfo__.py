# stdlib
import json
import pathlib
import shutil
from typing import Dict, List

# 3rd party
import pytest
from domdf_python_tools.paths import PathPlus

# this package
from sphinxcontrib.extras_require.sources import requirements_from___pkginfo__


class MockBuildEnvironment:

	def __init__(self, tmpdir: pathlib.Path):
		self.srcdir = tmpdir / "docs"


@pytest.mark.parametrize(
		"requirements, extra, expects",
		[
				({"extra_c": ["faker", "pytest", "tox"]}, "extra_c", ["faker", "pytest", "tox"]),
				({"extra_c": ["faker", "pytest", "tox; python<=3.6"]},
					"extra_c", ["faker", "pytest", "tox; python<=3.6"]),
				]
		)
def test_from___pkginfo__(
		tmp_pathplus: PathPlus,
		requirements: Dict[str, List[str]],
		extra: str,
		expects: List[str],
		):
	pkginfo_file = tmp_pathplus / "__pkginfo__.py"
	pkginfo_file.write_text(f"extras_require = {json.dumps(requirements)}")

	assert requirements_from___pkginfo__(
			package_root=tmp_pathplus,
			options={},
			env=MockBuildEnvironment(tmp_pathplus),
			extra=extra,
			) == expects


def test_from___pkginfo___not_found(tmp_pathplus: PathPlus):
	with pytest.raises(FileNotFoundError, match="Cannot find __pkginfo__.py in"):
		requirements_from___pkginfo__(
				package_root=tmp_pathplus,
				options={},
				env=MockBuildEnvironment(tmp_pathplus),
				extra="extra",
				)


def test_from___pkginfo___wrong_mime(tmp_pathplus: PathPlus):
	pkginfo_file = tmp_pathplus / "__pkginfo__.py"
	shutil.copy2(PathPlus(__file__).parent / "Example.png", pkginfo_file)

	with pytest.raises(ImportError, match="Could not import __pkginfo__.py"):
		requirements_from___pkginfo__(
				package_root=tmp_pathplus,
				options={},
				env=MockBuildEnvironment(tmp_pathplus),
				extra="extra",
				)
