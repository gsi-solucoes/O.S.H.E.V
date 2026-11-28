"""FÓRMULA ÚNICA: descobre o padrão de qualquer CSV, sem nada fixo de relatório.

Regras (pistas), na ordem em que são aplicadas. Cada uma veio da análise à mão (analise_manual.md).
 R1  Leitura: acha a codificação e o separador sozinho.
 R2  Centavos partidos: "R$ 864" seguido de célula com 2 dígitos = um valor só ("R$ 864,31").
 R3  Rótulo dentro da célula: "CLIENTE: ANA" vira rótulo + valor, quando o "CLIENTE:" se repete.
 R4  Cara da célula: data, tempo, valor, número, código, texto curto, texto longo; vazio/sujeira.
 R5  Rótulo: texto com cara de rótulo (minúscula ou ":") que se repete; sem repetição, basta a cara.
 R6  Título de bloco: texto sozinho na linha, que se repete e não tem rótulo em cima = título, não dado.
 R7  Linha de rótulo só se começa com rótulo; linha que começa com valor é toda de valores.
 R8  Linha de total: um número sozinho (com ou sem texto) igual à contagem de registros do grupo = total.
 R9  Identificador: número/código que não se repete marca o registro (um por registro).
 R10 Começo do bloco: linhas só de rótulo que sempre vêm logo antes do identificador são do registro.
 R11 Contexto: o que aparece antes do 1º registro, e menos vezes que eles, vale para os seguintes.
 R12 Registro sem número: mesmo desenho de registro sem o identificador ainda é registro;
     desenho diferente é detalhe do registro anterior.
 R13 Endereço do valor: rótulo à esquerda > cabeçalho em cima (encaixe por posição + tipo + vocabulário)
     > ordem dos tipos (quando não há rótulo nenhum).
 R14 Valor sem rótulo no cabeçalho: nomeado pela posição relativa ("depois de X"), não pela coluna.
 R15 Rodapé: linhas depois do último registro com desenho que nenhum outro registro tem = notas.
 R16 Lista: o mesmo grupo várias vezes no registro.
 R17 Não pertence: tipo/formato diferente da maioria; sugere o grupo onde se encaixa melhor.
 R18 Grupo raro: aparece em menos de 5% dos registros → perguntar se é mesmo grupo.
 R19 Datas: quem vem antes de quem, distância típica, quem fura a ordem.
 R20 Colunas só com vazio/sujeira: juntadas para a caixa "excluir".
"""
import csv, io, re, os, statistics
from collections import Counter, defaultdict
from datetime import datetime

csv.field_size_limit(10**8)

# ---------- R1 leitura ----------
def ler(caminho):
    bruto = open(caminho, 'rb').read()
    for enc in ('utf-8-sig', 'cp1252', 'latin1'):
        try: txt = bruto.decode(enc); break
        except UnicodeDecodeError: continue
    amostra = txt[:20000]
    sep = max([',', ';', '\t', '|'], key=lambda s: amostra.count(s))
    linhas = [[c.strip() for c in l] for l in csv.reader(io.StringIO(txt), delimiter=sep)]
    return preparar(linhas), sep, enc

# ---------- R2 centavos partidos, R3 rótulo dentro da célula ----------
R_SEM_CENT = re.compile(r'R\$ ?-?\d[\d.]*$')
R_ROT_CEL = re.compile(r'([^:\d]{1,30}?)\s*:\s+(\S.*)$')
def preparar(linhas):
    out = []
    for l in linhas:
        n = []
        for c in l:
            if n and re.fullmatch(r'\d{2}', c) and R_SEM_CENT.match(n[-1]):
                n[-1] = n[-1] + ',' + c; continue
            n.append(c)
        out.append(n)
    pref = Counter(m.group(1).strip() for l in out for c in l for m in [R_ROT_CEL.match(c)] if m)
    bons = {p for p, q in pref.items() if q >= 3 and len(p.split()) <= 4}
    if bons:
        out2 = []
        for l in out:
            cheias = [c for c in l if c and re.search(r'\w', c)]
            todas = cheias and all((lambda m: m and m.group(1).strip() in bons)(R_ROT_CEL.match(c)) for c in cheias)
            n = []
            for c in l:
                m = R_ROT_CEL.match(c)
                if todas and m and m.group(1).strip() in bons: n += [m.group(1).strip() + ':', m.group(2).strip()]   # só se a LINHA toda é "RÓTULO: valor"
                else: n.append(c)
            out2.append(n)
        out = out2
    return out

# ---------- R4 cara da célula ----------
R_DATA = re.compile(r'(\d{1,2}[/.-]\d{1,2}[/.-]\d{2,4}|\d{4}-\d{2}-\d{2})( \d{1,2}:(\d{2}(:\d{2})?)?)?$')   # aceita hora cortada ("10:")
R_TEMPO = re.compile(r'\d{1,4}:\d{2}(:\d{2})?$')
R_VALOR = re.compile(r'R\$ ?-?\d{1,3}(\.\d{3})*,\d{2}$|-?\d{1,3}(\.\d{3})+,\d{2}$|R\$ ?-?\d+([.,]\d+)?$')   # dinheiro: com R$ ou com milhar (1.234,56); "1,78" é número
R_NUM = re.compile(r'-?\d+([.,]\d+)?$')
def tipo(t):
    if not re.search(r'\w', t): return None
    if R_DATA.match(t): return 'data'
    if R_TEMPO.match(t): return 'tempo'
    if R_VALOR.match(t): return 'valor'
    if R_NUM.match(t): return 'numero'
    if ' ' not in t and re.search(r'\d', t) and re.search(r'[A-Za-zÀ-ú]', t): return 'codigo'
    return 'frase' if len(t.split()) >= 6 else 'termo'
