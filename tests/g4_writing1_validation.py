#!/usr/bin/env python3
"""G4 Writing Task 1 content validation.

Follows the template in docs/development_design_plan.md section 5 and the
precedent set by tests/g3_reading_validation.py: this script re-parses the
generated artifact and re-derives every check from the specification, never
from the generator. In particular the fact engine below is an independent
re-implementation, so a bug in scripts/build_writing1_curriculum.py that
produced self-consistent but wrong facts would still fail here.

Requirements checked (PROJECT_CHARTER.md section 9, CURRICULUM_SPEC.md
section 6, VALIDATION_SPEC.md section 11 G4):
  7 visual families, >=60 micro-exercises, >=20 full prompts, family coverage
  as set equality, unique IDs, required fields, reference integrity,
  progression-mode coverage, answer and model-response grounding in the item's
  own data, wrong-option reasoning, originality, and honest scoring language.
"""
from pathlib import Path
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]

# --- Specification constants, restated here rather than imported ------------
REQUIRED_FAMILIES = {
    "line_graph", "bar_chart", "pie_chart", "table",
    "process_diagram", "map_plan", "mixed_visual",
}
REQUIRED_MICRO_TYPES = {
    "feature_selection", "overview_selection", "comparison_building",
    "data_to_sentence", "sentence_correction", "grouping",
    "paragraph_ordering", "trend_language", "grammar_correction",
    "paraphrase_no_distortion",
}
REQUIRED_MODES = {"guided", "independent", "timed", "mastery"}
MIN_MICRO_EXERCISES = 60
MIN_PROMPTS = 20
MIN_FAMILIES = 7
TASK_MINUTES = 20
WORD_MINIMUM = 150

EXERCISE_REQUIRED_FIELDS = [
    "id", "type", "skill", "questionFamily", "difficulty", "prompt",
    "correctAnswer", "explanation", "errorCategory", "estimatedMinutes",
    "originality", "visualId", "microType", "mode", "uaSupport", "grounding",
]
PROMPT_REQUIRED_FIELDS = [
    "id", "type", "skill", "questionFamily", "difficulty", "prompt",
    "taskStatement", "estimatedMinutes", "originality", "visualId", "mode",
    "planning", "checklist", "modelResponse", "modelNotes", "targetFeatures",
    "errorCategory", "explanation", "uaSupport", "scoringNote", "wordMinimum",
]
MODULE_REQUIRED_FIELDS = [
    "id", "title", "skill", "subskill", "difficulty", "objectives", "lesson",
    "exercises", "masteryCheck", "prerequisites", "errorCategories",
]
DIFFICULTY_ENUM = {"foundation", "6.5", "7", "7.5", "8"}

cyrillic = re.compile(r"[Ѐ-ӿ]")
errors = []


def fail(msg):
    errors.append(msg)


# --- Parse the artifact independently ---------------------------------------
text = (ROOT / "web" / "writing1_data.js").read_text(encoding="utf-8")
m = re.search(r"window\.WRITING1_DATA=(\{.*\});\s*$", text, re.S)
if not m:
    raise SystemExit("FAIL: could not parse WRITING1_DATA out of web/writing1_data.js")
data = json.loads(m.group(1))

visuals = data["visuals"]
exercises = data["exercises"]
prompts = data["prompts"]
modules = data["modules"]
taxonomy = data["errorTaxonomy"]
visual_by_id = {v["id"]: v for v in visuals}
taxonomy_ids = {e["id"] for e in taxonomy}


# --- Independent fact engine -------------------------------------------------
def rnd(x, places=2):
    r = round(float(x), places)
    return int(r) if abs(r - int(r)) < 1e-9 else r


def series_facts(cats, series, prefix=""):
    f = {}
    for s in series:
        name, vals = s["name"], s["values"]
        for c, v in zip(cats, vals):
            f[f"{prefix}value.{name}.{c}"] = rnd(v)
        hi, lo = max(vals), min(vals)
        f[f"{prefix}max.{name}"] = rnd(hi)
        f[f"{prefix}min.{name}"] = rnd(lo)
        f[f"{prefix}max_at.{name}"] = cats[vals.index(hi)]
        f[f"{prefix}min_at.{name}"] = cats[vals.index(lo)]
        f[f"{prefix}first.{name}"] = rnd(vals[0])
        f[f"{prefix}last.{name}"] = rnd(vals[-1])
        f[f"{prefix}delta.{name}"] = rnd(vals[-1] - vals[0])
        if vals[0]:
            f[f"{prefix}pct_change.{name}"] = rnd((vals[-1] - vals[0]) / vals[0] * 100, 1)
        for i in range(len(cats)):
            for j in range(i + 1, len(cats)):
                f[f"{prefix}change.{name}.{cats[i]}.{cats[j]}"] = rnd(vals[j] - vals[i])
    for i, c in enumerate(cats):
        col = sorted(((s["name"], s["values"][i]) for s in series), key=lambda t: -t[1])
        f[f"{prefix}top.{c}"] = col[0][0]
        f[f"{prefix}bottom.{c}"] = col[-1][0]
        f[f"{prefix}total.{c}"] = rnd(sum(v for _, v in col))
        f[f"{prefix}rank.{c}"] = " > ".join(n for n, _ in col)
        for a in range(len(series)):
            for b in range(a + 1, len(series)):
                f[f"{prefix}gap.{series[a]['name']}.{series[b]['name']}.{c}"] = rnd(
                    series[a]["values"][i] - series[b]["values"][i])
    return f


