#!/usr/bin/env python3
"""Guard for the G4-A R2 final inventory + proposal-gap roster (Phase 1).

Fails closed on any of:

  * the inventory or gap roster is not byte-reproducible from its generator;
  * accepted reconciliation evidence, the Part-1 floor artifact, or the learner
    vocabulary blob drifted from canonical head 39d6f918;
  * the 1,007 residual ids are not partitioned exactly once across the three
    source stages (88 floor / 327 reconciled / 592 consensus-clean);
  * any inventory row's frozen word/pos/ua/definitionUa disagrees with the
    Part-1 intake;
  * the gap roster is not exactly {part1-floor} x {P1} x {proposal absent};
  * any gap id leaks into the 327-row reconciliation roster (which owns its own
    proposal requirement) or carries a non-empty proposal in the intake;
  * the P1 population is not the 265 rows the Stage A/B manifest will consume;
  * any generated artifact contains CRLF.

Read-only with respect to every accepted artifact: this guard regenerates only
the two Phase-1 outputs.
"""
from __future__ import annotations

import csv
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"

CANONICAL_HEAD = "39d6f918c7087d3616acc9654eecfaf5219aefc4"
EXPECTED_VOCAB_BLOB = "1c184e84e5c63e3a9f8e386af13787664a23bd66"
EXPECTED_FLOOR_BLOB = "7f34785e379ac76ee5341d4f65f33b123d57bc43"

FROZEN_PATHS = [
    "web/vocabulary.js",
    "docs/G4A_RESIDUAL_AUDIT_R2_INTAKE.csv",
    "docs/G4A_R2_RECON_CHUNK1.csv",
    "docs/G4A_R2_RECON_CHUNK2.csv",
    "docs/G4A_R2_RECON_CHUNK3.csv",
    "docs/G4A_R2_RECON_CONSENSUS_CLEAN.csv",
    "docs/G4A_R2_RECON_ROSTER.csv",
    "docs/G4A_R2_SEED_20260914_REVIEW.csv",
]

INVENTORY = DOCS / "G4A_R2_FINAL_INVENTORY.csv"
GAPS = DOCS / "G4A_R2_PROPOSAL_GAP_INVENTORY.csv"
ROSTER = DOCS / "G4A_R2_RECON_ROSTER.csv"
INTAKE = DOCS / "G4A_RESIDUAL_AUDIT_R2_INTAKE.csv"

EXPECTED = {"total": 1007, "floor": 88, "reconciled": 327,
            "consensus": 592, "gaps": 31, "p1": 265}

errors: list[str] = []


def err(msg: str) -> None:
    errors.append(msg)


def read_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def git_blob(rev: str, path: str) -> str:
    return subprocess.run(["git", "rev-parse", f"{rev}:{path}"], cwd=ROOT,
                          capture_output=True, text=True).stdout.strip()


def check_frozen() -> None:
    """Accepted evidence must be byte-identical to canonical head."""
    for path in FROZEN_PATHS:
        head, canon = git_blob("HEAD", path), git_blob(CANONICAL_HEAD, path)
        if not canon:
            err(f"{path}: not present at canonical head {CANONICAL_HEAD[:8]}")
        elif head != canon:
            err(f"{path}: drifted from canonical head ({head[:8]} != {canon[:8]})")
    if git_blob("HEAD", "web/vocabulary.js") != EXPECTED_VOCAB_BLOB:
        err("learner web/vocabulary.js blob changed")
    if git_blob("HEAD", "docs/G4A_RESIDUAL_AUDIT_R2_INTAKE.csv") != EXPECTED_FLOOR_BLOB:
        err("Part-1 floor intake artifact changed")


def check_reproducible() -> None:
    before = {p: p.read_bytes() for p in (INVENTORY, GAPS) if p.exists()}
    if len(before) != 2:
        err("inventory / gap roster missing; run scripts/qa/r2_final_inventory.py")
        return
    proc = subprocess.run([sys.executable, "scripts/qa/r2_final_inventory.py"],
                          cwd=ROOT, capture_output=True, text=True)
    if proc.returncode != 0:
        err(f"generator failed: {proc.stderr.strip()[:300]}")
        return
    for path, payload in before.items():
        if path.read_bytes() != payload:
            err(f"{path.name}: not byte-reproducible from its generator")
        if b"\r\n" in path.read_bytes():
            err(f"{path.name}: contains CRLF")


