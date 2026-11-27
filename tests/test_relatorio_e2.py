"""F-84: aceite da etapa E2 da tela Relatório, "O que o Raio X encontrou" (especificação 9c.7, CA-230 a CA-236).
Escrito SÓ a partir da especificação. Oráculos em Python sobre tests/dados/achados.csv e sem_achados.csv.
Relógio do navegador fixo em 28/11/2026 12:00. Gancho de teste: window.__achados(<relatório>) (9c.7)."""
import re, datetime, statistics
import pytest
from conftest import RAIZ
from test_relatorio_e1 import (pg, config, abrir_relatorio, secao, rel, gerar, br, d_, fd, HOJE, le_csv,
                               carregar, abrir_painel)

VAZIO_MSG = "O Raio X não encontrou nada fora do comum nestes registros."
ACHADOS = le_csv("achados.csv")
SEM = le_csv("sem_achados.csv")
CAB = ["Código", "Abertura", "Conclusão", "Grupo", "Responsável", "Valor", "Situação"]
PRIORIDADE = ["Data no futuro", "Datas fora de ordem", "Parados", "Fora da curva", "Pendências", "Mudança", "Concentração",
              "Buracos", "Repetidos"]


# ---------------- registros e oráculos ----------------
def regs_de(linhas):
    out = []
    for r in linhas:
        out.append({"cod": r["Código"], "ab": d_(r["Abertura"]), "cl": d_(r["Conclusão"]) if r["Conclusão"] else None,
                    "g": r["Grupo"], "resp": r["Responsável"], "val": float(r["Valor"].replace(",", ".")),
                    "sit": r["Situação"]})
    return out


R_ACH = regs_de(ACHADOS)
R_SEM = regs_de(SEM)


def mes(d):
    return (d.year, d.month)


def mmaaaa(m):
    return f"{m[1]:02d}/{m[0]}"


def V(x, base):
    """Regex dos jeitos aceitáveis de escrever o número x (arredondado a `base` casas; mais curto se exato)."""
    vs = []
    for c in range(0, base + 1):
        if c == base or round(x, c) == round(x, base):
            s = br(x, c)
            vs += [s, s.replace(".", "")]
    return "(?:" + "|".join(re.escape(v) for v in sorted(set(vs), key=len, reverse=True)) + ")"


def A(regra, titulo, frase, porque, regs):
    return {"regra": regra, "titulo": titulo, "frase": frase, "porque": porque, "codigos": {r["cod"] for r in regs}}


