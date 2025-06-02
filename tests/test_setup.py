# stdlib
from types import SimpleNamespace
from typing import Any, Tuple

# 3rd party
import sphinx
from sphinx.events import EventListener
from sphinx_toolbox.testing import Sphinx, run_setup

# this package
import sphinxcontrib.extras_require
from sphinxcontrib.extras_require import __version__, extras_require_purger
from sphinxcontrib.extras_require.directive import ExtrasRequireDirective


# https://github.com/sphinx-toolbox/sphinx-toolbox/blob/d1750cf9d19f8f5e7fc5e408f0b50164ac9fad63/tests/common.py#L32
def get_app_config_values(config: Any) -> Tuple[str, str, Any]:
	if sphinx.version_info >= (7, 3):
		valid_types = config.valid_types
		default = config.default
		rebuild = config.rebuild
	else:
		default, rebuild, valid_types = config

	if isinstance(valid_types, (set, frozenset, tuple, list)):
		valid_types = sorted(valid_types)

	if hasattr(valid_types, "_candidates"):
		new_valid_types = SimpleNamespace()
		new_valid_types.candidates = sorted(valid_types._candidates)
		valid_types = new_valid_types

	return (default, rebuild, valid_types)


def test_setup() -> None:

	app: Sphinx
	setup_ret, directives, roles, additional_nodes, app = run_setup(sphinxcontrib.extras_require.setup)

	assert setup_ret == {
			"version": __version__,
			"parallel_read_safe": True,
			"parallel_write_safe": True,
			}

	assert additional_nodes == set()

	assert get_app_config_values(app.config.values["package_root"]) == (None, "env", [str])
	assert get_app_config_values(app.config.values["pypi_name"]) == (None, "env", [str])

	assert directives == {"extras-require": ExtrasRequireDirective}

	assert app.events.listeners == {
			"env-purge-doc": [EventListener(id=0, handler=extras_require_purger.purge_nodes, priority=500)],
			}