def pie_facts(snapshots, prefix=""):
    f = {}
    for snap in snapshots:
        lab, slices = snap["label"], snap["slices"]
        for sl in slices:
            f[f"{prefix}share.{sl['label']}.{lab}"] = rnd(sl["value"])
        ordered = sorted(slices, key=lambda s: -s["value"])
        f[f"{prefix}largest.{lab}"] = ordered[0]["label"]
        f[f"{prefix}smallest.{lab}"] = ordered[-1]["label"]
        f[f"{prefix}total.{lab}"] = rnd(sum(s["value"] for s in slices))
        f[f"{prefix}rank.{lab}"] = " > ".join(s["label"] for s in ordered)
        for a in range(len(slices)):
            for b in range(a + 1, len(slices)):
                la, lb = slices[a]["label"], slices[b]["label"]
                f[f"{prefix}gap.{la}.{lb}.{lab}"] = rnd(slices[a]["value"] - slices[b]["value"])
                f[f"{prefix}sum.{la}.{lb}.{lab}"] = rnd(slices[a]["value"] + slices[b]["value"])
    if len(snapshots) == 2:
        a = {s["label"]: s["value"] for s in snapshots[0]["slices"]}
        for sl in snapshots[1]["slices"]:
            if sl["label"] in a:
                f[f"{prefix}delta_share.{sl['label']}"] = rnd(sl["value"] - a[sl["label"]])
    return f


def table_facts(columns, rows, prefix=""):
    f = {}
    for r in rows:
        for c, v in zip(columns, r["cells"]):
            f[f"{prefix}value.{r['label']}.{c}"] = rnd(v)
    for i, c in enumerate(columns):
        col = sorted(((r["label"], r["cells"][i]) for r in rows), key=lambda t: -t[1])
        f[f"{prefix}max.{c}"] = col[0][0]
        f[f"{prefix}min.{c}"] = col[-1][0]
        f[f"{prefix}total.{c}"] = rnd(sum(v for _, v in col))
    for r in rows:
        for i in range(len(columns)):
            for j in range(i + 1, len(columns)):
                f[f"{prefix}delta.{r['label']}.{columns[i]}.{columns[j]}"] = rnd(r["cells"][j] - r["cells"][i])
    return f


def derive_facts(v):
    k = v["kind"]
    if k in ("line", "bar"):
        return series_facts(v["categories"], v["series"])
    if k == "pie":
        return pie_facts(v["snapshots"])
    if k == "table":
        return table_facts(v["columns"], v["rows"])
    if k == "process":
        f = {
            "stage_count": len(v["stages"]),
            "input": v["input"],
            "output": v["output"],
            "cyclical": "yes" if v["cyclical"] else "no",
            "first_stage": v["stages"][0]["label"],
            "last_stage": v["stages"][-1]["label"],
        }
        for st in v["stages"]:
            f[f"stage.{st['n']}"] = st["label"]
        return f
    if k == "map":
        f = {}
        counts = {"added": 0, "removed": 0, "replaced": 0, "unchanged": 0}
        for ft in v["features"]:
            f[f"status.{ft['label']}"] = ft["status"]
            f[f"area.{ft['label']}"] = ft["area"]
            counts[ft["status"]] += 1
        for kk, n in counts.items():
            f[f"count.{kk}"] = n
        f["feature_count"] = len(v["features"])
        return f
    if k == "mixed":
        f = {}
        for i, c in enumerate(v["components"]):
            p = f"c{i}."
            if c["kind"] in ("line", "bar"):
                f.update(series_facts(c["categories"], c["series"], p))
            elif c["kind"] == "pie":
                f.update(pie_facts(c["snapshots"], p))
            elif c["kind"] == "table":
                f.update(table_facts(c["columns"], c["rows"], p))
        return f
    raise ValueError(f"unknown kind {v['kind']}")


# "Task 1" and "Task 2" are the names of the exam tasks, not data claims, so
# they are removed before any figure in a text is checked against a visual.
TASK_LABEL = re.compile(r"\bTask\s*[12]\b", re.I)


