"""Suite da etapa 6 (CA-60 a CA-66, Editar layout). Escrita SO a partir da especificacao v1.6
(secoes 0.5, 0.7 e 6). Seletores pelos rotulos R-100..R-108. Oraculos em Python sobre tests/dados/.

Suposicoes (texto mais literal):
 S1 o layout no backup fica em b["layout"][<id do conjunto>] (mesma chave de b["conjs"]), com {abas, itens}.
 S2 apos 'Nova aba' nao se assume qual aba fica aberta: os testes clicam na aba pelo nome.
 S3 a ordem das planilhas do Excel segue a ordem das abas (inclusive depois de 'Aba a esquerda').
 S4 a cartao/bloco 'Controles de <titulo>' e o grupo role=group; o valor do bloco e lido subindo do heading.
 S5 apos 'Mover para…' o bloco some da aba aberta (a aba aberta nao muda).
 S6 'Voltar ao padrao' apaga o layout do conjunto: nao ha mais b["layout"][conjunto] no backup.
 S7 'Duplicar' um bloco: a copia tem o mesmo titulo (heading) do original.
"""
import json, re
import pytest
from conftest import URL
from test_etapa1 import (le_csv, carregar, backup, abrir_config, abrir_painel, enviar, mapear_se_preciso,
                         codigos_no_backup)
from test_etapa2 import dlg, abrir_janela_r51, marcar, confirmar, fechar_seu_painel, texto_seu_painel, JANELA
from test_etapa4 import gerar, parse_painel

VENDAS = le_csv("vendas.csv")
N = len(VENDAS)
N_BR = f"{N:,}".replace(",", ".")
REGIOES = sorted({r["Região"] for r in VENDAS})
CONT_REG = {g: sum(1 for r in VENDAS if r["Região"] == g) for g in REGIOES}

TOTAL = "Total de registros"
VALOR = "Valor (soma, média e mediana)"
REG = "Por Região"
CLI = "Por Cliente"
PADRAO = [TOTAL, VALOR, REG]            # ordem de tela da etapa 2: numeros, depois graficos
AVISO_PIZZA = "Pizza com mais de 8 fatias: mostrando barras"


# ---------- auxiliares ----------
def preparar(page, extra=None, arquivo="vendas.csv"):
    abrir_janela_r51(page, arquivo)
    marcar(page, (extra or [TOTAL, REG, VALOR]))
    confirmar(page)
    fechar_seu_painel(page)


def vis(loc):
    return [e for e in loc.all() if e.is_visible()]


def heading(page, nome):
    return vis(page.get_by_role("heading", name=nome, exact=True))


def ordem(page, nomes=PADRAO):
    """Titulos (dos conhecidos) visiveis, na ordem da tela (y, depois x)."""
    achados = []
    for n in nomes:
        for h in heading(page, n):
            b = h.bounding_box()
            achados.append((round(b["y"]), round(b["x"]), n))
    return [n for _, _, n in sorted(achados)]


def edicao(page, ligar=True):
    alvo = "Editar layout" if ligar else "Concluir edição"
    page.get_by_role("button", name=alvo, exact=True).click()
    page.wait_for_timeout(300)


def em_edicao(page):
    return page.get_by_role("button", name="Concluir edição", exact=True).count() > 0


def grupo(page, nome, n=0):
    g = page.get_by_role("group", name=f"Controles de {nome}", exact=True)
    return vis(g)[n]


def clicar(page, nome, botao, n=0):
    grupo(page, nome, n).get_by_role("button", name=botao, exact=True).click()
    page.wait_for_timeout(250)


def sel(page, nome, rotulo, n=0):
    return grupo(page, nome, n).get_by_label(rotulo, exact=True)


def escolhido(s):
    return s.evaluate("e => e.selectedOptions[0].textContent.trim()")


def opcoes(s):
    return [o.strip() for o in s.locator("option").all_inner_texts() if o.strip()]


def nav(page):
    return page.get_by_role("navigation", name="Abas do painel")


def abas(page):
    return [t.strip() for t in nav(page).get_by_test_id("aba").all_inner_texts()]


def abrir_aba(page, nome):
    nav(page).get_by_test_id("aba").filter(has_text=re.compile(r"^\s*" + re.escape(nome) + r"\s*$")).first.click()
    page.wait_for_timeout(250)


def janela_nome(page):
    return page.locator("dialog, [role=dialog]").filter(has=page.get_by_label("Nome da aba", exact=True)).first


def alerta(page):
    al = page.get_by_role("alert").filter(has_text=re.compile(r"\S"))
    return " ".join(re.sub(r"\s+", " ", t).strip() for t in al.all_inner_texts()).lower()


def nova_aba(page, nome, salvar=True):
    page.get_by_role("button", name="Nova aba", exact=True).click()
    j = janela_nome(page)
    j.wait_for(state="visible")
    page.get_by_label("Nome da aba", exact=True).fill(nome)
    if salvar:
        j.get_by_role("button", name="Salvar", exact=True).click()
        page.wait_for_timeout(300)


