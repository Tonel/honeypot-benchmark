"""Scenario 6: Element.checkVisibility() with default options in Chromium, Firefox and WebKit."""

from common import package_version, run_playwright

NAME = "Element.checkVisibility() (default options)"

CHECK_JS = "els => els.map(el => [el.getAttribute('href'), el.checkVisibility()])"


def check(page):
    return [(href, not visible) for href, visible in page.eval_on_selector_all("a[href]", CHECK_JS)]


def run(target):
    return {"name": NAME, "tool": f"playwright {package_version('playwright')}", "runs": run_playwright(target, check)}
