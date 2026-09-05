#!/usr/bin/env python3
from pathlib import Path
import sys
from playwright.sync_api import sync_playwright
sys.path.insert(0, str(Path(__file__).resolve().parent))
from browser_env import launch_chromium, describe
ROOT=Path(__file__).resolve().parents[1]/'web'
html=(ROOT/'index.html').read_text(encoding='utf-8')
shim="<script>const __ls={};Object.defineProperty(window,'localStorage',{value:{getItem:k=>Object.prototype.hasOwnProperty.call(__ls,k)?__ls[k]:null,setItem:(k,v)=>{__ls[k]=String(v)},removeItem:k=>{delete __ls[k]},clear:()=>{Object.keys(__ls).forEach(k=>delete __ls[k])}}});</script>"
html=html.replace('<head>','<head>'+shim)
for name,tag in [('styles.css','style'),('vocabulary.js','script'),('data.js','script'),('reading_data.js','script'),('writing1_data.js','script'),('app.js','script')]:
    content=(ROOT/name).read_text(encoding='utf-8')
    if name=='styles.css': html=html.replace('<link rel="stylesheet" href="styles.css">',f'<style>{content}</style>')
    else: html=html.replace(f'<script src="{name}"></script>',f'<script>{content}</script>')
fails=[]
def check(cond,msg):
    if not cond:fails.append(msg)
with sync_playwright() as p:
    browser=launch_chromium(p)
    page=browser.new_page(viewport={'width':390,'height':900})
    page.set_content(html,wait_until='load');page.wait_for_timeout(100)
    # Navigate to Reading through drawer.
    page.click('#menuBtn');page.click('#secondaryNav button[data-route="reading"]');page.wait_for_timeout(50)
    check(page.locator('.reading-family-card').count()==15,'Reading family cards != 15')
    check('224' in page.text_content('body'),'Reading inventory count not visible')
    # Guided multiple choice, answer all correctly from in-page dataset.
    page.click('[data-reading-family="multiple_choice"]');page.click('[data-reading-passage$="P01"]');page.wait_for_timeout(40)
    answers=page.evaluate('''()=>{const p=READING_DATA.passages.find(x=>x.id===JSON.parse(localStorage.getItem("ieltsC1UAEN.state.v1")).reading.activePassageId);return p.questions.map(q=>[q.id,q.correctAnswer])}''')
    for qid,ans in answers: page.select_option(f'[data-reading-q="{qid}"]',label=ans)
    page.click('[data-reading-submit]');page.wait_for_timeout(80)
    check('4/4' in page.text_content('body'),'Guided correct set did not score 4/4')
    st=page.evaluate('()=>JSON.parse(localStorage.getItem("ieltsC1UAEN.state.v1"))')
    check(st['mastery'].get('READ-MULTIPLE-CHOICE',0)>=2,'Guided result did not advance to L2')
    # Independent set -> L3.
    page.click('[data-reading-back]');page.click('[data-reading-passage$="P02"]');page.wait_for_timeout(20)
    answers=page.evaluate('''()=>{const s=JSON.parse(localStorage.getItem("ieltsC1UAEN.state.v1"));const p=READING_DATA.passages.find(x=>x.id===s.reading.activePassageId);return p.questions.map(q=>[q.id,q.correctAnswer])}''')
    for qid,ans in answers: page.select_option(f'[data-reading-q="{qid}"]',label=ans)
    page.click('[data-reading-submit]');page.wait_for_timeout(60)
    st=page.evaluate('()=>JSON.parse(localStorage.getItem("ieltsC1UAEN.state.v1"))')
    check(st['mastery'].get('READ-MULTIPLE-CHOICE',0)>=3,'Independent result did not advance to L3')
    # Timed + mastery correct -> L4.
    for suffix in ['P03','P04']:
        page.click('[data-reading-back]');page.click(f'[data-reading-passage$="{suffix}"]');page.click('[data-reading-start-timer]');page.wait_for_timeout(10)
        answers=page.evaluate('''()=>{const s=JSON.parse(localStorage.getItem("ieltsC1UAEN.state.v1"));const p=READING_DATA.passages.find(x=>x.id===s.reading.activePassageId);return p.questions.map(q=>[q.id,q.correctAnswer])}''')
        for qid,ans in answers: page.select_option(f'[data-reading-q="{qid}"]',label=ans)
        page.click('[data-reading-submit]');page.wait_for_timeout(50)
    st=page.evaluate('()=>JSON.parse(localStorage.getItem("ieltsC1UAEN.state.v1"))')
    check(st['mastery'].get('READ-MULTIPLE-CHOICE',0)>=4,'Timed progression did not advance to L4')
    check(any(r.get('timed') for r in st['reading']['results']),'Timed reading result not recorded')
    # Wrong TFNG set should log errors/reviews.
    page.click('[data-reading-back]');page.click('[data-reading-home]');page.click('[data-reading-family="tfng"]');page.click('[data-reading-passage$="P01"]')
    for el in page.locator('[data-reading-q]').all(): el.select_option(label='False')
    page.click('[data-reading-submit]');page.wait_for_timeout(60)
    st=page.evaluate('()=>JSON.parse(localStorage.getItem("ieltsC1UAEN.state.v1"))')
    check(len([e for e in st['errors'] if e.get('skill')=='Reading'])>=1,'Wrong Reading answers did not enter error log')
    check(len([r for r in st['reviews'] if r.get('type')=='Reading'])>=1,'Wrong Reading answers did not create review items')
    # Reload state using same page content reload simulation via rerender: switch language and ensure state remains.
    before=len(st['reading']['results']);page.select_option('#languageMode','uahelp');page.wait_for_timeout(40)
    st2=page.evaluate('()=>JSON.parse(localStorage.getItem("ieltsC1UAEN.state.v1"))')
    check(len(st2['reading']['results'])==before,'Language switch lost reading results')
    check(page.locator('.ua-note').count()>0,'UA Help missing in reading workflow')
    # No horizontal overflow on reading passage at mobile.
    dims=page.evaluate('()=>({sw:document.documentElement.scrollWidth,cw:document.documentElement.clientWidth})')
    check(dims['sw']<=dims['cw']+1,f'Reading mobile horizontal overflow {dims}')
    browser.close()
if fails:
    print('G3 READING FUNCTIONAL FAIL')
    print('\n'.join(fails));sys.exit(1)
print('G3 READING FUNCTIONAL PASS')
