"""Scenario 5: Playwright click(trial=True) in Chromium, Firefox and WebKit.

A link is flagged when the trial click fails its actionability checks (visible, stable,
receives events), which also covers links covered by another element.
"""

from playwright.sync_api import Error as PlaywrightError

from common import package_version, run_playwright

NAME = "Playwright click(trial=True)"


def check(page):
    pairs = []
    # Snapshot the links first: a trial click scrolls, which can insert links and shift indexes.
    for link in page.query_selector_all("a[href]"):
        try:
            link.click(trial=True, timeout=1000)
            flagged = False
        except PlaywrightError:
            flagged = True
        pairs.append((link.get_attribute("href"), flagged))
    return pairs


def run(target):
    return {
        "name": NAME,
        "tool": f"playwright {package_version('playwright')}",
        "runs": run_playwright(target, check),
    }
