"""F-83: aceite da etapa E1 da tela Relatório (especificação 9c, CA-200 a CA-221).
Escrito SÓ a partir da especificação (9c.2, 9c.3, 9c.11). Oráculos em Python sobre tests/dados/.
Relógio do navegador fixo em 28/11/2026 12:00 (page.clock). Seletores por papel/rótulo/texto (9c.2)."""
import csv, json, re, datetime, statistics
from decimal import Decimal, ROUND_HALF_UP
import pytest
from conftest import URL, DADOS
from test_etapa1 import (le_csv, enviar, mapear_se_preciso, fechar_acompanhar, carregar,
                         abrir_config, abrir_painel, backup, codigos_no_backup)
from test_etapa2 import dlg
from test_etapa3 import num

HOJE = datetime.date(2026, 11, 28)
AGORA = datetime.datetime(2026, 11, 28, 12, 0)
VENDAS = le_csv("vendas.csv")
CHAMADOS = le_csv("chamados.csv")
ABERTO_NAO = ("conclu", "finaliz", "encerr", "fechad", "entreg", "cancel", "resolvid", "pag")


# ---------------- oráculos ----------------
def d_(s):
    return datetime.datetime.strptime(s, "%d/%m/%Y").date()


def dh_(s):
    f = "%d/%m/%Y %H:%M" if " " in s else "%d/%m/%Y"
    return datetime.datetime.strptime(s, f)


def val(s):
    return float(s.replace(",", "."))


def r_(x, casas):
    return Decimal(repr(x)).quantize(Decimal(1).scaleb(-casas), rounding=ROUND_HALF_UP)


def br(x, casas=2):
    s = f"{r_(x, casas):,.{casas}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def pct(a, b):
    return br(a / b * 100, 1) + "%"


def em_aberto(sit):
    import unicodedata
    s = "".join(c for c in unicodedata.normalize("NFD", sit) if unicodedata.category(c) != "Mn").lower()
    return not s.startswith(ABERTO_NAO)


def mm_aaaa(d):
    return f"{d.month:02d}/{d.year}"


def mediana(v):
    return statistics.median(v)


V_DATAS = [d_(r["Data"]) for r in VENDAS]
V_MIN, V_MAX = min(V_DATAS), max(V_DATAS)
fd = lambda d: d.strftime("%d/%m/%Y")


def concentra(regs, campo, medida=None):
    """[(nome, medida)] ordenado do maior ao menor, empate por nome."""
    ac = {}
    for r in regs:
        ac[r[campo]] = ac.get(r[campo], 0) + (val(r[medida]) if medida else 1)
    return sorted(ac.items(), key=lambda kv: (-kv[1], kv[0]))


# ---------------- auxiliares de tela ----------------
@pytest.fixture()
def pg(ctx):
    p = ctx.new_page()
    p.clock.set_fixed_time(AGORA)
    p.goto(URL)
    p.wait_for_timeout(800)
    p.erros = []
    p.on("pageerror", lambda e: p.erros.append(str(e)))
    p.on("console", lambda m: p.erros.append(m.text) if m.type == "error" else None)
    p.dialogos = []
    p.on("dialog", lambda d: (p.dialogos.append(d.message), d.dismiss()))
    return p


def config(page, area="Área Teste", cliente="Cliente Teste 01", meta=None, prazo=None):
    abrir_config(page)
    page.get_by_label("Cliente", exact=True).fill(cliente)
    page.get_by_label("Área", exact=True).fill(area)
    if meta is not None:
        page.get_by_label(re.compile("Meta dos indicadores")).fill(str(meta))
    if prazo is not None:
        page.get_by_label(re.compile("prazo", re.I)).first.fill(str(prazo))  # rótulo do prazo: ver docs/duvidas.md
    page.wait_for_timeout(600)


def rel(page):
    return page.get_by_role("region", name="Relatório", exact=True)


def gerar(page):
    abrir_painel(page)
    page.get_by_role("button", name="Gerar relatório", exact=True).click()
    rel(page).wait_for(state="visible")
    page.wait_for_timeout(500)
    return rel(page)


def abrir_relatorio(page, arquivo="vendas.csv", **cfg):
    config(page, **cfg)
    carregar(page, arquivo)
    return gerar(page)


