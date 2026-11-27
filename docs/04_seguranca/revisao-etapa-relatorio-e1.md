# Revisão de segurança: Raio X do Relatório, tela Relatório etapa E1 (F-83)

- Data: 27/11/2026 · Revisor: Revisor de segurança (Método GSI, seção 6)
- Base: branch `rodada-auto` em `17ad5eb`, comparado com `origin/main` em `cc0c152`. Escopo: `git diff origin/main -- src/` (`src/app.html`, `src/app.js`, `src/core.js`), a seção 10 da especificação e as revisões anteriores em `docs/04_seguranca/`.
- O que foi revisado: `relatoriosLimpo`, `relG`/`salvaRel` (localStorage `raiox_relatorio`), `relMat`, `relOrdem`, `relDefs` (todas as partes), `renderRel`, `abrirRel`/`iniciaRel`, a janela `#dlgExp`, o backup (baixar, validar, somar, substituir), `Apagar todos os dados`, as funções novas do `Core` (`idadeDias`, `estat`, `extremos`, `concentracao`, `compara`, `periodoAnterior`) e a CSP.
- Como foi conferido: leitura do diff e, no Node, `relatoriosLimpo` extraído do `app.js` rodando com entradas forjadas (`__proto__`, `constructor`, 201 chaves, 51 partes, id repetido, tipos errados, textos de 1 MB, pior caso de tamanho). Não havia Playwright nesta sessão, então o WebKit não foi testado (ver M-1). A suíte não foi rodada; o CA-221 (72 mil registros em até 5 s no Chrome) já está no `tests/test_relatorio_e1.py`.

## Veredito

**A E1 pode ser liberada**: não achei nada Crítico nem Alto. Há 1 Médio e 4 Baixos, que a fábrica corrige sozinha. O M-1 precisa ser confirmado no WebKit e corrigido antes da homologação.

| Severidade | Quantidade |
|---|---|
| Crítico | 0 |
| Alto | 0 |
| Médio | 1 |
| Baixo | 4 |

## Checklist 6.3 (o que cabe a um app estático e offline)

| Item | Resultado |
|---|---|
| Segredos no repositório, no histórico e no HTML/JS | O diff não tem senha, token nem chave. O `git log -S raiox_relatorio` só mostra os commits da F-77/F-83. |
| Sessão, limite de tentativas, RLS, bucket, porta 127.0.0.1, senha fora da URL | Não se aplica: não há servidor, login nem banco remoto. |
| Logs sem conteúdo sensível | O diff não tem `console.*` novo. |
| Rede e execução | O diff não tem `fetch`, XHR, `sendBeacon`, `WebSocket`, `eval`, `new Function`, `innerHTML` nem `document.write`. Os `href` do índice são âncoras internas (`#rel-pN`, `#rel-como`) geradas pelo próprio código. |
| CSP | A `<meta>` de `src/app.html:6` não mudou (`script-src 'self' 'sha256-…'`, `object-src 'none'`, `base-uri 'none'`, `form-action 'none'`). O HTML novo não tem `<script>` nem atributo `on*`. Os `style=` novos (inline em `app.html` e `width:…%` em `app.js`) já eram cobertos por `style-src 'unsafe-inline'` e só levam números. |
| Dublês (1.8) | Não se aplica: não há serviço externo nem IA paga. |
| Visão do atacante | Sem servidor, quem tem o link não vê dado de ninguém. As entradas novas são **um arquivo de dados** (nomes de campo e valores que aparecem nas partes do relatório) e **um backup forjado** com a chave `relatorio` que alguém entrega para a vítima restaurar. Nenhuma das duas executa código, faz rede ou polui protótipo. O pior que conseguem é negar serviço (M-1, B-2). |

## O que foi conferido e está bom

