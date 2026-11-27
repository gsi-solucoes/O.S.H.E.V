# Revisão de segurança: Raio X do Relatório, etapa E2 "O que o Raio X encontrou" (F-84)

- Data: 27/11/2026 · Revisor: Revisor de segurança (Método GSI, seção 6)
- Base: commit `f7672f6` (F-84) comparado com `bf2395a` (F-83). Escopo: `git diff bf2395a f7672f6 -- src/` (`src/app.js`, `src/core.js`; `src/app.html` não mudou), seção 9c.7 da especificação e a revisão da E1 (`revisao-etapa-relatorio-e1.md`). O `ef2250a` que veio depois só mexe no POP.
- O que foi revisado: `Core.achadosDe` (A1 a A9), `relAchados`, `achadosTela`, `window.__achados`, a parte `achados` de `relDefs` e a mudança em `relBase`.
- Como foi conferido: leitura do diff e, no Node (V8, o mesmo motor do Chrome), `Core.achadosDe` rodando com 72 mil registros forjados: muitos valores por categoria, `__proto__` como valor, 100 colunas meio vazias. Também foi medido o `Core.repetidos` com 5000 textos. Não havia Playwright nesta sessão, então o WebKit não foi testado. A suíte não foi rodada.

## Veredito

**A E2 não pode ser liberada ainda: há 1 achado Alto (A-1).** Ele volta ao Construtor. Também há 1 Médio e 2 Baixos, que a fábrica corrige sozinha.

| Severidade | Quantidade |
|---|---|
| Crítico | 0 |
| Alto | 1 |
| Médio | 1 |
| Baixo | 2 |

## Checklist 6.3 (o que cabe a um app estático e offline)

| Item | Resultado |
|---|---|
| Segredos no repositório, no histórico e no HTML/JS | O commit não tem senha, token nem chave. Os dados de teste (`tests/dados/achados.csv`, `sem_achados.csv`) são fictícios e saem do `tests/gerar_dados.py`. |
| Sessão, limite de tentativas, RLS, bucket, porta 127.0.0.1, senha fora da URL | Não se aplica: o app não tem servidor, login nem banco remoto. |
| Logs sem conteúdo sensível | O diff não tem `console.*` novo. |
| Rede e execução | O diff não tem `fetch`, XHR, `sendBeacon`, `WebSocket`, `eval`, `new Function`, `innerHTML`, `insertAdjacentHTML` nem `document.write`. A CSP de `src/app.html:6` não mudou. |
| Dublês (1.8) e IA paga | Não se aplica: as regras são fixas, sem IA e sem serviço externo. |
| Visão do atacante | Sem servidor, quem tem o link não vê dado de ninguém. A entrada nova é **um arquivo de dados**: os nomes de campo e os valores entram nas frases dos achados. Esse arquivo não executa código, não faz rede e não polui protótipo. O pior que ele consegue é travar a aba (A-1, M-1). |

## O que foi conferido e está bom

- **Texto vindo do arquivo vai sempre como texto.** `titulo`, `frase` e `porque` são montados por concatenação de strings (`k.n`, `val`, `gval`, `g.n`, `L[mi].codigo`) e só saem por `el(..., { text: ... })` (`src/app.js:1565`). No `el()` (`src/app.js:4-9`), `text` vira `textContent`. A lista vira `<ul>/<li>` e o botão usa `onclick` com função, nunca string. O `abre(a.titulo, a.lista)` segue para a `abrirJanela` que já existia e já foi revisada.
- **Protótipo.** Os objetos que usam valores do arquivo como chave (`ms` em `src/core.js:554`, `vals` em :567, `sv` em :578, `gv` em :582, `ds` em :604) só recebem `= 1`, que é um primitivo. Com o valor `__proto__`, o setter ignora a gravação. No Node, `Object.getPrototypeOf({}) === Object.prototype` continuou verdadeiro e `({}).x` continuou `undefined`. Não há poluição (só um efeito de exatidão, ver B-1). `id3[i]` usa índice numérico e `achadosTela` usa `regra`, que é fixa (`A1` a `A9`).
- **`window.__achados`** (`src/app.js:1633`) está previsto na especificação (9c.7) para os testes. Ele devolve uma cópia em JSON (`JSON.parse(JSON.stringify(...))`) só com `regra`, `titulo`, `frase`, `porque` e `codigos`, sem os objetos dos registros e sem referência ao estado interno. Os mesmos dados já estão na página, e nenhum script de fora roda nela por causa da CSP. Não expõe nada novo.
- **A9 (repetidos)** é limitado a 5000 registros e a 100 pares. No Node, `Core.repetidos` com 5000 textos levou 296 ms, e o índice por raiz (`df[k] <= 40`) evita comparar todos com todos. O índice dos pares é resolvido em `base` (`src/app.js:1631`), sem misturar com `L`.
- **A1 a A5 e A8 são lineares** em registros × colunas. A data no futuro deixou de contar como "último mês" no `relBase` (`src/app.js:1487`), o que é só uma comparação de string.

## Achados

