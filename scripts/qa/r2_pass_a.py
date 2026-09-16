#!/usr/bin/env python3
"""Validate and render explicit R2 Pass-A judgments without fallback-clean logic."""
from __future__ import annotations

import argparse
import csv
import io
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
INTAKE = ROOT / "docs" / "G4A_RESIDUAL_AUDIT_R2_INTAKE.csv"
MANIFEST = ROOT / "docs" / "G4A_R2_PASS_A_CHUNK_MANIFEST.json"
SOURCE_PATTERN = "scripts/qa/r2_pass_a_chunk_{chunk}_judgments.json"
OUT_PATTERN = "docs/G4A_R2_PASS_A_CHUNK_{chunk}.csv"

AXES = (
    "semantic_fidelity",
    "idiomatic_ukrainian",
    "grammar_morphology_syntax_punctuation_word_order",
    "pos_alignment",
    "learner_register",
    "russianism_surzhyk_calque_risk",
    "ua_definition_consistency",
    "pedagogical_accuracy",
    "ui_formatting_integrity",
)
AXIS_STATES = {"PASS", "DEFECT", "NA"}
DISPOSITIONS = {"P0", "P1", "P2", "clean-candidate"}
CONFIDENCE = {"high", "medium", "low"}
FIELDS = (
    "id", "word", "pos", "ua", "definitionUa", *AXES,
    "pass_a_disposition", "category", "confidence", "rationale",
    "proposed_target", "proposed_value",
)
CLEAN_RATIONALE = (
    "Fresh affirmative Pass-A review found the English sense, POS, Ukrainian "
    "pair, register, pedagogy, and UI presentation aligned on every rubric axis."
)


def load_inputs(chunk_number: int) -> tuple[list[dict[str, str]], dict[str, object]]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    try:
        chunk = manifest["chunks"][chunk_number - 1]
    except (IndexError, KeyError):
        raise ValueError(f"unknown chunk {chunk_number}") from None
    if chunk["chunk"] != chunk_number:
        raise ValueError("manifest chunk numbering mismatch")
    wanted = chunk["ids"]
    with INTAKE.open(encoding="utf-8", newline="") as fh:
        by_id = {row["id"]: row for row in csv.DictReader(fh)}
    return [by_id[stable_id] for stable_id in wanted], chunk


def validate_source(
    source: dict[str, object], rows: list[dict[str, str]], chunk: dict[str, object]
) -> tuple[set[str], dict[str, dict[str, object]]]:
    expected = [row["id"] for row in rows]
    if source.get("chunk") != chunk["chunk"]:
        raise ValueError("judgment source chunk does not match manifest")
    clean = source.get("clean_candidate_ids")
    defects = source.get("defects")
    if not isinstance(clean, list) or not isinstance(defects, list):
        raise ValueError("source must explicitly list clean candidates and defects")
    if len(clean) != len(set(clean)):
        raise ValueError("duplicate clean-candidate ID")
    defect_ids = [item.get("id") for item in defects if isinstance(item, dict)]
    if len(defect_ids) != len(defects) or len(defect_ids) != len(set(defect_ids)):
        raise ValueError("invalid or duplicate defect ID")
    if set(clean) & set(defect_ids):
        raise ValueError("ID cannot be both clean candidate and defect")
    accounted = set(clean) | set(defect_ids)
    if accounted != set(expected):
        missing = sorted(set(expected) - accounted)
        extra = sorted(accounted - set(expected))
        raise ValueError(f"no fallback-clean allowed; missing={missing} extra={extra}")

    defect_map: dict[str, dict[str, object]] = {}
    for item in defects:
        disposition = item.get("disposition")
        if disposition not in DISPOSITIONS - {"clean-candidate"}:
            raise ValueError(f"{item.get('id')}: invalid defect disposition")
        if item.get("confidence") not in CONFIDENCE:
            raise ValueError(f"{item.get('id')}: invalid confidence")
        for field in ("category", "rationale", "proposed_target", "proposed_value"):
            if not isinstance(item.get(field), str) or not item[field].strip():
                raise ValueError(f"{item.get('id')}: missing {field}")
        axes = item.get("axes")
        if not isinstance(axes, dict) or set(axes) != set(AXES):
            raise ValueError(f"{item.get('id')}: incomplete axis evidence")
        if any(state not in AXIS_STATES for state in axes.values()):
            raise ValueError(f"{item.get('id')}: invalid axis state")
        if "DEFECT" not in axes.values():
            raise ValueError(f"{item.get('id')}: defect row has no defective axis")
        defect_map[item["id"]] = item
    return set(clean), defect_map


def build_rows(chunk_number: int, source: dict[str, object]) -> list[dict[str, str]]:
    rows, chunk = load_inputs(chunk_number)
    clean, defects = validate_source(source, rows, chunk)
    rendered: list[dict[str, str]] = []
    for row in rows:
        stable_id = row["id"]
        if stable_id in clean:
            judgment: dict[str, object] = {
                "axes": {axis: "PASS" for axis in AXES},
                "disposition": "clean-candidate",
                "category": "none",
                "confidence": "high",
                "rationale": CLEAN_RATIONALE,
                "proposed_target": "",
                "proposed_value": "",
            }
        else:
            judgment = defects[stable_id]
        rendered.append({
            "id": stable_id,
            "word": row["word"],
            "pos": row["pos"],
            "ua": row["ua"],
            "definitionUa": row["definitionUa"],
            **{axis: judgment["axes"][axis] for axis in AXES},
            "pass_a_disposition": judgment["disposition"],
            "category": judgment["category"],
            "confidence": judgment["confidence"],
            "rationale": judgment["rationale"],
            "proposed_target": judgment["proposed_target"],
            "proposed_value": judgment["proposed_value"],
        })
    return rendered


def render_csv(rows: list[dict[str, str]]) -> bytes:
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=FIELDS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue().encode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--chunk", type=int, required=True, choices=range(1, 5))
    args = parser.parse_args()
    source_path = ROOT / SOURCE_PATTERN.format(chunk=args.chunk)
    source = json.loads(source_path.read_text(encoding="utf-8"))
    rows = build_rows(args.chunk, source)
    out = ROOT / OUT_PATTERN.format(chunk=args.chunk)
    out.write_bytes(render_csv(rows))
    counts = {key: sum(row["pass_a_disposition"] == key for row in rows)
              for key in DISPOSITIONS}
    print(f"chunk {args.chunk}: rows={len(rows)} counts={counts}")
    print("wrote:", out.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
