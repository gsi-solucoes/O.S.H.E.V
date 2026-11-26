"""Suite da etapa 7c (F-65): imagem e PDF escaneado com OCR. Escrita SO a partir da especificacao v1.9
(secoes 0.10 e 7: R-130 a R-134, regras 1-8, CA-74, CA-75, CA-76, CA-77b, CA-110z, PDF escaneado; 0.9 e 0.8 para o que ja existe).
Oraculo: tests/dados/vendas.csv (linhas 1-60 = vendas_foto_1 + vendas_foto_2), comparado pelas celulas da janela
'Conferir leitura' (aria-label 'Linha <n>, <coluna>') e pelo backup.

Suposicoes (texto mais literal):
 S1 mesmas da 7b: janela = dialog/[role=dialog] 'Conferir leitura'; celulas = input[type=text][aria-label].
 S2 'Linhas lidas' conta linhas de dados (30 numa foto, 60 nas duas).
 S3 a imagem reduzida e um <img alt='Imagem lida: <nome>'> dentro da janela; com duas fotos basta haver >= 1 delas
    (uma por foto ou so a primeira).
 S4 imagem corrompida = os primeiros 10% dos bytes de vendas_foto_1.jpg (decodificacao parcial nao pode dar tabela);
    arquivo vazio (0 byte) tambem = 'Não consegui ler <arquivo>.'.
 S5 foto de 12 MP = ruido uniforme 4000x3000 (JPEG). Sem tabela: aceita-se 'Não encontrei uma tabela neste arquivo',
    'Não consegui ler <arquivo>.' ou uma janela de conferencia (que o teste descarta). O que se exige: a pagina
    responde durante o OCR (page.evaluate('1+1') em < 5 s) e nenhuma requisicao externa.
 S6 limite de 20 imagens: 21 PNGs pequenos e em branco (OCR rapido) em vez de 21 fotos de vendas; a 21a
    (img21.png) recebe '<arquivo>: limite de 20 imagens.'.
 S7 antes de qualquer uso, offline: o envio de uma imagem mostra o toast exato de 'OCR indisponivel' (R-134).
 S8 'Células marcadas: m' = numero de inputs com data-baixa='true' (como na 7b).
 S9 'corrigir so as marcadas' deve bastar: depois de corrigir as marcadas para o valor do CSV, o backup tem os 60
    registros iguais ao CSV (confere_vendas). Celula errada e nao marcada = falha do app (R-132/regra 4).
 S10 'Lendo a imagem… <n>%' aparece em algum momento (capturado por MutationObserver) durante a leitura de uma foto.
 S11 PDF escaneado: gerado com reportlab (so a imagem, sem texto); testes pulados sem reportlab/Pillow.
Cada OCR e lento (10-40 s): timeouts de 240 s. Total de execucoes de OCR na suite: ~13 fotos + 20 imagens em branco.
"""
import re, io, time
import pytest
from conftest import DADOS
from test_etapa1 import (le_csv, enviar, mapear_se_preciso, fechar_acompanhar, backup)
from test_etapa7a import (confere_vendas, mapear_tudo, fechar_todos, codigos, zip_bytes, grava, vivo, N, VENDAS,
                          CHAMADOS, por_codigo)
from test_etapa7b import conf, conf_visivel, grade, CAB, TOAST_SEM_TABELA

LONGO = 240000
FOTO1, FOTO2, CONTRATO = "vendas_foto_1.jpg", "vendas_foto_2.jpg", "contrato_foto.jpg"
skip_fotos = pytest.mark.skipif(not (DADOS / FOTO1).exists(), reason="fotos nao geradas (sem Pillow)")
LEITOR_OFF = "O leitor de imagens ainda não está disponível neste aparelho. Use uma vez com internet."


# ---------- auxiliares ----------
@pytest.fixture()
def pg(page):
    page.set_default_timeout(LONGO)
    return page


def observar(page):
    page.evaluate("""()=>{window.__tt=[];new MutationObserver(ms=>{for(const m of ms){
      for(const n of m.addedNodes){window.__tt.push(n.textContent||'')}
      if(m.type==='characterData')window.__tt.push(m.target.textContent||'')}})
      .observe(document.body,{childList:true,subtree:true,characterData:true});}""")


