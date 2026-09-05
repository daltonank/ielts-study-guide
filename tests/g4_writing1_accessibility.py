#!/usr/bin/env python3
"""G4 Writing Task 1 accessibility validation.

UX_DESIGN_SPEC.md section 17 requires semantic structure, labelled controls,
visible focus, status feedback that is not colour-only, reduced-motion support
and, specifically for this gate, an accessible text equivalent for every
meaningful visual (section 18). This exercises the new G4 surfaces only; the
G0-G3 checks stay in tests/accessibility_static.py and
tests/g3_reading_accessibility.py.
"""
from pathlib import Path
import sys
from playwright.sync_api import sync_playwright
sys.path.insert(0, str(Path(__file__).resolve().parent))
from browser_env import launch_chromium, describe

ROOT = Path(__file__).resolve().parents[1] / 'web'
SHIM = ("<script>const __ls={};Object.defineProperty(window,'localStorage',{value:{"
        "getItem:k=>Object.prototype.hasOwnProperty.call(__ls,k)?__ls[k]:null,"
        "setItem:(k,v)=>{__ls[k]=String(v)},removeItem:k=>{delete __ls[k]},"
        "clear:()=>{Object.keys(__ls).forEach(k=>delete __ls[k])}}});</script>")
html = (ROOT / 'index.html').read_text(encoding='utf-8').replace('<head>', '<head>' + SHIM)
for name in ['styles.css', 'vocabulary.js', 'data.js', 'reading_data.js', 'writing1_data.js', 'app.js']:
    content = (ROOT / name).read_text(encoding='utf-8')
    if name == 'styles.css':
        html = html.replace('<link rel="stylesheet" href="styles.css">', f'<style>{content}</style>')
    else:
        html = html.replace(f'<script src="{name}"></script>', f'<script>{content}</script>')

FAMILIES = ['line_graph', 'bar_chart', 'pie_chart', 'table', 'process_diagram', 'map_plan', 'mixed_visual']
fails = []


def check(cond, msg):
    if not cond:
        fails.append(msg)


