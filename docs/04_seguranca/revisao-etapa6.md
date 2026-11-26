# Revisão de segurança — Raio X do Relatório, etapa 6 (Editar layout, F-57)

- Data: 26/11/2026 · Revisor: Revisor de segurança (Método GSI, seção 6)
- Base: `b9ba45d` + alterações ainda não commitadas em `src/` (`git diff HEAD -- src`: `src/app.js`, `src/app.html`). `index.html` é build e não foi revisado à parte (só serviu de página para os testes no Chrome).
- Escopo: bloco "etapa 6" de `src/app.js` (`NOME_RUIM`, `nomeAbaOk`, `layoutsLimpo`, `layGet`, `layMut`, `blocosVis`, `desenhaItem`, `pizzaSvg`, `linhaSvg`, `tabelaForma`, `renderLay`, arrastar e soltar, `pedeNomeAba`, `iniciaLay`), Excel por aba (`abasPainelXl`, `abaPainel`, `abasDoArquivo`, `nomeAba`), Seu painel (`blocosPainel`), backup e restauração (Somar, Substituir, Apagar tudo) e a janela `dlgAba` em `src/app.html`.
- A suíte de testes não foi rodada, como pedido. Foram exercitados: `layoutsLimpo` e `nomeAba` isolados em Node (com backup forjado), e a página `index.html` no Chrome (Playwright) para o caso de mais de 200 blocos e para o nome de planilha gerado pelo ExcelJS.

## Veredito

**A etapa 6 pode ser liberada**: não há achado Crítico nem Alto. Há 1 Médio e 3 Baixos, que a fábrica corrige sozinha. O Médio (M-1) deve ser corrigido antes da homologação, porque pode deixar o backup do usuário impossível de restaurar.

| Severidade | Quantidade |
|---|---|
| Crítico | 0 |
| Alto | 0 |
| Médio | 1 |
| Baixo | 3 |

## Checklist 6.3 (o que cabe a um app estático e offline)

| Item | Resultado |
|---|---|
| Segredos no repositório, no histórico e no HTML/JS | O diff não tem senha, token nem chave. A única URL nova é o namespace do SVG (`http://www.w3.org/2000/svg`), que não faz requisição. |
| Sessão, limite de tentativas, RLS, bucket, porta 127.0.0.1, senha fora da URL | Não se aplica: não há servidor, login nem banco remoto. |
| Logs sem conteúdo sensível | O diff não traz nenhum `console.*` novo. |
| Requisições externas | O diff não traz `fetch`, XHR, `eval`, `new Function`, `innerHTML` nem `document.write` novos. |
| Dublês (1.8) | Não se aplica: não há serviço externo nem IA paga. |
| Visão do atacante | Sem servidor, quem tem o link não vê dado de ninguém. Continuam como entrada de fora só o **arquivo de backup** (agora com o campo `layout`) e o relatório que alguém entrega para a vítima abrir. Os pontos abaixo olham o que um backup forjado consegue fazer. |

## O que foi conferido e está bom

