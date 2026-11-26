"""Suite da etapa 7b (F-64): PDF com texto e janela 'Conferir leitura'. Escrita SO a partir da especificacao v1.8
(secoes 0.9 e 7: R-120 a R-125, regras 1-6, CA-73, CA-73b/c/d, CA-77, CA-110y; 0.8 para o que ja existe).
Oraculo: tests/dados/vendas.csv, conferido pela janela, pelo backup e pelos exemplos de 'O que você quer acompanhar?'.

Suposicoes (texto mais literal):
 S1 a janela e um <dialog>/[role=dialog] com aria-labelledby e o titulo 'Conferir leitura'; as celulas sao
    input[type=text] com aria-label 'Linha <n>, <coluna>' e 'Cabeçalho, coluna <j>'.
 S2 os textos 'Arquivo: <nome>.', 'Linhas lidas: <n>' e 'Células marcadas: <m>' ficam dentro da janela.
 S3 'Linhas lidas' conta as linhas de DADOS (500 para vendas.pdf), sem o cabeçalho.
 S4 as celulas do vendas.pdf trazem o mesmo texto do CSV (datas dd/mm/aaaa, numeros com virgula).
 S5 'menos de 2 linhas' e testado so com um PDF de UMA linha (so cabecalho), que falha em qualquer leitura da regra.
 S6 PDF corrompido = bytes cortados (30% iniciais de vendas.pdf); espera-se 'Não consegui ler <arquivo>.'.
 S7 offline: set_context offline apos o 1o carregamento; o app deve ter o leitor de PDF em cache local (service worker).
 S8 a ordem entre a janela do PDF e 'Esta coluna é o quê?' do CSV de um mesmo zip nao e fixada: os testes aceitam as duas.
 S9 PDF forjado (reportlab) com uma linha sem a celula do meio: a linha continua na tabela (2 pedacos) e a celula
    vazia vem com data-baixa='true'. Testes que precisam de reportlab sao pulados sem ele.
 S10 toasts sao capturados por MutationObserver (enviar_vendo_mensagens).
Nota: test_etapa7a.py ainda afirma que .pdf e 'formato não suportado' e que o accept nao tem .pdf; isso muda na 7b
(R-120) e o Galindo/Construtor deve atualizar aqueles dois testes.
"""
import re, io, collections
import pytest
from conftest import DADOS
from test_etapa1 import (le_csv, enviar, mapear_se_preciso, fechar_acompanhar, carregar, backup)
from test_etapa2 import dlg, JANELA
from test_etapa7a import (por_codigo, confere_vendas, confere_exemplos, mapear_tudo, fechar_todos, codigos,
                          enviar_vendo_mensagens, zip_bytes, grava, vivo, N, VENDAS, CHAMADOS)

CAB = ["Código", "Data", "Cliente", "Região", "Vendedor", "Valor", "Situação"]
TOAST_SEM_TABELA = "Não encontrei uma tabela neste arquivo"
skip_pdf = pytest.mark.skipif(not (DADOS / "vendas.pdf").exists(), reason="vendas.pdf nao gerado (sem reportlab)")


# ---------- auxiliares ----------
def conf(page):
    return page.locator("dialog, [role=dialog]").filter(has_text="Conferir leitura").first


def conf_visivel(page):
    return conf(page).is_visible()


def esperar_conf(page, timeout=25000):
    conf(page).wait_for(state="visible", timeout=timeout)
    return conf(page)


def grade(d):
    """label -> valor de todas as celulas da janela."""
    pares = d.locator("input[type=text][aria-label]").evaluate_all("els=>els.map(e=>[e.getAttribute('aria-label'),e.value])")
    return dict(pares)


def resolver(page, descartar=(), maximo=12):
    """Resolve o que aparecer: conferencia (Confirmar, ou Descartar na ordem dada) e 'Esta coluna é o quê?'.
    Devolve quantas conferencias abriram."""
    abriu = 0
    for _ in range(maximo):
        page.wait_for_timeout(500)
        if conf_visivel(page):
            abriu += 1
            d = conf(page)
            nome = "Descartar" if (abriu - 1) in descartar else "Confirmar"
            d.get_by_role("button", name=nome, exact=True).click()
            page.wait_for_timeout(500)
        elif page.get_by_text("Esta coluna é o quê?").first.is_visible():
            mapear_se_preciso(page)
        else:
            break
    fechar_todos(page)
    return abriu


def abrir_pdf(page, *arquivos):
    enviar(page, *arquivos)
    return esperar_conf(page)


def sem_dados(page):
    assert codigos(page) == set(), "nada deveria ter entrado"


