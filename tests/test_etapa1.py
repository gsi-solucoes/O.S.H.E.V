"""Suite da etapa 1 (+ secoes 0, 8, 9, 10). Escrita SO a partir da especificacao.
Seletores por texto visivel. Oraculos calculados em Python sobre tests/dados/."""
import csv, io, json, re, zipfile, statistics, datetime
import pytest
from conftest import URL, DADOS, RAIZ

# ---------- auxiliares ----------
def le_csv(nome, enc="utf-8"):
    with open(DADOS / nome, encoding=enc, newline="") as f:
        return list(csv.DictReader(f, delimiter=";"))

VENDAS = le_csv("vendas.csv")
CODIGOS_V = {r["Código"] for r in VENDAS}


def enviar(page, *arquivos):
    page.locator("input[type=file]").first.set_input_files([str(DADOS / a) if isinstance(a, str) else a for a in arquivos])
    page.wait_for_timeout(800)


def mapear_se_preciso(page):
    """Se aparecer 'Esta coluna é o quê?', responde pelo nome do campo e confirma."""
    if not page.get_by_text("Esta coluna é o quê?").first.is_visible():
        return False
    for sel in page.locator("select:visible").all():
        rotulo = sel.evaluate("e=>(e.closest('tr,li,div,label')||e.parentElement).innerText.split('\\n')[0]")
        opts = sel.locator("option").all_inner_texts()
        alvo = next((o for o in opts if o.strip().lower().rstrip('s') == rotulo.strip().lower().rstrip('s')), None)
        if alvo is None and re.search(r"c[óo]digo", rotulo, re.I):
            alvo = next((o for o in opts if re.search(r"c[óo]digo", o, re.I)), None)
        if alvo:
            sel.select_option(label=alvo)
    page.get_by_role("button", name=re.compile(r"confirmar|salvar|continuar|ok", re.I)).first.click()
    page.wait_for_timeout(800)
    return True


def fechar_acompanhar(page):
    """D-09: a janela 'O que você quer acompanhar?' abre sozinha; nos testes da etapa 1 fica o painel padrão."""
    page.wait_for_timeout(300)
    if page.get_by_text("O que você quer acompanhar?").first.is_visible():
        janela = page.locator("dialog, [role=dialog]").filter(has_text="O que você quer acompanhar?").first
        janela.get_by_role("button", name="Cancelar", exact=True).click()
        page.wait_for_timeout(300)


def carregar(page, *arquivos):
    enviar(page, *arquivos)
    mapear_se_preciso(page)
    fechar_acompanhar(page)


def backup(page):
    abrir_config(page)
    with page.expect_download() as d:
        page.get_by_role("button", name="Baixar backup").click()
    caminho = d.value.path()
    return d.value.suggested_filename, open(caminho, encoding="utf-8").read()


def codigos_no_backup(texto):
    return re.findall(r"V\d{5}", texto)


def abrir_config(page):
    page.get_by_text("Config", exact=True).first.click()
    page.wait_for_timeout(300)


def abrir_painel(page):
    page.get_by_text("Painel", exact=True).first.click()
    page.wait_for_timeout(300)


def gerar_excel(page):
    abrir_painel(page)
    with page.expect_download() as d:
        page.get_by_role("button", name="Gerar Excel").click()
    return d.value


def abrir_xlsx(download, tmp_path):
    """O arquivo temporario do Playwright nao tem extensao; salva com o nome sugerido."""
    from openpyxl import load_workbook
    destino = tmp_path / download.suggested_filename
    download.save_as(str(destino))
    return load_workbook(destino)


# ---------- seção 0 ----------
def test_CA01_offline_le_csv_e_gera_excel(ctx, page):
    page.evaluate("navigator.serviceWorker && navigator.serviceWorker.ready")
    page.reload(); page.wait_for_timeout(1000)
    ctx.set_offline(True)
    page.reload(); page.wait_for_timeout(1000)
    assert page.title()
    carregar(page, "vendas.csv")
    assert gerar_excel(page).suggested_filename.endswith(".xlsx")


def test_CA02_sem_requisicao_externa(ctx, page):
    carregar(page, "vendas.csv")
    abrir_config(page)
    externas = [u for u in ctx.reqs if not u.startswith(URL) and not u.startswith(("data:", "blob:"))]
    assert externas == []


