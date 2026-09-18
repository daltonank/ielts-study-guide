#!/usr/bin/env python3
"""Assemble a Pass-B chunk judgment CSV from hand-authored per-row judgments.

This is scaffolding only: it joins the reviewer's authored judgment for each
stable ID (disposition, confidence, flagged axes, defect fields, and a
row-specific rationale) with that row's learner data, and writes the chunk CSV
with all nine axis columns explicit. It does NOT invent dispositions or
rationales — every judgment comes from the authored `judgments/chunkN.py`
module, one entry per manifest ID for that chunk. Missing or extra IDs are a
hard error, so the CSV cannot silently under/over-cover the chunk.
"""
from __future__ import annotations

import csv
import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / "docs"
INTAKE = DOCS / "G4A_RESIDUAL_AUDIT_R2_INTAKE.csv"
MANIFEST = DOCS / "G4A_R2_PASS_B_MANIFEST.csv"

AXES = ["ax_semantic", "ax_natural", "ax_grammar", "ax_pos", "ax_register",
        "ax_calque", "ax_consistency", "ax_pedagogical", "ax_ui"]
AXIS_ALIAS = {"s": "ax_semantic", "n": "ax_natural", "g": "ax_grammar",
              "p": "ax_pos", "r": "ax_register", "c": "ax_calque",
              "k": "ax_consistency", "d": "ax_pedagogical", "u": "ax_ui"}
COLS = (["id", "word", "pos", "ua", "definitionUa"] + AXES
        + ["disposition", "confidence", "category", "proposed_target",
           "proposed_value", "rationale"])


def load_judgments(chunk: int) -> dict:
    path = ROOT / "scripts" / "qa" / "judgments" / f"chunk{chunk}.py"
    spec = importlib.util.spec_from_file_location(f"chunk{chunk}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.JUDGMENTS


def main() -> None:
    chunk = int(sys.argv[1])
    ids = [r["id"] for r in csv.DictReader(MANIFEST.open(encoding="utf-8"))
           if int(r["chunk"]) == chunk]
    data = {r["id"]: r for r in csv.DictReader(INTAKE.open(encoding="utf-8"))}
    J = load_judgments(chunk)

    missing = [i for i in ids if i not in J]
    extra = [i for i in J if i not in ids]
    if missing or extra:
        raise SystemExit(f"chunk {chunk}: missing={missing[:5]} extra={extra[:5]}")

    out = DOCS / f"G4A_R2_PASS_B_CHUNK{chunk}.csv"
    with out.open("w", encoding="utf-8", newline="\n") as fh:
        w = csv.DictWriter(fh, fieldnames=COLS, lineterminator="\n")
        w.writeheader()
        for sid in ids:
            d = data[sid]
            j = J[sid]
            disp = j["disp"]
            flagged = {AXIS_ALIAS[a] for a in j.get("flag", "")}
            row = {"id": sid, "word": d["word"], "pos": d["pos"],
                   "ua": d["ua"], "definitionUa": d["definitionUa"],
                   "disposition": disp, "confidence": j["conf"],
                   "category": j.get("cat", ""),
                   "proposed_target": j.get("target", ""),
                   "proposed_value": j.get("value", ""),
                   "rationale": j["why"]}
            for ax in AXES:
                row[ax] = "flag" if ax in flagged else "pass"
            w.writerow(row)
    counts: dict[str, int] = {}
    for sid in ids:
        counts[J[sid]["disp"]] = counts.get(J[sid]["disp"], 0) + 1
    print(f"chunk {chunk}: {len(ids)} rows -> {out.name}  {counts}")


if __name__ == "__main__":
    main()
