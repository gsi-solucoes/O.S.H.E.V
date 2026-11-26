"""Suite da etapa 7a (F-58): planilhas, JSON, XML e zip. Escrita SO a partir da especificacao v1.7
(secoes 0.8 e 7: R-110 a R-112, regras 1-8, CA-70, CA-71, CA-72, CA-70b, CA-75a, CA-110x).
Oraculos em Python sobre tests/dados/vendas.csv, conferidos pelo backup e pelos exemplos da janela
'O que você quer acompanhar?' (nunca por codigo do app).

Suposicoes (texto mais literal):
 S1 o backup e um JSON; um registro e o dict que tem um valor-texto Vnnnnn/Cnnnnn (como no CA-81).
 S2 Valor e conferido pelo numero (1234,5 == 1234,50), pois a regra 2 tira zeros a direita; Data, Cliente,
    Regiao, Vendedor e Situacao, pelo texto exato do CSV.
 S3 nome sugerido do relatorio: aparece como valor de um campo de texto ou no texto da janela
    'Esta coluna é o quê?'; nome de conjunto tambem aparece no backup.
 S4 <arquivo> das mensagens e o nome do arquivo (no zip, a mensagem contem 'nome: formato ...' a partir do
    nome do arquivo de dentro, com ou sem pasta antes).
 S5 JSON/XML mal formado = 'Não consegui ler <arquivo>.' (arquivo corrompido).
 S6 'ate 50 arquivos uteis': 50 CSV no zip entram; 60 = 'zip grande demais'.
 S7 as mensagens (toast) sao capturadas por um MutationObserver (podem sumir antes de o teste olhar).
 S8 o <input type=file> tem atributo accept com as extensoes de R-110 (e sem .xlsm/.pdf).
"""
import io, json, re, zipfile, collections, datetime
import pytest
from conftest import DADOS
from test_etapa1 import (le_csv, enviar, mapear_se_preciso, fechar_acompanhar, carregar, backup, abrir_config,
                         abrir_painel)
from test_etapa2 import exemplo, lideres, num, valor

VENDAS = le_csv("vendas.csv")
CHAMADOS = le_csv("chamados.csv")
N = len(VENDAS)
COD = re.compile(r"[VC]\d{5}")
CAMPOS_TEXTO = ["Data", "Cliente", "Região", "Vendedor", "Situação"]


# ---------- auxiliares ----------
def registros(o):
    if isinstance(o, dict):
        if any(isinstance(v, str) and COD.fullmatch(v) for v in o.values()):
            yield o
        for v in o.values():
            yield from registros(v)
    elif isinstance(o, list):
        for v in o:
            yield from registros(v)


def escalares(o):
    if isinstance(o, dict):
        for v in o.values():
            yield from escalares(v)
    elif isinstance(o, list):
        for v in o:
            yield from escalares(v)
    else:
        yield o


def por_codigo(b):
    d = collections.defaultdict(list)
    for r in registros(json.loads(b)):
        cod = next(v for v in r.values() if isinstance(v, str) and COD.fullmatch(v))
        d[cod].append(list(escalares(r)))
    return d


def como_num(x):
    if isinstance(x, bool):
        return None
    if isinstance(x, (int, float)):
        return float(x)
    if isinstance(x, str) and re.fullmatch(r"-?\d+(,\d+)?", x.strip()):
        return float(x.strip().replace(",", "."))
    return None


def iso(t):
    """dd/mm/aaaa[ hh:mm] -> ISO como o backup guarda (aaaa-mm-ddThh:mm)."""
    m = re.fullmatch(r"(\d\d)/(\d\d)/(\d{4})(?: (\d\d):(\d\d))?", t)
    return f"{m[3]}-{m[2]}-{m[1]}T{m[4] or '00'}:{m[5] or '00'}"


def tem_data(esc, t):
    return t in esc or iso(t) in esc


def fechar_todos(page):
    for _ in range(3):
        fechar_acompanhar(page)


def tem_numero(esc, v):
    return any(como_num(x) is not None and abs(como_num(x) - v) < 0.005 for x in esc)


