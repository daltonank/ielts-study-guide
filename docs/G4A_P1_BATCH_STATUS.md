# G4-A P1 Batch — Application Status

**Ticket:** T2-T4 closeout · **Applied:** 2026-09-09 · **Label:** AI linguistic QA (P1) · **Status:** all registered P1 findings are now resolved in `web/vocabulary.js`.

## Summary

Tickets **T2-T4** resolved the full 311-item P1 remediation manifest. T2 applied 104
corrections. T3 made 102 byte edits, resolved `SB-0425` through the corrected
`SB-0424` sibling, and deferred `SB-0773` to a source-level fix. T4 applied all 103
semantic-fidelity corrections. The isolated structural commit then changed the
malformed `minute2` headword to `minute` in both the source workbook and
`web/vocabulary.js`.

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

**Blobs:** T2 `414fbeac` → `fe46b30a`; T3 `fe46b30a` → `3427a6a5`; T4
`3427a6a5` → `0d144c70`; `SB-0773` `0d144c70` → `9282d201`.

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
- **SB-0773 (minute2)** — removed from the ordinary field batch and fixed separately at
  the source. The source workbook and learner-facing output now use `minute`; the
  uniqueness regression proves no normalized-headword collision exists.
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
