#!/usr/bin/env python3
"""Validate completed R2 Pass-A chunks, including negative schema cases."""
from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import subprocess
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "qa" / "r2_pass_a.py"
LEARNER_BLOB = "1c184e84e5c63e3a9f8e386af13787664a23bd66"


def load_script():
    spec = importlib.util.spec_from_file_location("r2_pass_a", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def expect_rejected(module, chunk_number: int, source: dict, label: str) -> None:
    try:
        module.build_rows(chunk_number, source)
    except ValueError:
        return
    raise AssertionError(f"negative case was accepted: {label}")


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--through-chunk", type=int, required=True, choices=range(1, 5))
    args = parser.parse_args()
    module = load_script()
    all_ids: list[str] = []
    combined = Counter()
    for chunk_number in range(1, args.through_chunk + 1):
        source_path = ROOT / module.SOURCE_PATTERN.format(chunk=chunk_number)
        out_path = ROOT / module.OUT_PATTERN.format(chunk=chunk_number)
        source = json.loads(source_path.read_text(encoding="utf-8"))
        rows = module.build_rows(chunk_number, source)
        actual = out_path.read_bytes()
        assert actual == module.render_csv(rows), "non-deterministic chunk artifact"
        assert b"\r\n" not in actual and actual.endswith(b"\n")
        assert len(rows) == len({row["id"] for row in rows})
        assert all(row[axis] in module.AXIS_STATES for row in rows for axis in module.AXES)
        assert all(row["pass_a_disposition"] in module.DISPOSITIONS for row in rows)
        all_ids.extend(row["id"] for row in rows)
        combined.update(row["pass_a_disposition"] for row in rows)

        missing = copy.deepcopy(source)
        if missing["clean_candidate_ids"]:
            missing["clean_candidate_ids"].pop()
        else:
            missing["defects"].pop()
        expect_rejected(module, chunk_number, missing, "missing ID / fallback clean")

        duplicate = copy.deepcopy(source)
        duplicate["clean_candidate_ids"].append(duplicate["clean_candidate_ids"][0])
        expect_rejected(module, chunk_number, duplicate, "duplicate ID")

        if source["defects"]:
            bad_axis = copy.deepcopy(source)
            del bad_axis["defects"][0]["axes"][module.AXES[0]]
            expect_rejected(module, chunk_number, bad_axis, "missing axis evidence")
            bad_disposition = copy.deepcopy(source)
            bad_disposition["defects"][0]["disposition"] = "needs-human"
            expect_rejected(module, chunk_number, bad_disposition, "invalid disposition")

        print(
            f"chunk {chunk_number}: rows={len(rows)} "
            f"sha256={hashlib.sha256(actual).hexdigest()}"
        )

    assert len(all_ids) == len(set(all_ids))
    assert git("rev-parse", "HEAD:web/vocabulary.js") == LEARNER_BLOB
    if args.through_chunk == 4:
        summary_script = ROOT / "scripts" / "qa" / "r2_pass_a_summary.py"
        summary_spec = importlib.util.spec_from_file_location("r2_pass_a_summary", summary_script)
        assert summary_spec and summary_spec.loader
        summary_module = importlib.util.module_from_spec(summary_spec)
        summary_spec.loader.exec_module(summary_module)
        summary_path = ROOT / "docs" / "G4A_R2_PASS_A_SUMMARY.md"
        assert summary_path.read_bytes() == summary_module.render()
        assert b"\r\n" not in summary_path.read_bytes()
    print("G4-A R2 PASS-A GUARD PASS")
    print(f"through_chunk={args.through_chunk} rows={len(all_ids)} counts={dict(combined)}")
    print("negative cases: missing/fallback, duplicate, missing-axis, invalid-disposition rejected")
    print("learner blob unchanged=" + LEARNER_BLOB)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
