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


# ---------- etapa 7a: os mesmos dados de vendas em outros formatos (F-58) ----------
import json as _json, shutil as _shutil, subprocess as _sp, tempfile as _tmp, zipfile as _zf
from xml.sax.saxutils import escape as _esc
_ci = [dict(zip(CAB_V, r)) for r in vendas]


def _fixa_zip(caminho):
    """Regrava o zip (xlsx) com data fixa nas entradas: o mesmo arquivo a cada geração (CA-83)."""
    with _zf.ZipFile(caminho) as _a:
        _itens = [(i.filename, _a.read(i.filename)) for i in _a.infolist()]
    with _zf.ZipFile(caminho, "w", _zf.ZIP_DEFLATED) as _b:
        for _n, _d in _itens:
            if _n == "docProps/core.xml":
                import re as _re
                _d = _re.sub(rb"(<dcterms:(?:created|modified)[^>]*>)[^<]*", rb"\g<1>2026-01-01T00:00:00Z", _d)
            _zi = _zf.ZipInfo(_n, (2026, 1, 1, 0, 0, 0))
            _zi.compress_type = _zf.ZIP_DEFLATED
            _b.writestr(_zi, _d)


def _num(s):
    return float(s.replace(",", "."))


def _dt(s):
    return datetime.datetime.strptime(s, "%d/%m/%Y")


# JSON: lista de objetos (valores como no CSV, texto)
(D / "vendas.json").write_text(_json.dumps(_ci, ensure_ascii=False, indent=1), encoding="utf-8")
# XML: elementos repetidos <registro> dentro de <relatorio>
with open(D / "vendas.xml", "w", encoding="utf-8") as _f:
    _f.write('<?xml version="1.0" encoding="UTF-8"?>\n<relatorio>\n')
    for _r in _ci:
        _f.write("  <registro>" + "".join(f"<{_k}>{_esc(_v)}</{_k}>" for _k, _v in _r.items()) + "</registro>\n")
    _f.write("</relatorio>\n")
try:
    import openpyxl as _ox
    _wb = _ox.Workbook()
    _wb.properties.created = _wb.properties.modified = datetime.datetime(2026, 1, 1)   # reprodutível (CA-83)
    _ws = _wb.active
    _ws.title = "Vendas"
    _ws.append(CAB_V)
    for _r in vendas:
        _ws.append([_r[0], _dt(_r[1]), _r[2], _r[3], _r[4], _num(_r[5]), _r[6]])
    for _row in _ws.iter_rows(min_row=2, min_col=2, max_col=2):
        _row[0].number_format = "dd/mm/yyyy"
    _wb.save(D / "vendas.xlsx")
    _fixa_zip(D / "vendas.xlsx")
    # duas abas: Vendas + Chamados (cada aba vira um conjunto candidato)
    _ws2 = _wb.create_sheet("Chamados")
    _ws2.append(["Código", "Abertura", "Conclusão", "Categoria", "Responsável", "Situação"])
    for _r in chamados:
        _ws2.append(_r)
    _wb.save(D / "vendas_2abas.xlsx")
    _fixa_zip(D / "vendas_2abas.xlsx")
    # xls e ods pelo LibreOffice (se existir); sem ele, os testes desses formatos são pulados
    _so = _shutil.which("soffice") or "/usr/bin/soffice"
    # xls/ods carregam carimbo de data do LibreOffice: só se gera quando ainda não existem (reprodutível, CA-83)
    if pathlib.Path(_so).exists():
        for _fmt in [f for f in ("xls", "ods") if not (D / f"vendas.{f}").exists()]:
            _t = pathlib.Path(_tmp.mkdtemp())
            _sp.run([_so, "--headless", f"-env:UserInstallation=file://{_t}/p", "--convert-to", _fmt, "--outdir", str(_t), str(D / "vendas.xlsx")],
                    check=False, stdout=_sp.DEVNULL, stderr=_sp.DEVNULL, timeout=120)
            if (_t / f"vendas.{_fmt}").exists():
                _shutil.copy(_t / f"vendas.{_fmt}", D / f"vendas.{_fmt}")
            _shutil.rmtree(_t, ignore_errors=True)
    # zip com mistura: CSV + XLSX + JSON
    with _zf.ZipFile(D / "vendas_mistura.zip", "w", _zf.ZIP_DEFLATED) as _z:
        for _orig, _dest in (("chamados.csv", "chamados.csv"), ("vendas.xlsx", "vendas.xlsx"), ("vendas.json", "pasta/vendas.json")):
            _zi = _zf.ZipInfo(_dest, (2026, 1, 1, 0, 0, 0))
            _zi.compress_type = _zf.ZIP_DEFLATED
            _z.writestr(_zi, (D / _orig).read_bytes())
except ImportError:
    pass


# ---------- etapa 7b: PDFs de teste (F-64) ----------
try:
    from reportlab.lib.pagesizes import A4, landscape as _land
    from reportlab.pdfgen import canvas as _cv

    def _pdf_tabela(nome, cab, linhas, titulo, x0=(30, 90, 170, 300, 380, 470, 530), por_pagina=33):
        """Relatório de impressão: título, cabeçalho repetido em cada página, rodapé com número da página."""
        c = _cv.Canvas(str(D / nome), pagesize=_land(A4), invariant=1)
        w, h = _land(A4)
        pag = 0
        for ini in range(0, len(linhas), por_pagina):
            pag += 1
            c.setFont("Helvetica-Bold", 14)
            c.drawString(30, h - 30, titulo)
            c.setFont("Helvetica-Bold", 9)
            for x, t in zip(x0, cab):
                c.drawString(x, h - 55, t)
            c.setFont("Helvetica", 9)
            y = h - 72
            for lin in linhas[ini:ini + por_pagina]:
                for x, t in zip(x0, lin):
                    c.drawString(x, y, str(t))
                y -= 14
            c.setFont("Helvetica", 8)
            c.drawString(30, 20, f"Página {pag}")
            c.showPage()
        c.save()

    _pdf_tabela("vendas.pdf", CAB_V, vendas, "Relatório de vendas")
    # PDF que não é tabela (contrato): só parágrafos
    _c = _cv.Canvas(str(D / "contrato.pdf"), pagesize=A4, invariant=1)
    _c.setFont("Helvetica", 11)
    _y = 800
    for _t in ["CONTRATO DE PRESTAÇÃO DE SERVIÇOS", "", "Pelo presente instrumento particular, as partes abaixo",
               "qualificadas ajustam entre si o que segue, mediante as", "cláusulas e condições adiante estipuladas.", "",
               "Cláusula primeira. O objeto deste contrato é a prestação de", "serviços de consultoria, conforme proposta anexa.", "",
               "Cláusula segunda. O prazo de vigência é de doze meses."]:
        _c.drawString(60, _y, _t)
        _y -= 18
    _c.showPage()
    _c.save()
except ImportError:
    pass