def confere_vendas(b, esperado=VENDAS):
    """Oraculo do CSV contra o backup: total, uma entrada por codigo, por cliente e valor."""
    d = por_codigo(b)
    cods = {r["Código"] for r in esperado}
    assert {c for c in d if c.startswith("V")} == cods
    assert all(len(v) == 1 for v in d.values()), "registro duplicado"
    por_cli = collections.Counter()
    soma = 0.0
    for r in esperado:
        esc = d[r["Código"]][0]
        assert tem_data(esc, r["Data"]), f"{r['Código']}: Data {r['Data']} ausente em {esc!r}"
        for c in CAMPOS_TEXTO[1:]:
            assert r[c] in esc, f"{r['Código']}: {c}={r[c]!r} ausente em {esc!r}"
        assert tem_numero(esc, valor(r)), f"{r['Código']}: Valor {r['Valor']} ausente em {esc!r}"
        por_cli[r["Cliente"]] += 1
        soma += valor(r)
    assert por_cli == collections.Counter(x["Cliente"] for x in esperado)
    assert abs(soma - sum(valor(x) for x in esperado)) < 0.01


def confere_exemplos(page):
    """Exemplos da janela R-51 (total, lider por cliente, soma) contra o oraculo do CSV."""
    t = exemplo(page, "Total de registros")
    assert int(re.search(r"([\d.]+) registros", t).group(1).replace(".", "")) == N
    t = exemplo(page, "Por Cliente")
    m = re.search(r"Cliente:\s*(.+?) lidera com ([\d.]+)", t)
    assert m, t
    lid, mx = lideres(r["Cliente"] for r in VENDAS)
    assert m.group(1).strip() in lid and int(m.group(2).replace(".", "")) == mx
    t = exemplo(page, "Valor (soma, média e mediana)")
    m = re.search(r"Soma:\s*([\d.]+,\d{2})", t)
    assert m, t
    assert abs(num(m.group(1)) - sum(valor(r) for r in VENDAS)) <= 0.011


def mapear_tudo(page, maximo=6):
    """Responde 'Esta coluna é o quê?' ate nao aparecer mais; devolve (textos, valores de campos) de cada janela."""
    janelas = []
    for _ in range(maximo):
        if not page.get_by_text("Esta coluna é o quê?").first.is_visible():
            break
        d = page.locator("dialog, [role=dialog]").filter(has_text="Esta coluna é o quê?").first
        valores = d.locator("input").evaluate_all("els=>els.map(e=>e.value)")
        janelas.append((re.sub(r"\s+", " ", d.inner_text()), valores))
        mapear_se_preciso(page)
    return janelas


def carregar_tudo(page, *arquivos):
    enviar(page, *arquivos)
    j = mapear_tudo(page)
    fechar_todos(page)
    return j


def enviar_vendo_mensagens(page, *arquivos, espera=1500):
    """Envia os arquivos e devolve todo texto que apareceu na tela (toasts podem sumir rapido)."""
    page.evaluate("""()=>{window.__tt=[];new MutationObserver(ms=>{for(const m of ms){
      for(const n of m.addedNodes){window.__tt.push(n.textContent||'')}
      if(m.type==='characterData')window.__tt.push(m.target.textContent||'')}})
      .observe(document.body,{childList:true,subtree:true,characterData:true});}""")
    enviar(page, *arquivos)
    page.wait_for_timeout(espera)
    return " | ".join(page.evaluate("window.__tt")) + " | " + page.evaluate("document.body.innerText")


def codigos(page):
    return set(COD.findall(backup(page)[1]))


def vivo(page):
    """A pagina segue respondendo e nada poluiu o prototipo."""
    assert page.evaluate("({}).polluted") is None
    page.get_by_text("Config", exact=True).first.click()
    assert page.get_by_role("button", name="Baixar backup").is_visible()


def tem_nome(janelas, nome):
    for texto, valores in janelas:
        if nome in valores or (nome in texto and nome + ".xlsx" not in texto):
            return True
    return False


def csv_forjado(prefixo, i, n=3):
    linhas = ["Código;Cliente;Valor"] + [f"V{i * 10 + j:05d};Cli {prefixo}{j};{j + 1},5" for j in range(n)]
    return "\r\n".join(linhas) + "\r\n"


def zip_bytes(itens):
    b = io.BytesIO()
    with zipfile.ZipFile(b, "w", zipfile.ZIP_DEFLATED) as z:
        for nome, dados in itens:
            z.writestr(nome, dados)
    return b.getvalue()


