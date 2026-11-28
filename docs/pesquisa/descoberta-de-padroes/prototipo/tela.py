"""Gera a tela de teste das perguntas (HTML local) a partir do resultado da fórmula."""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import formula as F

PASTA, SAIDA = sys.argv[1], sys.argv[2]
ARQS = [('NAO_ATENDIDAS_R_ORDEM_SERVICO.csv', 'Ficha (uma OS em várias linhas)'),
        ('relatoriodetalhadas.csv', 'Agrupado por oficina e setor'),
        ('relatorioresumidas.csv', 'Tabela com cabeçalho repetido e deslocado'),
        ('CONCLUIDAS_R_ORDEM_SERVICO.csv', 'OS concluídas (ficha)'),
        ('1_vendas_loja.csv', 'Inventado: vendas com coluna faltando'),
        ('4_chamados_rotulo_na_celula.csv', 'Inventado: rótulo dentro da célula'),
        ('6_datas_sem_rotulo.csv', 'Inventado: sem cabeçalho'),
        ('7_mesmos_pedidos_em_ficha.csv', 'Inventado: os mesmos pedidos em ficha')]
import cruzar as C
SO = sys.argv[3:] if len(sys.argv) > 4 else None
if SO: ARQS = [(SO[i], SO[i + 1]) for i in range(0, len(SO), 2)]
from vista import vista
CRUZ = ['relatoriodetalhadas.csv', 'CONCLUIDAS_R_ORDEM_SERVICO.csv', 'relatorioresumidas.csv', 'NAO_ATENDIDAS_R_ORDEM_SERVICO.csv']
CRUZ2 = ['6_datas_sem_rotulo.csv', '7_mesmos_pedidos_em_ficha.csv']
if SO: CRUZ, CRUZ2 = [], []
NOMEARQ = dict(ARQS); NOMEARQ['CONCLUIDAS_R_ORDEM_SERVICO.csv'] = 'OS concluídas (ficha)'
LIN, RES = {}, {}
for nome in list(dict.fromkeys([n for n, _ in ARQS] + CRUZ + CRUZ2)):
    cam = os.path.join(PASTA, nome)
    if not os.path.exists(cam): cam = os.path.join(PASTA, '..', 'cegas', 'arq', nome)
    LIN[nome] = F.ler(cam)[0]; RES[nome] = F.montar(LIN[nome], cam); RES[nome]['cruz'] = {}
C.cruzar({n: RES[n] for n in CRUZ}); C.nomes_cruzados({n: RES[n] for n in CRUZ})
C.cruzar({n: RES[n] for n in CRUZ2}); C.nomes_cruzados({n: RES[n] for n in CRUZ2})
def ident(rr, reg):
    g = C.id_grupo(rr)
    if not g: return 'Registro %d' % (reg + 1)
    v = next((c[3] for c in g['cel'] if c[0] == reg), '')
    return ('%s %s' % (g['nome'] if '(sem nome)' not in g['nome'] else 'Registro', v)).strip()
