#!/usr/bin/env python3
"""Build and apply the accepted G4A-CX-09 Stage B post-migration payload."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import subprocess
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "docs/G4A_R2_P1_REMEDIATION_MANIFEST.csv"
PAYLOAD = ROOT / "docs/G4A_R2_STAGE_B_PAYLOAD.json"
VOCAB = ROOT / "web/vocabulary.js"
BASE = "db65e13ce66190b48ae6c1039dd93930b2798b25"
MANIFEST_COMMIT = "54daff49e05452eac3fef54e58a42c8719c673e5"
MANIFEST_SHA = "99aeb25b16e697fd3cbe42349a09d7bda80e50079ac5e6c5507f960f4b2c187a"
INPUT_BLOB = "d3153cdb71f4768a04bed883953ea788a38e0aaf"
IDS = ("SB-1709", "SB-1721", "SB-1723", "SB-1724", "SB-1731",
       "SB-1733", "SB-1735", "SB-1738", "SB-1747", "SB-1750",
       "SB-1752", "SB-1753", "SB-1759", "SB-1760", "SB-1769")
FIELDS = ("ua", "definitionUa")


def require(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)


def git_blob(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def pair_sha(sid: str, ua: str, definition: str) -> str:
    return hashlib.sha256(f"{sid}\0{ua}\0{definition}".encode("utf-8")).hexdigest()


def lf_text(data: bytes, label: str) -> str:
    require(data.endswith(b"\n") and b"\r" not in data and
            not data.startswith(b"\xef\xbb\xbf"), f"{label}: UTF-8/LF required")
    return data.decode("utf-8")


def accepted_rows(data: bytes) -> list[dict[str, str]]:
    text = lf_text(data, "manifest")
    require(hashlib.sha256(data).hexdigest() == MANIFEST_SHA,
            "accepted manifest SHA mismatch")
    reader = csv.DictReader(io.StringIO(text, newline=""))
    rows = list(reader)
    require(len(rows) == 265 and all(None not in row and
            all(value is not None for value in row.values()) for row in rows),
            "manifest row structure changed")
    all_ids = [row["id"] for row in rows]
    stage_a = [row for row in rows if row["stage"] == "A"]
    stage_b = [row for row in rows if row["stage"] == "B"]
    require(all_ids == sorted(set(all_ids)) and rows == stage_a + stage_b and
            len(stage_a) == 250 and tuple(row["id"] for row in stage_b) == IDS,
            "accepted Stage A/B partition or Stage B roster changed")
    return stage_b


def bank_parts(data: bytes) -> tuple[bytes, list[dict], bytes]:
    lf_text(data, "learner vocabulary")
    marker = b"\nwindow.VOCABULARY="
    require(data.count(marker) == 1 and data.startswith(b"window.VOCABULARY_META=")
            and data.endswith(b";\n"), "learner wrapper changed")
    prefix, body = data.split(marker, 1)
    require(prefix.endswith(b";"), "learner metadata wrapper changed")
    json.loads(prefix[len(b"window.VOCABULARY_META="):-1])
    raw_json = body[:-2]
    rows = json.loads(raw_json)
    require(isinstance(rows, list) and len(rows) == 1784 and
            all(isinstance(row, dict) and isinstance(row.get("id"), str)
                for row in rows), "learner record structure changed")
    require(len({row["id"] for row in rows}) == 1784, "duplicate learner IDs")
    require(json.dumps(rows, ensure_ascii=False).encode("utf-8") == raw_json,
            "learner JSON serialization changed")
    return prefix + marker, rows, b";\n"


def payload_bytes(payload: dict) -> bytes:
    return (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def candidate(input_bytes: bytes, manifest_bytes: bytes, payload: dict,
              *, require_pin: bool = True) -> bytes:
    """Return candidate bytes only after every manifest and payload guard passes."""
    require(git_blob(input_bytes) == INPUT_BLOB, "wrong input learner blob")
    verify_repository(manifest_bytes)
    accepted = accepted_rows(manifest_bytes)
    expected_meta = {
        "ticket": "G4A-CX-09", "stage": "B", "stage_a_base_commit": BASE,
        "source_manifest_commit": MANIFEST_COMMIT,
        "source_manifest_sha256": MANIFEST_SHA,
        "expected_input_learner_git_blob": INPUT_BLOB,
        "row_count": 15, "effective_ua_count": 1,
        "effective_definitionUa_count": 15,
    }
    require(isinstance(payload, dict) and set(payload) == {"_meta", "rows"} and
            isinstance(payload["_meta"], dict) and
            set(payload["_meta"]) == set(expected_meta) | {"expected_output_learner_git_blob"} and
            all(payload["_meta"][key] == value for key, value in expected_meta.items()),
            "payload metadata, base, or manifest pin mismatch")
    pin = payload["_meta"]["expected_output_learner_git_blob"]
    require(not require_pin or (isinstance(pin, str) and len(pin) == 40 and
            all(char in "0123456789abcdef" for char in pin)),
            "expected output blob is not pinned")
    rows = payload["rows"]
    require(isinstance(rows, list) and len(rows) == 15 and
            all(isinstance(row, dict) for row in rows) and
            tuple(row.get("id") for row in rows) == IDS,
            "payload ID set/order differs from exact Stage B roster")
    prefix, bank, suffix = bank_parts(input_bytes)
    by_id = {row["id"]: row for row in bank}
    fields = Counter()
    shapes = Counter()
    for item, source in zip(rows, accepted):
        sid = source["id"]
        require(set(item) == {"id", "current_pair_sha256", "changes"} and
                isinstance(item["changes"], dict), f"{sid}: payload row schema changed")
        current = by_id.get(sid)
        require(current is not None, f"{sid}: learner record missing")
        fingerprint = pair_sha(sid, current["ua"], current["definitionUa"])
        require(fingerprint == source["current_pair_sha256"] ==
                item["current_pair_sha256"], f"{sid}: current-pair fingerprint mismatch")
        changes = item["changes"]
        effective = tuple(source["effective_fields"].split("|"))
        require(tuple(changes) == effective and
                effective == tuple(field for field in FIELDS if field in effective),
                f"{sid}: unsupported or missing effective field")
        for field, replacement in changes.items():
            require(isinstance(replacement, str) and replacement and
                    replacement.strip() == replacement and
                    "\r" not in replacement and "\n" not in replacement,
                    f"{sid}.{field}: blank or unsupported replacement")
            require(replacement == source[f"proposed_{field}"] and
                    replacement != current[field],
                    f"{sid}.{field}: replacement differs from accepted effective proposal or is a no-op")
            fields[field] += 1
        shapes[tuple(changes)] += 1
    require(fields == {"ua": 1, "definitionUa": 15} and
            shapes == {("definitionUa",): 14, ("ua", "definitionUa"): 1} and
            rows[IDS.index("SB-1760")]["changes"].keys() == {"ua", "definitionUa"},
            "Stage B field counts or row shapes changed")
    for item in rows:
        for field, replacement in item["changes"].items():
            by_id[item["id"]][field] = replacement
    require(all(row.get("ua") and row.get("definitionUa") for row in bank),
            "blank Ukrainian learner field")
    output = prefix + json.dumps(bank, ensure_ascii=False).encode("utf-8") + suffix
    if require_pin:
        require(git_blob(output) == pin, "expected output learner blob mismatch")
    return output


def build_payload(input_bytes: bytes, manifest_bytes: bytes) -> dict:
    require(git_blob(input_bytes) == INPUT_BLOB, "wrong input learner blob")
    stage_b = accepted_rows(manifest_bytes)
    _, bank, _ = bank_parts(input_bytes)
    by_id = {row["id"]: row for row in bank}
    corrections = []
    for row in stage_b:
        sid = row["id"]
        current = by_id.get(sid)
        require(current is not None and pair_sha(sid, current["ua"],
                current["definitionUa"]) == row["current_pair_sha256"],
                f"{sid}: accepted current pair mismatch")
        effective = row["effective_fields"].split("|")
        changes = {field: row[f"proposed_{field}"] for field in effective}
        corrections.append({"id": sid, "current_pair_sha256": row["current_pair_sha256"],
                            "changes": changes})
    payload = {"_meta": {"ticket": "G4A-CX-09", "stage": "B",
                         "stage_a_base_commit": BASE,
                         "source_manifest_commit": MANIFEST_COMMIT,
                         "source_manifest_sha256": MANIFEST_SHA,
                         "expected_input_learner_git_blob": INPUT_BLOB,
                         "expected_output_learner_git_blob": "",
                         "row_count": 15, "effective_ua_count": 1,
                         "effective_definitionUa_count": 15},
               "rows": corrections}
    first = candidate(input_bytes, manifest_bytes, payload, require_pin=False)
    second = candidate(input_bytes, manifest_bytes, payload, require_pin=False)
    require(first == second, "compute-only rebuild changed output bytes")
    payload["_meta"]["expected_output_learner_git_blob"] = git_blob(first)
    require(candidate(input_bytes, manifest_bytes, payload) == first,
            "pinned output differs from candidate")
    return payload


def git_bytes(rev: str, path: str) -> bytes:
    return subprocess.run(["git", "show", f"{rev}:{path}"], cwd=ROOT,
                          check=True, capture_output=True).stdout


def verify_repository(manifest_bytes: bytes) -> None:
    merge_base = subprocess.run(["git", "merge-base", "HEAD", BASE], cwd=ROOT,
                                check=True, capture_output=True).stdout.decode().strip()
    require(merge_base == BASE, "HEAD does not descend from exact Stage A base")
    require(git_blob(git_bytes(BASE, "web/vocabulary.js")) == INPUT_BLOB,
            "Stage A base learner blob changed")
    require(git_bytes(MANIFEST_COMMIT, "docs/G4A_R2_P1_REMEDIATION_MANIFEST.csv") ==
            manifest_bytes and hashlib.sha256(manifest_bytes).hexdigest() == MANIFEST_SHA,
            "accepted manifest source or SHA mismatch")
    entries = subprocess.run(["git", "ls-tree", "-r", "-z", BASE], cwd=ROOT,
                             check=True, capture_output=True).stdout.split(b"\0")
    for entry in entries:
        if not entry:
            continue
        metadata, raw_path = entry.split(b"\t", 1)
        _, object_type, expected_blob = metadata.decode("ascii").split(" ")
        require(object_type == "blob", "unexpected Stage A base tree object")
        path = raw_path.decode("utf-8")
        if path != "web/vocabulary.js":
            require(git_blob((ROOT / path).read_bytes()) == expected_blob,
                    f"Stage A artifact or prior evidence changed: {path}")


def main() -> int:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--prepare", action="store_true")
    group.add_argument("--compute-only", action="store_true")
    group.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    try:
        manifest_bytes = MANIFEST.read_bytes()
        verify_repository(manifest_bytes)
        input_bytes = VOCAB.read_bytes()
        if args.prepare:
            payload = build_payload(input_bytes, manifest_bytes)
            raw = payload_bytes(payload)
            require(not PAYLOAD.exists() or PAYLOAD.read_bytes() == raw,
                    "existing payload differs from deterministic build")
            PAYLOAD.write_bytes(raw)
            print(f"PASS prepared 15 Stage B IDs; 1 ua / 15 definitionUa; output={payload['_meta']['expected_output_learner_git_blob']}")
            return 0
        raw = PAYLOAD.read_bytes()
        lf_text(raw, "payload")
        payload = json.loads(raw)
        require(payload_bytes(payload) == raw, "payload serialization differs from deterministic form")
        first = candidate(input_bytes, manifest_bytes, payload)
        second = candidate(VOCAB.read_bytes(), manifest_bytes, payload)
        require(first == second, "compute-only rebuild changed output bytes")
        if args.compute_only:
            print(f"PASS compute-only: two byte-identical candidates; output={git_blob(first)}; nothing written")
            return 0
        untouched = VOCAB.read_bytes()
        require(untouched == input_bytes, "learner input changed before apply")
        output = candidate(untouched, manifest_bytes, payload)
        require(output == first, "apply candidate differs from compute-only candidate")
        VOCAB.write_bytes(output)
        require(git_blob(VOCAB.read_bytes()) ==
                payload["_meta"]["expected_output_learner_git_blob"],
                "written learner blob differs from pin")
        print(f"PASS applied Stage B once; output={git_blob(output)}")
        return 0
    except (OSError, ValueError, KeyError, TypeError, UnicodeError,
            json.JSONDecodeError, subprocess.CalledProcessError) as exc:
        print(f"FAIL: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
