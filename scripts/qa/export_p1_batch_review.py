#!/usr/bin/env python3
"""Export one canonical G4-A P1 batch with current vocabulary evidence.

The output is review material only. It joins the immutable batch manifest,
the findings register, and the current learner-facing vocabulary record so a
reviewer can adjudicate every field before building a correction payload.
"""

import argparse
import csv
import json
import pathlib
import re
import sys


ROOT = pathlib.Path(__file__).resolve().parents[2]
BATCHES = ROOT / "docs" / "g4a_p1_batches.json"
FINDINGS = ROOT / "docs" / "G4A_UKRAINIAN_QA_FINDINGS.csv"
VOCAB = ROOT / "web" / "vocabulary.js"


def load_vocab() -> dict[str, dict]:
    content = VOCAB.read_text(encoding="utf-8")
    match = re.fullmatch(
        r"window\.VOCABULARY_META=(.*?);\s*\nwindow\.VOCABULARY=(.*);\s*",
        content,
        re.DOTALL,
    )
    if not match:
        raise SystemExit("vocabulary.js does not match the expected format")
    rows = json.loads(match.group(2))
    return {row["id"]: row for row in rows}


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser()
    parser.add_argument("batch", choices=("T2", "T3", "T4"))
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()

    batch_ids = json.loads(BATCHES.read_text(encoding="utf-8"))[args.batch]
    with FINDINGS.open(encoding="utf-8", newline="") as handle:
        findings = {row["id"]: row for row in csv.DictReader(handle)}
    vocab = load_vocab()

    missing = [item_id for item_id in batch_ids if item_id not in findings or item_id not in vocab]
    if missing:
        raise SystemExit(f"missing canonical evidence for: {', '.join(missing)}")

    joined = []
    for item_id in batch_ids:
        finding = findings[item_id]
        entry = vocab[item_id]
        joined.append(
            {
                "id": item_id,
                "word": entry["word"],
                "pos": entry["pos"],
                "ua": entry["ua"],
                "definitionUa": entry["definitionUa"],
                "category": finding["category"],
                "issue": finding["issue"],
                "proposed_correction": finding["proposed_correction"],
                "confidence": finding["confidence"],
            }
        )

    if args.as_json:
        json.dump(joined, sys.stdout, ensure_ascii=False, indent=2)
        print()
    else:
        writer = csv.DictWriter(sys.stdout, fieldnames=joined[0].keys(), dialect="excel-tab")
        writer.writeheader()
        writer.writerows(joined)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
