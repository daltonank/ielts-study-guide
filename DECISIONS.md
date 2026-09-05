# DECISIONS.md

This file records approved project decisions. Do not convert ordinary implementation details into permanent product policy.

---

## D-014 — Keep active development local HTML

**Date:** 2026-09-04  
**Status:** Active

### Decision
Continue development against the local HTML implementation.

Public deployment/reconciliation will occur only after the local curriculum build reaches the approved release stage.

### Rationale
Separating curriculum implementation from deployment reduces regression risk and avoids repeatedly reconciling an unfinished public build.

### Implications
- do not overwrite the public site;
- do not simplify the current local build to match the older public version;
- preserve local-first static architecture during the active build unless explicitly superseded.

---

## Standing constraints already established by passed gates

These are not new decisions; they summarize existing approved behavior:

- the primary mobile navigation remains Today / Skills / Practice / Words / Progress;
- language support uses EN / UA+EN / UA Help;
- learner state remains local-first;
- mastery is evidence-based;
- G2 vocabulary source count is 1,784 normalized records;
- original/legal training content is preferred over commercial IELTS reproduction;
- phase completion requires gate evidence.

---

## D-015 — Writing Task 1 mastery thresholds

**Date:** 2026-09-04
**Status:** Active

### Decision
Writing Task 1 mastery uses the six-level global scale with these skill-specific thresholds, recorded in `window.WRITING1_DATA.masteryRules`:

- **L1 Introduced** — the family lesson has been opened and explicitly marked as introduced.
- **L2 Guided** — at least 50% across the family's four guided micro-exercises.
- **L3 Independent** — at least 75% across the family's three independent micro-exercises.
- **L4 Timed** — at least 75% across the timed micro-exercises, *and* at least one full prompt submitted inside its 20-minute limit with the self-review checklist completed.
- **L5 Mastered** — at least 85% across three or more distinct exercise sets on at least two different dates, including the mastery-mode exercise, plus at least one timed full response.

### Rationale
`PRODUCT_SPEC.md` §4 sets the Reading precedent (L2 ≥50%, L3 ≥75%, L4 timed + ≥75%, L5 ≥85% across ≥3 sets on ≥2 dates) and explicitly allows other academies to define equivalent skill-specific thresholds. Task 1 differs from Reading in one respect that matters: the terminal skill is *producing* a response, not selecting an answer. L4 and L5 therefore additionally require a produced, timed response, so mastery cannot be reached by selected-answer work alone.

### Implications
- Opening a lesson never advances mastery beyond L1.
- The written response is self-assessed against a checklist; no band is computed from it (see D-016 and `PROJECT_CHARTER.md` §4.9).
- The thresholds are data, not code, so G9's adaptive engine can read them rather than re-deriving them.

---

## D-016 — Writing Task 1 error taxonomy

**Date:** 2026-09-04
**Status:** Active

### Decision
Writing Task 1 classifies errors into twelve categories: data misreading, invalid or unsupported comparison, missing or weak overview, list-like description without synthesis, tense misuse, unsupported causal claim, personal opinion in Task 1, imprecise quantity language, poor paragraph organisation, timing failure, article/preposition transfer error, and lexical variation that distorts the data.

Each category carries an English name, a Ukrainian name, a description, a correction and a Ukrainian correction, and every scored item is tagged with exactly one.

### Rationale
`CLAUDE.md` §15 proposes ten categories. Two were added because they are distinct failure modes with distinct repairs, and because they are the two most productive categories for this specific learner:

- **article_preposition_transfer** — Ukrainian has no articles, and the data prepositions (`rise to` vs `rise by`, `account for`) are fixed. `CURRICULUM_SPEC.md` §6 explicitly requires training "common Ukrainian-speaker grammar and article/preposition issues", which none of the ten proposed categories covers.
- **lexical_distortion** — `CURRICULUM_SPEC.md` §6 separately requires "lexical variation without data distortion". This is not the same failure as *imprecise quantity language*: one is choosing a synonym that changes the magnitude or the direction, the other is choosing an approximation that misstates the size.

The categories are shaped like the Reading taxonomy so that `recommendation()` and the shared Error Log consume them without special-casing.

### Implications
- No existing Reading category is renamed or renumbered.
- Later academies may reuse `tense_misuse`, `personal_opinion` and `timing_failure`; the rest are Task 1 specific.

---

## D-017 — Generated curriculum data is validated by re-derived facts

**Date:** 2026-09-04
**Status:** Active

### Decision
For generated curriculum banks, every visual or dataset carries a machine-computed `facts` map derived from its own data, and the paired validator re-implements that derivation independently and asserts the two agree. Answers and model responses are then checked so that every figure they cite is derivable from the item's own data.

### Rationale
G3 checked completion answers by substring match against the passage. That does not generalise to data tasks, where a claim can be fluent, well-formed and numerically invented. Deriving the facts mechanically and re-deriving them in the validator means a generator bug that produces self-consistent but wrong facts still fails the gate.

