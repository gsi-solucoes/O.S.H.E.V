"""Suite da etapa 4 (CA-40 a CA-50). Escrita SO a partir da especificacao v1.4 (secoes 0.5 e 4).
Excel lido com openpyxl; blocos localizados por TEXTO de celula (nunca por posicao fixa alem de A1/A2).
Oraculos em Python sobre tests/dados/. CA-40 e CA-44 ficam adiados (etapa 6)."""
import re, statistics, collections, datetime, zipfile
import pytest
from openpyxl import load_workbook
from test_etapa1 import le_csv, enviar, mapear_se_preciso, abrir_painel
from test_etapa2 import (dlg, abrir_janela_r51, marcar, confirmar, fechar_seu_painel, pos, JANELA, br)
from test_etapa3 import pedir, responder

VENDAS = le_csv("vendas.csv")
CHAMADOS = le_csv("chamados.csv")
CAB_V = list(VENDAS[0].keys())
FORMATO_CONTAGEM = "#,##0"
FORMATO_DECIMAL = "#,##0.00"


# ---------- geracao e leitura do Excel ----------
def valor(r):
    return float(r["Valor"].replace(",", "."))


def dmy(s):
    return datetime.datetime.strptime(s, "%d/%m/%Y").date()


def verifica_sem_formula_nem_macro(caminho):
    """CA-47: nenhuma celula com data_type 'f' e nenhum xl/vbaProject.bin."""
    with zipfile.ZipFile(caminho) as z:
        assert "xl/vbaProject.bin" not in z.namelist(), "macro dentro do .xlsx"
    wb = load_workbook(caminho)
    for ws in wb.worksheets:
        for row in ws.iter_rows():
            for c in row:
                assert c.data_type != "f", f"formula em {ws.title}!{c.coordinate}: {c.value!r}"
    return wb


def escolhe_formato(page, formato):
    if formato:
        page.get_by_role("combobox", name="Formato").select_option(label=formato)


def gerar(page, tmp_path, formato=None):
    """Clica em Gerar Excel (Formato opcional) e devolve o workbook (ja verificado: sem formula/macro)."""
    abrir_painel(page)
    escolhe_formato(page, formato)
    with page.expect_download() as d:
        page.get_by_role("button", name="Gerar Excel").click()
    destino = tmp_path / d.value.suggested_filename
    d.value.save_as(str(destino))
    return verifica_sem_formula_nem_macro(destino)


def gerar_varios(page, tmp_path, formato):
    """Formato com varios arquivos: junta todos os downloads disparados pelo clique."""
    abrir_painel(page)
    escolhe_formato(page, formato)
    baixados = []
    page.on("download", lambda d: baixados.append(d))
    page.get_by_role("button", name="Gerar Excel").click()
    page.wait_for_timeout(3000)
    wbs = []
    for i, d in enumerate(baixados):
        destino = tmp_path / f"{i}_{d.suggested_filename}"
        d.save_as(str(destino))
        wbs.append(verifica_sem_formula_nem_macro(destino))
    return wbs


def vazio(v):
    return v is None or (isinstance(v, str) and not v.strip())


def parse_painel(ws):
    """Divide a planilha de painel (a partir da linha 4) em grupos separados por linha vazia na coluna A.
    Devolve {'blocos': [{'titulo','linhas':[[celulas]],'meus':bool}], 'registros': {'cab': [...], 'linhas': [[...]]},
    'meus_antes': titulo ou None}. 'Meus indicadores' e ancora colada ao 1o bloco de pedido; 'Registros' e a ultima secao."""
    grupos, atual = [], []
    for row in ws.iter_rows(min_row=4):
        a = row[0].value
        if vazio(a):
            if atual:
                grupos.append(atual)
            atual = []
        else:
            atual.append(list(row))
    if atual:
        grupos.append(atual)
    out = {"blocos": [], "registros": None}
    for g in grupos:
        meus = False
        if g[0][0].value == "Meus indicadores":
            meus, g = True, g[1:]
            assert g, "'Meus indicadores' sem bloco logo abaixo"
        if g[0][0].value == "Registros" and g is grupos[-1] and len(g) >= 2 and not meus:
            out["registros"] = {"cab": [c.value for c in g[1] if not vazio(c.value)], "linhas": g[2:]}
            continue
        out["blocos"].append({"titulo": g[0][0].value, "linhas": g[1:], "meus": meus})
    return out