JS_SECAO = """(titulo) => {
  const reg = [...document.querySelectorAll('section')].find(s => s.getAttribute('aria-label') === 'Relatório');
  const hs = [...reg.querySelectorAll('h1,h2,h3,h4,h5,h6,[role=heading]')];
  const nivel = h => h.getAttribute('aria-level') ? +h.getAttribute('aria-level') : (/^H(\\d)$/.test(h.tagName) ? +h.tagName[1] : 3);
  const h = hs.find(x => x.textContent.trim() === titulo);
  if (!h) return null;
  const n = nivel(h);
  const outros = el => hs.some(o => o !== h && el.contains(o) && nivel(o) <= n);
  let a = h;
  while (a.parentElement && a.parentElement !== reg && !outros(a.parentElement)) a = a.parentElement;
  let els = [a];
  if (a === h) {
    els = [h]; let s = h.nextElementSibling;
    while (s && !(hs.includes(s) && nivel(s) <= n) && !hs.some(o => s.contains(o) && nivel(o) <= n)) { els.push(s); s = s.nextElementSibling; }
  }
  const tabs = els.flatMap(e => e.tagName === 'TABLE' ? [e] : [...e.querySelectorAll('table')]);
  const texto = els.map(e => e.innerText).join('\\n');
  const fora = els.flatMap(e => [...e.querySelectorAll('[data-fora-meta="true"]')]).map(e => e.innerText);
  return {
    texto,
    itens: els.flatMap(e => [...e.querySelectorAll('li')]).map(e => e.innerText.trim()),
    fora,
    tabelas: tabs.map(t => {
      const cap = t.querySelector('caption');
      const ant = cap ? cap.innerText : (t.previousElementSibling ? t.previousElementSibling.innerText : '');
      return {antes: ant, linhas: [...t.querySelectorAll('tr')].map(tr => [...tr.children].map(c => c.innerText.trim()))};
    }),
    ids: els.map(e => e.id || '').filter(Boolean),
  };
}"""


def secao(page, titulo):
    s = page.evaluate(JS_SECAO, titulo)
    assert s is not None, f"parte sem heading {titulo!r}"
    s["plano"] = re.sub(r"[ \t\r\n]+", " ", s["texto"])
    return s


def titulos(page):
    return page.evaluate("""() => { const reg=[...document.querySelectorAll('section')].find(s=>s.getAttribute('aria-label')==='Relatório');
      return [...reg.querySelectorAll('h1,h2,h3,h4,h5,h6,[role=heading]')].map(h=>h.textContent.trim()); }""")


def tabela(sec, primeira_coluna=None, cabecalho=None, rotulo=None):
    for i, t in enumerate(sec["tabelas"]):
        l = t["linhas"]
        if cabecalho and l and l[0] == cabecalho:
            return l
        if rotulo and rotulo in t["antes"]:
            return l
    if rotulo is not None:  # sem rótulo legível: usa a ordem (5 maiores antes de 5 menores)
        return sec["tabelas"][0 if rotulo == "5 maiores" else 1]["linhas"]
    raise AssertionError(f"tabela {cabecalho or rotulo} não encontrada: {[t['linhas'][:1] for t in sec['tabelas']]}")


def depois_do_rotulo(plano, rotulo):
    """Texto do cartão: primeiro número logo depois do rótulo."""
    i = plano.index(rotulo) + len(rotulo)
    return plano[i:i + 60]


def mes_ano(cel):
    m = re.search(r"(\d{2})/(\d{4})", cel)
    if m:
        return int(m.group(2)), int(m.group(1))
    m = re.search(r"(\d{4})-(\d{2})", cel)
    assert m, f"mês ilegível: {cel!r}"
    return int(m.group(1)), int(m.group(2))


def inteiro(cel):
    return int(cel.replace("−", "-").replace(".", "").strip() or 0)


def editar(page):
    page.get_by_role("button", name="Editar relatório", exact=True).click()
    page.wait_for_timeout(300)


def concluir(page):
    page.get_by_role("button", name="Concluir edição", exact=True).click()
    page.wait_for_timeout(300)


def controles(page, titulo):
    return page.get_by_role("group", name=f"Controles de {titulo}", exact=True)


def exportar_excel(page, formato=None):
    """Auxiliar do Testador (CA-216): Gerar relatório -> Exportar arquivo -> Exportar (Excel)."""
    if not rel(page).is_visible():
        gerar(page)
    page.get_by_role("button", name="Exportar arquivo", exact=True).click()
    j = dlg(page, "Tipo de arquivo")
    j.wait_for(state="visible")
    if formato:
        j.get_by_label("Formato", exact=True).select_option(label=formato)
    with page.expect_download() as d:
        j.get_by_role("button", name="Exportar", exact=True).click()
    return d.value


# ---------------- CA-200 / CA-201 ----------------
def test_CA200_painel_tem_gerar_relatorio_e_nao_gerar_excel(pg):
    config(pg)
    carregar(pg, "vendas.csv")
    abrir_painel(pg)
    assert pg.get_by_role("button", name="Gerar relatório", exact=True).is_visible()
    assert pg.get_by_text("Monta um relatório pronto para ler, ajustar e exportar.").first.is_visible()
    assert pg.get_by_role("button", name="Gerar Excel").count() == 0
    assert pg.get_by_role("heading", name="Gerar Excel").count() == 0
    assert "Gerar Excel" not in pg.inner_text("body")