def pdf_forjado(caminho, linhas, titulo=None, rodape=None):
    """linhas: lista de listas de (x, texto). Uma pagina A4 paisagem."""
    pytest.importorskip("reportlab")
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.pdfgen import canvas
    c = canvas.Canvas(str(caminho), pagesize=landscape(A4), invariant=1)
    w, h = landscape(A4)
    y = h - 30
    if titulo:
        c.setFont("Helvetica-Bold", 14)
        c.drawString(30, y, titulo)
        y -= 25
    c.setFont("Helvetica", 10)
    for lin in linhas:
        for x, t in lin:
            c.drawString(x, y, t)
        y -= 16
    if rodape:
        c.drawString(30, 20, rodape)
    c.showPage()
    c.save()
    return caminho


XS3 = (30, 150, 300)


def tabela3(n=12, falta=None):
    linhas = [[(x, t) for x, t in zip(XS3, ["Código", "Cliente", "Valor"])]]
    for i in range(1, n + 1):
        cel = [f"V{i:05d}", f"Cliente {i}", f"{i},50"]
        lin = [(x, t) for x, t in zip(XS3, cel)]
        if falta == i:
            lin = [lin[0], lin[2]]
        linhas.append(lin)
    return linhas


# ---------- R-120 ----------
def test_R120_botao_aceita_pdf(page):
    acc = (page.locator("input[type=file]").first.get_attribute("accept") or "").lower()
    assert ".pdf" in acc, acc
    for ext in [".csv", ".xlsx", ".json", ".xml", ".zip"]:
        assert ext in acc
    assert ".xlsm" not in acc and ".xlsb" not in acc


# ---------- CA-73, R-121, R-122, R-125 ----------
@skip_pdf
def test_CA73_janela_conferir_leitura_estrutura_e_contagens(page):
    d = abrir_pdf(page, "vendas.pdf")
    assert d.get_attribute("aria-labelledby"), "a janela precisa de aria-labelledby"
    ident = d.get_attribute("aria-labelledby").split()[0]
    assert page.locator(f"#{ident}").inner_text().strip() == "Conferir leitura"
    texto = re.sub(r"\s+", " ", d.inner_text())
    assert "Arquivo: vendas.pdf." in texto
    assert "Confira a tabela lida. As células marcadas podem estar erradas." in texto
    assert f"Linhas lidas: {N}" in texto, texto[:300]
    assert "Células marcadas: 0" in texto
    assert d.locator("[data-baixa=true]").count() == 0
    assert d.get_by_role("button", name="Confirmar", exact=True).is_visible()
    assert d.get_by_role("button", name="Descartar", exact=True).is_visible()
    # nada entrou ainda
    assert d.locator("input[type=text]").first.get_attribute("type") == "text"
    assert page.get_by_text("Esta coluna é o quê?").first.is_visible() is False
    # a janela esta aberta e ainda nao entrou nada: confere depois de descartar
    d.get_by_role("button", name="Descartar", exact=True).click()
    fechar_todos(page)
    sem_dados(page)


@skip_pdf
def test_CA73_cabecalho_celulas_e_aria_label_iguais_ao_csv(page):
    d = abrir_pdf(page, "vendas.pdf")
    g = grade(d)
    for j, nome in enumerate(CAB, 1):
        assert g.get(f"Cabeçalho, coluna {j}") == nome, (j, g.get(f"Cabeçalho, coluna {j}"))
    n_cab = len([k for k in g if k.startswith("Cabeçalho, coluna ")])
    assert n_cab == 7
    linhas = [k for k in g if k.startswith("Linha ")]
    assert len(linhas) == N * 7, len(linhas)
    for i, r in enumerate(VENDAS, 1):
        for c in CAB:
            assert g.get(f"Linha {i}, {c}") == r[c], (i, c, g.get(f"Linha {i}, {c}"), r[c])
    # cabecalho e titulo/rodape de cada pagina nao viram linhas
    assert not any("Página" in v or v == "Relatório de vendas" for v in g.values())
    assert not any(v == "Código" for k, v in g.items() if k.startswith("Linha "))


@skip_pdf
def test_CA73_confirmar_pergunta_coluna_e_da_os_mesmos_resultados_do_csv(page):
    d = abrir_pdf(page, "vendas.pdf")
    d.get_by_role("button", name="Confirmar", exact=True).click()
    page.wait_for_timeout(800)
    assert not conf_visivel(page)
    assert page.get_by_text("Esta coluna é o quê?").first.is_visible(), "1a vez: deve perguntar"
    mapear_tudo(page)
    dlg(page, JANELA).wait_for(state="visible")
    confere_exemplos(page)
    fechar_acompanhar(page)
    confere_vendas(backup(page)[1])


