#!/usr/bin/env python3
"""G4-A residual audit R2 — Pass B pre-inspection manifest generator.

Deterministic, reproducible, and blind: this script derives the Pass-B review
population from the *identifiers only* of the Part-1 intake
(`docs/G4A_RESIDUAL_AUDIT_R2_INTAKE.csv`). It never reads the learner-facing
`ua` / `definitionUa` text, so the ordering cannot be influenced by the content
under review. Run this and commit its output BEFORE any learner text is
inspected.

Algorithm (fixed):
  1. Select every intake row whose disposition == "needs-human" (the 919 rows
     left pending at the Part-1 checkpoint). The 88-row accepted floor
     (63 P1 + 25 P2) is excluded and is not part of Pass B.
  2. Sort the selected stable IDs in ascending lexicographic order. IDs are
     zero-padded (SB-0001 ...), so lexicographic order equals numeric order.
  3. Deterministically shuffle with Python's Mersenne-Twister PRNG seeded at
     20260916: `random.Random(20260916).shuffle(ids)`. This ordering is stable
     across CPython versions.
  4. Split the shuffled list into four chunks of 230 / 230 / 230 / 229.

Outputs:
  - docs/G4A_R2_PASS_B_MANIFEST.csv  (columns: chunk,seq,id)  LF / UTF-8
  - docs/G4A_R2_PASS_B.md            (algorithm, seed, split, manifest SHA-256)
"""
from __future__ import annotations

import csv
import hashlib
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
INTAKE = ROOT / "docs" / "G4A_RESIDUAL_AUDIT_R2_INTAKE.csv"
MANIFEST = ROOT / "docs" / "G4A_R2_PASS_B_MANIFEST.csv"
REPORT = ROOT / "docs" / "G4A_R2_PASS_B.md"

SEED = 20260916
SPLIT = (230, 230, 230, 229)


def select_ids() -> list[str]:
    """Return the needs-human stable IDs, reading the id/disposition columns only."""
    with INTAKE.open(encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        ids = [row["id"] for row in reader if row["disposition"] == "needs-human"]
    if len(ids) != sum(SPLIT):
        raise SystemExit(
            f"expected {sum(SPLIT)} needs-human rows, found {len(ids)}"
        )
    if len(set(ids)) != len(ids):
        raise SystemExit("duplicate stable IDs in needs-human population")
    return ids


def build_order(ids: list[str]) -> list[str]:
    ordered = sorted(ids)  # lexicographic == numeric (zero-padded)
    rng = random.Random(SEED)
    rng.shuffle(ordered)
    return ordered


def chunk_of(index: int) -> int:
    bound = 0
    for c, size in enumerate(SPLIT, start=1):
        bound += size
        if index < bound:
            return c
    raise AssertionError("index out of range")


def write_manifest(order: list[str]) -> None:
    # Explicit LF newlines, UTF-8, no BOM — deterministic bytes.
    lines = ["chunk,seq,id"]
    for seq, sid in enumerate(order):
        lines.append(f"{chunk_of(seq)},{seq},{sid}")
    MANIFEST.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_report(order: list[str], manifest_sha: str) -> None:
    counts = ", ".join(
        f"chunk {i}: {n}" for i, n in enumerate(SPLIT, start=1)
    )
    body = f"""# G4-A residual audit R2 — Pass B

Independent, blind, second-pass linguistic review of the residual-audit
population. Executor: Claude Code. Reasoning owner / reviewer: ChatGPT. Final
authority: Dalton.

Blind baseline commit: `5a5fd7d7ce8cc4e7c3f8a2b2a0253269ed803ac0`
Learner baseline (PR #7 head): `f34f109ae5b8564e7fa10317c167a6ca728c52fd`
Learner vocabulary blob (unchanged by Pass B): `1c184e84e5c63e3a9f8e386af13787664a23bd66`

Gate remains `G4 technical PASS · G4-A CHANGES REQUESTED · G5 BLOCKED`. Pass B
is second-pass *evidence only*; it applies no remediation, moves no PR, changes
no gate, and starts no G5 work.

## Population

The Pass-B population is the **919 `needs-human` rows** pending at the Part-1
checkpoint (`docs/G4A_RESIDUAL_AUDIT_R2_INTAKE.csv`). The accepted 88-row floor
(63 P1 + 25 P2) is **excluded** and must not be modified or downgraded.

## Deterministic ordering (fixed before inspection)

1. Select the 919 `needs-human` stable IDs from the Part-1 intake (id column
   only — learner text is not read to build this manifest).
2. Sort ascending lexicographically (zero-padded, so == numeric order).
3. Shuffle with CPython Mersenne-Twister: `random.Random({SEED}).shuffle(ids)`.
4. Split into four chunks of {" / ".join(str(n) for n in SPLIT)}.

Seed: `{SEED}`  ·  Split: {counts}  ·  Total: {sum(SPLIT)}

Manifest file: `docs/G4A_R2_PASS_B_MANIFEST.csv`
Manifest SHA-256: `{manifest_sha}`

Reproduce: `python3 scripts/qa/r2_pass_b_manifest.py` regenerates an identical
manifest and prints the same SHA-256.

## Judgment artifacts

Per-chunk row-level judgments (committed one chunk at a time, after that
chunk's judgments are complete):

- `docs/G4A_R2_PASS_B_CHUNK1.csv`
- `docs/G4A_R2_PASS_B_CHUNK2.csv`
- `docs/G4A_R2_PASS_B_CHUNK3.csv`
- `docs/G4A_R2_PASS_B_CHUNK4.csv`

Each row records explicit states for all nine axes (semantic fidelity;
natural/idiomatic contemporary Ukrainian; grammar/morphology/syntax/
punctuation/word-order; POS alignment; learner register;
Russianism/Surzhyk/calque risk; `ua` ↔ `definitionUa` consistency;
pedagogical accuracy for the intended IELTS sense; UI/formatting integrity),
plus disposition (`P0`/`P1`/`P2`/`clean-candidate`), confidence, and a
row-specific rationale. Defect rows additionally carry category, proposed
target field, and proposed replacement value. Clean candidates carry
affirmative per-row evidence — no synthesized generic rationale.

Guard/validator: `tests/g4a_r2_pass_b.py`.
"""
    REPORT.write_text(body, encoding="utf-8", newline="\n")


def main() -> None:
    ids = select_ids()
    order = build_order(ids)
    assert len(order) == sum(SPLIT)
    assert len(set(order)) == len(order)
    write_manifest(order)
    manifest_sha = sha256_of(MANIFEST)
    write_report(order, manifest_sha)
    print(f"needs-human population: {len(order)}")
    print(f"split: {SPLIT}")
    print(f"manifest: {MANIFEST.relative_to(ROOT)}")
    print(f"manifest SHA-256: {manifest_sha}")


if __name__ == "__main__":
    main()
