# G4-A residual audit R2 — Pass B

Independent, blind, second-pass linguistic review of the residual-audit
population. Executor: Claude Code. Reasoning owner / reviewer: ChatGPT. Final
authority: Dalton.

Blind baseline commit: `5a5fd7d7ce8cc4e7c3f8a2b2a0253269ed803ac0`
Learner baseline (PR #7 head): `f34f109ae5b8564e7fa10317c167a6ca728c52fd`
Learner vocabulary blob (unchanged by Pass B): `1c184e84e5c63e3a9f8e386af13787664a23bd66`

Gate remains `G4 technical PASS · G4-A CHANGES REQUESTED · G5 BLOCKED`. Pass B
is second-pass *evidence only*; it applies no remediation, moves no PR, changes
no gate, and starts no G5 work.

## Population

The Pass-B population is the **919 `needs-human` rows** pending at the Part-1
checkpoint (`docs/G4A_RESIDUAL_AUDIT_R2_INTAKE.csv`). The accepted 88-row floor
(63 P1 + 25 P2) is **excluded** and must not be modified or downgraded.

## Deterministic ordering (fixed before inspection)

1. Select the 919 `needs-human` stable IDs from the Part-1 intake (id column
   only — learner text is not read to build this manifest).
2. Sort ascending lexicographically (zero-padded, so == numeric order).
3. Shuffle with CPython Mersenne-Twister: `random.Random(20260916).shuffle(ids)`.
4. Split into four chunks of 230 / 230 / 230 / 229.

Seed: `20260916`  ·  Split: chunk 1: 230, chunk 2: 230, chunk 3: 230, chunk 4: 229  ·  Total: 919

Manifest file: `docs/G4A_R2_PASS_B_MANIFEST.csv`
Manifest SHA-256: `a4e1cd31bff89dc27c545aae2352007ca61a6cebe8a631940eb2106a1656f929`

Reproduce: `python3 scripts/qa/r2_pass_b_manifest.py` regenerates an identical
manifest and prints the same SHA-256.

## Judgment artifacts

Per-chunk row-level judgments (committed one chunk at a time, after that
chunk's judgments are complete):

- `docs/G4A_R2_PASS_B_CHUNK1.csv`
- `docs/G4A_R2_PASS_B_CHUNK2.csv`
- `docs/G4A_R2_PASS_B_CHUNK3.csv`
- `docs/G4A_R2_PASS_B_CHUNK4.csv`

Each row records explicit states for all nine axes (semantic fidelity;
natural/idiomatic contemporary Ukrainian; grammar/morphology/syntax/
punctuation/word-order; POS alignment; learner register;
Russianism/Surzhyk/calque risk; `ua` ↔ `definitionUa` consistency;
pedagogical accuracy for the intended IELTS sense; UI/formatting integrity),
plus disposition (`P0`/`P1`/`P2`/`clean-candidate`), confidence, and a
row-specific rationale. Defect rows additionally carry category, proposed
target field, and proposed replacement value. Clean candidates carry
affirmative per-row evidence — no synthesized generic rationale.

Guard/validator: `tests/g4a_r2_pass_b.py`.
