# Revisão de segurança — Raio X do Relatório, etapa 5 (contas personalizadas)

- Data: 26/11/2026 · Revisor: Revisor de segurança (Método GSI, seção 6)
- Base: `558ff55` + alterações ainda não commitadas em `src/` (`git diff HEAD~1 -- src`: `src/core.js`, `src/app.js`, `src/app.html`). `index.html` é build e não foi revisado à parte.
- Escopo: `Core.compilaFormula` e `Core.avaliaFormula` (`src/core.js:310-400`); bloco "etapa 5" de `src/app.js` (`contasLimpo`, `contaDe`, `compilaConta`, `valorConta`, `camposFormula`, `acharConta`, `entenderPed`, `conferirConta`, `renderContas`, `salvarConta`), uso das contas em `catalogo`, Seu painel, pedido escrito, `xlBloco`, backup e restauração.
- A suíte de testes não foi rodada, como pedido. O interpretador foi exercitado só em Node, isolado (`require` de `src/core.js`), com entradas hostis.

## Veredito

**A etapa 5 pode ser liberada**: não há achado Crítico nem Alto. Há 0 Médios e 3 Baixos, que a fábrica corrige sozinha.

| Severidade | Quantidade |
|---|---|
| Crítico | 0 |
| Alto | 0 |
| Médio | 0 |
| Baixo | 3 |

## Checklist 6.3 (o que cabe a um app estático e offline)

| Item | Resultado |
|---|---|
| Segredos no repositório, no histórico e no HTML/JS | O diff não tem senha, token nem chave. |
| Sessão, limite de tentativas, RLS, bucket, porta 127.0.0.1, senha fora da URL | Não se aplica: não há servidor, login nem banco remoto. |
| Logs sem conteúdo sensível | O diff não traz nenhum `console.*` novo. |
| Requisições externas | O diff não traz `fetch`, XHR nem URL nova. |
| Dublês (1.8) | Não se aplica: não há serviço externo nem IA paga. |
| Visão do atacante | Sem servidor, quem tem o link não vê dado de ninguém. O único jeito de entrada de fora é o **arquivo de backup** (ou o relatório) que alguém entrega para a vítima abrir. Por isso os pontos abaixo olham o que um backup forjado consegue fazer. |

## O que foi conferido e está bom

- **Nada de execução dinâmica:** `compilaFormula` é um tokenizador e um parser descendente próprio. Não há `eval`, `Function`, `Reflect.apply`, `setTimeout` com texto nem acesso `obj[nomeDoUsuario]()`. A avaliação (`ev`) só reconhece os tipos de nó `n`, `neg`, `op` e `f`, e os operadores são comparados um a um (`+ - * /`).
- **Nome de função:** só passa se `Object.prototype.hasOwnProperty.call(FUNC, nome)` (`core.js:356`). Testado: `constructor()`, `__proto__(Valor)`, `toString()` e `hasOwnProperty(x)` devolvem "função ... não existe".
- **Prototype pollution:** o mapa de campos (`core.js:315`), o conjunto de distintos (`core.js:386`), `contas` e o retorno de `contasLimpo` usam `Object.create(null)` (`nulo()`). Um campo chamado `constructor` funciona como campo comum; `soma(__proto__)` é recusado como campo inexistente. Depois dos testes, `({}).polluted` continua `undefined`.
- **DoS por recursão:** parênteses e sinal de menos têm limite de profundidade 40 (`core.js:353` e `core.js:361`); argumentos de função são tokens soltos (não há recursão dentro de `chamada`); cadeias `1+1+...` são iterativas e, com 300 caracteres, geram no máximo ~150 níveis na avaliação. Testado: 41 parênteses, 299 sinais de menos e 75 x `((((` respondem "fórmula complicada demais" em até 2 ms.
- **ReDoS:** as expressões regulares do tokenizador (`^\d+(\.\d+)?`, `^[\p{L}_][\p{L}\p{N}_]*`, `["“”]`) não têm quantificador aninhado nem alternância ambígua; a fórmula tem teto de 300 caracteres (`core.js:313`, `maxlength="300"` no HTML e `contasLimpo`). A frase do pedido é cortada em 300 antes de `acharConta` (`app.js:493`).
- **Números:** `9` x 300 vira `1e+300` e não quebra; divisão por zero, `Infinity` e `NaN` viram `null` ("sem dados") (`core.js:381-382`, `core.js:395`). `1e5` é recusado (o tokenizador não aceita expoente).
- **XSS:** nome e fórmula da conta só chegam à tela por `el(..., { text })`/`textContent`: lista de contas (`app.js:664`), prévia e erro (`app.js:654-658`), cartão do painel (`cartao` e `kpiBtn`, `app.js:312-313`), título da janela (`abrirJanela`) e resumo do pedido. A mensagem de erro que repete o trecho digitado (`"não entendi '...'"`) também vai por `textContent`. O diff não traz `innerHTML` novo; o `document.write` da impressão (`app.js:717`) passa o título por `esc()`.
- **Injeção de fórmula no Excel:** o bloco `conta` (`app.js:772`) grava número (`XD`) ou o texto "sem dados"; o título (nome da conta) e o texto "Como ler" (que inclui a fórmula) passam por `put()` → `primitivoXL` → `cortaCelula` e viram texto (`t="s"`), sem `<f>`, como conferido na etapa 4. Um nome `=HYPERLINK(...)` fica como texto.
- **Separador do id:** o id do bloco é `'conta' + '\u0001' + nome`; `salvarConta` e `contasLimpo` recusam caracteres de controle `\u0000-\u001f` no nome, então o nome não consegue injetar outro `\u0001` e confundir `xlBloco` (`app.js:769`).
- **Backup forjado:** `validarBackup` rejeita o arquivo inteiro se `contas` não for objeto de listas de `{nome, formula}` texto; corta em 200 relatórios x 50 contas; nome até 60, fórmula até 300; nomes repetidos (normalizados) são descartados. A fórmula restaurada é compilada pelo mesmo parser na hora do uso; se não compilar, a conta é ignorada (`app.js:355`). "Substituir" e "Apagar tudo" zeram `contas` (`app.js:905`, `app.js:913`).
- **Pedido escrito:** `pedLimpo` aceita `medida: 'conta'` só com `campo` que passa em `txtOk`; se a conta sumir, `faltaPed` mostra aviso por `text` e o Excel mostra aviso como texto.

