"""Oficina de testes: roda excel/RaioX_Relatorio.bas no LibreOffice Calc headless.

Uso: python3 tests/oficina/macro_libreoffice.py [saida.xlsx]
Funcao principal: rodar(saida_xlsx, perfil_dir=None) -> dict com mensagens da macro.
"""
import os, re, pathlib, shutil, socket, subprocess, sys, tempfile, time

RAIZ = pathlib.Path(__file__).resolve().parents[2]
BAS = RAIZ / "excel" / "RaioX_Relatorio.bas"
DADOS = RAIZ / "tests" / "dados"
SOFFICE = shutil.which("soffice") or "/usr/bin/soffice"


class ErroMacro(Exception):
    pass


# Scripting.Dictionary so existe no Windows. Na oficina entra um dubles em classe Basic (so chaves
# sem diferenciar maiusculas, como CompareMode = 1) e as chamadas dc(x) viram dc.Item(x).
DICIONARIO = """Option VBASupport 1
Option ClassModule
Private mK() As String
Private mV() As Variant
Private mN As Long
Public Property Let CompareMode(ByVal x As Long)
End Property
Private Function Achar(ByVal k As String) As Long
    Dim i As Long
    For i = 1 To mN
        If StrComp(mK(i), k, 1) = 0 Then Achar = i: Exit Function
    Next i
End Function
Public Property Get Count() As Long
    Count = mN
End Property
Public Function Exists(ByVal k As String) As Boolean
    Exists = (Achar(k) > 0)
End Function
Public Property Get Item(ByVal k As String) As Variant
    Dim i As Long
    i = Achar(k)
    If i = 0 Then Item = Empty Else Item = mV(i)
End Property
Public Sub Poe(ByVal k As String, ByVal v As Variant)
    Dim i As Long
    i = Achar(k)
    If i = 0 Then
        mN = mN + 1
        ReDim Preserve mK(1 To mN)
        ReDim Preserve mV(1 To mN)
        i = mN
        mK(i) = k
    End If
    mV(i) = v
End Sub
Public Function Keys() As Variant
    Dim a() As Variant, i As Long
    ReDim a(0 To mN - 1)
    For i = 1 To mN
        a(i - 1) = mK(i)
    Next i
    Keys = a
End Function
"""


def modulo_basic():
    """Conteudo do .bas sem a linha Attribute VB_Name, com Option VBASupport 1 no topo."""
    import re
    txt = BAS.read_bytes().decode("cp1252").replace("\r\n", "\n")
    linhas = []
    continua = False
    tratador = False
    for n, l in enumerate(txt.split("\n"), 1):
        if l.startswith("Attribute VB_Name"):
            l = ""
        st = l.strip()
        # mAqui = numero da linha no .bas (Erl do LibreOffice nao aceita varios rotulos), para dizer onde o erro aconteceu
        if st == "falha:":
            tratador = True
        elif st.startswith(("End Sub", "End Function")):
            tratador = False
        if (l.startswith("    ") and st and not continua and not tratador
                and not re.match(r"(Dim|Const|Case|Else|ElseIf|End|Next|Loop|Do|Wend|On Error|Exit|Static|ReDim|'|falha:|Rem)\b", st)
                and "Err." not in st and not st.endswith(":")):
            l = "    mAqui = %d\n%s" % (n, l)
        continua = st.endswith(" _")
        linhas.append(l)
    src = "\n".join(linhas)
    src = src.replace("Err.Description", 'Err.Description & " (linha " & mAqui & ")"')
    src = src.replace('CreateObject("Scripting.Dictionary")', "New Dicionario")
    src = re.sub(r"^(\s*(?:mAqui = \d+\n\s*)?)\b(dc|dr)\((.+?)\) = (.+)$", r"\1\2.Poe \3, \4", src, flags=re.M)
    src = re.sub(r"\b(dc|dr)\(", r"\1.Item(", src)
    return "Option VBASupport 1\nPrivate mAqui As Long\n" + src


def _porta_livre():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _conectar(porta, proc):
    import uno
    local = uno.getComponentContext()
    res = local.ServiceManager.createInstanceWithContext("com.sun.star.bridge.UnoUrlResolver", local)
    for _ in range(150):
        if proc.poll() is not None:
            raise ErroMacro("soffice terminou antes de conectar")
        try:
            return res.resolve(f"uno:socket,host=127.0.0.1,port={porta};urp;StarOffice.ComponentContext")
        except Exception:
            time.sleep(0.2)
    raise ErroMacro("soffice nao respondeu")


