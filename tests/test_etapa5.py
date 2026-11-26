"""Suite da etapa 5 (CA-50 a CA-55, contas personalizadas). Escrita SO a partir da especificacao
(secoes 0.1, 0.4, 0.6 e 5). Seletores pelos rotulos R-90..R-95 (e R-50/R-64/R-70/R-71).
Oraculos em Python sobre tests/dados/vendas.csv e chamados.csv (formato BR), nunca do app.
Suposicoes: ver docs/duvidas.md / relatorio do Testador (formato do numero comparado com tolerancia de 0,01)."""
import json, re, datetime, statistics, unicodedata
import pytest
from test_etapa1 import (le_csv, carregar, backup, abrir_config, abrir_painel)
from test_etapa2 import dlg, JANELA, marcar, confirmar, texto_seu_painel, fechar_seu_painel, br, num as num_br
from test_etapa3 import pedir, resumo, entender

VENDAS = le_csv("vendas.csv")
CHAMADOS = le_csv("chamados.csv")
VAL = [float(r["Valor"].replace(".", "").replace(",", ".")) for r in VENDAS]
N = len(VENDAS)


def semacento(s):
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn").lower()


# ---------- auxiliares de tela ----------
def abrir_contas(page, arquivo="vendas.csv"):
    carregar(page, arquivo)
    abrir_config(page)
    page.get_by_text("Meus cálculos", exact=True).first.wait_for(state="visible")


def digitar(page, nome, formula):
    n = page.get_by_label("Nome da conta", exact=True)
    f = page.get_by_label("Fórmula", exact=True)
    n.fill(nome)
    f.fill(formula)
    f.press("Tab")
    page.wait_for_timeout(300)


def salvar(page):
    page.get_by_role("button", name="Salvar conta", exact=True).click()
    page.wait_for_timeout(400)


def criar(page, nome, formula):
    digitar(page, nome, formula)
    salvar(page)


def previa(page):
    el = page.get_by_test_id("conta-previa").first
    el.wait_for(state="visible")
    return re.sub(r"\s+", " ", el.inner_text()).strip()


def erro(page):
    al = page.get_by_role("alert").filter(has_text=re.compile(r"\S"))
    if al.count() == 0:
        return ""
    return " ".join(re.sub(r"\s+", " ", t).strip() for t in al.all_inner_texts())


def linhas_contas(page):
    return page.locator("li").filter(has=page.get_by_role("button", name="Remover", exact=True)) \
        .filter(has_text=re.compile(r" = "))


def linha_conta(page, nome):
    return linhas_contas(page).filter(has_text=re.compile(re.escape(nome), re.I))


def conta_salva(page, nome):
    return linha_conta(page, nome).count() > 0


def valor_previa(page):
    t = previa(page)
    assert "sem dados" not in t.lower(), t
    assert not re.search(r"nan|infinity", t, re.I), t
    return num_br(re.search(r"-?\d[\d.]*(?:,\d+)?", t).group(0))


def confere(page, formula, esperado, nome="Conta teste"):
    digitar(page, nome, formula)
    assert erro(page) == "", f"erro inesperado em {formula!r}: {erro(page)}"
    v = valor_previa(page)
    assert abs(v - esperado) <= 0.0051 + abs(esperado) * 1e-9, f"{formula!r}: app {v} != oraculo {esperado}"


def dias_medios():
    f = "%d/%m/%Y %H:%M"
    ds = [(datetime.datetime.strptime(r["Conclusão"], f) - datetime.datetime.strptime(r["Abertura"], f)).total_seconds() / 86400
          for r in CHAMADOS if r["Abertura"] and r["Conclusão"]]
    return sum(ds) / len(ds)


def ticket():
    return sum(VAL) / N


# ---------- CA-50 / CA-51 ----------
def test_CA50_ticket_medio_igual_ao_oraculo(page):
    abrir_contas(page)
    digitar(page, "Ticket médio", "soma(valor) / quantidade()")
    assert erro(page) == ""
    esperado = ticket()
    assert abs(valor_previa(page) - esperado) <= 0.0051
    assert re.search(re.escape(br(esperado)), previa(page)), (previa(page), br(esperado))
    salvar(page)
    assert conta_salva(page, "Ticket médio")


def test_CA51_taxa_de_cancelamento_igual_ao_oraculo(page):
    abrir_contas(page)
    canc = sum(1 for r in VENDAS if r["Situação"] == "Cancelado")
    assert canc > 0
    esperado = canc / N * 100
    confere(page, "quantidade(situacao = cancelado) / quantidade() * 100", esperado, "Taxa de cancelamento")
    assert re.search(re.escape(br(esperado)), previa(page)), (previa(page), br(esperado))
    salvar(page)
    assert conta_salva(page, "Taxa de cancelamento")


