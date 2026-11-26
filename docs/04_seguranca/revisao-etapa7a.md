# Revisão de segurança — Raio X do Relatório, etapa 7a (planilhas, JSON, XML e zip, F-58)

- Data: 26/11/2026 · Revisor: Revisor de segurança (Método GSI, seção 6)
- Base: `9c7a0db` + alterações ainda não commitadas (`git diff HEAD`: `src/app.js`, `src/app.html`, `sw.js`, `tests/gerar_dados.py`). `index.html` é build e só serviu de página para os testes no Chrome. `vendor/xlsx.full.min.js` (já commitado em `9c7a0db`) foi revisado como dependência nova.
- Escopo: `EXTS`/`MAXCOL`/`ZIP`, `valorTxt`/`dataTxt`, `lerPlanilha`, `tabelaDeObjetos`, `lerJSON`, `lerXML`, `tabelasDe`, `lerZipEntrada`, `lerZip`, `processar`, `lerBuf`, `lerArquivo`, `carregar`, o `accept` do botão em `app.html`, o cache do `sw.js` e a geração reprodutível em `gerar_dados.py`. Especificação: seção 0.8 (v1.7).
- A suíte não foi rodada, como pedido. Foram exercitados no Chrome (Playwright, `index.html`, sem service worker) 20 arquivos forjados, chamando `tabelasDe`, `lerZip` e `lerArquivo` direto; mais `npm audit` e o hash da biblioteca. Os arquivos forjados ficaram fora do repositório.

## Veredito

**A etapa 7a pode ser liberada**: não há achado Crítico nem Alto. Há 1 Médio e 2 Baixos, que a fábrica corrige sozinha. O Médio (M-1) contraria o CA-110x ("nada trava") e deve ser corrigido antes da homologação.

| Severidade | Quantidade |
|---|---|
| Crítico | 0 |
| Alto | 0 |
| Médio | 1 |
| Baixo | 2 |

## Checklist 6.3 (o que cabe a um app estático e offline)

| Item | Resultado |
|---|---|
| Segredos no repositório, no histórico e no HTML/JS | O diff não tem senha, token nem chave (grep de `senha/token/secret/api key` = 0). Os dados de teste são os fictícios do `gerar_dados.py`. |
| Sessão, limite de tentativas, RLS, bucket, porta 127.0.0.1, senha fora da URL | Não se aplica: não há servidor, login nem banco remoto. |
| Logs sem conteúdo sensível | O diff não tem `console.*` novo. |
| Requisições externas e execução | O diff não tem `fetch`, XHR, `eval`, `new Function`, `innerHTML` nem `document.write` novos. SheetJS não faz rede ao ler; `sw.js` só acrescenta a biblioteca ao cache local (`raiox-v4`). |
| Dublês (1.8) | Não se aplica: não há serviço externo nem IA paga. |
| Visão do atacante | Sem servidor, quem tem o link não vê dado de ninguém. A entrada de fora agora é **qualquer planilha, JSON, XML ou zip** que alguém entrega para a vítima abrir. O pior que um arquivo forjado consegue hoje é travar a aba (M-1, B-1); não lê, não envia e não altera dado de outro relatório. |

## O que foi conferido e está bom

