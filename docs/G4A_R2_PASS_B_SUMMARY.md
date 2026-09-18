# G4-A residual audit R2 — Pass B summary

Independent, blind, second-pass linguistic review of the 919 `needs-human`
rows pending at the Part-1 checkpoint. Executor: Claude Code. Reasoning
owner / reviewer: ChatGPT. Final authority: Dalton.

**This is second-pass evidence only.** No learner-facing mutation, no
remediation applied, no PR movement, no gate change, no G5 work. Gate remains
`G4 technical PASS · G4-A CHANGES REQUESTED · G5 BLOCKED`.

## Provenance

- Blind baseline commit: `5a5fd7d7ce8cc4e7c3f8a2b2a0253269ed803ac0` (R2 Part-1 intake).
- Learner baseline (PR #7 head, verified open/draft/unmerged): `f34f109ae5b8564e7fa10317c167a6ca728c52fd`.
- Learner vocabulary blob (unchanged by Pass B): `1c184e84e5c63e3a9f8e386af13787664a23bd66`.
- Part-1 intake / accepted-floor artifact `docs/G4A_RESIDUAL_AUDIT_R2_INTAKE.csv`: unchanged from baseline (verified byte-identical).
- Manifest: `docs/G4A_R2_PASS_B_MANIFEST.csv`, SHA-256 `a4e1cd31bff89dc27c545aae2352007ca61a6cebe8a631940eb2106a1656f929`.
- Pass A was **not** read: this session did not open any `G4A_R2_PASS_A_*`
  artifact, did not inspect the Codex Pass-A branch/head, and did not read the
  canonical issue thread past the Part-1 checkpoint.

## Coverage

919 / 919 rows judged exactly once (no omissions, no duplicates, no
cross-chunk leakage — enforced by `tests/g4a_r2_pass_b.py`). The accepted
88-row floor (63 P1 + 25 P2) was excluded and left untouched.

| Chunk | Rows | clean-candidate | P2 | P1 | P0 |
|------:|-----:|----------------:|---:|---:|---:|
| 1 | 230 | 219 | 11 | 0 | 0 |
| 2 | 230 | 221 | 9 | 0 | 0 |
| 3 | 230 | 226 | 4 | 0 | 0 |
| 4 | 229 | 227 | 2 | 0 | 0 |
| **Total** | **919** | **893** | **26** | **0** | **0** |

Confidence across all 919 judgments: 784 high, 134 medium, 1 low.

## Findings (all P2; proposal-only, none applied)

Every row carries explicit per-axis states and a row-specific rationale in the
chunk CSVs. No P0 or P1 defects were found in this fresh 919-row pass. The 26
P2 findings, by category:

**Truncated / broken learner text (5)** — SB-0865 petition, SB-0860 peasant
(cut mid-word), SB-0917 problematic (dangling colon), SB-1303 widow (dangling
colon), SB-1443 document (truncated) — plus SB-1371 theory (truncated).
(6 truncation/punctuation items total across categories `truncated-definition`
and `dangling-punctuation`.)

**Redundant word repetition (2)** — SB-1175 sword («рубання» ×3), SB-1627
subsidiary («дочірньою компанією або дочірньою компанією»).

**Semantic / sense issues (4)** — SB-1345 individual («самотньою» = lonely for
'considered singly'), SB-0437 emergence («зовнішній вигляд» wrong sense of
'appearance'), SB-1544 clause (grammatical vs contract sense mismatch),
SB-0882 portfolio (investment def under the creative-works gloss «портфоліо»).

**Grammar / morphology (5)** — SB-1452 implies (agreement «прямого вказівки»),
SB-1137 submission (case «завершена робота»), SB-1640 decades (genitive
citation «десятиліть»), SB-1524 predicted / SB-1771 encountered (finite
past-tense citation forms), SB-0122 beloved (verb-framed def for an adjective).

**POS / gloss mismatch (1)** — SB-0099 attribute (verb def under a noun-only
gloss «атрибут»).

**Calque / imprecise definition (3)** — SB-0118 bay («тіло води» calque of
'body of water'), SB-1540 alter (calqued infinitive-style def), SB-1124 stir
(gloss «ворушити» imprecise for stirring liquid).

**Weak / circular / wrong-term definitions (3)** — SB-1753 restraints (weak
def incl. 'резерв'), SB-1565 modified (restatement def), SB-0114 barrel
(circular + «держаків» where staves are «клепки»), SB-0290 correspondence
(imprecise 'обмін люб'язністю').

## Method

Each row was judged on all nine axes — semantic fidelity; natural/idiomatic
contemporary Ukrainian; grammar/morphology/syntax/punctuation/word-order; POS
alignment; learner register; Russianism/Surzhyk/calque risk; `ua` ↔
`definitionUa` consistency; pedagogical accuracy for the intended IELTS sense;
UI/formatting integrity. Trivial house-style variance (a missing terminal
period, a lowercase initial, a benign cognate restatement) was treated as
clean; only genuine defects a learner would encounter were flagged. Clean
candidates carry affirmative, row-specific rationales (no synthesised generic
strings), enforced by the guard.

## Notes for reconciliation (ChatGPT's step, not done here)

- Reviewer should reconcile these 26 Pass-B P2 findings against Pass A;
  Pass B intentionally did not see Pass A.
- Several truncation and connector/adjacent-repeat items overlap conceptually
  with the T5-B "connector-separated repeat" class already registered
  open-deferred; Pass B reports them on their own merits without cross-checking
  that register.