- **Validação do backup (`layoutsLimpo`, `app.js:479`):** rejeita o arquivo inteiro se `layout` não for objeto; até 200 relatórios, de 1 a 20 abas e até 200 itens por relatório (os limites são conferidos antes de percorrer as listas); `id` da aba é texto de 1 a 50; nome da aba passa por `nomeAbaOk` (1 a 30 depois do `trim`, sem `NOME_RUIM`); ids e nomes de aba repetidos (normalizados por `chaveNome`) são recusados; item precisa de `k` único, `id` texto até 1000 e `aba` que exista; `tam` só `p/m/g`, `oculto` só booleano, `forma` só da lista `LAY_FORMAS`. Os objetos são reconstruídos campo a campo, então propriedades a mais do arquivo não passam. Testado em Node: 201 itens, 21 abas, nome com `U+202E`, 31 caracteres, só espaços, nomes `Vendas`/`vendas` e `forma: "<svg>"` são todos recusados.
- **Prototype pollution:** o mapa de layouts e `abaAb` usam `nulo()` (`Object.create(null)`). Testado: backup com relatório `__proto__`, aba de id `__proto__` e nome `constructor`, item com `k: "__proto__"` e `id: "toString"` vira chave comum (protótipo do resultado `null`); `({}).abas` continua `undefined`. `layGet` copia com `Object.assign({}, a)` objetos que já saíram limpos do validador.
- **XSS:** nome da aba só chega à tela por `textContent` (`el(..., { text })`): botões das abas, opções de "Mover para…", título da pergunta "Apagar a aba …?" (`perguntar` usa `textContent`). Títulos e rótulos dos gráficos novos (pizza, linha, tabela) vão por `document.createTextNode` ou `text`; os atributos do SVG são números calculados ou cores fixas (`COR_PZ`), postos por `setAttribute`. `data-k`, `data-tam` e `aria-label` também vão por `setAttribute`.
- **Arrastar e soltar:** o que se move vem da variável em memória `arrasta`, não do `dataTransfer`. Um texto arrastado de outra janela ou site chega com `arrasta = null` e é ignorado (`app.js:563` e `app.js:591`); soltar em bloco de outra aba é recusado; `ondragend` limpa a variável.
- **Excel por aba:** o nome da planilha passa por `nomeAba` (`app.js:893`): troca `[ ] : * ? / \` por espaço, tira `'` das pontas, corta em 28 caracteres, evita `History` e nome repetido sem diferenciar maiúsculas. Testado: `a:b`, `a?b` e `A B` viram `a b`, `a b 2`, `A B 3`; `[]*?/\:` vira `Aba`. Nome de planilha não é avaliado como fórmula; `=SOMA(1)` fica como nome. No conteúdo, o nome da aba (A1) e os títulos passam por `primitivoXL` e viram texto: no arquivo gerado pelo ExcelJS não há `<f>` (testado com `=HYPERLINK(...)`). Bloco escondido fica fora da planilha; aba sem bloco não vira planilha; os registros vão só na primeira planilha do relatório (`semReg`).
- **Seu painel:** `blocosPainel` passa a usar `blocosVis` (ordem do layout, escondidos fora); o texto da lista continua por nó de texto (`el('li', null, x.texto)`).
- **Restauração:** "Substituir" zera `layouts` antes de juntar; "Somar" só traz o layout de relatório que ainda não tem layout local (o local prevalece); "Apagar tudo" zera `layouts`, grava e desliga o modo de edição. "Voltar ao padrão" apaga só o layout daquele relatório. O modo de edição e a aba aberta ficam só na memória.
- **Limites na tela:** "Nova aba" para em 20 abas; "Duplicar" para em 200 blocos; o nome tem `maxlength="30"` e é conferido de novo ao salvar.

## Achados

### M-1 (Médio) — layout com mais de 200 blocos é gravado, some ao recarregar e torna o backup inteiro irrestaurável
- **Onde:** `src/app.js:508` (`layGet` acrescenta todo bloco escolhido em "O que acompanhar", sem teto), `src/app.js:408` (`acompOk` grava `layGet(c)`), `src/app.js:515` (`layMut`), `src/app.js:491` (`layoutsLimpo` recusa mais de 200 itens) e `src/app.js:500` (`layoutsLimpo(store.get(...)) || nulo()`).
- **Prova (Chrome, `index.html`):** relatório fictício com 15 campos de categoria e 15 numéricos (256 blocos no catálogo); 220 marcados em "O que acompanhar" (`acompLimpa` aceita até 500 e a janela não tem limite) e um layout editado. Resultado: `layGet` gravou 220 itens; `layoutsLimpo` da cópia gravada devolve `null`; depois de recarregar a página, `layouts` fica vazio, **inclusive o layout de outro relatório** que estava certo; e `validarBackup` de um backup feito nesse estado devolve `null`, ou seja, "Restaurar" diz "não é um backup do Raio X" e **não restaura nem os registros**. O mesmo acontece com 150 escolhidos + 50 duplicados + 1 indicador novo marcado, e ao Somar um backup cujo layout junta com escolhas locais.
- **Risco:** perda silenciosa da configuração de layout de todos os relatórios e backup que o app não aceita de volta (os dados continuam no JSON, mas o usuário comum não consegue recuperá-los). Não há vazamento nem execução; é integridade e disponibilidade.
- **Correção:** (1) aplicar o mesmo teto de 200 em `layGet` (acima disso, não acrescentar e avisar por `toast`) e limitar "O que acompanhar" a 200 escolhas por relatório quando houver layout, ou alinhar os dois limites; (2) em `layoutsLimpo`, para o localStorage, descartar só o relatório inválido em vez de zerar todos; (3) no backup, não rejeitar o arquivo inteiro por causa do layout: com layout inválido, restaurar o resto sem layout e avisar. Testes de regressão: 201 blocos escolhidos com layout editado (recarregar mantém o layout; backup restaura) e backup com um layout inválido e registros válidos.

