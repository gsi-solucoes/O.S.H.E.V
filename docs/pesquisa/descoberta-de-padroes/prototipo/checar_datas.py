import sys, os, json; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import formula as F, cruzar as C
pasta = sys.argv[1]; gab = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'gabarito_datas.json'), encoding='utf-8'))
ok = tot = 0
MARCUS = ['relatoriodetalhadas.csv', 'CONCLUIDAS_R_ORDEM_SERVICO.csv', 'relatorioresumidas.csv', 'NAO_ATENDIDAS_R_ORDEM_SERVICO.csv']
RM = {n: F.montar(F.ler(os.path.join(pasta, n))[0], n) for n in MARCUS}
C.cruzar(RM)                                       # R22: como o app fará quando a pessoa subir vários relatórios
for arq, esp in gab.items():
    cam = os.path.join(pasta, arq)
    if not os.path.exists(cam): cam = os.path.join(pasta, '..', 'cegas', 'arq', arq)
    r = RM[arq] if arq in RM else F.montar(F.ler(cam)[0], cam)
    gs = {g['nome']: g for g in r['grupos'] if 'qual_data' in g}
    print('==', arq)
    for nome, sig in esp.items():
        tot += 1; g = gs.get(nome)
        got = g['qual_data'] if g else None
        bom = got and got['sig'] == sig; ok += bool(bom)
        print('  %s %-18s esperado: %-28s achou: %s' % ('✅' if bom else '❌', nome, sig, got and '%s [%s] %s' % (got['sig'], got['conf'], got['mot'])))
    for n, g in gs.items():
        if n not in esp: print('     (outro grupo de data) %-14s → %s [%s]' % (n, g['qual_data']['sig'], g['qual_data']['conf']))
print('\n%d de %d datas certas' % (ok, tot))
