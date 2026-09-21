#!/usr/bin/env python3
"""Assemble a reconciliation chunk CSV from hand-authored per-row verdicts.

Joins, for each roster ID in the chunk:
  * frozen word/pos/ua/definitionUa + Pass-B disposition/rationale (from Pass B
    2b90574) and Pass-A disposition/rationale/category/proposal (from Pass A
    f7ddf7b1), all read by exact SHA;
  * the reviewer's authored final verdict from
    scripts/qa/recon_judgments/chunkN.py: J[id] = {
        "fd": final disposition, "conf": confidence,
        "ev": exact-substring evidence quote,
        "why": final row-specific rationale,
        optional "cat"/"tgt"/"val" overrides (else defaulted from Pass A),
    }.

For a defect final disposition, category/proposed_target/proposed_value default
to Pass A's (target 'ua+definitionUa' -> 'both') unless overridden. For a
clean-candidate/needs-human final, no proposal is emitted. Missing/extra IDs
are a hard error.
"""
from __future__ import annotations

import csv
import importlib.util
import io
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / "docs"
ROSTER = DOCS / "G4A_R2_RECON_ROSTER.csv"
PASS_A = "f7ddf7b1dadfd91a8126b15c0977873be02f883c"
PASS_B = "2b90574e3dafb88313ac6563ec094577fb7a95a2"

COLS = ["id", "word", "pos", "ua", "definitionUa",
        "pass_a_disposition", "pass_a_rationale",
        "pass_b_disposition", "pass_b_rationale",
        "evidence_quote", "final_disposition", "confidence",
        "category", "rationale", "proposed_target", "proposed_value"]
TARGET_MAP = {"ua+definitionUa": "both", "ua": "ua",
              "definitionUa": "definitionUa", "": ""}
DEFECTS = {"P0", "P1", "P2"}


def show(sha: str, p: str) -> str:
    return subprocess.run(["git", "show", f"{sha}:{p}"], cwd=ROOT,
                          capture_output=True, text=True, check=True).stdout


def main() -> None:
    chunk = int(sys.argv[1])
    ids = [r["id"] for r in csv.DictReader(ROSTER.open(encoding="utf-8"))
           if int(r["chunk"]) == chunk]

    A = {}
    for c in (1, 2, 3, 4):
        for r in csv.DictReader(io.StringIO(show(PASS_A, f"docs/G4A_R2_PASS_A_CHUNK_{c}.csv"))):
            A[r["id"]] = r
    B = {}
    for c in (1, 2, 3, 4):
        for r in csv.DictReader(io.StringIO(show(PASS_B, f"docs/G4A_R2_PASS_B_CHUNK{c}.csv"))):
            B[r["id"]] = r

    path = ROOT / "scripts" / "qa" / "recon_judgments" / f"chunk{chunk}.py"
    spec = importlib.util.spec_from_file_location(f"recon{chunk}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    J = mod.JUDGMENTS

    missing = [i for i in ids if i not in J]
    extra = [i for i in J if i not in ids]
    if missing or extra:
        raise SystemExit(f"chunk {chunk}: missing={missing[:5]} extra={extra[:5]}")

    out = DOCS / f"G4A_R2_RECON_CHUNK{chunk}.csv"
    counts: dict[str, int] = {}
    with out.open("w", encoding="utf-8", newline="\n") as fh:
        w = csv.DictWriter(fh, fieldnames=COLS, lineterminator="\n")
        w.writeheader()
        for sid in ids:
            a, b, j = A[sid], B[sid], J[sid]
            # Final disposition defaults to Pass A's (confirmed on the frozen
            # text) unless the reviewer explicitly overrides it.
            fd = j.get("fd", a["pass_a_disposition"])
            counts[fd] = counts.get(fd, 0) + 1
            if fd in DEFECTS:
                cat = j.get("cat", a["category"])
                tgt = j.get("tgt", TARGET_MAP.get(a["proposed_target"], a["proposed_target"]))
                val = j.get("val", a["proposed_value"])
            else:
                cat = tgt = val = ""
            w.writerow({
                "id": sid, "word": a["word"], "pos": a["pos"],
                "ua": a["ua"], "definitionUa": a["definitionUa"],
                "pass_a_disposition": a["pass_a_disposition"],
                "pass_a_rationale": a["rationale"],
                "pass_b_disposition": b["disposition"],
                "pass_b_rationale": b["rationale"],
                "evidence_quote": j["ev"], "final_disposition": fd,
                "confidence": j.get("conf", "high"), "category": cat,
                "rationale": j["why"], "proposed_target": tgt,
                "proposed_value": val,
            })
    print(f"chunk {chunk}: {len(ids)} rows -> {out.name}  {counts}")


if __name__ == "__main__":
    main()
