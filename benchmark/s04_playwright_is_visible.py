"""Scenario 4: Playwright is_visible() in Chromium, Firefox and WebKit."""

from common import package_version, run_playwright

NAME = "Playwright is_visible()"


def check(page):
    pairs = []
    for link in page.query_selector_all("a[href]"):
        pairs.append((link.get_attribute("href"), not link.is_visible()))
    return pairs


def run(target):
    return {"name": NAME, "tool": f"playwright {package_version('playwright')}", "runs": run_playwright(target, check)}
