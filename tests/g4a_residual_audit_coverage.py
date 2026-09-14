#!/usr/bin/env python3
"""CP4 coverage proof for the G4-A residual-population audit (issue #4). READ-ONLY.

Deterministically proves that the CP3 inventory covers the residual population exactly:
every residual ID appears exactly once with a valid disposition — none skipped, none
duplicated, none extra. Also re-checks the deterministic bucket reconciliation to 1,784
and that the 24 canonical known-open IDs are all present as P1 in the inventory.

Exit 0 only if all assertions hold. Non-vacuous: a seeded missing/duplicate/invalid row
is demonstrated to fail before the real check runs.
"""
from pathlib import Path
import csv, sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "qa"))
import residual_audit_lib as lib

INV = ROOT / "docs" / "G4A_RESIDUAL_AUDIT_CP3_INVENTORY.csv"
VALID = {"clean", "P0", "P1", "P2", "needs-human"}


def check_rows(rows, residual):
    ids = [r["id"] for r in rows]
    id_set = set(ids)
    errors = []
    if len(ids) != len(id_set):
        from collections import Counter
        dups = [k for k, v in Counter(ids).items() if v > 1]
        errors.append(f"duplicate inventory rows: {dups}")
    missing = set(residual) - id_set
    extra = id_set - set(residual)
    if missing:
        errors.append(f"{len(missing)} residual IDs missing from inventory: {sorted(missing)[:10]}")
    if extra:
        errors.append(f"{len(extra)} extra IDs in inventory: {sorted(extra)[:10]}")
    bad = [r["id"] for r in rows if r["disposition"] not in VALID]
    if bad:
        errors.append(f"{len(bad)} rows with invalid disposition: {bad[:10]}")
    return errors


def main():
    residual = lib.residual_ids()
    bk = lib.buckets()
    total = sum(len(v) for v in bk.values())

    # --- non-vacuity self-check: seeded broken inventory must be caught ---
    good = [{"id": _id, "disposition": "clean"} for _id in residual]
    seeded_missing = good[:-1]                              # drop one
    seeded_dup = good + [good[0]]                           # duplicate one
    seeded_bad = [dict(good[0], disposition="???")] + good[1:]  # invalid disposition
    assert check_rows(seeded_missing, residual), "self-check: missing row not caught"
    assert check_rows(seeded_dup, residual), "self-check: duplicate row not caught"
    assert check_rows(seeded_bad, residual), "self-check: invalid disposition not caught"

    # --- real check ---
    with INV.open(encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    errors = check_rows(rows, residual)

    known = set(lib.KNOWN_OPEN_24)
    disp_by_id = {r["id"]: r["disposition"] for r in rows}
    known_not_p1 = sorted(k for k in known if disp_by_id.get(k) != "P1")
    if known_not_p1:
        errors.append(f"known-open IDs not P1 in inventory: {known_not_p1}")

    examined = len(set(r["id"] for r in rows) & set(residual))
    coverage = examined / len(residual) if residual else 0

    print("G4-A RESIDUAL AUDIT — COVERAGE PROOF")
    print("====================================")
    print(f"  bucket reconciliation a+b+c+d = {total} (expected 1784):",
          "OK" if total == 1784 else "MISMATCH")
    print(f"  residual population: {len(residual)}")
    print(f"  inventory rows: {len(rows)}")
    print(f"  examined / residual-total = {examined} / {len(residual)} = {coverage*100:.1f}%")
    print(f"  24 known-open all present as P1: {'yes' if not known_not_p1 else 'NO'}")
    print(f"  non-vacuity self-check (seeded missing/dup/invalid all caught): yes")

    if errors or total != 1784 or coverage != 1.0:
        print("FAIL:")
        for e in errors:
            print("  -", e)
        if total != 1784:
            print("  - bucket reconciliation != 1784")
        if coverage != 1.0:
            print("  - coverage != 100%")
        return 1
    print("PASS: every residual ID dispositioned exactly once; 100% coverage; "
          "buckets reconcile to 1784; 24 known-open all present as P1.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