def digits(s):
    return {rnd(float(t)) for t in re.findall(r"\d+(?:\.\d+)?", TASK_LABEL.sub("Task", str(s)))}


def derive_support(v):
    """Every figure a claim about this visual may legitimately contain."""
    nums = set()
    for val in derive_facts(v).values():
        if isinstance(val, (int, float)) and not isinstance(val, bool):
            nums.add(rnd(val))
            nums.add(rnd(abs(val)))

    def add_series(cats, series):
        for s in series:
            for x in s["values"]:
                nums.add(rnd(x))
        for c in cats:
            nums.update(digits(c))

    def add_pie(snaps):
        for snap in snaps:
            nums.update(digits(snap["label"]))
            for sl in snap["slices"]:
                nums.add(rnd(sl["value"]))

    def add_table(columns, rows):
        for r in rows:
            for x in r["cells"]:
                nums.add(rnd(x))
        for c in columns:
            nums.update(digits(c))

    k = v["kind"]
    if k in ("line", "bar"):
        add_series(v["categories"], v["series"])
    elif k == "pie":
        add_pie(v["snapshots"])
    elif k == "table":
        add_table(v["columns"], v["rows"])
    elif k == "process":
        nums |= set(range(1, len(v["stages"]) + 1))
    elif k == "map":
        for p in v["periods"]:
            nums |= digits(p)
        nums |= set(range(0, len(v["features"]) + 1))
    elif k == "mixed":
        for c in v["components"]:
            if c["kind"] in ("line", "bar"):
                add_series(c["categories"], c["series"])
            elif c["kind"] == "pie":
                add_pie(c["snapshots"])
            elif c["kind"] == "table":
                add_table(c["columns"], c["rows"])
    for field in ("timeframe", "unit"):
        nums |= digits(v.get(field, ""))
    return {float(n) for n in nums}


# --- 1. Quantitative benchmarks ---------------------------------------------
families_present = {v["family"] for v in visuals}
if families_present != REQUIRED_FAMILIES:
    fail(f"visual family coverage mismatch: missing {REQUIRED_FAMILIES - families_present}, "
         f"unexpected {families_present - REQUIRED_FAMILIES}")
if len(families_present) < MIN_FAMILIES:
    fail(f"family count {len(families_present)} < {MIN_FAMILIES}")
if len(exercises) < MIN_MICRO_EXERCISES:
    fail(f"micro-exercise count {len(exercises)} < {MIN_MICRO_EXERCISES}")
if len(prompts) < MIN_PROMPTS:
    fail(f"full prompt count {len(prompts)} < {MIN_PROMPTS}")

ex_families = {e["questionFamily"] for e in exercises}
if ex_families != REQUIRED_FAMILIES:
    fail(f"exercise family coverage mismatch: {REQUIRED_FAMILIES ^ ex_families}")
pr_families = {p["questionFamily"] for p in prompts}
if pr_families != REQUIRED_FAMILIES:
    fail(f"prompt family coverage mismatch: {REQUIRED_FAMILIES ^ pr_families}")

# --- 2. Per-family depth: every micro-type and every progression mode --------
for fam in sorted(REQUIRED_FAMILIES):
    fam_ex = [e for e in exercises if e["questionFamily"] == fam]
    types = {e["microType"] for e in fam_ex}
    if types != REQUIRED_MICRO_TYPES:
        fail(f"{fam}: micro-type coverage mismatch, missing {REQUIRED_MICRO_TYPES - types}")
    modes = {e["mode"] for e in fam_ex}
    if modes != REQUIRED_MODES:
        fail(f"{fam}: exercise progression modes incomplete {modes}")
    fam_pr = [p for p in prompts if p["questionFamily"] == fam]
    if len(fam_pr) < 3:
        fail(f"{fam}: fewer than three full prompts ({len(fam_pr)})")
    pr_modes = {p["mode"] for p in fam_pr}
    if not {"guided", "independent", "timed"} <= pr_modes:
        fail(f"{fam}: full prompts do not cover guided, independent and timed ({pr_modes})")
    fam_vis = [v for v in visuals if v["family"] == fam]
    if len(fam_vis) < 3:
        fail(f"{fam}: fewer than three visuals ({len(fam_vis)})")

# --- 3. Unique IDs -----------------------------------------------------------
for label, seq in (("visual", visuals), ("exercise", exercises), ("prompt", prompts), ("module", modules)):
    ids = [x["id"] for x in seq]
    if len(ids) != len(set(ids)):
        dupes = {i for i in ids if ids.count(i) > 1}
        fail(f"duplicate {label} IDs: {sorted(dupes)}")
