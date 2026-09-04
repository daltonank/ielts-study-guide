#!/usr/bin/env python3
from pathlib import Path
import json,re,sys
ROOT=Path(__file__).resolve().parents[1]
text=(ROOT/'web'/'vocabulary.js').read_text(encoding='utf-8')
meta=json.loads(re.search(r'window\.VOCABULARY_META=(\{.*?\});',text,re.S).group(1))
data=json.loads(re.search(r'window\.VOCABULARY=(\[.*\]);',text,re.S).group(1))
errors=[]
if not meta.get('complete'): errors.append('Meta does not mark migration complete')
if len(data)!=1784: errors.append(f'Expected 1784 records, found {len(data)}')
ids=[x['id'] for x in data]
if len(ids)!=len(set(ids)): errors.append('Duplicate IDs present')
words=[x['word'].casefold() for x in data]
if len(words)!=len(set(words)): errors.append('Duplicate normalized headwords present')
blank_ua=[x['word'] for x in data if not str(x.get('ua','')).strip()]
if blank_ua: errors.append(f'Blank Ukrainian equivalents: {len(blank_ua)}')
source_counts={}
for x in data: source_counts[x['source']]=source_counts.get(x['source'],0)+1
starter=sum(1 for x in data if x.get('starter100'))
print('G2 VALIDATION REPORT')
print('====================')
print('Records:', len(data))
print('Starter100:', starter)
print('Sources:', source_counts)
if errors:
    for e in errors: print('FAIL:', e)
    sys.exit(1)
print('PASS: count, uniqueness, Ukrainian fields, starter flagging, source metadata')
