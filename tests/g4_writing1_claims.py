#!/usr/bin/env python3
"""G4 canonical-claim validation — exhaustive, every scored item.

Closes defect D4-006. The earlier grounding rule authorised any figure that was
arithmetically derivable from a visual, which included every column total and
every pairwise sum. A figure could therefore be "supported" while not being the
figure the item intended.

This script iterates over EVERY scored exercise, EVERY full prompt and EVERY
band-comparison response and validates, against the source dataset:

  * the intended claim, expressed as the fact keys the item declares;
  * the permitted operations — `total` and `sum` are NOT permitted unless the
    item explicitly authorises them;
  * the dataset fields used;
  * units and time period;
  * the correct option or accepted response variants;
  * that every wrong option carries a reason it is wrong;
  * that the explanation is tied to the intended evidence.

It re-implements the fact engine and the authorisation rules from scratch, so a
generator that authorised itself incorrectly still fails here.
"""
from pathlib import Path
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]

ALLOWED_REPORT_OPS = {
    "value", "first", "last", "max", "min", "max_at", "min_at", "delta",
    "pct_change", "change", "gap", "share", "delta_share", "largest",
    "smallest", "rank", "top", "bottom", "stage", "stage_count",
    "first_stage", "last_stage", "input", "output", "cyclical",
    "status", "area", "count", "feature_count",
}
RESTRICTED_OPS = {"total", "sum"}
MAX_STRUCTURAL = 10
UNIT_LEXICON = [
    (r"percentage points?", "%"), (r"per cent|percent\b|%", "%"),
    (r"million", "million"), (r"thousand", "thousand"),
    (r"terawatt-hours?|TWh", "terawatt-hour"), (r"pounds?\b", "pound"),
    (r"nights?\b", "night"), (r"index", "index"), (r"tonnes?\b", "tonne"),
    (r"stages?\b", "stage"),
]
UNIT_IN_CORPUS = {"%": r"%|per cent|percent", "million": "million", "thousand": "thousand",
                  "terawatt-hour": r"terawatt|twh", "pound": "pound", "night": "night",
                  "index": "index", "tonne": "tonne", "stage": "stage"}
LABEL_RE = re.compile(r"\bTask\s*[12]\b|\bBand\s*[0-9]\b", re.I)
YEAR_RE = re.compile(r"\b(19|20)\d{2}\b")
NUM_RE = re.compile(r"\d+(?:\.\d+)?")

errors = []


def fail(m):
    errors.append(m)


def rnd(x, places=2):
    r = round(float(x), places)
    return int(r) if abs(r - int(r)) < 1e-9 else r


# ---------------- independent fact engine (re-derived, not imported) --------
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


def pie_facts(snaps, prefix=""):
    f = {}
    for snap in snaps:
        lab, sl = snap["label"], snap["slices"]
        for x in sl:
            f[f"{prefix}share.{x['label']}.{lab}"] = rnd(x["value"])
        o = sorted(sl, key=lambda z: -z["value"])
        f[f"{prefix}largest.{lab}"] = o[0]["label"]
        f[f"{prefix}smallest.{lab}"] = o[-1]["label"]
        f[f"{prefix}total.{lab}"] = rnd(sum(z["value"] for z in sl))
        f[f"{prefix}rank.{lab}"] = " > ".join(z["label"] for z in o)
        for a in range(len(sl)):
            for b in range(a + 1, len(sl)):
                la, lb = sl[a]["label"], sl[b]["label"]
                f[f"{prefix}gap.{la}.{lb}.{lab}"] = rnd(sl[a]["value"] - sl[b]["value"])
                f[f"{prefix}sum.{la}.{lb}.{lab}"] = rnd(sl[a]["value"] + sl[b]["value"])
    if len(snaps) == 2:
        a = {z["label"]: z["value"] for z in snaps[0]["slices"]}
        for z in snaps[1]["slices"]:
            if z["label"] in a:
                f[f"{prefix}delta_share.{z['label']}"] = rnd(z["value"] - a[z["label"]])
    return f


def table_facts(cols, rows, prefix=""):
    f = {}
    for r in rows:
        for c, v in zip(cols, r["cells"]):
            f[f"{prefix}value.{r['label']}.{c}"] = rnd(v)
    for i, c in enumerate(cols):
        col = sorted(((r["label"], r["cells"][i]) for r in rows), key=lambda t: -t[1])
        f[f"{prefix}max.{c}"] = col[0][0]
        f[f"{prefix}min.{c}"] = col[-1][0]
        f[f"{prefix}total.{c}"] = rnd(sum(v for _, v in col))
    for r in rows:
        for i in range(len(cols)):
            for j in range(i + 1, len(cols)):
                f[f"{prefix}delta.{r['label']}.{cols[i]}.{cols[j]}"] = rnd(r["cells"][j] - r["cells"][i])
    return f


