import re
text = open('gemini.html', encoding='utf-8').read()
# Decode unicode escapes like \u003c
text = text.encode('utf-8').decode('unicode_escape', 'ignore')

matches = re.findall(r'[A-Za-zñÑáéíóúÁÉÍÓÚüÜ0-9 \.\,\:\-\!\?]{80,}', text)
for m in matches:
    if len(m.strip()) > 80:
        print(m.strip())