def test_CA201_capa_e_voltar_ao_painel(pg):
    r = abrir_relatorio(pg)
    assert not pg.get_by_role("button", name="Gerar relatório", exact=True).is_visible()
    assert pg.get_by_role("heading", name="Relatório vendas", level=2, exact=True).is_visible()
    t = r.inner_text()
    assert "Área Teste · Cliente Teste 01" in t
    assert f"Registros de {fd(V_MIN)} a {fd(V_MAX)}" in t
    assert "Filtros: sem filtros" in t
    assert re.search(r"Gerado em: \d{2}/\d{2}/\d{4} \d{2}:\d{2}", t)
    assert "Gerado em: 28/11/2026 12:" in t  # relógio fixo
    assert "Fonte: vendas (500 registros)" in t
    for b in ["Voltar ao painel", "Editar relatório", "Exportar arquivo"]:
        assert r.get_by_role("button", name=b, exact=True).is_visible(), b
    r.get_by_role("button", name="Voltar ao painel", exact=True).click()
    pg.wait_for_timeout(300)
    assert not r.is_visible()
    assert pg.get_by_role("button", name="Gerar relatório", exact=True).is_visible()


# ---------------- CA-202 ----------------
FRASES = {
    "Resumo executivo": "As frases principais, para ler em 1 minuto.",
    "Números principais": "Os números do período e a comparação com o período anterior.",
    "O que o Raio X encontrou": "O que foge do comum e merece atenção.",
    "Pendências por idade": "Há quanto tempo os registros em aberto esperam.",
    "Os 10 mais antigos em aberto": "Há quanto tempo os registros em aberto esperam.",
    "Entrou por mês (Data)": "Quantos entraram (e saíram) em cada mês.",
    "Valor: como os valores se distribuem": "Média, mediana, menores e maiores de Valor.",
    "Cliente: quem concentra": "Quem responde pela maior parte do total.",
    "Região: quem concentra": "Quem responde pela maior parte do total.",
    "Vendedor: quem concentra": "Quem responde pela maior parte do total.",
    "Registros": "A lista dos registros considerados.",
    "Como ler este relatório": "Como cada parte foi calculada.",
}


def test_CA202_indice_links_e_frases(pg):
    r = abrir_relatorio(pg)
    ind = secao(pg, "O que tem neste relatório")
    links = r.get_by_role("link")
    nomes = [t.strip() for t in links.all_inner_texts()]
    assert len(nomes) >= 8
    ordem_tela = [t for t in titulos(pg) if t in nomes]
    assert nomes == ordem_tela, (nomes, ordem_tela)  # índice na ordem da tela
    for n in ["Resumo executivo", "Números principais", "O que o Raio X encontrou", "Pendências por idade",
              "Entrou por mês (Data)", "Valor: como os valores se distribuem", "Cliente: quem concentra",
              "Registros", "Como ler este relatório"]:
        assert n in nomes, n
    assert "Do seu painel" not in nomes and "Tempo entre duas datas" not in nomes
    for i, n in enumerate(nomes):
        href = links.nth(i).get_attribute("href")
        assert href and href.startswith("#") and len(href) > 1, (n, href)
        alvo = pg.locator(f"[id='{href[1:]}']")
        assert alvo.count() == 1, (n, href)
        assert n in " ".join(alvo.locator("h1,h2,h3,h4,h5,h6,[role=heading]").all_inner_texts()) or \
            n in alvo.inner_text(), (n, href)
        assert FRASES[n] in ind["plano"], (n, FRASES[n])
    # frase logo depois do link
    assert re.search(r"Resumo executivo\s*\W*\s*As frases principais, para ler em 1 minuto\.", ind["plano"])


# ---------------- CA-203 / CA-204 ----------------
def test_CA203_resumo_executivo(pg):
    abrir_relatorio(pg)
    s = secao(pg, "Resumo executivo")
    it = s["itens"]
    assert 3 <= len(it) <= 5, it
    assert it[0] == f"O relatório tem 500 registros de {fd(V_MIN)} a {fd(V_MAX)}."
    a = sum(1 for r in VENDAS if em_aberto(r["Situação"]))
    assert f"{a} estão em aberto ({pct(a, 500)} do total)" in it[1], it[1]


