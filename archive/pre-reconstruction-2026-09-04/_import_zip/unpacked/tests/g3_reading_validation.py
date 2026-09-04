#!/usr/bin/env python3
from pathlib import Path
import json,re,sys,string
ROOT=Path(__file__).resolve().parents[1]
text=(ROOT/'web'/'reading_data.js').read_text(encoding='utf-8')
m=re.search(r'window\.READING_DATA=(\{.*\});\s*$',text,re.S)
if not m:
    raise SystemExit('FAIL: could not parse READING_DATA')
data=json.loads(m.group(1))
errors=[]
required_families={
'multiple_choice','tfng','ynng','matching_information','matching_headings','matching_features','matching_sentence_endings',
'sentence_completion','summary_completion','note_completion','table_completion','flow_chart_completion','diagram_label','short_answer','inference_author'}
passages=data['passages']; modules=data['modules']; questions=[q for p in passages for q in p['questions']]

def fail(msg): errors.append(msg)
def norm(x): return ' '.join(str(x or '').lower().strip().rstrip('.,;:!?').split())

if len(passages)<50: fail(f'passage count {len(passages)} < 50')
if len(questions)<200: fail(f'question count {len(questions)} < 200')
if set(p['family'] for p in passages)!=required_families: fail('question-family coverage mismatch')
if len(data['familyMeta'])!=15: fail('familyMeta count != 15')
if len([m for m in modules if m.get('kind')=='foundation'])<8: fail('foundation modules < 8')
if len([m for m in modules if m.get('kind')=='question_family'])<15: fail('question-family modules < 15')

pids=[p['id'] for p in passages]
qids=[q['id'] for q in questions]
mids=[m['id'] for m in modules]
if len(pids)!=len(set(pids)): fail('duplicate passage IDs')
if len(qids)!=len(set(qids)): fail('duplicate question IDs')
if len(mids)!=len(set(mids)): fail('duplicate module IDs')

module_ids=set(mids); qidset=set(qids)
for m in modules:
    for req in ['id','title','skill','subskill','difficulty','objectives','lesson','exercises','masteryCheck','prerequisites','errorCategories']:
        if req not in m: fail(f"module {m.get('id')} missing {req}")
    for prereq in m.get('prerequisites',[]):
        if prereq not in module_ids: fail(f'module {m["id"]} invalid prereq {prereq}')
    for mq in m.get('masteryCheck',[]):
        if mq not in qidset: fail(f'module {m["id"]} invalid mastery question {mq}')

for p in passages:
    if p['moduleId'] not in module_ids: fail(f'{p["id"]}: invalid moduleId')
    if len(p.get('paragraphs',[]))<1: fail(f'{p["id"]}: no passage text')
    if len(p.get('questions',[]))!=4: fail(f'{p["id"]}: expected 4 questions')
    if p.get('originality')!='original': fail(f'{p["id"]}: non-original passage flag')
    full=' '.join(p.get('paragraphs',[])).lower()
    for q in p['questions']:
        for req in ['id','type','skill','questionFamily','difficulty','prompt','correctAnswer','explanation','errorCategory','estimatedMinutes','originality']:
            if req not in q or (isinstance(q.get(req),str) and not q.get(req).strip()): fail(f'{q.get("id")}: missing/blank {req}')
        if not q.get('explanation','').strip(): fail(f'{q["id"]}: blank explanation')
        if q['type']=='select':
            if not q.get('options'): fail(f'{q["id"]}: select without options')
            opts={norm(x) for x in q.get('options',[])}
            if norm(q['correctAnswer']) not in opts: fail(f'{q["id"]}: correct answer absent from options')
            for opt in q.get('options',[]):
                if norm(opt)!=norm(q['correctAnswer']) and not str(q.get('distractorReasoning',{}).get(opt,'')).strip():
                    fail(f'{q["id"]}: missing distractor reasoning for {opt}')
        if q['type']=='text' and q['questionFamily'] in {'sentence_completion','summary_completion','note_completion','flow_chart_completion','diagram_label','short_answer','table_completion'}:
            # Completion/short-answer answers should be directly grounded in the passage.
            if norm(q['correctAnswer']) not in norm(full): fail(f'{q["id"]}: text answer not grounded in passage')

# Family distribution and progression.
for fam in required_families:
    ps=[p for p in passages if p['family']==fam]
    if len(ps)<4: fail(f'{fam}: fewer than four passages')
    modes={p['mode'] for p in ps}
    if modes!={'guided','independent','timed','mastery'}: fail(f'{fam}: progression modes incomplete {modes}')
    if sum(len(p['questions']) for p in ps)<16: fail(f'{fam}: fewer than 16 questions')

explanation_rate=sum(1 for q in questions if q.get('explanation','').strip())/len(questions)
print('G3 READING CONTENT VALIDATION')
print('=============================')
print('Passages:',len(passages))
print('Questions:',len(questions))
print('Families:',len(required_families))
print('Modules:',len(modules))
print('Explanation coverage:',f'{explanation_rate:.0%}')
if errors:
    for e in errors[:100]: print('FAIL:',e)
    print('Total failures:',len(errors))
    sys.exit(1)
print('PASS: G3 inventory, schemas, IDs, grounding, family coverage and answer reasoning')
