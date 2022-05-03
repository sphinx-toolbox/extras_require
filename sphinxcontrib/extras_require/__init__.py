#!/usr/bin/env python3
#
#  __init__.py
"""
A Sphinx directive to specify that a module has extra requirements, and show how to install them.
"""
#
#  Copyright © 2020 Dominic Davis-Foster <dominic@davis-foster.co.uk>
#
#  Redistribution and use in source and binary forms, with or without modification,
#  are permitted provided that the following conditions are met:
#
#      * Redistributions of source code must retain the above copyright notice,
#        this list of conditions and the following disclaimer.
#      * Redistributions in binary form must reproduce the above copyright notice,
#        this list of conditions and the following disclaimer in the documentation
#        and/or other materials provided with the distribution.
#
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
#  "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
#  LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
#  A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER
#  OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
#  EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
#  PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
#  PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
#  LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
#  NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
#  SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

# stdlib
import sys
from typing import Any, Dict

# This all has to be up here so it's triggered first.
if sys.version_info >= (3, 10):
	# stdlib
	import types
	types.Union = types.UnionType

# 3rd party
from sphinx.application import Sphinx

# this package
from sphinxcontrib.extras_require.directive import ExtrasRequireDirective
from sphinxcontrib.extras_require.purger import extras_require_purger
from sphinxcontrib.extras_require.sources import sources  # noqa: F401

__author__: str = "Dominic Davis-Foster"
__copyright__: str = "2020 Dominic Davis-Foster"
__license__: str = "BSD"
__version__: str = "0.4.2"
__email__: str = "dominic@davis-foster.co.uk"

__all__ = ["extras_require_purger", "setup"]


def setup(app: Sphinx) -> Dict[str, Any]:
	"""
	Setup :mod:`sphinxcontrib.extras_require`.

	:param app: The Sphinx app.
	"""

	app.setup_extension("sphinx-prompt")

	# Location of package source directory relative to documentation source directory
	app.add_config_value("package_root", None, "env", [str])
	app.add_config_value("pypi_name", None, "env", [str])

	app.add_directive("extras-require", ExtrasRequireDirective)
	app.connect("env-purge-doc", extras_require_purger.purge_nodes)

	return {
			"version": __version__,
			"parallel_read_safe": True,
			"parallel_write_safe": True,
			}