def test_CA204_numeros_principais(pg):
    abrir_relatorio(pg, meta=90)
    s = secao(pg, "Números principais")
    p = s["plano"]
    v = [val(r["Valor"]) for r in VENDAS]
    assert re.search(r"Total de registros\s*500\b", p), p
    assert br(sum(v)) in depois_do_rotulo(p, "Soma de Valor")
    assert br(mediana(v)) in depois_do_rotulo(p, "Mediana de Valor")
    nov = sum(1 for d in V_DATAS if (d.year, d.month) == (2026, 11))
    out = sum(1 for d in V_DATAS if (d.year, d.month) == (2026, 10))
    pp = abs(nov - out) / out * 100
    seta = "↑" if nov > out else ("↓" if nov < out else "=")
    esperado = f"{seta} {br(pp, 1)}% em relação a 10/2026"
    assert esperado in depois_do_rotulo(p, "Total de registros") + p[p.index("Total de registros"):][:200], (esperado, p[:300])
    conc = sum(1 for r in VENDAS if not em_aberto(r["Situação"]))
    pc = conc / 500 * 100
    assert pc < 90
    assert pct(conc, 500) in depois_do_rotulo(p, "Concluídos")
    assert any(pct(conc, 500) in f for f in s["fora"]), s["fora"]
    assert re.search(r"faltam .+ para a meta", p), p


# ---------------- CA-205 / CA-206 ----------------
def test_CA205_pendencias_por_idade(pg):
    abrir_relatorio(pg)
    ab = [(HOJE - d_(r["Data"])).days for r in VENDAS if em_aberto(r["Situação"])]
    ab = [i for i in ab if i >= 0]
    faixas = {"0 a 7 dias": sum(0 <= i <= 7 for i in ab), "8 a 15 dias": sum(8 <= i <= 15 for i in ab),
              "16 a 30 dias": sum(16 <= i <= 30 for i in ab), "Mais de 30 dias": sum(i > 30 for i in ab)}
    assert sum(faixas.values()) == len(ab) and faixas["Mais de 30 dias"] > 0
    s = secao(pg, "Pendências por idade")
    for nome, n in faixas.items():
        m = re.search(rf"(?m)^\s*{re.escape(nome)}\s+(\d+)", s["texto"])
        assert m and int(m.group(1)) == n, (nome, n, s["texto"])
    assert "Idade contada até 28/11/2026." in s["plano"]
    pg.get_by_text("Mais de 30 dias", exact=True).first.click()
    pg.wait_for_timeout(500)
    j = pg.locator("dialog, [role=dialog]").filter(has_text="Limpar seleção").last
    assert j.is_visible()
    assert re.search(rf"\b{faixas['Mais de 30 dias']}\b", j.inner_text()), j.inner_text()[:300]


def test_CA206_dez_mais_antigos(pg):
    abrir_relatorio(pg)
    ab = sorted((d_(r["Data"]), r["Código"]) for r in VENDAS if em_aberto(r["Situação"]))[:10]
    s = secao(pg, "Os 10 mais antigos em aberto")
    t = tabela(s, cabecalho=["Código", "Data", "Dias em aberto", "Situação"])
    assert len(t) == 11
    for linha, (d, cod) in zip(t[1:], ab):
        assert linha[0] == cod and inteiro(linha[2]) == (HOJE - d).days and linha[1].startswith(fd(d)), (linha, cod, d)


# ---------------- CA-207 ----------------
def atrasados_chamados(horas):
    return sum(1 for r in CHAMADOS if em_aberto(r["Situação"]) and (AGORA - dh_(r["Abertura"])).total_seconds() / 3600 > horas)


def test_CA207_atrasados_prazo_padrao_e_720(pg):
    abrir_relatorio(pg, arquivo="chamados.csv")
    n = atrasados_chamados(24)
    assert re.search(rf"\b{n} atrasados \(mais de 24 h em aberto\)", secao(pg, "Números principais")["plano"])
    rel(pg).get_by_role("button", name="Voltar ao painel", exact=True).click()
    config(pg, prazo=720)
    n2 = atrasados_chamados(720)
    assert n2 != n
    gerar(pg)
    assert re.search(rf"\b{n2} atrasados \(mais de 30 dias em aberto\)", secao(pg, "Números principais")["plano"])


