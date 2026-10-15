"""Bounded browser verification. Never fabricates frames; owns all browsers."""
import argparse,json,time
from pathlib import Path
from datetime import datetime,timezone
from patchright.sync_api import sync_playwright, Page
# Patchright defaults to an isolated evaluation world. Diagnostics and browser
# fallback injection must use the real page world, not a separate Window.
_original_evaluate=Page.evaluate
def live_evaluate(self,expression,arg=None,**kwargs):
    kwargs.setdefault('isolated_context',False)
    return _original_evaluate(self,expression,arg,**kwargs)
Page.evaluate=live_evaluate
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'.impeccable/review'; OUT.mkdir(exist_ok=True,parents=True)
CHROME='/opt/data/home/.linkedin-mcp/patchright-browsers/chromium-1243/chrome-linux64/chrome'
args=argparse.ArgumentParser();args.add_argument('--url',default='http://127.0.0.1:3417');args.add_argument('--inspect',action='store_true');args.add_argument('--release',action='store_true');a=args.parse_args()
report={'url':a.url,'capturedAt':datetime.now(timezone.utc).isoformat(),'checks':[],'viewports':[],'consoleErrors':[],'externalRequests':[],'failedRequests':[],'httpErrors':[],'screenshots':[]}
def check(value,name,detail=None):
    report['checks'].append({'name':name,'passed':bool(value),'detail':detail})
def attach(page):
    page.on('pageerror',lambda e:report['consoleErrors'].append(str(e)))
    page.on('console',lambda m:report['consoleErrors'].append(m.text) if m.type=='error' else None)
    page.on('request',lambda r:report['externalRequests'].append(r.url) if not r.url.startswith(a.url) else None)
    page.on('requestfailed',lambda r:report['failedRequests'].append({'url':r.url,'failure':r.failure}))
    page.on('response',lambda r:report['httpErrors'].append({'url':r.url,'status':r.status}) if r.status>=400 else None)
def shot(page,name,full=False):
    path=OUT/(('production-' if a.release else '')+name+'.png');page.screenshot(path=str(path),full_page=full)
    report['screenshots'].append(str(path.relative_to(ROOT)))
def settle(page):
    page.evaluate('document.fonts.ready')
    page.evaluate('''async()=>{for(const img of document.images){img.loading='eager';await img.decode().catch(()=>{});}}''')
    for image in page.locator('.topic-art img,.closing-art img').all():
        if image.is_visible():
            image.scroll_into_view_if_needed();page.wait_for_timeout(70)
    page.evaluate('scrollTo(0,0)');page.wait_for_timeout(180)