def rodar(saida_xlsx, extra_importacoes=None, config=None):
    """Instalar -> OficinaImportar(vendas) -> OficinaImportar(parte2) -> AtualizarPainel -> OficinaGerar."""
    import uno
    from com.sun.star.beans import PropertyValue
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="raiox_lo_"))
    porta = _porta_livre()
    proc = subprocess.Popen(
        [SOFFICE, "--headless", "--invisible", "--norestore", "--nologo", "--nodefault",
         f"-env:UserInstallation=file://{tmp}/perfil",
         f"--accept=socket,host=127.0.0.1,port={porta};urp;"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        ctx = _conectar(porta, proc)
        desk = ctx.ServiceManager.createInstanceWithContext("com.sun.star.frame.Desktop", ctx)
        doc = desk.loadComponentFromURL("private:factory/scalc", "_blank", 0, ())
        lib = doc.BasicLibraries
        if not lib.hasByName("Standard"):
            lib.createLibrary("Standard")
        lib.loadLibrary("Standard")
        lib.getByName("Standard").insertByName("Dicionario", DICIONARIO)
        lib.getByName("Standard").insertByName("RaioX", modulo_basic())
        sp = doc.getScriptProvider()

        def chamar(nome, *args):
            uri = f"vnd.sun.star.script:Standard.RaioX.{nome}?language=Basic&location=document"
            try:
                r = sp.getScript(uri).invoke(tuple(args), (), ()); (os.environ.get("DBG") and print(nome, repr(r))); return r[0]
            except Exception as e:
                msg = getattr(e, "Message", None) or str(e)
                raise ErroMacro(f"{nome}: {msg}") from None

        def memoria():
            return [l for l in str(chamar("OficinaMensagens") or "").split("\n") if l]

        import os
        if os.environ.get("DBG"):
            return {"mensagens": [str(chamar("Dbg"))]}
        chamar("OficinaLigar")
        chamar("Instalar")
        if "Config" not in doc.Sheets.ElementNames:
            raise ErroMacro("Instalar nao criou as abas: " + " / ".join(memoria()))
        if config:
            cfg = doc.Sheets.getByName("Config")
            cfg.getCellRangeByName("B3").String = config[0]
            cfg.getCellRangeByName("B4").String = config[1]
        chamar("OficinaImportar", str(DADOS / "vendas.csv"))
        chamar("OficinaImportar", str(DADOS / "vendas_parte2.csv"))
        for extra in extra_importacoes or []:
            chamar("OficinaImportar", str(extra))
        chamar("AtualizarPainel")
        chamar("OficinaGerar", str(saida_xlsx))
        # No LibreOffice o SaveAs com 51 grava .xls; por isso quem chama salva o relatorio como .xlsx.
        relatorio = None
        enum = desk.Components.createEnumeration()
        while enum.hasMoreElements():
            c = enum.nextElement()
            if c is not doc and hasattr(c, "Sheets") and "Capa" in c.Sheets.ElementNames:
                relatorio = c
        if relatorio is None:
            raise ErroMacro("OficinaGerar nao criou o relatorio (aba Capa): " + " / ".join(memoria()))
        f = PropertyValue(); f.Name = "FilterName"; f.Value = "Calc MS Excel 2007 XML"
        o = PropertyValue(); o.Name = "Overwrite"; o.Value = True
        relatorio.storeToURL(pathlib.Path(saida_xlsx).resolve().as_uri(), (f,))
        relatorio.close(True)
        erros = [m for m in memoria() if m.startswith("[ALERTA]")]
        if erros:
            raise ErroMacro("A macro mostrou alertas:\n" + "\n".join(erros))
        msgs = memoria()
        doc.close(True)
        return {"mensagens": msgs}
    finally:
        proc.terminate()
        try:
            proc.wait(10)
        except Exception:
            proc.kill()
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    saida = sys.argv[1] if len(sys.argv) > 1 else "/tmp/raiox_oficina.xlsx"
    r = rodar(saida, config=("Cliente Teste", "Area Teste"))
    print("\n".join(r["mensagens"]))
    print("OK ->", saida)