def tudo_visto(page):
    return " | ".join(page.evaluate("window.__tt")) + " | " + page.evaluate("document.body.innerText")


def esperar_texto(page, trecho, timeout=LONGO):
    fim = time.time() + timeout / 1000
    t = ""
    while time.time() < fim:
        t = tudo_visto(page)
        if trecho in t:
            return t
        page.wait_for_timeout(700)
    raise AssertionError(f"texto {trecho!r} nao apareceu em {timeout/1000:.0f}s; fim da tela: {t[-300:]}")


def esperar_conf(page, timeout=LONGO):
    """Espera a janela 'Conferir leitura', respondendo 'Esta coluna é o quê?' de outros arquivos do envio."""
    fim = time.time() + timeout / 1000
    while time.time() < fim:
        if conf_visivel(page):
            return conf(page)
        if page.get_by_text("Esta coluna é o quê?").first.is_visible():
            mapear_se_preciso(page)
        page.wait_for_timeout(700)
    raise AssertionError("a janela 'Conferir leitura' nao abriu")


def texto_conf(d):
    return re.sub(r"\s+", " ", d.inner_text())


def mostrar_tudo(d):
    for _ in range(40):
        b = d.get_by_role("button", name="Mostrar mais linhas")
        if b.count() and b.first.is_visible():
            b.first.click()
        else:
            break


def sem_dados(page):
    assert codigos(page) == set(), "nada deveria ter entrado"


def comparar(g, linhas):
    """Quantas das celulas (linhas 1..n do CSV x 7 colunas) estao iguais; devolve (iguais, total, erradas)."""
    ok, erradas = 0, []
    for i in linhas:
        r = VENDAS[i - 1]
        for c in CAB:
            if g.get(f"Linha {i}, {c}") == r[c]:
                ok += 1
            else:
                erradas.append((i, c, g.get(f"Linha {i}, {c}"), r[c]))
    return ok, len(linhas) * len(CAB), erradas


def corrigir_marcadas(d):
    """Edita SO as celulas com data-baixa='true' para o valor do CSV; devolve quantas editou."""
    rotulos = d.locator("input[type=text][data-baixa=true]").evaluate_all("els=>els.map(e=>e.getAttribute('aria-label'))")
    for rot in rotulos:
        m = re.fullmatch(r"Linha (\d+), (.+)", rot)
        if m:
            valor = VENDAS[int(m[1]) - 1][m[2]]
        else:
            m = re.fullmatch(r"Cabeçalho, coluna (\d+)", rot)
            valor = CAB[int(m[1]) - 1]
        d.locator(f'input[aria-label="{rot}"]').fill(valor)
    return len(rotulos)


def finalizar(page, maximo=8):
    """Depois do 'Confirmar': responde 'Esta coluna é o quê?' e fecha o 'O que você quer acompanhar?'."""
    for _ in range(maximo):
        page.wait_for_timeout(600)
        if page.get_by_text("Esta coluna é o quê?").first.is_visible():
            mapear_se_preciso(page)
        else:
            break
    fechar_todos(page)


def externas(ctx):
    return [u for u in ctx.reqs if not u.startswith(("http://localhost:8767", "data:", "blob:"))]


def png_branco(tmp_path, nome):
    PIL = pytest.importorskip("PIL.Image")
    p = tmp_path / nome
    PIL.new("RGB", (120, 80), "white").save(p, "PNG")
    return p


# ---------- R-130 ----------
def test_R130_botao_aceita_jpg_jpeg_png_e_os_anteriores(page):
    acc = (page.locator("input[type=file]").first.get_attribute("accept") or "").lower()
    for ext in [".jpg", ".jpeg", ".png", ".pdf", ".csv", ".xlsx", ".json", ".xml", ".zip"]:
        assert ext in acc, (ext, acc)


