"""Suite da etapa 3 (CA-30 a CA-37 e CA-28). Escrita SO a partir da especificacao (secoes 0, 0.1, 0.3, 0.4 e 3).
Seletores pelos rotulos R-70..R-79. Oraculos em Python sobre tests/dados/vendas.csv.
Conjunto: o nome usado em __entender e o nome do arquivo sem extensao ('vendas')."""
import json, re, pathlib, statistics, datetime, unicodedata
import pytest
from conftest import DADOS
from test_etapa1 import le_csv, enviar, mapear_se_preciso, gerar_excel, abrir_xlsx
from test_etapa2 import dlg, abrir_janela_r51, JANELA, marcar, confirmar, texto_seu_painel, fechar_seu_painel

VENDAS = le_csv("vendas.csv")
CONJUNTO = "vendas"
PEDIDOS = json.loads((pathlib.Path(__file__).parent / "pedidos.json").read_text(encoding="utf-8"))


# ---------- auxiliares de tela ----------
def carregar_vendas(page):
    """Carrega vendas.csv e fecha a janela R-51 com Cancelar (painel padrao); a caixa R-70 deve aparecer."""
    abrir_janela_r51(page, "vendas.csv")
    dlg(page, JANELA).get_by_role("button", name="Cancelar", exact=True).click()
    page.wait_for_timeout(300)


def pedir(page, frase):
    campo = page.get_by_label("Peça um indicador", exact=True)
    campo.fill(frase)
    campo.press("Enter")
    page.wait_for_timeout(400)


def bloco(page, ancora):
    """Elemento mais interno que contem o texto ancora (resumo, 'Tente um destes:' etc.)."""
    return page.locator("dialog, [role=dialog], section, div, form").filter(has_text=ancora).last


def resumo(page):
    page.get_by_text("Entendi assim:").first.wait_for(state="visible")
    return re.sub(r"\s+", " ", bloco(page, "Entendi assim:").inner_text())


def responder(page, nome):
    page.get_by_role("button", name=nome, exact=True).click()
    page.wait_for_timeout(400)


def previa_valor(page):
    el = page.get_by_test_id("previa-valor").first
    el.wait_for(state="visible")
    return el.inner_text()


def num(txt):
    """'R$ 1.234,56' -> 1234.56 (primeiro numero do texto)."""
    m = re.search(r"-?\d[\d.]*(?:,\d+)?", txt)
    assert m, f"sem numero em {txt!r}"
    return float(m.group(0).replace(".", "").replace(",", "."))


def entender(page, frase, conjunto=CONJUNTO):
    return page.evaluate("([f,c]) => window.__entender(f,c)", [frase, conjunto])


def semacento(s):
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn").lower()


def canon(o):
    """Forma comparavel: filtros e naoEntendi sem ordem."""
    o = dict(o)
    o["filtros"] = sorted(({"campo": f["campo"], "valor": f["valor"]} for f in o.get("filtros") or []),
                          key=lambda f: (f["campo"], f["valor"]))
    o["naoEntendi"] = sorted(o.get("naoEntendi") or [])
    return {k: o.get(k) for k in ("medida", "campo", "agrupar", "filtros", "periodo", "naoEntendi")}


# ---------- oraculos em Python ----------
def data(r):
    return datetime.datetime.strptime(r["Data"], "%d/%m/%Y").date()


def valor(r):
    return float(r["Valor"].replace(".", "").replace(",", "."))


def filtra(situacao=None, regiao=None, mes=None, de=None, ate=None, cliente=None):
    out = []
    for r in VENDAS:
        d = data(r)
        if situacao and r["Situação"] != situacao: continue
        if regiao and r["Região"] != regiao: continue
        if cliente and r["Cliente"] != cliente: continue
        if mes and (d.month != mes or d.year != 2026): continue
        if de and not (de <= d <= ate): continue
        out.append(r)
    return out


# ---------- bateria inteira (CA-30..34 e meta 100%) ----------
def test_bateria_pedidos_json_tem_cobertura_minima():
    assert len(PEDIDOS) >= 40
    for var in ("medida", "agrupar", "filtro", "periodo", "erro_digitacao", "nao_entendida"):
        assert sum(1 for p in PEDIDOS if p["variacao"] == var) >= 8, var


def test_funcao_entender_existe_e_nao_mexe_na_tela(page):
    carregar_vendas(page)
    antes = page.locator("body").inner_text()
    r = entender(page, "quantidade de registros")
    assert set(r) >= {"medida", "campo", "agrupar", "filtros", "periodo", "naoEntendi"}
    assert page.locator("body").inner_text() == antes
    assert not page.get_by_text("Entendi assim:").first.is_visible()


