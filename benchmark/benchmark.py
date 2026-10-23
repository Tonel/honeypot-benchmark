"""Run every benchmark scenario against the target page and write one JSON file.

Usage (from the repo root):
    python benchmark/benchmark.py
    python benchmark/benchmark.py --only 03 04
    python benchmark/benchmark.py --target http://localhost:8000/
"""

import argparse
import json
import platform
from datetime import datetime, timezone
from pathlib import Path

import s01_bs4_find_all
import s02_bs4_inline_style
import s03_selenium_is_displayed
import s04_playwright_is_visible
import s05_playwright_click_trial
import s06_check_visibility_default
import s07_check_visibility_all
import s08_custom_check
import s09_scrapingbee_markdown
import s10_scrapingbee_ai_extract
from common import GROUND_TRUTH, TARGET_URL, failed, package_version

SCENARIOS = {
    "01": s01_bs4_find_all,
    "02": s02_bs4_inline_style,
    "03": s03_selenium_is_displayed,
    "04": s04_playwright_is_visible,
    "05": s05_playwright_click_trial,
    "06": s06_check_visibility_default,
    "07": s07_check_visibility_all,
    "08": s08_custom_check,
    "09": s09_scrapingbee_markdown,
    "10": s10_scrapingbee_ai_extract,
}
PACKAGES = ["playwright", "selenium", "beautifulsoup4", "requests"]
DEFAULT_OUT = Path(__file__).resolve().parent.parent / "results" / "benchmark.json"


def main():
    parser = argparse.ArgumentParser(description="Benchmark link-visibility methods against a page.")
    parser.add_argument("--target", default=TARGET_URL, help="page to test")
    parser.add_argument("--out", default=str(DEFAULT_OUT), help="JSON file to write")
    parser.add_argument("--only", nargs="+", choices=list(SCENARIOS), help="scenario numbers to run")
    args = parser.parse_args()

    methods = {}
    for number in args.only or list(SCENARIOS):
        module = SCENARIOS[number]
        print(f"[{number}] {module.NAME}", flush=True)
        try:
            methods[number] = module.run(args.target)
        except Exception as exc:
            methods[number] = {"name": module.NAME, "tool": None, "runs": {"all": failed(exc)}}

    data = {
        "target": args.target,
        "run_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "packages": {name: package_version(name) for name in PACKAGES},
        },
        "ground_truth": GROUND_TRUTH,
        "methods": methods,
    }

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
