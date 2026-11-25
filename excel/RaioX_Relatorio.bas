Attribute VB_Name = "RaioX_Relatorio"
'==========================================================================
' Raio X do Relatório - versão Excel (Excel 2016 ou mais novo, Windows)
' Importa relatórios (CSV, XLSX, ZIP), pergunta "Esta coluna é o quê?" uma vez
' por formato, junta os registros pelo código (campo a campo) e monta o Painel.
' Macros: Instalar | ImportarArquivos | AtualizarPainel | GerarRelatorio
'         EsquecerFormatos | ApagarDados
' Sem referências externas: tudo por late binding (Scripting, ADODB, Shell).
'==========================================================================
Option Explicit

Private Const SH_PAINEL As String = "Painel"
Private Const SH_CONFIG As String = "Config"
Private Const SH_DADOS As String = "Dados"
Private Const SH_MEM As String = "_Memoria"
Private Const COD As String = "Código"
Private Const TODAS As String = "(todas)"

Private mLin As Collection
Private mCur() As String
Private mNc As Long
Private mBuf As String
Private mMax As Long
Private gNovos As Long
Private gAtualizados As Long
Private gLidos As Long
Private mOficina As Boolean      ' ligada so pela oficina de testes: nenhuma caixa bloqueia
Private mLogOficina As String   ' mensagens que a macro mostraria (uma por linha)
Private mSaidaOficina As String  ' caminho de saida usado pela oficina (sem dialogo)

'------------------------------------------------------------ oficina de testes
' Ganchos para teste automatico (LibreOffice headless). No uso normal nao sao chamados.
Public Sub OficinaLigar()
    mOficina = True
End Sub

Public Function OficinaMensagens() As String
    OficinaMensagens = mLogOficina
End Function

Public Sub OficinaImportar(ByVal caminhos As String)
    Dim v As Variant, i As Long
    mOficina = True
    If Not Pronto() Then Exit Sub
    v = Split(caminhos, "|")
    gNovos = 0: gAtualizados = 0: gLidos = 0
    For i = LBound(v) To UBound(v)
        If Len(Trim$(CStr(v(i)))) > 0 Then ImportarUm CStr(v(i)), True
    Next i
    AtualizarPainel
    Msg "Linhas lidas: " & gLidos & " | novos: " & gNovos & " | completados: " & gAtualizados, vbInformation, "Importar arquivos"
End Sub

Public Sub OficinaGerar(ByVal caminhoSaida As String)
    mOficina = True
    mSaidaOficina = caminhoSaida
    GerarRelatorio
End Sub

' Em oficina, as mensagens ficam em mLogOficina (lidas por OficinaMensagens) e nao bloqueiam.
Private Function Msg(ByVal texto As String, ByVal estilo As Long, ByVal titulo As String) As Long
    If mOficina Then
        mLogOficina = mLogOficina & IIf((estilo And 48) = 48, "[ALERTA] ", "") & titulo & ": " & texto & vbLf
        Msg = vbYes
    Else
        Msg = MsgBox(texto, estilo, titulo)
    End If
End Function

'------------------------------------------------------------ instalação
Public Sub Instalar()
    Dim ws As Worksheet
    On Error GoTo falha
    Application.ScreenUpdating = False
    Set ws = PegarOuCriar(SH_PAINEL)
    Set ws = PegarOuCriar(SH_CONFIG)
    Set ws = PegarOuCriar(SH_DADOS)
    Set ws = PegarOuCriar(SH_MEM)
    MontarMemoria
    MontarConfig
    MontarDados
    MontarPainel
    RemoverFolhaVazia "Planilha1"
    RemoverFolhaVazia "Sheet1"
    ThisWorkbook.Worksheets(SH_MEM).Visible = xlSheetHidden
    ThisWorkbook.Worksheets(SH_PAINEL).Activate
    Application.ScreenUpdating = True
    Msg "Instalação pronta. Na aba Painel, clique em Importar arquivos.", vbInformation, "Raio X do Relatório"
    Exit Sub
falha:
    Application.ScreenUpdating = True
    Msg "Não consegui instalar: " & Err.Description, vbExclamation, "Raio X do Relatório"
End Sub

Private Sub MontarMemoria()
    Dim ws As Worksheet
    Set ws = Folha(SH_MEM)
    If Len(CStr(ws.Range("A1").Value)) = 0 Then
        ws.Range("A1").Value = "Formato"
        ws.Range("B1").Value = "Coluna"
        ws.Range("C1").Value = "Papel"
        ws.Range("E1").Value = "Campos"
        ws.Range("G1").Value = "Categorias"
    End If
    ws.Columns("A:C").NumberFormat = "@"
    On Error Resume Next
    ThisWorkbook.Names("ListaCampos").Delete
    ThisWorkbook.Names("ListaCategorias").Delete
    On Error GoTo 0
    ThisWorkbook.Names.Add Name:="ListaCampos", RefersTo:="=OFFSET('" & SH_MEM & "'!$E$2,0,0,MAX(1,COUNTA('" & SH_MEM & "'!$E$2:$E$300)),1)"
    ThisWorkbook.Names.Add Name:="ListaCategorias", RefersTo:="=OFFSET('" & SH_MEM & "'!$G$2,0,0,MAX(1,COUNTA('" & SH_MEM & "'!$G$2:$G$5000)),1)"
End Sub

Private Sub MontarConfig()
    Dim ws As Worksheet
    Set ws = Folha(SH_CONFIG)
    ws.Range("A1").Value = "Config"
    ws.Range("A1").Font.Size = 18
    ws.Range("A1").Font.Bold = True
    ws.Range("A3").Value = "Cliente"
    ws.Range("A4").Value = "Área"
    ws.Range("A3:A4").Font.Bold = True
    ws.Range("B3:B4").Interior.Color = RGB(255, 249, 219)
    ws.Range("A6").Value = "Os formatos de arquivo ficam lembrados numa aba oculta. Use os botões abaixo para esquecer ou apagar."
    ws.Columns("A").ColumnWidth = 22
    ws.Columns("B").ColumnWidth = 40
    ApagarBotoes ws
    NovoBotao ws, "Esquecer formatos lembrados", "EsquecerFormatos", ws.Range("A8").Left, ws.Range("A8").Top, 190
    NovoBotao ws, "Apagar todos os dados", "ApagarDados", ws.Range("A8").Left + 200, ws.Range("A8").Top, 170
End Sub

Private Sub MontarDados()
    Dim ws As Worksheet
    Set ws = Folha(SH_DADOS)
    ws.Columns(1).NumberFormat = "@"
    If Len(CStr(ws.Range("A1").Value)) = 0 Then ws.Range("A1").Value = COD
    ws.Range("A1").Font.Bold = True