def test_bateria_100_por_cento(page):
    carregar_vendas(page)
    falhas = []
    for p in PEDIDOS:
        obtido = entender(page, p["frase"], p["conjunto"])
        if canon(obtido) != canon(p["esperado"]):
            falhas.append({"frase": p["frase"], "esperado": canon(p["esperado"]), "obtido": canon(obtido)})
    pct = 100 * (len(PEDIDOS) - len(falhas)) / len(PEDIDOS)
    assert not falhas, f"{pct:.1f}% da bateria; falhas ({len(falhas)}): " + json.dumps(falhas, ensure_ascii=False)[:3000]


# ---------- critérios CA-30 a CA-34 pela API (estrutura) e pela tela (resumo) ----------
def test_CA30_quantidade_por_cliente_em_outubro(page):
    carregar_vendas(page)
    r = entender(page, "quantidade de pedidos por cliente em outubro")
    assert r["medida"] == "quantidade" and r["agrupar"] == "Cliente"
    assert r["periodo"] == {"tipo": "mes", "mes": 10, "ano": 2026} and r["naoEntendi"] == []
    pedir(page, "quantidade de pedidos por cliente em outubro")
    t = resumo(page).lower()
    assert "quantidade de registros" in t and "por cliente" in t and "outubro/2026" in t
    assert page.get_by_text("É isso?").first.is_visible()
    assert page.get_by_text("Prévia", exact=True).first.is_visible()


def test_CA31_media_por_regiao_este_ano_so_entregues(page):
    # Duvida registrada: a especificacao diz "concluidos", mas vendas.csv nao tem essa situacao
    # (tem Entregue/Cancelado/Pendente/Em transporte). O teste usa "entregues".
    carregar_vendas(page)
    r = entender(page, "valor medio por regiao este ano, so entregues")
    assert r["medida"] == "media" and r["campo"] == "Valor" and r["agrupar"] == "Região"
    assert r["periodo"] == {"tipo": "ano", "ano": 2026}
    assert r["filtros"] == [{"campo": "Situação", "valor": "Entregue"}] and r["naoEntendi"] == []
    pedir(page, "valor medio por regiao este ano, so entregues")
    t = resumo(page).lower()
    assert "média" in t and "valor" in t and "por região" in t and "entregue" in t and "2026" in t


def test_CA32_erros_de_digitacao(page):
    carregar_vendas(page)
    r = entender(page, "soma do valr por clinte")
    assert (r["medida"], r["campo"], r["agrupar"]) == ("soma", "Valor", "Cliente")
    assert r["filtros"] == [] and r["periodo"] is None and r["naoEntendi"] == []
    pedir(page, "soma do valr por clinte")
    t = resumo(page).lower()
    assert "soma" in t and "valor" in t and "por cliente" in t
    assert "não entendi" not in page.locator("body").inner_text().lower()


def test_CA33_percentual_de_cancelados_por_mes(page):
    carregar_vendas(page)
    r = entender(page, "% de cancelados por mês")
    assert r["medida"] == "percentual" and r["agrupar"] == "mês"
    assert r["filtros"] == [{"campo": "Situação", "valor": "Cancelado"}] and r["naoEntendi"] == []
    pedir(page, "% de cancelados por mês")
    t = resumo(page).lower()
    assert "cancelado" in t and "por mês" in t


def test_CA34_quantos_registros_de_01_09_a_15_09(page):
    carregar_vendas(page)
    r = entender(page, "quantos registros de 01/09 a 15/09")
    assert r["medida"] == "quantidade"
    assert r["periodo"] == {"tipo": "intervalo", "de": "2026-09-01", "ate": "2026-09-15"}
    pedir(page, "quantos registros de 01/09 a 15/09")
    t = resumo(page)
    assert "01/09" in t and "15/09" in t


# ---------- CA-35: frase nao entendida ----------
def test_CA35_bom_dia_nao_entendi_exemplos_e_nada_no_painel(page):
    carregar_vendas(page)
    r = entender(page, "bom dia")
    assert r["medida"] is None and r["campo"] is None and r["agrupar"] is None
    assert r["filtros"] == [] and r["periodo"] is None and r["naoEntendi"] == ["bom dia"]
    pedir(page, "bom dia")
    page.get_by_text("não entendi: bom dia").first.wait_for(state="visible")
    page.get_by_text("Tente um destes:").first.wait_for(state="visible")
    ex = bloco(page, "Tente um destes:").get_by_role("button")
    assert ex.count() >= 3
    textos = [ex.nth(i).inner_text().strip() for i in range(3)]
    campos = {"cliente", "região", "regiao", "valor", "vendedor", "situação", "situacao", "data", "registros"}
    for t in textos:
        assert t and any(c in semacento(t) or c in t.lower() for c in campos), f"exemplo sem campo real: {t!r}"
    # nada entrou no painel
    assert page.get_by_text("Meus indicadores", exact=True).count() == 0 or \
        not page.get_by_text("Meus indicadores", exact=True).first.is_visible()
    # clicar num exemplo o preenche e envia
    ex.first.click()
    page.wait_for_timeout(500)
    page.get_by_text("Entendi assim:").first.wait_for(state="visible")
    assert page.get_by_text("É isso?").first.is_visible()