def bloco_de(p, titulo):
    achados = [b for b in p["blocos"] if b["titulo"] == titulo]
    assert achados, f"bloco ausente na planilha: {titulo!r}; ha {[b['titulo'] for b in p['blocos']]}"
    return achados[0]


def cartao(b):
    """{rotulo: celula-valor} do cartao (linha 2 = rotulos, linha 3 = valores)."""
    rot, val = b["linhas"][0], b["linhas"][1]
    return {c.value: val[i] for i, c in enumerate(rot) if not vazio(c.value)}


def tabela(b, a_partir=0):
    """Linhas Categoria/Valor/Barra: devolve [(cat, celula_valor, celula_barra)] depois do cabecalho."""
    lin = b["linhas"][a_partir:]
    assert [c.value for c in lin[0][:3]] == ["Categoria", "Valor", "Barra"], [c.value for c in lin[0][:3]]
    return [(r[0].value, r[1], r[2] if len(r) > 2 else None) for r in lin[1:]]


def capa(wb, rotulo):
    ws = wb["Capa"]
    for row in ws.iter_rows():
        if row[0].value == rotulo:
            return row[1].value
    pytest.fail(f"rotulo {rotulo!r} ausente na Capa")


# ---------- regras de formato ----------
def barras_esperadas(ns):
    """Regra 0.5: round(20*|n|/maior|n|) '█', minimo 1 se n != 0, vazia se n == 0."""
    mx = max((abs(n) for n in ns), default=0)
    out = []
    for n in ns:
        if n == 0 or mx == 0:
            out.append("")
        else:
            k = int(20 * abs(n) / mx + 0.5)
            out.append("█" * max(1, k))
    return out


def confere_barras(linhas_tab, ns):
    esp = barras_esperadas(ns)
    for (cat, _, barra), e in zip(linhas_tab, esp):
        got = "" if barra is None or barra.value is None else barra.value
        assert got == e, f"Barra de {cat!r}: {got!r} != {e!r}"


def confere_contagem(c, n):
    assert isinstance(c.value, int) and not isinstance(c.value, bool), f"contagem deve ser inteiro: {c.value!r}"
    assert c.value == n, (c.value, n)
    assert c.number_format == FORMATO_CONTAGEM, c.number_format


def confere_decimal(c, x):
    assert isinstance(c.value, (int, float)) and not isinstance(c.value, bool), f"decimal deve ser numero: {c.value!r}"
    assert abs(c.value - round(x, 2)) <= 0.006, (c.value, x)
    assert c.number_format == FORMATO_DECIMAL, c.number_format


def confere_percentual_texto(c, pct):
    assert isinstance(c.value, str), f"percentual deve ser texto: {c.value!r}"
    assert re.fullmatch(r"\d+,\d%", c.value), c.value
    assert abs(float(c.value[:-1].replace(",", ".")) - pct) <= 0.051, (c.value, pct)


def confere_tabela_contagem(tab, esperado: dict, ordenado=True):
    got = {cat: c for cat, c, _ in tab}
    assert set(got) == set(esperado), (sorted(map(str, got)), sorted(map(str, esperado)))
    for cat, n in esperado.items():
        confere_contagem(got[cat], n)
    if ordenado:
        corpo = [c.value for cat, c, _ in tab if cat != "Outros"]
        assert corpo == sorted(corpo, reverse=True), "linhas fora de ordem decrescente"
    confere_barras(tab, [c.value for _, c, _ in tab])


def confere_tabela_soma(tab, esperado: dict):
    got = {cat: c for cat, c, _ in tab}
    assert set(got) == set(esperado), (sorted(map(str, got)), sorted(map(str, esperado)))
    for cat, x in esperado.items():
        confere_decimal(got[cat], x)
    confere_barras(tab, [c.value for _, c, _ in tab])


# ---------- oraculos ----------
def conta_por(regs, campo):
    return dict(collections.Counter(r[campo] for r in regs))


def soma_por(regs, campo):
    d = collections.defaultdict(float)
    for r in regs:
        d[r[campo]] += valor(r)
    return dict(d)


