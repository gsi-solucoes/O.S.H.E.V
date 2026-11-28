"""Oráculo: confere o resultado do script contra o gabarito feito à mão.
Uso: python3 -I conferir.py PASTA_CSV [arquivo ...]   (sem arquivo = todos do gabarito, na ordem)"""
import sys, os, json, importlib.util
AQUI = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('formula', os.path.join(AQUI, 'formula.py'))
F = importlib.util.module_from_spec(spec); spec.loader.exec_module(F)
GAB = json.load(open(os.path.join(AQUI, 'gabaritos.json'), encoding='utf-8'))

def conferir(pasta, nome):
    g = GAB[nome]
    caminho = os.path.join(pasta, nome)
    if not os.path.exists(caminho): caminho = os.path.join(pasta, '..', 'cegas', 'arq', nome)
    r = F.montar(F.ler(caminho)[0], caminho)
    erros = []
    if r['registros'] != g['registros']:
        erros.append('registros: esperado %d, achou %d' % (g['registros'], r['registros']))
    ctx = {e for e in r['ordem'] if r['grupos_por_end'][e]['ctx']}
    # cada amostra: achar o registro pelo id, e em que grupo caiu cada valor
    onde = {}                                   # significado -> lista de conjuntos de grupos
    for am in g['amostras']:
        reg = next((l for l in r['tabela'] if any(am['id'] in v for e, v in l.items() if e not in ctx and not str(e).startswith('__'))), None)
        if reg is None:
            erros.append('amostra %s: registro não encontrado' % am['id']); continue
        for k, v in am.items():
            if k == 'id' or v == '': continue
            gs = {e for e, vals in reg.items() if v in vals}
            if not gs: erros.append('amostra %s: "%s" = "%s" não está no registro' % (am['id'], k, v[:40]))
            onde.setdefault(k, []).append(gs)
        for k, v in am.items():
            if v == '' and k in onde:           # campo que deve estar vazio neste registro
                pass
    for k, lst in onde.items():
        if len(lst) > 1 and all(lst) and not set.intersection(*lst):
            nomes = [sorted(r['grupos_por_end'][e]['nome'] for e in s) for s in lst]
            erros.append('"%s" caiu em grupos diferentes nas amostras: %s' % (k, nomes))
    # campo vazio esperado: o grupo daquele significado não pode ter valor nesse registro
    for am in g['amostras']:
        for k, v in am.items():
            if v != '' or k not in onde: continue
            certos = set.intersection(*[s for s in onde[k] if s]) if any(onde[k]) else set()
            reg = next((l for l in r['tabela'] if any(am['id'] in vv for e, vv in l.items() if e not in ctx and not str(e).startswith('__'))), {})
            for e in certos:
                if reg.get(e): erros.append('amostra %s: "%s" devia estar vazio, mas tem "%s"' % (am['id'], k, reg[e][0][:30]))
    # sujeira não pode virar dado de registro
    for s in g['ruido']:
        for e in r['ordem']:
            if e in ctx: continue
            if any(c[3] == s for c in r['grupos_por_end'][e]['cel'] if c[1] is not None):
                erros.append('sujeira "%s" entrou no grupo "%s"' % (s, r['grupos_por_end'][e]['nome'])); break
    return erros, r

if __name__ == '__main__':
    pasta = sys.argv[1]
    nomes = sys.argv[2:] or list(GAB)
    ok = 0
    for n in nomes:
        erros, r = conferir(pasta, n)
        print(('✅' if not erros else '❌'), '%-50s %s | registros %d' % (n[:50], GAB[n]['formato'], r['registros']))
        for e in erros[:8]: print('     -', e)
        ok += not erros
    print('\n%d de %d certos' % (ok, len(nomes)))
