# this package
from sphinx.events import EventListener

import sphinxcontrib.extras_require
from sphinxcontrib.extras_require import __version__, purge_extras_requires
from sphinxcontrib.extras_require.directive import ExtrasRequireDirective
from sphinx_toolbox.testing import run_setup, Sphinx


def test_setup():

	app: Sphinx
	setup_ret, directives, roles, additional_nodes, app = run_setup(sphinxcontrib.extras_require.setup)

	assert setup_ret == {
		"version": __version__,
		"parallel_read_safe": True,
		"parallel_write_safe": True,
		}

	assert additional_nodes == set()

	assert app.config.values["package_root"] == (None, "html", [str])

	assert directives == {
			"extras-require": ExtrasRequireDirective,
			}

	assert app.events.listeners == {
			"env-purge-doc": [EventListener(id=0, handler=purge_extras_requires, priority=500)],
			}
