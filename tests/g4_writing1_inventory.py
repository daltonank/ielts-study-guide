#!/usr/bin/env python3
"""G4 inventory — machine-derived counts, with the minimums as hard failures.

Every number this prints is counted from the generated artifact, not asserted
by hand. Each row names the source file and the identifiers it was counted
from, so a reviewer can reproduce it. If a later change reduces coverage below
an approved benchmark, this script fails.

Benchmarks: PROJECT_CHARTER.md section 9, CURRICULUM_SPEC.md section 6,
VALIDATION_SPEC.md section 11 (G4), and docs/requirements_ledger.csv REQ-019
for the band comparison lab.
"""
from pathlib import Path
from collections import Counter
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "web" / "writing1_data.js"
GEN = "scripts/build_writing1_curriculum.py"

REQUIRED_FAMILIES = ["line_graph", "bar_chart", "pie_chart", "table",
                     "process_diagram", "map_plan", "mixed_visual"]
REQUIRED_MICRO_TYPES = ["feature_selection", "overview_selection", "grouping",
                        "trend_language", "comparison_building", "data_to_sentence",
                        "paraphrase_no_distortion", "sentence_correction",
                        "grammar_correction", "paragraph_ordering"]
CYRILLIC = re.compile(r"[Ѐ-ӿ]")
LATIN = re.compile(r"[A-Za-z]")

data = json.loads(re.search(r"window\.WRITING1_DATA=(\{.*\});\s*$",
                            SRC.read_text(encoding="utf-8"), re.S).group(1))
visuals, exercises = data["visuals"], data["exercises"]
prompts, modules = data["prompts"], data["modules"]
bands = data.get("bandComparisons", [])
fam_modules = [m for m in modules if m.get("kind") == "visual_family"]

rows = []
failures = []


def row(metric, actual, minimum, source, identifiers):
    ok = True if minimum is None else (actual >= minimum if isinstance(minimum, int) else actual == minimum)
    rows.append((metric, actual, minimum, "PASS" if ok else "FAIL", source, identifiers))
    if not ok:
        failures.append(f"{metric}: {actual} against a required {minimum}")


# ---- families --------------------------------------------------------------
fams = sorted({v["family"] for v in visuals})
row("Visual families", len(fams), 7, "web/writing1_data.js", "visuals[].family")
if fams != sorted(REQUIRED_FAMILIES):
    failures.append(f"visual family set mismatch: {fams}")
for f in REQUIRED_FAMILIES:
    n = sum(1 for v in visuals if v["family"] == f)
    row(f"  visuals in {f}", n, 3, "web/writing1_data.js", f"visuals[] where family={f}")

# ---- primary benchmarks ----------------------------------------------------
row("Micro-exercises", len(exercises), 60, "web/writing1_data.js", "exercises[] (ids W1X-*)")
row("Full timed prompts", len(prompts), 20, "web/writing1_data.js", "prompts[] (ids W1P-*)")
row("Band comparison sets", len(bands), 7, "web/writing1_data.js", "bandComparisons[] (ids W1B-*)")
row("Band sample responses", sum(len(b["responses"]) for b in bands), 21,
    "web/writing1_data.js", "bandComparisons[].responses[]")
row("Worked examples", sum(len(m.get("workedExamples", [])) for m in modules), 11,
    "web/writing1_data.js", "modules[].workedExamples[]")
row("Annotated model responses",
    sum(1 for p in prompts if p.get("modelResponse") and p.get("modelNotes")), 20,
    "web/writing1_data.js", "prompts[] with modelResponse and modelNotes")
row("Original visuals", len(visuals), 21, "web/writing1_data.js", "visuals[] (ids W1V-*)")
row("Foundation modules", len([m for m in modules if m.get("kind") == "foundation"]), 4,
    "web/writing1_data.js", "modules[] where kind=foundation (ids W1F-*)")
row("Visual-family modules", len(fam_modules), 7,
    "web/writing1_data.js", "modules[] where kind=visual_family (ids W1M-*)")
row("Error taxonomy categories", len(data["errorTaxonomy"]), 10,
    "web/writing1_data.js", "errorTaxonomy[].id")

# ---- timed activities ------------------------------------------------------
timed_ex = [e for e in exercises if e["mode"] in ("timed", "mastery")]
timed_prompts = [p for p in prompts if p.get("estimatedMinutes")]
row("Timed activities (exercises)", len(timed_ex), 14,
    "web/writing1_data.js", "exercises[] where mode in {timed, mastery}")
row("Timed activities (full prompts)", len(timed_prompts), 20,
    "web/writing1_data.js", "prompts[] with estimatedMinutes")
row("Timed activities (total)", len(timed_ex) + len(timed_prompts), 34,
    "web/writing1_data.js", "the two rows above")

# ---- by interaction type ---------------------------------------------------
by_type = Counter(e["type"] for e in exercises)
for t in ("select", "cloze", "order"):
    row(f"Exercises of type {t}", by_type.get(t, 0), 7,
        "web/writing1_data.js", f"exercises[] where type={t}")

