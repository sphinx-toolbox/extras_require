# stdlib
import json
import pathlib
import shutil
import tempfile

# 3rd party
import pytest

# this package
from sphinxcontrib.extras_require.sources import requirements_from___pkginfo__


class MockBuildEnvironment:

	def __init__(self, tmpdir):
		self.srcdir = tmpdir / "docs"


@pytest.mark.parametrize(
		"requirements, extra, expects",
		[
				({"extra_c": ["faker", "pytest", "tox"]}, "extra_c", ["faker", "pytest", "tox"]),
				({"extra_c": ["faker", "pytest", "tox; python<=3.6"]},
					"extra_c", ["faker", "pytest", "tox; python<=3.6"]),
				]
		)
def test_from___pkginfo__(requirements, extra, expects):
	with tempfile.TemporaryDirectory() as tmpdir:
		tmpdir_p = pathlib.Path(tmpdir)
		pkginfo_file = tmpdir_p / "__pkginfo__.py"
		pkginfo_file.write_text(f"extras_require = {json.dumps(requirements)}")

		assert requirements_from___pkginfo__(
				package_root=tmpdir_p,
				options={},
				env=MockBuildEnvironment(tmpdir_p),  # type: ignore
				extra=extra,
				) == expects


def test_from___pkginfo___not_found():

	with tempfile.TemporaryDirectory() as tmpdir:
		tmpdir_p = pathlib.Path(tmpdir)
		with pytest.raises(FileNotFoundError, match="Cannot find __pkginfo__.py in"):
			requirements_from___pkginfo__(
					package_root=tmpdir_p,
					options={},
					env=MockBuildEnvironment(tmpdir_p),  # type: ignore
					extra='extra',
					)


def test_from___pkginfo___wrong_mime():

	with tempfile.TemporaryDirectory() as tmpdir:
		tmpdir_p = pathlib.Path(tmpdir)
		pkginfo_file = tmpdir_p / "__pkginfo__.py"
		shutil.copy2(pathlib.Path(__file__).parent / "Example.png", pkginfo_file)

		with pytest.raises(ImportError, match="Could not import __pkginfo__.py"):
			requirements_from___pkginfo__(
					package_root=tmpdir_p,
					options={},
					env=MockBuildEnvironment(tmpdir_p),  # type: ignore
					extra='extra',
					)
