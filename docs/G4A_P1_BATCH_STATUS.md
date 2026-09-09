# G4-A P1 Batch — Application Status

**Ticket:** T2 · **Applied:** 2026-09-09 · **Label:** AI linguistic QA (P1) · **Status:** corrections now **applied** to `web/vocabulary.js` (not merely proposed).

## Summary

Ticket **T2** applied the first batch of the outstanding P1 Ukrainian-QA backlog —
**104 corrections** — to `web/vocabulary.js`. The batch composition (per
`docs/G4A_P1_BATCH_MANIFEST.md`) is **circular-definition 26 / grammar 60 / other 18**.
The complete id list is in `scripts/qa/p1_t2_corrections.json` (`corrections` object,
104 ids); consult that payload rather than reproducing the ids here.

These are AI linguistic QA drafts accepted for this batch and stamped provenance `P1`.
Application does **not** claim a `G4-A PASS`; the gate remains **CHANGES REQUESTED**.

## Guarded, reproducible pipeline

Applied via `scripts/qa/apply_p1_t2_fixes.py` reading `scripts/qa/p1_t2_corrections.json`,
mirroring the P0 mechanism (`scripts/qa/apply_p0_fixes.py`):

- **Input git-blob guard:** `web/vocabulary.js` must equal
  `414fbeacf54aad367beb7dccfbda935635d7ef19` before mutation (clean baseline at
  `main`/`ba6c10a`). A second run fails closed on this guard (idempotent, no double-apply).
- **Fixed review date:** `translationQa` stamped with `2026-09-09`, never `date.today()`,
  so output is byte-identical on any run date.
- **Only `ua`/`definitionUa`/`pos`/`register`** are mutated (plus the per-entry
  `translationQa` provenance stamp). Nothing else is touched.
- **Output git-blob guard:** the rebuilt file must equal
  `fe46b30a86892f5de62ea4d1a90bfeb54db50729` before it is written to disk.

**Blobs:** input `414fbeacf54aad367beb7dccfbda935635d7ef19` → output
`fe46b30a86892f5de62ea4d1a90bfeb54db50729`.

**Review date:** 2026-09-09.

## Reviewer overrides

- **SB-1629 (transport)** — the entry carries both its noun and verb senses
  (noun "транспорт"; verb "перевозити, транспортувати"), per the manifest override.
- **SB-1378 (assistance)** — `ua` disambiguated to `допомога; сприяння; підтримка` to
  resolve a deterministic-gate `ua` collision with SB-0057 / SB-1631 ("допомога").
- **SB-1393 (elements)** — `ua` disambiguated to `елементи; складники; компоненти` to
  resolve a deterministic-gate `ua` collision with SB-1402 ("елементи").

## Verification

- `tests/g4a_ukrainian_deterministic.py` → EXIT 0 (no new colliding groups vs baseline;
  both prior collisions resolved).
- Record count unchanged at **1,784**; all **104** ids changed at least one field.
- Full regression packet re-run green (G2/G3/G4 non-browser + browser suites);
  `tests/release_integrity.py` fails only on a missing local git tag (environmental).

## Remaining after T2

- **207 P1** (311 − 104) still open — batches **T3** (104) and **T4** (103) pending.
- **246 P2** open (unchanged).
- The findings register (`docs/G4A_UKRAINIAN_QA_FINDINGS.csv`) still counts all 314 as P1;
  only the correction payloads fold applied fixes in.
