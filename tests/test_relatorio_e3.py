"""F-85: aceite da etapa E3 (formas de gráfico novas, especificação 9c.10, R-160 a R-162, CA-250 a CA-259, D-77).
Escrito SÓ a partir da especificação (não lê src/). Oráculos em Python sobre tests/dados/.
Seletores: só o que a 9c.10 define (role="img" com aria-label `<Forma>: <título>`, pedaços com aria-label
`<nome>: <valor>`, focáveis, abrem a janela de registros). `data-forma` NÃO é definido para as formas novas
(ver docs/duvidas.md), por isso não é usado. Relógio do navegador fixo em 28/11/2026 12:00."""
import re, json, datetime, collections
import pytest
from conftest import URL
from test_etapa1 import carregar, backup, abrir_config, abrir_painel
from test_etapa2 import dlg
from test_etapa4 import gerar as gerar_excel
from test_etapa6 import (preparar, edicao, sel, opcoes, escolhido, reabrir, restaurar, celular, heading)
from test_relatorio_e1 import (pg, abrir_relatorio, editar, concluir, controles, rel, br, pct, d_, val,
                               VENDAS, CHAMADOS, V_DATAS, concentra, em_aberto)

REGIOES = collections.Counter(r["Região"] for r in VENDAS)
CLIENTES = collections.Counter(r["Cliente"] for r in VENDAS)
SOMA_CLI = collections.defaultdict(float)
for _r in VENDAS:
    SOMA_CLI[_r["Cliente"]] += val(_r["Valor"])
MESES = collections.Counter(f"{d.month:02d}/{d.year}" for d in V_DATAS)
CONCLUIDOS = sum(1 for r in VENDAS if not em_aberto(r["Situação"]))

OPC_CONT = ["Barras", "Pizza", "Rosca", "Radar", "Tabela"]
OPC_VALOR = ["Barras", "Pizza", "Rosca", "Radar", "Bolhas", "Tabela"]
OPC_MES = ["Barras", "Linha", "Área", "Pizza", "Rosca", "Tabela"]
OPC_PCT = ["Barras", "Pizza", "Rosca", "Radar", "Velocímetro", "Tabela"]


# ---------------- auxiliares ----------------
def forma(pg, titulo, nome):
    """Painel (Editar layout): escolhe a forma de um bloco."""
    sel(pg, titulo, "Forma").select_option(label=nome)
    pg.wait_for_timeout(300)


def painel_com(pg, nomes, arquivo="vendas.csv"):
    preparar(pg, nomes, arquivo)
    abrir_painel(pg)
    edicao(pg)


def img(pg, forma_, titulo):
    return pg.get_by_role("img", name=f"{forma_}: {titulo}", exact=True).locator("visible=true")


def pedacos(el, prefixo=""):
    return el.locator(f"[aria-label^='{prefixo}'][aria-label*=': ']")


def rotulos(el):
    return el.evaluate("e => [...e.querySelectorAll('[aria-label]')].map(x => x.getAttribute('aria-label'))")


def texto_de(el):
    return re.sub(r"\s+", " ", el.evaluate("e => e.textContent"))


def janela_registros(pg):
    """Janela de registros: a que traz `Limpar seleção` (R-37). Devolve (texto, nº de linhas de dados)."""
    b = pg.get_by_role("button", name="Limpar seleção", exact=True).locator("visible=true").first
    b.wait_for(state="visible")
    return b.evaluate("""b => { let e = b; while (e.parentElement && !e.querySelector('table')) e = e.parentElement;
        return [e.innerText, e.querySelectorAll('tbody tr').length]; }""")


def confere_janela(pg, n):
    txt, linhas = janela_registros(pg)
    assert linhas == n or re.search(rf"(?<![\d.,]){n}(?![\d,])", txt), (n, linhas, txt[:200])


def fechar_janelas(pg):
    for b in pg.get_by_role("button", name="Fechar", exact=True).locator("visible=true").all():
        b.click()


def por_regiao_filtrado(pg, campo, valor):
    abrir_painel(pg)
    pg.get_by_text("Filtros", exact=True).locator("visible=true").first.click()
    pg.get_by_role("combobox", name="Campo categoria").select_option(label=campo)
    pg.get_by_role("combobox", name="Valor", exact=True).select_option(label=valor)
    pg.wait_for_timeout(500)


def janela_de_dois_regioes():
    """(início, fim) em datas com exatamente 2 regiões entre os registros (oráculo para CA-254)."""
    ds = sorted(set(V_DATAS))
    for i, ini in enumerate(ds):
        regs = set()
        for fim in ds[i:]:
            regs |= {r["Região"] for r in VENDAS if d_(r["Data"]) == fim}
            if len(regs) > 2:
                break
            if len(regs) == 2:
                ult = fim
        if len(regs) > 2 and 'ult' in locals():
            return ini, ult
    pytest.skip("sem janela de datas com 2 regiões nos dados")


