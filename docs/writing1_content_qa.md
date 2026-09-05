# Writing Task 1 Content QA Note

Phase 4 content was checked in three layers, following the pattern established by
`docs/reading_content_qa.md` and the loop in `docs/development_design_plan.md` §5 step 8.

## Layer 1 — structural validation

`tests/g4_writing1_validation.py` re-parses `web/writing1_data.js` and re-derives every
check from the specification rather than from the generator. It re-implements the fact
engine independently, so a generator bug producing self-consistent but wrong facts still
fails. Result: **PASS**.

## Layer 2 — prose-claim QA

Structural validation proves every *figure* in an answer or model response is derivable
from that item's own visual. It cannot prove that a *sentence* is true — "less than a
third", "the largest single step in the ranking", "the only mode to fall", "more steeply
in proportional terms" are all linguistic claims about the data.

`tests/g4_writing1_content_qa.py` re-derives **115 such claims** from the underlying data
and asserts each one. Result: **115 checked, 0 failed.**

Coverage includes, per family:

| Family | Representative claims re-derived |
|---|---|
| Line graphs | Tromso more than triples; Bergen leads in 2005 but Oslo leads in 2025; the crossover falls between two plotted years; Riverside and Northgate gained *exactly* the same amount so "grew faster" is genuinely unsupported; 2020 is not a plotted year |
| Bar charts | Eating out leads in all three age groups; cultural visits is the *only* category that rises with age; live events ends below a third of its youngest-group value; Copenhagen→Munich is the widest adjacent gap; Naples is one twelfth of Amsterdam; air freight quadrupled; rail did *not* halve |
| Pie charts | Every snapshot sums to 100; bathing + flushing is exactly three fifths; plastics more than doubled and moved exactly 14 points; exactly three categories moved ≥9 points; paper fell more steeply than organic *in proportional terms*; the distribution genuinely became more even |
| Tables | Riverford is the only destination to lose arrivals; Highland Park the only stay to rise; Coastal Bay has the largest stay reduction; every employment column sums to 100; services was already largest in 1995; food varies least across the four cities |
| Process diagrams | Stage counts and cyclicality; the 1–5 / 6–8 paragraph split lands on real stage boundaries; **no temperature or duration appears anywhere in the data**, so the "invented detail" distractor is genuinely invented; disinfection is a later stage than storage |
| Maps and plans | Every feature's status (added / removed / replaced / unchanged) matches what the exercises claim; the village shop is *replaced*, not removed; added and removed pairs share an area |
| Mixed visuals | Both component pies sum to 100; consumption is virtually flat after 2019 while growth before it is more than ten times larger; the two rail lines that gained passengers are exactly the two highest-satisfaction lines; humanities sits ~24 points below the leading field |

Two real defects were found and fixed by this process, both in the *fact engine* rather
than the content:

- **QA-G4-001.** The generator could not derive differences between two readings of the
  same series or two columns of the same row, so genuinely grounded claims (a 23-point
  gap between two cities, an 0.8 million fall between two columns) were rejected. Both
  the generator and the validator now compute pairwise differences, independently.
- **QA-G4-002.** The literal string "Task 1" was being read as the figure 1 and checked
  against the visual. Task labels are now stripped before any figure is extracted.

A third finding is recorded rather than fixed: the support set legitimately includes
column totals and pairwise sums, because a Task 1 report genuinely performs those
operations ("these two uses combined took up three fifths"). The grounding check
therefore proves a figure is *derivable* from the data, not that it is the *intended*
figure. Layer 2 exists precisely to close that gap for the claims that matter.

## Layer 3 — manual editorial review

Every item was authored and read against `VALIDATION_SPEC.md` §8:

- **Answer correctness and uniqueness.** For each select item the correct option is the
  only defensible one. Several distractors were rewritten during authoring because they
  turned out to be *true* — e.g. an early "Eastfield lost more students than Northgate
  gained" was accurate (10.5 against 6.0) and was replaced.
- **Distractor defensibility.** Every wrong option fails for a *different, nameable*
  reason, and each carries its own reasoning string. The four-option sets deliberately
  mix: true-but-trivial, structurally-about-the-graphic, unsupported-cause, and opinion.
- **Explanation quality.** Explanations state why the answer is right *and* what class of
  error the wrong choice belongs to, so the feedback is criteria-relevant rather than
  "Incorrect, try again".
- **Level appropriateness.** Calibrated to an advanced learner: the items train
  selection, grouping, proportional comparison and register, not vocabulary recognition.
- **Natural English and Ukrainian.** Ukrainian appears as strategy and transfer support
  only — never as a mirror translation of the English task content
  (`PROJECT_CHARTER.md` §4.2). Every exercise carries a UA note; the validator enforces
  that each contains actual Cyrillic.
- **Copyright and source status.** All 21 visuals and all datasets are original to this
  product. No commercial IELTS graphic, passage or answer key is reproduced. Place names
  are invented or generic.
- **Honest scoring.** Every full prompt carries a scoring note disclaiming official
  status, the validator asserts that disclaimer is present, and it also greps all
  learner-facing text for anything that reads as awarding the learner a band.

## Curriculum scope

The 70 micro-exercises isolate individual Task 1 sub-skills; the 21 full prompts are
single-task timed responses, not multi-task exam simulations. Full Writing-paper realism
(Task 1 and Task 2 together under one clock) belongs to the Mock Center in G9, and
nothing here is presented as a full exam simulation.

## Known limitation

Full written responses are learner-produced and cannot be auto-scored. They are assessed
against a 13-item self-review checklist mapped to the criteria IELTS Writing rewards.
This is deliberate: automated band estimation would violate `PROJECT_CHARTER.md` §4.9.
