"""Scenario 1: Beautiful Soup find_all('a') on the static HTML. It lists links and flags nothing."""

import requests
from bs4 import BeautifulSoup

from common import collect, ok, package_version

NAME = "Beautiful Soup find_all('a')"


def run(target):
    html = requests.get(target, timeout=30)
    html.raise_for_status()
    soup = BeautifulSoup(html.text, "html.parser")
    pairs = [(a["href"], False) for a in soup.find_all("a", href=True)]
    return {
        "name": NAME,
        "tool": f"beautifulsoup4 {package_version('beautifulsoup4')}",
        "runs": {"static_html": ok(None, collect(pairs))},
    }
