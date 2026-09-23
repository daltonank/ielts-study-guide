# G4-A R2 proposal completion — Opus review log

Auditable record of what the batch review gate changed between an implementer's
first pass and the accepted proposals. Proposals only: no learner-facing
mutation, no remediation, no correction manifest, no PR #7 movement, no gate
change, no G5.

**Read this alongside the proposals.** Every accepted value in
`docs/G4A_R2_SUPPLEMENTAL_PROPOSALS.csv` was held to recorded-defect scope by
review enforcement, not by the drafter's unaided restraint. A reviewer
adjudicating these proposals should know that.

## Artifacts

| batch | first pass | accepted |
|---|---|---|
| 1 | *not retained as a file* (see note) | `docs/batches/G4A_R2_PROPOSAL_BATCH1.csv` |
| 2 | `docs/batches/G4A_R2_PROPOSAL_BATCH2_PASS1.csv` | `docs/batches/G4A_R2_PROPOSAL_BATCH2.csv` |

**Provenance note on Batch 1.** The Batch-1 first pass was revised in place and
the pre-revision file was not retained. The four rejected values below are
reconstructed from the session transcript, not recovered from an artifact, and
are recorded here for audit context only — they are **not** evidence of the same
standing as the Batch-2 `_PASS1` file. From Batch 2 onward the first pass is
written to its own path before review, so the diff is a real artifact.

## The recurring failure mode

Across both batches the drafting model's **Ukrainian judgment was consistently
sound**. What required correction, repeatedly, was **boundary discipline**:
changes that improved the text but exceeded the recorded defect. Every instance
produced defensible or better Ukrainian while silently widening the diff.

This is why the 10/10/11 reviewed cadence is kept rather than relaxed: minimal
scope is the contract with the reviewer, and an unreviewed run would have
shipped these as confident, well-formed rows that no structural guard rejects.

## Batch 1 — 4 of 10 revised

| id | class | first pass (reconstructed) | accepted |
|---|---|---|---|
| SB-0073 | **over-correction** | `Придатний до застосування, актуальний.` — also rewrote the opening clause, which was outside the recorded defect | `Підходить для застосування, актуальний.` |
| SB-0556 | **introduced defects** | `Розтерти на дрібніші шматки шляхом подрібнення бічними рухами.` — perfective where the bank uses imperfectives, and circular (*crush by means of crushing*) | `Перетворювати щось на дрібні частинки, розтираючи або розмелюючи його.` |
| SB-0043 | inconsistency | `Той, що стосується…` — the dictionary formula and the recorded claim call for `Такий, що`, and the same submission used `Такий, що` one row later | `Такий, що стосується сільського господарства або пов'язаний із ним.` |
| SB-0328 | out of scope | changed `або` → `чи` in addition to the case fix | `…усний або письмовий;…` (conjunction preserved) |

Neither SB-0073 nor SB-0556 would have been caught by any structural guard.

## Batch 2 — 4 of 10 revised (one twice)

| id | class | first pass | accepted |
|---|---|---|---|
| SB-0885 | **tautology**, then **out of scope** | pass 1 paraphrased the ill-formed clause into `…відразу після закінчення війни, коли конфлікт уже закінчився` — restating the first clause. Pass 2 fixed that but introduced `відразу`→`одразу` and dropped `часу` | `Такий, що стосується періоду часу відразу після закінчення війни.` |
| SB-1171 | out of scope + **regression** | `Підозрювання когось або чогось, особливо у чомусь поганому.` — silently reordered the frozen `щось або когось`, and `в`→`у` is a regression (Ukrainian euphony prefers `в` after a vowel; `особливо` ends in `-о`) | `Підозрювання чогось або когось, особливо в чомусь поганому.` |
| SB-0907 | unclear phrasing | `Ймовірно, наскільки можна обґрунтовано припустити.` — two fragments comma-spliced | `Як можна обґрунтовано припустити; імовірно.` |
| SB-1247 | accepted, note added | unchanged | `студент бакалаврату` (target `ua`) |

