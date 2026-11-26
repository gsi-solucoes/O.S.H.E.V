# Roteiro de conferência manual - versão Excel (CA-110)

Feito no Excel 2016 (Windows). Leva uns 10 minutos. Use o arquivo `tests/dados/vendas.csv`.

## Antes
1. Baixe `excel/RaioX_Relatorio.bas` e o `tests/dados/vendas.csv`.
2. No app (navegador), carregue o mesmo `vendas.csv` e anote o **Total de registros** e a lista **Por cliente** (valores de cada cliente).

## No Excel
1. Pasta de trabalho nova, salvar como `.xlsm`. **Alt + F11** → Arquivo → Importar arquivo → `RaioX_Relatorio.bas`. Fechar o editor. (Se aparecer erro de compilação, anote a linha e o texto.)
2. **Alt + F8** → `Instalar` → Executar. Esperado: abas Painel, Config e Dados; botões "Importar arquivos", "Atualizar painel" e "Gerar relatório (Excel)" no Painel.
3. Aba **Config**: Cliente = `Cliente Teste`, Área = `Area Teste`.
4. Painel → **Importar arquivos** → `vendas.csv`. Esperado: pergunta "Esta coluna é o quê?" uma vez por coluna. Responda: Código = 1, Data = 2, Cliente = 3 (Categoria), Região = 3, Vendedor = 5, Valor = 4, Situação = 3.
5. Mensagem final com linhas lidas e registros novos. Painel mostra **Total de registros** e a tabela **Por Cliente** (se não, em "Campo categoria" escolha `Cliente` e clique em **Atualizar painel**).
6. **Conferência (CA-110):** o Total e cada contagem de "Por Cliente" são iguais aos do app.
7. Importe o mesmo arquivo de novo: nenhuma pergunta nova e o Total não muda (junção por código).
8. Em "Período de" / "até" ponha um intervalo (ex.: 01/01/2026 a 30/06/2026), em "Categoria" escolha um cliente, clique em **Atualizar painel**: o Total e a tabela diminuem de acordo.
9. Clique em **Gerar relatório (Excel)** e salve. Esperado: arquivo novo com abas **Capa** (Cliente Teste, Area Teste, período, filtros, total), **Resumo**, **Indicadores** e **Registros**, só com valores (sem fórmulas, sem macros).
9b. (F-56) No Painel, escolha em **Campo número (para somar)** o campo Valor e clique em **Atualizar painel**. Esperado: à direita (coluna F) a tabela **Indicadores**: Total de registros, Soma, Média, Mediana, Mínimo, Máximo, Registros sem valor, Soma por categoria e Registros por mês, iguais ao app. Mude o período e atualize: os números acompanham o filtro. A aba **Indicadores** do relatório traz a mesma tabela.
10. Config → **Esquecer formatos lembrados**; importe de novo: as perguntas voltam.

## O que a oficina não cobre (conferir no Excel real)
A oficina (`tests/oficina/macro_libreoffice.py`, usada por `tests/test_macro_oficina.py`) roda a macro no LibreOffice headless, com os ganchos `OficinaImportar`/`OficinaGerar` e sem nenhuma caixa de diálogo. Ela acha erros de lógica e de compilação, mas estes pontos só o Excel confere (passos acima):
- **Botões do Painel e da Config** (`Shapes.AddShape` + `OnAction`): em oficina `NovoBotao`/`ApagarBotoes` não fazem nada. Confira o visual e que cada botão dispara a macro certa (passos 2 e 4).
- **Diálogos reais**: `GetOpenFilename`, `GetSaveAsFilename`, `InputBox` ("Esta coluna é o quê?") e `MsgBox`. A oficina aceita o `PapelSugerido` e guarda as mensagens em memória. Confira a pergunta, o Cancelar e o texto das mensagens (passos 4, 5, 9, 10).
- **Leitura de arquivo com `ADODB.Stream`** (UTF-8 x Windows-1252): em oficina um decodificador próprio faz o serviço. Confira com `vendas_cp1252.csv` que acentos saem certos.
- **`Scripting.Dictionary`**: na oficina é trocado por um dublê escrito em Basic (só o test-runner, a macro continua igual).
- **ZIP** (`Shell.Application` + `Environ$("TEMP")`): não roda no LibreOffice; confira importando um `.zip` com CSV.
- **XLSX/XLS como entrada** (`Workbooks.Open` somente leitura) e `ThisWorkbook.Activate`: não exercitados.
- **`wb.SaveAs ..., 51`**: o LibreOffice grava `.xls` com esse código; na oficina o relatório é salvo como `.xlsx` pelo runner. Confira que o arquivo do Excel abre como `.xlsx` (passo 9).
- **Barras de dados** (`FormatConditions.AddDatabar`) na tabela "Por ...": pulado em oficina.
- **Lista suspensa** (validação) de B8:B10 do Painel, formatos de data/número (`dd/mm/yyyy`, `#,##0`), `AutoFit`, `DisplayGridlines` e `Format$(Now, "dd/mm/yyyy hh:nn")` (o LibreOffice não entende `nn`; no Excel é minutos): só conferência visual.
- **Aba `_Memoria` oculta** e `Names` com `OFFSET`: criados, mas a lista suspensa não é testada.

Erros reais achados e corrigidos pela oficina (valem também no Excel): `n = Selecionar d, ...` sem parênteses (não compila); variável local `cod` escondia a constante `COD` (VBA não diferencia maiúsculas) e a junção falhava; `PapelSugerido` não reconhecia "Código" (só "cod"); `Range("B7,D7")` com várias áreas separado em duas linhas.

## Resultado
Anote: passou / falhou, versão do Excel, e o que apareceu de diferente. Marque CA-110 como conferido em `docs/03_homologacao/estado.md`.