def oraculo(regs, hoje=HOJE):
    """Achados A1 a A8 sobre os registros (A9 fica de fora: depende de Core.repetidos). Lista na ordem de prioridade."""
    out, n = [], len(regs)
    # A1 data no futuro (cada campo de data)
    for campo, k in (("Abertura", "ab"), ("Conclusão", "cl")):
        fut = [r for r in regs if r[k] and r[k] > hoje]
        if fut:
            out.append(A(1, "Datas no futuro",
                         rf"{len(fut)} registros? com {campo} depois de hoje; a mais distante é {fd(max(r[k] for r in fut))}\.",
                         "data maior que a data de hoje", fut))
    # A2 data final antes da inicial
    ford = [r for r in regs if r["cl"] and r["cl"] < r["ab"]]
    if ford:
        out.append(A(2, "Datas fora de ordem", rf"{len(ford)} registros? com Conclusão antes de Abertura\.",
                     "Conclusão anterior a Abertura", ford))
    # A3 parados
    par = [r for r in regs if r["sit"] == "Aberto" and (hoje - r["ab"]).days > 30]
    if par:
        d = max((hoje - r["ab"]).days for r in par)
        out.append(A(3, "Parados há muito tempo",
                     rf"{len(par)} registros? em aberto há mais de 30 dias; o mais antigo há {d} dias\.",
                     "em aberto há mais de 30 dias", par))
    # A4 fora da curva
    vals = [r["val"] for r in regs]
    if vals and statistics.median(vals) > 0:
        med = statistics.median(vals)
        fora = [r for r in regs if r["val"] > 3 * med]
        if fora:
            mx = max(fora, key=lambda r: (r["val"], r["cod"]))
            out.append(A(4, "Valores fora da curva em Valor",
                         rf"{len(fora)} registros? com Valor acima de 3 vezes a mediana \({V(3 * med, 2)}\); "
                         rf"o maior é {V(mx['val'], 2)} \({mx['cod']}\)\.", "mais de 3 vezes a mediana", fora))
    # meses com registros (sem datas no futuro: ⚖️ ver docs/duvidas.md)
    meses = sorted({mes(r["ab"]) for r in regs if r["ab"] <= hoje})
    # A5 pendências crescendo
    if len(meses) >= 3:
        u = meses[-3:]
        c = [sum(1 for r in regs if r["sit"] == "Aberto" and mes(r["ab"]) == m) for m in u]
        if c[0] < c[1] < c[2]:
            cods = [r for r in regs if r["sit"] == "Aberto" and mes(r["ab"]) in u]
            out.append(A(5, "Pendências crescendo",
                         rf"Os registros em aberto que entram a cada mês cresceram 3 meses seguidos: "
                         rf"{mmaaaa(u[0])} {c[0]}, {mmaaaa(u[1])} {c[1]}, {mmaaaa(u[2])} {c[2]}\.",
                         "3 meses seguidos de alta", cods))
    # A6 mudança brusca (Situação e Grupo)
    if len(meses) >= 2:
        m1, m2 = meses[-2:]
        t1 = [r for r in regs if mes(r["ab"]) == m1]
        t2 = [r for r in regs if mes(r["ab"]) == m2]
        if len(t1) >= 20 and len(t2) >= 20:
            for campo, k in (("Situação", "sit"), ("Grupo", "g")):
                for v in sorted({r[k] for r in t1 + t2}):
                    p1 = sum(r[k] == v for r in t1) / len(t1) * 100
                    p2 = sum(r[k] == v for r in t2) / len(t2) * 100
                    if abs(p2 - p1) >= 15:
                        out.append(A(6, f"Mudança brusca em {campo}",
                                     rf"{re.escape(v)} foi de {V(p1, 1)}% em {mmaaaa(m1)} para {V(p2, 1)}% em {mmaaaa(m2)}\.",
                                     "mudou 15 pontos ou mais de um mês para o outro",
                                     [r for r in t1 + t2 if r[k] == v]))
    # A7 concentração escondida
    for v in sorted({r["sit"] for r in regs}):
        sub = [r for r in regs if r["sit"] == v]
        if len(sub) < 10:
            continue
        for g in sorted({r["g"] for r in sub}):
            p = sum(r["g"] == g for r in sub) / len(sub) * 100
            q = sum(r["g"] == g for r in regs) / n * 100
            if p >= 50 and p >= 2 * q:
                out.append(A(7, f"Concentração em {v}",
                             rf"(?:Grupo )?{re.escape(g)} responde por {V(p, 1)}% dos registros {re.escape(v)}, "
                             rf"mas só por {V(q, 1)}% do total\.".replace(re.escape(v), "(?i:" + re.escape(v) + ")"),
                             "metade ou mais de uma situação num só grupo", [r for r in sub if r["g"] == g]))
    # A8 buracos
    for campo, k in (("Grupo", "g"), ("Responsável", "resp"), ("Valor", "val"), ("Situação", "sit"),
                     ("Abertura", "ab"), ("Conclusão", "cl")):
        vz = [r for r in regs if r[k] in ("", None) and not (k == "cl" and r["sit"] == "Aberto")]
        if vz and len(vz) / n >= 0.2:
            out.append(A(8, f"Campo vazio: {campo}",
                         rf"{campo} está vazio em {V(len(vz) / n * 100, 1)}% dos registros \({len(vz)}\)\.",
                         "vazio em 20% ou mais", vz))
    for k in ("ab", "cl"):
        ds = sorted({r[k] for r in regs if r[k] and r[k] <= hoje})
        if sum(1 for r in regs if r[k] and r[k] <= hoje) >= 30:
            for a, b in zip(ds, ds[1:]):
                if (b - a).days - 1 >= 14:
                    ex = [r for r in regs if r[k] in (a, b)]
                    out.append(A(8, "Dias sem registro",
                                 rf"Nenhum registro de {fd(a + datetime.timedelta(days=1))} a "
                                 rf"{fd(b - datetime.timedelta(days=1))} \({(b - a).days - 1} dias\)\.",
                                 "14 dias ou mais sem registro", ex))
    out.sort(key=lambda a: (a["regra"], -len(a["codigos"])))
    return out