def titulos_blocos_excel(p):
    return [b["titulo"] for b in p["blocos"]]


# ---------- fluxo do CA-41 (reaproveitado por CA-47 e CA-50) ----------
ESCOLHA_41 = ["Total de registros", "Valor (soma, média e mediana)", "Por Cliente", "Valor por Região", "% por Situação"]


def fluxo_41(page, tmp_path):
    abrir_janela_r51(page, "vendas.csv")
    marcar(page, ESCOLHA_41)
    confirmar(page)
    fechar_seu_painel(page)
    return gerar(page, tmp_path)


def test_CA41_painel_igual_a_tela(page, tmp_path):
    wb = fluxo_41(page, tmp_path)
    assert wb.sheetnames[:3] == ["Capa", "Como ler este relatório", "Painel"], wb.sheetnames
    ws = wb["Painel"]
    assert ws["A1"].value == "Painel"
    assert ws["A2"].value == "Relatório: vendas"
    assert vazio(ws["A3"].value)
    p = parse_painel(ws)
    assert p["registros"] is not None, "secao Registros ausente"
    titulos = titulos_blocos_excel(p)
    assert sorted(titulos) == sorted(ESCOLHA_41), titulos
    # ordem dos titulos = ordem dos headings na tela
    na_tela = sorted(ESCOLHA_41, key=lambda n: pos(page, n))
    assert titulos == na_tela, (titulos, na_tela)

    n = len(VENDAS)
    # Total de registros
    b = bloco_de(p, "Total de registros")
    assert [c.value for c in b["linhas"][0] if not vazio(c.value)] == ["Registros"]
    confere_contagem(cartao(b)["Registros"], n)
    # Valor (soma, media, mediana)
    vals = [valor(r) for r in VENDAS]
    b = bloco_de(p, "Valor (soma, média e mediana)")
    c = cartao(b)
    assert list(c) == ["Soma", "Média", "Mediana"], list(c)
    confere_decimal(c["Soma"], sum(vals))
    confere_decimal(c["Média"], statistics.mean(vals))
    confere_decimal(c["Mediana"], statistics.median(vals))
    # Por Cliente (contagem)
    tab = tabela(bloco_de(p, "Por Cliente"))
    confere_tabela_contagem(tab, conta_por(VENDAS, "Cliente"))
    # Valor por Regiao (soma)
    tab = tabela(bloco_de(p, "Valor por Região"))
    confere_tabela_soma(tab, soma_por(VENDAS, "Região"))
    # % por Situacao: Valor = percentual (texto), Barra usa a contagem
    tab = tabela(bloco_de(p, "% por Situação"))
    cont = conta_por(VENDAS, "Situação")
    assert {cat for cat, _, _ in tab} == set(cont)
    for cat, cel, _ in tab:
        confere_percentual_texto(cel, 100 * cont[cat] / n)
    ordem = [cont[cat] for cat, _, _ in tab]
    confere_barras(tab, ordem)


def test_CA41_numeros_aparecem_na_tela_como_no_excel(page, tmp_path):
    """O total e a soma exibidos na tela (pt-BR) batem com o Excel."""
    wb = fluxo_41(page, tmp_path)
    p = parse_painel(wb["Painel"])
    corpo = re.sub(r"\s+", " ", page.inner_text("body"))
    total = cartao(bloco_de(p, "Total de registros"))["Registros"].value
    assert br(total, 0) in corpo or str(total) in corpo
    soma = cartao(bloco_de(p, "Valor (soma, média e mediana)"))["Soma"].value
    assert br(soma) in corpo, f"soma do Excel ({br(soma)}) nao aparece na tela"


