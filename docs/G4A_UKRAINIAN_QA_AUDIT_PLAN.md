# G4-A Ukrainian Linguistic QA — Audit Plan

**Status:** executed 2026-09-06. Results: [`G4A_UKRAINIAN_QA_FINDINGS.md`](G4A_UKRAINIAN_QA_FINDINGS.md); decision record: `DECISIONS.md` D-026.
**Ticket:** IELTS G4 external re-review repair (Slack `#proj-ielts`, G4 thread) · tracking issue `daltonank/ielts-study-guide#4`
**Candidate reviewed against:** `g4-candidate-3` / commit `2a51b46ab1b1950ff59ec8a7546d39b9fde840a5` (merged into `main` at `52d12dd`)

> **This plan describes an AI linguistic QA pass.** It does not constitute, replace, or satisfy a
> native-speaker editorial review. That gate is tracked separately and is not met by executing this plan.

This document is committed so that the findings register cites a plan that actually resolves. It was
referenced by path from `G4A_UKRAINIAN_QA_FINDINGS.md` before it existed in the repository; that
dangling reference is what this file closes.

---

## 1. Why this gate exists

The G4 external re-review validated structure, functionality, responsiveness, accessibility and
canonical-claim accuracy. It explicitly left Ukrainian linguistic quality as a separate, unstarted
gate. Treating the technical `PASS` as covering translation quality would let a vocabulary bank with
real translation errors reach learners unreviewed, so G4-A is scoped, gated and evidenced on its own.

## 2. Design principle: inventory first

An earlier escalation flagged that "review 100% of Ukrainian content" was too open-ended to execute
blind. This plan prices out exactly what "100%" means per file before sequencing any review work, so
each phase produces checkable evidence rather than one unverifiable "reviewed everything" claim.

### Verified scope — measured, not estimated

| Source file | Item unit | Count | UA fields in scope | Total UA strings |
|---|---|---:|---|---:|
| `web/reading_data.js` | question family / module | 15 families + 23 modules | `ua`, `uaSupport` | 38 |
| `web/writing1_data.js` | mixed | see below | `uaSupport`, `microTypeUa`, `ua`, `levelUa`, `uaTransferNote`, `uaCorrection` | 268 |
| `web/vocabulary.js` | vocabulary entry | 1,784 | `ua`, `definitionUa` | 3,568 |
| `web/app.js` | UI copy string | ~53 | inline UI/onboarding prose | 53 |

Total in scope: 3,927 Ukrainian strings.

## 3. Phases

**Phase 0 — Deterministic gate (100% coverage, scriptable).**
`tests/g4a_ukrainian_deterministic.py`. Mechanical checks only: missing or empty UA fields, fields
containing no Cyrillic, `ua` equal to the English headword, placeholder/HTML/encoding corruption, and
duplicate-translation collisions above policy thresholds. This phase is a precondition, not evidence
of quality — it cannot judge whether a well-formed Ukrainian string is the *right* Ukrainian string.
Required to pass before any semantic finding from later phases is trusted.

**Phase 1 — Reading UA scaffolding (38 strings, full manual review).**
Every family label and module `uaSupport` string read in full, including grammatical agreement
between generated template text and the labels interpolated into it.

**Phase 2 — Writing Task 1 bilingual content (268 strings, chunked by field type, `levelUa` first).**
Each Band 6/7/8 annotation cross-checked against the sample text it describes — the method that
caught R2-001 — plus contrastive-grammar notes and strategic tips checked for linguistic accuracy
rather than fluency.

**Phase 3 — Vocabulary bank (1,784 entries).**
Split into 18 chunks of ~100 entries, each reviewed independently against a fixed rubric: semantic
fidelity, definition accuracy, grammar/POS match, register, Russianisms and calques, and pedagogical
accuracy for a C1 IELTS learner. Findings returned structured, with severity.

## 4. Verification of the review itself

A review that cannot be checked is not evidence. Three mechanisms, all mandatory:

1. **Cross-chunk adjudication.** Every finding checked against the actual source data rather than
   trusted from the reviewer's report; a random sample re-verified in full to catch fabrication.
2. **Stratified spot-check.** A sample drawn *only* from entries the main pass judged clean,
   re-reviewed with no visibility into the main pass, to measure what the main pass missed. Note the
   sampling basis: this measures the unflagged pool, so its hit rate cannot be used to corroborate the
   bank-wide rate. Converting it into a bank-wide estimate requires a documented estimator, which this
   plan does not specify and this audit did not build.
3. **Seeded-defect meta-validation.** Synthetic entries carrying planted defects of each class the
   rubric targets, reviewed blind. Catching them is the "guards are not vacuous" proof that
   `tests/g4_writing1_negative.py` already applies to code, applied here to the review method.

## 5. Output contract

- A findings register with per-entry rows, stable IDs, severity, and a proposed correction.
- A decision record in `DECISIONS.md`.
- `CURRENT_STATE.md` updated to reflect the gate's real status.
- No content changes in the audit pass itself: findings are returned for routing, and corrections
  land separately so that the audit and the fix can be reviewed independently of each other.
- Severity meanings: **P0** actively wrong (false friend, wrong-headword definition, POS mismatch that
  misleads); **P1** learner-visible error that does not change meaning; **P2** narrow, incomplete or
  stylistically weak but not incorrect.

## 6. Exit criteria

`G4-A PASS` requires zero unresolved P0 and P1 findings, the deterministic gate passing before and
after every content change, and the stratified-sample check re-run against the corrected bank rather
than a re-read of the changed lines. P2 findings may remain open provided they are reported, not
closed for tidiness.

> **Note (2026-09-08):** The G4-A acceptance standard is **amended per D-027 (Approved 2026-09-08)**:
> the mandatory pre-release native-speaker editorial review is **replaced** by AI linguistic QA + a
> learner-facing flagging loop ("Flag mistake / Це виглядає неправильно"), with a native/human review
> now optional and advisory. Under the amended standard, `G4-A PASS` requires zero unresolved P0/P1
> findings, the deterministic gate passing before and after every content change, the stratified-sample
> check re-run against the corrected bank, and the learner flag loop present; P2 findings may remain an
> explicit backlog. This does not change the honesty banner above: this remains an AI linguistic QA pass
> and does not constitute or satisfy a native-speaker review.