# ---------------- CA-208 ----------------
def test_CA208_entrou_e_saiu_por_mes(pg):
    abrir_relatorio(pg, arquivo="chamados.csv")
    ent, sai = {}, {}
    for r in CHAMADOS:
        a = dh_(r["Abertura"]); ent[(a.year, a.month)] = ent.get((a.year, a.month), 0) + 1
        if r["Conclusão"]:
            c = dh_(r["Conclusão"]); sai[(c.year, c.month)] = sai.get((c.year, c.month), 0) + 1
    meses = sorted(set(ent) | set(sai))
    s = secao(pg, "Entrou e saiu por mês")
    t = tabela(s, cabecalho=["Mês", "Entrou", "Saiu", "Saldo"])
    corpo = {mes_ano(l[0]): l for l in t[1:]}
    assert sorted(corpo) == meses
    for m in meses:
        l = corpo[m]
        assert (inteiro(l[1]), inteiro(l[2]), inteiro(l[3])) == (ent.get(m, 0), sai.get(m, 0), ent.get(m, 0) - sai.get(m, 0)), (m, l)


def test_CA208_vendas_so_entrou(pg):
    abrir_relatorio(pg)
    assert "Entrou e saiu por mês" not in titulos(pg)
    s = secao(pg, "Entrou por mês (Data)")
    t = tabela(s, cabecalho=["Mês", "Entrou"])
    ent = {}
    for d in V_DATAS:
        ent[(d.year, d.month)] = ent.get((d.year, d.month), 0) + 1
    assert {mes_ano(l[0]): inteiro(l[1]) for l in t[1:]} == ent


# ---------------- CA-209 ----------------
def test_CA209_distribuicao_de_valor(pg):
    abrir_relatorio(pg)
    v = [val(r["Valor"]) for r in VENDAS]
    s = secao(pg, "Valor: como os valores se distribuem")
    p = s["plano"]
    for rot, x in [("Média", sum(v) / len(v)), ("Mediana", mediana(v)), ("Mínimo", min(v)), ("Máximo", max(v))]:
        assert br(x) in depois_do_rotulo(p, rot), (rot, br(x), p[:300])
    assert f"Metade dos registros ficou abaixo de {br(mediana(v))}." in p
    media, med = sum(v) / len(v), mediana(v)
    if med > 0 and media > 1.2 * med:
        assert "A média está acima da mediana porque alguns valores são bem altos." in p
    elif med > 0 and media < 0.8 * med:
        assert "A média está abaixo da mediana porque alguns valores são bem baixos." in p
    else:
        assert "A média está" not in p
    maiores = sorted(VENDAS, key=lambda r: (-val(r["Valor"]), r["Código"]))[:5]
    menores = sorted(VENDAS, key=lambda r: (val(r["Valor"]), r["Código"]))[:5]
    for rot, esp in [("5 maiores", maiores), ("5 menores", menores)]:
        t = tabela(s, rotulo=rot)
        assert t[0][0] == "Código" and t[0][1] == "Cliente" and t[0][-1] == "Valor", t[0]
        assert len(t) == 6
        for linha, r in zip(t[1:], esp):
            assert linha[0] == r["Código"] and linha[1] == r["Cliente"] and num(linha[-1]) == val(r["Valor"]), (rot, linha, r)


# ---------------- CA-210 ----------------
def frases_concentra(grupos, nome_campo):
    tot = sum(m for _, m in grupos)
    p3 = sum(m for _, m in grupos[:3]) / tot * 100
    acum, k = 0, None
    for i, (_, m) in enumerate(grupos, 1):
        acum += m
        if k is None and acum / tot * 100 >= 80:
            k = i
    return f"Os 3 primeiros de {nome_campo} fazem {br(p3, 1)}% do total.", f"Para chegar a 80% do total são {k} de {len(grupos)}."


def confere_concentra(s, grupos, campo, medida_titulo, formata):
    t = tabela(s, cabecalho=[campo, medida_titulo, "% do total", "% acumulado"])
    corpo = t[1:]
    assert len(corpo) == len(grupos)
    tot = sum(m for _, m in grupos)
    acum = 0
    for linha, (nome, m) in zip(corpo, grupos):
        acum += m
        assert linha[0] == nome and formata(m) in linha[1] and linha[2].startswith(br(m / tot * 100, 1)) \
            and linha[3].startswith(br(acum / tot * 100, 1)), (linha, nome, m)
    assert corpo[-1][3].startswith("100,0")


def test_CA210_quem_concentra_cliente(pg):
    abrir_relatorio(pg)
    grupos = concentra(VENDAS, "Cliente", "Valor")
    assert len(grupos) == 10
    s = secao(pg, "Cliente: quem concentra")
    confere_concentra(s, grupos, "Cliente", "Soma de Valor", lambda m: br(m))
    f1, f2 = frases_concentra(grupos, "Cliente")
    assert f1 in s["plano"] and f2 in s["plano"], (f1, f2)


def test_CA210_quem_concentra_categoria_chamados(pg):
    abrir_relatorio(pg, arquivo="chamados.csv")
    grupos = concentra(CHAMADOS, "Categoria")
    s = secao(pg, "Categoria: quem concentra")
    confere_concentra(s, grupos, "Categoria", "Registros", lambda m: str(int(m)))
    f1, f2 = frases_concentra(grupos, "Categoria")
    assert f1 in s["plano"] and f2 in s["plano"]


