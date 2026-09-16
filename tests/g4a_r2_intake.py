#!/usr/bin/env python3
"""Guard the audit-only R2 intake boundary and accepted known floor."""
from __future__ import annotations

import csv
import json
import re
import subprocess
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INTAKE = ROOT / "docs" / "G4A_RESIDUAL_AUDIT_R2_INTAKE.csv"
REVISED = ROOT / "scripts" / "qa" / "r2_revised_corrections.json"
BASE = "d98f3f46cb6d0cce5e5d2a32c42b1eaa16305537"
LEARNER_BLOB = "1c184e84e5c63e3a9f8e386af13787664a23bd66"
REVISED_IDS = {
    "SB-0024", "SB-0067", "SB-0467", "SB-1081",
    "SB-1464", "SB-1635", "SB-1695", "SB-1707",
}


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def main() -> int:
    with INTAKE.open(encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))
    ids = [row["id"] for row in rows]
    counts = Counter(row["disposition"] for row in rows)
    assert len(rows) == len(set(ids)) == 1007
    assert ids == sorted(ids)
    assert counts == {"needs-human": 919, "P1": 63, "P2": 25}
    assert all(row["disposition"] != "clean" for row in rows)
    assert all(row["evidence"].strip() for row in rows)
    assert all(row["category"].strip() for row in rows)

    r1_ids = {
        row["id"] for row in rows
        if row["provenance"].startswith("R1-listed defect")
    }
    assert len(r1_ids) == 32
    assert all(row["disposition"] == "P1" for row in rows if row["id"] in r1_ids)

    revised = json.loads(REVISED.read_text(encoding="utf-8"))
    assert revised["_meta"]["not_applied"] is True
    assert set(revised["corrections"]) == REVISED_IDS
    assert all(item["proposed"].strip() for item in revised["corrections"].values())
    assert all(item["rationale"].strip() for item in revised["corrections"].values())

    source = (ROOT / "web" / "vocabulary.js").read_text(encoding="utf-8")
    match = re.search(r"window\.VOCABULARY\s*=\s*(\[.*\]);", source, re.S)
    assert match and len(json.loads(match.group(1))) == 1784
    assert git("rev-parse", "HEAD:web/vocabulary.js") == LEARNER_BLOB
    assert git("merge-base", BASE, "HEAD") == BASE

    raw = INTAKE.read_bytes()
    assert b"\r\n" not in raw and raw.endswith(b"\n")

    print("G4-A R2 INTAKE PASS")
    print("rows=1007 P1=63 P2=25 needs-human=919 clean=0")
    print("R1 defects=32 all P1; revised-eight=8; learner blob unchanged")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