def test_CA42_periodo_de_ate_na_capa_e_no_painel(page, tmp_path):
    abrir_janela_r51(page, "vendas.csv")
    marcar(page, ["Total de registros"])
    confirmar(page)
    fechar_seu_painel(page)
    abrir_painel(page)
    page.get_by_text("Filtros", exact=True).locator("visible=true").first.click()
    page.get_by_role("combobox", name="Período").select_option(label="De–até")
    page.get_by_label("De", exact=True).fill("2026-10-01")
    page.get_by_label("Até", exact=True).fill("2026-10-31")
    page.wait_for_timeout(500)
    wb = gerar(page, tmp_path)
    esperado = sum(1 for r in VENDAS if r["Data"].endswith("/10/2026"))
    assert 0 < esperado < len(VENDAS)
    assert capa(wb, "Período") == "Registros de 01/10/2026 a 31/10/2026"
    assert capa(wb, "Filtros") == "de 01/10/2026 a 31/10/2026"
    gerado = capa(wb, "Gerado em")
    assert isinstance(gerado, str) and re.fullmatch(r"\d{2}/\d{2}/\d{4} \d{2}:\d{2}", gerado), gerado
    p = parse_painel(wb["Painel"])
    confere_contagem(cartao(bloco_de(p, "Total de registros"))["Registros"], esperado)
    assert len(p["registros"]["linhas"]) == esperado


def csv_tempo(tmp_path, nome, duracoes_min):
    """CSV com 2 campos de data (Abertura, Conclusão) e duracoes dadas em minutos."""
    linhas = ["Código;Abertura;Conclusão;Categoria;Situação"]
    base = datetime.datetime(2026, 3, 1, 8, 0)
    for i, m in enumerate(duracoes_min):
        a = base + datetime.timedelta(days=i * 2)
        c = a + datetime.timedelta(minutes=m)
        linhas.append(f"T{i+1:03d};{a:%d/%m/%Y %H:%M};{c:%d/%m/%Y %H:%M};{'Rede' if i % 2 else 'Acesso'};Concluido")
    arq = tmp_path / nome
    arq.write_text("\r\n".join(linhas) + "\r\n", encoding="utf-8")
    return arq


@pytest.mark.parametrize("duracoes,esperado", [
    ([20, 30, 40, 48, 48, 48, 48, 60, 90, 120], "48 min"),                    # mediana 0,8 h
    ([600, 900, 1200, 1560, 1560, 1560, 1560, 2000, 3000, 4000], "26 h 00 min"),  # mediana 26 h
], ids=["mediana_48_min", "mediana_26_h"])
def test_CA43_tempo_entre_datas_mediana_em_texto(page, tmp_path, duracoes, esperado):
    arq = csv_tempo(tmp_path, "tempo.csv", duracoes)
    enviar(page, arq)
    mapear_se_preciso(page)
    dlg(page, JANELA).wait_for(state="visible")
    marcar(page, ["Tempo entre duas datas"])
    confirmar(page)
    fechar_seu_painel(page)
    wb = gerar(page, tmp_path)
    p = parse_painel(wb["Painel"])
    b = bloco_de(p, "Tempo entre duas datas")
    rot = [c.value for c in b["linhas"][0]]
    assert rot[:4] and rot[0] == "De" and rot[1] == "Até" and rot[2] == "Mediana", rot
    assert str(rot[3]).startswith("Dentro de ") and str(rot[3]).endswith(" h"), rot
    med = b["linhas"][1][2]
    assert med.value == esperado, med.value
    assert med.data_type == "s" and isinstance(med.value, str), "duracao deve ser texto"
    # faixas logo abaixo: Categoria | Valor (contagem), somando todos os registros com duracao
    faixas = tabela(b, a_partir=2) if [c.value for c in b["linhas"][2][:2]] == ["Categoria", "Valor"] else None
    assert faixas, "tabela de faixas ausente logo abaixo do cartao"
    assert sum(c.value for _, c, _ in faixas) == len(duracoes)


@pytest.mark.skip(reason="CA-40 adiado para a etapa 6 (painel com 2 abas)")
def test_CA40_duas_abas_do_painel_viram_duas_planilhas():
    pass


@pytest.mark.skip(reason="CA-44 adiado para a etapa 6 (aba escondida)")
def test_CA44_aba_escondida_nao_sai_no_excel():
    pass


def carrega_dois(page):
    abrir_janela_r51(page, "vendas.csv")
    marcar(page, ["Total de registros", "Por Cliente"])
    confirmar(page)
    fechar_seu_painel(page)
    enviar(page, "chamados.csv")
    mapear_se_preciso(page)
    dlg(page, JANELA).wait_for(state="visible")
    marcar(page, ["Total de registros", "% por Situação"])
    confirmar(page)
    fechar_seu_painel(page)


