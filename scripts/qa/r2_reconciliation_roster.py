#!/usr/bin/env python3
"""G4-A residual audit R2 — A/B reconciliation, deterministic roster (v2).

Clean restart from canonical GitHub evidence (supersedes the lost, unpublished
ad70bfa/a1eb6e7 execution state — those SHAs are noncanonical and are NOT
referenced or recreated here).

Reads the two FROZEN audit artifacts by exact commit SHA:
  * Pass A: codex/4-g4a-residual-audit-r2 @ f7ddf7b1dadfd91a8126b15c0977873be02f883c
  * Pass B: claude/recent-slack-handoff-a0fx3d @ 2b90574e3dafb88313ac6563ec094577fb7a95a2
whose merge-base is the baseline 5a5fd7d7ce8cc4e7c3f8a2b2a0253269ed803ac0.

It mechanically proves the 919-ID equality and the A/B disposition matrix, then
emits the deterministic reconciliation roster BEFORE any linguistic
adjudication:
  * 327 union-defect IDs  -> docs/G4A_R2_RECON_ROSTER.csv (chunk,seq,id,pass_a,pass_b)
  * 592 consensus-clean   -> docs/G4A_R2_RECON_CONSENSUS_CLEAN.csv
  * matrix / seed / split / SHA-256 -> docs/G4A_R2_RECON.md

Roster order: sort union IDs ascending, then random.Random(20260919).shuffle,
then split 109 / 109 / 109 (chunks 1/2/3).
"""
from __future__ import annotations

import csv
import hashlib
import io
import random
import subprocess
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PASS_A = "f7ddf7b1dadfd91a8126b15c0977873be02f883c"
PASS_B = "2b90574e3dafb88313ac6563ec094577fb7a95a2"
BASELINE = "5a5fd7d7ce8cc4e7c3f8a2b2a0253269ed803ac0"
SEED = 20260919
SPLIT = (109, 109, 109)

ROSTER = ROOT / "docs" / "G4A_R2_RECON_ROSTER.csv"
CONSENSUS = ROOT / "docs" / "G4A_R2_RECON_CONSENSUS_CLEAN.csv"
REPORT = ROOT / "docs" / "G4A_R2_RECON.md"

EXPECTED_MATRIX = {
    ("P1", "clean-candidate"): 188,
    ("P2", "clean-candidate"): 113,
    ("P1", "P2"): 18,
    ("P2", "P2"): 6,
    ("clean-candidate", "P2"): 2,
    ("clean-candidate", "clean-candidate"): 592,
}


def show(sha: str, path: str) -> str:
    return subprocess.run(
        ["git", "show", f"{sha}:{path}"], cwd=ROOT,
        capture_output=True, text=True, check=True,
    ).stdout


