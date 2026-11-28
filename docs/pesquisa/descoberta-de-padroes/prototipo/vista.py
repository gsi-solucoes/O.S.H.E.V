"""Vista do registro inteiro: todas as linhas da OS, cada célula na sua posição, a célula perguntada destacada."""
_cache = {}
def _linhas_do_reg(r):
    if id(r) not in _cache:
        m = {}
        for g in r['grupos']:
            for c in g['cel']:
                if c[1]: m.setdefault(c[0], set()).add(c[1] - 1)
        _cache[id(r)] = m
    return _cache[id(r)]

def vista(linhas, r, reg, linha_alvo=None, col_alvo=None, marcar=()):
    minhas = _linhas_do_reg(r).get(reg) or ({linha_alvo - 1} if linha_alvo else set(r['blocos'][reg]))
    ult = max(minhas)
    bloco = [k for k in r['blocos'][reg] if any(linhas[k]) and k <= ult]   # corta o que já é da OS seguinte
    modo = 'bloco' if len(bloco) > 1 else 'linha'
    if modo == 'linha' and linha_alvo:                                # tabela: mostra vizinhas apagadas
        viz = []
        for d in (-2, -1, 1, 2):
            rr = reg + d
            if 0 <= rr < len(r['blocos']):
                ks = [k for k in r['blocos'][rr] if any(linhas[k])]
                if ks: viz.append((d, ks[0]))
        bloco = sorted([k for d, k in viz if d < 0]) + bloco + sorted([k for d, k in viz if d > 0])
    gl = r['gov_reg'][reg]
    idx = ([gl] if gl is not None and gl not in bloco else []) + bloco
    cols = sorted({j for k in idx for j, c in enumerate(linhas[k]) if c})
    rows = []
    for k in idx:
        cel = [(linhas[k][j] if j < len(linhas[k]) else '') for j in cols]
        # texto se estende sobre as vazias à direita (como no Excel): [texto, colspan, col_original]
        row, i = [], 0
        while i < len(cel):
            n = 1
            while cel[i] and i + n < len(cel) and not cel[i + n]: n += 1
            row.append([cel[i], n, cols[i]]); i += n
        rows.append(row)
    alvo = [idx.index(linha_alvo - 1), col_alvo - 1] if linha_alvo and (linha_alvo - 1) in idx else None
    marcas = [[idx.index(li - 1), co - 1] for li, co in marcar if (li - 1) in idx]
    ctx = [[r['grupos_por_end'][e]['nome'], v[0]] for e, v in r['tabela'][reg].items() if e in r['grupos_por_end'] and r['grupos_por_end'][e]['ctx']]
    cab = gl is not None and gl not in bloco
    apagadas = [i for i, k in enumerate(idx) if modo == 'linha' and linha_alvo and k != linha_alvo - 1 and not (cab and i == 0)]
    deitada = None
    if False:  # vista deitada desligada: mostrar sempre como vem no arquivo                    # tabela larga: cabeçalho → valor
        hd = {j: linhas[gl][j] for j in cols if j < len(linhas[gl]) and linhas[gl][j]}
        lin = linhas[linha_alvo - 1]
        deitada = [[hd.get(j, ''), lin[j] if j < len(lin) else '', j == col_alvo - 1] for j in cols if (j < len(lin) and lin[j]) or j in hd]
    return {'rows': rows, 'alvo': alvo, 'cab': cab, 'ctx': ctx, 'modo': modo, 'apagadas': apagadas, 'deitada': deitada, 'marcas': marcas}
