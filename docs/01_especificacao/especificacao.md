# Raio X do Relatório — Especificação v1.0

Agente 2 (Especificador) · 25/11/2026 · base: `docs/00_concepcao/concepcao.md` (portão 1 aprovado pelo Galindo em 25/11/2026 14h18)
Caminho direto (Método 5.5, 1.8.4): **sem encaixes e sem dublês**. Critérios rodam contra dados reais anonimizados em `tests/dados/`, sem rede.
Status: **esperando Galindo (portão 2)**.

---

## 0. Regras gerais (valem para todas as etapas)

**O que quero**
- App de uma página, estático (GitHub Pages), que roda inteiro no navegador. Todas as bibliotecas ficam em `vendor/` no próprio repositório.
- Termos neutros na tela: **registro** (cada linha), **campo** (coluna), **código** (campo que identifica o registro), **conjunto** (todos os registros de um mesmo tipo de relatório).
- Todo número do painel é clicável e abre a janela com os registros por trás dele (comportamento atual das janelas: arrastar, minimizar, filtrar por chips, imprimir, copiar).

**O que NÃO quero**
- Nenhuma requisição para fora da própria origem (sem API, sem IA, sem CDN, sem analytics).
- Nenhum nome de cliente, hospital, pessoa ou sistema no código, fora dos **modelos prontos** (seção 9), que são arquivos de configuração separados.
- Nenhum dado de usuário no repositório (o repositório é público).

**Critérios**
- CA-01: com a rede bloqueada depois do 1º carregamento, abrir o app, ler um CSV e gerar o Excel funcionam (Playwright em modo offline).
- CA-02: durante todos os testes, nenhuma requisição sai para outra origem (log de rede do Playwright = só a própria origem).
- CA-03: `grep -i` por "HEV", "Edmundo", "hospital", nomes de supervisores e "MV" no `index.html`, fora do arquivo do modelo pronto, devolve 0.
- CA-04: o app abre em celular (390 px de largura) sem barra de rolagem horizontal na tela inicial.

---

## 1. Etapa 1 — Nome, cliente na Config, app instalável e offline

**O que quero**
- Título e cabeçalho "Raio X do Relatório". Config → "Empresa / cliente": nome do cliente, área, logo (imagem reduzida e guardada no aparelho). Esses dados aparecem no cabeçalho, na capa do Excel e na impressão.
- Manifesto e service worker: instalável ("Adicionar à tela inicial" / "Instalar"); depois da 1ª abertura funciona sem internet; versão nova é baixada na próxima vez com internet e ativada ao reabrir, com aviso "Versão nova instalada".
- Nomes de arquivo gerados: `RaioX_<relatório>_<data>.xlsx`; backup `historico_RaioX_<data>.json`.

**O que NÃO quero**
- Perder a configuração ou o histórico de quem já usa o link (migração automática do que está salvo).

**Critérios**
- CA-10: abrir com o armazenamento vazio → título "Raio X do Relatório", sem nome de cliente no cabeçalho.
- CA-11: preencher cliente "Empresa Teste", área "Operações" e um logo PNG → aparecem no cabeçalho; ao recarregar continuam; a capa do Excel gerado mostra "Operações · Empresa Teste" e o logo.
- CA-12: apagar o logo → some do cabeçalho e da capa.
- CA-13: o manifesto é válido (nome, ícones 192 e 512, `display: standalone`) e o service worker fica ativo após o 1º carregamento.
- CA-14: com configuração antiga salva (formato atual do `localStorage`), o app abre, mantém nomes genéricos, de-para e limites, e o histórico do IndexedDB continua com a mesma contagem de registros.
- CA-15: publicar versão nova → aparelho com a antiga, ao voltar a ter internet e reabrir, mostra "Versão nova instalada" e roda a nova.

---

## 2. Etapa 2 — "O que você quer acompanhar?"

**O que quero**
- Depois de ler os arquivos, o app conhece os campos de cada conjunto e o **tipo** de cada campo: texto, categoria (poucos valores repetidos), número, data, data e hora, duração, situação (categoria escolhida como situação), código.
- Abre a tela **"O que você quer acompanhar?"** com o **catálogo de indicadores possíveis**. Cada indicador só aparece se os campos de que precisa existem e têm valor em pelo menos 1 registro. Cada um mostra o resultado real como exemplo.
- Catálogo mínimo:

