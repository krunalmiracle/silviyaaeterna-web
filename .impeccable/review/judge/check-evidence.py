import json,hashlib,subprocess
from pathlib import Path
from PIL import Image,ImageChops,ImageStat
R=Path.cwd();O=R/".impeccable/review/judge"
digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
m=json.loads((R/"tools/ASSET-MANIFEST.json").read_text());v=json.loads((R/".impeccable/review/verification.json").read_text())
report={"originals":[],"derivatives":[],"sourceFingerprints":[],"screenshots":[]}
for a in m["assets"]:
 src=Path(a["output"]);im=Image.open(src);im.load()
 cache=Path(a.get("image",a.get("original_cache_file")))
 report["originals"].append({"id":a["id"],"sha256":digest(src),"matchesManifest":digest(src)==a["originalSha256"],"dimensions":im.size,"provider":a["provider"],"requestedModel":a["model"],"promptPresent":bool(a["prompt"]),"providerCacheExists":cache.exists(),"providerCacheHashMatches":digest(cache)==digest(src) if cache.exists() else None})
 for d in a["derivatives"]:
  p=R/"assets/images"/d["filename"];w=Image.open(p);w.load();x=json.loads(w.info["xmp"])
  report["derivatives"].append({"name":d["filename"],"hashMatches":digest(p)==d["sha256"],"sizeMatches":w.size==(d["width"],d["height"]),"sourceMetadataMatches":x["sourceSha256"]==a["originalSha256"],"promptMetadataMatches":x["prompt"]==a["prompt"]})
for p,h in v["sourceFingerprints"].items(): report["sourceFingerprints"].append({"path":p,"matches":digest(R/p)==h,"actual":digest(R/p)})
for s in v["screenshots"]: report["screenshots"].append({"path":s["path"],"matches":digest(R/s["path"])==s["sha256"]})
t=json.loads((R/".impeccable/review/motion-timing.json").read_text())
report["motion"]={"captures":len(t),"monotonic":all(b["elapsedSeconds"]>a["elapsedSeconds"] for a,b in zip(t,t[1:])),"first":t[0],"last":t[-1],"captureSpan":round(t[-1]["elapsedSeconds"]-t[0]["elapsedSeconds"],3),"states":sorted(set(x["state"]["activeScene"] for x in t)),"file":json.loads(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration,size:stream=nb_frames","-of","json",str(R/".impeccable/review/sanctuary-motion.mp4")]))}
frames=R/".impeccable/review/motion-frames"
report["motion"]["sourceFramesPresent"]=all((frames/f"{i:03}.png").exists() for i in range(len(t)))
if report["motion"]["sourceFramesPresent"]:
 report["motion"]["distinctSourceFrames"]=len({digest(frames/f"{i:03}.png") for i in range(len(t))})
 a=Image.open(frames/"000.png");b=Image.open(frames/"011.png")
 report["motion"]["heroFrameDifferenceBBox"]=ImageChops.difference(a.convert("RGB"),b.convert("RGB")).getbbox()
 sheet=Image.new("RGB",(1280,1200))
 for pos,i in enumerate([0,6,11,12,20,35]):
  im=Image.open(frames/f"{i:03}.png");im.thumbnail((640,400));sheet.paste(im,((pos%2)*640,(pos//2)*400))
 sheet.save(O/"motion-evidence-contact.png")
(O/"asset-and-evidence-checks.json").write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
print(json.dumps(report,indent=2,ensure_ascii=False))
