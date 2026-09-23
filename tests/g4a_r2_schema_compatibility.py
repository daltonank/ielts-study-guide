#!/usr/bin/env python3
"""Check accepted legacy semantics and the approved native Batch-3 schema."""

from __future__ import annotations

import csv
import importlib.util
import io
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "11b2de229f7b1c51065abc3ec338fbf3d41df702"
DOCS = ROOT / "docs"
BATCHES = DOCS / "batches"
COMBINED = DOCS / "G4A_R2_SUPPLEMENTAL_PROPOSALS.csv"
COLS = ["id", "batch", "word", "pos", "ua", "definitionUa", "category",
        "existing_rationale", "evidence_quote", "proposed_ua",
        "proposed_definitionUa", "rationale", "confidence", "answer_kind"]
IDS3 = ["SB-1270", "SB-1275", "SB-1335", "SB-1495", "SB-1523",
        "SB-1570", "SB-1585", "SB-1590", "SB-1630", "SB-1668", "SB-1747"]
APPROVED3 = {
    "SB-1270": ("", "Підтвердити або перевірити правдивість або точність чогось."),
    "SB-1275": ("", "Такий, що можна здійснити на практиці; здійсненний."),
    "SB-1335": ("", "Такий, що існує протягом тривалого часу, тому визнаний і загальновизнаний."),
    "SB-1495": ("конференція", ""),
    "SB-1523": ("", "Окрема частина послідовності або циклу, що відбувається з часом."),
    "SB-1570": ("", "Ракурс або точка зору, з якої можна відчути, класифікувати, виміряти або кодифікувати досвід."),
    "SB-1585": ("", "Короткий виклад або підсумок більшої публікації."),
    "SB-1590": ("прикріплений; приєднаний", "Прикріплений або приєднаний до чогось."),
    "SB-1630": ("", "Особи, які досягли повноліття."),
    "SB-1668": ("", "Внесено або винесено на затвердження, розгляд, відмітку тощо."),
    "SB-1747": ("", "Загальноприйняті правила або стандарти поведінки."),
}


def rows(payload: bytes) -> tuple[list[str], list[dict[str, str]]]:
    reader = csv.DictReader(io.StringIO(payload.decode("utf-8"), newline=""))
    assert reader.fieldnames is not None
    result = list(reader)
    assert all(None not in row and all(value is not None for value in row.values())
               for row in result)
    return reader.fieldnames, result


def at_base(path: str) -> bytes:
    return subprocess.run(["git", "show", f"{BASE}:{path}"], cwd=ROOT,
                          check=True, capture_output=True).stdout


def main() -> None:
    old_cols, old_rows = rows(at_base("docs/G4A_R2_SUPPLEMENTAL_PROPOSALS.csv"))
    assert old_cols == ["id", "batch", "word", "pos", "ua", "definitionUa",
                        "category", "existing_rationale", "evidence_quote",
                        "proposed_target", "proposed_value", "rationale",
                        "confidence", "answer_kind"]
    assert len(old_rows) == 20 and len({r["id"] for r in old_rows}) == 20
    for batch in (1, 2):
        path = f"docs/batches/G4A_R2_PROPOSAL_BATCH{batch}.csv"
        assert (ROOT / path).read_bytes() == at_base(path), path

    cols, current = rows(COMBINED.read_bytes())
    assert cols == COLS
    assert len(current) == 31 and len({r["id"] for r in current}) == 31
    by_id = {r["id"]: r for r in current}
    for old in old_rows:
        now = by_id[old["id"]]
        for field in ("id", "batch", "word", "pos", "ua", "definitionUa",
                      "category", "existing_rationale", "evidence_quote",
                      "rationale", "confidence", "answer_kind"):
            assert now[field] == old[field], (old["id"], field)
        target, value = old["proposed_target"], old["proposed_value"]
        assert target in ("ua", "definitionUa", "")
        assert now["proposed_ua"] == (value if target == "ua" else "")
        assert now["proposed_definitionUa"] == (value if target == "definitionUa" else "")

    path3 = BATCHES / "G4A_R2_PROPOSAL_BATCH3.csv"
    payload3 = path3.read_bytes()
    assert b"\r" not in payload3
    cols3, batch3 = rows(payload3)
    assert cols3 == COLS
    assert [r["id"] for r in batch3] == IDS3
    assert all(r["batch"] == "3" and r["answer_kind"] == "correction" for r in batch3)
    for row in batch3:
        sid = row["id"]
        assert (row["proposed_ua"], row["proposed_definitionUa"]) == APPROVED3[sid]
        assert by_id[sid] == row

    assert [r["id"] for r in current if r["proposed_ua"] and
            r["proposed_definitionUa"]] == ["SB-1590"]
    assert sum(r["answer_kind"] == "correction" for r in current) == 31
    assert sum(r["answer_kind"] == "no-change" for r in current) == 0
    assert [sum(r["batch"] == str(batch) for r in current) for batch in (1, 2, 3)] == [10, 10, 11]

    spec = importlib.util.spec_from_file_location(
        "proposal_builder", ROOT / "scripts/qa/r2_supplemental_proposals.py")
    assert spec and spec.loader
    builder = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(builder)
    legacy = {"id": old_rows[0]["id"], "evidence_quote": old_rows[0]["evidence_quote"],
              "proposed_target": "both", "proposed_value": "ambiguous",
              "rationale": old_rows[0]["rationale"], "confidence": old_rows[0]["confidence"]}
    try:
        builder.normalize_authored(legacy, 1, old_rows[0])
    except SystemExit as exc:
        assert "ambiguous legacy" in str(exc)
    else:
        raise AssertionError("legacy proposed_target='both' was accepted")
    print("PASS: 20 legacy rows retain accepted semantics; Batch 3 has 11 approved rows; "
          "only SB-1590 changes both fields; legacy both fails closed; coverage 31/31")


if __name__ == "__main__":
    try:
        main()
    except (AssertionError, OSError, UnicodeError, subprocess.CalledProcessError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
