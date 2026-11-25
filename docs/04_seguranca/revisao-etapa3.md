# Revisão de segurança — Raio X do Relatório, etapa 3

- Data: 25/11/2026 · Revisor: Revisor de segurança (Método GSI, seção 6)
- Base: `f952774` + mudanças **não commitadas** da etapa 3 (`git diff`: `src/core.js`, `src/app.js`, `src/app.html`; `index.html` é build).
- Escopo: "Peça um indicador" (`Core.entender`), "Meus indicadores" (`raiox_meus`), Config → Sinônimos (`raiox_sin`), backup/restauração dessas chaves.
- Régua: checklist 6.3 no que cabe a app estático, offline, sem servidor, repositório público.

## Veredito

**Libera a etapa 3**: nenhum achado Crítico ou Alto. Há 2 Médios (M-1, M-2), que a fábrica deve corrigir com teste de regressão antes da próxima etapa, e 4 Baixos (B-1 a B-4).

## Checklist 6.3 (o que cabe)

| Item | Resultado |
|---|---|
| Segredos no repositório e no histórico | Nada no diff. A busca por senha, token, chave e `BEGIN PRIVATE` só achou falso positivo (`desenha`). |
| Segredos no HTML/JS | Não há. |
| Sessão, limite de tentativas, RLS, bucket, porta 127.0.0.1, senha fora da URL | Não se aplica: sem servidor, sem login, sem banco remoto. |
| Logs sem conteúdo sensível | Nenhum `console.*` novo. |
| Requisições externas | Nenhum `fetch`, XHR, WebSocket, `sendBeacon`, `import()` ou URL nova. O pedido é entendido só por regras locais. |
| CSP/hash | CSP sem mudança (`script-src 'self' 'sha256-…'`, `connect-src 'self'`, `form-action 'none'`). O form novo `#fPed` faz `preventDefault`; se o JS falhar, o envio é barrado pelo `form-action 'none'`. `build.py` refeito numa cópia gera `index.html` **idêntico** ao do diretório. Sem `</script` em `src/app.js` nem `src/core.js`. |
| Dublês (1.8) | Não se aplica (sem serviço externo, sem IA paga). |

## O que foi conferido e está bom

- **XSS:** não há `innerHTML`, `outerHTML`, `insertAdjacentHTML` nem `eval` novos. A frase digitada, os trechos "não entendi", os nomes de campo, os valores do CSV, os apelidos e o resumo do pedido entram só por `el()` com `text`/nó de texto, `option.value` ou `setAttribute('aria-label')`. O `el()` só trata como evento chaves `on*` escritas no código, nunca vindas de dado. Os títulos dos blocos novos que chegam ao `imprimir()` (`document.write`) passam por `esc()`. O `style` das barras só recebe número.
- **`__proto__` como apelido:** `sinMap()` devolve objeto sem protótipo, então `n['__proto__'] = 'Valor'` vira chave própria; o `JSON.stringify`/`JSON.parse` mantém chave própria e `sinLimpo` copia para `nulo()`. Teste em Node: `Core.entender('soma de __proto__ por UF', {sin: {"__proto__":"Valor"}})` deu `campo: Valor, agrupar: UF`, e `({}).Valor` continua `undefined`.
- **JSON malformado no localStorage:** `store.get` cai no padrão no `catch`; `sinLimpo`/`meusLimpo` recusam não objeto, array, valor não texto, medida fora de `MEDS`, período fora do formato.
- **Backup:** `validarBackup` passa `sin` e `meus` por `sinLimpo`/`meusLimpo`; inválido recusa o arquivo inteiro. "Substituir" e "Apagar tudo" zeram `meus` (e "Substituir" zera `raiox_sin`).
- **ReDoS:** as regex do motor são ancoradas e sem aninhamento. A de pontuação (`[)"'…]+$`) é quadrática, mas com `maxlength=300` custa 0 ms (100 mil caracteres só pelo gancho de teste: 5,6 s).
- **Planilha "Como ler":** os textos dos blocos novos passam por `primitivo()` e `cortaCelula()`.

## Achados

### Médios

**M-1. Pedido que não passa em `pedLimpo` é salvo como `null`, quebra o painel e, ao recarregar, apaga todos os "Meus indicadores"**
- Onde: `src/app.js`, botão "Sim" em `abrirPedido` (`const lim = pedLimpo(ped) … l.push(lim)`).
- Prova: `pedLimpo` devolve `null` com mais de 10 filtros, ou com campo/valor de mais de 200 caracteres. Teste em Node: a frase `SP RJ MG BA PR SC RS GO DF ES PE CE` (categoria UF) gera 12 filtros. Como "Sim" não confere o retorno, `null` entra em `meus[c]` e é salvo. Em seguida, `render()` → `blocosMeus` → `resumoPed(null)` dá `TypeError` e o painel para de desenhar. Ao recarregar, `meusLimpo` recusa a lista inteira, `meus` volta vazio e o próximo `salvaMeus` grava por cima: o usuário perde todos os indicadores, sem aviso.
- Correção: em "Sim", se `!lim`, mostrar erro ("Pedido grande demais: até 10 filtros…") e não salvar. Em `meusLimpo` (leitura do localStorage), descartar só o item inválido, não a lista toda. Regressão: frase com 11 valores → "Sim" → painel continua desenhando e `raiox_meus` sem `null`.