# ---------- CA-73b ----------
@skip_pdf
def test_CA73b_editar_celula_e_confirmar_entra_o_valor_corrigido(page):
    d = abrir_pdf(page, "vendas.pdf")
    celula = d.locator('input[aria-label="Linha 1, Cliente"]')
    assert celula.input_value() == VENDAS[0]["Cliente"]
    celula.fill("Cliente Corrigido Teste")
    d.locator('input[aria-label="Linha 7, Região"]').fill("Regiao Nova")
    d.get_by_role("button", name="Confirmar", exact=True).click()
    resolver(page)
    esperado = [dict(r) for r in VENDAS]
    esperado[0]["Cliente"] = "Cliente Corrigido Teste"
    esperado[6]["Região"] = "Regiao Nova"
    confere_vendas(backup(page)[1], esperado)


# ---------- CA-73c ----------
@skip_pdf
def test_CA73c_descartar_nada_entra(page):
    d = abrir_pdf(page, "vendas.pdf")
    d.get_by_role("button", name="Descartar", exact=True).click()
    page.wait_for_timeout(500)
    assert not conf_visivel(page)
    assert not page.get_by_text("Esta coluna é o quê?").first.is_visible()
    fechar_todos(page)
    sem_dados(page)
    vivo(page)


@skip_pdf
def test_R123_esc_equivale_a_descartar(page):
    abrir_pdf(page, "vendas.pdf")
    page.keyboard.press("Escape")
    page.wait_for_timeout(500)
    assert not conf_visivel(page)
    assert not page.get_by_text("Esta coluna é o quê?").first.is_visible()
    fechar_todos(page)
    sem_dados(page)


# ---------- CA-77 / R-124 ----------
@pytest.mark.skipif(not (DADOS / "contrato.pdf").exists(), reason="contrato.pdf nao gerado")
def test_CA77_contrato_pdf_toast_exato_sem_janela(page):
    msgs = enviar_vendo_mensagens(page, "contrato.pdf", espera=4000)
    assert re.search(re.escape(TOAST_SEM_TABELA) + r"(?!\.)", msgs), msgs[-300:]
    assert not conf_visivel(page)
    assert not page.get_by_text("Esta coluna é o quê?").first.is_visible()
    fechar_todos(page)
    sem_dados(page)
    vivo(page)


def test_R124_pdf_de_uma_coluna_nao_e_tabela(page, tmp_path):
    linhas = [[(40, f"Linha de texto numero {i}")] for i in range(12)]
    p = pdf_forjado(tmp_path / "umacoluna.pdf", linhas, titulo="Titulo")
    msgs = enviar_vendo_mensagens(page, p, espera=4000)
    assert TOAST_SEM_TABELA in msgs
    assert not conf_visivel(page)
    sem_dados(page)


def test_R124_pdf_de_uma_linha_nao_e_tabela(page, tmp_path):
    p = pdf_forjado(tmp_path / "umalinha.pdf", [[(x, t) for x, t in zip(XS3, ["Código", "Cliente", "Valor"])]])
    msgs = enviar_vendo_mensagens(page, p, espera=4000)
    assert TOAST_SEM_TABELA in msgs
    assert not conf_visivel(page)
    sem_dados(page)


# ---------- regra 3: baixa confianca ----------
def test_regra3_celula_faltando_fica_com_data_baixa(page, tmp_path):
    p = pdf_forjado(tmp_path / "falta.pdf", tabela3(12, falta=5), titulo="Relatório de teste", rodape="Página 1")
    d = abrir_pdf(page, p)
    marcadas = d.locator("[data-baixa=true]").count()
    assert marcadas >= 1, "a linha com coluna faltando deveria ter celula marcada"
    texto = re.sub(r"\s+", " ", d.inner_text())
    assert f"Células marcadas: {marcadas}" in texto, texto[:300]
    assert "Linhas lidas: 12" in texto
    # a marcada e de verdade uma celula da tabela (input) e nao tem todas marcadas
    assert d.locator("input[type=text][data-baixa=true]").count() == marcadas
    assert marcadas < 12 * 3
    # linhas inteiras (sem problema) nao ficam marcadas
    assert d.locator('input[aria-label="Linha 1, Cliente"]').get_attribute("data-baixa") != "true"
    # confirma: continua com o caminho de sempre
    d.get_by_role("button", name="Confirmar", exact=True).click()
    resolver(page)
    cods = codigos(page)
    assert {f"V{i:05d}" for i in range(1, 13)} <= cods