def grava(tmp_path, nome, dados):
    p = tmp_path / nome
    p.write_bytes(dados if isinstance(dados, bytes) else dados.encode("utf-8"))
    return p


skip_xls = pytest.mark.skipif(not (DADOS / "vendas.xls").exists(), reason="vendas.xls nao gerado (sem LibreOffice)")
skip_ods = pytest.mark.skipif(not (DADOS / "vendas.ods").exists(), reason="vendas.ods nao gerado (sem LibreOffice)")


# ---------- R-110 ----------
def test_R110_botao_aceita_os_formatos_novos_e_varios_arquivos(page):
    acc = page.locator("input[type=file]").first.get_attribute("accept") or ""
    for ext in [".csv", ".txt", ".tsv", ".xlsx", ".xls", ".ods", ".json", ".xml", ".zip"]:
        assert ext in acc.lower().split(",") or ext in acc.lower(), f"{ext} fora do accept: {acc!r}"
    assert ".xlsm" not in acc.lower() and ".xlsb" not in acc.lower()   # .pdf passou a valer na 7b (R-120)
    assert page.locator("input[type=file]").first.get_attribute("multiple") is not None


def test_R110_tipos_misturados_no_mesmo_envio(page):
    carregar_tudo(page, "chamados.csv", "vendas.xlsx", "vendas.json")
    d = por_codigo(backup(page)[1])
    assert len({c for c in d if c.startswith("V")}) == N
    assert len({c for c in d if c.startswith("C")}) == len(CHAMADOS)
    assert all(len(v) == 1 for v in d.values())


# ---------- CA-70, CA-71, CA-72 ----------
def _mesmos_resultados(page, arquivo):
    enviar(page, arquivo)
    mapear_tudo(page)
    from test_etapa2 import dlg, JANELA
    dlg(page, JANELA).wait_for(state="visible")
    confere_exemplos(page)
    fechar_acompanhar(page)
    confere_vendas(backup(page)[1])
    abrir_painel(page)
    assert page.get_by_text(f"{N:,}".replace(",", "."), exact=False).first.is_visible()


def test_CA70_xlsx_mesmos_resultados_do_csv(page):
    _mesmos_resultados(page, "vendas.xlsx")


@skip_xls
def test_CA71_xls_mesmos_resultados_do_csv(page):
    _mesmos_resultados(page, "vendas.xls")


@skip_ods
def test_CA71_ods_mesmos_resultados_do_csv(page):
    _mesmos_resultados(page, "vendas.ods")


def test_CA72_json_mesmos_resultados_do_csv(page):
    _mesmos_resultados(page, "vendas.json")


def test_CA72_xml_mesmos_resultados_do_csv(page):
    _mesmos_resultados(page, "vendas.xml")


# ---------- regra 1: nome sugerido ----------
def test_regra1_uma_aba_nome_do_arquivo_sem_extensao(page):
    enviar(page, "vendas.xlsx")
    j = mapear_tudo(page)
    assert j, "a tela 'Esta coluna é o quê?' deveria aparecer na 1a vez"
    assert tem_nome(j, "vendas"), j


# ---------- CA-70b ----------
def test_CA70b_duas_abas_dois_conjuntos(page):
    enviar(page, "vendas_2abas.xlsx")
    j = mapear_tudo(page)
    fechar_todos(page)
    assert tem_nome(j, "vendas_2abas - Vendas"), j
    assert tem_nome(j, "vendas_2abas - Chamados"), j
    b = backup(page)[1]
    d = por_codigo(b)
    assert len({c for c in d if c.startswith("V")}) == 500
    assert len({c for c in d if c.startswith("C")}) == 300
    assert "vendas_2abas - Vendas" in b and "vendas_2abas - Chamados" in b
    ch = {r["Código"]: r for r in CHAMADOS}
    for cod in list(ch)[:30]:
        esc = d[cod][0]
        assert ch[cod]["Categoria"] in esc and ch[cod]["Responsável"] in esc and tem_data(esc, ch[cod]["Abertura"])


# ---------- CA-75a ----------
def test_CA75a_zip_mistura_csv_xlsx_json_sem_duplicar(page):
    carregar_tudo(page, "vendas_mistura.zip")
    b = backup(page)[1]
    d = por_codigo(b)
    assert len({c for c in d if c.startswith("V")}) == 500
    assert len({c for c in d if c.startswith("C")}) == 300
    assert all(len(v) == 1 for v in d.values()), "xlsx e json deveriam juntar por codigo"
    confere_vendas(b)