- **Texto de arquivo sempre como texto:** todas as partes novas (capa, índice, resumo, números, pendências, os 10 mais antigos, entrou/saiu, distribuição, quem concentra, registros, como ler) montam a tela com `el()` (`src/app.js:4-9`), em que `text` vira `textContent`, filhos string viram `createTextNode` e atributos vão por `setAttribute`. Nome de campo (`k.n`, `g.n`, `cd`, `sit`), nome de conjunto (`c`), código e valores entram por esse caminho, inclusive `aria-label` e `<title>` do SVG (`createTextNode`). O título e a observação que a pessoa escreve vão para `input.value`/`textarea.value` e voltam por `text:`. `tabelaTxt` (`src/app.js:1493`) põe string por `String(x)` dentro do `el`.
- **`__proto__`/`constructor`:** `relatoriosLimpo` devolve `nulo()` (`Object.create(null)`). No Node, `{"__proto__":…,"constructor":…}` virou duas chaves próprias, `Object.getPrototypeOf(r) === null` e `({}).titulo` continuou `undefined`. `relG` é sempre `nulo()` (carga, substituir, apagar), então `relG[k] = …` no restaurar com Somar também não toca no protótipo.
- **Formato errado rejeita o arquivo inteiro:** em `validarBackup` (`src/app.js:68`), `relatorio` inválido devolve `null` antes de qualquer alteração. Conferido que dá `null`: mais de 200 relatórios, mais de 50 partes, `id` repetido, vazio ou com mais de 200 caracteres, `oculto` que não é booleano, `forma` objeto, `titulo`/`obs` que não são texto, `partes` que não é lista. O CA da E1 (`relatorio` = texto → backup rejeitado inteiro) já cobre o caso.
- **Textos longos:** título cortado em 80, resumo em 1000, observação em 500 e forma em 20, tanto na validação quanto no `oninput`; os campos também têm `maxlength`. Um título de 100 mil caracteres e uma observação de 1 MB foram cortados no limite. `p.n`/`resumoN` só são aceitos se forem número finito.
- **Forma do gráfico:** o valor guardado só é usado se estiver em `d.formas` (`src/app.js:1643`); fora disso vale `barras`.
- **Logo da capa:** o `cfg.logo` (`src/app.js:1634`) só é aceito pelo `cfgLimpa` como `''` ou `data:image/png;…`; `img-src` permite `data:`.
- **Apagar e backup:** `Apagar todos os dados` zera `relG` e grava `{}`. O backup baixado inclui `relatorio`. Substituir zera `relG`; Somar mantém o relatório que já existe no aparelho.
- **72 mil registros:** o CA-221 mede a abertura em até 5 s no Chrome. Escrever no resumo, no título ou na observação grava sem redesenhar (`mut(…, false)`). No Node, ordenar 72 mil registros com `localeCompare` (parte Registros) levou 79 ms.
- **Janela Exportar arquivo:** é um `<dialog>` com valores fixos. Por enquanto só chama o `gerarExcel` que já existia e não faz rede.

## Achados

### M-1 (Médio) Com mais de 65 mil números ou pendências, o relatório pode quebrar no Safari/iPhone
- **Onde:** `src/core.js:520` (`estat`: `Math.min.apply(null, v)` e `Math.max.apply(null, v)`, com `v` = todos os valores numéricos do campo) e `src/app.js:1522` (`Math.max(...abData.map(x => x.d))`, um argumento por registro em aberto).
- **Prova:** o JavaScriptCore (Safari e todo navegador no iOS) tem um limite de cerca de 65.536 argumentos por chamada e lança `RangeError` acima dele. O V8 (Chrome) aguenta: 72 mil passou no Node em 2 ms. Com o volume que a especificação pede (72 mil registros, CA-221), um campo Número preenchido em todas as linhas já passa do limite. `estat` é chamada no resumo executivo (`distDe` em `frasesResumo`), então o erro aparece no `vis.forEach` de `renderRel` e o relatório para logo depois da capa e do índice. Um arquivo forjado com 66 mil linhas basta para o relatório não abrir no iPhone da vítima. **Não medi no WebKit** porque não havia Playwright nesta sessão.
- **Correção:** calcular mínimo e máximo com laço ou `reduce` (`v.reduce((a, x) => x < a ? x : a, Infinity)`) em `estat` e no "mais antigo espera há". Conferir também o `Math.max(1, ...lin.map(...))` da linha Entrou/saiu (vai até o número de meses, então hoje não preocupa). Teste de regressão: `Core.estat` com 100 mil valores no Node, mais o CA-221 rodando no `webkit` do Playwright.

