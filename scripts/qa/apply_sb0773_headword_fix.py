#!/usr/bin/env python3
"""Apply the isolated SB-0773 structural provenance stamp.

The malformed ``minute2`` headword is repaired at the canonical source
(``Study Bank!A777`` and ``Oxford C1 Bank!B774`` are both ``minute``), so
``scripts/migrate_vocabulary.py`` already emits the correct ``minute`` headword
with its Oxford provenance retained. This isolated structural step therefore no
longer renames the headword; it verifies the source-repaired identity and
provenance, then applies the reviewed P1 structural-correction ``translationQa``
stamp (the T3-deferred SB-0773 disposition). Fail-closed input/output git-blob
guards keep the step deterministic and non-repeatable.
"""

import hashlib
import json
import pathlib
import re
import sys


ROOT = pathlib.Path(__file__).resolve().parents[2]
VOCAB_PATH = ROOT / "web" / "vocabulary.js"
EXPECTED_INPUT = "36c3d20539335cdffb505b0ab83957da8bea8110"
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
    # Headword repaired at source; migration already emits the correct identity.
    if entry["word"] != "minute" or entry["pos"] != "adj.":
        fail(f"unexpected SB-0773 identity: {entry['word']!r}, {entry['pos']!r}")
    # The source repair must also preserve the Oxford provenance join.
    if entry.get("sourceRefs", {}).get("oxfordId") != 773:
        fail("SB-0773 lost its Oxford provenance (sourceRefs.oxfordId != 773)")
    minute_ids = [item["id"] for item in vocab if item["word"].casefold() == "minute"]
    if minute_ids != ["SB-0773"]:
        fail(f"'minute' is not uniquely SB-0773: {minute_ids}")
    if any(item["word"].casefold() == "minute2" for item in vocab):
        fail("stale 'minute2' headword still present")

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
    print("applied SB-0773 structural provenance stamp (headword repaired at source)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