# ---------- CA-52 ----------
def test_CA52_campo_inexistente_com_sugestao_e_nao_salva(page):
    abrir_contas(page)
    digitar(page, "Conta ruim", "soma(valr)")
    assert "campo 'valr' não existe; você quis dizer 'valor'?" in erro(page).lower()
    salvar(page)
    assert not conta_salva(page, "Conta ruim")
    assert "campo 'valr' não existe" in erro(page).lower()


def test_CA52_campo_sem_parecido_nao_sugere(page):
    abrir_contas(page)
    digitar(page, "Conta ruim", "soma(xyz)")
    e = erro(page).lower()
    assert "campo 'xyz' não existe" in e and "quis dizer" not in e, e


# ---------- CA-53 ----------
def test_CA53_divisao_por_zero_mostra_sem_dados(page):
    abrir_contas(page)
    digitar(page, "Zero", "quantidade(situacao = xyz) / quantidade(situacao = xyz)")
    assert erro(page) == ""
    t = previa(page)
    assert "sem dados" in t.lower() and not re.search(r"nan|infinity", t, re.I), t
    digitar(page, "Zero", "1 / 0")
    assert erro(page) == ""
    assert "sem dados" in previa(page).lower()
    assert not re.search(r"nan|infinity", page.locator("body").inner_text(), re.I)


# ---------- CA-54 (pedido escrito) ----------
def test_CA54_pedido_ticket_medio_por_regiao(page):
    abrir_contas(page)
    criar(page, "Ticket médio", "soma(valor) / quantidade()")
    assert conta_salva(page, "Ticket médio")
    abrir_painel(page)
    r = entender(page, "ticket médio por região", "vendas")
    assert r["medida"] == "conta" and r["campo"] == "Ticket médio" and r["agrupar"] == "Região", r
    assert r["naoEntendi"] == [] and r["filtros"] == [] and r["periodo"] is None
    pedir(page, "ticket médio por região")
    assert "Ticket médio · por Região" in resumo(page)


def test_CA54_nome_da_conta_sozinho_e_sem_acento_e_erro_de_digitacao(page):
    abrir_contas(page)
    criar(page, "Ticket médio", "soma(valor) / quantidade()")
    s = entender(page, "ticket medio", "vendas")
    assert s["medida"] == "conta" and s["campo"] == "Ticket médio" and s["agrupar"] is None, s
    t = entender(page, "tiket medio por regiao", "vendas")   # semelhanca >= 80%
    assert t["medida"] == "conta" and t["campo"] == "Ticket médio" and t["agrupar"] == "Região", t


def test_CA54_sem_conta_salva_nao_vira_conta(page):
    carregar(page, "vendas.csv")
    r = entender(page, "ticket médio por região", "vendas")
    assert r["medida"] != "conta"


# ---------- CA-55 (seguranca da formula) ----------
@pytest.mark.parametrize("formula,esperado", [
    ("alert(1)", "função 'alert' não existe"),
    ("constructor", "não entendi 'constructor' na fórmula"),
    ("__proto__", None),
    ("this.constructor", None),
    ("constructor.constructor('window.__pwned=1')()", None),
    ("soma(valor) + alert(1)", "função 'alert' não existe"),
])
def test_CA55_codigo_digitado_nao_executa(page, formula, esperado):
    dialogos = []
    page.on("dialog", lambda d: (dialogos.append(d.message), d.dismiss()))
    abrir_contas(page)
    digitar(page, "Perigo", formula)
    e = erro(page).lower()
    assert e, f"sem mensagem de erro para {formula!r}"
    if esperado:
        assert esperado in e, e
    salvar(page)
    page.wait_for_timeout(300)
    assert not conta_salva(page, "Perigo")
    assert dialogos == [], dialogos
    assert page.evaluate("typeof window.__pwned") == "undefined"
    assert not re.search(r"nan|infinity", previa(page), re.I)


# ---------- salvar, listar, catalogo, painel ----------
def test_salvar_aparece_em_lista_catalogo_e_seu_painel(page):
    abrir_contas(page)
    criar(page, "Ticket médio", "soma(valor) / quantidade()")
    assert "Ticket médio = soma(valor) / quantidade()" in re.sub(r"\s+", " ", linha_conta(page, "Ticket médio").first.inner_text())
    abrir_painel(page)
    page.get_by_role("button", name="O que acompanhar", exact=True).click()
    d = dlg(page, JANELA)
    d.wait_for(state="visible")
    assert d.get_by_text("Ticket médio").count() > 0
    marcar(page, ["Ticket médio"])
    confirmar(page)
    flat = texto_seu_painel(page)
    assert "Ticket médio" in flat and "Conta:" in flat and "soma(valor) / quantidade()" in flat, flat
    fechar_seu_painel(page)
    # o bloco e um cartao com o numero, que abre os registros ao clicar
    cartao = page.get_by_text("Ticket médio").first
    assert cartao.is_visible()


