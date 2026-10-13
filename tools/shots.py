#!/usr/bin/env python3
"""Screenshot and verify the Silviya Aeterna page. One shot, browser closed at exit.

    uv run --with patchright python tools/shots.py http://127.0.0.1:43118 .impeccable/review

Writes desktop.png / mobile.png (full page), desktop-top.png / mobile-top.png (first
viewport), desktop-bg.png (language toggle proof) and prints a JSON report.
"""
import json
import sys
import tempfile
from pathlib import Path

from patchright.sync_api import sync_playwright

VIEWPORTS = [
    ("desktop", 1440, 900),
    ("mobile", 390, 844),
]


def find_chrome():
    import glob

    for root in (
        str(Path.home() / ".linkedin-mcp" / "patchright-browsers"),
        str(Path.home() / ".cache" / "ms-playwright"),
    ):
        hits = sorted(glob.glob(f"{root}/chromium*/chrome-linux*/chrome"))
        if hits:
            return hits[-1]
    return ""


def main() -> int:
    url = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:43118"
    out_dir = Path(sys.argv[2] if len(sys.argv) > 2 else ".impeccable/review")
    out_dir.mkdir(parents=True, exist_ok=True)

    report = {"url": url, "viewports": [], "console_errors": [], "failed_requests": []}
    chrome = find_chrome()

    with sync_playwright() as p:
        kwargs = dict(headless=True, args=["--disable-dev-shm-usage", "--no-sandbox"])
        if chrome:
            kwargs["executable_path"] = chrome
        ctx = p.chromium.launch_persistent_context(tempfile.mkdtemp(prefix="sa-shot-"), **kwargs)
        page = ctx.pages[0] if ctx.pages else ctx.new_page()

        page.on("console", lambda m: report["console_errors"].append(m.text) if m.type == "error" else None)
        page.on("pageerror", lambda e: report["console_errors"].append(f"pageerror: {e}"))
        page.on("requestfailed", lambda r: report["failed_requests"].append(f"{r.url} {r.failure}"))

        for name, width, height in VIEWPORTS:
            page.set_viewport_size({"width": width, "height": height})
            page.goto(url, wait_until="load", timeout=45000)
            page.wait_for_timeout(1400)

            base = page.evaluate(
                """() => ({
                  title: document.title,
                  h1: (document.querySelector('h1')||{}).textContent || null,
                  lang: document.documentElement.lang,
                  overflowX: document.documentElement.scrollWidth - document.documentElement.clientWidth,
                  images: [...document.images].map(i => ({src: i.currentSrc || i.src, ok: i.complete && i.naturalWidth > 0})),
                  hiddenReveal: [...document.querySelectorAll('[data-reveal]')].filter(e => getComputedStyle(e).opacity === '0' && e.getBoundingClientRect().top < innerHeight).length,
                  soonStates: [...document.querySelectorAll('.soon-state')].map(e => e.textContent.trim()),
                  soonAreLinks: [...document.querySelectorAll('.soon-state')].filter(e => e.closest('a,button')).length,
                  cta: [...document.querySelectorAll('.btn-primary')].map(e => ({text: e.textContent.trim(), href: e.getAttribute('href')})),
                  minTargets: Math.min(...[...document.querySelectorAll('a,button,summary')].filter(e => e.offsetParent !== null).map(e => Math.min(e.getBoundingClientRect().width, e.getBoundingClientRect().height))),
                })"""
            )

            # keyboard: focus must be visible on the first tab stop
            page.keyboard.press("Tab")
            focus = page.evaluate(
                """() => {
                  const el = document.activeElement;
                  if (!el || el === document.body) return {tag: null};
                  const s = getComputedStyle(el);
                  return {tag: el.tagName, text: (el.textContent||'').trim().slice(0,40),
                          outline: s.outlineStyle + ' ' + s.outlineWidth};
                }"""
            )
            page.keyboard.press("Escape")

            # language toggle
            page.click("#lang-bg")
            page.wait_for_timeout(250)
            bg = page.evaluate(
                """() => ({
                  lang: document.documentElement.lang,
                  sub: (document.querySelector('.hero-sub')||{}).textContent || '',
                  pressedEn: document.getElementById('lang-en').getAttribute('aria-pressed'),
                  pressedBg: document.getElementById('lang-bg').getAttribute('aria-pressed'),
                  nav: (document.querySelector('.primary-nav a')||{}).textContent || '',
                })"""
            )
            if name == "desktop":
                page.screenshot(path=str(out_dir / "desktop-bg.png"), full_page=False)
            page.click("#lang-en")
            page.wait_for_timeout(200)

            # scroll through so IntersectionObserver reveals run, then confirm nothing is hidden
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(1500)
            page.evaluate("window.scrollTo(0, 0)")
            page.wait_for_timeout(600)
            still_hidden = page.evaluate(
                """() => [...document.querySelectorAll('[data-reveal]')].filter(e => getComputedStyle(e).opacity === '0').length"""
            )
            images_after_scroll = page.evaluate(
                """() => [...document.images].filter(i => !(i.complete && i.naturalWidth > 0)).map(i => i.currentSrc || i.src)"""
            )

            page.screenshot(path=str(out_dir / f"{name}-top.png"), full_page=False)

            # full-page capture under reduced motion: entrance motion settled by design
            page.emulate_media(reduced_motion="reduce")
            page.reload(wait_until="load", timeout=45000)
            page.wait_for_timeout(900)
            reduced = page.evaluate(
                """() => ({
                  hidden: [...document.querySelectorAll('[data-reveal]')].filter(e => getComputedStyle(e).opacity === '0').length,
                  overflowX: document.documentElement.scrollWidth - document.documentElement.clientWidth,
                })"""
            )
            page.screenshot(path=str(out_dir / f"{name}.png"), full_page=True)
            page.emulate_media(reduced_motion="no-preference")

            report["viewports"].append(
                {
                    "name": name,
                    "width": width,
                    "height": height,
                    "title": base["title"],
                    "h1": base["h1"],
                    "lang": base["lang"],
                    "overflowX_px": base["overflowX"],
                    "images_total": len(base["images"]),
                    "images_not_loaded_at_top": base["images"],
                    "images_failed_after_scroll": images_after_scroll,
                    "hidden_reveals_in_view": base["hiddenReveal"],
                    "hidden_after_scroll": still_hidden,
                    "hidden_under_reduced_motion": reduced["hidden"],
                    "overflowX_reduced": reduced["overflowX"],
                    "min_visible_target_px": base["minTargets"],
                    "focus_after_tab": focus,
                    "coming_soon_states": base["soonStates"],
                    "coming_soon_wrapped_in_control": base["soonAreLinks"],
                    "primary_ctas": base["cta"],
                    "bg_toggle": bg,
                }
            )

        ctx.close()

    issues = []
    for view in report["viewports"]:
        if view["overflowX_px"] > 0 or view["overflowX_reduced"] > 0:
            issues.append(f"{view['name']}: horizontal overflow")
        if view["images_failed_after_scroll"]:
            issues.append(f"{view['name']}: images failed {view['images_failed_after_scroll']}")
        if view["hidden_after_scroll"] or view["hidden_under_reduced_motion"]:
            issues.append(f"{view['name']}: content left hidden")
        if view["min_visible_target_px"] < 44:
            issues.append(f"{view['name']}: touch target under 44px")
        if view["bg_toggle"]["lang"] != "bg" or "Астрология" not in view["bg_toggle"]["sub"]:
            issues.append(f"{view['name']}: language toggle failed")
        if view["coming_soon_wrapped_in_control"]:
            issues.append(f"{view['name']}: coming soon state wrapped in a control")
    if report["console_errors"]:
        issues.append(f"console errors: {report['console_errors']}")
    if report["failed_requests"]:
        issues.append(f"failed requests: {report['failed_requests']}")
    report["issues"] = issues

    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 1 if issues else 0


if __name__ == "__main__":
    sys.exit(main())
