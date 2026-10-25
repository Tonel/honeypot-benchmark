"""Shared settings, ground truth and helpers for the benchmark scripts."""

import os
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from urllib.parse import urljoin

from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
from scrapingbee import ScrapingBeeClient

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TARGET_URL = "https://tonel.github.io/honeypot-benchmark/"
PLAYWRIGHT_BROWSERS = ["chromium", "firefox", "webkit"]

# href -> (trap number, description)
TRAPS = {
    "trap/01-inline-display-none": (1, "Inline display:none"),
    "trap/02-stylesheet-display-none": (2, "display:none from a stylesheet"),
    "trap/03-visibility-hidden": (3, "visibility:hidden"),
    "trap/04-opacity-zero": (4, "opacity:0"),
    "trap/05-opacity-parent": (5, "opacity:0 on the parent"),
    "trap/06-zero-size": (6, "Zero width and height"),
    "trap/07-font-size-zero": (7, "font-size:0"),
    "trap/08-left-minus-9999": (8, "left:-9999px"),
    "trap/09-translate-200vw": (9, "transform: translateX(-200vw)"),
    "trap/10-clip-path": (10, "clip-path: inset(100%)"),
    "trap/11-clip-rect": (11, "clip: rect(0 0 0 0)"),
    "trap/12-same-color": (12, "Text the same color as the background"),
    "trap/13-covered-by-overlay": (13, "Covered by an overlay"),
    "trap/14-hidden-attribute": (14, "hidden attribute"),
    "trap/15-aria-hidden": (15, 'aria-hidden="true" only'),
    "trap/16-hidden-after-500ms": (16, "Hidden by JavaScript 500 ms after load"),
    "trap/17-noscript": (17, "Inside a noscript element"),
    "trap/18-html-comment": (18, "Inside an HTML comment"),
    "trap/19-content-visibility": (19, "content-visibility:hidden"),
    "trap/20-robots-disallowed": (20, "nofollow link to a robots.txt-disallowed path"),
}

# href -> description. None of these should be flagged.
CONTROLS = {
    "#skip-to-content": "Skip to content link",
    "control/mobile-offer": "Collapsed mobile menu",
    "control/below-fold-price-list": "Below the fold",
    "control/lazy-loaded-newsletter": "Lazy-loaded",
    "control/low-contrast-cookie-settings": "Low-contrast footer link",
}

GROUND_TRUTH = {
    href: {"kind": "trap", "number": number, "label": label}
    for href, (number, label) in TRAPS.items()
}
GROUND_TRUTH.update(
    {href: {"kind": "control", "number": None, "label": label} for href, label in CONTROLS.items()}
)


def collect(pairs):
    """Turn (href, hidden) pairs into one boolean per trap and control.

    Only the 20 traps and 5 controls are kept. A link the method did not find counts as hidden,
    the same as a link that ScrapingBee leaves out of its output.
    """
    found = {href for href, _ in pairs}
    marked = {href for href, hidden in pairs if hidden}
    return {href: href not in found or href in marked for href in GROUND_TRUTH}


def split(marks, field):
    """Split one boolean per link into the hidden_traps and controls maps, under the given field name."""
    return {
        "hidden_traps": {href: {field: marks[href]} for href in TRAPS},
        "controls": {href: {field: marks[href]} for href in CONTROLS},
    }


def ok(run_version, marks):
    """run_version is the browser version, or None when no browser was used."""
    return {"version": run_version, **split(marks, "hidden")}


def left_out(text, target):
    """One boolean per known link: True if the link does NOT appear in the ScrapingBee output text.

    ScrapingBee does not judge visibility. A link it leaves out is treated as hidden.
    """
    return {href: not mentioned(text, target, href) for href in GROUND_TRUTH}


def unavailable(reason):
    return {"unavailable": reason}


def failed(exc):
    return {"error": f"{type(exc).__name__}: {exc}"}


def package_version(name):
    try:
        return version(name)
    except PackageNotFoundError:
        return None


def mentioned(text, target, href):
    """True if the link appears in text, either as written or as an absolute URL."""
    return href in text or urljoin(target, href) in text


def run_scrapingbee(target, params):
    """Call the ScrapingBee HTML API. Returns (body, credits from the Spb-cost header)."""
    load_dotenv(PROJECT_ROOT / ".env")
    api_key = os.environ.get("SCRAPINGBEE_API_KEY")
    if not api_key:
        raise RuntimeError("SCRAPINGBEE_API_KEY is not set. Copy .env.sample to .env and add your key.")
    response = ScrapingBeeClient(api_key).html_api(target, params=params)
    response.raise_for_status()
    return response.text, response.headers.get("Spb-cost")


def run_playwright(target, check):
    """Run check(page) -> [(href, flagged)] in each Playwright browser, keyed by browser name."""
    runs = {}
    with sync_playwright() as p:
        for name in PLAYWRIGHT_BROWSERS:
            try:
                browser = getattr(p, name).launch()
                try:
                    page = browser.new_page()
                    page.goto(target)
                    runs[name] = ok(browser.version, collect(check(page)))
                finally:
                    browser.close()
            except Exception as exc:
                runs[name] = failed(exc)
    return runs