def inspect(page):
    return page.evaluate('''()=>{
      const visible=e=>e.checkVisibility({visibilityProperty:true}) && !(e.closest('details:not([open])')&&!e.closest('summary'));
      const targets=[...document.querySelectorAll('a,button,summary')].filter(visible).filter(e=>!e.classList.contains('skip-link'));
      const clipped=[...document.querySelectorAll('h1,h2,h3,p,a,summary')].filter(visible).filter(e=>!e.classList.contains('skip-link')).filter(e=>{const r=e.getBoundingClientRect();return r.left<-.5||r.right>innerWidth+.5||e.scrollWidth>e.clientWidth+1;}).map(e=>e.textContent.trim().slice(0,70));
      return {lang:document.documentElement.lang,width:innerWidth,overflowX:document.documentElement.scrollWidth-innerWidth,clipped,smallTargets:targets.filter(e=>{const r=e.getBoundingClientRect();return r.width<43.9||r.height<43.9}).map(e=>e.textContent.trim()),images:[...document.querySelectorAll('main img')].map(i=>({src:i.currentSrc||i.src,decoded:i.complete&&i.naturalWidth>0})),state:window.sanctuaryState?.(),heroH1:document.querySelector('h1').getBoundingClientRect().toJSON(),heroLinks:document.querySelector('.hero-links').getBoundingClientRect().toJSON(),cta:document.querySelector('.primary-action').getBoundingClientRect().toJSON()};
    }''')
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path=CHROME,headless=True,args=['--disable-dev-shm-usage','--enable-webgl','--enable-unsafe-swiftshader'])
    try:
        context=browser.new_context(viewport={'width':1440,'height':900},reduced_motion='reduce')
        page=context.new_page();attach(page)
        variants=[('desktop',1440,900),('mobile',390,844)] if a.inspect or a.release else [('desktop',1440,900),('mobile',390,844),('compact',320,844),('tablet',768,1024),('laptop',1024,900),('comp',1672,941)]
        for lang in ['en','bg']:
            for name,width,height in variants:
                page.set_viewport_size({'width':width,'height':height});page.goto(a.url,wait_until='load');page.click('#lang-'+lang);page.reload(wait_until='load');settle(page)
                result=inspect(page);result['name']=name;report['viewports'].append(result)
                check(result['lang']==lang,name+'-'+lang+': persisted language')
                check(result['overflowX']==0 and not result['clipped'],name+'-'+lang+': no clipping or overflow',result['clipped'])
                check(not result['smallTargets'],name+'-'+lang+': 44px targets',result['smallTargets'])
                check(all(i['decoded'] for i in result['images']),name+'-'+lang+': all images decoded')
                check(page.evaluate("document.fonts.check('300 48px Sanctuary','Любопитство')"),name+'-'+lang+': Cyrillic display font')
                check(result['state']['frames']==0 and not result['state']['running'],name+'-'+lang+': initial reduced motion')
                if name in ['desktop','mobile','comp']:
                    shot(page,name+'-'+lang+'-top');shot(page,name+'-'+lang+'-full',True)
                if a.inspect: continue
                for theme in ['astrology','numerology','skincare','wellbeing','family','mental-health']:
                    page.locator('.theme-nav [data-theme="'+theme+'"]').click();page.wait_for_timeout(180)
                    check(page.locator('#'+theme+' details').get_attribute('open') is not None,name+'-'+lang+': opens '+theme)
                    check(page.evaluate('(id)=>document.activeElement.id===id',theme),name+'-'+lang+': focus '+theme)
                    check(page.locator('#'+theme).bounding_box()['y']>=25,name+'-'+lang+': anchor headroom '+theme)
                    if name=='desktop' and lang=='en':
                        check(page.evaluate('window.sanctuaryState().activeScene')==theme,'stage scene '+theme)
                        shot(page,'scene-'+theme)
                if width<=900:
                    page.evaluate('scrollTo(0,0)');page.locator('.nav-more summary').click()
                    check(page.locator('.nav-more').get_attribute('open') is not None,name+'-'+lang+': menu opens')
                    if name=='mobile':shot(page,'mobile-menu-'+lang)
                    page.keyboard.press('Escape')
                    check(page.locator('.nav-more').get_attribute('open') is None and page.locator('.nav-more summary').evaluate('(e)=>e===document.activeElement'),name+'-'+lang+': Escape restores focus')
        if a.release:
            page.set_viewport_size({'width':1440,'height':900});page.emulate_media(reduced_motion='no-preference');page.goto(a.url);settle(page);page.wait_for_timeout(1800)
            before=page.evaluate('window.sanctuaryState()');page.wait_for_timeout(400);after=page.evaluate('window.sanctuaryState()')
            check(after['renderer']=='webgl' and after['frames']>before['frames'],'production real motion frames');shot(page,'motion-running')
            page.click('#motion-toggle');page.wait_for_timeout(150);frozen=page.evaluate('window.sanctuaryState()');page.wait_for_timeout(350)
            check(not frozen['running'] and page.evaluate('window.sanctuaryState().frames')==frozen['frames'],'production pause stops frames')
        if not a.inspect and not a.release:
            page.set_viewport_size({'width':1440,'height':900});page.goto(a.url);page.click('#lang-en');page.emulate_media(reduced_motion='no-preference');page.reload();settle(page);page.wait_for_timeout(3500)
            before=page.evaluate('window.sanctuaryState()');page.wait_for_timeout(600);after=page.evaluate('window.sanctuaryState()')
            check(before['renderer']=='webgl' and after['frames']>before['frames'],'normal motion: real WebGL frames',{'before':before,'after':after})
            shot(page,'motion-running')
            page.click('#motion-toggle');page.wait_for_timeout(100);stopped=page.evaluate('window.sanctuaryState()');page.wait_for_timeout(500)
            check(page.evaluate('window.sanctuaryState().frames')==stopped['frames'] and not stopped['running'],'pause freezes renderer')
            shot(page,'motion-paused');page.reload();settle(page)
            check(page.evaluate('window.sanctuaryState().paused && !window.sanctuaryState().running'),'pause persists on reload')
            page.click('#motion-toggle');page.wait_for_timeout(150);page.emulate_media(reduced_motion='reduce');page.wait_for_timeout(150)
            reduced=page.evaluate('window.sanctuaryState()');page.wait_for_timeout(500)
            check(not reduced['running'] and page.evaluate('window.sanctuaryState().frames')==reduced['frames'],'live reduced-motion change stops frames')
            shot(page,'reduced-motion');page.emulate_media(reduced_motion='no-preference');page.wait_for_timeout(150)
            page.locator('#atlas').scroll_into_view_if_needed();page.wait_for_timeout(200);off=page.evaluate('window.sanctuaryState()');page.wait_for_timeout(500)
            check(not off['running'] and not off['inView'] and page.evaluate('window.sanctuaryState().frames')==off['frames'],'offscreen hero stops frames')
            page.evaluate('scrollTo(0,0)');page.wait_for_timeout(250)
            # Real browser lifecycle visibility via a second active tab (CDP fallback evidence is explicit).
            other=context.new_page();other.goto('about:blank');other.bring_to_front();page.wait_for_timeout(250)
            visibility=page.evaluate('({hidden:document.hidden,state:window.sanctuaryState()})')
            report['tabVisibility']=visibility
            if visibility['hidden']:
                check(not visibility['state']['running'],'hidden tab stops renderer')
            else:
                page.evaluate("Object.defineProperty(document,'hidden',{configurable:true,value:true});document.dispatchEvent(new Event('visibilitychange'))")
                hidden=page.evaluate('window.sanctuaryState()');page.wait_for_timeout(350)
                check(not hidden['running'] and page.evaluate('window.sanctuaryState().frames')==hidden['frames'],'visibility handler stops renderer (synthetic hidden flag; headless tab did not hide)')
                page.evaluate("delete document.hidden;document.dispatchEvent(new Event('visibilitychange'))")
            other.close();page.bring_to_front()
            # Context loss must restore original image with no renderer loop.
            page.evaluate("document.querySelector('canvas').getContext('webgl').getExtension('WEBGL_lose_context').loseContext()")
            page.wait_for_timeout(200);check(page.evaluate("window.sanctuaryState().renderer==='static' && !window.sanctuaryState().running && !document.documentElement.classList.contains('shader-ready')"),'context-loss static fallback');shot(page,'context-loss')
            fallback=context.new_page();attach(fallback)
            fallback.add_init_script("const original=HTMLCanvasElement.prototype.getContext;HTMLCanvasElement.prototype.getContext=function(type,...args){return /webgl/.test(type)?null:original.call(this,type,...args)}")
            fallback.goto(a.url);settle(fallback);check(fallback.evaluate("window.sanctuaryState().renderer==='static' && document.querySelector('.hero-art img').naturalWidth>0"),'WebGL unavailable: original fallback');shot(fallback,'webgl-unavailable');fallback.close()
            denied=context.new_page();attach(denied);denied.add_init_script("Object.defineProperty(window,'localStorage',{get(){throw new Error('Storage denied')}})")
            denied.goto(a.url);denied.click('#lang-bg');denied.click('#motion-toggle');check(denied.locator('html').get_attribute('lang')=='bg' and denied.evaluate('window.sanctuaryState().paused'),'denied storage: language and pause work');denied.close()
            page.goto(a.url+'/#numerology');check(page.locator('#numerology details').get_attribute('open') is not None,'direct fragment opens reflection')
            page.goto(a.url);page.keyboard.press('Tab');check(page.locator('.skip-link').evaluate('(e)=>e===document.activeElement'),'keyboard skip link focus');page.keyboard.press('Enter');check(page.evaluate("location.hash==='#main'"),'keyboard skip target')
            page.locator('#astrology summary').focus();page.keyboard.press('Enter');check(page.locator('#astrology details').get_attribute('open') is not None,'keyboard native reflection')
            nojs=browser.new_context(java_script_enabled=False,viewport={'width':390,'height':844});np=nojs.new_page();attach(np);np.goto(a.url)
            check(np.locator('.topic').count()==6 and all(np.locator('#'+id+' h3').is_visible() for id in ['astrology','numerology','skincare','wellbeing','family','mental-health']),'no JS: all six themes visible');np.locator('#family summary').click();check(np.locator('#family details').get_attribute('open') is not None,'no JS: native disclosure');np.locator('.nav-more summary').click();check(np.locator('.mobile-nav a').first.is_visible(),'no JS: navigation');np.evaluate('scrollTo(0,0)');shot(np,'no-js-mobile');nojs.close()
            # Capture timed real screenshots, preserving an elapsed-time ledger.
            recording=browser.new_context(viewport={'width':1280,'height':800},reduced_motion='no-preference');rp=recording.new_page();rp.goto(a.url);settle(rp)
            frames=OUT/'motion-frames';frames.mkdir(exist_ok=True);ledger=[];start=time.monotonic()
            for frame in range(36):
                if frame==12:rp.locator('#atlas').scroll_into_view_if_needed()
                if frame==20:rp.locator('#numerology').scroll_into_view_if_needed()
                if frame==28:rp.locator('#skincare').scroll_into_view_if_needed()
                rp.screenshot(path=str(frames/f'{frame:03}.png'));ledger.append({'frame':frame,'elapsedSeconds':round(time.monotonic()-start,3),'state':rp.evaluate('window.sanctuaryState()')});rp.wait_for_timeout(160)
            (OUT/'motion-timing.json').write_text(json.dumps(ledger,indent=2)+'\n');recording.close()
        context.close()
    except Exception as error:
        report['exception']=str(error);raise
    finally:
        browser.close()
        report['passed']=sum(c['passed'] for c in report['checks']);report['total']=len(report['checks'])
        report['failed']=[c for c in report['checks'] if not c['passed']]
        file=OUT/('production-browser.json' if a.release else 'inspect.json' if a.inspect else 'browser-report.json');file.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
        print(json.dumps({k:report.get(k) for k in ['passed','total','failed','consoleErrors','externalRequests','failedRequests','httpErrors','exception']},indent=2,ensure_ascii=False))
raise SystemExit(1 if report['failed'] or any(report[k] for k in ['consoleErrors','externalRequests','failedRequests','httpErrors']) else 0)
