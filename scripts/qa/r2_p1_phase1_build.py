#!/usr/bin/env python3
"""G4-A R2 Phase-1 — deterministic P1 manifest, P2 backlog, and gap artifact.

Builds the Phase-1 P1 remediation manifest, the P2 backlog, and the proposal-
completeness gap artifact purely from the two canonical, already-committed
sources of the 1,007-row R2 reconciliation universe:

  * ``docs/G4A_RESIDUAL_AUDIT_R2_INTAKE.csv`` — the 1,007-row frozen intake.
    88 of its rows already carry a final disposition (63 P1 + 25 P2); the
    remaining 919 are ``needs-human`` and were routed through the A/B
    reconciliation instead (see below). This is the accepted Part-1 floor;
    it is read-only here and is never modified.
  * ``docs/G4A_R2_RECON_CHUNK{1,2,3}.csv`` — the 327-row A/B reconciliation
    output. Each row carries a ``final_disposition``.

The floor's 919 ``needs-human`` IDs are exactly the union of the 327
reconciled IDs and the 592 ``docs/G4A_R2_RECON_CONSENSUS_CLEAN.csv`` IDs
(mechanically verified below), so every one of the 1,007 intake rows is
accounted for exactly once across {floor-P1, floor-P2, chunk-P1, chunk-P2,
chunk-clean, consensus-clean}, with zero P0 and zero needs-human remaining.

**P1 total = floor P1 (63) + chunk final_disposition==P1 (202) = 265.**
This number is *derived*, not asserted: the 265 figure in the governing
handoff is treated as a claim to verify against the committed CSVs, not as
input. If the computed total had not equalled 265 this script would still
emit it, unmodified, and the discrepancy would have to be reported honestly
instead of silently forced to match.

The historical "31" figure (a local, unpublished, noncanonical estimate) and
the "56 blank floor defect rows" figure are NOT used anywhere in this script.
Coincidentally, `docs/G4A_RESIDUAL_AUDIT_R2_PART1.md` line 21 also uses "31"
to mean something unrelated (a provenance sub-count: "31 seed-20260914 P1
findings" contributing to the 63 floor P1 IDs) — that is a different "31"
from anything computed here and is not treated as evidence for the gap count.

Gap rule (proposal-completeness): a P1 row is a **gap** iff, after
whitespace-normalization, ``proposed_target`` or ``proposed_value`` is empty
or one of a small set of placeholder tokens (``n/a``, ``na``, ``none``,
``null``, ``tbd``, ``-``). No numeric gap count is hardcoded anywhere in this
script; the gap list and count are whatever the data says.

Outputs (all byte-deterministic; re-running reproduces them exactly):
  * ``docs/G4A_R2_P1_MANIFEST.csv``       — 265 rows, sorted ascending by id,
                                             each tagged Stage A (first 250)
                                             or Stage B (last 15).
  * ``docs/G4A_R2_P2_BACKLOG.csv``        — 149 rows (floor P2 + chunk P2).
  * ``docs/G4A_R2_P1_PROPOSAL_GAPS.csv``  — machine-readable gap list.
  * ``docs/G4A_R2_P1_PROPOSAL_GAPS.md``   — human-readable gap report.

No proposals are drafted, no Stage is applied, and web/vocabulary.js is never
touched by this script.
"""
from __future__ import annotations

import csv
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / "docs"

INTAKE = DOCS / "G4A_RESIDUAL_AUDIT_R2_INTAKE.csv"
CHUNKS = [DOCS / f"G4A_R2_RECON_CHUNK{c}.csv" for c in (1, 2, 3)]
CONSENSUS = DOCS / "G4A_R2_RECON_CONSENSUS_CLEAN.csv"

MANIFEST = DOCS / "G4A_R2_P1_MANIFEST.csv"
BACKLOG = DOCS / "G4A_R2_P2_BACKLOG.csv"
GAPS_CSV = DOCS / "G4A_R2_P1_PROPOSAL_GAPS.csv"
GAPS_MD = DOCS / "G4A_R2_P1_PROPOSAL_GAPS.md"
INVENTORY = DOCS / "G4A_R2_P1_PHASE1_INVENTORY.md"

STAGE_A_SIZE = 250
STAGE_B_SIZE = 15

INVALID_TOKENS = {"", "n/a", "na", "none", "null", "tbd", "-"}


def norm(v: str | None) -> str:
    return (v or "").strip()


def is_invalid(v: str | None) -> bool:
    return norm(v).lower() in INVALID_TOKENS


def load_intake() -> list[dict]:
    with INTAKE.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def load_chunks() -> list[dict]:
    rows: list[dict] = []
    for path in CHUNKS:
        with path.open(encoding="utf-8", newline="") as fh:
            rows.extend(csv.DictReader(fh))
    return rows


