#!/usr/bin/env python3
"""Apply the isolated SB-0773 malformed-headword correction."""

import hashlib
import json
import pathlib
import re
import sys


ROOT = pathlib.Path(__file__).resolve().parents[2]
VOCAB_PATH = ROOT / "web" / "vocabulary.js"
EXPECTED_INPUT = "0d144c7089e4993fac0b61a66b1c8b5a68c57834"
EXPECTED_OUTPUT = "9282d2013dcf382bbb439384247a0be0be0dede2"
REVIEW_DATE = "2026-09-09"


def blob_sha(data: bytes) -> str:
    digest = hashlib.sha1()
    digest.update(b"blob " + str(len(data)).encode() + b"\0")
    digest.update(data)
    return digest.hexdigest()


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def main() -> int:
    compute_only = "--compute-only" in sys.argv[1:]
    raw = VOCAB_PATH.read_bytes().replace(b"\r\n", b"\n")
    actual_input = blob_sha(raw)
    if actual_input != EXPECTED_INPUT:
        fail(f"input blob {actual_input} != expected {EXPECTED_INPUT}")

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
    entry = by_id.get("SB-0773")
    if not entry:
        fail("SB-0773 is missing")
    if entry["word"] != "minute2" or entry["pos"] != "adj.":
        fail(f"unexpected SB-0773 identity: {entry['word']!r}, {entry['pos']!r}")
    if any(other["word"].casefold() == "minute" for other in vocab):
        fail("minute already exists; rename would violate normalized-headword uniqueness")

    entry["word"] = "minute"
    entry["translationQa"] = f"Reviewed — G4-A P1 structural correction applied ({REVIEW_DATE})"
    words = [item["word"].casefold() for item in vocab]
    if len(words) != len(set(words)):
        fail("normalized-headword collision introduced")

    output = (
        f"window.VOCABULARY_META={meta_raw};\n"
        f"window.VOCABULARY={json.dumps(vocab, ensure_ascii=False)};\n"
    ).encode("utf-8")
    actual_output = blob_sha(output)
    print(f"input={actual_input} output={actual_output}")
    if compute_only:
        print("compute-only: nothing written")
        return 0
    if EXPECTED_OUTPUT == "TBD":
        fail("EXPECTED_OUTPUT is unset; run --compute-only and pin it")
    if actual_output != EXPECTED_OUTPUT:
        fail(f"output blob {actual_output} != expected {EXPECTED_OUTPUT}")
    VOCAB_PATH.write_bytes(output)
    print("applied SB-0773: minute2 -> minute")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
