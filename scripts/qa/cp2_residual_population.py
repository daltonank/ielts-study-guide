#!/usr/bin/env python3
"""CP2 — residual population definition + exhaustive mechanical scans (issue #4 audit).

READ-ONLY. Emits:
  docs/G4A_RESIDUAL_AUDIT_CP2_POPULATION.md   (human report)
  docs/G4A_RESIDUAL_AUDIT_CP2_ROSTER.csv      (one row per residual ID w/ provenance)
  docs/G4A_RESIDUAL_AUDIT_CP2_MECHANICAL.csv  (one row per mechanical hit)

Deterministic: sorted IDs, fixed detector set from residual_audit_lib.
"""
from pathlib import Path
import csv, sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import residual_audit_lib as lib

ROOT = lib.ROOT
DOCS = ROOT / "docs"


def main():
    vocab = lib.load_vocab()
    by_id = {e["id"]: e for e in vocab}
    bk = lib.buckets(vocab)
    residual = lib.residual_ids(vocab)

    # provenance label per residual ID
    def provenance(_id):
        if _id in bk["c_known_open"]:
            if _id == lib.KNOWN_OPEN_SB1015:
                return "known-open-24 (SB-1015; in supplemental register, re-opened by PR#7 review)"
            return f"known-open-24 (seed-20260913; {lib.SEED_20260913_CATEGORY[_id]})"
        return "clean-pool (never flagged)"

    # roster CSV
    roster_path = DOCS / "G4A_RESIDUAL_AUDIT_CP2_ROSTER.csv"
    with roster_path.open("w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["id", "word", "pos", "ua", "definitionUa", "bucket", "provenance"])
        for _id in residual:
            e = by_id[_id]
            bucket = "c_known_open" if _id in bk["c_known_open"] else "d_clean"
            w.writerow([_id, e.get("word", ""), e.get("pos", ""), e.get("ua", ""),
                        e.get("definitionUa", ""), bucket, provenance(_id)])

    # mechanical scan over residual population
    mech_path = DOCS / "G4A_RESIDUAL_AUDIT_CP2_MECHANICAL.csv"
    detector_counts = {}
    ids_with_hit = set()
    with mech_path.open("w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["id", "word", "pos", "detector", "field_or_evidence",
                    "ua", "definitionUa"])
        for _id in residual:
            e = by_id[_id]
            hits = lib.run_all_detectors(e)
            for detector, evidence in sorted(hits.items()):
                detector_counts[detector] = detector_counts.get(detector, 0) + 1
                ids_with_hit.add(_id)
                w.writerow([_id, e.get("word", ""), e.get("pos", ""), detector,
                            " | ".join(evidence), e.get("ua", ""),
                            e.get("definitionUa", "")])

    # also scan translationQa Draft (reported, not a defect) for transparency
    draft_residual = sum(
        1 for _id in residual
        if isinstance(by_id[_id].get("translationQa"), str)
        and "draft" in by_id[_id]["translationQa"].lower()
    )

    md = DOCS / "G4A_RESIDUAL_AUDIT_CP2_POPULATION.md"
    lines = []
    lines.append("# G4-A Residual-Population Audit — CP2: Population + Mechanical Scans\n")
    lines.append(f"**Audit branch:** `claude-code/4-g4a-residual-audit`  ")
    lines.append(f"**Baseline:** `f34f109ae5b8564e7fa10317c167a6ca728c52fd`  ")
    lines.append("**web/vocabulary.js blob:** `1c184e84e5c63e3a9f8e386af13787664a23bd66` (unchanged)  ")
    lines.append("**Gate language (unchanged):** `G4 technical PASS · G4-A CHANGES REQUESTED · G5 BLOCKED`\n")
    lines.append("## Deterministic bucket partition of all 1,784 IDs\n")
    lines.append("Each ID is assigned to exactly one bucket (no double counting). "
                 "SB-1015 physically appears in the supplemental register but is re-opened "
                 "by the PR #7 review, so it is assigned to bucket (c), not (b).\n")
    lines.append("| Bucket | Definition | Count |")
    lines.append("|---|---|---|")
    lines.append(f"| (a) historical-register findings | `docs/G4A_UKRAINIAN_QA_FINDINGS.csv` | {len(bk['a_historical'])} |")
    lines.append(f"| (b) supplemental corrected/benign (excl. SB-1015) | `docs/G4A_T5B_SUPPLEMENTAL_FINDINGS.csv` | {len(bk['b_supplemental'])} |")
    lines.append(f"| (c) known-open residual (24) | SB-1015 + 23 seed-20260913 | {len(bk['c_known_open'])} |")
    lines.append(f"| (d) never-flagged clean pool | remainder | {len(bk['d_clean'])} |")
    lines.append(f"| **TOTAL** | | **{sum(len(v) for v in bk.values())}** |")
    lines.append("")
    lines.append(f"**Residual population to audit = (c) + (d) = {len(residual)}.**")
    lines.append("")
    lines.append("Cross-check: the PR #7 review's seed-20260913 selector reported an eligible "
                 "pool of **1,006** = all IDs absent from *both* registers "
                 f"(historical ∪ supplemental = {len(bk['a_historical'] | (lib.supplemental_ids() & set(lib.all_ids(vocab))))}). "
                 "The residual-to-audit adds SB-1015 (re-opened) to that 1,006, giving 1,007.\n")
    lines.append("## The 24 known-open residual (independently listed here; re-derived in CP3)\n")
    lines.append("- **SB-1015** — `retrieve`; `ua` too generic, omits back/recover sense (in supplemental register, re-opened).")
    lines.append(f"- **Grammar/calque fragments (7):** {', '.join(lib.SEED_20260913_GRAMMAR_CALQUE)}")
    lines.append(f"- **POS/morphology mismatch (10):** {', '.join(lib.SEED_20260913_POS_MORPH)}")
    lines.append(f"- **Semantic/pedagogical error (6):** {', '.join(lib.SEED_20260913_SEMANTIC)}\n")
    lines.append("## Exhaustive mechanical detectors over the residual population\n")
    lines.append("Detectors are conservative *candidate* signals — CP3 adjudicates each. "
                 "They are deterministic and defined in `scripts/qa/residual_audit_lib.py`.\n")
    lines.append("| Detector | Residual IDs hit |")
    lines.append("|---|---|")
    for det in ("adjacent_repeat", "connector_repeat", "placeholder",
                "calque_marker", "empty_or_noncyrillic", "pos_morphology"):
        lines.append(f"| {det} | {detector_counts.get(det, 0)} |")
    lines.append(f"| **residual IDs with ≥1 mechanical hit** | **{len(ids_with_hit)}** |")
    lines.append("")
    lines.append(f"`translationQa` still carrying the migration default \"Draft — verify in "
                 f"context\": **{draft_residual}/{len(residual)}** residual IDs. This is the "
                 "unreviewed-stamp default, reported for transparency, **not** counted as a "
                 "learner-facing defect (it is not shown to the learner as a translation).\n")
    lines.append("## Interpretation\n")
    lines.append("The mechanical layer is intentionally low-yield: adjacent/connector repeats "
                 "are already fully remediated bank-wide (T5-B), and empty/placeholder/"
                 "non-Cyrillic fields are already blocked by the deterministic gate. The "
                 "substantive residual risk is **semantic/POS/calque meaning errors that are "
                 "well-formed Ukrainian** — invisible to mechanical detectors — which is why "
                 "CP3 applies the full linguistic rubric to every residual entry.\n")
    lines.append("Artifacts: `G4A_RESIDUAL_AUDIT_CP2_ROSTER.csv` (one row per residual ID), "
                 "`G4A_RESIDUAL_AUDIT_CP2_MECHANICAL.csv` (one row per mechanical hit).")
    md.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("CP2 residual population:", len(residual))
    print("bucket counts:", {k: len(v) for k, v in bk.items()})
    print("mechanical detector counts:", detector_counts)
    print("residual IDs with >=1 mechanical hit:", len(ids_with_hit))
    print("wrote:", roster_path.name, mech_path.name, md.name)


if __name__ == "__main__":
    main()