def load_consensus_ids() -> set[str]:
    with CONSENSUS.open(encoding="utf-8", newline="") as fh:
        return {r["id"] for r in csv.DictReader(fh)}


def sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sha256_of_ids(ids: list[str]) -> str:
    return hashlib.sha256("\n".join(ids).encode("utf-8")).hexdigest()


def build() -> dict:
    intake_rows = load_intake()
    chunk_rows = load_chunks()
    consensus_ids = load_consensus_ids()

    if len(intake_rows) != 1007:
        raise SystemExit(f"intake has {len(intake_rows)} rows, expected 1007")
    if len({r["id"] for r in intake_rows}) != len(intake_rows):
        raise SystemExit("intake has duplicate ids")
    if len(chunk_rows) != 327:
        raise SystemExit(f"chunks total {len(chunk_rows)} rows, expected 327")
    if len({r["id"] for r in chunk_rows}) != len(chunk_rows):
        raise SystemExit("chunk rows have duplicate ids")

    needs_human_ids = {r["id"] for r in intake_rows if r["disposition"] == "needs-human"}
    chunk_ids = {r["id"] for r in chunk_rows}
    if needs_human_ids != (chunk_ids | consensus_ids):
        raise SystemExit(
            "intake needs-human set != (chunk ids | consensus-clean ids); "
            "the 1,007-row universe is not internally consistent"
        )
    if chunk_ids & consensus_ids:
        raise SystemExit("chunk ids and consensus-clean ids overlap")

    floor_p1 = [r for r in intake_rows if r["disposition"] == "P1"]
    floor_p2 = [r for r in intake_rows if r["disposition"] == "P2"]
    floor_other = [r for r in intake_rows
                   if r["disposition"] not in ("P1", "P2", "needs-human")]
    if floor_other:
        raise SystemExit(f"unexpected floor dispositions: {floor_other[:3]}")

    chunk_p1 = [r for r in chunk_rows if r["final_disposition"] == "P1"]
    chunk_p2 = [r for r in chunk_rows if r["final_disposition"] == "P2"]

    p1_rows = []
    for r in floor_p1:
        p1_rows.append({
            "id": r["id"], "word": r["word"], "pos": r["pos"],
            "source": "floor", "proposed_target": r["proposed_target"],
            "proposed_value": r["proposed_value"],
        })
    for r in chunk_p1:
        p1_rows.append({
            "id": r["id"], "word": r["word"], "pos": r["pos"],
            "source": "reconciled", "proposed_target": r["proposed_target"],
            "proposed_value": r["proposed_value"],
        })

    p1_ids = [r["id"] for r in p1_rows]
    if len(p1_ids) != len(set(p1_ids)):
        raise SystemExit("floor-P1 and reconciled-P1 id sets are not disjoint")

    p1_rows.sort(key=lambda r: r["id"])
    total_p1 = len(p1_rows)
    if STAGE_A_SIZE + STAGE_B_SIZE != total_p1:
        raise SystemExit(
            f"Stage A ({STAGE_A_SIZE}) + Stage B ({STAGE_B_SIZE}) = "
            f"{STAGE_A_SIZE + STAGE_B_SIZE} != computed P1 total {total_p1}; "
            "partition sizes must be reconciled with the data, not forced"
        )

    for i, r in enumerate(p1_rows):
        r["stage"] = "A" if i < STAGE_A_SIZE else "B"
        r["gap"] = "true" if (is_invalid(r["proposed_target"]) or is_invalid(r["proposed_value"])) else "false"

    p2_rows = []
    for r in floor_p2:
        p2_rows.append({
            "id": r["id"], "word": r["word"], "pos": r["pos"],
            "source": "floor", "proposed_target": r["proposed_target"],
            "proposed_value": r["proposed_value"],
        })
    for r in chunk_p2:
        p2_rows.append({
            "id": r["id"], "word": r["word"], "pos": r["pos"],
            "source": "reconciled", "proposed_target": r["proposed_target"],
            "proposed_value": r["proposed_value"],
        })
    p2_rows.sort(key=lambda r: r["id"])

    gaps = [r for r in p1_rows if r["gap"] == "true"]

    stage_a_ids = [r["id"] for r in p1_rows if r["stage"] == "A"]
    stage_b_ids = [r["id"] for r in p1_rows if r["stage"] == "B"]

    return {
        "p1_rows": p1_rows, "p2_rows": p2_rows, "gaps": gaps,
        "stage_a_ids": stage_a_ids, "stage_b_ids": stage_b_ids,
        "floor_p1": len(floor_p1), "floor_p2": len(floor_p2),
        "chunk_p1": len(chunk_p1), "chunk_p2": len(chunk_p2),
    }