def facts_of(v):
    k = v["kind"]
    if k in ("line", "bar"):
        return series_facts(v["categories"], v["series"])
    if k == "pie":
        return pie_facts(v["snapshots"])
    if k == "table":
        return table_facts(v["columns"], v["rows"])
    if k == "process":
        f = {"stage_count": len(v["stages"]), "input": v["input"], "output": v["output"],
             "cyclical": "yes" if v["cyclical"] else "no",
             "first_stage": v["stages"][0]["label"], "last_stage": v["stages"][-1]["label"]}
        for st in v["stages"]:
            f[f"stage.{st['n']}"] = st["label"]
        return f
    if k == "map":
        f, counts = {}, {"added": 0, "removed": 0, "replaced": 0, "unchanged": 0}
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
            pre = f"c{i}."
            if c["kind"] in ("line", "bar"):
                f.update(series_facts(c["categories"], c["series"], pre))
            elif c["kind"] == "pie":
                f.update(pie_facts(c["snapshots"], pre))
            elif c["kind"] == "table":
                f.update(table_facts(c["columns"], c["rows"], pre))
        return f
    raise ValueError(v["kind"])


# ---------------- text helpers ---------------------------------------------
def strip_labels(t):
    return LABEL_RE.sub("Task", str(t))


def figures_in(t):
    return {rnd(float(x)) for x in NUM_RE.findall(strip_labels(t))}


def years_in(t):
    return {int(m.group(0)) for m in YEAR_RE.finditer(strip_labels(t))}


def op_of(key):
    k = key.split(".", 1)[1] if re.match(r"^c\d+\.", key) else key
    return k.split(".", 1)[0]


def time_labels(v):
    out = set()

    def scan(x):
        for m in YEAR_RE.finditer(str(x)):
            out.add(int(m.group(0)))
    scan(v.get("timeframe", ""))
    for c in [v] + list(v.get("components", []) or []):
        for a in (c.get("categories") or []):
            scan(a)
        for a in (c.get("columns") or []):
            scan(a)
        for a in (c.get("snapshots") or []):
            scan(a.get("label", ""))
    for a in (v.get("periods") or []):
        scan(a)
    return out


def label_figures(v):
    out = set()

    def scan(x):
        for t in NUM_RE.findall(str(x)):
            out.add(rnd(float(t)))
    for c in [v] + list(v.get("components", []) or []):
        for a in (c.get("categories") or []):
            scan(a)
        for a in (c.get("columns") or []):
            scan(a)
        for r in (c.get("rows") or []):
            scan(r.get("label", ""))
        for sn in (c.get("snapshots") or []):
            scan(sn.get("label", ""))
        scan(c.get("unit", ""))
        scan(c.get("axisLabel", ""))
    for a in (v.get("periods") or []):
        scan(a)
    scan(v.get("timeframe", ""))
    if v["kind"] == "process":
        out.update(range(1, len(v["stages"]) + 1))
    return out


def unit_corpus(v):
    parts = [v.get("unit", ""), v.get("axisLabel", "")] + list(v.get("columns") or [])
    for c in (v.get("components") or []):
        parts += [c.get("unit", ""), c.get("axisLabel", "")] + list(c.get("columns") or [])
    if v["kind"] == "process":
        parts.append("stages")
    return " ".join(str(x) for x in parts).lower()


def unit_tokens(v):
    corpus = unit_corpus(v)
    return {tok for tok, pat in UNIT_IN_CORPUS.items() if re.search(pat, corpus)}


def units_in(t):
    low = str(t).lower()
    return {tok for pat, tok in UNIT_LEXICON if re.search(pat, low)}


def check(where, v, text, authorised, structural, deliberate, units, times):
    for n in figures_in(text):
        if n not in authorised and n not in structural and n not in deliberate:
            fail(f"{where}: cites {n}, not authorised for {v['id']}")
    for y in years_in(text):
        if y not in times and y not in deliberate:
            fail(f"{where}: refers to {y}, not a time label of {v['id']}")
    for u in units_in(text):
        if u not in units:
            fail(f"{where}: uses unit {u!r}, which {v['id']} does not measure in")


# ---------------- load -------------------------------------------------------
raw = (ROOT / "web" / "writing1_data.js").read_text(encoding="utf-8")
data = json.loads(re.search(r"window\.WRITING1_DATA=(\{.*\});\s*$", raw, re.S).group(1))
V = {v["id"]: v for v in data["visuals"]}
exercises, prompts = data["exercises"], data["prompts"]
bands = data.get("bandComparisons", [])