# ---------- CA-74 (+ R-125, R-132, regra 3, regra 5) ----------
@skip_fotos
def test_CA74_duas_fotos_uma_janela_60_linhas_95_por_cento_e_corrigir_marcadas(ctx, pg):
    enviar(pg, FOTO1, FOTO2)
    d = esperar_conf(pg)
    pg.wait_for_timeout(1500)
    assert pg.locator("dialog[open], [role=dialog]").filter(has_text="Conferir leitura").count() == 1, "deve ser UMA janela"
    assert d.get_attribute("aria-labelledby")
    mostrar_tudo(d)
    texto = texto_conf(d)
    assert "Linhas lidas: 60" in texto, texto[:300]
    marcadas = d.locator("input[type=text][data-baixa=true]").count()
    assert f"Células marcadas: {marcadas}" in texto, (marcadas, texto[:300])
    # cabecalho uma vez so; numeracao continua 1..60
    g = grade(d)
    assert len([k for k in g if k.startswith("Cabeçalho, coluna ")]) == 7
    assert len({k for k in g if k.startswith("Linha ")}) == 60 * 7, len([k for k in g if k.startswith("Linha ")])
    assert not any(v == "Código" for k, v in g.items() if k.startswith("Linha "))
    # imagem ao lado
    imgs = d.locator("img[alt^='Imagem lida: ']").evaluate_all("els=>els.map(e=>e.alt)")
    assert imgs and all(a in ("Imagem lida: " + FOTO1, "Imagem lida: " + FOTO2) for a in imgs), imgs
    # >= 95% das 420 celulas antes de corrigir
    ok, total, erradas = comparar(g, range(1, 61))
    assert total == 420 and ok / total >= 0.95, f"{ok}/{total}; erradas: {erradas[:12]}"
    # regra 3: colunas de codigo e de numero sem letras trocadas
    cods = [g.get(f"Linha {i}, Código", "") for i in range(1, 61)]
    assert sum(bool(re.fullmatch(r"V\d{5}", c)) for c in cods) / 60 >= 0.95, cods
    vals = [g.get(f"Linha {i}, Valor", "") for i in range(1, 61)]
    assert sum(bool(re.fullmatch(r"[\d.]+,\d{2}", v)) for v in vals) / 60 >= 0.95, vals
    # corrige so as marcadas e confirma
    n = corrigir_marcadas(d)
    assert n == marcadas
    d.get_by_role("button", name="Confirmar", exact=True).click()
    finalizar(pg)
    b = backup(pg)[1]
    d60 = por_codigo(b)
    assert {c for c in d60 if c.startswith("V")} == {r["Código"] for r in VENDAS[:60]}
    confere_vendas(b, VENDAS[:60])
    assert not externas(ctx), externas(ctx)


# ---------- R-131, R-132, R-123 (Esc / Descartar) ----------
@skip_fotos
def test_R131_R132_progresso_imagem_ao_lado_esc_e_descartar_nada_entra(pg):
    observar(pg)
    enviar(pg, FOTO1)
    d = esperar_conf(pg)
    vistos = tudo_visto(pg)
    assert re.search(r"Lendo a imagem… ?\d+%", vistos), "faltou o progresso 'Lendo a imagem… <n>%'"
    texto = texto_conf(d)
    assert f"Arquivo: {FOTO1}." in texto
    assert "Confira a tabela lida. As células marcadas podem estar erradas." in texto
    assert "Linhas lidas: 30" in texto, texto[:300]
    marcadas = d.locator("input[type=text][data-baixa=true]").count()
    assert f"Células marcadas: {marcadas}" in texto
    assert d.locator(f'img[alt="Imagem lida: {FOTO1}"]').first.is_visible()
    assert pg.get_by_text("Esta coluna é o quê?").first.is_visible() is False, "nada entra sem Confirmar"
    pg.keyboard.press("Escape")
    pg.wait_for_timeout(600)
    assert not conf_visivel(pg)
    assert not pg.get_by_text("Esta coluna é o quê?").first.is_visible()
    fechar_todos(pg)
    sem_dados(pg)
    # segunda vez: Descartar
    enviar(pg, FOTO1)
    d = esperar_conf(pg)
    d.get_by_role("button", name="Descartar", exact=True).click()
    pg.wait_for_timeout(600)
    assert not conf_visivel(pg)
    assert not pg.get_by_text("Esta coluna é o quê?").first.is_visible()
    fechar_todos(pg)
    sem_dados(pg)
    vivo(pg)
    # "some ao terminar"
    assert not re.search(r"Lendo a imagem… ?\d+%", pg.evaluate("document.body.innerText"))