def test_CA45_tudo_numa_planilha(page, tmp_path):
    carrega_dois(page)
    wb = gerar(page, tmp_path, "Tudo numa planilha")
    assert wb.sheetnames == ["Capa", "Como ler este relatório", "Painel - vendas", "Painel - chamados", "Tudo"], wb.sheetnames
    pv, pc = wb["Painel - vendas"], wb["Painel - chamados"]
    assert pv["A2"].value == "Relatório: vendas"
    assert pc["A2"].value == "Relatório: chamados"
    tv = titulos_blocos_excel(parse_painel(pv))
    tc = titulos_blocos_excel(parse_painel(pc))
    assert sorted(tv) == ["Por Cliente", "Total de registros"], tv
    assert sorted(tc) == ["% por Situação", "Total de registros"], tc
    confere_contagem(cartao(bloco_de(parse_painel(pv), "Total de registros"))["Registros"], len(VENDAS))
    confere_contagem(cartao(bloco_de(parse_painel(pc), "Total de registros"))["Registros"], len(CHAMADOS))


def test_CA45_arquivos_separados(page, tmp_path):
    carrega_dois(page)
    wbs = gerar_varios(page, tmp_path, "Arquivos separados")
    assert len(wbs) == 2, f"esperados 2 arquivos, vieram {len(wbs)}"
    por_conjunto = {}
    for wb in wbs:
        assert "Painel" in wb.sheetnames, wb.sheetnames
        assert not any(n.startswith("Painel -") for n in wb.sheetnames), wb.sheetnames
        ws = wb["Painel"]
        por_conjunto[ws["A2"].value] = sorted(titulos_blocos_excel(parse_painel(ws)))
    assert por_conjunto == {"Relatório: vendas": ["Por Cliente", "Total de registros"],
                            "Relatório: chamados": ["% por Situação", "Total de registros"]}, por_conjunto


def test_CA45_uma_planilha_por_relatorio_ordem(page, tmp_path):
    """Formato padrao com 2 conjuntos: painel de cada conjunto antes das planilhas de registros."""
    carrega_dois(page)
    wb = gerar(page, tmp_path, "Uma planilha por relatório")
    n = wb.sheetnames
    assert n[:4] == ["Capa", "Como ler este relatório", "Painel - vendas", "Painel - chamados"], n
    assert "vendas" in n[4:] and "chamados" in n[4:], n


def test_CA46_painel_padrao_sem_escolha(page, tmp_path):
    abrir_janela_r51(page, "vendas.csv")
    dlg(page, JANELA).get_by_role("button", name="Cancelar", exact=True).click()
    page.wait_for_timeout(300)
    wb = gerar(page, tmp_path)
    assert "Como ler este relatório" not in wb.sheetnames
    assert wb.sheetnames[:2] == ["Capa", "Painel"], wb.sheetnames
    p = parse_painel(wb["Painel"])
    assert p["registros"] is not None
    tit = titulos_blocos_excel(p)
    assert tit[0] == "Números", tit
    assert not any("repetidos" in t.lower() for t in tit), tit
    cats = [t for t in tit if t.startswith("Por ") and not t.startswith("Por mês")]
    meses = [t for t in tit if t.startswith("Por mês (")]
    assert 1 <= len(cats) <= 3 and len(meses) == 1, tit
    assert tit == ["Números"] + cats + meses, tit
    # categorias aparecem na tela com o mesmo titulo
    for t in cats + meses:
        assert page.get_by_text(t, exact=True).count() >= 1, f"{t!r} nao aparece na tela"
    # Numeros: Total de registros | Mais antigo | Mais novo
    c = cartao(bloco_de(p, "Números"))
    rotulos = list(c)
    assert rotulos[0] == "Total de registros" and rotulos[1].startswith("Mais antigo") and rotulos[2].startswith("Mais novo"), rotulos
    confere_contagem(c[rotulos[0]], len(VENDAS))
    ds = [dmy(r["Data"]) for r in VENDAS]
    assert c[rotulos[1]].value == min(ds).strftime("%d/%m/%Y") and isinstance(c[rotulos[1]].value, str)
    assert c[rotulos[2]].value == max(ds).strftime("%d/%m/%Y") and isinstance(c[rotulos[2]].value, str)
    # Por <categoria>: 8 maiores, sem Outros
    for t in cats:
        campo = t[len("Por "):]
        assert campo in CAB_V, campo
        tab = tabela(bloco_de(p, t))
        assert len(tab) <= 8 and "Outros" not in [x for x, _, _ in tab], tab
        oraculo = sorted(conta_por(VENDAS, campo).values(), reverse=True)[:8]
        for _, cel, _ in tab:
            assert isinstance(cel.value, int) and cel.number_format == FORMATO_CONTAGEM
        assert sorted((cel.value for _, cel, _ in tab), reverse=True) == oraculo
        confere_barras(tab, [cel.value for _, cel, _ in tab])
    # Por mes: contagem por mm/aaaa (ultimos 12 meses)
    meses_dados = collections.Counter(dmy(r["Data"]).strftime("%m/%Y") for r in VENDAS)
    assert len(meses_dados) <= 12
    tab = tabela(bloco_de(p, meses[0]))
    got = {cat: cel.value for cat, cel, _ in tab}
    assert got == dict(meses_dados), (got, dict(meses_dados))
    confere_barras(tab, [cel.value for _, cel, _ in tab])


