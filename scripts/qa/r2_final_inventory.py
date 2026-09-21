#!/usr/bin/env python3
"""Deterministic G4-A R2 final inventory generator (Phase 1).

Unifies the three accepted R2 evidence populations into one 1,007-row inventory
and mechanically derives the proposal-completion gap roster from it.

Inputs (all byte-frozen at canonical head 39d6f918):
  * docs/G4A_RESIDUAL_AUDIT_R2_INTAKE.csv      1,007 rows; 88 Part-1 floor findings
                                               (63 P1 / 25 P2) + 919 needs-human
  * docs/G4A_R2_RECON_CHUNK{1,2,3}.csv         327 reconciled union-defect rows
  * docs/G4A_R2_RECON_CONSENSUS_CLEAN.csv      592 consensus-clean-candidate ids

Outputs:
  * docs/G4A_R2_FINAL_INVENTORY.csv            all 1,007 residual ids, exactly once
  * docs/G4A_R2_PROPOSAL_GAP_INVENTORY.csv     the Part-1-floor P1 rows carrying no
                                               correction proposal

The gap roster is DERIVED, never hand-listed: it is exactly those inventory rows
whose source_stage is the Part-1 floor, whose final disposition is P1, and whose
proposed_target/proposed_value are empty. At canonical head that yields the 31
seed-20260914 P1 findings -- the seed review carried only
id/disposition/category/rationale, with no proposal column, so those rows entered
the intake with empty proposals. The 32 R1-listed floor P1s all carry proposals
and are correctly excluded.

These rows sit OUTSIDE tests/g4a_r2_reconciliation.py's proposal requirement,
which governs only the 327-row union-defect roster. This generator reads the
reconciliation artifacts and never writes them.

Output is byte-deterministic across platforms: stable-id order, explicit LF,
UTF-8, written via write_bytes (never write_text, which would emit CRLF on
Windows and break raw-byte guards).
"""
from __future__ import annotations

import csv
import hashlib
import io
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / "docs"

INTAKE = DOCS / "G4A_RESIDUAL_AUDIT_R2_INTAKE.csv"
RECON_CHUNKS = [DOCS / f"G4A_R2_RECON_CHUNK{c}.csv" for c in (1, 2, 3)]
CONSENSUS = DOCS / "G4A_R2_RECON_CONSENSUS_CLEAN.csv"

INVENTORY_OUT = DOCS / "G4A_R2_FINAL_INVENTORY.csv"
GAP_OUT = DOCS / "G4A_R2_PROPOSAL_GAP_INVENTORY.csv"

EXPECTED_TOTAL = 1007
EXPECTED_FLOOR = 88
EXPECTED_RECONCILED = 327
EXPECTED_CONSENSUS = 592

STAGE_FLOOR = "part1-floor"
STAGE_RECON = "r2-reconciliation"
STAGE_CONSENSUS = "consensus-clean"

INVENTORY_COLS = [
    "id", "word", "pos", "ua", "definitionUa",
    "source_stage", "final_disposition", "category", "confidence",
    "provenance", "proposal_state", "proposed_target", "proposed_value",
]

GAP_COLS = [
    "id", "word", "pos", "ua", "definitionUa",
    "final_disposition", "category", "provenance", "existing_rationale",
    "proposal_state",
]


def read_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def stable_key(sid: str) -> tuple[str, int, str]:
    """Sort SB-0042 style ids numerically; fall back to lexical for anything else."""
    prefix, _, num = sid.partition("-")
    return (prefix, int(num), sid) if num.isdigit() else (prefix, 1 << 30, sid)


def nonempty(value: str | None) -> bool:
    return bool((value or "").strip())


def write_csv(path: Path, cols: list[str], rows: list[dict]) -> str:
    buf = io.StringIO(newline="")
    writer = csv.DictWriter(buf, fieldnames=cols, lineterminator="\n",
                            extrasaction="ignore")
    writer.writeheader()
    for row in rows:
        writer.writerow({c: row.get(c, "") for c in cols})
    payload = buf.getvalue().encode("utf-8")
    path.write_bytes(payload)
    return hashlib.sha256(payload).hexdigest()


