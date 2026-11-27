"""Suite da etapa 2 (CA-20 a CA-29). Escrita SO a partir da especificacao (secoes 0, 0.1, 0.3 e 2).
Seletores pelos rotulos exatos das tabelas 0.1/0.3. Oraculos em Python sobre tests/dados/."""
import re, statistics, datetime, unicodedata, collections
import pytest
from conftest import DADOS
from test_etapa1 import (le_csv, enviar, mapear_se_preciso, abrir_painel, gerar_excel, abrir_xlsx)

VENDAS = le_csv("vendas.csv")
CHAMADOS = le_csv("chamados.csv")
JANELA = "O que você quer acompanhar?"


# ---------- auxiliares de tela ----------
def dlg(page, titulo):
    return page.locator("dialog, [role=dialog]").filter(has_text=titulo).first


def abrir_janela_r51(page, arquivo):
    """Carrega o arquivo, responde 'Esta coluna é o quê?' se aparecer e espera a janela R-51 (sem Cancelar)."""
    enviar(page, arquivo)
    mapear_se_preciso(page)
    dlg(page, JANELA).wait_for(state="visible")


def linha(page, nome):
    """Linha (li/label com a caixa de marcar) cujo texto contem o nome exato (maiusculas conferidas)."""
    return (dlg(page, JANELA).locator("li, label")
            .filter(has=page.locator("input[type=checkbox]"))
            .filter(has_text=re.compile(re.escape(nome))).first)


def existe(page, nome):
    return linha(page, nome).count() > 0


def exemplo(page, nome):
    l = linha(page, nome)
    assert l.count() > 0, f"indicador ausente: {nome}"
    return re.sub(r"\s+", " ", l.inner_text())


def marcar(page, nomes):
    """Desmarca tudo e marca so os nomes, na ordem dada (a ordem de marcacao vale dentro de cada grupo)."""
    d = dlg(page, JANELA)
    for cb in d.locator("input[type=checkbox]").all():
        if cb.is_checked():
            cb.uncheck()
    for n in nomes:
        assert existe(page, n), f"indicador ausente: {n}"
        linha(page, n).locator("input[type=checkbox]").check()


def confirmar(page):
    dlg(page, JANELA).get_by_role("button", name="Confirmar", exact=True).click()
    page.wait_for_timeout(500)


def texto_seu_painel(page):
    d = dlg(page, "Seu painel")
    d.wait_for(state="visible")
    return re.sub(r"\s+", " ", d.inner_text())


def fechar_seu_painel(page):
    dlg(page, "Seu painel").get_by_role("button", name="Fechar").click()
    page.wait_for_timeout(300)


def item(flat, nome):
    m = re.search(re.escape(nome) + r" — .*?(?:Sem filtros|Filtros:\s*[^.]*)\.", flat)
    assert m, f"item '{nome}' ausente no texto: {flat!r}"
    return m.group(0)


# ---------- oraculos ----------
def br(x, casas=2):
    s = f"{x:,.{casas}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def num(s):
    return float(s.replace(".", "").replace(",", "."))


def sem_acento(s):
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn").lower()


def lideres(valores):
    c = collections.Counter(valores)
    mx = max(c.values())
    return {k for k, v in c.items() if v == mx}, mx


def valor(r):
    return float(r["Valor"].replace(",", "."))


def dmy(s):
    return datetime.datetime.strptime(s, "%d/%m/%Y")


def fmt_dur(med):
    """CA-96: minuto inteiro mais proximo (meio para cima); 'M min' ou 'H h MM min'."""
    h, m = divmod(int(med + 0.5), 60)
    return f"{h} h {m:02d} min" if h else f"{m} min"


def mediana_tempo():
    f = "%d/%m/%Y %H:%M"
    mins = []
    for r in CHAMADOS:
        if r["Abertura"] and r["Conclusão"]:
            d = (datetime.datetime.strptime(r["Conclusão"], f) - datetime.datetime.strptime(r["Abertura"], f)).total_seconds() / 60
            if d >= 0:
                mins.append(d)
    return statistics.median(mins)


PREFIXOS_FECHADO = ("conclu", "finaliz", "encerr", "fechad", "entreg", "cancel", "resolvid", "pag")


def mais_antigo_em_aberto():
    f = "%d/%m/%Y %H:%M"
    abertos = [datetime.datetime.strptime(r["Abertura"], f) for r in CHAMADOS
               if r["Abertura"] and not sem_acento(r["Situação"]).startswith(PREFIXOS_FECHADO)]
    return min(abertos).strftime("%d/%m/%Y")


def periodo_vendas(regs):
    ds = [dmy(r["Data"]) for r in regs]
    return min(ds).strftime("%d/%m/%Y"), max(ds).strftime("%d/%m/%Y")


