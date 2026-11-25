Attribute VB_Name = "GeradorOS"
'==========================================================================
' Gerador de Relatórios de OS - HEV  (Excel 2016 ou mais novo)
' Lê os CSVs do relatório R_ORDEM_SERVICO do MV (um por fila) e monta:
' Dashboard (indicadores, filtros, gráficos e lista de OS), Backlog,
' Equipe (homem-hora), Tempos, Para arrumar (erros e OS repetidas) e Histórico do backlog.
' Macros principais: Instalar  |  ImportarCSVs  |  RegistrarBacklog  |  GerarRelatorio
'==========================================================================
Option Explicit

Private Const SH_DASH As String = "Dashboard"
Private Const SH_BL As String = "Backlog"
Private Const SH_EQ As String = "Equipe"
Private Const SH_TP As String = "Tempos"
Private Const SH_ERR As String = "Para arrumar"
Private Const SH_CFG As String = "Config"
Private Const SH_CALC As String = "Calc"
Private Const SH_HIST As String = "Histórico"
Private Const SH_ARQ As String = "Arquivos"
Private Const SH_REP As String = "Repetidas"
Private Const NCOL As Long = 27
Private Const INI As String = ",tbOS[Pedido],"">=""&N(DataIni)"

Private gLabels As Object
Private gDePara As Object
Private gGenericos As Collection
Private gMaxExec As Double
Private gLog As Collection
Private gRegras As Collection

'------------------------------------------------------------ instalação
Public Sub Instalar()
    Application.ScreenUpdating = False
    GarantirConfig
    GarantirHistorico
    Dim ws As Worksheet
    Set ws = PegarOuCriar(SH_DASH, 1)
    If ws.ListObjects.Count = 0 Then
        ws.Cells.Clear
        ws.Range("A1").Value = "Gerador de OS - HEV"
        ws.Range("A1").Font.Size = 22: ws.Range("A1").Font.Bold = True
        ws.Range("A3").Value = "Clique em 'Importar CSVs do MV' e selecione TODOS os CSVs do período de uma vez (um por fila)."
    End If
    BotaoImportar ws
    ws.Activate
    Application.ScreenUpdating = True
    MsgBox "Pronto. Agora clique em 'Importar CSVs do MV' na aba Dashboard.", vbInformation, "Gerador de OS"
End Sub

Private Sub BotaoImportar(ws As Worksheet)
    Dim b As Object
    On Error Resume Next
    ws.Buttons("btnImportar").Delete
    On Error GoTo 0
    Set b = ws.Buttons.Add(ws.Range("H1").Left, 4, 190, 30)
    b.Name = "btnImportar"
    b.Caption = "Importar CSVs do MV"
    b.OnAction = "ImportarCSVs"
End Sub

'------------------------------------------------------------ importação
Public Sub ImportarCSVs()
    Dim fd As Object, i As Long, recs As Object, nArq As Long, nVazios As Long
    Set fd = Application.FileDialog(3) 'msoFileDialogFilePicker
    With fd
        .AllowMultiSelect = True
        .Title = "Selecione TODOS os CSVs do MV (um por fila) ou um .zip com todos dentro"
        .Filters.Clear
        .Filters.Add "CSV do MV ou .zip", "*.csv;*.txt;*.zip"
        If .Show <> -1 Then Exit Sub
    End With

    On Error GoTo Falha
    Application.ScreenUpdating = False
    Application.Calculation = xlCalculationManual
    Application.StatusBar = "Lendo arquivos..."

    GarantirConfig
    GarantirHistorico
    LerConfig
    IniciarLabels

    Set recs = CreateObject("Scripting.Dictionary")
    Set gLog = New Collection
    Dim caminhos As Collection, cam As Variant
    Dim txt As String, nLidas As Long, st As String, msg As String
    Dim wsCfg As Worksheet, rr As Long, vistos As Object, chave As String, nDup As Long
    Set caminhos = New Collection
    Set vistos = CreateObject("Scripting.Dictionary")
    Set wsCfg = ThisWorkbook.Worksheets(SH_CFG)
    ' fontes = arquivos/zips escolhidos agora + (se adicionar) os que já estavam carregados
    Dim fontes As Collection, fpath As Variant
    Set fontes = New Collection
    If wsCfg.Range("H4").Value <> "" Then
        If MsgBox("Já existem arquivos carregados." & vbCrLf & vbCrLf & _
            "Sim = ADICIONAR os novos aos que já estão" & vbCrLf & "Não = começar do zero", _
            vbYesNo + vbQuestion, "Gerador de OS") = vbYes Then
            rr = 4
            Do While wsCfg.Cells(rr, 8).Value <> ""
                If Dir(CStr(wsCfg.Cells(rr, 8).Value)) <> "" Then AddUnico fontes, CStr(wsCfg.Cells(rr, 8).Value)
                rr = rr + 1
            Loop
        End If
    End If
    For i = 1 To fd.SelectedItems.Count
        AddUnico fontes, CStr(fd.SelectedItems(i))
    Next i
    wsCfg.Range("H3").Value = "Arquivos carregados (não apague; use Importar para trocar)"
    wsCfg.Range("H4:H1000").ClearContents
    rr = 4
    For Each fpath In fontes
        wsCfg.Cells(rr, 8).Value = fpath: rr = rr + 1
        If LCase$(Right$(fpath, 4)) = ".zip" Then
            Application.StatusBar = "Abrindo .zip: " & NomeArquivo(CStr(fpath)) & "..."
            DoEvents
            ExtrairZip CStr(fpath), caminhos
        Else
            caminhos.Add CStr(fpath)
        End If
    Next fpath
    Dim kArq As Long
    For Each cam In caminhos
        kArq = kArq + 1
        chave = LCase$(NomeArquivo(CStr(cam))) & "|" & FileLen(CStr(cam))
        If vistos.Exists(chave) Then nDup = nDup + 1: GoTo Proximo
        vistos(chave) = True
        Application.StatusBar = "Carregando " & Format(kArq / (caminhos.Count + 1), "0%") & " - lendo arquivo " & kArq & " de " & caminhos.Count & ": " & NomeArquivo(CStr(cam)) & " (" & Format(FileLen(CStr(cam)) / 1024, "0") & " KB)..."
        DoEvents
        txt = "": nLidas = 0: msg = ""
        On Error Resume Next
        txt = LerTexto(CStr(cam))
        If Err.Number <> 0 Then msg = "não foi possível ler o arquivo"
        Err.Clear
        On Error GoTo Falha
        If msg = "" Then nLidas = LerMV(ParseCSV(txt), NomeArquivo(CStr(cam)), recs)
        If nLidas > 0 Then
            st = "OK"
        ElseIf msg = "" And InStr(1, Left$(txt, 3000), "Ordem de Servi", vbTextCompare) > 0 Then
            st = "VAZIO": msg = "fila vazia no MV": nVazios = nVazios + 1
        Else
            st = "ERRO"
            If msg = "" Then msg = "não parece um relatório R_ORDEM_SERVICO"
        End If
        gLog.Add Array(NomeArquivo(CStr(cam)), st, nLidas, msg, FileLen(CStr(cam)))
        nArq = nArq + 1
Proximo:
    Next cam
    If nDup > 0 Then Application.StatusBar = nDup & " arquivo(s) repetido(s) ignorado(s).

    Application.StatusBar = "Carregando 95% - montando relatórios (" & recs.Count & " OS)..."
    DoEvents
    Montar recs, nArq, nVazios

    Application.Calculation = xlCalculationAutomatic
    Application.StatusBar = False
    Application.ScreenUpdating = True
    ThisWorkbook.Worksheets(SH_DASH).Activate
    MsgBox ThisWorkbook.Worksheets(SH_DASH).Range("A2").Value, vbInformation, "Importação concluída"
    Exit Sub
Falha:
    Application.Calculation = xlCalculationAutomatic
    Application.StatusBar = False
    Application.ScreenUpdating = True
    MsgBox "Erro ao importar: " & Err.Description, vbExclamation, "Gerador de OS"
End Sub

Private Sub AddUnico(c As Collection, ByVal v As String)
    Dim x As Variant
    For Each x In c
        If LCase$(x) = LCase$(v) Then Exit Sub
    Next x
    c.Add v
End Sub

'------------------------------------------------------------ leitura do arquivo
Private Function LerTexto(caminho As String) As String
    Dim st As Object, t As String
    Set st = CreateObject("ADODB.Stream")
    st.Type = 2: st.Charset = "utf-8": st.Open
    st.LoadFromFile caminho
    t = st.ReadText
    st.Close
    If InStr(1, t, ChrW(&HFFFD)) > 0 Or (InStr(1, t, "Situa") > 0 And InStr(1, t, "Situação") = 0) Then
        st.Type = 2: st.Charset = "windows-1252": st.Open
        st.LoadFromFile caminho
        t = st.ReadText
        st.Close
    End If
    If Len(t) > 0 Then
        If AscW(Left$(t, 1)) = &HFEFF Then t = Mid$(t, 2)
    End If
    LerTexto = t
End Function

