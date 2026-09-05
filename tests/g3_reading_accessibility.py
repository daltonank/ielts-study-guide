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
for name in ['styles.css','vocabulary.js','data.js','reading_data.js','writing1_data.js','app.js']:
    content=(ROOT/name).read_text(encoding='utf-8')
    if name=='styles.css': html=html.replace('<link rel="stylesheet" href="styles.css">',f'<style>{content}</style>')
    else: html=html.replace(f'<script src="{name}"></script>',f'<script>{content}</script>')
fails=[]
with sync_playwright() as p:
    browser=launch_chromium(p)
    page=browser.new_page(viewport={'width':390,'height':900})
    page.set_content(html,wait_until='load');page.click('#menuBtn');page.click('#secondaryNav button[data-route="reading"]');page.click('[data-reading-family="tfng"]');page.click('[data-reading-passage$="P01"]');page.wait_for_timeout(30)
    # Inputs are nested in labels and therefore receive programmatic names.
    for i in range(page.locator('.reading-answer').count()):
        el=page.locator('.reading-answer').nth(i)
        lab=el.evaluate('(e)=>!!e.closest("label")')
        if not lab:fails.append(f'answer {i} lacks label')
    # Keyboard focus must be visibly styled globally and page needs semantic article/form landmarks for the task.
    if page.locator('article.reading-passage').count()!=1:fails.append('reading passage not semantic article')
    if page.locator('form#readingForm').count()!=1:fails.append('questions not grouped in form')
    if page.locator('[data-reading-submit]').get_attribute('type')!='button':fails.append('submit action type unclear')
    css=(ROOT/'styles.css').read_text(encoding='utf-8')
    if ':focus-visible' not in css:fails.append('visible focus rule missing')
    page.select_option('#languageMode','uahelp');page.wait_for_timeout(20)
    if page.locator('.ua-note').count()<1:fails.append('UA Help not exposed in Reading')
    browser.close()
if fails:
    print('G3 READING A11Y FAIL');print('\n'.join(fails));sys.exit(1)
print('G3 READING A11Y PASS')