# ---- by family and micro-type ---------------------------------------------
by_fam = Counter(e["questionFamily"] for e in exercises)
for f in REQUIRED_FAMILIES:
    row(f"Exercises in {f}", by_fam.get(f, 0), 10,
        "web/writing1_data.js", f"exercises[] where questionFamily={f}")
    types = {e["microType"] for e in exercises if e["questionFamily"] == f}
    row(f"  micro-types in {f}", len(types), 10,
        "web/writing1_data.js", f"distinct exercises[].microType where questionFamily={f}")
    if types != set(REQUIRED_MICRO_TYPES):
        failures.append(f"{f}: micro-type set mismatch, missing {set(REQUIRED_MICRO_TYPES) - types}")
    modes = {e["mode"] for e in exercises if e["questionFamily"] == f}
    if modes != {"guided", "independent", "timed", "mastery"}:
        failures.append(f"{f}: progression modes incomplete {sorted(modes)}")
    row(f"  prompts in {f}", sum(1 for p in prompts if p["questionFamily"] == f), 3,
        "web/writing1_data.js", f"prompts[] where questionFamily={f}")
    row(f"  band sets in {f}", sum(1 for b in bands if b["questionFamily"] == f), 1,
        "web/writing1_data.js", f"bandComparisons[] where questionFamily={f}")

by_type_fam = Counter((e["questionFamily"], e["type"]) for e in exercises)

# ---- bilingual coverage ----------------------------------------------------
ua_ex = sum(1 for e in exercises if CYRILLIC.search(e.get("uaSupport", "")))
ua_pr = sum(1 for p in prompts if CYRILLIC.search(p.get("uaSupport", "")))
ua_bd = sum(1 for b in bands if CYRILLIC.search(b.get("uaSupport", "")))
ua_mod = sum(1 for m in modules if CYRILLIC.search(m.get("uaSupport", "")))
ua_transfer = sum(1 for m in fam_modules if CYRILLIC.search(m.get("uaTransferNote", "")))
ua_tax = sum(1 for c in data["errorTaxonomy"]
             if CYRILLIC.search(c.get("ua", "")) and CYRILLIC.search(c.get("uaCorrection", "")))
row("Ukrainian support on exercises", ua_ex, len(exercises),
    "web/writing1_data.js", "exercises[].uaSupport containing Cyrillic")
row("Ukrainian support on prompts", ua_pr, len(prompts),
    "web/writing1_data.js", "prompts[].uaSupport containing Cyrillic")
row("Ukrainian support on band sets", ua_bd, len(bands),
    "web/writing1_data.js", "bandComparisons[].uaSupport containing Cyrillic")
row("Ukrainian support on modules", ua_mod, len(modules),
    "web/writing1_data.js", "modules[].uaSupport containing Cyrillic")
row("Ukrainian transfer notes", ua_transfer, len(fam_modules),
    "web/writing1_data.js", "modules[].uaTransferNote where kind=visual_family")
row("Ukrainian error taxonomy", ua_tax, len(data["errorTaxonomy"]),
    "web/writing1_data.js", "errorTaxonomy[].ua and .uaCorrection")

en_ex = sum(1 for e in exercises if LATIN.search(e["prompt"]) and LATIN.search(e["explanation"]))
row("English instruction on exercises", en_ex, len(exercises),
    "web/writing1_data.js", "exercises[].prompt and .explanation")
en_lesson = sum(1 for m in modules if m.get("lesson") and all(LATIN.search(x) for x in m["lesson"]))
row("English lesson content on modules", en_lesson, len(modules),
    "web/writing1_data.js", "modules[].lesson[]")

# ---- claim manifest coverage ----------------------------------------------
row("Exercises with a claim manifest", sum(1 for e in exercises if e.get("claim")), len(exercises),
    "web/writing1_data.js", "exercises[].claim")
row("Prompts with a claim manifest", sum(1 for p in prompts if p.get("claim")), len(prompts),
    "web/writing1_data.js", "prompts[].claim")
row("Band sets with a claim manifest", sum(1 for b in bands if b.get("claim")), len(bands),
    "web/writing1_data.js", "bandComparisons[].claim")

# ---- report ----------------------------------------------------------------
w = max(len(r[0]) for r in rows)
print("G4 WRITING TASK 1 INVENTORY (machine-derived)")
print("=" * 100)
print(f"Generated from : {GEN}")
print(f"Counted from   : web/writing1_data.js")
print("=" * 100)
print(f"{'Metric'.ljust(w)}  {'Actual':>7} {'Required':>9}  Status  Identifiers")
print("-" * 100)
for metric, actual, minimum, status, source, ident in rows:
    req = "-" if minimum is None else str(minimum)
    print(f"{metric.ljust(w)}  {actual:>7} {req:>9}  {status:<6}  {ident}")
print("-" * 100)
print("Exercises by family x interaction type:")
for f in REQUIRED_FAMILIES:
    parts = ", ".join(f"{t} {by_type_fam.get((f, t), 0)}" for t in ("select", "cloze", "order"))
    print(f"  {f.ljust(18)} {parts}")

if failures:
    print()
    for f in failures:
        print("FAIL:", f)
    print("Total failures:", len(failures))
    sys.exit(1)
print("\nPASS: every approved G4 benchmark met or exceeded")
