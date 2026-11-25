# Estado da homologação — etapa 1 (shell genérico)

Atualizado em 25/11/2026 pelo Construtor. Branch `etapa-1`. Nada publicado, nada no `main`.

## Pronto
- Junção (CA-81): arquivo com campo código de mesmo nome e códigos já existentes num conjunto entra nele campo a campo (só campos não vazios); sem códigos em comum, conjunto próprio.
- `src/core.js` novo e genérico: leitor CSV (`;` `,` tab, UTF-8/Windows-1252, cabeçalho automático), tipos por palpite, junção campo a campo, tempo entre datas em faixas e "h min", meta (padrão 90%), semelhança de texto (>= 80%), possíveis repetidos (peso por raridade).
- `src/app.js` + `src/app.html` novos: aba Painel (Total de registros, mais antigo/mais novo, barras por categoria e por mês, tempo entre datas, tabela de registros, filtros fechados no início: período tudo/mês/de–até, campo categoria, busca), aba Config (cliente, área, logo, metas, sinônimos vazios, formatos lembrados com "Esquecer", backup/restaurar/apagar, versão Excel com 4 passos).
- Importador "Esta coluna é o quê?" com formato lembrado (localStorage `raiox_fmt`); registros no IndexedDB `gos_hist` (store novo `registros`; o store antigo `os` fica intacto e é copiado uma vez como conjunto "Histórico anterior"); `gos_cfg` mantido.
- Janelas flutuantes (arrastar, minimizar para o rodapé, várias, chips, limpar seleção, imprimir A4, copiar).
- Excel (ExcelJS): capa com faixa de números, logo, período real e filtros; filtro automático, rodapé, impressão A4; formatos uma planilha por relatório / tudo numa / arquivos separados. Nome `RaioX_<relatório>_<data>.xlsx`; backup `historico_RaioX_<data>.json`.
- CSP por `<meta>` com hash do script embutido (calculado no `build.py`); texto de arquivo sempre por `textContent`/escape. Sem Google Fonts, sem CDN.
- `sw.js` v2 (inclui o `.bas` no cache; ignora outras origens), aviso "Versão nova instalada" (troca de versão do build ou troca do service worker).
- Conferido no Chrome/Playwright com CSV fictício fora do repositório: importa, total, tabela, janelas, Excel, backup, `.bas`, offline após 1º carregamento, 0 requisições externas, 390 px sem rolagem horizontal, termos proibidos = 0 no `index.html`.

## Falta / atenção
- `excel/RaioX_Relatorio.bas` ainda é o do caso de origem (CA-03/CA-16/CA-111 falham até ser reescrito; fora desta tarefa). Os passos falam da macro `Instalar`: confirmar o nome quando a macro nova existir.
- `README.md` e `docs/caminho-das-estrelas.md` não foram revisados.
- Migração do histórico antigo: campos viram os nomes das chaves guardadas (código = keyPath do store `os`); a regra do "genérico" da configuração antiga não é mantida (era do caso de origem).
- Cartão de repetidos olha até 5000 registros do filtro atual; CA-82 (72 mil) não medido.
- Etapas 2 a 7 não iniciadas.

## Conferência do coordenador (25/11/2026 14h55)
- Build da branch `etapa-1`: 0 termos proibidos no `index.html`.
- Suíte do Testador contra o build novo: **12 passam, 13 falham, 2 skip** (CA-15, CA-82).
- Causa das falhas: (1) a especificação não dá os **nomes dos botões e telas** (backup, restaurar, gerar Excel, campos cliente/área/logo, aba Histórico, tela "Esta coluna é o quê?"), então teste e app usaram textos diferentes; (2) macro `.bas` ainda é a antiga (CA-03, CA-16) — fica para a F-45.
- Próximo passo (nova sessão): Especificador acrescenta à seção 0 a **lista de nomes na tela** (rótulos exatos) e responde às dúvidas 1–3 do Testador (formato da mediana no CA-96; data no nome do arquivo no CA-98); depois Construtor e Testador alinham e a suíte roda de novo. Só então Revisor e publicação.

## Conferência do coordenador (25/11/2026 16h15)
- Suíte completa: **45 verdes, 2 skip** (etapa 1 + segurança + macro na oficina). Testes de segurança: 9 falham na versão anterior e passam nesta (servidor da suíte não reaproveita porta ocupada).
- Revisão de segurança: libera; M-1, M-3, M-4, B-2, B-4, B-6 corrigidos; pendentes: domínio próprio (M-2, Galindo), `frame-ancestors` e `style-src unsafe-inline` (B-3).
- Macro reescrita e rodando na oficina (LibreOffice); o que a oficina não cobre está no `roteiro-excel.md`.
- Falta: Galindo dizer "pode publicar no main". Próximo: F-46, etapa 2 na branch `etapa-2`.

## Etapa 2 (F-46) — Construtor, 25/11/2026, branch `etapa-2` (sem commit)
- **Feito:** catálogo de indicadores (R-53 a R-61) com exemplo calculado; janela R-51 (abre sozinha após ler conjunto sem escolha; Cancelar não salva); botão `O que acompanhar`; blocos na ordem número, gráfico, registros; escolha salva por conjunto em `localStorage` `raiox_acomp` e incluída no backup/restauração (somar/substituir/apagar); tipo `Situação` (sugestão por nome: situa/status/estado; conta como categoria nos filtros e gráficos); `Seu painel` + `Entender este painel`; planilha `Como ler este relatório` (2ª aba, só com escolha confirmada). Sem escolha, painel da etapa 1 idêntico.
- **Reutilização (etapas 3 e 6):** `resumoBlocos(c, blocos, L)` em `src/app.js` gera o texto a partir de qualquer lista de blocos; `catalogo(c)` e `blocosEscolhidos(c)` entregam os blocos.
- **Conferido** (Playwright próprio, 390 px, sem rolagem horizontal, 0 erros no console): vendas e chamados, exemplos, Seu painel com filtros (`só região Sul; outubro/2026`), Excel com a 2ª aba, backup com `acomp`.
- **Decisões/riscos:** (1) mediana do tempo no formato da etapa 1 (`11 h 50 min`), não `1 d 4 h` do exemplo da especificação (os dois textos da 0.3 divergem); (2) indicadores `Por`/`<Número> por` também para o campo Situação (superset do CA-20); (3) o tipo `Data e hora` da R-65 não existe separado (`Data` cobre as duas); (4) `Mais antigo` mostra a hora quando a data tem hora; (5) em aberto: situação vazia conta como em aberto (regra literal da 0.3); (6) conjuntos já guardados mantêm os tipos antigos (Situação só em formato novo ou após `Esquecer`).
- **Falta:** testes de aceite do Testador; CA-28 adiado (etapas 3 e 6).
