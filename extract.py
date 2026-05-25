import re, json

html = open('gemini.html', encoding='utf-8').read()
matches = re.findall(r'AF_initDataCallback\(\{.*?data:(\[.*?\])\s*\}\);', html, re.DOTALL)
text_all = ""
for m in matches:
    text_all += m + '\n'

import ast
try:
    for line in text_all.split(r'\n'):
        if len(line) > 50:
            clean = re.sub(r'<[^>]+>', '', line)
            print(clean[:200])
except Exception as e:
    print(e)
