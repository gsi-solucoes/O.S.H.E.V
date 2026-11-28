"""R22: cruzar arquivos pelo número do registro.
- junta o mesmo registro (mesmo identificador) de vários relatórios;
- se uma data de um arquivo é igual, na maioria dos registros em comum, a uma data de outro arquivo cujo significado
  já se sabe (pelo rótulo), herda esse significado ("Dt. Execução = Data Término → encerramento")."""
import formula as F
from collections import Counter

def id_grupo(r):
    return next((g for g in r['grupos'] if not g['ctx'] and F.sugerir_tipo(g, r['registros']).startswith('Código')), None)

def norm_id(v):
    v = v.strip()
    return v.lstrip('0') or v

def indice(r):
    g = id_grupo(r)
    if not g: return {}, None
    m = {}
    for c in g['cel']:
        m.setdefault(norm_id(c[3]), c[0])
    return m, g

def datas_por_reg(g):
    out = {}
    for c in g['cel']:
        d = F.para_data(c[3])
        if d: out.setdefault(c[0], (d, ':' in c[3]))
    return out

def mesma(a, b):                       # com hora dos dois lados: igual; se um lado só tem o dia: mesmo dia
    (da, ha), (db, hb) = a, b
    return da == db if (ha and hb) else da.date() == db.date()

def cruzar(arqs):
    """arqs: {nome: r}. Preenche r['cruz'] (id → [(outro_arquivo, reg)]) e ajusta qual_data pela R22."""
    idx = {n: indice(r) for n, r in arqs.items()}
    for n, r in arqs.items():
        mi, _ = idx[n]
        r['cruz'] = {}
        for i, reg in mi.items():
            for o, (mo, _) in idx.items():
                if o != n and i in mo: r['cruz'].setdefault(reg, []).append((o, mo[i]))
    # R22: significado das datas pelo outro arquivo
    for n, r in arqs.items():
        mi, _ = idx[n]
        inv = {reg: i for i, reg in mi.items()}
        for g in r['grupos']:
            if g.get('tipo_maioria') != 'data' or g['ctx']: continue
            A = datas_por_reg(g)
            melhor = None
            for o, ro in arqs.items():
                if o == n: continue
                mo, _ = idx[o]
                for h in ro['grupos']:
                    if h.get('tipo_maioria') != 'data' or 'qual_data' not in h or h['qual_data']['conf'] != 'alta': continue
                    B = datas_por_reg(h)
                    pares = [(A[reg], B[mo[inv[reg]]]) for reg in A if reg in inv and inv[reg] in mo and mo[inv[reg]] in B]
                    if len(pares) < 5: continue
                    iguais = sum(1 for a, b in pares if mesma(a, b)) / len(pares)
                    if iguais >= 0.8 and (not melhor or iguais > melhor[0]):
                        melhor = (iguais, o, h['nome'], h['qual_data']['sig'], len(pares))
            if melhor:
                fr, o, hn, sig, npar = melhor
                antes = g.get('qual_data', {}).get('sig')
                g['qual_data'] = {'sig': sig, 'conf': 'alta',
                                  'mot': 'é igual a "%s" do arquivo %s em %d%% de %d registros em comum%s' % (
                                      hn, o, fr * 100, npar, (' (o rótulo sozinho sugeria "%s")' % antes) if antes and antes != sig else '')}
    return arqs

def nomes_cruzados(arqs):
    """R22b: grupo (não-data) igual a um grupo com nome em outro arquivo, nos mesmos registros → sugere aquele nome.
    Aceita texto cortado (um começa com o outro), comum em relatório resumido."""
    idx = {n: indice(r) for n, r in arqs.items()}
    for n, r in arqs.items():
        mi, _ = idx[n]; inv = {reg: i for i, reg in mi.items()}
        for g in r['grupos']:
            if g['ctx'] or g.get('tipo_maioria') == 'data' or F.sugerir_tipo(g, r['registros']).startswith('Código'): continue
            A = {}
            for c in g['cel']: A.setdefault(c[0], c[3].strip())
            melhor = None
            for o, ro in arqs.items():
                if o == n: continue
                mo, _ = idx[o]
                for h in ro['grupos']:
                    if '(sem nome)' in h['nome'] or ' · ' in h['nome'] or h.get('tipo_maioria') == 'data': continue   # só nome de verdade
                    B = {}
                    for c in h['cel']: B.setdefault(c[0], c[3].strip())
                    pares = [(A[reg], B[mo[inv[reg]]]) for reg in A if reg in inv and inv[reg] in mo and mo[inv[reg]] in B]
                    if len(pares) < 5: continue
                    ok = sum(1 for a, b in pares if a == b or (min(len(a), len(b)) >= 15 and (a.startswith(b) or b.startswith(a)))) / len(pares)
                    if ok >= 0.8 and (not melhor or ok > melhor[0]): melhor = (ok, o, h['nome'], len(pares))
            if melhor and melhor[2] != g['nome']:
                g['nome_cruz'] = {'nome': melhor[2], 'arq': melhor[1], 'pct': round(melhor[0] * 100), 'n': melhor[3]}
    return arqs