# ---------- CA-75 ----------
@skip_fotos
def test_CA75_zip_com_csv_xlsx_e_jpg_os_tres_lidos_jpg_passa_pela_conferencia(pg, tmp_path):
    z = grava(tmp_path, "pacote.zip", zip_bytes([("chamados.csv", (DADOS / "chamados.csv").read_bytes()),
                                                  ("vendas.xlsx", (DADOS / "vendas.xlsx").read_bytes()),
                                                  (FOTO1, (DADOS / FOTO1).read_bytes())]))
    enviar(pg, z)
    d = esperar_conf(pg)
    assert f"Arquivo: {FOTO1}." in texto_conf(d)
    corrigir_marcadas(d)
    d.get_by_role("button", name="Confirmar", exact=True).click()
    finalizar(pg)
    b = backup(pg)[1]
    dd = por_codigo(b)
    assert len({c for c in dd if c.startswith("C")}) == len(CHAMADOS)
    assert len({c for c in dd if c.startswith("V")}) == N
    assert all(len(v) == 1 for v in dd.values()), "registro duplicado"
    confere_vendas(b)


# ---------- CA-76 ----------
@skip_fotos
def test_CA76_offline_depois_de_um_uso_do_ocr(ctx, pg):
    enviar(pg, FOTO1)
    d = esperar_conf(pg)
    d.get_by_role("button", name="Descartar", exact=True).click()
    pg.wait_for_timeout(800)
    fechar_todos(pg)
    ctx.set_offline(True)
    pg.reload()
    pg.wait_for_timeout(2000)
    enviar(pg, FOTO1)
    d = esperar_conf(pg)
    texto = texto_conf(d)
    assert "Linhas lidas: 30" in texto, texto[:300]
    ok, total, erradas = comparar(grade(d), range(1, 31))
    assert ok / total >= 0.95, f"{ok}/{total}; {erradas[:10]}"
    d.get_by_role("button", name="Descartar", exact=True).click()
    assert LEITOR_OFF not in pg.evaluate("document.body.innerText")


def test_R134_ocr_indisponivel_offline_antes_do_primeiro_uso(ctx, pg, tmp_path):
    pytest.importorskip("PIL")
    pg.wait_for_timeout(1500)
    ctx.set_offline(True)
    p = png_branco(tmp_path, "qualquer.png")
    observar(pg)
    enviar(pg, p)
    esperar_texto(pg, LEITOR_OFF, 60000)
    assert not conf_visivel(pg)
    sem_dados(pg)


# ---------- CA-77b ----------
@pytest.mark.skipif(not (DADOS / CONTRATO).exists(), reason="contrato_foto.jpg nao gerado")
def test_CA77b_foto_de_contrato_sem_tabela(pg):
    observar(pg)
    enviar(pg, CONTRATO)
    t = esperar_texto(pg, TOAST_SEM_TABELA)
    assert re.search(re.escape(TOAST_SEM_TABELA) + r"(?!\.)", t)
    pg.wait_for_timeout(1500)
    assert not conf_visivel(pg)
    assert not pg.get_by_text("Esta coluna é o quê?").first.is_visible()
    fechar_todos(pg)
    sem_dados(pg)
    vivo(pg)


