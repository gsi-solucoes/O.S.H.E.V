# Revisão de segurança — Raio X do Relatório, etapa 7b (PDF com texto e tela de conferência, F-64)

- Data: 26/11/2026 · Revisor: Revisor de segurança (Método GSI, seção 6)
- Base: `d5f5510` + alterações ainda não commitadas (`git diff HEAD`: `src/app.js`, `src/core.js`, `src/app.html`, `sw.js`, `vendor/LEIA-ME.md`). `vendor/pdf.min.mjs` e `vendor/pdf.worker.min.mjs` (já commitados em `d5f5510`) foram revisados como dependência nova. `index.html` é build e só serviu de página para os testes no Chrome.
- Escopo: `EXTS`/`PDFPAG`, `conferir` (janela `dlgConf`), `lerPdf`, o desvio de PDF em `lerBuf`, `Core.tabelaPdf`, o `accept` e o `dlgConf` em `app.html`, a CSP (sem mudança), o cache do `sw.js` (`raiox-v5`) e o registro da biblioteca no `vendor/LEIA-ME.md`. Especificação: seção 0.9 (v1.8) e seção 10.
- A suíte não foi rodada, como pedido. Foram exercitados no Chrome (Playwright, `index.html` servido em `localhost`, sem service worker) 12 PDFs forjados, gerados à mão (bytes crus + zlib), chamando `lerPdf` e `conferir` direto, com medidor de bloqueio da página (intervalo de 50 ms) e registro de todas as requisições; mais `Core.tabelaPdf` no Node com tabelas sintéticas, e o hash da biblioteca contra o tarball do npm. Os arquivos forjados ficaram fora do repositório.

## Veredito

**A etapa 7b pode ser liberada**: não há achado Crítico nem Alto. Há 1 Médio e 1 Baixo, que a fábrica corrige sozinha. O Médio (M-1) contraria o CA-110x ("nada trava") e deve ser corrigido antes da homologação.

| Severidade | Quantidade |
|---|---|
| Crítico | 0 |
| Alto | 0 |
| Médio | 1 |
| Baixo | 1 |

## Checklist 6.3 (o que cabe a um app estático e offline)

| Item | Resultado |
|---|---|
| Segredos no repositório, no histórico e no HTML/JS | O diff não tem senha, token nem chave (grep de `senha/token/secret/api key` só acha texto do POP). Os PDFs de teste são gerados pelo `gerar_dados.py` com dados fictícios. |
| Sessão, limite de tentativas, RLS, bucket, porta 127.0.0.1, senha fora da URL | Não se aplica: não há servidor, login nem banco remoto. PDF com senha não pede a senha (`getDocument` sem `onPassword` rejeita → `Não consegui ler`). |
| Logs sem conteúdo sensível | O diff não tem `console.*` novo. O pdf.js só escreve avisos técnicos (`getFontFileType`, `standardFontDataUrl`), sem texto do PDF. |
| Requisições externas e execução | O diff não tem `fetch`, XHR, `eval`, `new Function`, `innerHTML` nem `document.write` novos. Com os 12 PDFs forjados (link URI, `submitForm` em JavaScript, ação `Launch`, XFA) houve **0 requisições** fora de `index.html`/`vendor/`. A CSP não mudou: `script-src 'self' 'sha256-…'` (sem `unsafe-eval`, sem `blob:`), `worker-src 'self' blob:` (já existia), `connect-src 'self'`. |
| Dublês (1.8) | Não se aplica: não há serviço externo nem IA paga. |
| Visão do atacante | Sem servidor, quem tem o link não vê dado de ninguém. A entrada nova é **um PDF que alguém entrega para a vítima abrir**. O pior que um PDF forjado consegue hoje é travar a aba (M-1) ou deixá-la "lendo" por minutos (B-1); não executa código, não faz rede, não lê nem altera o que já está no IndexedDB, e nada entra sem `Confirmar`. |

## O que foi conferido e está bom