# ---------- CA-20 ----------
def test_CA20_vendas_lista_indicadores_e_nao_tempo(page):
    abrir_janela_r51(page, "vendas.csv")
    for nome in ["Total de registros", "Por Cliente", "Por Região", "Valor (soma, média e mediana)",
                 "Valor por Região", "Evolução por mês (Data)", "% por Situação"]:
        assert existe(page, nome), nome
    assert not existe(page, "Tempo entre duas datas")
    assert page.get_by_role("button", name="Cancelar", exact=True).first.is_visible()


# ---------- CA-21 ----------
def test_CA21_exemplos_iguais_ao_oraculo_vendas(page):
    abrir_janela_r51(page, "vendas.csv")
    # Total
    t = exemplo(page, "Total de registros")
    assert int(re.search(r"([\d.]+) registros", t).group(1).replace(".", "")) == len(VENDAS)
    # Por Cliente e Por Região (valor lider e contagem)
    for campo in ["Cliente", "Região"]:
        t = exemplo(page, f"Por {campo}")
        m = re.search(rf"{campo}:\s*(.+?) lidera com ([\d.]+)", t)
        assert m, t
        lid, mx = lideres(r[campo] for r in VENDAS)
        assert m.group(1).strip() in lid and int(m.group(2).replace(".", "")) == mx, (t, lid, mx)
    # Soma, media e mediana
    t = exemplo(page, "Valor (soma, média e mediana)")
    m = re.search(r"Soma:\s*([\d.]+,\d{2})\s*·\s*Média:\s*([\d.]+,\d{2})\s*·\s*Mediana:\s*([\d.]+,\d{2})", t)
    assert m, t
    vals = [valor(r) for r in VENDAS]
    for achado, esperado in zip(m.groups(), [sum(vals), statistics.mean(vals), statistics.median(vals)]):
        assert abs(num(achado) - esperado) <= 0.011, (achado, esperado)
    # Valor por Região: categoria lider pela soma
    t = exemplo(page, "Valor por Região")
    m = re.search(r"Maior soma:\s*(.+?)\s*\((?:R\$\s*)?([\d.]+,\d{2})\)", t)
    assert m, t
    somas = collections.defaultdict(float)
    for r in VENDAS:
        somas[r["Região"]] += valor(r)
    lider = max(somas, key=somas.get)
    assert m.group(1).strip() == lider and abs(num(m.group(2)) - somas[lider]) <= 0.011
    # Evolução por mês
    t = exemplo(page, "Evolução por mês (Data)")
    m = re.search(r"Mês com mais registros:\s*(\d{2}/\d{4})\s*\(([\d.]+)\)", t)
    assert m, t
    lid, mx = lideres(r["Data"][3:] for r in VENDAS)
    assert m.group(1) in lid and int(m.group(2).replace(".", "")) == mx, (t, lid, mx)
    # % por Situação
    t = exemplo(page, "% por Situação")
    m = re.search(r"(\S.*?): ([\d.]+,\d)%", t.replace("% por Situação", "", 1))
    assert m, t
    lid, mx = lideres(r["Situação"] for r in VENDAS)
    assert m.group(1).strip() in lid and abs(num(m.group(2)) - 100 * mx / len(VENDAS)) <= 0.051, (t, lid, mx)


# ---------- CA-22 ----------
def blocos_marcados(page):
    marcar(page, ["Por Região", "Valor (soma, média e mediana)", "Total de registros"])
    confirmar(page)
    fechar_seu_painel(page)


def pos(page, nome, tipo="heading"):
    if tipo == "heading":
        loc = page.get_by_role("heading", name=nome, exact=True).first
    else:
        loc = page.get_by_text(nome, exact=True).first
    b = loc.bounding_box()
    assert b, f"bloco ausente no painel: {nome}"
    return (round(b["y"]), round(b["x"]))


def test_CA22_tres_blocos_ordem_numero_grafico_tabela(page):
    abrir_janela_r51(page, "vendas.csv")
    blocos_marcados(page)
    abrir_painel(page)
    total = pos(page, "Total de registros")
    valor_ = pos(page, "Valor (soma, média e mediana)")
    graf = pos(page, "Por Região")
    reg = pos(page, "Registros", "texto")
    # numeros primeiro (dentro do grupo, ordem de marcacao: Valor foi marcado antes do Total)
    assert valor_ < total < graf < reg, (valor_, total, graf, reg)
    assert max(valor_[0], total[0]) <= graf[0]
    # so 3 blocos: os demais indicadores nao viram cartao
    for nome in ["Por Cliente", "Valor por Região", "% por Situação", "Evolução por mês (Data)"]:
        assert page.get_by_role("heading", name=nome, exact=True).count() == 0, nome


