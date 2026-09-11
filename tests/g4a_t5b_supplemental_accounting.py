#!/usr/bin/env python3
"""Accounting reconciliation for the G4-A T5-B supplemental findings register (issue #4).

Ties docs/G4A_T5B_SUPPLEMENTAL_FINDINGS.csv to the actual learner-facing bytes in
web/vocabulary.js and to BOTH guarded correction payloads, so the register cannot state
one thing while the shipped data says another. The register now covers two remediated
repeat classes plus the benign allowlist:

  * corrected — adjacent/punctuation-separated (35): id resolves; the on-disk definitionUa
    equals the recorded correction and equals the adjacent payload correction; it carries no
    adjacent/punctuation-separated repeat anymore.
  * corrected — connector-separated (64): id resolves; the on-disk definitionUa equals the
    recorded correction and equals the connector payload correction; it carries no
    connector-separated repeat anymore.
  * benign-allowlisted (2): id resolves; definitionUa is unchanged from the recorded
    original; the entry STILL carries an adjacent repeat (so the allowlist is live) and the
    set equals the adjacent payload's benign_allowlist and the guard's ADJACENT_ALLOWLIST.
  * open-deferred-followup / needs-human-adjudication (0): none may remain. If ANY confirmed
    supplemental P1 is still open, this fails closed and the gate stays CHANGES REQUESTED.

It also surfaces the historical P1 backlog count (314, frozen in G4A_UKRAINIAN_QA_FINDINGS.csv)
so historical vs supplemental P1 accounting can never be conflated. These are
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
HISTORICAL = ROOT / "docs" / "G4A_UKRAINIAN_QA_FINDINGS.csv"

WORD = re.compile(r"[A-Za-zА-Яа-яІіЇїЄєҐґ’']+(?:[-’'][A-Za-zА-Яа-яІіЇїЄєҐґ]+)*")
CONN = {"або", "чи", "та", "й", "і"}
COLUMNS = ["stable_id", "word", "field", "category", "severity", "original_text",
           "correction", "rationale", "confidence", "discovery_source",
           "discovery_date", "disposition"]
# Corrected rows split by source: adjacent/punctuation-separated (35) + connector (64) = 99.
ADJ_SOURCE_MARK = "adjacent+punctuation-separated"
CONN_SOURCE_MARK = "connector-separated"
EXPECTED = {"corrected": 99, "benign-allowlisted": 2}
EXPECTED_ADJ_CORRECTED = 35
EXPECTED_CONN_CORRECTED = 64
HISTORICAL_P1 = 314


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
    adj_payload = json.loads(ADJ_PAYLOAD.read_text(encoding="utf-8"))
    conn_payload = json.loads(CONN_PAYLOAD.read_text(encoding="utf-8"))
    adj_corr = adj_payload["corrections"]
    conn_corr = conn_payload["corrections"]
    pay_benign = set(adj_payload["_meta"]["benign_allowlist"])

    # Payload input/output blob chain: adjacent stage output feeds the connector stage input.
    if adj_payload["_meta"]["expected_output_blob_sha1"] != conn_payload["_meta"]["expected_input_blob_sha1"]:
        errors.append("adjacent stage output blob != connector stage input blob")

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
    # No confirmed supplemental P1 may still be open (would keep the gate CHANGES REQUESTED).
    still_open = len(by_disp.get("open-deferred-followup", []))
    needs_human = len(by_disp.get("needs-human-adjudication", []))
    if still_open:
        errors.append(f"{still_open} open-deferred-followup rows remain — gate stays CHANGES REQUESTED")
    if needs_human:
        errors.append(f"{needs_human} needs-human-adjudication rows remain — gate stays CHANGES REQUESTED")
    if len(rows) != sum(EXPECTED.values()):
        errors.append(f"total rows {len(rows)} != {sum(EXPECTED.values())}")

    corrected = by_disp.get("corrected", [])
    adj_rows = [r for r in corrected if ADJ_SOURCE_MARK in r["discovery_source"]]
    conn_rows = [r for r in corrected if CONN_SOURCE_MARK in r["discovery_source"]]
    if len(adj_rows) != EXPECTED_ADJ_CORRECTED:
        errors.append(f"adjacent corrected rows {len(adj_rows)} != {EXPECTED_ADJ_CORRECTED}")
    if len(conn_rows) != EXPECTED_CONN_CORRECTED:
        errors.append(f"connector corrected rows {len(conn_rows)} != {EXPECTED_CONN_CORRECTED}")
    if len(adj_rows) + len(conn_rows) != len(corrected):
        errors.append("corrected rows not cleanly partitioned into adjacent + connector by source")

    if {r["stable_id"] for r in adj_rows} != set(adj_corr):
        errors.append("adjacent corrected set != adjacent guarded payload corrections set")
    for r in adj_rows:
        cid = r["stable_id"]
        disk = by_id[cid]["definitionUa"]
        if disk != r["correction"]:
            errors.append(f"{cid}: on-disk definitionUa != register correction")
        if disk != adj_corr.get(cid, {}).get("definitionUa"):
            errors.append(f"{cid}: on-disk definitionUa != adjacent payload correction")
        if adjacent_repeats(disk):
            errors.append(f"{cid}: still has adjacent/punctuation repeat after correction")
        if r["severity"] != "P1" or not r["correction"].strip():
            errors.append(f"{cid}: adjacent corrected row severity/correction invalid")

    if {r["stable_id"] for r in conn_rows} != set(conn_corr):
        errors.append("connector corrected set != connector guarded payload corrections set")
    for r in conn_rows:
        cid = r["stable_id"]
        disk = by_id[cid]["definitionUa"]
        if disk != r["correction"]:
            errors.append(f"{cid}: on-disk definitionUa != register correction")
        if disk != conn_corr.get(cid, {}).get("definitionUa"):
            errors.append(f"{cid}: on-disk definitionUa != connector payload correction")
        if has_connector_repeat(disk):
            errors.append(f"{cid}: still has connector-separated repeat after correction")
        if r["severity"] != "P1" or not r["correction"].strip():
            errors.append(f"{cid}: connector corrected row severity/correction invalid")

    benign = by_disp.get("benign-allowlisted", [])
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

    # Historical vs supplemental separation: surface the frozen historical P1 backlog count so
    # nobody can read this reconciliation as though it covered the whole P1 universe.
    hist_p1 = 0
    if HISTORICAL.exists():
        with HISTORICAL.open(encoding="utf-8", newline="") as fh:
            hist_p1 = sum(1 for row in csv.DictReader(fh) if row["severity"] == "P1")
        if hist_p1 != HISTORICAL_P1:
            errors.append(f"historical register P1 count {hist_p1} != frozen {HISTORICAL_P1}")
    else:
        errors.append(f"{HISTORICAL} missing; cannot confirm historical P1 backlog is frozen")

    print("G4-A T5-B SUPPLEMENTAL FINDINGS ACCOUNTING")
    print("==========================================")
    print(f"  register rows: {len(rows)} "
          f"(corrected {len(corrected)} = adjacent {len(adj_rows)} + connector {len(conn_rows)}, "
          f"benign {len(benign)}, open {still_open}, needs-human {needs_human})")
    print(f"  historical P1 backlog (frozen, separate register): {hist_p1} resolved earlier "
          f"(T2/T3/T4/SB-0773)")
    print(f"  supplemental P1 confirmed & corrected: {len(adj_rows) + len(conn_rows)} "
          f"(adjacent {len(adj_rows)} + connector {len(conn_rows)})")
    print(f"  supplemental benign/allowlisted: {len(benign)}; supplemental open/needs-human: "
          f"{still_open + needs_human}")
    print(f"  all corrected values match guarded payloads + on-disk bytes; no residual repeats")
    print()
    if errors:
        for e in errors:
            print("FAIL:", e)
        print(f"\nFAIL: {len(errors)} accounting assertion(s) failed.")
        return 1
    print("PASS: supplemental register reconciles with vocabulary.js and both guarded payloads; "
          "zero unresolved supplemental P1; historical P1 backlog reported separately.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
