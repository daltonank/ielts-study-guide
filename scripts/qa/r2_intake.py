#!/usr/bin/env python3
"""Build the audit-only R2 intake register from the accepted known floor.

Part 1 deliberately does not inherit any R1 clean disposition. Rows without
accepted evidence enter R2 as needs-human pending fresh adjudication.
"""
from __future__ import annotations

import csv
import io
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import residual_audit_lib as lib


ROOT = lib.ROOT
R1_INVENTORY = ROOT / "docs" / "G4A_RESIDUAL_AUDIT_CP3_INVENTORY.csv"
R1_CORRECTIONS = ROOT / "scripts" / "qa" / "cp4_proposed_corrections.json"
R2_REVISED = ROOT / "scripts" / "qa" / "r2_revised_corrections.json"
SEED_REVIEW = ROOT / "docs" / "G4A_R2_SEED_20260914_REVIEW.csv"
OUT = ROOT / "docs" / "G4A_RESIDUAL_AUDIT_R2_INTAKE.csv"

FIELDS = [
    "id", "word", "pos", "ua", "definitionUa", "disposition", "category",
    "evidence", "confidence", "provenance", "proposed_target", "proposed_value",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def write_csv_lf(path: Path, rows: list[dict[str, str]]) -> None:
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=FIELDS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    path.write_bytes(buffer.getvalue().encode("utf-8"))


def main() -> int:
    vocab = lib.load_vocab()
    by_id = {entry["id"]: entry for entry in vocab}
    residual = lib.residual_ids(vocab)

    r1_rows = read_csv(R1_INVENTORY)
    r1_defects = {
        row["id"]: row for row in r1_rows
        if row["disposition"] in {"P0", "P1", "P2"}
    }
    if len(r1_defects) != 32:
        raise SystemExit(f"expected 32 R1 defects, got {len(r1_defects)}")

    seed_rows = {
        row["id"]: row for row in read_csv(SEED_REVIEW)
        if row["disposition"] in {"P0", "P1", "P2"}
    }
    if len(seed_rows) != 56:
        raise SystemExit(f"expected 56 seed findings, got {len(seed_rows)}")
    if set(r1_defects) & set(seed_rows):
        raise SystemExit("R1 defects and seed-20260914 findings overlap")

    original = json.loads(R1_CORRECTIONS.read_text(encoding="utf-8"))["corrections"]
    revised = json.loads(R2_REVISED.read_text(encoding="utf-8"))["corrections"]
    corrections = dict(original)
    corrections.update(revised)

    accepted: dict[str, dict[str, str]] = {}
    for stable_id, source in r1_defects.items():
        correction = corrections.get(stable_id, {})
        accepted[stable_id] = {
            "disposition": "P1",
            "category": source["category"],
            "evidence": source["rationale"],
            "confidence": source["confidence"],
            "provenance": "R1-listed defect; severity normalized to P1 by Codex acceptance review",
            "proposed_target": correction.get("target", ""),
            "proposed_value": correction.get("proposed", ""),
        }
    for stable_id, source in seed_rows.items():
        accepted[stable_id] = {
            "disposition": source["disposition"],
            "category": source["category"],
            "evidence": source["rationale"],
            "confidence": "high" if source["disposition"] == "P1" else "medium",
            "provenance": "Codex seed-20260914 blinded acceptance challenge",
            "proposed_target": "",
            "proposed_value": "",
        }

    rows = []
    for stable_id in residual:
        entry = by_id[stable_id]
        judgment = accepted.get(stable_id)
        if judgment is None:
            judgment = {
                "disposition": "needs-human",
                "category": "pending-r2-adjudication",
                "evidence": "No fresh R2 adjudication recorded; the R1 clean disposition is intentionally not inherited.",
                "confidence": "",
                "provenance": "R2 intake pending fresh stable-ID review",
                "proposed_target": "",
                "proposed_value": "",
            }
        rows.append({
            "id": stable_id,
            "word": entry.get("word", ""),
            "pos": entry.get("pos", ""),
            "ua": entry.get("ua", ""),
            "definitionUa": entry.get("definitionUa", ""),
            **judgment,
        })

    write_csv_lf(OUT, rows)
    counts = {key: sum(row["disposition"] == key for row in rows)
              for key in ("P0", "P1", "P2", "clean", "needs-human")}
    print("R2 intake rows:", len(rows))
    print("known floor:", {"P1": counts["P1"], "P2": counts["P2"]})
    print("pending fresh adjudication:", counts["needs-human"])
    print("wrote:", OUT.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