- **Biblioteca:** `vendor/pdf.min.mjs` e `vendor/pdf.worker.min.mjs` trazem a versão `5.7.284` no próprio arquivo. O tarball `npm pack pdfjs-dist@5.7.284` tem SHA-256 `f14db725…a0413d` (igual ao do `LEIA-ME.md`) e os dois arquivos são **idênticos** a `package/legacy/build/pdf.min.mjs` (`93a1c3b8…266959`) e `package/legacy/build/pdf.worker.min.mjs` (`cd10f3bd…5da52`), como registrado. Licença Apache-2.0 (`vendor/pdfjs.LICENSE`).
- **CVEs:** o CVE-2024-4367 (execução de JavaScript por `FontMatrix` de fonte forjada, via `new Function` no `FontFaceObject`) afeta até 4.1.392 e foi corrigido em 4.2.67; a 5.7.284 não é afetada. Na 5.x o caminho de `eval` das fontes foi removido: não há `eval(` nem `new Function` nos dois arquivos; os únicos `Function(…)` são do polyfill core-js (`return this`, `require` do Node), dentro de `try`, e a CSP da página os bloquearia. Não conheço outro aviso publicado para o pdf.js 5.x (não deu para rodar `npm audit`: o pacote não tem lockfile; as dependências opcionais do pacote são só do Node e não vão para o app).
- **Carregamento sob a CSP:** `import('./vendor/pdf.min.mjs')` (mesma origem, `script-src 'self'`) só acontece quando um PDF é escolhido; o worker sobe como **módulo da mesma origem** (`worker-src 'self'`), sem o `blob:` do `_createCDNWrapper` (só usado para worker de outra origem). Confirmado que o leitor roda no worker de verdade, não no "fake worker" da página: durante a bomba de 4 GB (29 s de leitura) o maior bloqueio da página foi de 58 ms. Nenhuma violação de CSP no console.
- **Opções de `getDocument`:** `enableXfa: false` (o texto `XFA-SEGREDO` do formulário XFA não aparece na tabela), `disableFontFace: true` (nenhuma fonte do PDF é instalada no documento), `useSystemFonts: false`; sem `cMapUrl`, `standardFontDataUrl`, `wasmUrl` nem `iccUrl`, por isso o worker não busca nada (só avisa). Só `getTextContent` é chamado: nada é desenhado, anotações e ações não são lidas, o `pdf.sandbox` (motor de JavaScript do PDF) não está em `vendor/`.
- **PDF ativo (`ativo.pdf`/`ativo2.pdf`):** `/OpenAction` e árvore `/JavaScript` com `app.alert` + `submitForm`, `/AA` na página e no campo, link URI sobre a página toda, ação `Launch calc.exe`, XFA com `<script>`: nenhum `alert`, nenhum popup, nenhuma requisição, `window.pwn` indefinido.
- **Fonte malformada:** TrueType com `FontFile2` de bytes aleatórios e `/Widths []`: só avisos (`Required "loca" table is not found`), sem exceção nem travamento; o texto sai sem largura útil e o resultado é `Não encontrei uma tabela neste arquivo`.
- **Muitos itens / muitas páginas:** uma página com 1 milhão de pedaços de texto (2,5 MB): 1,4 s no worker, página sem bloqueio, `null` → R-124. PDF de 500 páginas: lê só 200 (600 linhas = 200 x 3), como a regra 5.
- **Bomba de descompressão:** conteúdo de página `FlateDecode` de 1 GB (1 MB de arquivo) em 6,2 s e de 4 GB (4 MB) em 29 s, sem queda do worker e sem bloquear a página; a tabela escondida no fim é lida certa. Ver B-1 para o teto.
- **XSS na conferência:** `<img src=x onerror=…>` e `"><script>…</script>` dentro do PDF aparecem como texto da célula. Os valores vão para o atributo `value` por `setAttribute` (o helper `el`), o `aria-label` também por `setAttribute`, `Arquivo:` e as contagens por `textContent`, e a volta é lida por `.value`. `document.images` não cresce, `window.pwn` continua indefinido.
- **Prototype pollution:** `tabelaPdf` só usa arrays e um objeto `col` com chaves numéricas; cabeçalho `__proto__`/`constructor` vira coluna comum e segue para `processar`/`importar`, que já usam `nulo()`. `({}).polluted` continua `undefined` (Node e Chrome). Coordenadas `NaN`/`Infinity`/`1e308` não geram exceção.
- **Fluxo:** nada entra antes de `Confirmar`; `Descartar` e `Esc` fecham com `null`; o `onclose` limpa a tabela. Dentro de zip, cada PDF abre a sua janela em sequência (`await`). Mensagens por `toast` (`textContent`).
- **Cache offline:** `sw.js` passa para `raiox-v5` (o `activate` apaga o `raiox-v4`), acrescenta só os dois `.mjs` locais; o `fetch` continua recusando outra origem.

## Achados

