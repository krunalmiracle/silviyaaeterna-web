"""Independent instrumentation, real headed visibility, axe, performance."""
from pathlib import Path
import json,os,subprocess,time,statistics
from patchright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'.impeccable/review'
chrome='/opt/data/home/.linkedin-mcp/patchright-browsers/chromium-1243/chrome-linux64/chrome'
report={'axe':[],'performance':{},'visibility':{},'checks':[]}
def check(value,name):report['checks'].append({'name':name,'passed':bool(value)})
display=next(n for n in range(92,120) if not Path(f'/tmp/.X11-unix/X{n}').exists())
xvfb=subprocess.Popen(['Xvfb',f':{display}','-screen','0','1600x1000x24','-nolisten','tcp'],stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
try:
 for _ in range(50):
  if Path(f'/tmp/.X11-unix/X{display}').exists():break
  if xvfb.poll() is not None:raise RuntimeError('Task Xvfb failed')
  time.sleep(.1)
 with sync_playwright() as p:
  b=p.chromium.launch(executable_path=chrome,headless=False,env={**os.environ,'DISPLAY':f':{display}'},args=['--disable-dev-shm-usage','--enable-webgl','--enable-unsafe-swiftshader'])
  try:
   c=b.new_context(viewport={'width':1440,'height':900},reduced_motion='no-preference')
   page=c.new_page()
   page.add_init_script("window.perfAudit={lcp:[],longTasks:[]};new PerformanceObserver(list=>{for(const e of list.getEntries())window.perfAudit.lcp.push({start:e.startTime,size:e.size})}).observe({type:'largest-contentful-paint',buffered:true});new PerformanceObserver(list=>{for(const e of list.getEntries())window.perfAudit.longTasks.push({start:e.startTime,duration:e.duration})}).observe({type:'longtask',buffered:true})")
   page.goto('http://127.0.0.1:3417');page.wait_for_timeout(2500)
   report['performance']=page.evaluate("({observed:window.perfAudit,resources:performance.getEntriesByType('resource').map(r=>({name:new URL(r.name).pathname,bytes:r.transferSize,duration:r.duration})),navigation:performance.getEntriesByType('navigation')[0].toJSON(),state:window.sanctuaryState()})",isolated_context=False)
   report['performance']['throttling']='No network or CPU throttling; local host, software WebGL under Xvfb. Not field-performance metrics.'
   page.wait_for_timeout(400);before=page.evaluate('window.sanctuaryState()',isolated_context=False)
   # Raw CDP avoids Patchright evaluation auto-activating the target page.
   cdp=c.new_cdp_session(page)
   other=c.new_page();other.goto('about:blank');other.bring_to_front();time.sleep(.3)
   hidden=cdp.send('Runtime.evaluate',{'expression':'({hidden:document.hidden,state:window.sanctuaryState()})','returnByValue':True})['result']['value'];time.sleep(.65)
   after=cdp.send('Runtime.evaluate',{'expression':'window.sanctuaryState()','returnByValue':True})['result']['value']
   report['visibility']={'before':before,'hidden':hidden,'after':after,'mechanism':'Actual second foreground tab in headed Chromium under task-owned Xvfb'}
   report['visibility']['limitation']='Chromium reports document.hidden=false for the background target in this automation setup. Actual frame production is measured independently; the hidden visibilitychange handler is tested separately in browser-report.json.'
   check(hidden['state']['frames']==after['frames'] and after['frames']>before['frames'],'actual background tab stops frame production')
   other.close();page.bring_to_front();page.wait_for_timeout(400)
   check(page.evaluate('window.sanctuaryState().running',isolated_context=False),'foreground resumes shader')
   page.emulate_media(reduced_motion='reduce')
   source=(ROOT/'node_modules/axe-core/axe.min.js').read_text()
   for width,lang in [(1440,'en'),(1440,'bg'),(390,'en'),(390,'bg')]:
    page.set_viewport_size({'width':width,'height':900 if width==1440 else 844});page.goto('http://127.0.0.1:3417');page.click('#lang-'+lang);page.evaluate(source,isolated_context=False)
    results=page.evaluate("async()=>{const r=await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa']}});return {violations:r.violations.map(x=>({id:x.id,impact:x.impact,help:x.help,nodes:x.nodes.map(n=>({target:n.target,summary:n.failureSummary}))})),incomplete:r.incomplete.map(x=>({id:x.id,nodes:x.nodes.map(n=>n.target)})),passes:r.passes.length}}",isolated_context=False)
    results.update({'width':width,'lang':lang});report['axe'].append(results);check(not results['violations'],f'axe {width} {lang}: no WCAG A/AA violations')
   c.close()
  finally:b.close()
finally:
 xvfb.terminate()
 try:xvfb.wait(timeout=5)
 except subprocess.TimeoutExpired:xvfb.kill();xvfb.wait()
 (OUT/'accessibility-performance.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
 print(json.dumps({'checks':report['checks'],'violations':[{'width':r['width'],'lang':r['lang'],'violations':r['violations']} for r in report['axe']],'visibility':report['visibility'],'performance':report['performance'].get('observed')},indent=2))
raise SystemExit(0 if all(c['passed'] for c in report['checks']) else 1)
