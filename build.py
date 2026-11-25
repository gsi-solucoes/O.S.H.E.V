"""Monta o index.html: src/app.html + src/core.js + src/app.js num único script embutido (/*CORE*/).
A versão (VERSAO) e o hash do script para a CSP saem do próprio conteúdo."""
import base64, hashlib
from pathlib import Path
raiz = Path(__file__).parent
app = (raiz / 'src/app.html').read_text(encoding='utf-8')
core = '\n'.join(l for l in (raiz / 'src/core.js').read_text(encoding='utf-8').splitlines() if 'module.exports' not in l)
js = (raiz / 'src/app.js').read_text(encoding='utf-8')
assert app.count('/*CORE*/') == 1, 'marcador /*CORE*/ precisa aparecer uma vez'
versao = hashlib.sha256((core + js + app).encode()).hexdigest()[:10]
script = core + '\nconst VERSAO = "' + versao + '";\n' + js
h = base64.b64encode(hashlib.sha256(script.encode('utf-8')).digest()).decode()
out = app.replace('/*CORE*/', script).replace('/*CSPHASH*/', h)
(raiz / 'index.html').write_text(out, encoding='utf-8')
print('index.html gerado, versão', versao)
