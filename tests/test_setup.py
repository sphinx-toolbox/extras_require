from sphinxcontrib.extras_require import __version__, ExtrasRequireDirective, purge_extras_requires
import sphinxcontrib.extras_require


class MockApp:

	def __init__(self):
		self.config_values = []
		self.directives = []
		self.connections = []

	def add_config_value(self, *args):
		self.config_values.append(args)

	def add_directive(self, *args):
		self.directives.append(args)

	def connect(self, *args):
		self.connections.append(args)


def test_setup():
	app = MockApp()

	assert sphinxcontrib.extras_require.setup(app=app) == {  # type: ignore
		"version": __version__,
		"parallel_read_safe": True,
		"parallel_write_safe": True,
		}

	assert app.config_values == [("package_root", None, "html")]
	assert app.directives == [("extras-require", ExtrasRequireDirective)]
	assert app.connections == [("env-purge-doc", purge_extras_requires)]
