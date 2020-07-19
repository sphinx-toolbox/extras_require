import shutil

import pytest
import tempfile
import pathlib

from sphinxcontrib.extras_require.sources import requirements_from_file


@pytest.mark.parametrize(
		"requirements, extra, expects",
		[
				("faker\npytest\ntox", "extra_c", ["faker", "pytest", "tox"]),
				("""\
faker
pytest
tox; python<=3.6
""", "extra_c", ["faker", "pytest", "tox; python<=3.6"]),
				]
		)
def test_from_file(requirements, extra, expects):
	with tempfile.TemporaryDirectory() as tmpdir:
		tmpdir_p = pathlib.Path(tmpdir)
		(tmpdir_p / "a_subdirectory" / "another_subdir").mkdir(parents=True)

		# to demonstrate the filename doesn't matter
		requirements_file = tmpdir_p / "a_subdirectory" / "another_subdir" / "requirements_list.txt"
		requirements_file.write_text(requirements)

		assert requirements_from_file(
				package_root=tmpdir_p,
				options={"file": "a_subdirectory/another_subdir/requirements_list.txt"},
				env=None,
				extra=extra,
				) == expects


def test_from_file_errors():
	with tempfile.TemporaryDirectory() as tmpdir:
		tmpdir_p = pathlib.Path(tmpdir)
		(tmpdir_p / "a_subdirectory" / "another_subdir").mkdir(parents=True)

		# to demonstrate the filename doesn't matter
		requirements_file = tmpdir_p / "a_subdirectory" / "another_subdir" / "Example.png"
		shutil.copy2(pathlib.Path(__file__).parent / "Example.png", requirements_file)

		with pytest.raises(ValueError, match="'.*' is not a text file."):
			requirements_from_file(
					package_root=tmpdir_p,
					options={"file": "a_subdirectory/another_subdir/Example.png"},
					env=None,
					extra='extra',
					)

		with pytest.raises(FileNotFoundError, match="Cannot find requirements file"):
			requirements_from_file(
					package_root=tmpdir_p,
					options={"file": "a_subdirectory/nonexistant_file.txt"},
					env=None,
					extra='extra',
					)
