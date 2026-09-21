#!/usr/bin/env python3
"""Deterministic validator for the G4-A R2 Phase-1 P1 manifest/backlog/gap set.

Independently re-derives the P1 set, the P2 backlog, and the Stage A/B split
from the two canonical committed sources (the accepted floor intake and the
327-row A/B reconciliation chunks) and asserts the committed
`docs/G4A_R2_P1_MANIFEST.csv`, `docs/G4A_R2_P2_BACKLOG.csv`, and
`docs/G4A_R2_P1_PROPOSAL_GAPS.csv` match that recomputation exactly.

Every check below fails closed (hard assertion / non-zero exit), matching
the project's established validator convention
(`tests/g4a_r2_reconciliation.py`, `tests/g4a_p1_closeout_accounting.py`) —
no notes-only or print-only checks.

**By design, exactly one subtest is expected to fail: the proposal-
completeness guard** (`test_proposal_completeness_guard`), because gap rows
genuinely exist in the committed data (see
`docs/G4A_R2_P1_PROPOSAL_GAPS.md`). That guard does NOT assert any
preselected numeric gap count; it asserts zero gaps, which is the
proposal-completeness bar this Phase-1 inventory has not yet cleared. Every
other check must pass. If more than one check fails, or the completeness
guard passes, that is a bug in the artifacts, not an acceptable result.
"""
from __future__ import annotations

import csv
import hashlib
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"

INTAKE = DOCS / "G4A_RESIDUAL_AUDIT_R2_INTAKE.csv"
CHUNKS = [DOCS / f"G4A_R2_RECON_CHUNK{c}.csv" for c in (1, 2, 3)]
CONSENSUS = DOCS / "G4A_R2_RECON_CONSENSUS_CLEAN.csv"
MANIFEST = DOCS / "G4A_R2_P1_MANIFEST.csv"
BACKLOG = DOCS / "G4A_R2_P2_BACKLOG.csv"
GAPS_CSV = DOCS / "G4A_R2_P1_PROPOSAL_GAPS.csv"
BUILDER = ROOT / "scripts" / "qa" / "r2_p1_phase1_build.py"

BASELINE_REF = "f34f109ae5b8564e7fa10317c167a6ca728c52fd"  # PR #8 base branch head SHA (claude/slack-session-62m83z)
EXPECTED_VOCAB_BLOB = "1c184e84e5c63e3a9f8e386af13787664a23bd66"
EXPECTED_FLOOR_BLOB = "7f34785e379ac76ee5341d4f65f33b123d57bc43"
STAGE_A_SIZE = 250
STAGE_B_SIZE = 15
INVALID_TOKENS = {"", "n/a", "na", "none", "null", "tbd", "-"}

LEARNER_FACING_PREFIXES = ("web/",)

results: list[tuple[str, bool, str]] = []


def record(name: str, ok: bool, detail: str = "") -> None:
    results.append((name, ok, detail))


def norm(v: str | None) -> str:
    return (v or "").strip()


def is_invalid(v: str | None) -> bool:
    return norm(v).lower() in INVALID_TOKENS


def git_blob(rev: str, path: str) -> str:
    return subprocess.run(
        ["git", "rev-parse", f"{rev}:{path}"], cwd=ROOT,
        capture_output=True, text=True,
    ).stdout.strip()


def git_show(rev: str, path: str) -> str | None:
    p = subprocess.run(
        ["git", "show", f"{rev}:{path}"], cwd=ROOT,
        capture_output=True, text=True,
    )
    return p.stdout if p.returncode == 0 else None


def git_diff_names(rev_a: str, rev_b: str) -> list[str]:
    p = subprocess.run(
        ["git", "diff", "--name-only", rev_a, rev_b], cwd=ROOT,
        capture_output=True, text=True, check=True,
    )
    return [ln for ln in p.stdout.splitlines() if ln.strip()]


def load_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sha256_of_ids(ids: list[str]) -> str:
    return hashlib.sha256("\n".join(ids).encode("utf-8")).hexdigest()


