"""Oficina de testes da macro VBA no LibreOffice headless (sem Playwright).
Roda excel/RaioX_Relatorio.bas de ponta a ponta e confere o .xlsx gerado com openpyxl.
O que o LibreOffice nao cobre esta em docs/03_homologacao/roteiro-excel.md."""
import csv, pathlib, shutil, sys
from collections import Counter
import pytest

RAIZ = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "tests" / "oficina"))
DADOS = RAIZ / "tests" / "dados"

pytestmark = pytest.mark.skipif(
    shutil.which("soffice") is None and not pathlib.Path("/usr/bin/soffice").exists(),
    reason="LibreOffice (soffice) nao instalado: a oficina da macro nao roda aqui")

openpyxl = pytest.importorskip("openpyxl")
CLIENTE, AREA = "Cliente Oficina", "Area Oficina"


def le(nome):
    with open(DADOS / nome, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f, delimiter=";"))


@pytest.fixture(scope="module")
def relatorio(tmp_path_factory):
    import macro_libreoffice
    saida = tmp_path_factory.mktemp("oficina") / "relatorio.xlsx"
    res = macro_libreoffice.rodar(saida, config=(CLIENTE, AREA))
    return openpyxl.load_workbook(saida), res


def test_abas_capa_resumo_registros(relatorio):
    wb, _ = relatorio
    assert {"Capa", "Resumo", "Registros"} <= set(wb.sheetnames)


def test_total_de_registros_igual_ao_calculado(relatorio):
    wb, _ = relatorio
    vendas, p2 = le("vendas.csv"), le("vendas_parte2.csv")
    esperado = len({r["Código"] for r in vendas} | {r["Código"] for r in p2})
    capa = {r[0]: r[1] for r in wb["Capa"].iter_rows(values_only=True) if r[0]}
    assert capa["Total de registros"] == esperado
    ws = wb["Registros"]
    linhas = [r for r in ws.iter_rows(min_row=2, values_only=True) if r[0]]
    assert len(linhas) == esperado
    resumo = {r[0]: r[1] for r in wb["Resumo"].iter_rows(min_row=4, values_only=True) if r[0]}
    assert resumo["Total"] == esperado


def test_contagem_por_cliente(relatorio):
    wb, _ = relatorio
    esperado = Counter(r["Cliente"] for r in le("vendas.csv"))
    resumo = {r[0]: r[1] for r in wb["Resumo"].iter_rows(min_row=4, values_only=True) if r[0] and r[0] != "Total"}
    # o codigo extra da parte 2 (V90001) nao existe em vendas.csv: fica no grupo "(vazio)"
    assert resumo.pop("(vazio)", 0) == 1
    assert resumo == dict(esperado)


def test_so_valores_sem_formulas(relatorio):
    wb, _ = relatorio
    formulas = [f"{ws.title}!{c.coordinate}" for ws in wb for row in ws.iter_rows() for c in row if c.data_type == "f"]
    assert formulas == []


def test_capa_com_cliente_e_area_da_config(relatorio):
    wb, _ = relatorio
    capa = {r[0]: r[1] for r in wb["Capa"].iter_rows(values_only=True) if r[0]}
    assert capa["Cliente"] == CLIENTE and capa["Área"] == AREA


def test_juncao_sem_duplicar_e_com_prioridade(relatorio):
    wb, _ = relatorio
    ws = wb["Registros"]
    cab = [c.value for c in ws[1]]
    assert "Prioridade" in cab
    ic, ip = cab.index("Código"), cab.index("Prioridade")
    linhas = [r for r in ws.iter_rows(min_row=2, values_only=True) if r[ic]]
    codigos = [r[ic] for r in linhas]
    assert len(codigos) == len(set(codigos)), "codigos duplicados apos a juncao"
    p2 = {r["Código"]: r["Prioridade"] for r in le("vendas_parte2.csv")}
    por_cod = {r[ic]: r[ip] for r in linhas}
    for cod, pr in p2.items():
        assert cod in por_cod
        assert (por_cod[cod] or "") == pr


def test_sem_termos_proibidos_no_relatorio(relatorio):
    wb, _ = relatorio
    termos = [t.strip().lower() for t in open(RAIZ / "tests/termos_proibidos.txt", encoding="utf-8") if t.strip()]
    texto = " ".join(str(c.value).lower() for ws in wb for row in ws.iter_rows() for c in row if c.value is not None)
    assert [t for t in termos if t in texto] == []


def test_macro_sem_alertas(relatorio):
    _, res = relatorio
    assert not [m for m in res["mensagens"] if m.startswith("[ALERTA]")]
