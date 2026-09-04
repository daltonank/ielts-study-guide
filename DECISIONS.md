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