def recompute_universe() -> dict:
    intake_rows = load_csv(INTAKE)
    chunk_rows: list[dict] = []
    for c in CHUNKS:
        chunk_rows.extend(load_csv(c))
    consensus_ids = {r["id"] for r in load_csv(CONSENSUS)}

    assert len(intake_rows) == 1007, f"intake has {len(intake_rows)} rows"
    assert len({r["id"] for r in intake_rows}) == 1007, "intake has duplicate ids"
    assert len(chunk_rows) == 327, f"chunks total {len(chunk_rows)} rows"
    assert len({r["id"] for r in chunk_rows}) == 327, "chunk rows have duplicate ids"

    needs_human_ids = {r["id"] for r in intake_rows if r["disposition"] == "needs-human"}
    chunk_ids = {r["id"] for r in chunk_rows}
    assert needs_human_ids == (chunk_ids | consensus_ids), (
        "intake needs-human set != chunk ids | consensus-clean ids"
    )
    assert not (chunk_ids & consensus_ids), "chunk ids overlap consensus-clean ids"

    floor_p1 = [r for r in intake_rows if r["disposition"] == "P1"]
    floor_p2 = [r for r in intake_rows if r["disposition"] == "P2"]
    for r in intake_rows:
        assert r["disposition"] in ("P1", "P2", "needs-human"), (
            f"{r['id']}: unexpected floor disposition {r['disposition']!r}"
        )

    chunk_p1 = [r for r in chunk_rows if r["final_disposition"] == "P1"]
    chunk_p2 = [r for r in chunk_rows if r["final_disposition"] == "P2"]

    p1_ids = sorted([r["id"] for r in floor_p1] + [r["id"] for r in chunk_p1])
    assert len(p1_ids) == len(set(p1_ids)), "floor-P1 and reconciled-P1 overlap"

    p2_ids = sorted([r["id"] for r in floor_p2] + [r["id"] for r in chunk_p2])
    assert len(p2_ids) == len(set(p2_ids)), "floor-P2 and reconciled-P2 overlap"
    assert not (set(p1_ids) & set(p2_ids)), "a P1 id is also counted as P2"

    proposal_by_id: dict[str, tuple[str, str]] = {}
    for r in floor_p1 + chunk_p1:
        proposal_by_id[r["id"]] = (r["proposed_target"], r["proposed_value"])

    return {
        "p1_ids": p1_ids, "p2_ids": p2_ids,
        "proposal_by_id": proposal_by_id,
        "floor_p1": len(floor_p1), "floor_p2": len(floor_p2),
        "chunk_p1": len(chunk_p1), "chunk_p2": len(chunk_p2),
    }


def test_universe_consistency() -> None:
    u = recompute_universe()
    assert len(u["p1_ids"]) == 265, f"computed P1 total is {len(u['p1_ids'])}, not 265"
    assert len(u["p2_ids"]) == 149, f"computed P2 total is {len(u['p2_ids'])}, not 149"
    record("universe_consistency", True,
           f"P1={len(u['p1_ids'])} (floor {u['floor_p1']} + reconciled {u['chunk_p1']}); "
           f"P2={len(u['p2_ids'])} (floor {u['floor_p2']} + reconciled {u['chunk_p2']})")


def test_manifest_matches_recomputation() -> None:
    u = recompute_universe()
    p1_ids_sorted = sorted(u["p1_ids"])
    manifest_rows = load_csv(MANIFEST)
    manifest_ids = [r["id"] for r in manifest_rows]

    assert manifest_ids == p1_ids_sorted, "manifest id order/set does not match recomputed P1 set"
    assert len(manifest_ids) == len(set(manifest_ids)), "manifest has duplicate ids"

    for i, r in enumerate(manifest_rows):
        expected_stage = "A" if i < STAGE_A_SIZE else "B"
        assert r["stage"] == expected_stage, (
            f"{r['id']}: stage {r['stage']!r} != expected {expected_stage!r} "
            f"(index {i}; Stage A must be exactly the first {STAGE_A_SIZE}, "
            f"Stage B exactly the last {STAGE_B_SIZE})"
        )
        pt, pv = u["proposal_by_id"][r["id"]]
        assert norm(r["proposed_target"]) == norm(pt), f"{r['id']}: proposed_target drifted from source"
        assert norm(r["proposed_value"]) == norm(pv), f"{r['id']}: proposed_value drifted from source"
        expected_gap = "true" if (is_invalid(pt) or is_invalid(pv)) else "false"
        assert r["gap"] == expected_gap, f"{r['id']}: gap flag {r['gap']!r} != expected {expected_gap!r}"

    stage_a = [r["id"] for r in manifest_rows if r["stage"] == "A"]
    stage_b = [r["id"] for r in manifest_rows if r["stage"] == "B"]
    assert len(stage_a) == STAGE_A_SIZE, f"Stage A has {len(stage_a)} ids, expected {STAGE_A_SIZE}"
    assert len(stage_b) == STAGE_B_SIZE, f"Stage B has {len(stage_b)} ids, expected {STAGE_B_SIZE}"
    record("manifest_matches_recomputation", True,
           f"265/265 ids match; Stage A={len(stage_a)}, Stage B={len(stage_b)}")


def test_backlog_matches_recomputation() -> None:
    u = recompute_universe()
    p2_ids_sorted = sorted(u["p2_ids"])
    backlog_rows = load_csv(BACKLOG)
    backlog_ids = [r["id"] for r in backlog_rows]
    assert backlog_ids == p2_ids_sorted, "backlog id order/set does not match recomputed P2 set"
    assert len(backlog_ids) == len(set(backlog_ids)), "backlog has duplicate ids"
    assert not (set(backlog_ids) & set(u["p1_ids"])), "a P1 id leaked into the P2 backlog"
    record("backlog_matches_recomputation", True, f"{len(backlog_ids)}/149 ids match")