### Implications
- Adding a visual kind requires extending the fact engine in *both* the generator and the validator, deliberately and separately. This duplication is the point, not an oversight.
- Grounding proves a figure is *derivable*, not that it is the *intended* figure. `tests/g4_writing1_content_qa.py` closes that gap for the linguistic claims that matter (see `docs/writing1_content_qa.md`).
- The same shape should be reused for G5–G8 rather than reinvented.

---

## D-018 — Local toolchain required to run the validation suite

**Date:** 2026-09-04
**Status:** Active

### Decision
The repository's validation suite requires Python 3 with `jsonschema` and `playwright`, plus any Chromium-family browser. `tests/browser_env.py` resolves the browser (honouring `$IELTS_CHROMIUM`, then known Linux/Windows/macOS paths, then Playwright's own bundle).

### Rationale
Defect D4-001: the four Playwright tests hard-coded `executable_path="/usr/bin/chromium"`, a path that only exists in the Linux environment G3 was authored in. Every browser-driven gate check therefore failed to launch anywhere else, which meant the responsive and accessibility evidence could not be reproduced on the machine the project actually runs on.

### Implications
- A gate claim of "responsive PASS" is only meaningful on a machine where these tests can launch. Record the browser used in the phase report.
- Node is required only to assemble Claude Design mockups, not to run the app or its tests. The application itself remains dependency-free static HTML/CSS/JS per D-014.

---

## D-019 — The visual panel is the only new G4 component

**Date:** 2026-09-04
**Status:** Active

### Decision
G4 extends the design system by exactly one component, `.w1-visual` (documented in `UX_DESIGN_SPEC.md` §8). Every other Writing Task 1 surface reuses the existing component vocabulary: `card`, `badge`, `progress`, `session-item`, `notice`, `ua-note`, `trap`, `question-card`, `answer-feedback`, `timer`, `table-wrap`, `kpi-grid`, `module-item`, `mastery-dot`, `strategy-block`, `lesson-objective`.

The family grid and card selectors G3 introduced as `.reading-family-grid` / `.reading-family-card` were generalised to also match `.family-grid` / `.family-card`, rather than duplicating the rules for Writing.

### Rationale
`UX_DESIGN_SPEC.md` §20 forbids rewriting the design system mid-curriculum-phase. Chart, diagram and map rendering is genuinely new surface that no existing component covers, and §17–18 impose specific obligations on it (text equivalents, no illegible data labels, contained scrolling instead of clipping). Those obligations are properties of the component, so they belong in one place rather than being re-implemented per family.

### Implications
- A new visual kind must be added to the panel's renderer, not given its own component.
- The panel's obligations are enforced by `tests/g4_writing1_accessibility.py` and `tests/g4_writing1_responsive.py`, which check every one of the seven families rather than a sample.
- G5–G8 should extend `.w1-visual` if they need graphics, or state why they cannot.


---

## D-020 — Canonical claim manifest for generated curriculum data

**Date:** 2026-09-04
**Status:** Active
**Supersedes the grounding rule established by D-017 for scored items.**

### Decision
Every scored item in a generated curriculum bank carries a `claim` manifest declaring the
intended claim, the fact keys it derives from, the permitted operations, the dataset
fields, the unit and period, the accepted responses, and the reason each distractor is
wrong.

Authorisation is then strict:

- an **exercise** may cite only the values of the fact keys it declares;
- a **full report** (a prompt or a band sample) may cite any fact of its own visual whose
  operation is in an approved set;
- `total` and `sum` are **not** in that set and must be authorised per item;
- figures printed on the visual as labels — axis categories, column headings, an index
  base, stage numbers — are authorised as labels;
- a deliberately faulty figure quoted for the learner to repair must be declared with a
  reason;
- any year mentioned must be a real time label of that visual, and any unit mentioned must
  be one that visual measures in.

The generator refuses to emit if any of this fails, and the paired validator re-derives all
of it independently.

### Rationale
D-017 authorised any figure "derivable from the visual". Because the fact engine computes
column totals and pairwise sums, a figure could be arithmetically derivable and still not
be the figure the item intended — so an item could pass grounding while being
pedagogically wrong. Logged as defect D4-006.

### Implications
- Adding a figure to an item's text now requires declaring the derivation that produces it,
  which is a deliberate authoring step rather than an automatic allowance.
- `tests/g4_writing1_claims.py` was proven against eight seeded defects, including a
  smuggled column total and a smuggled pairwise sum; all eight were caught.
- G5–G8 should adopt this shape rather than the looser D-017 rule.

---

## D-021 — Canonical teaching prose is bound sentence by sentence
**Date:** 2026-09-05 · **Status:** Approved · **Supersedes part of D-020

### Decision
A figure in a model response or a band sample must belong to an entity that the sentence
names in the same clause. The claim manifest records, per sentence, the entities named and
the fact keys each figure resolves to.

- a fact is indexed with its **subjects** (series, slice, row, feature) and its **contexts**
  (year, column, category);
- a figure may cite only a fact whose subjects are all named in its clause, whose context
  does not contradict a year or category named there, and which is anchored by a name on
  one axis or the other;
