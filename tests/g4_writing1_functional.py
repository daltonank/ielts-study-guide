#!/usr/bin/env python3
"""G4 Writing Task 1 functional validation.

Drives the real learner flow in a browser: navigation, scoring of all three
interaction types, mastery transitions against DECISIONS.md D-015, timing
evidence, autosave, error-log and review-queue integration, and state survival
across a reload. Mirrors tests/g3_reading_functional.py.
"""
from pathlib import Path
import json
import sys
from playwright.sync_api import sync_playwright
sys.path.insert(0, str(Path(__file__).resolve().parent))
from browser_env import launch_chromium, describe

ROOT = Path(__file__).resolve().parents[1] / 'web'
STORE = "ieltsC1UAEN.state.v1"
ASSETS = {n: (ROOT / n).read_text(encoding='utf-8')
          for n in ['styles.css', 'vocabulary.js', 'data.js', 'reading_data.js', 'writing1_data.js', 'app.js']}
INDEX = (ROOT / 'index.html').read_text(encoding='utf-8')


def build_html(seed=None):
    """Inline the app. `seed` pre-populates localStorage, which is how the
    reload test proves state genuinely round-trips through serialised JSON."""
    store = "{}" if seed is None else "{%s:%s}" % (json.dumps(STORE), json.dumps(seed))
    shim = ("<script>window.__ls=" + store + ";Object.defineProperty(window,'localStorage',{value:{"
            "getItem:k=>Object.prototype.hasOwnProperty.call(window.__ls,k)?window.__ls[k]:null,"
            "setItem:(k,v)=>{window.__ls[k]=String(v)},removeItem:k=>{delete window.__ls[k]},"
            "clear:()=>{Object.keys(window.__ls).forEach(k=>delete window.__ls[k])}}});</script>")
    out = INDEX.replace('<head>', '<head>' + shim)
    for name, content in ASSETS.items():
        if name == 'styles.css':
            out = out.replace('<link rel="stylesheet" href="styles.css">', f'<style>{content}</style>')
        else:
            out = out.replace(f'<script src="{name}"></script>', f'<script>{content}</script>')
    return out


html = build_html()

fails = []


def check(cond, msg):
    if not cond:
        fails.append(msg)


def st(page):
    return page.evaluate(f'()=>JSON.parse(localStorage.getItem("{STORE}"))')


def open_family(page, fam):
    page.click('#menuBtn')
    page.click('#secondaryNav button[data-route="task1"]')
    page.wait_for_timeout(60)
    page.click(f'[data-w1-family="{fam}"]')
    page.wait_for_timeout(60)


def answer_exercise(page, ex_id, correct=True):
    """Open one exercise and answer it, reading the key from the in-page data."""
    if page.locator(f'[data-w1-exercise="{ex_id}"]').count() == 0:
        fam_of = page.evaluate('(id)=>WRITING1_DATA.exercises.find(e=>e.id===id).questionFamily', ex_id)
        page.click(f'[data-w1-back-family="{fam_of}"]')
        page.wait_for_timeout(60)
    page.click(f'[data-w1-exercise="{ex_id}"]')
    page.wait_for_timeout(60)
    ex = page.evaluate('(id)=>WRITING1_DATA.exercises.find(e=>e.id===id)', ex_id)
    if ex['type'] == 'select':
        opts = ex['options']
        target = ex['correctAnswer'] if correct else next(o for o in opts if o != ex['correctAnswer'])
        page.locator(f'input[name="w1opt-{ex_id}"]').nth(opts.index(target)).check()
    elif ex['type'] == 'cloze':
        page.fill(f'[data-w1-answer="{ex_id}"]', ex['correctAnswer'] if correct else 'zzz')
    else:
        order = ex['correctAnswer']
        cur = page.evaluate('(id)=>{const s=JSON.parse(localStorage.getItem("%s"));'
                            'const ex=WRITING1_DATA.exercises.find(e=>e.id===id);'
                            'const a=s.writing1.answers[id];'
                            'return (Array.isArray(a)&&a.length===ex.items.length)?a:ex.items.map(i=>i.id)}' % STORE, ex_id)
        if correct:
            # Selection-sort the list using only the visible Up controls.
            for target_i, want in enumerate(order):
                cur = page.evaluate('(id)=>JSON.parse(localStorage.getItem("%s")).writing1.answers[id]' % STORE, ex_id) or cur
                have = cur.index(want)
                while have > target_i:
                    page.click(f'[data-w1-up="{ex_id}:{have}"]')
                    page.wait_for_timeout(25)
                    have -= 1
                cur = page.evaluate('(id)=>JSON.parse(localStorage.getItem("%s")).writing1.answers[id]' % STORE, ex_id)
        elif cur == order:
            page.click(f'[data-w1-up="{ex_id}:1"]')
            page.wait_for_timeout(25)
    page.click(f'[data-w1-submit="{ex_id}"]')
    page.wait_for_timeout(80)


