"""Independent source-key audit and conservative near-duplicate inventory."""
from pathlib import Path
from difflib import SequenceMatcher
import json,re,hashlib
ROOT=Path(__file__).resolve().parents[1]
questions=json.loads((ROOT/'src/data/questions.json').read_text())
report=json.loads((ROOT/'src/data/import-report.json').read_text())
for bank,expected in [(1,91),(2,90),(3,90)]:
 text=(ROOT/f'public/sources/bank-{bank}.txt').read_text().split('Answer Keys',1)[1]
 keys={int(n):letter for n,letter in re.findall(r'(?<!\d)(\d+)\.\s*([a-e])\)',text)}
 assert len(keys)==expected
 for q in [q for q in questions if q['bank']==bank]:assert keys[q['number']] in q['originalAnswer'],q['id']
def asset_hash(path):return hashlib.sha256((ROOT/'public'/path.lstrip('/')).read_bytes()).hexdigest()
seen={}
for q in questions:
 signature=json.dumps([' '.join(q['text'].split()),[(c['id'],' '.join(c['text'].split()),asset_hash(c['image']) if len(c['text'].strip())<=3 else None) for c in q['choices']],[asset_hash(p) for p in q.get('promptFigures',[])]],ensure_ascii=False)
 q['duplicateOf']=seen.get(signature)
 seen.setdefault(signature,q['id'])
report['unique']=sum(q['duplicateOf'] is None for q in questions)
(ROOT/'src/data/questions.json').write_text(json.dumps(questions,ensure_ascii=False,indent=2))
normalized={q['id']:' '.join(q['text'].lower().split()) for q in questions}
pairs=[]
for i,a in enumerate(questions):
 for b in questions[i+1:]:
  if a['bank']==b['bank']:continue
  left,right=normalized[a['id']],normalized[b['id']]
  if len(left)<80 or min(len(left),len(right))/max(len(left),len(right))<.94:continue
  score=SequenceMatcher(None,left,right).ratio()
  if score>=.94:pairs.append({'a':a['id'],'b':b['id'],'similarity':round(score,3),'note':'Similar prompt only; choices and images may differ. Not automatically merged.'})
report['similarQuestionPairs']=pairs
report['sourceSha256']={f'bank-{i}.pdf':hashlib.sha256((ROOT/f'public/sources/bank-{i}.pdf').read_bytes()).hexdigest() for i in [1,2,3]}
report['independentKeyAudit']='All 271 primary key letters matched independently against pdftotext layout extraction. Multi-select sets are additionally retained from column-aware key extraction.'
(ROOT/'src/data/import-report.json').write_text(json.dumps(report,indent=2))
print('271 source keys audited;',len(pairs),'similar prompt pairs flagged')