# ---------- CA-80 entre tipos ----------
@pytest.mark.parametrize("outro", ["vendas.xlsx", "vendas.json", "vendas.xml"])
def test_CA80_formato_lembrado_vale_entre_tipos_csv_depois_de_outro(page, outro):
    carregar(page, "vendas.csv")
    enviar(page, outro)
    assert not page.get_by_text("Esta coluna é o quê?").first.is_visible(), "formato lembrado deveria valer"
    fechar_acompanhar(page)
    b = backup(page)[1]
    d = por_codigo(b)
    assert len(d) == N and all(len(v) == 1 for v in d.values()), "contagem dobrou"
    confere_vendas(b)


def test_CA80_formato_lembrado_vale_entre_tipos_xlsx_depois_de_csv_e_reenvio(page):
    carregar(page, "vendas.xlsx")
    enviar(page, "vendas.csv")
    assert not page.get_by_text("Esta coluna é o quê?").first.is_visible()
    fechar_acompanhar(page)
    enviar(page, "vendas.xlsx")
    fechar_acompanhar(page)
    d = por_codigo(backup(page)[1])
    assert len(d) == N and all(len(v) == 1 for v in d.values())


# ---------- regra 2: valores ----------
def test_regra2_tipos_de_celula_viram_o_texto_esperado(page, tmp_path):
    ox = pytest.importorskip("openpyxl")
    wb = ox.Workbook()
    ws = wb.active
    ws.title = "Tipos"
    ws.append(["Código", "Valor", "Qtd", "Data", "Hora", "Ativo", "Inativo", "Erro", "Vazio", "Texto"])
    ws.append(["V00001", 2014.78, 3, datetime.date(2026, 3, 5), datetime.datetime(2026, 3, 5, 14, 30), True, False,
               None, None, "abc"])
    ws["H2"].value = "#DIV/0!"
    ws["H2"].data_type = "e"
    ws.append(["V00002", 1234567.5, 10.0, datetime.date(2026, 12, 31), datetime.datetime(2026, 12, 31, 0, 5), False,
               True, None, None, "def"])
    p = tmp_path / "tipos.xlsx"
    wb.save(p)
    carregar_tudo(page, p)
    d = por_codigo(backup(page)[1])
    a, c = d["V00001"][0], d["V00002"][0]
    assert tem_numero(a, 2014.78)
    assert not any(isinstance(x, str) and re.search(r"\d\.\d{3},", x) for x in a + c), "milhar nao deveria ter ponto"
    assert tem_numero(c, 1234567.5) and tem_numero(a, 3) and tem_numero(c, 10)
    assert not any(isinstance(x, str) and x in ("10,0", "3,0") for x in a + c), "inteiro sem casas"
    assert tem_data(a, "05/03/2026") and tem_data(a, "05/03/2026 14:30")
    assert tem_data(c, "31/12/2026") and tem_data(c, "31/12/2026 00:05")
    assert "Sim" in a and "Não" in a and "Sim" in c and "Não" in c
    assert not any(isinstance(x, str) and "#DIV" in x for x in a), "erro de celula deveria virar vazio"
    assert "abc" in a and "def" in c


# ---------- regra 3: JSON ----------
def test_regra3_json_objeto_com_uma_lista_e_valores(page, tmp_path):
    dados = {"vendas": [{"Código": "V00001", "Cliente": "Alfa", "Valor": 10.5, "Ok": True, "Obs": {"a": 1}, "Lst": [1, 2]},
                        {"Código": "V00002", "Cliente": "Beta", "Valor": 20, "Ok": False, "Extra": "x"}]}
    carregar_tudo(page, grava(tmp_path, "obj.json", json.dumps(dados)))
    d = por_codigo(backup(page)[1])
    a, c = d["V00001"][0], d["V00002"][0]
    assert tem_numero(a, 10.5) and "Sim" in a and "Não" in c
    assert '{"a":1}' in a or '{"a": 1}' in a, a
    assert "[1,2]" in a or "[1, 2]" in a, a
    assert "x" in c