# ---------------- CA-211 ----------------
def test_CA211_periodo_mes_outubro(pg):
    config(pg)
    carregar(pg, "vendas.csv")
    abrir_painel(pg)
    pg.get_by_text("Filtros", exact=True).locator("visible=true").first.click()
    pg.get_by_role("combobox", name="Período").select_option(label="Mês")
    pg.get_by_label("Mês", exact=True).fill("2026-10")
    pg.wait_for_timeout(500)
    r = gerar(pg)
    t = r.inner_text()
    assert "Registros de 01/10/2026 a 31/10/2026" in t
    assert "Filtros: outubro/2026" in t
    out = sum(1 for d in V_DATAS if (d.year, d.month) == (2026, 10))
    set_ = sum(1 for d in V_DATAS if (d.year, d.month) == (2026, 9))
    p = secao(pg, "Números principais")["plano"]
    assert re.search(rf"Total de registros\s*{out}\b", p), p[:200]
    seta = "↑" if out > set_ else "↓"
    assert f"{seta} {br(abs(out - set_) / set_ * 100, 1)}% em relação a 09/2026" in p, p[:300]
    # volta ao painel com o mesmo filtro
    r.get_by_role("button", name="Voltar ao painel", exact=True).click()
    assert pg.get_by_label("Mês", exact=True).input_value() == "2026-10"


# ---------------- CA-212 / CA-214 / CA-215 ----------------
T_VAL = "Valor: como os valores se distribuem"


def editar_ca212(pg):
    editar(pg)
    g = controles(pg, T_VAL)
    g.get_by_label("Título", exact=True).fill("Valores do período")
    g.get_by_label("Observação", exact=True).fill("Observação de teste 01")
    controles(pg, "Pendências por idade").get_by_role("button", name="Esconder", exact=True).click()
    controles(pg, "Números principais").get_by_role("button", name="Descer", exact=True).click()
    concluir(pg)


def confere_ca212(pg):
    ts = titulos(pg)
    assert "Valores do período" in ts and T_VAL not in ts
    assert "Pendências por idade" not in ts
    assert ts.index("Números principais") > ts.index("O que o Raio X encontrou")
    ind = secao(pg, "O que tem neste relatório")["plano"]
    assert "Valores do período" in ind and "Pendências por idade" not in ind
    ler = secao(pg, "Como ler este relatório")["plano"]
    assert "Pendências por idade" not in ler
    s = secao(pg, "Valores do período")
    assert "Observação: Observação de teste 01" in s["plano"]
    ital = pg.get_by_text("Observação: Observação de teste 01", exact=True).first
    assert ital.evaluate("e => getComputedStyle(e).fontStyle") == "italic"


def test_CA212_edicao_titulo_observacao_esconder_ordem_e_guarda(pg):
    abrir_relatorio(pg)
    editar_ca212(pg)
    confere_ca212(pg)
    pg.reload(); pg.wait_for_timeout(1000)
    gerar(pg)
    confere_ca212(pg)


def test_CA214_resumo_editado_aviso_e_voltar_ao_padrao(pg):
    abrir_relatorio(pg)
    editar_ca212(pg)
    editar(pg)
    pg.get_by_label("Texto do resumo executivo", exact=True).fill("Primeira frase minha.\n\nSegunda frase minha.")
    concluir(pg)
    assert secao(pg, "Resumo executivo")["itens"] == ["Primeira frase minha.", "Segunda frase minha."]
    aviso = "Texto editado por você: confira se os números ainda valem."
    assert aviso not in rel(pg).inner_text()
    rel(pg).get_by_role("button", name="Voltar ao painel", exact=True).click()
    enviar(pg, "vendas_parte2.csv"); mapear_se_preciso(pg); fechar_acompanhar(pg)
    gerar(pg)
    assert secao(pg, "Resumo executivo")["itens"] == ["Primeira frase minha.", "Segunda frase minha."]
    assert aviso in rel(pg).inner_text()
    editar(pg)
    rel(pg).get_by_role("button", name="Voltar ao padrão", exact=True).click()
    j = dlg(pg, "Voltar ao padrão do relatório?")
    j.wait_for(state="visible")
    j.get_by_role("button", name="Voltar ao padrão", exact=True).click()
    pg.wait_for_timeout(400)
    if pg.get_by_role("button", name="Concluir edição", exact=True).count():
        concluir(pg)
    it = secao(pg, "Resumo executivo")["itens"]
    assert it[0].startswith("O relatório tem ") and "Primeira frase minha." not in it
    ts = titulos(pg)
    assert T_VAL in ts and "Valores do período" not in ts and "Pendências por idade" in ts
    assert ts.index("Números principais") < ts.index("O que o Raio X encontrou")