### SB-1171 — an accepted grammatical change

The accepted value changes `щось` → `чогось`. This is **not** scope creep: the
recorded fix nominalises the verb to `Підозрювання`, and a Ukrainian deverbal
noun in `-ння` cannot govern the accusative, so the inanimate complement must
take the genitive. The animate `когось` is unchanged because accusative and
genitive coincide for animates. The frozen order is preserved. The change is
stated explicitly in the row's rationale rather than made silently.

### SB-1247 — the cross-field row

`ua = студент` is broader than *undergraduate*, while `definitionUa` already
carried the first-degree constraint. The correction targets the **single** field
responsible for the inconsistency — the broad gloss — and leaves the precise
definition untouched. This is the only `ua`-targeted row in the first twenty.

## Schema rule established before Batch 2

`proposed_target = both` is **rejected** at both the builder and the guard. The
artifact carries one `proposed_value`, so `both` cannot express two different
replacements for `ua` and `definitionUa`; validating it by comparing one string
against both frozen fields is meaningless. A genuine two-field case requires
extending the schema to separate `proposed_ua` / `proposed_definitionUa` columns
first. No row in batches 1–2 needed it.

## Reviewer notes carried forward

Concerns real but outside the recorded defect, recorded as prose rather than
folded into any correction:

- **SB-0073** — `Підходить` is a finite verb, not an adjectival predicate; the
  opening clause may be a separate non-adjectival-formula defect.
- **SB-0885** — `періоду часу` is pleonastic and `відразу`/`одразу` are
  interchangeable; both left frozen.
- **SB-1111** — the gloss `загін` carries a military connotation that may not
  fit nonmilitary senses of *squad*.
- **SB-1168** — `Віддатися` is perfective, against this bank's imperfective
  convention for verb definitions; predates the recorded defect.
- **SB-1171** — frozen `Дія підозрювати` looks like a mangled
  `Дія за значенням підозрювати`, the standard dictionary formula; if that is
  house style it may be the better target than `Підозрювання`.
- **SB-1247** — `наукового ступеня` denotes a *research* degree in Ukrainian
  academic usage, whereas a bachelor's is an `освітній ступінь`, so the frozen
  definition is arguably imprecise on its own terms.

## Status after Batch 2

20 of 31 authored (batches 1–2), 20 corrections, 0 no-change, confidence
11 high / 9 medium. Batch 3 (11 rows) pending under the same cadence.

Gate unchanged: `G4 technical PASS · G4-A CHANGES REQUESTED · G5 BLOCKED`.

## Batch 3 — 11 accepted corrections

ChatGPT semantically adjudicated the 11 Batch-3 rows against the frozen input
packet. There were 11 accepted corrections and 0 no-change answers. No Batch-3
first-pass artifact was created. The accepted rows are in
`docs/batches/G4A_R2_PROPOSAL_BATCH3.csv`.

Dalton approved the explicit `proposed_ua` and `proposed_definitionUa` schema
because SB-1590 is a genuine two-field correction. The combined supplemental
artifact now carries those two nullable columns. The builder mechanically maps
the accepted legacy Batch-1 and Batch-2 target/value pairs into them. Their
proposal values, rationales, evidence quotes, confidence values, and answer
kinds retain the accepted semantics; their source CSVs were not rewritten.

Review kept each Batch-3 correction within its recorded defect. Possible
improvements outside those defects were intentionally left out of the accepted
proposals. No learner-facing vocabulary was changed.

The combined artifact now has 31 of 31 authored rows: Batch 1 = 10, Batch 2 =
10, Batch 3 = 11; 31 corrections, 0 no-change. SB-1590 is its only two-field
row. Gate unchanged: `G4 technical PASS · G4-A CHANGES REQUESTED · G5 BLOCKED`.
