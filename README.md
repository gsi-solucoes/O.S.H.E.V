# Raio X do Relatório

Lê os dados extraídos de qualquer sistema (relatórios em CSV, Excel, PDF e imagem) e monta sozinho o painel e os relatórios que a pessoa escolher. Funciona no navegador, sem API e sem custo por uso, e serve para qualquer cliente.

- **App:** https://gsi-solucoes.github.io/raio-x-do-relatorio/
- Os arquivos são lidos **somente no navegador**; nada é enviado para servidor. Depois da primeira abertura, funciona sem internet.
- Configuração (cliente, área, logo, frases padrão) e histórico ficam salvos no próprio aparelho; backup e restauração pela aba Config.

## Documentos (Fábrica GSI, Método 1.8.4, caminho direto)
- [Concepção](docs/00_concepcao/concepcao.md) · [Como funciona](docs/00_concepcao/como-funciona.md) · [Diário](docs/00_concepcao/diario.md)
- [Especificação](docs/01_especificacao/especificacao.md) · [Caminho das estrelas](docs/caminho-das-estrelas.md)

## Versão Excel para baixar e usar no PC

**Baixar:** https://github.com/gsi-solucoes/raio-x-do-relatorio/raw/main/excel/RaioX_Relatorio.bas

Arquivo: `excel/RaioX_Relatorio.bas` (Excel 2016 ou mais novo).

1. Abra uma pasta de trabalho nova no Excel e aperte **Alt + F11**.
2. **Arquivo → Importar arquivo** → escolha o `.bas` e feche o editor.
3. Salve como **Pasta de Trabalho Habilitada para Macro (.xlsm)**.
4. **Alt + F8** → **Instalar** → Executar.
5. Na aba Dashboard, clique em **Importar CSVs** e selecione os arquivos (ou um .zip).
6. O botão **Gerar relatório (Excel)** cria um arquivo novo, só com valores, com capa, período, filtros e um relatório por aba.