def test_CA47_sem_formula_e_sem_macro(page, tmp_path):
    abrir_janela_r51(page, "vendas.csv")
    marcar(page, ESCOLHA_41)
    confirmar(page)
    fechar_seu_painel(page)
    abrir_painel(page)
    with page.expect_download() as d:
        page.get_by_role("button", name="Gerar Excel").click()
    destino = tmp_path / d.value.suggested_filename
    d.value.save_as(str(destino))
    assert destino.suffix == ".xlsx"
    verifica_sem_formula_nem_macro(destino)  # (todos os outros testes tambem passam por aqui via gerar())


def test_CA48_meus_indicadores_entre_blocos_e_registros(page, tmp_path):
    abrir_janela_r51(page, "vendas.csv")
    marcar(page, ["Total de registros", "Por Cliente"])
    confirmar(page)
    fechar_seu_painel(page)
    abrir_painel(page)
    pedir(page, "soma do valor por cliente")
    responder(page, "Sim")
    headings = [re.sub(r"\s+", " ", h).strip() for h in page.get_by_role("heading").all_inner_texts()]
    if "Meus indicadores" in headings:
        titulo = headings[headings.index("Meus indicadores") + 1]
    else:
        titulo = headings[-1]
    wb = gerar(page, tmp_path)
    ws = wb["Painel"]
    linhas_a = [ws.cell(row=i, column=1).value for i in range(1, ws.max_row + 1)]
    assert linhas_a.count("Meus indicadores") == 1, "ancora 'Meus indicadores' deve existir uma vez"
    r_meus = linhas_a.index("Meus indicadores") + 1
    r_ult = max(i + 1 for i, v in enumerate(linhas_a) if v == "Registros")
    r_cli = linhas_a.index("Por Cliente") + 1
    r_tot = linhas_a.index("Total de registros") + 1
    assert max(r_cli, r_tot) < r_meus < r_ult, (r_cli, r_tot, r_meus, r_ult)
    assert ws.cell(row=r_meus + 1, column=1).value == titulo, (ws.cell(row=r_meus + 1, column=1).value, titulo)
    p = parse_painel(ws)
    b = [b for b in p["blocos"] if b["meus"]]
    assert len(b) == 1 and b[0]["titulo"] == titulo
    confere_tabela_soma(tabela(b[0]), soma_por(VENDAS, "Cliente"))


def tabela_da_tela(page):
    """(cabecalho, linhas de texto) da tabela de registros da tela."""
    t = page.locator("table:visible").filter(has_text="Código").first
    t.wait_for(state="visible")
    cab = [re.sub(r"\s+", " ", x).strip() for x in t.locator("thead th, tr th").all_inner_texts()]
    linhas = [[re.sub(r"\s+", " ", c).strip() for c in tr.locator("td").all_inner_texts()]
              for tr in t.locator("tbody tr").all()]
    return cab, [l for l in linhas if l]


