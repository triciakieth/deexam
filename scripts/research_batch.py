"""Fetch approved official pages, preserving existing evidence metadata."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from urllib.request import urlopen
from urllib.parse import urlparse
from datetime import date
import json,sys
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parents[1]; dest=ROOT/'research'
def fetch(pair):
 key,url=pair
 assert urlparse(url).hostname in ['docs.databricks.com','www.databricks.com']
 try:
  with urlopen(url,timeout=45) as response:
   final=response.url;html=response.read().decode()
  assert urlparse(final).hostname in ['docs.databricks.com','www.databricks.com']
  soup=BeautifulSoup(html,'html.parser');main=soup.find('main') or soup
  for node in main(['script','style','nav']):node.decompose()
  text=main.get_text('\n',strip=True)
  (dest/f'{key}.txt').write_text(text)
  return key,{'url':final,'requestedUrl':url,'title':soup.title.get_text() if soup.title else key,'characters':len(text),'retrieved':str(date.today())}
 except Exception as e:return key,{'url':url,'error':str(e)}
manifest=json.loads((dest/'sources.json').read_text())
urls=json.loads(Path(sys.argv[1]).read_text())
results=dict(ThreadPoolExecutor(max_workers=6).map(fetch,urls.items()))
manifest.update(results);(dest/'sources.json').write_text(json.dumps(manifest,indent=2))
for key,result in results.items():print(key,result.get('error') or str(result['characters'])+' characters')