def mover(page, bloco, aba, n=0):
    sel(page, bloco, "Mover para…", n).select_option(label=aba)
    page.wait_for_timeout(300)


def texto_cartao(page, nome, n=0):
    """Texto do cartao: sobe do heading ate o 1o ancestral que traz algo alem do titulo."""
    h = heading(page, nome)[n]
    return re.sub(r"\s+", " ", h.evaluate("""h => { let t = h.innerText, e = h;
        while (e.parentElement && e.innerText.replace(t, '').trim() === '') e = e.parentElement;
        return e.innerText; }"""))


def layout_do_backup(page):
    _, txt = backup(page)
    b = json.loads(txt)
    return b, list(b["conjs"].keys())[0]


def excel(page, tmp_path, formato=None):
    wb = gerar(page, tmp_path, formato)
    return wb


def titulos_planilha(wb, nome="Painel"):
    return [b["titulo"] for b in parse_painel(wb[nome])["blocos"]]


def reabrir(page):
    page.reload()
    page.wait_for_timeout(1000)


def restaurar(page, texto, botao="Substituir"):
    abrir_config(page)
    with page.expect_file_chooser() as fc:
        page.get_by_role("button", name="Restaurar backup").click()
    fc.value.set_files([{"name": "b.json", "mimeType": "application/json", "buffer": texto.encode()}])
    page.wait_for_timeout(500)
    if botao:
        page.get_by_role("button", name=botao, exact=True).click()
        page.wait_for_timeout(800)


@pytest.fixture()
def celular(browser):
    c = browser.new_context(viewport={"width": 390, "height": 844}, accept_downloads=True)
    c.set_default_timeout(4000)
    pg = c.new_page()
    pg.goto(URL)
    pg.wait_for_timeout(800)
    yield pg
    c.close()


# ---------- regra de ouro (R-100, 0.7) ----------
def test_regra_de_ouro_sem_blocos_escolhidos_nao_ha_editar_layout(page):
    carregar(page, "vendas.csv")        # fecha a janela com Cancelar: painel padrao
    abrir_painel(page)
    assert page.get_by_role("button", name="Editar layout", exact=True).count() == 0
    assert nav(page).count() == 0 or not nav(page).is_visible()


def test_regra_de_ouro_com_blocos_escolhidos_aparece_e_nao_muda_a_tela(page, tmp_path):
    preparar(page)
    assert page.get_by_role("button", name="Editar layout", exact=True).is_visible()
    antes = ordem(page)
    assert antes == PADRAO, antes
    assert nav(page).count() == 0 or not nav(page).is_visible()      # 1 aba e sem edicao: sem barra
    edicao(page)
    edicao(page, False)
    assert ordem(page) == PADRAO
    wb = excel(page, tmp_path)
    assert wb.sheetnames == ["Capa", "Como ler este relatório", "Painel", "vendas"], wb.sheetnames
    assert titulos_planilha(wb) == PADRAO


def test_modo_edicao_nao_se_guarda_ao_recarregar(page):
    preparar(page)
    edicao(page)
    assert em_edicao(page)
    reabrir(page)
    assert page.get_by_role("button", name="Editar layout", exact=True).is_visible()
    assert not em_edicao(page)


def test_controles_so_aparecem_em_modo_edicao(page):
    preparar(page)
    assert page.get_by_role("group", name=re.compile("^Controles de ")).count() == 0
    edicao(page)
    for t in PADRAO:
        g = grupo(page, t)
        for b in ("Subir", "Descer", "Esconder", "Duplicar"):
            assert g.get_by_role("button", name=b, exact=True).count() == 1, (t, b)
        for s in ("Mover para…", "Tamanho", "Forma"):
            assert g.get_by_label(s, exact=True).count() == 1, (t, s)
    edicao(page, False)
    assert page.get_by_role("group", name=re.compile("^Controles de ")).count() == 0


def test_subir_no_primeiro_e_descer_no_ultimo_desabilitados(page):
    preparar(page)
    edicao(page)
    assert grupo(page, PADRAO[0]).get_by_role("button", name="Subir", exact=True).is_disabled()
    assert grupo(page, PADRAO[-1]).get_by_role("button", name="Descer", exact=True).is_disabled()
    assert grupo(page, PADRAO[1]).get_by_role("button", name="Subir", exact=True).is_enabled()


# ---------- CA-60 ----------
def test_CA60_mover_B_acima_de_A_tela_recarregar_e_excel(page, tmp_path):
    preparar(page)
    edicao(page)
    clicar(page, VALOR, "Subir")                       # B = Valor sobe acima de A = Total
    esperado = [VALOR, TOTAL, REG]
    assert ordem(page) == esperado
    edicao(page, False)
    assert ordem(page) == esperado
    reabrir(page)
    assert ordem(page) == esperado, "ordem perdida ao recarregar"
    wb = excel(page, tmp_path)
    assert titulos_planilha(wb) == esperado, titulos_planilha(wb)
    assert page.evaluate('() => window.__abasPainel("vendas")') == [{"nome": "Painel", "blocos": esperado}]