# ---------- CA-73d ----------
@skip_pdf
def test_CA73d_pdf_dentro_de_zip_com_csv(page, tmp_path):
    z = grava(tmp_path, "pacote.zip", zip_bytes([("a/chamados.csv", (DADOS / "chamados.csv").read_bytes()),
                                                  ("b/vendas.pdf", (DADOS / "vendas.pdf").read_bytes())]))
    enviar(page, z)
    abriu = resolver(page)
    assert abriu == 1, "o PDF do zip deveria abrir a conferencia (uma vez)"
    d = por_codigo(backup(page)[1])
    assert len({c for c in d if c.startswith("C")}) == len(CHAMADOS)
    assert len({c for c in d if c.startswith("V")}) == N
    assert all(len(v) == 1 for v in d.values())
    confere_vendas(backup(page)[1])


@skip_pdf
def test_CA73d_zip_descartando_o_pdf_so_o_csv_entra(page, tmp_path):
    z = grava(tmp_path, "pacote2.zip", zip_bytes([("chamados.csv", (DADOS / "chamados.csv").read_bytes()),
                                                   ("vendas.pdf", (DADOS / "vendas.pdf").read_bytes())]))
    enviar(page, z)
    abriu = resolver(page, descartar=(0,))
    assert abriu == 1
    cods = codigos(page)
    assert len(cods) == len(CHAMADOS) and all(c.startswith("C") for c in cods)


# ---------- CA-110y ----------
@skip_pdf
def test_CA110y_pdf_corrompido_nao_consegui_ler(page, tmp_path):
    bruto = (DADOS / "vendas.pdf").read_bytes()
    p = grava(tmp_path, "cortado.pdf", bruto[: int(len(bruto) * 0.3)])
    msgs = enviar_vendo_mensagens(page, p, espera=5000)
    assert "Não consegui ler cortado.pdf." in msgs, msgs[-300:]
    assert not conf_visivel(page)
    assert not page.get_by_text("Esta coluna é o quê?").first.is_visible()
    sem_dados(page)
    vivo(page)


def test_CA110y_pdf_lixo_nao_consegui_ler(page, tmp_path):
    p = grava(tmp_path, "lixo.pdf", b"isto nao e um pdf" * 100)
    msgs = enviar_vendo_mensagens(page, p, espera=4000)
    assert "Não consegui ler lixo.pdf." in msgs
    assert not conf_visivel(page)
    sem_dados(page)
    vivo(page)


@skip_pdf
def test_CA110y_offline_le_igual(ctx, page):
    page.wait_for_timeout(1500)
    ctx.set_offline(True)
    d = abrir_pdf(page, "vendas.pdf")
    texto = re.sub(r"\s+", " ", d.inner_text())
    assert f"Linhas lidas: {N}" in texto and "Células marcadas: 0" in texto
    d.get_by_role("button", name="Confirmar", exact=True).click()
    resolver(page)
    confere_vendas(backup(page)[1])


# ---------- regra 4: varios PDFs ----------
@skip_pdf
def test_regra4_varios_pdfs_cada_um_abre_a_sua_janela_em_sequencia(page, tmp_path):
    copia = grava(tmp_path, "vendas_copia.pdf", (DADOS / "vendas.pdf").read_bytes())
    enviar(page, "vendas.pdf", copia)
    d = esperar_conf(page)
    primeiro = re.sub(r"\s+", " ", d.inner_text())
    nomes = [n for n in ["vendas.pdf", "vendas_copia.pdf"] if f"Arquivo: {n}." in primeiro]
    assert len(nomes) == 1, primeiro[:200]
    abriu = resolver(page)
    # a primeira ja estava aberta quando chamamos resolver (conta como 1); a segunda tem de vir depois
    assert abriu == 2, f"esperava 2 janelas em sequencia, vieram {abriu}"
    d = por_codigo(backup(page)[1])
    assert len(d) == N and all(len(v) == 1 for v in d.values()), "mesmo formato e mesmos codigos: sem duplicar"
    confere_vendas(backup(page)[1])


@skip_pdf
def test_regra4_so_a_primeira_janela_aberta_por_vez(page, tmp_path):
    copia = grava(tmp_path, "vendas_b.pdf", (DADOS / "vendas.pdf").read_bytes())
    enviar(page, "vendas.pdf", copia)
    esperar_conf(page)
    assert page.locator("dialog[open], [role=dialog]").filter(has_text="Conferir leitura").count() == 1
    resolver(page, descartar=(0, 1))
    sem_dados(page)