all_ids = [x["id"] for x in visuals + exercises + prompts + modules]
if len(all_ids) != len(set(all_ids)):
    fail("IDs collide across record types")

# --- 4. Visual integrity and originality ------------------------------------
for v in visuals:
    if v.get("originality") != "original":
        fail(f"{v['id']}: originality flag is {v.get('originality')!r}")
    if not str(v.get("altText", "")).strip():
        fail(f"{v['id']}: missing altText (UX_DESIGN_SPEC.md section 17 requires a text equivalent)")
    if len(str(v.get("altText", ""))) < 80:
        fail(f"{v['id']}: altText too short to substitute for the visual")
    if not str(v.get("taskStatement", "")).strip():
        fail(f"{v['id']}: missing taskStatement")
    if not str(v.get("sourceNote", "")).strip():
        fail(f"{v['id']}: missing sourceNote")
    derived = derive_facts(v)
    if v.get("facts") != derived:
        differing = [k for k in set(derived) | set(v.get("facts", {}))
                     if derived.get(k) != v.get("facts", {}).get(k)]
        fail(f"{v['id']}: stored facts do not match independently derived facts ({differing[:5]})")
    if v["kind"] == "pie":
        for snap in v["snapshots"]:
            total = sum(s["value"] for s in snap["slices"])
            if abs(total - 100) > 0.5:
                fail(f"{v['id']}: pie snapshot {snap['label']} sums to {total}, not 100")
    if v["kind"] == "mixed":
        for c in v["components"]:
            if c["kind"] == "pie":
                for snap in c["snapshots"]:
                    total = sum(s["value"] for s in snap["slices"])
                    if abs(total - 100) > 0.5:
                        fail(f"{v['id']}: component pie {snap['label']} sums to {total}, not 100")
    if v["kind"] == "map":
        for ft in v["features"]:
            if ft["status"] not in {"added", "removed", "replaced", "unchanged"}:
                fail(f"{v['id']}: feature {ft['label']} has invalid status {ft['status']}")
    if v["kind"] == "process":
        ns = [s["n"] for s in v["stages"]]
        if ns != list(range(1, len(ns) + 1)):
            fail(f"{v['id']}: process stages are not numbered consecutively from 1")

# --- 5. Exercise fields, references and grounding ---------------------------
for e in exercises:
    eid = e["id"]
    for field in EXERCISE_REQUIRED_FIELDS:
        val = e.get(field)
        if val is None or (isinstance(val, str) and not val.strip()) or (isinstance(val, list) and not val):
            fail(f"{eid}: missing or blank required field {field}")
    if e.get("difficulty") not in DIFFICULTY_ENUM:
        fail(f"{eid}: difficulty {e.get('difficulty')!r} outside the approved enum")
    if e.get("originality") != "original":
        fail(f"{eid}: originality flag is {e.get('originality')!r}")
    if e.get("microType") not in REQUIRED_MICRO_TYPES:
        fail(f"{eid}: unknown microType {e.get('microType')!r}")
    if e.get("errorCategory") not in taxonomy_ids:
        fail(f"{eid}: errorCategory {e.get('errorCategory')!r} is not in the error taxonomy")
    if e.get("visualId") not in visual_by_id:
        fail(f"{eid}: visualId {e.get('visualId')!r} does not exist")
        continue
    v = visual_by_id[e["visualId"]]
    if v["family"] != e["questionFamily"]:
        fail(f"{eid}: visual {v['id']} belongs to {v['family']}, not {e['questionFamily']}")

    facts = derive_facts(v)
    for key in e["grounding"]:
        if key not in facts:
            fail(f"{eid}: grounding key {key!r} is not derivable from {v['id']}")

    allowed_extra = set(e.get("allowedNumbers", []) or [])
    for n in allowed_extra:
        if n > 10:
            fail(f"{eid}: allowedNumbers entry {n} exceeds 10, so it may be a data claim in disguise")
    if allowed_extra and not str(e.get("allowedNumbersReason", "")).strip():
        fail(f"{eid}: allowedNumbers declared without allowedNumbersReason")

    support = derive_support(v) | {float(n) for n in allowed_extra}
    option_numbers = set()
    for opt in e.get("options", []) or []:
        option_numbers |= {float(x) for x in digits(opt)}

    # The correct answer may only contain figures the visual supports.
    if e["type"] == "select":
        for n in digits(e["correctAnswer"]):
            if float(n) not in support:
                fail(f"{eid}: correct answer cites {n}, which is not derivable from {v['id']}")
    # The explanation may additionally quote a figure offered by a wrong option.
    for n in digits(e["explanation"]):
        if float(n) not in support | option_numbers:
            fail(f"{eid}: explanation cites {n}, which is neither in {v['id']} nor in any option")

    if e["type"] == "select":
        opts = e.get("options") or []
        if len(opts) < 3:
            fail(f"{eid}: select item has fewer than three options")
        if e["correctAnswer"] not in opts:
            fail(f"{eid}: correct answer is not among the options")
        reasoning = e.get("distractorReasoning") or {}
        for opt in opts:
            if opt == e["correctAnswer"]:
                continue
            if not str(reasoning.get(opt, "")).strip():
                fail(f"{eid}: no reasoning given for wrong option {opt[:48]!r}")
    elif e["type"] == "cloze":
        if "____" not in e.get("sentence", ""):
            fail(f"{eid}: cloze sentence has no gap marker")
        accept = e.get("acceptableAnswers") or []
        if e["correctAnswer"] not in accept:
            fail(f"{eid}: correct answer is not present in acceptableAnswers")
    elif e["type"] == "order":
        item_ids = [i["id"] for i in e.get("items", [])]
        if len(item_ids) < 3:
            fail(f"{eid}: ordering item has fewer than three parts")
        if sorted(item_ids) != sorted(e["correctAnswer"]):
            fail(f"{eid}: correctAnswer is not a permutation of the item ids")
        if len(set(item_ids)) != len(item_ids):
            fail(f"{eid}: duplicate ordering item ids")
    else:
        fail(f"{eid}: unknown interaction type {e['type']!r}")