def test_CA60_descer_troca_com_o_seguinte_e_nao_mexe_nos_outros(page):
    preparar(page)
    edicao(page)
    clicar(page, TOTAL, "Descer")
    assert ordem(page) == [VALOR, TOTAL, REG]
    clicar(page, TOTAL, "Descer")
    assert ordem(page) == [VALOR, REG, TOTAL]


def test_regra8_arrastar_bloco_sobre_outro_ocupa_o_lugar_dele(page):
    preparar(page)
    edicao(page)
    origem = page.locator('[draggable="true"]').filter(has=page.get_by_role("heading", name=REG, exact=True)).first
    alvo = page.locator('[draggable="true"]').filter(has=page.get_by_role("heading", name=TOTAL, exact=True)).first
    origem.drag_to(alvo)
    page.wait_for_timeout(300)
    assert ordem(page) == [REG, TOTAL, VALOR], ordem(page)


def test_regra8_arrastar_bloco_ate_o_botao_de_outra_aba_vai_para_o_fim_dela(page):
    preparar(page)
    edicao(page)
    nova_aba(page, "Reunião")
    abrir_aba(page, "Painel")
    origem = page.locator('[draggable="true"]').filter(has=page.get_by_role("heading", name=TOTAL, exact=True)).first
    origem.drag_to(nav(page).get_by_test_id("aba").filter(has_text="Reunião").first)
    page.wait_for_timeout(300)
    assert TOTAL not in ordem(page)
    abrir_aba(page, "Reunião")
    assert ordem(page) == [TOTAL]


# ---------- CA-61 / CA-62 ----------
def test_CA61_criar_aba_e_mover_dois_blocos_para_ela(page, tmp_path):
    preparar(page)
    edicao(page)
    nova_aba(page, "Reunião")
    assert abas(page) == ["Painel", "Reunião"]
    abrir_aba(page, "Painel")
    mover(page, TOTAL, "Reunião")
    mover(page, REG, "Reunião")
    assert ordem(page) == [VALOR]                       # nao na aba de origem
    abrir_aba(page, "Reunião")
    assert ordem(page) == [TOTAL, REG]                  # aparecem la
    edicao(page, False)
    assert abas(page) == ["Painel", "Reunião"]          # 2 abas: a barra fica fora da edicao
    abrir_aba(page, "Painel")
    assert ordem(page) == [VALOR]
    reabrir(page)
    abrir_aba(page, "Reunião")
    assert ordem(page) == [TOTAL, REG]
    wb = excel(page, tmp_path)
    assert wb.sheetnames == ["Capa", "Como ler este relatório", "Painel", "Reunião", "vendas"], wb.sheetnames
    assert titulos_planilha(wb, "Painel") == [VALOR]
    assert titulos_planilha(wb, "Reunião") == [TOTAL, REG]
    assert wb["Reunião"]["A1"].value == "Reunião"


def _com_reuniao(page):
    preparar(page)
    edicao(page)
    nova_aba(page, "Reunião")
    abrir_aba(page, "Painel")
    mover(page, TOTAL, "Reunião")
    mover(page, REG, "Reunião")
    abrir_aba(page, "Reunião")


def test_CA62_apagar_aba_confirmando_blocos_voltam_para_a_primeira(page, tmp_path):
    _com_reuniao(page)
    page.get_by_role("button", name="Apagar aba", exact=True).click()
    d = dlg(page, "Apagar a aba Reunião?")
    d.wait_for(state="visible")
    assert "Os 2 blocos dela vão para a primeira aba." in re.sub(r"\s+", " ", d.inner_text())
    d.get_by_role("button", name="Apagar", exact=True).click()
    page.wait_for_timeout(300)
    assert abas(page) == ["Painel"]
    assert ordem(page) == [VALOR, TOTAL, REG]           # no fim da 1a aba, na ordem em que estavam
    edicao(page, False)
    assert nav(page).count() == 0 or not nav(page).is_visible()
    wb = excel(page, tmp_path)
    assert "Reunião" not in wb.sheetnames
    assert titulos_planilha(wb) == [VALOR, TOTAL, REG]


def test_CA62_sem_confirmar_nada_muda(page):
    _com_reuniao(page)
    page.get_by_role("button", name="Apagar aba", exact=True).click()
    d = dlg(page, "Apagar a aba Reunião?")
    d.wait_for(state="visible")
    d.get_by_role("button", name="Cancelar", exact=True).click()
    page.wait_for_timeout(300)
    assert abas(page) == ["Painel", "Reunião"]
    assert ordem(page) == [TOTAL, REG]
    abrir_aba(page, "Painel")
    assert ordem(page) == [VALOR]


def test_apagar_aba_vazia_pergunta_sem_texto_dos_blocos(page):
    preparar(page)
    edicao(page)
    nova_aba(page, "Vazia")
    abrir_aba(page, "Vazia")
    page.get_by_role("button", name="Apagar aba", exact=True).click()
    d = dlg(page, "Apagar a aba Vazia?")
    d.wait_for(state="visible")
    assert "vão para a primeira aba" not in d.inner_text()
    d.get_by_role("button", name="Apagar", exact=True).click()
    page.wait_for_timeout(300)
    assert abas(page) == ["Painel"]