def build() -> tuple[list[dict], list[dict], dict[str, str]]:
    intake = {r["id"]: r for r in read_csv(INTAKE)}
    if len(intake) != EXPECTED_TOTAL:
        sys.exit(f"FAIL: intake holds {len(intake)} ids, expected {EXPECTED_TOTAL}")

    recon: dict[str, dict] = {}
    for path in RECON_CHUNKS:
        for row in read_csv(path):
            if row["id"] in recon:
                sys.exit(f"FAIL: id {row['id']} appears in more than one recon chunk")
            recon[row["id"]] = row
    if len(recon) != EXPECTED_RECONCILED:
        sys.exit(f"FAIL: recon holds {len(recon)} ids, expected {EXPECTED_RECONCILED}")

    consensus = {r["id"] for r in read_csv(CONSENSUS)}
    if len(consensus) != EXPECTED_CONSENSUS:
        sys.exit(f"FAIL: consensus holds {len(consensus)} ids, "
                 f"expected {EXPECTED_CONSENSUS}")

    floor = {sid for sid, r in intake.items()
             if r["disposition"] in ("P1", "P2")}
    if len(floor) != EXPECTED_FLOOR:
        sys.exit(f"FAIL: floor holds {len(floor)} ids, expected {EXPECTED_FLOOR}")

    # The three populations must partition the intake exactly once each.
    if floor & recon.keys() or floor & consensus or recon.keys() & consensus:
        sys.exit("FAIL: populations overlap; each residual id must appear once")
    if floor | recon.keys() | consensus != set(intake):
        sys.exit("FAIL: populations do not cover the intake exactly")

    inventory: list[dict] = []
    for sid in sorted(intake, key=stable_key):
        base = intake[sid]
        if sid in floor:
            has_proposal = nonempty(base["proposed_target"]) and \
                           nonempty(base["proposed_value"])
            inventory.append({
                "id": sid,
                "word": base["word"], "pos": base["pos"],
                "ua": base["ua"], "definitionUa": base["definitionUa"],
                "source_stage": STAGE_FLOOR,
                "final_disposition": base["disposition"],
                "category": base["category"],
                "confidence": base["confidence"],
                "provenance": base["provenance"],
                "proposal_state": "present" if has_proposal else "absent",
                "proposed_target": base["proposed_target"],
                "proposed_value": base["proposed_value"],
            })
        elif sid in recon:
            row = recon[sid]
            has_proposal = nonempty(row["proposed_target"]) and \
                           nonempty(row["proposed_value"])
            disposition = row["final_disposition"]
            # A reconciled clean-candidate is not a defect, so it needs no proposal.
            state = "n/a" if disposition == "clean-candidate" else \
                    ("present" if has_proposal else "absent")
            inventory.append({
                "id": sid,
                "word": row["word"], "pos": row["pos"],
                "ua": row["ua"], "definitionUa": row["definitionUa"],
                "source_stage": STAGE_RECON,
                "final_disposition": disposition,
                "category": row["category"],
                "confidence": row["confidence"],
                "provenance": "R2 A/B reconciliation (union-defect roster)",
                "proposal_state": state,
                "proposed_target": row["proposed_target"],
                "proposed_value": row["proposed_value"],
            })
        else:
            inventory.append({
                "id": sid,
                "word": base["word"], "pos": base["pos"],
                "ua": base["ua"], "definitionUa": base["definitionUa"],
                "source_stage": STAGE_CONSENSUS,
                "final_disposition": "consensus-clean-candidate",
                "category": "", "confidence": "",
                "provenance": "R2 Pass A/B consensus clean; awaits fresh acceptance sample",
                "proposal_state": "n/a",
                "proposed_target": "", "proposed_value": "",
            })

    gaps = [
        {
            "id": r["id"], "word": r["word"], "pos": r["pos"],
            "ua": r["ua"], "definitionUa": r["definitionUa"],
            "final_disposition": r["final_disposition"],
            "category": r["category"],
            "provenance": r["provenance"],
            "existing_rationale": intake[r["id"]]["evidence"],
            "proposal_state": r["proposal_state"],
        }
        for r in inventory
        if r["source_stage"] == STAGE_FLOOR
        and r["final_disposition"] == "P1"
        and r["proposal_state"] == "absent"
    ]

    counts = {
        "total": len(inventory),
        "floor": sum(1 for r in inventory if r["source_stage"] == STAGE_FLOOR),
        "reconciled": sum(1 for r in inventory if r["source_stage"] == STAGE_RECON),
        "consensus": sum(1 for r in inventory if r["source_stage"] == STAGE_CONSENSUS),
        "gaps": len(gaps),
        "p1_total": sum(1 for r in inventory if r["final_disposition"] == "P1"),
    }
    return inventory, gaps, counts


def main() -> int:
    inventory, gaps, counts = build()
    inv_sha = write_csv(INVENTORY_OUT, INVENTORY_COLS, inventory)
    gap_sha = write_csv(GAP_OUT, GAP_COLS, gaps)

    print(f"inventory rows : {counts['total']}")
    print(f"  part1-floor      : {counts['floor']}")
    print(f"  r2-reconciliation: {counts['reconciled']}")
    print(f"  consensus-clean  : {counts['consensus']}")
    print(f"P1 total (floor + reconciled): {counts['p1_total']}")
    print(f"proposal gaps  : {counts['gaps']}")
    print(f"inventory SHA-256: {inv_sha}")
    print(f"gap SHA-256      : {gap_sha}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