checked = {"exercise": 0, "prompt": 0, "band": 0, "texts": 0}

# ---------------- exercises: strict, declared derivations only ---------------
for e in exercises:
    v = V[e["visualId"]]
    f = facts_of(v)
    claim = e.get("claim")
    if not claim:
        fail(f"{e['id']}: no canonical claim manifest")
        continue
    # Some fields are legitimately empty: an undated process has no time
    # references, and an item grounded on string-valued facts (a rank, a row
    # label) authorises no figures. The KEY must always be present.
    for field in ("intent", "groundingKeys", "permittedOperations", "authorisedFigures",
                  "unit", "period", "timeReferences", "acceptedResponses",
                  "datasetFields", "structuralNumbers"):
        if field not in claim:
            fail(f"{e['id']}: claim has no {field} key")
    for field in ("intent", "groundingKeys", "permittedOperations", "unit", "period",
                  "acceptedResponses"):
        if not claim.get(field):
            fail(f"{e['id']}: claim {field} is empty")

    keys = claim["groundingKeys"]
    if keys != e["grounding"]:
        fail(f"{e['id']}: claim grounding keys disagree with the item")
    auth = set()
    for k in keys:
        if k not in f:
            fail(f"{e['id']}: declared key {k!r} is not derivable from {v['id']}")
            continue
        val = f[k]
        if isinstance(val, (int, float)) and not isinstance(val, bool):
            auth.add(rnd(val))
            auth.add(rnd(abs(val)))
    extra = set(claim["permittedOperations"]) - {op_of(k) for k in keys}
    for op in extra:
        for k, val in f.items():
            if op_of(k) == op and isinstance(val, (int, float)) and not isinstance(val, bool):
                auth.add(rnd(val))
                auth.add(rnd(abs(val)))
    # Restricted operations must be declared explicitly on the item.
    for op in RESTRICTED_OPS:
        if op in claim["permittedOperations"] and op not in {op_of(k) for k in keys} and op not in (e.get("extraOps") or []):
            fail(f"{e['id']}: restricted operation {op!r} appears without explicit authorisation")

    # The manifest's own figure list must match what the declared keys produce.
    derived = sorted(auth - time_labels(v) - label_figures(v))
    stated = sorted(set(claim["authorisedFigures"]) - time_labels(v) - label_figures(v))
    if derived != stated:
        fail(f"{e['id']}: manifest authorisedFigures do not match the declared derivation")

    auth |= time_labels(v) | label_figures(v)
    structural = {rnd(n) for n in (e.get("allowedNumbers") or [])}
    for n in structural:
        if n > MAX_STRUCTURAL:
            fail(f"{e['id']}: structural number {n} exceeds {MAX_STRUCTURAL}")
    deliberate = {rnd(n) for n in (e.get("deliberateErrorFigures") or [])}
    if deliberate and not str(e.get("deliberateErrorReason", "")).strip():
        fail(f"{e['id']}: deliberate error figures declared without a reason")
    units, times = unit_tokens(v), time_labels(v)

    opt_figs = set()
    for o in (e.get("options") or []):
        opt_figs |= figures_in(o)

    texts = [("prompt", e["prompt"]), ("explanation", e["explanation"])]
    if e["type"] == "select":
        texts.append(("correctAnswer", e["correctAnswer"]))
    if e["type"] == "cloze":
        texts.append(("sentence", e["sentence"]))
    if e["type"] == "order":
        texts += [(f"item[{i}]", it["text"]) for i, it in enumerate(e["items"])]
    for label, t in texts:
        allowed = auth | (opt_figs if label == "explanation" else set())
        check(f"{e['id']}.{label}", v, t, allowed, structural, deliberate, units, times)
        checked["texts"] += 1

    # Units and period must be the visual's own.
    if claim["unit"] != v["unit"]:
        fail(f"{e['id']}: claim unit does not match {v['id']}")
    if claim["period"] != v["timeframe"]:
        fail(f"{e['id']}: claim period does not match {v['id']}")

    # Accepted responses and distractor reasoning.
    if e["type"] == "select":
        if claim["acceptedResponses"] != [e["correctAnswer"]]:
            fail(f"{e['id']}: accepted responses do not match the correct option")
        for o in e["options"]:
            if o == e["correctAnswer"]:
                continue
            why = (claim.get("distractorFaults") or {}).get(o, "")
            if len(str(why).strip()) < 30:
                fail(f"{e['id']}: distractor has no substantive reason it is wrong")
    elif e["type"] == "cloze":
        if e["correctAnswer"] not in claim["acceptedResponses"]:
            fail(f"{e['id']}: correct answer missing from accepted response variants")
    else:
        if claim["acceptedResponses"] != e["correctAnswer"]:
            fail(f"{e['id']}: accepted response order does not match the correct order")
    checked["exercise"] += 1