def test_nao_apaga_a_ultima_aba(page):
    preparar(page)
    edicao(page)
    assert abas(page) == ["Painel"]                      # em edicao a barra aparece mesmo com 1 aba
    assert page.get_by_role("button", name="Apagar aba", exact=True).is_disabled()


# ---------- abas: barra, nomes, ordem ----------
def test_barra_de_abas_so_com_2_ou_mais_abas_ou_em_edicao(page):
    preparar(page)
    assert nav(page).count() == 0 or not nav(page).is_visible()
    edicao(page)
    assert nav(page).is_visible() and abas(page) == ["Painel"]
    for b in ("Nova aba", "Renomear aba", "Apagar aba", "Aba à esquerda", "Aba à direita"):
        assert page.get_by_role("button", name=b, exact=True).count() == 1, b
    nova_aba(page, "Reunião")
    edicao(page, False)
    assert nav(page).is_visible() and abas(page) == ["Painel", "Reunião"]
    for b in ("Nova aba", "Renomear aba", "Apagar aba", "Aba à esquerda", "Aba à direita"):
        assert page.get_by_role("button", name=b, exact=True).count() == 0, b


def test_nome_de_aba_invalido_vazio_e_repetido(page):
    preparar(page)
    edicao(page)
    nova_aba(page, "   ")
    assert "escreva o nome da aba" in alerta(page)
    page.get_by_label("Nome da aba", exact=True).fill("PAINEL")        # repetido sem diferenciar maiusculas
    janela_nome(page).get_by_role("button", name="Salvar", exact=True).click()
    assert "já existe uma aba com esse nome" in alerta(page)
    janela_nome(page).get_by_role("button", name="Cancelar", exact=True).click()
    page.wait_for_timeout(300)
    assert abas(page) == ["Painel"]
    nova_aba(page, "Reunião")
    nova_aba(page, "reuniao")                                          # sem diferenciar acentos
    assert "já existe uma aba com esse nome" in alerta(page)
    janela_nome(page).get_by_role("button", name="Cancelar", exact=True).click()
    page.wait_for_timeout(300)
    assert abas(page) == ["Painel", "Reunião"]


def test_nome_de_aba_ate_30_caracteres(page):
    preparar(page)
    edicao(page)
    nova_aba(page, "x" * 50, salvar=False)
    assert len(page.get_by_label("Nome da aba", exact=True).input_value()) <= 30


def test_nome_de_aba_com_html_vira_texto(page):
    dialogos = []
    page.on("dialog", lambda d: (dialogos.append(d.message), d.dismiss()))
    preparar(page)
    edicao(page)
    nome = "<img src=x onerror=alert(1)>"
    nova_aba(page, nome)
    assert nome in abas(page)
    assert nav(page).locator("img").count() == 0
    assert dialogos == []


def test_renomear_aba(page, tmp_path):
    _com_reuniao(page)
    page.get_by_role("button", name="Renomear aba", exact=True).click()
    j = janela_nome(page)
    j.wait_for(state="visible")
    page.get_by_label("Nome da aba", exact=True).fill("Painel")
    j.get_by_role("button", name="Salvar", exact=True).click()
    assert "já existe uma aba com esse nome" in alerta(page)
    page.get_by_label("Nome da aba", exact=True).fill("Equipe")
    j.get_by_role("button", name="Salvar", exact=True).click()
    page.wait_for_timeout(300)
    assert abas(page) == ["Painel", "Equipe"]
    edicao(page, False)
    wb = excel(page, tmp_path)
    assert "Equipe" in wb.sheetnames and "Reunião" not in wb.sheetnames
    assert titulos_planilha(wb, "Equipe") == [TOTAL, REG]


def test_aba_a_esquerda_e_a_direita_reordenam(page, tmp_path):
    _com_reuniao(page)
    page.get_by_role("button", name="Aba à esquerda", exact=True).click()
    page.wait_for_timeout(250)
    assert abas(page) == ["Reunião", "Painel"]
    page.get_by_role("button", name="Aba à direita", exact=True).click()
    page.wait_for_timeout(250)
    assert abas(page) == ["Painel", "Reunião"]
    page.get_by_role("button", name="Aba à esquerda", exact=True).click()
    page.wait_for_timeout(250)
    edicao(page, False)
    reabrir(page)
    assert abas(page) == ["Reunião", "Painel"]
    wb = excel(page, tmp_path)
    nomes = wb.sheetnames
    assert nomes.index("Reunião") < nomes.index("Painel"), nomes      # S3


# ---------- CA-63 ----------
def test_CA63_duplicar_bloco_mover_para_outra_aba_mesmo_valor(page):
    preparar(page, [TOTAL, REG, VALOR])
    edicao(page)
    nova_aba(page, "Reunião")
    abrir_aba(page, "Painel")
    for nome in (TOTAL, REG):
        clicar(page, nome, "Duplicar")
        assert len(heading(page, nome)) == 2, f"copia de {nome} deve ficar na mesma aba"   # S7 + regra 2
        mover(page, nome, "Reunião", n=1)                 # a copia vem logo depois do original
        assert len(heading(page, nome)) == 1
    edicao(page, False)
    t_a = texto_cartao(page, TOTAL)
    r_a = texto_cartao(page, REG)
    abrir_aba(page, "Reunião")
    assert texto_cartao(page, TOTAL) == t_a
    assert texto_cartao(page, REG) == r_a
    assert N_BR in t_a, (t_a, N_BR)                                   # oraculo: total de registros
    for g, c in CONT_REG.items():
        assert g in r_a and str(c) in r_a, (g, c, r_a)