def test_regra7_json_com_chave_proto_e_coluna_comum(page, tmp_path):
    txt = ('[{"Código":"V00001","__proto__":{"polluted":"sim"},"constructor":"c1","Valor":1},'
           '{"Código":"V00002","__proto__":"p2","constructor":"c2","Valor":2}]')
    msgs = enviar_vendo_mensagens(page, grava(tmp_path, "proto.json", txt))
    mapear_tudo(page)
    fechar_acompanhar(page)
    assert page.evaluate("({}).polluted") is None
    b = backup(page)[1]
    assert {"V00001", "V00002"} <= codigos(page)
    assert "__proto__" in b and "c1" in b and "p2" in b
    vivo(page)


# ---------- regra 7 e CA-110x ----------
def test_CA110x_planilha_com_coluna_proto_e_comum(page, tmp_path):
    ox = pytest.importorskip("openpyxl")
    wb = ox.Workbook()
    ws = wb.active
    ws.append(["Código", "__proto__", "constructor", "Valor"])
    for i in range(1, 21):
        ws.append([f"V{i:05d}", '{"polluted":"sim"}', f"k{i}", i])
    p = tmp_path / "proto.xlsx"
    wb.save(p)
    carregar_tudo(page, p)
    assert page.evaluate("({}).polluted") is None
    b = backup(page)[1]
    assert len(por_codigo(b)) == 20 and "__proto__" in b
    vivo(page)


def test_regra6_nome_de_coluna_so_entra_por_texto(page, tmp_path):
    ox = pytest.importorskip("openpyxl")
    wb = ox.Workbook()
    ws = wb.active
    ws.title = "<i>aba"
    ws.append(["Código", "<img src=x onerror=window.__x=1>", "Valor"])
    for i in range(1, 6):
        ws.append([f"V{i:05d}", "abc", i])
    p = tmp_path / "html.xlsx"
    wb.save(p)
    enviar(page, p)
    assert page.locator("img[src='x']").count() == 0
    mapear_tudo(page)
    fechar_acompanhar(page)
    assert page.evaluate("window.__x") is None
    assert page.locator("img[src='x']").count() == 0


def test_CA110x_zip_com_60_arquivos_zip_grande_demais(page, tmp_path):
    z = grava(tmp_path, "muitos.zip", zip_bytes([(f"a{i:02d}.csv", csv_forjado("m", i)) for i in range(60)]))
    msgs = enviar_vendo_mensagens(page, z)
    assert "muitos.zip: zip grande demais." in msgs
    assert not page.get_by_text("Esta coluna é o quê?").first.is_visible()
    fechar_acompanhar(page)
    assert codigos(page) == set(), "nada do zip deveria entrar"
    vivo(page)


def test_CA110x_zip_com_50_arquivos_ainda_entra(page, tmp_path):
    z = grava(tmp_path, "cinquenta.zip", zip_bytes([(f"a{i:02d}.csv", csv_forjado("m", i)) for i in range(50)]))
    msgs = enviar_vendo_mensagens(page, z)
    assert "zip grande demais" not in msgs
    mapear_tudo(page)
    fechar_acompanhar(page)
    assert len(codigos(page)) == 150


def test_CA110x_zip_com_mais_de_200mb_declarados_zip_grande_demais(page, tmp_path):
    bloco = b"x" * (41 * 1024 * 1024)
    z = grava(tmp_path, "enorme.zip", zip_bytes([(f"g{i}.csv", bloco) for i in range(5)]))
    assert z.stat().st_size < 20 * 1024 * 1024
    msgs = enviar_vendo_mensagens(page, z, espera=3000)
    assert "enorme.zip: zip grande demais." in msgs
    fechar_acompanhar(page)
    assert codigos(page) == set()
    vivo(page)


def test_CA110x_json_lista_aninhada_nao_acho_cabecalho(page, tmp_path):
    p = grava(tmp_path, "aninhado.json", json.dumps([[{"Código": "V00001", "a": 1}], [{"Código": "V00002", "a": 2}]]))
    msgs = enviar_vendo_mensagens(page, p)
    assert "Não achei o cabeçalho em aninhado.json." in msgs
    assert not page.get_by_text("Esta coluna é o quê?").first.is_visible()
    assert codigos(page) == set()
    vivo(page)