# ---------- CA-36: corrigir pelos botoes ----------
def test_CA36_nao_troca_agrupar_para_regiao_e_sim(page):
    carregar_vendas(page)
    pedir(page, "quantidade de registros por cliente")
    t0 = resumo(page).lower()
    assert "por cliente" in t0
    responder(page, "Não")
    for nome in ("Medida", "Campo", "Agrupar por", "Filtro", "Período"):
        assert page.get_by_role("button", name=nome, exact=True).first.is_visible(), nome
    page.get_by_role("button", name="Agrupar por", exact=True).click()
    page.get_by_role("combobox", name="Agrupar por").select_option(label="Região")
    page.get_by_role("button", name="Aplicar", exact=True).click()
    page.wait_for_timeout(500)
    t1 = resumo(page).lower()
    assert "por região" in t1 and "por cliente" not in t1
    assert page.get_by_text("Prévia", exact=True).first.is_visible()
    responder(page, "Sim")
    sec = page.get_by_text("Meus indicadores", exact=True).first
    sec.wait_for(state="visible")
    cont = bloco(page, "Meus indicadores").inner_text().lower()
    assert "região" in cont, cont


# ---------- CA-37: sinonimos ----------
def test_CA37_sinonimo_fat_vira_valor_pela_config(page):
    carregar_vendas(page)
    page.get_by_text("Config", exact=True).first.click()
    page.get_by_text("Apelidos para o pedido escrito", exact=True).first.wait_for(state="visible")
    page.get_by_label("Apelido", exact=True).fill("fat")
    page.get_by_role("combobox", name="Significa").select_option(label="Valor")
    page.get_by_role("button", name="Adicionar sinônimo", exact=True).click()
    page.wait_for_timeout(300)
    assert json.loads(page.evaluate("localStorage.getItem('raiox_sin')")).get("fat") == "Valor"
    r = entender(page, "fat por cliente")
    assert (r["medida"], r["campo"], r["agrupar"]) == ("soma", "Valor", "Cliente"), r
    assert r["naoEntendi"] == []
    page.get_by_text("Painel", exact=True).first.click()
    pedir(page, "fat por cliente")
    t = resumo(page).lower()
    assert "soma" in t and "valor" in t and "por cliente" in t
    # remover apaga o sinonimo
    page.get_by_text("Config", exact=True).first.click()
    page.get_by_role("button", name="Remover").first.click()
    page.wait_for_timeout(300)
    assert "fat" not in json.loads(page.evaluate("localStorage.getItem('raiox_sin') || '{}'"))


def test_sinonimo_de_medida_via_localStorage(page):
    carregar_vendas(page)
    page.evaluate("localStorage.setItem('raiox_sin', JSON.stringify({qtd:'quantidade', fat:'Valor'}))")
    r = entender(page, "qtd por região")
    assert r["medida"] == "quantidade" and r["agrupar"] == "Região" and r["naoEntendi"] == []


def test_sinonimos_entram_no_backup_chave_sin(page, tmp_path):
    carregar_vendas(page)
    page.evaluate("localStorage.setItem('raiox_sin', JSON.stringify({fat:'Valor'}))")
    page.reload(); page.wait_for_timeout(800)
    page.get_by_text("Config", exact=True).first.click()
    with page.expect_download() as d:
        page.get_by_role("button", name="Baixar backup", exact=True).click()
    p = tmp_path / "b.json"; d.value.save_as(str(p))
    j = json.loads(p.read_text(encoding="utf-8"))
    assert j.get("sin") == {"fat": "Valor"}, list(j)


# ---------- valor da previa contra Python ----------
CASOS_PREVIA = [
    ("soma do valor", lambda: sum(valor(r) for r in VENDAS)),
    ("média do valor", lambda: statistics.mean(valor(r) for r in VENDAS)),
    ("mediana do valor", lambda: statistics.median(valor(r) for r in VENDAS)),
    ("valor máximo", lambda: max(valor(r) for r in VENDAS)),
    ("valor mínimo", lambda: min(valor(r) for r in VENDAS)),
    ("quantidade de registros", lambda: len(VENDAS)),
    ("soma do valor só entregues", lambda: sum(valor(r) for r in filtra(situacao="Entregue"))),
    ("quantidade de registros da região Sul", lambda: len(filtra(regiao="Sul"))),
    ("quantidade de registros em outubro", lambda: len(filtra(mes=10))),
    ("média do valor em setembro", lambda: statistics.mean(valor(r) for r in filtra(mes=9))),
    ("quantos registros de 01/09 a 15/09",
     lambda: len(filtra(de=datetime.date(2026, 9, 1), ate=datetime.date(2026, 9, 15)))),
    ("soma do valor da região Norte, só cancelados",
     lambda: sum(valor(r) for r in filtra(situacao="Cancelado", regiao="Norte"))),
]


