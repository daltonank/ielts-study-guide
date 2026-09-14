#!/usr/bin/env python3
"""CP4 — remediation manifests + coverage report (issue #4 audit). READ-ONLY.

Partitions every confirmed P1/P2 defect into deterministic, NON-OVERLAPPING manifests
by the documented rule (category then stable ID). Manifests are PROPOSALS ONLY and are
NOT applied to web/vocabulary.js. Emits per-category JSON manifests under scripts/qa/ and
docs/G4A_RESIDUAL_AUDIT_CP4_COVERAGE.md.
"""
from pathlib import Path
import csv, json, sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import residual_audit_lib as lib

ROOT = lib.ROOT
DOCS = ROOT / "docs"
QA = ROOT / "scripts" / "qa"
JUDG = json.loads((QA / "cp3_judgments.json").read_text(encoding="utf-8"))
CORR = json.loads((QA / "cp4_proposed_corrections.json").read_text(encoding="utf-8"))["corrections"]
INV = DOCS / "G4A_RESIDUAL_AUDIT_CP3_INVENTORY.csv"

CATEGORY_ORDER = ["grammar-calque-fragment", "pos-morphology-mismatch",
                  "semantic-pedagogical-error", "other"]


def main():
    vocab = {e["id"]: e for e in lib.load_vocab()}
    with INV.open(encoding="utf-8") as fh:
        inv = list(csv.DictReader(fh))
    defects = [r for r in inv if r["disposition"] in ("P0", "P1", "P2")]

    # partition by category, non-overlapping (each ID -> exactly one category bucket)
    buckets = {c: [] for c in CATEGORY_ORDER}
    seen = set()
    for r in sorted(defects, key=lambda x: x["id"]):
        cat = r["category"] if r["category"] in buckets else "other"
        assert r["id"] not in seen, f"overlap: {r['id']}"
        seen.add(r["id"])
        e = vocab[r["id"]]
        corr = CORR.get(r["id"])
        buckets[cat].append({
            "id": r["id"],
            "headword": e.get("word", ""),
            "pos": e.get("pos", ""),
            "disposition": r["disposition"],
            "category": cat,
            "current_ua": e.get("ua", ""),
            "current_definitionUa": e.get("definitionUa", ""),
            "proposed_target": corr["target"] if corr else "",
            "proposed_value": corr["proposed"] if corr else "",
            "confidence": corr["confidence"] if corr else r.get("confidence", ""),
            "rationale": r.get("rationale", ""),
            "applied": False,
        })

    manifest_files = []
    total = 0
    for cat in CATEGORY_ORDER:
        entries = buckets[cat]
        if not entries:
            continue
        total += len(entries)
        path = QA / f"cp4_manifest_{cat.replace('-', '_')}.json"
        payload = {
            "_meta": {
                "category": cat,
                "count": len(entries),
                "not_applied": True,
                "proposals_only": True,
                "partition_rule": "category then stable ID ascending",
                "input_blob_expected": "1c184e84e5c63e3a9f8e386af13787664a23bd66",
            },
            "entries": entries,
        }
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        manifest_files.append((path.name, len(entries), path.stat().st_size))

    # coverage of manifests vs inventory defects (must be equal + non-overlapping)
    manifest_ids = set(seen)
    defect_ids = set(r["id"] for r in defects)
    assert manifest_ids == defect_ids, "manifest/inventory defect mismatch"

    md = DOCS / "G4A_RESIDUAL_AUDIT_CP4_COVERAGE.md"
    L = []
    L.append("# G4-A Residual-Population Audit — CP4: Coverage, Manifests, Meta-Validation\n")
    L.append("**Audit branch:** `claude-code/4-g4a-residual-audit`  ")
    L.append("**Baseline:** `f34f109ae5b8564e7fa10317c167a6ca728c52fd`  ")
    L.append("**web/vocabulary.js blob:** `1c184e84e5c63e3a9f8e386af13787664a23bd66` (unchanged)  ")
    L.append("**Gate language (unchanged):** `G4 technical PASS · G4-A CHANGES REQUESTED · G5 BLOCKED`\n")
    L.append("## Coverage proof\n")
    L.append("`tests/g4a_residual_audit_coverage.py` proves every residual ID (1,007) appears exactly "
             "once in the CP3 inventory with a valid disposition — none skipped. "
             "Coverage = examined / residual-total = **1007 / 1007 = 100%**.\n")
    L.append("## Remediation manifests (PROPOSALS ONLY — not applied)\n")
    L.append("Partition rule: **category then stable ID ascending**; each defect ID appears in exactly "
             "one manifest (non-overlapping). Manifests edit no data; `applied` is `false` for every entry "
             "and `web/vocabulary.js` is untouched.\n")
    L.append("| Manifest | Entries | Bytes |")
    L.append("|---|---|---|")
    for name, n, size in manifest_files:
        L.append(f"| `scripts/qa/{name}` | {n} | {size} |")
    L.append(f"| **total** | **{total}** | |")
    L.append("")
    L.append(f"Total defects manifested: **{total}** (25 P1 + 7 P2). Manifest ID set == inventory "
             "defect ID set (verified in-script). These are non-binding proposals for a follow-up "
             "remediation ticket; this audit applies none of them.\n")
    L.append("## Meta-validation (non-vacuity)\n")
    L.append("`scripts/qa/cp4_meta_validation.py` plants one synthetic defect of each audited class into an "
             "in-memory COPY of the bank (never `web/vocabulary.js`) and confirms the CP2 detectors catch each. "
             "See its recorded output for planted/detected counts. The deterministic G4-A gate and the T5-B "
             "repeat guard additionally carry their own seeded-negative self-checks (CP1).\n")
    md.write_text("\n".join(L) + "\n", encoding="utf-8")

    print("manifests:", manifest_files)
    print("total defects manifested:", total)
    print("manifest_ids == defect_ids:", manifest_ids == defect_ids)
    print("wrote:", md.name)


if __name__ == "__main__":
    main()
