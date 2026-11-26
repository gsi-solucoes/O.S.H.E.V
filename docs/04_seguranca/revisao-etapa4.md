# Revisão de segurança — Raio X do Relatório, etapa 4

- Data: 26/11/2026 · Revisor: Revisor de segurança (Método GSI, seção 6)
- Base: branch `rodada-auto` (`90a5859`), `git diff origin/main -- src/app.js` (`index.html` é build).
- Escopo: Excel seguindo o painel: `xlBloco`, `xlPadrao`, `abasPainelXl`, `abaPainel`, `abasDoArquivo`, `celulaReg`, `periodoCapa`, `capa`, `comoLer`, `gerarExcel`, gancho `window.__abasPainel`.
- Régua: checklist 6.3 no que cabe a um app estático, offline, sem servidor, com repositório público.

## Veredito

**A etapa 4 pode ser liberada**: não há achado Crítico nem Alto. Há 1 Médio (M-1) e 2 Baixos (B-1, B-2), que a fábrica corrige sozinha, com teste de regressão.

| Severidade | Quantidade |
|---|---|
| Crítico | 0 |
| Alto | 0 |
| Médio | 1 |
| Baixo | 2 |

## Checklist 6.3 (o que cabe)

| Item | Resultado |
|---|---|
| Segredos no repositório e no histórico | O diff não tem senha, token, chave nem `BEGIN PRIVATE`. |
| Segredos no HTML/JS | Não há. |
| Sessão, limite de tentativas, RLS, bucket, porta 127.0.0.1, senha fora da URL | Não se aplica: o app não tem servidor, login nem banco remoto. |
| Logs sem conteúdo sensível | O diff não traz nenhum `console.*` novo. |
| Requisições externas | O diff não traz `fetch`, XHR nem URL nova. A planilha é montada e baixada só no navegador (`Blob` + `download`). |
| CSP/hash | A CSP não mudou. Refeito numa cópia, o `build.py` gera um `index.html` **idêntico** ao do diretório. Não há `</script` em `src/app.js`. |
| Dublês (1.8) | Não se aplica: não há serviço externo nem IA paga. |

## O que foi conferido e está bom

- **Injeção de fórmula:** o código não usa `{ formula }`, `sharedFormula`, `hyperlink` nem `richText` vindos de dado. Teste em Node com o `vendor/exceljs.min.js`: os valores `=HYPERLINK(...)`, `+1+1` e `@SUM(1)` foram gravados como `t="s"` (texto compartilhado), sem `<f>`. No `put()` de `abaPainel`, só os objetos `XI`/`XD` montados no próprio código viram valor com `numFmt`. Os formatos são constantes (`#,##0`, `#,##0.00`). Um dado do arquivo nunca chega como objeto: o `importar` usa `Core.t`, e o `validarBackup` passa tudo por `paraTexto`. O teste CA-47 cobre "sem fórmula e sem macro".
- **Limite de 32.767 caracteres:** títulos, rótulos, categorias, avisos, valores e registros passam por `put()` → `primitivoXL` → `cortaCelula` (32.000). A barra tem no máximo 20 caracteres. As exceções estão em B-2.
- **XSS:** o diff não traz `innerHTML`, `document.write` nem `eval` novos. O código novo só escreve na planilha. `window.__abasPainel` devolve uma cópia JSON de nomes de abas e títulos: são dados do próprio navegador, de mesma origem (informativo, igual ao `__entender`).
- **Vazamento de dados:** abas com `escondida` não saem. A seção "Registros" usa a mesma lista filtrada (`g.lista`) e os mesmos campos (`g.campos`) da aba de dados. A capa mostra só filtros e período escolhidos pela própria pessoa. Nada sai do navegador.
- **Rodapé:** só o rodapé antigo leva texto do usuário (`ORG()`), com `&` escapado. O código novo não põe dado em cabeçalho ou rodapé.

## Achados

### Médio

**M-1. Nome de planilha que colide sem diferenciar maiúsculas de minúsculas, ou que é proibido, derruba a exportação inteira.**
- Prova: `nomeAba` confere duplicata com `wb.getWorksheet(x)`, que diferencia maiúsculas de minúsculas (teste: com `Painel` criada, `getWorksheet('painel')` dá `false`). Já o `addWorksheet` do ExcelJS recusa duplicata sem diferenciar a caixa (`Worksheet name already exists: painel`), além de nomes que começam ou terminam com `'` e do nome `History`. A etapa 4 cria casos novos:
  - relatório chamado "painel" (ou "PAINEL") em arquivo único ou separado: a aba `Painel` já existe e `aba(wb, 'painel')` lança erro;
  - dois relatórios que diferem só na caixa ("Vendas" e "vendas") com "uma planilha só": `Painel - Vendas` e `Painel - vendas` colidem;
  - relatório cujo nome termina com `'`: `Painel - x'` é recusado.
  O `catch` de `gerarExcel` mostra "Não consegui gerar o Excel" e nenhum arquivo é baixado. Não vaza dado, mas a pessoa perde a função por causa de um nome legítimo.
- Correção: em `nomeAba`, comparar com `wb.worksheets.some(w => w.name.toLowerCase() === x.toLowerCase())`; tirar `'` do começo e do fim; trocar `History` (sem diferenciar a caixa) por `History 2`. Teste de regressão: relatório "painel" e um par "Vendas"/"vendas" exportam sem erro.

### Baixos

**B-1. `XI`/`XD` não passam pelo filtro de número finito: `Infinity` ou `NaN` vão para o XML.**
- Prova: `put()` grava `v.n` direto, sem o `isFinite` do `primitivo`. `Core.numero('9'.repeat(400))` dá `Infinity`. Uma coluna numérica com esse valor faz o bloco "num" (Soma/Média) ou um "Meu indicador" de soma gravar `<v>Infinity</v>`. Teste em Node: o ExcelJS grava `<v>Infinity</v>` e `<v>NaN</v>` sem reclamar, e o Excel abre esse arquivo como "conteúdo ilegível" e pede reparo.
- Correção: no `put()`, `if (!isFinite(v.n)) cl.value = '—'`. Opcional: o `Core.numero` passar a recusar resultado não finito. Teste de regressão com o valor de 400 dígitos.

**B-2. Duas células fora do `cortaCelula`.**
- Prova: em `abaPainel`, `ws.getCell('A2').value = 'Relatório: ' + c` e `ws.getCell('A1').value = ab.nome` vão direto para a célula. O nome do relatório não tem limite de tamanho: `validarBackup` e `camposOk` só pedem `trim()`. Um backup com nome de relatório acima de 32.767 caracteres gera uma célula inválida, e o Excel repara o arquivo. Hoje `ab.nome` é fixo ("Painel"), mas a etapa 6 vai passar nomes dados pela pessoa. Problema parecido, anterior a esta etapa: o cabeçalho de `aba()` (`ws.addRow(cols.map(c => c.n))`) também não corta.
- Correção: usar `put(1, 1, ab.nome)` e `put(2, 1, 'Relatório: ' + c)`, e passar o cabeçalho de `aba()` por `primitivoXL`. Opcional: limitar o tamanho do nome de relatório e de campo no `validarBackup`.

### Informativo

- Se alguém abrir o `.xlsx` e "Salvar como CSV" no próprio Excel, um texto como `=...` volta a ser lido como fórmula quando esse CSV for aberto de novo. Isso fica fora do app, e o arquivo gerado está correto. Se um dia o app exportar CSV, prefixar com `'` os valores que começam com `= + - @`, tabulação ou CR.
