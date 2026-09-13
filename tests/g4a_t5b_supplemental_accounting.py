#!/usr/bin/env python3
"""Accounting reconciliation for the G4-A T5-B supplemental findings register (issue #4).

Ties docs/G4A_T5B_SUPPLEMENTAL_FINDINGS.csv to the actual learner-facing bytes in
web/vocabulary.js and to the THREE guarded correction payloads, so the register cannot state
one thing while the shipped data says another. The three guarded stages layer in order:

  1. adjacent/punctuation-separated repeats     (scripts/qa/t5b_repeat_corrections.json,   35)
  2. connector-separated repeats                (scripts/qa/t5b_connector_corrections.json, 64)
  3. PR #7 follow-up full-rubric re-adjudication (scripts/qa/t5b_followup_corrections.json,  23)

The follow-up stage RE-corrects 8 of the 64 connector entries (a further semantic/grammar P1
beyond the repeat) and adds 15 new findings, so the *effective* shipped value for an entry is the
last stage that touched it (followup > connector > adjacent). The register's `correction` column is
required to equal both that effective value and the on-disk bytes.

Categories the register must distinguish (item 7 of the PR #7 review):
  * supplemental-P1-confirmed/corrected and supplemental-P0-confirmed/corrected — id resolves;
    on-disk definitionUa == register correction == effective payload value; no adjacent/connector
    repeat remains.
  * supplemental-benign — id resolves; definitionUa unchanged from the recorded original; the entry
    STILL carries an adjacent repeat (allowlist live); equals the adjacent payload benign_allowlist.
  * supplemental-open (open-deferred-followup / needs-human-adjudication) — MUST be zero. Any open
    supplemental P0/P1 fails closed and the gate stays CHANGES REQUESTED.

It also surfaces the frozen historical P1 backlog (314, in G4A_UKRAINIAN_QA_FINDINGS.csv) so
historical-P1-resolved and supplemental-P1 accounting can never be conflated. These are
structural/consistency assertions, not a semantic judgement of the Ukrainian.
"""

import csv
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
REGISTER = ROOT / "docs" / "G4A_T5B_SUPPLEMENTAL_FINDINGS.csv"
VOCAB = ROOT / "web" / "vocabulary.js"
ADJ_PAYLOAD = ROOT / "scripts" / "qa" / "t5b_repeat_corrections.json"
CONN_PAYLOAD = ROOT / "scripts" / "qa" / "t5b_connector_corrections.json"
FOLLOWUP_PAYLOAD = ROOT / "scripts" / "qa" / "t5b_followup_corrections.json"
HISTORICAL = ROOT / "docs" / "G4A_UKRAINIAN_QA_FINDINGS.csv"

WORD = re.compile(r"[A-Za-zА-Яа-яІіЇїЄєҐґ’']+(?:[-’'][A-Za-zА-Яа-яІіЇїЄєҐґ]+)*")
CONN = {"або", "чи", "та", "й", "і"}
COLUMNS = ["stable_id", "word", "field", "category", "severity", "original_text",
           "correction", "rationale", "confidence", "discovery_source",
           "discovery_date", "disposition"]
HISTORICAL_P1 = 314


def adjacent_repeats(s):
    t = list(WORD.finditer(s or ""))
    return [t[i].group() for i in range(len(t) - 1)
            if t[i].group().casefold() == t[i + 1].group().casefold()]


def _gap_only_ws_punct(gap):
    return re.search(r"[0-9A-Za-zА-Яа-яІіЇїЄєҐґ]", gap) is None