# ---------- R-134 / CA-110z ----------
@skip_fotos
def test_CA110z_imagem_corrompida_nao_consegui_ler(pg, tmp_path):
    bruto = (DADOS / FOTO1).read_bytes()
    p = grava(tmp_path, "cortada.jpg", bruto[: len(bruto) // 10])
    observar(pg)
    enviar(pg, p)
    esperar_texto(pg, "Não consegui ler cortada.jpg.")
    assert not conf_visivel(pg)
    assert not pg.get_by_text("Esta coluna é o quê?").first.is_visible()
    sem_dados(pg)
    vivo(pg)


def test_CA110z_imagem_vazia_nao_consegui_ler(pg, tmp_path):
    p = grava(tmp_path, "vazio.png", b"")
    observar(pg)
    enviar(pg, p)
    esperar_texto(pg, "Não consegui ler vazio.png.", 90000)
    assert not conf_visivel(pg)
    sem_dados(pg)


def test_CA110z_lixo_com_extensao_de_imagem_nao_consegui_ler(pg, tmp_path):
    p = grava(tmp_path, "lixo.png", b"isto nao e uma imagem" * 200)
    observar(pg)
    enviar(pg, p)
    esperar_texto(pg, "Não consegui ler lixo.png.", 90000)
    assert not conf_visivel(pg)
    sem_dados(pg)
    vivo(pg)


def test_CA110z_foto_de_12_megapixels_nao_trava_a_aba_e_nao_usa_rede(ctx, pg, tmp_path):
    Im = pytest.importorskip("PIL.Image")
    import os
    ruido = Im.frombytes("L", (4000, 3000), os.urandom(4000 * 3000))
    p = tmp_path / "grande12mp.jpg"
    ruido.save(p, "JPEG", quality=70)
    assert p.stat().st_size < 50 * 1024 * 1024
    observar(pg)
    enviar(pg, p)
    # a pagina responde durante o OCR
    maior = 0.0
    fim = time.time() + 150
    while time.time() < fim:
        t0 = time.time()
        assert pg.evaluate("1+1") == 2
        maior = max(maior, time.time() - t0)
        t = tudo_visto(pg)
        if conf_visivel(pg) or "Não encontrei uma tabela" in t or "Não consegui ler grande12mp.jpg." in t:
            break
        pg.wait_for_timeout(500)
    else:
        raise AssertionError("a leitura nao terminou em 150 s (limite do OCR e 120 s por imagem)")
    assert maior < 5, f"a pagina ficou {maior:.1f}s sem responder"
    if conf_visivel(pg):
        conf(pg).get_by_role("button", name="Descartar", exact=True).click()
    fechar_todos(pg)
    sem_dados(pg)
    vivo(pg)
    assert not externas(ctx), externas(ctx)


# ---------- regra 7: limite de 20 ----------
def test_regra7_limite_de_20_imagens_o_excedente_e_avisado(pg, tmp_path):
    arqs = [png_branco(tmp_path, f"img{i:02d}.png") for i in range(1, 22)]
    observar(pg)
    enviar(pg, *arqs)
    t = esperar_texto(pg, "img21.png: limite de 20 imagens.", 240000)
    for i in range(1, 21):
        assert f"img{i:02d}.png: limite de 20 imagens." not in t
    vivo(pg)


# ---------- PDF escaneado (regra 6) ----------
@skip_fotos
def test_pdf_escaneado_so_imagem_mesma_conferencia_linhas_1_a_30(pg, tmp_path):
    pytest.importorskip("reportlab")
    from reportlab.pdfgen import canvas
    from reportlab.lib.utils import ImageReader
    from PIL import Image
    im = Image.open(DADOS / FOTO1)
    w, h = im.size
    pdf = tmp_path / "escaneado.pdf"
    c = canvas.Canvas(str(pdf), pagesize=(w * 0.5, h * 0.5), invariant=1)
    c.drawImage(ImageReader(im), 0, 0, width=w * 0.5, height=h * 0.5)
    c.showPage()
    c.save()
    observar(pg)
    enviar(pg, pdf)
    d = esperar_conf(pg)
    assert "Arquivo: escaneado.pdf." in texto_conf(d)
    assert "Linhas lidas: 30" in texto_conf(d), texto_conf(d)[:300]
    assert re.search(r"Lendo a página 1 de 1…", tudo_visto(pg)), "faltou o progresso do PDF escaneado"
    ok, total, erradas = comparar(grade(d), range(1, 31))
    assert ok / total >= 0.95, f"{ok}/{total}; {erradas[:10]}"
    corrigir_marcadas(d)
    d.get_by_role("button", name="Confirmar", exact=True).click()
    finalizar(pg)
    b = backup(pg)[1]
    assert {c for c in por_codigo(b) if c.startswith("V")} == {r["Código"] for r in VENDAS[:30]}
    confere_vendas(b, VENDAS[:30])