def na_tela(ach):
    """Até 2 por regra e 5 no total (D-72)."""
    por, tela = {}, []
    for a in ach:
        por[a["regra"]] = por.get(a["regra"], 0) + 1
        if por[a["regra"]] <= 2 and len(tela) < 5:
            tela.append(a)
    return tela


def regra_do_titulo(t):
    if t.startswith("Datas no"): return 1
    if t.startswith("Datas fora"): return 2
    if t.startswith("Parados"): return 3
    if t.startswith("Valores fora"): return 4
    if t.startswith("Pendências"): return 5
    if t.startswith("Mudança"): return 6
    if t.startswith("Concentração"): return 7
    if t.startswith("Campo vazio") or t == "Dias sem registro": return 8
    if t.startswith("Possíveis"): return 9
    raise AssertionError(f"título de achado desconhecido: {t!r}")


def casa(a, js):
    """Algum achado do app (dict do window.__achados) bate com o achado do oráculo?"""
    return any(j["titulo"] == a["titulo"] and re.fullmatch(a["frase"], re.sub(r"\s+", " ", j["frase"]).strip())
               for j in js)


# ---------------- gancho e tela ----------------
def js_achados(page, nome):
    return page.evaluate("async (n) => JSON.parse(JSON.stringify(await window.__achados(n)))", nome)


def itens_tela(page):
    s = secao(page, "O que o Raio X encontrou")
    return s, [i for i in s["itens"] if i.strip()]


def titulo_do_item(item):
    return item.split("\n")[0].strip()


def janela_registros(page):
    page.wait_for_timeout(500)
    j = page.locator("dialog:visible, [role=dialog]:visible").last
    assert j.is_visible()
    return j


def filtra_mes(page, aaaa_mm="2026-10"):
    abrir_painel(page)
    page.get_by_text("Filtros", exact=True).locator("visible=true").first.click()
    page.get_by_role("combobox", name="Período").select_option(label="Mês")
    page.get_by_label("Mês", exact=True).fill(aaaa_mm)
    page.wait_for_timeout(500)
    return gerar(page)


# ---------------- o próprio CSV tem as propriedades P1 a P9 (9c.11) ----------------
def test_CA230_dados_achados_csv_tem_as_propriedades_P1_a_P9():
    assert len(ACHADOS) == 240 and [r["Código"] for r in ACHADOS] == [f"A{i:05d}" for i in range(1, 241)]
    assert list(ACHADOS[0].keys()) == CAB
    assert {r["sit"] for r in R_ACH} == {"Aberto", "Concluido"}
    assert sum(r["ab"].year == 2027 for r in R_ACH) == 2                                      # P1
    assert sum(1 for r in R_ACH if r["cl"] and r["cl"] < r["ab"]) == 3                        # P2
    med = statistics.median(r["val"] for r in R_ACH)
    assert sum(r["val"] > 3 * med for r in R_ACH) == 4                                        # P3
    assert sum(r["resp"] == "" for r in R_ACH) == 72                                          # P4
    ab = {r["ab"] for r in R_ACH}
    assert not any(datetime.date(2026, 7, 1) <= d <= datetime.date(2026, 7, 24) for d in ab)  # P5
    assert datetime.date(2026, 6, 30) in ab and datetime.date(2026, 7, 25) in ab
    cont = {m: sum(1 for r in R_ACH if r["sit"] == "Aberto" and mes(r["ab"]) == (2026, m)) for m in (8, 9, 10)}
    assert cont[8] < cont[9] < cont[10]                                                       # P6
    tot = {m: sum(1 for r in R_ACH if mes(r["ab"]) == (2026, m)) for m in (9, 10)}
    assert cont[9] >= 20 and cont[10] >= 20                                                   # P7
    assert cont[10] / tot[10] * 100 - cont[9] / tot[9] * 100 >= 15
    abertos = [r for r in R_ACH if r["sit"] == "Aberto"]
    g2 = [r for r in abertos if r["g"] == "Grupo Teste 2"]
    assert len(g2) / len(abertos) >= 0.6 and sum(r["g"] == "Grupo Teste 2" for r in R_ACH) / 240 <= 0.25   # P8
    assert any(r["ab"] < datetime.date(2026, 10, 28) for r in abertos)                        # P9
    assert all(not (r["sit"] == "Aberto" and r["cl"]) for r in R_ACH)
    assert max(r["cl"] for r in R_ACH if r["cl"]) <= HOJE
    # sem_achados
    assert len(SEM) == 60 and {r["sit"] for r in R_SEM} == {"Concluido"}
    assert [r["ab"] for r in R_SEM] == [datetime.date(2026, 9, 1) + datetime.timedelta(days=i) for i in range(60)]
    assert all((r["cl"] - r["ab"]).days == 1 and 100 <= r["val"] <= 110 for r in R_SEM)
    assert all(v != "" for r in SEM for v in r.values())