### B-1 (Baixo) — `NOME_RUIM` ainda deixa passar marcas de direção e separadores
- **Onde:** `src/app.js:62` (vale para nome de aba e de conta).
- **Prova (Node):** nomes de aba com `U+061C` (marca de letra árabe, controle de direção), `U+2028`/`U+2029` (separador de linha/parágrafo) e surrogate solto (`\ud800`) são aceitos por `layoutsLimpo`.
- **Risco:** só engano visual (texto com direção trocada ou quebra de linha no botão da aba); não executa nada.
- **Correção:** acrescentar `؜­  ￹-￻` e surrogates soltos (`/[\ud800-\udbff](?![\udc00-\udfff])|(?:[^\ud800-\udbff]|^)[\udc00-\udfff]/`) à regra, com teste de regressão no salvar e no backup.

### B-2 (Baixo) — `nomeAba` corta no meio de um emoji
- **Onde:** `src/app.js:894` (`.slice(0, 28)` e `.slice(0, 26)` contam unidades UTF-16).
- **Prova (Chrome + ExcelJS):** a aba "27 letras + 😀" (29 unidades, aceita pelo `maxlength="30"`) vira a planilha `aaaa…\ud83d`; no arquivo, o surrogate solto sai como `U+FFFD` (bytes `EF BF BD`). O XML continua UTF-8 válido, mas a planilha aparece com um caractere estranho no fim.
- **Correção:** cortar por ponto de código (`Array.from(b).slice(0, 28).join('')`) e teste com nome terminado em emoji.

### B-3 (Baixo) — negação de serviço local pelo layout
- **Onde:** `src/app.js:491` (`k` e `id` de item até 1000 caracteres), `src/app.js:550` e `src/app.js:558` (cada bloco da aba aberta é calculado sobre a lista inteira a cada `render()`; `layGet` e `catalogo` são chamados mais de uma vez por `render()`).
- **Prova:** o validador aceita, em 188 ms, um backup forjado com 200 relatórios x 20 abas x 200 itens de chaves de ~1000 caracteres (77 MB); ao gravar, o localStorage (5 a 10 MB) estoura e o layout não fica salvo (aparece "Sem espaço para guardar"). Com 200 blocos pesados duplicados numa aba e 100 mil registros, cada troca de filtro recalcula 200 agrupamentos.
- **Risco:** aba lenta ou layout que não grava; só local, sem perda de registro.
- **Correção:** `k` e `id` de item até 200 caracteres (o maior id do catálogo é bem menor), teto de tamanho total do layout no backup, e reaproveitar o resultado de `layGet`/`catalogo` dentro do mesmo `render()` (junto com o B-2 da etapa 5).

## Observações (não são achados de segurança)

- `window.__abasPainel` é um gancho de teste exposto na página; não abre nada novo (mesma origem, só leitura), mas pode sair do build de produção.
- A forma "Tabela" de `% por …` e `Evolução por mês` lista todos os grupos, como o desenho antigo já fazia; com campo de muitos valores distintos a tabela fica muito grande.

## Correção (F-63, 26/11/2026)
M-1 (teto de 200 em `layGet`; carga do navegador descarta só o layout inválido de um relatório), B-1 (`NOME_RUIM` com U+2028/2029, U+061C e surrogate solto), B-2 (nome de planilha cortado por caractere inteiro) e B-3 (chaves de item até 200 caracteres) corrigidos, com 2 testes de regressão (`test_f63_*`). Backup continua rejeitando o arquivo inteiro com layout inválido.
