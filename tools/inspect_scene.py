from patchright.sync_api import sync_playwright
from pathlib import Path
root=Path(__file__).resolve().parents[1]
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/opt/data/home/.linkedin-mcp/patchright-browsers/chromium-1243/chrome-linux64/chrome',headless=True,args=['--disable-dev-shm-usage'])
 try:
  page=b.new_page(viewport={'width':390,'height':844},reduced_motion='reduce');page.goto('http://127.0.0.1:3417');page.locator('#astrology').scroll_into_view_if_needed();page.wait_for_timeout(700)
  print(page.locator('#astrology').evaluate("e=>({article:e.getBoundingClientRect().toJSON(),figure:e.querySelector('figure').getBoundingClientRect().toJSON(),image:e.querySelector('img').getBoundingClientRect().toJSON(),imgCSS:[getComputedStyle(e.querySelector('img')).opacity,getComputedStyle(e.querySelector('img')).visibility,getComputedStyle(e.querySelector('figure')).display],natural:e.querySelector('img').naturalWidth})"))
  page.screenshot(path=str(root/'.impeccable/review/mobile-astrology-debug.png'))
 finally:b.close()
