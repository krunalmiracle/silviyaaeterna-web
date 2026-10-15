"""Real BFCache and bilingual AX-tree regressions for sanctuary review fixes."""
from pathlib import Path
import json,sys
from patchright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'.impeccable/review/fix';OUT.mkdir(parents=True,exist_ok=True)
phase=sys.argv[1] if len(sys.argv)>1 else 'green'
URL='http://127.0.0.1:3417';CHROME='/opt/data/home/.linkedin-mcp/patchright-browsers/chromium-1243/chrome-linux64/chrome'
report={'checks':[],'errors':[],'states':[],'ax':[]}
def check(ok,name):report['checks'].append({'name':name,'passed':bool(ok)})
def ev(page,source):return page.evaluate(source,isolated_context=False)
def state(page):return ev(page,"({state:window.sanctuaryState(),label:document.querySelector('#motion-label').textContent,pressed:document.querySelector('#motion-toggle').getAttribute('aria-pressed'),classes:document.documentElement.className,triggers:window.ScrollTrigger.getAll().length,marker:window.returnMarker,events:window.returnEvents})")
with sync_playwright() as pw:
 browser=pw.chromium.launch(executable_path=CHROME,headless=True,ignore_default_args=['--disable-back-forward-cache'],args=['--disable-dev-shm-usage','--enable-webgl','--enable-unsafe-swiftshader'])
 try:
  context=browser.new_context(viewport={'width':1440,'height':900},reduced_motion='no-preference');page=context.new_page();page.on('pageerror',lambda e:report['errors'].append(str(e)))
  page.goto(URL);page.wait_for_timeout(900)
  ev(page,"window.returnMarker=crypto.randomUUID();window.returnEvents=[];for(const type of ['pagehide','pageshow'])addEventListener(type,e=>window.returnEvents.push({type,persisted:e.persisted}))")
  first=state(page);report['states'].append({'first':first})
  def roundtrip(number):
   page.goto(URL+'/index.htm?lifecycle-away='+str(number));page.wait_for_timeout(150);page.go_back(wait_until='commit');page.wait_for_timeout(500)
   result=state(page);report['states'].append({'return':number,**result})
   check(result['marker']==first['marker'] and any(e['type']=='pageshow' and e['persisted'] for e in result['events']),f'{number}: actual BFCache restore')
   return result
  returned=roundtrip(1);frame=returned['state']['frames'];page.wait_for_timeout(400)
  check(ev(page,'window.sanctuaryState().frames')>frame and returned['triggers']>=5,'restored renderer and ScrollTriggers run')
  page.click('#motion-toggle');page.wait_for_timeout(180);paused=state(page);report['states'].append({'paused':paused})
  check(paused['state']['paused'] and not paused['state']['running'] and paused['pressed']=='true' and 'motion-off' in paused['classes'] and paused['label']=='Resume motion','post-return pause synchronizes renderer, CSS, label and aria')
  page.click('#lang-bg');page.wait_for_timeout(180);check(state(page)['label']=='Пусни движението','post-return Bulgarian label updates')
  returned=roundtrip(2)
  check(returned['state']['paused'] and not returned['state']['running'] and returned['pressed']=='true' and returned['label']=='Пусни движението','paused preference survives second native return')
  page.click('#motion-toggle');page.wait_for_timeout(500);resumed=state(page)
  check(not resumed['state']['paused'] and resumed['state']['running'] and resumed['pressed']=='false' and resumed['label']=='Спри движението','resume works after repeated return')
  page.emulate_media(reduced_motion='reduce');page.wait_for_timeout(180);returned=roundtrip(3)
  check(returned['state']['reduced'] and not returned['state']['running'] and returned['triggers']==0 and returned['label']=='Намалено движение' and 'motion-off' in returned['classes'],'live reduced motion survives third native return')
  page.screenshot(path=str(OUT/(phase+'-restored-bg.png')))
  manifest=json.loads((ROOT/'tools/ASSET-MANIFEST.json').read_text())
  ax=context.new_cdp_session(page)
  for width in [1440,390]:
   page.set_viewport_size({'width':width,'height':900 if width==1440 else 844})
   for lang in ['en','bg']:
    page.click('#lang-'+lang);page.wait_for_timeout(150)
    nodes=ax.send('Accessibility.getFullAXTree')['nodes']
    by_id={node['nodeId']:node for node in nodes}
    def in_reading_order(node):
     yield node
     for child in node.get('childIds',[]):
      if child in by_id:yield from in_reading_order(by_id[child])
    actual=[n.get('name',{}).get('value') for n in in_reading_order(nodes[0]) if n.get('role',{}).get('value')=='image' and not n.get('ignored',False)]
    expected=[a['alt'][lang] for a in manifest['assets']]
    report['ax'].append({'width':width,'lang':lang,'actual':actual,'expected':expected})
    check(actual==expected,f'AX {width} {lang}: exactly eight localized source descriptions in document order')
  context.close()
 finally:browser.close()
report['passed']=sum(c['passed'] for c in report['checks']);report['total']=len(report['checks']);report['failed']=[c['name'] for c in report['checks'] if not c['passed']]
(OUT/(phase+'-regression.json')).write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
print(json.dumps({'phase':phase,'passed':report['passed'],'total':report['total'],'failed':report['failed'],'errors':report['errors']},indent=2))
raise SystemExit(0 if not report['failed'] and not report['errors'] else 1)