## Achados

### B-1 (Baixo) — nome da conta aceita caracteres invisíveis e de direção do texto
- **Onde:** `src/app.js:452` (`contasLimpo`) e `src/app.js:670` (`salvarConta`).
- **Prova:** o filtro só barra `\u0000-\u001f`. Passam `\u007f-\u009f`, `​-‏`, `‪-‮` e `⁦-⁩`. Um backup forjado pode trazer uma conta cujo nome, com `U+202E`, aparece invertido no painel e na planilha, ou duas contas que parecem iguais na tela e não são (a deduplicação usa `Core.norm`, que não tira esses caracteres).
- **Risco:** só engano visual; não executa nada e não vaza dado.
- **Correção:** trocar a regra por `/[\u0000-\u001f\u007f-\u009f​-‏‪-‮⁦-⁩﻿]/` nas duas funções (de preferência numa constante só) e criar teste de regressão com nome contendo `U+202E` no salvar e no backup.

### B-2 (Baixo) — fórmula recompilada a cada valor; 50 contas avaliadas sobre a lista inteira a cada `render()`
- **Onde:** `src/app.js:466-468` (`valorConta` compila de novo a cada chamada), `src/app.js:355-358` e `src/app.js:360` (`catalogo` chama `ex(todos)` de cada conta para filtrar), `src/app.js:534` (`calcPed` chama `valorConta` por grupo).
- **Prova:** cada conta pode ter cerca de 30 funções; com 50 contas e 100 mil registros, um `render()` pode passar de 100 milhões de leituras, e isso se repete a cada troca de filtro. Um backup forjado com 50 contas pesadas trava a aba do próprio usuário.
- **Risco:** negação de serviço só local (a aba fica lenta); sem perda de dado.
- **Correção:** guardar o AST compilado por `(conjunto, nome, formula, versão dos campos)` num `Map` e invalidar ao salvar, remover ou mudar campos; no `catalogo`, decidir se a conta "dá para calcular" pela compilação (`f.ok`), sem avaliar sobre `todos`.

### B-3 (Baixo) — mensagem de estouro de pilha depende do texto do Chrome
- **Onde:** `src/core.js:368`.
- **Prova:** o `catch` só troca a mensagem quando ela é `'Maximum call stack size exceeded'`; no Firefox o texto é `too much recursion` (`InternalError`) e iria cru para a tela. Hoje a profundidade é limitada (40), então o caso não foi alcançado nos testes; é defesa em profundidade.
- **Correção:** testar `e instanceof RangeError || /recursion|call stack/i.test(e.message)`, ou lançar erros próprios com uma marca (`e.gsi = true`) e mostrar "fórmula complicada demais" para qualquer outro erro.

## Observações (não são achados de segurança)

- Restaurar com "Somar" descarta em silêncio as contas acima de 50 (`app.js:907`); "Meus indicadores" e sinônimos avisam por `toast`. Vale o mesmo aviso.
- `acharConta` aceita nome parecido a 80% (`app.js:478`): uma conta chamada, por exemplo, "total" pode capturar um pedido escrito que não era sobre ela. É questão de produto (a pessoa confirma em "É isso?"), não de segurança.
