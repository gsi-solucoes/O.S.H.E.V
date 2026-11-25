# Revisão de segurança — Raio X do Relatório, etapa 2

- Data: 25/11/2026 · Revisor: Revisor de segurança (Método GSI, seção 6)
- Branch: `etapa-2` (último commit revisado: `22846f7`)
- Escopo: só o que mudou desde a etapa 1 (`git diff origin/etapa-1 -- src build.py`): `src/app.html`, `src/app.js`, `src/core.js`. `build.py` não mudou. `index.html` só conferido contra o build.
- Régua: checklist 6.3 no que cabe a app estático, offline, sem servidor, repositório público.

## Veredito

**Libera a etapa 2**: nenhum achado Crítico, Alto ou Médio. Há 4 achados Baixos (B-1 a B-4), que podem ir para a fila.

## Checklist 6.3 (o que cabe)

| Item | Resultado |
|---|---|
| Segredos no repositório e no histórico | Nada nos commits `origin/etapa-1..etapa-2`. A busca por chave, token, senha e `BEGIN PRIVATE` só achou falsos positivos (`desenha`). |
| Segredos no HTML/JS | Não há. |
| Sessão, limite de tentativas, RLS, bucket, porta 127.0.0.1, senha fora da URL | Não se aplica: sem servidor, sem login, sem banco remoto. |
| Logs sem conteúdo sensível | Nenhum `console.*` novo. |
| Requisições externas | Nenhuma URL, `fetch` ou XHR novos. A CSP (`src/app.html:6`) não mudou: `connect-src 'self'`, sem `unsafe-inline` nem `unsafe-eval` em `script-src`. |
| CSP/hash | O `build.py` refeito numa cópia gera um `index.html` **idêntico** ao commitado, com o hash coerente. Sem `</script` em `src/app.js` nem em `src/core.js`. |
| Dublês (1.8) | Não se aplica (projeto sem serviço externo). |

## O que foi conferido e está bom

- **XSS em "O que acompanhar", "Seu painel" e nos blocos:** nomes de campo, valores do CSV, nome do relatório e o texto da busca (`F.q`) entram só por `el()` (`textContent` ou nó de texto) ou `setAttribute` (`aria-label`): `src/app.js:370`, `src/app.js:381`, e os cartões e barras de `catalogo()` (`src/app.js:303`). Não há `innerHTML` novo. O `style` das barras só recebe número. Os ids com `\u0001` não vão para o DOM.
- **Injeção de fórmula na aba "Como ler este relatório"** (`src/app.js:449-455`): o texto passa por `primitivo()` e o ExcelJS grava string como texto (`t="s"`). Teste feito: `=HYPERLINK(...)` e `@SUM(1)` gravados com o `vendor/exceljs.min.js` saíram como `<c r="A2" t="s">`, sem fórmula. O texto sempre começa com o nome do bloco, então um campo chamado `=...` só aparece no começo em "`<campo>` (soma, média e mediana)" e em "`<campo>` por ...", e mesmo assim como texto.
- **`raiox_acomp` no localStorage** (`src/app.js:48`): é carregado por `copiaNula` (objeto sem protótipo). O uso confere `Array.isArray` e filtra os ids pelo catálogo (`src/app.js:344`, `janelaAcomp`). Id estranho é ignorado.
- **Restauração de backup** (`src/app.js:40-41`, `src/app.js:518`): `acomp` precisa ser objeto (não array), cada valor precisa ser array de strings com até 500 itens, e tudo é copiado para um objeto sem protótipo. Com `__proto__`, `constructor` etc., o nome vira chave própria e não polui protótipo (o `JSON.parse` cria propriedade própria e o destino é `nulo()`). Em "Substituir" e em "Apagar tudo", `acomp` também é zerado.
- **Tipo novo `situacao`:** entra em `TIPOS_OK`, então o backup aceita e `camposOk` continua barrando tipo desconhecido. A mudança em `core.js` é só a sugestão por nome da coluna.

## Achados

### Baixos

**B-1. Backup preparado com ids repetidos multiplica os blocos (travamento da aba)**
- Onde: `src/app.js:41` (validação) e `src/app.js:344` (`blocosEscolhidos`).
- Prova: `{"acomp": {"Rel": ["total","total", ... 500 vezes]}}` passa na validação. `blocosEscolhidos` desenha 500 cartões a cada `render()`, e com muitos registros a aba fica lenta. Também não há limite de quantidade de chaves em `acomp` (só o limite de 200 MB do arquivo).
- Correção: na validação, tirar repetidos (`[...new Set(l)]`), limitar o tamanho de cada id (por exemplo 1000 caracteres) e o número de chaves. Repetir o mesmo cuidado ao ler `raiox_acomp`.

**B-2. `catalogo()` é refeito em todo `render()`, com custo de campos numéricos × categorias × registros**
- Onde: `src/app.js:240`, que chama `blocosEscolhidos` → `catalogo`, e este roda `ex(todos)` em todos os itens (`src/app.js:303`).
- Prova: um CSV com 30 campos numéricos e 30 de categoria gera cerca de 900 indicadores "X por Y". Cada um percorre todos os registros a cada tecla na busca. É uma negação de serviço local (só o próprio aparelho, com o próprio arquivo).
- Correção: guardar o catálogo por conjunto e só refazer quando os dados ou os tipos mudarem; em `blocosEscolhidos`, montar só os ids escolhidos.

**B-3. Célula da aba "Como ler" pode passar de 32.767 caracteres**
- Onde: `src/app.js:454`.
- Prova: o texto junta o nome do bloco, os campos e os filtros (`F.q`, `F.val` vindo do CSV). Com nome de campo ou busca muito longos, a célula passa do limite do Excel e ele abre o arquivo pedindo reparo. É integridade do arquivo, não execução de código.
- Correção: cortar o texto (`.slice(0, 32000)`) antes de gravar. O mesmo vale para `aba()`, que já existia.

**B-4. `const esc` dentro de `render()` esconde o `esc()` que escapa HTML**
- Onde: `src/app.js:240`.
- Prova: hoje `esc()` não é usado dentro de `render()`, então nada quebra. Mas uma mudança futura que use `esc(...)` ali (por exemplo, para impressão) chamaria um array: daria erro, ou levaria alguém a "resolver" tirando o escape.
- Correção: renomear a variável local para `escolhidos`.

### Informativo
- A injeção de fórmula segue como na etapa 1: o Excel abre o texto `=...` como texto. Só vira fórmula se a pessoa editar a célula e der Enter. Opcional, para ficar igual ao "Copiar" (`src/app.js:423`): pôr `'` na frente de textos que começam com `= + - @` também na aba "Como ler".
- Falta teste de regressão de segurança da etapa 2 em `tests/test_etapa2.py`. Sugestões:
  1. Restaurar um backup com `acomp` contendo `__proto__`, valor que não é array e ids repetidos.
  2. CSV com cabeçalho `<img src=x onerror=...>` e `=HYPERLINK(...)`: conferir que não aparece elemento novo no DOM e que o xlsx não tem `t="f"`.
