# G4-A P0 Corrections — Status

**Review date (fixed):** 2026-09-06
**Branch head dependency:** built on PR #2 (`claude-code/g4a-ukrainian-qa-audit`)
head **`8cf8e08`**. The PR #3 base is set to that branch so the dependency is
explicit and the deterministic gate, findings register and D-026 record are all
present in this branch's tree. Do not merge PR #3 before PR #2.
**Scope:** the 142 P0-severity findings from the G4-A Ukrainian linguistic QA
audit (`docs/G4A_UKRAINIAN_QA_FINDINGS.md`, `docs/G4A_UKRAINIAN_QA_FINDINGS.csv`,
`DECISIONS.md` D-026 on PR #2), the two entries required to fully clear
deterministic-gate defect `G4A-V-001`, and the three Reading case-agreement
defects `G4A-R-001..003`.
**Authorization:** executed under Dalton's explicit instruction to batch-fix the
P0 entries, and the `[CHATGPT → CLAUDE]` "Proceed with Phase 2 now" handoff.
`D-026` remains **Proposed** and this is an AI linguistic QA pass, not a
native-speaker editorial review — that gate is separate and unmet.

## Vocabulary corrections (`web/vocabulary.js`)

The payload now carries **145 corrections** (was 142):

| Change | Entries | Reason |
|---|---|---|
| Preserved from the original P0 payload | 139 | unchanged concrete `ua`/`definitionUa`/`pos`/`register` corrections |
| **Modified for accuracy** | `SB-0670`, `SB-1161`, `SB-0256` | see below |
| **Added — clears `G4A-V-001`** | `SB-0208`, `SB-1728` | see below |
| **Added — clears collision ratchet** | `SB-1160` | see below |

The `web/vocabulary.js` data file itself **is committed on this branch** (it is
not a script-only PR anymore).

### Modified for accuracy
- **`SB-0670` `irrelevant`** — `ua` was `неактуальний`, which back-translates to
  "outdated / not topical", a different concept. Changed to
  `недоречний; такий, що не стосується справи`. `definitionUa` already correct,
  left as-is.
- **`SB-1161` `supportive`** — `ua` used `підтримуючий`, a dispreferred active
  participle (exactly the russianism-calque pattern the audit flags). Changed to
  `доброзичливий, готовий підтримати`.
- **`SB-0256` `consistency`** — the payload had truncated the correction to
  `послідовність`, which collided with the untouched `SB-1473 sequence`
  (`послідовність`) and misses the "logical coherence" sense. Restored to the
  register's own proposed correction `послідовність; узгодженість`.

### Added — clears deterministic-gate defect `G4A-V-001`
`SB-0208` (commence), `SB-0432` (embark) and `SB-1728` (commenced) all carried the
circular gloss `Щоб почати, почніть.` The original payload fixed only `SB-0432`,
which would have dropped the group to a pair and slipped under the duplicate
threshold while the defect stayed live. Both remaining members are now corrected
with genuine, distinct, contextually-correct Ukrainian written from each
headword's English sense and POS:
- **`SB-0208` `commence` (v.)** — `ua` `розпочинати; починати`; `definitionUa`
  `Офіційно або формально починати щось — дію, процес чи подію.`
- **`SB-1728` `commenced` (word family)** — `ua` `розпочав; розпочато`;
  `definitionUa`
  `Форма минулого часу дієслова commence (розпочинати): розпочав, було розпочато.`

All three glosses are now distinct, so `G4A-V-001` clears.

### Added — clears the identity collision ratchet
Correcting `SB-1679 appendix` to `додаток` (its correct document-sense term)
collided with the untouched `SB-1160 supplement` (`додаток`, imprecise). Rather
than degrade the `appendix` fix, `SB-1160` is corrected to the register's own P1
proposal `додаток (n.); доповнювати (v.)`, which is both more accurate and
distinct.

## Reproducible, byte-identical patch

- `scripts/qa/p0_corrections.json` — the 145 corrections under `corrections`,
  plus a `_meta` block carrying the fixed `review_date`, the `base_commit`, and
  the expected input/output git blob SHA-1s.
- `scripts/qa/apply_p0_fixes.py` — applies them to `web/vocabulary.js` with three
  guarantees enforced as **executable assertions** (the script exits non-zero and
  writes nothing on any mismatch), not as prose:
  1. **INPUT GUARD** — the on-disk `web/vocabulary.js` git blob SHA-1 must equal
     `_meta.expected_input_blob_sha1`
     (`01a8c5acd2ab0bcf9a8eefbec0a11d7530f19038`, i.e. `main` @ `52d12dd`) before
     any mutation. A second run on an already-patched file fails loudly instead of
     double-applying.
  2. **FIXED REVIEW DATE** — `translationQa` is stamped
     `Reviewed — G4-A P0 correction applied (2026-09-06)` from
     `_meta.review_date`, never `date.today()`, so the output is byte-identical on
     any run date.
  3. **OUTPUT GUARD** — the computed new file's git blob SHA-1 must equal
     `_meta.expected_output_blob_sha1`
     (`df6df637916f0695b3b080b53cc7743a1026eb20`) before it is written.

Running `scripts/qa/apply_p0_fixes.py` against a clean base reproduces the exact
committed `web/vocabulary.js` (`df6df637…`) every time.

## Reading case-agreement fix (`G4A-R-001..003`)

Fixed at the **generator source**, not by hand-editing generated data. The
`uaSupport` scaffolding line "Цей тип завдань перевіряє <X>. …" uses the verb
`перевіряє`, which governs the accusative case, but
`scripts/build_reading_curriculum.py` interpolated the nominative
`FAMILY_META[fam][3]` labels. Twelve labels are nom/acc syncretic and read
correctly by coincidence; three feminine-headed labels did not:

| Finding | Module | Before | After |
|---|---|---|---|
| `G4A-R-001` | `READ-MULTIPLE-CHOICE` | …перевіряє … головна думка | …головну думку |
| `G4A-R-002` | `READ-YNNG` | перевіряє позиція … | перевіряє позицію … |
| `G4A-R-003` | `READ-SHORT-ANSWER` | коротка точна відповідь … | коротку точну відповідь … |

A new `FAMILY_UA_SKILL_ACCUSATIVE` table supplies the accusative form used only in
that sentence (`familyMeta.ua` keeps the nominative citation form, which
`web/app.js` surfaces standalone). A fail-closed assertion requires every family
to have an accusative entry, so a future feminine-headed label cannot silently
reintroduce the bug. `web/reading_data.js` was regenerated
(only the three `uaSupport` strings change) and
`tests/g4a_reading_case_agreement.py` re-parses the generated file independently to
enforce both the failure mode (no nominative fragment survives after `перевіряє`)
and the exact accusative string for all 15 families.

## Validation performed this session (exact commands, exit codes)

Run from repository root against the committed artifacts:

| Check | Result |
|---|---|
| `tests/g4a_ukrainian_deterministic.py` | **PASS** — `G4A-V-001` clears; 0 new collision groups vs the ratchet baseline; 1639/1784 still Draft (145 vocab entries newly reviewed) |
| `scripts/validate_build.py` | PASS |
| `tests/g2_vocabulary_validation.py` | PASS (1784 records, unique IDs, UA fields) |
| `tests/ui_vocabulary_static.py` | PASS |
| `tests/g3_reading_validation.py` | PASS (60 passages / 240 questions / 15 families) |
| `tests/g4a_reading_case_agreement.py` | PASS (15 family labels accusative; no forbidden nominative fragment) |
| `tests/g4_writing1_validation.py` | PASS |
| `tests/g4_writing1_inventory.py` | PASS |
| `tests/g4_writing1_claims.py` | PASS |
| `tests/g4_writing1_content_qa.py` | PASS |
| `tests/g4_writing1_negative.py` | PASS |
| `tests/release_integrity.py` | PASS |

Browser/responsive suites were not run (no Chromium in this environment); this
change touches vocabulary data, generated reading data and non-browser tests only.

## What's left

- **305 P1 + 246 P2** lower-severity findings from the same audit remain open,
  tracked in `docs/G4A_UKRAINIAN_QA_FINDINGS.md` / `.csv`. (The two P1 entries
  `SB-0208`/`SB-1728` and `SB-1160` folded into this batch remain counted as P1 in
  the register; only the correction payload includes them.)
- A **native-Ukrainian human editorial review** is still required before any
  `G4-A PASS`. Untouched by this batch.
- `CURRENT_STATE.md` / `DECISIONS.md` are edited by PR #2; this branch does not
  re-edit them to avoid conflicting with it. `D-026` stays **Proposed**.

## Gate

`G4 technical PASS · G4-A CHANGES REQUESTED · G5 BLOCKED`