def check_inventory() -> tuple[list[dict], dict[str, dict]]:
    inv = read_csv(INVENTORY)
    intake = {r["id"]: r for r in read_csv(INTAKE)}

    if len(inv) != EXPECTED["total"]:
        err(f"inventory holds {len(inv)} rows, expected {EXPECTED['total']}")
    ids = [r["id"] for r in inv]
    if len(set(ids)) != len(ids):
        err("inventory contains duplicate ids")
    if set(ids) != set(intake):
        err("inventory id set does not match the Part-1 intake")

    stages = {"part1-floor": 0, "r2-reconciliation": 0, "consensus-clean": 0}
    for row in inv:
        if row["source_stage"] not in stages:
            err(f"{row['id']}: unknown source_stage {row['source_stage']!r}")
            continue
        stages[row["source_stage"]] += 1
        base = intake.get(row["id"], {})
        for field in ("word", "pos", "ua", "definitionUa"):
            if row[field] != base.get(field):
                err(f"{row['id']}: {field} disagrees with the frozen intake")

    for stage, key in (("part1-floor", "floor"),
                       ("r2-reconciliation", "reconciled"),
                       ("consensus-clean", "consensus")):
        if stages[stage] != EXPECTED[key]:
            err(f"stage {stage}: {stages[stage]} rows, expected {EXPECTED[key]}")

    p1 = sum(1 for r in inv if r["final_disposition"] == "P1")
    if p1 != EXPECTED["p1"]:
        err(f"P1 population is {p1}, expected {EXPECTED['p1']} "
            "(Stage A/B remediation scope)")
    return inv, intake


def check_gaps(inv: list[dict], intake: dict[str, dict]) -> None:
    gaps = read_csv(GAPS)
    if len(gaps) != EXPECTED["gaps"]:
        err(f"gap roster holds {len(gaps)} rows, expected {EXPECTED['gaps']}")

    gap_ids = {r["id"] for r in gaps}
    if len(gap_ids) != len(gaps):
        err("gap roster contains duplicate ids")

    # The roster must equal the derived predicate exactly -- never hand-curated.
    derived = {r["id"] for r in inv
               if r["source_stage"] == "part1-floor"
               and r["final_disposition"] == "P1"
               and r["proposal_state"] == "absent"}
    if gap_ids != derived:
        err(f"gap roster is not the derived predicate "
            f"(+{sorted(gap_ids - derived)[:3]} / -{sorted(derived - gap_ids)[:3]})")

    # These rows sit outside the 327-row reconciliation guard's proposal duty.
    roster_ids = {r["id"] for r in read_csv(ROSTER)}
    leak = gap_ids & roster_ids
    if leak:
        err(f"gap ids overlap the 327-row reconciliation roster: {sorted(leak)[:5]}")

    for row in gaps:
        base = intake.get(row["id"], {})
        if base.get("disposition") != "P1":
            err(f"{row['id']}: intake disposition is not P1")
        if (base.get("proposed_target") or "").strip() or \
           (base.get("proposed_value") or "").strip():
            err(f"{row['id']}: intake already carries a proposal; not a gap")
        if row["proposal_state"] != "absent":
            err(f"{row['id']}: proposal_state is not 'absent'")
        if not (row["category"] or "").strip():
            err(f"{row['id']}: missing category")


def main() -> int:
    check_frozen()
    check_reproducible()
    if not INVENTORY.exists() or not GAPS.exists():
        print("FAIL: Phase-1 artifacts missing", file=sys.stderr)
        return 1
    inv, intake = check_inventory()
    check_gaps(inv, intake)

    if errors:
        print(f"FAIL - {len(errors)} violation(s):", file=sys.stderr)
        for e in errors[:40]:
            print(f"  - {e}", file=sys.stderr)
        return 1
    print(f"PASS - inventory {EXPECTED['total']} rows "
          f"({EXPECTED['floor']} floor / {EXPECTED['reconciled']} reconciled / "
          f"{EXPECTED['consensus']} consensus-clean); "
          f"P1 population {EXPECTED['p1']}; "
          f"proposal gaps {EXPECTED['gaps']}; accepted evidence byte-frozen.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