### A-1 (Alto) A6 e A7 são quadráticos: com uma categoria de muitos valores, o Relatório trava por dezenas de segundos a cada redesenho
- **Onde:** `src/core.js:568-569` (A6: para cada valor distinto, `r1.filter` e `r2.filter` sobre os registros dos 2 últimos meses) e `src/core.js:580-584` (A7: para cada situação × grupo × valor do grupo, `base.filter` **e `L.filter` sobre todos os registros**; além disso, o `gv` de :582 é recalculado para cada valor de situação). O `relAchados` roda dentro de `relDefs` (`src/app.js:1504`), então a conta se repete a cada `renderRel`, ou seja, a cada filtro ou edição.
- **Prova (Node/V8, 72 mil registros em 2 meses, 3 situações e 1 coluna Categoria):**
  - com 100 valores, A6 + A7 levam 0,98 s;
  - com 1.000 valores, só A6 leva 1,7 s e A6 + A7 levam 8,5 s (com 5 situações);
  - com 5.000 valores, só A6 leva 7,2 s e A6 + A7 levam **23,0 s**.

  Cada coluna Categoria a mais soma outro tanto. O tipo `categoria` é decidido só pelas 200 primeiras linhas (`palpites`, `src/core.js:59-65`: até 30 valores distintos nessa amostra). Por isso, um arquivo real ordenado por data, com uma coluna como cliente ou cidade que ganha valores novos ao longo do tempo, chega a milhares de valores sem deixar de ser Categoria. Um arquivo forjado chega a cerca de 10 mil valores sem esforço. A aba fica sem responder e o navegador oferece "Página sem resposta". Isso também fura o limite de 5 s do CA-221.
- **Correção:** contar numa passada só, com `Map`.
  - A6: um laço sobre `r1` e outro sobre `r2`, cada um somando `cont1[val]++` / `cont2[val]++` e juntando as listas de índices por valor.
  - A7: para cada grupo, calcular **uma vez** `totalPorValor` (para o `pt`) e, para cada situação, `contagem[gval]` numa passada sobre `base`.

  O custo fica em O(n × colunas). Teste de regressão: `Core.achadosDe` com 72 mil registros e uma categoria de 5.000 valores em menos de 1 s no Node, mais o CA-221 medindo o Relatório com achados.

### M-1 (Médio) A3 repete o `Math.max.apply` da E1 e pode quebrar no Safari/iPhone com mais de 65 mil registros em aberto
- **Onde:** `src/core.js:543` (`Math.max.apply(null, ix3.map(...))`, com um argumento por registro em aberto há mais de 30 dias).
- **Prova:** é o mesmo padrão do M-1 da E1, que ainda está aberto em `src/core.js:618` (`estat`). O JavaScriptCore lança `RangeError` acima de cerca de 65.536 argumentos. O V8 aguentou 72 mil no Node. Um arquivo com 66 mil registros em aberto e antigos faz o `relAchados` lançar erro no iPhone, e a parte "O que o Raio X encontrou" (e o que vem depois dela no `renderRel`) não aparece. Não medi no WebKit.
- **Correção:** guardar o maior na mesma passada do `idx` (`if (d > maior) maior = d`) e corrigir junto o `estat` da E1. Teste de regressão: `Core.achadosDe` com 100 mil registros em aberto e o CA-221 no `webkit` do Playwright.

### B-1 (Baixo) Valor `__proto__` no arquivo some das contas de A6 e A7
- **Onde:** `src/core.js:567`, `:578` e `:582` (`{}` com `obj[valor] = 1`).
- **Prova:** no Node, 60 de 100 registros com situação `__proto__` e grupo `__proto__` deram 0 achados. A gravação `obj['__proto__'] = 1` é ignorada, então esse valor nunca entra em `Object.keys`. Não há risco de segurança (o protótipo fica intacto), só um achado que deixa de aparecer.
- **Correção:** usar `new Map()` ou `Object.create(null)`, o que já sai naturalmente da correção do A-1. Teste: `__proto__` e `constructor` como valores de situação e de grupo geram o achado A7 esperado.

### B-2 (Baixo) `relAchados` monta `lista` e `codigos` de todos os achados, mas a tela mostra só 5
- **Onde:** `src/app.js:1631` (`ix.map(...)` duas vezes para cada achado, sem corte).
- **Prova:** no Node, 72 mil registros com 100 colunas Texto meio vazias geraram 100 achados A8 de 36 mil índices cada. Isso deu cerca de 99 MB a mais no heap e 1 s, refeitos a cada redesenho. A tela usa no máximo 5 achados (`achadosTela`).
- **Correção:** montar `lista` só para os achados que vão para a tela (ou na hora do clique em `Ver os registros`) e `codigos` só no `window.__achados`. Opcional: limitar o A8 a um número fixo de campos.

## Observações (não contam como achado)

- O A9 olha só os 5000 primeiros registros filtrados (`src/app.js:1626`), e a frase não diz isso. Vale registrar como ⚖️ no POP.
- `a.ix.map(i => i, 0)` (`src/app.js:1631`) não serve para nada (o `0` vira `thisArg`). É só limpeza de código.
