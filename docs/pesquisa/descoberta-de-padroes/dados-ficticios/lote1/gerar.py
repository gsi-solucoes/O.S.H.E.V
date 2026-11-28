"""Arquivos às cegas: estruturas que o protótipo nunca viu, de outros ramos.
Cada um traz a resposta certa (gabarito) ANTES de rodar o protótipo."""
import random, json, os, sys
random.seed(7)
OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True)
gab = {}
nomes = ['ANA PAULA SOUZA', 'BRUNO LIMA', 'CARLA DIAS', 'DIEGO MOURA', 'ELIS REGINA COSTA', 'FABIO NUNES']
cidades = ['CAMPINAS', 'SANTOS', 'SOROCABA', 'BAURU', 'MARILIA']
prods = ['CAFE 500G', 'ACUCAR 1KG', 'ARROZ 5KG', 'FEIJAO 1KG', 'OLEO 900ML', 'MACARRAO 500G']
def d(dia, h=None): return '%02d/11/2026' % dia + (' %02d:%02d' % (h, random.randint(0, 59)) if h is not None else '')
def rs(): return 'R$ %d,%02d' % (random.randint(5, 900), random.randint(0, 99))

# 1. tabela de vendas com ; , valores em R$, e algumas linhas SEM uma coluna (menos separadores)
L = ['Pedido;Data;Cliente;Cidade;Produto;Qtde;Total']
n1 = 60
for i in range(n1):
    cel = [str(9100 + i), d(random.randint(1, 28)), random.choice(nomes), random.choice(cidades), random.choice(prods), str(random.randint(1, 20)), rs()]
    if i % 9 == 4: del cel[3]                      # cidade some: a linha fica com uma célula a menos
    L.append(';'.join(cel))
open(OUT + '/1_vendas_loja.csv', 'w', encoding='utf-8').write('\n'.join(L))
gab['1_vendas_loja.csv'] = {'registros': n1, 'grupos_esperados': ['Pedido', 'Data', 'Cliente', 'Cidade', 'Produto', 'Qtde', 'Total'],
                           'pegadinha': '7 linhas sem a coluna Cidade: o resto não pode escorregar de grupo'}

# 2. ficha de alunos: rótulo EM CIMA do valor (não ao lado), blocos de tamanho variável (ocorrências)
L = []
n2 = 25
for i in range(n2):
    L += ['FICHA DO ALUNO,,,', 'Matrícula,Nome,Turma,Nascimento', '%d,%s,%s,%s' % (20260 + i, random.choice(nomes), random.choice(['6A', '7B', '8C']), '%02d/%02d/2013' % (random.randint(1, 28), random.randint(1, 12)))]
    k = random.randint(0, 3)
    if k:
        L.append('Ocorrência,Data,,')
        for _ in range(k): L.append('%s,%s,,' % (random.choice(['ATRASO', 'FALTA JUSTIFICADA', 'ESQUECEU MATERIAL']), d(random.randint(1, 28))))
    L.append(',,,')
open(OUT + '/2_ficha_alunos.csv', 'w', encoding='utf-8').write('\n'.join(L))
gab['2_ficha_alunos.csv'] = {'registros': n2, 'grupos_esperados': ['Matrícula', 'Nome', 'Turma', 'Nascimento', 'Ocorrência (lista)', 'Data da ocorrência (lista)'],
                             'pegadinha': 'rótulo em cima do valor; nº de ocorrências varia de 0 a 3 por aluno'}

# 3. agrupado por vendedor com subtotal, TAB como separador, horas de atendimento (duração)
L = ['RELATÓRIO DE ATENDIMENTOS\t\t\t', '']
n3 = 0
for v in nomes[:4]:
    L.append('Vendedor:\t%s\t\t' % v)
    L.append('Protocolo\tAbertura\tFechamento\tDuração')
    tot = 0
    for _ in range(random.randint(5, 12)):
        n3 += 1; dia = random.randint(1, 27); h = random.randint(8, 15)
        L.append('A-%05d\t%s\t%s\t%d:%02d' % (random.randint(10000, 99999), d(dia, h), d(dia, h + 2), random.randint(0, 3), random.randint(0, 59)))
        tot += 1
    L.append('Subtotal:\t%d\t\t' % tot)
    L.append('')
open(OUT + '/3_atendimentos_agrupado.tsv.csv', 'w', encoding='utf-8').write('\n'.join(L))
gab['3_atendimentos_agrupado.tsv.csv'] = {'registros': n3, 'grupos_esperados': ['Vendedor (contexto)', 'Protocolo', 'Abertura', 'Fechamento', 'Duração'],
                                         'pegadinha': 'subtotal no fim de cada grupo não é registro; Abertura antes de Fechamento'}

# 4. rótulo e valor NA MESMA célula ("CLIENTE: JOAO"), rótulos em MAIÚSCULAS
L = []
n4 = 30
for i in range(n4):
    L.append('CHAMADO: %d,ABERTO EM: %s' % (500 + i, d(random.randint(1, 28), 9)))
    L.append('CLIENTE: %s,CIDADE: %s' % (random.choice(nomes), random.choice(cidades)))
    L.append('DEFEITO: %s,' % random.choice(['NAO LIGA', 'TELA QUEBRADA', 'SEM SOM', 'BATERIA']))
open(OUT + '/4_chamados_rotulo_na_celula.csv', 'w', encoding='utf-8').write('\n'.join(L))
gab['4_chamados_rotulo_na_celula.csv'] = {'registros': n4, 'grupos_esperados': ['CHAMADO', 'ABERTO EM', 'CLIENTE', 'CIDADE', 'DEFEITO'],
                                          'pegadinha': 'rótulo e valor dentro da mesma célula, em maiúsculas'}

# 5. tabela SEM cabeçalho nenhum
L = []
n5 = 40
for i in range(n5):
    L.append('%s,%s,%s,%s' % (d(random.randint(1, 28)), 'NF%06d' % (330000 + i), random.choice(prods), rs()))
open(OUT + '/5_notas_sem_cabecalho.csv', 'w', encoding='utf-8').write('\n'.join(L))
gab['5_notas_sem_cabecalho.csv'] = {'registros': n5, 'grupos_esperados': ['Grupo sem nome: data', 'código NF', 'produto', 'valor'],
                                    'pegadinha': 'não há rótulo nenhum: tudo deve virar "sem nome" e ser perguntado'}

json.dump(gab, open(OUT + '/gabarito.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('gerados', len(gab))
