#!/usr/bin/env python3
"""Release-identity check for the external review packet.

External review finding R4: at commit `fe720d5` the packet named a candidate
SHA that does not exist in the repository, because the SHA was stamped by a
later commit and then rewritten. A reviewer following the packet could not
resolve the release it described.

This check makes that failure automatic rather than editorial:

  1. the packet must identify its candidate by a git TAG, not by a bare hash
     that no commit can contain about itself;
  2. that tag must resolve to a commit in this repository;
  3. the packet stored *inside* the tagged commit must name the same tag, so
     the release describes itself;
  4. every commit-like hash mentioned anywhere in the packet must resolve;
  5. every repository path the packet lists must exist.

Run it after tagging a candidate.
"""
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs" / "G4_EXTERNAL_REVIEW_PACKET.md"
TAG_RE = re.compile(r"`(g\d+-candidate[-\w.]*)`")
SHA_RE = re.compile(r"`([0-9a-f]{7,40})`")
PATH_RE = re.compile(r"`((?:web|tests|scripts|docs|schemas)/[A-Za-z0-9_./*-]+)`")

fails = []


def fail(m):
    fails.append(m)


def git(*args):
    r = subprocess.run(["git", "-C", str(ROOT)] + list(args),
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    return r.returncode, (r.stdout or "").strip(), (r.stderr or "").strip()


if not PACKET.exists():
    print("FAIL: no review packet at", PACKET)
    sys.exit(1)

text = PACKET.read_text(encoding="utf-8")
section = text.split("## 2.")[0]

# --- 1. the candidate is named by a tag -------------------------------------
tags = sorted(set(TAG_RE.findall(section)))
if len(tags) != 1:
    fail(f"section 1 must name exactly one candidate tag, found {tags or 'none'}")
tag = tags[0] if tags else None

# --- 2. the tag resolves ----------------------------------------------------
tagged_sha = None
if tag:
    code, out, err = git("rev-parse", f"{tag}^{{commit}}")
    if code != 0:
        fail(f"candidate tag {tag!r} does not resolve in this repository ({err})")
    else:
        tagged_sha = out
        code, _, _ = git("merge-base", "--is-ancestor", tagged_sha, "HEAD")
        if code != 0:
            fail(f"candidate tag {tag!r} is not reachable from HEAD")

# --- 3. the tagged commit's own packet names the same tag -------------------
if tag and tagged_sha:
    code, out, err = git("show", f"{tag}:docs/G4_EXTERNAL_REVIEW_PACKET.md")
    if code != 0:
        fail(f"the commit tagged {tag} does not contain the review packet ({err})")
    elif f"`{tag}`" not in out.split("## 2.")[0]:
        fail(f"the packet inside {tag} does not identify itself as {tag}; a reviewer "
             f"checking out the tag would read a different release identity")

# --- 4. every hash mentioned must be reachable ------------------------------
# `git cat-file -e` is not enough: the SHA the first packet cited *did* exist in
# the local object store, as an orphan left by an amended commit, which is
# exactly why a reviewer on GitHub could not resolve it. The test is whether the
# commit is reachable from the branch a reviewer would check out.
shas = sorted(set(SHA_RE.findall(text)))
unresolved = []
for sha in shas:
    code, _, _ = git("merge-base", "--is-ancestor", sha, "HEAD")
    if code != 0:
        unresolved.append(sha)
for sha in unresolved:
    fail(f"the packet cites commit {sha}, which is not reachable from HEAD; a reviewer "
         f"cloning the repository could not resolve it")

# --- 5. every path mentioned must exist -------------------------------------
missing = []
for rel in sorted(set(PATH_RE.findall(text))):
    if "*" in rel:
        if not list(ROOT.glob(rel)):
            missing.append(rel)
    elif not (ROOT / rel).exists():
        missing.append(rel)
for rel in missing:
    fail(f"the packet cites {rel}, which does not exist")

print("RELEASE IDENTITY CHECK")
print("======================")
print("Packet            :", PACKET.relative_to(ROOT))
print("Candidate tag     :", tag or "(none)")
print("Resolves to       :", tagged_sha or "(unresolved)")
print("Hashes cited      :", len(shas), "checked,", len(unresolved), "unreachable")
print("Paths cited       :", len(set(PATH_RE.findall(text))), "checked,", len(missing), "missing")

if fails:
    for f in fails:
        print("FAIL:", f)
    sys.exit(1)
print("PASS: the packet identifies a release that exists and describes itself")
