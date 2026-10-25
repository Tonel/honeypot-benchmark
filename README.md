# Honeypot trap test site

A static, one-page test site for checking how well link-visibility methods detect hidden honeypot links. It is a fictional landing page for a wizard-for-hire business, with:

- **20 trap links**, each hidden a different way, with a unique `trap/NN-…` URL so a result can be tied to the method that produced it.
- **5 control links** that a person can see or use, and that a detector must not flag: a skip link, a link in a collapsed mobile menu, a link below the fold, a lazy-loaded link and a low-contrast footer link.

It is plain HTML, CSS and JavaScript with no build step.

## Live site

Once GitHub Pages is enabled for this repo (see below), the site is served at:

`https://tonel.github.io/honeypot-benchmark/`

## Repository layout

| Path             | Purpose                                                                              |
| ---------------- | ------------------------------------------------------------------------------------ |
| `index.html`     | The landing page with all trap and control links                                     |
| `styles.css`     | Layout, and one class per CSS-based trap                                             |
| `script.js`      | Mobile menu + trap 16 (hidden 500 ms after load) + lazy-loaded control link handling |
| `robots.txt`     | Disallows `/trap/` for trap 20                                                       |
| `pyproject.toml` | Python dependencies for the test and benchmark tooling                               |

## Trap and control reference

### Traps:

| #   | Method                                               | href                              |
| --- | ---------------------------------------------------- | --------------------------------- |
| 1   | Inline `display:none`                                | `trap/01-inline-display-none`     |
| 2   | `display:none` from a stylesheet                     | `trap/02-stylesheet-display-none` |
| 3   | `visibility:hidden`                                  | `trap/03-visibility-hidden`       |
| 4   | `opacity:0`                                          | `trap/04-opacity-zero`            |
| 5   | `opacity:0` on the parent                            | `trap/05-opacity-parent`          |
| 6   | Zero width and height                                | `trap/06-zero-size`               |
| 7   | `font-size:0`                                        | `trap/07-font-size-zero`          |
| 8   | `left:-9999px`                                       | `trap/08-left-minus-9999`         |
| 9   | `transform: translateX(-200vw)`                      | `trap/09-translate-200vw`         |
| 10  | `clip-path: inset(100%)`                             | `trap/10-clip-path`               |
| 11  | `clip: rect(0 0 0 0)`                                | `trap/11-clip-rect`               |
| 12  | Text the same colour as the background               | `trap/12-same-colour`             |
| 13  | Covered by an overlay                                | `trap/13-covered-by-overlay`      |
| 14  | `hidden` attribute                                   | `trap/14-hidden-attribute`        |
| 15  | `aria-hidden="true"` only                            | `trap/15-aria-hidden`             |
| 16  | Hidden by JavaScript 500 ms after load               | `trap/16-hidden-after-500ms`      |
| 17  | Inside a `<noscript>` element                        | `trap/17-noscript`                |
| 18  | Inside an HTML comment                               | `trap/18-html-comment`            |
| 19  | `content-visibility:hidden`                          | `trap/19-content-visibility`      |
| 20  | `nofollow` link to a path disallowed in `robots.txt` | `trap/20-robots-disallowed`       |

### Controls:

| Control                         | href                                                                                         |
| ------------------------------- | -------------------------------------------------------------------------------------------- |
| Skip to content                 | `#skip-to-content`                                                                           |
| Collapsed mobile menu           | `control/mobile-offer`                                                                       |
| Below the fold                  | `control/below-fold-price-list`                                                              |
| Lazy-loaded                     | `control/lazy-loaded-newsletter`                                                             |
| Low-contrast footer             | `control/low-contrast-cookie-settings`                                                       |

## Benchmark

`benchmark/` runs eight link-detection methods against the live page and writes every result to one file, `results/benchmark.json`. Scenarios 9 and 10 use the ScrapingBee API, so they need an API key. Every Playwright, Selenium, or ScrapingBee scenario does a plain page load with the tool's default settings: no waiting, scrolling or other setup.

