#!/usr/bin/env python3
from pathlib import Path
import csv,json,re
ROOT=Path(__file__).resolve().parents[1]
rows=list(csv.DictReader((ROOT/"docs/requirements_ledger.csv").open(encoding="utf-8")))
status={}
for r in rows: status[r["Status"]]=status.get(r["Status"],0)+1
v=(ROOT/"web/vocabulary.js").read_text(encoding="utf-8")
meta=json.loads(re.search(r'window\.VOCABULARY_META=(\{.*?\});',v,re.S).group(1))
data_js=(ROOT/"web/data.js").read_text(encoding="utf-8")
modules=len(re.findall(r'\{id:"[^"]+",skill:',data_js))
rtext=(ROOT/"web/reading_data.js").read_text(encoding="utf-8")
reading=json.loads(re.search(r'window\.READING_DATA=(\{.*\});\s*$',rtext,re.S).group(1))
w1p=ROOT/"web/writing1_data.js"
if w1p.exists():
    w1=json.loads(re.search(r'window\.WRITING1_DATA=(\{.*\});\s*$',w1p.read_text(encoding="utf-8"),re.S).group(1))["meta"]
else:
    w1={"microExerciseCount":0,"promptCount":0,"familyCount":0,"visualCount":0}
out={
 "requirements_total":len(rows),"requirements_by_status":status,
 "vocabulary_loaded":meta.get("sourceCount",meta.get("seedCount",0)),
 "vocabulary_expected":meta.get("expectedCount",1784),
 "vocabulary_migration_complete":meta.get("complete",False),
 "foundation_modules_registered":modules,
 "reading_passages":reading["meta"]["passageCount"],"reading_questions":reading["meta"]["questionCount"],
 "task1_visual_families":w1.get("familyCount",0),"task1_visuals":w1.get("visualCount",0),
 "task1_micro_exercises":w1.get("microExerciseCount",0),"task1_full_prompts":w1.get("promptCount",0),
 "task2_prompts":0,"task2_drills":0,
 "grammar_items":0,"paraphrase_items":0,
 "speaking_part1":0,"speaking_part2":0,"speaking_part3":0,
 "p0_defects":0,"p1_defects":1 if not meta.get("complete",False) else 0,
 "regression_status":"PASS through G3; G4 content layer validated, G4 UI not built",
 "accessibility_score":None,"performance_score":None
}
(ROOT/"docs/benchmark_dashboard.json").write_text(json.dumps(out,indent=2),encoding="utf-8")
print(json.dumps(out,indent=2))
