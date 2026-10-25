"""Scenario 10: ScrapingBee AI extraction asked for "all links on the page".

Counts which trap and control URLs appear in the AI answer. The answer is not checked for
hidden links, so marked_as_hidden is always false here, as in scenario 1.
"""

from common import (
    GROUND_TRUTH,
    collect,
    mentioned,
    ok,
    package_version,
    run_scrapingbee,
)

NAME = 'ScrapingBee AI extraction ("all links on the page")'
PARAMS = {"ai_query": "return all links on the page"}


def run(target):
    answer, credits = run_scrapingbee(target, PARAMS)
    pairs = [(href, False) for href in GROUND_TRUTH if mentioned(answer, target, href)]
    return {
        "name": NAME,
        "tool": f"scrapingbee {package_version('scrapingbee')}",
        "runs": {
            "scrapingbee": {
                **ok(None, collect(pairs)),
                "credits": credits,
                "output": answer,
            }
        },
    }