Private Function NomeArquivo(p As String) As String
    NomeArquivo = Mid$(p, InStrRev(p, "\") + 1)
End Function

Private Function ParseCSV(txt As String) As Collection
    Dim rows As New Collection, cells() As String, nc As Long
    Dim i As Long, n As Long, c As String, cell As String, q As Boolean, sep As String
    Dim primeira As String, p As Long
    p = InStr(1, txt, vbLf): If p = 0 Then p = Len(txt)
    primeira = Left$(txt, p)
    sep = ","
    If Len(primeira) - Len(Replace(primeira, ";", "")) > Len(primeira) - Len(Replace(primeira, ",", "")) Then sep = ";"
    n = Len(txt)
    ReDim cells(0 To 63): nc = 0
    For i = 1 To n
        c = Mid$(txt, i, 1)
        If q Then
            If c = """" Then
                If Mid$(txt, i + 1, 1) = """" Then cell = cell & """": i = i + 1 Else q = False
            Else
                cell = cell & c
            End If
        ElseIf c = """" Then
            q = True
        ElseIf c = sep Then
            If nc > UBound(cells) Then ReDim Preserve cells(0 To nc * 2)
            cells(nc) = cell: nc = nc + 1: cell = ""
        ElseIf c = vbLf Then
            If nc > UBound(cells) Then ReDim Preserve cells(0 To nc * 2)
            cells(nc) = cell: nc = nc + 1: cell = ""
            rows.Add FecharLinha(cells, nc)
            ReDim cells(0 To 63): nc = 0
        ElseIf c <> vbCr Then
            cell = cell & c
        End If
    Next i
    If cell <> "" Or nc > 0 Then
        If nc > UBound(cells) Then ReDim Preserve cells(0 To nc * 2)
        cells(nc) = cell: nc = nc + 1
        rows.Add FecharLinha(cells, nc)
    End If
    Set ParseCSV = rows
End Function

Private Function FecharLinha(cells() As String, nc As Long) As Variant
    Dim a() As String, k As Long
    ReDim a(0 To nc - 1)
    For k = 0 To nc - 1: a(k) = cells(k): Next k
    FecharLinha = a
End Function

'------------------------------------------------------------ interpretação dos blocos do MV
Private Sub IniciarLabels()
    Set gLabels = CreateObject("Scripting.Dictionary")
    gLabels("situação") = "situacao": gLabels("situacao") = "situacao"
    gLabels("tipo") = "tipo": gLabels("especialidade") = "especialidade"
    gLabels("solicitante") = "solicitante": gLabels("data pedido") = "pedido"
    gLabels("data término") = "termino": gLabels("data termino") = "termino"
    gLabels("setor") = "setor": gLabels("localidade") = "localidade"
    gLabels("bem") = "bem": gLabels("nr. do patrimônio") = "patrimonio"
    gLabels("marca") = "marca": gLabels("modelo") = "modelo"
    gLabels("série") = "serie": gLabels("serie") = "serie"
    gLabels("observações") = "obs": gLabels("observacoes") = "obs"
    gLabels("prioridade") = "criticidade": gLabels("criticidade") = "criticidade"
End Sub

Private Function Tz(ByVal s As String) As String
    s = Trim$(Replace(Replace(Replace(Replace(s, vbCr, " "), vbLf, " "), ChrW(160), " "), vbTab, " "))
    Do While InStr(1, s, "  ") > 0
        s = Replace(s, "  ", " ")
    Loop
    Tz = s
End Function

Private Function EhData(ByVal s As String) As Boolean
    s = Tz(s)
    EhData = (s Like "##/##/#### #*:##*") Or (s Like "##/##/## #*:##*")
End Function

Private Function ParaData(ByVal s As String) As Variant
    Dim p() As String, d() As String, h() As String, y As Long
    ParaData = Empty
    s = Tz(s)
    If Not EhData(s) Then Exit Function
    p = Split(s, " "): d = Split(p(0), "/"): h = Split(p(1), ":")
    y = CLng(d(2)): If y < 100 Then y = y + 2000
    ParaData = DateSerial(y, CLng(d(1)), CLng(d(0))) + TimeSerial(CLng(h(0)), CLng(h(1)), 0)
End Function

Private Function EhNumOS(ByVal v As String) As Boolean
    EhNumOS = (Len(v) >= 4 And Len(v) <= 7 And v Like String(Len(v), "#"))
End Function

Private Function FilaDe(ByVal s As String) As String
    s = LCase$(s)
    If s Like "*n?o*atend*" Or InStr(s, "nao_atend") > 0 Then
        FilaDe = "não atendida"
    ElseIf InStr(s, "abert") > 0 Then
        FilaDe = "aberta"
    ElseIf InStr(s, "agend") > 0 Then
        FilaDe = "agendar"
    ElseIf InStr(s, "aguard") > 0 Or InStr(s, "material") > 0 Then
        FilaDe = "aguardando material"
    ElseIf InStr(s, "extern") > 0 Then
        FilaDe = "conserto externo"
    ElseIf InStr(s, "cancel") > 0 Then
        FilaDe = "cancelada"
    ElseIf InStr(s, "conclu") > 0 Then
        FilaDe = "concluída"
    Else
        FilaDe = ""
    End If
End Function

Private Function NovoRec(arq As String) As Object
    Dim r As Object
    Set r = CreateObject("Scripting.Dictionary")
    r("os") = "": r("desc") = "": r("arquivo") = arq
    Set r("exec") = New Collection
    Set NovoRec = r
End Function

Private Function LerMV(rows As Collection, arq As String, recs As Object) As Long
    Dim row As Variant, first As String, modo As String, cur As Object
    Dim k As Long, v As String, lab As String, key As String, pendFim As String
    Dim vals As Collection, datas As Collection, func As String, x As Object, z As Long
    For Each row In rows
        first = Tz(CStr(row(0)))
        If LCase$(first) Like "ordem de servi?o relacionadas*" Then
            modo = "rel"
        ElseIf LCase$(first) Like "ordem de servi?o" Then
            If Not cur Is Nothing Then
                If cur("os") <> "" Then LerMV = LerMV + 1
            End If
            FecharRec cur, arq, recs
            Set cur = NovoRec(arq): modo = "head": pendFim = ""
        ElseIf cur Is Nothing Then
            ' antes da primeira OS
        ElseIf modo = "head" Then
            For k = 0 To UBound(row)
                v = Tz(CStr(row(k)))
                If cur("os") = "" And EhNumOS(v) Then
                    cur("os") = v
                ElseIf cur("os") <> "" And v <> "" Then
                    cur("desc") = v: Exit For
                End If
            Next k
            If cur("os") <> "" Then modo = "fields"
        ElseIf LCase$(first) = "serviço" Or LCase$(first) = "servico" Then
            modo = "exec"
        ElseIf modo = "fields" Then
            lab = ""
            For k = 0 To UBound(row)
                v = Tz(CStr(row(k)))
                If v <> "" Then
                    If gLabels.Exists(LCase$(v)) Then
                        lab = gLabels(LCase$(v))
                    ElseIf lab <> "" Then
                        If Not cur.Exists(lab) Then cur(lab) = v
                        lab = ""
                    End If
                End If
            Next k
        ElseIf modo = "exec" Then
            Set vals = New Collection: Set datas = New Collection
            For k = 0 To UBound(row)
                v = Tz(CStr(row(k)))
                If v <> "" And v <> ":" Then
                    vals.Add v
                    If EhData(v) Then datas.Add v
                End If
            Next k
            If vals.Count > 0 Then
                If first = "" Then
                    If datas.Count > 0 Then pendFim = datas(1)
                Else
                    func = ""
                    For z = 2 To vals.Count
                        If Not EhData(vals(z)) And Not (vals(z) Like "*#:##") Then func = vals(z): Exit For
                    Next z
                    Set x = CreateObject("Scripting.Dictionary")
                    x("servico") = first: x("func") = func
                    x("ini") = Empty: x("fim") = Empty
                    If datas.Count >= 1 Then x("ini") = ParaData(datas(1))
                    If datas.Count >= 2 Then
                        x("fim") = ParaData(datas(2))
                    ElseIf pendFim <> "" Then
                        x("fim") = ParaData(pendFim)
                    End If
                    cur("exec").Add x
                    pendFim = ""
                End If
            End If
        End If
    Next row
    If Not cur Is Nothing Then
        If cur("os") <> "" Then LerMV = LerMV + 1
    End If
    FecharRec cur, arq, recs
End Function

Private Function Rank(f As String) As Long
    If f = "concluída" Or f = "cancelada" Then Rank = 3 Else Rank = 0
End Function

Private Sub FecharRec(cur As Object, arq As String, recs As Object)
    If cur Is Nothing Then Exit Sub
    If cur("os") <> "" Then
        Dim f As String
        f = FilaDe(IIf(cur.Exists("situacao"), cur("situacao"), ""))
        If f = "" Then f = FilaDe(arq)
        If f = "" Then f = "sem fila"
        cur("fila") = f
        If recs.Exists(cur("os")) Then
            If Rank(f) >= Rank(recs(cur("os"))("fila")) Then Set recs(cur("os")) = cur
        Else
            recs.Add cur("os"), cur
        End If
    End If
    Set cur = Nothing
End Sub

'------------------------------------------------------------ configurações
Private Sub GarantirConfig()
    Dim ws As Worksheet
    If Existe(SH_CFG) Then Exit Sub
    Set ws = ThisWorkbook.Worksheets.Add(After:=ThisWorkbook.Worksheets(ThisWorkbook.Worksheets.Count))
    ws.Name = SH_CFG
    ws.Range("A1").Value = "Configurações": ws.Range("A1").Font.Size = 16: ws.Range("A1").Font.Bold = True
    ws.Range("A3").Value = "Nomes genéricos (um por linha, pode ser o começo do nome)"
    ws.Range("A4").Value = "WALTER ANDR"
    ws.Range("C3").Value = "De-para: nome no MV": ws.Range("D3").Value = "Nome correto"
    ws.Range("F3").Value = "Limite de horas por execução": ws.Range("F4").Value = 12
    ws.Range("A3:F3").Font.Bold = True
    ws.Columns("A").ColumnWidth = 40: ws.Columns("C:D").ColumnWidth = 36: ws.Columns("F").ColumnWidth = 30
    GravarRegrasPadrao ws
    ws.Range("A20").Value = "Lançamentos com nome genérico aparecem como 'WALTER / LANÇAMENTOS GENÉRICOS'. " & _
        "Execuções acima do limite de horas vão para a aba 'Para arrumar' e ficam fora dos relatórios."
End Sub

Private Sub LerConfig()
    Dim ws As Worksheet, r As Long
    Set ws = ThisWorkbook.Worksheets(SH_CFG)
    Set gGenericos = New Collection
    Set gDePara = CreateObject("Scripting.Dictionary")
    For r = 4 To 200
        If Trim$(ws.Cells(r, 1).Value) <> "" Then gGenericos.Add UCase$(Trim$(ws.Cells(r, 1).Value))
        If Trim$(ws.Cells(r, 3).Value) <> "" And Trim$(ws.Cells(r, 4).Value) <> "" Then _
            gDePara(UCase$(Trim$(ws.Cells(r, 3).Value))) = UCase$(Trim$(ws.Cells(r, 4).Value))
    Next r
    If Trim$(ws.Range("J4").Value) = "" Then GravarRegrasPadrao ws
    Set gRegras = New Collection
    For r = 4 To 60
        If Trim$(ws.Cells(r, 10).Value) <> "" And Trim$(ws.Cells(r, 11).Value) <> "" Then gRegras.Add Array(Trim$(ws.Cells(r, 10).Value), Split(ws.Cells(r, 11).Value, ";"))
    Next r
    ' regras novas entram mesmo com regras antigas salvas na Config
    Dim regs As Variant, q As Long, tem As Boolean, rg As Variant, ultima As Long
    regs = RegrasPadrao()
    For q = 0 To UBound(regs) Step 2
        tem = False
        For Each rg In gRegras
            If rg(0) = regs(q) Then tem = True
        Next rg
        If Not tem Then
            gRegras.Add Array(regs(q), Split(regs(q + 1), ";"))
            ultima = ws.Cells(ws.Rows.Count, 10).End(xlUp).Row + 1
            ws.Cells(ultima, 10).Value = regs(q): ws.Cells(ultima, 11).Value = regs(q + 1)
        End If
    Next q
    gMaxExec = 12
    If IsNumeric(ws.Range("F4").Value) Then
        If ws.Range("F4").Value > 0 Then gMaxExec = ws.Range("F4").Value
    End If
End Sub

Private Function NomeTecnico(ByVal n As String) As String
    Dim g As Variant
    n = UCase$(Trim$(n))
    If gDePara.Exists(n) Then n = gDePara(n)
    For Each g In gGenericos
        If Len(g) > 0 And Left$(n, Len(g)) = g Then n = "WALTER / LANÇAMENTOS GENÉRICOS": Exit For
    Next g
    If n = "" Then n = "SEM FUNCIONÁRIO"
    NomeTecnico = n
End Function

Private Function RegrasPadrao() As Variant
    ' Frases padrão do planejamento (22/11/26) + frases antigas. O que não bater = recado do solicitante.
    '   TRATATIVA SUPERVISÃO 22/11/26 · TRATATIVA COMPRADOR 22/11/26 · TRATATIVA PLANEJAMENTO 22/11/26
    '   PROGRAMADO PARA 29/11/26 (FIM DE SEMANA) · EM EXECUÇÃO 22/11/26 · SERVIÇO REALIZADO, AGUARDANDO FECHAMENTO 22/11/26
    RegrasPadrao = Array("Supervisão", "TRATATIVA SUPERVISÃO; TRATATIVA (SUPERVISÃO; TRATATIVA DA SUPERVISÃO; AGUARDAR SUPERVISOR; AGUARDANDO SUPERVISOR; (SUPERVISOR)", _
        "Comprador", "TRATATIVA COMPRADOR; TRATATIVA DE COMPRA; (COMPRADOR); TRATATIVA (COMPRA; TRATATIVA DO COMPRADOR; AGUARDANDO COMPRADOR", _
        "Planejador", "TRATATIVA PLANEJAMENTO; PLANEJADOR; A AGENDAR; MATERIAL ENTREGUE", _
        "Gestor", "(GESTOR); TRATATIVA (GESTOR; TRATATIVA DO GESTOR; AGUARDANDO GESTOR", _
        "Externo", "TRATATIVA EXTERNA; SERVIÇO EXTERNO; SERVICO EXTERNO; TRATATIVA DE SERVIÇO EXTERNO", _
        "Material", "AGUARDANDO MATERIAL; MATERIAL SOLICITADO; SOLICITADO MATERIAL; PEDIDO FEITO", _
        "Feito, falta fechar", "AGUARDANDO FECHAMENTO", _
        "Em execução", "EM EXECUÇÃO", _
        "Programado", "PROGRAMADO PARA")
End Function

Private Sub GravarRegrasPadrao(ws As Worksheet)
    ws.Range("J3").Value = "Pendente de (responsável)": ws.Range("K3").Value = "Frases padrão na observação (separadas por ;) - aceita 80% de semelhança, sem acento. O que não bater = recado do solicitante."
    ws.Range("J3:K3").Font.Bold = True
    Dim regs As Variant, q As Long
    regs = RegrasPadrao()
    ws.Range("J4:K60").ClearContents
    For q = 0 To UBound(regs) Step 2
        ws.Cells(4 + q \ 2, 10).Value = regs(q)
        ws.Cells(4 + q \ 2, 11).Value = regs(q + 1)
    Next q
    ws.Columns("J").ColumnWidth = 22: ws.Columns("K").ColumnWidth = 90
End Sub

'------------------------------------------------------------ observação -> pendente de
Private Function NormTxt(ByVal s As String) As String
    Dim i As Long, c As String, o As String, de As String, para As String, k As Long
    de = "ÁÀÂÃÄÉÈÊËÍÌÎÏÓÒÔÕÖÚÙÛÜÇ": para = "AAAAAEEEEIIIIOOOOOUUUUC"
    s = UCase$(s)
    For i = 1 To Len(s)
        c = Mid$(s, i, 1)
        k = InStr(1, de, c, vbBinaryCompare)
        If k > 0 Then c = Mid$(para, k, 1)
        If Not (c Like "[A-Z0-9/.]") Then c = " "
        o = o & c
    Next i
    NormTxt = Tz(o)
End Function

Private Function Lev(a As String, b As String) As Long
    Dim m As Long, n As Long, i As Long, j As Long, d() As Long, prev As Long, tmp As Long, cost As Long
    m = Len(a): n = Len(b)
    If m = 0 Then Lev = n: Exit Function
    If n = 0 Then Lev = m: Exit Function
    ReDim d(0 To n)
    For j = 0 To n: d(j) = j: Next j
    For i = 1 To m
        prev = d(0): d(0) = i
        For j = 1 To n
            tmp = d(j)
            If Mid$(a, i, 1) = Mid$(b, j, 1) Then cost = 0 Else cost = 1
            d(j) = Application.Min(d(j) + 1, d(j - 1) + 1, prev + cost)
            prev = tmp
        Next j
    Next i
    Lev = d(n)
End Function

' posição (palavra) da última ocorrência parecida da expressão; -1 se não achar
Private Function Achar(sg As String, ByVal expr As String) As Long
    Dim w() As String, kw() As String, n As Long, i As Long, t As Long, ok As Boolean, a As String, b As String
    Achar = -1
    expr = NormTxt(expr): If expr = "" Or sg = "" Then Exit Function
    w = Split(sg, " "): kw = Split(expr, " "): n = UBound(kw) + 1
    For i = 0 To UBound(w) - n + 1
        ok = True
        For t = 0 To n - 1
            a = w(i + t): b = kw(t)
            If a <> b Then
                If Len(a) <= 3 Or Len(b) <= 3 Then
                    ok = False
                ElseIf Len(b) >= 5 And Left$(a, Len(b)) = b Then
                    ' palavra encurtada (ex.: SUPERVIS)
                ElseIf 1 - Lev(a, b) / Application.Max(Len(a), Len(b)) < 0.8 Then
                    ok = False
                End If
            End If
            If Not ok Then Exit For
        Next t
        If ok Then Achar = i
    Next i
End Function

Private Function DataNoTexto(seg As String) As Variant
    Dim toks() As String, tk As Variant, p() As String, sep As String, d As Long, m As Long, y As Long, melhor As Variant, dt As Date
    DataNoTexto = Empty
    toks = Split(Replace(Replace(Replace(Replace(seg, ",", " "), "(", " "), ")", " "), "-", " "), " ")
    For Each tk In toks
        tk = Trim$(tk)
        Do While Len(tk) > 0 And (Right$(tk, 1) = "." Or Right$(tk, 1) = "/")
            tk = Left$(tk, Len(tk) - 1)
        Loop
        sep = ""
        If InStr(tk, "/") > 0 Then
            sep = "/"
        ElseIf InStr(tk, ".") > 0 Then
            sep = "."
        End If
        If sep <> "" Then
            p = Split(tk, sep)
            If (UBound(p) = 2 Or (UBound(p) = 1 And sep = "/")) Then
                If IsNumeric(p(0)) And IsNumeric(p(1)) And Len(p(0)) <= 2 And Len(p(1)) <= 2 Then
                    d = CLng(p(0)): m = CLng(p(1)): y = Year(Date)
                    If UBound(p) = 2 Then
                        If IsNumeric(p(2)) Then y = CLng(p(2)) Else y = 0
                        If y < 100 And y > 0 Then y = y + 2000
                    End If
                    If d >= 1 And d <= 31 And m >= 1 And m <= 12 And y > 2000 Then
                        dt = DateSerial(y, m, d)
                        If IsEmpty(melhor) Then
                            melhor = dt
                        ElseIf dt > melhor Then
                            melhor = dt
                        End If
                    End If
                End If
            End If
        End If
    Next tk
    DataNoTexto = melhor
End Function

' descobre com quem a OS está parada: divide a observação em trechos e usa o trecho mais recente
Private Sub Classificar(ByVal obs As String, resp As String, em As Variant)
    Dim segs() As String, i As Long, sg As String, rg As Variant, ex As Variant, x As Long, pos As Long
    Dim rsp As String, dt As Variant, ultEm As Variant, proprio As Boolean
    Dim bEm As Double, bProp As Long, bIdx As Long, achou As Boolean
    resp = "": em = Empty
    If Trim$(obs) = "" Then resp = "Sem observação": Exit Sub
    obs = UCase$(obs)
    obs = Replace(Replace(Replace(obs, " - ", Chr(1)), "|", Chr(1)), ";", Chr(1))
    segs = Split(obs, Chr(1))
    For i = 0 To UBound(segs)
        sg = NormTxt(segs(i)): rsp = "": pos = -1
        For Each rg In gRegras
            For Each ex In rg(1)
                If Trim$(ex) <> "" Then
                    x = Achar(sg, CStr(ex))
                    If x >= 0 And x >= pos Then pos = x: rsp = rg(0)
                End If
            Next ex
        Next rg
        dt = DataNoTexto(CStr(segs(i)))
        proprio = Not IsEmpty(dt)
        If proprio Then ultEm = dt Else dt = ultEm
        If rsp = "" And proprio And achou Then
            If IsEmpty(em) Then
                em = dt
            ElseIf dt > em Then
                em = dt
            End If
        End If
        If rsp <> "" Then
            Dim kEm As Double
            If IsEmpty(dt) Then kEm = 0 Else kEm = CDbl(dt)
            If Not achou Or kEm > bEm Or (kEm = bEm And (IIf(proprio, 1, 0) > bProp Or (IIf(proprio, 1, 0) = bProp And i > bIdx))) Then
                achou = True: resp = rsp: em = dt: bEm = kEm: bProp = IIf(proprio, 1, 0): bIdx = i
            End If
        End If
    Next i
    If Not achou Then resp = "Outro": em = ultEm
End Sub

'------------------------------------------------------------ cálculos e montagem
Private Function Campo(r As Object, k As String, padrao As String) As String
    If r.Exists(k) Then Campo = r(k) Else Campo = padrao
    If Campo = "" Then Campo = padrao
End Function

Private Sub Montar(recs As Object, nArq As Long, nVazios As Long)
    Dim okA() As Variant, errA() As Variant, nOk As Long, nErr As Long
    Dim key As Variant, r As Object, e As Object, x As Object, iss As String
    Dim ped As Variant, ter As Variant, ini As Variant, fim As Variant
    Dim esp As Variant, horas As Double, tot As Variant, agora As Date, maxPed As Date
    Dim f As String, tec As String, i As Long, avs As String, nProv As Long
    Dim cEsp As Object, cTipo As Object, cSetor As Object, cTec As Object, cCrit As Object
    Set cEsp = CreateObject("Scripting.Dictionary"): Set cTipo = CreateObject("Scripting.Dictionary")
    Set cSetor = CreateObject("Scripting.Dictionary"): Set cTec = CreateObject("Scripting.Dictionary")
    Set cCrit = CreateObject("Scripting.Dictionary")
    Dim cPend As Object
    Set cPend = CreateObject("Scripting.Dictionary")
    agora = Now
    ReDim okA(1 To Application.Max(1, recs.Count), 1 To NCOL - 1)
    ReDim errA(1 To Application.Max(1, recs.Count), 1 To NCOL)

    For Each key In recs.Keys
        Set r = recs(key)
        iss = "": avs = ""
        ped = ParaData(Campo(r, "pedido", "")): ter = ParaData(Campo(r, "termino", ""))
        ini = Empty: fim = Empty: tec = "": horas = 0
        If r("exec").Count > 0 Then
            Set e = r("exec")(1)
            ini = e("ini"): fim = e("fim"): tec = NomeTecnico(e("func"))
        End If
        For Each x In r("exec")
            If Not IsEmpty(x("ini")) And Not IsEmpty(x("fim")) Then
                If x("fim") < x("ini") Then
                    iss = iss & "; Fim da execução antes do início"
                Else
                    If (x("fim") - x("ini")) * 24 > gMaxExec Then
                        ' entra no cálculo com 1 h provisória até ser corrigida no MV
                        avs = avs & "; Execução de " & Round((x("fim") - x("ini")) * 24, 0) & " h (acima de " & gMaxExec & " h): usado 1 h provisória no cálculo"
                        horas = horas + 1
                    Else
                        horas = horas + (x("fim") - x("ini")) * 24
                    End If
                End If
            ElseIf Not IsEmpty(x("ini")) And r("fila") = "concluída" Then
                avs = avs & "; Execução sem hora de fim: usado 1 h provisória no cálculo"
                horas = horas + 1
            End If
            If Not IsEmpty(x("ini")) Then
                If x("ini") > agora Then iss = iss & "; Execução com data futura"
            End If
        Next x
        esp = Empty: tot = Empty
        If IsEmpty(ped) Then
            iss = iss & "; Sem data do pedido"
        Else
            If ped > agora Then iss = iss & "; Data futura no pedido"
            If Not IsEmpty(ini) Then
                ' o MV valida pelo DIA: hora anterior no mesmo dia não é erro (espera = 0)
                If Int(ini) < Int(ped) Then
                    iss = iss & "; Atendimento antes da abertura"
                ElseIf ini < ped Then
                    esp = 0
                Else
                    esp = (ini - ped) * 24
                End If
            End If
            If Not IsEmpty(ter) Then
                If Int(ter) < Int(ped) Then
                    iss = iss & "; Término antes da abertura"
                ElseIf ter < ped Then
                    tot = 0
                Else
                    tot = (ter - ped) * 24
                End If
            End If
        End If
        If Not IsEmpty(ter) And Not IsEmpty(ini) Then
            If Int(ter) < Int(ini) Then iss = iss & "; Término antes do início do atendimento"
        End If
        f = r("fila")
        If f = "concluída" And r("exec").Count = 0 Then iss = iss & "; Concluída sem execução lançada"

        Dim linha(1 To 26) As Variant
        linha(1) = CDbl(r("os")): linha(2) = r("desc"): linha(3) = f
        linha(4) = Campo(r, "tipo", "Sem tipo"): linha(5) = Campo(r, "especialidade", "Sem especialidade")
        linha(6) = Campo(r, "criticidade", "Não informada"): linha(7) = Campo(r, "solicitante", "")
        linha(8) = Campo(r, "setor", "Sem setor"): linha(9) = Campo(r, "localidade", "")
        linha(10) = ped: linha(11) = ter
        If r("exec").Count > 0 Then linha(12) = ServicoDe(r) Else linha(12) = ""
        linha(13) = IIf(r("exec").Count > 0, tec, "")
        linha(14) = ini: linha(15) = fim: linha(16) = esp
        If horas > 0 Then linha(17) = horas Else linha(17) = Empty
        linha(18) = tot
        linha(19) = IIf(f = "aberta" Or f = "não atendida" Or f = "agendar", "S", "N")
        linha(20) = IIf(f = "aguardando material" Or f = "conserto externo", "S", "N")
        linha(21) = r("arquivo")
        linha(22) = Campo(r, "obs", "")
        Dim pResp As String, pEm As Variant
        pResp = "": pEm = Empty
        If f <> "concluída" And f <> "cancelada" Then Classificar CStr(linha(22)), pResp, pEm
        ' aguardando material / conserto externo: a parte nossa já foi feita, a pendência é a fila
        If f = "aguardando material" Then pResp = "Material"
        If f = "conserto externo" Then pResp = "Externo"
        linha(23) = pResp: linha(24) = pEm
        If Not IsEmpty(pEm) Then linha(25) = Application.Max(0, Int(agora - pEm)) Else linha(25) = Empty
        If IsEmpty(ped) Then linha(26) = "" Else linha(26) = Format(ped, "yyyy-mm")
        If pResp <> "" And linha(19) = "S" Then cPend(pResp) = cPend(pResp) + 1
        ' provável erro de dia: execução fora do período da OS, mas cabe trocando 1 dia
        If (InStr(iss, "antes da abertura") > 0 Or InStr(iss, "antes do início do atendimento") > 0) And Not IsEmpty(ini) And Not IsEmpty(ped) Then
            Dim sh As Long, ni As Date, nfim As Variant, lim As Date
            If IsEmpty(ter) Then lim = agora Else lim = ter
            For sh = -1 To 1 Step 2
                ni = ini + sh
                If IsEmpty(fim) Then nfim = Empty Else nfim = fim + sh
                If ni >= ped And ni <= lim Then
                    If IsEmpty(nfim) Then
                        iss = "; Provável erro de dia na execução: data sugerida " & Format(ni, "dd/mm/yyyy hh:nn") & iss: Exit For
                    ElseIf nfim <= lim Then
                        iss = "; Provável erro de dia na execução: data sugerida " & Format(ni, "dd/mm/yyyy hh:nn") & iss: Exit For
                    End If
                End If
            Next sh
        End If

        If iss = "" And avs <> "" Then
            ' provisória: entra nos cálculos E aparece em Para arrumar
            nProv = nProv + 1
            nErr = nErr + 1
            errA(nErr, 1) = Mid$(avs, 3)
            For i = 1 To 26: errA(nErr, i + 1) = linha(i): Next i
        End If
        If iss = "" Then
            nOk = nOk + 1
            For i = 1 To 26: okA(nOk, i) = linha(i): Next i
            Contar cEsp, linha(5): Contar cTipo, linha(4): Contar cSetor, linha(8): Contar cCrit, linha(6)
            If linha(13) <> "" Then cTec(linha(13)) = cTec(linha(13)) + horas
            If Not IsEmpty(ped) Then
                If ped > maxPed Then maxPed = ped
            End If
        Else
            nErr = nErr + 1
            errA(nErr, 1) = Mid$(iss & avs, 3) & " (fora dos relatórios)"
            For i = 1 To 26: errA(nErr, i + 1) = linha(i): Next i
        End If
    Next key

    Dim dIni As Variant, dFim As Variant
    dIni = Empty: dFim = Empty
    If Existe(SH_BL) Then
        If IsDate(ThisWorkbook.Worksheets(SH_BL).Range("B3").Value) Then dIni = ThisWorkbook.Worksheets(SH_BL).Range("B3").Value
        If IsDate(ThisWorkbook.Worksheets(SH_BL).Range("B4").Value) Then dFim = ThisWorkbook.Worksheets(SH_BL).Range("B4").Value
    End If

    LimparAntigos
    Dim wsB As Worksheet
    Set wsB = ThisWorkbook.Worksheets.Add(After:=ThisWorkbook.Worksheets(ThisWorkbook.Worksheets.Count))
    wsB.Name = SH_BL
    wsB.Range("B3").Value = dIni: wsB.Range("B4").Value = dFim
    ThisWorkbook.Names.Add Name:="DataIni", RefersTo:="='" & SH_BL & "'!$B$3"
    ThisWorkbook.Names.Add Name:="DataCorte", RefersTo:="=IF('" & SH_BL & "'!$B$4="""",TODAY(),'" & SH_BL & "'!$B$4)"
    MontarDashboard okA, nOk, recs.Count, nErr - nProv, nArq, nVazios, errA, cEsp, cTipo, cSetor, nProv
    MontarErros errA, nErr
    MontarBacklog cEsp, cPend
    MontarEquipe cTec
    MontarTempos cEsp, cTipo, cCrit
    MontarArquivos
    MontarRepetidas okA, nOk
    ' ordem: Dashboard, Backlog, Tempos, Equipe, Para arrumar (erros + repetidas), Arquivos...
    ThisWorkbook.Worksheets(SH_BL).Move After:=ThisWorkbook.Worksheets(SH_DASH)
    ThisWorkbook.Worksheets(SH_TP).Move After:=ThisWorkbook.Worksheets(SH_BL)
    ThisWorkbook.Worksheets(SH_EQ).Move After:=ThisWorkbook.Worksheets(SH_TP)
    ThisWorkbook.Worksheets(SH_ERR).Move After:=ThisWorkbook.Worksheets(SH_EQ)
    ThisWorkbook.Worksheets(SH_ARQ).Move After:=ThisWorkbook.Worksheets(SH_ERR)
    ThisWorkbook.Worksheets(SH_DASH).Activate
    Application.Calculate
End Sub

Private Function ServicoDe(r As Object) As String
    ServicoDe = r("exec")(1)("servico")
End Function

Private Sub Contar(d As Object, k As Variant)
    d(k) = d(k) + 1
End Sub

Private Sub LimparAntigos()
    Dim nm As Variant
    On Error Resume Next
    Do While ThisWorkbook.SlicerCaches.Count > 0
        ThisWorkbook.SlicerCaches(1).Delete
        If Err.Number <> 0 Then Exit Do
    Loop
    Application.DisplayAlerts = False
    For Each nm In Array(SH_DASH, SH_BL, SH_EQ, SH_TP, SH_ERR, SH_CALC, SH_ARQ, SH_REP)
        ThisWorkbook.Worksheets(nm).Delete
    Next nm
    ThisWorkbook.Names("DataCorte").Delete
    ThisWorkbook.Names("DataIni").Delete
    Application.DisplayAlerts = True
    On Error GoTo 0
End Sub

Private Function Cabecalhos() As Variant
    Cabecalhos = Array("OS", "Descrição", "Fila", "Tipo", "Especialidade", "Criticidade", "Solicitante", "Setor", _
        "Localidade", "Pedido", "Término", "Serviço", "Técnico", "Início atend.", "Fim atend.", "Espera_h", _
        "Execucao_h", "Total_h", "Backlog", "Terceiros", "Arquivo", "Observações", "Pendente de", "Encaminhado em", _
        "Parado_dias", "Mês do pedido", "Visivel")
End Function

Private Function OrdenarPorValor(d As Object, maxItens As Long) As Variant
    Dim k() As Variant, v() As Double, n As Long, i As Long, j As Long, tk As Variant, tv As Double, kk As Variant
    n = d.Count
    If n = 0 Then OrdenarPorValor = Array(): Exit Function
    ReDim k(0 To n - 1): ReDim v(0 To n - 1)
    i = 0
    For Each kk In d.Keys: k(i) = kk: v(i) = d(kk): i = i + 1: Next kk
    For i = 0 To n - 2
        For j = i + 1 To n - 1
            If v(j) > v(i) Then tv = v(i): v(i) = v(j): v(j) = tv: tk = k(i): k(i) = k(j): k(j) = tk
        Next j
    Next i
    If maxItens > 0 And n > maxItens Then ReDim Preserve k(0 To maxItens - 1)
    OrdenarPorValor = k
End Function

Private Sub MontarDashboard(okA() As Variant, nOk As Long, nTot As Long, nErr As Long, nArq As Long, nVazios As Long, _
        errA() As Variant, cEsp As Object, cTipo As Object, cSetor As Object, nProv As Long)
    Dim ws As Worksheet, wc As Worksheet, lo As ListObject, hdr As Variant, i As Long, tRow As Long
    Set ws = ThisWorkbook.Worksheets.Add(Before:=ThisWorkbook.Worksheets(1)): ws.Name = SH_DASH
    Set wc = ThisWorkbook.Worksheets.Add(After:=ThisWorkbook.Worksheets(ThisWorkbook.Worksheets.Count)): wc.Name = SH_CALC
    ws.Activate
    ActiveWindow.DisplayGridlines = False

    ws.Range("A1").Value = "Gerador de OS - HEV"
    ws.Range("A1").Font.Size = 22: ws.Range("A1").Font.Bold = True: ws.Range("A1").Font.Color = RGB(11, 31, 75)
    ws.Range("A2").Value = "Relatório importado: " & nTot & " OS em " & nArq & " arquivo(s) · " & nOk & _
        " entraram nos cálculos: " & (nOk - nProv) & " normais" & IIf(nProv > 0, " + " & nProv & " com horário ajustado (contadas com 1 h; corrigir no MV)", "") & IIf(nErr > 0, " · " & nErr & " fora por erro de data", "") & " · veja a aba 'Para arrumar'" & _
        IIf(nVazios > 0, " · " & nVazios & " arquivo(s) sem OS (fila vazia)", "")
    ws.Range("A2").Font.Color = RGB(91, 102, 131)
    BotaoImportar ws

    ' tabela de OS
    hdr = Cabecalhos()
    tRow = 86
    For i = 0 To NCOL - 1: ws.Cells(tRow, i + 1).Value = hdr(i): Next i
    If nOk > 0 Then ws.Cells(tRow + 1, 1).Resize(nOk, NCOL - 1).Value = okA
    Set lo = ws.ListObjects.Add(1, ws.Cells(tRow, 1).Resize(Application.Max(nOk, 1) + 1, NCOL), , 1)
    lo.Name = "tbOS"
    lo.TableStyle = "TableStyleMedium2"
    lo.ListColumns("Visivel").DataBodyRange.Formula = "=SUBTOTAL(103,[@OS])"
    lo.ListColumns("Pedido").DataBodyRange.NumberFormat = "dd/mm/yyyy hh:mm"
    lo.ListColumns("Término").DataBodyRange.NumberFormat = "dd/mm/yyyy hh:mm"
    lo.ListColumns("Início atend.").DataBodyRange.NumberFormat = "dd/mm/yyyy hh:mm"
    lo.ListColumns("Fim atend.").DataBodyRange.NumberFormat = "dd/mm/yyyy hh:mm"
    lo.ListColumns("Espera_h").DataBodyRange.NumberFormat = "0.0"
    lo.ListColumns("Execucao_h").DataBodyRange.NumberFormat = "0.0"
    lo.ListColumns("Total_h").DataBodyRange.NumberFormat = "0.0"
    lo.ListColumns("Encaminhado em").DataBodyRange.NumberFormat = "dd/mm/yyyy"
    lo.ListColumns("Observações").DataBodyRange.WrapText = False
    ws.Columns("A:Z").ColumnWidth = 14
    ws.Columns("V").ColumnWidth = 48
    ws.Columns("B").ColumnWidth = 48
    ws.Cells(tRow - 1, 1).Value = "Ordens de serviço (a lista segue os filtros acima)"
    ws.Cells(tRow - 1, 1).Font.Bold = True: ws.Cells(tRow - 1, 1).Font.Size = 13

    ' indicadores (respeitam os filtros: usam a coluna Visivel)
    Dim E As String
    E = "(DataCorte+0.99999)"
    ' Dashboard = como foi o mês (OS abertas no período; use o filtro "Mês do pedido").
    ' O que é de backlog (pendente até a data, tratativas, cobrar) fica na aba Backlog.
    Dim TRAT As String
    TRAT = "COUNTIFS(tbOS[Visivel],1,tbOS[Backlog],""S"",tbOS[Pendente de],""<>Sem observação"",tbOS[Pendente de],""<>Outro"",tbOS[Pendente de],""<>"")"
    Kpi ws, "A4", "Atendidas em até 24 h", "=IFERROR(COUNTIFS(tbOS[Visivel],1,tbOS[Espera_h],""<=24"")/COUNTIFS(tbOS[Visivel],1,tbOS[Espera_h],"">=0""),0)", "da abertura até a hora inicial do 1º atendimento"
    Kpi ws, "C4", "Total de OS", "=SUBTOTAL(103,tbOS[OS])", ""
    ws.Range("E4").Value = "Com terceiros (fora do backlog)"
    ws.Range("E5").Formula = "=COUNTIFS(tbOS[Visivel],1,tbOS[Fila],""aguardando material"")"
    ws.Range("F5").Formula = "=COUNTIFS(tbOS[Visivel],1,tbOS[Fila],""conserto externo"")"
    ws.Range("E6").Value = "aguardando material": ws.Range("F6").Value = "conserto externo"
    Kpi ws, "G4", "Espera mediana até 1º atend. (h)", "", ""
    ws.Range("G5").FormulaArray = "=IFERROR(MEDIAN(IF((tbOS[Visivel]=1)*(tbOS[Espera_h]<>""""),tbOS[Espera_h])),""-"")"
    ws.Range("G6").Formula = "=""média ""&IFERROR(ROUND(AVERAGEIFS(tbOS[Espera_h],tbOS[Visivel],1),1),""-"")&"" h"""
    Kpi ws, "I4", "Homem-hora lançado (h)", "=SUMIFS(tbOS[Execucao_h],tbOS[Visivel],1)", ""
    ws.Range("I6").Formula = "=COUNTIFS(tbOS[Visivel],1,tbOS[Execucao_h],"">0"")&"" OS com execução"""
    ws.Range("A4:J4").Font.Color = RGB(91, 102, 131)
    ws.Range("A5,C5,E5,F5,G5,I5").Font.Size = 24: ws.Range("A5,C5,E5,F5,G5,I5").Font.Bold = True
    ws.Range("A5").NumberFormat = "0%"
    ws.Range("G5,I5").NumberFormat = "0.0"
    ws.Range("A6:J6").Font.Color = RGB(91, 102, 131): ws.Range("A6:J6").Font.Size = 9
    ' Total de OS em forma de fração: total em cima, realizadas embaixo, % ao lado
    ws.Range("C6").Formula = "=SUBTOTAL(103,tbOS[OS])-COUNTIFS(tbOS[Visivel],1,tbOS[Backlog],""S"")"
    ws.Range("C6").Font.Size = 24: ws.Range("C6").Font.Bold = True: ws.Range("C6").Font.Color = RGB(11, 22, 48)
    ws.Range("C5").Borders(xlEdgeBottom).Weight = xlMedium
    ws.Range("D5").Formula = "=IFERROR(C6/C5,0)": ws.Range("D5").NumberFormat = "0.0%"
    ws.Range("D5").Font.Size = 28: ws.Range("D5").Font.Bold = True: ws.Range("D5").Font.Color = RGB(224, 17, 95)
    ' verde a partir de 90%
    Dim fc As Object
    Set fc = ws.Range("D5").FormatConditions.Add(Type:=xlCellValue, Operator:=xlGreaterEqual, Formula1:="=0.9")
    fc.Font.Color = RGB(18, 122, 58)
    Set fc = ws.Range("A5").FormatConditions.Add(Type:=xlCellValue, Operator:=xlGreaterEqual, Formula1:="=0.9")
    fc.Font.Color = RGB(18, 122, 58)
    ' % fantasma dourado: até onde vai se resolvermos as OS do backlog que já têm tratativa
    ws.Range("D3").Formula = "=""se resolver as ""&" & TRAT & "&"" com tratativa"""
    ws.Range("D4").Formula = "=IFERROR((C6+" & TRAT & ")/C5,0)"
    ws.Range("D4").NumberFormat = "0.0%"
    ws.Range("D3:D4").Font.Color = RGB(201, 162, 39): ws.Range("D4").Font.Bold = True: ws.Range("D4").Font.Size = 14
    ws.Range("D3").Font.Size = 8
    ' quantas OS faltam para 90%
    ws.Range("D6").Formula = "=IF(C6>=ROUNDUP(C5*0.9,0),""meta de 90% batida"",ROUNDUP(C5*0.9,0)-C6&"" OS faltam p/ 90%"")"
    ws.Range("D6").Font.Bold = True: ws.Range("D6").Font.Size = 10: ws.Range("D6").Font.Color = RGB(11, 22, 48)
    ws.Range("C7").Formula = "=COUNTIFS(tbOS[Visivel],1,tbOS[Fila],""concluída"")&"" concluídas + ""&COUNTIFS(tbOS[Visivel],1,tbOS[Fila],""aguardando material"")&"" aguardando material + ""&COUNTIFS(tbOS[Visivel],1,tbOS[Fila],""conserto externo"")&"" conserto externo + ""&COUNTIFS(tbOS[Visivel],1,tbOS[Fila],""cancelada"")&"" canceladas · ""&COUNTIFS(tbOS[Visivel],1,tbOS[Backlog],""S"")&"" pendentes nossas"""
    ws.Range("C7").Font.Size = 9: ws.Range("C7").Font.Color = RGB(91, 102, 131)
    BotaoRelatorio ws

    ' dados dos gráficos (aba Calc)
    Dim filas As Variant, r As Long, k As Variant, arr As Variant
    filas = Array("concluída", "não atendida", "aberta", "agendar", "aguardando material", "conserto externo", "cancelada")
    wc.Range("A1:B1").Value = Array("Fila", "OS")
    For i = 0 To UBound(filas)
        wc.Cells(i + 2, 1).Value = filas(i)
        wc.Cells(i + 2, 2).Formula = "=COUNTIFS(tbOS[Visivel],1,tbOS[Fila],A" & (i + 2) & ")"
    Next i
    BlocoCalc wc, 4, "Especialidade", OrdenarPorValor(cEsp, 12)
    BlocoCalc wc, 7, "Tipo", OrdenarPorValor(cTipo, 12)
    BlocoCalc wc, 10, "Setor", OrdenarPorValor(cSetor, 10)
    ' tempo da abertura até a hora inicial do 1º atendimento, por faixa
    Dim fx As Variant, lim As Variant
    fx = Array("Até 1 h", "1 a 4 h", "4 a 24 h", "1 a 3 dias", "3 a 7 dias", "Mais de 7 dias")
    lim = Array(0, 1, 4, 24, 72, 168, 1E+15)
    wc.Range("M1:N1").Value = Array("Tempo até o 1º atendimento", "OS")
    For i = 0 To 5
        wc.Cells(i + 2, 13).Value = fx(i)
        If i = 0 Then
            wc.Cells(i + 2, 14).Formula = "=COUNTIFS(tbOS[Visivel],1,tbOS[Espera_h],"">=0"",tbOS[Espera_h],""<=1"")"
        Else
            wc.Cells(i + 2, 14).Formula = "=COUNTIFS(tbOS[Visivel],1,tbOS[Espera_h],"">" & lim(i) & """,tbOS[Espera_h],""<=" & lim(i + 1) & """)"
        End If
    Next i

    ' filtros (segmentações) e gráficos
    Dim topo As Double, esq As Double, nomes As Variant, sc As SlicerCache
    topo = ws.Range("A8").Top: esq = ws.Range("A8").Left
    nomes = Array("Mês do pedido", "Fila", "Pendente de", "Especialidade", "Técnico", "Tipo", "Setor", "Criticidade")
    On Error Resume Next
    For i = 0 To UBound(nomes)
        Set sc = ThisWorkbook.SlicerCaches.Add2(lo, nomes(i))
        sc.Slicers.Add ws, , "sl" & i, nomes(i), topo, esq + i * 118, 113, 150
    Next i
    On Error GoTo 0
    topo = topo + 160
    Grafico ws, wc, "A2:B" & (UBound(filas) + 2), "OS por fila", esq, topo
    Grafico ws, wc, "D2:E" & (1 + UltimaLinha(wc, 4)), "OS por especialidade", esq + 455, topo
    Grafico ws, wc, "G2:H" & (1 + UltimaLinha(wc, 7)), "OS por tipo", esq, topo + 235
    Grafico ws, wc, "J2:K" & (1 + UltimaLinha(wc, 10)), "Setores que mais abrem OS", esq + 455, topo + 235
    Grafico ws, wc, "M2:N7", "Tempo até o 1º atendimento (da abertura à hora inicial)", esq, topo + 470
    CoresGrafico ws, "OS por especialidade", wc, 4
    CoresFaixas ws
    wc.Visible = xlSheetHidden
    ws.Activate: ws.Range("A1").Select
End Sub

Private Function CorEsp(ByVal nome As String) As Long
    nome = NormTxt(nome)
    Select Case True
        Case Left$(nome, 5) = "CIVIL": CorEsp = RGB(240, 124, 27)
        Case Left$(nome, 5) = "MARCE": CorEsp = RGB(31, 157, 85)
        Case Left$(nome, 5) = "ELETR": CorEsp = RGB(230, 184, 0)
        Case Left$(nome, 5) = "HIDRA": CorEsp = RGB(47, 111, 224)
        Case Left$(nome, 5) = "PINTU": CorEsp = RGB(142, 68, 173)
        Case Left$(nome, 5) = "CABIS": CorEsp = RGB(0, 163, 163)
        Case Left$(nome, 5) = "TRANS": CorEsp = RGB(127, 140, 141)
        Case Left$(nome, 5) = "ENGEN": CorEsp = RGB(192, 57, 43)
        Case Else: CorEsp = RGB(35, 71, 197)
    End Select
End Function

' cada especialidade com a sua cor (civil laranja, marcenaria verde, elétrica amarela, hidráulica azul...)
Private Sub CoresGrafico(ws As Worksheet, titulo As String, wc As Worksheet, col As Long)
    Dim sh As Shape, i As Long
    On Error Resume Next
    For Each sh In ws.Shapes
        If sh.HasChart Then
            If sh.Chart.ChartTitle.Text = titulo Then
                For i = 1 To sh.Chart.SeriesCollection(1).Points.Count
                    sh.Chart.SeriesCollection(1).Points(i).Format.Fill.ForeColor.RGB = CorEsp(CStr(wc.Cells(i + 1, col).Value))
                Next i
            End If
        End If
    Next sh
    On Error GoTo 0
End Sub

Private Sub CoresFaixas(ws As Worksheet)
    Dim sh As Shape, i As Long, cores As Variant
    cores = Array(RGB(31, 157, 85), RGB(88, 179, 104), RGB(230, 184, 0), RGB(240, 124, 27), RGB(224, 17, 95), RGB(142, 27, 63))
    On Error Resume Next
    For Each sh In ws.Shapes
        If sh.HasChart Then
            If Left$(sh.Chart.ChartTitle.Text, 11) = "Tempo até o" Then
                For i = 1 To 6
                    sh.Chart.SeriesCollection(1).Points(i).Format.Fill.ForeColor.RGB = cores(i - 1)
                Next i
            End If
        End If
    Next sh
    On Error GoTo 0
End Sub

Private Sub BotaoRelatorio(ws As Worksheet)
    Dim b As Object
    On Error Resume Next
    ws.Buttons("btnRelatorio").Delete
    On Error GoTo 0
    Set b = ws.Buttons.Add(ws.Range("H1").Left + 200, 4, 210, 30)
    b.Name = "btnRelatorio"
    b.Caption = "Gerar relatório (Excel)"
    b.OnAction = "GerarRelatorio"
End Sub

Private Function UltimaLinha(wc As Worksheet, col As Long) As Long
    UltimaLinha = Application.Max(1, Application.CountA(wc.Columns(col)) - 1)
End Function

Private Sub BlocoCalc(wc As Worksheet, col As Long, nome As String, itens As Variant)
    Dim i As Long
    wc.Cells(1, col).Value = nome: wc.Cells(1, col + 1).Value = "OS"
    If Not IsArray(itens) Then Exit Sub
    For i = 0 To UBound(itens)
        wc.Cells(i + 2, col).Value = itens(i)
        wc.Cells(i + 2, col + 1).Formula = "=COUNTIFS(tbOS[Visivel],1,tbOS[" & nome & "]," & wc.Cells(i + 2, col).Address(False, False) & ")"
    Next i
End Sub

Private Sub Kpi(ws As Worksheet, cel As String, titulo As String, formula As String, sub_ As String)
    ws.Range(cel).Value = titulo
    If formula <> "" Then ws.Range(cel).Offset(1, 0).Formula = formula
    If sub_ <> "" Then ws.Range(cel).Offset(2, 0).Value = sub_
End Sub

Private Sub Grafico(ws As Worksheet, wc As Worksheet, faixa As String, titulo As String, esq As Double, topo As Double)
    Dim sh As Shape
    Set sh = ws.Shapes.AddChart2(-1, xlBarClustered, esq, topo, 445, 225)
    With sh.Chart
        .SetSourceData wc.Range(faixa)
        .HasTitle = True: .ChartTitle.Text = titulo
        .HasLegend = False
        .Axes(xlCategory).ReversePlotOrder = True
        .SeriesCollection(1).HasDataLabels = True
        .SeriesCollection(1).Format.Fill.ForeColor.RGB = RGB(35, 71, 197)
        .PlotVisibleOnly = False
    End With
    sh.Placement = xlFreeFloating
End Sub

' fórmula do backlog na data de corte (opcional: filtro extra, ex.: ",tbOS[Especialidade],A5")
Private Function FormBacklog(extra As String) As String
    Dim E As String
    E = "(DataCorte+0.99999)"
    FormBacklog = "COUNTIFS(tbOS[Visivel],1,tbOS[Backlog],""S"",tbOS[Pedido],""<=""&" & E & INI & extra & ")" & _
        "+COUNTIFS(tbOS[Visivel],1,tbOS[Fila],""concluída"",tbOS[Pedido],""<=""&" & E & INI & ",tbOS[Término],"">""&" & E & extra & ")" & _
        "+COUNTIFS(tbOS[Visivel],1,tbOS[Fila],""cancelada"",tbOS[Pedido],""<=""&" & E & INI & ",tbOS[Término],"">""&" & E & extra & ")"
End Function

Private Sub MontarErros(errA() As Variant, nErr As Long)
    Dim ws As Worksheet, hdr As Variant, i As Long
    Set ws = ThisWorkbook.Worksheets.Add(After:=ThisWorkbook.Worksheets(SH_DASH)): ws.Name = SH_ERR
    ws.Range("A1").Value = "Para arrumar no MV (" & nErr & " OS)"
    ws.Range("A1").Font.Size = 16: ws.Range("A1").Font.Bold = True
    ws.Range("A2").Value = "Nada é alterado no MV por aqui: corrija lá e importe de novo. Execução acima de " & gMaxExec & " h (aba Config) ou sem hora de fim entra nos cálculos com 1 h provisória até ser corrigida; os demais erros ficam fora dos relatórios."
    hdr = Cabecalhos()
    ws.Range("A4").Value = "Problema"
    For i = 0 To NCOL - 2: ws.Cells(4, i + 2).Value = hdr(i): Next i
    If nErr > 0 Then ws.Range("A5").Resize(nErr, NCOL).Value = errA
    ws.Range("A4").Resize(1, NCOL).Font.Bold = True
    ws.Range("K:L,O:P").NumberFormat = "dd/mm/yyyy hh:mm"
    ws.Range("Y:Y").NumberFormat = "dd/mm/yyyy"
    ws.Columns("A").ColumnWidth = 45: ws.Columns("C").ColumnWidth = 45: ws.Columns("B,D:V").ColumnWidth = 14
    If nErr > 0 Then ws.Range("A4").Resize(nErr + 1, NCOL).AutoFilter
End Sub

Private Sub MontarBacklog(cEsp As Object, cPend As Object)
    Dim ws As Worksheet, E As String, filas As Variant, rot As Variant, faixas As Variant, i As Long, j As Long, r As Long
    Dim esp As Variant, base As String
    Set ws = ThisWorkbook.Worksheets(SH_BL)
    ws.Move After:=ThisWorkbook.Worksheets(SH_DASH)
    ws.Range("A1").Value = "Backlog mensal": ws.Range("A1").Font.Size = 18: ws.Range("A1").Font.Bold = True
    ws.Range("A3").Value = "Data início": ws.Range("A4").Value = "Data fim"
    ws.Range("A3:A4").Font.Bold = True
    ws.Range("B3:B4").NumberFormat = "dd/mm/yyyy"
    ws.Range("B3:B4").Interior.Color = RGB(255, 242, 204)
    ws.Range("C3").Value = "<- deixe as duas vazias para pegar TUDO o que foi carregado (pendente hoje)."
    ws.Range("C4").Value = "<- com datas: OS abertas no período que estavam pendentes na data fim. Os filtros do Dashboard também valem aqui."
    E = "(DataCorte+0.99999)"

    ws.Range("A5:F5").Value = Array("Fila", "0–7 dias", "8–15 dias", "16–30 dias", "Mais de 30 dias", "Total")
    filas = Array("aberta", "não atendida", "agendar")
    rot = Array("Aberta (aguardando triagem)", "Não atendida (triada, aguardando execução)", "Agendar")
    faixas = Array(",tbOS[Pedido],"">=""&(DataCorte-7)", _
                   ",tbOS[Pedido],"">=""&(DataCorte-15),tbOS[Pedido],""<""&(DataCorte-7)", _
                   ",tbOS[Pedido],"">=""&(DataCorte-30),tbOS[Pedido],""<""&(DataCorte-15)", _
                   ",tbOS[Pedido],""<""&(DataCorte-30)")
    For i = 0 To 2
        ws.Cells(6 + i, 1).Value = rot(i)
        For j = 0 To 3
            ws.Cells(6 + i, 2 + j).Formula = "=COUNTIFS(tbOS[Visivel],1,tbOS[Fila],""" & filas(i) & """,tbOS[Pedido],""<=""&" & E & INI & faixas(j) & ")"
        Next j
        ws.Cells(6 + i, 6).Formula = "=SUM(B" & (6 + i) & ":E" & (6 + i) & ")"
    Next i
    ws.Cells(9, 1).Value = "Pendentes no corte, resolvidas depois"
    For j = 0 To 3
        base = "COUNTIFS(tbOS[Visivel],1,tbOS[Fila],""{F}"",tbOS[Pedido],""<=""&" & E & INI & ",tbOS[Término],"">""&" & E & faixas(j) & ")"
        ws.Cells(9, 2 + j).Formula = "=" & Replace(base, "{F}", "concluída") & "+" & Replace(base, "{F}", "cancelada")
    Next j
    ws.Cells(9, 6).Formula = "=SUM(B9:E9)"
    ws.Cells(10, 1).Value = "Backlog total"
    For j = 2 To 6: ws.Cells(10, j).FormulaR1C1 = "=SUM(R6C:R9C)": Next j
    ws.Range("A5:F5,A10:F10").Font.Bold = True
    ws.Range("F10").Font.Color = RGB(224, 17, 95): ws.Range("F10").Font.Size = 16


    ws.Range("A12:B12").Value = Array("Backlog por especialidade", "OS"): ws.Range("A12:B12").Font.Bold = True
    r = 13
    For Each esp In OrdenarPorValor(cEsp, 0)
        ws.Cells(r, 1).Value = esp
        ws.Cells(r, 2).Formula = "=" & FormBacklog(",tbOS[Especialidade],A" & r)
        r = r + 1
    Next esp

    ' tratativas do backlog (frases padrão do planejamento) e quanto o % realizado sobe se resolver cada uma
    Dim tr As Variant, tv As Variant, rT As Long, q As Long, crit As String, totOS As String
    totOS = "MAX(1,SUBTOTAL(103,tbOS[OS]))"
    r = r + 1
    ws.Cells(r, 1).Resize(1, 4).Value = Array("Pendentes por tratativa (backlog)", "OS", "+% no total se resolver", "Mediana de dias parada")
    ws.Cells(r, 1).Resize(1, 4).Font.Bold = True
    r = r + 1: rT = r
    tr = Array("Feito, falta fechar", "Em execução", "Programado", "Supervisão", "Comprador", "Planejamento", "Gestor", "Sem tratativa (nada escrito ou só recado)")
    tv = Array("Feito, falta fechar", "Em execução", "Programado", "Supervisão", "Comprador", "Planejador", "Gestor", "")
    For q = 0 To UBound(tr)
        ws.Cells(r, 1).Value = tr(q)
        If tv(q) = "" Then
            ws.Cells(r, 2).Formula = "=COUNTIFS(tbOS[Visivel],1,tbOS[Backlog],""S"",tbOS[Pendente de],""Sem observação"")+COUNTIFS(tbOS[Visivel],1,tbOS[Backlog],""S"",tbOS[Pendente de],""Outro"")"
            ws.Cells(r, 4).Value = ""
        Else
            crit = "(tbOS[Pendente de]=""" & tv(q) & """)"
            ws.Cells(r, 2).Formula = "=COUNTIFS(tbOS[Visivel],1,tbOS[Backlog],""S"",tbOS[Pendente de],""" & tv(q) & """)"
            ws.Cells(r, 4).Formula = "=IFERROR(AGGREGATE(17,6,tbOS[Parado_dias]/((tbOS[Visivel]=1)*(tbOS[Backlog]=""S"")*" & crit & "*(tbOS[Parado_dias]<>"""")),2),"""")"
        End If
        ws.Cells(r, 3).Formula = "=B" & r & "/" & totOS
        r = r + 1
    Next q
    ws.Range(ws.Cells(rT, 3), ws.Cells(r - 1, 3)).NumberFormat = "+0.0%"
    ws.Range(ws.Cells(rT, 3), ws.Cells(r - 1, 3)).Font.Color = RGB(201, 162, 39)
    ws.Range(ws.Cells(rT, 3), ws.Cells(r - 1, 3)).Font.Bold = True
    ws.Cells(r, 1).Value = "Backlog com tratativa"
    ws.Cells(r, 2).Formula = "=SUM(B" & rT & ":B" & (r - 2) & ")"
    ws.Cells(r, 3).Formula = "=IFERROR(B" & r & "/(B" & r & "+B" & (r - 1) & "),0)": ws.Cells(r, 3).NumberFormat = "0%"
    ws.Cells(r, 4).Value = "do backlog tem tratativa escrita"
    ws.Range(ws.Cells(r, 1), ws.Cells(r, 3)).Font.Bold = True
    Dim rCom As Long: rCom = r
    r = r + 1
    ' cobrar primeiro = a mais antiga com tratativa
    Dim cTr As String
    cTr = "(tbOS[Visivel]=1)*(tbOS[Backlog]=""S"")*(tbOS[Pendente de]<>""Sem observação"")*(tbOS[Pendente de]<>""Outro"")*(tbOS[Pendente de]<>"""")*(tbOS[Pedido]<>"""")"
    ws.Cells(r, 1).Value = "Cobrar primeiro (mais antiga com tratativa)"
    ws.Cells(r, 5).Formula = "=IFERROR(AGGREGATE(15,6,tbOS[Pedido]/(" & cTr & "),1),"""")"
    ws.Cells(r, 5).NumberFormat = "dd/mm/yyyy"
    ws.Cells(r, 2).Formula = "=IFERROR(INDEX(tbOS[OS],MATCH(E" & r & ",tbOS[Pedido],0)),""-"")"
    ws.Cells(r, 3).Formula = "=IFERROR(INT(NOW()-E" & r & ")&"" dias"",""-"")"
    ws.Cells(r, 4).Formula = "=IFERROR(INDEX(tbOS[Pendente de],MATCH(E" & r & ",tbOS[Pedido],0)),"""")"
    ws.Range(ws.Cells(r, 1), ws.Cells(r, 4)).Font.Bold = True: ws.Cells(r, 1).Font.Color = RGB(224, 17, 95)
    Dim rCob As Long: rCob = r

    ' período das OS pendentes (mais antiga e mais nova até a data fim)
    Dim cBl As String
    cBl = "(tbOS[Visivel]=1)*(tbOS[Backlog]=""S"")*(tbOS[Pedido]<>"""")*(tbOS[Pedido]<=" & E & ")"
    ws.Range("A2").Value = "OS pendentes de"
    ws.Range("B2").Formula = "=IFERROR(AGGREGATE(15,6,tbOS[Pedido]/(" & cBl & "),1),"""")"
    ws.Range("C2").Value = "até"
    ws.Range("D2").Formula = "=IFERROR(AGGREGATE(14,6,tbOS[Pedido]/(" & cBl & "),1),"""")"
    ws.Range("E2").Formula = "=IFERROR(""mais antiga: OS ""&INDEX(tbOS[OS],MATCH(B2,tbOS[Pedido],0))&"" (""&INT(DataCorte-B2)&"" dias) · mais nova: OS ""&INDEX(tbOS[OS],MATCH(D2,tbOS[Pedido],0)),"""")"
    ws.Range("B2,D2").NumberFormat = "dd/mm/yyyy"
    ws.Range("A2:E2").Font.Bold = True: ws.Range("A2:E2").Font.Color = RGB(11, 31, 75)

    ' resumo pronto para copiar e mandar ao gerente
    ws.Range("H5").Font.Bold = True
    ws.Range("H6").Formula = "=""Backlog da manutenção ""&IF(AND(B3="""",B4=""""),""atual (todos os arquivos carregados)"",IF(B3="""","""",""de ""&TEXT(DAY(B3),""00"")&""/""&TEXT(MONTH(B3),""00"")&""/""&YEAR(B3)&"" "")&""até ""&TEXT(DAY(DataCorte),""00"")&""/""&TEXT(MONTH(DataCorte),""00"")&""/""&YEAR(DataCorte))"
    ws.Range("H7").Formula = "=""Backlog total: ""&F10"
    ws.Range("H8").Formula = "=""- Aguardando triagem (aberta): ""&F6"
    ws.Range("H9").Formula = "=""- Triadas, aguardando execução (não atendida): ""&F7"
    ws.Range("H10").Formula = "=""- Agendar: ""&F8"
    ws.Range("H11").Formula = "=""- Pendentes no corte e resolvidas depois: ""&F9"
    ws.Range("H12").Formula = "=""Por idade: 0–7 dias: ""&B10&"" | 8–15: ""&C10&"" | 16–30: ""&D10&"" | mais de 30: ""&E10"
    ws.Range("H13").Formula = "=""Aguardando material: ""&COUNTIFS(tbOS[Visivel],1,tbOS[Fila],""aguardando material"",tbOS[Pedido],""<=""&" & E & INI & ")&"" · Conserto externo: ""&COUNTIFS(tbOS[Visivel],1,tbOS[Fila],""conserto externo"",tbOS[Pedido],""<=""&" & E & INI & ")&"" (fora do backlog)"""
    Dim txtT As String
    txtT = "=""Por tratativa: """
    For q = 0 To UBound(tr)
        txtT = txtT & "&""" & IIf(q > 0, " | ", "") & Split(tr(q), " (")(0) & ": ""&B" & (rT + q)
    Next q
    ws.Range("H14").Formula = txtT
    ws.Range("H15").Formula = "=""Backlog com tratativa: ""&ROUND(C" & rCom & "*100,0)&""% · Cobrar primeiro: OS ""&B" & rCob & "&"" (""&C" & rCob & "&"")"""
    ws.Range("H5").Value = "Resumo para o gerente (selecione H6:H15 e copie)"
    ws.Columns("A").ColumnWidth = 42: ws.Columns("B:F").ColumnWidth = 13: ws.Columns("H").ColumnWidth = 70

    Dim b As Object
    Set b = ws.Buttons.Add(ws.Range("H1").Left, 4, 210, 28)
    b.Caption = "Registrar no histórico": b.OnAction = "RegistrarBacklog"
End Sub

Private Sub MontarEquipe(cTec As Object)
    Dim ws As Worksheet, r As Long, t As Variant
    Set ws = ThisWorkbook.Worksheets.Add(After:=ThisWorkbook.Worksheets(SH_BL)): ws.Name = SH_EQ
    ws.Range("A1").Value = "Homem-hora por técnico": ws.Range("A1").Font.Size = 18: ws.Range("A1").Font.Bold = True
    ws.Range("A2").Value = "Horas = soma de fim - início das execuções lançadas. Respeita os filtros do Dashboard."
    ws.Range("A4:D4").Value = Array("Técnico", "OS", "Horas", "Média h/OS"): ws.Range("A4:D4").Font.Bold = True
    r = 5
    For Each t In OrdenarPorValor(cTec, 0)
        ws.Cells(r, 1).Value = t
        ws.Cells(r, 2).Formula = "=COUNTIFS(tbOS[Visivel],1,tbOS[Técnico],A" & r & ")"
        ws.Cells(r, 3).Formula = "=SUMIFS(tbOS[Execucao_h],tbOS[Visivel],1,tbOS[Técnico],A" & r & ")"
        ws.Cells(r, 4).Formula = "=IFERROR(C" & r & "/B" & r & ","""")"
        r = r + 1
    Next t
    ws.Range("C:D").NumberFormat = "0.0"
    ws.Columns("A").ColumnWidth = 42: ws.Columns("B:D").ColumnWidth = 13
End Sub

Private Sub MontarTempos(cEsp As Object, cTipo As Object, cCrit As Object)
    Dim ws As Worksheet, r As Long
    Set ws = ThisWorkbook.Worksheets.Add(After:=ThisWorkbook.Worksheets(SH_EQ)): ws.Name = SH_TP
    ws.Range("A1").Value = "Tempos de atendimento (h)": ws.Range("A1").Font.Size = 18: ws.Range("A1").Font.Bold = True
    ws.Range("A2").Value = "Espera = início do 1º atendimento - pedido. Execução = fim - início. Respeita os filtros do Dashboard."
    r = 4
    r = BlocoTempo(ws, r, "Especialidade", OrdenarPorValor(cEsp, 0))
    r = BlocoTempo(ws, r + 1, "Tipo", OrdenarPorValor(cTipo, 0))
    r = BlocoTempo(ws, r + 1, "Criticidade", OrdenarPorValor(cCrit, 0))
    ws.Range("C:F").NumberFormat = "0.0"
    ws.Columns("A").ColumnWidth = 34: ws.Columns("B:F").ColumnWidth = 16
End Sub

Private Function BlocoTempo(ws As Worksheet, r As Long, col As String, itens As Variant) As Long
    Dim it As Variant, c As String
    ws.Cells(r, 1).Resize(1, 6).Value = Array(col, "OS", "Espera mediana", "Espera média", "Execução média", "Pedido -> término")
    ws.Cells(r, 1).Resize(1, 6).Font.Bold = True
    r = r + 1
    If IsArray(itens) Then
        For Each it In itens
            c = "A" & r
            ws.Cells(r, 1).Value = it
            ws.Cells(r, 2).Formula = "=COUNTIFS(tbOS[Visivel],1,tbOS[" & col & "]," & c & ")"
            ws.Cells(r, 3).FormulaArray = "=IFERROR(MEDIAN(IF((tbOS[Visivel]=1)*(tbOS[" & col & "]=" & c & ")*(tbOS[Espera_h]<>""""),tbOS[Espera_h])),"""")"
            ws.Cells(r, 4).Formula = "=IFERROR(AVERAGEIFS(tbOS[Espera_h],tbOS[Visivel],1,tbOS[" & col & "]," & c & "),"""")"
            ws.Cells(r, 5).Formula = "=IFERROR(AVERAGEIFS(tbOS[Execucao_h],tbOS[Visivel],1,tbOS[" & col & "]," & c & ",tbOS[Execucao_h],"">0""),"""")"
            ws.Cells(r, 6).Formula = "=IFERROR(AVERAGEIFS(tbOS[Total_h],tbOS[Visivel],1,tbOS[" & col & "]," & c & "),"""")"
            r = r + 1
        Next it
    End If
    BlocoTempo = r
End Function

Private Sub MontarArquivos()
    Dim ws As Worksheet, r As Long, it As Variant, ic As String
    Set ws = ThisWorkbook.Worksheets.Add(After:=ThisWorkbook.Worksheets(SH_DASH)): ws.Name = SH_ARQ
    ws.Range("A1").Value = "Arquivos carregados": ws.Range("A1").Font.Size = 16: ws.Range("A1").Font.Bold = True
    ws.Range("A2").Value = ChrW(10003) & " carregado  |  " & ChrW(9888) & " arquivo sem OS (fila vazia no MV)  |  " & ChrW(10007) & " não foi lido. Faltou algum? Importe de novo selecionando todos."
    ws.Range("A4:E4").Value = Array("", "Arquivo", "OS", "Situação", "Tamanho (KB)"): ws.Range("A4:E4").Font.Bold = True
    r = 5
    For Each it In gLog
        Select Case it(1)
            Case "OK": ic = ChrW(10003): ws.Cells(r, 1).Font.Color = RGB(26, 143, 76)
            Case "VAZIO": ic = ChrW(9888): ws.Cells(r, 1).Font.Color = RGB(179, 90, 0)
            Case Else: ic = ChrW(10007): ws.Cells(r, 1).Font.Color = RGB(224, 17, 95)
        End Select
        ws.Cells(r, 1).Value = ic: ws.Cells(r, 1).Font.Bold = True: ws.Cells(r, 1).Font.Size = 14
        ws.Cells(r, 2).Value = it(0): ws.Cells(r, 3).Value = it(2)
        If it(1) = "OK" Then ws.Cells(r, 4).Value = "carregado" Else ws.Cells(r, 4).Value = it(3)
        ws.Cells(r, 5).Value = Round(it(4) / 1024, 0)
        r = r + 1
    Next it
    ws.Columns("A").ColumnWidth = 4: ws.Columns("B").ColumnWidth = 45: ws.Columns("C").ColumnWidth = 10
    ws.Columns("D").ColumnWidth = 45: ws.Columns("E").ColumnWidth = 14
End Sub

Private Sub ExtrairZip(zipPath As String, caminhos As Collection)
    Dim fso As Object, dest As String, sh As Object, n As Long, ultimo As Long, t As Single
    Set fso = CreateObject("Scripting.FileSystemObject")
    Randomize
    dest = Environ$("TEMP") & "\GeradorOS_" & Format(Now, "yyyymmddhhnnss") & "_" & Int(Rnd * 10000)
    fso.CreateFolder dest
    Set sh = CreateObject("Shell.Application")
    sh.Namespace(CVar(dest)).CopyHere sh.Namespace(CVar(zipPath)).Items, 4 + 16
    t = Timer
    ultimo = -1
    Do
        DoEvents
        n = ContarArquivos(fso.GetFolder(dest))
        If n > 0 And n = ultimo Then Exit Do
        ultimo = n
        Application.Wait Now + TimeSerial(0, 0, 1)
    Loop While Timer - t < 60
    ColetarCSV fso.GetFolder(dest), caminhos
End Sub

Private Function ContarArquivos(pasta As Object) As Long
    Dim sf As Object, n As Long
    n = pasta.Files.Count
    For Each sf In pasta.SubFolders
        n = n + ContarArquivos(sf)
    Next sf
    ContarArquivos = n
End Function

Private Sub ColetarCSV(pasta As Object, caminhos As Collection)
    Dim f As Object, sf As Object
    For Each f In pasta.Files
        If LCase$(Right$(f.Name, 4)) = ".csv" Or LCase$(Right$(f.Name, 4)) = ".txt" Then caminhos.Add f.Path
    Next f
    For Each sf In pasta.SubFolders
        ColetarCSV sf, caminhos
    Next sf
End Sub

'------------------------------------------------------------ histórico do backlog
Private Sub GarantirHistorico()
    Dim ws As Worksheet
    If Existe(SH_HIST) Then Exit Sub
    Set ws = ThisWorkbook.Worksheets.Add(After:=ThisWorkbook.Worksheets(ThisWorkbook.Worksheets.Count))
    ws.Name = SH_HIST
    ws.Range("A1").Value = "Histórico do backlog (um registro por mês)": ws.Range("A1").Font.Size = 16: ws.Range("A1").Font.Bold = True
    ws.Range("A3:I3").Value = Array("Data de corte", "Backlog total", "Aberta", "Não atendida", "Agendar", _
        "Resolvidas depois", "Aguardando material", "Conserto externo", "Registrado em")
    ws.Range("A3:I3").Font.Bold = True
    ws.Columns("A:I").ColumnWidth = 16
End Sub

Public Sub RegistrarBacklog()
    Dim wb As Worksheet, wh As Worksheet, r As Long
    If Not Existe(SH_BL) Then MsgBox "Importe os CSVs primeiro.", vbExclamation: Exit Sub
    GarantirHistorico
    Set wb = ThisWorkbook.Worksheets(SH_BL): Set wh = ThisWorkbook.Worksheets(SH_HIST)
    r = 4
    Dim dc As Date
    dc = Application.Evaluate("DataCorte")
    Do While wh.Cells(r, 1).Value <> ""
        If wh.Cells(r, 1).Value = dc Then Exit Do
        r = r + 1
    Loop
    wh.Cells(r, 1).Resize(1, 9).Value = Array(dc, wb.Range("F10").Value, wb.Range("F6").Value, _
        wb.Range("F7").Value, wb.Range("F8").Value, wb.Range("F9").Value, wb.Range("B13").Value, wb.Range("B14").Value, Now)
    wh.Cells(r, 1).NumberFormat = "dd/mm/yyyy": wh.Cells(r, 9).NumberFormat = "dd/mm/yyyy hh:mm"
    MsgBox "Backlog de " & Format(dc, "dd/mm/yyyy") & " registrado na aba Histórico.", vbInformation
End Sub

'------------------------------------------------------------ utilidades
'------------------------------------------------------------ OS repetidas (em aberto)
' Mesmo setor e descrição parecida, só OS em aberto (backlog ou terceiros). Palavras genéricas não contam,
' palavras raras pesam mais, lugares diferentes (sala x WC) não se juntam. É só um aviso para conferir.
Private Function PalavrasRep(ByVal t As String) As Collection
    Dim c As New Collection, w As Variant, sw As String, d As Object
    Set d = CreateObject("Scripting.Dictionary")
    sw = " SOLICITO SOLICITAMOS SOLICITA SOLICITACAO FAVOR GENTILEZA PARA COM DOS DAS NOS NAS QUE UMA UNS UMAS ESTA ESTAO ESTAR MESMA MESMO MANUTENCAO REALIZAR VERIFICAR VERIFICACAO NECESSARIO PRECISA PRECISAMOS PELO PELA AOS SEU SUA SEM MAIS MUITO URGENTE URGENCIA ENCONTRA POR BOM DIA TARDE NOITE PFV FMS VMS DEPARTAMENTO VISTO CONCERTO SAINDO OBRIGADO AGRADECO EVIDENCIADO EVIDENCIADA ADEQUACAO ADEQUAR DANIFICADO DANIFICADA DANIFICADOS DANIFICADAS QUEBRADO QUEBRADA QUEBRADOS QUEBRADAS CONSERTO CONSERTAR REPARO REPARAR TROCA TROCAR AJUSTE AJUSTAR ARRUMAR PROBLEMA DEFEITO ESTRAGADO ESTRAGADA SOLTO SOLTA LOCAL SETOR FUNCIONANDO NAO APRESENTANDO APRESENTA "
    t = Replace(Replace(NormTxt(t), "/", " "), ".", " ")
    For Each w In Split(t, " ")
        If w <> "" Then
            If (Len(w) >= 3 And InStr(1, sw, " " & w & " ", vbBinaryCompare) = 0) Or IsNumeric(w) Then
                If Not d.Exists(w) Then
                    d(w) = 1
                    c.Add CStr(w)
                End If
            End If
        End If
    Next w
    Set PalavrasRep = c
End Function

Private Function PareceW(a As String, b As String) As Boolean
    If a = b Then PareceW = True: Exit Function
    If IsNumeric(a) Or IsNumeric(b) Then Exit Function
    If Len(a) > 3 And Len(b) > 3 Then
        If 1 - Lev(a, b) / Application.Max(Len(a), Len(b)) >= 0.8 Then PareceW = True: Exit Function
    End If
    If Len(a) >= 5 And Len(b) >= 5 Then PareceW = (Left$(a, 5) = Left$(b, 5))
End Function

Private Function TemPalavra(c As Collection, w As String) As Boolean
    Dim x As Variant
    For Each x In c
        If PareceW(CStr(x), w) Then TemPalavra = True: Exit Function
    Next x
End Function

Private Function LugarDif(A As Collection, B As Collection) As Boolean
    Dim lg As String, la As New Collection, lb As New Collection, x As Variant, y As Variant
    lg = " CORREDOR BANHEIRO BANHEIROS SANITARIO WC SALA QUARTO LEITO LEITOS PORTA RECEPCAO COPA POSTO EXPURGO VESTIARIO ESCADA ELEVADOR CONSULTORIO DML ALMOXARIFADO CORREDORES HALL ENTRADA JANELA TETO FORRO PISO PAREDE COZINHA REFEITORIO LAVABO ENFERMARIA BOX ISOLAMENTO "
    For Each x In A
        If InStr(lg, " " & x & " ") > 0 Then la.Add CStr(x)
    Next x
    For Each x In B
        If InStr(lg, " " & x & " ") > 0 Then lb.Add CStr(x)
    Next x
    If la.Count = 0 Or lb.Count = 0 Then Exit Function
    For Each x In la
        For Each y In lb
            If x = y Or x & "S" = y Or y & "S" = x Then Exit Function
        Next y
    Next x
    LugarDif = True
End Function

Private Function SimDesc(A As Collection, B As Collection, peso As Object, tira As String) As Double
    Dim x As Variant, na As Long, nb As Long, achouNum As Boolean, k As Long, kt As Long
    Dim sm As Double, sa As Double, sb As Double, p As Double
    If A.Count = 0 Or B.Count = 0 Then Exit Function
    ' leito 3 x leito 5: números diferentes = não é a mesma coisa
    For Each x In A
        If IsNumeric(x) Then
            na = na + 1
            If TemNum(B, CStr(x)) Then achouNum = True
        End If
    Next x
    For Each x In B
        If IsNumeric(x) Then nb = nb + 1
    Next x
    If na > 0 And nb > 0 And Not achouNum Then Exit Function
    If LugarDif(A, B) Then Exit Function
    For Each x In A
        p = PesoW(CStr(x), peso, tira): sa = sa + p
        If TemPalavra(B, CStr(x)) Then
            k = k + 1: sm = sm + p
            If Not IsNumeric(x) Then kt = kt + 1
        End If
    Next x
    For Each x In B
        sb = sb + PesoW(CStr(x), peso, tira)
    Next x
    If kt < 2 Or sa + sb = 0 Then Exit Function
    SimDesc = 2 * sm / (sa + sb)
End Function

Private Function TemNum(c As Collection, n As String) As Boolean
    Dim x As Variant
    For Each x In c
        If x = n Then TemNum = True: Exit Function
    Next x
End Function

Private Function PesoW(w As String, peso As Object, tira As String) As Double
    ' palavra que é o nome do setor/localidade pesa pouco; palavra rara pesa muito
    If InStr(1, tira, " " & w & " ", vbBinaryCompare) > 0 Then PesoW = 0.3: Exit Function
    If peso.Exists(Left$(w, 5)) Then PesoW = peso(Left$(w, 5)) Else PesoW = 1
End Function

Private Function RaizUF(pai() As Long, ByVal x As Long) As Long
    Do While pai(x) <> x
        pai(x) = pai(pai(x)): x = pai(x)
    Loop
    RaizUF = x
End Function

Private Function PesoRep(fila As String, pend As String) As Long
    If fila = "aguardando material" Or fila = "conserto externo" Or pend = "Feito, falta fechar" Then
        PesoRep = 0
    ElseIf pend = "Em execução" Or pend = "Programado" Or pend = "Comprador" Or pend = "Externo" Or pend = "Material" Then
        PesoRep = 1
    ElseIf pend = "Supervisão" Or pend = "Planejador" Or pend = "Gestor" Then
        PesoRep = 2
    Else
        PesoRep = 3
    End If
End Function

Private Sub MontarRepetidas(okA() As Variant, nOk As Long)
    Dim ws As Worksheet, i As Long, j As Long, n As Long, idx() As Long, w() As Collection, x As Variant
    Dim df As Object, peso As Object, k As Variant, sim As Double, loc As Boolean, tira As String
    ' fica na mesma aba "Para arrumar", embaixo dos erros de data/hora
    Dim r0 As Long
    Set ws = ThisWorkbook.Worksheets(SH_ERR)
    r0 = ws.Cells.Find("*", , xlValues, , xlByRows, xlPrevious).Row + 4
    ws.Cells(r0, 1).Value = "OS repetidas em aberto": ws.Cells(r0, 1).Font.Size = 16: ws.Cells(r0, 1).Font.Bold = True
    ws.Cells(r0 + 1, 1).Value = "Mesmo setor e descrição parecida, só OS em aberto (fechadas e canceladas não entram). A primeira de cada grupo é a que fica; as outras: fechar no MV informando a OS que já está tratando. É só um aviso para conferir."
    If nOk = 0 Then Exit Sub
    Application.StatusBar = "Procurando OS repetidas..."
    ' peso de cada palavra pela raridade (palavra que aparece em muitas OS vale pouco)
    Set df = CreateObject("Scripting.Dictionary"): Set peso = CreateObject("Scripting.Dictionary")
    ReDim w(1 To nOk)
    Dim vistos As Object
    For i = 1 To nOk
        Set w(i) = PalavrasRep(CStr(okA(i, 2)))
        Set vistos = CreateObject("Scripting.Dictionary")
        For Each x In w(i)
            If Not vistos.Exists(Left$(x, 5)) Then
                vistos(Left$(x, 5)) = 1
                df(Left$(x, 5)) = df(Left$(x, 5)) + 1
            End If
        Next x
    Next i
    For Each k In df.Keys: peso(k) = Log((nOk + 1) / df(k)): Next k
    ' só as OS em aberto (backlog ou terceiros)
    ReDim idx(1 To nOk)
    For i = 1 To nOk
        If okA(i, 19) = "S" Or okA(i, 20) = "S" Then
            n = n + 1: idx(n) = i
        End If
    Next i
    If n < 2 Then Exit Sub
    Dim pai() As Long
    ReDim pai(1 To n)
    For i = 1 To n: pai(i) = i: Next i
    For i = 1 To n - 1
        For j = i + 1 To n
            If okA(idx(i), 8) = okA(idx(j), 8) Then
                tira = " " & NormTxt(okA(idx(i), 8) & " " & okA(idx(i), 9) & " " & okA(idx(j), 9)) & " "
                sim = SimDesc(w(idx(i)), w(idx(j)), peso, tira)
                loc = (CStr(okA(idx(i), 9)) <> "" And okA(idx(i), 9) = okA(idx(j), 9))
                If sim >= 0.6 Or (sim >= 0.45 And loc) Then pai(RaizUF(pai, i)) = RaizUF(pai, j)
            End If
        Next j
    Next i
    ' grupos com 2 ou mais
    Dim grp As Object, rt As Long, g As Variant, membros As Collection
    Set grp = CreateObject("Scripting.Dictionary")
    For i = 1 To n
        rt = RaizUF(pai, i)
        If Not grp.Exists(rt) Then grp.Add rt, New Collection
        grp(rt).Add idx(i)
    Next i
    Dim out() As Variant, nOut As Long, nG As Long, nFechar As Long, nAnd As Long
    ReDim out(1 To n, 1 To 11)
    For Each g In grp.Keys
        Set membros = grp(g)
        If membros.Count > 1 Then
            nG = nG + 1
            ' ordena: a mais adiantada primeiro, depois a mais antiga
            Dim arr() As Long, a As Long, b As Long, t As Long, pa As Long, pb As Long
            ReDim arr(1 To membros.Count)
            For a = 1 To membros.Count: arr(a) = membros(a): Next a
            For a = 1 To UBound(arr) - 1
                For b = a + 1 To UBound(arr)
                    pa = PesoRep(CStr(okA(arr(a), 3)), CStr(okA(arr(a), 23))): pb = PesoRep(CStr(okA(arr(b), 3)), CStr(okA(arr(b), 23)))
                    If pb < pa Or (pb = pa And okA(arr(b), 10) < okA(arr(a), 10)) Then t = arr(a): arr(a) = arr(b): arr(b) = t
                Next b
            Next a
            Dim p0 As Long, anda As Boolean, onde As String
            p0 = arr(1): anda = (PesoRep(CStr(okA(p0, 3)), CStr(okA(p0, 23))) <= 2)
            If okA(p0, 20) = "S" Then
                onde = " (" & okA(p0, 3) & ")"
            ElseIf CStr(okA(p0, 23)) = "Sem observação" Or CStr(okA(p0, 23)) = "Outro" Or CStr(okA(p0, 23)) = "" Then
                onde = ""
            Else
                onde = " (" & Replace(CStr(okA(p0, 23)), "Planejador", "Planejamento") & ")"
            End If
            For a = 1 To UBound(arr)
                nOut = nOut + 1
                out(nOut, 1) = nG
                If a = 1 Then
                    out(nOut, 2) = IIf(anda, "Manter: já em andamento" & onde, "Manter: tratar esta (mais antiga)")
                Else
                    out(nOut, 2) = IIf(anda, "Fechar: informar que já está sendo tratada na OS " & okA(p0, 1) & onde, "Fechar: juntar na OS " & okA(p0, 1))
                    nFechar = nFechar + 1
                    If anda Then nAnd = nAnd + 1
                End If
                out(nOut, 3) = okA(arr(a), 1): out(nOut, 4) = okA(arr(a), 3): out(nOut, 5) = okA(arr(a), 23)
                out(nOut, 6) = okA(arr(a), 10): out(nOut, 7) = okA(arr(a), 8): out(nOut, 8) = okA(arr(a), 9)
                out(nOut, 9) = okA(arr(a), 7): out(nOut, 10) = okA(arr(a), 2): out(nOut, 11) = okA(arr(a), 22)
            Next a
        End If
    Next g
    ws.Cells(r0 + 3, 1).Resize(1, 4).Value = Array("OS repetidas para tratar (fechar)", "Já tratadas em outra OS", "Ainda sem tratativa (juntar numa OS só)", "Grupos")
    ws.Cells(r0 + 4, 1).Resize(1, 4).Value = Array(nFechar, nAnd, nFechar - nAnd, nG)
    ws.Cells(r0 + 3, 1).Resize(1, 4).Font.Color = RGB(91, 102, 131)
    ws.Cells(r0 + 4, 1).Resize(1, 4).Font.Size = 18: ws.Cells(r0 + 4, 1).Resize(1, 4).Font.Bold = True
    ws.Cells(r0 + 6, 1).Resize(1, 11).Value = Array("Grupo", "O que fazer", "OS", "Fila", "Pendente de", "Pedido", "Setor", "Localidade", "Solicitante", "Descrição", "Observação")
    ws.Cells(r0 + 6, 1).Resize(1, 11).Font.Bold = True: ws.Cells(r0 + 6, 1).Resize(1, 11).Interior.Color = RGB(214, 51, 108): ws.Cells(r0 + 6, 1).Resize(1, 11).Font.Color = vbWhite
    If nOut > 0 Then
        ws.Cells(r0 + 7, 1).Resize(nOut, 11).Value = out
        ws.Cells(r0 + 7, 6).Resize(nOut, 1).NumberFormat = "dd/mm/yyyy hh:mm"
        For i = 1 To nOut
            If Left$(out(i, 2), 6) = "Manter" Then ws.Cells(r0 + 6 + i, 2).Font.Color = RGB(18, 122, 58) Else ws.Cells(r0 + 6 + i, 2).Font.Color = RGB(179, 90, 0)
            If out(i, 1) Mod 2 = 0 Then ws.Range(ws.Cells(r0 + 6 + i, 1), ws.Cells(r0 + 6 + i, 11)).Interior.Color = RGB(245, 247, 250)
        Next i
        ws.Cells(r0 + 7, 1).Resize(nOut, 11).VerticalAlignment = xlTop
    Else
        ws.Cells(r0 + 7, 1).Value = "Nenhuma OS repetida em aberto."
    End If
End Sub

'------------------------------------------------------------ relatório em Excel (arquivo novo)
' Usa o que está filtrado no Dashboard (inclusive o filtro "Mês do pedido") e gera um arquivo novo,
' só com valores, com capa (título, período, filtros, índice e regras) e um relatório por aba.
Public Sub GerarRelatorio()
    Dim esc As String, op As Variant, nomes As Variant, i As Long, quer As Object
    If Not Existe(SH_DASH) Then MsgBox "Importe os CSVs primeiro.", vbExclamation, "Gerador de OS": Exit Sub
    esc = InputBox("Quais relatórios? Digite os números separados por vírgula:" & vbCrLf & vbCrLf & _
        "1 Indicadores do período" & vbCrLf & "2 Backlog (tratativas, cobrar primeiro)" & vbCrLf & "3 Tempos de atendimento" & vbCrLf & _
        "4 Homem-hora por técnico" & vbCrLf & "5 Para arrumar no MV (erros de data/hora e OS repetidas)" & vbCrLf & "6 Lista de OS" & vbCrLf & vbCrLf & _
        "O período e os filtros são os que estão marcados no Dashboard (use 'Mês do pedido' para escolher o mês).", "Gerar relatório", "1,2,3,4,5,6")
    If Trim$(esc) = "" Then Exit Sub
    Set quer = CreateObject("Scripting.Dictionary")
    For Each op In Split(Replace(esc, " ", ""), ",")
        If IsNumeric(op) Then
            If CLng(op) >= 1 And CLng(op) <= 6 Then quer(CLng(op)) = 1
        End If
    Next op
    If quer.Count = 0 Then Exit Sub

    Application.ScreenUpdating = False
    Application.StatusBar = "Gerando o relatório..."
    Dim wb As Workbook, wsD As Worksheet, wc As Worksheet, per As String, fil As String
    Set wsD = ThisWorkbook.Worksheets(SH_DASH): Set wc = ThisWorkbook.Worksheets(SH_CALC)
    Application.Calculate
    per = PeriodoTexto(wsD): fil = FiltrosTexto()
    Set wb = Workbooks.Add(xlWBATWorksheet)
    Dim capa As Worksheet
    Set capa = wb.Worksheets(1): capa.Name = "Capa"

    Dim ws As Worksheet, r As Long, lista As New Collection
    If quer.Exists(1) Then
        Set ws = wb.Worksheets.Add(After:=wb.Worksheets(wb.Worksheets.Count)): ws.Name = "Indicadores do período"
        CabecalhoRel ws, "Indicadores do período", per, fil
        ws.Range("B5:F5").Value = Array("Total de OS", "Realizadas", "% realizado", "Pendentes nossas", "Faltam p/ 90%")
        ws.Range("B6").Value = wsD.Range("C5").Value: ws.Range("C6").Value = wsD.Range("C6").Value
        ws.Range("D6").Value = wsD.Range("D5").Value: ws.Range("D6").NumberFormat = "0.0%"
        ws.Range("E6").Value = wsD.Range("C5").Value - wsD.Range("C6").Value
        ws.Range("F6").Value = Application.Max(0, Application.RoundUp(wsD.Range("C5").Value * 0.9, 0) - wsD.Range("C6").Value)
        Cartoes ws, "B5:F6"
        If wsD.Range("D5").Value >= 0.9 Then ws.Range("D6").Font.Color = RGB(18, 122, 58) Else ws.Range("D6").Font.Color = RGB(214, 51, 108)
        r = 8
        r = TabelaRel(ws, r, "Resumo", Array("Indicador", "Valor"), Array( _
            Array("Realizadas (concluídas + aguardando material + conserto externo + canceladas)", wsD.Range("C6").Value), _
            Array("% se resolver as do backlog com tratativa", Format(wsD.Range("D4").Value, "0.0%")), _
            Array("Aguardando material", wsD.Range("E5").Value), _
            Array("Conserto externo", wsD.Range("F5").Value), _
            Array("Atendidas em até 24 h", Format(wsD.Range("A5").Value, "0%")), _
            Array("Espera até o 1º atendimento - mediana (h)", wsD.Range("G5").Value), _
            Array("Espera até o 1º atendimento - " & wsD.Range("G6").Value, ""), _
            Array("Homem-hora lançado (h)", wsD.Range("I5").Value)))
        r = TabelaCalc(ws, r, wc, 1, "Por fila")
        r = TabelaCalc(ws, r, wc, 4, "Por especialidade")
        r = TabelaCalc(ws, r, wc, 7, "Por tipo")
        r = TabelaCalc(ws, r, wc, 10, "Setores que mais abrem OS")
        r = TabelaCalc(ws, r, wc, 13, "Tempo da abertura até a hora inicial do 1º atendimento")
        FormatarRel ws
        lista.Add Array(ws.Name, "Total, realizadas e %, faltam para 90%, terceiros, tempos, por fila, especialidade, tipo e setor")
    End If
    If quer.Exists(2) Then CopiarAba wb, SH_BL, "Backlog", per, fil, lista, "Pendentes até a data (desde o começo): fila e idade, tratativas, cobrar primeiro, resumo para o gerente"
    If quer.Exists(3) Then CopiarAba wb, SH_TP, "Tempos de atendimento", per, fil, lista, "Espera até o 1º atendimento e execução por especialidade, tipo e criticidade"
    If quer.Exists(4) Then CopiarAba wb, SH_EQ, "Homem-hora por técnico", per, fil, lista, "OS, horas e média por técnico"
    If quer.Exists(5) Then CopiarAba wb, SH_ERR, "Para arrumar no MV", per, fil, lista, "OS com erro de data/hora para corrigir no MV e OS repetidas em aberto (quais fechar)"
    If quer.Exists(6) Then
        Set ws = wb.Worksheets.Add(After:=wb.Worksheets(wb.Worksheets.Count)): ws.Name = "Lista de OS"
        CabecalhoRel ws, "Lista de OS", per, fil
        Dim lo As ListObject
        Set lo = wsD.ListObjects("tbOS")
        lo.Range.Resize(, NCOL - 1).SpecialCells(xlCellTypeVisible).Copy
        ws.Range("B5").PasteSpecial xlPasteValuesAndNumberFormats
        Application.CutCopyMode = False
        ws.Range("B5").Resize(1, NCOL - 1).Font.Bold = True
        ws.Range("B5").Resize(1, NCOL - 1).Interior.Color = RGB(214, 51, 108): ws.Range("B5").Resize(1, NCOL - 1).Font.Color = vbWhite
        ws.Range("B5").CurrentRegion.AutoFilter
        FormatarRel ws
        ws.Columns("C").ColumnWidth = 50: ws.Columns("W").ColumnWidth = 50
        lista.Add Array(ws.Name, "As OS do período com todos os campos (com filtro no cabeçalho)")
    End If
    MontarCapa capa, per, fil, lista
    capa.Activate
    Application.StatusBar = False
    Application.ScreenUpdating = True
    Dim nomeArq As Variant
    nomeArq = Application.GetSaveAsFilename("Relatorio_OS_HEV_" & Format(Date, "yyyy-mm-dd") & ".xlsx", "Pasta de trabalho do Excel (*.xlsx), *.xlsx", , "Salvar relatório")
    If nomeArq <> False Then wb.SaveAs CStr(nomeArq), 51
End Sub

Private Function PeriodoTexto(wsD As Worksheet) As String
    Dim sc As SlicerCache, it As SlicerItem, sel As String, n As Long, tot As Long, mn As Variant, mx As Variant
    On Error Resume Next
    For Each sc In ThisWorkbook.SlicerCaches
        If sc.SourceName = "Mês do pedido" Or InStr(sc.Name, "Mês") > 0 Then
            For Each it In sc.SlicerItems
                tot = tot + 1
                If it.Selected Then n = n + 1: sel = sel & IIf(sel = "", "", ", ") & it.Name
            Next it
        End If
    Next sc
    mn = wsD.Evaluate("AGGREGATE(5,5,tbOS[Pedido])"): mx = wsD.Evaluate("AGGREGATE(4,5,tbOS[Pedido])")
    On Error GoTo 0
    If n = 0 Or n = tot Then PeriodoTexto = "tudo o que foi carregado" Else PeriodoTexto = "mês do pedido: " & sel
    If IsNumeric(mn) And IsNumeric(mx) Then
        If mn > 0 Then PeriodoTexto = PeriodoTexto & " (OS abertas de " & Format(mn, "dd/mm/yyyy") & " a " & Format(mx, "dd/mm/yyyy") & ")"
    End If
End Function

Private Function FiltrosTexto() As String
    Dim sc As SlicerCache, it As SlicerItem, sel As String, n As Long, tot As Long, t As String
    On Error Resume Next
    For Each sc In ThisWorkbook.SlicerCaches
        If InStr(sc.Name, "Mês") = 0 And sc.SourceName <> "Mês do pedido" Then
            If Not sc.FilterCleared Then
                sel = "": n = 0: tot = 0
                For Each it In sc.SlicerItems
                    tot = tot + 1
                    If it.Selected Then n = n + 1: sel = sel & IIf(sel = "", "", ", ") & it.Name
                Next it
                If n > 0 And n < tot Then t = t & IIf(t = "", "", " · ") & sc.Slicers(1).Caption & ": " & sel
            End If
        End If
    Next sc
    On Error GoTo 0
    If t = "" Then t = "sem filtros"
    FiltrosTexto = t
End Function

Private Sub CabecalhoRel(ws As Worksheet, titulo As String, per As String, fil As String)
    ActiveWindow.DisplayGridlines = False
    ws.Columns("A").ColumnWidth = 2
    ws.Range("B1").Value = "RELATÓRIO DE ORDENS DE SERVIÇO · MANUTENÇÃO · HOSPITAL EDMUNDO VASCONCELOS"
    ws.Range("B1").Font.Bold = True: ws.Range("B1").Font.Size = 9: ws.Range("B1").Font.Color = RGB(214, 51, 108)
    ws.Range("B2").Value = titulo
    ws.Range("B2:G2").Interior.Color = RGB(15, 42, 74)
    ws.Range("B2").Font.Size = 16: ws.Range("B2").Font.Bold = True: ws.Range("B2").Font.Color = vbWhite
    ws.Rows(2).RowHeight = 30: ws.Range("B2").VerticalAlignment = xlCenter
    ws.Range("B3").Value = "Período: " & per & " · Filtros: " & fil & " · Gerado em " & Format(Now, "dd/mm/yyyy hh:nn")
    ws.Range("B3").Font.Italic = True: ws.Range("B3").Font.Size = 9: ws.Range("B3").Font.Color = RGB(102, 112, 133)
End Sub

Private Sub Cartoes(ws As Worksheet, faixa As String)
    With ws.Range(faixa)
        .HorizontalAlignment = xlCenter
        .Interior.Color = RGB(241, 244, 250)
        .Borders.Color = RGB(208, 213, 221)
    End With
    ws.Range(faixa).Rows(1).Font.Size = 9: ws.Range(faixa).Rows(1).Font.Color = RGB(102, 112, 133)
    ws.Range(faixa).Rows(2).Font.Size = 18: ws.Range(faixa).Rows(2).Font.Bold = True
    ws.Range(faixa).Rows(1).Borders(xlEdgeTop).Color = RGB(214, 51, 108): ws.Range(faixa).Rows(1).Borders(xlEdgeTop).Weight = xlMedium
    ws.Range(faixa).Rows(2).RowHeight = 32
End Sub

Private Function TabelaRel(ws As Worksheet, r As Long, titulo As String, cab As Variant, linhas As Variant) As Long
    Dim i As Long, j As Long
    ws.Cells(r, 2).Value = titulo: ws.Cells(r, 2).Font.Bold = True: ws.Cells(r, 2).Font.Size = 12: ws.Cells(r, 2).Font.Color = RGB(15, 42, 74)
    r = r + 1
    For j = 0 To UBound(cab): ws.Cells(r, 2 + j).Value = cab(j): Next j
    EstiloCab ws.Range(ws.Cells(r, 2), ws.Cells(r, 2 + UBound(cab)))
    For i = 0 To UBound(linhas)
        r = r + 1
        For j = 0 To UBound(linhas(i)): ws.Cells(r, 2 + j).Value = linhas(i)(j): Next j
        ws.Range(ws.Cells(r, 2), ws.Cells(r, 2 + UBound(cab))).Borders.Color = RGB(208, 213, 221)
        ws.Range(ws.Cells(r, 3), ws.Cells(r, 2 + UBound(cab))).HorizontalAlignment = xlCenter
    Next i
    TabelaRel = r + 2
End Function

Private Function TabelaCalc(ws As Worksheet, r As Long, wc As Worksheet, col As Long, titulo As String) As Long
    Dim i As Long, n As Long, ln() As Variant
    n = UltimaLinha(wc, col)
    If col = 1 Then n = 7
    If col = 13 Then n = 6
    ReDim ln(0 To n - 1)
    For i = 0 To n - 1
        ln(i) = Array(wc.Cells(i + 2, col).Value, wc.Cells(i + 2, col + 1).Value)
    Next i
    TabelaCalc = TabelaRel(ws, r, titulo, Array(IIf(col = 13, "Faixa", wc.Cells(1, col).Value), "OS"), ln)
End Function

Private Sub EstiloCab(rg As Range)
    rg.Font.Bold = True: rg.Font.Color = vbWhite: rg.Interior.Color = RGB(214, 51, 108)
    rg.HorizontalAlignment = xlCenter: rg.Cells(1, 1).HorizontalAlignment = xlLeft
End Sub

Private Sub CopiarAba(wb As Workbook, origem As String, titulo As String, per As String, fil As String, lista As Collection, desc As String)
    Dim ws As Worksheet, src As Worksheet
    If Not Existe(origem) Then Exit Sub
    Set src = ThisWorkbook.Worksheets(origem)
    Set ws = wb.Worksheets.Add(After:=wb.Worksheets(wb.Worksheets.Count)): ws.Name = Left$(titulo, 31)
    CabecalhoRel ws, titulo, per, fil
    src.UsedRange.Copy
    ws.Range("B5").PasteSpecial xlPasteColumnWidths
    ws.Range("B5").PasteSpecial xlPasteValuesAndNumberFormats
    ws.Range("B5").PasteSpecial xlPasteFormats
    Application.CutCopyMode = False
    ws.Columns("A").ColumnWidth = 2
    FormatarRel ws
    lista.Add Array(ws.Name, desc)
End Sub

Private Sub FormatarRel(ws As Worksheet)
    With ws.PageSetup
        .Orientation = xlLandscape
        .Zoom = False
        .FitToPagesWide = 1
        .FitToPagesTall = False
        .CenterHorizontally = True
        .LeftFooter = "&8Gerador de OS HEV · Manutenção"
        .RightFooter = "&8Página &P de &N"
    End With
    ws.Columns("B").ColumnWidth = Application.Max(ws.Columns("B").ColumnWidth, 40)
    ws.Range("B5:B3000").WrapText = True
End Sub

Private Sub MontarCapa(ws As Worksheet, per As String, fil As String, lista As Collection)
    Dim i As Long, it As Variant, r As Long
    ws.Activate: ActiveWindow.DisplayGridlines = False
    ws.Columns("A").ColumnWidth = 3: ws.Columns("B").ColumnWidth = 42: ws.Columns("C").ColumnWidth = 80
    ws.Range("B2:C4").Interior.Color = RGB(15, 42, 74)
    ws.Range("B2").Value = "MANUTENÇÃO · HOSPITAL EDMUNDO VASCONCELOS": ws.Range("B2").Font.Bold = True: ws.Range("B2").Font.Size = 10: ws.Range("B2").Font.Color = RGB(247, 161, 196)
    ws.Range("B3").Value = "Relatório de Ordens de Serviço": ws.Range("B3").Font.Bold = True: ws.Range("B3").Font.Size = 22: ws.Range("B3").Font.Color = vbWhite
    ws.Range("B4").Value = "Período: " & per: ws.Range("B4").Font.Color = RGB(221, 227, 240)
    ws.Rows(3).RowHeight = 38
    ws.Range("B6").Value = "Filtros": ws.Range("C6").Value = fil
    ws.Range("B7").Value = "Gerado em": ws.Range("C7").Value = Format(Now, "dd/mm/yyyy hh:nn")
    ws.Range("B8").Value = "Fonte": ws.Range("C8").Value = "Relatórios de OS exportados do MV (R_ORDEM_SERVICO)"
    ws.Range("B6:B8").Font.Bold = True
    ws.Range("B10").Value = "O que tem neste arquivo": ws.Range("B10").Font.Bold = True: ws.Range("B10").Font.Size = 13
    r = 11
    For Each it In lista
        i = i + 1
        ws.Hyperlinks.Add Anchor:=ws.Cells(r, 2), Address:="", SubAddress:="'" & it(0) & "'!A1", TextToDisplay:=i & ". " & it(0)
        ws.Cells(r, 3).Value = it(1): ws.Cells(r, 3).Font.Color = RGB(102, 112, 133)
        r = r + 1
    Next it
    r = r + 1
    ws.Cells(r, 2).Value = "Regras usadas": ws.Cells(r, 2).Font.Bold = True: ws.Cells(r, 2).Font.Size = 13
    For Each it In Array("Realizadas = concluídas + aguardando material + conserto externo + canceladas.", _
        "Backlog (pendentes nossas) = aberta + não atendida + agendar. Aguardando material e conserto externo ficam fora.", _
        "Tratativa = só as frases padrão do planejamento na Observação; recado do solicitante não conta.", _
        "Execução acima do limite ou sem hora de fim conta 1 h provisória e aparece em 'Para arrumar no MV'.")
        r = r + 1
        ws.Cells(r, 2).Value = "• " & it: ws.Cells(r, 2).Font.Color = RGB(102, 112, 133)
    Next it
    With ws.PageSetup
        .Orientation = xlPortrait: .Zoom = False: .FitToPagesWide = 1: .FitToPagesTall = False: .CenterHorizontally = True
    End With
End Sub

Private Function Existe(nome As String) As Boolean
    Dim ws As Worksheet
    On Error Resume Next
    Set ws = ThisWorkbook.Worksheets(nome)
    Existe = Not ws Is Nothing
    On Error GoTo 0
End Function

Private Function PegarOuCriar(nome As String, pos As Long) As Worksheet
    If Existe(nome) Then
        Set PegarOuCriar = ThisWorkbook.Worksheets(nome)
    Else
        Set PegarOuCriar = ThisWorkbook.Worksheets.Add(Before:=ThisWorkbook.Worksheets(pos))
        PegarOuCriar.Name = nome
    End If
End Function