# --- 6. Prompt fields, model responses and grounding ------------------------
for p in prompts:
    pid = p["id"]
    for field in PROMPT_REQUIRED_FIELDS:
        val = p.get(field)
        if val is None or (isinstance(val, str) and not val.strip()) or (isinstance(val, (list, dict)) and not val):
            fail(f"{pid}: missing or blank required field {field}")
    if p.get("originality") != "original":
        fail(f"{pid}: originality flag is {p.get('originality')!r}")
    if p.get("estimatedMinutes") != TASK_MINUTES:
        fail(f"{pid}: estimatedMinutes is {p.get('estimatedMinutes')}, not the {TASK_MINUTES} Task 1 allows")
    if p.get("wordMinimum") != WORD_MINIMUM:
        fail(f"{pid}: wordMinimum is {p.get('wordMinimum')}, not {WORD_MINIMUM}")
    if p.get("errorCategory") not in taxonomy_ids:
        fail(f"{pid}: errorCategory {p.get('errorCategory')!r} is not in the error taxonomy")
    for cat in p.get("errorCategoriesWatched", []):
        if cat not in taxonomy_ids:
            fail(f"{pid}: watched category {cat!r} is not in the error taxonomy")
    if p.get("visualId") not in visual_by_id:
        fail(f"{pid}: visualId {p.get('visualId')!r} does not exist")
        continue
    v = visual_by_id[p["visualId"]]
    if v["family"] != p["questionFamily"]:
        fail(f"{pid}: visual {v['id']} belongs to {v['family']}, not {p['questionFamily']}")

    plan = p.get("planning") or {}
    if len(plan.get("steps", [])) < 4:
        fail(f"{pid}: planning stage has fewer than four steps")
    if len(p.get("checklist", [])) < 8:
        fail(f"{pid}: self-review checklist has fewer than eight items")
    for item in p.get("checklist", []):
        if not str(item.get("text", "")).strip() or not str(item.get("criterion", "")).strip():
            fail(f"{pid}: checklist item missing text or criterion")

    body = p.get("modelResponse") or []
    if len(body) < 4:
        fail(f"{pid}: model response has fewer than four paragraphs")
    joined = " ".join(body)
    words = len(joined.split())
    if words < WORD_MINIMUM:
        fail(f"{pid}: model response is {words} words, below the {WORD_MINIMUM}-word minimum it teaches")
    if not any(par.strip().startswith("Overall,") for par in body):
        fail(f"{pid}: model response has no paragraph beginning 'Overall,' so it models no overview")
    if len(p.get("targetFeatures", [])) < 3:
        fail(f"{pid}: fewer than three target features declared")

    support = derive_support(v)
    for text_block in body + list(p.get("modelNotes", [])) + list(p.get("targetFeatures", [])):
        for n in digits(text_block):
            if float(n) not in support:
                fail(f"{pid}: model text cites {n}, which is not derivable from {v['id']}")

    if not str(p.get("scoringNote", "")).strip():
        fail(f"{pid}: no scoring note, so feedback could be mistaken for an official band")
    if "not an official" not in p["scoringNote"].lower():
        fail(f"{pid}: scoring note does not disclaim official IELTS scoring")

# --- 6b. Band comparison lab (REQ-019) --------------------------------------
bands = data.get("bandComparisons", [])
if len(bands) < MIN_FAMILIES:
    fail(f"band comparison sets {len(bands)} < one per visual family ({MIN_FAMILIES})")
