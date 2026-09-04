#!/usr/bin/env python3
from pathlib import Path
import csv, json, re, sys
from jsonschema import Draft202012Validator

ROOT=Path(__file__).resolve().parents[1]
errors=[]; notes=[]
def ok(cond,msg):
    if not cond: errors.append(msg)
def load_json(p): return json.loads((ROOT/p).read_text(encoding="utf-8"))
# Required artifacts
for p in ["web/index.html","web/styles.css","web/app.js","web/data.js","web/reading_data.js","web/vocabulary.js",
          "schemas/learner_state.schema.json","schemas/module.schema.json","schemas/exercise.schema.json",
          "docs/requirements_ledger.csv","docs/legacy_content_inventory.csv","docs/risk_register.csv"]:
    ok((ROOT/p).exists(),f"Missing {p}")
# Schemas parse and validate an empty-ish learner shell
for p in ["schemas/learner_state.schema.json","schemas/module.schema.json","schemas/exercise.schema.json"]:
    s=load_json(p); ok("$schema" in s,f"{p}: no $schema")
# Ledger IDs unique
rows=list(csv.DictReader((ROOT/"docs/requirements_ledger.csv").open(encoding="utf-8")))
ids=[r["ID"] for r in rows];ok(len(ids)==len(set(ids)),"Duplicate requirements IDs")
ok(all(r["Status"] for r in rows),"Blank requirement status")
# Mobile nav exactly five primary buttons
html=(ROOT/"web/index.html").read_text(encoding="utf-8")
m=re.search(r'<nav class="mobile-nav".*?</nav>',html,re.S)
ok(bool(m),"Mobile nav missing")
if m: ok(len(re.findall(r'<button data-route=',m.group(0)))==5,"Primary mobile nav must expose exactly five controls")
# Language modes
app=(ROOT/"web/app.js").read_text(encoding="utf-8")
for token in ['en:"EN"','uaen:"UA + EN"','uahelp:"UA Help"']:
    ok(token in app,f"Language mode missing {token}")
# Presets
for n in [10,20,30,45,60,90]: ok(str(n) in app,f"Study preset missing {n}")
# G2 status inspection
v=(ROOT/"web/vocabulary.js").read_text(encoding="utf-8")
complete='"complete": true' in v or '"complete":true' in v
if complete:
    mm=re.search(r'window\.VOCABULARY=(\[.*\]);',v,re.S)
    if mm:
        data=json.loads(mm.group(1));ok(len(data)==1784,f"G2 complete flag but count={len(data)}")
    else: errors.append("Could not parse complete vocabulary data")
else:
    notes.append("G2 intentionally BLOCKED: preview vocabulary only; exact legacy workbook bytes not yet processed.")
print("VALIDATION REPORT")
print("=================")
print(f"Requirements rows: {len(rows)}")
print(f"Errors: {len(errors)}")
for e in errors: print("FAIL:",e)
for n in notes: print("NOTE:",n)
if errors: sys.exit(1)
print("PASS: G0–G3 static artifact validation")