def load(sha: str, files, dispo_col: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for f in files:
        for r in csv.DictReader(io.StringIO(show(sha, f))):
            out[r["id"]] = r[dispo_col]
    return out


def sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    A = load(PASS_A, [f"docs/G4A_R2_PASS_A_CHUNK_{c}.csv" for c in (1, 2, 3, 4)], "pass_a_disposition")
    B = load(PASS_B, [f"docs/G4A_R2_PASS_B_CHUNK{c}.csv" for c in (1, 2, 3, 4)], "disposition")

    if set(A) != set(B):
        raise SystemExit("Pass A and Pass B do not cover the same ID set")
    if len(A) != 919:
        raise SystemExit(f"expected 919 IDs, found {len(A)}")

    matrix = Counter((A[i], B[i]) for i in A)
    if dict(matrix) != EXPECTED_MATRIX:
        raise SystemExit(f"A/B matrix mismatch: {dict(matrix)} != {EXPECTED_MATRIX}")

    union = sorted(i for i in A if A[i] != "clean-candidate" or B[i] != "clean-candidate")
    consensus = sorted(i for i in A if A[i] == "clean-candidate" and B[i] == "clean-candidate")
    if len(union) != 327:
        raise SystemExit(f"union-defect roster is {len(union)}, expected 327")
    if len(consensus) != 592:
        raise SystemExit(f"consensus-clean is {len(consensus)}, expected 592")

    order = sorted(union)
    random.Random(SEED).shuffle(order)

    def chunk_of(idx: int) -> int:
        b = 0
        for c, n in enumerate(SPLIT, start=1):
            b += n
            if idx < b:
                return c
        raise AssertionError

    lines = ["chunk,seq,id,pass_a_disposition,pass_b_disposition"]
    for seq, sid in enumerate(order):
        lines.append(f"{chunk_of(seq)},{seq},{sid},{A[sid]},{B[sid]}")
    ROSTER.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")

    clines = ["id,pass_a_disposition,pass_b_disposition"]
    for sid in consensus:
        clines.append(f"{sid},{A[sid]},{B[sid]}")
    CONSENSUS.write_text("\n".join(clines) + "\n", encoding="utf-8", newline="\n")

    roster_sha = sha256_of(ROSTER)
    consensus_sha = sha256_of(CONSENSUS)
    per_chunk = Counter(chunk_of(s) for s in range(len(order)))

    REPORT.write_text(f"""# G4-A residual audit R2 — A/B reconciliation (v2)

Evidence-first reconciliation of the Pass A vs Pass B dispositions, restarted
cleanly from canonical GitHub evidence. The earlier unpublished commits
`ad70bfa` / `a1eb6e7` are treated as noncanonical/lost and are neither
referenced as evidence nor recreated.

## Frozen inputs (by exact SHA)

- Baseline (merge-base of A and B): `{BASELINE}`
- Pass A: `codex/4-g4a-residual-audit-r2` @ `{PASS_A}`
- Pass B: `claude/recent-slack-handoff-a0fx3d` @ `{PASS_B}`
- PR #7: open / draft / unmerged @ `f34f109…`
- Learner `web/vocabulary.js` blob (must remain): `1c184e84e5c63e3a9f8e386af13787664a23bd66`
- Accepted 88-row Part-1 floor `docs/G4A_RESIDUAL_AUDIT_R2_INTAKE.csv`: unchanged (blob `7f34785e379ac76ee5341d4f65f33b123d57bc43`).

## Mechanically reproduced A/B matrix (919/919, same ID set)

| Pass A | Pass B | count |
|---|---|---:|
| P1 | clean-candidate | 188 |
| P2 | clean-candidate | 113 |
| P1 | P2 | 18 |
| P2 | P2 | 6 |
| clean-candidate | P2 | 2 |
| clean-candidate | clean-candidate | 592 |

A-defect set = 325 · B-defect set = 26 · overlap = 24 · **union-defect roster = 327** · consensus-clean = 592.

## Deterministic roster (committed before adjudication)

Union-defect IDs sorted ascending, then `random.Random({SEED}).shuffle`, then
split {" / ".join(str(n) for n in SPLIT)}: chunk 1 = {per_chunk[1]}, chunk 2 = {per_chunk[2]}, chunk 3 = {per_chunk[3]}.

- Roster: `docs/G4A_R2_RECON_ROSTER.csv` — SHA-256 `{roster_sha}`
- Consensus-clean carry-forward: `docs/G4A_R2_RECON_CONSENSUS_CLEAN.csv` — SHA-256 `{consensus_sha}`

Reproduce: `python3 scripts/qa/r2_reconciliation_roster.py` regenerates both
files byte-identically and prints the same SHA-256 values.

## Adjudication (chunks 1-3, evidence-first)

Each of the 327 rows is re-adjudicated against the **actual frozen Ukrainian
text** (exact `ua` / `definitionUa` substring evidence), carrying both the
Pass-A and Pass-B disposition + rationale, and a final disposition
(`P0`/`P1`/`P2`/`clean-candidate`/`needs-human`) with confidence, category,
rationale, and a proposal for defects. A final clean verdict must explicitly
rebut every prior defect claim; a generic "sense is accurate" is not accepted.
Output: `docs/G4A_R2_RECON_CHUNK{{1,2,3}}.csv`. Guard: `tests/g4a_r2_reconciliation.py`.

No learner-facing mutation, no remediation, no PR #7 movement, no merge, no
gate change, no G5. Gate remains `G4 technical PASS · G4-A CHANGES REQUESTED ·
G5 BLOCKED`.
""", encoding="utf-8", newline="\n")

    print(f"union-defect roster: {len(order)}  split {SPLIT}")
    print(f"consensus-clean: {len(consensus)}")
    print(f"roster SHA-256: {roster_sha}")
    print(f"consensus SHA-256: {consensus_sha}")


if __name__ == "__main__":
    main()
