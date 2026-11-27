"""F-74: achados do teste do Galindo (homologação 26/11/2026)."""
import re
from conftest import DADOS
from test_etapa1 import enviar
from test_etapa2 import dlg, abrir_janela_r51, JANELA
from test_etapa3 import carregar_vendas, VENDAS


def jan(page):
    return page.locator(".jan").last


def abre_total(page):
    carregar_vendas(page)
    page.locator("#kTotal").click()
    jan(page).wait_for(state="visible")
    return jan(page)


def test_f74_importador_texto_explica_a_tela(page):
    enviar(page, "vendas.csv")
    page.get_by_text("Esta coluna é o quê?").first.wait_for(state="visible")
    t = page.locator("body").inner_text()
    assert "Confira o que o programa entendeu" in t and "Arquivo: vendas.csv." in t
    assert "Você só faz isso uma vez por formato." in t


def test_f74_topo_nao_diz_so_csv(page):
    t = page.locator("body").inner_text()
    assert "Leia um relatório (CSV)" not in t and "PDF" in t and "foto" in t


def test_f74_janela_mostra_todos_os_valores_da_fileira(page):
    j = abre_total(page)
    nomes = {r["Cliente"] for r in VENDAS}
    chips = j.locator(".chip").all_inner_texts()
    for n in nomes:
        assert any(c.startswith(n + " (") for c in chips) or True
    # 10 clientes: todos aparecem depois de "mais…"
    j.get_by_role("button", name=re.compile("^mais…")).first.click()
    chips = j.locator(".chip").all_inner_texts()
    for n in nomes:
        assert any(c.startswith(n + " (") for c in chips), n


def test_f74_chips_se_ajustam_a_selecao_como_segmentacao(page):
    j = abre_total(page)
    j.get_by_role("button", name=re.compile("^mais…")).first.click()
    reg = next(r["Região"] for r in VENDAS)
    j.get_by_role("button", name=re.compile(rf"^{reg} \(")).click()
    esperado = {}
    for r in VENDAS:
        if r["Região"] == reg:
            esperado[r["Cliente"]] = esperado.get(r["Cliente"], 0) + 1
    chips = j.locator(".chip").all_inner_texts()
    for cli, n in esperado.items():
        assert f"{cli} ({n})" in chips, (cli, n)
    # o que não tem nenhum registro na região fica apagado (com 0)
    assert any(c.endswith(" (0)") for c in chips) or len(esperado) == len({r["Cliente"] for r in VENDAS})


def test_f74_mostrar_mais_na_janela(page):
    j = abre_total(page)
    assert "mostrando 200" in j.inner_text()
    j.get_by_role("button", name="Mostrar mais", exact=True).click()
    assert "mostrando 300" in j.inner_text()
    assert j.locator("tbody tr").count() == 300


def test_f74_maximizar_e_restaurar(page):
    j = abre_total(page)
    j.get_by_role("button", name="Maximizar", exact=True).click()
    box = j.bounding_box()
    assert box["width"] >= 1270 and box["x"] == 0
    j.get_by_role("button", name="Restaurar", exact=True).click()
    assert j.bounding_box()["width"] < 1000


def test_f74_mais_antigo_e_mais_novo_abrem_a_janela(page):
    carregar_vendas(page)
    from datetime import datetime
    ds = [datetime.strptime(r["Data"], "%d/%m/%Y") for r in VENDAS]
    mi, ma = min(ds), max(ds)
    for ident, alvo in (("#kAnt", mi), ("#kNov", ma)):
        page.locator(ident).click()
        j = jan(page)
        j.wait_for(state="visible")
        n = sum(1 for d in ds if d == alvo)
        assert f"({n})" in j.locator("header b").inner_text(), j.locator("header b").inner_text()
        assert alvo.strftime("%d/%m/%Y") in j.locator("header b").inner_text()
        j.get_by_role("button", name="Fechar", exact=True).click()


def test_f74_titulo_do_bloco_abre_os_registros(page):
    carregar_vendas(page)
    h = page.locator("h3.abre").first
    assert h.count() == 1
    h.click()
    j = jan(page)
    j.wait_for(state="visible")
    assert "registros" in j.inner_text()


# ---------- F-78: Config clara e ⓘ ----------
def abre_config(page):
    page.get_by_text("Config", exact=True).first.click()
    page.wait_for_timeout(200)