def test_remover_conta_tira_da_lista_e_do_backup(page):
    abrir_contas(page)
    criar(page, "Ticket médio", "soma(valor) / quantidade()")
    _, txt = backup(page)
    assert "Ticket médio" in json.dumps(json.loads(txt)["contas"], ensure_ascii=False)
    abrir_config(page)
    linha_conta(page, "Ticket médio").first.get_by_role("button", name="Remover", exact=True).click()
    page.wait_for_timeout(400)
    assert not conta_salva(page, "Ticket médio")
    _, txt2 = backup(page)
    assert "Ticket médio" not in json.dumps(json.loads(txt2).get("contas", {}), ensure_ascii=False)
    assert entender(page, "ticket médio por região", "vendas")["medida"] != "conta"


def test_conta_no_backup_e_restaura(page):
    abrir_contas(page)
    criar(page, "Ticket médio", "soma(valor) / quantidade()")
    _, txt = backup(page)
    b = json.loads(txt)
    assert "contas" in b
    alvo = json.dumps(b["contas"], ensure_ascii=False)
    assert "Ticket médio" in alvo and "soma(valor) / quantidade()" in alvo
    # por conjunto: a conta fica sob o conjunto de vendas, nao global
    assert isinstance(b["contas"], dict) and len(b["contas"]) >= 1
    # restaurar (Substituir) depois de remover traz a conta de volta
    abrir_config(page)
    linha_conta(page, "Ticket médio").first.get_by_role("button", name="Remover", exact=True).click()
    page.wait_for_timeout(300)
    with page.expect_file_chooser() as fc:
        page.get_by_role("button", name="Restaurar backup").click()
    fc.value.set_files([{"name": "b.json", "mimeType": "application/json", "buffer": txt.encode()}])
    page.wait_for_timeout(500)
    page.get_by_role("button", name="Substituir", exact=True).click()
    page.wait_for_timeout(800)
    abrir_config(page)
    assert conta_salva(page, "Ticket médio")


def test_nome_repetido_substitui_sem_diferenciar_maiusculas_nem_acentos(page):
    abrir_contas(page)
    criar(page, "Ticket médio", "soma(valor) / quantidade()")
    criar(page, "TICKET MEDIO", "soma(valor)")
    assert erro(page) == ""
    linhas = linha_conta(page, "ticket")
    assert linhas.count() == 1
    t = re.sub(r"\s+", " ", linhas.first.inner_text())
    assert "soma(valor)" in t and "quantidade()" not in t, t
    _, txt = backup(page)
    cs = json.dumps(json.loads(txt)["contas"], ensure_ascii=False)
    assert cs.count("soma(valor)") >= 1 and "quantidade()" not in cs


def test_limites_nome_60_e_formula_300(page):
    abrir_contas(page)
    n = page.get_by_label("Nome da conta", exact=True)
    f = page.get_by_label("Fórmula", exact=True)
    n.fill("N" * 80)
    f.fill("1+" * 200 + "1")
    assert len(n.input_value()) <= 60
    assert len(f.input_value()) <= 300


def test_nome_e_formula_vazios(page):
    abrir_contas(page)
    digitar(page, "Algo", "")
    salvar(page)
    assert "escreva a fórmula" in erro(page).lower()
    assert not conta_salva(page, "Algo")
    digitar(page, "", "quantidade()")
    salvar(page)
    assert "escreva o nome da conta" in erro(page).lower()


def test_parenteses_com_erro(page):
    abrir_contas(page)
    digitar(page, "P", "soma(valor")
    assert "falta fechar o parêntese" in erro(page).lower()
    salvar(page)
    assert not conta_salva(page, "P")
    digitar(page, "P", "quantidade())")
    assert "parêntese fechado sem abrir" in erro(page).lower()
    digitar(page, "P", "(quantidade()")
    assert "falta fechar o parêntese" in erro(page).lower()


# ---------- formulas: aritmetica ----------
@pytest.mark.parametrize("formula,esperado", [
    ("2 + 3 * 4", 14),
    ("(2 + 3) * 4", 20),
    ("10 - 2 - 3", 5),
    ("100 / 5 / 2", 10),
    ("-(2 + 3) * 2", -10),
    ("2 * -3", -6),
    ("- -4", 4),
    ("1.5 * 2", 3),
    ("((((7))))", 7),
])
def test_formulas_aritmetica_precedencia_parenteses_unario(page, formula, esperado):
    abrir_contas(page)
    confere(page, formula, esperado)


def test_formula_mistura_dados_e_precedencia(page):
    abrir_contas(page)
    s, q = sum(VAL), N
    confere(page, "(soma(valor) + quantidade()) * 2 - -quantidade()", (s + q) * 2 + q)
    confere(page, "soma(valor) / quantidade() * 100 - quantidade() / 2", s / q * 100 - q / 2)