with sync_playwright() as p:
    browser = launch_chromium(p)
    page = browser.new_page(viewport={'width': 390, 'height': 900})
    page.set_content(html, wait_until='load')
    page.wait_for_timeout(120)
    page.click('#menuBtn')
    page.click('#secondaryNav button[data-route="task1"]')
    page.wait_for_timeout(90)

    # Primary navigation must not have grown for this gate.
    check(page.locator('.mobile-nav button').count() == 5, 'Primary navigation is no longer five controls')

    # --- every visual carries an accessible equivalent -------------------
    for fam in FAMILIES:
        page.click(f'[data-w1-family="{fam}"]')
        page.wait_for_timeout(60)
        first = page.evaluate('(f)=>WRITING1_DATA.exercises.find(e=>e.questionFamily===f).id', fam)
        page.click(f'[data-w1-exercise="{first}"]')
        page.wait_for_timeout(80)

        check(page.locator('section.w1-visual').count() == 1, f'{fam}: visual is not a labelled section')
        check(page.locator('section.w1-visual[aria-label]').count() == 1, f'{fam}: visual section has no aria-label')
        alt = page.locator('.w1-alt p')
        check(alt.count() == 1, f'{fam}: no text equivalent for the visual')
        check(len((alt.text_content() or '').strip()) > 80, f'{fam}: text equivalent too short to replace the visual')
        summary = page.locator('.w1-alt summary')
        check(summary.count() == 1 and 'words' in (summary.text_content() or ''),
              f'{fam}: text equivalent is not discoverable')

        # Any SVG conveying meaning must have an image role and a name.
        unnamed = page.evaluate('''()=>{const bad=[];
          document.querySelectorAll('.w1-visual svg').forEach(s=>{
            if(s.getAttribute('role')!=='img'||!(s.getAttribute('aria-label')||'').trim()) bad.push(s.outerHTML.slice(0,60));});
          return bad}''')
        check(not unnamed, f'{fam}: SVG without role="img" and an accessible name {unnamed}')

        # Decorative marks inside must not be announced separately.
        check(page.evaluate('()=>[...document.querySelectorAll(".w1-visual svg *")].every(n=>!n.hasAttribute("alt"))'),
              f'{fam}: unexpected alt attributes inside SVG')

        # Data is never colour-only: every chart also ships a table or a labelled list.
        kind = page.evaluate('(f)=>WRITING1_DATA.visuals.find(v=>v.family===f).kind', fam)
        if kind in ('line', 'bar', 'pie', 'mixed'):
            check(page.locator('.w1-visual table').count() >= 1,
                  f'{fam}: chart has no data table, so identity would rest on colour alone')
        if kind == 'map':
            check(page.locator('.w1-feature .badge').count() >= 1,
                  f'{fam}: map statuses are not text-labelled')

        # --- answer controls -------------------------------------------
        ex_type = page.evaluate('(id)=>WRITING1_DATA.exercises.find(e=>e.id===id).type', first)
        if ex_type == 'select':
            check(page.locator('fieldset.w1-options').count() == 1, f'{fam}: options not grouped in a fieldset')
            check(page.locator('fieldset.w1-options legend').count() == 1, f'{fam}: option group has no legend')
        unlabelled = page.evaluate('''()=>{const bad=[];
          document.querySelectorAll('#w1Form input, #w1Form textarea').forEach(el=>{
            const named=el.closest('label')||el.getAttribute('aria-label')||
              (el.id&&document.querySelector(`label[for="${el.id}"]`));
            if(!named) bad.push(el.outerHTML.slice(0,60));});
          return bad}''')
        check(not unlabelled, f'{fam}: unlabelled answer control {unlabelled}')

        page.click(f'[data-w1-back-family="{fam}"]')
        page.wait_for_timeout(40)
        page.click('[data-w1-home]')
        page.wait_for_timeout(40)

    # --- feedback must not be colour-only --------------------------------
    page.click('[data-w1-family="line_graph"]')
    page.wait_for_timeout(60)
    eid = page.evaluate('()=>WRITING1_DATA.exercises.find(e=>e.questionFamily==="line_graph").id')
    page.click(f'[data-w1-exercise="{eid}"]')
    page.wait_for_timeout(70)
    ex = page.evaluate('(id)=>WRITING1_DATA.exercises.find(e=>e.id===id)', eid)
    wrong = next(o for o in ex['options'] if o != ex['correctAnswer'])
    page.locator(f'input[name="w1opt-{eid}"]').nth(ex['options'].index(wrong)).check()
    page.click(f'[data-w1-submit="{eid}"]')
    page.wait_for_timeout(90)
    fb = page.text_content('.answer-feedback') or ''
    check('Review' in fb or 'Correct' in fb, 'Feedback state is not conveyed in text')
    check('Error category' in fb, 'Error classification not exposed to the learner')
    check(page.locator('.answer-feedback .badge').count() >= 1, 'Feedback has no text badge, so it reads as colour-only')

    # --- keyboard operability --------------------------------------------
    page.focus(f'input[name="w1opt-{eid}"]')
    page.keyboard.press('ArrowDown')
    page.wait_for_timeout(60)
    moved = page.evaluate(f'()=>document.querySelector(\'input[name="w1opt-{eid}"]:checked\')?.value')
    check(moved is not None, 'Radio group is not keyboard operable')
    focused = page.evaluate('()=>document.activeElement.tagName')
    check(focused == 'INPUT', f'Focus left the answer control on keyboard use ({focused})')

    # --- the writing flow --------------------------------------------------
    page.click('[data-w1-back-family="line_graph"]')
    page.wait_for_timeout(50)
    pid = page.evaluate('()=>WRITING1_DATA.prompts.find(p=>p.questionFamily==="line_graph").id')
    page.click(f'[data-w1-prompt="{pid}"]')
    page.wait_for_timeout(90)
    unlabelled = page.evaluate('''()=>{const bad=[];
      document.querySelectorAll('textarea, input[type=checkbox]').forEach(el=>{
        const named=el.closest('label')||el.getAttribute('aria-label')||
          (el.id&&document.querySelector(`label[for="${el.id}"]`));
        if(!named) bad.push(el.outerHTML.slice(0,60));});
      return bad}''')
    check(not unlabelled, f'Writing flow has an unlabelled control {unlabelled}')
    check(page.locator('.progress[aria-label]').count() >= 1, 'Time-used progress bar has no accessible name')
    check(page.locator('[role="status"]').count() >= 1, 'No live status region on the page')
    check('not an official' in (page.text_content('body') or '').lower(),
          'Scoring disclaimer not exposed in the writing flow')
    details_open = page.evaluate('()=>[...document.querySelectorAll("details")].every(d=>d.querySelector("summary"))')
    check(details_open, 'A disclosure has no summary, so it cannot be reached by keyboard')

    # --- global rules still in force ---------------------------------------
    css = (ROOT / 'styles.css').read_text(encoding='utf-8')
    check(':focus-visible' in css, 'visible focus rule missing')
    check('@media(prefers-reduced-motion:reduce)' in css, 'reduced-motion support missing')
    page.select_option('#languageMode', 'uahelp')
    page.wait_for_timeout(60)
    check(page.locator('.ua-note').count() >= 1, 'UA Help exposes no Ukrainian support in Writing Task 1')
    check(page.evaluate('()=>document.documentElement.lang') == 'uk', 'Document language not switched for UA Help')

    browser.close()

if fails:
    print('G4 WRITING TASK 1 A11Y FAIL')
    print('\n'.join(fails))
    sys.exit(1)
print('G4 WRITING TASK 1 A11Y PASS')
