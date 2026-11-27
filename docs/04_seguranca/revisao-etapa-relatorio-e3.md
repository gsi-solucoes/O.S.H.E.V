# Revisão de segurança: Raio X do Relatório, etapa E3 "formas de gráfico novas" (F-85)

- Data: 27/11/2026 · Revisor: Revisor de segurança (Método GSI, seção 6)
- Base: commit `18ea9d4` (F-85) comparado com `73e4d16` (F-84). Escopo: `git diff HEAD~1 -- src/` (`src/app.js`, `src/core.js`; `src/app.html` e a CSP não mudaram), seção 9c.10 da especificação, modelo `revisao-etapa-relatorio-e2.md`.
- O que foi revisado: `pizzaSvg` (rosca), `linhaSvg` (área), `radarSvg`, `bolhasSvg`, `velocSvg`, `desenhaItem`, `FORMAS_TIPO`/`LAY_FORMAS`, os `veloc` dos blocos `tempo` e `sit`, as formas novas em `relDefs` e as funções de geometria do `Core` (`arcoPath`, `radarOk`, `radarGeom`, `velocPonto`, `velocArco`, `bolhasGeom`, `areaPath`).
- Como foi conferido: leitura do diff e, no Node, as funções de geometria do `Core` com `Infinity`, `NaN`, valores negativos e 200 mil valores. A suíte Playwright **não** foi rodada, por ordem do coordenador (a porta 8767 estava em uso).

## Veredito

**A E3 pode ser liberada: não há achado Crítico nem Alto.** Os 2 Baixos são de exatidão do desenho, sem risco de segurança, e a fábrica corrige sozinha.

| Severidade | Quantidade |
|---|---|
| Crítico | 0 |
| Alto | 0 |
| Médio | 0 |
| Baixo | 2 |

## Checklist 6.3 (o que cabe a um app estático e offline)

| Item | Resultado |
|---|---|
| Segredos no repositório, no histórico e no HTML/JS | O commit não tem senha, token nem chave. |
| Sessão, limite de tentativas, RLS, bucket, porta 127.0.0.1, senha fora da URL | Não se aplica: o app não tem servidor, login nem banco remoto. |
| Logs sem conteúdo sensível | As linhas novas não têm `console.*`. |
| Rede e execução | As linhas novas não têm `fetch`, XHR, `sendBeacon`, `WebSocket`, `eval`, `new Function`, `innerHTML`, `insertAdjacentHTML`, `.apply(` nem `Math.max(...)`/`Math.min(...)` com espalhamento. A CSP de `src/app.html:6` não mudou. |
| Dublês (1.8) e IA paga | Não se aplica. |
| Visão do atacante | Sem servidor, quem tem o link não vê dado de ninguém. A entrada nova continua sendo **um arquivo de dados**: nomes de grupo e de campo, e os números. O pior que o arquivo consegue nas formas novas é um desenho errado (B-1). Ele não executa código, não faz rede e não trava a aba. |

## O que foi conferido e está bom

- **SVG só por DOM.** Todo elemento SVG sai do `sv()` (`src/app.js:907`), que usa `createElementNS` e `setAttribute(nome, String(valor))`. Os nomes de atributo são fixos no código e nenhum vem do arquivo. Os valores que vêm do arquivo (nomes de grupo `x[0]`, nomes de campo em `b.nome`/`i.titulo`, rótulos) entram só em:
  - `textContent` (rótulos do radar, `src/app.js:940`; total da rosca, :921);
  - `document.createTextNode` dentro de `<title>` (:913-919, 931, 936, 943, 950, 958, 963);
  - `setAttribute('aria-label' | 'title', ...)`, que não interpreta marcação.
  Atributos perigosos (`href`, `on*`, `style`) nunca recebem dado do arquivo: `style` e `fill` são constantes (`COR_PZ`, `var(--...)`). Os eventos são funções (`onclick`/`onkeydown`), nunca string. Na lista ao lado (`el(...)`, `src/app.js:4-9`), o nome vai por `text`, que vira `textContent`.
