# Revisão de segurança — Raio X do Relatório, etapa 7c (OCR de imagem e PDF escaneado no aparelho, F-65)

- Data: 26/11/2026 · Revisor: Revisor de segurança (Método GSI, seção 6)
- Base: `81080bd` + alterações ainda não commitadas (`git diff HEAD`: `src/app.js`, `src/core.js`, `src/app.html`, `sw.js`). `vendor/ocr/` e `vendor/LEIA-ME.md` (já commitados em `81080bd`) foram revisados como dependência nova. `index.html` é build e só serviu de página para os testes no Chrome.
- Escopo: `OCR`/`IMGS`, `ocrPronto` (injeção de `tesseract.min.js` e criação do leitor), `ocrPartes`, `ocrLer`, `infoImg`, `melhora`, `miniatura`, `imgCanvas`, `lerItem`, `lerImagens`, o desvio de imagem e de PDF sem texto em `lerBuf`, `conferir` com imagens, `Core.itensOcr`/`corrigeOcr`/`tabelaOcr`, o `accept` e `#cfImgs` em `app.html`, a CSP (sem mudança), o cache de runtime `raiox-ocr-v1` do `sw.js` e o registro das bibliotecas. Especificação: seção 0.10 (v1.9) e seção 10.
- A suíte não foi rodada, como pedido. Foram exercitados no Chrome (Playwright, `index.html` servido em `localhost` nas portas 8791 a 8793, já fechadas; sem service worker, salvo no teste do cache) 10 arquivos forjados gerados com Pillow e zlib (fora do repositório): PNG-bomba de 20.000² e 40.000², ruído de 3000², PDF escaneado com imagem de 20.000² e de 60.000², PDF de 3 páginas de ruído, PNG em branco, nome de arquivo com HTML; mais os 4 arquivos do leitor recusados um de cada vez (404 e queda de rede). Em todos: medidor de bloqueio da página (intervalo de 50 ms), registro de **todas** as requisições (página e workers) e de violações de CSP. `Core.corrigeOcr`/`tabelaOcr` no Node com tabelas sintéticas. Hashes conferidos contra `npm pack`.

## Veredito

**A etapa 7c pode ser liberada**: não há achado Crítico nem Alto. Há 1 Médio e 3 Baixos, que a fábrica corrige sozinha. O Médio (M-1) contraria a R-134 e o "nada trava" e deve ser corrigido antes da homologação.

| Severidade | Quantidade |
|---|---|
| Crítico | 0 |
| Alto | 0 |
| Médio | 1 |
| Baixo | 3 |

## Checklist 6.3 (o que cabe a um app estático e offline)

| Item | Resultado |
|---|---|
| Segredos no repositório, no histórico e no HTML/JS | O diff não tem senha, token nem chave. As fotos de teste (`vendas_foto_*.jpg`, `contrato_foto.jpg`) são geradas pelo `gerar_dados.py` com dados fictícios. |
| Sessão, limite de tentativas, RLS, bucket, porta 127.0.0.1, senha fora da URL | Não se aplica: não há servidor, login nem banco remoto. |
| Logs sem conteúdo sensível | O diff não tem `console.*` novo. O `logger` do tesseract.js só repassa o percentual para o toast. Nenhum erro de console com texto lido nos cenários. |
| Requisições externas e execução | **0 requisições** a outro host em todos os cenários (incluindo as dos workers do OCR e do pdf.js). O diff não tem `fetch`, XHR, `eval`, `new Function`, `innerHTML` nem `document.write`. A CSP não mudou e não tem `unsafe-eval` (até o `wait_for_function` do Playwright foi recusado por ela). |
| Dublês (1.8) | Não se aplica: não há serviço externo nem IA paga; o OCR é local. |
| Visão do atacante | Sem servidor, quem tem o link não vê dado de ninguém. A entrada nova é **uma imagem ou um PDF escaneado que alguém entrega para a vítima abrir**. O pior que um arquivo forjado consegue hoje é deixar a leitura ocupada por minutos (B-2). Não executa código, não faz rede, não lê nem altera o IndexedDB, e nada entra sem `Confirmar`. |

## O que foi conferido e está bom