End Sub

Private Sub MontarPainel()
    Dim ws As Worksheet
    Set ws = Folha(SH_PAINEL)
    ws.Cells.Font.Name = "Calibri"
    ws.Range("A1").Value = "Raio X do Relatório"
    ws.Range("A1").Font.Size = 20
    ws.Range("A1").Font.Bold = True
    ws.Range("A7").Value = "Período de"
    ws.Range("C7").Value = "até"
    ws.Range("A8").Value = "Campo de data"
    ws.Range("A9").Value = "Campo categoria"
    ws.Range("A10").Value = "Categoria"
    ws.Range("A7:A10").Font.Bold = True
    ws.Range("B7").NumberFormat = "dd/mm/yyyy"
    ws.Range("D7").NumberFormat = "dd/mm/yyyy"
    ws.Range("B7:B10").Interior.Color = RGB(255, 249, 219)
    ws.Range("D7").Interior.Color = RGB(255, 249, 219)
    ws.Range("A12").Value = "Total de registros"
    ws.Range("A12:B12").Font.Bold = True
    ws.Range("A12:B12").Font.Size = 14
    ws.Range("B12").NumberFormat = "#,##0"
    ws.Range("A5").Value = "Depois de mudar período, campo ou categoria, clique em Atualizar painel."
    ws.Range("A5").Font.Italic = True
    ws.Columns("A").ColumnWidth = 30
    ws.Columns("B").ColumnWidth = 22
    ws.Columns("C").ColumnWidth = 6
    ws.Columns("D").ColumnWidth = 16
    ListaValidacao ws.Range("B8"), "=ListaCampos"
    ListaValidacao ws.Range("B9"), "=ListaCampos"
    ListaValidacao ws.Range("B10"), "=ListaCategorias"
    ApagarBotoes ws
    NovoBotao ws, "Importar arquivos", "ImportarArquivos", ws.Range("A3").Left, ws.Range("A3").Top, 140
    NovoBotao ws, "Atualizar painel", "AtualizarPainel", ws.Range("A3").Left + 150, ws.Range("A3").Top, 130
    NovoBotao ws, "Gerar relatório", "GerarRelatorio", ws.Range("A3").Left + 290, ws.Range("A3").Top, 170
    ActiveWindow.DisplayGridlines = False
End Sub

Private Sub ListaValidacao(ByVal r As Range, ByVal formula As String)
    r.Validation.Delete
    r.Validation.Add Type:=xlValidateList, AlertStyle:=xlValidAlertStop, Formula1:=formula
    r.Validation.IgnoreBlank = True
    r.Validation.ShowError = False
End Sub

Private Sub NovoBotao(ByVal ws As Worksheet, ByVal texto As String, ByVal macro As String, ByVal x As Double, ByVal y As Double, ByVal larg As Double)
    If mOficina Then Exit Sub   ' LibreOffice nao cria Shapes com OnAction (ver roteiro-excel.md)
    Dim s As Shape
    Set s = ws.Shapes.AddShape(msoShapeRoundedRectangle, x, y, larg, 26)
    s.Name = "btn_" & macro
    s.OnAction = macro
    s.Fill.ForeColor.RGB = RGB(31, 78, 121)
    s.Line.Visible = msoFalse
    s.TextFrame.Characters.Text = texto
    s.TextFrame.Characters.Font.Color = RGB(255, 255, 255)
    s.TextFrame.Characters.Font.Bold = True
    s.TextFrame.HorizontalAlignment = xlHAlignCenter
    s.TextFrame.VerticalAlignment = xlVAlignCenter
End Sub

Private Sub ApagarBotoes(ByVal ws As Worksheet)
    If mOficina Then Exit Sub   ' LibreOffice nao cria Shapes com OnAction (ver roteiro-excel.md)
    Dim i As Long
    For i = ws.Shapes.Count To 1 Step -1
        If Left$(ws.Shapes(i).Name, 4) = "btn_" Then ws.Shapes(i).Delete
    Next i
End Sub

Private Sub RemoverFolhaVazia(ByVal nome As String)
    Dim ws As Worksheet
    Set ws = Folha(nome)
    If ws Is Nothing Then Exit Sub
    If Application.WorksheetFunction.CountA(ws.Cells) = 0 And ThisWorkbook.Worksheets.Count > 1 Then
        Application.DisplayAlerts = False
        ws.Delete
        Application.DisplayAlerts = True
    End If
End Sub

Private Function Folha(ByVal nome As String) As Worksheet
    Dim ws As Worksheet
    For Each ws In ThisWorkbook.Worksheets
        If StrComp(ws.Name, nome, vbTextCompare) = 0 Then
            Set Folha = ws
            Exit Function
        End If
    Next ws
End Function

Private Function PegarOuCriar(ByVal nome As String) As Worksheet
    Dim ws As Worksheet
    Set ws = Folha(nome)
    If ws Is Nothing Then
        Set ws = ThisWorkbook.Worksheets.Add(After:=ThisWorkbook.Worksheets(ThisWorkbook.Worksheets.Count))
        ws.Name = nome
    End If
    Set PegarOuCriar = ws
End Function

Private Function Dic() As Object
    Dim o As Object
    Set o = CreateObject("Scripting.Dictionary")
    o.CompareMode = 1
    Set Dic = o
End Function

Private Function Pronto() As Boolean
    If Folha(SH_PAINEL) Is Nothing Or Folha(SH_DADOS) Is Nothing Or Folha(SH_MEM) Is Nothing Or Folha(SH_CONFIG) Is Nothing Then
        Msg "Rode primeiro a macro Instalar (Alt + F8).", vbExclamation, "Raio X do Relatório"
    Else
        Pronto = True
    End If
End Function

'------------------------------------------------------------ importação
Public Sub ImportarArquivos()
    Dim v As Variant, i As Long, n As Long
    If Not Pronto() Then Exit Sub
    v = Application.GetOpenFilename("Arquivos de dados (*.csv;*.txt;*.xlsx;*.xls;*.zip),*.csv;*.txt;*.xlsx;*.xls;*.zip", , "Importar arquivos", , True)
    If Not IsArray(v) Then Exit Sub
    On Error GoTo falha
    gNovos = 0: gAtualizados = 0: gLidos = 0
    Application.ScreenUpdating = False
    For i = LBound(v) To UBound(v)
        n = n + ImportarUm(CStr(v(i)), True)
    Next i
    AtualizarPainel
    Application.ScreenUpdating = True
    Msg "Linhas lidas: " & gLidos & vbCrLf & "Registros novos: " & gNovos & vbCrLf & "Registros completados (mesmo código): " & gAtualizados, vbInformation, "Importar arquivos"
    Exit Sub