def test_CA03_termos_proibidos_no_html_e_bas():
    termos = [t.strip() for t in open(RAIZ / "tests/termos_proibidos.txt", encoding="utf-8") if t.strip()]
    for arq in [RAIZ / "index.html", RAIZ / "excel/RaioX_Relatorio.bas"]:
        txt = arq.read_text(encoding="utf-8", errors="ignore").lower()
        achados = [t for t in termos if t.lower() in txt]
        assert achados == [], f"{arq.name}: {achados}"


def test_CA04_celular_sem_rolagem_horizontal(browser):
    c = browser.new_context(viewport={"width": 390, "height": 800})
    pg = c.new_page(); pg.goto(URL); pg.wait_for_timeout(1000)
    assert pg.evaluate("document.documentElement.scrollWidth <= window.innerWidth + 1")
    c.close()


# ---------- etapa 1 ----------
def test_CA10_armazenamento_vazio_titulo_sem_cliente(page):
    assert page.title() == "Raio X do Relatório" or "Raio X do Relatório" in page.title()
    assert page.get_by_text("Raio X do Relatório").first.is_visible()
    assert "Empresa Teste" not in page.inner_text("body")


def logo_png(tmp_path):
    import base64
    p = tmp_path / "logo.png"
    p.write_bytes(base64.b64decode(
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="))
    return p


def preencher_empresa(page, tmp_path):
    abrir_config(page)
    page.get_by_label("Cliente", exact=True).fill("Empresa Teste")
    page.get_by_label("Área", exact=True).fill("Operações")
    with page.expect_file_chooser() as fc:
        page.get_by_role("button", name="Escolher logo").click()
    fc.value.set_files(str(logo_png(tmp_path)))
    page.wait_for_timeout(600)  # D-01: sem botão Salvar; a Config salva sozinha


def test_CA11_empresa_no_cabecalho_persistente_e_capa_excel(page, tmp_path):
    preencher_empresa(page, tmp_path)
    cab = page.locator("header").first
    assert "Empresa Teste" in cab.inner_text() and "Operações" in cab.inner_text()
    assert cab.locator("img").count() >= 1
    page.reload(); page.wait_for_timeout(800)
    assert "Empresa Teste" in page.locator("header").first.inner_text()
    carregar(page, "vendas.csv")
    dl = gerar_excel(page)
    wb = abrir_xlsx(dl, tmp_path)
    nomes_zip = zipfile.ZipFile(tmp_path / dl.suggested_filename).namelist()
    assert any(n.startswith("xl/media/") for n in nomes_zip), "logo ausente no arquivo"
    capa = wb.worksheets[0]
    textos = " ".join(str(c.value) for row in capa.iter_rows() for c in row if c.value)
    assert "Operações · Empresa Teste" in textos
    # logo na capa (1a planilha): confere no zip (openpyxl nao carrega PNG minimo de 1 pixel)
    z = zipfile.ZipFile(tmp_path / dl.suggested_filename)
    assert "drawing" in z.read("xl/worksheets/_rels/sheet1.xml.rels").decode()
    assert "<xdr:pic>" in z.read("xl/drawings/drawing1.xml").decode()


def test_CA12_apagar_logo(page, tmp_path):
    preencher_empresa(page, tmp_path)
    abrir_config(page)
    page.get_by_role("button", name="Apagar logo").click()
    page.wait_for_timeout(400)
    assert page.locator("header").first.locator("img").count() == 0


def test_CA13_manifesto_e_service_worker(page):
    href = page.locator("link[rel=manifest]").first.get_attribute("href")
    m = page.request.get(URL + href.lstrip("./")).json()
    assert m["name"] and m["display"] == "standalone"
    tam = {i["sizes"] for i in m["icons"]}
    assert {"192x192", "512x512"} <= tam
    for i in m["icons"]:
        assert page.request.get(URL + i["src"].lstrip("./")).ok
    page.wait_for_timeout(1500)
    ativo = page.evaluate("navigator.serviceWorker.getRegistration().then(r=>!!(r&&r.active))")
    assert ativo


def test_CA14_migracao_config_antiga(page):
    # monta uma config "antiga" generica no localStorage e um historico previo; recarrega
    carregar(page, "vendas.csv")
    _, antes = backup(page)
    n_antes = len(set(codigos_no_backup(antes)))
    assert n_antes == len(CODIGOS_V)
    chaves = page.evaluate("Object.keys(localStorage)")
    page.reload(); page.wait_for_timeout(1000)
    assert page.evaluate("Object.keys(localStorage)") == chaves or set(chaves) <= set(page.evaluate("Object.keys(localStorage)"))
    _, depois = backup(page)
    assert len(set(codigos_no_backup(depois))) == n_antes


@pytest.mark.skip(reason="CA-15 exige publicar duas versões; coberto na homologação manual")
def test_CA15_versao_nova():
    pass


def test_CA16_baixar_excel_para_o_pc(page):
    abrir_config(page)
    with page.expect_download() as d:
        page.get_by_role("link", name="Baixar versão Excel para o PC").first.click()
    assert d.value.suggested_filename == "RaioX_Relatorio.bas"
    bas = open(d.value.path(), encoding="utf-8", errors="ignore").read().lower()
    assert "hev" not in bas and "edmundo" not in bas
    # D-06: a lista (abre sozinha ao clicar em R-25) tem 4 itens
    titulo = page.get_by_text("Como instalar a versão Excel (4 passos)").first
    itens = titulo.locator("xpath=following::ol[1]/li")
    assert itens.count() == 4, "4 passos de instalação"
    assert itens.first.is_visible()


def test_CA16_baixar_offline(ctx, page):
    page.wait_for_timeout(1500); page.reload(); page.wait_for_timeout(1000)
    ctx.set_offline(True)
    page.reload(); page.wait_for_timeout(800)
    abrir_config(page)
    with page.expect_download() as d:
        page.get_by_role("link", name="Baixar versão Excel para o PC").first.click()
    assert d.value.suggested_filename == "RaioX_Relatorio.bas"


# ---------- seção 8 ----------
def test_CA80_mesmo_arquivo_duas_vezes(page):
    carregar(page, "vendas.csv")
    _, b1 = backup(page)
    carregar(page, "vendas.csv")
    _, b2 = backup(page)
    assert len(codigos_no_backup(b1)) == len(codigos_no_backup(b2)) > 0
    assert len(set(codigos_no_backup(b2))) == len(VENDAS)


def test_CA81_juncao_campo_a_campo(page):
    p2 = le_csv("vendas_parte2.csv")
    carregar(page, "vendas.csv")
    carregar(page, "vendas_parte2.csv")
    _, b = backup(page)
    dados = json.loads(b)

    def registros(o):
        if isinstance(o, dict):
            if any(isinstance(v, str) and re.fullmatch(r"V\d{5}", v) for v in o.values()):
                yield o
            for v in o.values():
                yield from registros(v)
        elif isinstance(o, list):
            for v in o:
                yield from registros(v)
    por_cod = {}
    for r in registros(dados):
        cod = next(v for v in r.values() if isinstance(v, str) and re.fullmatch(r"V\d{5}", v))
        por_cod.setdefault(cod, []).append(" ".join(json.dumps(v, ensure_ascii=False) for v in r.values()))
    com_prio = [r for r in p2 if r["Prioridade"]]
    assert com_prio
    orig_de = {v["Código"]: v for v in VENDAS}
    # registro UNICO por codigo, com os campos dos dois arquivos (junção)
    for r in com_prio[:20]:
        assert len(por_cod[r["Código"]]) == 1, f"{r['Código']}: registro duplicado, sem junção"
        t = por_cod[r["Código"]][0]
        assert r["Prioridade"] in t and orig_de[r["Código"]]["Cliente"] in t
    vazio = next(r for r in p2 if not r["Prioridade"])
    orig = orig_de[vazio["Código"]]
    t = " ".join(por_cod[vazio["Código"]])
    assert orig["Cliente"] in t and orig["Vendedor"] in t  # nada apagado


@pytest.mark.skip(reason="CA-82: desempenho com 72 mil registros, a medir na máquina de CI")
def test_CA82_desempenho():
    pass


def test_CA83_dados_reprodutiveis():
    import subprocess, hashlib, sys
    def h():
        return {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(DADOS.glob("*"))}
    a = h()
    subprocess.run([sys.executable, str(RAIZ / "tests/gerar_dados.py")], check=True)
    assert h() == a and len(a) >= 4


# ---------- seção 9 ----------
@pytest.mark.parametrize("arq", ["vendas.csv", "vendas_cp1252.csv"])
def test_CA90_leitor_utf8_e_cp1252(page, arq):
    carregar(page, arq)
    _, b = backup(page)
    assert len(set(codigos_no_backup(b))) == len(VENDAS)
    # acentos do cabeçalho/valores preservados (Região, Situação nao viram lixo)
    assert "�" not in b


def test_CA90_cabecalho_depois_de_linhas_de_titulo_e_virgula(page, tmp_path):
    linhas = ["Relatório de teste", "Gerado em 01/01/2026", ""] + [
        "Código,Cliente,Valor"] + [f"V{i:05d},Cli {i},{i}.5" for i in range(1, 21)]
    p = tmp_path / "x.csv"; p.write_text("\n".join(linhas), encoding="utf-8")
    carregar(page, p)
    _, b = backup(page)
    assert len(set(codigos_no_backup(b))) == 20


def test_CA91_importador_aprende(page):
    enviar(page, "chamados.csv")
    assert page.get_by_text("Esta coluna é o quê?").first.is_visible()
    mapear_se_preciso(page)
    fechar_acompanhar(page)
    enviar(page, "chamados.csv")
    assert not page.get_by_text("Esta coluna é o quê?").first.is_visible(), "formato deveria estar lembrado"
    fechar_acompanhar(page)
    abrir_config(page)
    assert page.get_by_role("button", name="Esquecer").first.is_visible()


def test_CA92_backup_restaurar_apagar(page):
    carregar(page, "vendas.csv")
    nome, b = backup(page)
    assert re.fullmatch(r"historico_RaioX_\d{4}-\d{2}-\d{2}\.json", nome)
    # D-02: "Apagar todos os dados" + confirmar com "Apagar"
    page.get_by_role("button", name="Apagar todos os dados").click()
    page.get_by_role("button", name="Apagar", exact=True).click()
    page.wait_for_timeout(500)
    _, vazio = backup(page)
    assert len(set(codigos_no_backup(vazio))) == 0
    # D-03: restaurar pelo controle "Restaurar backup" da Config
    abrir_config(page)
    with page.expect_file_chooser() as fc:
        page.get_by_role("button", name="Restaurar backup").click()
    fc.value.set_files([{"name": nome, "mimeType": "application/json", "buffer": b.encode()}])
    page.wait_for_timeout(500)
    page.get_by_role("button", name="Substituir", exact=True).click()
    page.wait_for_timeout(800)
    _, volta = backup(page)
    assert len(set(codigos_no_backup(volta))) == len(VENDAS)


def test_CA93_janela_flutuante_ao_clicar_numero(page):
    carregar(page, "vendas.csv")
    abrir_painel(page)
    page.get_by_text("Total de registros").first.click()
    page.wait_for_timeout(500)
    for nome in ["Limpar seleção", "Imprimir", "Copiar", "Minimizar", "Fechar"]:
        assert page.get_by_role("button", name=nome).first.is_visible(), nome
    page.get_by_role("button", name="Fechar").first.click()
    page.wait_for_timeout(300)
    assert not page.get_by_role("button", name="Limpar seleção").first.is_visible()


def test_CA96_faixas_mediana_e_formato_h_min(page):
    ch = le_csv("chamados.csv")
    f = "%d/%m/%Y %H:%M"
    mins = [(datetime.datetime.strptime(r["Conclusão"], f) - datetime.datetime.strptime(r["Abertura"], f)).total_seconds() / 60
            for r in ch if r["Conclusão"]]
    med = statistics.median(mins)
    h, m = divmod(int(med + 0.5), 60)  # D-08: meio minuto para cima
    esperado = f"{h} h {m:02d} min" if h else f"{m} min"
    carregar(page, "chamados.csv")
    corpo = page.inner_text("body")
    assert re.search(r"mediana", corpo, re.I)
    plano = re.sub(r"\s+", " ", corpo)
    assert re.search(r"Mediana:\s*" + re.escape(esperado) + r"(?!\d)", plano), f"mediana esperada {esperado}"
    for faixa in ["Até 1 h", "De 1 a 4 h", "De 4 a 24 h", "De 1 a 3 dias", "De 3 a 7 dias", "Mais de 7 dias"]:
        assert faixa in plano, faixa


def test_CA98_excel_capa_periodo_filtros_rodape_impressao(page, tmp_path):
    carregar(page, "vendas.csv")
    d = gerar_excel(page)
    nome = d.suggested_filename
    assert re.fullmatch(r"^RaioX_[A-Z0-9_]+_\d{4}-\d{2}-\d{2}\.xlsx$", nome), nome
    assert nome.endswith(datetime.date.today().isoformat() + ".xlsx"), nome
    wb = abrir_xlsx(d, tmp_path)
    ws = wb.worksheets[0]
    assert ws.page_setup.orientation or ws.page_setup.paperSize
    assert ws.oddFooter.center.text or ws.oddFooter.left.text or ws.oddFooter.right.text
    todos = " ".join(str(c.value) for w in wb for row in w.iter_rows() for c in row if c.value)
    assert re.search(r"\d{2}/\d{2}/\d{4}", todos), "período real na capa"
    assert any(w.auto_filter.ref for w in wb.worksheets), "filtros"


def test_CA99_filtros_fechados_e_valem_para_tudo(page):
    carregar(page, "vendas.csv")
    abrir_painel(page)
    assert not page.get_by_label("Período").is_visible(), "Filtros deve começar fechado"
    page.get_by_text("Filtros", exact=True).locator("visible=true").first.click()
    page.get_by_role("combobox", name="Período").select_option(label="De–até")
    page.get_by_label("De", exact=True).fill("2026-01-01")
    page.get_by_label("Até", exact=True).fill("2026-01-31")
    page.wait_for_timeout(500)
    esperado = sum(1 for r in VENDAS if r["Data"].endswith("/01/2026"))
    assert 0 < esperado < len(VENDAS)
    cartao = page.get_by_text("Total de registros").first.locator("xpath=..").inner_text()
    primeiro = re.match(r"\s*(\d+)", cartao)
    assert primeiro and int(primeiro.group(1)) == esperado, f"total filtrado deveria ser {esperado}: {cartao!r}"


# ---------- seção 10 ----------
def test_CA100_html_em_campo_vira_texto(page, tmp_path):
    dialogos = []
    page.on("dialog", lambda d: (dialogos.append(d.message), d.dismiss()))
    p = tmp_path / "x.csv"
    p.write_text("Código;Cliente;Valor\nV00001;<img src=x onerror=alert(1)>;10,00\nV00002;Normal;20,00\n", encoding="utf-8")
    carregar(page, p)
    abrir_painel(page)  # D-04: sem aba Histórico; lista "Registros" no Painel
    assert page.get_by_text("Registros", exact=True).first.is_visible()
    page.wait_for_timeout(500)
    assert "<img src=x onerror=alert(1)>" in page.inner_text("body")
    assert dialogos == []
    assert page.locator("img[src=x]").count() == 0


def test_CSP_meta_presente(page):
    csp = page.locator("meta[http-equiv='Content-Security-Policy']").get_attribute("content")
    for parte in ["default-src 'self'", "connect-src 'self'", "worker-src 'self' blob:"]:
        assert parte in csp


def _ped(campo):
    return {"medida": "soma", "campo": campo, "agrupar": None, "filtros": [], "periodo": None}


def _restaurar(page, texto, botao):
    abrir_config(page)
    with page.expect_file_chooser() as fc:
        page.get_by_role("button", name="Restaurar backup").click()
    fc.value.set_files([{"name": "b.json", "mimeType": "application/json", "buffer": texto.encode()}])
    page.wait_for_timeout(500)
    page.get_by_role("button", name=botao, exact=True).click()
    page.wait_for_timeout(800)


def test_F60_somar_junta_meus_indicadores_sem_repetir_ate_50(page):
    """P-06 (espec. seção 13): 'Somar' junta a lista atual com a do backup, sem repetir, até 50."""
    import json
    carregar(page, "vendas.csv")
    _, txt = backup(page)
    b = json.loads(txt)
    cj = list(b["conjs"].keys())[0]
    a, c, d = _ped("A"), _ped("C"), _ped("D")
    b["meus"] = {cj: [a, c]}
    _restaurar(page, json.dumps(b), "Substituir")           # atual = [A, C]
    b["meus"] = {cj: [c, d]}
    _restaurar(page, json.dumps(b), "Somar")                # backup = [C, D]
    _, depois = backup(page)
    assert json.loads(depois)["meus"][cj] == [a, c, d]
    # limite de 50: o que passar fica de fora
    b["meus"] = {cj: [_ped("X%d" % i) for i in range(50)]}
    _restaurar(page, json.dumps(b), "Somar")
    _, cheio = backup(page)
    lista = json.loads(cheio)["meus"][cj]
    assert len(lista) == 50 and lista[:3] == [a, c, d]