# ---------------- CA-250 ----------------
def test_CA250_opcoes_de_forma_no_painel_vendas(pg):
    painel_com(pg, ["Total de registros", "Por Cliente", "Valor por Região", "Evolução por mês (Data)", "% por Situação"])
    assert opcoes(sel(pg, "Por Cliente", "Forma")) == OPC_CONT
    assert opcoes(sel(pg, "Valor por Região", "Forma")) == OPC_VALOR
    assert opcoes(sel(pg, "Evolução por mês (Data)", "Forma")) == OPC_MES
    assert opcoes(sel(pg, "% por Situação", "Forma")) == OPC_PCT
    assert opcoes(sel(pg, "Total de registros", "Forma")) == ["Número"]


def test_CA250_opcoes_de_forma_no_painel_chamados(pg):
    painel_com(pg, ["Tempo entre duas datas"], "chamados.csv")
    assert opcoes(sel(pg, "Tempo entre duas datas", "Forma")) == ["Número", "Velocímetro"]


# ---------------- CA-251 ----------------
def test_CA251_rosca_por_regiao_no_painel(pg):
    painel_com(pg, ["Total de registros", "Por Região"])
    forma(pg, "Por Região", "Rosca")
    r = img(pg, "Rosca", "Por Região")
    assert r.count() == 1
    ps = {}
    for rot in rotulos(r):
        m = re.fullmatch(r"(\S.*?): (\d+)", rot)
        if m and m.group(1) in REGIOES:
            ps[m.group(1)] = int(m.group(2))
    assert ps == dict(REGIOES), ps
    assert "500" in texto_de(r.first)          # total no centro
    assert pedacos(r, "Centro: ").count() == 1
    # clicar num pedaço abre a janela com n registros
    pedacos(r, "Sul: ").first.click()
    confere_janela(pg, REGIOES["Sul"])


# ---------------- CA-252 ----------------
def test_CA252_rosca_com_mais_de_8_fatias_vira_barras(pg):
    painel_com(pg, ["Por Cliente"])
    forma(pg, "Por Cliente", "Rosca")
    assert len(CLIENTES) == 10
    assert pg.get_by_text("Rosca com mais de 8 fatias: mostrando barras").locator("visible=true").count() >= 1
    assert img(pg, "Rosca", "Por Cliente").count() == 0


# ---------------- CA-253 ----------------
def test_CA253_velocimetro_pct_por_situacao_e_meta(pg):
    painel_com(pg, ["% por Situação"])
    forma(pg, "% por Situação", "Velocímetro")
    v = img(pg, "Velocímetro", "% por Situação")
    assert v.count() == 1
    p = br(CONCLUIDOS / 500 * 100, 1)       # Entregue + Cancelado (não em aberto, D-77)
    corpo = re.sub(r"\s+", " ", pg.locator("body").inner_text())
    assert f"{p}% de 90%" in corpo + " " + texto_de(v.first), (p, corpo[:300])
    assert re.search(r"faltam [^.]*?para a meta", corpo), corpo[:300]
    # clicar abre os registros que formam o %
    v.first.click()
    confere_janela(pg, CONCLUIDOS)


def test_CA253_velocimetro_sem_meta_mostra_so_o_percentual(pg):
    painel_com(pg, ["% por Situação"])
    abrir_config(pg)
    pg.get_by_label(re.compile("Meta dos indicadores")).fill("")
    pg.wait_for_timeout(500)
    abrir_painel(pg)
    forma(pg, "% por Situação", "Velocímetro")
    v = img(pg, "Velocímetro", "% por Situação")
    p = br(CONCLUIDOS / 500 * 100, 1)
    t = texto_de(v.first)
    corpo = re.sub(r"\s+", " ", pg.locator("body").inner_text())
    assert f"{p}%" in t + corpo
    assert f"{p}% de" not in t + corpo


def test_CA253_velocimetro_tempo_entre_datas_chamados(pg):
    painel_com(pg, ["Tempo entre duas datas"], "chamados.csv")
    forma(pg, "Tempo entre duas datas", "Velocímetro")
    v = img(pg, "Velocímetro", "Tempo entre duas datas")
    assert v.count() == 1
    corpo = re.sub(r"\s+", " ", pg.locator("body").inner_text()) + texto_de(v.first)
    assert re.search(r"\d+,\d% de 90%", corpo), corpo[:300]


