#!/usr/bin/env python3
"""Guard / validator for G4-A residual audit R2 Pass B.

Independently re-derives the Pass-B manifest and validates the per-chunk
row-level judgment artifacts against the handoff contract:

  * the manifest regenerates deterministically to the recorded SHA-256;
  * every present chunk uses exactly the IDs the manifest assigns to it
    (no missing IDs, no duplicates, no cross-chunk leakage);
  * every judged row states all nine axes with a valid state;
  * disposition and confidence are from the allowed vocabularies;
  * defect rows (P0/P1/P2) flag >=1 axis and carry category + proposed target
    + proposed value;
  * clean-candidate rows pass all nine axes, carry no proposal, and carry
    affirmative, row-specific rationale evidence (references the row's own
    headword or its Ukrainian gloss) that is not a synthesized generic string;
  * the learner vocabulary blob and the Part-1 intake (which carries the
    accepted 88-row floor) are unchanged from the blind baseline;
  * when all four chunks are present, union coverage is exactly 919/919.

Exit non-zero on any violation. Prints an honest coverage summary either way.
"""
from __future__ import annotations

import csv
import hashlib
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
MANIFEST = DOCS / "G4A_R2_PASS_B_MANIFEST.csv"
REPORT = DOCS / "G4A_R2_PASS_B.md"
INTAKE = DOCS / "G4A_RESIDUAL_AUDIT_R2_INTAKE.csv"
CHUNK_FILES = {c: DOCS / f"G4A_R2_PASS_B_CHUNK{c}.csv" for c in (1, 2, 3, 4)}

BASELINE = "5a5fd7d7ce8cc4e7c3f8a2b2a0253269ed803ac0"
EXPECTED_VOCAB_BLOB = "1c184e84e5c63e3a9f8e386af13787664a23bd66"

AXES = [
    "ax_semantic",
    "ax_natural",
    "ax_grammar",
    "ax_pos",
    "ax_register",
    "ax_calque",
    "ax_consistency",
    "ax_pedagogical",
    "ax_ui",
]
AXIS_STATES = {"pass", "flag"}
DISPOSITIONS = {"P0", "P1", "P2", "clean-candidate"}
DEFECT_DISPOSITIONS = {"P0", "P1", "P2"}
CONFIDENCE = {"high", "medium", "low"}
REQUIRED_COLS = (
    ["id", "word", "pos", "ua", "definitionUa"]
    + AXES
    + ["disposition", "confidence", "category", "proposed_target", "proposed_value", "rationale"]
)

TOTAL = 919
errors: list[str] = []


def err(msg: str) -> None:
    errors.append(msg)


def sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_blob(rev: str, path: str) -> str:
    return subprocess.run(
        ["git", "rev-parse", f"{rev}:{path}"],
        cwd=ROOT, capture_output=True, text=True,
    ).stdout.strip()


def recorded_manifest_sha() -> str | None:
    for line in REPORT.read_text(encoding="utf-8").splitlines():
        if "Manifest SHA-256:" in line:
            return line.split("`")[1]
    return None


def check_manifest() -> dict[str, int]:
    """Regenerate the manifest and confirm it matches the committed bytes + SHA."""
    committed = MANIFEST.read_bytes()
    subprocess.run(
        [sys.executable, "scripts/qa/r2_pass_b_manifest.py"],
        cwd=ROOT, capture_output=True, text=True, check=True,
    )
    if MANIFEST.read_bytes() != committed:
        err("manifest is not reproducible: regeneration changed the bytes")
    sha = sha256_of(MANIFEST)
    rec = recorded_manifest_sha()
    if rec != sha:
        err(f"manifest SHA-256 mismatch: report={rec} actual={sha}")
    id_to_chunk: dict[str, int] = {}
    with MANIFEST.open(encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh):
            id_to_chunk[row["id"]] = int(row["chunk"])
    if len(id_to_chunk) != TOTAL:
        err(f"manifest holds {len(id_to_chunk)} ids, expected {TOTAL}")
    return id_to_chunk


def token_match(rationale: str, word: str, ua: str) -> bool:
    """Affirmative row-specificity: rationale references this row's own content."""
    low = rationale.lower()
    if word and word.lower() in low:
        return True
    for tok in ua.replace("/", " ").replace(",", " ").replace(";", " ").split():
        tok = tok.strip().lower()
        if len(tok) >= 3 and tok in low:
            return True
    return False


