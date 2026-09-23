#!/usr/bin/env python3
"""Deterministic builder for the G4-A R2 supplemental proposal-completion artifact.

Assembles per-batch authored proposals into one supplemental artifact covering
the 31 Part-1-floor P1 findings that carry no correction proposal.

This is a SEPARATE artifact by design. The accepted A/B reconciliation evidence
(`docs/G4A_R2_RECON_CHUNK{1,2,3}.csv` and friends) stays byte-frozen; nothing
here edits it, and the 327-row reconciliation guard is untouched.

Inputs:
  * docs/G4A_R2_PROPOSAL_GAP_INVENTORY.csv   the 31-row derived gap roster
  * docs/batches/G4A_R2_PROPOSAL_BATCH{N}.csv authored batches (N = 1..3)

Output:
  * docs/G4A_R2_SUPPLEMENTAL_PROPOSALS.csv

Batches are the deterministic 10/10/11 split of the gap roster in stable-id
order: rows 1-10 -> batch 1, 11-20 -> batch 2, 21-31 -> batch 3. Batches land
incrementally and each is reviewed before the next is authored, so a partial
build is normal and is reported as such.

These are PROPOSALS ONLY. Nothing here is applied to learner-facing content; a
reviewer (ChatGPT) adjudicates before any correction manifest is authorized.

Output is byte-deterministic: stable-id order, explicit LF, UTF-8, write_bytes.
"""
from __future__ import annotations

import csv
import hashlib
import io
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / "docs"
GAPS = DOCS / "G4A_R2_PROPOSAL_GAP_INVENTORY.csv"
BATCH_DIR = DOCS / "batches"
OUT = DOCS / "G4A_R2_SUPPLEMENTAL_PROPOSALS.csv"

EXPECTED_GAPS = 31
BATCH_SIZES = {1: 10, 2: 10, 3: 11}

COLS = [
    "id", "batch", "word", "pos", "ua", "definitionUa",
    "category", "existing_rationale",
    "evidence_quote", "proposed_ua", "proposed_definitionUa",
    "rationale", "confidence", "answer_kind",
]
LEGACY_COLS = ["id", "evidence_quote", "proposed_target", "proposed_value",
               "rationale", "confidence"]


def read_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        if not reader.fieldnames or len(reader.fieldnames) != len(set(reader.fieldnames)):
            sys.exit(f"FAIL: {path}: missing or duplicate CSV header")
        rows = list(reader)
        if any(None in row or any(value is None for value in row.values()) for row in rows):
            sys.exit(f"FAIL: {path}: malformed CSV row")
        return rows


def normalize_authored(row: dict, batch: int, gap: dict) -> dict:
    """Map accepted legacy rows mechanically; Batch 3 uses the native schema."""
    sid = row["id"]
    if batch in (1, 2):
        if set(row) != set(LEGACY_COLS):
            sys.exit(f"FAIL: {sid}: legacy batch has unexpected columns")
        target, value = row["proposed_target"].strip(), row["proposed_value"].strip()
        if target == "both":
            sys.exit(f"FAIL: {sid}: ambiguous legacy proposed_target='both'")
        if target not in ("", "ua", "definitionUa") or bool(target) != bool(value):
            sys.exit(f"FAIL: {sid}: invalid legacy target/value pair")
        return {
            "evidence_quote": row["evidence_quote"],
            "proposed_ua": value if target == "ua" else "",
            "proposed_definitionUa": value if target == "definitionUa" else "",
            "rationale": row["rationale"], "confidence": row["confidence"],
            "answer_kind": "correction" if target else "no-change",
        }

    if set(row) != set(COLS):
        sys.exit(f"FAIL: {sid}: Batch 3 must use the explicit proposal columns")
    if row["batch"] != str(batch):
        sys.exit(f"FAIL: {sid}: source batch {row['batch']!r}, expected {batch}")
    for field in ("word", "pos", "ua", "definitionUa", "category", "existing_rationale"):
        if row[field] != gap[field]:
            sys.exit(f"FAIL: {sid}: source {field} differs from frozen gap roster")
    return {field: row[field] for field in COLS if field not in
            ("id", "batch", "word", "pos", "ua", "definitionUa", "category",
             "existing_rationale")}


def stable_key(sid: str) -> tuple[str, int, str]:
    prefix, _, num = sid.partition("-")
    return (prefix, int(num), sid) if num.isdigit() else (prefix, 1 << 30, sid)


def batch_assignment(gap_ids: list[str]) -> dict[str, int]:
    """Deterministic 10/10/11 split over the gap roster in stable-id order."""
    ordered = sorted(gap_ids, key=stable_key)
    assignment: dict[str, int] = {}
    cursor = 0
    for batch, size in sorted(BATCH_SIZES.items()):
        for sid in ordered[cursor:cursor + size]:
            assignment[sid] = batch
        cursor += size
    if cursor != len(ordered):
        sys.exit(f"FAIL: batch sizes cover {cursor} ids, roster holds {len(ordered)}")
    return assignment


def main() -> int:
    gaps = {r["id"]: r for r in read_csv(GAPS)}
    if len(gaps) != EXPECTED_GAPS:
        sys.exit(f"FAIL: gap roster holds {len(gaps)} rows, expected {EXPECTED_GAPS}")
    assignment = batch_assignment(list(gaps))

    authored: dict[str, dict] = {}
    present: list[int] = []
    for batch in sorted(BATCH_SIZES):
        path = BATCH_DIR / f"G4A_R2_PROPOSAL_BATCH{batch}.csv"
        if not path.exists():
            continue
        present.append(batch)
        for row in read_csv(path):
            sid = row["id"]
            if sid in authored:
                sys.exit(f"FAIL: {sid} authored in more than one batch")
            if sid not in gaps:
                sys.exit(f"FAIL: {sid} is not on the 31-row gap roster")
            if assignment[sid] != batch:
                sys.exit(f"FAIL: {sid} belongs to batch {assignment[sid]}, "
                         f"found in batch {batch}")
            authored[sid] = row

    rows = []
    for sid in sorted(authored, key=stable_key):
        g, a = gaps[sid], authored[sid]
        proposal = normalize_authored(a, assignment[sid], g)
        rows.append({
            "id": sid,
            "batch": assignment[sid],
            "word": g["word"], "pos": g["pos"],
            "ua": g["ua"], "definitionUa": g["definitionUa"],
            "category": g["category"],
            "existing_rationale": g["existing_rationale"],
            **proposal,
        })

    buf = io.StringIO(newline="")
    writer = csv.DictWriter(buf, fieldnames=COLS, lineterminator="\n",
                            extrasaction="ignore")
    writer.writeheader()
    for row in rows:
        writer.writerow(row)
    payload = buf.getvalue().encode("utf-8")
    OUT.write_bytes(payload)

    corrections = sum(1 for r in rows if r["answer_kind"] == "correction")
    nochange = sum(1 for r in rows if r["answer_kind"] == "no-change")
    print(f"batches present : {present}")
    print(f"rows authored   : {len(rows)} / {EXPECTED_GAPS}")
    print(f"  corrections   : {corrections}")
    print(f"  no-change     : {nochange}")
    conf = {}
    for r in rows:
        conf[r["confidence"]] = conf.get(r["confidence"], 0) + 1
    print(f"confidence      : {conf}")
    print(f"SHA-256         : {hashlib.sha256(payload).hexdigest()}")
    print("coverage        : " +
          ("COMPLETE" if len(rows) == EXPECTED_GAPS else "PARTIAL (batches pending)"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
