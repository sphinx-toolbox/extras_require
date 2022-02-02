# stdlib
import shutil
from typing import ContextManager, List

# 3rd party
import pytest
from domdf_python_tools.compat import nullcontext
from domdf_python_tools.paths import PathPlus

# this package
from sphinxcontrib.extras_require.sources import requirements_from_file


@pytest.mark.parametrize(
		"requirements, extra, expects, warningfilter",
		[
				("faker\npytest\ntox", "extra_c", ["faker", "pytest", "tox"], nullcontext()),
				(
						"\n".join(["faker", "pytest", 'tox; python_version <= "3.6"']),
						"extra_c",
						["faker", "pytest", 'tox; python_version <= "3.6"'],
						nullcontext(),
						),
				(
						"\n".join(["faker", "pytest", "tox; python<=3.6"]),
						"extra_c",
						["faker", "pytest"],
						pytest.warns(UserWarning, match="Ignored invalid requirement 'tox; python<=3.6'"),
						),
				]
		)
def test_from_file(
		tmp_pathplus: PathPlus,
		requirements: str,
		extra: str,
		expects: List[str],
		warningfilter: ContextManager,
		):
	(tmp_pathplus / "a_subdirectory" / "another_subdir").mkdir(parents=True)

	# to demonstrate the filename doesn't matter
	requirements_file = tmp_pathplus / "a_subdirectory" / "another_subdir" / "requirements_list.txt"
	requirements_file.write_text(requirements)

	with warningfilter:

		assert requirements_from_file(
				package_root=tmp_pathplus,
				options={"file": "a_subdirectory/another_subdir/requirements_list.txt"},
				env=None,
				extra=extra,
				) == expects


def test_from_file_errors(tmp_pathplus: PathPlus):
	(tmp_pathplus / "a_subdirectory" / "another_subdir").mkdir(parents=True)

	# to demonstrate the filename doesn't matter
	requirements_file = tmp_pathplus / "a_subdirectory" / "another_subdir" / "Example.png"
	shutil.copy2(PathPlus(__file__).parent / "Example.png", requirements_file)

	with pytest.raises(ValueError, match="'.*' is not a text file."):
		requirements_from_file(
				package_root=tmp_pathplus,
				options={"file": "a_subdirectory/another_subdir/Example.png"},
				env=None,
				extra="extra",
				)

	with pytest.raises(FileNotFoundError, match="Cannot find requirements file"):
		requirements_from_file(
				package_root=tmp_pathplus,
				options={"file": "a_subdirectory/nonexistant_file.txt"},
				env=None,
				extra="extra",
				)