def test_gap_artifact_self_consistent() -> None:
    """Gap artifact must equal the manifest's own gap='true' rows. No fixed count asserted."""
    manifest_rows = load_csv(MANIFEST)
    manifest_gap_ids = sorted(r["id"] for r in manifest_rows if r["gap"] == "true")
    gap_rows = load_csv(GAPS_CSV)
    gap_ids = sorted(r["id"] for r in gap_rows)
    assert gap_ids == manifest_gap_ids, (
        "gap artifact ids != manifest gap='true' ids "
        f"(artifact has {len(gap_ids)}, manifest flags {len(manifest_gap_ids)})"
    )
    assert len(gap_ids) == len(set(gap_ids)), "gap artifact has duplicate ids"
    record("gap_artifact_self_consistent", True,
           f"gap artifact matches manifest exactly ({len(gap_ids)} ids)")


def test_builder_reproducibility() -> None:
    before = {p: p.read_bytes() for p in (MANIFEST, BACKLOG, GAPS_CSV)}
    proc = subprocess.run([sys.executable, str(BUILDER)], cwd=ROOT,
                          capture_output=True, text=True)
    assert proc.returncode == 0, f"builder exited {proc.returncode}: {proc.stderr}"
    for p, orig in before.items():
        assert p.read_bytes() == orig, f"{p.name} is not byte-reproducible from the builder"
    record("builder_reproducibility", True, "manifest/backlog/gaps regenerate byte-identically")


def test_protected_blobs_unchanged() -> None:
    assert git_blob("HEAD", "web/vocabulary.js") == EXPECTED_VOCAB_BLOB, (
        "learner-facing web/vocabulary.js blob changed"
    )
    assert git_blob("HEAD", "docs/G4A_RESIDUAL_AUDIT_R2_INTAKE.csv") == EXPECTED_FLOOR_BLOB, (
        "accepted 88-row floor artifact changed"
    )
    merge_base = subprocess.run(
        ["git", "merge-base", "HEAD", BASELINE_REF], cwd=ROOT,
        capture_output=True, text=True,
    )
    assert merge_base.returncode == 0, f"could not resolve merge-base with {BASELINE_REF}"
    base = merge_base.stdout.strip()
    assert git_blob("HEAD", "web/vocabulary.js") == git_blob(base, "web/vocabulary.js"), (
        "web/vocabulary.js diverged from PR #8 base branch"
    )
    record("protected_blobs_unchanged", True,
           "web/vocabulary.js and the 88-row floor are byte-identical to baseline/HEAD")


def test_no_other_learner_facing_paths_touched() -> None:
    merge_base = subprocess.run(
        ["git", "merge-base", "HEAD", BASELINE_REF], cwd=ROOT,
        capture_output=True, text=True,
    )
    assert merge_base.returncode == 0, f"could not resolve merge-base with {BASELINE_REF}"
    base = merge_base.stdout.strip()
    changed = git_diff_names(base, "HEAD")
    offenders = [f for f in changed if f.startswith(LEARNER_FACING_PREFIXES)]
    assert not offenders, f"learner-facing paths changed vs base: {offenders}"
    record("no_other_learner_facing_paths_touched", True,
           f"{len(changed)} files changed vs base, none under web/")


def test_proposal_completeness_guard() -> None:
    """Expected to FAIL: gap rows genuinely exist. See docs/G4A_R2_P1_PROPOSAL_GAPS.md."""
    gap_rows = load_csv(GAPS_CSV)
    assert len(gap_rows) == 0, (
        f"proposal-completeness guard: {len(gap_rows)} P1 row(s) have an "
        "empty/invalid proposed_target or proposed_value "
        "(see docs/G4A_R2_P1_PROPOSAL_GAPS.md for the full sorted list and "
        "derivation; this is the one check this validator expects to fail "
        "at Phase-1 — no proposal drafting has occurred)"
    )
    record("proposal_completeness_guard", True, "0 gap rows")


CHECKS = [
    test_universe_consistency,
    test_manifest_matches_recomputation,
    test_backlog_matches_recomputation,
    test_gap_artifact_self_consistent,
    test_builder_reproducibility,
    test_protected_blobs_unchanged,
    test_no_other_learner_facing_paths_touched,
    test_proposal_completeness_guard,
]


def main() -> int:
    failed = 0
    for check in CHECKS:
        name = check.__name__[5:] if check.__name__.startswith("test_") else check.__name__
        try:
            check()
        except AssertionError as e:
            record(name, False, str(e))
            failed += 1
    for name, ok, detail in results:
        print(f"{'PASS' if ok else 'FAIL'} — {name}: {detail}")
    print(f"\n{len(results) - failed}/{len(results)} passed, {failed} failed")
    if failed == 1 and not next(ok for n, ok, _ in results if n == "proposal_completeness_guard"):
        print("Expected outcome: exactly one failure (proposal_completeness_guard).")
        return 1
    if failed == 0:
        print("UNEXPECTED: proposal_completeness_guard passed — gap list is empty; re-verify.")
        return 1
    print(f"UNEXPECTED: {failed} failure(s), not exactly the expected one.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
