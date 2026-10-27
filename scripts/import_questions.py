"""Reproducible, coordinate-aware PDF import. Never infer missing text or answers."""
from pathlib import Path
import json, re, hashlib, logging, sys
import pdfplumber, fitz
logging.getLogger('pdfminer').setLevel(logging.ERROR)
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'public/question-images'; OUT.mkdir(exist_ok=True)
allq=[]; reports=[]
CACHE=ROOT/'.import-cache'; CACHE.mkdir(exist_ok=True)
def clean(text):
 return (text or '').strip()
def topic(text):
 text=text.lower()
 groups=[('Deployment & orchestration',r'bundle|\bjob\b|\bjobs\b|\btask\b|workflow|git|repos|trigger|dashboard|alert'),('Governance & security',r'unity catalog|privilege|grant|permission|governance|federation|sharing|owner|\baccess\b'),('Ingestion & streaming',r'auto loader|stream|kafka|copy into|checkpoint|cloudfiles'),('Data transformation & modeling',r'bronze|silver|gold|medallion|\bjoin\b|\bgroup\b|\bpivot\b|\bfunction\b|\bsql\b|\bdataframe\b'),('Delta Lake & storage',r'delta|vacuum|optimize|parquet|table|storage'),('Platform & compute',r'.')]
 return next(name for name,pattern in groups if re.search(pattern,text))