# ---------------- prompts and band responses: report-level authorisation -----
def report_auth(v, extra):
    allowed = ALLOWED_REPORT_OPS | set(extra)
    nums = set()
    for k, val in facts_of(v).items():
        if op_of(k) in allowed and isinstance(val, (int, float)) and not isinstance(val, bool):
            nums.add(rnd(val))
            nums.add(rnd(abs(val)))
    return nums | time_labels(v) | label_figures(v)


for p in prompts:
    v = V[p["visualId"]]
    claim = p.get("claim")
    if not claim:
        fail(f"{p['id']}: no canonical claim manifest")
        continue
    extra = set(claim.get("restrictedOperationsAuthorised") or [])
    for op in RESTRICTED_OPS:
        if op in set(claim["permittedOperations"]) and op not in extra:
            fail(f"{p['id']}: restricted operation {op!r} permitted without authorisation")
    auth = report_auth(v, extra)
    structural = {rnd(n) for n in (p.get("allowedNumbers") or [])}
    units, times = unit_tokens(v), time_labels(v)
    for i, par in enumerate(p["modelResponse"]):
        check(f"{p['id']}.model[{i}]", v, par, auth, structural, set(), units, times)
        checked["texts"] += 1
    for i, n in enumerate(p["modelNotes"]):
        check(f"{p['id']}.note[{i}]", v, n, auth, structural, set(), units, times)
        checked["texts"] += 1
    for i, t in enumerate(p["targetFeatures"]):
        check(f"{p['id']}.target[{i}]", v, t, auth, structural, set(), units, times)
        checked["texts"] += 1
    if claim["unit"] != v["unit"] or claim["period"] != v["timeframe"]:
        fail(f"{p['id']}: claim unit or period does not match {v['id']}")
    checked["prompt"] += 1

for b in bands:
    v = V[b["visualId"]]
    claim = b.get("claim")
    if not claim:
        fail(f"{b['id']}: no canonical claim manifest")
        continue
    auth = report_auth(v, set())
    units, times = unit_tokens(v), time_labels(v)
    for r in b["responses"]:
        for i, par in enumerate(r["text"]):
            check(f"{b['id']}.{r['level']}[{i}]", v, par, auth, set(), set(), units, times)
            checked["texts"] += 1
    checked["band"] += 1

# ---------------- coverage: the manifest must be exhaustive -----------------
if checked["exercise"] != len(exercises):
    fail(f"only {checked['exercise']} of {len(exercises)} exercises carry a claim manifest")
if checked["prompt"] != len(prompts):
    fail(f"only {checked['prompt']} of {len(prompts)} prompts carry a claim manifest")
if bands and checked["band"] != len(bands):
    fail(f"only {checked['band']} of {len(bands)} band sets carry a claim manifest")

# ---------------- the rule must actually bite -------------------------------
# A column total is derivable from every series visual, but must not be
# authorised for an exercise that did not declare it.
probe = next((e for e in exercises if e["visualId"].startswith("W1V-LINE-01")), None)
if probe:
    v = V[probe["visualId"]]
    totals = {rnd(val) for k, val in facts_of(v).items()
              if op_of(k) == "total" and isinstance(val, (int, float))}
    declared = set()
    for k in probe["grounding"]:
        val = facts_of(v).get(k)
        if isinstance(val, (int, float)) and not isinstance(val, bool):
            declared |= {rnd(val), rnd(abs(val))}
    leak = totals - declared - time_labels(v) - label_figures(v)
    if not leak:
        fail("self-check: could not construct a column total outside the declared set, "
             "so the restriction is untestable here")

print("G4 CANONICAL CLAIM VALIDATION")
print("=============================")
print("Exercises with a manifest :", checked["exercise"], "/", len(exercises))
print("Prompts with a manifest   :", checked["prompt"], "/", len(prompts))
print("Band sets with a manifest :", checked["band"], "/", len(bands))
print("Text blocks checked       :", checked["texts"])
print("Restricted operations     : total, sum — never authorised implicitly")

if errors:
    for e in errors[:80]:
        print("FAIL:", e)
    print("Total failures:", len(errors))
    sys.exit(1)
print("PASS: every scored item's figures, years, units and accepted responses trace to a "
      "declared derivation from its own dataset")