def test_regra2_duplicar_cria_copia_logo_depois_do_original(page, tmp_path):
    preparar(page)
    edicao(page)
    clicar(page, TOTAL, "Duplicar")
    assert ordem(page) == [TOTAL, TOTAL, VALOR, REG]
    edicao(page, False)
    wb = excel(page, tmp_path)
    assert titulos_planilha(wb) == [TOTAL, TOTAL, VALOR, REG]
    assert page.evaluate('() => window.__abasPainel("vendas")')[0]["blocos"] == [TOTAL, TOTAL, VALOR, REG]


def test_regra4_desmarcar_indicador_tira_todas_as_copias_e_novo_entra_no_fim(page):
    preparar(page)
    edicao(page)
    clicar(page, TOTAL, "Duplicar")
    edicao(page, False)
    page.get_by_role("button", name="O que acompanhar", exact=True).click()
    marcar(page, [VALOR, REG])
    confirmar(page)
    fechar_seu_painel(page)
    assert ordem(page) == [VALOR, REG]
    page.get_by_role("button", name="O que acompanhar", exact=True).click()
    marcar(page, [VALOR, REG, TOTAL])
    confirmar(page)
    fechar_seu_painel(page)
    assert ordem(page) == [VALOR, REG, TOTAL], ordem(page)            # indicador novo entra no fim da 1a aba


