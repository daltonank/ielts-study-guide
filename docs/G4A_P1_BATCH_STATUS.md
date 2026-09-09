# G4-A P1 Batch — Application Status

**Ticket:** T2-T4 closeout · **Applied:** 2026-09-09 · **Label:** AI linguistic QA (P1) · **Status:** all registered P1 findings are now resolved in `web/vocabulary.js`.

## Summary

Tickets **T2-T4** resolved the full 311-item P1 remediation manifest. T2 applied 104
corrections. T3 made 102 byte edits, resolved `SB-0425` through the corrected
`SB-0424` sibling, and deferred `SB-0773` to a source-level fix. T4 applied all 103
semantic-fidelity corrections. The malformed `minute2` headword is repaired at the
canonical source — **both** `Study Bank!A777` and `Oxford C1 Bank!B774` now read
`minute` — so `scripts/migrate_vocabulary.py` re-migrates the workbook to the correct
`minute` headword with its Oxford provenance (`oxfordId`, `topicTags`, `sourceUrls`)
retained. The isolated structural step
(`scripts/qa/apply_sb0773_headword_fix.py`) therefore no longer renames the headword;
it verifies the source-repaired identity/provenance and applies the reviewed P1
structural `translationQa` stamp. The learner-facing `web/vocabulary.js` is
byte-identical to the prior reviewed output (`9282d201`).

These are AI linguistic QA drafts accepted for this batch and stamped provenance `P1`.
Application does **not** claim a `G4-A PASS`; the gate remains **CHANGES REQUESTED**.

## Guarded, reproducible pipeline

T2 used `scripts/qa/apply_p1_t2_fixes.py`. T3 and T4 use the shared
`scripts/qa/apply_p1_batch_fixes.py` with reviewed JSON payloads. The structural
follow-up uses `scripts/qa/apply_sb0773_headword_fix.py`:

- **Input and output git-blob guards:** each step pins the exact prior and resulting
  `web/vocabulary.js` bytes. A second run fails closed.
- **Fixed review date:** `translationQa` stamped with `2026-09-09`, never `date.today()`,
  so output is byte-identical on any run date.
- **Bounded fields:** T2-T4 mutate only `ua`, `definitionUa`, `pos`, and `register`,
  plus the provenance stamp. The isolated structural script changes only the
  `SB-0773` headword and its provenance stamp.
- **Manifest accounting:** `tests/g4a_p1_closeout_accounting.py` independently checks
  that all 314 registered P1 findings equal 3 earlier fixes plus the 311 T2-T4 IDs.

**Blobs (repaired source chain):** migration base `4ed00c96`; P0 `4ed00c96` →
`30a3e1dc`; T2 `30a3e1dc` → `b39e5223`; T3 `b39e5223` → `8e28af35`; T4
`8e28af35` → `36c3d205`; `SB-0773` structural stamp `36c3d205` → `9282d201`
(final unchanged). Reproduced end-to-end by `tests/g4a_sb0773_source_chain.py`.

**Review date:** 2026-09-09.

## Special dispositions

- **SB-1629 (transport)** — the entry carries both its noun and verb senses
  (noun "транспорт"; verb "перевозити, транспортувати"), per the manifest override.
- **SB-1378 (assistance)** — `ua` disambiguated to `допомога; сприяння; підтримка` to
  resolve a deterministic-gate `ua` collision with SB-0057 / SB-1631 ("допомога").
- **SB-1393 (elements)** — `ua` disambiguated to `елементи; складники; компоненти` to
  resolve a deterministic-gate `ua` collision with SB-1402 ("елементи").
- **SB-0425 (efficiency)** — resolved without a byte edit because T3 changed sibling
  `SB-0424` (effectiveness) from `ефективність` to `результативність`.
- **SB-0773 (minute2)** — removed from the ordinary field batch and repaired at the
  source in both the `Study Bank` and `Oxford C1 Bank` sheets, so migration emits the
  correct `minute` headword with Oxford provenance retained. The uniqueness regression
  (`tests/g4a_sb0773_headword.py`) and the source-chain reproduction
  (`tests/g4a_sb0773_source_chain.py`) prove no normalized-headword collision exists and
  that the workbook deterministically reproduces the reviewed final output.
- **SB-1519 (output)** — remained in T4 and uses the T1-approved production sense.

## Verification

- `tests/g4a_ukrainian_deterministic.py` → EXIT 0 (no new colliding groups vs baseline;
  both prior collisions resolved).
- Record count remains **1,784** and normalized headwords remain unique.
- T2-T4 manifest union, exception accounting, provenance, special cases, and final
  unresolved counts are checked by `tests/g4a_p1_closeout_accounting.py`.
- Final combined regression: **24/24 commands PASS**, including responsive checks at
  320/375/430/768/1024/1440, Reading and Writing functional/accessibility suites,
  obstruction, persistence over real HTTP, eight seeded defects caught, and release
  integrity against `g4-candidate-3`.

## Remaining after P1 closeout

- **0 P1** remain open.
- **246 P2** open (unchanged).
- The findings register (`docs/G4A_UKRAINIAN_QA_FINDINGS.csv`) still counts all 314 as P1;
  the closeout test reconciles those historical classifications to the applied payloads.
- G4-A remains **CHANGES REQUESTED** because T5, the learner-facing flag/correction loop,
  is a separate outstanding acceptance requirement. No G4-A PASS is claimed.
