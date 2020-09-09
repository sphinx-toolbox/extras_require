# From https://github.com/takluyver/flit/blob/master/flit_core/flit_core/config.py
#
# Copyright (c) 2015, Thomas Kluyver and contributors
# All rights reserved.
#
# BSD 3-clause license:
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
# list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation and/or
# other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its contributors
# may be used to endorse or promote products derived from this software without
# specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
# ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# stdlib
import difflib
import logging

# 3rd party
import pytoml as toml  # type: ignore

__all__ = ["ConfigError", "read_flit_config", "prep_toml_config", "LoadedConfig"]

log = logging.getLogger(__name__)


class ConfigError(ValueError):
	pass


metadata_list_fields = {"classifiers", "requires", "dev-requires"}

metadata_allowed_fields = {
		"module",
		"author",
		"author-email",
		"maintainer",
		"maintainer-email",
		"home-page",
		"license",
		"keywords",
		"requires-python",
		"dist-name",
		"description-file",
		"requires-extra",
		} | metadata_list_fields

metadata_required_fields = {
		"module",
		"author",
		}


def read_flit_config(path):
	"""Read and check the `pyproject.toml` file with data about the package.
	"""
	with path.open('r', encoding="utf-8") as f:
		d = toml.load(f)
	return prep_toml_config(d, path)


def prep_toml_config(d, path):
	"""Validate config loaded from pyproject.toml and prepare common metadata

	Returns a LoadedConfig object.
	"""
	if ("tool" not in d) or ("flit" not in d["tool"]) or (not isinstance(d["tool"]["flit"], dict)):
		raise ConfigError("TOML file missing [tool.flit] table.")

	d = d["tool"]["flit"]
	unknown_sections_ = set(d) - {"metadata", "scripts", "entrypoints", "sdist"}
	unknown_sections = [s for s in unknown_sections_ if not s.lower().startswith("x-")]
	if unknown_sections:
		raise ConfigError("Unknown sections: " + ", ".join(unknown_sections))

	if "metadata" not in d:
		raise ConfigError("[tool.flit.metadata] section is required")

	loaded_cfg = _prep_metadata(d["metadata"], path)

	return loaded_cfg


class LoadedConfig:

	def __init__(self):
		self.module = None
		self.metadata = {}
		self.reqs_by_extra = {}
		self.entrypoints = {}
		self.referenced_files = []
		self.sdist_include_patterns = []
		self.sdist_exclude_patterns = []


readme_ext_to_content_type = {
		".rst": "text/x-rst",
		".md": "text/markdown",
		".txt": "text/plain",
		}


def _prep_metadata(md_sect, path):
	"""Process & verify the metadata from a config file

	- Pull out the module name we're packaging.
	- Read description-file and check that it's valid rst
	- Convert dashes in key names to underscores
	  (e.g. home-page in config -> home_page in metadata)
	"""
	if not set(md_sect).issuperset(metadata_required_fields):
		missing = metadata_required_fields - set(md_sect)
		raise ConfigError("Required fields missing: " + '\n'.join(missing))

	res = LoadedConfig()

	res.module = md_sect.get("module")
	if not str.isidentifier(res.module):
		raise ConfigError(f"Module name {res.module!r} is not a valid identifier")

	md_dict = res.metadata

	for key, value in md_sect.items():
		if key in ["description-file", "module"]:
			continue
		if key not in metadata_allowed_fields:
			closest = difflib.get_close_matches(key, metadata_allowed_fields, n=1, cutoff=0.7)
			msg = f"Unrecognised metadata key: {key!r}"
			if closest:
				msg += f" (did you mean {closest[0]!r}?)"
			raise ConfigError(msg)

		k2 = key.replace('-', '_')
		md_dict[k2] = value
		if key == "requires-extra":
			if not isinstance(value, dict):  # pragma: no cover
				raise ConfigError(f"Expected a dict for requires-extra field, found {value!r}")
			if not all(isinstance(e, list) for e in value.values()):
				raise ConfigError("Expected a dict of lists for requires-extra field")
			for e, reqs in value.items():
				if not all(isinstance(a, str) for a in reqs):
					raise ConfigError(f"Expected a string list for requires-extra. (extra {e})")
		else:
			if not isinstance(value, str):
				raise ConfigError(f"Expected a string for {key} field, found {value!r}")

	# Move dev-requires into requires-extra
	reqs_noextra = md_dict.pop("requires_dist", [])
	res.reqs_by_extra = md_dict.pop("requires_extra", {})
	dev_requires = md_dict.pop("dev_requires", None)
	if dev_requires is not None:
		if "dev" in res.reqs_by_extra:
			raise ConfigError("dev-requires occurs together with its replacement requires-extra.dev.")
		else:
			log.warning('"dev-requires = ..." is obsolete. Use "requires-extra = {"dev" = ...}" instead.')
			res.reqs_by_extra["dev"] = dev_requires

	# Add requires-extra requirements into requires_dist
	md_dict["requires_dist"] = reqs_noextra + list(_expand_requires_extra(res.reqs_by_extra))

	md_dict["provides_extra"] = sorted(res.reqs_by_extra.keys())

	# For internal use, record the main requirements as a '.none' extra.
	res.reqs_by_extra[".none"] = reqs_noextra

	return res


def _expand_requires_extra(re):
	for extra, reqs in sorted(re.items()):
		for req in reqs:
			if ';' in req:
				name, envmark = req.split(';', 1)
				yield f'{name} ; extra == "{extra}" and ({envmark})'
			else:
				yield f'{req} ; extra == "{extra}"'
