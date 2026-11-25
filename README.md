# Raio X do Relatório

Lê os dados extraídos de qualquer sistema (relatórios em CSV, Excel, PDF e imagem) e monta sozinho o painel e os relatórios que a pessoa escolher. Funciona no navegador, sem API e sem custo por uso, e serve para qualquer cliente.

- **App:** https://gsi-solucoes.github.io/raio-x-do-relatorio/
- Os arquivos são lidos **somente no navegador**; nada é enviado para servidor. Depois da primeira abertura, funciona sem internet.
- Configuração (cliente, área, logo, frases padrão) e histórico ficam salvos no próprio aparelho; backup e restauração pela aba Config.

## Documentos (Fábrica GSI, Método 1.8.4, caminho direto)
- [Concepção](docs/00_concepcao/concepcao.md) · [Como funciona](docs/00_concepcao/como-funciona.md) · [Diário](docs/00_concepcao/diario.md)
- [Especificação](docs/01_especificacao/especificacao.md) · [Caminho das estrelas](docs/caminho-das-estrelas.md)

## Versão Excel para baixar e usar no PC

Mesma estrutura do app (importar, dizer o que é cada coluna, juntar por código, painel, relatório com capa), no Excel 2016 ou mais novo, Windows.

**Baixar:** https://github.com/gsi-solucoes/raio-x-do-relatorio/raw/main/excel/RaioX_Relatorio.bas

Arquivo: `excel/RaioX_Relatorio.bas`.

1. Abra uma pasta de trabalho nova no Excel, salve como **Pasta de Trabalho Habilitada para Macro (.xlsm)** e aperte **Alt + F11**.
2. **Arquivo → Importar arquivo** → escolha o `.bas` e feche o editor.
3. **Alt + F8** → macro **Instalar** → Executar (se o Excel avisar sobre macros, escolha "Habilitar conteúdo"). Surgem as abas **Painel**, **Config** e **Dados** (mais uma aba oculta que lembra os formatos).
4. Na aba **Config**, preencha Cliente e Área. Na aba **Painel**, clique em **Importar arquivos** (CSV com `;`, `,` ou tab, XLSX ou .zip) e responda "Esta coluna é o quê?" (uma vez por formato).

Depois: escolha período, campo categoria e categoria no Painel e clique em **Atualizar painel**. O botão **Gerar relatório** cria um arquivo novo, só com valores, com capa (cliente, área, período, filtros), um resumo por categoria e a lista de registros. Roteiro de conferência: `docs/03_homologacao/roteiro-excel.md`.
