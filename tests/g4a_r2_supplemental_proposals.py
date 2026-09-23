#!/usr/bin/env python3
"""Guard for the G4-A R2 supplemental proposal-completion artifact.

Fails closed on any of:

  * the artifact is not byte-reproducible from its builder;
  * accepted reconciliation evidence, the Part-1 floor, the gap roster or the
    learner vocabulary blob drifted from canonical head 39d6f918;
  * any authored id is not on the 31-row derived gap roster, or is assigned to
    the wrong batch under the deterministic 10/10/11 split;
  * any row's frozen word/pos/ua/definitionUa disagrees with the gap roster;
  * an evidence_quote is not an EXACT substring of that row's frozen ua or
    definitionUa;
  * a correction is not SUBSTANTIVE -- empty, identical to the frozen value, or
    differing from it only in whitespace;
  * each populated proposal field changes its corresponding frozen field;
  * a no-change answer carries a proposed value, or fails to rebut the recorded
    claim;
  * two rows share a rationale after whitespace and case normalization;
  * rationale is too short, or confidence is outside {high, medium, low};
  * when all three batches are present, coverage is not exactly 31/31.

The substantiveness and duplicate-rationale checks exist because an implementer
asked to fill N proposal gaps will produce N proposals whether or not each is
warranted. Structural validity is not evidence of a real correction.

Partial coverage is expected: batches land one at a time and are reviewed before
the next is authored.
"""
from __future__ import annotations

import csv
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"

CANONICAL_HEAD = "39d6f918c7087d3616acc9654eecfaf5219aefc4"
EXPECTED_VOCAB_BLOB = "1c184e84e5c63e3a9f8e386af13787664a23bd66"
EXPECTED_FLOOR_BLOB = "7f34785e379ac76ee5341d4f65f33b123d57bc43"

FROZEN_PATHS = [
    "web/vocabulary.js",
    "docs/G4A_RESIDUAL_AUDIT_R2_INTAKE.csv",
    "docs/G4A_R2_RECON_CHUNK1.csv",
    "docs/G4A_R2_RECON_CHUNK2.csv",
    "docs/G4A_R2_RECON_CHUNK3.csv",
    "docs/G4A_R2_RECON_CONSENSUS_CLEAN.csv",
    "docs/G4A_R2_RECON_ROSTER.csv",
    "docs/G4A_R2_RECON_SUMMARY.md",
    "docs/G4A_R2_SEED_20260914_REVIEW.csv",
]

ARTIFACT = DOCS / "G4A_R2_SUPPLEMENTAL_PROPOSALS.csv"
GAPS = DOCS / "G4A_R2_PROPOSAL_GAP_INVENTORY.csv"
BATCH_DIR = DOCS / "batches"

EXPECTED_GAPS = 31
BATCH_SIZES = {1: 10, 2: 10, 3: 11}
COLS = ["id", "batch", "word", "pos", "ua", "definitionUa", "category",
        "existing_rationale", "evidence_quote", "proposed_ua",
        "proposed_definitionUa", "rationale", "confidence", "answer_kind"]
CONFIDENCE = {"high", "medium", "low"}
REBUTTAL_CUES = ["not ", "no ", "does not", "already", "in fact", "actually",
                 "claim", "hold", "unfounded", "incorrect", "rebut", "refut",
                 "stands", "correct as", "насправді", "вже"]

errors: list[str] = []


def err(msg: str) -> None:
    errors.append(msg)


def read_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames != COLS and path == ARTIFACT:
            err("combined artifact header does not use explicit proposal columns")
        rows = list(reader)
        if any(None in row or any(value is None for value in row.values()) for row in rows):
            err(f"{path.name}: malformed CSV row")
        return rows


def git_blob(rev: str, path: str) -> str:
    return subprocess.run(["git", "rev-parse", f"{rev}:{path}"], cwd=ROOT,
                          capture_output=True, text=True).stdout.strip()


def stable_key(sid: str) -> tuple[str, int, str]:
    prefix, _, num = sid.partition("-")
    return (prefix, int(num), sid) if num.isdigit() else (prefix, 1 << 30, sid)


def norm(text: str) -> str:
    return " ".join(text.split())


def check_frozen() -> None:
    for path in FROZEN_PATHS:
        head, canon = git_blob("HEAD", path), git_blob(CANONICAL_HEAD, path)
        if not canon:
            err(f"{path}: missing at canonical head")
        elif head != canon or git_blob_worktree(path) != canon:
            err(f"{path}: drifted from canonical head")
    if git_blob("HEAD", "web/vocabulary.js") != EXPECTED_VOCAB_BLOB:
        err("learner web/vocabulary.js blob changed")
    if git_blob("HEAD", "docs/G4A_RESIDUAL_AUDIT_R2_INTAKE.csv") != EXPECTED_FLOOR_BLOB:
        err("accepted 88-row floor blob changed")


def git_blob_worktree(path: str) -> str:
    return subprocess.run(["git", "hash-object", path], cwd=ROOT,
                          capture_output=True, text=True).stdout.strip()


