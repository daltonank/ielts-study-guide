#!/usr/bin/env python3
"""Regression for the SB-0773 learner-facing headword and uniqueness rule."""

import json
import pathlib
import re


ROOT = pathlib.Path(__file__).resolve().parents[1]
text = (ROOT / "web" / "vocabulary.js").read_text(encoding="utf-8")
vocab = json.loads(re.search(r"window\.VOCABULARY=(\[.*\]);", text, re.DOTALL).group(1))
by_id = {entry["id"]: entry for entry in vocab}

assert by_id["SB-0773"]["word"] == "minute"
assert by_id["SB-0773"]["pos"] == "adj."
words = [entry["word"].casefold() for entry in vocab]
assert len(words) == len(set(words))
assert "minute2" not in words
print("G4-A SB-0773 HEADWORD PASS: minute is unique and minute2 is absent")
