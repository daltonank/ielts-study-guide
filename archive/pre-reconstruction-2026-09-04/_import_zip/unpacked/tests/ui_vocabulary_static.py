#!/usr/bin/env python3
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
html=(ROOT/'web'/'index.html').read_text(encoding='utf-8')
app=(ROOT/'web'/'app.js').read_text(encoding='utf-8')
fails=[]
for token in ['vocabFilterSource','vocabFilterPriority','vocabFilterTopic','vocabFilterStage','renderVocabResults','Starter 100','definitionUa']:
    if token not in app and token not in html:
        fails.append(f'Missing vocabulary UI token: {token}')
if fails:
    print('UI VOCAB STATIC FAIL')
    print('\n'.join(fails))
    sys.exit(1)
print('UI VOCAB STATIC PASS')