| Indicador | Precisa de | Exemplo na tela |
|---|---|---|
| Total de registros | nada | "1.284 registros" |
| Quantidade por categoria (top 10 + outros) | 1 categoria | "Por região: Sul lidera com 57" |
| Soma / média / mediana de um número | 1 número | "Valor total: R$ 48.210" |
| Soma / média de um número por categoria | número + categoria | "Valor por cliente: …" |
| Evolução por mês | 1 data | "Mês com mais registros: out/2026 (212)" |
| Tempo entre duas datas (mediana, faixas, % dentro do prazo) | 2 datas | "Mediana: 1 d 4 h" |
| % de uma situação | situação | "Concluídos: 87,4%" |
| Registros sem valor num campo | qualquer campo | "38 sem responsável" |
| Mais antigos em aberto | data + situação | "Mais antigo: 12/03/2026" |

- O que for marcado vira **bloco** no painel: números em cima, gráficos no meio, **tabela de registros sempre embaixo**. A escolha fica salva por conjunto; o botão "O que acompanhar" reabre a tela.
- Os indicadores de um **modelo pronto** (seção 9) vêm marcados quando o conjunto é reconhecido como daquele modelo.

**O que NÃO quero**
- Indicador que não dá para calcular aparecer (ex.: tempo entre datas sem 2 datas).
- Exemplo inventado: todo exemplo é calculado dos dados carregados.

**Critérios**
- CA-20: arquivo `tests/dados/vendas.csv` (código, data, cliente, região, valor, situação) → tela lista Total, Por cliente, Por região, Valor (soma/média), Valor por região, Evolução por mês, % por situação; **não** lista "Tempo entre duas datas".
- CA-21: o número de exemplo de cada indicador é igual ao calculado pelo oráculo do teste (script Python sobre o mesmo CSV).
- CA-22: marcar 3 indicadores e confirmar → painel com 3 blocos na ordem número → gráfico → tabela de registros no fim.
- CA-23: recarregar → mesmos 3 blocos; reabrir "O que acompanhar" → os 3 continuam marcados.
- CA-24: campo com ≤ 30 valores distintos e ≥ 50% de repetição é sugerido como categoria; a pessoa pode trocar o tipo do campo na tela de colunas.
- CA-25: arquivo do modelo pronto de ordens de serviço → painel atual completo (todas as abas da seção 9), sem passar pela tela.

---

## 3. Etapa 3 — Pedido escrito com "É isso?"

**O que quero**
- Caixa "Peça um indicador". O app separa a frase em: **medida** (quantidade, soma, média, mediana, mínimo, máximo, percentual), **campo** da medida, **agrupar por**, **filtros** (valor de categoria, situação) e **período** (mês por nome, ano, "este mês", "mês passado", "este ano", "de dd/mm a dd/mm", "últimos N dias").
- Reconhece nomes de campos e valores **pelos dados carregados**, aceitando erro de digitação (semelhança ≥ 80%), sem acento e no plural. Sinônimos editáveis na Config (ex.: "qtd" = quantidade, "atendimento" = campo X).
- Mostra o que entendeu em linguagem simples ("Quantidade de registros · por cliente · outubro/2026") e a **prévia** do bloco, e pergunta **"É isso?"**. Sim → bloco entra no painel. Não → botões para corrigir cada parte (medida, campo, agrupar, filtros, período).
- Frase não entendida → mostra 3 exemplos montados com os campos reais e os botões para montar clicando.

**O que NÃO quero**
- Adivinhar: parte que não foi entendida aparece como "não entendi: <trecho>", nunca preenchida por chute.
- IA ou serviço externo.

**Critérios** (sobre `vendas.csv`; o oráculo é a estrutura esperada e o valor calculado em Python)
- CA-30: "quantidade de pedidos por cliente em outubro" → {quantidade, agrupar: cliente, período: out do ano mais recente dos dados}.
- CA-31: "valor medio por regiao este ano, so concluidos" → {média de valor, agrupar: região, período: ano atual, filtro situação = concluído}.
- CA-32: "soma do valr por clinte" (erros) → {soma de valor, agrupar: cliente}.
- CA-33: "% de cancelados por mês" → {percentual com situação = cancelado, agrupar: mês}.
- CA-34: "quantos registros de 01/09 a 15/09" → {quantidade, período 01/09–15/09}.
- CA-35: "bom dia" → "não entendi" + 3 exemplos + botões; nada entra no painel.
- CA-36: responder "Não" e trocar o agrupar para região pelos botões → prévia atualizada; "Sim" → bloco no painel com o novo agrupar.
- CA-37: sinônimo "fat" = valor cadastrado na Config → "fat por cliente" = soma de valor por cliente.
- Bateria: `tests/pedidos.json` com pelo menos 40 frases e a estrutura esperada; meta: 100% das frases da bateria.

