# Análise à mão: como eu identifiquei cada arquivo (e com qual pista)

Regra do jogo: primeiro eu identifico olhando o arquivo cru, anoto a pista que me levou à conclusão
e escrevo o gabarito. Só depois o script tenta fazer igual.

## A. Ficha simples (NAO_ATENDIDAS_R_ORDEM_SERVICO.csv) — 107 registros
- Um texto aparece 107 vezes sempre no começo de um bloco ("Ordem de Serviço"), e logo abaixo vem um
  número que nunca se repete → **cada bloco é um registro** (pistas: repetição + identificador único).
- Textos com letra minúscula que se repetem 107 vezes, no começo da linha ("Situação", "Setor"...) são
  **rótulos**; o que vem à direita deles é o **valor** (pista: vizinho à esquerda).
- Linha só de rótulos ("Serviço / Funcionário / Data Inicial / Data Final / Tempo Gasto") seguida de
  linhas de valores → **cabeçalho em cima** (pista: rótulo em cima). Pode ter várias linhas → **lista**.
- "Data Inicial" sempre antes de "Data Final", ~5 min de diferença (pista: linha do tempo).

## B. Ficha com cabeçalho de página (R_ORDEM_SERVICO [xlsx]) — 96 registros
- Igual à A, mas a cada página repete: "Página:", "1", "24", "Emitido por:", "Em: 01/03/2024 17:07",
  "Período de ... Oficina: ...". **Pista nova (P-página):** linha que se repete com o MESMO valor a cada
  N registros, e não acompanha cada registro, é cabeçalho de página: vira informação geral, não dado.
- "Período de 01/02/2024 até 29/02/2024 Oficina: ENGENHARIA PREDIAL": **pista nova (P-célula):**
  rótulo e valor dentro da mesma célula ("Oficina: X").

## C. Agrupado (relatoriodetalhadas.csv) — 904 registros
- "Oficina:" e "Setor:" aparecem poucas vezes e valem para todos os registros que vêm depois
  → **contexto** (pista: aparece antes dos registros e menos vezes que eles).
- Cabeçalho "Nr.OS / Dt. Pedido / ... " em cima, uma linha por OS embaixo; o identificador (277378)
  não se repete. "Servico:" e "Funcionário da Oficina:" vêm logo depois → **detalhe do registro**.
- Linhas soltas com "1", "3"... e "Total da Setor:": **pista nova (P-total):** um número sozinho
  que é IGUAL à quantidade de registros do grupo que acabou de fechar é um **total**, não dado.
  O "904" do fim é igual ao total de registros do arquivo → total geral.

## D. Agrupado com outro espaçamento (Kaue [xls]) — 2416 registros
- Mesmo jeito da C, mas com linhas em branco no meio e as colunas em outras posições.
  Mesmas pistas funcionam porque nada depende da posição absoluta.
- "Setor:" às vezes sem valor → contexto vazio (não pode puxar o valor de outra coisa).

## E. Tabela com cabeçalho repetido e deslocado (relatorioresumidas.csv) — 904 registros
- 1ª linha = cabeçalho; uma linha por OS. O cabeçalho se repete por página e, numa das páginas,
  com OUTRO espaçamento: as OS dessa página ficam com as colunas empurradas.
  **Pista nova (P-encaixe):** quando a posição muda, encaixar pela sequência de tipos
  (número, data, texto longo, número pequeno, texto curto), não pela coluna.
- Linhas que começam com "*" e não têm número: **pista nova (P-marcador):** linha com o mesmo
  desenho de registro, mas sem identificador, é registro sem número (o total do rodapé confirma:
  "Total de Ordem de Serviço: 904" = 902 com número + 2 com "*").
- Linha de equipamento (HILL-ROM, ADVANCED E...) embaixo de um 2º cabeçalho → detalhe do registro.
- Rodapé "Total de Ordem de Serviço : 904" e "* O relatório imprimirá..." → total e nota.

## F. Planilha com área de título + tabela (Diego RC31 [xlsx]) — 119 registros
- Topo: título, "Setor: Manutenção", "Responsável: Diego", data → informação geral (contexto).
- Cabeçalho + linhas com código (305, 310...) que não se repete → registros.
- "TOTAL" no fim, e embaixo textos longos de orientação → total e notas (não são registros).
- "Área (m²)" repete igual em todas as linhas: é VALOR constante, não rótulo — porque a linha
  começa com número (**pista nova (P-linha):** linha que começa com valor é linha de valores).

## G. Formulário vazio (ABERTAS_R_ORDEM_SERVICO.csv) — 0 registros
- Só rótulos, nenhum valor. Sem repetição não dá para aprender pela repetição:
  **pista nova (P-sozinho):** com um bloco só, rótulo é o que tem cara de rótulo (minúscula ou ":").

## H. Inventados (outros ramos)
- 1 vendas: cabeçalho + linhas; 7 linhas sem "Cidade" → P-encaixe.
- 2 ficha de aluno: rótulo em cima; título "FICHA DO ALUNO" em MAIÚSCULAS repete por bloco
  → é título de bloco (mesmo texto em todo bloco, sem valor ao lado), não dado.
- 3 agrupado por vendedor, TAB, "Subtotal: N" = nº de registros do grupo → P-total.
- 4 "CLIENTE: CARLA DIAS" → P-célula (rótulo em maiúsculas, antes dos dois-pontos).
- 5 sem cabeçalho; "R$ 864" + "31" partidos pela vírgula → **pista nova (P-centavos):** célula de
  valor sem centavos seguida de célula com exatamente 2 dígitos, sempre juntas → é um valor só.
