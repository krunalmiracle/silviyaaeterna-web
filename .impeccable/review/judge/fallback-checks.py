import json,traceback
from pathlib import Path
from patchright.sync_api import sync_playwright
O=Path.cwd()/".impeccable/review/judge";U="http://127.0.0.1:3417"
C="/opt/data/home/.linkedin-mcp/patchright-browsers/chromium-1243/chrome-linux64/chrome"
r={"checks":[],"states":{},"errors":[]}
def ev(p,s): return p.evaluate(s,isolated_context=False)
def st(p): return ev(p,"window.sanctuaryState()")
def check(n,v): r["checks"].append({"name":n,"passed":bool(v)})
with sync_playwright() as w:
 b=w.chromium.launch(executable_path=C,headless=True,args=["--disable-dev-shm-usage","--enable-webgl","--enable-unsafe-swiftshader"])
 try:
  c=b.new_context(viewport={"width":1440,"height":900},reduced_motion="no-preference");p=c.new_page();p.on("pageerror",lambda e:r["errors"].append(str(e)))
  p.goto(U);p.wait_for_timeout(3600)
  p.click("#motion-toggle");p.wait_for_timeout(150);s=st(p);p.wait_for_timeout(400);check("normal pause stops frames",s["paused"] and not s["running"] and s["frames"]==st(p)["frames"])
  check("normal pause disables CSS atlas transitions",ev(p,"getComputedStyle(document.querySelector(\".stage-images img\")).transitionDuration")=="0s")
  p.reload();p.wait_for_timeout(300);check("pause persists after reload",st(p)["paused"] and not st(p)["running"])
  p.click("#motion-toggle");p.wait_for_timeout(350);check("resume reinitializes renderer",st(p)["running"])
  p.emulate_media(reduced_motion="reduce");p.wait_for_timeout(100);s=st(p);p.wait_for_timeout(300);check("live reduced motion stops frames",s["reduced"] and not s["running"] and s["frames"]==st(p)["frames"])
  p.emulate_media(reduced_motion="no-preference");p.wait_for_timeout(300);check("live no-preference resumes",st(p)["running"])
  ev(p,"document.querySelector(\"#atlas\").scrollIntoView()");p.wait_for_timeout(250);s=st(p);p.wait_for_timeout(350);check("offscreen stops frames",not s["inView"] and not s["running"] and s["frames"]==st(p)["frames"])
  ev(p,"scrollTo(0,0)");p.wait_for_timeout(350);check("onscreen resumes",st(p)["running"])
  p.set_viewport_size({"width":390,"height":844});p.wait_for_timeout(350);s=st(p);p.wait_for_timeout(300);check("mobile stops desktop shader",not s["running"] and s["frames"]==st(p)["frames"])
  p.set_viewport_size({"width":1440,"height":900});p.wait_for_timeout(350);check("desktop resize resumes shader",st(p)["running"])
  ev(p,"document.querySelector(\"canvas\").getContext(\"webgl\").getExtension(\"WEBGL_lose_context\").loseContext()");p.wait_for_timeout(300);s=st(p);check("context loss static fallback",s["renderer"]=="static" and not s["running"]);r["states"]["context_loss"]=s
  p.emulate_media(reduced_motion="reduce");p.reload();p.wait_for_timeout(300);check("initial reduced motion",st(p)["frames"]==0 and not st(p)["running"])
  for lang in ["en","bg"]:
   p.click("#lang-"+lang)
   for theme in ["astrology","numerology","skincare","wellbeing","family","mental-health"]:
    p.locator(".theme-nav [data-theme=\""+theme+"\"]").click();p.wait_for_timeout(100)
    check(lang+" theme "+theme,st(p)["activeScene"]==theme and p.locator("#"+theme+" details").get_attribute("open") is not None and ev(p,"document.activeElement.id")==theme)
  c.close()
  c=b.new_context(viewport={"width":1440,"height":900},reduced_motion="no-preference");p=c.new_page()
  p.add_init_script("const old=HTMLCanvasElement.prototype.getContext;HTMLCanvasElement.prototype.getContext=function(t,...args){return /webgl/.test(t)?null:old.call(this,t,...args)}")
  p.goto(U);p.wait_for_timeout(350);check("no WebGL uses original hero",st(p)["renderer"]=="static" and ev(p,"document.querySelector(\".hero-art img\").naturalWidth>0"));c.close()
  c=b.new_context(java_script_enabled=False,viewport={"width":390,"height":844});p=c.new_page();p.goto(U)
  check("no-JS six topics visible",p.locator(".topic").count()==6 and all(x.is_visible() for x in p.locator(".topic h3").all()))
  p.locator("#family summary").click();check("no-JS native disclosure",p.locator("#family details").get_attribute("open") is not None)
  p.locator(".nav-more summary").click();check("no-JS native menu",p.locator(".mobile-nav a").first.is_visible());c.close()
 except Exception: r["exception"]=traceback.format_exc()
 finally:
  b.close();r["total"]=len(r["checks"]);r["passed"]=sum(x["passed"] for x in r["checks"]);(O/"fallback-checks.json").write_text(json.dumps(r,indent=2)+"\n");print(json.dumps(r,indent=2))
