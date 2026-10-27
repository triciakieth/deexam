"""Human-reviewed study categories (not an assertion of official blueprint weights)."""
import json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
names={'P':'Platform & compute','D':'Delta Lake & storage','T':'Data transformation & modeling','I':'Ingestion & streaming','G':'Governance & security','O':'Deployment & orchestration','Q':'Data quality & pipelines'}
groups={
1:{'P':[1,2,3,37,58,61,62,65,69,70,76,79,83], 'G':[11,13,14,59,66,67,74,78], 'D':[4,5,6,7,9,16,25,44,71,75,80,81,82,85,89], 'T':[12,15,17,18,22,23,24,26,29,30,34,36,40,45,72,73,77,84,86,90,91], 'I':[20,21,28,31,32,33,39,46,50,52,88], 'Q':[27,35,38,41,47,48,49,51], 'O':[8,10,19,42,43,53,54,55,56,57,60,63,64,68,87]},
2:{'P':[7,8,11,18,20,24,33,38,39,40,80,86], 'D':[13,17,21,22,57,59,65,66,69,73], 'T':[1,2,3,4,5,6], 'I':[9,12,14,16,19,32,60], 'Q':[10,15,23,27,31,41,72,74,75,77], 'G':[42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,58,61,62,63,64,67,68,70,71,76], 'O':[25,26,28,29,30,34,35,36,37,78,79,81,82,83,84,85,87,88,89,90]},
3:{'P':[8,13,17,40,41,42,43,50,58,61,63,64,66,70,71,75,76,77,78,79,81,82,83,84,85,88], 'O':[1,2,3,4,5,6,9,10,11,12,14,15,19,87,90], 'Q':[7,16,18], 'I':[20,21,23,24,25,26,27,28,30,33,34,35,36,47,59,32], 'D':[22,29,56,60,62,68,80,86,89], 'T':[31,37,38,39,44,45,46,48,49,51,52,53,54,55,57,65,67,69,73,74], 'G':[72]}}
lookup={}
for b,values in groups.items():
 for key,numbers in values.items():
  for number in numbers:
   qid=f'b{b}-q{number}';assert qid not in lookup,qid;lookup[qid]=names[key]
questions=json.loads((root/'src/data/questions.json').read_text());missing=[q['id'] for q in questions if q['id'] not in lookup];assert not missing,missing
assert len(lookup)==len(questions)
for q in questions:q['topic']=lookup[q['id']]
(root/'src/data/questions.json').write_text(json.dumps(questions,ensure_ascii=False,indent=2))
print('Assigned study categories to',len(questions),'questions')