def check_chunk(chunk: int, path: Path, id_to_chunk: dict[str, int]) -> set[str]:
    with path.open(encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        missing_cols = [c for c in REQUIRED_COLS if c not in (reader.fieldnames or [])]
        if missing_cols:
            err(f"chunk {chunk}: missing columns {missing_cols}")
            return set()
        rows = list(reader)

    seen: set[str] = set()
    clean_rationales: dict[str, str] = {}
    for r in rows:
        sid = r["id"]
        if sid in seen:
            err(f"chunk {chunk}: duplicate id {sid}")
        seen.add(sid)
        if id_to_chunk.get(sid) != chunk:
            err(f"chunk {chunk}: id {sid} is not assigned to this chunk by manifest")

        for ax in AXES:
            if r[ax] not in AXIS_STATES:
                err(f"{sid}: axis {ax}={r[ax]!r} invalid (need pass/flag)")
        disp = r["disposition"]
        if disp not in DISPOSITIONS:
            err(f"{sid}: disposition {disp!r} invalid")
        if r["confidence"] not in CONFIDENCE:
            err(f"{sid}: confidence {r['confidence']!r} invalid")
        rationale = (r["rationale"] or "").strip()
        if len(rationale) < 12:
            err(f"{sid}: rationale too short / empty")
        if not token_match(rationale, r["word"], r["ua"]):
            err(f"{sid}: rationale lacks affirmative row-specific reference")

        flagged = [ax for ax in AXES if r[ax] == "flag"]
        if disp in DEFECT_DISPOSITIONS:
            if not flagged:
                err(f"{sid}: {disp} defect flags no axis")
            for field in ("category", "proposed_target", "proposed_value"):
                if not (r[field] or "").strip():
                    err(f"{sid}: {disp} defect missing {field}")
            if r["proposed_target"] and r["proposed_target"] not in {"ua", "definitionUa", "both"}:
                err(f"{sid}: proposed_target {r['proposed_target']!r} invalid")
        else:  # clean-candidate
            if flagged:
                err(f"{sid}: clean-candidate must not flag axes {flagged}")
            for field in ("category", "proposed_target", "proposed_value"):
                if (r[field] or "").strip():
                    err(f"{sid}: clean-candidate must not carry {field}")
            clean_rationales[sid] = rationale

    # Anti-synthesis: clean rationales must be materially distinct, not a template.
    vals = list(clean_rationales.values())
    if vals and len(set(vals)) < len(vals):
        dupes = {v for v in vals if vals.count(v) > 1}
        err(f"chunk {chunk}: {len(dupes)} clean rationale(s) reused verbatim (synthesized?)")
    return seen


def main() -> int:
    if not MANIFEST.exists() or not REPORT.exists():
        print("FAIL: manifest/report missing", file=sys.stderr)
        return 1
    id_to_chunk = check_manifest()

    # Blob integrity: learner content and the accepted-floor-bearing intake.
    vocab_now = git_blob("HEAD", "web/vocabulary.js")
    if vocab_now != EXPECTED_VOCAB_BLOB:
        err(f"learner vocabulary.js blob changed: {vocab_now} != {EXPECTED_VOCAB_BLOB}")
    if git_blob("HEAD", "docs/G4A_RESIDUAL_AUDIT_R2_INTAKE.csv") != git_blob(
        BASELINE, "docs/G4A_RESIDUAL_AUDIT_R2_INTAKE.csv"
    ):
        err("Part-1 intake (accepted-floor artifact) changed from baseline")

    present = {c: p for c, p in CHUNK_FILES.items() if p.exists()}
    covered: set[str] = set()
    for c, path in present.items():
        covered |= check_chunk(c, path, id_to_chunk)

    manifest_ids = set(id_to_chunk)
    stray = covered - manifest_ids
    if stray:
        err(f"judged ids not in manifest: {sorted(stray)[:5]} ...")

    all_present = len(present) == 4
    if all_present and covered != manifest_ids:
        missing = manifest_ids - covered
        err(f"full coverage required but {len(missing)} ids unjudged")

    print(f"chunks present: {sorted(present)}")
    print(f"rows judged: {len(covered)} / {TOTAL}")
    if errors:
        print(f"\nFAIL — {len(errors)} violation(s):", file=sys.stderr)
        for e in errors[:60]:
            print(f"  - {e}", file=sys.stderr)
        return 1
    status = "COMPLETE" if all_present else "PARTIAL (honest, chunks pending)"
    print(f"PASS — structural validation clean; coverage {status}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