falha:
    Application.ScreenUpdating = True
    Msg "Importação interrompida: " & Err.Description, vbExclamation, "Importar arquivos"
End Sub

Private Function ImportarUm(ByVal caminho As String, ByVal aceitaZip As Boolean) As Long
    Dim ext As String, t As Variant
    On Error GoTo falha
    ext = LCase$(Mid$(caminho, InStrRev(caminho, ".") + 1))
    Select Case ext
        Case "csv", "txt"
            t = LerCsv(caminho)
            If Not IsEmpty(t) Then ImportarUm = Incorporar(t)
        Case "xlsx", "xls", "xlsm"
            ImportarUm = ImportarPlanilha(caminho)
        Case "zip"
            If aceitaZip Then ImportarUm = ImportarZip(caminho)
    End Select
    Exit Function
falha:
    Msg "Não consegui ler " & Mid$(caminho, InStrRev(caminho, "\") + 1) & ": " & Err.Description, vbExclamation, "Importar arquivos"
End Function

Private Function ImportarZip(ByVal caminho As String) As Long
    Dim fso As Object, sh As Object, tmp As String, f As Object, esperado As Long, t0 As Single, n As Long
    Set fso = CreateObject("Scripting.FileSystemObject")
    Set sh = CreateObject("Shell.Application")
    tmp = Environ$("TEMP") & "\RaioX_" & Format$(Now, "yyyymmddhhnnss")
    fso.CreateFolder tmp
    esperado = sh.Namespace(CVar(caminho)).Items.Count
    sh.Namespace(CVar(tmp)).CopyHere sh.Namespace(CVar(caminho)).Items, 20
    t0 = Timer
    Do While fso.GetFolder(tmp).Files.Count + fso.GetFolder(tmp).SubFolders.Count < esperado And Timer - t0 < 90
        DoEvents
    Loop
    Application.Wait Now + TimeSerial(0, 0, 1)
    For Each f In fso.GetFolder(tmp).Files
        n = n + ImportarUm(CStr(f.Path), False)
    Next f
    On Error Resume Next
    fso.DeleteFolder tmp, True
    On Error GoTo 0
    ImportarZip = n
End Function

Private Function ImportarPlanilha(ByVal caminho As String) As Long
    Dim wb As Workbook, ws As Worksheet, t As Variant, n As Long
    Set wb = Workbooks.Open(caminho, False, True)
    For Each ws In wb.Worksheets
        If ws.UsedRange.Cells.Count > 1 Then
            t = ws.UsedRange.Value
            n = n + Incorporar(t)
        End If
    Next ws
    wb.Close False
    ThisWorkbook.Activate
    ImportarPlanilha = n
End Function

Private Function LerCsv(ByVal caminho As String) As Variant
    Dim txt As String, d As String
    txt = LerTexto(caminho)
    If Len(txt) = 0 Then Exit Function
    d = DetectarSeparador(txt)
    LerCsv = AnalisarCsv(txt, d)
End Function

Private Function LerTexto(ByVal caminho As String) As String
    Dim f As Integer, b() As Byte, stm As Object, cs As String
    f = FreeFile
    Open caminho For Binary Access Read As #f
    If LOF(f) = 0 Then
        Close #f
        Exit Function
    End If
    ReDim b(0 To LOF(f) - 1)
    Get #f, , b
    Close #f
    If Utf8Valido(b) Then cs = "utf-8" Else cs = "windows-1252"
    If mOficina Then
        LerTexto = DecodificarOficina(b, cs = "utf-8")   ' sem ADODB (nao existe fora do Windows)
        Exit Function
    End If
    Set stm = CreateObject("ADODB.Stream")
    stm.Type = 1
    stm.Open
    stm.Write b
    stm.Position = 0
    stm.Type = 2
    stm.Charset = cs
    LerTexto = stm.ReadText
    stm.Close
End Function

' Somente oficina: decodifica UTF-8 ou Windows-1252 sem ADODB.Stream.
Private Function DecodificarOficina(ByRef b() As Byte, ByVal utf8 As Boolean) As String
    Dim i As Long, n As Long, c As Long, sb As String, cp As Long
    Const CP1252 As String = "20AC 81 201A 0192 201E 2026 2020 2021 02C6 2030 0160 2039 0152 8D 017D 8F 90 2018 2019 201C 201D 2022 2013 2014 02DC 2122 0161 203A 0153 9D 017E 0178"
    Dim t As Variant
    t = Split(CP1252, " ")
    n = UBound(b)
    i = 0
    Do While i <= n
        c = b(i)
        If utf8 And c >= 194 Then
            If c <= 223 Then
                cp = (c And 31) * 64 + (b(i + 1) And 63): i = i + 2
            ElseIf c <= 239 Then
                cp = (c And 15) * 4096 + (b(i + 1) And 63) * 64 + (b(i + 2) And 63): i = i + 3
            Else
                cp = 63: i = i + 4
            End If
        ElseIf Not utf8 And c >= 128 And c <= 159 Then
            cp = CLng("&H" & t(c - 128)): i = i + 1
        Else
            cp = c: i = i + 1
        End If
        sb = sb & ChrW(cp)
    Loop
    DecodificarOficina = sb
End Function

Private Function Utf8Valido(ByRef b() As Byte) As Boolean
    Dim i As Long, n As Long, c As Long, falta As Long, k As Long
    n = UBound(b)
    i = 0
    Do While i <= n
        c = b(i)
        If c < 128 Then
            falta = 0
        ElseIf c >= 194 And c <= 223 Then
            falta = 1
        ElseIf c >= 224 And c <= 239 Then
            falta = 2
        ElseIf c >= 240 And c <= 244 Then
            falta = 3
        Else
            Exit Function
        End If
        For k = 1 To falta
            If i + k > n Then Exit Function
            If b(i + k) < 128 Or b(i + k) > 191 Then Exit Function
        Next k
        i = i + falta + 1
    Loop
    Utf8Valido = True
End Function

Private Function DetectarSeparador(ByVal t As String) As String
    Dim i As Long, ch As String, aspas As Boolean, pv As Long, tb As Long, vg As Long
    For i = 1 To Len(t)
        ch = Mid$(t, i, 1)
        If ch = """" Then
            aspas = Not aspas
        ElseIf Not aspas Then
            If ch = vbLf Or ch = vbCr Then Exit For
            If ch = ";" Then
                pv = pv + 1
            ElseIf ch = vbTab Then
                tb = tb + 1
            ElseIf ch = "," Then
                vg = vg + 1
            End If
        End If
    Next i
    If pv >= tb And pv >= vg And pv > 0 Then
        DetectarSeparador = ";"
    ElseIf tb >= vg And tb > 0 Then
        DetectarSeparador = vbTab
    Else
        DetectarSeparador = ","
    End If
End Function

Private Function SepCampo() As String
    SepCampo = Chr$(1)
End Function

Private Sub PCampo()
    mNc = mNc + 1
    If mNc = 1 Then
        ReDim mCur(1 To 8)
    ElseIf mNc > UBound(mCur) Then
        ReDim Preserve mCur(1 To UBound(mCur) * 2)
    End If
    mCur(mNc) = mBuf
    mBuf = ""
End Sub

Private Sub PLinha()
    Dim r() As String, j As Long
    PCampo
    If mNc = 1 And Len(Trim$(mCur(1))) = 0 Then
        mNc = 0
        Exit Sub
    End If
    ReDim r(1 To mNc)
    For j = 1 To mNc
        r(j) = mCur(j)
    Next j
    mLin.Add Join(r, SepCampo())   ' texto em vez de matriz: Collection de matrizes falha no LibreOffice
    If mNc > mMax Then mMax = mNc
    mNc = 0
End Sub

Private Function AnalisarCsv(ByVal t As String, ByVal d As String) As Variant
    Dim i As Long, n As Long, ch As String, aspas As Boolean
    Dim res() As Variant, r As Long, j As Long, lin As Variant
    Set mLin = New Collection
    mNc = 0: mBuf = "": mMax = 0
    n = Len(t)
    i = 1
    Do While i <= n
        ch = Mid$(t, i, 1)
        If aspas Then
            If ch = """" Then
                If Mid$(t, i + 1, 1) = """" Then
                    mBuf = mBuf & """"
                    i = i + 1
                Else
                    aspas = False
                End If
            Else
                mBuf = mBuf & ch
            End If
        ElseIf ch = """" Then
            aspas = True
        ElseIf ch = d Then
            PCampo
        ElseIf ch = vbCr Or ch = vbLf Then
            If ch = vbCr And Mid$(t, i + 1, 1) = vbLf Then i = i + 1
            PLinha
        Else
            mBuf = mBuf & ch
        End If
        i = i + 1
    Loop
    If Len(mBuf) > 0 Or mNc > 0 Then PLinha
    If mLin.Count = 0 Then Exit Function
    ReDim res(1 To mLin.Count, 1 To mMax)
    For r = 1 To mLin.Count
        lin = Split(CStr(mLin.Item(r)), SepCampo())
        For j = 0 To UBound(lin)
            res(r, j + 1) = lin(j)
        Next j
    Next r
    AnalisarCsv = res
End Function

'------------------------------------------------------------ papéis das colunas
Private Function NomesPapel() As Variant
    NomesPapel = Array("Código", "Data", "Categoria", "Valor", "Outro", "Ignorar")
End Function

Private Sub LimparCabecalho(ByRef t As Variant, ByVal nc As Long)
    Dim j As Long, s As String
    For j = 1 To nc
        s = ""
        If Not IsError(t(1, j)) Then s = CStr(t(1, j))
        s = Trim$(Replace(s, ChrW(65279), ""))
        If Len(s) = 0 Then s = "Coluna " & j
        t(1, j) = s
    Next j
End Sub

Private Function Assinatura(ByRef t As Variant, ByVal nc As Long) As String
    Dim j As Long, s As String
    For j = 1 To nc
        s = s & LCase$(CStr(t(1, j))) & "|"
    Next j
    Assinatura = s
End Function

Private Function PapelSugerido(ByVal nome As String, ByVal jaTemCodigo As Boolean) As Long
    Dim n As String
    n = LCase$(nome)
    PapelSugerido = 5
    If Not jaTemCodigo And (InStr(n, "cod") > 0 Or InStr(n, "cód") > 0 Or n = "id" Or InStr(n, "número") > 0 Or InStr(n, "numero") > 0 Or InStr(n, "protocolo") > 0) Then
        PapelSugerido = 1
    ElseIf InStr(n, "data") > 0 Or Left$(n, 3) = "dt " Or InStr(n, "date") > 0 Then
        PapelSugerido = 2
    ElseIf InStr(n, "valor") > 0 Or InStr(n, "preço") > 0 Or InStr(n, "preco") > 0 Or InStr(n, "total") > 0 Then
        PapelSugerido = 4
    ElseIf InStr(n, "cliente") > 0 Or InStr(n, "categ") > 0 Or InStr(n, "tipo") > 0 Or InStr(n, "situa") > 0 Or InStr(n, "regi") > 0 Or InStr(n, "status") > 0 Or InStr(n, "grupo") > 0 Then
        PapelSugerido = 3
    End If
End Function

Private Function ObterPapeis(ByRef t As Variant, ByVal nc As Long, ByRef pap() As String) As Boolean
    Dim ws As Worksheet, sig As String, ult As Long, r As Long, j As Long, dc As Object, ok As Boolean
    Dim nomes As Variant, sug As Long, resp As String, p As Long, tem As Boolean, ex As String, k As Long
    Set ws = Folha(SH_MEM)
    sig = Assinatura(t, nc)
    ReDim pap(1 To nc)
    Set dc = Dic()
    ult = ws.Cells(ws.Rows.Count, 1).End(xlUp).Row
    For r = 2 To ult
        If CStr(ws.Cells(r, 1).Value) = sig Then dc(CStr(ws.Cells(r, 2).Value)) = CStr(ws.Cells(r, 3).Value)
    Next r
    ok = (dc.Count > 0)
    For j = 1 To nc
        If Not dc.Exists(CStr(t(1, j))) Then ok = False
    Next j
    If ok Then
        For j = 1 To nc
            pap(j) = dc(CStr(t(1, j)))
        Next j
        ObterPapeis = True
        Exit Function
    End If
    If dc.Count > 0 Then EsquecerFormato sig
    nomes = NomesPapel()
    For j = 1 To nc
        sug = PapelSugerido(CStr(t(1, j)), tem)
        ex = ""
        For k = 2 To UBound(t, 1)
            If Not IsError(t(k, j)) Then
                If Len(CStr(t(k, j))) > 0 Then
                    ex = Left$(CStr(t(k, j)), 40)
                    Exit For
                End If
            End If
        Next k
        If mOficina Then
            resp = CStr(sug)
        Else
            resp = InputBox("Coluna: " & CStr(t(1, j)) & vbCrLf & "Exemplo: " & ex & vbCrLf & vbCrLf & _
                "1 = Código (identifica o registro)" & vbCrLf & "2 = Data" & vbCrLf & "3 = Categoria (texto para agrupar)" & vbCrLf & _
                "4 = Valor (número)" & vbCrLf & "5 = Outro (texto)" & vbCrLf & "6 = Ignorar esta coluna" & vbCrLf & vbCrLf & _
                "Digite o número e confirme (Cancelar para parar este arquivo).", "Esta coluna é o quê?", CStr(sug))
        End If
        If Not mOficina Then If StrPtr(resp) = 0 Then Exit Function
        p = CLng(Val(resp))
        If p < 1 Or p > 6 Then p = sug
        If p = 1 And tem Then p = 5
        If p = 1 Then tem = True
        pap(j) = nomes(p - 1)
    Next j
    If Not tem Then
        Msg "É preciso indicar uma coluna de Código para juntar os registros. Este arquivo não foi importado.", vbExclamation, "Esta coluna é o quê?"
        Exit Function
    End If
    r = ult + 1
    For j = 1 To nc
        ws.Cells(r, 1).Value = sig
        ws.Cells(r, 2).Value = CStr(t(1, j))
        ws.Cells(r, 3).Value = pap(j)
        r = r + 1
    Next j
    ObterPapeis = True
End Function

Private Sub EsquecerFormato(ByVal sig As String)
    Dim ws As Worksheet, r As Long
    Set ws = Folha(SH_MEM)
    For r = ws.Cells(ws.Rows.Count, 1).End(xlUp).Row To 2 Step -1
        If CStr(ws.Cells(r, 1).Value) = sig Then ws.Rows(r).Delete
    Next r
End Sub

Public Sub EsquecerFormatos()
    Dim ws As Worksheet
    If Not Pronto() Then Exit Sub
    If Msg("Esquecer o que cada coluna significa? Será perguntado de novo no próximo arquivo.", vbYesNo + vbQuestion, "Formatos lembrados") <> vbYes Then Exit Sub
    Set ws = Folha(SH_MEM)
    ws.Range("A2:C" & ws.Rows.Count).ClearContents
End Sub

Private Function PapelDoCampo(ByVal nome As String) As String
    Dim ws As Worksheet, r As Long
    If StrComp(nome, COD, vbTextCompare) = 0 Then
        PapelDoCampo = COD
        Exit Function
    End If
    Set ws = Folha(SH_MEM)
    For r = 2 To ws.Cells(ws.Rows.Count, 1).End(xlUp).Row
        If StrComp(CStr(ws.Cells(r, 2).Value), nome, vbTextCompare) = 0 Then
            PapelDoCampo = CStr(ws.Cells(r, 3).Value)
            Exit Function
        End If
    Next r
End Function

'------------------------------------------------------------ junção por código
Private Function Incorporar(ByRef tbl As Variant) As Long
    Dim nl As Long, nc As Long, j As Long, r As Long, pap() As String
    Dim d As Variant, nr As Long, ncd As Long, nd() As Variant, cap As Long
    Dim mapa() As Long, cCod As Long, dc As Object, dr As Object, nome As String
    Dim lin As Long, chave As String, v As Variant, saida As Variant
    nl = UBound(tbl, 1): nc = UBound(tbl, 2)
    If nl < 2 Then Exit Function
    LimparCabecalho tbl, nc
    If Not ObterPapeis(tbl, nc, pap) Then Exit Function
    For j = 1 To nc
        If pap(j) = COD And cCod = 0 Then cCod = j
    Next j
    LerDados d, nr, ncd
    cap = nr + nl
    ReDim nd(1 To cap, 1 To ncd + nc)
    For r = 1 To nr
        For j = 1 To ncd
            nd(r, j) = d(r, j)
        Next j
    Next r
    Set dc = Dic()
    For j = 1 To ncd
        dc(CStr(nd(1, j))) = j
    Next j
    ReDim mapa(1 To nc)
    For j = 1 To nc
        If j <> cCod And pap(j) <> "Ignorar" Then
            nome = CStr(tbl(1, j))
            If Not dc.Exists(nome) Then
                ncd = ncd + 1
                nd(1, ncd) = nome
                dc(nome) = ncd
            End If
            mapa(j) = dc(nome)
            If mapa(j) = 1 Then mapa(j) = 0
        End If
    Next j
    Set dr = Dic()
    For r = 2 To nr
        dr(CStr(nd(r, 1))) = r
    Next r
    For r = 2 To nl
        If IsError(tbl(r, cCod)) Then
            chave = ""
        Else
            chave = Trim$(CStr(tbl(r, cCod)))
        End If
        If Len(chave) > 0 Then
            gLidos = gLidos + 1
            If dr.Exists(chave) Then
                lin = dr(chave)
                gAtualizados = gAtualizados + 1
            Else
                nr = nr + 1
                lin = nr
                nd(lin, 1) = chave
                dr(chave) = lin
                gNovos = gNovos + 1
            End If
            For j = 1 To nc
                If mapa(j) > 0 Then
                    v = ConverterValor(tbl(r, j), pap(j))
                    If Not IsEmpty(v) Then nd(lin, mapa(j)) = v
                End If
            Next j
        End If
    Next r
    saida = Aparar(nd, nr, ncd)
    EscreverDados saida, nr, ncd
    Incorporar = nl - 1
End Function

Private Function Aparar(ByRef nd() As Variant, ByVal nr As Long, ByVal nc As Long) As Variant
    Dim o() As Variant, r As Long, j As Long
    ReDim o(1 To nr, 1 To nc)
    For r = 1 To nr
        For j = 1 To nc
            o(r, j) = nd(r, j)
        Next j
    Next r
    Aparar = o
End Function

Private Sub LerDados(ByRef d As Variant, ByRef nr As Long, ByRef nc As Long)
    Dim ws As Worksheet, rg As Range
    Set ws = Folha(SH_DADOS)
    If Len(CStr(ws.Range("A1").Value)) = 0 Then ws.Range("A1").Value = COD
    Set rg = ws.Range("A1").CurrentRegion
    nr = rg.Rows.Count
    nc = rg.Columns.Count
    If rg.Cells.Count = 1 Then
        ReDim d(1 To 1, 1 To 1)
        d(1, 1) = rg.Value
    Else
        d = rg.Value
    End If
End Sub

Private Sub EscreverDados(ByRef d As Variant, ByVal nr As Long, ByVal nc As Long)
    Dim ws As Worksheet
    Set ws = Folha(SH_DADOS)
    ws.Cells.Clear
    FormatarColunas ws, d, nc
    ws.Range(ws.Cells(1, 1), ws.Cells(nr, nc)).Value = d
    ws.Range(ws.Cells(1, 1), ws.Cells(1, nc)).Font.Bold = True
    ws.Range(ws.Cells(1, 1), ws.Cells(1, nc)).Interior.Color = RGB(221, 235, 247)
    ws.Range(ws.Cells(1, 1), ws.Cells(nr, nc)).Columns.AutoFit
End Sub

Private Sub FormatarColunas(ByVal ws As Worksheet, ByRef d As Variant, ByVal nc As Long)
    Dim j As Long
    For j = 1 To nc
        Select Case PapelDoCampo(CStr(d(1, j)))
            Case "Data": ws.Columns(j).NumberFormat = "dd/mm/yyyy"
            Case "Valor": ws.Columns(j).NumberFormat = "#,##0.00"
            Case COD, "Categoria", "Outro": ws.Columns(j).NumberFormat = "@"
        End Select
    Next j
End Sub

Public Sub ApagarDados()
    Dim ws As Worksheet
    If Not Pronto() Then Exit Sub
    If Msg("Apagar todos os registros importados?", vbYesNo + vbExclamation, "Apagar todos os dados") <> vbYes Then Exit Sub
    Set ws = Folha(SH_DADOS)
    ws.Cells.Clear
    MontarDados
    AtualizarPainel
End Sub

'------------------------------------------------------------ conversões
Private Function ConverterValor(ByVal v As Variant, ByVal papel As String) As Variant
    Dim s As String, p As Variant
    If IsError(v) Or IsEmpty(v) Then Exit Function
    Select Case papel
        Case "Data"
            If VarType(v) = vbDate Then
                ConverterValor = Int(CDate(v))
            ElseIf VarType(v) = vbString Then
                s = Trim$(CStr(v))
                If Len(s) = 0 Then Exit Function
                p = ParseData(s)
                If IsEmpty(p) Then ConverterValor = s Else ConverterValor = p
            ElseIf IsNumeric(v) Then
                ConverterValor = Int(CDate(CDbl(v)))
            End If
        Case "Valor"
            If VarType(v) = vbString Then
                s = Trim$(CStr(v))
                If Len(s) = 0 Then Exit Function
                p = ParseNumero(s)
                If IsEmpty(p) Then ConverterValor = s Else ConverterValor = p
            ElseIf IsNumeric(v) Then
                ConverterValor = CDbl(v)
            End If
        Case Else
            If VarType(v) = vbDate Then
                ConverterValor = Format$(v, "dd/mm/yyyy")
            Else
                s = Trim$(CStr(v))
                If Len(s) > 0 Then ConverterValor = s
            End If
    End Select
End Function

Private Function ParseData(ByVal s As String) As Variant
    Dim p As Long, a() As String, y As Long, m As Long, d As Long, i As Long
    p = InStr(s, " ")
    If p > 0 Then s = Left$(s, p - 1)
    p = InStr(s, "T")
    If p > 0 Then s = Left$(s, p - 1)
    s = Replace(Replace(s, "-", "/"), ".", "/")
    a = Split(s, "/")
    If UBound(a) <> 2 Then Exit Function
    For i = 0 To 2
        If Len(a(i)) = 0 Or Not IsNumeric(a(i)) Then Exit Function
    Next i
    If Len(a(0)) = 4 Then
        y = CLng(a(0)): m = CLng(a(1)): d = CLng(a(2))
    Else
        d = CLng(a(0)): m = CLng(a(1)): y = CLng(a(2))
    End If
    If y < 100 Then y = y + 2000
    If m < 1 Or m > 12 Or d < 1 Or d > 31 Or y < 1900 Or y > 2200 Then Exit Function
    If Day(DateSerial(y, m, d)) <> d Then Exit Function
    ParseData = CDate(DateSerial(y, m, d))
End Function

Private Function ParseNumero(ByVal s As String) As Variant
    Dim i As Long, ch As String, lv As Long, lp As Long, neg As Boolean
    s = Replace(Replace(Replace(s, " ", ""), ChrW(160), ""), "R$", "")
    If Len(s) = 0 Then Exit Function
    If Left$(s, 1) = "-" Then
        neg = True
        s = Mid$(s, 2)
    End If
    For i = 1 To Len(s)
        ch = Mid$(s, i, 1)
        If InStr("0123456789.,", ch) = 0 Then Exit Function
    Next i
    lv = InStrRev(s, ",")
    lp = InStrRev(s, ".")
    If lv > 0 And lp > 0 Then
        If lv > lp Then
            s = Replace(s, ".", "")
            s = Replace(s, ",", ".")
        Else
            s = Replace(s, ",", "")
        End If
    ElseIf lv > 0 Then
        If lv <> InStr(s, ",") Then Exit Function
        s = Replace(s, ",", ".")
    ElseIf lp > 0 Then
        If lp <> InStr(s, ".") Then s = Replace(s, ".", "")
    End If
    If neg Then ParseNumero = -Val(s) Else ParseNumero = Val(s)
End Function

'------------------------------------------------------------ painel
Private Function IndiceCampo(ByRef d As Variant, ByVal nc As Long, ByVal nome As String) As Long
    Dim j As Long
    If Len(nome) = 0 Then Exit Function
    For j = 1 To nc
        If StrComp(CStr(d(1, j)), nome, vbTextCompare) = 0 Then
            IndiceCampo = j
            Exit Function
        End If
    Next j
End Function

Private Function NomeCampo(ByRef d As Variant, ByVal idx As Long, ByVal padrao As String) As String
    If idx > 0 Then NomeCampo = CStr(d(1, idx)) Else NomeCampo = padrao
End Function

Private Function PrimeiroDoPapel(ByRef d As Variant, ByVal nc As Long, ByVal papel As String) As String
    Dim j As Long
    For j = 2 To nc
        If PapelDoCampo(CStr(d(1, j))) = papel Then
            PrimeiroDoPapel = CStr(d(1, j))
            Exit Function
        End If
    Next j
End Function

Private Function DataCel(ByVal c As Range, ByRef saida As Date) As Boolean
    Dim p As Variant
    If IsEmpty(c.Value) Then Exit Function
    If IsDate(c.Value) Then
        saida = Int(CDate(c.Value))
        DataCel = True
    Else
        p = ParseData(CStr(c.Value))
        If Not IsEmpty(p) Then
            saida = CDate(p)
            DataCel = True
        End If
    End If
End Function

Private Function Selecionar(ByRef d As Variant, ByVal nr As Long, ByVal ic As Long, ByVal idt As Long, ByRef sel() As Long) As Long
    Dim ws As Worksheet, de As Date, ate As Date, temDe As Boolean, temAte As Boolean
    Dim fcat As String, r As Long, n As Long, v As Variant, ok As Boolean
    Set ws = Folha(SH_PAINEL)
    temDe = DataCel(ws.Range("B7"), de)
    temAte = DataCel(ws.Range("D7"), ate)
    fcat = CStr(ws.Range("B10").Value)
    If fcat = TODAS Then fcat = ""
    ReDim sel(1 To nr)
    For r = 2 To nr
        ok = True
        If idt > 0 And (temDe Or temAte) Then
            v = d(r, idt)
            If VarType(v) <> vbDate Then
                ok = False
            Else
                If temDe And Int(CDate(v)) < de Then ok = False
                If temAte And Int(CDate(v)) > ate Then ok = False
            End If
        End If
        If ok And ic > 0 And Len(fcat) > 0 Then
            If CStr(d(r, ic)) <> fcat Then ok = False
        End If
        If ok Then
            n = n + 1
            sel(n) = r
        End If
    Next r
    Selecionar = n
End Function

Private Sub PrepararCampos(ByRef d As Variant, ByVal nc As Long, ByRef ic As Long, ByRef idt As Long)
    Dim ws As Worksheet, s As String
    Set ws = Folha(SH_PAINEL)
    If IndiceCampo(d, nc, CStr(ws.Range("B9").Value)) = 0 Then
        s = PrimeiroDoPapel(d, nc, "Categoria")
        If Len(s) = 0 And nc >= 2 Then s = CStr(d(1, 2))
        ws.Range("B9").Value = s
    End If
    If IndiceCampo(d, nc, CStr(ws.Range("B8").Value)) = 0 Then ws.Range("B8").Value = PrimeiroDoPapel(d, nc, "Data")
    ic = IndiceCampo(d, nc, CStr(ws.Range("B9").Value))
    idt = IndiceCampo(d, nc, CStr(ws.Range("B8").Value))
End Sub

Private Sub AtualizarListas(ByRef d As Variant, ByVal nr As Long, ByVal nc As Long, ByVal ic As Long)
    Dim ws As Worksheet, j As Long, r As Long, dc As Object, k() As String, n As Long, ult As Long
    Set ws = Folha(SH_MEM)
    ws.Range("E2:E300").ClearContents
    ws.Range("G2:G5000").ClearContents
    For j = 2 To nc
        If j - 1 <= 299 Then ws.Cells(j, 5).Value = CStr(d(1, j))
    Next j
    If ic = 0 Then Exit Sub
    Set dc = Dic()
    For r = 2 To nr
        If Len(CStr(d(r, ic))) > 0 Then dc(CStr(d(r, ic))) = 1
    Next r
    n = dc.Count
    ws.Cells(2, 7).Value = TODAS
    If n = 0 Then Exit Sub
    ReDim k(1 To n)
    j = 0
    Dim ch As Variant
    For Each ch In dc.Keys
        j = j + 1
        k(j) = CStr(ch)
    Next ch
    OrdenarTexto k, n
    If n > 4990 Then n = 4990
    For j = 1 To n
        ws.Cells(j + 2, 7).NumberFormat = "@"
        ws.Cells(j + 2, 7).Value = k(j)
    Next j
End Sub

Private Sub OrdenarTexto(ByRef a() As String, ByVal n As Long)
    Dim i As Long, j As Long, t As String
    For i = 2 To n
        t = a(i)
        j = i - 1
        Do While j >= 1
            If StrComp(a(j), t, vbTextCompare) <= 0 Then Exit Do
            a(j + 1) = a(j)
            j = j - 1
        Loop
        a(j + 1) = t
    Next i
End Sub

Private Sub OrdenarContagem(ByRef k() As String, ByRef c() As Long, ByVal n As Long)
    Dim i As Long, j As Long, tk As String, tc As Long
    For i = 2 To n
        tk = k(i): tc = c(i)
        j = i - 1
        Do While j >= 1
            If c(j) > tc Or (c(j) = tc And StrComp(k(j), tk, vbTextCompare) <= 0) Then Exit Do
            k(j + 1) = k(j): c(j + 1) = c(j)
            j = j - 1
        Loop
        k(j + 1) = tk: c(j + 1) = tc
    Next i
End Sub

Private Sub ContarPorCategoria(ByRef d As Variant, ByRef sel() As Long, ByVal n As Long, ByVal ic As Long, ByRef k() As String, ByRef c() As Long, ByRef nk As Long)
    Dim dc As Object, i As Long, s As String, ch As Variant
    Set dc = Dic()
    nk = 0
    If ic = 0 Or n = 0 Then Exit Sub
    For i = 1 To n
        s = CStr(d(sel(i), ic))
        If Len(s) = 0 Then s = "(vazio)"
        dc(s) = dc(s) + 1
    Next i
    nk = dc.Count
    ReDim k(1 To nk)
    ReDim c(1 To nk)
    i = 0
    For Each ch In dc.Keys
        i = i + 1
        k(i) = CStr(ch)
        c(i) = dc(ch)
    Next ch
    OrdenarContagem k, c, nk
End Sub

Public Sub AtualizarPainel()
    Dim ws As Worksheet, d As Variant, nr As Long, nc As Long, ic As Long, idt As Long
    Dim sel() As Long, n As Long, k() As String, c() As Long, nk As Long, i As Long, sai() As Variant
    If Not Pronto() Then Exit Sub
    Set ws = Folha(SH_PAINEL)
    LerDados d, nr, nc
    PrepararCampos d, nc, ic, idt
    AtualizarListas d, nr, nc, ic
    n = Selecionar(d, nr, ic, idt, sel)
    ContarPorCategoria d, sel, n, ic, k, c, nk
    ws.Range("A2").Value = TextoCliente()
    ws.Range("B12").Value = n
    ws.Range("A14:C3000").Clear
    ws.Range("A14").Value = "Por " & NomeCampo(d, ic, "categoria (escolha o campo em B9)")
    ws.Range("B14").Value = "Registros"
    ws.Range("A14:B14").Font.Bold = True
    ws.Range("A14:B14").Interior.Color = RGB(221, 235, 247)
    If nk > 0 Then
        ReDim sai(1 To nk, 1 To 2)
        For i = 1 To nk
            sai(i, 1) = k(i)
            sai(i, 2) = c(i)
        Next i
        ws.Range(ws.Cells(15, 1), ws.Cells(14 + nk, 1)).NumberFormat = "@"
        ws.Range(ws.Cells(15, 1), ws.Cells(14 + nk, 2)).Value = sai
        ws.Range(ws.Cells(15, 2), ws.Cells(14 + nk, 2)).NumberFormat = "#,##0"
        If Not mOficina Then ws.Range(ws.Cells(15, 2), ws.Cells(14 + nk, 2)).FormatConditions.AddDatabar   ' LibreOffice nao tem barras de dados via VBA
    End If
End Sub

Private Function TextoCliente() As String
    Dim c As String, a As String
    c = Trim$(CStr(Folha(SH_CONFIG).Range("B3").Value))
    a = Trim$(CStr(Folha(SH_CONFIG).Range("B4").Value))
    If Len(c) = 0 Then c = "(cliente não informado na aba Config)"
    TextoCliente = c
    If Len(a) > 0 Then TextoCliente = c & " - " & a
End Function

'------------------------------------------------------------ relatório
Public Sub GerarRelatorio()
    Dim d As Variant, nr As Long, nc As Long, ic As Long, idt As Long, sel() As Long, n As Long
    Dim k() As String, c() As Long, nk As Long, wb As Workbook, ws As Worksheet, i As Long, j As Long
    Dim sai() As Variant, cfg As Worksheet, pn As Worksheet, per As String, fil As String, cam As Variant
    Dim de As Date, ate As Date, temDe As Boolean, temAte As Boolean
    If Not Pronto() Then Exit Sub
    On Error GoTo falha
    AtualizarPainel
    Set cfg = Folha(SH_CONFIG)
    Set pn = Folha(SH_PAINEL)
    LerDados d, nr, nc
    PrepararCampos d, nc, ic, idt
    n = Selecionar(d, nr, ic, idt, sel)
    If n = 0 Then
        Msg "Não há registros com os filtros atuais.", vbInformation, "Gerar relatório"
        Exit Sub
    End If
    ContarPorCategoria d, sel, n, ic, k, c, nk
    temDe = DataCel(pn.Range("B7"), de)
    temAte = DataCel(pn.Range("D7"), ate)
    If temDe And temAte Then
        per = Format$(de, "dd/mm/yyyy") & " a " & Format$(ate, "dd/mm/yyyy")
    ElseIf temDe Then
        per = "a partir de " & Format$(de, "dd/mm/yyyy")
    ElseIf temAte Then
        per = "até " & Format$(ate, "dd/mm/yyyy")
    Else
        per = "todo o período"
    End If
    fil = "Campo de data: " & NomeCampo(d, idt, "(nenhum)") & vbLf & "Campo categoria: " & NomeCampo(d, ic, "(nenhum)") & vbLf & _
          "Categoria: " & IIf(Len(CStr(pn.Range("B10").Value)) = 0, TODAS, CStr(pn.Range("B10").Value))
    Application.ScreenUpdating = False
    Set wb = Workbooks.Add(xlWBATWorksheet)
    Set ws = wb.Worksheets(1)
    ws.Name = "Capa"
    ws.Range("A1").Value = "Relatório"
    ws.Range("A1").Font.Size = 24
    ws.Range("A1").Font.Bold = True
    ws.Range("A3").Value = "Cliente"
    ws.Range("B3").Value = Trim$(CStr(cfg.Range("B3").Value))
    ws.Range("A4").Value = "Área"
    ws.Range("B4").Value = Trim$(CStr(cfg.Range("B4").Value))
    ws.Range("A5").Value = "Período"
    ws.Range("B5").Value = per
    ws.Range("A6").Value = "Filtros"
    ws.Range("B6").NumberFormat = "@"
    ws.Range("B6").Value = fil
    ws.Range("A7").Value = "Total de registros"
    ws.Range("B7").Value = n
    ws.Range("A8").Value = "Gerado em"
    ws.Range("B8").NumberFormat = "@"
    ws.Range("B8").Value = Format$(Now, "dd/mm/yyyy hh:nn")
    ws.Range("A3:A8").Font.Bold = True
    ws.Range("B3:B8").HorizontalAlignment = xlLeft
    ws.Range("B6").WrapText = True
    ws.Columns("A").ColumnWidth = 20
    ws.Columns("B").ColumnWidth = 50
    Set ws = wb.Worksheets.Add(After:=wb.Worksheets(wb.Worksheets.Count))
    ws.Name = "Resumo"
    ws.Range("A1").Value = "Resumo por " & NomeCampo(d, ic, "categoria")
    ws.Range("A1").Font.Bold = True
    ws.Range("A1").Font.Size = 14
    ws.Range("A3").Value = NomeCampo(d, ic, "Categoria")
    ws.Range("B3").Value = "Registros"
    ws.Range("A3:B3").Font.Bold = True
    ws.Range("A3:B3").Interior.Color = RGB(221, 235, 247)
    If nk > 0 Then
        ReDim sai(1 To nk, 1 To 2)
        For i = 1 To nk
            sai(i, 1) = k(i)
            sai(i, 2) = c(i)
        Next i
        ws.Range(ws.Cells(4, 1), ws.Cells(3 + nk, 1)).NumberFormat = "@"
        ws.Range(ws.Cells(4, 1), ws.Cells(3 + nk, 2)).Value = sai
    End If
    ws.Cells(4 + nk, 1).Value = "Total"
    ws.Cells(4 + nk, 2).Value = n
    ws.Range(ws.Cells(4 + nk, 1), ws.Cells(4 + nk, 2)).Font.Bold = True
    ws.Columns("A").ColumnWidth = 32
    ws.Columns("B").ColumnWidth = 14
    Set ws = wb.Worksheets.Add(After:=wb.Worksheets(wb.Worksheets.Count))
    ws.Name = "Registros"
    ReDim sai(1 To n + 1, 1 To nc)
    For j = 1 To nc
        sai(1, j) = d(1, j)
    Next j
    For i = 1 To n
        For j = 1 To nc
            sai(i + 1, j) = d(sel(i), j)
        Next j
    Next i
    FormatarColunas ws, d, nc
    ws.Range(ws.Cells(1, 1), ws.Cells(n + 1, nc)).Value = sai
    ws.Range(ws.Cells(1, 1), ws.Cells(1, nc)).Font.Bold = True
    ws.Range(ws.Cells(1, 1), ws.Cells(1, nc)).Interior.Color = RGB(221, 235, 247)
    ws.Range(ws.Cells(1, 1), ws.Cells(n + 1, nc)).Columns.AutoFit
    wb.Worksheets("Capa").Activate
    Application.ScreenUpdating = True
    If mOficina Then
        cam = mSaidaOficina
    Else
    cam = Application.GetSaveAsFilename("Relatorio_" & Format$(Date, "yyyy-mm-dd") & ".xlsx", "Pasta de trabalho do Excel (*.xlsx),*.xlsx", , "Salvar relatório")
    End If
    If VarType(cam) = vbBoolean Then
        Msg "O relatório está aberto, mas não foi salvo. Use Arquivo > Salvar como.", vbInformation, "Gerar relatório"
    ElseIf mOficina Then
        Msg "Relatório pronto (oficina: quem chamou salva o arquivo em " & CStr(cam) & ")", vbInformation, "Gerar relatório"
    Else
        Application.DisplayAlerts = False
        wb.SaveAs CStr(cam), 51
        Application.DisplayAlerts = True
        Msg "Relatório salvo em:" & vbCrLf & CStr(cam), vbInformation, "Gerar relatório"
    End If
    Exit Sub
falha:
    Application.ScreenUpdating = True
    Application.DisplayAlerts = True
    Msg "Não consegui gerar o relatório: " & Err.Description, vbExclamation, "Gerar relatório"
End Sub