def test_CA49_registros_filtrados_por_regiao(page, tmp_path):
    abrir_janela_r51(page, "vendas.csv")
    dlg(page, JANELA).get_by_role("button", name="Cancelar", exact=True).click()
    page.wait_for_timeout(300)
    abrir_painel(page)
    page.get_by_text("Filtros", exact=True).locator("visible=true").first.click()
    page.get_by_role("combobox", name="Campo categoria").select_option(label="Região")
    page.get_by_role("combobox", name="Valor", exact=True).select_option(label="Sul")
    page.wait_for_timeout(500)
    cab_tela, lin_tela = tabela_da_tela(page)
    ic = [x.lower() for x in cab_tela].index("cliente")   # a tela não mostra a coluna Código
    cinco_tela = [l[ic] for l in lin_tela[:5]]
    assert len(cinco_tela) == 5
    wb = gerar(page, tmp_path)
    p = parse_painel(wb["Painel"])
    reg = p["registros"]
    assert reg is not None
    assert reg["cab"] == CAB_V, reg["cab"]
    sul = [r for r in VENDAS if r["Região"] == "Sul"]
    assert 0 < len(sul) < len(VENDAS)
    assert len(reg["linhas"]) == len(sul)
    ic_x = reg["cab"].index("Código")
    codigos = [str(l[ic_x].value) for l in reg["linhas"]]
    assert set(codigos) == {r["Código"] for r in sul}
    ic_c = reg["cab"].index("Cliente")
    clientes = [str(l[ic_c].value) for l in reg["linhas"]]
    assert clientes[:5] == cinco_tela, (clientes[:5], cinco_tela)
    ir = reg["cab"].index("Região")
    assert {l[ir].value for l in reg["linhas"]} == {"Sul"}


def test_CA50_abas_do_painel_igual_a_planilha(page, tmp_path):
    wb = fluxo_41(page, tmp_path)
    titulos = titulos_blocos_excel(parse_painel(wb["Painel"]))
    abas = page.evaluate('() => window.__abasPainel("vendas")')
    assert abas == [{"nome": "Painel", "blocos": titulos}], abas


# ---- F-54: regressão da revisão de segurança da etapa 4 (SEG4) ----
def csv_tmp(tmp_path, nome, linhas):
    p = tmp_path / nome
    p.write_text("\n".join(linhas) + "\n", encoding="utf-8")
    return p


def carrega_csv(page, caminho):
    enviar(page, caminho)
    mapear_se_preciso(page)
    cancelar = dlg(page, JANELA).get_by_role("button", name="Cancelar", exact=True)
    if cancelar.is_visible():
        cancelar.click()
        page.wait_for_timeout(300)


def test_SEG4_M1_relatorio_chamado_painel_exporta(page, tmp_path):
    p = csv_tmp(tmp_path, "painel.csv", ["Código;Cliente;Valor", "1;A;10,00", "2;B;20,00"])
    abrir_painel(page)
    carrega_csv(page, p)
    wb = gerar(page, tmp_path)
    assert "Painel" in wb.sheetnames and len({n.lower() for n in wb.sheetnames}) == len(wb.sheetnames), wb.sheetnames


def test_SEG4_M1_nomes_que_diferem_so_na_caixa(page, tmp_path):
    a = csv_tmp(tmp_path, "Vendas.csv", ["Código;Cliente;Valor", "1;A;10,00"])
    b = csv_tmp(tmp_path, "vendas2.csv", ["Código;Cliente;Valor", "1;A;10,00"])
    carrega_csv(page, a)
    carrega_csv(page, b)
    wb = gerar(page, tmp_path, "Tudo numa planilha")
    assert len({n.lower() for n in wb.sheetnames}) == len(wb.sheetnames), wb.sheetnames


def test_SEG4_B1_numero_gigante_nao_vira_infinity(page, tmp_path):
    p = csv_tmp(tmp_path, "grande.csv", ["Código;Cliente;Valor", "1;A;" + "9" * 400, "2;B;5,00"])
    carrega_csv(page, p)
    wb = gerar(page, tmp_path)
    for ws in wb.worksheets:
        for row in ws.iter_rows():
            for c in row:
                assert not (isinstance(c.value, float) and (c.value != c.value or c.value in (float("inf"), float("-inf")))), (ws.title, c.coordinate)
