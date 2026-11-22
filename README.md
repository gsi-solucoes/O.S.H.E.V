# O.S.H.E.V – Gerador de relatórios de OS (HEV)

Página web que lê os CSVs do relatório **R_ORDEM_SERVICO** do MV (um por fila) e monta dashboard, backlog mensal, tempos de atendimento, homem-hora e a lista "Para arrumar".

- Os arquivos são lidos **somente no navegador**; nada é enviado para servidor.
- As configurações (nomes genéricos, de-para de técnicos, limite de horas) ficam salvas no navegador de cada aparelho.
- Site: https://gsi-solucoes.github.io/O.S.H.E.V/

## Versão Excel (computador do hospital)

Arquivo: `excel/GeradorOS_HEV.bas` (Excel 2016 ou mais novo).

1. Abra uma pasta de trabalho nova no Excel e aperte **Alt + F11**.
2. **Arquivo → Importar arquivo** → escolha `GeradorOS_HEV.bas` e feche o editor.
3. Salve como **Pasta de Trabalho Habilitada para Macro (.xlsm)**.
4. **Alt + F8** → **Instalar** → Executar.
5. Na aba Dashboard, clique em **Importar CSVs do MV** e selecione todos os CSVs (ou um .zip com todos).
6. Para escolher o mês, use o filtro **Mês do pedido** no Dashboard. O botão **Gerar relatório (Excel)** cria um arquivo novo, só com valores, com capa, período, filtros e um relatório por aba.

Abas do Excel: Dashboard (como foi o mês) · Backlog (o que está parado e com quem: tratativas, cobrar primeiro, resumo do gerente) · Tempos · Equipe · Para arrumar · Repetidas · Arquivos · Histórico · Config (frases padrão das tratativas).

Atualizando de uma versão anterior: no editor (Alt + F11), remova o módulo antigo **GeradorOS**, importe o arquivo novo e clique em Importar CSVs de novo.
