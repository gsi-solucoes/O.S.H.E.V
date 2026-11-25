#!/usr/bin/env python3
"""Gera dados FICTICIOS de teste, com semente fixa (CA-83). Saida: tests/dados/."""
import csv, random, datetime, pathlib

D = pathlib.Path(__file__).parent / "dados"
D.mkdir(exist_ok=True)
rnd = random.Random(20261125)

CLIENTES = ["Alfa Comercial", "Beta Distribuidora", "Gama Papelaria", "Delta Moveis", "Epsilon Tecidos",
            "Zeta Ferragens", "Eta Livraria", "Theta Brinquedos", "Iota Cosmeticos", "Kappa Calcados"]
REGIOES = ["Norte", "Sul", "Leste", "Oeste", "Centro"]
VENDEDORES = ["Ana Teste", "Bruno Teste", "Carla Teste", "Diego Teste", "Elisa Teste"]
SIT_V = ["Entregue", "Pendente", "Cancelado", "Em transporte"]
CATEG = ["Rede", "Impressora", "Acesso", "Sistema", "Equipamento"]
RESP = ["Fulano Teste", "Sicrano Teste", "Beltrano Teste", "Ciclano Teste"]
SIT_C = ["Concluido", "Aberto", "Em andamento"]


def grava(nome, cab, linhas, enc="utf-8"):
    with open(D / nome, "w", newline="", encoding=enc) as f:
        w = csv.writer(f, delimiter=";", lineterminator="\r\n")
        w.writerow(cab)
        w.writerows(linhas)


base = datetime.datetime(2026, 1, 1)
vendas = []
for i in range(1, 501):
    d = base + datetime.timedelta(days=rnd.randint(0, 330))
    vendas.append([f"V{i:05d}", d.strftime("%d/%m/%Y"), rnd.choice(CLIENTES), rnd.choice(REGIOES),
                   rnd.choice(VENDEDORES), f"{rnd.randint(1000, 250000) / 100:.2f}".replace(".", ","),
                   rnd.choice(SIT_V)])
CAB_V = ["Código", "Data", "Cliente", "Região", "Vendedor", "Valor", "Situação"]
grava("vendas.csv", CAB_V, vendas)
# copia Windows-1252 (acentos viram bytes cp1252)
grava("vendas_cp1252.csv", CAB_V, vendas, enc="cp1252")

chamados = []
for i in range(1, 301):
    a = base + datetime.timedelta(days=rnd.randint(0, 330), hours=rnd.randint(7, 18), minutes=rnd.randint(0, 59))
    sit = rnd.choice(SIT_C)
    if sit == "Concluido" or rnd.random() < 0.1:
        c = a + datetime.timedelta(minutes=rnd.choice([20, 45, 90, 200, 700, 1500, 3000, 9000, 14000]) + rnd.randint(0, 15))
        cs = c.strftime("%d/%m/%Y %H:%M")
    else:
        cs = ""
    chamados.append([f"C{i:05d}", a.strftime("%d/%m/%Y %H:%M"), cs, rnd.choice(CATEG), rnd.choice(RESP), sit])
grava("chamados.csv", ["Código", "Abertura", "Conclusão", "Categoria", "Responsável", "Situação"], chamados)

# parte 2: codigos que cruzam com vendas (V00001..V00200) + alguns inexistentes; alguns vazios
p2 = []
for i in range(1, 201):
    pr = rnd.choice(["Alta", "Média", "Baixa"])
    if i % 7 == 0:
        pr = ""
    p2.append([f"V{i:05d}", pr])
p2.append(["V90001", "Alta"])
grava("vendas_parte2.csv", ["Código", "Prioridade"], p2)