def vistas(nome, r, g):
    out = []
    cels = [c for c in g['cel'] if c[1]]
    for c in [cels[i] for i in sorted({0, len(cels) // 2})] if cels else []:
        v = vista(LIN[nome], r, c[0], c[1], c[2]); v['ident'] = ident(r, c[0]); v['arq'] = NOMEARQ.get(nome, nome)
        d = F.para_data(c[3]); ex = []
        for o, ro in r['cruz'].get(c[0], []):
            iguais = [(x[1], x[2]) for h in RES[o]['grupos'] for x in h['cel'] if d and x[0] == ro and x[1] and F.para_data(x[3]) and F.para_data(x[3]).date() == d.date()]
            ve = vista(LIN[o], RES[o], ro, marcar=iguais); ve['ident'] = ident(RES[o], ro); ve['arq'] = NOMEARQ.get(o, o); ex.append(ve)
        v['extras'] = ex; out.append(v)
    return out
dados = []
for nome, desc in ARQS:
    r = RES[nome]
    ids = {e: 'g%d' % i for i, e in enumerate(r['ordem'])}
    # cabeçalho deslocado: sobra coluna cheia SEM rótulo e há rótulos SEM dado no mesmo cabeçalho
    desloc = set()                     # dados passam da última coluna do cabeçalho = cabeçalho desalinhado
    gl = next((x for x in r['gov_reg'] if x is not None), None)
    if gl is not None:
        ult_rot = max(j for j, c in enumerate(LIN[nome][gl]) if c)
        for e in r['ordem']:
            g = r['grupos_por_end'][e]
            if e[0] in ('cab', 'cab-sem') and e[-1] == 'reg' and g['preenchido'] > 0.5:
                cols = [c[2] - 1 for c in g['cel'] if c[1]]
                if cols and sum(1 for j in cols if j > ult_rot) > 0.5 * len(cols): desloc.add(e[1])
    grupos = []
    for e in r['ordem']:
        g = r['grupos_por_end'][e]
        if e[0] in ('cab', 'cab-sem') and e[1] in desloc and not g['ctx']:
            g['aviso'] = g.get('aviso') or 'o cabeçalho deste relatório parece deslocado em relação aos dados: confira se o nome bate com o conteúdo'
        vals = [c[3] for c in g['cel'] if c[1] is not None] or [c[3] for c in g['cel']]
        nc = g.get('nome_cruz')
        if nc: nc = dict(nc, arq=NOMEARQ.get(nc['arq'], nc['arq']))
        sem_nome = ('(sem nome)' in g['nome'] or ' · ' in g['nome']) and not nc   # o cruzamento deu o nome: não é mais dúvida
        qd = g.get('qual_data')
        if sem_nome and qd and qd['conf'] == 'alta' and qd['mot'].startswith('é igual a'):   # data sem nome resolvida pelo cruzamento
            nc = {'nome': qd['mot'].split('"')[1], 'arq': NOMEARQ.get(qd['mot'].split('do arquivo ')[1].split(' em ')[0], ''), 'pct': 100, 'n': int(qd['mot'].split(' de ')[1].split(' ')[0])}
            sem_nome = False
        gid_aqui = C.id_grupo(r)
        if sem_nome and gid_aqui is g:                                # identificador sem nome: usa o nome do identificador no outro arquivo
            for o, _ in [x for v in r['cruz'].values() for x in v][:1]:
                go = C.id_grupo(RES[o])
                if go and '(sem nome)' not in go['nome']:
                    nc = {'nome': go['nome'], 'arq': NOMEARQ.get(o, o), 'pct': 100, 'n': len(r['cruz'])}; sem_nome = False
        if g['ctx'] and len(set(vals)) == 1 and sem_nome:            # texto único do topo = informação geral do relatório, não coluna
            g['nome'] = 'Informação do relatório'; sem_nome = False
        duvida = sem_nome or bool(g['marcadas']) or bool(g.get('aviso')) or (qd is not None and qd['conf'] != 'alta')
        grupos.append({'id': ids[e], 'nome': g['nome'], 'sug': F.sugerir_tipo(g, r['registros']), 'tipo': F.nome_tipo(g['tipo_maioria']),
                       'pre': round(g['preenchido'] * 100), 'lista': g['lista'], 'ctx': g['ctx'], 'ex': list(dict.fromkeys(vals))[:6],
                       'distintos': len(set(vals)), 'aviso': g.get('aviso', ''), 'duvida': duvida,
                       'marc': [{'v': m['valor'], 'mot': m['motivo'], 'sug': m['sugestao'], 'reg': m['reg']} for m in g['marcadas'][:15]],
                       'nmarc': len(g['marcadas']), 'qd': qd, 'nc': nc, 'cod': g.get('codigo_de'), 'vistas': vistas(nome, r, g) if (duvida and not g['ctx']) else []})
    linhas = [{ids[e]: ' | '.join(v) for e, v in l.items() if e in ids} for l in r['tabela'][:40]]
    dados.append({'arquivo': nome, 'desc': desc, 'reg': r['registros'], 'como': r['como'], 'totais': len(r['totais']),
                  'notas': r['notas'], 'sujeira': r['colunas_sujeira'], 'grupos': grupos, 'linhas': linhas, 'datas': r['datas']})

html = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tela_modelo.html'), encoding='utf-8').read()
open(SAIDA, 'w', encoding='utf-8').write(html.replace('/*DADOS*/', 'const DADOS = ' + json.dumps(dados, ensure_ascii=False) + ';'))
print('ok', SAIDA, os.path.getsize(SAIDA) // 1024, 'KB')
