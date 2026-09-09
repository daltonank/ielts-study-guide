# G4-A P0 Corrections — Status

**Review date (fixed):** 2026-09-06
**Branch head dependency:** built on PR #2 (`claude-code/g4a-ukrainian-qa-audit`)
head **`8cf8e08`**. The PR #3 base is set to that branch so the dependency is
explicit and the deterministic gate, findings register and D-026 record are all
present in this branch's tree. Do not merge PR #3 before PR #2.
**Scope:** the 142 P0-severity findings from the G4-A Ukrainian linguistic QA
audit (`docs/G4A_UKRAINIAN_QA_FINDINGS.md`, `docs/G4A_UKRAINIAN_QA_FINDINGS.csv`,
`DECISIONS.md` D-026 on PR #2), **plus three P1 additions** — `SB-0208` and
`SB-1728` (required to fully clear deterministic-gate defect `G4A-V-001`) and
`SB-1160` (required to clear the identity-collision ratchet triggered by the
`SB-1679 appendix` fix) — for **145 vocabulary corrections total (142 P0 + 3
P1)**, and the three Reading case-agreement defects `G4A-R-001..003`. The three
P1 additions remain counted as P1 in the findings register; their
`translationQa` provenance is stamped P1, not P0.
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

### Nine P0 entries refined for ua/definitionUa consistency
A review pass tightened nine P0 corrections so each entry's `ua` and
`definitionUa` are internally consistent and free of calques / inaccurate sense
claims. These stay P0; only their correction values changed.

| Entry | Word | Change |
|---|---|---|
| `SB-0333` | default | `ua` `типове значення` → `значення за замовчуванням; налаштування за замовчуванням`; definition aligned to the settings sense |
| `SB-0814` | nursery | `ua` `дитячі ясла` → `дитячі ясла; дитяча кімната` so the room sense the definition already names is covered |
| `SB-0954` | rally | `ua` `мітинг` → added the verb sense `згуртовуватися, збиратися на підтримку (v.)` to match `pos = n., v.` |
| `SB-1180` | tackle | `ua` `підкат` (football-specific) → broader `захват; відбір м'яча`; definition broadened accordingly |
| `SB-1287` | ward | `ua` `палата` → `палата (лікарняна); район, округ (адмін.)` so the administrative-district sense in the definition is represented |
| `SB-1308` | withdrawal | `ua` now labels the financial (`зняття коштів`), military and medical senses separately; adds the funds sense the definition cited |
| `SB-1444` | dominant | `ua` calque `домінуючий` → idiomatic `панівний; переважний; домінантний` |
| `SB-0150` | brutal | definition de-scoped from `часто в нерозважливий спосіб` to center on extreme cruelty/harshness/severity; `ua` `жорстокий; нещадний; суворий` |
| `SB-1121` | stem | removed the inaccurate "grows vertically upward" claim; noun sense = plant axis supporting leaves/flowers/fruit and carrying water/nutrients; `stem from` verb sense preserved separately |

## Reproducible, byte-identical patch

- `scripts/qa/p0_corrections.json` — the 145 corrections under `corrections`,
  plus a `_meta` block carrying the fixed `review_date`, the `base_commit`, and
  the expected input/output git blob SHA-1s.
- `scripts/qa/apply_p0_fixes.py` — applies them to `web/vocabulary.js` with three
  guarantees enforced as **executable assertions** (the script exits non-zero and
  writes nothing on any mismatch), not as prose:
  1. **INPUT GUARD** — the on-disk `web/vocabulary.js` git blob SHA-1 must equal
     `_meta.expected_input_blob_sha1`
     (`4ed00c96e8a5fc72b2074b37980c40fbb6541b18`, the repaired-source migration base;
     the pre-SB-0773-repair base was `01a8c5ac…`) before
     any mutation. A second run on an already-patched file fails loudly instead of
     double-applying.
  2. **FIXED, SEVERITY-AWARE REVIEW STAMP** — `translationQa` is stamped from
     `_meta.review_date` (never `date.today()`), so the output is byte-identical on
     any run date. The label is **severity-aware**: the 142 P0 entries get
     `Reviewed — G4-A P0 correction applied (2026-09-06)`, while the three P1
     additions listed in `_meta.p1_ids` (`SB-0208`, `SB-1728`, `SB-1160`) get
     `Reviewed — G4-A P1 correction applied (2026-09-06)`, so no P1 entry is
     mislabeled P0.
  3. **OUTPUT GUARD** — the computed new file's git blob SHA-1 must equal
     `_meta.expected_output_blob_sha1`
     (`30a3e1dcd073a6e9c51ea0ddb2b5603437912b0b`) before it is written.

Running `scripts/qa/apply_p0_fixes.py` against a clean base reproduces the exact
P0-stage `web/vocabulary.js` blob (`30a3e1dc…`) every time; the T2-T4 and SB-0773
steps then carry it to the reviewed final (`9282d201`).

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
| `tests/g4_writing1_negative.py` | PASS (8/8 seeded defects caught; restored tree passes) |
| `tests/release_integrity.py` | PASS |

Byte-reproduction check: restored the clean base `web/vocabulary.js`
(input blob `4ed00c96…`, the repaired-source migration base), re-ran
`apply_p0_fixes.py`, output reproduced the new pinned blob `30a3e1dc…` exactly;
a second run fails closed (idempotent).
Reading generator re-run (`scripts/build_reading_curriculum.py`) leaves
`web/reading_data.js` byte-identical (blob `f1e6a6d…`, no diff).

Browser/responsive suites (Chromium `/opt/pw-browsers/chromium-1194`, via the
`IELTS_CHROMIUM` override in `tests/browser_env.py`) — all PASS this session:

| Browser check | Result |
|---|---|
| `tests/responsive_check.py` | PASS — 320/375/430/768/1024/1440 |
| `tests/g3_reading_functional.py` | PASS |
| `tests/g3_reading_responsive.py` | PASS — 320/375/430/768/1024/1440 |
| `tests/g3_reading_accessibility.py` | PASS |
| `tests/g4_writing1_functional.py` | PASS |
| `tests/g4_writing1_responsive.py` | PASS — 320/375/430/768/1024/1440 |
| `tests/g4_writing1_accessibility.py` | PASS |
| `tests/accessibility_static.py` | PASS |

## What's left

- **207 P1 + 246 P2** lower-severity findings from the same audit remain open.
  Reconciled mechanically from `docs/G4A_UKRAINIAN_QA_FINDINGS.csv`, which holds
  314 P1 + 246 P2; the P0 batch fixed 3 P1 (`SB-0208`, `SB-1728`, `SB-1160`),
  leaving 311 P1 + 246 P2. (Those three remain counted as P1 in the register;
  only the correction payload folds them in.) **Ticket T2 (2026-09-09) then
  applied the first P1 batch — 104 corrections — to `web/vocabulary.js`**, so the
  open P1 backlog is now **311 − 104 = 207** (246 P2 unchanged). The **27
  spot-check rows (9 P1, 18 P2)** that previously lacked a proposed correction /
  confidence are **triaged in ticket T1 (2026-09-08)**: each carries a
  `proposed_correction` and a `confidence`, severity was re-confirmed with no
  reclassification, so all 702 register rows are populated. The remaining P1/P2
  corrections are **not yet applied to `web/vocabulary.js`** — application is
  deferred to the P1 batch tickets T3–T4 and the P2 backlog (see
  `docs/G4A_P1_BATCH_MANIFEST.md`, `docs/G4A_P1_BATCH_STATUS.md`,
  `docs/G4A_SPOTCHECK_TRIAGE.md`). Unresolved counts are now **207 P1 + 246 P2**.
- Under **D-027 (Approved 2026-09-08)** the mandatory pre-release native-Ukrainian
  human editorial gate is replaced by AI linguistic QA + a learner flagging loop as
  the governing `G4-A PASS` standard; native/human review is now advisory/optional and
  must not be claimed as completed. This batch does not by itself satisfy the standard.
- `CURRENT_STATE.md` / `DECISIONS.md` are edited by PR #2; this branch does not
  re-edit them to avoid conflicting with it. `D-026` stays **Proposed**.

## Gate

`G4 technical PASS · G4-A CHANGES REQUESTED · G5 BLOCKED`
