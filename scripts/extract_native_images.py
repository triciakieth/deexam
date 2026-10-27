"""Keep native PDF screenshot pixels instead of downsampling tiny placed code images."""
from pathlib import Path
import fitz,json,re
ROOT=Path(__file__).resolve().parents[1]
qs=json.loads((ROOT/'src/data/questions.json').read_text());out=ROOT/'public/native-images';out.mkdir(exist_ok=True)
docs={b:fitz.open(ROOT/f'public/sources/bank-{b}.pdf') for b in [1,2,3]}
choices=figures=0
for q in qs:
 d=docs[q['bank']];p=d[q['pages'][0]-1];words=p.get_text('words')
 starts=[w for w in words if w[4]==str(q['number'])+'.' and 55<=w[0]<=72]
 if not starts:raise ValueError(q['id'])
 top=starts[0][1]-2
 other=[w[1] for w in words if re.fullmatch(r'\d+\.',w[4]) and 55<=w[0]<=72 and w[1]>top+5]
 bottom=min(other,default=p.rect.height-30)-3
 labels=[w for w in words if re.fullmatch(r'[a-e]\)',w[4]) and 70<w[0]<335 and top<w[1]<bottom]
 first=min([w[1] for w in labels],default=bottom)
 infos=p.get_image_info(xrefs=True)
 def native(info,name):
  if not info['xref']:return None
  data=d.extract_image(info['xref']);name=name+'.'+data['ext'];(out/name).write_bytes(data['image']);return '/native-images/'+name
 q['promptFigures']=[]
 for i,info in enumerate(infos):
  box=fitz.Rect(info['bbox']);cy=(box.y0+box.y1)/2
  if top<cy<first:
   file=native(info,f"{q['id']}-figure-{i}")
   if file:q['promptFigures'].append(file);figures+=1
 for c in q['choices']:
  if len(c['text'].strip())>3:continue
  hits=[w for w in labels if w[4]==c['id']+')']
  if len(hits)!=1:continue
  label=hits[0];rightcol=label[0]>200
  after=[w[1] for w in labels if (w[0]>200)==rightcol and w[1]>label[1]+3]
  end=min(after,default=bottom)
  matches=[]
  for info in infos:
   b=fitz.Rect(info['bbox']);cx=(b.x0+b.x1)/2;cy=(b.y0+b.y1)/2
   if label[1]-3<cy<end and (cx>p.rect.width/2)==rightcol:matches.append(info)
  if len(matches)==1:
   file=native(matches[0],f"{q['id']}-choice-{c['id']}")
   if file:c.setdefault('sourceCrop',c['image']);c['image']=file;choices+=1
(ROOT/'src/data/questions.json').write_text(json.dumps(qs,ensure_ascii=False,indent=2))
print('Preserved native code-choice images:',choices,'native prompt diagrams:',figures)
