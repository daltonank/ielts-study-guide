#!/usr/bin/env python3
"""G4 persistence, backup and keyboard-only validation — served over real HTTP.

The other browser suites inline the app with set_content, which cannot test a
genuine page reload because the localStorage shim dies with the JS context.
This one serves web/ over a local HTTP server, so localStorage is the browser's
own, page.reload() is a real reload, and the export/import round-trip goes
through the real download and file-input paths.

Covers: real reload persistence, export/import round-trip preservation of G4
state, malformed-import rejection, backup snapshot retention, error log and
review queue restoration, mastery restoration, autosaved drafts and timers,
search behaviour, the 1,784-word vocabulary bank, and keyboard-only operation.
"""
from pathlib import Path
import http.server
import json
import socket
import socketserver
import sys
import tempfile
import threading

from playwright.sync_api import sync_playwright
sys.path.insert(0, str(Path(__file__).resolve().parent))
from browser_env import launch_chromium, describe

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "web"
STORE = "ieltsC1UAEN.state.v1"
fails = []


def check(cond, msg):
    if not cond:
        fails.append(msg)


def free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=str(WEB), **kw)

    def log_message(self, *a):
        pass


PORT = free_port()
httpd = socketserver.TCPServer(("127.0.0.1", PORT), Handler)
threading.Thread(target=httpd.serve_forever, daemon=True).start()
BASE = f"http://127.0.0.1:{PORT}/index.html"


def st(page):
    return page.evaluate(f'()=>JSON.parse(localStorage.getItem("{STORE}") || "null")')


def tab_to(page, selector, limit=120):
    """Reach an element using Tab only. Returns True if focus landed on it."""
    for _ in range(limit):
        if page.evaluate("(sel)=>document.activeElement===document.querySelector(sel)", selector):
            return True
        page.keyboard.press("Tab")
    return page.evaluate("(sel)=>document.activeElement===document.querySelector(sel)", selector)