# ---------------- CA-254 ----------------
def test_CA254_radar_por_regiao(pg):
    painel_com(pg, ["Por Região"])
    forma(pg, "Por Região", "Radar")
    r = img(pg, "Radar", "Por Região")
    assert r.count() == 1
    pontos = {m.group(1): int(m.group(2)) for rot in rotulos(r.first)
              if (m := re.fullmatch(r"(\S.*?): (\d+)", rot)) and m.group(1) in REGIOES}
    assert pontos == dict(REGIOES)
    t = texto_de(r.first)
    for reg in REGIOES:                      # um eixo com o nome de cada região
        assert reg in t, reg
    pedacos(r, "Norte: ").first.click()
    confere_janela(pg, REGIOES["Norte"])


def test_CA254_radar_com_2_regioes_vira_barras(pg):
    painel_com(pg, ["Por Região"])
    forma(pg, "Por Região", "Radar")
    ini, fim = janela_de_dois_regioes()
    edicao(pg, False)
    abrir_painel(pg)
    pg.get_by_text("Filtros", exact=True).locator("visible=true").first.click()
    pg.get_by_role("combobox", name="Período").select_option(label="De–até")
    pg.get_by_label("De", exact=True).fill(ini.isoformat())
    pg.get_by_label("Até", exact=True).fill(fim.isoformat())
    pg.wait_for_timeout(600)
    assert pg.get_by_text("Radar precisa de 3 a 10 grupos: mostrando barras").locator("visible=true").count() >= 1
    assert img(pg, "Radar", "Por Região").count() == 0


# ---------------- CA-255 ----------------
def test_CA255_area_evolucao_por_mes(pg):
    painel_com(pg, ["Evolução por mês (Data)"])
    forma(pg, "Evolução por mês (Data)", "Área")
    a = img(pg, "Área", "Evolução por mês (Data)")
    assert a.count() == 1
    pts = {m.group(1): int(m.group(2)) for rot in rotulos(a.first)
           if (m := re.fullmatch(r"(\d{2}/\d{4}): (\d+)", rot))}
    assert pts == dict(MESES), pts


# ---------------- CA-256 ----------------
def _bolhas(pg):
    b = img(pg, "Bolhas", "Valor por Cliente")
    assert b.count() == 1
    achadas = {}
    for rot in rotulos(b.first):
        m = re.fullmatch(r"(\S.*?): (\d+) registros, média ([\d.]+,\d{2}), total ([\d.]+,\d{2})", rot)
        if m:
            achadas[m.group(1)] = (int(m.group(2)), m.group(3), m.group(4))
    return b, achadas


def test_CA256_bolhas_valor_por_cliente(pg):
    painel_com(pg, ["Valor por Cliente"])
    forma(pg, "Valor por Cliente", "Bolhas")
    b, achadas = _bolhas(pg)
    esperado = {c: (CLIENTES[c], br(SOMA_CLI[c] / CLIENTES[c]), br(SOMA_CLI[c])) for c in CLIENTES}
    assert len(achadas) == 10 and achadas == esperado, achadas
    # área proporcional à soma: a ordem das larguras (raios) é a ordem das somas
    larg = {}
    for c in achadas:
        bb = pedacos(b.first, f"{c}: ").first.bounding_box()
        larg[c] = bb["width"]
    por_soma = sorted(larg, key=lambda c: -SOMA_CLI[c])
    por_larg = sorted(larg, key=lambda c: -larg[c])
    assert por_soma == por_larg, (por_soma, por_larg)
    maior, menor = por_soma[0], por_soma[-1]
    razao = (larg[maior] / larg[menor]) ** 2   # área ~ largura²
    esperada = SOMA_CLI[maior] / SOMA_CLI[menor]
    assert razao == pytest.approx(esperada, rel=0.15), (razao, esperada)
    pedacos(b.first, f"{maior}: ").first.click()
    confere_janela(pg, CLIENTES[maior])


def test_CA256_bolhas_com_1_cliente_vira_barras(pg):
    painel_com(pg, ["Valor por Cliente"])
    forma(pg, "Valor por Cliente", "Bolhas")
    edicao(pg, False)
    por_regiao_filtrado(pg, "Cliente", "Alfa Comercial")
    assert pg.get_by_text("Bolhas precisam de pelo menos 2 grupos: mostrando barras").locator("visible=true").count() >= 1
    assert img(pg, "Bolhas", "Valor por Cliente").count() == 0


