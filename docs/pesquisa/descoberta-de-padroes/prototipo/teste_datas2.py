"""Teste 2: o arquivo sem cabeçalho + o mesmo pedido em outro relatório com nomes; com quadro da linha do tempo."""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import formula as F, cruzar as C
from vista import vista
P, SAIDA = sys.argv[1], sys.argv[2]
A = os.path.join(P, 'cegas', 'arq')
NOMES = {'6_datas_sem_rotulo.csv': 'Relatório sem cabeçalho', '7_mesmos_pedidos_em_ficha.csv': 'Ficha do pedido'}
LIN = {n: F.ler(os.path.join(A, n))[0] for n in NOMES}; RES = {n: F.montar(LIN[n], n) for n in NOMES}
C.cruzar(RES)
r, L = RES['6_datas_sem_rotulo.csv'], LIN['6_datas_sem_rotulo.csv']
# nome conhecido de cada grupo (pelo outro relatório), para escrever a linha do tempo
apelido = {}
for g in r['grupos']:
    m = g.get('qual_data', {}).get('mot', '')
    apelido[g['nome']] = ('a coluna que é igual a "%s" na ficha' % m.split('"')[1]) if m.startswith('é igual a') else 'outra coluna sem nome (%s)' % g['nome'].replace(' (sem nome)', '')
def ident(rr, reg):
    g = C.id_grupo(rr); v = next((c[3] for c in g['cel'] if c[0] == reg), '') if g else ''
    return ('%s %s' % (g['nome'] if g and '(sem nome)' not in g['nome'] else 'Registro', v)).strip()
qs = []
for nome in ['Grupo 2 (sem nome)', 'Grupo 3 (sem nome)', 'Grupo 4 (sem nome)', 'Grupo 5 (sem nome)', 'Grupo 6 (sem nome)']:
    g = next(x for x in r['grupos'] if x['nome'] == nome)
    cels = [c for c in g['cel'] if c[1]][:3]
    vs = []
    for c in cels:
        v = vista(L, r, c[0], c[1], c[2]); v['ident'] = ident(r, c[0]); v['arq'] = NOMES['6_datas_sem_rotulo.csv']
        d = F.para_data(c[3]); ex = []
        for o, ro in r['cruz'].get(c[0], []):
            iguais = [(x[1], x[2]) for h in RES[o]['grupos'] for x in h['cel'] if x[0] == ro and x[1] and F.para_data(x[3]) and d and F.para_data(x[3]) == d]
            ve = vista(LIN[o], RES[o], ro, marcar=iguais); ve['ident'] = ident(RES[o], ro); ve['arq'] = NOMES[o]; ex.append(ve)
        v['extras'] = ex; vs.append(v)
    tempo = []
    for n in r['datas']:
        if n['antes'] == nome: tempo.append('Vem ANTES de %s (diferença típica %s)' % (apelido[n['depois']], n['tipico']))
        if n['depois'] == nome: tempo.append('Vem DEPOIS de %s (diferença típica %s)' % (apelido[n['antes']], n['tipico']))
    mot = g['qual_data']['mot']
    if mot.startswith('sem rótulo; anda junto'):
        par = mot.split('"')[1]; dif = mot.split('diferença típica ')[1].split(')')[0]
        papel = 'o INÍCIO' if 'começo' in mot else 'o FIM'
        tempo.append('💡 Conclusão: esta coluna e a "%s" andam sempre juntas, a ~%s uma da outra. Parecem o início e o fim de um mesmo serviço; esta seria %s. Confere?' % (par.replace(' (sem nome)', ''), dif, papel))
    qs.append({'arq': NOMES['6_datas_sem_rotulo.csv'], 'grupo': nome, 'regra': g['qual_data']['sig'], 'vistas': vs, 'tempo': tempo})
html = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'teste_datas_modelo.html'), encoding='utf-8').read()
open(SAIDA, 'w', encoding='utf-8').write(html.replace('/*DADOS*/', 'const QS = ' + json.dumps(qs, ensure_ascii=False) + ';').replace('<h1>Teste das datas: qual data é?</h1>', '<h1>Teste das datas 2: sem cabeçalho, mas com o outro relatório junto</h1>'))
print('ok', len(qs))
