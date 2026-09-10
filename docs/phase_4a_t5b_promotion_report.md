# G4-A T5-B — Fresh Promotion Evidence Packet

**Ticket:** T5-B (GitHub issue #4) · **Generated:** 2026-09-10 · **Author:** Claude Code (AI QA)
**Base:** `origin/main` = `128b54c36f99b865c8b8bc49c5e835eb19c7c732` (verified against GitHub API; matched)
**Branch:** `claude-code/4-g4a-t5b-promotion` (branched from the exact base above)
**Gate language (unchanged):** `G4 technical PASS · G4-A CHANGES REQUESTED · G5 BLOCKED`

> This packet produces the *fresh* promotion evidence that determines whether the merged
> product is eligible to be **proposed** for G4-A PASS. It does not decide PASS, does not
> close issue #4, and does not start G5. Nothing was merged; no history was rewritten; no
> pinned blob/hash was repinned.

## Proposed disposition: **CHANGES REQUESTED**

Every automated check (28/28) and the deterministic G4-A gate PASS, and the entire changed-P1
sample re-review is clean. However, the **blind stratified sample of currently-"clean"
(never-flagged) entries surfaced a new, reproducible P1-class defect** — adjacent identical-word
repetition inside `definitionUa` — in entries that are neither remediated nor tracked in the
246-item P2 backlog. Per the ticket rule ("Any new P0/P1 finding => the disposition is CHANGES
REQUESTED"), and because the project's own findings register classifies this exact "Word repeated"
defect as **P1** (e.g. `SB-0125`, `SB-1673`), the honest disposition is **CHANGES REQUESTED**.
I propose; I do not decide — an independent reviewer confirms severity and disposition.

## 1. Environment

- Chromium: `/opt/pw-browsers/chromium-1194/chrome-linux/chrome`, exported as `IELTS_CHROMIUM`. `PYTHONUTF8=1`. `playwright install` was **not** run.
- Python deps installed into the session (were missing): `jsonschema`, `playwright` (pip package), `openpyxl` (required by `scripts/migrate_vocabulary.py`, which the source-chain test drives). Installing `openpyxl` lets the raw-byte source-chain test actually run the migration; no test logic or pin was weakened.

## 2. Command → exit-code → result table

### Non-browser (17)

| # | Command | Exit | Result |
|---|---|---:|---|
| 1 | `python3 tests/g4a_ukrainian_deterministic.py` | 0 | PASS — 1784 entries; register 142 P0 / 314 P1 / 246 P2; main-pass 675 / spot-check 27 disjoint |
| 2 | `python3 tests/g4a_p1_closeout_accounting.py` | 0 | PASS — registered P1=314 resolved=314 unresolved=0; P2=246 unchanged |
| 3 | `python3 tests/g4a_sb0773_source_chain.py` | 0 | PASS — workbook→…→final `9282d201` reproduced (after `openpyxl` install) |
| 4 | `python3 tests/g4a_sb0773_headword.py` | 0 | PASS — `minute` unique, `minute2` absent |
| 5 | `python3 tests/g4a_migration_portability.py` | 0 | PASS — regenerated LF artifacts reproduce pinned base `4ed00c96` + manifest `2a01f381`; no CRLF |
| 6 | `python3 scripts/validate_build.py` | 0 | PASS — 139 requirement rows, 0 errors |
| 7 | `python3 tests/g2_vocabulary_validation.py` | 0 | PASS — 1784 records |
| 8 | `python3 tests/ui_vocabulary_static.py` | 0 | PASS |
| 9 | `python3 tests/g4a_reading_case_agreement.py` | 0 | PASS — 15 family labels accusative (G4A-R-001..003) |
| 10 | `python3 tests/g3_reading_validation.py` | 0 | PASS — 60 passages / 240 questions / 15 families / 100% explanations |
| 11 | `python3 tests/g4_writing1_validation.py` | 0 | PASS — 11 modules, 13 error categories, 21 model responses |
| 12 | `python3 tests/g4_writing1_inventory.py` | 0 | PASS — every benchmark met |
| 13 | `python3 tests/g4_writing1_claims.py` | 0 | PASS — 531 text blocks, 21/21 prompts + 7/7 band sets traced |
| 14 | `python3 tests/g4_writing1_content_qa.py` | 0 | PASS — 115 claims re-derived, 0 failed |
| 15 | `python3 tests/g4_writing1_negative.py` | 0 | PASS — 8/8 seeded defects caught |
| 16 | `python3 tests/accessibility_static.py` | 0 | PASS |
| 17 | `python3 tests/release_integrity.py` | 0 | PASS — `g4-candidate-3` → `2a51b46…`; 5 hashes / 35 paths reachable (`git fetch --tags` first) |

### Browser (Chromium, widths 320/375/430/768/1024/1440) (11)

| # | Command | Exit | Result |
|---|---|---:|---|
| 18 | `python3 tests/responsive_check.py` | 0 | PASS — all six widths |
| 19 | `python3 tests/g3_reading_functional.py` | 0 | PASS |
| 20 | `python3 tests/g3_reading_responsive.py` | 0 | PASS — six widths |
| 21 | `python3 tests/g3_reading_accessibility.py` | 0 | PASS |
| 22 | `python3 tests/g4_writing1_functional.py` | 0 | PASS |
| 23 | `python3 tests/g4_writing1_responsive.py` | 0 | PASS — six widths, all 7 families |
| 24 | `python3 tests/g4_writing1_accessibility.py` | 0 | PASS — all 7 families |
| 25 | `python3 tests/g4_writing1_obstruction.py` | 0 | PASS — six widths, no sticky occlusion |
| 26 | `python3 tests/g4_writing1_persistence.py` | 0 | PASS — real HTTP, genuine reload |
| 27 | `python3 tests/g4a_content_flag_static.py` | 0 | PASS — T5-A flag loop static |
| 28 | `python3 tests/g4a_content_flag_functional.py` | 0 | PASS — T5-A flag loop functional, six widths |

**28 / 28 PASS.** No required check was skipped.

## 3. P0 / P1 / P2 accounting (as the accounting test reported)

- Registered **P0 = 142** (all resolved via T2–T4 + SB-0773 source fix).
- Registered **P1 = 314**, resolved = 314, **unresolved = 0**.
- **P2 = 246** remaining (deferred backlog, unchanged — acceptable for a PASS candidate).
- Deterministic gate `G4A-V-001`: 0 unresolved shared glosses. No new colliding groups above baseline.

## 4. Seeded-defect meta-validation

`tests/g4_writing1_negative.py`: **8 planted, 8 caught** (`8 of 8 seeded defects caught`), and the restored artifact still passes.

## 5. Changed-P1 fresh re-review (real inspection)

- All **309** batch corrections (T2 104 + T3 102 edited + T4 103) were confirmed to have **landed** in the current `web/vocabulary.js` with **0 landing mismatches** against the correction JSON (`scripts/qa/p1_t{2,3,4}_corrections.json`). (The remaining 2 of 311 are `SB-0425` resolved via sibling `SB-0424` and `SB-0773` via the structural source fix.)
- Reproducible sample: **seed = 42, n = 24** ids drawn from the 309 corrected set: `SB-0109, SB-0111, SB-0125, SB-0130, SB-0301, SB-0316, SB-0336, SB-0389, SB-0423, SB-0618, SB-0691, SB-0696, SB-0703, SB-0745, SB-0785, SB-0861, SB-1290, SB-1297, SB-1331, SB-1519, SB-1624, SB-1673, SB-1765, SB-1782`.
- Each was opened in the current file and checked for: English headword/POS, intended IELTS sense, `ua` translation, `definitionUa` definition, and agreement with the recorded correction. **All 24 are accurate, natural, and match the recorded correction.** Examples: `SB-0618 infamous` — the non-word "безсолідний" is gone ("сумно відомий"); `SB-0423 educator` — narrow "вихователь" replaced by "педагог; освітянин"; `SB-0861 peculiar` — the "непарний" mistranslation of "odd" removed.
- Non-blocking observations (not defects): `SB-0691 leap` keeps a thin one-word gloss definition ("Стрибати."); `SB-0389 displace` retains "витісняти" alongside the forced-resettlement sense (defensible for the supplant meaning).

## 6. Blind stratified sample of currently-"clean" entries — NEW P1-class finding

**Selection method (fixed before review):** from the 1,082 entries carrying **no** finding in the register, stratify by `pos`, sort by `id` ascending within each stratum, and take a deterministic stride (`offset = stride//2`, `stride = len(stratum)//4`) across the strata with ≥20 entries. Sample size **n = 20**.

Reviewing the Ukrainian fields of those 20 entries surfaced a recurring, unambiguous defect: **adjacent identical-word repetition in `definitionUa`** (e.g. `SB-0476 exclusion` "Акт виключення або виключення", `SB-0758 mere` "Тільки, тільки;", `SB-1199 thereafter` "…відтоді; відтоді.").

A full deterministic scan of all 1,082 clean entries for adjacent / punctuation-separated identical-word repetition in `definitionUa` found **~21 affected clean entries**, of which the following are unambiguous literal duplications:

| id | word | definitionUa (excerpt) |
|---|---|---|
| SB-0013 | accordance | …відповідність; **відповідність**. |
| SB-0357 | desirable | …приємний; **приємний**. |
| SB-0484 | expenditure | …витрати; **витрати**. |
| SB-0576 | hazard | …небезпека, **небезпека**, ризик… |
| SB-0577 | heighten | …збільшувати, **збільшувати**, робити більшим… |
| SB-0759 | merely | …тільки, **тільки**, і більше нічого. |
| SB-1230 | transparent | Прозорий, **прозорий**; має властивість… |
| SB-1259 | utterly | Повністю; **повністю**; в повній мірі. |
| SB-1486 | apparent | …очевидний; **очевидний**; відомий… |
| SB-0029 | adjacent | Лежать поруч, **поруч** або **поруч**;… |
| SB-0157 | burial | Акт поховання; **поховання**;… |

**Severity judgement.** The register itself classifies the identical "Word repeated" defect as **P1** (`SB-0125` "Word repeated", `SB-1673` "Word repeated three times" — both P1, category `other`). These clean entries carry the same defect but were never captured by the audit, so they are neither remediated nor in the deferred P2 backlog. This is a **NEW P1-class finding** (confidence: high for the literal duplications listed above; medium that the full set is exactly ~21). The automated gate and accounting still PASS because they verify the register's internal consistency and structural invariants — **not** exhaustive linguistic coverage — which is exactly what this independent human-style sample is designed to catch.

No new P0 was found. The changed-P1 material is clean; the finding is confined to previously-unaudited "clean" entries.

## 7. Why CHANGES REQUESTED (not PASS CANDIDATE)

- All 28 automated checks + the deterministic gate PASS, and the changed-P1 re-review is clean — the *tracked* remediation is solid.
- But an independent blind sample surfaced a reproducible NEW P1-class defect class outside the register. Per the ticket, any new P0/P1 => CHANGES REQUESTED, and the register's own precedent rates this defect P1.
- **Recommended remediation (next ticket):** extend the "Word repeated" audit sweep across the full bank (not just previously-flagged rows), register the newly-found entries with `id/category=other/severity`, correct the duplicated `definitionUa` fragments, and re-run this packet. Then T5-B can be re-issued for a genuinely clean promotion attempt.

## 8. Integrity statement

- `main` verified = `128b54c36f99b865c8b8bc49c5e835eb19c7c732` (GitHub API + `origin/main`), matched the expected SHA.
- Branch `claude-code/4-g4a-t5b-promotion` created from that exact base. Nothing merged. No tag moved, no force-push, no blob/hash repinned. `web/vocabulary.js` blob remains `9282d201…` (untouched — this packet added evidence docs only).