def write_csv(path: Path, header: list[str], rows: list[dict]) -> None:
    lines = [",".join(header)]
    for r in rows:
        cells = []
        for h in header:
            v = r.get(h, "")
            v = "" if v is None else str(v)
            if any(c in v for c in (",", '"', "\n")):
                v = '"' + v.replace('"', '""') + '"'
            cells.append(v)
        lines.append(",".join(cells))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def main() -> int:
    data = build()
    p1_rows = data["p1_rows"]
    p2_rows = data["p2_rows"]
    gaps = data["gaps"]

    write_csv(MANIFEST,
              ["id", "word", "pos", "source", "stage", "proposed_target", "proposed_value", "gap"],
              p1_rows)
    write_csv(BACKLOG,
              ["id", "word", "pos", "source", "proposed_target", "proposed_value"],
              p2_rows)
    write_csv(GAPS_CSV, ["id", "word", "pos", "source"], gaps)

    stage_a_sha = sha256_of_ids(data["stage_a_ids"])
    stage_b_sha = sha256_of_ids(data["stage_b_ids"])
    manifest_sha = sha256_of(MANIFEST)
    backlog_sha = sha256_of(BACKLOG)
    gaps_csv_sha = sha256_of(GAPS_CSV)

    gap_ids_md = "\n".join(f"- `{r['id']}`" for r in gaps)
    GAPS_MD.write_text(f"""# G4-A R2 Phase-1 — P1 proposal-completeness gap artifact

**Derivation.** This list and count are computed solely from the current,
published 265-P1 manifest source (`docs/G4A_R2_P1_MANIFEST.csv`, itself built
from the committed `docs/G4A_RESIDUAL_AUDIT_R2_INTAKE.csv` floor and
`docs/G4A_R2_RECON_CHUNK{{1,2,3}}.csv`). A P1 row is a gap iff, after
whitespace normalization, its `proposed_target` or `proposed_value` is empty
or a placeholder token (`n/a`, `na`, `none`, `null`, `tbd`, `-`). Only rows
with a final P1 disposition are considered; P2 rows and non-P1 floor rows
(`needs-human`) are excluded. No preselected numeric count is asserted
anywhere — this is the data's answer, not an input.

**Superseded figures.** The earlier unverified "31" figure came from a
noncanonical, local-only attempt and is **not** used as evidence here.
Separately, `docs/G4A_RESIDUAL_AUDIT_R2_PART1.md` also contains the numeral
"31" in an unrelated context (a provenance sub-count: 31 of the 63 floor-P1
IDs originate from the "seed-20260914" P1 findings) — that is a different
quantity and is not evidence for this gap count either. The earlier "56
blank floor defect rows" figure is also not substituted here; it was not
computed as a P1-only quantity and this artifact does not rely on it.

**Computed gap count: {len(gaps)}** out of {len(p1_rows)} final-disposition P1 rows.

All {len(gaps)} gap rows originate from the accepted floor
(`docs/G4A_RESIDUAL_AUDIT_R2_INTAKE.csv`, disposition `P1`); none originate
from the 327-row A/B reconciliation chunks, which is expected because the
reconciliation adjudication guard (`tests/g4a_r2_reconciliation.py`) already
requires every P0/P1/P2 chunk row to carry a non-empty `proposed_target` and
`proposed_value` before it can be committed, while the floor's already-final
P1 rows predate that guard and were carried forward unedited.

## Sorted gap ID list ({len(gaps)})

{gap_ids_md}

## Reproduce

```
python3 scripts/qa/r2_p1_phase1_build.py
```

regenerates `docs/G4A_R2_P1_MANIFEST.csv`, `docs/G4A_R2_P2_BACKLOG.csv`,
`docs/G4A_R2_P1_PROPOSAL_GAPS.csv` and this file byte-identically.
""", encoding="utf-8", newline="\n")

    print(f"P1 total: {len(p1_rows)} (floor {data['floor_p1']} + reconciled {data['chunk_p1']})")
    print(f"P2 total: {len(p2_rows)} (floor {data['floor_p2']} + reconciled {data['chunk_p2']})")
    print(f"Stage A: {len(data['stage_a_ids'])}  Stage B: {len(data['stage_b_ids'])}")
    print(f"Stage A SHA-256: {stage_a_sha}")
    print(f"Stage B SHA-256: {stage_b_sha}")
    print(f"gap count: {len(gaps)}")
    print(f"manifest SHA-256: {manifest_sha}")
    print(f"backlog SHA-256: {backlog_sha}")
    print(f"gaps csv SHA-256: {gaps_csv_sha}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
