# Bibliotecas de terceiros (cópias locais, o app não usa rede)

| Arquivo | Origem | Versão | Licença | SHA-256 |
|---|---|---|---|---|
| `xlsx.full.min.js` | npm `@e965/xlsx` (espelho mantido do SheetJS CE; `dist/xlsx.full.min.js`) | 0.20.3 | Apache-2.0 (`xlsx.LICENSE`) | `cc015130aa8521e7f088f88898eba949ccdcbfb38df0bd129b44b7273c3a6f41` |
| `exceljs.min.js` | npm `exceljs` | ver cabeçalho do arquivo | MIT | — |
| `jszip.min.js` | npm `jszip` | ver cabeçalho do arquivo | MIT ou GPL-3.0 | — |
| `pdf.min.mjs` + `pdf.worker.min.mjs` | npm `pdfjs-dist` (`legacy/build/`; módulo ESM, carregado só quando um PDF é escolhido) | 5.7.284 | Apache-2.0 (`pdfjs.LICENSE`) | `93a1c3b8106822070313c9a001623d086be33bc1f7743081eef27353f7266959` (pdf.min.mjs) · `cd10f3bdfa9bb5eb7632776675385f5948f4b09afe6b8b563b6199aa99d5da52` (pdf.worker.min.mjs) |

O tarball do npm `@e965/xlsx@0.20.3` tem SHA-256 `f93cd23533d5356f34d4b24ea48431f8cf8945d1ae1bd2045ab5d92163c82bb2` (conferido em 26/11/2026; `npm audit` sem alertas). O `cdn.sheetjs.com` (origem oficial) não é alcançável do ambiente da fábrica, por isso o espelho do npm; compare com o oficial quando possível. Para atualizar: `npm pack @e965/xlsx@<versão>`, copie o arquivo, atualize esta tabela e rode a suíte da etapa 7a.

O tarball do npm `pdfjs-dist@5.7.284` tem SHA-256 `f14db72530dec74fe666910e246242b9bb698df30f0e06622c4471b340a0413d`. Sem `eval` (o app abre com `isEvalSupported: false`) e sem rede.
