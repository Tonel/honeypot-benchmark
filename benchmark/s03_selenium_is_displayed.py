"""Scenario 3: Selenium is_displayed() in Chromium, Firefox and WebKit (Safari, macOS only)."""

import platform

from selenium import webdriver
from selenium.webdriver.common.by import By

from common import collect, failed, ok, package_version, unavailable

NAME = "Selenium is_displayed()"


def _chrome(target):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    return _measure(webdriver.Chrome(options=options), target)


def _firefox(target):
    options = webdriver.FirefoxOptions()
    options.add_argument("-headless")
    return _measure(webdriver.Firefox(options=options), target)


def _safari(target):
    # Selenium drives Safari through safaridriver, which only exists on macOS.
    if platform.system() != "Darwin":
        return unavailable("Selenium has no WebKit driver on this OS; safaridriver runs on macOS only")
    return _measure(webdriver.Safari(), target)


def _measure(driver, target):
    try:
        driver.get(target)
        pairs = []
        for element in driver.find_elements(By.CSS_SELECTOR, "a[href]"):
            href = driver.execute_script("return arguments[0].getAttribute('href')", element)
            pairs.append((href, not element.is_displayed()))
        return ok(driver.capabilities.get("browserVersion"), collect(pairs))
    finally:
        driver.quit()


def run(target):
    browsers = {}
    for name, opener in {"chromium": _chrome, "firefox": _firefox, "webkit": _safari}.items():
        try:
            browsers[name] = opener(target)
        except Exception as exc:
            browsers[name] = failed(exc)
    return {"name": NAME, "tool": f"selenium {package_version('selenium')}", "runs": browsers}