try:
    with sync_playwright() as p:
        browser = launch_chromium(p)
        ctx = browser.new_context(viewport={"width": 420, "height": 900}, accept_downloads=True)
        page = ctx.new_page()
        page.goto(BASE, wait_until="load")
        page.wait_for_timeout(300)

        # ---------- the platform still loads ---------------------------------
        check(page.locator(".mobile-nav button").count() == 5, "primary navigation is not five controls")
        vocab = page.evaluate("()=>window.VOCABULARY.length")
        check(vocab == 1784, f"vocabulary bank is {vocab}, not 1784")
        check(page.evaluate("()=>!!window.WRITING1_DATA"), "Writing Task 1 data did not load over HTTP")
        check(page.evaluate("()=>!!window.READING_DATA"), "Reading data did not load over HTTP")

        # ---------- do real G4 work ------------------------------------------
        page.click("#menuBtn")
        page.click('#secondaryNav button[data-route="task1"]')
        page.wait_for_timeout(150)
        fam = "line_graph"
        page.click(f'[data-w1-family="{fam}"]')
        page.wait_for_timeout(120)
        mod_id = page.evaluate('(f)=>WRITING1_DATA.modules.find(m=>m.subskill===f).id', fam)
        page.click(f'[data-w1-foundation="{mod_id}"]')
        page.wait_for_timeout(80)

        exs = page.evaluate('(f)=>WRITING1_DATA.exercises.filter(e=>e.questionFamily===f)', fam)
        guided = [e for e in exs if e["mode"] == "guided"]

        # one correct, one deliberately wrong so an error and a review exist
        for e, correct in ((guided[0], True), (guided[1], False)):
            page.click(f'[data-w1-exercise="{e["id"]}"]')
            page.wait_for_timeout(100)
            opts = e["options"]
            target = e["correctAnswer"] if correct else next(o for o in opts if o != e["correctAnswer"])
            page.locator(f'input[name="w1opt-{e["id"]}"]').nth(opts.index(target)).check()
            page.click(f'[data-w1-submit="{e["id"]}"]')
            page.wait_for_timeout(120)
            page.click(f'[data-w1-back-family="{fam}"]')
            page.wait_for_timeout(60)

        pid = page.evaluate('(f)=>WRITING1_DATA.prompts.find(p=>p.questionFamily===f).id', fam)
        page.click(f'[data-w1-prompt="{pid}"]')
        page.wait_for_timeout(120)
        page.fill(f'[data-w1-plan="{pid}"]', "2005-2025, past simple. Oslo+Bergen, Tromso apart.")
        page.click(f'[data-w1-start-timer="{pid}"]')
        page.wait_for_timeout(60)
        page.fill(f'[data-w1-draft="{pid}"]', "The line graph compares recycling rates. " * 12)
        page.wait_for_timeout(150)

        before = st(page)
        check(before is not None, "nothing was written to localStorage")
        check(before["mastery"].get(mod_id, 0) >= 1, "mastery not recorded before reload")
        check(len(before["writing1"]["results"]) == 2, "exercise results not recorded")
        check(len([e for e in before["errors"] if e.get("skill") == "Writing Task 1"]) >= 1,
              "Writing Task 1 error not logged")
        check(any(r.get("type") == "Writing Task 1" for r in before["reviews"]),
              "Writing Task 1 review item not created")
        check(before["writing1"]["timer"]["promptId"] == pid, "timer state not persisted")
        check(before["writing1"]["drafts"][pid]["text"].startswith("The line graph"), "draft not autosaved")

        # ---------- a genuine browser reload ---------------------------------
        page.reload(wait_until="load")
        page.wait_for_timeout(300)
        after = st(page)
        check(after is not None, "state was lost entirely on reload")
        check(len(after["writing1"]["results"]) == 2, "exercise results did not survive a real reload")
        check(after["mastery"].get(mod_id, 0) >= 1, "mastery did not survive a real reload")
        check(after["writing1"]["drafts"][pid]["text"].startswith("The line graph"),
              "autosaved draft did not survive a real reload")
        check(after["writing1"]["timer"] and after["writing1"]["timer"]["promptId"] == pid,
              "running timer did not survive a real reload")
        check(len([e for e in after["errors"] if e.get("skill") == "Writing Task 1"]) >= 1,
              "error log did not survive a real reload")
        check(any(r.get("type") == "Writing Task 1" for r in after["reviews"]),
              "review queue did not survive a real reload")

        # the app must actually re-render that state, not just hold it
        page.click("#menuBtn")
        page.click('#secondaryNav button[data-route="errors"]')
        page.wait_for_timeout(150)
        check("Writing Task 1" in (page.text_content("body") or ""),
              "Error Log does not show the restored Writing Task 1 error")
        page.click("#menuBtn")
        page.click('#secondaryNav button[data-route="review"]')
        page.wait_for_timeout(150)
        check("Writing Task 1" in (page.text_content("body") or ""),
              "Review queue does not show the restored Writing Task 1 item")

        # ---------- search still works, and reaches G4 -----------------------
        page.click("#menuBtn")
        page.click('#secondaryNav button[data-route="search"]')
        page.wait_for_timeout(120)
        page.fill("#globalSearch", "recycling")
        page.wait_for_timeout(150)
        hits = page.text_content("#globalResults") or ""
        check("Writing Task 1" in hits, "global search does not reach Writing Task 1 content")
        page.fill("#globalSearch", "articles")
        page.wait_for_timeout(150)
        check(len(page.text_content("#globalResults") or "") > 10, "global search regressed")

        # ---------- export / import round-trip -------------------------------
        page.click("#menuBtn")
        page.click('#secondaryNav button[data-route="settings"]')
        page.wait_for_timeout(120)
        with page.expect_download() as dl:
            page.click("#exportBtn")
        exported = Path(tempfile.gettempdir()) / "g4_export.json"
        dl.value.save_as(str(exported))
        payload = json.loads(exported.read_text(encoding="utf-8"))
        check(payload.get("writing1", {}).get("results") and len(payload["writing1"]["results"]) == 2,
              "export did not include Writing Task 1 results")
        check(payload["writing1"]["drafts"][pid]["text"].startswith("The line graph"),
              "export did not include the autosaved draft")
        check(payload["mastery"].get(mod_id, 0) >= 1, "export did not include mastery")
        check(any(e.get("skill") == "Writing Task 1" for e in payload["errors"]),
              "export did not include the Writing Task 1 error")

        # wipe, then import the file back and confirm G4 state is restored
        page.evaluate(f'()=>localStorage.removeItem("{STORE}")')
        page.reload(wait_until="load")
        page.wait_for_timeout(250)
        page.click("#menuBtn")
        page.click('#secondaryNav button[data-route="task1"]')
        page.wait_for_timeout(150)
        wiped = st(page)
        check(not (wiped or {}).get("writing1", {}).get("results"), "state was not actually cleared before import")

        page.click("#menuBtn")
        page.click('#secondaryNav button[data-route="settings"]')
        page.wait_for_timeout(120)
        page.set_input_files("#importFile", str(exported))
        page.wait_for_timeout(400)
        restored = st(page)
        check(len(restored["writing1"]["results"]) == 2, "import did not restore Writing Task 1 results")
        check(restored["mastery"].get(mod_id, 0) >= 1, "import did not restore mastery")
        check(restored["writing1"]["drafts"][pid]["text"].startswith("The line graph"),
              "import did not restore the autosaved draft")
        check(any(e.get("skill") == "Writing Task 1" for e in restored["errors"]),
              "import did not restore the error log")
        check(isinstance(restored.get("backups"), list) and len(restored["backups"]) >= 1,
              "import did not retain a backup snapshot of the previous state")

        # ---------- malformed import must be rejected ------------------------
        bad = Path(tempfile.gettempdir()) / "g4_bad.json"
        bad.write_text('{"nope": true}', encoding="utf-8")
        page.set_input_files("#importFile", str(bad))
        page.wait_for_timeout(400)
        still = st(page)
        check(len(still["writing1"]["results"]) == 2, "a malformed import damaged existing state")

        # ---------- keyboard-only operation ----------------------------------
        # Start from a clean store. Restored state legitimately resumes into the
        # last open prompt (the same behaviour Reading has), which would put the
        # keyboard walk inside a sub-view rather than at the family grid.
        page.evaluate(f'()=>localStorage.removeItem("{STORE}")')
        page.goto(BASE, wait_until="load")
        page.wait_for_timeout(250)
        page.evaluate("()=>document.body.focus()")
        check(tab_to(page, ".skip-link"), "the skip link is not the first tab stop")
        check(page.evaluate("()=>{const r=document.querySelector('.skip-link').getBoundingClientRect();"
                            "return r.top>=0}"),
              "the skip link does not become visible when focused")
        check(tab_to(page, "#menuBtn"), "the drawer button is not reachable by keyboard")
        page.keyboard.press("Enter")
        page.wait_for_timeout(120)
        check(page.locator("#drawer").get_attribute("hidden") is None, "Enter did not open the drawer")
        check(tab_to(page, '#secondaryNav button[data-route="task1"]'),
              "Writing Task 1 is not reachable by keyboard from the drawer")
        page.keyboard.press("Enter")
        page.wait_for_timeout(200)
        check(page.locator(".family-card").count() == 7, "keyboard navigation did not open Writing Task 1")
        check(tab_to(page, '[data-w1-family="line_graph"]'), "family card not reachable by keyboard")
        page.keyboard.press("Enter")
        page.wait_for_timeout(200)
        first_ex = page.evaluate('()=>WRITING1_DATA.exercises.find(e=>e.questionFamily==="line_graph").id')
        check(tab_to(page, f'[data-w1-exercise="{first_ex}"]'), "exercise link not reachable by keyboard")
        page.keyboard.press("Enter")
        page.wait_for_timeout(220)
        check(tab_to(page, f'input[name="w1opt-{first_ex}"]'), "answer options not reachable by keyboard")
        page.keyboard.press("Space")
        page.wait_for_timeout(80)
        picked = page.evaluate(f'()=>!!document.querySelector(\'input[name="w1opt-{first_ex}"]:checked\')')
        check(picked, "an option could not be selected with the keyboard")
        check(tab_to(page, f'[data-w1-submit="{first_ex}"]'), "the check button is not reachable by keyboard")
        page.keyboard.press("Enter")
        page.wait_for_timeout(220)
        check(page.locator(".answer-feedback").count() >= 1, "keyboard submission produced no feedback")
        ks = st(page)
        check(len(ks["writing1"]["results"]) == 1, "keyboard-only attempt was not scored")

        # ---------- no accidental deployment surface -------------------------
        reqs = page.evaluate("()=>performance.getEntriesByType('resource').map(r=>r.name)")
        external = [r for r in reqs if not r.startswith(f"http://127.0.0.1:{PORT}")]
        check(not external, f"the app requested something off the local origin: {external[:3]}")

        ctx.close()
        browser.close()
finally:
    httpd.shutdown()

if fails:
    print("G4 PERSISTENCE / BACKUP / KEYBOARD FAIL")
    print("\n".join(fails))
    sys.exit(1)
print("G4 PERSISTENCE / BACKUP / KEYBOARD PASS (served over real HTTP, genuine reload)")