# ---------------- CA-230 ----------------
def test_CA230_cinco_achados_na_ordem(pg):
    abrir_relatorio(pg, "achados.csv")
    s, itens = itens_tela(pg)
    esperado = na_tela(oraculo(R_ACH))
    assert [a["titulo"] for a in esperado] == ["Datas no futuro", "Datas fora de ordem", "Parados há muito tempo",
                                                "Valores fora da curva em Valor", "Pendências crescendo"]
    assert [titulo_do_item(i) for i in itens] == [a["titulo"] for a in esperado], itens
    assert VAZIO_MSG not in s["plano"]
    for i, a in zip(itens, esperado):
        assert re.search(a["frase"], re.sub(r"\s+", " ", i)), (a["frase"], i)


# ---------------- CA-231 ----------------
def test_CA231_window_achados_todos_na_ordem_e_frases(pg):
    abrir_relatorio(pg, "achados.csv")
    js = js_achados(pg, "achados")
    regras = [regra_do_titulo(j["titulo"]) for j in js]
    assert regras == sorted(regras), regras                                  # ordem de prioridade
    assert sorted(set(regras)) == [1, 2, 3, 4, 5, 6, 7, 8], regras           # A1..A8 e nenhum A9
    titulos = {j["titulo"] for j in js}
    assert "Mudança brusca em Situação" in titulos and "Concentração em Aberto" in titulos
    assert "Campo vazio: Responsável" in titulos and "Dias sem registro" in titulos
    assert "Campo vazio: Conclusão" not in titulos
    orac = oraculo(R_ACH)
    for a in orac:
        if a["regra"] == 6 and "Aberto" not in a["frase"].split(" foi")[0]:
            continue                                                         # o espelho (Concluido) pode vir ou não
        assert casa(a, js), (a["titulo"], a["frase"], [j["frase"] for j in js if j["titulo"] == a["titulo"]])
    # A1: exatamente o exemplo da especificação
    a1 = [j for j in js if j["titulo"] == "Datas no futuro"]
    assert len(a1) == 1 and re.fullmatch(r"2 registros com Abertura depois de hoje; a mais distante é 20/03/2027\.",
                                         a1[0]["frase"].strip())
    # nada inventado fora do oráculo (exceto o espelho de A6 e buracos que dependem de datas no futuro)
    for j in js:
        r = regra_do_titulo(j["titulo"])
        if r in (6, 8) and not any(casa(a, [j]) for a in orac):
            assert r == 6 or j["titulo"] == "Dias sem registro", j
        elif r not in (6, 8):
            assert casa(next(a for a in orac if a["titulo"] == j["titulo"]), [j]), j
    for j in js:                                                              # estrutura {regra, titulo, frase, porque, codigos}
        assert {"regra", "titulo", "frase", "porque", "codigos"} <= set(j)
        assert isinstance(j["codigos"], list) and j["codigos"]