if {b["questionFamily"] for b in bands} != REQUIRED_FAMILIES:
    fail("band comparison lab does not cover the seven families exactly")
band_levels = [lv["level"] for lv in data.get("bandLevels", [])]
if len(band_levels) < 3:
    fail("fewer than three band levels defined")
for b in bands:
    bid = b["id"]
    for field in ("id", "type", "skill", "questionFamily", "visualId", "focus", "aspects",
                  "comparison", "responses", "takeaway", "uaSupport", "scoringNote", "prompt"):
        if not b.get(field):
            fail(f"{bid}: missing {field}")
    if b.get("visualId") not in visual_by_id:
        fail(f"{bid}: visualId does not exist")
        continue
    bv = visual_by_id[b["visualId"]]
    if bv["family"] != b["questionFamily"]:
        fail(f"{bid}: visual belongs to {bv['family']}, not {b['questionFamily']}")
    if [r["level"] for r in b["responses"]] != band_levels:
        fail(f"{bid}: responses do not cover every declared band level in order")
    band_minimum = b.get("wordMinimum")
    if band_minimum != 150:
        fail(f"{bid}: band set does not record the 150-word Academic Task 1 minimum")
    for r in b["responses"]:
        words = sum(len(p.split()) for p in r["text"])
        # IELTS Academic Task 1 asks for at least 150 words. A sample under that
        # is underlength writing presented as a model, and it also makes length
        # an uncontrolled variable between the three levels.
        if words < 150:
            fail(f"{bid}/{r['level']}: sample response is {words} words, under the 150-word "
                 f"Academic Task 1 minimum")
        if r.get("wordMinimum") != 150 or not r.get("meetsMinimum"):
            fail(f"{bid}/{r['level']}: sample does not record meeting the Task 1 minimum")
        if not re.match(r"illustrative band \d-style sample$", str(r.get("styleLabel", "")).strip(), re.I):
            fail(f"{bid}/{r['level']}: sample is not labelled as an illustrative Band-style sample")
        if r["wordCount"] != words:
            fail(f"{bid}/{r['level']}: stated word count does not match the text")
        if not r["does"]:
            fail(f"{bid}/{r['level']}: no annotation of what the response does")
        if r["level"] != band_levels[-1] and not r["missing"]:
            fail(f"{bid}/{r['level']}: a non-target sample must say what holds it back")
        if r["level"] == band_levels[-1] and r["missing"]:
            fail(f"{bid}/{r['level']}: the target sample should have nothing holding it back")
        if not any(par.strip().startswith("Overall,") for par in r["text"]) and r["level"] == band_levels[-1]:
            fail(f"{bid}/{r['level']}: the target sample models no overview")
    if len(b["comparison"]) < 4:
        fail(f"{bid}: fewer than four compared aspects")
    criteria = b.get("aspectCriteria") or {}
    official = {"Task Achievement", "Coherence and Cohesion", "Lexical Resource",
                "Grammatical Range and Accuracy"}
    for aspect in b.get("aspects", []):
        if criteria.get(aspect) not in official:
            fail(f"{bid}: aspect {aspect!r} is not mapped to a published IELTS Writing criterion")
    if "ielts.org" not in str(b.get("descriptorReference", "")):
        fail(f"{bid}: no pointer to the published IELTS Writing band descriptors")
    for rowc in b["comparison"]:
        for k in ("aspect", "b6", "b7", "b8"):
            if not str(rowc.get(k, "")).strip():
                fail(f"{bid}: comparison row missing {k}")
    if "not an official" not in b["scoringNote"].lower():
        fail(f"{bid}: band labels are not disclaimed as non-official")
    if not cyrillic.search(b.get("uaSupport", "")):
        fail(f"{bid}: no Ukrainian support")

# --- 7. Honest scoring language across all learner-facing text --------------
band_claim = re.compile(r"\b(you|your)\b[^.]{0,60}\bband\s*\d", re.I)
for rec in exercises + prompts + bands:
    blob = json.dumps(rec, ensure_ascii=False)
    if band_claim.search(blob):
        fail(f"{rec['id']}: text appears to award the learner an IELTS band")

# --- 8. Module integrity -----------------------------------------------------
module_ids = {m["id"] for m in modules}
exercise_ids = {e["id"] for e in exercises}
prompt_ids = {p["id"] for p in prompts}
visual_ids = set(visual_by_id)
family_modules = [m for m in modules if m.get("kind") == "visual_family"]
foundation_modules = [m for m in modules if m.get("kind") == "foundation"]

if len(family_modules) != MIN_FAMILIES:
    fail(f"expected {MIN_FAMILIES} visual-family modules, found {len(family_modules)}")
if len(foundation_modules) < 4:
    fail(f"fewer than four foundation modules ({len(foundation_modules)})")