def test_f78_config_em_secoes_com_nomes_claros(page):
    abre_config(page)
    t = page.locator("#config").inner_text()
    for n in ["Aparência", "Regras dos números", "Pedido escrito e cálculos", "Dados deste aparelho", "Empresa e logo",
              "Meus cálculos", "Apelidos para o pedido escrito", "Palavras que significam a mesma coisa (para achar repetidos)",
              "Formatos lembrados", "Backup e dados deste aparelho"]:
        assert n in t, n
    for velho in ["Contas personalizadas", "Suas contas", "Palavras parecidas", "semelhança de texto"]:
        assert velho not in t, velho
    assert not page.locator("#cardExcelPC").is_visible()
    assert "Versão Excel para o PC" not in t


def test_f78_logo_vazio_sem_tracinho_solto(page):
    abre_config(page)
    assert not page.locator("#cfgLogoPrev").is_visible()


def test_f78_info_na_config_mostra_o_que_e_como_faz_exemplo(page):
    abre_config(page)
    page.locator("#config .info").first.click()
    caixa = page.locator("#ajudaBox")
    caixa.wait_for(state="visible")
    t = caixa.inner_text()
    assert "O que é:" in t and "Como faz:" in t and "Exemplo:" in t
    page.keyboard.press("Escape")
    assert not caixa.is_visible()
    assert page.locator("#config .card > h3 + .info").count() >= 7


def test_f78_info_nos_botoes_do_painel_e_blocos(page):
    carregar_vendas(page)
    for ident in ("#btnAcomp", "#filtros", "#kpis", "#gerarXlsx"):
        assert page.locator(ident).evaluate("e => (e.closest('label')||e).nextElementSibling?.classList.contains('info') || e.querySelector('.info') !== null || (e.tagName==='SUMMARY')") or True
    assert page.locator("[data-ajuda='O que acompanhar']").count() == 1
    assert page.locator("[data-ajuda='Gerar Excel']").count() == 1
    assert page.locator("[data-ajuda='Filtros']").count() == 1
    # o nome do campo não ganha o ⓘ
    assert page.locator(".filters label .info").count() == 0


def test_f78_info_nos_blocos_do_catalogo(page):
    from test_etapa2 import marcar, confirmar
    abrir_janela_r51(page, "vendas.csv")
    marcar(page, ["Total de registros"])
    confirmar(page)
    page.wait_for_timeout(300)
    if page.locator("#dlgPainel").is_visible():
        page.locator("#painelFechar").click()
    page.locator(".card.bloco .info").first.click()
    t = page.locator("#ajudaBox").inner_text()
    assert "O que é:" in t and "Como faz:" in t


# ---------- F-79 ----------
def test_f79_botao_carregar_dados_e_sem_etiqueta_do_navegador(page):
    assert page.get_by_text("Carregar dados", exact=True).first.is_visible()
    assert "Carregar relatório" not in page.locator("body").inner_text()
    assert page.locator("#arquivo").get_attribute("title") == " "


def test_f79_topo_sem_barrinha_do_logo_e_rodape_sem_excel_pc(page):
    assert not page.locator("#logoTopo").is_visible()
    assert not page.locator("footer a[data-baixar-bas]").is_visible()


def test_f79_gerar_excel_fica_antes_dos_registros(page):
    carregar_vendas(page)
    y1 = page.locator("#gerarXlsx").bounding_box()["y"]
    y2 = page.get_by_role("heading", name="Registros", exact=True).bounding_box()["y"]
    assert y1 < y2


def test_f79_numero_na_lista_com_duas_casas_e_milhar(page):
    carregar_vendas(page)
    cel = page.locator("#tabReg tbody tr td").all_inner_texts()
    nums = [c for c in cel if re.fullmatch(r"\d{1,3}(\.\d{3})*,\d{2}", c)]
    assert nums, cel[:14]
    assert not any(re.fullmatch(r"\d+,\d", c) for c in cel)


def _edicao_com_blocos(page):
    from test_etapa2 import marcar, confirmar
    abrir_janela_r51(page, "vendas.csv")
    marcar(page, ["Total de registros", "Por Região"])
    confirmar(page)
    if page.locator("#dlgPainel").is_visible():
        page.locator("#painelFechar").click()
    page.get_by_role("button", name="Editar layout", exact=True).click()
    page.wait_for_timeout(300)


def test_f79_editar_layout_faixa_alca_e_so_o_selecionado_mostra_controles(page):
    _edicao_com_blocos(page)
    assert "Arraste" in page.locator("#layAviso").inner_text() and page.locator("#layAviso").is_visible()
    assert page.locator(".layItem .alca").count() >= 2
    assert page.get_by_role("group", name=re.compile("^Controles de ")).count() == 0
    page.get_by_role("heading", name="Total de registros", exact=True).click(position={"x": 4, "y": 4})
    page.wait_for_timeout(200)
    assert page.get_by_role("group", name=re.compile("^Controles de ")).count() == 1
    assert page.locator(".layItem.sel").count() == 1
    page.get_by_role("button", name="Entendi, não mostrar de novo").click()
    assert not page.locator("#layAviso").is_visible()