# ---------------- CA-257 ----------------
def test_CA257_forma_volta_depois_de_recarregar_e_restaurar_e_excel_igual(pg, tmp_path):
    painel_com(pg, ["Total de registros", "Por Região"])
    forma(pg, "Por Região", "Rosca")
    txt = backup(pg)[1]
    assert "Rosca" in txt or "rosca" in txt.lower()
    reabrir(pg)
    abrir_painel(pg)
    assert img(pg, "Rosca", "Por Região").count() == 1
    # backup -> apagar a escolha -> restaurar (Substituir)
    edicao(pg)
    forma(pg, "Por Região", "Barras")
    edicao(pg, False)
    assert img(pg, "Rosca", "Por Região").count() == 0
    restaurar(pg, txt, "Substituir")
    abrir_painel(pg)
    assert img(pg, "Rosca", "Por Região").count() == 1
    # Excel: a planilha Painel continua com a tabela do bloco (D-33)
    wb = gerar_excel(pg, tmp_path)
    celulas = [str(c.value) for linha in wb["Painel"].iter_rows() for c in linha if c.value is not None]
    for reg, n in REGIOES.items():
        assert reg in celulas, reg
        assert any(c in (str(n), f"{n}.0") for c in celulas), n


# ---------------- CA-258 (Relatório) ----------------
def test_CA258_relatorio_forma_regiao_quem_concentra_e_rosca(pg):
    abrir_relatorio(pg)
    editar(pg)
    s = controles(pg, "Região: quem concentra").get_by_label("Forma", exact=True)
    assert opcoes(s) == OPC_CONT              # as mesmas de Por Região (contagem)
    s.select_option(label="Rosca")
    concluir(pg)
    r = rel(pg).get_by_role("img", name="Rosca: Região: quem concentra", exact=True)
    assert r.count() == 1
    # D-69: "quem concentra" mede a SOMA do 1º Número (Valor); o rótulo traz a soma formatada (pt-BR)
    esperado = {}
    for linha in VENDAS:
        esperado[linha["Região"]] = esperado.get(linha["Região"], 0) + float(linha["Valor"].replace(".", "").replace(",", "."))
    ps = {}
    for rot in rotulos(r.first):
        m = re.fullmatch(r"(\S.*?): ([\d.]+,\d{2})", rot)
        if m and m.group(1) in REGIOES:
            ps[m.group(1)] = float(m.group(2).replace(".", "").replace(",", "."))
    assert set(ps) == set(REGIOES)
    for reg, v in ps.items():
        assert abs(v - esperado[reg]) < 0.02, (reg, v, esperado[reg])
    pedacos(r, "Leste: ").first.click()
    confere_janela(pg, REGIOES["Leste"])


def test_CA258_relatorio_forma_vira_barras_e_bolhas_nao_oferecida_em_contagem(pg):
    abrir_relatorio(pg)
    editar(pg)
    s = controles(pg, "Cliente: quem concentra").get_by_label("Forma", exact=True)
    assert "Bolhas" not in opcoes(s) and "Velocímetro" not in opcoes(s)
    s.select_option(label="Rosca")
    concluir(pg)
    assert "Rosca com mais de 8 fatias: mostrando barras" in re.sub(r"\s+", " ", rel(pg).inner_text())


# ---------------- CA-259 ----------------
def test_CA259_teclado_tab_chega_ao_pedaco_e_enter_abre_a_janela(pg):
    painel_com(pg, ["Por Região"])
    forma(pg, "Por Região", "Rosca")
    sel(pg, "Por Região", "Forma").focus()
    achou = None
    for _ in range(40):
        pg.keyboard.press("Tab")
        rot = pg.evaluate("document.activeElement && document.activeElement.getAttribute('aria-label')")
        if rot and re.fullmatch(r"\S.*?: \d+", rot) and rot.split(":")[0] in REGIOES:
            achou = rot
            break
    assert achou, "Tab não chegou a um pedaço da rosca"
    pg.keyboard.press("Enter")
    confere_janela(pg, REGIOES[achou.split(":")[0]])


def test_CA259_celular_390px_sem_rolagem_horizontal(celular):
    pg = celular
    preparar(pg, ["Por Região", "Valor por Região", "Evolução por mês (Data)", "% por Situação"])
    abrir_painel(pg)
    edicao(pg)
    for titulo, f in [("Por Região", "Rosca"), ("Valor por Região", "Bolhas"),
                      ("Evolução por mês (Data)", "Área"), ("% por Situação", "Velocímetro")]:
        forma(pg, titulo, f)
        assert pg.evaluate("document.documentElement.scrollWidth <= window.innerWidth + 1"), f
        assert img(pg, f, titulo).count() == 1, f
    forma(pg, "Por Região", "Radar")
    assert pg.evaluate("document.documentElement.scrollWidth <= window.innerWidth + 1"), "Radar"