def test_CA110x_json_objeto_com_duas_listas_nao_acho_cabecalho(page, tmp_path):
    p = grava(tmp_path, "duas.json", json.dumps({"a": [{"Código": "V00001"}], "b": [{"Código": "V00002"}]}))
    msgs = enviar_vendo_mensagens(page, p)
    assert "Não achei o cabeçalho em duas.json." in msgs
    assert codigos(page) == set()
    vivo(page)


def test_CA110x_json_que_nao_e_lista_nem_objeto_com_lista(page, tmp_path):
    msgs = enviar_vendo_mensagens(page, grava(tmp_path, "num.json", "42"))
    assert "Não achei o cabeçalho em num.json." in msgs
    vivo(page)


def test_CA110x_xml_sem_repeticao_nao_acho_cabecalho(page, tmp_path):
    p = grava(tmp_path, "unico.xml", "<?xml version='1.0'?><r><Código>V00001</Código><Cliente>Alfa</Cliente></r>")
    msgs = enviar_vendo_mensagens(page, p)
    assert "Não achei o cabeçalho em unico.xml." in msgs
    assert not page.get_by_text("Esta coluna é o quê?").first.is_visible()
    assert codigos(page) == set()
    vivo(page)


def test_regra4_xml_atributos_depois_dos_filhos_e_colunas_na_ordem(page, tmp_path):
    xml = ("<?xml version='1.0'?><lista>"
           "<item id='1'><Código>V00001</Código><Cliente>Alfa</Cliente></item>"
           "<item id='2'><Código>V00002</Código><Cliente>Beta</Cliente></item></lista>")
    carregar_tudo(page, grava(tmp_path, "itens.xml", xml))
    d = por_codigo(backup(page)[1])
    assert set(d) == {"V00001", "V00002"}
    assert "Alfa" in d["V00001"][0] and "1" in [str(x) for x in d["V00001"][0]]


