from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from urllib.request import urlopen
from urllib.parse import urlparse
import json
from datetime import datetime,timezone
root=Path(__file__).resolve().parents[1]
qs=json.loads((root/'src/data/questions.json').read_text())
urls=sorted({ref['url'] for q in qs for ref in q['references']})
def check(url):
 try:
  with urlopen(url,timeout=40) as r:
   status=r.status;final=r.url;html=r.read()
  if urlparse(final).hostname not in ['docs.databricks.com','www.databricks.com']:raise ValueError('Unexpected redirect host')
  if not html:raise ValueError('Empty documentation response')
  return {'url':url,'finalUrl':final,'status':status,'checkedAt':datetime.now(timezone.utc).isoformat(),'bytes':len(html)}
 except Exception as e:return {'url':url,'error':str(e),'checkedAt':datetime.now(timezone.utc).isoformat()}
results=list(ThreadPoolExecutor(max_workers=6).map(check,urls))
(root/'research/link-checks.json').write_text(json.dumps(results,indent=2))
print('Checked',len(results),'official URLs; failures:',[x for x in results if 'error' in x])
if any('error' in x for x in results):raise SystemExit(1)
