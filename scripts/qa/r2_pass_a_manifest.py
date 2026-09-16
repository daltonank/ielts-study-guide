#!/usr/bin/env python3
"""Freeze deterministic stable-ID chunks for the R2 Pass-A review."""
from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
INTAKE = ROOT / "docs" / "G4A_RESIDUAL_AUDIT_R2_INTAKE.csv"
OUT = ROOT / "docs" / "G4A_R2_PASS_A_CHUNK_MANIFEST.json"
SIZES = (230, 230, 230, 229)


def load_pending_ids() -> list[str]:
    with INTAKE.open(encoding="utf-8", newline="") as fh:
        rows = csv.DictReader(fh)
        ids = [row["id"] for row in rows if row["disposition"] == "needs-human"]
    if len(ids) != 919 or len(set(ids)) != 919:
        raise ValueError("expected 919 unique pending stable IDs")
    if ids != sorted(ids):
        raise ValueError("pending stable IDs are not lexicographically sorted")
    return ids


def build_manifest(ids: list[str]) -> dict[str, object]:
    chunks: list[dict[str, object]] = []
    offset = 0
    for number, size in enumerate(SIZES, start=1):
        chunk_ids = ids[offset:offset + size]
        if len(chunk_ids) != size:
            raise ValueError(f"chunk {number} expected {size} IDs")
        chunks.append({
            "chunk": number,
            "count": size,
            "first_id": chunk_ids[0],
            "last_id": chunk_ids[-1],
            "ids": chunk_ids,
        })
        offset += size
    if offset != len(ids):
        raise ValueError("chunk sizes do not exhaust pending population")
    return {
        "schema_version": 1,
        "source": "docs/G4A_RESIDUAL_AUDIT_R2_INTAKE.csv",
        "selection": "all needs-human rows, stable IDs in lexicographic order",
        "pending_count": len(ids),
        "chunk_sizes": list(SIZES),
        "chunks": chunks,
    }


def render(manifest: dict[str, object]) -> bytes:
    return (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def main() -> int:
    manifest = build_manifest(load_pending_ids())
    OUT.write_bytes(render(manifest))
    for chunk in manifest["chunks"]:
        print(
            f"chunk {chunk['chunk']}: {chunk['count']} "
            f"{chunk['first_id']}..{chunk['last_id']}"
        )
    print("pending coverage: 919/919")
    print("wrote:", OUT.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
