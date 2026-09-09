#!/usr/bin/env python3
"""Apply a reviewed G4-A P1 correction batch with fail-closed guards."""

import argparse
import hashlib
import json
import pathlib
import re


ROOT = pathlib.Path(__file__).resolve().parents[2]
VOCAB_PATH = ROOT / "web" / "vocabulary.js"
BATCH_PATH = ROOT / "docs" / "g4a_p1_batches.json"
MUTABLE_FIELDS = ("ua", "definitionUa", "pos", "register")


def git_blob_sha1(data: bytes) -> str:
    digest = hashlib.sha1()
    digest.update(b"blob " + str(len(data)).encode() + b"\0")
    digest.update(data)
    return digest.hexdigest()


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("payload", type=pathlib.Path)
    parser.add_argument("--compute-only", action="store_true")
    args = parser.parse_args()

    payload = json.loads(args.payload.read_text(encoding="utf-8"))
    meta = payload["_meta"]
    corrections = payload["corrections"]
    batch_name = meta["manifest_batch"]
    manifest = json.loads(BATCH_PATH.read_text(encoding="utf-8"))[batch_name]
    resolved_without_edit = meta.get("resolved_without_edit", [])
    deferred = meta.get("deferred", [])

    accounted = list(corrections) + resolved_without_edit + deferred
    if len(accounted) != len(set(accounted)):
        fail("corrections, resolved_without_edit, and deferred overlap")
    if set(accounted) != set(manifest):
        missing = sorted(set(manifest) - set(accounted))
        extra = sorted(set(accounted) - set(manifest))
        fail(f"manifest accounting mismatch; missing={missing}, extra={extra}")
    if len(manifest) != meta["manifest_count"]:
        fail("manifest_count does not match canonical batch manifest")
    if len(corrections) != meta["apply_count"]:
        fail("apply_count does not match correction payload")

    raw_on_disk = VOCAB_PATH.read_bytes()
    if b"\r\n" in raw_on_disk and b"\n" in raw_on_disk.replace(b"\r\n", b""):
        fail("vocabulary.js contains mixed line endings")
    # Git stores this generated artifact with LF. Windows may check it out with
    # CRLF, so normalize before enforcing the canonical git-blob guard.
    raw = raw_on_disk.replace(b"\r\n", b"\n")
    actual_in = git_blob_sha1(raw)
    if actual_in != meta["expected_input_blob_sha1"]:
        fail(
            f"input blob {actual_in} != expected {meta['expected_input_blob_sha1']}; "
            "refusing to mutate"
        )

    match = re.fullmatch(
        r"window\.VOCABULARY_META=(.*?);\s*\nwindow\.VOCABULARY=(.*);\s*",
        raw.decode("utf-8"),
        re.DOTALL,
    )
    if not match:
        fail("vocabulary.js does not match the expected format")
    meta_raw = match.group(1)
    vocab = json.loads(match.group(2))
    by_id = {entry["id"]: entry for entry in vocab}

    missing_ids = sorted(set(accounted) - set(by_id))
    if missing_ids:
        fail(f"vocabulary records missing: {missing_ids}")

    applied = []
    for item_id, correction in corrections.items():
        unsupported = sorted(set(correction) - set(MUTABLE_FIELDS))
        if unsupported:
            fail(f"{item_id} attempts unsupported fields: {unsupported}")
        entry = by_id[item_id]
        changed = []
        for field in MUTABLE_FIELDS:
            if field in correction and correction[field] != entry.get(field):
                entry[field] = correction[field]
                changed.append(field)
        if not changed:
            fail(f"{item_id} changes no field")
        entry["translationQa"] = (
            f"Reviewed — G4-A P1 correction applied ({meta['review_date']})"
        )
        applied.append((item_id, changed))

    if len(vocab) != 1784:
        fail(f"record count changed: {len(vocab)}")
    ids = [entry["id"] for entry in vocab]
    if len(ids) != len(set(ids)):
        fail("duplicate IDs introduced")
    if any(not entry.get("ua") or not entry.get("definitionUa") for entry in vocab):
        fail("blank ua or definitionUa introduced")

    new_content = (
        f"window.VOCABULARY_META={meta_raw};\n"
        f"window.VOCABULARY={json.dumps(vocab, ensure_ascii=False)};\n"
    ).encode("utf-8")
    actual_out = git_blob_sha1(new_content)

    print(f"batch={batch_name} manifest={len(manifest)} applied={len(applied)} ")
    print(
        f"resolved_without_edit={len(resolved_without_edit)} deferred={len(deferred)}"
    )
    print(f"input={actual_in} output={actual_out}")
    if args.compute_only:
        print("compute-only: nothing written")
        return 0
    expected_out = meta["expected_output_blob_sha1"]
    if not expected_out or expected_out == "TBD":
        fail("expected_output_blob_sha1 is unset; run --compute-only and pin it")
    if actual_out != expected_out:
        fail(f"output blob {actual_out} != expected {expected_out}; nothing written")
    VOCAB_PATH.write_bytes(new_content)
    print(f"wrote {VOCAB_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