### M-1 (Médio) — PDF de 6 MB trava a aba por mais de 18 minutos (conferência sem teto de colunas nem de células)
- **Onde:** `src/core.js` `tabelaPdf` não limita o número de colunas (o `MAXCOL = 200` das planilhas não vale para PDF) e roda **na página**, com `colDe` percorrendo todas as colunas para cada célula (custo linhas x colunas²); `src/app.js` `conferir` cria um `<input>` por célula (até 20.000 linhas x qualquer número de colunas) num só `DocumentFragment` e o `showModal` só acontece depois de montar tudo.
- **Prova:** no Node, `tabelaPdf` com 20.000 linhas x 100 colunas leva 3,3 s (364 MB); x 300 colunas, 10,6 s (852 MB); 20 milhões de pedaços (20.000 x 1.000) levam 45 s e 3,5 GB. No Chrome, `conferir` gasta cerca de 40 µs por célula: 200 mil células = 7,7 s, 500 mil = 20,8 s com a aba congelada. Pelo caminho real: PDF de 12 MB (`3.000 x 80`) congela a página por **12 s**; PDF de **6 MB** com 200 páginas x 100 linhas x 100 colunas (2 milhões de células) ficou **mais de 18 minutos** sem resposta até ser interrompido.
- **Risco:** negação de serviço local por um arquivo que alguém entrega (também dentro de um zip). Não vaza nem apaga dado (o IndexedDB fica intacto), mas contraria o CA-110x ("nada trava") e não há como cancelar.
- **Correção:** (1) em `tabelaPdf`, aplicar o mesmo teto de colunas das planilhas (`MAXCOL = 200`, passando-o como parâmetro) e um teto de células (por exemplo 400 mil = 20.000 x 20, ou 2 milhões como na F-66 para a leitura, e bem menos para a tela), acima disso `<arquivo>: arquivo grande demais.`; parar de chamar `monta` quando `rows.length > maxLin` (hoje monta todas e só descarta); trocar o laço de `colDe` por busca binária em `cols` (já está ordenado); (2) em `conferir`, não criar um `<input>` por célula para tabelas grandes: mostrar as primeiras N linhas (por exemplo 500) e paginar, ou criar o `<input>` só na célula clicada (célula como `td` com `textContent`), sempre com as marcadas visíveis; guardar as edições num array. Teste de regressão: o PDF de 200 páginas x 100 linhas x 100 colunas termina (janela aberta ou mensagem) em menos de 3 s, sem bloqueio maior que 1 s, e o `vendas.pdf` continua com 500 linhas e 0 marcadas.

### B-1 (Baixo) — bomba de descompressão deixa a leitura rodando por minutos, sem aviso nem cancelamento
- **Onde:** `lerArquivo`/`lerZip` limitam o tamanho do PDF **compactado** (50 MB); o pdf.js descompacta cada conteúdo de página inteiro no worker, sem teto; `lerPdf` não tem limite de tempo nem mostra progresso.
- **Prova (Chrome):** conteúdo `FlateDecode` de 4 GB num PDF de 4 MB: 29 s até o resultado. Um PDF de 50 MB chega a ~50 GB descompactados (estimado em ~6 min); um zip com vários desses soma. A página continua respondendo (o trabalho é no worker), mas a tela não diz nada e o próximo arquivo espera.
- **Risco:** só lentidão local; o worker não caiu em nenhum teste e nada é lido ou enviado.
- **Correção:** mostrar `Lendo <arquivo>…` no `#status` durante `lerPdf` e pôr um limite de tempo (por exemplo 60 s): ao estourar, `doc.destroy()`/`loadingTask.destroy()` e `Não consegui ler <arquivo>.`; somar por PDF o `tc.items.length` e parar ao passar de um teto (por exemplo 2 milhões de pedaços). Teste com a bomba de 4 GB: mensagem em até 60 s.

## Observações (não são achados de segurança)

- `isEvalSupported` **não existe** na 5.7.284 (o nome não aparece nos dois arquivos): a opção passada em `lerPdf` é ignorada. A proteção real é que a versão não tem caminho de `eval` e que a CSP da página não tem `unsafe-eval`. Corrigir a regra 5 da 0.9, o `vendor/LEIA-ME.md` e o comentário, para não dar a falsa ideia de que a opção protege; se uma versão futura voltar a ter a opção, ela continua valendo.
- O worker é carregado da mesma origem e, como o GitHub Pages não manda cabeçalho CSP, **dentro do worker não há CSP** (a `<meta>` só vale para a página). Hoje isso não importa (sem `eval`, sem URLs configuradas, 0 requisições medidas); só registrar que a proteção ali é o próprio pdf.js.
- Sem `standardFontDataUrl` o pdf.js avisa a cada PDF com fonte padrão (Helvetica etc.). A leitura de texto funciona; se um dia as larguras ficarem erradas em algum PDF real, a solução é copiar `standard_fonts/` para `vendor/` e apontar para ela (local, sem rede), não usar CDN.
- O `sw.js` guarda as bibliotecas por "guardado primeiro": ao trocar `pdf.min.mjs` numa atualização futura, lembrar de subir `V` (como foi feito agora), senão o aparelho continua com a versão antiga.
- Se o navegador não conseguir criar o worker de módulo, o pdf.js cai sozinho no "fake worker" (lê na própria página, mais lento e travando a tela); não aconteceu no Chrome, mas vale um teste no navegador mais antigo suportado.
- `tabelaPdf` acha o cabeçalho só na 1ª página (`linhas[0]`); PDF com capa sem tabela cai em R-124. Funcional, não de segurança.

## Correção
(a preencher pela fábrica)

## Correção (F-67, 26/11/2026)
M-1 (teto de 200 colunas, 1 milhão de células e 400 mil pedaços de texto; busca binária em `colDe`; conferência de tabela grande com `Mostrar mais linhas`), B-1 (limite de 60 s com `destroy()` e aviso `Lendo o PDF…`) e a documentação do `isEvalSupported` corrigidos, com 2 testes de regressão (`test_f67_*`); 7a + 7b: 68 verdes.
