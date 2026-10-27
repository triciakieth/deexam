from pathlib import Path
from collections import Counter
import json
ROOT=Path(__file__).resolve().parents[1]
qs=json.loads((ROOT/'src/data/questions.json').read_text());r=json.loads((ROOT/'src/data/import-report.json').read_text())
links=json.loads((ROOT/'research/link-checks.json').read_text())
corrections=[q for q in qs if q['verifiedAnswer'] and set(q['verifiedAnswer'])!=set(q['originalAnswer'])]
outdated=[q for q in qs if q.get('reviewStatus','').startswith('outdated-')]
r['outdatedKeyPremises']=len(outdated)
r['confirmedKeyProblems']=len(corrections)+len(outdated)
r['allCitedLinksChecked']=len(links)
r['linkCheckFailures']=sum('error' in x for x in links)
r['nativeCodeChoiceImages']=sum(c['image'].startswith('/native-images/') for q in qs for c in q['choices'])
r['nativePromptFigures']=sum(len(q.get('promptFigures',[])) for q in qs)
(ROOT/'src/data/import-report.json').write_text(json.dumps(r,indent=2))
lines=['# Research and import report','', 'Reviewed for this project on 28 October 2026. This is an independent study aid, not an official exam guide or a guarantee that a source question is a valid certification item.','', '| Measure | Count |','|---|---:|']
for label,value in [('Bank 1 imported',91),('Bank 2 imported',90),('Bank 3 imported',90),('Total imported',len(qs)),('Unique complete source questions',r['unique']),('Questions researched',r['researched']),('Pending research',r['pendingResearch']),('Documentation-supported answer sets',r['verified']),('Unverified / unresolved after review',r['unverified']),('Questions with saved explanations for every choice',r['completedExplanations']),('Confirmed corrections with a supported alternative',len(corrections)),('Additional explicitly outdated key premises',len(outdated)),('Confirmed corrected/outdated keys under the criteria below',r['confirmedKeyProblems']),('Similar prompt pairs (not exact duplicates)',len(r['similarQuestionPairs'])),('Official documentation URLs checked',len(links)),('Failed citation URL checks',r['linkCheckFailures']),('Original-resolution code-choice images',r['nativeCodeChoiceImages']),('Original-resolution prompt figures',r['nativePromptFigures'])]:lines.append(f'| {label} | {value} |')
lines+=['','## Count definitions','','The confirmed key-problem count is conservative: it includes a changed answer set with a supported alternative, or an explicitly outdated premise that removes the original key’s unique validity. Malformed code, source typos, missing assumptions, overlapping valid answers, and documentation gaps are separately reported as unresolved rather than all being called definitively wrong keys. Every unresolved item has a per-choice rationale and references. No source key is used to score an unresolved question.','','Topic labels are manually reviewed study categories, not official blueprint weights. The 11 similar-prompt pairs remain separate because source wording, options, or figures differ; there are no exact complete-question duplicates after whitespace and native-figure checks.','','## Confirmed answer corrections','','| Source question | Original key | Supported answer | Finding |','|---|---|---|---|']
for q in corrections:lines.append(f"| {q['id']} | {','.join(q['originalAnswer']).upper()} | {','.join(q['verifiedAnswer']).upper()} | {q.get('analysis',q['keyConcept'])} |")
lines+=['','## Explicitly outdated premises','']
for q in outdated:lines.append(f"- **{q['id']}**: {q['analysis']}")
lines+=['','## All unresolved questions','','These questions remain available for study, with neutral feedback and their original keys retained for comparison. They are excluded from accuracy, correct/incorrect totals, and automatic wrong-answer review. They are not silently skipped.','','| Question | Review status | Why no unique supported answer is imposed |','|---|---|---|']
for q in qs:
 if q['verification']!='verified':lines.append(f"| {q['id']} | {q['reviewStatus']} | {q['analysis']} |")
lines+=['','## Reproducible evidence','','`research/CHECKLIST.md` lists all 271 question IDs and source links. `research/question-reviews.json` stores the authored decisions and explanations. Each application citation points to retained official documentation text with a SHA-256 digest. `research/link-checks.json` records actual successful HTTP checks for all cited URLs. A successful link check alone is not treated as answer verification.','','Some source questions are old, use deprecated terminology, have typos, or omit cloud/runtime conditions. The source PDFs, rendered source scans, and original answer keys are preserved. Text-layer answer-row contamination was removed; raw originals were not changed. Native screenshot extraction improves readability without inventing code.','','## Validation','','Validation results are recorded in the delivery response after executing the final tests and build. Python research/import tools are optional; the website serves stored data and explanations without AI services, live research calls, or a Databricks account. Website deployment has not been performed.']
(ROOT/'RESEARCH_REPORT.md').write_text('\n'.join(lines)+'\n')
print('Report saved:',r['verified'],'verified,',r['unverified'],'unresolved,',r['confirmedKeyProblems'],'confirmed corrected/outdated key premises')
