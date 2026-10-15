from pathlib import Path
import json
root=Path.cwd()
for name in ["browser-report.json","verification.json","accessibility-performance.json"]:
 d=json.loads((root/".impeccable/review"/name).read_text())
 print("REPORT",name)
 if name=="browser-report.json":
  print(json.dumps({k:v for k,v in d.items() if k not in ["viewports","checks","screenshots"]},ensure_ascii=False))
  print("COUNT",len(d["checks"]),sum(x["passed"] for x in d["checks"]))
  print(json.dumps(d["checks"][280:],ensure_ascii=False))
 elif name=="verification.json":
  print(json.dumps({k:v for k,v in d.items() if k!="screenshots"},ensure_ascii=False))
 else:
  print("AXE",len(d["axe"]),sum(len(x["violations"]) for x in d["axe"]));print(json.dumps(d["visibility"]))
print("DIFF FILES")
text=(root/".impeccable/review/candidate-source.diff").read_text()
for s in text.split("diff --git "):
 if s: print(s.splitlines()[0])