# ---------------- CA-232 ----------------
def test_CA232_por_que_apareceu_e_ver_os_registros(pg):
    abrir_relatorio(pg, "achados.csv")
    s, itens = itens_tela(pg)
    esperado = na_tela(oraculo(R_ACH))
    assert len(itens) == 5
    for i, a in zip(itens, esperado):
        assert f"Por que apareceu: {a['porque']}" in re.sub(r"[ \t]+", " ", i), (a["porque"], i)
    botoes = rel(pg).get_by_role("button", name="Ver os registros", exact=True)
    assert botoes.count() >= 5
    for idx, titulo in ((3, "Valores fora da curva em Valor"), (1, "Datas fora de ordem")):
        alvo = next(a for a in esperado if a["titulo"] == titulo)
        botoes.nth(idx).click()
        j = janela_registros(pg)
        achou = set(re.findall(r"A\d{5}", j.inner_text()))
        assert achou == alvo["codigos"], (titulo, sorted(achou), sorted(alvo["codigos"]))
        assert len(alvo["codigos"]) == (4 if idx == 3 else 3)
        pg.keyboard.press("Escape")
        pg.wait_for_timeout(300)
        if j.is_visible():
            for nome in ("Fechar", "Cancelar", "Ok", "OK"):
                b = j.get_by_role("button", name=nome, exact=True)
                if b.count():
                    b.first.click()
                    break
        pg.wait_for_timeout(300)


# ---------------- CA-233 ----------------
def test_CA233_sem_achados(pg):
    abrir_relatorio(pg, "sem_achados.csv")
    assert oraculo(R_SEM) == []
    s = secao(pg, "O que o Raio X encontrou")
    assert VAZIO_MSG in s["plano"]
    assert js_achados(pg, "sem_achados") == []
    resumo = secao(pg, "Resumo executivo")
    assert "Atenção:" not in resumo["plano"]
    assert not any(i.startswith("Atenção") for i in resumo["itens"])


# ---------------- CA-234 ----------------
def test_CA234_periodo_mes_outubro_sem_datas_no_futuro(pg):
    config(pg)
    carregar(pg, "achados.csv")
    filtra_mes(pg)
    outubro = [r for r in R_ACH if mes(r["ab"]) == (2026, 10)]
    orac = oraculo(outubro)
    assert orac and all(a["regra"] != 1 for a in orac)
    js = js_achados(pg, "achados")
    assert "Datas no futuro" not in {j["titulo"] for j in js}
    s, itens = itens_tela(pg)
    assert "Datas no futuro" not in s["plano"]
    esperado = na_tela(orac)
    assert sorted(titulo_do_item(i) for i in itens) == sorted(a["titulo"] for a in esperado), (itens, esperado)
    for a in esperado:
        assert casa(a, js), (a["titulo"], a["frase"], [j["frase"] for j in js if j["titulo"] == a["titulo"]])


# ---------------- CA-235 ----------------
def test_CA235_quarto_item_do_resumo_e_atencao(pg):
    abrir_relatorio(pg, "achados.csv")
    resumo = secao(pg, "Resumo executivo")["itens"]
    primeiro = oraculo(R_ACH)[0]
    assert len(resumo) >= 4, resumo
    assert resumo[3].startswith("Atenção: "), resumo
    assert re.fullmatch(primeiro["frase"], re.sub(r"\s+", " ", resumo[3][len("Atenção: "):]).strip()), resumo[3]
    js = js_achados(pg, "achados")
    assert resumo[3] == "Atenção: " + js[0]["frase"].strip()
    assert len(resumo) <= 5


# ---------------- CA-236 ----------------
@pytest.mark.parametrize("arq", ["vendas.csv", "chamados.csv"])
def test_CA236_achados_nao_citam_o_que_nao_vem_dos_dados(pg, arq):
    abrir_relatorio(pg, arq)
    cab = list(le_csv(arq)[0].keys())
    js = js_achados(pg, arq.rsplit(".", 1)[0])
    s = secao(pg, "O que o Raio X encontrou")
    texto = (s["texto"] + "\n" + "\n".join(f"{j['titulo']} {j['frase']} {j['porque']}" for j in js)).lower()
    termos = [t.strip() for t in open(RAIZ / "tests/termos_proibidos.txt", encoding="utf-8") if t.strip()]
    assert [t for t in termos if t.lower() in texto] == []
    for j in js:                                                              # campos citados existem no arquivo
        m = re.match(r"(?:Campo vazio|Valores fora da curva em|Mudança brusca em|Concentração em):? (.+)$", j["titulo"])
        if m and not j["titulo"].startswith("Concentração"):
            assert m.group(1) in cab, (j["titulo"], cab)
        assert j["frase"].strip() and j["porque"].strip()