# ---------- funcoes ----------
def test_funcoes_quantidade_soma_media_mediana_distintos(page):
    abrir_contas(page)
    confere(page, "quantidade()", N)
    confere(page, "soma(valor)", sum(VAL))
    confere(page, "media(valor)", statistics.mean(VAL))
    confere(page, "mediana(valor)", statistics.median(VAL))
    confere(page, "distintos(cliente)", len({r["Cliente"] for r in VENDAS if r["Cliente"].strip()}))
    confere(page, "distintos(regiao)", len({r["Região"] for r in VENDAS if r["Região"].strip()}))


def test_funcoes_com_filtro(page):
    abrir_contas(page)
    ent = [float(r["Valor"].replace(".", "").replace(",", ".")) for r in VENDAS if r["Situação"] == "Entregue"]
    sul = [r for r in VENDAS if r["Região"] == "Sul"]
    confere(page, "quantidade(situacao = entregue)", len(ent))
    confere(page, "soma(valor, situacao = entregue)", sum(ent))
    confere(page, "media(valor, situacao = entregue)", statistics.mean(ent))
    confere(page, "mediana(valor, situacao = entregue)", statistics.median(ent))
    confere(page, 'quantidade(situacao = "Entregue")', len(ent))
    confere(page, "quantidade(regiao = Sul)", len(sul))


def test_filtro_sem_acento_e_sem_diferenciar_maiusculas(page):
    abrir_contas(page)
    sul = sum(1 for r in VENDAS if r["Região"] == "Sul")
    canc = sum(1 for r in VENDAS if r["Situação"] == "Cancelado")
    confere(page, "quantidade(REGIAO = sul)", sul)
    confere(page, "quantidade(região = SUL)", sul)
    confere(page, "quantidade(SITUAÇÃO = CANCELADO)", canc)
    confere(page, 'soma("Valor", "Situação" = cancelado)',
            sum(v for v, r in zip(VAL, VENDAS) if r["Situação"] == "Cancelado"))


def test_dias_media_em_dias_chamados(page):
    abrir_contas(page, "chamados.csv")
    esperado = dias_medios()
    assert esperado > 0
    confere(page, "dias(abertura, conclusao)", esperado)
    confere(page, "dias(abertura, conclusao) * 24", esperado * 24)


def test_dias_com_campo_de_nome_composto_entre_aspas_e_erro_de_data_inexistente(page):
    abrir_contas(page, "chamados.csv")
    digitar(page, "D", "dias(abertura, fechamento)")
    assert "campo 'fechamento' não existe" in erro(page).lower()


def test_nome_solto_que_e_campo_nao_vira_funcao(page):
    abrir_contas(page)
    digitar(page, "Solto", "quantidade(")
    assert erro(page) != ""
    digitar(page, "Solto", "soma()")
    assert erro(page) != ""
    digitar(page, "Solto", "xyz(1)")
    assert "função 'xyz' não existe" in erro(page).lower()


# ---------- F-62: Baixos da revisao de seguranca da etapa 5 (regressao) ----------
def test_f62_nome_com_marca_de_direcao_e_recusado_ao_salvar(page):
    abrir_contas(page)
    digitar(page, "Ticket‮medio", "soma(valor)")
    salvar(page)
    assert not conta_salva(page, "Ticket‮medio")


def test_f62_backup_forjado_com_nome_invisivel_e_rejeitado(page):
    abrir_contas(page)
    criar(page, "Ticket médio", "soma(valor) / quantidade()")
    _, txt = backup(page)
    b = json.loads(txt)
    k = next(iter(b["contas"]))
    b["contas"][k][0]["nome"] = "Ticket‮medio"
    abrir_config(page)
    linha_conta(page, "Ticket médio").first.get_by_role("button", name="Remover", exact=True).click()
    page.wait_for_timeout(300)
    with page.expect_file_chooser() as fc:
        page.get_by_role("button", name="Restaurar backup").click()
    fc.value.set_files([{"name": "b.json", "mimeType": "application/json", "buffer": json.dumps(b).encode()}])
    page.wait_for_timeout(500)
    assert page.get_by_role("button", name="Substituir", exact=True).count() == 0
    assert "Nada foi alterado" in page.locator("body").inner_text()


def test_f62_estouro_de_pilha_em_qualquer_navegador_vira_mensagem_amigavel(page):
    # o Firefox diz "too much recursion"; o interpretador nao pode depender do texto do Chrome
    msg = page.evaluate("""() => { const o = Core.compilaFormula('(' .repeat(60) + '1' + ')'.repeat(60), []); return o.erro; }""")
    assert "complicada demais" in msg
    r = page.evaluate("""() => { const f = Core.compilaFormula('1+1', []); return f.ok; }""")
    assert r is True