def check_reproducible() -> None:
    if not ARTIFACT.exists():
        err("artifact missing; run scripts/qa/r2_supplemental_proposals.py")
        return
    before = ARTIFACT.read_bytes()
    proc = subprocess.run([sys.executable, "scripts/qa/r2_supplemental_proposals.py"],
                          cwd=ROOT, capture_output=True, text=True)
    if proc.returncode != 0:
        err(f"builder failed: {(proc.stderr or proc.stdout).strip()[:300]}")
        return
    after = ARTIFACT.read_bytes()
    if after != before:
        err("artifact is not byte-reproducible from its builder")
    if b"\r\n" in after:
        err("artifact contains CRLF")


def batch_assignment(gap_ids: list[str]) -> dict[str, int]:
    ordered = sorted(gap_ids, key=stable_key)
    out: dict[str, int] = {}
    cursor = 0
    for batch, size in sorted(BATCH_SIZES.items()):
        for sid in ordered[cursor:cursor + size]:
            out[sid] = batch
        cursor += size
    return out


def main() -> int:
    check_frozen()
    check_reproducible()
    if not ARTIFACT.exists() or not GAPS.exists():
        print("FAIL: artifact or gap roster missing", file=sys.stderr)
        return 1

    gaps = {r["id"]: r for r in read_csv(GAPS)}
    if len(gaps) != EXPECTED_GAPS:
        err(f"gap roster holds {len(gaps)} rows, expected {EXPECTED_GAPS}")
    assignment = batch_assignment(list(gaps))

    rows = read_csv(ARTIFACT)
    seen: set[str] = set()
    rationales: dict[str, str] = {}

    for row in rows:
        sid = row["id"]
        if sid in seen:
            err(f"{sid}: duplicate row")
        seen.add(sid)
        if sid not in gaps:
            err(f"{sid}: not on the 31-row gap roster")
            continue
        g = gaps[sid]

        if row["batch"] != str(assignment[sid]):
            err(f"{sid}: batch {row['batch']}, expected {assignment[sid]}")
        for field in ("word", "pos", "ua", "definitionUa", "category", "existing_rationale"):
            if row[field] != g[field]:
                err(f"{sid}: {field} disagrees with the frozen gap roster")

        quote = (row["evidence_quote"] or "").strip()
        if len(quote) < 3 or (quote not in g["ua"] and quote not in g["definitionUa"]):
            err(f"{sid}: evidence_quote is not an exact substring of the frozen text")

        rationale = (row["rationale"] or "").strip()
        if len(rationale) < 25:
            err(f"{sid}: rationale too short")
        rationale_key = norm(rationale).casefold()
        if rationale_key in rationales:
            err(f"{sid}: rationale duplicates {rationales[rationale_key]}")
        else:
            rationales[rationale_key] = sid

        if row["confidence"] not in CONFIDENCE:
            err(f"{sid}: confidence {row['confidence']!r} invalid")

        proposals = {"ua": (row["proposed_ua"] or "").strip(),
                     "definitionUa": (row["proposed_definitionUa"] or "").strip()}
        kind = row["answer_kind"]

        if kind == "correction":
            if not any(proposals.values()):
                err(f"{sid}: correction carries no proposed value")
            for field, value in proposals.items():
                if value and norm(value) == norm(g[field]):
                    err(f"{sid}: proposal for {field} does not substantively change frozen text")
        elif kind == "no-change":
            if any(proposals.values()):
                err(f"{sid}: no-change answer carries a proposal")
            low = rationale.lower()
            if not any(cue in low for cue in REBUTTAL_CUES):
                err(f"{sid}: no-change answer does not rebut the recorded claim")
        else:
            err(f"{sid}: answer_kind {kind!r} invalid")

    present = [b for b in sorted(BATCH_SIZES)
               if (BATCH_DIR / f"G4A_R2_PROPOSAL_BATCH{b}.csv").exists()]
    complete = len(present) == len(BATCH_SIZES)
    if complete and seen != set(gaps):
        err(f"full coverage required but {len(set(gaps) - seen)} gap ids unauthored")
    for batch in present:
        got = sum(1 for r in rows if r["batch"] == str(batch))
        if got != BATCH_SIZES[batch]:
            err(f"batch {batch}: {got} rows, expected {BATCH_SIZES[batch]}")
    if complete:
        two_field = [r["id"] for r in rows if r["proposed_ua"] and r["proposed_definitionUa"]]
        if two_field != ["SB-1590"]:
            err(f"two-field rows {two_field}, expected only SB-1590")
        if sum(r["answer_kind"] == "correction" for r in rows) != 31:
            err("complete artifact must contain 31 corrections")

    print(f"batches present: {present}")
    print(f"rows authored  : {len(seen)} / {EXPECTED_GAPS}")
    if errors:
        print(f"\nFAIL - {len(errors)} violation(s):", file=sys.stderr)
        for e in errors[:40]:
            print(f"  - {e}", file=sys.stderr)
        return 1
    print("PASS - proposals substantive, ids on roster, batches correct, "
          "accepted evidence byte-frozen; coverage "
          + ("COMPLETE" if complete else "PARTIAL (batches pending)"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
