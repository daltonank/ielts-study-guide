#!/usr/bin/env python3
"""Mechanically reconcile every registered P1 finding after T2-T4 closeout."""

import csv
import json
import pathlib
import re


ROOT = pathlib.Path(__file__).resolve().parents[1]


def load_json(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


manifest = load_json("docs/g4a_p1_batches.json")
t2 = load_json("scripts/qa/p1_t2_corrections.json")
t3 = load_json("scripts/qa/p1_t3_corrections.json")
t4 = load_json("scripts/qa/p1_t4_corrections.json")

with (ROOT / "docs/G4A_UKRAINIAN_QA_FINDINGS.csv").open(encoding="utf-8", newline="") as handle:
    rows = list(csv.DictReader(handle))
p1 = {row["id"] for row in rows if row["severity"] == "P1"}
p2 = {row["id"] for row in rows if row["severity"] == "P2"}

prior = {"SB-0208", "SB-1728", "SB-1160"}
t2_ids = set(t2["corrections"])
t3_ids = set(t3["corrections"])
t3_no_edit = set(t3["_meta"]["resolved_without_edit"])
t3_deferred = set(t3["_meta"]["deferred"])
t4_ids = set(t4["corrections"])

assert len(p1) == 314 and len(p2) == 246
assert t2_ids == set(manifest["T2"])
assert t3_ids | t3_no_edit | t3_deferred == set(manifest["T3"])
assert not (t3_ids & t3_no_edit or t3_ids & t3_deferred or t3_no_edit & t3_deferred)
assert t4_ids == set(manifest["T4"])
assert len(t2_ids) == 104
assert len(t3_ids) == 102 and t3_no_edit == {"SB-0425"} and t3_deferred == {"SB-0773"}
assert len(t4_ids) == 103

resolved = prior | t2_ids | t3_ids | t3_no_edit | t4_ids | t3_deferred
assert resolved == p1

text = (ROOT / "web/vocabulary.js").read_text(encoding="utf-8")
vocab = json.loads(re.search(r"window\.VOCABULARY=(\[.*\]);", text, re.DOTALL).group(1))
by_id = {entry["id"]: entry for entry in vocab}
for item_id in t2_ids | t3_ids | t4_ids | t3_deferred:
    assert by_id[item_id]["translationQa"].startswith("Reviewed — G4-A P1")
assert by_id["SB-0424"]["ua"] == "результативність"
assert by_id["SB-0425"]["ua"] == "ефективність"
assert by_id["SB-0773"]["word"] == "minute"

print("G4-A P1 CLOSEOUT PASS")
print("registered P1=314 resolved=314 unresolved=0; registered P2=246 unchanged")
print("T3: 102 edited, 1 resolved via sibling, 1 structural follow-up")
