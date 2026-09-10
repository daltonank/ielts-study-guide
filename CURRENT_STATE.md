# CURRENT_STATE.md

**Updated:** 2026-09-10
**Last passed gate:** G3 Reading Complete — PASS  
**Candidate gate:** G4 technical layer — PASS (external re-review `TECHNICAL PASS`, 21/21 commands, 8/8 seeded defects, re-verified independently at `2a51b46`/`52d12dd`). **G4-A Ukrainian linguistic QA — CHANGES REQUESTED**. The registered P1 backlog is now fully remediated: **0 P1 + 246 P2** remain open after T2-T4 and the isolated `SB-0773` source fix. Native/human review remains advisory and must not be claimed as completed. No G4-A PASS is claimed.

**T5-A progress (2026-09-09):** D-027's learner-facing flag/correction loop is now **implemented and validated** (ticket T5-A). A keyboard-native `Flag mistake / Це виглядає неправильно` control sits on all three G4-A Ukrainian-content surfaces (vocabulary `ua`/`definitionUa`, Reading UA support, Writing Task 1 UA support); reports are captured to the canonical local state (`ieltsC1UAEN.state.v1.contentFlags`), reviewable/copyable/exportable, round-trip through Export/Import without disturbing unrelated progress, and are strictly local (no network). Evidence: `tests/g4a_content_flag_static.py` and `tests/g4a_content_flag_functional.py` (six-width responsive + keyboard + reload + round-trip), full G2/G3/G4/G4-A regression re-run. **The gate still stays `G4-A CHANGES REQUESTED` and G5 stays BLOCKED** — the T5-B fresh promotion packet (zero unresolved P0/P1 re-verified end-to-end) remains outstanding. No G4-A PASS is claimed.
**T5-B fresh promotion packet (2026-09-10):** the independent T5-B promotion-evidence packet was run end-to-end from `origin/main` `128b54c`. All **28/28** validation commands PASS (17 non-browser + 11 browser at 320/375/430/768/1024/1440), the deterministic G4-A gate passes, `tests/g4a_p1_closeout_accounting.py` reports **314/314 registered P1 resolved · 0 unresolved · 246 P2 remaining**, seeded-defect meta-validation catches **8/8**, and a seed-42 re-review of 24 corrected P1 entries is fully accurate. **However, a blind stratified sample of never-flagged ("clean") entries surfaced a NEW P1-class defect** — adjacent identical-word repetition in `definitionUa` (~21 clean entries; unambiguous literal duplications include `SB-0013, SB-0357, SB-0484, SB-0576, SB-0577, SB-0759, SB-1230, SB-1259, SB-1486`), the same "Word repeated" class the register rates P1 (`SB-0125`, `SB-1673`) yet outside the register and the 246-item P2 backlog. Per the T5-B rule, any new P0/P1 ⇒ **CHANGES REQUESTED**, not a PASS candidate. Gate language stays `G4 technical PASS · G4-A CHANGES REQUESTED · G5 BLOCKED`; no G4-A PASS is claimed. Evidence: `docs/phase_4a_t5b_promotion_report.md`. Recommended next ticket: sweep the "Word repeated" audit across the full bank, register + correct the newly-found entries, then re-issue T5-B.
**T5-B repeat remediation (2026-09-10, branch `claude/slack-session-62m83z`, issue #4):** the failed packet's "~21" estimate was resolved to **exact numbers** by a deterministic full-bank (1,784) scan of `definitionUa` for adjacent + punctuation-separated identical-word repetition: **37 candidates → 35 confirmed P1 defects corrected, 2 benign** (`SB-0660`, `SB-1197`, allowlisted with rationale), **0 needing human adjudication**. Corrections applied as a guarded post-migration stage (`scripts/qa/apply_t5b_repeat_fixes.py` + `t5b_repeat_corrections.json`): fail-closed input git-blob guard `9282d201` → new pinned output blob **`bb173f36…`**; the workbook is deliberately **not** edited (`definitionUa` flows from Study Bank col D into base blob `4ed00c96`, and editing source would repin a frozen historical stage — forbidden), so the correction is layered post-migration exactly like P0/T2/T3/T4/SB-0773. New guards: `tests/g4a_t5b_repeat_guard.py` (full-bank adjacent/punctuation repeat guard, proven non-vacuous, 2-entry benign allowlist), `tests/g4a_t5b_supplemental_accounting.py`, and `tests/g4a_sb0773_source_chain.py` extended to end at `bb173f36` (no earlier stage repinned; base `4ed00c96` still reproduced). Supplemental register: `docs/G4A_T5B_SUPPLEMENTAL_FINDINGS.csv`. **A NEW distinct class was discovered and is left open: connector-separated repeats ("X або X", "X чи X"), 64 entries**, registered as open-deferred follow-up (out of T5-B's adjacent/punctuation scan scope). Fresh T5-B blind sample (seed `20260910`, fixed before inspection, n=40 stratified by POS over the 1,683 unflagged entries): **0/40 repeat-class defects**; the 35 corrected entries re-review clean. Full regression re-run: **20 non-browser + 11 browser (320/375/430/768/1024/1440) all PASS**. **Disposition stays CHANGES REQUESTED** — 64 connector-separated P1-class repeats remain open (D-027: zero unresolved P0/P1 required for PASS). Gate language unchanged; issue #4 not closed; no G4-A PASS claimed. See D-028 and `docs/phase_4a_t5b_promotion_report.md` §9–15.
**T5-A review corrections (2026-09-10, PR #6):** three reviewer findings (CHANGES REQUESTED) corrected on the same branch. **(1)** The vocabulary surface now renders TWO per-field flag controls — `field:"ua"` (captures `v.ua`) and `field:"definitionUa"` (captures `v.definitionUa`), each labelled `переклад / ua` and `визначення / definitionUa`; `flagTexts` no longer concatenates the two fields, so reports are accurately attributable. **(2)** `copyFlags` no longer shows a false success when both the Clipboard API and the `execCommand` fallback fail (honest failure toast + promise-rejection handling); `exportFlags` is wrapped in try/catch; `importData` validates/coerces each `contentFlags` member via `normalizeFlags` (malformed members dropped/coerced) and `renderFlagList` defensively normalises, so a malformed import can never crash the Settings flag view. **(3)** Browser coverage now opens the `<details>` control and asserts no overflow, an unclipped/unoccluded textarea + submit button, and tap-target sizing on all three UA surfaces at 320/375 px. Gate language unchanged; D-026/D-027 status unchanged; no G4-A PASS is claimed. Evidence: `tests/g4a_content_flag_static.py` + `tests/g4a_content_flag_functional.py` (updated), `app_ua_strings` ratchet 61 → 66, full G2/G3/G4/G4-A + browser regression re-run.
**T1 progress (2026-09-08):** the 27 spot-check findings are triaged (proposed_correction + confidence assigned; severity re-confirmed, no reclassification); the 311 unresolved P1 findings are partitioned into batch manifests T2/T3/T4.
**T2-T4 progress (2026-09-09):** T2 applied 104 corrections; T3 resolved 103 findings through 102 byte edits plus the `SB-0425` sibling disposition; T4 applied 103 corrections; the deferred `SB-0773` malformed headword was then corrected at the canonical source. Final vocabulary blob: `9282d201`. The P1 closeout test reconciles all **314/314 registered P1 findings**, leaving **0 P1 + 246 P2** open. Final combined regression: **24/24 commands PASS**, including all browser, responsive, accessibility, persistence, seeded-defect, and release-integrity checks. See `docs/G4A_P1_BATCH_STATUS.md`.

**Review remediation (2026-09-09, PR #5):** two blocking review findings fixed without changing learner-facing output (`web/vocabulary.js` stays `9282d201`). (1) The `SB-0773` source repair was completed — `Oxford C1 Bank!B774` is now `minute` to match `Study Bank!A777` — so a clean migration retains Oxford provenance and the guarded blob chain was repinned end-to-end (base `4ed00c96` → P0 `30a3e1dc` → T2 `b39e5223` → T3 `8e28af35` → T4 `36c3d205` → SB-0773 `9282d201`). (2) `apply_p1_t2_fixes.py` now normalizes CRLF before its input guard, matching `apply_p1_batch_fixes.py`. New guard `tests/g4a_sb0773_source_chain.py` proves clean workbook → reviewed final reproduction.

**Migration byte-determinism (2026-09-10, PR #6 follow-up, REQ-072):** `scripts/migrate_vocabulary.py` wrote `web/vocabulary.js` and `docs/vocabulary_migration_manifest.json` via `Path.write_text(...)`, which on Windows emits CRLF (`\n` → `os.linesep`) and changes the raw git blob away from the reviewed LF artifact — so `tests/g4a_sb0773_source_chain.py` fails on a Windows-style checkout under `PYTHONUTF8=1`. Both artifacts are now written with `write_bytes(payload.encode("utf-8"))` and explicit `\n`, giving byte-identical output on every OS. No content change: `web/vocabulary.js` blob stays `9282d201`, manifest blob stays `2a01f381`, and regenerating on Linux reproduces the pinned migration base `4ed00c96`. No hash/pin was repinned. New portability regression `tests/g4a_migration_portability.py` fails closed on CRLF or blob drift (static `write_bytes` guard + dynamic regeneration byte check; proven non-vacuous). Gate language unchanged; T5-B still outstanding; no G4-A PASS claimed.
**Next gate:** G5 Writing Task 2, blocked until G4-A corrections land and are re-verified  
**Deployment:** local HTML only; public reconciliation deferred

---

## Passed Gates

### G0 — Audit & Requirements Lock
PASS.

### G1 — Foundation & Design System
PASS.

### G2 — Legacy Integration & Vocabulary Migration
PASS.

The source workbook is reconciled at 1,784 / 1,784 normalized Study Bank records.

### G3 — Reading Academy
PASS.

Current Reading evidence:

- 8 / 8 foundation strategies
- 15 question families
- 60 original texts/extracts
- 240 scored questions
- 240 / 240 explanations
- timed/mastery evidence
- error/review integration
- responsive pass at 320/375/430/768/1024/1440
- accessibility/regression pass

---

### G4 — Writing Task 1
**TECHNICAL LAYER: PASS. OVERALL GATE: OPEN, pending G4-A.** External review of the
first candidate (`fe720d5`) returned **CHANGES REQUESTED** and produced candidate 2.
External re-review of `g4-candidate-2` returned **CHANGES REQUESTED** with one P1,
two P2 and one P3 finding. All four are fixed in candidate 3, and the third external
re-review returned **TECHNICAL PASS** on `g4-candidate-3` (21/21 commands, 8/8 seeded
defects, re-verified independently at `2a51b46`/`52d12dd`).

That `TECHNICAL PASS` covers structure, functionality, responsiveness, accessibility
and canonical-claim accuracy. It does **not** cover Ukrainian linguistic quality, which
is gated separately as G4-A (below) and is currently `CHANGES REQUESTED`. G4 as a whole
is therefore not complete.

Review packet: `docs/G4_EXTERNAL_REVIEW_PACKET.md`.

| Benchmark | Required | Actual |
|---|---:|---:|
| Visual families | 7 | 7 |
| Micro-exercises | ≥60 | 70 |
| Full timed prompts | ≥20 | 21 |
| Band comparison sets | 1 per family | 7 |
| Band samples at 150+ words | 21 | 21 |

Also delivered: 21 original visuals, all 10 micro-exercise types in every family,
guided/independent/timed/mastery progression per family, 4 foundation modules, 7 family
modules, a 13-category error taxonomy, and the learner-facing UI under
Skills → Writing Task 1.

Current Writing Task 1 evidence:

- `tests/g4_writing1_inventory.py` — every benchmark met, fails automatically if coverage drops
- `tests/g4_writing1_validation.py` — PASS
- `tests/g4_writing1_claims.py` — 531 text blocks, every figure traced to a declared derivation; canonical `respectively` constructions rejected
- `tests/g4_writing1_content_qa.py` — 115 prose claims re-derived, 0 failed
- `tests/g4_writing1_functional.py` — PASS (scoring, mastery, timing, autosave, error/review, reload)
- `tests/g4_writing1_responsive.py` — PASS at 320/375/430/768/1024/1440 across all 7 families
- `tests/g4_writing1_accessibility.py` — PASS across all 7 families
- `tests/g4_writing1_persistence.py` — real HTTP, genuine reload, export/import, keyboard-only
- `tests/g4_writing1_obstruction.py` — real viewport states at all six widths
- `tests/g4_writing1_negative.py` — eight seeded defects, all caught, including the ordered-pair blind spot and annotation/prose drift
- `tests/release_integrity.py` — the packet names a release that resolves
- G0–G3 regression re-run and passing
- `docs/phase_4_report.md`, `docs/writing1_content_qa.md`

Decisions: D-015 mastery thresholds (amended by D-022), D-016 error taxonomy (13
categories after D-022), D-017 grounding by re-derived facts, D-018 toolchain, D-019 the
visual panel as the only new component, D-020 canonical claim manifest, D-021
sentence-scoped binding of canonical prose, D-022 the 150-word Task 1 minimum enforced,
D-023 release identity by tag, D-024 canonical `respectively` ban, D-025 executable
band-diagnostic evidence.

---

## Active Work

### G4-A — Ukrainian Linguistic QA — CHANGES REQUESTED

Full audit executed against `g4-candidate-3` (2026-09-06): deterministic gate (100%
coverage; **now PASSES on current `main`** — `G4A-V-001` was resolved in PR #3, see below), Reading
scaffolding (38/38 strings, 3 grammar findings), Writing Task 1
content (268/268 strings, 0 defects — confirms D-025/R2-001 holds), vocabulary bank
(1,784/1,784 entries, 18-chunk review — **675 findings, 37.8% of entries, 142 P0**),
a stratified spot-check (70 previously-clean entries, 27 more findings), and a
seeded-defect meta-validation of the review process (4/4 planted defects caught).

**This is an AI linguistic QA pass.** It does not constitute, replace or satisfy a
native-speaker editorial review. Under approved D-027 (2026-09-08) the mandatory
pre-release native-Ukrainian editorial review is no longer a G4-A completion gate;
native/human review is now advisory/optional and must not be claimed as completed. A
paid or native-speaker spot-check is excluded from the current scope by Dalton's decision.

Counts, reconciled: **705 findings total** — 702 in the vocabulary bank (675 first pass +
27 spot-check, in 702 distinct entries = 39.4% of 1,784; severity 142 P0 / 314 P1 /
246 P2) plus 3 in Reading (`G4A-R-001`–`G4A-R-003`, not in the CSV). Both defect rates
are observed, not extrapolated: 675/1,784 = 37.8% for the full first pass, 27/70 = 38.6%
for a stratified sample of entries that pass judged clean. Those measure disjoint
populations; no bank-wide estimate is asserted. See the register §7.

Scope of correction: `web/vocabulary.js` **and** the three Reading family labels in
`scripts/build_reading_curriculum.py`. Writing Task 1 needs no changes.

Method: `docs/G4A_UKRAINIAN_QA_AUDIT_PLAN.md`. Register:
`docs/G4A_UKRAINIAN_QA_FINDINGS.md` (methodology, category patterns, worked examples —
**not** a per-entry P0 list). Decision record: D-026, status **Proposed**, pending
independent review and Dalton's sign-off. No content was changed by this pass — findings
are returned for routing per the established Claude Code/Codex correction protocol.

- `tests/g4a_ukrainian_deterministic.py` — **now PASSES (exit 0) on current `main`.**
  Its structural checks (inventory counts, Cyrillic presence, no corruption, collision
  ratchet, findings-register reconciliation) pass, and `G4A-V-001` is **resolved**:
  entries `SB-0208` (commence), `SB-0432` (embark) and `SB-1728` (commenced) were
  corrected in PR #3 and no longer share the circular gloss "Щоб почати, почніть."
  ("To begin, begin."). The earlier "fails by design (exit 1)" behaviour was retired
  once those three landed. Run first and last in every future G4-A session (this is what
  would catch drift like the `main`-merge discrepancy an earlier preflight found); any
  failure now is real drift.

**Blocker closed 2026-09-06:** `docs/G4A_UKRAINIAN_QA_FINDINGS.csv` is now in the
repository — 702 per-entry rows with `id, word, source, category, severity, issue,
proposed_correction, confidence`. It reconciles against every claim made about it:
702 distinct entry ids with no duplicates, all 702 present in `web/vocabulary.js`,
142 P0 / 314 P1 / 246 P2, and main-pass (675) and spot-check (27) sets that do not
overlap at all — the disjointness the count reconciliation assumes. The audit is now
reproducible from the repository alone. `tests/g4a_ukrainian_deterministic.py` asserts
all of it, so the register cannot drift from the register's own claims.

Category attribution is now complete: the 137 first-pass findings previously
unattributed are `other` 98, `russianism-calque` 24 and `register` 15. The former gap —
the 27 spot-check rows carrying no `proposed_correction` and no `confidence` — is
**closed by ticket T1 (2026-09-08)**: all 27 now carry a proposed_correction and a
confidence value (9 P1 + 18 P2), severity re-confirmed with no reclassification, so all
702 register rows are populated. T2-T4 and the isolated `SB-0773` structural correction
now account for every P1 item, including all P1 spot-check rows. The historical register
totals remain 142 P0 / 314 P1 / 246 P2, while executable closeout accounting reports
**0 unresolved P1 + 246 unresolved P2**. See `docs/G4A_P1_BATCH_STATUS.md` and
`tests/g4a_p1_closeout_accounting.py`.

**T5-A — learner flag / correction loop — implemented and validated (2026-09-09).**
D-027 replaced the mandatory native-Ukrainian editorial gate with AI linguistic QA plus a
learner-facing `Flag mistake / Це виглядає неправильно` correction loop; T5-A delivers that
loop. A keyboard-native `<details>/<summary>` control appears on all three G4-A
Ukrainian-content surfaces (vocabulary entries `ua`/`definitionUa`, Reading UA support,
Writing Task 1 UA support). Submitting captures a structured report into the canonical local
state (`ieltsC1UAEN.state.v1.contentFlags`: `id, kind, contentId, field, en, ua, note,
appVersion, createdAt`) bound to the surface's stable content id. Settings → "Flagged content ·
Позначені помилки" provides a review list, an explicit local-only privacy notice, Copy JSON and
Export JSON, empty/confirmation states, and the flags round-trip through the existing
Export/Import backup (`importData` normalises the new key for older backups) without disturbing
unrelated progress. The path is strictly local — no fetch/XHR/beacon/socket anywhere.
Artifacts: `web/app.js`, `web/styles.css`. Evidence: `tests/g4a_content_flag_static.py`,
`tests/g4a_content_flag_functional.py` (six-width responsive + keyboard + reload + round-trip),
`tests/g4a_ukrainian_deterministic.py` (UA UI ratchet 53 → 61). **This does not advance the
gate:** G4-A remains **CHANGES REQUESTED** and G5 remains **BLOCKED** — the T5-B fresh promotion
packet (zero unresolved P0/P1, re-verified end-to-end) is still outstanding. No G4-A PASS is
claimed; D-026/D-027 statuses are unchanged.

### G5 — Writing Task 2 — BLOCKED

Do not begin G5 until the G4 candidate release is independently reviewed and
approved. Minimum gate (`PROJECT_CHARTER.md` §9):

- ≥60 full prompts
- ≥100 micro-drills
- ≥15 annotated model responses
- ≥10 Band 6/7/8 comparison sets
- ≥12 timed simulations

Reuse the G4 shape: a Python generator producing `web/writing2_data.js`, an independent
validator that re-derives every check from the specification, a prose-claim QA pass, and
functional/responsive/accessibility suites covering every essay family rather than a
sample. The `.w1-visual` panel does not apply; Task 2 has no graphic.

---

## Defects

| ID | Severity | Status | Note |
|---|---|---|---|
| D4-001 | P2 | **Fixed** | Four Playwright tests hard-coded `/usr/bin/chromium` and could not launch off Linux, so the browser-driven gate evidence was not reproducible on the development machine. `tests/browser_env.py` resolves a Chromium binary portably; all four now pass. |
| D4-002 | P2 | **Fixed** | Task 1 exercise controls stayed disabled after an attempt, so "Try again" was impossible. |
| D4-003 | P3 | **Fixed** | `.field textarea` out-specified `.w1-draft`, leaving the drafting box 73px tall. |
| D4-004 | P3 | **Fixed** | `.question-card label{display:grid}` out-specified `.w1-opt`, stacking each radio above its option text. |
| D4-005 | P3 | **Fixed** | The chart axis caption collided with the top tick label. |
| QA-G4-001 | P3 | **Fixed** | The fact engine could not derive pairwise differences, rejecting genuinely grounded claims. |
| QA-G4-002 | P3 | **Fixed** | The literal string "Task 1" was read as the figure 1 during grounding checks. |
| D4-006 | P2 | **Fixed** | Grounding authorised any arithmetically derivable figure, including column totals and pairwise sums, so an item could look supported without being correct. Replaced by the canonical claim manifest (D-020). |
| D4-007 | P3 | **Fixed** | `.w1-chart{margin:0 -2px}` made every chart 4px wider than its parent's content box, so ancestors reported horizontal overflow. |
| D4-008 | P2 | **Fixed** | `.half`, `.third` and `.twoThird` only received a column span at 760px and above, so any non-`.card` grid child collapsed to one twelfth of the row on a phone: the band-lab annotation blocks became 28px slivers and the four vocabulary filters on Words became 14px slivers. Found by looking at a 375px screenshot, not by an assertion. Fixed in `web/styles.css`; `tests/responsive_check.py` now measures every grid child on all five primary routes at all six widths. |
| R1-001 | P1 | **Fixed** | Eighteen of 21 band samples were under the 150-word Academic Task 1 minimum, four of them labelled Strong (external review). All 21 are now 158-202 words. |
| R1-002 | P1 | **Fixed** | Mastery L4 and L5 could be reached with a 20-word response (external review). Both now require a response of at least `wordMinimum` words; underlength submissions log an error instead. |
| R1-003 | P2 | **Fixed** | Report-level grounding authorised a set of figures unbound to any entity, so two real values could be swapped between two series (external review). Replaced by sentence-scoped binding (D-021). |
| R1-004 | P2 | **Fixed** | The review packet named a candidate SHA that does not exist (external review). The candidate is now a tag, checked by `tests/release_integrity.py` (D-023). |
| R1-005 | P3 | **Fixed** | The Task 1 inventory printed `Completed 0+0` without naming its operands, and Reading foundation modules printed `foundation • undefined min` (external review). |
| R2-001 | P1 | **Fixed** | Five Band 6 teaching annotations contradicted the extended prose. The annotations now describe the final samples and carry executable presence/absence evidence rules (D-025). |
| R2-002 | P2 | **Fixed** | The canonical Band 8 line sample used a non-interleaved multi-entity `respectively` construction that allowed an ordered value swap. Canonical prose now bans the construction until ordered-pair parsing exists (D-024). |
| R2-003 | P2 | **Fixed** | Words overflowed the whole page at 320px and 375px because the migration filename could not wrap and the regression test measured document overflow only on Today. Notices now wrap; document and body widths are asserted after every route navigation. |
| R2-004 | P3 | **Fixed** | `Nothing holding it back` made an absolute claim stronger than the annotated evidence. The UI now says `Annotated criteria demonstrated` and explicitly bounds the statement to the criteria shown. |
| D4-009 | P2 | **Fixed** | Chromium exposed a 3px overflow on the 320px Task 1 family list: the three-column foundation `.module-item` could not shrink around its action button. Mobile module items now use two columns and place the action across the full row. |

Open P0: 0 · Open P1: 0 · Open P2: 0 · Open P3: 0

---

## Toolchain

Running the validation suite requires (see D-018):

- Python 3 with `jsonschema` and `playwright`
- any Chromium-family browser (override with `$IELTS_CHROMIUM`)

The application itself remains dependency-free static HTML/CSS/JS per D-014. Node is
needed only to assemble Claude Design mockups, not to run the app or its tests.

---

## Current Source Tree

Primary implementation:

- `web/index.html`
- `web/styles.css`
- `web/app.js`
- `web/data.js`
- `web/vocabulary.js`
- `web/reading_data.js`
- `web/writing1_data.js`

Schemas:

- `schemas/learner_state.schema.json`
- `schemas/module.schema.json`
- `schemas/exercise.schema.json`

Automated validation covers G2, G3 and G4 content, plus functional, responsive and
accessibility suites for Reading and Writing Task 1, and a whole-app responsive check.

---

## Known Constraints

- Do not deploy publicly yet.
- Do not reopen G0–G3 without an actual regression.
- Do not discard structured source in favor of editing only the monolithic release HTML.
- Do not remove the 1,784-word vocabulary bank.
- Do not grant mastery from page views.
- Do not use copyrighted commercial IELTS content.
- Practice guidance must not be labeled official scoring.

---

## Known Documentation Recovery

The earlier G0–G3 ZIP contains the source/test artifacts that were previously reported as missing from the local Claude folder.

The root canonical project documents were not present in that archive and have now been reconstructed from the approved context, ledger, and phase evidence.
