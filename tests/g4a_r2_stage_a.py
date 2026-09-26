#!/usr/bin/env python3
"""Independent Stage A post-apply proof and isolated applicator negatives."""

from __future__ import annotations

import copy
import csv
import hashlib
import io
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts/qa"))
import apply_r2_p1_stage as app  # noqa: E402

BASE = "54daff49e05452eac3fef54e58a42c8719c673e5"
CHECKPOINT = "39d6f918c7087d3616acc9654eecfaf5219aefc4"
MANIFEST_SHA = "99aeb25b16e697fd3cbe42349a09d7bda80e50079ac5e6c5507f960f4b2c187a"
INPUT_BLOB = "1c184e84e5c63e3a9f8e386af13787664a23bd66"
STAGE_B = ("SB-1709", "SB-1721", "SB-1723", "SB-1724", "SB-1731",
           "SB-1733", "SB-1735", "SB-1738", "SB-1747", "SB-1750",
           "SB-1752", "SB-1753", "SB-1759", "SB-1760", "SB-1769")


def check(ok: bool, message: str) -> None:
    if not ok:
        raise AssertionError(message)


def git(*args: str) -> bytes:
    return subprocess.run(["git", *args], cwd=ROOT, check=True, capture_output=True).stdout


def blob(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def parse_bank(data: bytes) -> tuple[bytes, list[dict], bytes]:
    check(data.endswith(b";\n") and b"\r" not in data and not data.startswith(b"\xef\xbb\xbf"),
          "vocabulary is not UTF-8/LF")
    text = data.decode("utf-8")
    lines = text.splitlines(keepends=True)
    check(len(lines) == 2 and lines[0].startswith("window.VOCABULARY_META=") and
          lines[1].startswith("window.VOCABULARY="), "vocabulary wrapper changed")
    metadata = lines[0][len("window.VOCABULARY_META="):-2]
    records = lines[1][len("window.VOCABULARY="):-2]
    return metadata.encode("utf-8"), json.loads(records), lines[0].encode("utf-8")


def frozen_base_files() -> int:
    """Check every prior tracked blob, including manifest and guarded history."""
    entries = git("ls-tree", "-r", "-z", BASE).split(b"\0")
    checked = 0
    for entry in entries:
        if not entry:
            continue
        meta, raw_path = entry.split(b"\t", 1)
        mode, obj_type, expected = meta.decode("ascii").split(" ")
        check(obj_type == "blob", f"unexpected base tree object: {raw_path!r}")
        path = raw_path.decode("utf-8")
        if path == "web/vocabulary.js":
            continue
        actual = (ROOT / path).read_bytes()
        check(blob(actual) == expected, f"accepted base/history bytes changed: {path}")
        checked += 1
    check(git("merge-base", "HEAD", BASE).decode().strip() == BASE,
          "branch does not descend from exact accepted base")
    check(git("cat-file", "-t", CHECKPOINT).strip() == b"commit",
          "accepted reconciliation checkpoint missing")
    return checked


def negative_tests(input_bytes: bytes, manifest_bytes: bytes, payload: dict,
                   output_bytes: bytes) -> None:
    canonical = (ROOT / "web/vocabulary.js").read_bytes()

    def rejected(label: str, source: bytes, item: dict) -> None:
        try:
            app.candidate(source, manifest_bytes, item)
        except (ValueError, KeyError, TypeError, UnicodeError):
            pass
        else:
            raise AssertionError(f"negative accepted: {label}")
        check((ROOT / "web/vocabulary.js").read_bytes() == canonical,
              f"negative changed canonical learner file: {label}")
        print(f"PASS negative: {label}; canonical learner bytes unchanged")

    rejected("wrong input blob", input_bytes + b" ", copy.deepcopy(payload))
    missing = copy.deepcopy(payload)
    missing["rows"].pop(0)
    rejected("missing Stage A ID", input_bytes, missing)
    stage_b = copy.deepcopy(payload)
    stage_b["rows"][-1]["id"] = STAGE_B[0]
    rejected("injected Stage B ID", input_bytes, stage_b)
    altered = copy.deepcopy(payload)
    altered["rows"][0]["changes"]["definitionUa"] += " змінено"
    rejected("altered replacement value", input_bytes, altered)
    fingerprint = copy.deepcopy(payload)
    fingerprint["rows"][0]["current_pair_sha256"] = "0" * 64
    rejected("altered current-pair fingerprint", input_bytes, fingerprint)
    no_op = copy.deepcopy(payload)
    target = next(row for row in no_op["rows"] if row["id"] == "SB-1469")
    before = {row["id"]: row for row in parse_bank(input_bytes)[1]}
    target["changes"]["ua"] = before["SB-1469"]["ua"]
    rejected("inserted no-op correction", input_bytes, no_op)
    unsupported = copy.deepcopy(payload)
    unsupported["rows"][0]["changes"]["pos"] = "n."
    rejected("unsupported field", input_bytes, unsupported)
    wrong_output = copy.deepcopy(payload)
    wrong_output["_meta"]["expected_output_learner_git_blob"] = "0" * 40
    rejected("wrong expected-output blob", input_bytes, wrong_output)
    rejected("rerun against Stage A output", output_bytes, copy.deepcopy(payload))


def main() -> int:
    try:
        input_bytes = git("show", f"{BASE}:web/vocabulary.js")
        manifest_bytes = (ROOT / "docs/G4A_R2_P1_REMEDIATION_MANIFEST.csv").read_bytes()
        payload_bytes = (ROOT / "docs/G4A_R2_STAGE_A_PAYLOAD.json").read_bytes()
        output_bytes = (ROOT / "web/vocabulary.js").read_bytes()
        check(blob(input_bytes) == INPUT_BLOB, "accepted input learner blob mismatch")
        check(hashlib.sha256(manifest_bytes).hexdigest() == MANIFEST_SHA and
              manifest_bytes == git("show", f"{BASE}:docs/G4A_R2_P1_REMEDIATION_MANIFEST.csv"),
              "accepted manifest changed")
        check(b"\r" not in payload_bytes and payload_bytes.endswith(b"\n") and
              b"\r" not in output_bytes and output_bytes.endswith(b"\n"),
              "payload/output is not UTF-8/LF")
        payload = json.loads(payload_bytes.decode("utf-8"))
        check(payload_bytes == app.payload_bytes(payload), "payload encoding is not deterministic")
        pin = payload["_meta"]["expected_output_learner_git_blob"]
        check(blob(output_bytes) == pin, "written output blob differs from payload pin")
        check(app.candidate(input_bytes, manifest_bytes, payload) == output_bytes,
              "independent preimage rebuild differs from written learner bytes")

        before_meta, before, before_wrapper = parse_bank(input_bytes)
        after_meta, after, after_wrapper = parse_bank(output_bytes)
        check(len(before) == len(after) == 1784, "learner record count changed")
        before_ids = [row["id"] for row in before]
        after_ids = [row["id"] for row in after]
        check(before_ids == after_ids and len(set(after_ids)) == 1784,
              "learner stable ID order changed")
        check(before_meta == after_meta and before_wrapper == after_wrapper,
              "wrapper metadata changed")
        manifest = list(csv.DictReader(io.StringIO(manifest_bytes.decode("utf-8"), newline="")))
        targets = {row["id"]: row for row in manifest if row["stage"] == "A"}
        check(len(targets) == 250 and
              [row["id"] for row in manifest if row["stage"] == "B"] == list(STAGE_B),
              "Stage A/B roster changed")
        by_before = {row["id"]: row for row in before}
        by_after = {row["id"]: row for row in after}
        changed_ids = []
        field_counts = Counter()
        shapes = Counter()
        for sid in before_ids:
            old, new = by_before[sid], by_after[sid]
            check(old.get("ua") and old.get("definitionUa") and
                  new.get("ua") and new.get("definitionUa"), f"blank Ukrainian field: {sid}")
            check(old.get("translationQa") == new.get("translationQa"),
                  f"translationQa changed: {sid}")
            changed = tuple(key for key in ("ua", "definitionUa") if old[key] != new[key])
            if sid not in targets:
                check(old == new, f"non-target record changed: {sid}")
                continue
            accepted = targets[sid]
            effective = tuple(accepted["effective_fields"].split("|"))
            check(changed == effective, f"effective field set differs: {sid}")
            check(set(old) == set(new) and
                  all(old[key] == new[key] for key in old if key not in effective),
                  f"unauthorized target field changed: {sid}")
            for field in effective:
                check(new[field] == accepted[f"proposed_{field}"],
                      f"target differs from accepted proposal: {sid}.{field}")
                field_counts[field] += 1
            changed_ids.append(sid)
            shapes[changed] += 1
        check(len(changed_ids) == 250 and
              field_counts == {"ua": 38, "definitionUa": 246} and
              sum(field_counts.values()) == 284 and
              shapes == {("ua",): 4, ("definitionUa",): 212, ("ua", "definitionUa"): 34},
              "Stage A changed IDs, fields, or row shapes mismatch")
        check(by_before["SB-1469"]["ua"] == by_after["SB-1469"]["ua"] and
              by_before["SB-1469"]["definitionUa"] != by_after["SB-1469"]["definitionUa"],
              "SB-1469 no-op proposal was written or definition change omitted")
        for sid in STAGE_B:
            check((by_before[sid]["ua"], by_before[sid]["definitionUa"]) ==
                  (by_after[sid]["ua"], by_after[sid]["definitionUa"]),
                  f"Stage B pair changed: {sid}")
        frozen = frozen_base_files()
        negative_tests(input_bytes, manifest_bytes, payload, output_bytes)
    except (AssertionError, OSError, ValueError, KeyError, TypeError, UnicodeError,
            json.JSONDecodeError, subprocess.CalledProcessError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    print(f"PASS Stage A: 1784/1784 records; 250 IDs; 284 fields (38 ua / 246 definitionUa); shapes 4/212/34")
    print(f"PASS Stage B: all 15 full records and current pairs byte-equivalent; SB-1469.ua unchanged")
    print(f"PASS freeze: {frozen} accepted base/history files match exact Git blobs; checkpoint reachable")
    print(f"PASS output: UTF-8/LF; pinned blob {pin}; wrapper and translationQa unchanged")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