---

## 4. Etapa 4 — Excel seguindo o painel

**O que quero**
- "Gerar Excel" produz um arquivo com: **capa** (cliente, área, título, período real dos dados, filtros, data de geração, logo), e **uma planilha por aba do painel**, com os blocos na mesma ordem: números como cartões, gráficos como tabela de valores + gráfico, tabela de registros no fim.
- Mantém as opções atuais: período (tudo / mês / de–até), formato (uma planilha por relatório / tudo numa / arquivos separados), durações em "h min", percentuais formatados.

**O que NÃO quero**
- Fórmula ou macro no arquivo gerado (só valores, como hoje).

**Critérios**
- CA-40: painel com 2 abas (3 e 2 blocos) → Excel com capa + 2 planilhas; nomes das planilhas = nomes das abas; ordem dos blocos igual.
- CA-41: os valores de cada bloco no Excel são iguais aos da tela (leitura do .xlsx com openpyxl).
- CA-42: período "de 01/10 a 31/10" → a capa diz "Registros de 01/10/2026 a 31/10/2026" e os números batem com o filtro.
- CA-43: duração de 0,8 h aparece como "48 min"; 26 h como "26 h 00 min".
- CA-44: aba escondida no painel não sai no Excel.

---

## 5. Etapa 5 — Contas personalizadas

**O que quero**
- Config → "Contas personalizadas": nome + fórmula com `+ - * /`, parênteses, números e funções sobre o conjunto: `quantidade(filtro)`, `soma(campo, filtro)`, `media(campo, filtro)`, `mediana(campo, filtro)`, `dias(data1, data2)`, `distintos(campo)`. Filtro opcional no formato `campo = valor`.
- Validação na hora (campo inexistente, parêntese aberto, divisão por zero → mensagem clara) e prévia com os dados.
- Depois de salva, a conta aparece no catálogo da etapa 2 e é entendida pelo nome no pedido escrito ("<nome> por cliente").

**O que NÃO quero**
- Execução de código digitado (`eval` ou similar). A fórmula é lida por um interpretador próprio.

**Critérios**
- CA-50: "Ticket médio" = `soma(valor) / quantidade()` → igual ao oráculo.
- CA-51: "Taxa de cancelamento" = `quantidade(situacao = cancelado) / quantidade() * 100` → igual ao oráculo.
- CA-52: `soma(valr)` → erro "campo 'valr' não existe; você quis dizer 'valor'?"; não salva.
- CA-53: `quantidade(situacao = xyz) / quantidade(situacao = xyz)` → mostra "sem dados" (não "NaN" nem "Infinity").
- CA-54: "ticket médio por região" no pedido escrito → a conta agrupada por região.
- CA-55: fórmula `alert(1)` ou `constructor` → erro de fórmula, nada executa.

---

## 6. Etapa 6 — Editar layout

**O que quero**
- Botão "Editar layout" liga o modo edição: arrastar bloco (no celular: botões subir/descer), mover para outra aba (arrastar até a aba ou "Mover para…"), criar/renomear/reordenar/apagar aba, tamanho (pequeno, médio, grande), esconder/mostrar, duplicar, trocar forma (número, barras, linha, pizza, tabela, quando o tipo de dado permite), "Voltar ao padrão".
- O layout é salvo por conjunto, vai no backup e é o mesmo usado no Excel (etapa 4).

**O que NÃO quero**
- Apagar aba com blocos sem confirmar; blocos de aba apagada vão para a 1ª aba.
- Forma de gráfico que não combina com o dado (pizza com mais de 8 fatias vira barras, com aviso).

**Critérios**
- CA-60: mover bloco B para cima de A → ordem B, A na tela, após recarregar e no Excel.
- CA-61: criar aba "Reunião", mover 2 blocos para ela → aparecem lá e não na aba de origem.
- CA-62: apagar aba "Reunião" confirmando → os 2 blocos voltam para a 1ª aba.
- CA-63: duplicar bloco para outra aba → mesmo valor nas duas.
- CA-64: "Voltar ao padrão" → layout igual ao da etapa 2 para aquele conjunto.
- CA-65: backup → apagar dados → restaurar → mesmo layout e mesmos registros.
- CA-66: no celular (390 px), "subir" e "descer" mudam a ordem.

