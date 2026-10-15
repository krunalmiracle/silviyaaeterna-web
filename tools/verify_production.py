"""Compare exact HTTPS-served production bytes with reviewed local artifact."""
from pathlib import Path
from datetime import datetime,timezone
from urllib.request import Request,urlopen
from urllib.error import HTTPError
import hashlib,json,subprocess,concurrent.futures
ROOT=Path(__file__).resolve().parents[1];ORIGIN='https://silviyaaeterna.krusil.com'
files=['index.html']+[str(p.relative_to(ROOT)) for p in (ROOT/'assets').rglob('*') if p.is_file() and '/plates/' not in str(p)]
def fetch(name):
 path='/' if name=='index.html' else '/'+name
 with urlopen(Request(ORIGIN+path,headers={'Cache-Control':'no-cache'}),timeout=40) as response:
  body=response.read();headers=dict(response.headers);code=response.status
 expected=hashlib.sha256((ROOT/name).read_bytes()).hexdigest();actual=hashlib.sha256(body).hexdigest()
 return {'path':path,'local':name,'status':code,'bytes':len(body),'expectedSha256':expected,'actualSha256':actual,'matches':expected==actual,'headers':headers if name=='index.html' else None}
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:results=list(pool.map(fetch,files))
blocked=[]
for path in ['/.git/config','/.impeccable/review/HANDOFF.md','/tools/ASSET-MANIFEST.json','/server.ts','/package.json']:
 try:
  with urlopen(ORIGIN+path,timeout=30) as response:status=response.status
 except HTTPError as e:status=e.code
 blocked.append({'path':path,'status':status,'blocked':status==404})
report={'verifiedAt':datetime.now(timezone.utc).isoformat(),'origin':ORIGIN,'candidateCommit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'runtimeFiles':results,'allRuntimeBytesMatch':all(r['matches'] and r['status']==200 for r in results),'privatePaths':blocked,'allPrivatePathsBlocked':all(p['blocked'] for p in blocked)}
(ROOT/'.impeccable/review/production-hashes.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'origin':ORIGIN,'candidateCommit':report['candidateCommit'],'runtimeFiles':len(results),'allRuntimeBytesMatch':report['allRuntimeBytesMatch'],'allPrivatePathsBlocked':report['allPrivatePathsBlocked'],'mismatches':[r['path'] for r in results if not r['matches']]},indent=2))
raise SystemExit(0 if report['allRuntimeBytesMatch'] and report['allPrivatePathsBlocked'] else 1)
