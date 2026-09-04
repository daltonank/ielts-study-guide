# Cowork Operating Plan — IELTS Academic C1 UA+EN Adaptive Study Webapp

**Established:** 2026-09-04
**Status:** Active
**Precedence:** This document is operating process, not product authority. Where it conflicts with `PROJECT_CHARTER.md` through `DECISIONS.md`, those win.

---

## 1. Where Cowork fits

`CLAUDE_WORKSPACE_SCOPE.md` defines a three-part system: ChatGPT for product/curriculum design and research, GitHub for canonical memory, Claude for implementation. This session runs in Cowork, which is Claude connected directly to your computer and to a persistent cloud workspace. In practice it fills a fourth role that the three-part model didn't have a name for yet:

**Cowork is the reconciliation and continuity layer.** It's where you come when you need someone to actually look at the state of the project — read the repo, cross-check claims against evidence, fix drift between what the docs say and what's true, and hand a clean, verified state to whichever tool does the next piece of work (Claude Code for implementation, Claude Design for mockups, ChatGPT for curriculum research). It is not a second place to write product decisions — those still belong in `DECISIONS.md`.

What happened in this session is the template for that role: your local folder had no canonical specs and no git history; a ChatGPT-side reconstruction filled the gap; Cowork's job was to verify the reconstruction was real (by actually running the validation scripts, not reading the claims) before treating it as truth, then commit it as the durable record.

## 2. Today's reconciliation, for the record

- Confirmed no GitHub repository exists yet; the connected local folder had a flat file layout with no canonical specs and no git history.
- You supplied a ChatGPT-reconstructed package restoring `PROJECT_CHARTER.md`, `PRODUCT_SPEC.md`, `CURRICULUM_SPEC.md`, `UX_DESIGN_SPEC.md`, `VALIDATION_SPEC.md`, `CLAUDE.md`, `CHANGELOG.md`, plus the recovered `web/`, `schemas/`, `scripts/`, `tests/`, `docs/` implementation tree.
- Independently ran `scripts/validate_build.py`, `tests/g2_vocabulary_validation.py`, `tests/g3_reading_validation.py`, and `tests/responsive_check.py` (real headless-browser run at all six target widths) against the actual files. All passed. G0–G3 are genuinely complete, not just claimed complete.
- Reorganized the connected folder into the canonical repo layout, preserved every pre-existing file under `archive/pre-reconstruction-2026-09-04/` rather than deleting anything, initialized git, and made the first commit (147 files).
- Open item: a real GitHub remote. No `gh` CLI or GitHub credentials are available on this machine or in the cloud workspace, so this needs one of two things from you: run `gh auth login` on your computer and tell me the repo name you want, or create an empty repo on github.com and paste me the URL — either way I'll add the remote and push.

## 3. Standing rule: verify before accepting

The single most important thing this session learned: a prior AI session's gate reports (`phase_3_report.md`, etc.) and a "canonical source precedence" note in `LESIA_IELTS_CLAUDE_CONTEXT.md` both instructed future sessions to treat newer self-reported PASS claims as authoritative over contradicting evidence (a blocked gate report, a stale dashboard). That instruction turned out to be defensible in this specific case — the content was real — but it was defensible only because I ran the actual validation scripts and got real PASS output, not because the claim was self-consistent.

**Standing rule for every future session (Cowork, Claude Code, or otherwise):** never mark a requirement or gate complete because a report says so. Run the actual validation script named in `VALIDATION_SPEC.md` for that gate and read its real output. If a script referenced by a report doesn't exist or doesn't run, that gate is not verified, regardless of what the report claims. This is already `VALIDATION_SPEC.md` §13 (Truthfulness Rule) — this section exists to make sure Cowork actually enforces it rather than just repeating it.

## 4. Division of labor

| Task | Tool |
|---|---|
| Curriculum design, pedagogy research, IELTS band-descriptor accuracy, drafting new spec sections | ChatGPT |
| Writing/editing application code, running the validation suite, generating curriculum data files, git operations | Claude Code |
| UI mockups for new academies, component states, chart/visual layouts before they're built | Claude Design |
| Reconciling drift between local/GitHub/chat-side state, verifying claims, cross-tool handoffs, repo housekeeping, answering "what's actually true right now" | Cowork (here) |

If you're not sure which one a task belongs to, the test is: does it require reading and cross-checking the actual repo state against multiple sources? Cowork. Does it require writing or testing code against the repo? Claude Code. Does it require a visual before code exists? Claude Design. Is it about what the curriculum *should* contain, independent of the app? ChatGPT.

## 5. Recurring Cowork checklist

At the start of any Cowork session touching this project:

1. Read `CURRENT_STATE.md` and `DECISIONS.md` first — not from memory, from the file, since either may have changed since last session.
2. If GitHub is connected by then, check `git status` and `git log` on both the local folder and the remote for drift before doing anything else.
3. Check `INBOX.md`/the candidate-features list for anything the user wants triaged — triage means deciding whether an idea becomes a documented decision or requirement, not implementing it directly. Guardrail: never add a feature to the product because it's sitting in the inbox.
4. If asked to confirm a gate, requirement, or "is X done" — go run the validation script. Don't answer from the docs alone.
5. At the end of substantial work: update `CURRENT_STATE.md`, add a `DECISIONS.md` entry for anything that changed product/architecture direction, append `CHANGELOG.md`, and commit.

## 6. Backup and sync cadence

Until GitHub is wired up, the local git repo in your connected folder is the only durable history. Recommend: commit at the end of every session that changes files (Claude Code should do this as part of its own definition of done), and push to GitHub as soon as the remote exists so the repo — not any single machine — becomes the actual source of truth `CLAUDE_WORKSPACE_SCOPE.md` describes.

## 7. Open items

- [ ] Wire up the GitHub remote (needs your input — see §2).
- [ ] Decide whether `INBOX.md` candidate features (adaptive passage difficulty, writing band estimator, pronunciation drills, daily streaks, exam-day simulator) should be triaged into `CURRICULUM_SPEC.md`/`PROJECT_CHARTER.md` now or deferred until G9 (Adaptive Engine) per the existing roadmap.
- [ ] Confirm whether Lesia (the learner) should have any visibility into this planning layer, or whether it stays entirely on your side.