# ---------- CA-23 ----------
def test_CA23_recarregar_mantem_blocos_e_marcas(page):
    abrir_janela_r51(page, "vendas.csv")
    blocos_marcados(page)
    page.reload(); page.wait_for_timeout(1200)
    abrir_painel(page)
    for nome in ["Total de registros", "Valor (soma, média e mediana)", "Por Região"]:
        assert page.get_by_role("heading", name=nome, exact=True).count() >= 1, nome
    assert page.get_by_role("heading", name="Por Cliente", exact=True).count() == 0
    page.get_by_role("button", name="O que acompanhar", exact=True).click()
    dlg(page, JANELA).wait_for(state="visible")
    marcadas = {n for n in ["Total de registros", "Por Cliente", "Por Região", "Valor (soma, média e mediana)",
                            "Valor por Região", "Evolução por mês (Data)", "% por Situação"]
                if linha(page, n).locator("input[type=checkbox]").is_checked()}
    assert marcadas == {"Total de registros", "Valor (soma, média e mediana)", "Por Região"}


# ---------- CA-24 ----------
def tipos_da_tela(page):
    """Le {nome da coluna: (select do Tipo, texto escolhido)} da tela 'Esta coluna é o quê?' (prévia, F-80)."""
    res = {}
    for i, inp in enumerate(page.locator("input[aria-label^='Nome da coluna']:visible").all(), start=1):
        sel = page.get_by_label(f"Tipo da coluna {i}", exact=True)
        res[inp.input_value()] = (sel, sel.evaluate("e=>e.options[e.selectedIndex].text").strip())
    return res


def test_CA24_grupo_sugerido_e_trocar_para_situacao(page):
    enviar(page, "vendas.csv")
    assert page.get_by_text("Esta coluna é o quê?").first.is_visible()
    tipos = tipos_da_tela(page)
    # <= 30 distintos e >= 50% de repeticao -> Grupo (antes Categoria)
    for campo in ["Cliente", "Região", "Vendedor"]:
        assert tipos[campo][1] == "Grupo", (campo, tipos[campo][1])
    assert tipos["Valor"][1] == "Número" and tipos["Data"][1] == "Data"
    # o andamento (Situação) e uma pergunta a parte, sugerida pelo nome da coluna
    assert page.get_by_label("Qual coluna mostra o andamento?").evaluate("e=>e.options[e.selectedIndex].text") == "Situação"
    assert page.get_by_label("Qual coluna identifica cada linha?").evaluate("e=>e.options[e.selectedIndex].text") == "Código"
    # a pessoa troca o andamento para Região
    page.get_by_label("Qual coluna mostra o andamento?").select_option(label="Região")
    page.get_by_role("button", name="Confirmar", exact=True).first.click()
    dlg(page, JANELA).wait_for(state="visible")
    assert existe(page, "% por Região"), "Região como andamento deve gerar '% por Região'"


# ---------- CA-25 ----------
def test_CA25_chamados_tempo_e_mais_antigos_iguais_ao_oraculo(page):
    abrir_janela_r51(page, "chamados.csv")
    assert existe(page, "Tempo entre duas datas")
    assert existe(page, "Mais antigos em aberto")
    # Total
    t = exemplo(page, "Total de registros")
    assert int(re.search(r"([\d.]+) registros", t).group(1).replace(".", "")) == len(CHAMADOS)
    # Tempo entre duas datas: formato CA-96 ('H h MM min'); aceita tambem 'N d N h' (R-58) com a mesma mediana
    t = exemplo(page, "Tempo entre duas datas")
    med = mediana_tempo()
    if re.search(r"Mediana:\s*\d+ d\b", t):
        m = re.search(r"Mediana:\s*(\d+) d (\d+) h", t)
        assert m, t
        achado = int(m.group(1)) * 1440 + int(m.group(2)) * 60
        assert abs(achado - med) <= 60, (t, med)
    else:
        esperado = fmt_dur(med)
        assert re.search(r"Mediana:\s*" + re.escape(esperado) + r"(?!\d)", t), (t, esperado)
    # Mais antigos em aberto
    t = exemplo(page, "Mais antigos em aberto")
    assert f"Mais antigo: {mais_antigo_em_aberto()}" in t, (t, mais_antigo_em_aberto())
    # % por Situação
    t = exemplo(page, "% por Situação")
    lid, mx = lideres(r["Situação"] for r in CHAMADOS)
    m = re.search(r"(\S.*?): ([\d.]+,\d)%", t.replace("% por Situação", ""))
    assert m and m.group(1).strip() in lid and abs(num(m.group(2)) - 100 * mx / len(CHAMADOS)) <= 0.051, (t, lid)
    # Sem valor: so campos com >= 1 vazio
    vazios = {c: sum(1 for r in CHAMADOS if not r[c]) for c in CHAMADOS[0]}
    for c, n in vazios.items():
        if n:
            tt = exemplo(page, f"Sem valor em {c}")
            assert int(re.search(r"([\d.]+) sem valor em", tt).group(1).replace(".", "")) == n, (tt, n)
        else:
            assert not existe(page, f"Sem valor em {c}"), f"Sem valor em {c} nao deveria aparecer (0 vazios)"


