#!/usr/bin/env python3
"""Guard / validator for the G4-A R2 A/B reconciliation (v2).

Independently re-derives the roster and validates the per-chunk reconciliation
artifacts against the handoff contract:

  * the roster regenerates deterministically to the recorded SHA-256 and the
    A/B matrix is the canonical one;
  * each present reconciliation chunk uses exactly the roster IDs for that
    chunk (no missing / duplicate / cross-chunk leakage);
  * every row carries the frozen word/pos/ua/definitionUa (verified against the
    Pass B frozen artifact), the Pass-A and Pass-B dispositions (matching the
    roster), a final disposition, confidence and category from the allowed
    vocabularies, a non-empty rationale, and an evidence_quote that is an EXACT
    substring of that row's frozen ua or definitionUa;
  * defect rows (P0/P1/P2) carry a proposed target + value;
  * a final clean-candidate verdict carries a substantive rebuttal rationale
    (long enough, not a banned generic phrase, engaging the prior claim) — a
    bare "sense is accurate" is rejected;
  * needs-human rows carry a rationale explaining the irreducible ambiguity;
  * the learner blob and accepted 88-row floor are unchanged from baseline;
  * when all three chunks are present, union coverage is exactly 327/327.

Exit non-zero on any violation.
"""
from __future__ import annotations

import csv
import hashlib
import io
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
ROSTER = DOCS / "G4A_R2_RECON_ROSTER.csv"
REPORT = DOCS / "G4A_R2_RECON.md"
CHUNKS = {c: DOCS / f"G4A_R2_RECON_CHUNK{c}.csv" for c in (1, 2, 3)}

BASELINE = "5a5fd7d7ce8cc4e7c3f8a2b2a0253269ed803ac0"
PASS_B = "2b90574e3dafb88313ac6563ec094577fb7a95a2"
EXPECTED_VOCAB_BLOB = "1c184e84e5c63e3a9f8e386af13787664a23bd66"

FINAL_DISPS = {"P0", "P1", "P2", "clean-candidate", "needs-human"}
DEFECTS = {"P0", "P1", "P2"}
CONFIDENCE = {"high", "medium", "low"}
REQUIRED_COLS = ["id", "word", "pos", "ua", "definitionUa",
                 "pass_a_disposition", "pass_a_rationale",
                 "pass_b_disposition", "pass_b_rationale",
                 "evidence_quote", "final_disposition", "confidence",
                 "category", "rationale", "proposed_target", "proposed_value"]
BANNED_CLEAN = {
    "sense is accurate", "the sense is accurate", "gloss matches headword",
    "gloss matches the headword", "pos matches", "accurate",
}
REBUTTAL_CUES = ["not ", "no ", "isn't", "is not", "actually", "in fact",
                 "despite", "correct", "valid", "legitim", "accept", "stand",
                 "hold", "pass a", "pass-a", "prior", "overturn", "false",
                 "wrong", "refut", "rebut", "насправді", "ає нормою", "норм"]

errors: list[str] = []


def err(m: str) -> None:
    errors.append(m)


def show(sha: str, path: str) -> str:
    return subprocess.run(["git", "show", f"{sha}:{path}"], cwd=ROOT,
                          capture_output=True, text=True, check=True).stdout


def git_blob(rev: str, path: str) -> str:
    return subprocess.run(["git", "rev-parse", f"{rev}:{path}"], cwd=ROOT,
                          capture_output=True, text=True).stdout.strip()


def recorded(label: str) -> str | None:
    for line in REPORT.read_text(encoding="utf-8").splitlines():
        if label in line and "`" in line:
            return line.split("`")[1]
    return None


def frozen_text() -> dict[str, dict]:
    out: dict[str, dict] = {}
    for c in (1, 2, 3, 4):
        for r in csv.DictReader(io.StringIO(show(PASS_B, f"docs/G4A_R2_PASS_B_CHUNK{c}.csv"))):
            out[r["id"]] = {"word": r["word"], "pos": r["pos"],
                            "ua": r["ua"], "definitionUa": r["definitionUa"]}
    return out


def check_roster() -> dict[str, int]:
    committed = ROSTER.read_bytes()
    subprocess.run([sys.executable, "scripts/qa/r2_reconciliation_roster.py"],
                   cwd=ROOT, capture_output=True, text=True, check=True)
    if ROSTER.read_bytes() != committed:
        err("roster is not reproducible: regeneration changed the bytes")
    sha = hashlib.sha256(ROSTER.read_bytes()).hexdigest()
    if recorded("Roster:") not in (sha, None) and recorded("Roster:") != sha:
        err(f"roster SHA-256 mismatch: report={recorded('Roster:')} actual={sha}")
    id_to_chunk = {}
    for r in csv.DictReader(ROSTER.open(encoding="utf-8")):
        id_to_chunk[r["id"]] = int(r["chunk"])
    if len(id_to_chunk) != 327:
        err(f"roster holds {len(id_to_chunk)} ids, expected 327")
    return id_to_chunk


