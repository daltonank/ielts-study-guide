# G4-A Ukrainian Linguistic QA — Findings Register

**Ticket:** IELTS G4 external re-review repair (Slack #proj-ielts, G4 thread)
**Reviewed candidate:** `g4-candidate-3` / commit `2a51b46ab1b1950ff59ec8a7546d39b9fde840a5` (now merged into `main` at `52d12dd`)
**Authorization:** Executed under Dalton's direct, explicit instruction given in this session ("I'm Dalton. I want you to execute the plan...") — the highest-priority authority in the `ai-control-plane-operator` skill's order, and satisfying the explicit-assignment test independent of any Slack relay.
**Scope executed:** the full audit plan, now committed alongside this register at [`docs/G4A_UKRAINIAN_QA_AUDIT_PLAN.md`](G4A_UKRAINIAN_QA_AUDIT_PLAN.md) (Phases 0–3 plus adjudication, spot-check and meta-validation): deterministic gate, Reading scaffolding, Writing Task 1 bilingual content, the full 1,784-entry vocabulary bank in 18 chunks, cross-chunk adjudication, a stratified spot-check, and a seeded-defect meta-validation of the review process itself.
**Not executed:** no content was changed. Per the original ChatGPT handoff and the skill's protocol, corrections are returned as findings here for routing, not applied directly.

> **This is an AI linguistic QA pass.** It does not constitute, replace, or satisfy a native-speaker editorial review. See §9.

---

## 1. Headline result

| Phase | Coverage | Result |
|---|---:|---|
| Phase 0 — deterministic gate | 100% of 3,927 UA strings | **FAILS BY DESIGN (exit 1)** on `G4A-V-001`; 0 structural defects otherwise (no untranslated/corrupted/placeholder content) |
| Phase 1 — Reading scaffolding | 38/38 strings | 3 grammar defects (case agreement) |
| Phase 2 — Writing Task 1 content | 268/268 strings | 0 defects in the highest-risk `levelUa` band annotations (confirms R2-001 fix holds); clean elsewhere |
| Phase 3 — Vocabulary bank | 1,784/1,784 entries, 18 chunks | **675 findings** (142 P0, 305 P1, 228 P2) across 675 entries (37.8% of the bank) |
| Stratified spot-check | 70 entries the main pass judged clean | **27 further findings** (0 P0, 9 P1, 18 P2) in 27 distinct entries — 27/70 = 38.6% of that sample |
| Seeded-defect meta-validation | 10 synthetic entries, 4 seeded defects | **4/4 caught**, 0 false positives beyond one reasonable P2 nuance |
| **Total** | — | **705 findings: 702 vocabulary (702 distinct entries, 39.4% of the bank) + 3 Reading** |

**Bottom line:** the mechanical/technical gates (structure, encoding, translation presence) are solid — this is not a "broken" data file. But the semantic/lexicographic quality of the vocabulary bank has a substantial observed defect rate, concentrated in false-friend translations, part-of-speech mismatches between `ua` and `pos`, and definitions that describe the wrong sense of a polysemous English word (or, in ~15 cases, an entirely unrelated word — evidence of a source-dictionary merge error, e.g. `fees` defined as a German surname, `consequences` defined as a Victorian parlor game). Two observed rates, stated separately because they measure different things and neither has been converted into a validated bank-wide estimate (see §7): **675/1,784 = 37.8%** of entries flagged by the full first pass, and **27/70 = 38.6%** of a stratified sample drawn from the entries that pass judged clean. This is **not** a `G4-A PASS`.

---

## 1a. Count reconciliation

| Quantity | Value | Basis |
|---|---:|---|
| Vocabulary entries in bank | 1,784 | `web/vocabulary.js`, unchanged since G2 |
| First-pass findings | 675 | 142 P0 + 305 P1 + 228 P2 |
| Spot-check findings | 27 | 0 P0 + 9 P1 + 18 P2 |
| **Vocabulary findings total** | **702** | 675 + 27 — the row count of `G4A_UKRAINIAN_QA_FINDINGS.csv` |
| **Distinct vocabulary entries affected** | **702** | one finding per entry, and the two sets are disjoint by construction: the spot-check sampled only entries the first pass did not flag |
| Share of bank affected | 39.4% | 702 / 1,784 |
| Severity totals across both passes | 142 P0 · 314 P1 · 246 P2 | 142+314+246 = 702 |
| Reading findings | 3 | §4 — **not** in the CSV, and not part of the 702 |
| **All findings, all files** | **705** | 702 + 3 |

Two things this table deliberately does **not** claim:

- **No bank-wide defect estimate.** See §7.

### Category attribution — complete as of 2026-09-06

Counted from the landed CSV, first pass only (n = 675). The 137 findings this register
previously left unattributed are the last three rows:

| Category | Findings |
|---|---:|
| `semantic-fidelity` (false friends, wrong sense) | 212 |
| `grammar` (part-of-speech mismatch, agreement) | 144 |
| `pedagogical-accuracy` (narrowing) | 121 |
| `other` | 98 |
| `circular-definition` | 61 |
| `russianism-calque` | 24 |
| `register` | 15 |
| **Total** | **675** |

Across both passes (n = 702) the totals are `semantic-fidelity` 216, `grammar` 145,
`pedagogical-accuracy` 133, `other` 100, `circular-definition` 67,
`russianism-calque` 26, `register` 15.

---

## 2. Methodology (what was actually done)

1. **Deterministic gate** (`tests/g4a_ukrainian_deterministic.py`, committed on this branch): scripted checks across `vocabulary.js`, `reading_data.js`, `writing1_data.js`, `app.js` for missing/untranslated fields, no-Cyrillic fields, placeholder/HTML corruption, and suspicious duplicate translations. Zero structural errors, but the gate exits 1 by design on the one genuine content defect it flags (`G4A-V-001`: 3 vocabulary entries sharing the circular gloss "Щоб почати, почніть" / "To begin, begin") and stays red until all three entries are corrected.
2. **Reading & Writing content**: read in full by hand (306 strings), cross-checking every Band 6/7/8 annotation in Writing Task 1 against its actual sample text (the exact method that caught R2-001 previously) and verifying all 7 contrastive-grammar notes and 13 strategic-tip strings for factual linguistic accuracy, not just fluency.
3. **Vocabulary bank**: split into 18 chunks of ~100 entries, each independently reviewed by a separate model instance against a fixed rubric (semantic fidelity, definition accuracy, grammar/POS match, register, Russianisms/calques, pedagogical accuracy for a C1 IELTS learner), returning structured findings.
4. **Cross-chunk adjudication**: every finding was checked against the actual `vocabulary.js` source (not just trusted) — a random sample of 20 across all severity levels was independently re-verified by directly reading the source data, and 100% held up as real, not hallucinated. Adjudication also surfaced a **systemic pattern** the chunk reviewers under-labeled: a cluster of entries tagged `pos: "word family"` have their `ua` field extracted in the wrong grammatical case (genitive instead of nominative — e.g. `безпеки` instead of `безпека`, `доступу` instead of `доступ`, `коштів` instead of `кошти`). These were filed as "grammar" findings by the chunk reviewers, which is accurate in substance even though "word family" entries aren't single-POS by design.
5. **Stratified spot-check**: 70 entries *not* flagged by the main pass (stratified across Core/High/Medium priority) were independently re-reviewed from scratch by a reviewer with no visibility into the main pass's results, to estimate the false-negative rate honestly rather than claim unverified 100% precision.
6. **Seeded-defect meta-validation**: 10 synthetic entries were built, 4 with deliberately planted defects mirroring the real defect classes found (a false friend, a circular definition, a POS mismatch, a missing-dominant-sense error). An independent review call caught all 4 with correct diagnoses and did not raise false alarms on the 6 genuinely clean entries — confirming the review methodology itself is sound, not just lucky.

---

## 3. Phase 0 — Deterministic gate: FAILS BY DESIGN (exit 1) on one real content flag

- Zero missing/untranslated UA fields, zero placeholder/HTML/encoding corruption, zero suspicious duplicate translations across all four files (100% coverage, re-run against the current `main` commit).
- One content-level flag the mechanical pass surfaces but a pure "is it Ukrainian text" check can't judge on its own: **`SB-0208` (commence), `SB-0432` (embark), `SB-1728` (commenced)** all share the identical, non-informative circular definition *"Щоб почати, почніть."* ("To begin, begin.") — this is a real pedagogical defect, not just a duplicate string.
- All 1,784 vocabulary entries still carry `"translationQa": "Draft — verify in context"` — this audit is, in effect, the first per-item linguistic sign-off pass this data has had.

## 4. Phase 1 — Reading scaffolding (38 strings): 3 findings

The reading module template *"Цей тип завдань перевіряє [X]. Не обирайте відповідь лише через знайоме слово."* embeds a nominative-case family label into an accusative-governing verb (`перевіряє`, "tests/checks"). This breaks for 3 of the 15 families where the label is a nominative feminine noun without syncretic nom/acc form:

| ID | Severity | Module | Current (wrong case) | Correction |
|---|---|---|---|---|
| `G4A-R-001` | P1 | `READ-MULTIPLE-CHOICE` | "...перевіряє детальне розуміння та **головна думка**." | "...та **головну думку**." |
| `G4A-R-002` | P1 | `READ-YNNG` | "...перевіряє **позиція** та твердження автора." | "...перевіряє **позицію** та твердження автора." |
| `G4A-R-003` | P1 | `READ-SHORT-ANSWER` | "...перевіряє **коротка точна відповідь** на основі тексту." | "...перевіряє **коротку точну відповідь**..." |

**Adjudication (2026-09-06).** All three re-verified directly against `web/reading_data.js` at `139f692` by extracting every Cyrillic-bearing string and inspecting the 15 that contain `перевіряє`; all three reproduce exactly as recorded. Severity **P1**: learner-visible grammatical errors in scaffolding copy, but they do not change the meaning of the guidance or make any exercise unanswerable, so they are not P0.

Root cause confirmed in the generator, not the data: `scripts/build_reading_curriculum.py:401` composes this string as `f'Цей тип завдань перевіряє {ua_skill}. …'`, interpolating `FAMILY_META[fam][3]` — a set of labels written in the nominative — into a slot governed by the accusative verb `перевіряє`. `ua_skill` has exactly one consumer, this f-string, so the labels can be stored in the case the sentence actually requires.

Checked all 15 labels, not only the three that broke:

- **3 need correction** — the ones above, where a feminine adjective or noun has a distinct accusative form (`головна думка` → `головну думку`; `позиція` → `позицію`; `коротка точна` → `коротку точну`, the noun `відповідь` being third-declension feminine and identical in both cases).
- **12 are already correct, by coincidence rather than design** — they head on neuter `-ння` nouns (`розрізнення`, `визначення`, `зіставлення`, `поєднання`, `відтворення`, `розпізнавання`, `порівняння`, `відстеження`, `ставлення`) or masculine inanimates (`пошук`, `вибір`, `підтекст`), all of which are syncretic in the nominative and accusative. A new family whose label begins with a feminine noun would reintroduce the bug silently.

**Status: open — fix assigned to Phase 2.** These are content corrections, so they land on the correction branch with the vocabulary fixes rather than in this audit/evidence PR, via the generator plus a regression check that fails if any `uaSupport` string places a nominative-only feminine form after `перевіряє`.

## 5. Phase 2 — Writing Task 1 content (268 strings): confirms prior repair holds, no new defects

All 21 Band 6/7/8 annotations in `bandComparisons` were cross-checked against their actual sample text (the method that caught R2-001's 5/7 contradictions previously). **No contradictions found in any of the 7 families** — the earlier fix was not a narrow patch for the originally-flagged cases; it holds generally. All 7 `uaTransferNote` contrastive-grammar claims and all 13 `uaCorrection` strategic tips were verified as linguistically accurate (e.g. the Ukrainian "на" → English "by" mapping, the present-perfect-vs-past-simple rule for map tasks, the reflexive-verb-to-passive-voice correspondence for process diagrams — all checked and correct). All 70 `microTypeUa` exercise labels matched their 10 canonical definitions with zero mismatches. All 109 `uaSupport` strings were read in full: natural, idiomatic, pedagogically sharp, no errors found.

One terminology observation, not a defect: "overview" and "body(-абзац)" are consistently kept as untranslated English loanwords throughout this file (never rendered as "огляд", which doesn't appear anywhere) — this reads as a deliberate house-style choice (parallel to keeping "Task 1" in English), not an oversight. Worth a one-line confirmation from Dalton that this is the intended style.

## 6. Phase 3 — Vocabulary bank (1,784 entries): the substantive finding

**675 of 1,784 entries (37.8%) were flagged by the first pass.** The recurring patterns:

- **False-friend translations** (the largest single category, 212 findings tagged semantic-fidelity): Ukrainian words that look/sound like the English headword but mean something different — `консистенція`≠consistency (means physical texture), `брутальний`≠brutal (means rude/coarse), `сенсація`≠the physical-sensation sense, `актуальний`-adjacent confusion for relevant, `патрон`≠patron (means cartridge), `непарний`≠odd(strange) (means odd-number), `резюме`≠resume(verb) (means CV), and many more.
- **Part-of-speech mismatches** (144 grammar findings): the entry's `pos` field says one part of speech but `ua` is given as another — e.g. `craft` (v.) translated as the noun "ремесло", `resemble` (v.) translated as the adjective "схожий", `criteria` (plural) defined in the singular.
- **Wrong-sense definitions** (throughout): `definitionUa` describes a completely different, unrelated meaning of a polysemous English word than the one `ua` translates — `fees` defined as *"a German surname"*, `consequences` defined as an obscure Victorian parlor game, `goals` defined as *"extremely admirable, worthy of emulation,"* `civil` defined as *"to behave politely,"* `via` defined as the PCB-electronics sense. These read as source-dictionary entries merged from the wrong headword during data construction.
- **Circular/garbled/truncated definitions** (61 + much of "other"): definitions that just restate the headword, or that were cut off mid-sentence, or contain duplicated/garbled machine-translation artifacts.
- **Pedagogical narrowing** (121 findings): a technically correct but overly narrow sense given as the *only* one — e.g. `trend` defined only as "a fad/fashionable style," missing the statistical sense central to Writing Task 1; `dramatic` defined only via theatre, missing "sudden and striking."

### First-pass category counts (asserted by the deterministic gate)

Counted from the landed CSV, first pass only (n = 675). Every first-pass finding
carries a non-blank category. These are the numbers `tests/g4a_ukrainian_deterministic.py`
now asserts against the CSV, so this section cannot drift from the register:

| Category | Findings (first pass, n=675) |
|---|---:|
| `semantic-fidelity` | 212 |
| `grammar` | 144 |
| `pedagogical-accuracy` | 121 |
| `other` | 98 |
| `circular-definition` | 61 |
| `russianism-calque` | 24 |
| `register` | 15 |
| **Total** | **675** |

Across both passes (n = 702) the totals are `semantic-fidelity` 216, `grammar` 145,
`pedagogical-accuracy` 133, `other` 100, `circular-definition` 67, `russianism-calque` 26,
`register` 15 (see §1a). The deterministic gate asserts both breakdowns.

### Status of the per-entry register — landed 2026-09-06

The per-entry register is now committed at [`docs/G4A_UKRAINIAN_QA_FINDINGS.csv`](G4A_UKRAINIAN_QA_FINDINGS.csv): 702 rows, columns `id, word, source, category, severity, issue, proposed_correction, confidence`. This document remains the methodology, category patterns and worked examples; the CSV is the per-entry record, including all 142 P0 entries with proposed corrections.

It was verified on landing rather than accepted on assertion, and reconciles with every claim this register makes about it:

| Check | Result |
|---|---|
| Row count | 702 |
| Distinct entry ids | 702 — no duplicates, so one finding per entry as claimed |
| Ids resolving in `web/vocabulary.js` | 702 / 702 |
| Severity split | 142 P0 · 314 P1 · 246 P2 |
| Source split | 675 main-pass · 27 spot-check |
| **Overlap between the two sets** | **0** — the disjointness §1a depends on |
| Spot-check severity | 9 P1 · 18 P2 · 0 P0 |
| P0 rows drawn from the first pass only | yes, 142 / 142 |

`tests/g4a_ukrainian_deterministic.py` asserts all of the above, so the CSV cannot drift away from the claims made about it without failing the gate.

**One real gap remains:** the 27 spot-check rows carry an empty `proposed_correction` and an empty `confidence`. They record what the first pass missed, not what to do about it, and the corrections for those entries still have to be written. The other 675 rows all carry a proposed correction, with confidence recorded as high (325), medium (332) or low (18).

## 7. Stratified spot-check: honest confidence, not an unverified "100% clean" claim

70 entries the main pass did **not** flag (stratified across Core/High/Medium priority, ~4% of the bank) were independently re-reviewed with no visibility into the main pass's results. 27 had a real issue the first pass missed — 0 P0, 9 P1, 18 P2, mostly "a valid but overly narrow sense given as the only one" (e.g. `momentum` defined only via physics, missing "the campaign gained momentum"; `documentation` given an invented paraphrase instead of its actual meaning) plus two newly-discovered stray etymological tags leaking into definitions (`enrich`, `missile` both carry a bracketed `[з 14 ст.]`/`[з 20 ст.]` dating artifact).

**Correction to an earlier reading of this result.** A previous version of this register argued that 27/70 "confirms the true defect rate is close to 38%." That inference is invalid, and it is wrong in the direction that flatters the audit. The 70 entries were drawn *only* from the 1,109 the first pass judged clean, so a 38.6% hit rate inside that pool cannot corroborate the 37.8% rate measured across the whole bank — the two rates describe disjoint populations. If anything it points the other way: a miss rate that high among supposedly-clean entries implies the bank-wide rate is materially **higher** than 37.8%, not equal to it.

What this register therefore states is the observed rates only, per the review instruction to avoid unfounded extrapolation:

- **675/1,784 (37.8%)** — entries flagged by the full first pass.
- **27/70 (38.6%)** — entries flagged in a stratified sample of those the first pass judged clean.
- **0/70** — P0-severity findings in that sample. The first pass appears to have caught the severe cases; what it missed skews mild (18 of 27 were P2).

A naive projection of the 38.6% miss rate across all 1,109 unflagged entries would put the bank-wide figure near 60%. **This register does not assert that number**, and it should not be quoted as a finding. It rests on a sample that was stratified by priority tag rather than randomised, n=70 (~6% of the unflagged pool), reviewed in a single pass with no second adjudication, and counting any-severity findings — and no confidence interval was computed. Producing a defensible bank-wide estimate needs a documented estimator and sampling basis that this audit did not set out to build.

What the spot-check does establish, without any estimator: the first pass is **not** exhaustive, its clean verdicts are not evidence of correctness, and "the remaining 1,109 entries are fine" is an unsupported claim. It does not mean the first pass is unreliable about what it *did* flag — that was separately verified (§2.4). The likeliest reading is that the bank's underlying construction (evidently assembled by merging entries from a general-purpose English dictionary rather than writing IELTS-specific glosses) distributes defects fairly evenly, so no single chunked pass finds all of them.

## 8. Seeded-defect meta-validation: the review process itself checks out

4 synthetic defects planted in a 10-entry test set (a false friend, a circular definition, a POS mismatch, a definition covering only a non-dominant sense) were **all 4 caught** by an independent review call using the same rubric, with correct diagnoses in each case, and no false alarms raised on the 6 genuinely clean entries beyond one reasonable, low-confidence P2 stylistic nuance. This is the same "guards are not vacuous" principle `tests/g4_writing1_negative.py` already applies to code, applied here to the review methodology instead — it gives real grounds to trust the 675+27 findings above are not systematically over- or under-sensitive.

## 9. What this means for the G4 gate

Per the original assignment: **not promoting to `G4-A PASS`.** The technical/structural layer is solid (Phase 0 finds zero structural defects — though its gate is red by design on `G4A-V-001` until all three entries are corrected — and Phase 2 holds up completely). But an observed 37.8% first-pass defect rate in the vocabulary bank — including 142 actively-wrong entries, several of which are outright wrong-headword definitions — cannot be called `G4-A PASS`.

**Scope of `G4-A CHANGES REQUESTED`: `web/vocabulary.js` *and* the Reading family labels in `scripts/build_reading_curriculum.py` → `web/reading_data.js`.** An earlier version of this register, of `DECISIONS.md` D-026 and of the PR description described the scope as `web/vocabulary.js` only, while §4 of this same document recorded three Reading defects — a direct self-contradiction, corrected here. Writing Task 1 content is the only area that needs no changes from this pass.

Per protocol, corrections are **not applied** in this pass — the findings are returned here for routing. Given the volume (142 P0 alone), this is a real content-repair project, not a quick patch: recommend batching the P0 corrections first (they're unambiguous — most have an obvious, uncontroversial fix already proposed in the register), then deciding separately whether the P1/P2 volume gets fixed in bulk or is triaged by priority tag (`Core`/`High`/`Medium`) given `Core` entries are learner-facing most often.

### What this review is, and what it is not

This is an **AI linguistic QA pass**, and it stays labelled that way in every document it touches. Dalton has excluded a paid or native-speaker editorial spot-check from the current scope, so no human-language review stands behind these findings; validation from here is a second AI pass plus a fresh blind sample of entries classified clean.

That decision is recorded, not argued with, but its consequence should be stated plainly rather than left implied: the seeded-defect meta-validation (§8) shows the *method* catches planted defects of the classes it was designed for, and the adjudication sample (§2.4) shows the flagged findings are real. Neither establishes that the corrections written for those findings are idiomatic, register-appropriate Ukrainian — that is a different claim, and the same system is on both sides of it. Nothing in this register may be read as satisfying the original human-native editorial gate, which remains separate and unmet.

Concretely, before `G4-A PASS` is declared: re-run the full stratified-sample check against the corrected bank rather than re-reading only the changed lines, and keep any P2 findings open and reported rather than closed for tidiness.
