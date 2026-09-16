#!/usr/bin/env python3
"""Render the deterministic R2 Pass-A accounting summary."""
from __future__ import annotations

import csv
import hashlib
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs" / "G4A_R2_PASS_A_SUMMARY.md"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def render() -> bytes:
    combined: list[dict[str, str]] = []
    chunk_lines: list[str] = []
    for number, expected in enumerate((230, 230, 230, 229), start=1):
        path = ROOT / "docs" / f"G4A_R2_PASS_A_CHUNK_{number}.csv"
        with path.open(encoding="utf-8", newline="") as fh:
            rows = list(csv.DictReader(fh))
        if len(rows) != expected:
            raise ValueError(f"chunk {number}: expected {expected} rows")
        counts = Counter(row["pass_a_disposition"] for row in rows)
        combined.extend(rows)
        chunk_lines.append(
            f"| {number} | {rows[0]['id']}..{rows[-1]['id']} | {len(rows)} | "
            f"{counts['P0']} | {counts['P1']} | {counts['P2']} | "
            f"{counts['clean-candidate']} | `{sha256(path)}` |"
        )
    ids = [row["id"] for row in combined]
    if not (len(ids) == len(set(ids)) == 919):
        raise ValueError("combined Pass-A IDs are not 919 unique rows")
    counts = Counter(row["pass_a_disposition"] for row in combined)
    p0 = [row["id"] for row in combined if row["pass_a_disposition"] == "P0"]
    p1 = [row["id"] for row in combined if row["pass_a_disposition"] == "P1"]
    p2 = [row["id"] for row in combined if row["pass_a_disposition"] == "P2"]
    text = "\n".join([
        "# G4-A R2 Pass-A accounting summary",
        "",
        "This is first-pass audit evidence only. `clean-candidate` is not a final validation.",
        "No Pass-B adjudication or learner-facing correction is included.",
        "",
        "| Chunk | Stable-ID range | Rows | P0 | P1 | P2 | Clean candidate | CSV SHA-256 |",
        "|---:|---|---:|---:|---:|---:|---:|---|",
        *chunk_lines,
        "",
        f"Total: {len(combined)} rows; P0={counts['P0']}; P1={counts['P1']}; "
        f"P2={counts['P2']}; clean-candidate={counts['clean-candidate']}.",
        "",
        "## Defect stable IDs",
        "",
        "P0: " + (", ".join(p0) if p0 else "none"),
        "",
        "P1: " + ", ".join(p1),
        "",
        "P2: " + ", ".join(p2),
        "",
    ])
    return text.encode("utf-8")


def main() -> int:
    content = render()
    OUT.write_bytes(content)
    print("wrote:", OUT.relative_to(ROOT))
    print("sha256=" + hashlib.sha256(content).hexdigest())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
