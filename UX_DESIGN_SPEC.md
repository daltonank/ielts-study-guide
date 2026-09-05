# UX_DESIGN_SPEC.md

## IELTS Academic C1 • UA+EN UX and Design Specification

---

## 1. Experience Goal

The application should feel calm, academically credible, personal, and easy to continue using every day.

It should not feel like:

- a cluttered enterprise LMS;
- a spreadsheet rendered as a website;
- a giant menu of disconnected lessons;
- a dashboard with excessive metrics;
- a childish language-learning game.

The learner should be able to open the site and quickly answer:

**What should I do next, why, and how long will it take?**

---

## 2. Mobile-First Principle

Primary design widths:

- 320 px
- 375 px
- 430 px
- 768 px
- 1024 px
- 1440 px

Requirements:

- no unintended horizontal overflow;
- readable long passages;
- comfortable forms;
- touch-friendly controls;
- clear fixed/sticky navigation where used;
- wrapping that preserves meaning;
- charts/visuals that remain interpretable;
- timers that do not dominate the screen;
- feedback that remains readable;
- no essential action hidden behind hover.

---

## 3. Primary Navigation

Exactly five primary mobile controls:

1. Today
2. Skills
3. Practice
4. Words
5. Progress

These controls provide the stable top-level mental model.

Secondary functions belong in a drawer or secondary surface.

---

## 4. Secondary Navigation

Supported destinations include:

- Start Here
- Reading Lab
- Listening Lab
- Writing Task 1
- Writing Task 2
- Speaking Lab
- Grammar Clinic
- Paraphrasing
- Pronunciation
- Error Log
- Review Today
- Global Search
- Settings / Backup
- Component Lab

Do not expand primary navigation just because new phases add curriculum.

---

## 5. Scrollable Learning

The learner prefers a scrollable experience.

Use continuous flow where it supports:

- lesson reading;
- strategy;
- worked examples;
- guided practice;
- review;
- feedback.

Use navigation boundaries when they genuinely reduce cognitive load.

Avoid excessive modal dialogs and multi-step overlays.

---

## 6. Visual Hierarchy

Each study surface should make clear:

1. what skill/module is active;
2. why it matters;
3. what the learner should do;
4. progress within the current activity;
5. whether the activity is guided/independent/timed;
6. feedback;
7. next action.

Avoid decorative complexity that competes with the task.

---

## 7. Language Modes

Modes:

- EN
- UA+EN
- UA Help

Changing modes must preserve learner state and current work.

### EN
English-forward experience.

### UA+EN
Strategic Ukrainian support visible alongside selected difficult explanations.

### UA Help
Additional Ukrainian help available without replacing the underlying English task.

The language mode is presentation support, not a separate curriculum.

---

## 8. Components

Maintain reusable patterns for:

- cards;
- section headers;
- progress/mastery markers;
- question blocks;
- answer options;
- feedback boxes;
- timers;
- filter controls;
- vocabulary rows/cards;
- search;
- review items;
- error items;
- writing text areas;
- charts/visual prompts;
- data tables;
- empty states;
- alerts/status messages;
- backup controls.

Component behavior should remain consistent across academies.

### Added at G4 — the visual panel

G4 introduced one new component, because chart and diagram rendering is a surface
Reading never needed. Everything else in Writing Task 1 reuses the existing classes
above.

**`.w1-visual`** — a labelled `<section>` that presents one Task 1 graphic. It always
contains, in this order:

1. the task rubric (`.w1-rubric`), unless the surrounding page already shows it;
2. the graphic itself — inline SVG for charts, a real `<table>` for tables, a numbered
   stage list for processes, a status-coded feature list for maps and plans;
3. a legend (`.w1-legend`) whenever two or more series are shown;
4. a data table, so category identity is never carried by colour alone;
5. a `<details>` text equivalent (`.w1-alt`) — the accessible substitute required by
   §17 and §18;
6. the source and unit note (`.w1-src`).

Rules the component must keep:

- Charts sit in a `.w1-chart` scroll container with a minimum SVG width. A graphic that
  cannot compress **scrolls inside its own container**; it never shrinks its data labels
  below roughly 9px, and it never clips (§18).