def test_CA215_backup_leva_relatorio_e_rejeita_formato_errado(pg):
    abrir_relatorio(pg)
    editar_ca212(pg)
    _, b = backup(pg)
    dados = json.loads(b)
    assert "relatorio" in dados and "vendas" in dados["relatorio"], list(dados)
    pg.get_by_role("button", name="Apagar todos os dados").click()
    pg.get_by_role("button", name="Apagar", exact=True).click()
    pg.wait_for_timeout(500)

    def restaurar(texto):
        abrir_config(pg)
        with pg.expect_file_chooser() as fc:
            pg.get_by_role("button", name="Restaurar backup").click()
        fc.value.set_files([{"name": "b.json", "mimeType": "application/json", "buffer": texto.encode()}])
        pg.wait_for_timeout(500)
        bt = pg.get_by_role("button", name="Substituir", exact=True)
        if bt.count() and bt.first.is_visible():
            bt.first.click()
        pg.wait_for_timeout(800)

    ruim = dict(dados); ruim["relatorio"] = "isto não é um relatório"
    restaurar(json.dumps(ruim))
    _, depois = backup(pg)
    assert len(set(codigos_no_backup(depois))) == 0, "backup com 'relatorio' errado deveria ser rejeitado inteiro"
    restaurar(b)
    carregar_ok = len(set(codigos_no_backup(backup(pg)[1]))) == len(VENDAS)
    assert carregar_ok
    gerar(pg)
    confere_ca212(pg)


# ---------------- CA-213 ----------------
def test_CA213_forma_pizza(pg):
    abrir_relatorio(pg)
    editar(pg)
    controles(pg, "Cliente: quem concentra").get_by_label("Forma", exact=True).select_option(label="Pizza")
    controles(pg, "Região: quem concentra").get_by_label("Forma", exact=True).select_option(label="Pizza")
    concluir(pg)
    sc = secao(pg, "Cliente: quem concentra")
    assert "Pizza com mais de 8 fatias: mostrando barras" in sc["plano"]
    assert not rel(pg).locator("[data-forma='pizza']").filter(has_text="Cliente").count() or \
        "Pizza com mais de 8 fatias" in sc["plano"]
    sr = secao(pg, "Região: quem concentra")
    assert "Pizza com mais de 8 fatias" not in sr["plano"]
    pizza = rel(pg).locator("[data-forma='pizza']")
    assert pizza.count() >= 1
    regioes = {r["Região"] for r in VENDAS}
    assert len(regioes) == 5
    for reg in regioes:
        assert pizza.locator(f"[aria-label^='{reg}: ']").count() >= 1, reg


# ---------------- CA-216 ----------------
def test_CA216_exportar_arquivo_excel(pg):
    abrir_relatorio(pg)
    pg.get_by_role("button", name="Exportar arquivo", exact=True).click()
    j = dlg(pg, "Tipo de arquivo")
    j.wait_for(state="visible")
    assert j.get_by_role("radio", name="Excel").is_checked()
    assert j.get_by_label("Formato", exact=True).is_visible()
    assert j.get_by_role("button", name="Cancelar", exact=True).is_visible()
    j.get_by_role("button", name="Cancelar", exact=True).click()
    d = exportar_excel(pg)
    nome = d.suggested_filename
    assert re.fullmatch(r"RaioX_[A-Z0-9_]+_\d{4}-\d{2}-\d{2}\.xlsx", nome), nome
    assert nome.endswith("2026-11-28.xlsx"), nome
    assert "Excel gerado." in pg.inner_text("body")


# ---------------- CA-217 ----------------
def test_CA217_offline_390px_sem_origem_externa(ctx, pg):
    abrir_relatorio(pg)
    ctx.set_offline(True)
    rel(pg).get_by_role("button", name="Voltar ao painel", exact=True).click()
    gerar(pg)
    d = exportar_excel(pg)
    assert d.suggested_filename.endswith(".xlsx")
    pg.set_viewport_size({"width": 390, "height": 800})
    pg.wait_for_timeout(400)
    assert pg.evaluate("document.documentElement.scrollWidth <= window.innerWidth + 1"), "rolagem horizontal em 390 px"
    ctx.set_offline(False)
    for u in ctx.reqs:
        assert u.startswith(URL) or u.startswith(("data:", "blob:")), u


