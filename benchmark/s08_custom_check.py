"""Scenario 8: the custom check (computed style, bounding box, contrast and overlap) in Chromium,
Firefox and WebKit. A link is flagged when is_safe_link returns False."""

from common import package_version, run_playwright

NAME = "Custom check (computed style, box, contrast, overlap) via Playwright"

SAFE_LINK_JS = r"""
(el) => {
  const rgba = (css) => css.match(/[\d.]+/g).map(Number);
  const lum = (rgb) => {
    const [r, g, b] = rgb.slice(0, 3).map((c) => (c /= 255) <= 0.03928 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4);
    return 0.2126 * r + 0.7152 * g + 0.0722 * b;
  };
  const contrast = (a, b) => (Math.max(lum(a), lum(b)) + 0.05) / (Math.min(lum(a), lum(b)) + 0.05);

  // Ancestor walk: display and clip-path are per element, opacity multiplies down the chain.
  let opacity = 1;
  for (let n = el; n; n = n.parentElement) {
    const cs = getComputedStyle(n);
    if (cs.display === 'none' || /inset\(\s*100%/.test(cs.clipPath)) return false;
    opacity *= parseFloat(cs.opacity);
  }
  if (getComputedStyle(el).visibility === 'hidden' || opacity < 0.05) return false;

  // Bounding box against the page. Skip links are off-page until focused, so focus and re-measure.
  const box = el.getBoundingClientRect();
  if (!box.width || !box.height) return false;
  if (box.left + scrollX + box.width <= 0 || box.top + scrollY + box.height <= 0 ||
      box.left + scrollX >= document.documentElement.scrollWidth) {
    el.focus({ preventScroll: true });
    const focused = el.getBoundingClientRect();
    el.blur();
    if (focused.right <= 0 || focused.bottom <= 0 || focused.left >= innerWidth || focused.top >= innerHeight) {
      return false;
    }
  }

  // Contrast: text colour against the nearest opaque background (white if none).
  let bg = [255, 255, 255];
  for (let n = el; n; n = n.parentElement) {
    const c = rgba(getComputedStyle(n).backgroundColor);
    if ((c[3] ?? 1) > 0) { bg = c; break; }
  }
  if (el.textContent.trim() && contrast(rgba(getComputedStyle(el).color), bg) < 1.2) return false;

  // Overlap: the element on top at the link's centre must be the link or inside it.
  el.scrollIntoView({ block: 'center', behavior: 'instant' }); // hit-testing only works in the viewport
  const first = el.getClientRects()[0]; // first line box, so wrapped links are tested on text
  const x = first.left + first.width / 2;
  const y = first.top + first.height / 2;
  if (x < 0 || y < 0 || x >= innerWidth || y >= innerHeight) return true;
  const hit = document.elementFromPoint(x, y);
  return !hit || el.contains(hit);
}
"""


def check(page):
    pairs = []
    for handle in page.query_selector_all("a[href]"):
        pairs.append((handle.get_attribute("href"), not handle.evaluate(SAFE_LINK_JS)))
    return pairs


def run(target):
    return {"name": NAME, "tool": f"playwright {package_version('playwright')}", "runs": run_playwright(target, check)}