**M-2. Os limites de leitura (200 sinônimos, 50 indicadores por relatório) não existem na gravação: passou do limite, tudo some**
- Onde: `#sinAdd` e "Sim" (sem limite); restauração "Somar" (`sn` junta os atuais com os do backup, e cada lado pode ter 200); `sinLimpo`/`meusLimpo` na leitura (`ks.length > 200` / `l.length > 50` → `null`).
- Prova: com 200 sinônimos, adicionar o 201º grava 201 chaves; `sinMap()` passa a devolver `{}`, a lista na Config aparece vazia e o próximo "Adicionar" grava só 1 sinônimo por cima. O mesmo vale para o 51º indicador de um relatório (no recarregamento todos são descartados) e para "Somar" de um backup com 150 sinônimos sobre 100 atuais.
- Correção: conferir o limite **antes** de gravar (toast "Limite de 200 sinônimos"); no "Somar", recusar ou avisar quando a soma passar; na leitura, cortar no limite em vez de descartar tudo. Regressão: 201º sinônimo recusado e os 200 continuam lá.

### Baixos

**B-1. Custo do motor de frase cresce com valores × palavras (trava a aba)**
- Onde: `src/core.js`, `achar()` × `sim()`/`casados()` (busca recursiva da maior substring comum), e `src/app.js` `ctxPedido` (percorre todos os registros a cada chamada; no editor "Filtro" é chamado uma vez por campo de categoria; `exemplosPed` chama `entender` até 6 vezes).
- Prova (Node): 20 campos de categoria × 500 valores de ~40 letras: frase típica de 8 palavras = **1,0 s**; frase de 60 palavras (300 caracteres) = **14,4 s** na thread principal. Valor de 2.000 letras iguais × frase de 300 letras iguais = 0,3 s. É negação de serviço só local (próprio arquivo, própria frase).
- Correção: pré-filtro barato antes de `sim()` (diferença de tamanho que já impede 0,8: `2·min/(a+b) < 0,8` → pula), cortar a chave do valor (ex.: 60 caracteres), montar `vls` uma vez por conjunto e reaproveitar `ctxPedido` no editor.

**B-2. Campo de texto/situação chamado `constructor`, `toString`, `valueOf`… derruba o pedido**
- Onde: `src/app.js` `ctxPedido` (`valores = {}`), lido em `src/core.js` como `(vals[k.n] || []).map`.
- Prova (Node): campo `constructor` do tipo `texto` e a frase `constructor x` → `TypeError: (vals[k.n] || []).map is not a function`; o "Pedir" não responde. Um campo de categoria chamado `__proto__` troca o protótipo do objeto local `valores` (não polui o `Object.prototype` global) e some de `Object.keys(vals)`. O mesmo padrão aparece em `cont = {}` no editor "Filtro" (hoje sem efeito visível).
- Correção: `valores = nulo()` e `cont = nulo()`; em `core.js`, `var vals = Object.assign(Object.create(null), ctx.valores)` e `Array.isArray(vals[k.n]) ? … : []`. Regressão: CSV com cabeçalhos `__proto__`, `constructor`, `toString` (já existe em `test_seguranca.py`) + pedido que cita cada um.

**B-3. Separador `\u0001` no editor "Filtro"**
- Onde: `abrirPedido` → editor "Filtro" (`k + '\u0001' + v` e `v.split('\u0001')`).
- Prova: nome de campo ou valor do CSV com `\u0001` é cortado no lugar errado e o filtro aplicado fica diferente do escolhido (integridade, sem execução).
- Correção: usar o índice da opção (`ops[i]`) como `value`, em vez de juntar textos.

**B-4. Gancho de teste `window.__entender` publicado no app**
- Onde: `src/app.js` (`window.__entender = …`).
- Prova: qualquer script da mesma origem chama o motor com frase sem limite de tamanho (sem `maxlength`); com a CSP atual não há script de terceiros, então o risco é baixo.
- Correção: aplicar o mesmo corte de 300 caracteres no gancho, ou expor só quando a página abre com parâmetro de teste.

### Informativo
- "Somar" de backup troca a lista inteira de "Meus indicadores" de um relatório pela do backup (`meus[k] = b.meus[k]`), em vez de juntar. Não é segurança; conferir se é o comportamento desejado na especificação.
- Testes de regressão sugeridos em `tests/test_seguranca.py`: (1) apelido `__proto__` adicionado e usado num pedido, sem `Object.prototype` alterado; (2) `raiox_sin`/`raiox_meus` com JSON quebrado e com `{"__proto__":…}` no localStorage; (3) backup com `sin` de 201 chaves e `meus` com item inválido é recusado; (4) frase com `<img src=x onerror=…>` e cabeçalho igual no CSV: nenhum elemento novo no DOM nos cartões "Seu pedido" e "Meus indicadores"; (5) M-1 e M-2 acima.