- **Forma escolhida vinda de fora.** `i.forma` do layout salvo ou do backup é validada contra `LAY_FORMAS` (`src/app.js:870`). Em `desenhaItem` (:971) ela também precisa estar em `formasDe(b)`, senão volta à forma de origem. `FORMAS_TIPO[tipoBloco(b)]` (:883) usa o prefixo do `id`, que é fixo no código (`cat`, `numcat`, `mes`, `sit`, `tempo`) e não vem do arquivo. Por isso não há busca por `__proto__`/`constructor`.
- **Meta da Config.** `cfg.meta` só entra como número finito (`cfgLimpa`, `src/app.js:31`; campo, :1772). `velocPonto` (`src/core.js:695`) limita o valor entre 0 e 100, então uma meta negativa ou enorme não tira o ponteiro do lugar.
- **Custo.** Os limites de grupos estão no código: rosca até 8 (`src/app.js:982`), radar de 3 a 10 e sem "Outros" (`Core.radarOk`, `src/core.js:682`). As bolhas só existem em `<Número> por <Grupo>`, que já chega cortado em 10 + "Outros" pelo `top10` (`src/app.js:707`), e o "Outros" é tirado (:984). Linha e área por mês são lineares no número de meses. As geometrias são lineares: `gMax`/`gMin` (`src/core.js:673-674`) são laços simples, que **substituíram** os `Math.max(1, ...lista)` antigos de `linhaSvg` e do gráfico Entrou/Saiu (`src/app.js:925` e :1638). Isso tira o risco de estouro da pilha com muitos meses. `radarGeom` com 200 mil valores levou 240 ms no Node, e na tela ele nunca recebe mais de 10. Não há laço O(n²).
- **Divisão por zero.** Rosca e pizza: com total 0 ou `NaN`, `!tot` cai em barras (`src/app.js:912`). Radar: `mx > 0 ? ... : 0` (`src/core.js:687`). Bolhas: `n1 > n0`, `m1 > m0` e `s1 > 0` protegem os denominadores (`src/core.js:698-704`), e a média só é calculada com a lista não vazia (`src/app.js:948`). `pctDentro` com lista vazia devolve `null` (`src/core.js:100`), que `velocSvg` mostra como "—". Uma volta inteira na rosca é encurtada em `arcoPath` (`src/core.js:677`), para o arco não sumir.
- **Teclado e acessibilidade.** Pontos, fatias, bolhas e o trilho do velocímetro ganharam `role="button"`, `tabindex` e Enter/Espaço, sem abrir caminho novo: `abrir`/`abre` são as janelas que já foram revisadas.

## Achados

### B-1 (Baixo) Número sem limite de dígitos vira `Infinity` e o desenho sai com `NaN`

- **Onde:** `Core.numero` (`src/core.js:49-55`, que já existia) aceita `^-?\d+(\.\d+)?$` sem limite de tamanho. As formas novas usam o valor sem conferir se é finito: `radarGeom` (`src/core.js:684-693`), `bolhasGeom` (:698-705), `arcoPath` (:676-680), `velocPonto` (:695), `pizzaSvg` com rosca (`src/app.js:911-923`) e `linhaSvg` com área (:924-933).
- **Prova (Node):** `Core.numero('9'.repeat(400))` devolve `Infinity`. A soma de dois valores perto de `1e308` dá o mesmo resultado, e `+Infinity` com `-Infinity` dá `NaN`. Com isso:
  - `radarGeom([Infinity,1,2])` põe o ponto do grupo infinito em `x/y = NaN` e **encolhe os outros para o centro**;
  - `bolhasGeom` devolve `y` e `r` iguais a `NaN`;
  - `arcoPath(..., NaN)` gera `d="... NaN NaN ..."`;
  - a rosca com um grupo infinito não desenha nenhuma fatia e mostra "∞" no centro.
- **Efeito:** só visual. O navegador ignora o atributo inválido (fica um aviso no console) e o gráfico sai vazio ou enganoso. Não executa código e não trava a aba. A lista e a tabela ao lado continuam com os valores.
- **Correção proposta:** em `Core.numero`, devolver `null` quando `!Number.isFinite(resultado)`, o que vale para o app todo. Nas formas novas, tratar o grupo que tiver soma ou média não finita como "sem valor": cair em barras, como já é feito com `!tot`. Teste de regressão: um CSV com um valor de 400 dígitos e um `<Número> por <Grupo>` em radar e em bolhas, conferindo que nenhum atributo `d`, `points`, `cx`, `cy` ou `r` contém `NaN`/`Infinity`.

### B-2 (Baixo) Valores negativos somem do desenho, mas continuam na legenda

- **Onde:** a rosca soma só os positivos para o total do centro (`src/app.js:912` e :921). O radar zera os negativos (`src/core.js:687`). As bolhas dão raio mínimo 2 a uma soma negativa (`src/core.js:699-702`).
- **Efeito:** com `<Número> por <Grupo>` e somas negativas (estornos, por exemplo), o total no centro da rosca não bate com a soma da legenda, e o grupo negativo aparece na legenda sem fatia. Não há risco de segurança, só de leitura errada.
- **Correção proposta:** quando algum item tiver valor menor que 0, a rosca e o radar caem em barras, com o aviso "Valores negativos: mostrando barras", e as bolhas mostram a soma no rótulo, como já fazem. Teste de regressão com um grupo de soma negativa.

## Observação (sem severidade)

- O `<svg>` recebe também um atributo `title` (`src/app.js:913, 926, 935, 949, 958`). No SVG ele não tem efeito, porque o nome acessível vem do `aria-label` e do `<title>` filho. É inofensivo e pode sair numa limpeza.