- **Bibliotecas:** `npm pack tesseract.js@7.0.0`, `tesseract.js-core@6.1.2` e `@tesseract.js-data/por@1.0.0` têm os SHA-256 do `vendor/ocr/SHA256.txt`; `tesseract.min.js` e `worker.min.js` são idênticos a `dist/` do pacote, os dois `core/*.wasm.js` idênticos aos do core 6.1.2 e `lang/por.traineddata.gz` idêntico a `4.0.0_best_int/` do pacote de dados. Os hashes por arquivo do `SHA256.txt` batem com os arquivos.
- **CVEs:** não conheço aviso publicado para o tesseract.js 7.0.0 nem para o tesseract.js-core 6.1.2. O wasm traz Tesseract `5.1.0-284`, libpng `1.6.38`, zlib `1.2.12`, libtiff e libwebp (há CVEs públicos de decodificação para essas versões), mas **nenhum byte do usuário chega a esses decodificadores**: o app sempre entrega ao leitor um PNG refeito pelo canvas (`cv.toBlob`), tanto para imagem quanto para página de PDF. Quem decodifica o arquivo do usuário é o navegador (`createImageBitmap`) ou o pdf.js.
- **Carregamento sob a CSP:** a `<script>` injetada aponta para `vendor/ocr/tesseract.min.js` (mesma origem, `script-src 'self'`; caminho fixo, não vem de dado do usuário). `workerBlobURL: false` faz o worker subir como arquivo da mesma origem (`worker-src 'self'`), sem `blob:`; o core entra por `importScripts` **dentro do worker** e o wasm vem embutido no `.wasm.js` (nenhum `.wasm` buscado). O documento não compila wasm: `WebAssembly.validate` (teste de SIMD) não é compilação e não gerou violação; por isso não é preciso `'wasm-unsafe-eval'` na página. Nenhuma violação de CSP no console.
- **Nenhum caminho para CDN:** o código tem 3 padrões de jsDelivr (`workerPath` em `tesseract.min.js`; `corePath` e `langPath` em `worker.min.js`) e os três são sobrescritos por `ocrUrl(...)`. `corePath` termina em `.js`, então é usado direto (sem a escolha automática de variante, que montaria caminho próprio). `cacheMethod: 'none'` desliga leitura e escrita no IndexedDB do tesseract. Com cada arquivo local recusado (404 ou queda de rede), **nenhuma** requisição foi a outro host: falha de `tesseract.min.js`, `worker.min.js` ou do core dá a mensagem exata da R-134 em 2 a 4 s; falha do idioma, ver M-1.
- **Bomba de descompressão e imagem gigante:** PNG de 20.000 x 20.000 (430 KB, 400 megapixels) lido em 8,4 s, reduzido antes de desenhar (`createImageBitmap` com `resizeWidth`), maior bloqueio da página 0,98 s, `Não encontrei uma tabela neste arquivo`. PNG de 40.000² (1,6 MB, 1,6 gigapixel): o navegador recusa e sai `Não consegui ler bomba40k.png.` em 1,3 s. Aba não caiu em nenhum caso. Dimensões declaradas absurdas (até 2³² em PNG) viram tamanho 0 na redução e caem no `catch`.
- **PDF escaneado gigante:** página com imagem de 20.000² (390 KB) e de 60.000² (3,5 MB) desenhada em canvas de no máximo 2000 px (o pdf.js reduz a imagem no worker): 22 s e 15 s, maior bloqueio 0,25 s e 0,57 s, sem queda. O canvas de cada página é limitado a 2000 px no maior lado e o da melhoria a 3000 px (ampliação no máximo até 1600 px).
- **Endireitar por projeção:** amostragem com passo e teto de 150 mil pontos; 32 ângulos testados. No pior caso medido (ruído 3000², metade dos pontos escuros) a página ficou presa 1,4 s; não trava.
- **XSS:** arquivo chamado `"><img src=x onerror=window.pwn=1>.jpg` com tabela real: o `alt` da imagem fica `Imagem lida: "><img…` (por `setAttribute`), `Arquivo:` por `textContent`, `document.images` só tem a miniatura, `window.pwn` indefinido. As células seguem pelo `value` (helper `el`, revisado na 7b). A miniatura é `data:image/jpeg` (permitido por `img-src data:`), gerada pelo canvas.
- **Privacidade:** a imagem só vai ao worker como `Blob` em memória (`recognize(blob)`), nunca por `fetch`. No caminho real (`createImageBitmap`) **nenhuma** URL `blob:` é criada. Depois de um OCR com o service worker ligado, o `raiox-ocr-v1` tem só os 4 arquivos do leitor e nenhuma entrada `blob:`, `data:` ou de imagem; o `raiox-v6` só o precache. `Descartar` esvazia a tabela e `#cfImgs`.
- **Cache de runtime (`sw.js`):** só pedidos `GET` da própria origem cujo caminho contém `/vendor/ocr/`; grava só resposta `200` (um `404` de `vendor/ocr/` não entrou no cache, conferido). O `activate` preserva o `raiox-ocr-v1` ao subir `V` e apaga um `raiox-ocr-*` antigo quando o nome mudar. Envenenamento: exigiria servir conteúdo pela própria origem em HTTPS (GitHub Pages); não há entrada do usuário que vire chave de cache.
- **Prototype pollution:** `corrigeOcr` usa objetos com chaves `"i,j"` e tamanhos numéricos; `lerImagens` agrupa por `Map`. Cabeçalho `__proto__`/`constructor` vira coluna comum; `({}).polluted` continua `undefined`. Coordenadas `NaN`/`Infinity`/`1e308` dão `null` sem exceção.
- **Fluxo e limites:** nada entra antes de `Confirmar`; 20 imagens/páginas por envio (`resta` vale também para PDF escaneado); 120 s por imagem com `terminate()` do leitor (ruído 3000²: abandonado aos 127 s com `Não consegui ler ruido3000.png.`). Mensagens por `toast` (`textContent`).