- a comparison between two entities may take its second entity from earlier in the same
  sentence, never both;
- an entity carried by ordinary anaphora ("It then fell to 12 per cent") inherits the
  scope of the previous clause or sentence, and nothing else does;
- a figure printed on the visual as a label is authorised only in a clause that names that
  label, rather than through a flat numeric whitelist.

Exercise stems, model notes and target-feature lists keep the declared-key set check of
D-020: that prose is commentary about language, and a rule written for reports misreads it.

### Rationale
External review of candidate `fe720d5` found that report-level authorisation was a set of
numbers with no opinion about which entity each belonged to, so two real values could be
swapped between two series and still pass. That is tolerable for learner-authored free
text and not tolerable for the prose the learner is asked to copy.

### Implications
- `tests/g4_writing1_claims.py` re-implements the binder from the specification by
  resolving fact keys against the visual's label vocabulary, which is the opposite
  direction from the generator; both must agree, figure by figure.
- Authoring canonical prose now means naming the subject near the figure. Four sentences
  were rewritten for this reason, none of them for accuracy.
- Known limit, stated rather than papered over: two entities named inside one clause with
  the figures not interleaved ("A and B rose to 46 and 44 respectively") are bound to the
  clause, not to each other, so a swap inside that one construction is not detected.

---

## D-022 — The 150-word Task 1 minimum is enforced, not assumed
**Date:** 2026-09-05 · **Status:** Approved · **Amends D-015

### Decision
IELTS Academic Task 1 asks for at least 150 words, so:

- every band comparison sample is at least 150 words, and the generator refuses to emit a
  shorter one;
- mastery L4 and L5 require a full response of at least `wordMinimum` words, in addition to
  the timing and self-review checklist conditions of D-015;
- an underlength submission is logged against a new error category,
  `underlength_response`, taking the Writing Task 1 taxonomy from twelve categories to
  thirteen (D-016 amended);
- band samples are labelled "Illustrative Band N-style sample", and each compared aspect is
  mapped to the public IELTS Writing criterion it belongs to, with a pointer to the
  published descriptors. No descriptor text is reproduced.

### Rationale
External review found eighteen of twenty-one samples under 150 words, four of them in the
"Strong" position, and a mastery path that reached L4 and L5 from a twenty-word response.
Both taught the wrong lesson: length became an invisible variable between the levels, and
performance levels could be earned without performance.

### Implications
- All 21 samples were extended in their own voice; every added figure is accurate and
  bound under D-021.
- `tests/g4_writing1_functional.py` submits 20 words and 149 words in the browser and
  requires mastery to stay at L3, then submits a full-length response and requires L4.

---

## D-023 — A release is identified by a tag, not by a hash inside itself
**Date:** 2026-09-05 · **Status:** Approved

### Decision
The external review packet names its candidate by a git tag. `tests/release_integrity.py`
requires that the tag resolves, that the packet stored inside the tagged commit names the
same tag, that every commit hash the packet cites exists, and that every path it cites
exists.

### Rationale
At candidate `fe720d5` the packet named a SHA that no commit in the repository has: the
hash was stamped by a following commit and then rewritten. The durable handoff pointed at
nothing. A commit cannot contain its own hash; a tag is created afterwards, so it can
always be checked.

---

## D-024 — Canonical prose bans non-interleaved `respectively` constructions
**Date:** 2026-09-05 · **Status:** Approved · **Amends D-021**

### Decision
Until the canonical-claim engine binds ordered entity/value pairs, model responses and
band samples must not use `respectively`. Canonical comparisons name each entity next to
its value instead, for example: "Oslo stood at 46 per cent, compared with Bergen at 44
per cent."

### Rationale
External re-review proved that sentence-scoped binding could accept a silent value swap
when one clause named several entities followed by several non-interleaved values. Both
values belonged to the clause, but the validator could not prove their order.

### Implications
- the generator refuses to emit canonical prose containing `respectively`;
- `tests/g4_writing1_claims.py` independently enforces the same ban;
- `tests/g4_writing1_negative.py` seeds the actual multi-entity sentence shape and
  requires the claims validator to reject it;
- learner-authored free text is unaffected because the app does not claim to score it.

---

## D-025 — Band-sample diagnostics carry executable prose evidence
**Date:** 2026-09-05 · **Status:** Approved

### Decision
A band-sample diagnostic that depends on the presence or absence of concrete wording
must carry a `diagnosticChecks` evidence rule. Each rule names one displayed annotation
and lists phrases that must occur or must not occur in the adjacent response. The
generator and the independent G4 validator both enforce these rules.

### Rationale
External re-review found five Band 6 samples whose lengthening pass changed the prose but
left older teaching annotations in place. The resulting tables denied comparisons,
exceptions, cycle language, or compass directions that the learner could see directly.

### Implications
- the five affected annotation sets now describe the final prose accurately;
- future edits that reintroduce an explicit crossover against an annotation saying it is
  only implied, for example, fail validation;
- the seeded-defect suite proves the check by introducing that exact contradiction.
