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
9. Clique em **Gerar relatório (Excel)** e salve. Esperado: arquivo novo com abas **Capa** (Cliente Teste, Area Teste, período, filtros, total), **Resumo** e **Registros**, só com valores (sem fórmulas, sem macros).
10. Config → **Esquecer formatos lembrados**; importe de novo: as perguntas voltam.

## Resultado
Anote: passou / falhou, versão do Excel, e o que apareceu de diferente. Marque CA-110 como conferido em `docs/03_homologacao/estado.md`.