## Achados

### M-1 (Médio) — se o arquivo de idioma não carrega, a leitura fica parada para sempre em `Lendo a imagem… 0%`
- **Onde:** `src/app.js` `ocrPronto` espera `Tesseract.createWorker(...)` sem limite de tempo; o limite de 120 s de `ocrLer` só começa depois. No `worker.min.js`, a falha ao buscar `por.traineddata.gz` lança `Network error while fetching …`, mas o `createWorker` do tesseract.js 7.0.0 não rejeita.
- **Prova (Chrome):** com `vendor/ocr/lang/por.traineddata.gz` respondendo 404, a importação de um PNG ficou **600 s** sem mensagem, até o teste parar; com a conexão desse arquivo derrubada, 60 s sem mensagem (parado no limite do teste). A página responde, mas o `carregar` não termina (`#status` não atualiza, os outros arquivos do mesmo envio esperam). Com os outros 3 arquivos recusados, a R-134 aparece em 2 a 4 s.
- **Risco:** disponibilidade, sem vazamento. Cenário real: no 1º uso a conexão cai depois de baixar `tesseract.min.js`, `worker.min.js` e o core (4 MB) e antes do idioma (1,4 MB); esses 3 ficam no `raiox-ocr-v1` e, offline, toda imagem trava do mesmo jeito, em vez da mensagem `O leitor de imagens ainda não está disponível neste aparelho. Use uma vez com internet.` da R-134.
- **Correção:** em `ocrPronto`, `Promise.race` de `createWorker` + `setParameters` com um limite (por exemplo 30 s); ao estourar, `terminate()` no que existir, `ocrW = null` e `throw 'indisp'`. Opcional: conferir antes (`fetch(ocrUrl('lang/por.traineddata.gz'), { method: 'HEAD' })` passa pelo SW e responde do cache). Teste de regressão: com `por.traineddata.gz` em 404 (e com a rota abortada), a mensagem exata da R-134 aparece em menos de 35 s e nenhuma requisição sai para outro host.

### B-1 (Baixo) — a regra 3 altera células de texto (sem dígito) dentro de coluna de códigos ou de números
- **Onde:** `src/core.js` `corrigeOcr`: depois de decidir o modo da coluna (≥ 60% de códigos ou números), aplica `cod()`/`troca()` a **todas** as células, inclusive as que não têm dígito; no modo código ainda tira os espaços.
- **Prova (Node):** coluna `Codigo` com `V001, V002, V0O3, Isento, Sem codigo` → `Isent0`, `Semc0dig0`; coluna `Valor` com `10,00 … Isento, N/D` → `1sent0`, `N/0`; coluna `Sala` com `B12, A3, Bloco Sul, Diretoria, C7` → `B10c05u1`, `Diret0ria`. Coluna só de texto não é alterada (conferido: `Bob Olsen`, `Zeta SA`, `DOIS`, `Ilha Bela` iguais, 0 marcadas).
- **Risco:** integridade do dado, não segurança: as células alteradas ficam marcadas e passam pela conferência, mas um `Confirmar` apressado grava texto estragado. A regra 3 diz que "texto de colunas de texto nunca é alterado"; uma palavra numa coluna de códigos é texto.
- **Correção:** só trocar a célula que tem ao menos um dígito **e** que, depois da troca, casa com o formato da coluna (`COD` no modo código, `NUM` no modo número); as outras ficam como estão (podem ser marcadas, sem alterar). Teste de regressão com os três exemplos acima: `Isento`, `Sem codigo`, `N/D`, `Bloco Sul` e `Diretoria` iguais ao lido.