def has_connector_repeat(s):
    s = s or ""
    t = list(WORD.finditer(s))
    for i in range(len(t) - 2):
        if (t[i].group().casefold() == t[i + 2].group().casefold()
                and t[i + 1].group().casefold() in CONN
                and _gap_only_ws_punct(s[t[i].end():t[i + 1].start()])
                and _gap_only_ws_punct(s[t[i + 1].end():t[i + 2].start()])):
            return True
    return False


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


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

    adj = load(ADJ_PAYLOAD)
    conn = load(CONN_PAYLOAD)
    foll = load(FOLLOWUP_PAYLOAD)
    adj_corr = adj["corrections"]
    conn_corr = conn["corrections"]
    foll_corr = foll["corrections"]
    pay_benign = set(adj["_meta"]["benign_allowlist"])

    # Payload input/output blob chain: each stage output feeds the next stage input.
    if adj["_meta"]["expected_output_blob_sha1"] != conn["_meta"]["expected_input_blob_sha1"]:
        errors.append("adjacent stage output blob != connector stage input blob")
    if conn["_meta"]["expected_output_blob_sha1"] != foll["_meta"]["expected_input_blob_sha1"]:
        errors.append("connector stage output blob != follow-up stage input blob")

    # Effective shipped value = last stage to touch the id (followup > connector > adjacent).
    effective = {}
    for cid, c in adj_corr.items():
        effective[cid] = c["definitionUa"]
    for cid, c in conn_corr.items():
        effective[cid] = c["definitionUa"]
    for cid, c in foll_corr.items():
        effective[cid] = c["definitionUa"]

    ids = [r["stable_id"] for r in rows]
    if len(ids) != len(set(ids)):
        errors.append("duplicate stable_id in register")
    unknown = sorted(set(ids) - set(by_id))
    if unknown:
        errors.append(f"register ids not in vocabulary.js: {unknown[:10]}")

    by_disp = {}
    for r in rows:
        by_disp.setdefault(r["disposition"], []).append(r)
    corrected = by_disp.get("corrected", [])
    benign = by_disp.get("benign-allowlisted", [])
    still_open = len(by_disp.get("open-deferred-followup", []))
    needs_human = len(by_disp.get("needs-human-adjudication", []))
    other_disp = sorted(set(by_disp) - {"corrected", "benign-allowlisted",
                                        "open-deferred-followup", "needs-human-adjudication"})
    if other_disp:
        errors.append(f"unexpected disposition value(s): {other_disp}")
    if still_open:
        errors.append(f"{still_open} open-deferred-followup rows remain — gate stays CHANGES REQUESTED")
    if needs_human:
        errors.append(f"{needs_human} needs-human-adjudication rows remain — gate stays CHANGES REQUESTED")

    # The corrected set must exactly equal the union of the three guarded payloads' ids.
    corrected_ids = {r["stable_id"] for r in corrected}
    payload_ids = set(adj_corr) | set(conn_corr) | set(foll_corr)
    if corrected_ids != payload_ids:
        errors.append(f"corrected set != union of guarded payloads "
                      f"(only in register: {sorted(corrected_ids - payload_ids)[:5]}; "
                      f"only in payloads: {sorted(payload_ids - corrected_ids)[:5]})")

    p0 = p1 = 0
    for r in corrected:
        cid = r["stable_id"]
        disk = by_id[cid]["definitionUa"]
        if r["severity"] not in {"P0", "P1"}:
            errors.append(f"{cid}: corrected row severity {r['severity']} not P0/P1")
        if r["severity"] == "P0":
            p0 += 1
        elif r["severity"] == "P1":
            p1 += 1
        if not r["correction"].strip():
            errors.append(f"{cid}: corrected row has blank correction")
        if disk != r["correction"]:
            errors.append(f"{cid}: on-disk definitionUa != register correction")
        if cid in effective and disk != effective[cid]:
            errors.append(f"{cid}: on-disk definitionUa != effective (layered) payload value")
        if adjacent_repeats(disk):
            errors.append(f"{cid}: still has adjacent/punctuation repeat after correction")
        if has_connector_repeat(disk):
            errors.append(f"{cid}: still has connector-separated repeat after correction")

    if {r["stable_id"] for r in benign} != pay_benign:
        errors.append("benign-allowlisted set != adjacent payload benign_allowlist")
    for r in benign:
        cid = r["stable_id"]
        disk = by_id[cid]["definitionUa"]
        if disk != r["original_text"]:
            errors.append(f"{cid}: benign row original_text != on-disk value (should be untouched)")
        if not adjacent_repeats(disk):
            errors.append(f"{cid}: benign row no longer carries a repeat — should leave allowlist")
        if r["correction"].strip():
            errors.append(f"{cid}: benign row should carry no correction")

    # Historical vs supplemental separation: surface the frozen historical P1 backlog count.
    hist_p1 = 0
    if HISTORICAL.exists():
        with HISTORICAL.open(encoding="utf-8", newline="") as fh:
            hist_p1 = sum(1 for row in csv.DictReader(fh) if row["severity"] == "P1")
        if hist_p1 != HISTORICAL_P1:
            errors.append(f"historical register P1 count {hist_p1} != frozen {HISTORICAL_P1}")
    else:
        errors.append(f"{HISTORICAL} missing; cannot confirm historical P1 backlog is frozen")

    # Source-based split for reporting (structural, not brittle to exact counts).
    adj_rows = [r for r in corrected if "adjacent+punctuation-separated" in r["discovery_source"]]
    conn_rows = [r for r in corrected if "connector-separated" in r["discovery_source"]]
    foll_new = [r for r in corrected if r["stable_id"] in set(foll_corr) - set(conn_corr) - set(adj_corr)]
    conn_readjudicated = [r for r in corrected if r["stable_id"] in (set(conn_corr) & set(foll_corr))]

    print("G4-A T5-B SUPPLEMENTAL FINDINGS ACCOUNTING")
    print("==========================================")
    print(f"  register rows: {len(rows)} (corrected {len(corrected)}, benign {len(benign)}, "
          f"open {still_open}, needs-human {needs_human})")
    print(f"  historical-P1-resolved (frozen, separate register): {hist_p1} (T2/T3/T4/SB-0773)")
    print(f"  supplemental-P0-confirmed/corrected: {p0}")
    print(f"  supplemental-P1-confirmed/corrected: {p1}")
    print(f"    by stage source: adjacent {len(adj_rows)}, connector {len(conn_rows)} "
          f"(of which {len(conn_readjudicated)} re-adjudicated in the follow-up), "
          f"follow-up-new {len(foll_new)}")
    print(f"  supplemental-benign: {len(benign)}; supplemental-open: {still_open + needs_human}")
    print(f"  all corrected values match the layered guarded payloads + on-disk bytes; no residual "
          f"adjacent OR connector repeats")
    print()
    if errors:
        for e in errors:
            print("FAIL:", e)
        print(f"\nFAIL: {len(errors)} accounting assertion(s) failed.")
        return 1
    print("PASS: supplemental register reconciles with vocabulary.js and all three guarded payloads; "
          "zero open supplemental P0/P1; historical P1 backlog reported separately.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
