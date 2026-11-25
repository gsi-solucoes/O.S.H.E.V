"""Monta o index.html: src/app.html com src/core.js injetado em /*CORE*/."""
from pathlib import Path
raiz = Path(__file__).parent
app = (raiz / 'src/app.html').read_text(encoding='utf-8')
core = '\n'.join(l for l in (raiz / 'src/core.js').read_text(encoding='utf-8').splitlines()
                 if 'module.exports' not in l)
assert app.count('/*CORE*/') == 1, 'marcador /*CORE*/ precisa aparecer uma vez'
(raiz / 'index.html').write_text(app.replace('/*CORE*/', core), encoding='utf-8')
print('index.html gerado')
