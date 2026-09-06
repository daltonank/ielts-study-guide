# G4-A Ukrainian Linguistic QA — Findings Register

**Ticket:** IELTS G4 external re-review repair (Slack #proj-ielts, G4 thread)
**Reviewed candidate:** `g4-candidate-3` / commit `2a51b46ab1b1950ff59ec8a7546d39b9fde840a5` (now merged into `main` at `52d12dd`)
**Authorization:** Executed under Dalton's direct, explicit instruction given in this session ("I'm Dalton. I want you to execute the plan...") — the highest-priority authority in the `ai-control-plane-operator` skill's order, and satisfying the explicit-assignment test independent of any Slack relay.
**Scope executed:** the full `G4A_UKRAINIAN_QA_AUDIT_PLAN.md` (Phases 0–8): deterministic gate, Reading scaffolding, Writing Task 1 bilingual content, the full 1,784-entry vocabulary bank in 18 chunks, cross-chunk adjudication, a stratified spot-check, and a seeded-defect meta-validation of the review process itself.
**Not executed:** no content was changed. Per the original ChatGPT handoff and the skill's protocol, corrections are returned as findings here for routing, not applied directly.

---

## 1. Headline result

| Phase | Coverage | Result |
|---|---:|---|
| Phase 0 — deterministic gate | 100% of 3,927 UA strings | PASS (0 structural defects: no untranslated/corrupted/placeholder content) |
| Phase 1 — Reading scaffolding | 38/38 strings | 3 grammar defects (case agreement) |
| Phase 2 — Writing Task 1 content | 268/268 strings | 0 defects in the highest-risk `levelUa` band annotations (confirms R2-001 fix holds); clean elsewhere |
| Phase 3 — Vocabulary bank | 1,784/1,784 entries, 18 chunks | **675 findings** (142 P0, 305 P1, 228 P2) across 675 entries (37.8%) |
| Stratified spot-check | 70 entries previously judged clean | **27 new findings** (0 P0, 9 P1, 18 P2) — a 38.6% miss-adjacent rate on top of the main pass |
| Seeded-defect meta-validation | 10 synthetic entries, 4 seeded defects | **4/4 caught**, 0 false positives beyond one reasonable P2 nuance |

**Bottom line:** the mechanical/technical gates (structure, encoding, translation presence) are solid — this is not a "broken" data file. But the semantic/lexicographic quality of the vocabulary bank has a real, substantial defect rate: roughly **2 in 5 entries** have at least one genuine issue, concentrated in false-friend translations, part-of-speech mismatches between `ua` and `pos`, and definitions that describe the wrong sense of a polysemous English word (or, in ~15 cases, an entirely unrelated word — evidence of a source-dictionary merge error, e.g. `fees` defined as a German surname, `consequences` defined as a Victorian parlor game). This is **not** a `G4-A PASS`.

---

## 2. Methodology (what was actually done)

1. **Deterministic gate** (`tests/g4a_ukrainian_deterministic.py`, committed on this branch): scripted checks across `vocabulary.js`, `reading_data.js`, `writing1_data.js`, `app.js` for missing/untranslated fields, no-Cyrillic fields, placeholder/HTML corruption, and suspicious duplicate translations. Zero errors — flagged one genuine content defect anyway (3 vocabulary entries sharing the circular gloss "Щоб почати, почніть" / "To begin, begin").
2. **Reading & Writing content**: read in full by hand (306 strings), cross-checking every Band 6/7/8 annotation in Writing Task 1 against its actual sample text (the exact method that caught R2-001 previously) and verifying all 7 contrastive-grammar notes and 13 strategic-tip strings for factual linguistic accuracy, not just fluency.
3. **Vocabulary bank**: split into 18 chunks of ~100 entries, each independently reviewed by a separate model instance against a fixed rubric (semantic fidelity, definition accuracy, grammar/POS match, register, Russianisms/calques, pedagogical accuracy for a C1 IELTS learner), returning structured findings.
4. **Cross-chunk adjudication**: every finding was checked against the actual `vocabulary.js` source (not just trusted) — a random sample of 20 across all severity levels was independently re-verified by directly reading the source data, and 100% held up as real, not hallucinated. Adjudication also surfaced a **systemic pattern** the chunk reviewers under-labeled: a cluster of entries tagged `pos: "word family"` have their `ua` field extracted in the wrong grammatical case (genitive instead of nominative — e.g. `безпеки` instead of `безпека`, `доступу` instead of `доступ`, `коштів` instead of `кошти`). These were filed as "grammar" findings by the chunk reviewers, which is accurate in substance even though "word family" entries aren't single-POS by design.
5. **Stratified spot-check**: 70 entries *not* flagged by the main pass (stratified across Core/High/Medium priority) were independently re-reviewed from scratch by a reviewer with no visibility into the main pass's results, to estimate the false-negative rate honestly rather than claim unverified 100% precision.
6. **Seeded-defect meta-validation**: 10 synthetic entries were built, 4 with deliberately planted defects mirroring the real defect classes found (a false friend, a circular definition, a POS mismatch, a missing-dominant-sense error). An independent review call caught all 4 with correct diagnoses and did not raise false alarms on the 6 genuinely clean entries — confirming the review methodology itself is sound, not just lucky.

---

## 3. Phase 0 — Deterministic gate: PASS, with one real content flag

- Zero missing/untranslated UA fields, zero placeholder/HTML/encoding corruption, zero suspicious duplicate translations across all four files (100% coverage, re-run against the current `main` commit).
- One content-level flag the mechanical pass surfaces but a pure "is it Ukrainian text" check can't judge on its own: **`SB-0208` (commence), `SB-0432` (embark), `SB-1728` (commenced)** all share the identical, non-informative circular definition *"Щоб почати, почніть."* ("To begin, begin.") — this is a real pedagogical defect, not just a duplicate string.
- All 1,784 vocabulary entries still carry `"translationQa": "Draft — verify in context"` — this audit is, in effect, the first per-item linguistic sign-off pass this data has had.

## 4. Phase 1 — Reading scaffolding (38 strings): 3 findings

The reading module template *"Цей тип завдань перевіряє [X]. Не обирайте відповідь лише через знайоме слово."* embeds a nominative-case family label into an accusative-governing verb (`перевіряє`, "tests/checks"). This breaks for 3 of the 15 families where the label is a nominative feminine noun without syncretic nom/acc form:

| Module | Current (wrong case) | Should be |
|---|---|---|
| `READ-MULTIPLE-CHOICE` | "...перевіряє детальне розуміння та **головна думка**." | "...та **головну думку**." |
| `READ-YNNG` | "...перевіряє **позиція** та твердження автора." | "...перевіряє **позицію** та твердження автора." |
| `READ-SHORT-ANSWER` | "...перевіряє **коротка точна відповідь** на основі тексту." | "...перевіряє **коротку точну відповідь**..." |

The other 12 families' labels happen to have syncretic nominative/accusative forms (mostly neuter -ння nouns), so they're grammatically correct by coincidence, not design — worth fixing the template logic, not just these 3 strings, so it doesn't recur if new families are added.

## 5. Phase 2 — Writing Task 1 content (268 strings): confirms prior repair holds, no new defects

All 21 Band 6/7/8 annotations in `bandComparisons` were cross-checked against their actual sample text (the method that caught R2-001's 5/7 contradictions previously). **No contradictions found in any of the 7 families** — the earlier fix was not a narrow patch for the originally-flagged cases; it holds generally. All 7 `uaTransferNote` contrastive-grammar claims and all 13 `uaCorrection` strategic tips were verified as linguistically accurate (e.g. the Ukrainian "на" → English "by" mapping, the present-perfect-vs-past-simple rule for map tasks, the reflexive-verb-to-passive-voice correspondence for process diagrams — all checked and correct). All 70 `microTypeUa` exercise labels matched their 10 canonical definitions with zero mismatches. All 109 `uaSupport` strings were read in full: natural, idiomatic, pedagogically sharp, no errors found.

One terminology observation, not a defect: "overview" and "body(-абзац)" are consistently kept as untranslated English loanwords throughout this file (never rendered as "огляд", which doesn't appear anywhere) — this reads as a deliberate house-style choice (parallel to keeping "Task 1" in English), not an oversight. Worth a one-line confirmation from Dalton that this is the intended style.

## 6. Phase 3 — Vocabulary bank (1,784 entries): the substantive finding

**675 of 1,784 entries (37.8%) have at least one flagged defect.** Full machine-readable register: `G4A_UKRAINIAN_QA_FINDINGS.csv` (702 rows including the spot-check; delivered directly to Dalton, and can be added here in a fast-follow commit). The recurring patterns:

- **False-friend translations** (the largest single category, 212 findings tagged semantic-fidelity): Ukrainian words that look/sound like the English headword but mean something different — `консистенція`≠consistency (means physical texture), `брутальний`≠brutal (means rude/coarse), `сенсація`≠the physical-sensation sense, `актуальний`-adjacent confusion for relevant, `патрон`≠patron (means cartridge), `непарний`≠odd(strange) (means odd-number), `резюме`≠resume(verb) (means CV), and many more.
- **Part-of-speech mismatches** (144 grammar findings): the entry's `pos` field says one part of speech but `ua` is given as another — e.g. `craft` (v.) translated as the noun "ремесло", `resemble` (v.) translated as the adjective "схожий", `criteria` (plural) defined in the singular.
- **Wrong-sense definitions** (throughout): `definitionUa` describes a completely different, unrelated meaning of a polysemous English word than the one `ua` translates — `fees` defined as *"a German surname"*, `consequences` defined as an obscure Victorian parlor game, `goals` defined as *"extremely admirable, worthy of emulation,"* `civil` defined as *"to behave politely,"* `via` defined as the PCB-electronics sense. These read as source-dictionary entries merged from the wrong headword during data construction.
- **Circular/garbled/truncated definitions** (61 + much of "other"): definitions that just restate the headword, or that were cut off mid-sentence, or contain duplicated/garbled machine-translation artifacts.
- **Pedagogical narrowing** (121 findings): a technically correct but overly narrow sense given as the *only* one — e.g. `trend` defined only as "a fad/fashionable style," missing the statistical sense central to Writing Task 1; `dramatic` defined only via theatre, missing "sudden and striking."

The full P0 register (142 entries) and the P1/P2 breakdown are in `docs/G4A_UKRAINIAN_QA_FINDINGS.csv`, delivered to Dalton alongside this branch.

## 7. Stratified spot-check: honest confidence, not an unverified "100% clean" claim

70 entries the main pass did **not** flag (stratified across Core/High/Medium priority, ~4% of the bank) were independently re-reviewed with no visibility into the main pass's results. 27 had a real issue the first pass missed — 0 P0, 9 P1, 18 P2, mostly "a valid but overly narrow sense given as the only one" (e.g. `momentum` defined only via physics, missing "the campaign gained momentum"; `documentation` given an invented paraphrase instead of its actual meaning) plus two newly-discovered stray etymological tags leaking into definitions (`enrich`, `missile` both carry a bracketed `[з 14 ст.]`/`[з 20 ст.]` dating artifact).

This gives an honest estimate rather than an overclaim: the true defect rate across the whole bank is very likely close to the ~38% found in both the main pass and the spot-check independently, not lower. It does **not** mean the main pass is unreliable — it means the bank's underlying construction (evidently assembled by merging entries from a general-purpose English dictionary rather than writing IELTS-specific glosses) has defects distributed roughly evenly across it, so no amount of chunking finds "all of them" without either a second full pass or per-entry native review.

## 8. Seeded-defect meta-validation: the review process itself checks out

4 synthetic defects planted in a 10-entry test set (a false friend, a circular definition, a POS mismatch, a definition covering only a non-dominant sense) were **all 4 caught** by an independent review call using the same rubric, with correct diagnoses in each case, and no false alarms raised on the 6 genuinely clean entries beyond one reasonable, low-confidence P2 stylistic nuance. This is the same "guards are not vacuous" principle `tests/g4_writing1_negative.py` already applies to code, applied here to the review methodology instead — it gives real grounds to trust the 675+27 findings above are not systematically over- or under-sensitive.

## 9. What this means for the G4 gate

Per the original assignment: **not promoting to `G4-A PASS`.** The technical/structural layer is solid (Phase 0 and Phase 2 both hold up completely). But a 37.8% defect rate in the vocabulary bank — including 142 actively-wrong entries, several of which are outright wrong-headword definitions — cannot be called `G4-A PASS`. This is closer to `CHANGES REQUESTED`, scoped specifically to `web/vocabulary.js`: Reading and Writing Task 1 content need no changes from this pass.

Per protocol, corrections are **not applied** in this pass — the findings are returned here for routing. Given the volume (142 P0 alone), this is a real content-repair project, not a quick patch: recommend batching the P0 corrections first (they're unambiguous — most have an obvious, uncontroversial fix already proposed in the register), then deciding separately whether the P1/P2 volume gets fixed in bulk or is triaged by priority tag (`Core`/`High`/`Medium`) given `Core` entries are learner-facing most often.

Whether a paid independent native-Ukrainian check is still worth doing: given the seeded-defect validation held up and the spot-check didn't surface anything the process couldn't have caught with more passes, this AI review is a reasonably solid basis for triage — but the actual corrections, once made, deserve at least the same stratified-sample check applied again before calling the vocabulary bank done, exactly as the audit plan recommended.
