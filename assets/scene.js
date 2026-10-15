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
let renderer = null;
let disposed = false;
const stats = {frames:0, renderer:'static', activeScene:'astrology', running:false};
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
    gsap.fromTo('.about h2',{color:'#86aaa5'},{color:'#f3efe5',ease:'none',scrollTrigger:{trigger:'.about',start:'top 75%',end:'center 45%',scrub:1}});
    gsap.fromTo('.section-heading h2',{y:30},{y:0,ease:'none',scrollTrigger:{trigger:'.section-heading',start:'top 95%',end:'bottom 70%',scrub:1}});
    gsap.fromTo('.closing-art img',{scale:1.09,y:-25},{scale:1,y:0,ease:'none',scrollTrigger:{trigger:'.next',start:'top bottom',end:'center center',scrub:1.2}});
  });
  window.ScrollTrigger.refresh();
}

// The only custom renderer: low-amplitude refraction over the lower 45%
// of the original hero. No invented 3D geometry and no WebGL dependency.
function createWater() {
  const canvas=document.querySelector('#garden-water');
  const gl=canvas.getContext('webgl',{alpha:true,antialias:false,powerPreference:'low-power',preserveDrawingBuffer:false});
  if (!gl) return null;
  const vertex='attribute vec2 p;varying vec2 uv;void main(){uv=p*.5+.5;gl_Position=vec4(p,0.,1.);}';
  const fragment=`precision mediump float;
  uniform sampler2D artwork;uniform vec2 view;uniform float imageRatio;uniform float time;
  varying vec2 uv;
  void main(){
    vec2 whole=vec2(uv.x,uv.y*.45);
    float ratio=view.x/view.y;
    vec2 crop=vec2(min(1.,ratio/imageRatio),min(1.,imageRatio/ratio));
    vec2 sampleUV=(whole-.5)*crop+.5;
    float edge=(1.-smoothstep(.78,1.,uv.y))*smoothstep(0.,.10,uv.y);
    float center=exp(-pow((uv.x-.51)*2.5,2.));
    float wave=sin(uv.y*61.+time*.65+sin(uv.x*19.))*.0007;
    sampleUV.x+=wave*edge*center;
    sampleUV.y+=sin(uv.x*39.+time*.45)*.00025*edge;
    vec3 col=texture2D(artwork,sampleUV).rgb;
    for(int i=0;i<4;i++){
      float fi=float(i);vec2 at=vec2(.25+fi*.15+sin(time*.12+fi)*.028,.24+sin(time*.18+fi*2.)*.14);
      float light=exp(-length((uv-at)*vec2(1.,.45))*650.);
      col+=vec3(.8,.60,.28)*light*(.35+.25*sin(time+fi));
    }
    gl_FragColor=vec4(col,edge*.7);
  }`;
  const shaders=[];
  let program,buffer,texture,raf=0,ready=false,dead=false,last=0,elapsed=0,previous=0;
  function compile(type,source){
    const shader=gl.createShader(type);gl.shaderSource(shader,source);gl.compileShader(shader);
    if (!gl.getShaderParameter(shader,gl.COMPILE_STATUS)){gl.deleteShader(shader);throw new Error('Shader compilation unavailable');}
    shaders.push(shader);return shader;
  }
  try {
    program=gl.createProgram();gl.attachShader(program,compile(gl.VERTEX_SHADER,vertex));gl.attachShader(program,compile(gl.FRAGMENT_SHADER,fragment));gl.linkProgram(program);
    if(!gl.getProgramParameter(program,gl.LINK_STATUS))throw new Error('Shader linking unavailable');
    gl.useProgram(program);
    buffer=gl.createBuffer();gl.bindBuffer(gl.ARRAY_BUFFER,buffer);gl.bufferData(gl.ARRAY_BUFFER,new Float32Array([-1,-1,1,-1,-1,1,-1,1,1,-1,1,1]),gl.STATIC_DRAW);
    const p=gl.getAttribLocation(program,'p');gl.enableVertexAttribArray(p);gl.vertexAttribPointer(p,2,gl.FLOAT,false,0,0);
    texture=gl.createTexture();gl.bindTexture(gl.TEXTURE_2D,texture);
    gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_S,gl.CLAMP_TO_EDGE);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_T,gl.CLAMP_TO_EDGE);
    gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MIN_FILTER,gl.LINEAR);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MAG_FILTER,gl.LINEAR);
  } catch (_) { cleanup(); return null; }
  const timeLocation=gl.getUniformLocation(program,'time');
  const viewLocation=gl.getUniformLocation(program,'view');
  const ratioLocation=gl.getUniformLocation(program,'imageRatio');
  function resize(){
    const rect=hero.getBoundingClientRect();
    const dpr=Math.min(devicePixelRatio||1,1.25);
    canvas.width=Math.round(Math.min(rect.width,1672)*dpr);
    canvas.height=Math.round(canvas.width/rect.width*rect.height*.45);
    gl.viewport(0,0,canvas.width,canvas.height);gl.uniform2f(viewLocation,rect.width,rect.height);
  }
  function permitted(){return !dead&&ready&&desktop.matches&&motionAllowed({paused,reduced:reduce.matches,visible:!document.hidden,inView});}
  function tick(now){
    raf=0;if(!permitted()){stats.running=false;previous=0;return;}
    stats.running=true;
    if(now-last>=32){
      elapsed+=previous?Math.min(now-previous,60)/1000:0;
      previous=now;last=now;
      gl.uniform1f(timeLocation,elapsed);gl.drawArrays(gl.TRIANGLES,0,6);stats.frames++;
    }
    raf=requestAnimationFrame(tick);
  }
  function sync(){
    if(permitted()){if(!raf){previous=0;raf=requestAnimationFrame(tick);}}
    else{if(raf)cancelAnimationFrame(raf);raf=0;stats.running=false;previous=0;}
  }
  function cleanup(){
    if(dead)return;
    canvas.removeEventListener('webglcontextlost',onContextLost);
    dead=true;if(raf)cancelAnimationFrame(raf);raf=0;stats.running=false;
    root.classList.remove('shader-ready');stats.renderer='static';
    if(texture)gl.deleteTexture(texture);if(buffer)gl.deleteBuffer(buffer);if(program)gl.deleteProgram(program);shaders.forEach(s=>gl.deleteShader(s));
  }
  function onContextLost(event){event.preventDefault();cleanup();}
  canvas.addEventListener('webglcontextlost',onContextLost,{once:true});
  const source=new Image();
  source.onload=()=>{
    if(dead)return;
    try {
      gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL,true);gl.bindTexture(gl.TEXTURE_2D,texture);
      gl.texImage2D(gl.TEXTURE_2D,0,gl.RGBA,gl.RGBA,gl.UNSIGNED_BYTE,source);
      gl.uniform1f(ratioLocation,source.naturalWidth/source.naturalHeight);resize();ready=true;
      stats.renderer='webgl';root.classList.add('shader-ready');sync();
    }catch(_){cleanup();}
  };
  source.onerror=cleanup;
  source.src=document.querySelector('.hero-art img').src;
  return {sync,resize,cleanup};
}
function syncAll(){
  if(disposed)return;
  buildChoreography();
  if(!renderer && desktop.matches && !reduce.matches && !paused)renderer=createWater();
  if(renderer)renderer.sync();
}
button.addEventListener('click',()=>{
  paused=!paused;
  try { localStorage.setItem('silviya-motion',paused?'paused':'playing'); } catch (_) { /* storage is optional */ }
  syncAll();
});
reduce.addEventListener('change',syncAll);
desktop.addEventListener('change',()=>{syncAll();if(renderer)renderer.resize();});
const heroObserver=new IntersectionObserver(entries=>{
  inView=entries[0].isIntersecting;
  if(renderer)renderer.sync();
},{threshold:0});
heroObserver.observe(hero);
document.addEventListener('visibilitychange',syncAll);
const langObserver=new MutationObserver(()=>{updateLabel();if(window.ScrollTrigger)window.ScrollTrigger.refresh();});
langObserver.observe(root,{attributes:true,attributeFilter:['lang']});
let resizeTimer;
addEventListener('resize',()=>{clearTimeout(resizeTimer);resizeTimer=setTimeout(()=>{if(renderer)renderer.resize();chooseChapter();},180);},{passive:true});
function suspendPage(){
  disposed=true;
  if(renderer){renderer.cleanup();renderer=null;}
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