@pytest.mark.parametrize("frase,oraculo", CASOS_PREVIA, ids=[c[0] for c in CASOS_PREVIA])
def test_previa_valor_igual_ao_oraculo_python(page, frase, oraculo):
    carregar_vendas(page)
    pedir(page, frase)
    resumo(page)
    obtido = num(previa_valor(page))
    esperado = oraculo()
    assert abs(obtido - esperado) <= 0.011 + abs(esperado) * 1e-9, f"{frase}: app {obtido} x python {esperado}"


# ---------- CA-28: pedido escrito entra no "Seu painel" e na planilha ----------
def test_CA28_pedido_entra_no_resumo_e_retirado_sai(page, tmp_path):
    abrir_janela_r51(page, "vendas.csv")
    marcar(page, ["Total de registros", "Por Cliente"])
    confirmar(page)
    fechar_seu_painel(page)
    pedir(page, "soma do valor por região")
    resumo(page)
    responder(page, "Sim")
    page.get_by_text("Meus indicadores", exact=True).first.wait_for(state="visible")
    page.get_by_role("button", name="Entender este painel", exact=True).click()
    flat = texto_seu_painel(page)
    assert "soma do campo Valor, separada por Região" in flat, flat
    assert "Por Cliente" in flat and flat.count("Conta:") == 3, flat
    fechar_seu_painel(page)
    # Excel: mesma linha na planilha "Como ler este relatório"
    wb = abrir_xlsx(gerar_excel(page), tmp_path)
    assert wb.sheetnames[1] == "Como ler este relatório"
    ws = wb.worksheets[1]
    linhas = [str(ws.cell(row=i, column=1).value) for i in range(2, ws.max_row + 1) if ws.cell(row=i, column=1).value]
    assert any("soma do campo Valor, separada por Região" in l for l in linhas), linhas
    # retirar um bloco em "O que acompanhar": some do resumo, o pedido continua
    page.get_by_text("Painel", exact=True).first.click()
    page.get_by_role("button", name="O que acompanhar", exact=True).click()
    dlg(page, JANELA).wait_for(state="visible")
    marcar(page, ["Total de registros"])
    confirmar(page)
    flat2 = texto_seu_painel(page)
    assert "Por Cliente —" not in flat2 and "contagem de registros por Cliente" not in flat2, flat2
    assert "soma do campo Valor, separada por Região" in flat2, flat2


def test_CA28_nao_entendido_nao_entra_no_resumo(page):
    abrir_janela_r51(page, "vendas.csv")
    marcar(page, ["Total de registros"])
    confirmar(page)
    fechar_seu_painel(page)
    pedir(page, "bom dia")
    page.get_by_text("não entendi: bom dia").first.wait_for(state="visible")
    page.get_by_role("button", name="Entender este painel", exact=True).click()
    assert texto_seu_painel(page).count("Conta:") == 1


# ---------- F-70: depois de "Não" não aparece "null" solto ----------
def test_f70_depois_de_nao_o_cartao_nao_mostra_null(page):
    carregar_vendas(page)
    pedir(page, "quantidade de registros por cliente")
    responder(page, "Não")
    caixa = page.locator("#pedBox")
    assert "null" not in caixa.inner_text()
    page.get_by_role("button", name="Período", exact=True).click()
    assert "null" not in caixa.inner_text()


# ---------- F-71: meta opcional ----------
def _cartao_tempo(page, meta):
    abrir_janela_r51(page, "chamados.csv")
    dlg(page, JANELA).get_by_role("button", name="Cancelar", exact=True).click()
    page.get_by_text("Config", exact=True).first.click()
    page.locator("#cfgMeta").fill(meta)
    page.get_by_text("Painel", exact=True).first.click()
    page.wait_for_timeout(400)
    return page.locator("#cartaoTempo").inner_text()


def test_f71_meta_vazia_nao_mostra_frase_da_meta(page):
    t = _cartao_tempo(page, "")
    assert "Dentro de" in t and "meta" not in t.lower(), t


def test_f71_meta_zero_vale_zero_e_nao_volta_para_90(page):
    t = _cartao_tempo(page, "0")
    assert "meta de 0%" in t and "90" not in t.replace("Dentro de 24", ""), t


def test_f71_padrao_continua_90(page):
    abrir_janela_r51(page, "chamados.csv")
    dlg(page, JANELA).get_by_role("button", name="Cancelar", exact=True).click()
    page.wait_for_timeout(300)
    assert "meta de 90%" in page.locator("#cartaoTempo").inner_text()