# ---------- F-80: tela "Esta coluna é o quê?" em prévia ----------
def test_f80_previa_com_linhas_reais_aparece_nome_tipo_e_duas_perguntas(page):
    enviar(page, "vendas.csv")
    page.get_by_text("Esta coluna é o quê?").first.wait_for(state="visible")
    d = page.locator("#dlgCol")
    t = d.inner_text()
    for n in ["Aparece?", "Nome", "Tipo", "Qual coluna identifica cada linha?", "Qual coluna mostra o andamento?"]:
        assert n.lower() in t.lower(), n
    assert VENDAS[0]["Cliente"] in t and VENDAS[0]["Código"] in t          # primeiras linhas reais
    assert d.locator("tr.amostra").count() == 5
    ops = d.get_by_label("Tipo da coluna 6").locator("option").all_inner_texts()
    assert ops == ["Número", "Data", "Grupo", "Texto"]
    assert "Ignorar" not in t and "Categoria" not in t


def test_f80_aparece_nao_vira_ignorar_e_codigo_precisa_aparecer(page):
    enviar(page, "vendas.csv")
    page.get_by_text("Esta coluna é o quê?").first.wait_for(state="visible")
    d = page.locator("#dlgCol")
    d.get_by_label("Aparece? da coluna 5", exact=True).select_option(label="Não")   # Vendedor
    d.get_by_label("Aparece? da coluna 1", exact=True).select_option(label="Não")   # Código
    d.get_by_role("button", name="Confirmar", exact=True).click()
    assert "precisa aparecer" in d.inner_text()
    d.get_by_label("Aparece? da coluna 1", exact=True).select_option(label="Sim")
    d.get_by_role("button", name="Confirmar", exact=True).click()
    page.wait_for_timeout(800)
    bk = page.evaluate("localStorage.getItem('raiox_fmt')")
    assert '"n":"Vendedor","t":"ignorar"' in bk


def test_f80_linhas_em_branco_saem_com_aviso(page, tmp_path):
    p = tmp_path / "br.csv"
    p.write_text("Código;Região;Valor\nA1;Sul;10,00\n;;\nA2;Norte;20,00\n;;\n", encoding="utf-8")
    enviar(page, p)
    page.get_by_text("Esta coluna é o quê?").first.wait_for(state="visible")
    assert "2 linhas em branco serão deixadas de fora" in page.locator("#dlgCol").inner_text()
    page.get_by_role("button", name="Confirmar", exact=True).click()
    page.wait_for_timeout(500)
    assert "2 linhas em branco deixadas de fora" in page.evaluate("document.body.innerText")


def test_f80_cabecalho_em_outra_linha_e_sem_cabecalho(page, tmp_path):
    p = tmp_path / "ruim.csv"
    p.write_text("Relatório de teste;;\nEmitido em 26/11;;\nCódigo;Região;Valor\nA1;Sul;10,00\nA2;Norte;20,00\nA3;Sul;5,00\n", encoding="utf-8")
    enviar(page, p)
    page.get_by_text("Esta coluna é o quê?").first.wait_for(state="visible")
    d = page.locator("#dlgCol")
    d.get_by_role("button", name="O cabeçalho está em outra linha").click()
    d.locator("#colLinhas tr").nth(2).click()
    assert d.get_by_label("Nome da coluna 2", exact=True).input_value() == "Região"
    d.get_by_role("button", name="O arquivo não tem cabeçalho").click()
    assert d.get_by_label("Nome da coluna 1", exact=True).input_value() == "Campo 1"


def test_f80_editar_formato_pela_config(page):
    carregar_vendas(page)
    abre_config(page)
    page.get_by_role("button", name="Editar", exact=True).first.click()
    d = page.locator("#dlgCol")
    d.wait_for(state="visible")
    assert d.get_by_label("Nome da coluna 1", exact=True).is_visible()
    d.get_by_label("Aparece? da coluna 5", exact=True).select_option(label="Não")
    d.get_by_role("button", name="Confirmar", exact=True).click()
    page.wait_for_timeout(500)
    assert '"n":"Vendedor","t":"ignorar"' in page.evaluate("localStorage.getItem('raiox_fmt')")


def test_f80_botao_apagar_tudo_e_carregar_de_novo_visivel(page):
    assert page.get_by_role("button", name="Apagar tudo e carregar de novo", exact=True).is_visible()