- Every SVG carries `role="img"` and an accessible name.
- Series colour uses a validated categorical palette; status colour (added / removed /
  replaced / unchanged) always ships with a text label as well.
- At ≥760px the visual and the exercise sit side by side (`.w1-workspace`) so the learner
  does not scroll away from the data they are describing; below that they stack, visual
  first.

Supporting classes added alongside it: `.w1-opt` (answer option), `.w1-cloze` (inline gap),
`.w1-order` (sequencing control), `.w1-stepper` (plan → draft → review), `.w1-chk`
(self-review checklist row), `.w1-stages`, `.w1-features`.

---

## 9. Learning-State Communication

The interface must distinguish:

- not assessed;
- introduced;
- guided;
- independent;
- timed;
- mastered.

Do not reward passive page opening with visible mastery progress.

Whenever mastery changes, the learner should be able to understand what evidence supported the change.

---

## 10. Feedback UX

Feedback should be:

- immediate where pedagogically useful;
- specific;
- readable;
- connected to the learner's answer;
- actionable.

Avoid generic feedback such as “Incorrect, try again” when the system has enough information to explain the error.

Reading feedback should identify evidence and reasoning.

Writing/Speaking feedback should identify criteria-relevant strengths and corrections without implying official examiner authority.

---

## 11. Error and Review UX

Errors should not feel punitive.

The UI should help the learner see:

- what went wrong;
- why;
- what category it belongs to;
- what to do differently;
- when it will be reviewed.

Review should feel like a continuation of learning, not a second unrelated subsystem.

---

## 12. Timer UX

Timers should:

- be clearly labeled;
- support the intended task;
- record elapsed evidence where required;
- avoid accidental loss of learner work;
- not obstruct mobile content;
- distinguish untimed learning from timed assessment.

---

## 13. Writing UX

Long responses require:

- autosave;
- clear saved state;
- robust text areas;
- prompt visibility;
- data/visual visibility;
- planning support;
- word-count display where useful;
- timer integration;
- review/editing phase;
- protection against accidental navigation loss where feasible.

---

## 14. Vocabulary UX

Vocabulary should support quick browsing and targeted filtering.

Prioritize:

- search;
- source;
- priority;
- topic;
- mastery/study status;
- Ukrainian meaning;
- productive-use fields.

Do not force the learner through 1,784 items sequentially.

---

## 15. Today UX

Today should prioritize one or a few useful actions rather than display every metric.

A recommendation should include:

- task;
- approximate duration;
- reason;
- relevant weakness/review signal.

The learner should be able to start promptly.

---

## 16. Progress UX

Progress should emphasize actionable evidence.

Prefer:

- mastery distribution;
- recent gains;
- persistent weak areas;
- review debt;
- timing trend;
- mock trend;
- vocabulary active-use progress.

Avoid vanity metrics that do not support decisions.

---

## 17. Accessibility

Required baseline:

- semantic HTML;
- keyboard-operable controls;
- visible focus;
- meaningful labels;
- readable contrast;
- reduced-motion support;
- accessible form states;
- text alternatives or accessible equivalents for meaningful visuals;
- status/error feedback that is not color-only;
- adequate touch targets.

Accessibility regressions block relevant phase gates.

---

## 18. Responsive Visuals

Writing Task 1 charts, diagrams, maps, and tables must remain interpretable on phones.

When a visual cannot be safely compressed:

- allow contained scrolling where necessary;
- preserve labels;
- preserve data relationships;
- avoid clipping;
- provide accessible textual descriptions where appropriate.

Do not shrink data labels to illegibility.

---

## 19. Motion

Motion is optional and subordinate to study clarity.

Respect `prefers-reduced-motion`.

Do not require animation to understand progress or correct answers.

---

## 20. Design Change Rule

Do not rewrite the design system or navigation during a curriculum phase unless:

1. a concrete defect is identified;
2. the proposed change supports the active requirement;
3. prior regression behavior is preserved;
4. the change is documented when architecturally significant.
