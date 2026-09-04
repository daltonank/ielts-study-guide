## D-014: Application remains local HTML during curriculum build

Date: 2026-09-04
Status: Active

### Decision

Continue development against the local HTML implementation.

Public deployment will occur only after the local curriculum build meets the
defined phase-gate criteria.

### Reason

Separating curriculum implementation from deployment reduces regression risk
and avoids repeatedly reconciling an unfinished public build.

### Implications

Claude should modify the local implementation rather than attempt deployment
unless this decision is superseded.