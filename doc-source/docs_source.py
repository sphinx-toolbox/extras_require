"""
Examples:

**Source code:** :source:`sphinxcontrib/extras_require/directive.py`

--------------------------------------------------------------------------

:issue:`3`

:pr:`3`

:pull:`3`

"""

# stdlib
import warnings
from typing import Any, Dict, List, Optional, Tuple

# 3rd party
import requests
from bs4 import BeautifulSoup
from docutils import nodes, utils
from docutils.nodes import Node, system_message
from docutils.parsers.rst.states import Inliner
from sphinx.application import Sphinx
from sphinx.config import Config
from sphinx.util.nodes import split_explicit_title
from sphinx.writers.html import HTMLTranslator


def source_role(
		typ: str,
		rawtext: str,
		text: str,
		lineno: int,
		inliner: Inliner,
		options: Dict = {},
		content: List[str] = []
		) -> Tuple[List[Node], List[system_message]]:
	"""
	Adds a link to the given Python source file on GitHub.

	Based on ``pyspecific.py`` from the Python documentation.

	:copyright: 2008-2014 by Georg Brandl.
	:license: Python license.

	:param typ:
	:param rawtext:
	:param text:
	:param lineno:
	:param inliner:
	:param options:
	:param content:

	:return:
	"""

	has_t, title, target = split_explicit_title(text)
	title = utils.unescape(title)
	target = utils.unescape(target)
	refnode = nodes.reference(
			title,
			title,
			refuri=inliner.document.settings.env.app.config.github_source_url % target,
			)

	return [refnode], []


class IssueNode(nodes.reference):
	"""
	Docutils Node to represent a link to a GitHub *Issue* or *Pull Request*

	:param issue_number:
	:param refuri:
	"""

	has_tooltip: bool
	issue_number: int
	issue_url: str

	def __init__(
			self,
			issue_number: int,
			refuri: Optional[str] = None,
			):
		self.has_tooltip = False
		self.issue_number = int(issue_number)
		self.issue_url = str(refuri)

		super().__init__(f"#{issue_number}", f"#{issue_number}", refuri=refuri)


def issue_role(
		typ: str,
		rawtext: str,
		text: str,
		lineno: int,
		inliner: Inliner,
		options: Dict = {},
		content: List[str] = []
		) -> Tuple[List[Node], List[system_message]]:
	"""
	Adds a link to the given Python source file on GitHub.

	Based on ``pyspecific.py`` from the Python documentation.

	:copyright: 2008-2014 by Georg Brandl.
	:license: Python license.

	:param typ:
	:param rawtext:
	:param text:
	:param lineno:
	:param inliner:
	:param options:
	:param content:

	:return:
	"""

	# TODO: issue preview

	has_t, title, target = split_explicit_title(text)
	title = utils.unescape(title)
	target = utils.unescape(target)
	refnode = IssueNode(
			target,
			refuri=inliner.document.settings.env.app.config.github_issues_url % int(target),
			)

	return [refnode], []


def pull_role(
		typ: str,
		rawtext: str,
		text: str,
		lineno: int,
		inliner: Inliner,
		options: Dict = {},
		content: List[str] = []
		) -> Tuple[List[Node], List[system_message]]:
	"""
	Adds a link to the given Python source file on GitHub.

	Based on ``pyspecific.py`` from the Python documentation.

	:copyright: 2008-2014 by Georg Brandl.
	:license: Python license.

	:param typ:
	:param rawtext:
	:param text:
	:param lineno:
	:param inliner:
	:param options:
	:param content:

	:return:
	"""

	# TODO: PR preview

	has_t, title, target = split_explicit_title(text)
	title = utils.unescape(title)
	target = utils.unescape(target)
	refnode = IssueNode(
			target,
			refuri=inliner.document.settings.env.app.config.github_pull_url % target,
			)

	return [refnode], []


class MissingOptionError(ValueError):
	"""
	Subclass of :exc:`ValueError` to indicate a missing configuration option.
	"""


def validate_config(app: Sphinx, config: Config) -> None:
	"""
	Validate the provided configuration values.

	:param app:
	:param config:
	"""

	if not config.github_username:
		raise MissingOptionError("The 'github_username' option is required.")
	else:
		config.github_username = str(config.github_username)

	if not config.github_repository:
		raise MissingOptionError("The 'github_repository' option is required.")
	else:
		config.github_repository = str(config.github_repository)

	config.github_url = f"https://github.com/{config.github_username}/{config.github_repository}"
	config.github_source_url = f"{config.github_url}/tree/master/%s"
	config.github_issues_url = f"{config.github_url}/issues/%s"
	config.github_pull_url = f"{config.github_url}/pull/%s"


def visit_issue_node(translator: HTMLTranslator, node: IssueNode):
	"""
	Visit a :class:`~.IssueNode`.

	If the node points to a valid issue / pull request,
	add a tooltip giving the title of the issue / pull request and a hyperlink to the page on GitHub.

	:param translator:
	:param node: The node being visited.
	"""

	r = requests.get(node.issue_url)

	if r.status_code == 200:
		soup = BeautifulSoup(r.content)
		node.has_tooltip = True
		issue_title = soup.find_all("span", attrs={"class": "js-issue-title"})[0].contents[0].strip().strip()
		translator.body.append(f'<abbr title="{issue_title}">')
		translator.visit_reference(node)
	else:
		warnings.warn(f"Issue/Pull Request #{node.issue_number} ")


def depart_issue_node(translator: HTMLTranslator, node: IssueNode):
	"""
	Depart a :class:`~.IssueNode`.

	:param translator:
	:param node: The node being visited.
	"""

	if node.has_tooltip:
		translator.depart_reference(node)
		translator.body.append("</abbr>")


def setup(app: Sphinx) -> Dict[str, Any]:
	"""
	Setup Sphinx Extension.

	:param app:

	:return:
	"""

	# Link to source code
	app.add_role('source', source_role)

	# Link to GH issue
	app.add_role('issue', issue_role)

	# Link to GH pull request
	app.add_role('pr', pull_role)
	app.add_role('pull', pull_role)

	# Custom node for issues and PRs
	app.add_node(IssueNode, html=(visit_issue_node, depart_issue_node))

	# Configuration values.
	app.add_config_value("github_username", None, "env", types=[str])
	app.add_config_value("github_repository", None, "env", types=[str])

	app.connect('config-inited', validate_config, priority=850)

	return {'version': '1.0', 'parallel_read_safe': True}
