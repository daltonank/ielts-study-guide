#!/usr/bin/env python3
"""CP3 — full-rubric residual findings inventory (issue #4 audit). READ-ONLY.

Emits docs/G4A_RESIDUAL_AUDIT_CP3_INVENTORY.csv with exactly one row per residual ID
(disposition clean|P0|P1|P2|needs-human) and docs/G4A_RESIDUAL_AUDIT_CP3_SUMMARY.md.

Sources of non-clean dispositions: scripts/qa/cp3_judgments.json
  - known_open_confirmations: independent re-derivation of the 24 known-open residuals
  - new_findings: defects discovered by the exhaustive clean-pool read
Everything else in the residual roster is dispositioned 'clean' (AI full-rubric read).
"""
from pathlib import Path
import csv, json, sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import residual_audit_lib as lib

ROOT = lib.ROOT
DOCS = ROOT / "docs"
JUDG = ROOT / "scripts" / "qa" / "cp3_judgments.json"


def main():
    vocab = lib.load_vocab()
    by_id = {e["id"]: e for e in vocab}
    residual = lib.residual_ids(vocab)
    bk = lib.buckets(vocab)
    judg = json.loads(JUDG.read_text(encoding="utf-8"))
    ko = judg["known_open_confirmations"]
    nf = judg["new_findings"]

    rows = []
    counts = {"clean": 0, "P0": 0, "P1": 0, "P2": 0, "needs-human": 0}
    for _id in residual:
        e = by_id[_id]
        if _id in ko:
            j = ko[_id]
            source = "known-open-confirmation"
        elif _id in nf:
            j = nf[_id]
            source = "new-finding"
        else:
            j = {"disposition": "clean", "category": "", "rationale": "", "confidence": "medium"}
            source = "clean-pool"
        disp = j["disposition"]
        counts[disp] = counts.get(disp, 0) + 1
        rows.append({
            "id": _id,
            "bucket": "c_known_open" if _id in bk["c_known_open"] else "d_clean",
            "source": source,
            "disposition": disp,
            "category": j.get("category", ""),
            "headword": e.get("word", ""),
            "pos": e.get("pos", ""),
            "ua": e.get("ua", ""),
            "definitionUa": e.get("definitionUa", ""),
            "rationale": j.get("rationale", ""),
            "confidence": j.get("confidence", ""),
            "reviewer_agree": str(j.get("reviewer_agree", "")),
        })

    out = DOCS / "G4A_RESIDUAL_AUDIT_CP3_INVENTORY.csv"
    with out.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    # summary
    from collections import Counter
    cat_counts = Counter(r["category"] for r in rows if r["disposition"] not in ("clean",))
    new_p1 = [r["id"] for r in rows if r["source"] == "new-finding" and r["disposition"] == "P1"]
    new_p2 = [r["id"] for r in rows if r["source"] == "new-finding" and r["disposition"] == "P2"]

    md = DOCS / "G4A_RESIDUAL_AUDIT_CP3_SUMMARY.md"
    L = []
    L.append("# G4-A Residual-Population Audit — CP3: Full-Rubric Findings Inventory\n")
    L.append("**Audit branch:** `claude-code/4-g4a-residual-audit`  ")
    L.append("**Baseline:** `f34f109ae5b8564e7fa10317c167a6ca728c52fd`  ")
    L.append("**web/vocabulary.js blob:** `1c184e84e5c63e3a9f8e386af13787664a23bd66` (unchanged)  ")
    L.append("**Gate language (unchanged):** `G4 technical PASS · G4-A CHANGES REQUESTED · G5 BLOCKED`\n")
    L.append(f"Complete inventory: **{len(rows)}** residual IDs, each dispositioned exactly once "
             "(coverage proven mechanically by `tests/g4a_residual_audit_coverage.py`).\n")
    L.append("## Method and depth (honest)\n")
    L.append(judg["_meta"]["method"] + "\n")
    L.append("> " + judg["_meta"]["depth_caveat"] + "\n")
    L.append("**Principled POS bar (applied consistently):** " + judg["_meta"]["pos_bar"] + "\n")
    L.append("## Disposition counts (whole residual population)\n")
    L.append("| Disposition | Count |")
    L.append("|---|---|")
    for k in ("clean", "P0", "P1", "P2", "needs-human"):
        L.append(f"| {k} | {counts.get(k,0)} |")
    L.append(f"| **total** | **{len(rows)}** |")
    L.append("")
    L.append("## The 24 known-open residual — independently re-derived\n")
    L.append("All 24 were verified against each entry's own fields. **All 24 are genuine defects.** "
             "Agreement with the PR #7 review: **18 full agreement**; **6 genuine-defect-but-milder-severity** "
             "(under the principled POS/number bar they are P2 rather than P1): "
             "SB-0058, SB-0306, SB-1695, SB-1707, SB-1731, SB-1635. See the inventory rows "
             "(source=known-open-confirmation) for per-ID rationale and `independent_severity_note` in "
             "`scripts/qa/cp3_judgments.json`.\n")
    L.append("## NEW findings from the exhaustive clean-pool read\n")
    L.append(f"- **New P1: {len(new_p1)}** — {', '.join(new_p1) if new_p1 else '(none)'}")
    L.append(f"- **New P2: {len(new_p2)}** — {', '.join(new_p2) if new_p2 else '(none)'}")
    L.append(f"- **New P0: 0**, **needs-human: {counts.get('needs-human',0)}**\n")
    L.append("Non-clean categories: " + ", ".join(f"{k}={v}" for k, v in sorted(cat_counts.items()) if k) + "\n")
    L.append("## Divergence from the PR #7 sample density — flagged for reviewer\n")
    L.append("The PR #7 seed-20260913 sample found 23 P1 in 48 (~48%). This exhaustive pass finds a far lower "
             "clean-pool defect density (1 new P1 + 7 P2 in 983). The two documented reasons are in the depth "
             "caveat above. This is surfaced explicitly rather than reconciled away: it means either the reviewer's "
             "bar is stricter (borderline POS/number cases counted P1) and/or AI screening depth under-detects "
             "some subtle sense errors. **Either way the clean pool is NOT asserted defect-free and G4-A is NOT a "
             "PASS.** A deeper or native-Ukrainian semantic pass over the clean pool is the recommended follow-up.\n")
    L.append("Artifacts: `G4A_RESIDUAL_AUDIT_CP3_INVENTORY.csv` (per-entry inventory), "
             "`scripts/qa/cp3_judgments.json` (judgment source).")
    md.write_text("\n".join(L) + "\n", encoding="utf-8")

    print("CP3 inventory rows:", len(rows))
    print("disposition counts:", counts)
    print("new P1:", new_p1)
    print("new P2:", new_p2)
    print("wrote:", out.name, md.name)


if __name__ == "__main__":
    main()
