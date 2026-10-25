"""Scenario 9: ScrapingBee with JavaScript rendering and markdown output.

Counts which trap and control URLs appear in the markdown. The markdown is not checked for
hidden links, so marked_as_hidden is always false here, as in scenario 1.
"""

from common import GROUND_TRUTH, collect, mentioned, ok, package_version, run_scrapingbee

NAME = "ScrapingBee with JavaScript rendering and markdown output"
PARAMS = {"render_js": True, "return_page_markdown": True}


def run(target):
    markdown, credits = run_scrapingbee(target, PARAMS)
    pairs = [(href, False) for href in GROUND_TRUTH if mentioned(markdown, target, href)]
    return {
        "name": NAME,
        "tool": f"scrapingbee {package_version('scrapingbee')}",
        "runs": {"scrapingbee":{**ok(None, collect(pairs)), "credits": credits, "output": markdown}},
    }
