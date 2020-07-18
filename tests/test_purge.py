import pytest

from sphinxcontrib.extras_require import purge_extras_requires


class MockBuildEnvironment:
	pass


@pytest.mark.parametrize(
		"nodes, output",
		[
				([], []),
				([{"docname": "document"}], []),
				([{"docname": "foo"}], [{"docname": "foo"}]),
				([{"docname": "foo"}, {"docname": "document"}], [{"docname": "foo"}]),
				]
		)
def test_purge_extras_require(nodes, output):
	env = MockBuildEnvironment()

	purge_extras_requires('', env, "document")  # type: ignore
	assert not hasattr(env, "all_extras_requires")

	env.all_extras_requires = nodes
	purge_extras_requires('', env, "document")  # type: ignore
	assert hasattr(env, "all_extras_requires")
	assert env.all_extras_requires == output
