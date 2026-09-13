#!/usr/bin/env python3
"""Durable, mechanical, reproducible blind-sample selector for G4-A T5-B follow-up review.

Records, in one deterministic run, the seed, the pool definition, the allocation rule, and
the exact selected stable IDs so a reviewer can re-derive the identical 48-item sample and
audit the linguistic review against a fixed target set (no post-hoc cherry-picking).

Selector contract (fixed):
  * Pool: every learner-facing record in web/vocabulary.js (the full shipped bank, 1,784).
  * Strata: group by `pos`.
  * Ordering: POS keys sorted lexicographically; IDs sorted ascending within each stratum.
  * Size: n = 48.
  * Allocation: proportional by largest remainder (Hamilton), with POS-lexicographic tie-break
    when fractional remainders tie.
  * Randomisation: a SINGLE random.Random(SEED) instance, walking strata in sorted-POS order,
    shuffling each stratum's ascending-sorted ID list, then taking that stratum's allocation.

Usage:
  python scripts/qa/select_blind_sample.py            # writes the durable JSON artifact
  python scripts/qa/select_blind_sample.py --check     # re-derive and verify it matches
"""
import argparse
import json
import pathlib
import random
import re

SEED = 20260912
SAMPLE_N = 48
ROOT = pathlib.Path(__file__).resolve().parents[2]
VOCAB = ROOT / "web" / "vocabulary.js"
OUT = ROOT / "docs" / "G4A_T5B_BLIND_SAMPLE_20260912.json"


def load_vocab():
    text = VOCAB.read_text(encoding="utf-8")
    return json.loads(re.search(r"window\.VOCABULARY=(\[.*\]);", text, re.DOTALL).group(1))


def allocate(strata_sizes, n):
    """Largest-remainder proportional allocation; tie-break by POS-lexicographic order."""
    total = sum(strata_sizes.values())
    exact = {pos: n * size / total for pos, size in strata_sizes.items()}
    floor = {pos: int(v) for pos, v in exact.items()}
    remaining = n - sum(floor.values())
    # Order candidates by descending remainder, then ascending POS (lexicographic) tie-break.
    order = sorted(strata_sizes, key=lambda pos: (-(exact[pos] - floor[pos]), pos))
    for pos in order[:remaining]:
        floor[pos] += 1
    # Never allocate more than a stratum has.
    for pos in floor:
        floor[pos] = min(floor[pos], strata_sizes[pos])
    return floor


def select():
    vocab = load_vocab()
    strata = {}
    for e in vocab:
        strata.setdefault(e.get("pos") or "", []).append(e["id"])
    sizes = {pos: len(ids) for pos, ids in strata.items()}
    quota = allocate(sizes, SAMPLE_N)
    rng = random.Random(SEED)
    selected = []
    per_pos = {}
    for pos in sorted(strata):            # sorted-POS order, single RNG instance
        ids = sorted(strata[pos])         # ascending
        rng.shuffle(ids)
        take = ids[:quota[pos]]
        per_pos[pos] = sorted(take)
        selected.extend(take)
    selected = sorted(selected)
    assert len(selected) == SAMPLE_N, f"selected {len(selected)} != {SAMPLE_N}"
    assert len(set(selected)) == SAMPLE_N, "duplicate ids selected"
    return {
        "seed": SEED,
        "sample_n": SAMPLE_N,
        "pool_definition": "All learner-facing records in web/vocabulary.js (full shipped bank).",
        "pool_size": len(vocab),
        "allocation_rule": ("Strata by pos; POS keys sorted lexicographically, IDs ascending; "
                            "n=48 proportional allocation by largest remainder (Hamilton) with "
                            "POS-lexicographic tie-break; single random.Random(20260912) shuffling "
                            "each stratum in sorted-POS order, then taking its allocation."),
        "strata_sizes": dict(sorted(sizes.items())),
        "allocation": dict(sorted(quota.items())),
        "selected_by_pos": per_pos,
        "selected_ids": selected,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    result = select()
    if args.check:
        existing = json.loads(OUT.read_text(encoding="utf-8"))
        same = existing.get("selected_ids") == result["selected_ids"] and existing.get("seed") == SEED
        print("CHECK", "PASS" if same else "FAIL", "- selected_ids reproduce" if same else "- MISMATCH")
        return 0 if same else 1
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"seed={SEED} n={SAMPLE_N} pool={result['pool_size']}")
    print("selected:", ",".join(result["selected_ids"]))
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