---

## 7. Etapa 7 — Todos os formatos de arquivo

**O que quero**
| Formato | Como lê |
|---|---|
| CSV / TXT (`;`, `,`, tab; UTF-8 ou Windows-1252) | direto (atual) |
| Excel .xlsx, .xls, .ods | biblioteca local; cada aba vira um conjunto candidato |
| JSON (lista de objetos) e XML (elementos repetidos) | direto |
| PDF com texto | biblioteca local; texto e colunas pela posição na página |
| PDF escaneado e imagem (JPG, PNG, foto ou print) | OCR no aparelho (português), com melhoria de imagem (cinza, contraste, endireitar) |
| .zip | abre e lê cada arquivo de dentro, qualquer mistura |

- Tudo que vem por **OCR ou PDF** passa pela **tela de conferência**: a tabela lida, com as células de baixa confiança marcadas, editável, e os botões "Confirmar" e "Descartar". Várias fotos do mesmo relatório viram um conjunto só (mesmos campos).
- Relatório "de impressão" (blocos, cabeçalho repetido por página) tem leitor próprio por modelo; o 1º é o detalhado do sistema do modelo de ordens de serviço (já existe).

**O que NÃO quero**
- Dado de OCR entrar sem conferência.
- Baixar o leitor de OCR toda vez: o modelo de idioma fica no cache depois do 1º uso.

**Critérios**
- CA-70: `tests/dados/vendas.xlsx` (mesmos dados do CSV) → mesmos resultados do CA-20.
- CA-71: `.ods` e `.xls` com os mesmos dados → mesmos resultados.
- CA-72: `vendas.json` e `vendas.xml` → mesmos resultados.
- CA-73: `vendas.pdf` (gerado do CSV, com texto) → tela de conferência; após confirmar, mesmos resultados.
- CA-74: `vendas_foto_1.jpg` e `vendas_foto_2.jpg` (fotos de impressão do mesmo relatório) → uma tela de conferência; ≥ 95% das células iguais ao original antes de corrigir; após corrigir as marcadas, mesmos resultados.
- CA-75: `.zip` com CSV + XLSX + JPG → os três lidos; o JPG passa pela conferência.
- CA-76: offline, depois de 1 uso do OCR → OCR funciona sem rede.
- CA-77: arquivo que não é tabela (ex.: PDF de contrato) → mensagem "Não encontrei uma tabela neste arquivo", nada entra.

---

## 8. Dados e armazenamento

- **Sem Supabase, sem R2, sem servidor.** Tudo no navegador:
  - `localStorage`: configuração, layouts de colunas aprendidos, indicadores escolhidos, layout do painel, sinônimos, contas personalizadas.
  - `IndexedDB`: registros de cada conjunto (chave = código do registro); juntar arquivos atualiza campo a campo, sem apagar o que o arquivo novo não traz (regra atual).
- O arquivo original não é guardado: lê, guarda os registros e descarta.
- Backup = um arquivo `.json` com tudo; restaurar substitui ou soma (pergunta).
- **Sensível:** os relatórios podem ter nomes de pessoas. Por isso nada sai do aparelho, e o repositório só recebe dados de teste anonimizados.
- Dados de teste em `tests/dados/`: `vendas.*` (fictício, gerado por script com semente fixa), e os CSVs reais do modelo de ordens de serviço **anonimizados** por script (`tests/anonimizar.py`: troca nomes de pessoas por "Pessoa 01…", mantém datas, situações e números).

**Critérios**
- CA-80: carregar o mesmo arquivo duas vezes → contagem não muda.
- CA-81: arquivo A (código, cliente) + arquivo B (código, prioridade) → registros com os dois campos; campo vazio em B não apaga valor de A.
- CA-82: 72 mil registros no histórico → painel abre em ≤ 5 s em notebook comum (medido no Playwright, máquina de CI).
- CA-83: nenhum arquivo em `tests/dados/` contém nome de pessoa real (lista de nomes de teste no script de conferência).

---

## 9. Modelo pronto "Ordens de serviço" (regressão do que já existe)

O app atual vira o 1º **modelo pronto**, num arquivo de configuração separado (`modelos/ordens-servico.js`): reconhecimento dos relatórios, abas, regras e frases padrão. Tudo abaixo já funciona e **não pode quebrar**; cada item é um critério de regressão.

