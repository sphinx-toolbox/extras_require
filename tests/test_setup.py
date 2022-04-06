# 3rd party
from sphinx.events import EventListener
from sphinx_toolbox.testing import Sphinx, run_setup

# this package
import sphinxcontrib.extras_require
from sphinxcontrib.extras_require import __version__, extras_require_purger
from sphinxcontrib.extras_require.directive import ExtrasRequireDirective


def test_setup() -> None:

	app: Sphinx
	setup_ret, directives, roles, additional_nodes, app = run_setup(sphinxcontrib.extras_require.setup)

	assert setup_ret == {
			"version": __version__,
			"parallel_read_safe": True,
			"parallel_write_safe": True,
			}

	assert additional_nodes == set()

	assert app.config.values["package_root"] == (None, "env", [str])
	assert app.config.values["pypi_name"] == (None, "env", [str])

	assert directives == {"extras-require": ExtrasRequireDirective}

	assert app.events.listeners == {
			"env-purge-doc": [EventListener(id=0, handler=extras_require_purger.purge_nodes, priority=500)],
			}