FAMILIA = {'frase': 'texto', 'termo': 'texto'}
def familia(t): return FAMILIA.get(t, t)
def mascara(t): return re.sub(r'\d', '9', re.sub(r'[A-Za-zÀ-ú]', 'A', t))
def cara_de_rotulo(t):
    return tipo(t) in ('termo', 'frase') and len(t) <= 40 and len(t.split()) <= 6 and (t.endswith(':') or bool(re.search(r'[a-zà-ú]', t)))
def para_data(t):
    t = re.sub(r' (\d{1,2}):$', r' \1:00', t)   # hora cortada vira hora cheia
    for f in ('%d/%m/%Y %H:%M', '%d/%m/%y %H:%M', '%d/%m/%Y', '%d/%m/%y', '%d/%m/%Y %H:%M:%S', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d'):
        try: return datetime.strptime(t, f)
        except ValueError: pass
    return None

# ---------- R5 a R8: o desenho de cada linha ----------
def analisar(linhas):
    cont = Counter(c for l in linhas for c in l if c)
    candidatos = [t for t in cont if cara_de_rotulo(t)]
    repetem = any(cont[t] >= 2 for t in candidatos)
    rot = {t for t in candidatos if cont[t] >= 2}                                      # R5
    cheias = [[(j, c) for j, c in enumerate(l) if c and tipo(c) is not None] for l in linhas]
    cabecalho = set()
    for i, cel in enumerate(cheias[:30]):                                              # R5 cabeçalho único
        prox = next((x for x in cheias[i + 1:i + 4] if x), [])
        if len(cel) >= 3 and all(cara_de_rotulo(c) for _, c in cel) and any(tipo(c) in ('numero', 'data', 'codigo', 'valor') for _, c in prox):
            cabecalho.update(c for _, c in cel)
    rot |= cabecalho
    if cabecalho:                                                                    # R5b: em linha de DADOS, texto repetido é valor
        ncab = max(len([c for c in l if c]) for l in linhas[:30] if any(c in cabecalho for c in l))
        cols_cab = {j for l in linhas[:30] if any(c in cabecalho for c in l) for j, c in enumerate(l) if c in cabecalho}
        como_valor, total_vez = Counter(), Counter()
        for cel in cheias:
            if not cel or all(c in cabecalho for _, c in cel): continue
            alinhadas = sum(1 for j, _ in cel if j in cols_cab or j - 1 in cols_cab or j + 1 in cols_cab) / len(cel)   # embaixo das colunas do cabeçalho
            dados = alinhadas >= 0.7 and len(cel) >= max(2, 0.5 * ncab) and any(tipo(c) in ('numero', 'data', 'valor', 'codigo', 'tempo') for _, c in cel)
            for _, c in cel:
                if c in rot and c not in cabecalho and not c.endswith(':'):
                    total_vez[c] += 1; como_valor[c] += dados
        rot -= {t for t in total_vez if como_valor[t] >= 0.5 * total_vez[t]}
    if not repetem and not cabecalho: rot = set(candidatos)                          # formulário sem repetição e sem cabeçalho: vale a cara
    # R6 título de bloco
    sozinho = Counter(); acompanhado = Counter(); titulo_ok = Counter()
    ant = []
    for cel in cheias:
        if not cel: continue
        if len(cel) == 1:
            t = cel[0][1]; sozinho[t] += 1
            if not (ant and all(c in rot for _, c in ant)): titulo_ok[t] += 1
        else:
            for _, c in cel: acompanhado[c] += 1
        ant = cel
    for t, q in sozinho.items():
        if q >= 3 and not acompanhado[t] and titulo_ok[t] == q and t not in rot and tipo(t) in ('termo', 'frase'):
            rot.add(t)
    info = []
    for i, cel in enumerate(cheias):
        linha_rot = bool(cel) and cel[0][1] in rot                                     # R7
        r, v = [], []
        for j, c in cel: (r if linha_rot and c in rot else v).append((j, c))
        nums = [c for _, c in v if tipo(c) in ('numero', 'valor')]
        outros = [c for _, c in v if tipo(c) not in ('numero', 'valor')]
        total = len(nums) == 1 and len(outros) <= 2 and all(cara_de_rotulo(c) or c in rot for c in outros)  # R8 candidato
        info.append({'i': i, 'rot': r, 'val': v, 'cand_total': total})
    com_valor = set()
    for d in info:
        if d['rot']:
            d['chave'] = ('R',) + tuple(t for _, t in d['rot'])
            if d['val']: com_valor.add(d['chave'])
    gov = None
    for d in info:
        if d['rot']:
            if not d['val'] and d['chave'] not in com_valor: gov = d
        elif d['val']:
            d['gov'] = gov
            d['chave'] = ('V', gov['chave'] if gov else ('-',), len(d['val']) > 1)
        else:
            d['chave'] = None
    return info, rot

# ---------- R9 identificador ----------
def achar_ancora(info):
    cand = defaultdict(list)
    for d in info:
        if not d['chave'] or not d['val'] or d['cand_total']: continue
        for k, (_, t) in enumerate(d['val'][:3]):
            if tipo(t) in ('numero', 'codigo') and not re.search(r'\d[.,]\d', t): cand[(d['chave'], k)].append(t)   # decimal = medida, não identifica
    melhor, nota = None, 0
    for ch, vals in cand.items():
        dist = len(set(vals))
        if len(vals) >= 3 and dist / len(vals) >= 0.85 and dist > nota: melhor, nota = ch, dist
    if melhor: return melhor[0], melhor[1], 'identificador único (%d valores diferentes)' % nota
    cont = Counter(d['chave'] for d in info if d['chave'] and not d['cand_total'])
    return cont.most_common(1)[0][0], None, 'desenho de linha que mais se repete'

# ---------- R12 registro sem número / detalhe ----------
def alinhar_tipos(seq, ref):
    n, m = len(seq), len(ref)
    D = [[0.0] * (m + 1) for _ in range(n + 1)]
    for i in range(n + 1): D[i][0] = i * 2
    for j in range(m + 1): D[0][j] = j
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            D[i][j] = min(D[i - 1][j - 1] + (0 if familia(seq[i - 1]) == familia(ref[j - 1]) else 1.5), D[i - 1][j] + 2, D[i][j - 1] + 1)
    res, i, j = [None] * n, n, m
    while i > 0 and j > 0:
        if D[i][j] == D[i - 1][j - 1] + (0 if familia(seq[i - 1]) == familia(ref[j - 1]) else 1.5): res[i - 1] = j - 1; i -= 1; j -= 1
        elif D[i][j] == D[i - 1][j] + 2: i -= 1
        else: j -= 1
    return res, D[n][m]

def reancorar(info, ancora, k_id):
    linhas_id = [d for d in info if d['chave'] == ancora and not d['cand_total'] and len(d['val']) > k_id and tipo(d['val'][k_id][1]) in ('numero', 'codigo')]
    ids = [d['val'][k_id][1] for d in linhas_id]
    mascs = Counter(mascara(v) for v in ids)
    tid = Counter(tipo(v) for v in ids).most_common(1)[0][0]
    def tem_id(d, forte=False):
        if len(d['val']) <= k_id: return False
        v = d['val'][k_id][1]
        if tid == 'numero' and not forte: return tipo(v) == 'numero'  # R9b: número de identificação cresce com o tempo
        return tipo(v) == tid and mascs[mascara(v)] >= max(1, 0.05 * len(ids))
    modelo = linhas_id[0]
    ref = Counter(tuple(tipo(t) for k, (_, t) in enumerate(d['val']) if k != k_id) for d in linhas_id).most_common(1)[0][0]
    for d in info:                      # mesmo identificador sob outro cabeçalho = registro
        if d['chave'] and d['chave'][0] == 'V' and d['chave'] != ancora and not d['cand_total'] and len(d['val']) > 1 and tem_id(d, forte=True):
            d['gov'], d['chave'] = modelo.get('gov'), ancora
    for d in info:
        if d['chave'] != ancora: continue
        if d['cand_total']: d['chave'] = ('TOT',) + d['chave']; continue
        if tem_id(d): d['sem_id'] = False; continue
        seq = tuple(tipo(t) for _, t in d['val'])
        _, custo = alinhar_tipos(seq, ref)
        if custo <= 2.0 and len(seq) >= 0.6 * len(ref): d['sem_id'] = True   # registro sem número
        else: d['chave'] = ('DET',) + d['chave']; d['papel'] = 'det'  # detalhe do anterior

def registros(info, ancora):
    cont = Counter(d['chave'] for d in info if d['chave'])
    n = cont[ancora]
    idx = [k for k, d in enumerate(info) if d['chave'] == ancora and not d.get('cand_total')]
    recuo = 0                                                         # R10
    while True:
        ant = [info[k - recuo - 1] for k in idx if k - recuo - 1 >= 0]
        if not ant: break
        ch, q = Counter(d['chave'] for d in ant).most_common(1)[0]
        if ch and q >= 0.95 * n and cont[ch] <= n * 1.05 and ch[0] == 'R' and not any(d['val'] for d in ant if d['chave'] == ch): recuo += 1
        else: break
    inicios = [k - recuo for k in idx]
    antes = {d['chave'] for d in info[:inicios[0]] if d['chave']}
    contexto = {c for c in antes if cont[c] < n}                      # R11
    blocos = [list(range(a, b)) for a, b in zip(inicios, inicios[1:] + [len(info)])]
    # R15 rodapé: no último bloco, desenhos que nenhum outro bloco tem
    notas = []
    if len(blocos) > 1:
        vistos = {info[k]['chave'] for b in blocos[:-1] for k in b}
        ult = []
        for k in blocos[-1]:
            ch = info[k]['chave']
            if ch is None or ch in vistos or ch == ancora or ch in contexto: ult.append(k)
            else: notas.append(k)
        blocos[-1] = ult
    return blocos, contexto, recuo, notas

# ---------- R13 / R14 endereço de cada valor ----------
def custo_dp(vals, labs, custo, falta=4.0):
    n, m = len(vals), len(labs)
    INF = 1e18
    D = [[INF] * (m + 1) for _ in range(n + 1)]; P = [[None] * (m + 1) for _ in range(n + 1)]
    D[0] = [0.0] * (m + 1)
    for i in range(1, n + 1):
        D[i][0] = D[i - 1][0] + falta; P[i][0] = 'v'
        for j in range(1, m + 1):
            D[i][j], P[i][j] = min((D[i - 1][j - 1] + custo(i - 1, j - 1), 'd'), (D[i - 1][j] + falta, 'v'), (D[i][j - 1], 'h'))
    res, i, j = [None] * n, n, m
    while i > 0:
        p = P[i][j]
        if p == 'd': res[i - 1] = j - 1; i -= 1; j -= 1
        elif p == 'v': i -= 1
        else: j -= 1
    return res

def enderecar(info):
    sob_cab = [d for d in info if d['chave'] and d['chave'][0] in ('V', 'DET', 'TOT') and d.get('gov') and len(d['gov']['rot']) >= 2]
    # 1ª passada: só posição, para aprender o tipo e o vocabulário de cada rótulo do cabeçalho
    stats = defaultdict(lambda: {'fam': Counter(), 'voc': Counter(), 'n': 0})
    larg = defaultdict(Counter)                                       # R13b: aprender só com linhas completas
    for d in sob_cab: larg[d['gov']['chave']][len(d['val'])] += 1
    moda = {ch: c.most_common(1)[0][0] for ch, c in larg.items()}
    for d in sob_cab:
        if len(d['val']) != moda[d['gov']['chave']]: continue
        hc = [c for c, _ in d['gov']['rot']]
        al = custo_dp([j for j, _ in d['val']], hc, lambda a, b, d=d, hc=hc: abs(d['val'][a][0] - hc[b]))
        for (j, t), k in zip(d['val'], al):
            if k is None: continue
            s = stats[(d['gov']['chave'], k)]; s['fam'][familia(tipo(t))] += 1; s['voc'][t] += 1; s['n'] += 1
    def custo_conteudo(d, hc, a, b):
        j, t = d['val'][a]; s = stats[(d['gov']['chave'], b)]
        c = 0.5 * abs(j - hc[b])
        if s['n'] >= 5:
            fam, q = s['fam'].most_common(1)[0]
            if q >= 0.7 * s['n'] and familia(tipo(t)) != fam: c += 3
            if t not in s['voc'] and any(t in o['voc'] for (gk, ob), o in stats.items() if gk == d['gov']['chave'] and ob != b): c += 2   # visto em OUTRA coluna
        return c
    seqs = defaultdict(Counter)
    for d in info:
        if d['chave'] and d['chave'][0] in ('V', 'DET', 'TOT') and not (d.get('gov') and len(d['gov']['rot']) >= 2):
            seqs[d['chave']][tuple(tipo(t) for _, t in d['val'])] += 1
    ref = {ch: max((s for s in c if len(s) == max(len(x) for x in c)), key=lambda s: c[s]) for ch, c in seqs.items()}
    for d in info:
        d['end'] = []
        if not d['chave']: continue
        papel = d.get('papel', 'reg')
        if d['chave'][0] == 'R':                                       # rótulo à esquerda
            for j, t in d['val']:
                esq = [r for r in d['rot'] if r[0] < j]
                if esq: d['end'].append((('rot', esq[-1][1]), esq[-1][1].rstrip(':').strip(), j, t))
                else: d['end'].append((('ini', d['chave']), 'Antes de "%s"' % d['rot'][0][1].rstrip(':'), j, t))
        elif d.get('gov') and len(d['gov']['rot']) >= 2:                # cabeçalho em cima
            g = d['gov']; hc = [c for c, _ in g['rot']]
            al = custo_dp(list(range(len(d['val']))), hc, lambda a, b, d=d, hc=hc: custo_conteudo(d, hc, a, b))
            ultimo = None
            for (j, t), k in zip(d['val'], al):
                if k is None:
                    nome = 'Sem nome (depois de "%s")' % ultimo if ultimo else 'Sem nome (antes de "%s")' % g['rot'][0][1].rstrip(':')
                    d['end'].append((('cab-sem', g['chave'], ultimo, papel), nome, j, t))
                else:
                    nome = g['rot'][k][1].rstrip(':').strip(); ultimo = nome
                    d['end'].append((('cab', g['chave'], nome, papel), nome + (' (detalhe)' if papel == 'det' else ''), j, t))
        else:                                                           # título em cima ou nada
            g = d.get('gov'); titulo = g['rot'][0][1].rstrip(':').strip() if g else None
            al, _ = alinhar_tipos([tipo(t) for _, t in d['val']], ref[d['chave']])
            for (j, t), k in zip(d['val'], al):
                nome = (titulo if len(ref[d['chave']]) == 1 else '%s · %d' % (titulo, (k or 0) + 1)) if titulo else None   # um valor só: o nome é o título
                d['end'].append((('ord', d['chave'], k, papel), nome, j, t))

# ---------- montagem ----------
def montar(linhas, caminho):
    base = {'arquivo': os.path.basename(caminho), 'linhas': len(linhas), 'recuo': 0, 'grupos': [], 'tabela': [], 'ordem': [],
            'datas': [], 'sem_id': 0, 'totais': [], 'notas': 0, 'colunas_sujeira': [], 'grupos_por_end': {}}
    info, rot = analisar(linhas)
    base['rotulos'] = len(rot)
    if not any(d['val'] for d in info):
        base.update(registros=0, como='só modelo, nenhum valor preenchido'); return base
    ancora, k_id, como = achar_ancora(info)
    if k_id is not None: reancorar(info, ancora, k_id)
    blocos, contexto, recuo, notas = registros(info, ancora)
    enderecar(info)

    grupos, ordem = {}, []
    def grupo(end, nome, ctx):
        if end not in grupos:
            grupos[end] = {'end': end, 'nome': nome, 'ctx': ctx, 'cel': [], 'por_reg': Counter()}; ordem.append(end)
        return grupos[end]

    # R8: confirmar linhas de total (número = registros do trecho ou do arquivo)
    pos_reg = [b[0] for b in blocos]
    total_reg = len(blocos)
    totais, desde = [], 0
    marcos, atual = [], {}                       # R11b: contexto repetido com o mesmo valor é continuação (quebra de página)
    for k, d in enumerate(info):
        if d['cand_total']: marcos.append(k)
        elif d['chave'] in contexto and d['val']:
            vals = tuple(t for _, t in d['val'])
            if atual.get(d['chave']) != vals: marcos.append(k); atual[d['chave']] = vals
    for k, d in enumerate(info):
        if not d['cand_total']: continue
        num = next(t for _, t in d['val'] if tipo(t) in ('numero', 'valor'))
        ant = max([m for m in marcos if m < k], default=-1)
        trecho = sum(1 for p in pos_reg if ant < p < k)
        def valor_num(t):
            t = re.sub(r'[R$\s]', '', t)
            if ',' in t: t = t.replace('.', '').replace(',', '.')
            try: return float(t)
            except ValueError: return None
        vn = valor_num(num)
        if vn is not None and vn in (trecho, total_reg):
            d['eh_total'] = True; totais.append({'linha': k + 1, 'valor': num, 'conferido': 'igual a %d registros' % (trecho if vn == trecho else total_reg)})
        elif vn is not None:                                            # R8b: igual à SOMA da coluna nos registros do trecho
            col = next(j for j, t in d['val'] if t == num)
            soma, parcelas = 0.0, 0
            for p in pos_reg:
                if ant < p < k:
                    for kk in blocos[pos_reg.index(p)]:
                        if kk == k: continue                            # a própria linha não entra na soma
                        for j, t in info[kk]['val']:
                            if j == col and valor_num(t) is not None: soma += valor_num(t); parcelas += 1
            if parcelas >= 2 and abs(soma - vn) < 0.01:                 # soma de pelo menos 2 registros
                d['eh_total'] = True; totais.append({'linha': k + 1, 'valor': num, 'conferido': 'igual à soma da coluna (%s)' % num})

    tabela, ctx_atual, sem_id = [], {}, 0
    for d in info[:blocos[0][0]]:
        if d['chave'] in contexto and not d.get('eh_total'):
            for end, nome, j, t in d['end']: ctx_atual[end] = t; grupo(end, nome, True)
    for r, bloco in enumerate(blocos):
        lin = {}
        ctx_reg = None
        if info[bloco[0] + recuo if bloco[0] + recuo < len(info) else bloco[0]].get('sem_id'): lin['__sem_id__'] = ['sim']; sem_id += 1
        for k in bloco:
            d = info[k]
            if not d['chave'] or d.get('eh_total'): continue
            if d['chave'] in contexto:
                if ctx_reg is None and k > bloco[0] + recuo: ctx_reg = dict(ctx_atual)
                for end, nome, j, t in d['end']: ctx_atual[end] = t; grupo(end, nome, True)
                continue
            viz = [(c, x) for c, x in d['rot']] + ([(c, x) for c, x in d['gov']['rot']] if d.get('gov') else [])
            for end, nome, j, t in d['end']:
                g = grupo(end, nome, False); g['cel'].append((r, d['i'] + 1, j + 1, t)); g['por_reg'][r] += 1
                if len(g['cel']) <= 50:
                    g.setdefault('viz_todos', Counter()).update(x for _, x in viz)
                    perto = sorted(viz, key=lambda cx: abs(cx[0] - j))
                    g.setdefault('viz_perto', Counter()).update(x for _, x in perto[:3] if x.rstrip(':').strip() != (nome or ''))
                lin.setdefault(end, []).append(t)
        for end, t in (ctx_reg if ctx_reg is not None else ctx_atual).items():
            lin[end] = [t]; grupos[end]['cel'].append((r, None, None, t))
        tabela.append(lin)

    total = len(tabela); sem_nome = 0
    for end in ordem:
        g = grupos[end]; vals = [c[3] for c in g['cel']]
        tipos = Counter(tipo(v) for v in vals)
        g['tipo_maioria'] = tipos.most_common(1)[0][0] if tipos else None
        g['mascaras'] = Counter(mascara(v) for v in vals if tipo(v) == g['tipo_maioria'])
        g['vocab'] = Counter(vals)
        g['preenchido'] = len({c[0] for c in g['cel']}) / total if total else 0
        g['lista'] = max(g['por_reg'].values()) if g['por_reg'] else 1
        if not g['nome']: sem_nome += 1; g['nome'] = 'Grupo %d (sem nome)' % sem_nome
    vistos_nome = Counter()                                           # nomes repetidos ganham número
    for end in ordem:
        g = grupos[end]; vistos_nome[g['nome']] += 1
        if vistos_nome[g['nome']] > 1: g['nome'] = '%s (%d)' % (g['nome'], vistos_nome[g['nome']])

    def estranha(g, v):                                                 # R17
        tp = tipo(v); fm = familia(g['tipo_maioria'])
        if g['tipo_maioria'] and familia(tp) != fm and g['vocab'][v] <= 2:
            if sum(1 for c in g['cel'] if familia(tipo(c[3])) == fm) >= 0.6 * len(g['cel']):
                return 'tipo diferente (%s no meio de %s)' % (nome_tipo(tp), nome_tipo(g['tipo_maioria']))
        if tp in ('numero', 'codigo') and tp == g['tipo_maioria'] and g['mascaras']:
            mc, qm = g['mascaras'].most_common(1)[0]
            if qm >= 0.8 * sum(g['mascaras'].values()) and abs(len(mascara(v)) - len(mc)) >= 2:
                return 'formato diferente (%s; a maioria é %s)' % (mascara(v), mc)
        return None
    def nota(g, v):
        p = 0
        if familia(tipo(v)) == familia(g['tipo_maioria']): p += 3
        if mascara(v) in g['mascaras']: p += 2
        if g['vocab'][v]: p += 3
        return p
    for end in ordem:
        g = grupos[end]; g['marcadas'] = []
        for c in g['cel']:
            if c[1] is None: continue
            motivo = estranha(g, c[3])
            if motivo:
                outros = sorted(((nota(h, c[3]), h['nome']) for h in grupos.values() if h is not g), reverse=True)
                g['marcadas'].append({'reg': c[0] + 1, 'linha': c[1], 'valor': c[3], 'motivo': motivo,
                                      'sugestao': outros[0][1] if outros and outros[0][0] >= 5 else 'grupo novo'})
        if 0 < g['preenchido'] < 0.05 and not g['ctx'] and total > 20:       # R18
            g['aviso'] = 'aparece só em %d de %d registros: é mesmo um grupo?' % (len(g['por_reg']), total)

    # R23 número que é "apelido" de uma categoria (cada número anda sempre com o mesmo texto, e vice-versa) = código daquela categoria
    por_reg_val = {e: {} for e in ordem}
    for e in ordem:
        for c in grupos[e]['cel']: por_reg_val[e].setdefault(c[0], c[3])
    for e in ordem:
        g = grupos[e]
        if g['tipo_maioria'] != 'numero' or g['ctx'] or g['preenchido'] < 0.5 or any(re.search(r'\d[.,]\d', v) for v in por_reg_val[e].values()): continue
        A = por_reg_val[e]
        if len(set(A.values())) < 3 or len(set(A.values())) > 0.5 * len(A): continue
        for e2 in ordem:
            h = grupos[e2]
            if e2 == e or familia(h['tipo_maioria']) != 'texto': continue
            B = por_reg_val[e2]; com = [r for r in A if r in B]
            if len(com) < 10: continue
            ida, volta = defaultdict(Counter), defaultdict(Counter)
            for r in com: ida[A[r]][B[r]] += 1; volta[B[r]][A[r]] += 1
            fiel = sum(c.most_common(1)[0][1] for c in ida.values()) / len(com)
            fiel2 = sum(c.most_common(1)[0][1] for c in volta.values()) / len(com)
            if fiel >= 0.95 and fiel2 >= 0.95: g['codigo_de'] = h['nome']; break
    datas = [grupos[e] for e in ordem if grupos[e]['tipo_maioria'] == 'data' and not grupos[e]['ctx']]   # R19
    por = {}
    for g in datas:
        for c in g['cel']:
            dt = para_data(c[3])
            if dt: por.setdefault(g['nome'], {}).setdefault(c[0], dt)
    notas_datas = []
    for a in range(len(datas)):
        for b in range(a + 1, len(datas)):
            A, B = por.get(datas[a]['nome'], {}), por.get(datas[b]['nome'], {})
            com = [r for r in A if r in B]
            if len(com) < 5: continue
            fr = sum(1 for r in com if A[r] <= B[r]) / len(com)
            if fr >= 0.9 or fr <= 0.1:
                pri, seg, X, Y = (datas[a], datas[b], A, B) if fr >= 0.9 else (datas[b], datas[a], B, A)
                ok = [r for r in com if X[r] <= Y[r]]
                dif = statistics.median((Y[r] - X[r]).total_seconds() for r in ok) if ok else 0
                furam = [r + 1 for r in com if X[r] > Y[r]]
                notas_datas.append({'antes': pri['nome'], 'depois': seg['nome'], 'tipico': tempo_txt(dif), 'seg': dif, 'casos': len(com), 'furam': furam[:8], 'n_furam': len(furam)})

    inferir_datas([grupos[e] for e in ordem if grupos[e]['tipo_maioria'] == 'data'], notas_datas)   # R21
    sujeira = Counter(); cheio = Counter()                              # R20
    for l in linhas:
        for j, c in enumerate(l):
            if c: (cheio if tipo(c) else sujeira)[j] += 1
    col_suj = sorted(j + 1 for j in sujeira if not cheio[j])

    gov_reg = []                                                      # linha do cabeçalho que governa cada registro
    for b in blocos:
        gl = next((info[k]['gov']['i'] for k in b if info[k].get('gov') and len(info[k]['gov']['rot']) >= 2), None)
        gov_reg.append(gl)
    base.update(blocos=blocos, gov_reg=gov_reg)
    base.update(como=como, recuo=recuo, registros=total, grupos=[grupos[e] for e in ordem], tabela=tabela, ordem=ordem,
                datas=notas_datas, sem_id=sem_id, totais=totais, notas=len(notas), colunas_sujeira=col_suj, grupos_por_end=grupos)
    return base

def tempo_txt(s):
    if s < 3600: return '%d min' % (s // 60)
    if s < 86400 * 2: return '%.1f h' % (s / 3600)
    return '%.0f dias' % (s / 86400)
NOMES = {'data': 'data', 'tempo': 'tempo', 'valor': 'valor (R$)', 'numero': 'número', 'codigo': 'código',
         'frase': 'texto longo', 'termo': 'texto curto', None: 'vazio'}
def nome_tipo(t): return NOMES.get(t, t)
def sugerir_tipo(g, total):
    t = g['tipo_maioria']; vals = [c[3] for c in g['cel']]; dist = len(set(vals))
    if g.get('codigo_de'): return 'Categoria'   # R23: código de "%s"
    if t == 'numero' and re.search(r'valor|pre[cç]o|total|custo|r\$', (g['nome'] or '').lower()) and all(re.search(r',\d{2}$', v) for v in vals): return 'Valor (R$)'   # rótulo de dinheiro
    if t == 'numero' and any(re.search(r'\d[.,]\d', v) for v in vals): return 'Número'   # tem casas decimais: é medida
    if t == 'termo' and dist == len(vals) and len(vals) >= 0.9 * total and total >= 3: return 'Categoria'   # um nome por registro: serve para filtrar/agrupar
    if t in ('numero', 'codigo') and dist >= 0.95 * len(vals) and len(vals) >= 0.9 * total: return 'Código (identifica o registro)'
    if t == 'data': return 'Data'
    if t == 'tempo': return 'Tempo (duração)'
    if t == 'valor': return 'Valor (R$)'
    if t in ('numero', 'codigo') and len(vals) >= 3 and dist >= 0.9 * len(vals): return 'Código'   # ⚖️ cada valor diferente (plaqueta, patrimônio, série): identifica, não se soma
    if t == 'numero': return 'Número'
    if t == 'frase': return 'Texto'
    if t in ('termo', 'codigo') and dist <= 0.5 * len(vals): return 'Categoria'   # curto e repete (2x ou mais em média)
    return 'Texto'

# ---------- R21 qual data é: rótulo > vizinhos > linha do tempo ----------
import unicodedata
SIGNIFICADOS = [   # (significado, raízes de palavras) — vocabulário geral da língua, não de um relatório
    ('Previsão / programada', ['prev', 'program', 'agend', 'prazo', 'venc', 'estimad']),
    ('Nascimento', ['nasc']),
    ('Competência / período', ['compet', 'referen', 'period']),
    ('Encerramento / baixa', ['baixa', 'encerr', 'fech', 'finaliz', 'saida']),
    ('Início do serviço', ['inici', 'comec', 'partida']),
    ('Fim do serviço / executado', ['exec', 'realiz', 'atendid']),
    ('Fim', ['final', 'fim', 'termin', 'conclu']),
    ('Abertura / pedido', ['abert', 'pedid', 'solicit', 'emiss', 'emitid', 'criad', 'criac', 'cadastr', 'registr', 'entrada', 'chamad']),
    ('Compra / nota', ['compra', 'nota', 'fatur', 'venda']),
]
SERVICO = ['funcion', 'tecnic', 'colabor', 'servic', 'executor', 'operador', 'mao']
def _tokens(t):
    t = unicodedata.normalize('NFKD', t).encode('ascii', 'ignore').decode().lower()
    return [x for x in re.split(r'[^a-z0-9]+', t) if len(x) >= 3]
def _bate(tokens, raizes):
    return any(tk.startswith(r) or (len(tk) <= 4 and r.startswith(tk)) for tk in tokens for r in raizes)   # só abreviação curta
def _significado(texto):
    tk = _tokens(texto)
    for sig, raizes in SIGNIFICADOS:
        if _bate(tk, raizes): return sig
    return None
def inferir_datas(gs, notas):
    for g in gs:
        nome = g['nome'] or ''
        sig = _significado(nome); conf, mot = 'alta', 'o rótulo diz "%s"' % nome
        if not sig:
            for v, _ in (g.get('viz_perto') or Counter()).most_common():
                sig = _significado(v)
                if sig: conf, mot = 'média', 'não tem rótulo próprio; o vizinho mais perto é "%s"' % v; break
        if sig == 'Fim':
            serv = any(_bate(_tokens(v), SERVICO) for v in (g.get('viz_todos') or {}))
            sig = 'Fim do serviço / executado' if serv else 'Encerramento / baixa'
            mot += ' (perto de quem fez o serviço)' if serv else ' (sem ninguém do serviço por perto: é o fim do registro)'
        if not sig:
            viz = [v.rstrip(':').strip() for v, _ in (g.get('viz_perto') or Counter()).most_common(1)]
            if viz: sig, conf, mot = 'Outra', 'média', 'nenhuma palavra de data conhecida; está junto de "%s" → data de %s' % (viz[0], viz[0])
        g['qual_data'] = {'sig': sig or '?', 'conf': conf if sig else 'baixa', 'mot': mot if sig else 'sem rótulo e sem vizinho: preciso que você diga'}
    # R21b ordem natural: Abertura → Compra → Início → Fim do serviço → Encerramento (Previsão fica de fora)
    ORDEM = {'Abertura / pedido': 0, 'Compra / nota': 1, 'Início do serviço': 2, 'Fim do serviço / executado': 3, 'Encerramento / baixa': 4}
    por_nome = {g['nome']: g for g in gs}
    for n in notas:                                                  # confere rótulo contra o tempo
        a, b = por_nome.get(n['antes']), por_nome.get(n['depois'])
        if not a or not b: continue
        sa, sb = a['qual_data']['sig'], b['qual_data']['sig']
        if sa in ORDEM and sb in ORDEM and ORDEM[sa] > ORDEM[sb]:
            for g in (a, b):
                g['qual_data']['conf'] = 'baixa'; g['qual_data']['mot'] += '; mas a ordem no tempo não bate (%s vem antes de %s)' % (n['antes'], n['depois'])
    sem = [g for g in gs if g['qual_data']['sig'] == '?']
    if len(gs) < 2 or not sem: return
    ordenaveis = [g for g in gs if g['qual_data']['sig'] not in ('Previsão / programada', 'Nascimento', 'Competência / período')]
    antes_de = Counter(); depois_de = Counter()
    for n in notas:
        if n['antes'] in por_nome and n['depois'] in por_nome:
            depois_de[n['depois']] += 1; antes_de[n['antes']] += 1
    usados = {g['qual_data']['sig'] for g in gs}
    def marca(g, sig, conf, mot): g['qual_data'].update(sig=sig, conf=conf, mot=mot); usados.add(sig)
    # R21c par por proximidade: duas sem rótulo quase sempre a minutos/horas uma da outra = início e fim do serviço
    pares = sorted((n for n in notas if por_nome.get(n['antes']) in sem and por_nome.get(n['depois']) in sem and n['seg'] <= 86400), key=lambda n: n['seg'])
    for n in pares:
        a, b = por_nome[n['antes']], por_nome[n['depois']]
        if a['qual_data']['sig'] != '?' or b['qual_data']['sig'] != '?' or 'Início do serviço' in usados: continue
        marca(a, 'Início do serviço', 'média', 'sem rótulo; anda junto com "%s" (diferença típica %s): é o começo do par' % (b['nome'], n['tipico']))
        marca(b, 'Fim do serviço / executado', 'média', 'sem rótulo; anda junto com "%s" (diferença típica %s): é o fim do par' % (a['nome'], n['tipico']))
    # pontas: a mais antiga é a abertura, a mais recente o encerramento
    pos = {g['nome']: depois_de[g['nome']] for g in ordenaveis}
    if pos:
        mn, mx = min(pos.values()), max(pos.values())
        for g in [g for g in ordenaveis if g['qual_data']['sig'] == '?']:
            if pos[g['nome']] == mn and 'Abertura / pedido' not in usados: marca(g, 'Abertura / pedido', 'média', 'sem rótulo; é a mais antiga de todas as datas do registro')
            elif pos[g['nome']] == mx and 'Encerramento / baixa' not in usados: marca(g, 'Encerramento / baixa', 'média', 'sem rótulo; é a mais recente de todas as datas do registro')
    # meio: entre a abertura e o início do serviço = compra/material; senão, perguntar
    ini = next((g for g in gs if g['qual_data']['sig'] == 'Início do serviço'), None)
    abe = next((g for g in gs if g['qual_data']['sig'] == 'Abertura / pedido'), None)
    for g in [g for g in ordenaveis if g['qual_data']['sig'] == '?']:
        dep_abe = any(n['antes'] == (abe and abe['nome']) and n['depois'] == g['nome'] for n in notas)
        ant_ini = any(n['antes'] == g['nome'] and n['depois'] == (ini and ini['nome']) for n in notas)
        if dep_abe and ant_ini: marca(g, 'Compra / nota', 'baixa', 'sem rótulo; fica entre a abertura e o início do serviço (compra de material?) — confira')
        else: g['qual_data'].update(mot='sem rótulo; fica no meio do processo e não deu para saber qual é: preciso que você diga')
