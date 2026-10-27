from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import urllib.request,json
from bs4 import BeautifulSoup
urls={
'lakehouse':'https://docs.databricks.com/aws/en/lakehouse/',
'medallion':'https://docs.databricks.com/aws/en/lakehouse/medallion',
'auto-loader':'https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/',
'vacuum':'https://docs.databricks.com/aws/en/delta/vacuum',
'delete':'https://docs.databricks.com/aws/en/sql/language-manual/delta-delete-from',
'insert':'https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-dml-insert-into',
'optimize':'https://docs.databricks.com/aws/en/delta/optimize',
'delta':'https://docs.databricks.com/aws/en/delta/',
'copy':'https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/copy-into/',
'bundles':'https://docs.databricks.com/aws/en/dev-tools/bundles/variables',
'jobs':'https://docs.databricks.com/aws/en/jobs/run-if',
'file-arrival':'https://docs.databricks.com/aws/en/jobs/file-arrival-triggers',
'connect':'https://docs.databricks.com/aws/en/dev-tools/databricks-connect/',
'federation':'https://docs.databricks.com/aws/en/query-federation/',
'sql-warehouses':'https://docs.databricks.com/aws/en/compute/sql-warehouse/warehouse-behavior',
'notebooks':'https://docs.databricks.com/aws/en/notebooks/notebooks-code',
'git':'https://docs.databricks.com/aws/en/repos/git-operations-with-repos',
'expectations':'https://docs.databricks.com/aws/en/delta-live-tables/expectations',
'streaming':'https://docs.databricks.com/aws/en/structured-streaming/triggers',
'architecture':'https://docs.databricks.com/aws/en/getting-started/overview',
'countif':'https://docs.databricks.com/aws/en/sql/language-manual/functions/count_if',
'views':'https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-ddl-create-view',
'create-table':'https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-ddl-create-table-using',
'privileges':'https://docs.databricks.com/aws/en/data-governance/unity-catalog/manage-privileges/privileges',
'debugger':'https://docs.databricks.com/aws/en/notebooks/debugger',
'pools':'https://docs.databricks.com/aws/en/compute/pools-index',
'sharing':'https://docs.databricks.com/aws/en/delta-sharing/',
'python':'https://docs.databricks.com/aws/en/pyspark/',
}
root=Path(__file__).resolve().parents[1]/'research';root.mkdir(exist_ok=True)
def fetch(item):
 key,url=item
 try:
  with urllib.request.urlopen(url,timeout=45) as response:
   html=response.read().decode();final=response.url
  soup=BeautifulSoup(html,'html.parser');main=soup.find('main') or soup
  for tag in main(['script','style','nav']):tag.decompose()
  text=main.get_text('\n',strip=True)
  (root/f'{key}.txt').write_text(text)
  return key,{'url':final,'requestedUrl':url,'title':soup.title.get_text() if soup.title else key,'characters':len(text),'retrieved':'2026-10-27'}
 except Exception as e:return key,{'url':url,'error':str(e)}
results=dict(ThreadPoolExecutor(max_workers=6).map(fetch,urls.items()))
(root/'sources.json').write_text(json.dumps(results,indent=2));print(json.dumps(results,indent=2))