- **Assinatura do arquivo (`lerPlanilha`):** `.xlsx`/`.ods` precisam começar com `PK`; `.xls`, com OLE (`D0 CF 11 E0`) ou `<` (XML 2003/HTML). Texto renomeado para `.xlsx` cai em `Não consegui ler`. Um `.xls` que é HTML com `<img onerror>` e `<script>` vira só texto de célula: nada entra no DOM (`document.images.length = 0`, `window.pwn` indefinido).
- **Opções de leitura:** `cellFormula: false` (fórmula vale o resultado guardado, nunca é avaliada), `sheetRows: 200001`, `cellDates: true`; `bookVBA` fica no padrão (desligado). `.xlsm`/`.xlsb` não estão em `EXTS`. Só `ce.v` é usado: hiperlink (`l`), HTML (`h`) e estilos da célula são descartados. Erro de célula (`t: 'e'`) vira vazio.
- **`!ref` declarado:** `<dimension ref="A1:XFD1048576"/>` com 2 células reais é ignorado pelo SheetJS (recalcula pelo conteúdo): 2 linhas x 2 colunas em 7 ms. O teto de 200 colunas e 200.001 linhas é aplicado no laço. O problema real é outro (M-1).
- **Datas:** com fuso `UTC` e `America/Sao_Paulo` o `vendas.xlsx` dá as mesmas datas do CSV (`05/01/2026`, `24/09/2026`).
- **JSON:** `[` x 200 mil aninhados → `[]` (sem exceção, sem travar); valor com 50 mil níveis vira texto JSON; JSON quebrado cai no `try` → `Não consegui ler`.
- **XML (`DOMParser`):** "billion laughs" (10^10) é recusado pelo Chrome (`parsererror` → `Não consegui ler`, 2 ms); entidade externa `SYSTEM "file:///etc/passwd"` não é carregada (célula vazia). O laço de `lerXML` é linear na prática: 40 mil irmãos iguais em 133 ms; alternados (`<a/><b/>`) em 148 ms.
- **Prototype pollution:** colunas `__proto__`, `constructor` e `toString` (JSON e planilha) viram colunas comuns; `idx`, `v` e o registro em `importar` usam `nulo()`; `fmts` e `conjs` também. `({}).polluted` continua `undefined` (também coberto em `test_etapa7a.py`).
- **Zip:** o limite de 200 MB é medido pelo tamanho declarado e **conferido na leitura** (`lerZipEntrada` conta os bytes de verdade e para ao passar de 50 MB por arquivo). Zip que declara 100 bytes e tem 60 MB: `a.csv` marcado `grande` sem ler o resto. 5 arquivos de 45 MB declarando 100 bytes cada: o JSZip 3.10.1 recusa (`uncompressed data size mismatch`) → `Não consegui ler`. Zip dentro de zip é ignorado com aviso. Caminhos: o JSZip 3.10.1 (já corrigido do CVE-2022-48285) normaliza `../fora.csv` para `fora.csv`; `/abs.csv`, `C:/x.csv` e `a\b.csv` são descartados pelo filtro. Os caminhos só viram nome sugerido e texto de mensagem; nada é gravado em disco.
- **Mensagens:** `toast` usa `textContent`; o nome sugerido vai para `value` de `input`. O caminho `ok/<img src=x onerror=1>.csv` aparece como texto.
- **Biblioteca `vendor/xlsx.full.min.js`:** versão `0.20.3` (conferida no arquivo), licença Apache-2.0 (`vendor/xlsx.LICENSE`). SHA-256 `cc015130…3a6f41`, idêntico ao `dist/xlsx.full.min.js` do tarball `@e965/xlsx@0.20.3` do npm. `npm audit` = 0 vulnerabilidades. Os CVEs conhecidos do SheetJS (CVE-2023-30533, prototype pollution, corrigido em 0.19.3; CVE-2024-22363, ReDoS, corrigido em 0.20.2) não afetam esta versão.
- **`gerar_dados.py`:** só regrava os dados fictícios com data fixa (CA-83); não lê nada de fora de `tests/dados/`.

## Achados

### M-1 (Médio) — planilha de 1,5 KB trava a aba por 17 s e ocupa meio GB
- **Onde:** `src/app.js` `lerPlanilha` (laço `for r … for c …` sobre o retângulo `!ref` inteiro, com `encode_cell` e `push` de `''` em cada posição vazia); `out` guarda todas as abas antes de processar; não há teto de abas nem de células.
- **Prova (Chrome):** `.xlsx` de 1,5 KB com cabeçalho em A1:B2 e uma única célula em `XFD200000`: `tabelasDe` leva **16,9 s** e devolve 200.000 x 200 posições (heap 469 MB). Com 4 abas iguais (2,5 KB), `lerArquivo` chega a **726 MB** e a janela da primeira aba abre só depois disso. Com uns 10 abas ou um zip com alguns desses arquivos a aba do navegador cai por falta de memória.
- **Risco:** negação de serviço local, com amplificação de ~300.000 vezes, por um arquivo que alguém entrega. Não vaza nem apaga dado (o que já estava no IndexedDB fica), mas contraria o CA-110x ("nada trava").
- **Correção:** (1) montar as linhas só a partir das células que existem (`Object.keys(ws)` sem as chaves `!…`, ou `dense: true` e percorrer `ws['!data']`), limitando as colunas à maior coluna com valor dentro das 200 e pulando linhas vazias; (2) teto de células por arquivo (por exemplo 5 milhões) e de abas (por exemplo 50), acima disso `<arquivo>: arquivo grande demais.`; (3) processar aba por aba em vez de montar todas antes. Teste de regressão: o `.xlsx` forjado acima termina em menos de 3 s, sem janela travada, e `({}).polluted` continua indefinido.

