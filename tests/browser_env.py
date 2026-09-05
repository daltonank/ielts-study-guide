#!/usr/bin/env python3
"""Portable Chromium resolution for the Playwright-driven validation scripts.

Defect D4-001: tests/responsive_check.py, tests/g3_reading_responsive.py,
tests/g3_reading_functional.py and tests/g3_reading_accessibility.py originally
hard-coded executable_path="/usr/bin/chromium". That path only exists on the
Linux environment the G3 scripts were authored in, so every browser-driven gate
check failed to launch anywhere else. The checks themselves were correct; only
the browser lookup was not portable.

Resolution order:
  1. $IELTS_CHROMIUM                      (explicit override)
  2. the first existing well-known Chromium/Chrome/Edge binary (Linux, then Windows, then macOS)
  3. Playwright's own bundled Chromium    (executable_path=None)
"""
from pathlib import Path
import os

CANDIDATES = [
    # Linux — the original G3 authoring environment.
    "/usr/bin/chromium",
    "/usr/bin/chromium-browser",
    "/usr/bin/google-chrome",
    # Windows.
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    # macOS.
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
]


def chromium_executable():
    """Return a Chromium-family executable path, or None to use Playwright's bundle."""
    override = os.environ.get("IELTS_CHROMIUM")
    if override:
        if not Path(override).exists():
            raise SystemExit(f"IELTS_CHROMIUM is set but does not exist: {override}")
        return override
    for c in CANDIDATES:
        if Path(c).exists():
            return c
    return None


def launch_chromium(playwright):
    """Launch headless Chromium for a validation run."""
    exe = chromium_executable()
    kwargs = {"headless": True, "args": ["--no-sandbox"]}
    if exe:
        kwargs["executable_path"] = exe
    return playwright.chromium.launch(**kwargs)


def describe():
    return chromium_executable() or "playwright-bundled chromium"