with sync_playwright() as p:
    browser = launch_chromium(p)
    page = browser.new_page(viewport={'width': 390, 'height': 900})
    page.set_content(html, wait_until='load')
    page.wait_for_timeout(120)

    # --- navigation -----------------------------------------------------
    page.click('#menuBtn')
    page.click('#secondaryNav button[data-route="task1"]')
    page.wait_for_timeout(80)
    check(page.locator('.family-card').count() == 7, 'Writing Task 1 does not expose seven family cards')
    body = page.text_content('body')
    check('70' in body and '21' in body, 'G4 inventory counts not rendered')
    check(page.locator('.mobile-nav button').count() == 5, 'Primary navigation is no longer five items')

    fam = 'line_graph'
    exs = page.evaluate('(f)=>WRITING1_DATA.exercises.filter(e=>e.questionFamily===f)', fam)
    mod_id = page.evaluate('(f)=>WRITING1_DATA.modules.find(m=>m.subskill===f).id', fam)
    guided = [e['id'] for e in exs if e['mode'] == 'guided']
    independent = [e['id'] for e in exs if e['mode'] == 'independent']
    timed = [e['id'] for e in exs if e['mode'] == 'timed']
    mastery = [e['id'] for e in exs if e['mode'] == 'mastery']

    # --- opening content must not grant mastery -------------------------
    open_family(page, fam)
    check(st(page)['mastery'].get(mod_id, 0) == 0, 'Opening the family page advanced mastery')
    page.click(f'[data-w1-foundation="{mod_id}"]')
    page.wait_for_timeout(60)
    check(st(page)['mastery'].get(mod_id, 0) == 1, 'Mark-introduced did not set L1')

    # --- visual rendering ------------------------------------------------
    page.click(f'[data-w1-exercise="{guided[0]}"]')
    page.wait_for_timeout(80)
    check(page.locator('.w1-visual svg').count() >= 1, 'No SVG visual rendered for the line-graph family')
    check(page.locator('.w1-alt').count() == 1, 'No text-equivalent disclosure on the visual')
    alt_len = page.evaluate('()=>document.querySelector(".w1-alt p").textContent.length')
    check(alt_len > 80, 'Text equivalent is too short to substitute for the visual')
    page.click(f'[data-w1-back-family="{fam}"]')
    page.wait_for_timeout(50)

    # --- guided set correct -> L2 ---------------------------------------
    for eid in guided:
        answer_exercise(page, eid, correct=True)
        page.click(f'[data-w1-back-family="{fam}"]')
        page.wait_for_timeout(40)
    s = st(page)
    check(s['mastery'].get(mod_id, 0) >= 2, f'Guided set did not advance to L2 (got {s["mastery"].get(mod_id)})')
    check(len([r for r in s['writing1']['results'] if r['mode'] == 'guided']) == len(guided),
          'Not every guided exercise recorded a result')
    check(all(r['correct'] for r in s['writing1']['results'] if r['mode'] == 'guided'),
          'A guided exercise answered from its own key was marked wrong')

    # --- independent set correct -> L3 ----------------------------------
    for eid in independent:
        answer_exercise(page, eid, correct=True)
        page.click(f'[data-w1-back-family="{fam}"]')
        page.wait_for_timeout(40)
    s = st(page)
    check(s['mastery'].get(mod_id, 0) >= 3, f'Independent set did not advance to L3 (got {s["mastery"].get(mod_id)})')

    # --- timed exercises record timing evidence -------------------------
    for eid in timed:
        page.click(f'[data-w1-exercise="{eid}"]')
        page.wait_for_timeout(50)
        check(page.locator('#w1ExTimer').count() == 1, f'{eid}: timed exercise has no timer')
        page.click(f'[data-w1-ex-timer="{eid}"]')
        page.wait_for_timeout(40)
        ex = page.evaluate('(id)=>WRITING1_DATA.exercises.find(e=>e.id===id)', eid)
        if ex['type'] == 'select':
            page.locator(f'input[name="w1opt-{eid}"]').nth(ex['options'].index(ex['correctAnswer'])).check()
        else:
            page.fill(f'[data-w1-answer="{eid}"]', ex['correctAnswer'])
        page.click(f'[data-w1-submit="{eid}"]')
        page.wait_for_timeout(70)
        page.click(f'[data-w1-back-family="{fam}"]')
        page.wait_for_timeout(40)
    s = st(page)
    timed_results = [r for r in s['writing1']['results'] if r['mode'] == 'timed']
    check(len(timed_results) == len(timed), 'Timed exercises did not all record results')
    check(all(r['timed'] and r['elapsedSeconds'] is not None for r in timed_results),
          'Timed exercises did not record elapsed time')
    check(all(r['withinLimit'] for r in timed_results), 'Timed exercises were not recorded as within limit')
    # L4 must still be withheld: it also requires a completed timed full response.
    check(s['mastery'].get(mod_id, 0) == 3,
          f'L4 granted without a timed full response (got {s["mastery"].get(mod_id)})')

    # --- mastery-mode ordering exercise ---------------------------------
    answer_exercise(page, mastery[0], correct=True)
    s = st(page)
    mres = [r for r in s['writing1']['results'] if r['mode'] == 'mastery']
    check(mres and mres[-1]['correct'], 'Paragraph-ordering exercise did not score correctly when ordered correctly')
    page.click(f'[data-w1-back-family="{fam}"]')
    page.wait_for_timeout(40)

    # --- full prompt: plan, timed draft, checklist, submit --------------
    prompts = page.evaluate('(f)=>WRITING1_DATA.prompts.filter(p=>p.questionFamily===f)', fam)
    pid = prompts[0]['id']
    page.click(f'[data-w1-prompt="{pid}"]')
    page.wait_for_timeout(80)
    check(page.locator('.w1-stepper .w1-step').count() == 3, 'Plan/draft/review stepper missing')
    page.fill(f'[data-w1-plan="{pid}"]', '2005-2025, past simple. Oslo+Bergen together, Tromso separate.')
    page.wait_for_timeout(60)
    check(st(page)['writing1']['drafts'][pid]['plan'].startswith('2005'), 'Plan did not autosave')
    page.click(f'[data-w1-start-timer="{pid}"]')
    page.wait_for_timeout(40)
    check(st(page)['writing1']['timer']['promptId'] == pid, 'Timed draft did not start')
    minimum = prompts[0]['wordMinimum']
    check(minimum == 150, f'Prompt does not carry the 150-word Task 1 minimum (got {minimum})')

    def words(n):
        """A response of exactly n words."""
        return ' '.join(['recycling'] * n)

    # --- an underlength response must not buy a performance level -------
    for length, label in ((20, 'twenty-word'), (minimum - 1, f'{minimum - 1}-word')):
        if page.locator(f'[data-w1-start-timer="{pid}"]').count():
            page.click(f'[data-w1-start-timer="{pid}"]')
            page.wait_for_timeout(40)
        page.fill(f'[data-w1-draft="{pid}"]', words(length))
        page.wait_for_timeout(80)
        for c in prompts[0]['checklist']:
            page.check(f'[data-w1-check="{pid}:{c["id"]}"]')
            page.wait_for_timeout(10)
        page.click(f'[data-w1-submit-prompt="{pid}"]')
        page.wait_for_timeout(120)
        s = st(page)
        subs = s['writing1']['submissions']
        check(subs and subs[-1]['words'] == length,
              f'{label} response was not recorded with its real length')
        check(subs and subs[-1]['meetsLength'] is False,
              f'{label} response was recorded as meeting the length minimum')
        check(s['mastery'].get(mod_id, 0) == 3,
              f'{label} response advanced mastery to L{s["mastery"].get(mod_id)} — '
              f'a response under {minimum} words must not reach L4')
        check(any(e.get('questionId') == pid and 'word' in str(e.get('learnerAnswer', ''))
                  for e in s['errors']),
              f'{label} response did not log an underlength error')

    # --- a genuine full-length response does ----------------------------
    if page.locator(f'[data-w1-start-timer="{pid}"]').count():
        page.click(f'[data-w1-start-timer="{pid}"]')
        page.wait_for_timeout(40)
    check(st(page)['writing1']['timer']['promptId'] == pid, 'Timed draft did not restart')
    essay = ' '.join(['The line graph compares recycling rates in three cities between 2005 and 2025.'] * 20)
    page.fill(f'[data-w1-draft="{pid}"]', essay)
    page.wait_for_timeout(80)
    saved = st(page)['writing1']['drafts'][pid]['text']
    check(len(saved) > 100, 'Draft did not autosave')
    check(page.text_content('#w1Words').strip().isdigit(), 'Word count not rendered')
    check(int(page.text_content('#w1Words').strip()) >= minimum,
          'The full-length probe is itself under the minimum')
    for c in prompts[0]['checklist']:
        if not page.is_checked(f'[data-w1-check="{pid}:{c["id"]}"]'):
            page.check(f'[data-w1-check="{pid}:{c["id"]}"]')
            page.wait_for_timeout(10)
    page.click(f'[data-w1-submit-prompt="{pid}"]')
    page.wait_for_timeout(120)
    s = st(page)
    subs = s['writing1']['submissions']
    check(len(subs) == 3, f'Expected three submissions, found {len(subs)}')
    check(subs[-1]['meetsLength'] is True, 'Full-length response not recorded as meeting the minimum')
    check(subs[-1]['withinLimit'], 'Submission inside the limit was not recorded as within limit')
    check(subs[-1]['checklistDone'] == subs[-1]['checklistTotal'], 'Checklist ticks not recorded')
    check(subs[-1]['words'] >= 150, 'Word count not recorded on submission')
    check(any(r.get('promptId') == pid for r in s['savedResponses']), 'Response text not persisted')
    check(s['mastery'].get(mod_id, 0) >= 4,
          f'Timed exercises plus a completed timed response did not reach L4 (got {s["mastery"].get(mod_id)})')

    # --- wrong answers must feed the error log and review queue ---------
    before_err = len(s['errors'])
    answer_exercise(page, guided[1], correct=False)
    s = st(page)
    w1_errors = [e for e in s['errors'] if e.get('skill') == 'Writing Task 1']
    check(len(s['errors']) > before_err, 'A wrong answer did not create an error record')
    check(w1_errors, 'Wrong Writing Task 1 answer did not enter the error log')
    e0 = w1_errors[0]
    for field in ('category', 'explanation', 'correction', 'reviewDate', 'questionId', 'learnerAnswer', 'correctAnswer'):
        check(str(e0.get(field, '')).strip() != '', f'Error record missing {field}')
    check(any(r.get('type') == 'Writing Task 1' for r in s['reviews']),
          'Wrong Writing Task 1 answer did not create a review item')
    check(page.locator('.answer-feedback').count() >= 1, 'No feedback shown after a wrong answer')
    fb = page.text_content('.answer-feedback')
    check('Why your choice fails' in fb, 'Wrong-option reasoning not shown to the learner')

    # --- honest scoring --------------------------------------------------
    page.click(f'[data-w1-back-family="{fam}"]')
    page.click(f'[data-w1-prompt="{pid}"]')
    page.wait_for_timeout(80)
    txt = page.text_content('body')
    check('not an official' in txt.lower(), 'Scoring disclaimer not visible on the prompt page')

    # --- language mode must not lose work --------------------------------
    before = len(st(page)['writing1']['results'])
    page.select_option('#languageMode', 'uahelp')
    page.wait_for_timeout(80)
    s = st(page)
    check(len(s['writing1']['results']) == before, 'Language switch lost Writing Task 1 results')
    check(page.locator('.ua-note').count() > 0, 'UA Help produced no Ukrainian support in Writing Task 1')

    # --- state must survive a reload -------------------------------------
    # A fresh page, seeded only with the serialised store, so this exercises
    # loadState() rehydrating everything rather than in-memory carry-over.
    saved = page.evaluate(f'()=>localStorage.getItem("{STORE}")')
    page.set_content(build_html(saved), wait_until='load')
    page.wait_for_timeout(180)
    s = st(page)
    check(len(s['writing1']['results']) == before, 'Results did not survive reload')
    check(len(s['writing1']['submissions']) == 3, 'Submissions did not survive reload')
    check(s['writing1']['drafts'][pid]['text'].startswith('The line graph'), 'Draft did not survive reload')
    check(s['mastery'].get(mod_id, 0) >= 4, 'Mastery did not survive reload')

    # --- no horizontal overflow in the new surfaces ----------------------
    page.click('#menuBtn')
    page.click('#secondaryNav button[data-route="task1"]')
    page.wait_for_timeout(80)
    dims = page.evaluate('()=>({sw:document.documentElement.scrollWidth,cw:document.documentElement.clientWidth})')
    check(dims['sw'] <= dims['cw'] + 1, f'Writing Task 1 mobile horizontal overflow {dims}')

    browser.close()

if fails:
    print('G4 WRITING TASK 1 FUNCTIONAL FAIL')
    print('\n'.join(fails))
    sys.exit(1)
print('G4 WRITING TASK 1 FUNCTIONAL PASS')
