from sphinxcontrib.extras_require.sources import flag
import pytest


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
def test_flag(value):
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
def test_flag_errors(value):
	with pytest.raises(ValueError, match='No argument is allowed; ".*" supplied'):
		flag(value)
