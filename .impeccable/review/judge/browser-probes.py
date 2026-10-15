import json, time, traceback
from pathlib import Path
from patchright.sync_api import sync_playwright
OUT=Path.cwd()/".impeccable/review/judge"
CHROME="/opt/data/home/.linkedin-mcp/patchright-browsers/chromium-1243/chrome-linux64/chrome"
URL="http://127.0.0.1:3417"
report={"scope":"Independent local browser probes; no deployment","errors":[]}
def ev(p,js): return p.evaluate(js,isolated_context=False)
def state(p):
 return ev(p,"""()=>({state:window.sanctuaryState?.(),label:document.querySelector("#motion-label").textContent,pressed:document.querySelector("#motion-toggle").getAttribute("aria-pressed"),root:document.documentElement.className,lang:document.documentElement.lang,triggers:window.ScrollTrigger?.getAll().length,events:window.judgeEvents,marker:window.judgeMarker})""")
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path=CHROME,headless=True,ignore_default_args=["--disable-back-forward-cache"],args=["--disable-dev-shm-usage","--enable-webgl","--enable-unsafe-swiftshader"])
 try:
  c=b.new_context(viewport={"width":1440,"height":900},reduced_motion="no-preference")
  p=c.new_page();p.on("pageerror",lambda e:report["errors"].append(str(e)))
  p.goto(URL,wait_until="load");p.wait_for_timeout(3800)
  report["motion_before"]=state(p);p.wait_for_timeout(500);report["motion_after"]=state(p)
  ev(p,"""()=>{window.judgeEvents=[];window.judgeMarker=crypto.randomUUID();for(const name of ["pagehide","pageshow"]){addEventListener(name,e=>window.judgeEvents.push({type:e.type,persisted:e.persisted,time:performance.now()}));}}""")
  report["lifecycle_before"]=state(p)
  p.goto(URL+"/index.htm?judge-away=1",wait_until="load");p.wait_for_timeout(300)
  try: p.go_back(wait_until="commit",timeout=5000)
  except Exception as e: report["back_navigation_tool_note"]=str(e)
  p.wait_for_timeout(1000)
  report["lifecycle_return"]=state(p)
  p.click("#motion-toggle");p.wait_for_timeout(250);report["lifecycle_pause_click"]=state(p)
  p.click("#lang-bg");p.wait_for_timeout(250);report["lifecycle_bg_click"]=state(p)
  p.screenshot(path=str(OUT/"bfcache-return.png"))
  p.click("#motion-toggle");p.wait_for_timeout(500);report["lifecycle_resume_click"]=state(p)
  p.emulate_media(reduced_motion="reduce");p.wait_for_timeout(250);report["lifecycle_reduce"]=state(p)
  p.reload(wait_until="load");p.wait_for_timeout(350)
  ax=c.new_cdp_session(p);tree=ax.send("Accessibility.getFullAXTree")["nodes"]
  report["desktop_accessible_images"]=[{"name":n.get("name",{}).get("value"),"ignored":n.get("ignored")} for n in tree if n.get("role",{}).get("value")=="image"]
  report["desktop_source_images"]=ev(p,"""()=>[...document.querySelectorAll("main img")].map(i=>({src:i.getAttribute("src"),alt:i.alt,display:getComputedStyle(i.closest("figure")||i).display,hiddenAncestor:!!i.closest("[aria-hidden=true]")}))""")
  p.set_viewport_size({"width":390,"height":844});p.wait_for_timeout(300)
  tree=ax.send("Accessibility.getFullAXTree")["nodes"]
  report["mobile_accessible_images"]=[n.get("name",{}).get("value") for n in tree if n.get("role",{}).get("value")=="image"]
  report["narrow_layouts"]=[]
  for width in [320,901,920,1000,1024]:
   p.set_viewport_size({"width":width,"height":720});p.wait_for_timeout(250)
   report["narrow_layouts"].append(ev(p,"""()=>({width:innerWidth,overflow:document.documentElement.scrollWidth-innerWidth,header:[...document.querySelectorAll(".brand,.primary-nav,.header-tools")].map(e=>({name:e.className,rect:e.getBoundingClientRect().toJSON()}))})"""))
  c.close()
 except Exception as e:
  report["exception"]=traceback.format_exc()
 finally:
  b.close()
  (OUT/"browser-probes.json").write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
  print(json.dumps(report,indent=2,ensure_ascii=False))