if {m["subskill"] for m in family_modules} != REQUIRED_FAMILIES:
    fail("visual-family modules do not cover the seven families exactly")

for mod in modules:
    for field in MODULE_REQUIRED_FIELDS:
        if field not in mod:
            fail(f"module {mod['id']}: missing field {field}")
    if mod.get("difficulty") not in DIFFICULTY_ENUM:
        fail(f"module {mod['id']}: difficulty {mod.get('difficulty')!r} outside the approved enum")
    if not mod.get("objectives"):
        fail(f"module {mod['id']}: no objectives")
    if len(mod.get("lesson", [])) < 5:
        fail(f"module {mod['id']}: lesson has fewer than five steps")
    for pre in mod.get("prerequisites", []):
        if pre not in module_ids:
            fail(f"module {mod['id']}: prerequisite {pre} does not exist")
    for rel in mod.get("relatedModules", []):
        if rel not in module_ids:
            fail(f"module {mod['id']}: relatedModule {rel} does not exist")
    for cat in mod.get("errorCategories", []):
        if cat not in taxonomy_ids:
            fail(f"module {mod['id']}: error category {cat!r} is not in the taxonomy")
    for ex in mod.get("exercises", []):
        if ex not in exercise_ids:
            fail(f"module {mod['id']}: exercise {ex} does not exist")
    for pr in mod.get("prompts", []):
        if pr not in prompt_ids:
            fail(f"module {mod['id']}: prompt {pr} does not exist")
    for vi in mod.get("visuals", []):
        if vi not in visual_ids:
            fail(f"module {mod['id']}: visual {vi} does not exist")
    for mc in mod.get("masteryCheck", []):
        if mc not in exercise_ids | prompt_ids:
            fail(f"module {mod['id']}: masteryCheck {mc} references nothing that exists")

for mod in family_modules:
    if not mod.get("masteryCheck"):
        fail(f"module {mod['id']}: no mastery check")
    if len(mod.get("exercises", [])) != len(REQUIRED_MICRO_TYPES):
        fail(f"module {mod['id']}: does not list all {len(REQUIRED_MICRO_TYPES)} micro-exercises")
    if len(mod.get("commonErrors", [])) < 3:
        fail(f"module {mod['id']}: fewer than three documented common errors")
    for ce in mod.get("commonErrors", []):
        if ce.get("errorId") not in taxonomy_ids:
            fail(f"module {mod['id']}: common error {ce.get('errorId')!r} is not in the taxonomy")
        if not str(ce.get("symptom", "")).strip() or not str(ce.get("repair", "")).strip():
            fail(f"module {mod['id']}: common error missing symptom or repair")
    if not mod.get("workedExamples"):
        fail(f"module {mod['id']}: no worked example")
    for key in ("whatItTests", "howIeltsConstructs", "trap", "tenseRule", "uaTransferNote", "uaSupport"):
        if not str(mod.get(key, "")).strip():
            fail(f"module {mod['id']}: missing instructional field {key}")
    if not mod.get("languageBank"):
        fail(f"module {mod['id']}: no language bank")
    if len(mod.get("prompts", [])) < 3:
        fail(f"module {mod['id']}: fewer than three full prompts attached")
    if not mod.get("bandComparisons"):
        fail(f"module {mod['id']}: no band comparison set attached")

# Every exercise and prompt must be reachable from exactly one family module.
listed_ex = [x for mod in family_modules for x in mod.get("exercises", [])]
if sorted(listed_ex) != sorted(exercise_ids):
    fail("exercises listed by modules do not match the exercise bank exactly")
listed_pr = [x for mod in family_modules for x in mod.get("prompts", [])]
if sorted(listed_pr) != sorted(prompt_ids):
    fail("prompts listed by modules do not match the prompt bank exactly")

# --- 8b. The shared JSON schemas, reused rather than redefined --------------
# docs/development_design_plan.md section 4: every generated exercise and
# module must still validate against schemas/ that G1 established.
try:
    from jsonschema import Draft202012Validator
except ImportError:  # pragma: no cover - dependency is declared in the gate report
    fail("jsonschema is not installed, so schemas/ could not be enforced")
else:
    ex_schema = json.loads((ROOT / "schemas" / "exercise.schema.json").read_text(encoding="utf-8"))
    mod_schema = json.loads((ROOT / "schemas" / "module.schema.json").read_text(encoding="utf-8"))
    ex_validator = Draft202012Validator(ex_schema)
    mod_validator = Draft202012Validator(mod_schema)
    for rec in exercises + prompts:
        for err in ex_validator.iter_errors(rec):
            fail(f"{rec['id']}: exercise.schema.json - {err.message}")
    for mod in modules:
        for err in mod_validator.iter_errors(mod):
            fail(f"module {mod['id']}: module.schema.json - {err.message}")

