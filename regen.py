import re
with open('app.py', encoding='utf-8') as f:
    code = f.read()

m = re.search(r'html_code\s*=\s*f\"\"\"(.*?)\"\"\"', code, re.DOTALL)
h = m.group(1).replace('{{', '{').replace('}}', '}')
h = re.sub(r'\{FIREBASE_[^\}]+\}', 'test', h)
h = h.replace('signInAnonymously(auth).catch(e => setError("Error conectando. Revisa tu configuración de Firebase. " + e.message));', 'setUser({uid: "123"});//')

with open('test.html', 'w', encoding='utf-8') as f:
    f.write(h)