| Script                            | Method                                                                                               | Runs on                            |
| --------------------------------- | ---------------------------------------------------------------------------------------------------- | ---------------------------------- |
| `s01_bs4_find_all.py`             | BeautifulSoup `find_all('a')`                                                                        | Static HTML                        |
| `s02_bs4_inline_style.py`         | BeautifulSoup with an inline-style filter                                                            | Static HTML                        |
| `s03_selenium_is_displayed.py`    | Selenium `is_displayed()`                                                                            | Chromium, Firefox, WebKit (Safari) |
| `s04_playwright_is_visible.py`    | Playwright `is_visible()`                                                                            | Chromium, Firefox, WebKit          |
| `s05_playwright_click_trial.py`   | Playwright `click(trial=True)`                                                                       | Chromium, Firefox, WebKit          |
| `s06_check_visibility_default.py` | `Element.checkVisibility()`, default options                                                         | Chromium, Firefox, WebKit          |
| `s07_check_visibility_all.py`     | `Element.checkVisibility()` with `opacityProperty`, `visibilityProperty` and `contentVisibilityAuto` | Chromium, Firefox, WebKit          |
| `s08_custom_check.py`             | Custom check: computed style, box, contrast, overlap                                                 | Chromium, Firefox, WebKit          |
| `s09_scrapingbee_markdown.py`     | ScrapingBee with JavaScript rendering and markdown output                                            | ScrapingBee cloud                  |
| `s10_scrapingbee_ai_extract.py`   | ScrapingBee AI extraction, "all links on the page"                                                   | ScrapingBee cloud                  |
| `common.py`                       | Target URL, ground truth, result helpers                                                             |                                    |
| `benchmark.py`                    | Runs every scenario and writes the JSON                                                              |                                    |

### Setup

1. Install the pinned Python packages and the Playwright browsers. Run these from the repo root with your virtual environment active:

   ```bash
   pip install -e .
   playwright install chromium firefox webkit
   ```

   On Linux, also run `playwright install-deps` so WebKit can start.

2. Selenium drives the browsers installed on your machine. Install Google Chrome and Mozilla Firefox. Selenium Manager downloads the matching chromedriver and geckodriver on the first run, so an internet connection is needed.

3. Selenium with Safari needs macOS. Run `sudo safaridriver --enable` once. In Safari, enable **Settings → Advanced → Show features for web developers**, then **Develop → Allow Remote Automation**. On Windows and Linux, scenario 3 records WebKit as `unavailable`. Playwright's WebKit (scenarios 4–8) works on all three systems.

4. ScrapingBee (scenarios 9 and 10). Copy `.env.sample` to `.env` and replace the value with your [ScrapingBee API key](https://www.scrapingbee.com/documentation/#getting-started). Scenario 9 costs `5` credits per page (JavaScript rendering). Scenario 10 costs `10` credits (5 for rendering and 5 for AI extraction). Each of these runs records the credits charged in its `credits` field.

### Run

```bash
python benchmark/benchmark.py                                  # all scenarios, live page
python benchmark/benchmark.py --only 03 04                     # selected scenarios
python benchmark/benchmark.py --target http://localhost:8000/  # a local copy, after `python -m http.server 8000`
```

### Output

`results/benchmark.json` contains:

- `target`, `run_at`, and `environment` (Python, OS, and package versions).
- `ground_truth`: The 20 traps and 5 controls, with `kind`, `number` and `label`.
- `methods`: One entry per scenario, with its `name`, the `tool` and its version, and `runs`. Each run is keyed by where the method ran: `static_html` for scenarios 1 and 2, `scrapingbee` for scenarios 9 and 10, otherwise `chromium`, `firefox` or `webkit`. Runs for scenarios 9 and 10 also have `credits` (number of credits spent via the ScrapingBee API) and `output` (the markdown or AI answer, as returned). A run has a `version` (`null` for static HTML) and two maps: `hidden_traps` (the 20 traps) and `controls` (the 5 controls). Each link has one boolean, `marked_as_hidden`. A trap is caught when it is `true`. A trap that is not on the page, such as trap 17 or 18 in a browser run, is `false`. For a control, `true` is a false positive. A run that could not start has `unavailable` (the reason) or `error` instead of these maps.