# ---------- Tamanho ----------
def test_tamanho_opcoes_padrao_e_efeito_na_tela(page):
    preparar(page)
    edicao(page)
    s = sel(page, TOTAL, "Tamanho")
    assert opcoes(s) == ["Pequeno", "Médio", "Grande"]
    assert escolhido(s) == "Médio"
    for t in PADRAO:
        sel(page, t, "Tamanho").select_option(label="Pequeno")
    page.wait_for_timeout(300)
    ys = [heading(page, t)[0].bounding_box() for t in PADRAO]
    assert len({round(b["y"]) // 10 for b in ys}) < len(PADRAO), "3 blocos pequenos deveriam dividir a linha"
    sel(page, VALOR, "Tamanho").select_option(label="Grande")
    page.wait_for_timeout(300)
    yv = heading(page, VALOR)[0].bounding_box()["y"]
    outros = [heading(page, t)[0].bounding_box()["y"] for t in (TOTAL, REG)]
    assert all(abs(yv - y) > 10 for y in outros), "bloco grande ocupa a linha toda"
    edicao(page, False)
    reabrir(page)
    edicao(page)
    assert escolhido(sel(page, VALOR, "Tamanho")) == "Grande"
    assert escolhido(sel(page, TOTAL, "Tamanho")) == "Pequeno"


def test_tamanho_nao_muda_o_excel(page, tmp_path):
    preparar(page)
    edicao(page)
    for t in PADRAO:
        sel(page, t, "Tamanho").select_option(label="Grande")
    edicao(page, False)
    wb = excel(page, tmp_path)
    assert titulos_planilha(wb) == PADRAO


# ---------- Esconder / Mostrar (R-108) ----------
def test_esconder_some_fora_da_edicao_do_seu_painel_e_do_excel_e_mostrar_volta(page, tmp_path):
    preparar(page)
    edicao(page)
    clicar(page, TOTAL, "Esconder")
    esc = page.locator('[data-escondido="true"]')
    assert len(vis(esc)) == 1                                          # em edicao: esmaecido, ainda na tela
    assert grupo(page, TOTAL).get_by_role("button", name="Mostrar", exact=True).is_visible()
    assert grupo(page, TOTAL).get_by_role("button", name="Esconder", exact=True).count() == 0
    edicao(page, False)
    assert heading(page, TOTAL) == []
    assert page.locator('[data-escondido="true"]').count() == 0 or not vis(page.locator('[data-escondido="true"]'))
    page.get_by_role("button", name="Entender este painel", exact=True).click()
    assert TOTAL + " —" not in texto_seu_painel(page)
    fechar_seu_painel(page)
    wb = excel(page, tmp_path)
    assert titulos_planilha(wb) == [VALOR, REG]
    reabrir(page)
    assert heading(page, TOTAL) == []
    edicao(page)
    clicar(page, TOTAL, "Mostrar")
    edicao(page, False)
    assert ordem(page) == PADRAO


def test_aba_sem_blocos_visiveis_nao_gera_planilha(page, tmp_path):
    preparar(page)
    edicao(page)
    nova_aba(page, "Reunião")
    abrir_aba(page, "Painel")
    mover(page, TOTAL, "Reunião")
    abrir_aba(page, "Reunião")
    clicar(page, TOTAL, "Esconder")
    edicao(page, False)
    wb = excel(page, tmp_path)
    assert "Reunião" not in wb.sheetnames and "Painel" in wb.sheetnames, wb.sheetnames    # CA-44


# ---------- Forma (R-105) ----------
def test_forma_opcoes_por_tipo_de_bloco(page):
    preparar(page, [TOTAL, VALOR, REG, "Valor por Região", "Evolução por mês (Data)"])
    edicao(page)
    assert opcoes(sel(page, TOTAL, "Forma")) == ["Número"]
    assert opcoes(sel(page, VALOR, "Forma")) == ["Número"]
    assert set(opcoes(sel(page, REG, "Forma"))) == {"Barras", "Pizza", "Tabela"}
    assert set(opcoes(sel(page, "Valor por Região", "Forma"))) == {"Barras", "Pizza", "Tabela"}
    assert set(opcoes(sel(page, "Evolução por mês (Data)", "Forma"))) == {"Barras", "Linha", "Pizza", "Tabela"}
    assert escolhido(sel(page, TOTAL, "Forma")) == "Número"
    assert escolhido(sel(page, REG, "Forma")) == "Barras"             # forma de origem = padrao


def test_forma_tabela_mostra_os_numeros_do_oraculo_e_persiste(page, tmp_path):
    preparar(page)
    edicao(page)
    sel(page, REG, "Forma").select_option(label="Tabela")
    page.wait_for_timeout(300)
    txt = texto_cartao(page, REG)
    for g, c in CONT_REG.items():
        assert g in txt and str(c) in txt, (g, c, txt)
    reabrir(page)
    edicao(page)
    assert escolhido(sel(page, REG, "Forma")) == "Tabela"
    edicao(page, False)
    wb = excel(page, tmp_path)                                         # o dado do Excel nao muda
    assert titulos_planilha(wb) == PADRAO


def test_forma_pizza_com_mais_de_8_fatias_vira_barras_com_aviso(page):
    preparar(page, [TOTAL, CLI])
    edicao(page)
    assert len({r["Cliente"] for r in VENDAS}) > 8                    # oraculo: 10 clientes
    assert AVISO_PIZZA not in page.locator("body").inner_text()
    sel(page, CLI, "Forma").select_option(label="Pizza")
    page.wait_for_timeout(300)
    assert AVISO_PIZZA in page.locator("body").inner_text()
    assert AVISO_PIZZA in texto_cartao(page, CLI)


def test_forma_pizza_com_ate_8_fatias_sem_aviso(page):
    preparar(page)
    edicao(page)
    assert len(CONT_REG) <= 8
    sel(page, REG, "Forma").select_option(label="Pizza")
    page.wait_for_timeout(300)
    assert AVISO_PIZZA not in page.locator("body").inner_text()
    assert escolhido(sel(page, REG, "Forma")) == "Pizza"


# ---------- CA-64 ----------
def _bagunca(page):
    nova_aba(page, "Reunião")
    abrir_aba(page, "Painel")
    clicar(page, VALOR, "Subir")
    clicar(page, TOTAL, "Duplicar")
    clicar(page, REG, "Esconder")
    sel(page, VALOR, "Tamanho").select_option(label="Pequeno")
    sel(page, REG, "Forma").select_option(label="Tabela")
    mover(page, TOTAL, "Reunião", n=1)


def test_CA64_voltar_ao_padrao_com_confirmacao(page, tmp_path):
    preparar(page)
    edicao(page)
    _bagunca(page)
    assert ordem(page) != PADRAO or abas(page) != ["Painel"]
    page.get_by_role("button", name="Voltar ao padrão", exact=True).click()
    d = dlg(page, "Voltar ao padrão?")
    d.wait_for(state="visible")
    d.get_by_role("button", name="Voltar ao padrão", exact=True).click()
    page.wait_for_timeout(400)
    assert abas(page) == ["Painel"]
    assert ordem(page) == PADRAO                                       # igual ao da etapa 2
    assert escolhido(sel(page, VALOR, "Tamanho")) == "Médio"
    assert escolhido(sel(page, REG, "Forma")) == "Barras"
    assert page.locator('[data-escondido="true"]').count() == 0
    edicao(page, False)
    assert nav(page).count() == 0 or not nav(page).is_visible()
    wb = excel(page, tmp_path)
    assert wb.sheetnames == ["Capa", "Como ler este relatório", "Painel", "vendas"]
    assert titulos_planilha(wb) == PADRAO
    b, cj = layout_do_backup(page)
    assert cj not in b.get("layout", {}), b.get("layout")             # S6


def test_CA64_cancelar_nao_muda_nada(page):
    preparar(page)
    edicao(page)
    _bagunca(page)
    depois = ordem(page)
    page.get_by_role("button", name="Voltar ao padrão", exact=True).click()
    d = dlg(page, "Voltar ao padrão?")
    d.wait_for(state="visible")
    d.get_by_role("button", name="Cancelar", exact=True).click()
    page.wait_for_timeout(300)
    assert ordem(page) == depois
    assert abas(page) == ["Painel", "Reunião"]


def test_layout_vale_por_conjunto(page):
    preparar(page)
    edicao(page)
    clicar(page, VALOR, "Subir")
    edicao(page, False)
    enviar(page, "chamados.csv")
    mapear_se_preciso(page)
    dlg(page, JANELA).wait_for(state="visible")
    marcar(page, ["Total de registros"])
    confirmar(page)
    fechar_seu_painel(page)
    b, _ = layout_do_backup(page)
    assert len(b["conjs"]) == 2
    assert len(b["layout"]) == 1, "so o conjunto editado tem layout"


# ---------- CA-65 ----------
def _layout_editado(page):
    edicao(page)
    nova_aba(page, "Reunião")
    abrir_aba(page, "Painel")
    clicar(page, VALOR, "Subir")
    mover(page, REG, "Reunião")
    clicar(page, TOTAL, "Esconder")
    sel(page, VALOR, "Tamanho").select_option(label="Grande")
    edicao(page, False)


def _estado(page):
    """Tudo o que o layout muda na tela (abas, ordem por aba, escondido)."""
    est = {}
    for a in abas(page):
        abrir_aba(page, a)
        est[a] = ordem(page)
    return est


def test_CA65_backup_apagar_restaurar_substituir_mesmo_layout(page):
    preparar(page)
    _layout_editado(page)
    antes = _estado(page)
    assert antes == {"Painel": [VALOR], "Reunião": [REG]}, antes
    nome, txt = backup(page)
    b = json.loads(txt)
    cj = list(b["conjs"].keys())[0]
    assert "layout" in b and cj in b["layout"]
    lay = b["layout"][cj]
    assert [a["nome"] for a in lay["abas"]] == ["Painel", "Reunião"]
    assert len(lay["itens"]) == 3
    assert sum(1 for i in lay["itens"] if i["oculto"] is True) == 1
    assert {"k", "id", "aba", "tam", "oculto", "forma"} <= set(lay["itens"][0])
    # apagar tudo
    abrir_config(page)
    page.get_by_role("button", name="Apagar todos os dados").click()
    page.get_by_role("button", name="Apagar", exact=True).click()
    page.wait_for_timeout(500)
    vazio_txt = backup(page)[1]
    assert len(set(codigos_no_backup(vazio_txt))) == 0
    assert not json.loads(vazio_txt).get("layout")
    # restaurar com Substituir
    restaurar(page, txt, "Substituir")
    if dlg(page, JANELA).count() and dlg(page, JANELA).is_visible():
        pytest.fail("a janela 'O que você quer acompanhar?' reabriu depois de restaurar")
    abrir_painel(page)
    assert _estado(page) == antes
    b2, cj2 = layout_do_backup(page)
    assert b2["layout"][cj2] == lay
    assert len(set(codigos_no_backup(json.dumps(b2)))) == N
    reabrir(page)
    assert _estado(page) == antes


def _forjado(page, mut):
    preparar(page)
    _layout_editado(page)
    _, txt = backup(page)
    b = json.loads(txt)
    cj = list(b["conjs"].keys())[0]
    mut(b, cj)
    restaurar(page, json.dumps(b), None)
    return b


def _abas_n(n):
    return [{"id": f"a{i}", "nome": f"Aba {i}"} for i in range(n)]


FORJADOS = {
    "layout_nao_e_objeto": lambda b, cj: b.__setitem__("layout", ["x"]),
    "abas_nao_e_lista": lambda b, cj: b["layout"][cj].__setitem__("abas", "x"),
    "itens_nao_e_lista": lambda b, cj: b["layout"][cj].__setitem__("itens", {"a": 1}),
    "item_sem_chave_k": lambda b, cj: b["layout"][cj]["itens"][0].pop("k"),
    "tamanho_invalido": lambda b, cj: b["layout"][cj]["itens"][0].__setitem__("tam", "Gigante"),
    "oculto_nao_booleano": lambda b, cj: b["layout"][cj]["itens"][0].__setitem__("oculto", "sim"),
    "aba_sem_nome": lambda b, cj: b["layout"][cj]["abas"][0].pop("nome"),
    "mais_de_20_abas": lambda b, cj: b["layout"][cj].__setitem__("abas", _abas_n(21)),
    "mais_de_200_itens": lambda b, cj: b["layout"][cj].__setitem__(
        "itens", [dict(b["layout"][cj]["itens"][0], k=f"k{i}") for i in range(201)]),
}


@pytest.mark.parametrize("caso", list(FORJADOS))
def test_CA65_backup_forjado_com_layout_de_formato_errado_e_rejeitado_inteiro(page, caso):
    _forjado(page, FORJADOS[caso])
    assert page.get_by_role("button", name="Substituir", exact=True).count() == 0
    assert page.get_by_role("button", name="Somar", exact=True).count() == 0
    assert "Nada foi alterado" in page.locator("body").inner_text()
    abrir_painel(page)
    assert abas(page) == ["Painel", "Reunião"]                         # layout atual intacto


def test_CA65_backup_com_20_abas_e_aceito(page):
    _forjado(page, lambda b, cj: b["layout"][cj].__setitem__("abas", _abas_n(20)))
    assert page.get_by_role("button", name="Substituir", exact=True).count() == 1


def test_CA65_indicador_que_nao_existe_mais_e_ignorado_nao_rejeita(page):
    def mut(b, cj):
        it = dict(b["layout"][cj]["itens"][0], k="fantasma", id="indicador-que-nao-existe")
        b["layout"][cj]["itens"].append(it)
    _forjado(page, mut)
    page.get_by_role("button", name="Substituir", exact=True).click()
    page.wait_for_timeout(800)
    abrir_painel(page)
    assert "indicador-que-nao-existe" not in page.locator("body").inner_text()
    todos = []
    for a in abas(page):
        abrir_aba(page, a)
        todos += ordem(page)
    assert sorted(todos) == sorted([VALOR, REG])                       # o Total segue escondido


def test_D32_somar_so_traz_layout_para_conjunto_sem_layout(page):
    # conjunto COM layout: o do backup nao entra
    preparar(page)
    edicao(page)
    nova_aba(page, "Atual")
    edicao(page, False)
    _, txt = backup(page)
    b = json.loads(txt)
    cj = list(b["conjs"].keys())[0]
    b["layout"][cj]["abas"][-1]["nome"] = "Do backup"
    restaurar(page, json.dumps(b), "Somar")
    abrir_painel(page)
    assert abas(page) == ["Painel", "Atual"], abas(page)


def test_D32_somar_traz_layout_quando_o_conjunto_nao_tem(page):
    preparar(page)
    edicao(page)
    nova_aba(page, "Reunião")
    edicao(page, False)
    _, txt = backup(page)
    page.reload()
    page.wait_for_timeout(500)
    abrir_config(page)
    page.get_by_role("button", name="Apagar todos os dados").click()
    page.get_by_role("button", name="Apagar", exact=True).click()
    page.wait_for_timeout(500)
    carregar(page, "vendas.csv")                                       # conjunto de volta, sem layout
    restaurar(page, txt, "Somar")
    abrir_painel(page)
    b2, cj = layout_do_backup(page)
    assert cj in b2.get("layout", {})
    assert "Reunião" in [a["nome"] for a in b2["layout"][cj]["abas"]]


# ---------- CA-66 ----------
def test_CA66_celular_subir_e_descer_mudam_a_ordem(celular):
    page = celular
    preparar(page)
    assert ordem(page) == PADRAO
    edicao(page)
    clicar(page, REG, "Subir")
    assert ordem(page) == [TOTAL, REG, VALOR]
    clicar(page, TOTAL, "Descer")
    assert ordem(page) == [REG, TOTAL, VALOR]
    edicao(page, False)
    assert ordem(page) == [REG, TOTAL, VALOR]
    assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth + 1")


def test_CA66_celular_blocos_pequenos_ocupam_a_largura_toda(celular):
    page = celular
    preparar(page)
    edicao(page)
    for t in PADRAO:
        sel(page, t, "Tamanho").select_option(label="Pequeno")
    page.wait_for_timeout(300)
    ys = sorted(round(heading(page, t)[0].bounding_box()["y"]) for t in PADRAO)
    assert all(b - a > 10 for a, b in zip(ys, ys[1:])), ys           # empilhados, um por linha
    assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth + 1")


def test_CA66_celular_nova_aba_e_mover_funcionam_sem_arrastar(celular):
    page = celular
    preparar(page)
    edicao(page)
    nova_aba(page, "Reunião")
    abrir_aba(page, "Painel")
    mover(page, TOTAL, "Reunião")
    abrir_aba(page, "Reunião")
    assert ordem(page) == [TOTAL]


# ---------- F-63: Médio e Baixos da revisão de segurança da etapa 6 (regressão) ----------
def test_f63_layout_invalido_no_navegador_descarta_so_o_relatorio_ruim(page):
    carregar(page, "vendas.csv")
    r = page.evaluate("""() => {
      const ok = { abas: [{ id: 'a1', nome: 'Painel' }], itens: [] };
      const ruim = { abas: [{ id: 'a1', nome: 'Painel' }], itens: Array.from({ length: 201 }, (_, i) => ({ k: 'k' + i, id: 'x' + i, aba: 'a1' })) };
      const t = layoutsLimpo({ A: ok, B: ruim }, true), s = layoutsLimpo({ A: ok, B: ruim });
      return [Object.keys(t || {}), s];
    }""")
    assert r[0] == ["A"] and r[1] is None


def test_f63_nome_de_aba_sem_invisiveis_nem_emoji_partido(page):
    carregar(page, "vendas.csv")
    r = page.evaluate("""() => [NOME_RUIM.test('a\\u2028b'), NOME_RUIM.test('a\\u061cb'), NOME_RUIM.test('a\\ud800b'), NOME_RUIM.test('ok \\ud83d\\ude00'),
      nomeAba({ worksheets: [] }, '\\ud83d\\ude00'.repeat(40))]""")
    assert r[:4] == [True, True, True, False]
    assert "�" not in r[4] and len(list(r[4])) <= 28
