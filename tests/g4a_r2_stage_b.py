#!/usr/bin/env python3
"""Independent Stage B learner diff proof and isolated applicator negatives."""

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
import apply_r2_p1_stage_b as app  # noqa: E402

BASE = "db65e13ce66190b48ae6c1039dd93930b2798b25"
MANIFEST_COMMIT = "54daff49e05452eac3fef54e58a42c8719c673e5"
MANIFEST_SHA = "99aeb25b16e697fd3cbe42349a09d7bda80e50079ac5e6c5507f960f4b2c187a"
INPUT_BLOB = "d3153cdb71f4768a04bed883953ea788a38e0aaf"
IDS = ("SB-1709", "SB-1721", "SB-1723", "SB-1724", "SB-1731",
       "SB-1733", "SB-1735", "SB-1738", "SB-1747", "SB-1750",
       "SB-1752", "SB-1753", "SB-1759", "SB-1760", "SB-1769")


def check(ok: bool, message: str) -> None:
    if not ok:
        raise AssertionError(message)


def git(*args: str) -> bytes:
    return subprocess.run(["git", *args], cwd=ROOT, check=True,
                          capture_output=True).stdout


def blob(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def pair_sha(sid: str, ua: str, definition: str) -> str:
    return hashlib.sha256(f"{sid}\0{ua}\0{definition}".encode("utf-8")).hexdigest()


def parse_bank(data: bytes) -> tuple[bytes, list[dict]]:
    check(data.endswith(b";\n") and b"\r" not in data and
          not data.startswith(b"\xef\xbb\xbf"), "vocabulary is not UTF-8/LF")
    text = data.decode("utf-8")
    lines = text.splitlines(keepends=True)
    check(len(lines) == 2 and lines[0].startswith("window.VOCABULARY_META=") and
          lines[1].startswith("window.VOCABULARY="), "vocabulary wrapper changed")
    rows = json.loads(lines[1][len("window.VOCABULARY="):-2])
    check(isinstance(rows, list), "vocabulary records are not an array")
    return lines[0].encode("utf-8"), rows


def frozen_base_files() -> int:
    """Compare every Stage A tracked file except the authorized learner bank."""
    entries = git("ls-tree", "-r", "-z", BASE).split(b"\0")
    checked = 0
    for entry in entries:
        if not entry:
            continue
        meta, raw_path = entry.split(b"\t", 1)
        _, obj_type, expected = meta.decode("ascii").split(" ")
        check(obj_type == "blob", f"unexpected base tree object: {raw_path!r}")
        path = raw_path.decode("utf-8")
        if path == "web/vocabulary.js":
            continue
        check(blob((ROOT / path).read_bytes()) == expected,
              f"Stage A artifact or prior evidence changed: {path}")
        checked += 1
    check(git("merge-base", "HEAD", BASE).decode().strip() == BASE,
          "branch does not descend from exact Stage A base")
    return checked


def negative_tests(input_bytes: bytes, manifest_bytes: bytes, payload: dict,
                   output_bytes: bytes, before: dict[str, dict]) -> None:
    canonical = (ROOT / "web/vocabulary.js").read_bytes()

    def rejected(label: str, source: bytes, item: dict) -> None:
        try:
            app.candidate(source, manifest_bytes, item)
        except (ValueError, KeyError, TypeError, UnicodeError):
            pass
        else:
            raise AssertionError(f"negative accepted: {label}")
        check((ROOT / "web/vocabulary.js").read_bytes() == canonical,
              f"negative changed canonical learner bytes: {label}")
        print(f"PASS negative: {label}; canonical learner bytes unchanged")

    rejected("wrong input blob", input_bytes + b" ", copy.deepcopy(payload))
    missing = copy.deepcopy(payload)
    missing["rows"].pop(0)
    rejected("missing Stage B ID", input_bytes, missing)
    injected = copy.deepcopy(payload)
    injected["rows"][-1]["id"] = "SB-1707"
    rejected("injected non-Stage-B ID", input_bytes, injected)
    altered = copy.deepcopy(payload)
    altered["rows"][0]["changes"]["definitionUa"] += " змінено"
    rejected("altered proposal", input_bytes, altered)
    fingerprint = copy.deepcopy(payload)
    fingerprint["rows"][0]["current_pair_sha256"] = "0" * 64
    rejected("altered fingerprint", input_bytes, fingerprint)
    no_op = copy.deepcopy(payload)
    no_op["rows"][IDS.index("SB-1760")]["changes"]["ua"] = before["SB-1760"]["ua"]
    rejected("no-op insertion", input_bytes, no_op)
    unsupported = copy.deepcopy(payload)
    unsupported["rows"][0]["changes"]["pos"] = "n."
    rejected("unsupported field", input_bytes, unsupported)
    wrong_pin = copy.deepcopy(payload)
    wrong_pin["_meta"]["expected_output_learner_git_blob"] = "0" * 40
    rejected("wrong output pin", input_bytes, wrong_pin)
    rejected("rerun against Stage B output", output_bytes, copy.deepcopy(payload))


def main() -> int:
    try:
        input_bytes = git("show", f"{BASE}:web/vocabulary.js")
        manifest_bytes = (ROOT / "docs/G4A_R2_P1_REMEDIATION_MANIFEST.csv").read_bytes()
        payload_bytes = (ROOT / "docs/G4A_R2_STAGE_B_PAYLOAD.json").read_bytes()
        output_bytes = (ROOT / "web/vocabulary.js").read_bytes()
        check(blob(input_bytes) == INPUT_BLOB, "Stage A input blob mismatch")
        check(hashlib.sha256(manifest_bytes).hexdigest() == MANIFEST_SHA and
              manifest_bytes == git("show", f"{MANIFEST_COMMIT}:docs/G4A_R2_P1_REMEDIATION_MANIFEST.csv"),
              "accepted manifest bytes changed")
        check(payload_bytes.endswith(b"\n") and b"\r" not in payload_bytes and
              not payload_bytes.startswith(b"\xef\xbb\xbf"), "payload is not UTF-8/LF")
        payload = json.loads(payload_bytes.decode("utf-8"))
        check(payload_bytes == (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode("utf-8"),
              "payload serialization changed")
        pin = payload["_meta"]["expected_output_learner_git_blob"]
        check(blob(output_bytes) == pin, "written learner blob differs from payload pin")
        check(app.candidate(input_bytes, manifest_bytes, payload) == output_bytes,
              "guarded preimage rebuild differs from written bytes")

        before_wrapper, before_rows = parse_bank(input_bytes)
        after_wrapper, after_rows = parse_bank(output_bytes)
        check(before_wrapper == after_wrapper, "wrapper metadata changed")
        check(len(before_rows) == len(after_rows) == 1784,
              "learner record count changed")
        before_ids = [row["id"] for row in before_rows]
        after_ids = [row["id"] for row in after_rows]
        check(before_ids == after_ids and len(set(after_ids)) == 1784,
              "stable ID order or uniqueness changed")
        before = dict(zip(before_ids, before_rows))
        after = dict(zip(after_ids, after_rows))

        manifest = list(csv.DictReader(io.StringIO(manifest_bytes.decode("utf-8"), newline="")))
        targets = {row["id"]: row for row in manifest if row["stage"] == "B"}
        stage_a_ids = {row["id"] for row in manifest if row["stage"] == "A"}
        check(tuple(targets) == IDS and len(stage_a_ids) == 250,
              "accepted Stage A/B roster changed")
        check(tuple(item["id"] for item in payload["rows"]) == IDS and
              len(payload["rows"]) == 15, "payload roster changed")
        changed_ids = []
        field_counts = Counter()
        shapes = Counter()
        expected_after = copy.deepcopy(before_rows)
        by_expected = {row["id"]: row for row in expected_after}
        for sid in before_ids:
            old, new = before[sid], after[sid]
            check(old.get("ua") and old.get("definitionUa") and
                  new.get("ua") and new.get("definitionUa"),
                  f"blank Ukrainian field: {sid}")
            check(old.get("translationQa") == new.get("translationQa"),
                  f"translationQa changed: {sid}")
            if sid not in targets:
                check(old == new, f"non-Stage-B record changed: {sid}")
                continue
            accepted = targets[sid]
            effective = tuple(accepted["effective_fields"].split("|"))
            changed = tuple(field for field in ("ua", "definitionUa")
                            if old[field] != new[field])
            check(changed == effective and
                  pair_sha(sid, old["ua"], old["definitionUa"]) ==
                  accepted["current_pair_sha256"],
                  f"effective changes or accepted current pair differ: {sid}")
            check(set(old) == set(new) and
                  all(old[key] == new[key] for key in old if key not in effective),
                  f"unauthorized target field changed: {sid}")
            for field in effective:
                proposal = accepted[f"proposed_{field}"]
                check(proposal and new[field] == proposal,
                      f"final value differs from accepted proposal: {sid}.{field}")
                by_expected[sid][field] = proposal
                field_counts[field] += 1
            changed_ids.append(sid)
            shapes[changed] += 1
        check(tuple(changed_ids) == IDS and
              field_counts == {"ua": 1, "definitionUa": 15} and
              sum(field_counts.values()) == 16 and
              shapes == {("definitionUa",): 14, ("ua", "definitionUa"): 1},
              "Stage B changed IDs, fields, or row shapes mismatch")
        check(all(before[sid] == after[sid] for sid in stage_a_ids),
              "one of 250 Stage A records changed")
        independent_output = before_wrapper + b"window.VOCABULARY=" + \
            json.dumps(expected_after, ensure_ascii=False).encode("utf-8") + b";\n"
        check(independent_output == output_bytes,
              "independent manifest projection differs from written output")
        frozen = frozen_base_files()
        negative_tests(input_bytes, manifest_bytes, payload, output_bytes, before)
    except (AssertionError, OSError, ValueError, KeyError, TypeError, UnicodeError,
            json.JSONDecodeError, subprocess.CalledProcessError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    print("PASS Stage B: 1784/1784 records; 15 IDs; 16 fields (1 ua / 15 definitionUa); shapes 14/1")
    print("PASS Stage A: all 250 full records unchanged; every non-Stage-B record identical")
    print(f"PASS freeze: {frozen} Stage A base/history files match exact Git blobs")
    print(f"PASS output: UTF-8/LF; pinned blob {pin}; wrapper and translationQa unchanged")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