### B-1 (Baixo) Ao somar backups, o limite de 200 relatórios não é respeitado, e na carga seguinte as edições somem todas
- **Onde:** `src/app.js:1727` (`Object.keys(b.relatorio).forEach(k => { if (!relG[k]) relG[k] = … })`, sem teto), `src/app.js:1457` (carga: `relatoriosLimpo(...) || nulo()`) e `src/app.js:1441` (`ks.length > 200 → null`).
- **Prova:** somar dois backups com 150 relatórios editados cada grava 300 chaves. Na próxima abertura, `relatoriosLimpo` devolve `null`, `relG` vira vazio sem aviso, e a primeira edição sobrescreve o que estava guardado. O backup que o próprio app baixa nesse estado é recusado por inteiro na restauração. O mesmo vale se a pessoa editar relatórios de mais de 200 conjuntos (`relMat` cria a chave sem teto). O `layout` já tinha esse mesmo padrão e herda o problema. É improvável de acontecer, mas é o mesmo tipo de falha do SEG3_M2.
- **Correção:** no Somar, parar em 200 com o aviso `Limite de 200 relatórios: alguns do backup ficaram de fora.` (como meus/contas/sinônimos), e não criar um 201º em `relMat`. Teste de regressão no estilo do `test_SEG3_M2_somar_backup_que_estoura_o_limite_nao_apaga_a_lista`.

### B-2 (Baixo) No pior caso, `raiox_relatorio` passa da cota do localStorage e impede as outras gravações
- **Onde:** `REL_LIM` em `src/app.js:1437` e `relatoriosLimpo`. O nome do conjunto (a chave) não tem limite de tamanho.
- **Prova:** no Node, 200 relatórios com todos os campos no máximo dão **8,65 milhões de caracteres** em JSON, acima da cota de cerca de 5 milhões. Um backup forjado assim passa na validação (só tem cerca de 9 MB, e o limite do backup é 200 MB). Na restauração, `salvaRel` falha com `Sem espaço para guardar neste aparelho.` e a edição se perde ao recarregar. Se ficar perto da cota, quem passa a falhar são `cfg`, `layout` e `meus`. Uma chave de 1 milhão de caracteres também foi aceita. Escrevendo pela tela isso não acontece.
- **Correção:** teto total, por exemplo recusar o `relatorio` se `JSON.stringify(r).length > 1.000.000`, e limitar a chave a 200 caracteres, como o `id`.

### B-3 (Baixo) Na carga, uma entrada inválida no localStorage apaga todas as edições
- **Onde:** `src/app.js:1457`.
- **Prova:** basta um relatório com formato inválido em `raiox_relatorio` (por adulteração ou, mais adiante, por uma E2 a E5 que deixe a validação mais rígida) para descartar os outros também, e a gravação seguinte apaga tudo. O `layoutsLimpo(o, tolera)` (`src/app.js:853`) já resolve isso descartando só o item ruim na carga, e o SEG3_M1 pediu o mesmo para os pedidos.
- **Correção:** dar a `relatoriosLimpo` o mesmo modo `tolera` (só na carga do navegador): descarta o relatório ou a parte inválida e mantém o resto. O backup continua rejeitando o arquivo inteiro.

### B-4 (Baixo) A parte escondida ainda sai no arquivo exportado, e o botão Exportar aceita vários cliques
- **Onde:** `src/app.js:1680` (`$('#expOk').onclick = () => { gerarExcel(); }`).
- **Prova:** na E1, `Exportar` gera o Excel antigo, com todos os conjuntos que têm dados e todos os registros. Ele ignora o que foi escondido e as observações; isso só entra na E4 (9c.8: "parte escondida não sai"). A ajuda do `Editar relatório` diz "Esconder uma parte que você não quer mostrar", então a pessoa pode mandar o arquivo achando que a parte saiu. Além disso, o botão não fica desativado enquanto gera: com 72 mil registros, cada clique a mais monta outro arquivo inteiro na memória.
- **Correção:** desativar `#expOk` durante o `gerarExcel` e fechar a janela no fim. Até a E4, mostrar na janela a frase `Nesta versão o Excel ainda traz todas as partes e todos os registros.`, ou garantir que a E4 entre antes da homologação.

## O que fica para as próximas etapas

- E2 (achados): os textos de `a.titulo`, `a.frase` e `a.porque` já saem por `text:`, então as regras novas devem continuar devolvendo texto puro.
- E4 e E5: o título e as observações guardados vão para o Excel e o PDF. No Excel, manter a defesa de fórmula do SEG_M1 (texto que começa com `=`, `+`, `-` ou `@` não pode virar fórmula) também para título, resumo e observação. No PDF, `document.title` deve continuar sendo o nome fixo `RaioX_<conjunto>_<data>` (CA-280).
