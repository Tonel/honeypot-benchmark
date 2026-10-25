"""Scenario 10: ScrapingBee AI extraction asked for "all links on the page".

ScrapingBee does not judge visibility. A trap or control counts as hidden here when the
AI answer leaves it out.
"""

from common import left_out, package_version, run_scrapingbee, split

NAME = 'ScrapingBee AI extraction ("all links on the page")'
PARAMS = {"ai_query": "return all links on the page"}


def run(target):
    answer, credits = run_scrapingbee(target, PARAMS)
    return {
        "name": NAME,
        "tool": f"scrapingbee {package_version('scrapingbee')}",
        "runs": {
            "scrapingbee": {
                "version": None,
                **split(left_out(answer, target), "hidden"),
                "credits": credits,
                "output": answer,
            }
        },
    }
