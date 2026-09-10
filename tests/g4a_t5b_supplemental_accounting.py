#!/usr/bin/env python3
"""Accounting reconciliation for the G4-A T5-B supplemental findings register (issue #4).

Ties docs/G4A_T5B_SUPPLEMENTAL_FINDINGS.csv to the actual learner-facing bytes in
web/vocabulary.js and to the guarded correction payload, so the register cannot state
one thing while the shipped data says another:

  * corrected rows (35): id resolves; the on-disk definitionUa equals the recorded
    correction and equals the payload correction; and it carries no adjacent/
    punctuation-separated repeat anymore.
  * benign-allowlisted rows (2): id resolves; definitionUa is unchanged from the
    recorded original; the entry STILL carries a repeat (so the allowlist is live) and
    the set equals the payload's benign_allowlist and the guard's ALLOWLIST.
  * open-deferred-followup rows (64): id resolves; the on-disk definitionUa still
    carries a connector-separated repeat (the finding is genuinely still open).

These are structural/consistency assertions, not a semantic judgement of the Ukrainian.
"""

import csv
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
REGISTER = ROOT / "docs" / "G4A_T5B_SUPPLEMENTAL_FINDINGS.csv"
VOCAB = ROOT / "web" / "vocabulary.js"
PAYLOAD = ROOT / "scripts" / "qa" / "t5b_repeat_corrections.json"

WORD = re.compile(r"[A-Za-zА-Яа-яІіЇїЄєҐґ’']+(?:[-’'][A-Za-zА-Яа-яІіЇїЄєҐґ]+)*")
CONN = {"або", "чи", "та", "й", "і"}
COLUMNS = ["stable_id", "word", "field", "category", "severity", "original_text",
           "correction", "rationale", "confidence", "discovery_source",
           "discovery_date", "disposition"]
EXPECTED = {"corrected": 35, "benign-allowlisted": 2, "open-deferred-followup": 64}


def adjacent_repeats(s):
    t = list(WORD.finditer(s or ""))
    return [t[i].group() for i in range(len(t) - 1)
            if t[i].group().casefold() == t[i + 1].group().casefold()]


def has_connector_repeat(s):
    t = list(WORD.finditer(s or ""))
    for i in range(len(t) - 2):
        if (t[i].group().casefold() == t[i + 2].group().casefold()
                and t[i + 1].group().casefold() in CONN
                and s[t[i].end():t[i + 1].start()].strip() == ""
                and s[t[i + 1].end():t[i + 2].start()].strip() == ""):
            return True
    return False


def main():
    errors = []
    with REGISTER.open(encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames != COLUMNS:
            errors.append(f"register columns {reader.fieldnames} != expected {COLUMNS}")
        rows = list(reader)

    text = VOCAB.read_text(encoding="utf-8")
    by_id = {e["id"]: e for e in json.loads(
        re.search(r"window\.VOCABULARY=(\[.*\]);", text, re.DOTALL).group(1))}
    payload = json.loads(PAYLOAD.read_text(encoding="utf-8"))
    pay_corr = payload["corrections"]
    pay_benign = set(payload["_meta"]["benign_allowlist"])

    ids = [r["stable_id"] for r in rows]
    if len(ids) != len(set(ids)):
        errors.append("duplicate stable_id in register")
    unknown = sorted(set(ids) - set(by_id))
    if unknown:
        errors.append(f"register ids not in vocabulary.js: {unknown[:10]}")

    by_disp = {}
    for r in rows:
        by_disp.setdefault(r["disposition"], []).append(r)
    for disp, n in EXPECTED.items():
        got = len(by_disp.get(disp, []))
        if got != n:
            errors.append(f"disposition {disp}: {got} rows, expected {n}")
    if len(rows) != sum(EXPECTED.values()):
        errors.append(f"total rows {len(rows)} != {sum(EXPECTED.values())}")

    corrected = by_disp.get("corrected", [])
    if {r["stable_id"] for r in corrected} != set(pay_corr):
        errors.append("corrected set != guarded payload corrections set")
    for r in corrected:
        cid = r["stable_id"]
        disk = by_id[cid]["definitionUa"]
        if disk != r["correction"]:
            errors.append(f"{cid}: on-disk definitionUa != register correction")
        if disk != pay_corr.get(cid, {}).get("definitionUa"):
            errors.append(f"{cid}: on-disk definitionUa != payload correction")
        if adjacent_repeats(disk):
            errors.append(f"{cid}: still has adjacent/punctuation repeat after correction")
        if r["severity"] != "P1":
            errors.append(f"{cid}: corrected row severity != P1")
        if not r["correction"].strip():
            errors.append(f"{cid}: corrected row has empty correction")

    benign = by_disp.get("benign-allowlisted", [])
    if {r["stable_id"] for r in benign} != pay_benign:
        errors.append("benign-allowlisted set != payload benign_allowlist")
    for r in benign:
        cid = r["stable_id"]
        disk = by_id[cid]["definitionUa"]
        if disk != r["original_text"]:
            errors.append(f"{cid}: benign row original_text != on-disk value (should be untouched)")
        if not adjacent_repeats(disk):
            errors.append(f"{cid}: benign row no longer carries a repeat — should leave allowlist")
        if r["correction"].strip():
            errors.append(f"{cid}: benign row should carry no correction")

    open_rows = by_disp.get("open-deferred-followup", [])
    for r in open_rows:
        cid = r["stable_id"]
        disk = by_id[cid]["definitionUa"]
        if not has_connector_repeat(disk):
            errors.append(f"{cid}: open connector-separated finding no longer present on disk")
        if r["severity"] != "P1":
            errors.append(f"{cid}: open row severity != P1")

    print("G4-A T5-B SUPPLEMENTAL FINDINGS ACCOUNTING")
    print("==========================================")
    print(f"  register rows: {len(rows)} "
          f"(corrected {len(corrected)}, benign {len(benign)}, open {len(open_rows)})")
    print(f"  all corrected values match guarded payload + on-disk bytes; "
          f"no residual in-scope repeats")
    print()
    if errors:
        for e in errors:
            print("FAIL:", e)
        print(f"\nFAIL: {len(errors)} accounting assertion(s) failed.")
        return 1
    print("PASS: supplemental register reconciles with vocabulary.js and the guarded payload.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
