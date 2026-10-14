#!/usr/bin/env python3
"""Bounded local browser acceptance batch. Owns and closes server and browser.
uv run --with patchright python tools/shots.py
"""
import json
import subprocess
import tempfile
import sys
from datetime import datetime, timezone
from pathlib import Path
from patchright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / '.impeccable/review'
URL = 'http://127.0.0.1:43118'
LAYOUT_ONLY = '--layout-only' in sys.argv

def chrome_path():
    for base in [Path.home() / '.linkedin-mcp/patchright-browsers', Path.home() / '.cache/ms-playwright']:
        for found in sorted(base.glob('chromium*/chrome-linux*/chrome'), reverse=True):
            return str(found)
    raise RuntimeError('No local Chromium binary found')

def settle(page):
    page.evaluate('document.fonts.ready')
    if not LAYOUT_ONLY:
        for img in page.locator('main img').all():
            img.scroll_into_view_if_needed()
            img.evaluate('(i) => i.decode()')
    page.evaluate('window.scrollTo(0, 0)')
    page.wait_for_timeout(180)

def inspect(page):
    return page.evaluate('''() => {
      const visible = e => {
        const closed = e.closest('details:not([open])');
        if (closed && !closed.querySelector(':scope > summary').contains(e)) return false;
        return e.checkVisibility({visibilityProperty:true});
      };
      const targets = [...document.querySelectorAll('a,button,summary')].filter(visible).filter(e => !e.classList.contains('skip-link'));
      const small = targets.filter(e => Math.min(e.getBoundingClientRect().width,e.getBoundingClientRect().height) < 43.9).map(e => e.textContent.trim());
      const clipped = [...document.querySelectorAll('h1,h2,h3,h4,p,a,summary')].filter(visible).filter(e => !e.classList.contains('skip-link')).filter(e => {const r=e.getBoundingClientRect();return r.left < -.5 || r.right > innerWidth+.5 || e.scrollWidth > e.clientWidth+1;}).map(e=>e.textContent.trim().slice(0,70));
      return {lang:document.documentElement.lang, overflowX:document.documentElement.scrollWidth-document.documentElement.clientWidth,
        smallTargets:small, clipped, images:[...document.images].map(i=>({src:new URL(i.currentSrc || i.src).pathname,decoded:i.complete&&i.naturalWidth>0,width:i.naturalWidth,height:i.naturalHeight})),
        allTopics:document.querySelectorAll('.topic').length, cta:document.querySelector('.primary-action').getAttribute('href'),
        heading:document.querySelector('h1').innerText, font:getComputedStyle(document.querySelector('h1')).fontFamily,
        soonAreControls:document.querySelectorAll('a.soon-state,button.soon-state,.soon-state a,.soon-state button').length,
        heroImageTop:Math.round(document.querySelector('.hero-art img').getBoundingClientRect().top),
        heroImageBottom:Math.round(document.querySelector('.hero-art img').getBoundingClientRect().bottom)};
    }''')

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    report = {'capturedAt':datetime.now(timezone.utc).isoformat(),'url':URL,'mode':'layout-only, original images pending' if LAYOUT_ONLY else 'full acceptance','viewports':[], 'interactions':[], 'screenshots':[], 'consoleErrors':[], 'failedRequests':[], 'externalRequests':[], 'httpErrors':[], 'issues':[]}
    server = None
    browser = None
    def check(ok, name):
        report['interactions'].append({'name':name,'passed':bool(ok)})
        if not ok: report['issues'].append(name)
    try:
        import os
        server = subprocess.Popen(['node','server.ts'], cwd=ROOT, env={**os.environ,'HOST':'127.0.0.1','PORT':'43118'}, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        line = server.stdout.readline()
        if 'listening' not in line: raise RuntimeError('Preview failed: '+line+server.stderr.read())
        with sync_playwright() as p, tempfile.TemporaryDirectory(prefix='glasshouse-review-') as profile:
            browser = p.chromium.launch_persistent_context(profile, executable_path=chrome_path(), headless=True, args=['--disable-dev-shm-usage'], reduced_motion='reduce')
            page = browser.pages[0]
            page.on('console',lambda m:report['consoleErrors'].append(m.text) if m.type=='error' else None)
            page.on('pageerror',lambda e:report['consoleErrors'].append(str(e)))
            page.on('requestfailed',lambda r:report['failedRequests'].append(r.url+' '+str(r.failure)))
            page.on('request',lambda r:report['externalRequests'].append(r.url) if not r.url.startswith(URL) else None)
            page.on('response',lambda r:report['httpErrors'].append({'url':r.url,'status':r.status}) if r.status>=400 else None)
            for lang in ['en','bg']:
                for name,width,height in [('desktop',1440,900),('mobile',390,844),('compact',320,844),('tablet',768,1024),('laptop',1024,900)]:
                    page.set_viewport_size({'width':width,'height':height})
                    page.goto(URL,wait_until='load')
                    page.click('#lang-'+lang)
                    page.reload(wait_until='load')
                    settle(page)
                    result=inspect(page)
                    result.update({'name':name,'width':width,'height':height,'language':lang})
                    report['viewports'].append(result)
                    check(result['lang']==lang and page.locator('#lang-'+lang).get_attribute('aria-pressed')=='true',f'{name}-{lang}: language persistence and aria')
                    check(result['overflowX']==0 and not result['clipped'],f'{name}-{lang}: no overflow or clipped text')
                    check(not result['smallTargets'],f'{name}-{lang}: 44px touch targets')
                    if not LAYOUT_ONLY:
                        check(all(i['decoded'] for i in result['images']),f'{name}-{lang}: four decoded still lifes')
                    check(result['allTopics']==6 and result['soonAreControls']==0 and result['cta']=='#atlas',f'{name}-{lang}: semantic content')
                    check(page.evaluate("document.fonts.check('500 48px Onest', 'Любопитство')"),f'{name}-{lang}: display font loaded')
                    if name in ['desktop','mobile'] and not LAYOUT_ONLY:
                        stem=name+('-bg' if lang=='bg' else '')
                        for suffix,full in [('-top',False),('',True)]:
                            target=OUT/(stem+suffix+'.png'); page.screenshot(path=str(target),full_page=full)
                            report['screenshots'].append(str(target.relative_to(ROOT)))
                    # Theme anchors must open useful prompts, move focus and respect sticky headroom.
                    for theme in ['astrology','numerology','skincare','wellbeing','family','mental-health']:
                        page.locator('[data-theme="'+theme+'"]').click()
                        check(page.locator('#'+theme+' details').get_attribute('open') is not None and page.locator('[data-theme="'+theme+'"]').get_attribute('aria-current')=='true',f'{name}-{lang}: select {theme}')
                        check(page.evaluate('(id)=>document.activeElement.id===id',theme),f'{name}-{lang}: focus {theme}')
                        top=page.locator('#'+theme).bounding_box()['y']
                        header=page.locator('.site-header').bounding_box()['height']
                        check(top>=header-1,f'{name}-{lang}: anchor headroom {theme}')
                    if width<=800:
                        page.evaluate('scrollTo(0,0)')
                        page.locator('.nav-more summary').click()
                        check(page.locator('.nav-more').get_attribute('open') is not None,f'{name}-{lang}: menu opens')
                        menu_result=inspect(page)
                        check(not menu_result['smallTargets'] and not menu_result['clipped'] and menu_result['overflowX']==0,f'{name}-{lang}: open menu targets and overflow')
                        if name=='mobile' and not LAYOUT_ONLY:
                            target=OUT/f'mobile-menu-{lang}.png'; page.screenshot(path=str(target))
                            report['screenshots'].append(str(target.relative_to(ROOT)))
                        page.keyboard.press('Escape')
                        check(page.locator('.nav-more').get_attribute('open') is None and page.locator('.nav-more summary').evaluate('(el)=>el===document.activeElement'),f'{name}-{lang}: Escape closes and restores focus')
                        page.keyboard.press('Enter')
                        page.locator('.mobile-nav a[href="#manifesto"]').click()
                        check(page.locator('.nav-more').get_attribute('open') is None,f'{name}-{lang}: selection closes menu')
                        check(page.locator('#manifesto').bounding_box()['y']>=header-1,f'{name}-{lang}: mobile nav headroom')
            # Real keyboard entry, reduced motion, native disclosures, and failure modes.
            page.goto(URL,wait_until='load'); page.keyboard.press('Tab')
            check(page.locator('.skip-link').evaluate('(e)=>e===document.activeElement && getComputedStyle(e).outlineStyle!=="none"'), 'keyboard: visible skip-link focus')
            page.keyboard.press('Enter')
            check(page.evaluate('location.hash==="#main"'),'keyboard: skip-link reaches main')
            check(page.locator('.hero-art img').evaluate('(e)=>getComputedStyle(e).animationName==="none"'),'reduced motion: no image animation')
            page.emulate_media(reduced_motion='no-preference'); page.reload(wait_until='load'); page.wait_for_timeout(900)
            check(page.locator('.hero-art img').evaluate('(e)=>getComputedStyle(e).opacity==="1"'),'normal motion: content remains visible')
            page.goto(URL+'/#numerology',wait_until='load')
            check(page.locator('#numerology details').get_attribute('open') is not None,'direct fragment: correct prompt opens')
            blocked=browser.new_page()
            blocked.add_init_script("Object.defineProperty(window, 'localStorage', {get(){throw new Error('Storage denied')}})")
            blocked.goto(URL,wait_until='load'); blocked.click('#lang-bg')
            check(blocked.locator('html').get_attribute('lang')=='bg','denied storage: language control still works'); blocked.close()
            nojs=browser.browser.new_context(java_script_enabled=False,viewport={'width':390,'height':844}) if browser.browser else None
            # Persistent contexts may not expose browser; use a second bounded browser instead.
            second=None
            if nojs is None:
                second=p.chromium.launch(executable_path=chrome_path(),headless=True,args=['--disable-dev-shm-usage'])
                nojs=second.new_context(java_script_enabled=False,viewport={'width':390,'height':844})
            try:
                np=nojs.new_page(); np.goto(URL,wait_until='load')
                check(np.locator('.topic').count()==6 and all(np.locator('#'+i+' h4').is_visible() for i in ['astrology','numerology','skincare','wellbeing','family','mental-health']),'no JS: all six topics visible')
                np.locator('#wellbeing summary').click()
                check(np.locator('#wellbeing details').get_attribute('open') is not None,'no JS: native reflection opens')
                np.locator('.nav-more summary').click()
                check(np.locator('.mobile-nav a').first.is_visible(),'no JS: native mobile navigation works')
            finally:
                nojs.close()
                if second: second.close()
            browser.close(); browser=None
        def lum(hexcolor):
            vals=[int(hexcolor[i:i+2],16)/255 for i in (1,3,5)]
            vals=[v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in vals]
            return sum(a*b for a,b in zip(vals,[.2126,.7152,.0722]))
        report['contrast']={}
        for fg,bg in [('#183f35','#e6ede3'),('#466255','#e6ede3'),('#466255','#f2f6ef'),('#f2f6ef','#183f35'),('#f2f6ef','#285344')]:
            a,b=sorted([lum(fg),lum(bg)]); ratio=(b+.05)/(a+.05)
            report['contrast'][fg+' on '+bg]=round(ratio,2); check(ratio>=4.5,'contrast: '+fg+' on '+bg)
        for key in ['consoleErrors','failedRequests','externalRequests','httpErrors']:
            if report[key]: report['issues'].append(key)
    except Exception as error:
        report['issues'].append(str(error))
        raise
    finally:
        if browser:
            try: browser.close()
            except Exception: pass  # Playwright's context manager already closed it on error.
        if server:
            server.terminate()
            try: server.wait(timeout=8)
            except subprocess.TimeoutExpired: server.kill(); server.wait()
        report['checksPassed']=sum(c['passed'] for c in report['interactions'])
        report['checksTotal']=len(report['interactions'])
        report_name = 'layout-only.json' if LAYOUT_ONLY else 'report.json'
        (OUT/report_name).write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
        print(json.dumps({'checksPassed':report['checksPassed'],'checksTotal':report['checksTotal'],'issues':report['issues'],'report':str(OUT/report_name)},indent=2))
    return 1 if report['issues'] else 0

if __name__=='__main__':
    raise SystemExit(main())