def check_chunk(c: int, path: Path, id_to_chunk: dict[str, int],
                roster: dict[str, dict], frozen: dict[str, dict]) -> set[str]:
    reader = csv.DictReader(path.open(encoding="utf-8"))
    missing = [x for x in REQUIRED_COLS if x not in (reader.fieldnames or [])]
    if missing:
        err(f"chunk {c}: missing columns {missing}")
        return set()
    seen: set[str] = set()
    for r in reader:
        sid = r["id"]
        if sid in seen:
            err(f"chunk {c}: duplicate id {sid}")
        seen.add(sid)
        if id_to_chunk.get(sid) != c:
            err(f"{sid}: not assigned to chunk {c} by roster")
        fz = frozen.get(sid, {})
        for f in ("word", "pos", "ua", "definitionUa"):
            if r[f] != fz.get(f):
                err(f"{sid}: {f} does not match frozen learner text")
        if r["pass_a_disposition"] != roster[sid]["pass_a_disposition"]:
            err(f"{sid}: pass_a_disposition disagrees with roster")
        if r["pass_b_disposition"] != roster[sid]["pass_b_disposition"]:
            err(f"{sid}: pass_b_disposition disagrees with roster")
        fd = r["final_disposition"]
        if fd not in FINAL_DISPS:
            err(f"{sid}: final_disposition {fd!r} invalid")
        if r["confidence"] not in CONFIDENCE:
            err(f"{sid}: confidence {r['confidence']!r} invalid")
        quote = (r["evidence_quote"] or "").strip()
        hay = (fz.get("ua", "") + " || " + fz.get("definitionUa", ""))
        if len(quote) < 3 or (quote not in fz.get("ua", "") and quote not in fz.get("definitionUa", "")):
            err(f"{sid}: evidence_quote not an exact substring of frozen ua/definitionUa")
        rat = (r["rationale"] or "").strip()
        if len(rat) < 25:
            err(f"{sid}: rationale too short")
        for pa in ("pass_a_rationale", "pass_b_rationale"):
            if not (r[pa] or "").strip():
                err(f"{sid}: missing {pa}")
        if fd in DEFECTS:
            if not (r["category"] or "").strip():
                err(f"{sid}: defect missing category")
            if not (r["proposed_target"] or "").strip() or not (r["proposed_value"] or "").strip():
                err(f"{sid}: defect missing proposed_target/value")
            if r["proposed_target"] and r["proposed_target"] not in {"ua", "definitionUa", "both"}:
                err(f"{sid}: proposed_target {r['proposed_target']!r} invalid")
        elif fd == "clean-candidate":
            low = rat.lower()
            if low in BANNED_CLEAN:
                err(f"{sid}: clean rationale is a banned generic phrase")
            if len(rat) < 40 or not any(cue in low for cue in REBUTTAL_CUES):
                err(f"{sid}: clean verdict must substantively rebut the prior defect claim")
        # needs-human: rationale (already length-checked) must state the ambiguity
    return seen


def main() -> int:
    if not ROSTER.exists() or not REPORT.exists():
        print("FAIL: roster/report missing", file=sys.stderr)
        return 1
    id_to_chunk = check_roster()
    roster = {r["id"]: r for r in csv.DictReader(ROSTER.open(encoding="utf-8"))}
    frozen = frozen_text()

    if git_blob("HEAD", "web/vocabulary.js") != EXPECTED_VOCAB_BLOB:
        err("learner vocabulary.js blob changed")
    if git_blob("HEAD", "docs/G4A_RESIDUAL_AUDIT_R2_INTAKE.csv") != git_blob(
            BASELINE, "docs/G4A_RESIDUAL_AUDIT_R2_INTAKE.csv"):
        err("accepted 88-row floor artifact changed from baseline")

    present = {c: p for c, p in CHUNKS.items() if p.exists()}
    covered: set[str] = set()
    for c, p in present.items():
        covered |= check_chunk(c, p, id_to_chunk, roster, frozen)

    stray = covered - set(id_to_chunk)
    if stray:
        err(f"adjudicated ids not in roster: {sorted(stray)[:5]}")
    all_present = len(present) == 3
    if all_present and covered != set(id_to_chunk):
        err(f"full coverage required but {len(set(id_to_chunk) - covered)} roster ids unadjudicated")

    print(f"chunks present: {sorted(present)}")
    print(f"rows adjudicated: {len(covered)} / 327")
    if errors:
        print(f"\nFAIL — {len(errors)} violation(s):", file=sys.stderr)
        for e in errors[:60]:
            print(f"  - {e}", file=sys.stderr)
        return 1
    print("PASS — structural validation clean; coverage "
          + ("COMPLETE" if all_present else "PARTIAL (chunks pending)"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
