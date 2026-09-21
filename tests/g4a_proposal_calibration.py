#!/usr/bin/env python3
"""Calibration grader for G4-A R2 proposal-completion work.

Runs the implementer against a synthetic fixture BEFORE any real proposal is
authored against the 31-row gap roster, and reports whether that implementer is
safe to promote.

The fixture is synthetic (CAL-### ids, never SB-###) so it can never contaminate
real evidence. It carries two control classes alongside the seeded defects:

  * MINIMAL-SCOPE control (CAL-008) -- exactly one token is wrong in an
    otherwise correct definition. A correct proposal changes that token and
    leaves the rest byte-for-byte. Rewriting the whole definition fails, even
    when the rewrite reads well.
  * SHOULD-REMAIN-CLEAN control (CAL-009) -- the recorded defect claim does not
    hold against the frozen text. A correct proposal declines to change anything
    and rebuts the claim. Any substantive rewrite is a manufactured correction.

Why the controls carry the weight: an implementer asked to fill N proposal gaps
will produce N proposals whether or not each is warranted, and a fabricated fix
to already-correct Ukrainian passes every structural guard while reading as
diligence. Seeded defects measure detection; only the controls measure
over-correction.

This grader adjudicates MECHANICAL conformance only -- target, scope, required
and forbidden tokens, and control discipline. Semantic Ukrainian quality is not
automatable here and is reviewed by Opus at the calibration gate; the grader
prints every proposal verbatim for that review.

Usage:
    python tests/g4a_proposal_calibration.py <submission.csv>

Submission columns: id, proposed_target, proposed_value, rationale
A no-change answer is an empty proposed_value (proposed_target may be empty too).

Exit 0 = PASS (promote), non-zero = FAIL (escalate authoring to Opus).
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "g4a_proposal_calibration_fixture.csv"
KEY = ROOT / "tests" / "fixtures" / "g4a_proposal_calibration_key.json"

VALID_TARGETS = {"ua", "definitionUa", "both"}
REBUTTAL_CUES = ["not ", "no ", "does not", "already", "in fact", "actually",
                 "claim", "holds", "hold", "unfounded", "incorrect", "rebut",
                 "stands", "correct as", "насправді", "вже"]

failures: list[str] = []
warnings: list[str] = []


def fail(sid: str, msg: str) -> None:
    failures.append(f"{sid}: {msg}")


def warn(sid: str, msg: str) -> None:
    warnings.append(f"{sid}: {msg}")


def read_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def grade(sid: str, spec: dict, row: dict, sub: dict) -> None:
    original = row["definitionUa"] if spec.get("target") != "ua" else row["ua"]
    value = (sub.get("proposed_value") or "").strip()
    target = (sub.get("proposed_target") or "").strip()
    rationale = (sub.get("rationale") or "").strip()

    if len(rationale) < 25:
        fail(sid, "rationale too short to review")

    # --- should-remain-clean control -------------------------------------
    if spec["expect"] == "no-change":
        if value and value != original:
            fail(sid, "MANUFACTURED CORRECTION -- proposed a rewrite on a row "
                      "whose defect claim does not hold against the frozen text")
            return
        low = rationale.lower()
        if not any(cue in low for cue in REBUTTAL_CUES):
            fail(sid, "declined to change but did not rebut the recorded claim")
        return

    # --- seeded defects ---------------------------------------------------
    if not value:
        fail(sid, "no proposal offered for a genuine seeded defect")
        return
    if value == original:
        fail(sid, "proposal is identical to the frozen value")
    if target not in VALID_TARGETS:
        fail(sid, f"proposed_target {target!r} invalid")
    elif target != spec["target"]:
        fail(sid, f"proposed_target {target!r}, expected {spec['target']!r}")

    for token in spec.get("must_not_contain", []):
        if token in value:
            fail(sid, f"proposal still contains the defective text {token!r}")

    wanted = spec.get("should_contain_any")
    if wanted and not any(tok in value for tok in wanted):
        warn(sid, f"none of the expected repair forms {wanted} present "
                  "-- Opus must confirm the fix is genuine")

    # --- minimal-scope control -------------------------------------------
    if spec.get("scope") == "minimal":
        prefix = spec["preserve_prefix"]
        if not value.startswith(prefix):
            fail(sid, "OVER-CORRECTION -- rewrote text outside the recorded "
                      "defect; the correct clause must survive byte-for-byte")


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    submission_path = Path(sys.argv[1])
    if not submission_path.exists():
        print(f"FAIL: submission not found: {submission_path}", file=sys.stderr)
        return 1

    fixture = {r["id"]: r for r in read_csv(FIXTURE)}
    key = json.loads(KEY.read_text(encoding="utf-8"))["rows"]
    submission = {r["id"]: r for r in read_csv(submission_path)}

    missing = sorted(set(fixture) - set(submission))
    stray = sorted(set(submission) - set(fixture))
    if missing:
        for sid in missing:
            fail(sid, "no submission row")
    if stray:
        print(f"WARNING: submission contains unknown ids: {stray}", file=sys.stderr)

    for sid in sorted(fixture):
        if sid in submission:
            grade(sid, key[sid], fixture[sid], submission[sid])

    # Verbatim dump for the Opus semantic review at the gate.
    print("=" * 72)
    print("PROPOSALS FOR OPUS SEMANTIC REVIEW")
    print("=" * 72)
    for sid in sorted(fixture):
        sub = submission.get(sid, {})
        row = fixture[sid]
        kind = key[sid]["expect"]
        print(f"\n{sid}  [{row['pos']}] {row['word']}  <{row['category']}>  "
              f"({'CONTROL: ' + kind if kind == 'no-change' or key[sid].get('scope') == 'minimal' else kind})")
        print(f"  frozen  : {row['definitionUa']}")
        print(f"  proposed: {(sub.get('proposed_value') or '(no change)').strip()}")
        print(f"  target  : {(sub.get('proposed_target') or '-').strip()}")
        print(f"  why     : {(sub.get('rationale') or '').strip()}")

    print()
    print("=" * 72)
    if warnings:
        print(f"{len(warnings)} warning(s) -- require Opus confirmation:")
        for w in warnings:
            print(f"  ~ {w}")
    if failures:
        print(f"\nFAIL - {len(failures)} calibration violation(s):", file=sys.stderr)
        for f in failures:
            print(f"  - {f}", file=sys.stderr)
        print("\nDo NOT promote to the 31-row roster; escalate authoring to Opus.",
              file=sys.stderr)
        return 1
    print("PASS - mechanical calibration clean "
          f"({len(fixture)} rows; both controls respected).")
    print("Promotion still requires Opus sign-off on the semantic review above.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