# ---------------- CA-218 ----------------
def test_CA218_html_em_dado_e_observacao_vira_texto(pg, tmp_path):
    xss = "<img src=x onerror=alert(1)>"
    arq = tmp_path / "xss.csv"
    linhas = ["Código;Data;Cliente;Valor;Situação"]
    for i in range(1, 7):
        linhas.append(f"X{i:03d};{i:02d}/10/2026;{xss if i % 2 else 'Cliente B'};{i * 10},50;{'Pendente' if i % 2 else 'Entregue'}")
    arq.write_text("\n".join(linhas), encoding="utf-8")
    config(pg)
    enviar(pg, str(arq)); mapear_se_preciso(pg); fechar_acompanhar(pg)
    r = gerar(pg)
    t = r.inner_text()
    assert xss in t, "o texto do dado deve aparecer como texto"
    editar(pg)
    controles(pg, "Cliente: quem concentra").get_by_label("Observação", exact=True).fill(xss)
    controles(pg, "Cliente: quem concentra").get_by_label("Título", exact=True).fill(xss)
    concluir(pg)
    pg.wait_for_timeout(500)
    assert f"Observação: {xss}" in rel(pg).inner_text()
    assert rel(pg).locator("img[src='x']").count() == 0
    assert pg.dialogos == [], pg.dialogos


# ---------------- CA-219 ----------------
def test_CA219_so_codigo_e_texto(pg, tmp_path):
    arq = tmp_path / "simples.csv"
    arq.write_text("Código;Nota\nS001;primeira\nS002;segunda\nS003;terceira\n", encoding="utf-8")
    config(pg)
    enviar(pg, str(arq)); mapear_se_preciso(pg); fechar_acompanhar(pg)
    r = gerar(pg)
    ts = titulos(pg)
    for n in ["Resumo executivo", "Números principais", "O que o Raio X encontrou", "Registros", "Como ler este relatório"]:
        assert n in ts, (n, ts)
    for n in ["Pendências por idade", "Entrou por mês", "Do seu painel", "Tempo entre duas datas"]:
        assert not any(t.startswith(n) for t in ts), n
    assert not any("quem concentra" in t or "como os valores se distribuem" in t for t in ts), ts
    assert len(secao(pg, "Resumo executivo")["itens"]) == 1
    p = secao(pg, "Números principais")["plano"]
    assert "Total de registros" in p
    for n in ["Em aberto", "Concluídos", "Atrasados", "Soma de", "Mediana de"]:
        assert n not in p, n
    assert pg.erros == [], pg.erros


# ---------------- CA-220 ----------------
def test_CA220_como_ler_e_registros(pg):
    abrir_relatorio(pg)
    ler = secao(pg, "Como ler este relatório")
    visiveis = [t for t in rel(pg).get_by_role("link").all_inner_texts()]
    visiveis = [t.strip() for t in visiveis if t.strip() != "Como ler este relatório"]
    linhas = ler["itens"] or [l for l in ler["texto"].split("\n") if l.strip()]
    for t in visiveis:
        achou = [l for l in linhas if l.startswith(t + " — ")]
        assert achou, (t, linhas[:3])
        assert re.search(r"Período: .+\. .*sem filtros\.?$", achou[0]) or "Período:" in achou[0], achou[0]
        assert "Filtros" in achou[0] or "sem filtros" in achou[0].lower(), achou[0]
    s = secao(pg, "Registros")
    assert "Mostrando 100 de 500 registros. No Excel vão todos." in s["plano"]
    t = s["tabelas"][0]["linhas"]
    assert len(t) == 101, len(t)


# ---------------- CA-221 ----------------
def test_CA221_72_mil_registros_em_ate_5s(ctx, tmp_path):
    arq = tmp_path / "grande.csv"
    with open(arq, "w", encoding="utf-8", newline="") as f:
        f.write("Código;Data;Cliente;Região;Vendedor;Valor;Situação\n")
        for i in range(72000):
            r = VENDAS[i % 500]
            f.write(f"G{i:06d};{r['Data']};{r['Cliente']};{r['Região']};{r['Vendedor']};{r['Valor']};{r['Situação']}\n")
    ctx.set_default_timeout(120000)
    p = ctx.new_page()
    p.clock.set_fixed_time(AGORA)
    p.goto(URL); p.wait_for_timeout(800)
    enviar(p, str(arq)); p.wait_for_timeout(6000)
    mapear_se_preciso(p); p.wait_for_timeout(3000); fechar_acompanhar(p)
    abrir_painel(p)
    import time
    t0 = time.time()
    p.get_by_role("button", name="Gerar relatório", exact=True).click()
    rel(p).wait_for(state="visible")
    p.get_by_role("heading", name="Resumo executivo").wait_for(state="visible")
    assert time.time() - t0 <= 5, f"{time.time() - t0:.1f}s"
