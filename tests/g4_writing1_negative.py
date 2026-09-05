#!/usr/bin/env python3
"""Seeded-defect proof that the G4 guards are not vacuous.

A passing suite only means something if it can fail. This script introduces one
real defect at a time -- the exact defects the external review found -- and
requires the guard that is supposed to catch it to fail. Every file it touches
is restored, including on error.

Cases
  1  a band sample cut below the 150-word Academic Task 1 minimum
  2  a band sample stripped of its illustrative-sample label
  3  a model response given another series' real value (the swap the set-based
     model could not see)
  4  a model response citing a column total it never declared
  5  the mastery word floor removed from web/app.js
  6  the review packet pointed at a tag that does not exist
"""
from pathlib import Path
import json
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
PY = sys.executable
GEN = ROOT / "scripts" / "build_writing1_curriculum.py"
DATA = ROOT / "web" / "writing1_data.js"
APP = ROOT / "web" / "app.js"
PACKET = ROOT / "docs" / "G4_EXTERNAL_REVIEW_PACKET.md"

results = []


def run(script):
    r = subprocess.run([PY, str(ROOT / script)], capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    return r.returncode, (r.stdout or "") + (r.stderr or "")


def load_data():
    text = DATA.read_text(encoding="utf-8")
    return json.loads(re.search(r"window\.WRITING1_DATA=(\{.*\});\s*$", text, re.S).group(1))


def write_data(obj):
    DATA.write_text("window.WRITING1_DATA=" + json.dumps(obj, ensure_ascii=False,
                                                         separators=(",", ":")) + ";\n",
                    encoding="utf-8")


def case(label, guard, mutate, source=DATA):
    """Apply `mutate`, require `guard` to fail, then restore `source`."""
    backup = Path(tempfile.gettempdir()) / (source.name + ".negbak")
    shutil.copy(source, backup)
    try:
        mutate()
        code, out = run(guard)
        caught = code != 0
        line = next((l for l in out.splitlines()
                     if l.startswith("FAIL") or "BUILD FAIL" in l or l.strip().startswith("-")), "")
        results.append((label, guard, caught, line.strip()[:110]))
    finally:
        shutil.copy(backup, source)
        backup.unlink(missing_ok=True)


# 1 -- underlength band sample -----------------------------------------------
def cut_sample():
    d = load_data()
    r = d["bandComparisons"][0]["responses"][-1]
    while sum(len(p.split()) for p in r["text"]) >= 150:
        r["text"] = r["text"][:-1]
    r["wordCount"] = sum(len(p.split()) for p in r["text"])
    write_data(d)


case("band sample cut under 150 words", "tests/g4_writing1_validation.py", cut_sample)


# 2 -- band sample presented as an awarded band ------------------------------
def strip_label():
    d = load_data()
    d["bandComparisons"][0]["responses"][0].pop("styleLabel", None)
    write_data(d)


case("sample labelled as a band, not a sample", "tests/g4_writing1_validation.py", strip_label)


# 3 -- a real value attributed to the wrong series ---------------------------
def swap_values():
    d = load_data()
    p = next(x for x in d["prompts"] if x["visualId"] == "W1V-LINE-01")
    v = next(x for x in d["visuals"] if x["id"] == "W1V-LINE-01")
    a, b = v["series"][0], v["series"][1]
    for i, par in enumerate(p["modelResponse"]):
        if f"{a['values'][0]} per cent" in par:
            p["modelResponse"][i] = par.replace(f"{a['values'][0]} per cent",
                                                f"{b['values'][0]} per cent")
            break
    else:                                    # nothing to swap: say so loudly
        p["modelResponse"].append(
            f"{a['name']} began the period at {b['values'][0]} per cent.")
    write_data(d)


case("one series given another's real value", "tests/g4_writing1_claims.py", swap_values)


# 4 -- an undeclared column total --------------------------------------------
def smuggle_total():
    d = load_data()
    v = next(x for x in d["visuals"] if x["id"] == "W1V-LINE-01")
    total = sum(s["values"][0] for s in v["series"])
    p = next(x for x in d["prompts"] if x["visualId"] == "W1V-LINE-01")
    p["modelResponse"].append(f"The three cities together recycled {total} per cent in 2005.")
    write_data(d)


case("undeclared column total in a model response", "tests/g4_writing1_claims.py", smuggle_total)


# 5 -- the mastery word floor removed ----------------------------------------
def drop_word_floor():
    s = APP.read_text(encoding="utf-8")
    s = s.replace("&&fullLength(s)", "")
    APP.write_text(s, encoding="utf-8", newline="\n")


case("mastery word floor removed", "tests/g4_writing1_functional.py", drop_word_floor, source=APP)


# 6 -- the packet pointing at a release that does not exist ------------------
def break_tag():
    s = PACKET.read_text(encoding="utf-8")
    head, rest = s.split("## 2.", 1)
    head = re.sub(r"`(g\d+-candidate[-\w.]*)`", "`g4-candidate-does-not-exist`", head)
    PACKET.write_text(head + "## 2." + rest, encoding="utf-8", newline="\n")


case("packet naming a release that does not exist", "tests/release_integrity.py",
     break_tag, source=PACKET)


print("G4 SEEDED-DEFECT PROOF")
print("======================")
width = max(len(c[0]) for c in results)
for label, guard, caught, line in results:
    print(f"  {'caught' if caught else 'MISSED':>7}  {label:<{width}}  {Path(guard).name}")
    if line:
        print(f"           {line}")
missed = [c for c in results if not c[2]]
print()
print(f"{len(results) - len(missed)} of {len(results)} seeded defects caught")
if missed:
    print("FAIL: a guard did not fail on a defect it is supposed to catch")
    sys.exit(1)

# and the clean tree must still pass
code, _ = run("tests/g4_writing1_validation.py")
code2, _ = run("tests/g4_writing1_claims.py")
if code or code2:
    print("FAIL: the restored tree does not pass, so a mutation leaked")
    sys.exit(1)
print("PASS: every guard fails on its defect, and the restored artifact still passes")