- CA-90: realizadas = concluída + aguardando material + conserto externo + cancelada.
- CA-91: backlog não inclui aguardando material nem conserto externo; esses dois aparecem sempre **separados**, nunca somados.
- CA-92: % de atendimento ≥ 90% em verde; "% fantasma" (se resolver as com tratativa) em dourado; "faltam X para 90%".
- CA-93: tratativas reconhecidas pelas frases padrão da Config (semelhança ≥ 80%), vale a data mais recente; frase escrita pelo solicitante não conta; tratativa só conta no backlog.
- CA-94: repetidas: só registros abertos, pesos por raridade da palavra, "lugar diferente" não junta; ação sugerida por registro; ficam na aba "Para arrumar".
- CA-95: tempo até o 1º atendimento: faixas (até 1 h … mais de 7 dias), % em até 24 h, ainda sem atendimento.
- CA-96: durações mostradas em "h min".
- CA-97: abas Dashboard, Backlog (2ª), Tempos, Equipe, Para arrumar, Histórico, Config; filtros começam fechados.
- CA-98: histórico do relatório detalhado: soma por código, KPIs por ano, mês a mês, backup/restaurar/apagar.
- CA-99: Excel com as 6 opções atuais de relatório e os 3 formatos, valores iguais aos atuais para o mesmo arquivo (comparação com saída de referência gerada antes da mudança).
- Oráculo: antes de mexer no código, gerar **saídas de referência** (números da tela e Excel) com os CSVs anonimizados; depois de cada etapa, comparar.

Macro Excel (`excel/GeradorOS_HEV.bas`): continua só com o modelo de ordens de serviço; etapas 2 a 7 **não** vão para a macro nesta versão (ver P-01).

---

## 10. Segurança (Método 6, ajustado a app sem servidor)

- Sem login, sem segredo, sem chave: não há nada a proteger no servidor porque não há servidor.
- `Content-Security-Policy` por `<meta>`: `default-src 'self'; img-src 'self' data: blob:; connect-src 'self'; worker-src 'self' blob:` (confere CA-02).
- Arquivos lidos nunca são executados: texto vindo de arquivo é sempre inserido como texto (nunca `innerHTML` sem escapar). Teste: CSV com `<img src=x onerror=alert(1)>` num campo → aparece como texto (CA-100).
- Fórmulas das contas personalizadas por interpretador próprio (CA-55).
- Revisão de segurança (agente 5) antes de liberar cada etapa para o link público.

---

## 11. Testes e entrega

- Suíte Playwright em `tests/` (Chrome), rodando sobre `index.html` construído; `tests/rodar.sh` roda tudo e imprime uma linha de resumo.
- Ordem de cada etapa: Construtor + Testador (Testador recebe só esta especificação e os dados de teste) → suíte verde → Revisor → publicar no link com `?v=` novo → atualizar como-funciona e a tabela de etapas do documento do cliente.
- Publicação: GitHub Pages do repositório atual (push no `main`) e o artifact antigo do claude.ai deixa de ser atualizado (só o link do Pages vale).

## 12. Fora do escopo desta versão
- Compartilhar painel entre pessoas ou aparelhos em tempo real (só backup/restaurar).
- Ler letra de mão.
- Conectar direto em banco ou API de outro sistema.
- Idiomas além do português.
- Levar as etapas 2 a 7 para a macro Excel.

## 13. Perguntas abertas (PERGUNTAR AO GALINDO) — com decisão provisória
- **P-01** Macro Excel acompanha o Raio X genérico? *Provisório: não; fica só com o modelo de ordens de serviço.*
- **P-02** Nome do repositório e do link (hoje "O.S.H.E.V"). Renomear muda o link. *Provisório: mantém até você decidir.*
- **P-03** A meta de 90% vira configurável por indicador (cada cliente tem a sua)? *Provisório: sim, na Config, padrão 90%.*
- **P-04** O modelo pronto de ordens de serviço continua mostrando as frases e regras do hospital como padrão, ou começa vazio para cliente novo? *Provisório: frases genéricas de manutenção como padrão, editáveis.*
- **P-05** Ordem das etapas: 1 → 2 → 3 → 4 → 5 → 6 → 7? Ou trazer a 7 (formatos/OCR) para antes? *Provisório: ordem numérica.*
