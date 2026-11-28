"""Teste das datas: o registro inteiro no arquivo da pergunta + o mesmo registro em todos os outros arquivos (R22)."""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import formula as F, cruzar as C
from vista import vista
P, SAIDA = sys.argv[1], sys.argv[2]
MARCUS = {'relatoriodetalhadas.csv': 'Relatório detalhado', 'CONCLUIDAS_R_ORDEM_SERVICO.csv': 'OS concluídas (ficha)',
          'relatorioresumidas.csv': 'Relatório resumido', 'NAO_ATENDIDAS_R_ORDEM_SERVICO.csv': 'OS não atendidas (ficha)'}
LIN, RES = {}, {}
for n in MARCUS:
    LIN[n] = F.ler(os.path.join(P, 'csv', n))[0]; RES[n] = F.montar(LIN[n], n)
C.cruzar(RES)
for n, d in [('1_vendas_loja.csv', 'Inventado: vendas'), ('6_datas_sem_rotulo.csv', 'Inventado: sem cabeçalho')]:
    LIN[n] = F.ler(os.path.join(P, 'cegas', 'arq', n))[0]; RES[n] = F.montar(LIN[n], n); RES[n]['cruz'] = {}; MARCUS[n] = d
CASOS = [('relatoriodetalhadas.csv', ['Dt. Execução', 'Dt. Pedido']), ('NAO_ATENDIDAS_R_ORDEM_SERVICO.csv', ['Data Final', 'Data Inicial']),
         ('relatorioresumidas.csv', ['Dt Programada']), ('1_vendas_loja.csv', ['Data']), ('6_datas_sem_rotulo.csv', ['Grupo 2 (sem nome)', 'Grupo 6 (sem nome)'])]
def ident(r, reg):
    g = C.id_grupo(r)
    if not g: return 'Registro %d' % (reg + 1)
    v = next((c[3] for c in g['cel'] if c[0] == reg), '')
    return ('%s %s' % (g['nome'] if '(sem nome)' not in g['nome'] else 'Registro', v)).strip()
qs = []
for arq, nomes in CASOS:
    r, L = RES[arq], LIN[arq]
    for nome in nomes:
        g = next(x for x in r['grupos'] if x['nome'] == nome)
        cels = [c for c in g['cel'] if c[1]]
        def contas(c):                                              # (datas iguais no mesmo dia, datas diferentes) nos outros arquivos
            d = F.para_data(c[3]); n, t = set(), set()
            for o, reg_o in r.get('cruz', {}).get(c[0], []):
                for h in RES[o]['grupos']:
                    for x in h['cel']:
                        dx = F.para_data(x[3]) if x[0] == reg_o and x[1] else None
                        if dx and d:
                            sig = h.get('qual_data', {}).get('sig', h['nome'])
                            (n if dx.date() == d.date() else t).add(sig) if isinstance(n, set) else None
            return len(n), len(t - n)
        def n_iguais(c): return contas(c)[0]
        cand = cels[:: max(1, len(cels) // 60)][:60]
        if r.get('cruz'):                                           # exemplos que desempatam: batem com UMA só data
            cand = sorted(cand, key=lambda c: (contas(c)[0] != 1, -contas(c)[1]))   # bate com 1 e tem MAIS datas diferentes
            escolha = cand[:3]
        else:
            escolha = [cels[i] for i in (0, len(cels) // 2, len(cels) - 1)]
        vs = []
        for c in escolha:
            v = vista(L, r, c[0], c[1], c[2]); v['ident'] = ident(r, c[0]); v['arq'] = MARCUS[arq]
            alvo_d = F.para_data(c[3]); extras = []
            for o, reg_o in r.get('cruz', {}).get(c[0], []):
                ro = RES[o]; iguais = []
                for h in ro['grupos']:
                    for x in h['cel']:
                        if x[0] == reg_o and x[1] and alvo_d and F.para_data(x[3]) and F.para_data(x[3]).date() == alvo_d.date(): iguais.append((x[1], x[2]))
                ve = vista(LIN[o], ro, reg_o, marcar=iguais); ve['ident'] = ident(ro, reg_o); ve['arq'] = MARCUS[o]; extras.append(ve)
            v['extras'] = extras; vs.append(v)
        qs.append({'arq': MARCUS[arq], 'grupo': nome, 'regra': g.get('qual_data', {}).get('sig'), 'vistas': vs})
html = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'teste_datas_modelo.html'), encoding='utf-8').read()
open(SAIDA, 'w', encoding='utf-8').write(html.replace('/*DADOS*/', 'const QS = ' + json.dumps(qs, ensure_ascii=False) + ';'))
print('ok', len(qs), 'perguntas', os.path.getsize(SAIDA) // 1024, 'KB')
