"""Persist explicitly authored per-question research; never infer answers from keys."""
from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parents[1]
questions=json.loads((ROOT/'src/data/questions.json').read_text()); byid={q['id']:q for q in questions}
manifest=json.loads((ROOT/'research/sources.json').read_text())
path=ROOT/'research/question-reviews.json'
reviews=json.loads(path.read_text()) if path.exists() else {q['id']:{k:q[k] for k in ['verifiedAnswer','verification','explanations','references','keyConcept','examTip'] if k in q} for q in questions if q['verification']=='verified'}
def review(qid,correct,docs,section,summary,tip,*reasons,status=None):
 q=byid[qid];assert len(reasons)==len(q['choices']),(qid,len(reasons),len(q['choices']))
 refs=[]
 for key in docs.split(','):
  source=manifest[key];assert 'error' not in source,(key,source)
  evidence=ROOT/'research'/f'{key}.txt';assert evidence.exists()
  refs.append({'title':source['title'].split(' | ')[0],'url':source['url'],'section':section,'support':summary,'retrieved':source['retrieved'],'evidenceFile':f'research/{key}.txt','evidenceSha256':hashlib.sha256(evidence.read_bytes()).hexdigest()})
 expected=correct.split(',') if correct else None
 if expected:assert set(expected)<={c['id'] for c in q['choices']}
 reviews[qid]={'verifiedAnswer':expected,'verification':'verified' if expected else 'unverified','reviewStatus':status or ('verified' if expected else 'ambiguous'),'reviewedAt':'2026-10-28','analysis':summary,'keyConcept':summary,'examTip':tip,'explanations':dict(zip([c['id'] for c in q['choices']],reasons)),'references':refs}
def save():
 path.write_text(json.dumps(reviews,ensure_ascii=False,indent=2))
 for q in questions:
  if q['id'] in reviews:q.update(reviews[q['id']])
  # Repair text-layer contamination only. Rendered originals are kept byte-for-byte.
  import re
  q['text']=re.split(r'\n\s*a\)\s*(?=b\)|\S)',q['text'],maxsplit=1)[0].strip()
  if q.get('verifiedAnswer') and set(q['verifiedAnswer'])!=set(q['originalAnswer']):
   q['issues'].append('Research correction: source key '+','.join(q['originalAnswer']).upper()+' differs from documentation-supported answer '+','.join(q['verifiedAnswer']).upper()+'.')
  q['issues']=list(dict.fromkeys(q['issues']))
  for ref in q.get('references',[]):
   if 'evidenceFile' not in ref:
    key=next((key for key,source in manifest.items() if source.get('url')==ref['url'] and (ROOT/'research'/f'{key}.txt').exists()),None)
    if key:
     ref['evidenceFile']=f'research/{key}.txt'
     ref['evidenceSha256']=hashlib.sha256((ROOT/ref['evidenceFile']).read_bytes()).hexdigest()
 (ROOT/'src/data/questions.json').write_text(json.dumps(questions,ensure_ascii=False,indent=2))
 report=json.loads((ROOT/'src/data/import-report.json').read_text())
 report.update(verified=sum(q['verification']=='verified' for q in questions),unverified=sum(q['verification']!='verified' for q in questions),researched=len(reviews),pendingResearch=len(questions)-len(reviews),completedExplanations=sum(set(q['explanations'])=={c['id'] for c in q['choices']} for q in questions),correctedKeys=sum(bool(q.get('verifiedAnswer')) and set(q['verifiedAnswer'])!=set(q['originalAnswer']) for q in questions),reviewedUnresolved=sum(q['verification']!='verified' and q['id'] in reviews for q in questions))
 report['issues']=[{'id':q['id'],'issues':q['issues']} for q in questions if q['issues']]
 (ROOT/'src/data/import-report.json').write_text(json.dumps(report,indent=2))
 ledger=['# Question research checklist','','Every row is a real imported source question. Pending rows have not been reviewed; fetched documentation alone does not complete a row.','','| Question | Research status | Sources |','|---|---|---|']
 for q in questions:
  r=reviews.get(q['id']);state=(r.get('reviewStatus',r['verification']) if r else 'PENDING')
  links='; '.join('['+ref['title']+']('+ref['url']+')' for ref in r['references']) if r else ''
  ledger.append(f"| {q['id']} | {state} | {links} |")
 (ROOT/'research/CHECKLIST.md').write_text('\n'.join(ledger)+'\n')
 print({k:report[k] for k in ['researched','pendingResearch','verified','unverified','completedExplanations','correctedKeys','reviewedUnresolved']})
def reuse(target,source,mapping,correct):
 old=reviews[source];reasons=[old['explanations'][letter] for letter in mapping]
 keys=','.join(next(k for k,v in manifest.items() if v.get('url')==ref['url']) for ref in old['references'])
 review(target,correct,keys,old['references'][0]['section'],old['keyConcept'],old['examTip'],*reasons,status=old.get('reviewStatus'))