### B-2 (Baixo) — sem teto de tempo por envio nem cancelamento; o desenho de PDF escaneado não tem limite de tempo
- **Onde:** `lerImagens` soma até 20 x 120 s; `lerItem` abre o PDF escaneado com `getDocument` e `render` sem o limite de 60 s que `lerPdf` tem; não há botão para parar; `melhora` roda na página.
- **Prova (Chrome):** uma imagem de ruído 3000² (9 MB) ocupa o leitor por **127 s** e termina em `Não consegui ler`; 20 dessas num zip (180 MB, dentro dos limites) dariam cerca de **42 min** de "Lendo a imagem…". PDF de 3 páginas de ruído: 104 s (cerca de 35 s por página; 20 páginas dariam uns 12 min). A página responde (maior bloqueio 1,4 s), mas o envio inteiro espera e não há como desistir sem recarregar.
- **Risco:** só lentidão local; nada é lido de fora nem enviado.
- **Correção:** teto total por envio (por exemplo 5 min; o restante sai com `<arquivo>: limite de 20 imagens.` ou mensagem própria na especificação) e um botão `Parar` no toast/janela que faz `terminate()`; em `lerItem`, aplicar o mesmo limite de 60 s do `lerPdf` a `getDocument` + `render` de cada página (`destroy()` ao estourar). Teste: 3 imagens de ruído com o teto reduzido no teste terminam com mensagem dentro do teto.

### B-3 (Baixo) — registro das bibliotecas do OCR com versão e licença divergentes
- **Onde:** `vendor/LEIA-ME.md`, `vendor/ocr/`, seção 0.10.
- **Prova:** o `package.json` do `tesseract.js@7.0.0` declara `"tesseract.js-core": "^7.0.0"`, mas o vendor usa o core **6.1.2** (o 7.0.0 existe no npm); a combinação funciona nos testes, mas não é a que o autor publica e testa. O `package.json` do `@tesseract.js-data/por@1.0.0` diz `"license": "MIT"`, o `LEIA-ME.md` diz Apache-2.0, e não há arquivo de licença para `lang/` (os dados de origem, do `tessdata_best`, são Apache-2.0).
- **Risco:** rastreabilidade de dependência e licença; nenhum risco de execução hoje (ver CVEs acima).
- **Correção:** ou subir para o core 7.0.0 (só as variantes `lstm` e `simd-lstm` `.wasm.js`, hashes novos, suíte 7c), ou registrar no `LEIA-ME.md` e na 0.10 por que o 6.1.2 foi mantido; corrigir a licença do pacote de dados para "MIT (pacote npm); dados `tessdata_best` Apache-2.0" e copiar o aviso para `vendor/ocr/lang/`.

## Observações (não são achados de segurança)

- **Worker sem CSP:** o GitHub Pages não manda cabeçalho CSP, então dentro dos workers do OCR e do pdf.js **não vale** o `connect-src 'self'` da `<meta>`. A garantia de "nenhuma requisição externa" é que os três caminhos estão explícitos e que a falha local não cai para o CDN (conferido). Ao atualizar o tesseract.js, repetir a busca por `jsdelivr`/`http` nos dois arquivos e o teste com cada arquivo em 404.
- **SRI opcional:** dá para pôr `sc.integrity = 'sha384-…'` na `<script>` injetada (vale para mesma origem) e proteger o `tesseract.min.js` contra cópia alterada no cache; o worker e o core não aceitam SRI por `importScripts`.
- **Cache "guardado primeiro" sem versão ligada a `V`:** ao trocar qualquer arquivo de `vendor/ocr/`, mudar o nome `raiox-ocr-v1`, senão o aparelho continua com o antigo para sempre. A expressão `/\/vendor\/ocr\//` não está ancorada ao escopo do app; hoje só o próprio app pede esses caminhos, mas `startsWith(new URL('vendor/ocr/', self.registration.scope).pathname)` é mais preciso.
- **Dois envios ao mesmo tempo:** `#arquivo` continua ativo durante o OCR; um segundo envio usa o mesmo `ocrW` e o `finally` do primeiro faz `terminate()` no meio do segundo (que sai por `Não consegui ler` em até 120 s). Desabilitar o botão durante `carregar` ou ter um leitor por envio.
- **Caminho antigo de imagem (sem `createImageBitmap`):** a URL `blob:` é revogada no `onload`, mas não no `onerror`; revogar nos dois.
- **Fotos com dados depois do fim do JPEG** (por exemplo "foto com movimento" de alguns celulares, que anexam vídeo depois do `FFD9`) são recusadas por `infoImg` (procura o fim só nos últimos 64 bytes) com `Não consegui ler`. Funcional, não de segurança.
- A `melhora` em 3000² prende a página até 1,4 s; se aparecer reclamação em celular fraco, mover para `OffscreenCanvas` num worker.

## Correção
(a preencher pela fábrica)