for bank,total in [(1,91),(2,90),(3,90)]:
 if '--resume' in sys.argv and (CACHE/f'bank-{bank}.json').exists():
  allq.extend(json.loads((CACHE/f'bank-{bank}.json').read_text()))
  reports.append({'bank':bank,'declared':total,'imported':total,'answerKeys':total,'sourceFile':f'[{bank}] Databricks Data Engineer Associate V3.{bank}.pdf'})
  continue
 path=ROOT/f'public/sources/bank-{bank}.pdf'
 pdf=pdfplumber.open(path); render=fitz.open(path)
 keypage=next(i for i,p in enumerate(render) if 'Answer Keys' in p.get_text())
 keys={}; keyraw={}
 # The answer key is printed in three independent columns.
 for p in pdf.pages[keypage:]:
  for left,right in ([(60,222),(222,377),(377,p.width-30)] if bank<3 else [(60,227),(227,387),(387,p.width-30)]):
   text=render[p.page_number-1].get_text(clip=fitz.Rect(left,35 if bank<3 else 0,right,p.height-35 if bank<3 else p.height))
   for match in re.finditer(r'(?<!\d)(\d+)\.\s*([a-e]\))([\s\S]*?)(?=(?<!\d)\d+\.\s*[a-e]\)|\Z)',text):
    n=int(match[1]); raw=match[2]+match[3]
    keys[n]=sorted(set(re.findall(r'\b([a-e])\)',raw)));keyraw[n]=raw.strip()
 markers=[]
 for pi,p in enumerate(pdf.pages[:keypage]):
  for w in p.extract_words():
   if 55<=w['x0']<=72 and re.fullmatch(r'\d+\.',w['text']):
    markers.append((int(w['text'][:-1]),pi,w['top']))
 assert [n for n,_,_ in markers]==list(range(1,total+1)),(bank,markers)
 assert set(keys)==set(range(1,total+1)),(bank,'missing keys',set(range(1,total+1))-keys.keys())
 def image(pi,box,name):
  target=OUT/name
  render[pi].get_pixmap(matrix=fitz.Matrix(1.6,1.6),clip=fitz.Rect(*box),alpha=False).save(str(target))
  return '/question-images/'+name
 for idx,(number,pi,y) in enumerate(markers):
  qid=f'b{bank}-q{number}'; p=pdf.pages[pi]
  nextpi,nexty=(markers[idx+1][1],markers[idx+1][2]) if idx+1<len(markers) else (keypage,0)
  # Each page fragment is preserved; page headers and footers are excluded.
  segments=[]
  for pagei in range(pi,min(nextpi+1,keypage)):
   page=pdf.pages[pagei]; top=y-2 if pagei==pi else (30 if bank<3 else 12)
   bottom=nexty-8 if pagei==nextpi else (page.height-50 if bank<3 else page.height-20)
   if bottom>top: segments.append((pagei,top,bottom))
  choices=[]; promptparts=[]; sourceimgs=[]; promptimgs=[]
  for si,(pagei,top,bottom) in enumerate(segments):
   page=pdf.pages[pagei]; words=page.extract_words()
   labels=[w for w in words if top<=w['top']<bottom and re.fullmatch(r'[a-e]\)',w['text']) and 70<w['x0']<335]
   sourceimgs.append(image(pagei,(54,top,page.width-35,bottom),f'{qid}-source-{si}.png'))
   first=min([w['top'] for w in labels],default=bottom)
   if first>top:
    promptparts.append(page.crop((54,top,page.width-35,first)).extract_text(layout=False) or '')
    promptimgs.append(image(pagei,(54,top,page.width-35,max(top+1,first-2)),f'{qid}-prompt-{si}.png'))
   for w in labels:
    label=w['text'][0]; rightcol=w['x0']>200
    same=[other['top'] for other in labels if (other['x0']>200)==rightcol and other['top']>w['top']+3]
    stop=min(same,default=bottom)-2
    left=w['x0']; right=page.width-35 if rightcol else page.width/2+7
    box=(left,w['top']-1,right,max(w['top']+2,stop))
    txt=clean(page.crop(box).extract_text(layout=False))
    txt=re.sub(r'^'+label+r'\)\s*','',txt)
    choices.append({'id':label,'text':txt,'image':image(pagei,box,f'{qid}-{label}.png')})
  choices.sort(key=lambda c:c['id'])
  text=clean('\n'.join(promptparts)); text=re.sub(r'^'+str(number)+r'\.\s*','',text)
  issues=[]
  if len(choices)<2 or len({c['id'] for c in choices})!=len(choices): issues.append('Option extraction requires source review')
  if any(k not in [c['id'] for c in choices] for k in keys[number]): issues.append('Source answer key has an unmapped option')
  if any(not c['text'] for c in choices): issues.append('Image-based choices: consult preserved choice images')
  allq.append({'id':qid,'bank':bank,'number':number,'sourceFile':f'[{bank}] Databricks Data Engineer Associate V3.{bank}.pdf','pages':list(range(pi+1,(segments[-1][0]+1 if segments else pi+1)+1)), 'text':text,'promptImages':promptimgs,'sourceImages':sourceimgs,'choices':choices,'type':'multiple' if len(keys[number])>1 or re.search(r'choose (two|three)|select (two|three)|which two',text,re.I) else 'single','originalAnswer':keys[number],'originalKeyText':keyraw[number],'verifiedAnswer':None,'verification':'unverified','topic':topic(text),'issues':issues,'explanations':{},'references':[]})
 (CACHE/f'bank-{bank}.json').write_text(json.dumps([q for q in allq if q['bank']==bank],ensure_ascii=False,indent=2))
 pdf.close();render.close()
 reports.append({'bank':bank,'declared':total,'imported':len(markers),'answerKeys':len(keys),'pages':len(render) if False else keypage,'sourceFile':f'[{bank}] Databricks Data Engineer Associate V3.{bank}.pdf'})
# Exact text duplicates only; do not collapse distinct image-based questions.
seen={}
for q in allq:
 signature=json.dumps([' '.join(q['text'].split()),[(c['id'],' '.join(c['text'].split())) for c in q['choices']]],ensure_ascii=False)
 has_image=any(not c['text'] for c in q['choices'])
 digest=hashlib.sha256(signature.encode()).hexdigest()
 q['duplicateOf']=seen.get(digest) if not has_image else None
 if not has_image:seen.setdefault(digest,q['id'])
(ROOT/'src/data/questions.json').write_text(json.dumps(allq,ensure_ascii=False,indent=2))
report={'banks':reports,'total':len(allq),'unique':sum(not q['duplicateOf'] for q in allq),'verified':0,'unverified':len(allq),'issues':[{'id':q['id'],'issues':q['issues']} for q in allq if q['issues']]}
(ROOT/'src/data/import-report.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
