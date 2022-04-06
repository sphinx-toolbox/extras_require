# 3rd party
import pytest

# this package
from sphinxcontrib.extras_require.sources import flag


@pytest.mark.parametrize("value", [
		'',
		' ',
		"  ",
		"   ",
		"    ",
		'\t',
		'\n',
		"\t ",
		"\t  ",
		"\t   ",
		"\t    ",
		])
def test_flag(value: str) -> None:
	assert isinstance(flag(value), bool)
	assert flag(value) is True


@pytest.mark.parametrize("value", [
		"Hello",
		"  Hello",
		"Foo",
		" Foo",
		"True",
		"   True",
		"\tFalse",
		])
def test_flag_errors(value: str) -> None:
	with pytest.raises(ValueError, match="No argument is allowed; '.*' supplied"):
		flag(value)