def test_CA110x_xlsx_truncado_nao_consegui_ler(page, tmp_path):
    bruto = (DADOS / "vendas.xlsx").read_bytes()
    p = grava(tmp_path, "truncado.xlsx", bruto[: len(bruto) // 2])
    msgs = enviar_vendo_mensagens(page, p)
    assert "Não consegui ler truncado.xlsx." in msgs
    assert not page.get_by_text("Esta coluna é o quê?").first.is_visible()
    assert codigos(page) == set()
    vivo(page)


def test_CA110x_xlsx_lixo_e_json_mal_formado_nao_consegui_ler(page, tmp_path):
    a = grava(tmp_path, "lixo.xlsx", b"isto nao e um zip" * 50)
    b = grava(tmp_path, "quebrado.json", '[{"Código": "V00001", ')
    c = grava(tmp_path, "quebrado.xml", "<r><a><b></r>")
    msgs = enviar_vendo_mensagens(page, a, b, c)
    for nome in ["lixo.xlsx", "quebrado.json", "quebrado.xml"]:
        assert f"Não consegui ler {nome}." in msgs, nome
    vivo(page)


def test_R112_planilha_vazia_nao_acho_cabecalho(page, tmp_path):
    ox = pytest.importorskip("openpyxl")
    p = tmp_path / "vazia.xlsx"
    ox.Workbook().save(p)
    msgs = enviar_vendo_mensagens(page, p)
    assert "Não achei o cabeçalho em vazia.xlsx." in msgs
    assert codigos(page) == set()


@pytest.mark.parametrize("nome", ["macro.xlsm", "doc.rtf", "foto.png", "bin.xlsb", "texto.docx"])
def test_R112_formato_nao_suportado_mensagem_exata(page, tmp_path, nome):
    p = grava(tmp_path, nome, b"%PDF-1.4 conteudo qualquer\x00\x01\x02")
    msgs = enviar_vendo_mensagens(page, p)
    assert f"{nome}: formato não suportado." in msgs
    assert not page.get_by_text("Esta coluna é o quê?").first.is_visible()
    assert codigos(page) == set()
    vivo(page)


def test_R112_nao_suportado_nao_impede_os_outros_do_mesmo_envio(page, tmp_path):
    p = grava(tmp_path, "macro.xlsm", b"PK\x03\x04 nada")
    msgs = enviar_vendo_mensagens(page, p, DADOS / "vendas.csv")
    assert "macro.xlsm: formato não suportado." in msgs
    mapear_tudo(page)
    fechar_acompanhar(page)
    assert len(codigos(page)) == N


def test_regra5_zip_dentro_de_zip_nao_e_aberto_e_os_outros_entram(page, tmp_path):
    interno = zip_bytes([("dentro.csv", csv_forjado("i", 90))])
    z = grava(tmp_path, "externo.zip", zip_bytes([("a.csv", csv_forjado("e", 1)), ("interno.zip", interno)]))
    msgs = enviar_vendo_mensagens(page, z)
    mapear_tudo(page)
    fechar_todos(page)
    msgs += " | ".join(page.evaluate("window.__tt"))
    assert "interno.zip: formato não suportado (ignorado)." in msgs
    cods = codigos(page)
    assert {f"V{10 + j:05d}" for j in range(3)} <= cods
    assert not {f"V{900 + j:05d}" for j in range(3)} & cods, "o zip de dentro nao deveria ser aberto"


def test_regra5_zip_com_arquivo_nao_suportado_ignora_so_ele(page, tmp_path):
    z = grava(tmp_path, "com_pdf.zip", zip_bytes([("a.csv", csv_forjado("p", 2)), ("foto.png", b"\x89PNG\r\n"),
                                                   ("pasta/b.csv", csv_forjado("q", 3))]))
    msgs = enviar_vendo_mensagens(page, z)
    mapear_tudo(page)
    fechar_todos(page)
    msgs += " | ".join(page.evaluate("window.__tt"))
    assert "foto.png: formato não suportado (ignorado)." in msgs
    assert "com_pdf.zip: zip grande demais" not in msgs
    cods = codigos(page)
    assert {f"V{20 + j:05d}" for j in range(3)} | {f"V{30 + j:05d}" for j in range(3)} <= cods


def test_regra5_zip_com_pastas_le_arquivos_de_dentro(page, tmp_path):
    z = grava(tmp_path, "pastas.zip", zip_bytes([("x/y/a.csv", csv_forjado("a", 4)), ("z/b.csv", csv_forjado("b", 5))]))
    carregar_tudo(page, z)
    assert len(codigos(page)) == 6


# ---------- regra 7: nada executa, sem rede ----------
def test_regra7_sem_rede_ao_ler_formatos_novos(ctx, page):
    carregar_tudo(page, "vendas.xlsx", "vendas.json", "vendas.xml", "vendas_mistura.zip")
    externas = [u for u in ctx.reqs if not u.startswith(("http://localhost:8767", "data:", "blob:"))]
    assert not externas, externas


def test_regra7_leitor_e_local_sem_cdn(page):
    html = page.content()
    assert not re.search(r"<script[^>]+src=[\"']https?://", html)


# ---------- F-66: Médio e Baixos da revisão de segurança da etapa 7a (regressão) ----------
def test_f66_celula_longe_nao_monta_grade_gigante(page, tmp_path):
    import time
    openpyxl = pytest.importorskip("openpyxl")
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(["Código", "Cliente"])
    ws.append(["V00001", "Alfa Teste"])
    ws["XFD200000"] = "longe"
    p = tmp_path / "longe.xlsx"
    wb.save(p)
    t0 = time.time()
    enviar(page, p)
    page.wait_for_timeout(500)
    mapear_tudo(page)
    fechar_acompanhar(page)
    assert time.time() - t0 < 12, "a aba travou lendo uma planilha de 1,5 KB"
    assert "V00001" in codigos(page)
    vivo(page)


def test_f66_bomba_de_descompressao_em_xlsx_nao_consegui_ler(page, tmp_path):
    import zipfile
    openpyxl = pytest.importorskip("openpyxl")
    wb = openpyxl.Workbook()
    wb.active.append(["Código", "Cliente"])
    base = tmp_path / "base.xlsx"
    wb.save(base)
    p = tmp_path / "bomba.xlsx"
    with zipfile.ZipFile(base) as a, zipfile.ZipFile(p, "w", zipfile.ZIP_DEFLATED) as b:
        for i in a.infolist():
            b.writestr(i.filename, a.read(i.filename))
        with b.open("xl/bomba.bin", "w", force_zip64=True) as f:
            bloco = bytes(1024 * 1024)
            for _ in range(250):
                f.write(bloco)
    msgs = enviar_vendo_mensagens(page, p, espera=6000)
    assert "Não consegui ler bomba.xlsx." in msgs
    vivo(page)