# ---------- CA-26 ----------
def test_CA26_seu_painel_com_tres_itens(page):
    abrir_janela_r51(page, "vendas.csv")
    marcar(page, ["Total de registros", "Por Cliente", "Valor por Região"])
    confirmar(page)
    flat = texto_seu_painel(page)
    assert flat.count("Período:") == 3, flat
    ini, fim = periodo_vendas(VENDAS)
    it = item(flat, "Valor por Região")
    assert "Quanto Valor soma em cada Região" in it, it
    assert f"Período: de {ini} a {fim}" in it, it
    assert "Sem filtros" in it, it
    assert "Quantas linhas o arquivo tem" in item(flat, "Total de registros")
    assert "Quantos registros há em cada Cliente" in item(flat, "Por Cliente")
    for nome in ["Total de registros", "Por Cliente"]:
        assert "Sem filtros" in item(flat, nome)
    # R-63 reabre o mesmo texto
    fechar_seu_painel(page)
    page.get_by_role("button", name="Entender este painel", exact=True).click()
    assert texto_seu_painel(page) == flat


# ---------- CA-27 ----------
def test_CA27_filtros_aparecem_no_resumo(page):
    abrir_janela_r51(page, "vendas.csv")
    marcar(page, ["Total de registros", "Por Cliente", "Valor por Região"])
    confirmar(page)
    fechar_seu_painel(page)
    abrir_painel(page)
    page.get_by_text("Filtros", exact=True).locator("visible=true").first.click()
    page.get_by_role("combobox", name="Campo categoria").select_option(label="Região")
    page.get_by_role("combobox", name="Valor", exact=True).select_option(label="Sul")
    page.get_by_role("combobox", name="Período").select_option(label="Mês")
    page.get_by_label("Mês", exact=True).fill("2026-10")
    page.wait_for_timeout(500)
    regs = [r for r in VENDAS if r["Região"] == "Sul" and r["Data"].endswith("/10/2026")]
    assert regs, "dados de teste sem Sul/outubro"
    page.get_by_role("button", name="Entender este painel", exact=True).click()
    flat = texto_seu_painel(page)
    ini, fim = periodo_vendas(regs)
    for nome in ["Total de registros", "Por Cliente", "Valor por Região"]:
        it = item(flat, nome)
        assert "só região Sul" in it, it
        assert "outubro/2026" in it, it
        assert "Sem filtros" not in it, it
        assert f"Período: de {ini} a {fim}" in it, it


# ---------- CA-28 ----------
@pytest.mark.skip(reason="adiado: etapas 3 e 6")
def test_CA28_pedido_escrito_e_editar_layout():
    pass


# ---------- CA-29 ----------
def test_CA29_excel_segunda_planilha_igual_ao_texto_da_tela(page, tmp_path):
    abrir_janela_r51(page, "vendas.csv")
    marcar(page, ["Total de registros", "Por Cliente", "Valor por Região"])
    confirmar(page)
    fechar_seu_painel(page)
    dl = gerar_excel(page)
    wb = abrir_xlsx(dl, tmp_path)
    assert len(wb.sheetnames) >= 2 and wb.sheetnames[1] == "Como ler este relatório", wb.sheetnames
    ws = wb.worksheets[1]
    assert ws["A1"].value == "Seu painel"
    linhas = [str(ws.cell(row=i, column=1).value).strip() for i in range(2, ws.max_row + 1)
              if ws.cell(row=i, column=1).value]
    assert len(linhas) == 3, linhas
    page.get_by_role("button", name="Entender este painel", exact=True).click()
    flat = texto_seu_painel(page)
    for l in linhas:
        assert re.sub(r"\s+", " ", l) in flat, f"linha do Excel sem igual na tela: {l!r}"
    assert flat.count("Período:") == len(linhas)


def test_CA29_sem_escolha_confirmada_nao_cria_planilha(page, tmp_path):
    abrir_janela_r51(page, "vendas.csv")
    dlg(page, JANELA).get_by_role("button", name="Cancelar", exact=True).click()
    page.wait_for_timeout(300)
    wb = abrir_xlsx(gerar_excel(page), tmp_path)
    assert "Como ler este relatório" not in wb.sheetnames
