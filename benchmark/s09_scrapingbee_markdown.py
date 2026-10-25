"""Scenario 9: ScrapingBee with JavaScript rendering and markdown output.

ScrapingBee does not judge visibility. A trap or control counts as hidden here when the
markdown leaves it out.
"""

from common import left_out, package_version, run_scrapingbee, split

NAME = "ScrapingBee with JavaScript rendering and markdown output"
PARAMS = {"render_js": True, "return_page_markdown": True}


def run(target):
    markdown, credits = run_scrapingbee(target, PARAMS)
    return {
        "name": NAME,
        "tool": f"scrapingbee {package_version('scrapingbee')}",
        "runs": {
            "scrapingbee": {
                "version": None,
                **split(left_out(markdown, target), "hidden"),
                "credits": credits,
                "output": markdown,
            }
        },
    }
