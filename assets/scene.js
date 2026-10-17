import {motionAllowed} from './motion-state.js';

const root = document.documentElement;
root.classList.add('js');
const reduce = matchMedia('(prefers-reduced-motion: reduce)');
const desktop = matchMedia('(min-width: 901px)');
const button = document.querySelector('#motion-toggle');
const label = document.querySelector('#motion-label');
const hero = document.querySelector('.hero');
let paused = false;
try { paused = localStorage.getItem('silviya-motion') === 'paused'; } catch (_) { /* private mode stays usable */ }
let inView = true;
let context = null;
let entranceDone = false;
let disposed = false;
const stats = {frames:0, renderer:'static', activeScene:'skincare', running:false};
const allowed = () => motionAllowed({paused,reduced:reduce.matches,visible:!document.hidden});

// A static, semantic source image for every chapter remains in the HTML.
// The desktop art stage is presentation-only and never replaces that content.
const chapters = [...document.querySelectorAll('.topic')];
const stage = document.querySelector('.stage-images');
const images = chapters.map(chapter => {
  const image = chapter.querySelector('img').cloneNode();
  image.alt = '';
  image.removeAttribute('data-alt-en'); image.removeAttribute('data-alt-bg');
  image.loading = 'lazy';
  stage.append(image);
  return image;
});
let active = -1;
function activate(index) {
  if (index === active || index < 0) return;
  active = index;
  images.forEach((image,i) => image.classList.toggle('is-active',i === index));
  document.querySelectorAll('.theme-nav [data-theme]').forEach(link => {
    if (link.dataset.theme === chapters[index].id) link.setAttribute('aria-current','true');
    else link.removeAttribute('aria-current');
  });
  stats.activeScene = chapters[index].id;
}
activate(0);
function chooseChapter() {
  const center = innerHeight * .52;
  const distances = chapters.map(chapter => {
    const r=chapter.getBoundingClientRect();
    return r.top <= center && r.bottom >= center ? 0 : Math.min(Math.abs(r.top-center),Math.abs(r.bottom-center));
  });
  activate(distances.indexOf(Math.min(...distances)));
}
let scrollFrame=0;
function onScroll() {
  if (!scrollFrame) scrollFrame=requestAnimationFrame(()=>{scrollFrame=0;chooseChapter();});
}
addEventListener('scroll',onScroll,{passive:true});

function updateLabel() {
  const bg=root.lang==='bg';
  const stopped=paused||reduce.matches;
  button.setAttribute('aria-pressed',String(stopped));
  label.textContent=reduce.matches ? (bg?'Намалено движение':'Motion reduced') : stopped ? (bg?'Пусни движението':'Resume motion') : (bg?'Спри движението':'Pause motion');
  button.setAttribute('aria-label',label.textContent);
}

function buildChoreography() {
  if (context) { context.revert(); context=null; }
  const enabled=allowed();
  root.classList.toggle('motion-on',enabled);
  root.classList.toggle('motion-off',!enabled);
  updateLabel();
  if (!enabled || !window.gsap || !window.ScrollTrigger) return;
  const gsap=window.gsap;
  gsap.registerPlugin(window.ScrollTrigger);
  context=gsap.context(()=>{
    if (!entranceDone && inView) {
      entranceDone=true;
      gsap.timeline({defaults:{ease:'power2.out'}})
        .fromTo('.hero-art img',{scale:1.045},{scale:1,duration:3.2},0)
        .fromTo('.hero h1',{y:26,opacity:.45},{y:0,opacity:1,duration:1.6},.2)
        .fromTo('.hero-sub, .hero .primary-action',{y:14,opacity:.55},{y:0,opacity:1,duration:1.1,stagger:.12},.6);
    }
    if (desktop.matches) {
      gsap.to('.hero-intro',{y:85,ease:'none',scrollTrigger:{trigger:hero,start:'top top',end:'bottom top',scrub:1}});
      gsap.to('.hero-art',{y:70,ease:'none',scrollTrigger:{trigger:hero,start:'top top',end:'bottom top',scrub:1}});
    }
    gsap.fromTo('.about h2',{color:'#6d858f'},{color:'#263840',ease:'none',scrollTrigger:{trigger:'.about',start:'top 75%',end:'center 45%',scrub:1}});
    gsap.fromTo('.section-heading h2',{y:30},{y:0,ease:'none',scrollTrigger:{trigger:'.section-heading',start:'top 95%',end:'bottom 70%',scrub:1}});
    gsap.fromTo('.closing-art img',{scale:1.09,y:-25},{scale:1,y:0,ease:'none',scrollTrigger:{trigger:'.next',start:'top bottom',end:'center center',scrub:1.2}});
  });
  window.ScrollTrigger.refresh();
}

function syncAll(){
  if(disposed)return;
  buildChoreography();
}
button.addEventListener('click',()=>{
  paused=!paused;
  try { localStorage.setItem('silviya-motion',paused?'paused':'playing'); } catch (_) { /* storage is optional */ }
  syncAll();
});
reduce.addEventListener('change',syncAll);
desktop.addEventListener('change',syncAll);
const heroObserver=new IntersectionObserver(entries=>{
  inView=entries[0].isIntersecting;
},{threshold:0});
heroObserver.observe(hero);
document.addEventListener('visibilitychange',syncAll);
const langObserver=new MutationObserver(()=>{updateLabel();if(window.ScrollTrigger)window.ScrollTrigger.refresh();});
langObserver.observe(root,{attributes:true,attributeFilter:['lang']});
let resizeTimer;
addEventListener('resize',()=>{clearTimeout(resizeTimer);resizeTimer=setTimeout(()=>{chooseChapter();},180);},{passive:true});
function suspendPage(){
  disposed=true;
  if(context){context.revert();context=null;}
  heroObserver.disconnect();langObserver.disconnect();
  clearTimeout(resizeTimer);resizeTimer=undefined;
  if(scrollFrame)cancelAnimationFrame(scrollFrame);
  scrollFrame=0;
  root.classList.remove('motion-on');root.classList.add('motion-off');
}
function restorePage(event){
  if(!event.persisted || !disposed)return;
  disposed=false;
  try { paused=localStorage.getItem('silviya-motion')==='paused'; } catch (_) { /* retain in-memory preference */ }
  const rect=hero.getBoundingClientRect();
  inView=rect.bottom>0 && rect.top<innerHeight;
  heroObserver.observe(hero);
  langObserver.observe(root,{attributes:true,attributeFilter:['lang']});
  chooseChapter();
  syncAll();
}
// BFCache preserves this JS document: suspend resources, then recreate them
// on a native persisted pageshow. Listeners remain singletons across returns.
addEventListener('pagehide',suspendPage);
addEventListener('pageshow',restorePage);
// Read-only diagnostics for actual frame/pause/fallback verification.
window.sanctuaryState=()=>({...stats,paused,reduced:reduce.matches,visible:!document.hidden,inView});
syncAll();
