"""Scenario 2: BeautifulSoup on the static HTML, flagging only inline styles and the hidden attribute."""

import re

import requests
from bs4 import BeautifulSoup

from common import collect, ok, package_version

NAME = "BeautifulSoup with an inline-style filter"

INLINE_HIDING = re.compile(
    r"display\s*:\s*none|visibility\s*:\s*hidden|opacity\s*:\s*0(?![.\d])|font-size\s*:\s*0(?![.\d])"
    r"|left\s*:\s*-\d{3,}px|transform\s*:|clip-path\s*:|clip\s*:\s*rect\(0",
    re.IGNORECASE,
)


def is_hidden_inline(tag):
    """True if the link or one of its ancestors has the hidden attribute or a hiding inline style."""
    for node in [tag, *tag.find_parents()]:
        if node.has_attr("hidden") or INLINE_HIDING.search(node.get("style", "")):
            return True
    return False


def run(target):
    html = requests.get(target, timeout=30)
    html.raise_for_status()
    soup = BeautifulSoup(html.text, "html.parser")
    pairs = [(a["href"], is_hidden_inline(a)) for a in soup.find_all("a", href=True)]
    return {
        "name": NAME,
        "tool": f"beautifulsoup4 {package_version('beautifulsoup4')}",
        "runs": {"static_html": ok(None, collect(pairs))},
    }