# --- 9. Error taxonomy and mastery rules ------------------------------------
if len(taxonomy) < 10:
    fail(f"error taxonomy has only {len(taxonomy)} categories")
for cat in taxonomy:
    for field in ("id", "en", "ua", "description", "correction", "uaCorrection"):
        if not str(cat.get(field, "")).strip():
            fail(f"error category {cat.get('id')}: missing {field}")
used_categories = {e["errorCategory"] for e in exercises} | {p["errorCategory"] for p in prompts}
unused = taxonomy_ids - used_categories
if len(unused) > 3:
    fail(f"error taxonomy has {len(unused)} categories no item ever uses: {sorted(unused)}")

mastery = data.get("masteryRules", {})
levels = {lv["level"] for lv in mastery.get("levels", [])}
if levels != {1, 2, 3, 4, 5}:
    fail(f"mastery rules do not define levels 1-5 ({sorted(levels)})")
for lv in mastery.get("levels", []):
    if not str(lv.get("rule", "")).strip() or not str(lv.get("ua", "")).strip():
        fail(f"mastery level {lv.get('level')}: missing rule or Ukrainian gloss")
# L4 and L5 are performance levels, so the response that earns them has to be a
# real Task 1 answer and not twenty words submitted inside the time limit.
if mastery.get("wordMinimum") != 150:
    fail("mastery rules do not record the 150-word minimum for a full response")
if "150" not in str(mastery.get("lengthRule", "")):
    fail("mastery rules do not state that an underlength response cannot advance mastery")
for lv in mastery.get("levels", []):
    if lv.get("level") in (4, 5) and "150 words" not in str(lv.get("rule", "")):
        fail(f"mastery level {lv.get('level')} does not require a 150-word response")

# --- 10. Meta counts must match the artifact --------------------------------
meta = data["meta"]
checks = [
    ("familyCount", len(families_present)),
    ("visualCount", len(visuals)),
    ("microExerciseCount", len(exercises)),
    ("promptCount", len(prompts)),
    ("moduleCount", len(modules)),
    ("errorCategoryCount", len(taxonomy)),
    ("bandComparisonCount", len(bands)),
    ("bandResponseCount", sum(len(b["responses"]) for b in bands)),
]
for key, actual in checks:
    if meta.get(key) != actual:
        fail(f"meta.{key} says {meta.get(key)} but the artifact contains {actual}")
if "not an official" not in str(meta.get("scoringNote", "")).lower():
    fail("meta.scoringNote does not disclaim official IELTS scoring")

# --- 11. Bilingual coverage --------------------------------------------------
missing_ua = [e["id"] for e in exercises if not str(e.get("uaSupport", "")).strip()]
if missing_ua:
    fail(f"{len(missing_ua)} exercises have no Ukrainian support note")
for e in exercises:
    if not cyrillic.search(e.get("uaSupport", "")):
        fail(f"{e['id']}: uaSupport contains no Cyrillic text")
for mod in family_modules:
    if not cyrillic.search(mod.get("uaTransferNote", "")):
        fail(f"module {mod['id']}: uaTransferNote contains no Cyrillic text")

# --- Report ------------------------------------------------------------------
mode_counts = {}
for e in exercises:
    mode_counts[e["mode"]] = mode_counts.get(e["mode"], 0) + 1
print("G4 WRITING TASK 1 CONTENT VALIDATION")
print("====================================")
print("Visual families :", len(families_present))
print("Visuals         :", len(visuals))
print("Micro-exercises :", len(exercises), f"(benchmark {MIN_MICRO_EXERCISES})")
print("  by mode       :", ", ".join(f"{k} {v}" for k, v in sorted(mode_counts.items())))
print("Micro-types     :", len(REQUIRED_MICRO_TYPES), "in every family")
print("Full prompts    :", len(prompts), f"(benchmark {MIN_PROMPTS})")
print("Modules         :", len(modules), f"({len(foundation_modules)} foundation, {len(family_modules)} family)")
print("Error categories:", len(taxonomy))
print("Band comparison :", len(bands), "sets,", sum(len(b["responses"]) for b in bands), "sample responses")
print("Model responses :", f"{len(prompts)} annotated, all >= {WORD_MINIMUM} words with an overview")
print("Band samples    :", f"{sum(len(b['responses']) for b in bands)} illustrative samples, "
      f"all >= {WORD_MINIMUM} words, aspects mapped to the public IELTS criteria")

if errors:
    for e in errors[:120]:
        print("FAIL:", e)
    print("Total failures:", len(errors))
    sys.exit(1)
print("PASS: G4 inventory, family and micro-type coverage, IDs, references, "
      "data grounding, wrong-option reasoning, bilingual support and honest scoring")