# ---------- formato lembrado (R-111/regra 6, CA-80) ----------
@skip_pdf
def test_CA80_csv_depois_pdf_nao_pergunta_de_novo_e_nao_duplica(page):
    carregar(page, "vendas.csv")
    d = abrir_pdf(page, "vendas.pdf")
    d.get_by_role("button", name="Confirmar", exact=True).click()
    page.wait_for_timeout(800)
    assert not page.get_by_text("Esta coluna é o quê?").first.is_visible(), "formato lembrado deveria valer"
    fechar_acompanhar(page)
    b = backup(page)[1]
    d = por_codigo(b)
    assert len(d) == N and all(len(v) == 1 for v in d.values()), "contagem dobrou"
    confere_vendas(b)


@skip_pdf
def test_CA80_pdf_depois_csv_nao_pergunta_de_novo_e_nao_duplica(page):
    d = abrir_pdf(page, "vendas.pdf")
    d.get_by_role("button", name="Confirmar", exact=True).click()
    page.wait_for_timeout(800)
    mapear_tudo(page)
    fechar_todos(page)
    enviar(page, "vendas.csv")
    assert not page.get_by_text("Esta coluna é o quê?").first.is_visible()
    fechar_acompanhar(page)
    b = backup(page)[1]
    d = por_codigo(b)
    assert len(d) == N and all(len(v) == 1 for v in d.values())
    confere_vendas(b)


@skip_pdf
def test_CA80_mesmo_pdf_duas_vezes_nao_duplica(page):
    d = abrir_pdf(page, "vendas.pdf")
    d.get_by_role("button", name="Confirmar", exact=True).click()
    page.wait_for_timeout(800)
    mapear_tudo(page)
    fechar_todos(page)
    d = abrir_pdf(page, "vendas.pdf")
    d.get_by_role("button", name="Confirmar", exact=True).click()
    page.wait_for_timeout(800)
    assert not page.get_by_text("Esta coluna é o quê?").first.is_visible()
    fechar_todos(page)
    d = por_codigo(backup(page)[1])
    assert len(d) == N and all(len(v) == 1 for v in d.values())


# ---------- seguranca / rede ----------
@skip_pdf
def test_regra5_nenhuma_requisicao_externa_ao_ler_pdf(ctx, page):
    abrir_pdf(page, "vendas.pdf")
    resolver(page)
    externas = [u for u in ctx.reqs if not u.startswith(("http://localhost:8767", "data:", "blob:"))]
    assert not externas, externas


def test_regra5_conteudo_do_pdf_so_entra_como_texto(page, tmp_path):
    linhas = tabela3(8)
    linhas[2][1] = (150, "<img src=x onerror=window.__x=1>")
    p = pdf_forjado(tmp_path / "html.pdf", linhas)
    d = abrir_pdf(page, p)
    assert page.locator("img[src='x']").count() == 0
    d.get_by_role("button", name="Confirmar", exact=True).click()
    resolver(page)
    assert page.evaluate("window.__x") is None
    assert page.locator("img[src='x']").count() == 0
    vivo(page)


# ---------- F-67: Médio e Baixo da revisão de segurança da etapa 7b (regressão) ----------
def test_f67_tabela_pdf_com_muitas_colunas_e_linhas_nao_trava(page):
    r = page.evaluate("""() => {
      const t0 = performance.now(), pgs = [];
      for (let p = 0; p < 30; p++) { const it = []; for (let l = 0; l < 100; l++) for (let c = 0; c < 400; c++) it.push({ x: 10 + c * 40, y: 800 - l * 8, w: 20, h: 8, t: 'c' + c + 'l' + l }); pgs.push(it); }
      const t = Core.tabelaPdf(pgs, 20000);
      return [performance.now() - t0, t ? t.rows[0].length : -1];
    }""")
    assert r[0] < 15000, f"tabelaPdf levou {r[0]:.0f} ms"
    assert r[1] <= 200


def test_f67_conferencia_grande_mostra_primeiras_linhas_e_mais(page):
    carregar_vazio = None  # a janela é chamada direto, sem arquivo
    n = page.evaluate("""async () => {
      const rows = [Array.from({ length: 50 }, (_, j) => 'Col' + j)];
      for (let i = 1; i <= 2000; i++) rows.push(Array.from({ length: 50 }, (_, j) => 'v' + i + '_' + j));
      conferir('grande.pdf', rows, []);
      await new Promise(r => setTimeout(r, 300));
      const antes = document.querySelectorAll('#cfTab input').length;
      document.querySelector('#cfMais').click();
      const depois = document.querySelectorAll('#cfTab input').length;
      return [antes, depois, document.querySelector('#cfMais').hidden];
    }""")
    assert n[0] < 2001 * 50 and n[0] > 0 and n[1] > n[0]