### B-1 (Baixo) — bomba de descompressão dentro do `.xlsx`/`.ods`
- **Onde:** `lerArquivo`/`lerZip` limitam o tamanho do arquivo **compactado** (50 MB); `XLSX.read` descompacta todas as partes internas na memória, sem teto.
- **Prova (Chrome):** `.xlsx` de 300 KB com `sheet1.xml` de 300 MB (espaços): 1,4 s e heap de 612 MB; com 700 KB/700 MB: 2,5 s e o SheetJS desiste sozinho (cai em `Não achei o cabeçalho`). Um zip com 50 desses passa nos limites do zip (cada um tem 700 KB reais) e trava a aba por cerca de 2 minutos.
- **Risco:** só lentidão/travamento local; o limite de texto do V8 impede que uma bomba única derrube a aba.
- **Correção:** antes do `XLSX.read`, abrir o `.xlsx`/`.ods` com o JSZip (já carregado) e aplicar a mesma conferência do zip (`ZIP.total` pelo tamanho declarado e pela leitura real com `lerZipEntrada`); acima disso, `arquivo grande demais`. Somar esse total ao do zip de fora quando a planilha vem dentro de um zip. Teste com a bomba de 300 KB.

### B-2 (Baixo) — biblioteca vem de um espelho de terceiro sem procedência registrada
- **Onde:** `vendor/xlsx.full.min.js` (pacote `@e965/xlsx`, republicação no npm; o SheetJS oficial publica 0.20.x só em `cdn.sheetjs.com`).
- **Prova:** o hash bate com o tarball do espelho, mas não deu para comparar com o arquivo oficial (o proxy desta sessão recusou `cdn.sheetjs.com`). Nenhum documento registra a origem nem o SHA-256.
- **Risco:** cadeia de suprimento: um espelho alterado passaria sem ser notado numa atualização futura. Não há indício de alteração.
- **Correção:** registrar origem, versão e SHA-256 (`cc015130aa8521e7f088f88898eba949ccdcbfb38df0bd129b44b7273c3a6f41`) num `vendor/LEIA.md` (o mesmo para JSZip e ExcelJS), conferir uma vez com `https://cdn.sheetjs.com/xlsx-0.20.3/package/dist/xlsx.full.min.js` e criar um teste que falha se o hash mudar sem atualização do registro.

## Observações (não são achados de segurança)

- No zip, arquivos sem extensão e caminhos descartados pelo filtro (`/abs.csv`, `C:/x.csv`, `a\b.csv`) somem **sem mensagem**; a regra 5 pede `formato não suportado (ignorado)`. E o teto de 50 conta também os de tipo não suportado (por exemplo `.pdf`), que não são "úteis".
- Zip com tamanho declarado falso cai em `Não consegui ler <arquivo>.` (erro do JSZip) em vez de `zip grande demais`; seguro, só a mensagem difere.
- `lerZip` usa o campo interno `_data.uncompressedSize` do JSZip; se ele sumir numa atualização, a conferência declarada vira 0 e só a leitura real protege (que já basta).
- `lerXML`: depois que um grupo vira `melhor`, as repetições seguintes não são conferidas como "filhos simples"; um elemento com netos no fim do grupo vira linha com o texto dos netos colado. Correção funcional, não de segurança.
- Para leitura mais rápida, `cellText: false` e `cellHTML: false` evitam gerar o texto formatado e o HTML de cada célula, que não são usados.

## Correção
(a preencher pela fábrica)
