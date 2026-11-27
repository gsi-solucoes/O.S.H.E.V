# Raio X do Relatório — Especificação v2.0

Agente 2 (Especificador) · 25/11/2026 · base: `docs/00_concepcao/concepcao.md` (portão 1 aprovado pelo Galindo em 25/11/2026 14h18)

**Histórico de versões**
- v2.0 (27/11/2026, tarefas F-77 + F-76, Especificador): seção 9c "Tela Relatório" (R-140 a R-169, CA-200 a CA-284, decisões provisórias D-64 a D-84, etapas E1 a E5, fontes da pesquisa). Muda o caminho do Excel (botão `Gerar relatório` → `Exportar arquivo`) e o visual do Excel (substitui R-81 e a barra `█` da 0.5 a partir da E4).
- v1.9 (26/11/2026, tarefa F-65, coordenador): seção 0.10 "etapa 7c: imagem e PDF escaneado com OCR" (R-130 a R-134, regras, CA-74 a CA-77b, CA-110z, decisões D-60 a D-63).
- v1.8 (26/11/2026, tarefa F-64, coordenador): seção 0.9 "etapa 7b: PDF com texto e tela de conferência" (R-120 a R-125, regras, CA-73, CA-73b a d, CA-77, decisões D-50 a D-52).
- v1.7 (26/11/2026, tarefa F-58, coordenador): seção 0.8 "etapa 7a: planilhas, JSON, XML e zip" (R-110 a R-112, regras, CA-70 a CA-72 e CA-75a, decisões D-40 a D-43).
- v1.6 (26/11/2026, tarefa F-57, coordenador): seção 0.7 "Nomes e regras — etapa 6" (R-100 a R-108, modelo do layout, regras, decisões D-30 a D-34).
- v1.5 (26/11/2026, tarefa F-55, Especificador): seção 0.6 "Nomes e regras — etapa 5" (R-90 a R-95, fórmula, textos de erro, pedido escrito com conta, decisões D-20 a D-23).
- v1.4 (26/11/2026, tarefa F-53, Especificador): seção 0.5 "Nomes e estrutura — etapa 4" (R-80 a R-89: planilha de painel, células-âncora, tipos e formatos de célula, capa); seção 4 completada (CA-41 a CA-43 detalhados, CA-45 a CA-50 novos; CA-40 e CA-44 adiados para a etapa 6 com teste `skip`). Na etapa 4 o painel tem uma única aba implícita, `Painel`. Nenhuma regra de negócio nova além das decisões de formato registradas na 0.5.
- v1.3 (25/11/2026): seção 0.4 "Nomes na tela — etapa 3".
- v1.2 (25/11/2026, tarefa F-46, coordenador): seção 0.3 "Nomes na tela — etapa 2" (rótulos, formatos de exemplo, regra de "em aberto", texto do "Seu painel"); CA-28 só vale quando existirem pedido escrito (etapa 3) e Editar layout (etapa 6): na etapa 2 fica marcado como adiado. Nenhuma regra de negócio mudou.
- v1.0 (25/11/2026 14h18): primeira versão; portão 2 em 14h43.
- v1.1 (25/11/2026 15h10, tarefa F-43): seção 0.1 "Nomes na tela (rótulos exatos)"; CAs das seções 1, 8 e 9 apontam para os rótulos; dúvidas do Testador decididas no próprio critério (CA-96 formato da mediana, CA-98 data no nome do arquivo, D-01 a D-08 na seção 0.2). Nenhuma regra de negócio mudou.
Caminho direto (Método 5.5, 1.8.4): **sem encaixes e sem dublês**. Critérios rodam contra dados reais anonimizados em `tests/dados/`, sem rede.
Status: ✋ **portão 2 aprovado pelo Galindo em 25/11/2026 14h43** (P-03 e P-05 confirmados como estão).

---

## 0. Regras gerais (valem para todas as etapas)

**O que quero**
- App de uma página, estático (GitHub Pages), que roda inteiro no navegador. Todas as bibliotecas ficam em `vendor/` no próprio repositório.
- Termos neutros na tela: **registro** (cada linha), **campo** (coluna), **código** (campo que identifica o registro), **conjunto** (todos os registros de um mesmo tipo de relatório).
- Todo número do painel é clicável e abre a janela com os registros por trás dele (comportamento atual das janelas: arrastar, minimizar, filtrar por chips, imprimir, copiar).

**O que NÃO quero**
- Nenhuma requisição para fora da própria origem (sem API, sem IA, sem CDN, sem analytics).
- Nenhum nome de cliente, pessoa, sistema ou ramo de negócio no código; nenhum indicador ou regra de negócio fixo: tudo nasce dos dados e da escolha da pessoa.
- Nenhum dado de usuário no repositório (o repositório é público).

**Critérios**
- CA-01: com a rede bloqueada depois do 1º carregamento, abrir o app, ler um CSV (`Carregar relatório`, R-02) e gerar o Excel (`Gerar Excel`, R-18) funcionam (Playwright em modo offline).
- CA-02: durante todos os testes, nenhuma requisição sai para outra origem (log de rede do Playwright = só a própria origem).
- CA-03: busca no `index.html` e no `.bas` pelos termos da lista `tests/termos_proibidos.txt` (nomes, siglas e termos do protótipo de origem; arquivo mantido pelo coordenador) devolve 0.
- CA-04: o app abre em celular (390 px de largura) sem barra de rolagem horizontal na tela inicial.

### 0.1 Nomes na tela (rótulos exatos) — etapa 1

Os textos abaixo são **exatos** (maiúsculas, acentos e pontuação). Os testes localizam os elementos **por estes rótulos** (`get_by_role(..., name=...)`, `get_by_label`, `get_by_text`), nunca por `id` ou classe. Foram adotados os textos que o app já usa. Mudar um rótulo = mudar esta tabela antes (nova versão da especificação).

| Nº | Rótulo exato | Tipo | Onde aparece | CA que usa |
|---|---|---|---|---|
| R-01 | `Raio X do Relatório` | título da página (`<title>`) e do cabeçalho | aba do navegador; topo | CA-10, CA-11 |
| R-02 | `Carregar relatório` | botão (abre a escolha de arquivos, aceita vários) | cabeçalho | CA-01, CA-11, CA-80, CA-81, CA-90, CA-91 |
| R-03 | `Painel` | aba | barra de abas | CA-93, CA-99, CA-100 |
| R-04 | `Config` | aba | barra de abas | CA-11, CA-12, CA-16, CA-91, CA-92 |
| R-05 | (não existe aba `Histórico` na etapa 1) | — | os registros aparecem na lista `Registros` do Painel | CA-100 |
| R-06 | `Registros` | título da lista de registros | Painel, abaixo dos blocos | CA-100 |
| R-07 | `Total de registros` | número clicável (abre janela) | Painel, 1º número | CA-93 |
| R-08 | `Empresa / cliente` | título do cartão | Config | CA-11 |
| R-09 | `Cliente` | campo de texto | Config → Empresa / cliente | CA-11 |
| R-10 | `Área` | campo de texto | Config → Empresa / cliente | CA-11 |
| R-11 | `Escolher logo` | botão (imagem) | Config → Empresa / cliente | CA-11 |
| R-12 | `Apagar logo` | botão (só aparece quando há logo) | Config → Empresa / cliente | CA-12 |
| R-13 | (sem botão Salvar) | — | Config salva sozinha a cada letra digitada ou logo escolhido | CA-11, CA-12 |
| R-14 | `Dados deste aparelho` | título do cartão | Config | CA-92 |
| R-15 | `Baixar backup` | botão (baixa `historico_RaioX_AAAA-MM-DD.json`) | Config → Dados deste aparelho | CA-14, CA-80, CA-81, CA-90, CA-92 |
| R-16 | `Restaurar backup` | botão (escolhe o `.json`); depois pergunta com título `Restaurar backup` e botões `Somar`, `Substituir`, `Cancelar` | Config → Dados deste aparelho | CA-92 |
| R-17 | `Apagar todos os dados` | botão; depois pergunta com título `Apagar todos os dados` e botões `Apagar`, `Cancelar` | Config → Dados deste aparelho | CA-92 |
| R-18 | `Gerar Excel` | título do cartão e botão | Painel, no fim | CA-01, CA-11, CA-12, CA-98 |
| R-19 | `Formato` com opções `Uma planilha por relatório`, `Tudo numa planilha`, `Arquivos separados` | lista de escolha | Painel → Gerar Excel | CA-98 |
| R-20 | `Gerar relatório` | botão **da macro** (não do app) | planilha da versão Excel | CA-110 |
| R-21 | `Esta coluna é o quê?` | título da tela de colunas | janela ao carregar formato novo | CA-91 |
| R-22 | `Confirmar` / `Cancelar` | botões | tela "Esta coluna é o quê?" | CA-91 |
| R-23 | `Formatos lembrados` | título do cartão | Config | CA-91 |
| R-24 | `Esquecer` | botão (um por formato lembrado) | Config → Formatos lembrados | CA-91 |
| R-25 | `Baixar versão Excel para o PC` | link de download | Config (cartão `Versão Excel para o PC`) e rodapé | CA-16 |
| R-26 | `Como instalar a versão Excel (4 passos)` | título que abre a lista numerada dos 4 passos (abre sozinho ao clicar em R-25) | Config → Versão Excel para o PC | CA-16 |
| R-27 | `Versão nova instalada` | aviso rápido (some sozinho) | rodapé da tela | CA-15 |
| R-28 | `Filtros` | painel que abre/fecha (começa fechado) | Painel, no topo | CA-99 |
| R-29 | `Relatório` | lista de escolha (conjunto) | Painel → Filtros | CA-99 |
| R-30 | `Período` com opções `Tudo`, `Mês`, `De–até`; campos `Mês`, `De`, `Até` (aparecem conforme a opção) | lista de escolha e datas | Painel → Filtros | CA-98, CA-99 |
| R-31 | `Campo de data` | lista de escolha | Painel → Filtros | CA-96, CA-99 |
| R-32 | `Campo categoria` | lista de escolha | Painel → Filtros | CA-99 |
| R-33 | `Valor` | lista de escolha | Painel → Filtros | CA-99 |
| R-34 | `Buscar texto` | campo de busca | Painel → Filtros | CA-99 |
| R-35 | `Minimizar` (o botão mostra `_`; `Minimizar` é o nome acessível) | botão | barra de título de cada janela | CA-93 |
| R-36 | `Fechar` (o botão mostra `×`; `Fechar` é o nome acessível) | botão | barra de título de cada janela | CA-93 |
| R-37 | `Limpar seleção` | botão | rodapé de cada janela | CA-93 |
| R-38 | `Imprimir` | botão | rodapé de cada janela | CA-93 |
| R-39 | `Copiar` | botão; ao copiar mostra `Copiado.` | rodapé de cada janela | CA-93 |
| R-40 | `Mediana:`; `Dentro de N h:`; faixas `Até 1 h`, `De 1 a 4 h`, `De 4 a 24 h`, `De 1 a 3 dias`, `De 3 a 7 dias`, `Mais de 7 dias` | textos do bloco de tempo entre datas | Painel | CA-96 |
| R-41 | `Metas`; `Meta dos indicadores em % (padrão 90)`; `faltam X para a meta` | cartão e campo da Config; texto no bloco percentual | Config; Painel | CA-97 |

### 0.2 Decisões sobre suposições do Testador (v1.1)

Divergências entre `tests/test_etapa1.py` e o app, decididas aqui. "Muda" diz quem ajusta.

- **D-01 (CA-11/12, R-13):** não há botão Salvar; a Config salva sozinha. O teste não deve clicar em "salvar". **Muda: Testador.**
- **D-02 (CA-92, R-17):** o botão é `Apagar todos os dados` (não "Apagar histórico"); confirmar com `Apagar`. **Muda: Testador.**
- **D-03 (CA-92, R-15/R-16):** backup e restaurar ficam na aba `Config`; o teste abre `Config` antes, clica em `Baixar backup` e restaura pelo campo do rótulo `Restaurar backup` (não pela "2ª entrada de arquivo" da página, que é a do logo). **Muda: Testador.**
- **D-04 (CA-100, R-05/R-06):** não existe aba `Histórico` na etapa 1; o texto do arquivo é conferido na lista `Registros` do Painel. **Muda: Testador.**
- **D-05 (CA-99, R-30):** o período De–até se usa escolhendo `De–até` em `Período` e preenchendo `De` e `Até` (por rótulo). O teste não pode passar sem conferir quando não acha os campos. **Muda: Testador.**
- **D-06 (CA-16, R-26):** os 4 passos são uma lista numerada (`<ol>`) com 4 itens; o teste conta os 4 itens sob `Como instalar a versão Excel (4 passos)` em vez de procurar "1." no texto. **Muda: Testador.**
- **D-07 (CA-93, R-37):** o teste precisa conferir que `Limpar seleção` está **visível** (hoje a conferência sempre passa). **Muda: Testador.**
- **D-08 (CA-96):** formato e arredondamento da mediana, ver o próprio CA-96. **Muda: Construtor** (formato) e **Testador** (arredondamento).

### 0.3 Nomes na tela — etapa 2 (v1.2)

Valem as mesmas regras da 0.1 (rótulos exatos; testes localizam por rótulo/texto, nunca por id ou classe). Números em pt-BR: milhar com ponto, decimal com vírgula; valores monetários/numéricos com 2 casas.

| Nº | Rótulo exato | Tipo | Onde / observação |
|---|---|---|---|
| R-50 | `O que acompanhar` | botão | Painel, no topo, ao lado de `Filtros`; reabre a tela R-51 |
| R-51 | `O que você quer acompanhar?` | título da janela (dialog) | abre **sozinha** depois que um conjunto novo é lido (após a tela R-21, se houver) e quando o conjunto ainda não tem escolha salva. `Cancelar` mantém o painel padrão da etapa 1 (todos os blocos automáticos) e não salva nada |
| R-52 | uma caixa de marcar (checkbox) por indicador, com o nome exato da linha R-53 a R-61 | checkbox | cada linha da janela = a caixa + o texto de exemplo na mesma linha (elemento `li`/`label` que contém os dois) |
| R-53 | `Total de registros` | indicador | exemplo: `1.284 registros` |
| R-54 | `Por <campo>` (campo categoria; ex. `Por Cliente`, `Por Região`) | indicador | exemplo: `<Campo>: <valor líder> lidera com <n>` (top 10 + `Outros` no gráfico) |
| R-55 | `<Campo> (soma, média e mediana)` (campo número; ex. `Valor (soma, média e mediana)`) | indicador | exemplo: `Soma: 48.210,35 · Média: 123,45 · Mediana: 100,00` |
| R-56 | `<Número> por <categoria>` (ex. `Valor por Região`) | indicador | exemplo: `Maior soma: <valor da categoria líder> (<soma>)` |
| R-57 | `Evolução por mês (<campo data>)` (ex. `Evolução por mês (Data)`) | indicador | exemplo: `Mês com mais registros: 10/2026 (212)` |
| R-58 | `Tempo entre duas datas` | indicador (só com 2 campos de data ou data e hora) | exemplo: `Mediana: 1 d 4 h` (mesmo formato do bloco da etapa 1, R-40) |
| R-59 | `% por <campo situação>` (ex. `% por Situação`) | indicador (só com campo do tipo situação) | exemplo: `<valor mais frequente>: 87,4%` |
| R-60 | `Sem valor em <campo>` | indicador (só para campo com ≥ 1 registro vazio) | exemplo: `38 sem valor em Responsável` |
| R-61 | `Mais antigos em aberto` | indicador (data + situação) | exemplo: `Mais antigo: 12/03/2026` |
| R-62 | `Confirmar` / `Cancelar` | botões | da janela R-51 |
| R-63 | `Entender este painel` | botão | Painel, no topo (só com escolha confirmada) |
| R-64 | `Seu painel` | título da janela (dialog) | aparece sozinha ao `Confirmar` e ao clicar R-63; botão `Fechar` |
| R-65 | `Situação` | opção da lista de tipo na tela R-21 (junto de Texto, Categoria, Número, Data, Data e hora, Código) | CA-24 |
| R-66 | `Como ler este relatório` | nome da 2ª planilha do Excel | CA-29 |

**Regras de conta (valem para exemplos e blocos)**
- Categoria sugerida (CA-24): ≤ 30 valores distintos e ≥ 50% de repetição (já existe). Situação **não** é palpite do app: vem como sugestão quando o campo é categoria e o nome contém `situa`, `status` ou `estado` (sem acento, minúsculas); a pessoa troca na tela R-21.
- Indicador só aparece se os campos existem e têm valor em ≥ 1 registro. Todos os exemplos são calculados dos registros do conjunto (sem filtros).
- **Em aberto (R-61):** registro cuja situação, sem acento e em minúsculas, **não** começa com nenhum de: `conclu`, `finaliz`, `encerr`, `fechad`, `entreg`, `cancel`, `resolvid`, `pag`. O campo de data usado é o primeiro campo de data (ou o escolhido em `Campo de data`).
- **Tempo entre duas datas:** mesma conta da etapa 1 (primeiro campo de data → segundo; só pares com fim ≥ início).
- Blocos no painel (CA-22): cada bloco é um cartão com título (heading) igual ao nome R-53 a R-61. Ordem: primeiro os de número (Total, soma/média/mediana, sem valor, % situação, mais antigos em aberto, tempo entre datas), depois os gráficos (por categoria, por categoria com soma, evolução por mês), por fim a lista `Registros`. Dentro de cada grupo vale a ordem em que foram marcados na janela. Escolha salva por conjunto no navegador.
- Os indicadores continuam clicáveis (abrem a janela de registros), como na etapa 1. Sem escolha salva, o painel é o da etapa 1.

**Texto do "Seu painel" (R-64) e da planilha R-66**
- Uma linha por bloco, no formato: `<nome do bloco> — <o que mostra>. Conta: <conta em palavras>. Campos: <campos usados>. Período: <de dd/mm/aaaa a dd/mm/aaaa>. Filtros: <sem filtros | só região Sul; outubro/2026>.`
- Conta em palavras, exemplos exatos: `contagem de todos os registros`; `contagem de registros por Cliente`; `soma do campo Valor, separada por Região`; `soma, média e mediana do campo Valor`; `registros por mês do campo Data`; `mediana do tempo entre Abertura e Conclusão`; `percentual de registros por Situação`; `registros com o campo Responsável vazio`; `registros em aberto mais antigos pela data Abertura`.
- Período = menor e maior data do campo de data dos registros considerados. Filtro com campo categoria: `só <campo em minúsculas> <valor>` (ex. `só região Sul`); mês: `<mês por extenso em minúsculas>/<aaaa>` (ex. `outubro/2026`); De–até: `de dd/mm/aaaa a dd/mm/aaaa`; busca: `busca “texto”`; unidos por `; `.
- Excel: 2ª planilha `Como ler este relatório`, logo depois da capa; célula A1 `Seu painel`; da A2 em diante uma linha por bloco, com o mesmo texto da tela. Sem escolha confirmada a planilha não é criada.
- **CA-28** (pedido escrito e Editar layout) fica **adiado** para as etapas 3 e 6: na etapa 2 o teste existe marcado `skip` e o resumo já é gerado a partir da lista de blocos, para entrar de graça depois.
- **D-09:** a janela R-51 abre sozinha; os testes da etapa 1 que carregam arquivo passam a fechá-la com `Cancelar` (painel padrão, comportamento da etapa 1 inalterado). **Muda: Testador** (ajuste do auxiliar `carregar`).

---

## 1. Etapa 1 — Nome, cliente na Config, app instalável e offline

**O que quero**
- Título e cabeçalho "Raio X do Relatório". Config → "Empresa / cliente": nome do cliente, área, logo (imagem reduzida e guardada no aparelho). Esses dados aparecem no cabeçalho, na capa do Excel e na impressão.
- Manifesto e service worker: instalável ("Adicionar à tela inicial" / "Instalar"); depois da 1ª abertura funciona sem internet; versão nova é baixada na próxima vez com internet e ativada ao reabrir, com aviso "Versão nova instalada".
- **Versão Excel para baixar:** botão "Baixar versão Excel para o PC" na Config e no rodapé, que baixa `excel/RaioX_Relatorio.bas` com as instruções de instalação (passo a passo curto na própria tela). Sem nome de hospital no arquivo nem na macro.
- Nomes de arquivo gerados: `RaioX_<relatório>_<data>.xlsx`; backup `historico_RaioX_<data>.json`.

**O que NÃO quero**
- Perder a configuração ou o histórico de quem já usa o link (migração automática do que está salvo).

**Critérios**
- CA-10: abrir com o armazenamento vazio → título "Raio X do Relatório" (R-01), sem nome de cliente no cabeçalho.
- CA-11: na aba `Config` (R-04), preencher `Cliente` "Empresa Teste" (R-09), `Área` "Operações" (R-10) e um logo PNG por `Escolher logo` (R-11), sem botão Salvar (R-13) → aparecem no cabeçalho; ao recarregar continuam; carregar um CSV (R-02) e clicar em `Gerar Excel` (R-18) → a capa do Excel gerado mostra "Operações · Empresa Teste" e o logo.
- CA-12: clicar em `Apagar logo` (R-12) → some do cabeçalho e da capa.
- CA-13: o manifesto é válido (nome, ícones 192 e 512, `display: standalone`) e o service worker fica ativo após o 1º carregamento.
- CA-14: com configuração antiga salva (formato atual do `localStorage`), o app abre, mantém nomes genéricos, de-para e limites, e o histórico do IndexedDB continua com a mesma contagem de registros.
- CA-15: publicar versão nova → aparelho com a antiga, ao voltar a ter internet e reabrir, mostra "Versão nova instalada" (R-27) e roda a nova.
- CA-16: clicar em "Baixar versão Excel para o PC" (R-25, online ou offline) → baixa `RaioX_Relatorio.bas`; a tela mostra os 4 passos de instalação (R-26: lista numerada com 4 itens); `grep -i` por "HEV" e "Edmundo" no `.bas` = 0.

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

- **Resumo em texto do que foi criado (Galindo, 25/11/2026 14h45):** ao confirmar a escolha, o app mostra **"Seu painel"**, um texto simples que explica cada bloco criado: o nome, o que ele mostra, a conta em palavras (ex.: "soma do campo Valor, separada por Cliente"), os campos usados, o período e os filtros. O resumo fica disponível pelo botão **"Entender este painel"** e é atualizado sempre que um bloco entra, sai ou muda (pedido escrito, contas personalizadas, Editar layout).
- O mesmo texto vai no Excel, numa planilha **"Como ler este relatório"** logo depois da capa.

**O que NÃO quero**
- Indicador que não dá para calcular aparecer (ex.: tempo entre datas sem 2 datas).
- Exemplo inventado: todo exemplo é calculado dos dados carregados.

**Critérios**
- CA-20: arquivo `tests/dados/vendas.csv` (código, data, cliente, região, valor, situação) → tela lista Total, Por cliente, Por região, Valor (soma/média), Valor por região, Evolução por mês, % por situação; **não** lista "Tempo entre duas datas".
- CA-21: o número de exemplo de cada indicador é igual ao calculado pelo oráculo do teste (script Python sobre o mesmo CSV).
- CA-22: marcar 3 indicadores e confirmar → painel com 3 blocos na ordem número → gráfico → tabela de registros no fim.
- CA-23: recarregar → mesmos 3 blocos; reabrir "O que acompanhar" → os 3 continuam marcados.
- CA-24: campo com ≤ 30 valores distintos e ≥ 50% de repetição é sugerido como categoria; a pessoa pode trocar o tipo do campo na tela de colunas.
- CA-25: `tests/dados/chamados.csv` (código, abertura, conclusão, categoria, responsável, situação) → lista também "Tempo entre duas datas" e "Mais antigos em aberto", com valores iguais ao oráculo.
- CA-26: marcar "Total", "Por cliente" e "Valor por região" e confirmar → aparece "Seu painel" com 3 itens; o item de "Valor por região" diz "soma do campo Valor, separada por Região", o período dos dados e "sem filtros".
- CA-27: aplicar filtro região = Sul e período outubro → "Entender este painel" passa a dizer "só região Sul" e "outubro/2026" em cada item afetado.
- CA-28: adicionar um bloco pelo pedido escrito, tirar outro no Editar layout → o resumo mostra o novo e não mostra mais o retirado.
- CA-29: Excel gerado → 2ª planilha "Como ler este relatório" com o mesmo texto da tela.

### 0.4 Nomes na tela — etapa 3 (v1.3, 25/11/2026)

Mesmas regras da 0.1 (rótulos exatos; testes localizam por rótulo/texto, nunca por id ou classe).

| Nº | Rótulo exato | Tipo | Onde / observação |
|---|---|---|---|
| R-70 | `Peça um indicador` | campo de texto (rótulo) + botão `Pedir` | Painel, no topo, ao lado de `O que acompanhar`; só aparece com conjunto carregado. Enter também envia |
| R-71 | `Entendi assim:` | texto que abre o resumo | janela/cartão de confirmação. Seguido do resumo em linguagem simples, formato `<Medida> · por <agrupar> · <filtros> · <período>`, partes ausentes omitidas. Ex.: `Quantidade de registros · por Cliente · outubro/2026` |
| R-72 | `É isso?` | pergunta, com botões `Sim` e `Não` | abaixo do resumo e da prévia |
| R-73 | `Prévia` | título da prévia | mostra o bloco (número ou gráfico) calculado; para número, o valor aparece em elemento com `data-testid="previa-valor"` (única exceção ao "só por rótulo", para o oráculo comparar o valor) |
| R-74 | `Medida`, `Campo`, `Agrupar por`, `Filtro`, `Período` | botões de correção, 1 por parte, só depois de `Não` | cada um abre lista de escolha com as opções reais dos dados (rótulo da lista = nome do botão); `Aplicar` confirma e atualiza o resumo e a prévia |
| R-75 | `não entendi: <trecho>` | texto (minúsculas, trecho exato da frase) | uma linha por parte não entendida; nunca preenche com chute |
| R-76 | `Tente um destes:` + 3 botões com frases-exemplo montadas com os campos reais | texto e botões | só quando nada da frase foi entendido (CA-35); clicar num exemplo o preenche e envia |
| R-77 | `Sinônimos` | título do cartão | Config |
| R-78 | `Apelido` e `Significa` com botão `Adicionar sinônimo`; `Remover` por linha | campos e botões | Config → Sinônimos. `Significa` é lista com medidas e campos do conjunto atual (ex.: `soma`, `Valor`). Salvo em `localStorage` `raiox_sin` e incluído no backup (chave `sin`) |
| R-79 | `Meus indicadores` | título da seção do Painel | blocos criados por pedido (depois de `Sim`); entram no `Seu painel` (R-64) e na planilha R-66, com a conta em palavras |

**Estrutura (oráculo da bateria).** O app expõe `window.__entender(frase, nomeConjunto)` que devolve (sem tocar na tela) um objeto JSON:
`{medida, campo, agrupar, filtros:[{campo, valor}], periodo, naoEntendi:[trechos]}`, onde
- `medida`: `quantidade` | `soma` | `media` | `mediana` | `minimo` | `maximo` | `percentual` | `null`;
- `campo`, `agrupar`: nome exato do campo no conjunto (ou `"mês"` para agrupar por mês) ou `null`;
- `filtros`: lista com nome do campo e valor exatos como estão nos dados (ex. `{campo:"Situação", valor:"Entregue"}`);
- `periodo`: `null` | `{tipo:"mes", mes:10, ano:2026}` | `{tipo:"ano", ano:2026}` | `{tipo:"intervalo", de:"2026-09-01", ate:"2026-09-15"}`; "este mês/ano", "mês passado" e "últimos N dias" usam como "hoje" a **maior data dos registros** (nunca o relógio), e "outubro" sem ano usa o ano mais recente dos dados com esse mês;
- `percentual` carrega `filtros` com a situação cuja fatia se quer (CA-33: `[{campo:"Situação",valor:"Cancelado"}]`) e `agrupar:"mês"`;
- `naoEntendi`: lista vazia quando tudo foi entendido.
Sinônimos são lidos de `localStorage` `raiox_sin` (`{apelido: "soma"|"Valor"|...}`) pela mesma função. A sugestão `Tente um destes` e a prévia usam o mesmo motor. Semelhança ≥ 80% (razão de caracteres iguais, sem acento/minúsculas/plural).
Bateria: `tests/pedidos.json` = lista de `{frase, conjunto, esperado}` (≥ 40 frases, ≥ 8 por variação: medida, agrupar, filtro, período, erro de digitação, não entendida); meta 100%.
**CA-28** (pedido escrito) passa a valer nesta etapa: o `Seu painel` gerado inclui as linhas de `Meus indicadores`.

**Decisões (v1.3.1, dúvidas do Testador):** D-10 CA-31 usa a situação existente nos dados (`entregues` → `Entregue`; no `vendas.csv` não existe "concluído"). D-11 o nome do conjunto em `__entender` é o nome do arquivo sem extensão (`vendas`). D-12 "últimos N dias" = os N dias que terminam na maior data dos registros, inclusive (fora da bateria). D-13 CA-28 na etapa 3 tira o bloco desmarcando em `O que acompanhar`; "Editar layout" fica para a etapa 6. D-14 em `naoEntendi` o trecho é só a palavra/expressão sem a preposição (`por`, `de`, `em`), ex. `zzzzz`.

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

### 0.5 Nomes e estrutura — etapa 4 (v1.4, 26/11/2026)

Mesmas regras da 0.1. No Excel, os testes localizam por **texto de célula** (openpyxl), nunca por posição fixa além das indicadas aqui (A1, A2 da planilha de painel; rótulos da capa na coluna A).

**Abas do painel.** Até a etapa 6 o painel **não tem abas na tela**: tem uma única **aba implícita** chamada `Painel`. A geração do Excel já recebe, por conjunto, a **lista de abas** `[{nome, blocos}]` (na etapa 4: `[{nome: "Painel", blocos: <blocos do painel na ordem da tela>}]`), gera **uma planilha por aba** e ignora abas escondidas; a etapa 6 só passa a lista nova (CA-40 e CA-44 entram de graça). O app expõe `window.__abasPainel(nomeConjunto)` que devolve essa lista com os **nomes** dos blocos: `[{nome:"Painel", blocos:["Total de registros", ...]}]` (oráculo do CA-50; nome do conjunto como na D-11).

| Nº | Rótulo / conteúdo exato | Onde | Observação |
|---|---|---|---|
| R-80 | `Painel` | nome da planilha de painel | Com **1 conjunto** no arquivo: `<nome da aba>` = `Painel`. Com **≥ 2 conjuntos** no mesmo arquivo: `<nome da aba> - <conjunto>` (ex. `Painel - vendas`). O nome passa pela regra atual de nome de planilha (`nomeAba`): `[ ] : * ? / \` viram espaço, corta em 28 caracteres, repetido ganha ` 2`, ` 3`… |
| R-81 | A1 = nome da aba (`Painel`); A2 = `Relatório: <conjunto>` | planilha de painel | A3 vazia; o 1º bloco começa na linha 4 |
| R-82 | título do bloco = nome exato R-53 a R-61 (ou o nome do bloco de pedido, igual ao heading da tela) | coluna A, em negrito | uma linha vazia depois de cada bloco |
| R-83 | `Categoria`, `Valor`, `Barra` | cabeçalho (colunas A, B, C) da tabela de cada gráfico | linha logo abaixo do título |
| R-84 | `Meus indicadores` | coluna A, linha logo antes do 1º bloco de pedido | só existe se houver bloco de pedido (R-79) |
| R-85 | `Registros` | coluna A, última seção da planilha de painel | linha seguinte = cabeçalho com os nomes dos campos |
| R-86 | rótulos de cartão (ver tabela abaixo) | linha logo abaixo do título, colunas A, B, C… | valores na linha seguinte, mesma coluna |
| R-87 | `Período` → `Registros de dd/mm/aaaa a dd/mm/aaaa` | Capa: rótulo na coluna A, texto na coluna B | sem datas: `sem datas` |
| R-88 | `Filtros` → mesmo texto de filtros do `Seu painel` (`sem filtros` ou `só região Sul; outubro/2026`) | Capa, A/B | substitui o antigo `nenhum` |
| R-89 | `Gerado em` → `dd/mm/aaaa hh:mm` (texto, hora local) | Capa, A/B | os rótulos `Relatório`, `Período`, `Filtros`, `Gerado em` continuam na coluna A, um por linha; logo continua na capa (CA-11/CA-12) |

**Ordem das planilhas** (todos os formatos): `Capa` → `Como ler este relatório` (só com escolha confirmada, regra da etapa 2) → planilhas de painel (uma por aba de cada conjunto, na ordem dos conjuntos) → planilhas de registros do formato escolhido, como hoje (`<conjunto>` por relatório, ou `Tudo`). As planilhas de registros continuam iguais (regressão CA-98).
- `Uma planilha por relatório` e `Tudo numa planilha`: um arquivo, uma planilha de painel por conjunto com registros.
- `Arquivos separados`: um arquivo por conjunto, cada um com `Capa`, `Como ler este relatório` (se houver), `Painel` (sempre sem sufixo) e a planilha de registros.

**Layout de cada bloco na planilha de painel** (mesma ordem da tela: blocos escolhidos — números, depois gráficos —, depois `Meus indicadores`, depois `Registros`):
- **Cartão de números:** linha 1 = título (R-82); linha 2 = rótulos; linha 3 = valores.
- **Gráfico:** linha 1 = título; linha 2 = `Categoria` | `Valor` | `Barra`; uma linha por barra da tela, na mesma ordem e com o mesmo nome (top 10 + `Outros` onde a tela mostra; meses como `10/2026`). **Não há gráfico nativo do Excel**: a coluna `Barra` é texto com `█` repetido `round(20 × |n| / maior |n| do bloco)` vezes (mínimo 1 quando n ≠ 0; célula vazia quando n = 0), onde n é o número por trás da barra (contagem ou soma).
- **Tempo entre datas:** cartão (rótulos `De`, `Até`, `Mediana`, `Dentro de <prazo> h`; valores: campo inicial, campo final, duração, percentual) e, logo abaixo, a tabela de faixas (`Categoria` = nome da faixa, `Valor` = contagem).
- **Bloco de pedido sem resultado:** linha 2 = o mesmo aviso da tela (ex. `Nenhum registro para este pedido.`).
- **Registros:** linha `Registros`; cabeçalho com os campos do conjunto (mesma ordem e mesmos tipos de célula da planilha de registros atual); uma linha por registro **depois de filtros e período** (todos, não só os 100 da tela), na mesma ordem da tabela da tela (mais novo primeiro pelo campo de data; sem data, por código).

**Rótulos de cartão (R-86)**

| Bloco | Rótulos (linha 2) | Valores (linha 3) |
|---|---|---|
| `Total de registros` (R-53) | `Registros` | contagem |
| `<Campo> (soma, média e mediana)` (R-55) | `Soma`, `Média`, `Mediana` | decimais |
| `Sem valor em <campo>` (R-60) | `Registros` | contagem |
| `Mais antigos em aberto` (R-61) | `Mais antigo`, `Em aberto` | data como texto `dd/mm/aaaa` (como na tela), contagem |
| `Tempo entre duas datas` (R-58) | `De`, `Até`, `Mediana`, `Dentro de <prazo> h` | texto, texto, duração, percentual |
| Pedido sem `Agrupar por` (R-79) | `Valor`, `Registros considerados` | conforme a medida, contagem |
| `Números` (painel padrão, CA-46) | os mesmos textos da faixa da tela: `Total de registros`, `Mais antigo`, `Mais novo` (com o complemento `(<campo de data>)` quando a tela mostra) | contagem, texto, texto |

Gráficos: `Por <campo>` (R-54), `<Número> por <categoria>` (R-56), `Evolução por mês (<campo>)` (R-57), `% por <campo>` (R-59) e pedido com `Agrupar por`. No `% por <campo>`, `Valor` é o percentual da barra (texto) e a `Barra` usa a contagem.

**Tipo e formato de cada célula** (o que o oráculo do CA-41 compara)
- **Contagem** (registros, quantidade, contagem de barra): **número inteiro**, `number_format` `#,##0` (o Excel em português mostra `1.284`).
- **Soma, média, mediana, mínimo, máximo** (inclusive `Valor` de R-56 e de pedidos com essas medidas): **número arredondado a 2 casas**, `number_format` `#,##0.00` (mostra `48.210,35`). Igual ao número da tela convertido de pt-BR.
- **Percentual:** **texto**, igual à tela (`87,4%`, 1 casa).
- **Duração:** **texto**, igual à tela (`48 min`, `26 h 00 min`; mesma função da tela).
- **Data em cartão:** texto `dd/mm/aaaa` como na tela. **Sem valor:** texto `—` (onde a tela mostra `—`).
- **Nenhuma fórmula e nenhuma macro:** nenhuma célula com `data_type == 'f'` em nenhuma planilha; o `.xlsx` não contém `xl/vbaProject.bin`.

**Período da capa (R-87):** cada ponta vem do filtro quando ele a define (`Mês` → 1º e último dia do mês; `De–até` → as datas informadas) e, quando não define (`Tudo` ou ponta em branco), da menor/maior data do campo de data dos registros filtrados.

**Painel padrão (sem escolha confirmada):** a planilha de painel traz os blocos da etapa 1, como na tela: `Números`; `Por <categoria>` para até 3 categorias (8 maiores, sem `Outros`); `Por mês (<campo de data>)` (últimos 12 meses); `Tempo entre datas` (só com ≥ 2 campos de data); depois `Meus indicadores` (se houver) e `Registros`. `Possíveis repetidos` **não** vai ao Excel (é um botão de busca).

**Macro (9b):** a planilha de painel na versão Excel é tarefa à parte (cabe no Excel 2016: só valores e texto); não entra nos CAs da etapa 4.

---

## 4. Etapa 4 — Excel seguindo o painel

**O que quero**
- "Gerar Excel" produz um arquivo com: **capa** (cliente, área, título, período, filtros, data de geração, logo), e **uma planilha por aba do painel**, com os blocos na mesma ordem: números como cartões, gráficos como tabela de valores com barra em texto, tabela de registros no fim. Nomes, layout e formatos exatos na seção 0.5 (R-80 a R-89).
- Na etapa 4 o painel tem uma só aba implícita (`Painel`); a geração já trabalha com a lista de abas para a etapa 6.
- Mantém as opções atuais: período (tudo / mês / de–até), formato (uma planilha por relatório / tudo numa / arquivos separados), durações em "h min", percentuais formatados. As planilhas de registros de cada formato continuam como hoje, depois das planilhas de painel.

**O que NÃO quero**
- Fórmula ou macro no arquivo gerado (só valores, como hoje).
- Gráfico nativo do Excel (a barra é texto `█`, seção 0.5).
- Valor no Excel diferente do que a tela mostra para os mesmos filtros.
- Bloco que não está na tela (ex.: `Possíveis repetidos`) ou bloco da tela que falta no Excel.

**Critérios** (dados de `tests/dados/`; leitura do `.xlsx` com openpyxl; `Formato` = `Uma planilha por relatório` quando não dito)
- CA-40 (**adiado para a etapa 6**, teste existe marcado `skip`): painel com 2 abas (3 e 2 blocos) → Excel com capa + 2 planilhas de painel; nomes das planilhas = nomes das abas; ordem dos blocos igual.
- CA-41: `vendas.csv`; em `O que acompanhar` marcar `Total de registros`, `Valor (soma, média e mediana)`, `Por Cliente`, `Valor por Região` e `% por Situação`, `Confirmar`; `Gerar Excel` → existe a planilha `Painel` (3ª, depois de `Capa` e `Como ler este relatório`); A1 = `Painel`, A2 = `Relatório: vendas`; os títulos de bloco na coluna A aparecem na mesma ordem dos headings dos cartões da tela; para cada bloco, cada valor do cartão (linha abaixo do rótulo R-86) e cada linha `Categoria`/`Valor` da tabela é igual ao texto da tela (números convertidos de pt-BR; contagens inteiras com `#,##0`; decimais com 2 casas e `#,##0.00`; percentuais texto igual, ex. `87,4%`); a coluna `Barra` tem a quantidade de `█` da regra da 0.5.
- CA-42: em `Filtros`, `Período` = `De–até` de 01/10/2026 a 31/10/2026; `Gerar Excel` → na `Capa`, a célula à direita de `Período` é `Registros de 01/10/2026 a 31/10/2026`, a de `Filtros` é `de 01/10/2026 a 31/10/2026`, a de `Gerado em` casa com `^\d{2}/\d{2}/\d{4} \d{2}:\d{2}$`; na planilha `Painel`, o valor de `Total de registros` e a quantidade de linhas da seção `Registros` = quantidade de registros com data em outubro/2026 (oráculo Python).
- CA-43: CSV de teste com 2 campos de data cuja mediana do tempo é 0,8 h → no bloco `Tempo entre duas datas` da planilha `Painel`, a célula abaixo de `Mediana` é o texto `48 min`; outro CSV com mediana de 26 h → `26 h 00 min`; as duas células são texto (não número).
- CA-44 (**adiado para a etapa 6**, teste existe marcado `skip`): aba escondida no painel não sai no Excel.
- CA-45: carregar `vendas.csv` e `chamados.csv`, escolher blocos nos dois; `Formato` = `Tudo numa planilha` → um arquivo com `Capa`, `Como ler este relatório`, `Painel - vendas`, `Painel - chamados` e `Tudo`, nessa ordem; cada planilha de painel tem A2 = `Relatório: <conjunto>` e só os blocos do seu conjunto. `Formato` = `Arquivos separados` → 2 arquivos, cada um com uma planilha `Painel` (sem sufixo) com os blocos do seu conjunto.
- CA-46: `vendas.csv` sem escolha confirmada (fechar `O que acompanhar` com `Cancelar`) → não há `Como ler este relatório`; a planilha `Painel` é a 2ª e traz, na coluna A e nesta ordem, `Números`, os `Por <categoria>` que a tela mostra, `Por mês (<campo de data>)` e `Registros`; não há `Possíveis repetidos`; os valores batem com a tela como no CA-41.
- CA-47: em todos os arquivos gerados pelos CAs desta seção, nenhuma célula de nenhuma planilha tem `data_type == 'f'` e o zip do `.xlsx` não contém `xl/vbaProject.bin`.
- CA-48: `vendas.csv` com escolha confirmada; pedir `soma do valor por cliente` e responder `Sim` → na planilha `Painel` a linha `Meus indicadores` vem depois do último bloco escolhido e antes de `Registros`; logo abaixo, o título do bloco igual ao heading da tela, com tabela `Categoria`/`Valor` igual à tela.
- CA-49: filtro `Região` = `Sul` → a seção `Registros` da planilha `Painel` tem cabeçalho = nomes dos campos do conjunto, uma linha por registro da região Sul (contagem = oráculo) e as 5 primeiras linhas têm o mesmo código das 5 primeiras da tabela da tela.
- CA-50: depois do CA-41, `window.__abasPainel("vendas")` devolve `[{nome:"Painel", blocos:[...]}]` com `blocos` = os títulos de bloco da planilha `Painel`, na mesma ordem (sem `Meus indicadores` e sem `Registros`, que são âncoras de seção).

---

### 0.6 Nomes e regras — etapa 5 (v1.5, 26/11/2026, F-55)

Mesmas regras da 0.1 (rótulos exatos; testes localizam por rótulo/texto). Contas são **por conjunto** (cada relatório tem as suas).

| Nº | Rótulo exato | Tipo | Onde / observação |
|---|---|---|---|
| R-90 | `Contas personalizadas` | título do cartão | Config; vale para o relatório aberto no Painel |
| R-91 | `Nome da conta`, `Fórmula`, botão `Salvar conta` | campos e botão | `Nome da conta` até 60 caracteres, `Fórmula` até 300. Nome repetido (sem diferenciar maiúsculas/acentos) substitui a conta antiga |
| R-92 | `Prévia da conta` | título; valor em elemento com `data-testid="conta-previa"` | atualiza ao digitar (ou ao sair do campo), com os dados do relatório aberto. Número formatado como o resto do app (`1.234,56`); sem resultado = texto `sem dados` |
| R-93 | mensagem de erro, `role="alert"`, junto da fórmula | texto | nunca salva quando há erro. Textos exatos abaixo |
| R-94 | lista `Suas contas` com `<nome> = <fórmula>` e botão `Remover` por linha | lista | |
| R-95 | a conta salva aparece em `O que acompanhar` (R-50) com o próprio nome, exemplo calculado e sem campo específico; o bloco é um cartão com o número (clicável, abre todos os registros) | catálogo | entra no `Seu painel` e na planilha `Painel` (etapa 4) como bloco de número, com a fórmula em "Conta:" |

**Fórmula.** Números (`.` decimal), `+ - * /`, `-` unário, parênteses e as funções abaixo, todas sobre os registros do conjunto (após os filtros do painel, como os outros blocos). Nomes de campo e valores comparados sem acento e sem diferenciar maiúsculas; campo com espaço vai entre aspas (`"Data do pedido"`). Filtro opcional: `campo = valor` (valor sem aspas ou entre aspas).
- `quantidade()` / `quantidade(filtro)`: registros (que passam no filtro).
- `soma(campo)` / `soma(campo, filtro)`; `media(...)`; `mediana(...)`: sobre os valores numéricos do campo (vazios fora).
- `dias(data1, data2)`: **média**, em dias (com casas decimais), de `data2 − data1` nos registros que têm as duas datas.
- `distintos(campo)`: quantidade de valores diferentes e não vazios.
- Tudo é lido por um interpretador próprio (nunca `eval`, nunca `Function`); qualquer nome fora da lista é erro.

**Textos de erro (exatos, sem diferenciar maiúsculas na sugestão, que sai em minúsculas):**
- campo inexistente: `campo 'valr' não existe; você quis dizer 'valor'?` (sem sugestão quando nada parece: `campo 'xyz' não existe`)
- função desconhecida (inclui `alert(1)`): `função 'alert' não existe`; nome solto que não é campo nem função (ex. `constructor`): `não entendi 'constructor' na fórmula`
- parêntese aberto: `falta fechar o parêntese`; sobrando: `parêntese fechado sem abrir`
- divisão por zero ou resultado indefinido: não é erro de fórmula; o resultado é `sem dados` (nunca `NaN`, `Infinity` ou exceção)
- fórmula vazia: `escreva a fórmula`; nome vazio: `escreva o nome da conta`

**Pedido escrito (CA-54).** `<nome da conta> por <campo>` e `<nome da conta>` sozinho: `window.__entender` devolve `medida: "conta"`, `campo: <nome exato da conta>`, `agrupar` como nas outras medidas. A conta é calculada em cada grupo (a fórmula inteira sobre os registros do grupo); resumo `Entendi assim: Ticket médio · por Região`. O nome da conta vale como o de um campo: semelhança ≥ 80% como nas demais palavras. Contas entram em backup/restauração (chave `contas`, `localStorage` `raiox_contas`; somar junta sem repetir nome, até 50 por conjunto).

**Decisões (v1.5):** D-20 `dias` = média (a especificação não dizia qual estatística). D-21 divisão por zero = `sem dados` em vez de erro de fórmula (CA-53 pede "sem dados"). D-22 a sugestão do campo sai em minúsculas como no CA-52. D-23 contas valem por conjunto, não globais.

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

### 0.7 Nomes e regras — etapa 6 (v1.6, 26/11/2026, F-57)

Mesmas regras da 0.1 (rótulos exatos; testes localizam por rótulo/texto/`aria-label`). **Regra de ouro: sem layout editado, a tela e o Excel ficam idênticos aos das etapas 2 a 5** (nenhum teste antigo muda). O layout vale **por conjunto**.

| Nº | Rótulo exato | Tipo | Onde / observação |
|---|---|---|---|
| R-100 | `Editar layout` / `Concluir edição` | botão (o mesmo botão troca de texto) | Painel, junto de `O que acompanhar`; só aparece quando há blocos escolhidos (etapa 2). Liga/desliga o modo edição |
| R-101 | barra de abas `<nav aria-label="Abas do painel">` com um botão por aba (texto = nome da aba, `data-testid="aba"`) | navegação | A aba inicial chama `Painel`. **A barra só aparece com 2 ou mais abas ou em modo edição** |
| R-102 | `Nova aba`, `Renomear aba`, `Apagar aba`, `Aba à esquerda`, `Aba à direita` | botões | só em modo edição; agem sobre a aba aberta. `Nova aba` e `Renomear aba` pedem o nome numa janela (campo `Nome da aba`, botões `Salvar` e `Cancelar`), até 30 caracteres, sem repetir (sem diferenciar maiúsculas/acentos); nome inválido: `role="alert"` com `escreva o nome da aba` ou `já existe uma aba com esse nome` |
| R-103 | por bloco, em modo edição, um grupo `role="group"` com `aria-label` = `Controles de <título do bloco>` e dentro: botões `Subir`, `Descer`, `Esconder` (vira `Mostrar` no bloco escondido), `Duplicar`; selects `Mover para…`, `Tamanho`, `Forma` | controles | `Subir`/`Descer` valem em qualquer largura (no celular são os únicos meios; no computador o arrastar também funciona). `Subir` no 1º bloco e `Descer` no último não fazem nada (botão desabilitado) |
| R-104 | `Tamanho`: opções `Pequeno`, `Médio`, `Grande` | select | padrão `Médio`. Na tela o bloco ocupa 1/3, 1/2 ou toda a largura (em 390 px sempre a largura toda). No Excel o tamanho não muda nada |
| R-105 | `Forma`: opções `Número`, `Barras`, `Linha`, `Pizza`, `Tabela` | select | **só as formas que o dado permite**: bloco de um número só (cartão): apenas `Número`; bloco agrupado por categoria: `Barras`, `Pizza`, `Tabela`; agrupado por mês: também `Linha`. A forma de origem é a do padrão. Pizza com mais de 8 fatias vira `Barras` e mostra o aviso `Pizza com mais de 8 fatias: mostrando barras` |
| R-106 | `Voltar ao padrão` | botão | em modo edição; pede confirmação (`Voltar ao padrão?`, botões `Voltar ao padrão` e `Cancelar`); apaga o layout do conjunto: ordem, abas, tamanhos, escondidos, duplicados e formas voltam ao da etapa 2 |
| R-107 | confirmação ao apagar aba: `Apagar a aba <nome>?` com botões `Apagar` e `Cancelar`; texto `Os N blocos dela vão para a primeira aba.` (só se N > 0) | janela | sempre pergunta; não se apaga a última aba (o botão `Apagar aba` fica desabilitado quando há 1 aba) |
| R-108 | bloco escondido: em modo edição aparece esmaecido (`data-escondido="true"`) com o botão `Mostrar`; fora do modo edição **não aparece** nem no Excel nem em `Seu painel` | | |

**Modelo.** `layout[conjunto] = { abas: [{ id, nome }], itens: [{ k, id, aba, tam, oculto, forma }] }`, onde `id` é o do indicador (etapa 2/5) e `k` é a chave única do item (permite o mesmo indicador duas vezes, por `Duplicar`). Ausente = padrão. Salvo no navegador por conjunto e no **backup** (campo `layout`, validado como as contas: formato errado rejeita o arquivo inteiro; até 20 abas e 200 itens por conjunto; indicador que não existe mais é ignorado). Restaurar com `Substituir` troca; com `Somar` o layout do backup só entra para conjuntos que ainda não têm layout.

**Regras.** (1) A ordem dos blocos é a da lista `itens`; a tela mostra os blocos da aba aberta, na ordem. (2) `Duplicar` cria uma cópia logo depois do original, **na mesma aba** (para outra aba: duplicar e depois `Mover para…`), com mesmo valor. (3) Apagar aba: os itens dela vão, na ordem, para o fim da 1ª aba. (4) Indicador desmarcado em `O que acompanhar` sai do layout (todas as cópias); indicador novo entra no fim da 1ª aba. (5) `Seu painel` e a planilha de cada aba do Excel seguem a ordem do layout; blocos escondidos ficam de fora. (6) **Excel (etapa 4):** uma planilha por aba do layout, na ordem das abas, com o nome da aba (1ª = `Painel`); aba sem blocos visíveis não gera planilha; a macro Excel não ganha layout (fora do escopo, seção 12). (7) O modo edição não se guarda: ao recarregar, volta desligado. (8) Arrastar: o bloco (`draggable`) solto sobre outro bloco da mesma aba ocupa o lugar dele; solto sobre o botão de outra aba vai para o fim dela.

**Decisões (v1.6):** D-30 a aba inicial chama `Painel` (o mesmo nome da planilha do Excel da etapa 4). D-31 `Duplicar` cria a cópia na mesma aba. D-32 "Somar" no backup só traz layout de conjunto sem layout. D-33 tamanho não afeta o Excel. D-34 formas permitidas por tipo de bloco (tabela acima), a decisão do que "o tipo de dado permite". D-35 (implementação) a mensagem de apagar aba usa o texto literal, também com 1 bloco. D-36 (implementação) a tabela de registros do Excel só vai na 1ª planilha de painel de cada conjunto.

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
- Relatório "de impressão" (blocos, cabeçalho repetido por página): o app tenta tirar a tabela repetindo o cabeçalho de cada página; se não conseguir, cai na tela "Esta coluna é o quê?".

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

### 0.8 Nomes e regras — etapa 7a: planilhas, JSON, XML e zip (v1.7, 26/11/2026, F-58)

PDF (7b, F-64) e imagem com OCR (7c, F-65) **não** entram aqui. Mesmas regras da 0.1. Tudo local, sem rede, sem servidor. Leitor de planilha: `vendor/xlsx.full.min.js` (SheetJS 0.20.3).

| Nº | Rótulo exato | Tipo | Onde / observação |
|---|---|---|---|
| R-110 | `Carregar relatório` (R-02) passa a aceitar `.csv .txt .tsv .xlsx .xls .ods .json .xml .zip` | botão | mesmo botão, vários arquivos de tipos misturados |
| R-111 | `Esta coluna é o quê?` (tela já existente) | janela | cada tabela nova passa por ela, uma vez por formato de colunas (o formato lembrado vale para qualquer tipo de arquivo: `vendas.csv` e `vendas.xlsx` com as mesmas colunas usam o mesmo formato) |
| R-112 | mensagens (toast), exatas | texto | arquivo de tipo não suportado: `<arquivo>: formato não suportado.`; arquivo sem tabela legível (ou planilha vazia): `Não achei o cabeçalho em <arquivo>.`; arquivo corrompido: `Não consegui ler <arquivo>.`; zip com arquivo de dentro não suportado: `<arquivo>: formato não suportado (ignorado).` (os outros do zip seguem); zip passando dos limites: `<arquivo>: zip grande demais.` |

**Regras.**
1. **Planilha (.xlsx, .xls, .ods):** cada aba com dados vira uma tabela candidata; a primeira linha com cabeçalho é achada como no CSV. Aba vazia é ignorada. Com **uma** aba, o nome sugerido do relatório (em `Esta coluna é o quê?`) é o do arquivo sem extensão; com **mais de uma**, `<arquivo> - <aba>` (cada aba é um conjunto à parte). Só os valores entram (fórmulas valem o resultado guardado; nunca são executadas).
2. **Valores:** número vira texto com vírgula decimal e sem separador de milhar (`2014,78`); inteiro sem casas; data (célula de data) vira `dd/mm/aaaa` e, se tem hora, `dd/mm/aaaa hh:mm`; célula vazia, vazio; verdadeiro/falso viram `Sim`/`Não`; erro de célula (`#DIV/0!` etc.) vira vazio. Com isso `vendas.xlsx` dá **os mesmos resultados** de `vendas.csv` (CA-70).
3. **JSON:** lista de objetos (ou objeto com **uma** propriedade que é essa lista); colunas = união das chaves na ordem em que aparecem (até 200); valor texto/número/booleano como na regra 2 (número JSON com `.` vira vírgula); objeto ou lista dentro de um valor vira o texto JSON dele. Qualquer outra forma = `Não achei o cabeçalho em <arquivo>.`
4. **XML:** acha o elemento que mais se repete (mesmo nome, mesmo pai) cujos filhos são elementos simples; cada repetição é uma linha, colunas = nomes dos filhos (e atributos do elemento, depois) na ordem em que aparecem. Sem repetição = `Não achei o cabeçalho em <arquivo>.`
5. **Zip:** abre e lê cada arquivo de dentro (qualquer pasta, qualquer mistura de tipos desta tabela), na ordem alfabética do caminho; zip dentro de zip não é aberto (`formato não suportado (ignorado)`). Limites: até 50 arquivos úteis e 200 MB no total depois de descompactar (medidos pelo tamanho declarado e conferidos na leitura); acima disso `zip grande demais` e nada do zip entra.
6. **Limites:** cada arquivo (ou arquivo dentro do zip) até 50 MB (o limite do CSV); planilha até 200 colunas e 200 mil linhas por aba (o excedente é cortado em silêncio); nome de coluna/aba só entra na tela por `textContent`.
7. **Nada executa:** sem `eval`, sem macros (um `.xlsm`/`.xlsb` não é aceito), sem links externos, sem rede. Chave de coluna chamada `__proto__`/`constructor` é coluna comum.
8. O mesmo registro vindo de dois arquivos se junta pelo código como já faz (CA-80, CA-81).

**Critérios (v1.7).** CA-70 `vendas.xlsx`, CA-71 `vendas.xls` e `vendas.ods`, CA-72 `vendas.json` e `vendas.xml`: os mesmos resultados de `vendas.csv` (total, por cliente, valor total) conferidos pelo backup e pelo painel. CA-75a `vendas_mistura.zip` (CSV + XLSX + JSON dentro de uma pasta): os três lidos (mesmos códigos: 500 vendas + 300 chamados; o XLSX e o JSON repetem as vendas do CSV de vendas sem duplicar, pois juntam por código). CA-70b `vendas_2abas.xlsx`: dois conjuntos (`vendas_2abas - Vendas` e `vendas_2abas - Chamados`) com 500 e 300 registros. CA-110x: arquivos forjados (zip com 60 arquivos; JSON de lista aninhada; XML sem repetição; `.xlsx` truncado; nome de coluna `__proto__`) → só mensagens R-112, nada trava e `({}).polluted` continua `undefined`.

**Decisões (v1.7):** D-40 cada aba é um relatório à parte (espec. 7: "cada aba vira um conjunto candidato"). D-41 número sai com vírgula e sem milhar, data como `dd/mm/aaaa`, para o mesmo formato lembrado do CSV servir. D-42 `.xlsm`, `.xlsb` e `.xlsx` com senha não são lidos. D-43 limites de zip (50 arquivos, 200 MB).

### 0.9 Nomes e regras — etapa 7b: PDF com texto e tela de conferência (v1.8, 26/11/2026, F-64)

Foto/PDF escaneado com OCR **não** entram aqui (7c, F-65), mas a **tela de conferência** é feita para servir às duas. Leitor de PDF: `vendor/pdf.min.mjs` + `vendor/pdf.worker.min.mjs` (pdf.js 5.7.284, local, carregado só quando um PDF é escolhido; sem rede). Mesmas regras da 0.1.

| Nº | Rótulo exato | Tipo | Onde / observação |
|---|---|---|---|
| R-120 | `Carregar relatório` (R-02) aceita também `.pdf` | botão | e `.pdf` dentro de `.zip` (regra 6 da 0.8 deixa de ignorar PDF) |
| R-121 | janela `Conferir leitura` (`<dialog>` com `aria-labelledby`, título exato `Conferir leitura`) | janela | abre depois de ler um PDF (e, na 7c, uma imagem), **antes** de qualquer dado entrar; mostra `Arquivo: <nome>.` e `Confira a tabela lida. As células marcadas podem estar erradas.` |
| R-122 | tabela editável: cada célula é um `<input type="text">` com `aria-label` = `Linha <n>, <coluna>` (n começa em 1 na primeira linha **de dados**; a linha de cabeçalho é `Cabeçalho, coluna <j>`, j a partir de 1) | tabela | o usuário corrige o texto; célula de baixa confiança tem `data-baixa="true"` e fundo destacado |
| R-123 | botões `Confirmar` e `Descartar` | botões | `Confirmar` segue para `Esta coluna é o quê?` (formato lembrado se já houver) e importa o que está na tabela (com as correções); `Descartar` fecha e nada entra; `Esc` = `Descartar` |
| R-124 | mensagem (toast) `Não encontrei uma tabela neste arquivo` | texto exato (sem ponto final) | PDF sem texto em colunas (ex.: contrato) ou com menos de 2 colunas ou menos de 2 linhas; nenhuma janela abre, nada entra |
| R-125 | texto `Linhas lidas: <n>` e `Células marcadas: <m>` na janela | texto | contagens da tabela mostrada |

**Regras.**
1. **Texto do PDF:** o leitor pega cada pedaço de texto com sua posição (x, y) por página. Pedaços com o mesmo y (tolerância de metade do corpo da letra) formam uma linha; as colunas vêm dos x onde os pedaços começam: x parecidos (tolerância de 6 pontos) entre muitas linhas formam uma coluna. Pedaços muito próximos na mesma linha (espaço menor que 1,5 vez a largura média de um caractere) pertencem à mesma célula (nome com espaço, "Zeta Ferragens").
2. **Relatório de impressão:** a linha de cabeçalho é a primeira linha de tabela da 1ª página que tem texto em todas as colunas; **linhas iguais ao cabeçalho nas páginas seguintes são descartadas**; linhas com um só pedaço (título "Relatório de vendas", rodapé "Página 3") são descartadas. Se depois disso restarem menos de 2 colunas ou 2 linhas: R-124.
3. **Baixa confiança** (`data-baixa="true"`): célula vazia numa linha que tem as demais preenchidas; célula de linha com número de colunas diferente do cabeçalho; texto de uma coluna que foge do padrão dela (coluna em que ≥ 90% das células são número/data e esta não é). Toda a tabela do PDF com texto correto tem 0 células marcadas (o PDF de teste `vendas.pdf` não pode ter células marcadas).
4. **Várias páginas e vários PDFs do mesmo formato (mesmo cabeçalho)** viram uma só tabela de conferência por PDF; cada PDF abre a sua janela, em sequência.
5. Limites: PDF até 50 MB (limite do CSV) e até 200 páginas e 20 mil linhas; acima disso corta em silêncio. Senha/arquivo corrompido: `Não consegui ler <arquivo>.`. Nada do PDF é executado (o build do leitor não usa `eval` e a CSP não permite `unsafe-eval`; sem scripts do PDF, sem rede); leitura passada de 60 s é abandonada com `Não consegui ler <arquivo>.`; até 200 colunas e 1 milhão de células; conferência de tabela grande mostra as primeiras linhas e o botão `Mostrar mais linhas`.
6. Depois de `Confirmar`, o caminho é o de sempre (`Esta coluna é o quê?`, formato lembrado, junção por código). Valores entram como texto da célula (datas dd/mm/aaaa e números com vírgula, como no CSV).

**Critérios (v1.8).** CA-73 `vendas.pdf` (relatório de impressão de 500 vendas em várias páginas, cabeçalho repetido, título e rodapé em cada página): janela `Conferir leitura` com 500 linhas, **0 células marcadas**, cabeçalho `Código, Data, Cliente, Região, Vendedor, Valor, Situação`; após `Confirmar` (e responder `Esta coluna é o quê?`) os mesmos resultados do CSV (total, por cliente, soma). CA-73b: editar uma célula na conferência (ex.: trocar o cliente de uma linha) e confirmar → o valor corrigido entra. CA-73c: `Descartar` → nada entra (backup sem registros). CA-77 `contrato.pdf` → toast `Não encontrei uma tabela neste arquivo` e nenhuma janela. CA-73d: o mesmo `vendas.pdf` dentro de um `.zip` com um CSV → o CSV entra e o PDF abre a conferência. CA-110y: PDF corrompido (bytes cortados) → `Não consegui ler <arquivo>.`; offline (rede bloqueada) o PDF é lido igual.

**Decisões (v1.8):** D-50 PDF abre sempre a conferência, mesmo sem célula marcada (espec. 7: "tudo que vem por OCR ou PDF passa pela tela de conferência"). D-51 limites de 200 páginas/20 mil linhas. D-52 colunas pela posição do texto (sem aprender de tabelas desenhadas por linhas).

### 0.10 Nomes e regras — etapa 7c: imagem e PDF escaneado com OCR (v1.9, 26/11/2026, F-65)

Reaproveita a tela `Conferir leitura` (0.9) e `Core.tabelaPdf` (colunas pela posição). OCR **no aparelho**, sem rede, sem servidor: `vendor/ocr/` (tesseract.js 7.0.0, núcleo `tesseract-core` 6.1.2 nas versões `lstm` e `simd-lstm`, dados de idioma `por` 4.0.0 best_int). Os arquivos de `vendor/ocr/` **não** entram no cache de instalação do service worker: são guardados no cache **na primeira vez que o OCR é usado** (runtime) e depois valem offline (CA-76). Mesmas regras da 0.1.

| Nº | Rótulo exato | Tipo | Onde / observação |
|---|---|---|---|
| R-130 | `Carregar relatório` (R-02) aceita também `.jpg .jpeg .png` (e `.pdf` escaneado, regra 6) | botão | também dentro de `.zip` |
| R-131 | texto de progresso `Lendo a imagem… <n>%` (e `Lendo a página <p> de <n>…` para PDF escaneado) | texto no toast/janela | só informativo; atualiza durante o OCR; some ao terminar |
| R-132 | janela `Conferir leitura` (0.9) com células de baixa confiança marcadas (`data-baixa="true"`) | janela | **sempre** abre depois do OCR; nada entra sem `Confirmar`. Para imagem, mostra também a imagem reduzida ao lado da tabela, com `alt` = `Imagem lida: <nome>` |
| R-133 | `Várias fotos` : ao escolher 2 ou mais imagens (ou PDFs escaneados) **no mesmo envio** com o mesmo cabeçalho, uma única janela `Conferir leitura` com as linhas de todas na ordem dos arquivos (cabeçalho uma vez) | regra | cabeçalho diferente: uma janela por grupo de cabeçalho igual |
| R-134 | mensagens (toast), exatas | texto | imagem sem tabela: `Não encontrei uma tabela neste arquivo` (sem ponto final); imagem corrompida/vazia: `Não consegui ler <arquivo>.`; OCR indisponível (arquivos do leitor não carregaram, ex.: offline antes do 1º uso): `O leitor de imagens ainda não está disponível neste aparelho. Use uma vez com internet.` |

**Regras.**
1. **Melhoria de imagem** antes do OCR (no aparelho, em canvas): cinza, ajuste de contraste, redução para no máximo 3000 px no maior lado (e ampliação para pelo menos 1600 px se menor), e endireitar (estimar o giro entre −5° e +5° pelo alinhamento das linhas de texto e girar de volta). Foto de 12 megapixels não pode travar a aba (processar em partes ou reduzir antes).
2. **OCR:** português, modo de página em bloco (`psm 6`), palavras com caixa e confiança. As palavras viram itens `{x, y, w, h, t}` e passam por `Core.tabelaPdf` (mesmas regras de linhas, colunas e cabeçalho da 0.9; o cabeçalho repetido é descartado).
3. **Confusões do OCR:** numa coluna em que ≥ 60% das células têm o formato `letra + dígitos` (códigos) ou só dígitos/`,`/`.`/`/`/`:` (números e datas), as letras `O o Q D` viram `0`, `I l |` viram `1`, `S` vira `5`, `B` vira `8` e `Z` vira `2` **só nas células dessa coluna** (e a célula corrigida fica marcada como baixa confiança). Texto de colunas de texto nunca é alterado.
4. **Baixa confiança** (`data-baixa="true"`): célula com palavra de confiança < 75, as regras 3 da 0.9 e as células alteradas pela regra 3 acima.
5. **Várias páginas/fotos do mesmo relatório** (R-133): cabeçalho repetido descartado; a numeração de linhas da conferência segue contínua.
6. **PDF escaneado:** PDF em que a leitura de texto (0.9) não acha tabela e as páginas não têm texto é desenhado página a página em canvas (até 20 páginas) e passa pelo mesmo OCR.
7. **Limites:** imagem até 50 MB; até 20 imagens/páginas por envio (o excedente é ignorado com `<arquivo>: limite de 20 imagens.`); OCR passado de 120 s por imagem é abandonado com `Não consegui ler <arquivo>.`. Nada é enviado à internet; os arquivos do leitor são só os de `vendor/ocr/`.
8. O resultado confirmado segue o caminho de sempre (`Esta coluna é o quê?`, formato lembrado, junção por código). Datas e números entram como texto da célula.

**Critérios (v1.9).** CA-74 `vendas_foto_1.jpg` + `vendas_foto_2.jpg` (fotos de impressão com leve giro e ruído, 30 vendas cada, cabeçalho `Código Data Cliente Região Vendedor Valor Situação`, escolhidas no mesmo envio) → **uma** janela `Conferir leitura` com 60 linhas; **≥ 95% das células** (60 x 7 = 420) iguais às de `vendas.csv` (linhas 1 a 60) **antes de corrigir**; após corrigir as marcadas (o teste edita só células marcadas para o valor do CSV) e `Confirmar`, os 60 registros do CSV entram com os mesmos valores. CA-75 `.zip` com CSV + XLSX + JPG → os três lidos; o JPG passa pela conferência. CA-76 depois de 1 uso do OCR, com a rede bloqueada (contexto offline) e a página recarregada, o OCR de `vendas_foto_1.jpg` funciona igual. CA-77b `contrato_foto.jpg` (texto sem tabela) → toast `Não encontrei uma tabela neste arquivo`, nenhuma janela, nada entra. CA-110z: imagem corrompida (bytes cortados) → `Não consegui ler <arquivo>.`; nenhuma requisição a outro host; foto de 12 MP (gerada no teste) lida sem travar a aba (a página continua respondendo). PDF escaneado: um PDF feito de `vendas_foto_1.jpg` (gerado no teste com reportlab, só imagem, sem texto) → mesma conferência do CA-74 (linhas 1 a 30).

**Decisões (v1.9):** D-60 correções por padrão da coluna (regra 3) são automáticas mas sempre marcadas e sempre passam pela conferência. D-61 modelo de idioma `best_int` (1,4 MB; menos preciso que o `best` completo, de 6,7 MB, mas leve para o celular). D-62 limite de 20 imagens/páginas e 120 s. D-63 só português.

---

## 8. Dados e armazenamento

- **Sem Supabase, sem R2, sem servidor.** Tudo no navegador:
  - `localStorage`: configuração, layouts de colunas aprendidos, indicadores escolhidos, layout do painel, sinônimos, contas personalizadas.
  - `IndexedDB`: registros de cada conjunto (chave = código do registro); juntar arquivos atualiza campo a campo, sem apagar o que o arquivo novo não traz (regra atual).
- O arquivo original não é guardado: lê, guarda os registros e descarta.
- Backup = um arquivo `.json` com tudo; restaurar substitui ou soma (pergunta).
- **Sensível:** os relatórios podem ter nomes de pessoas. Por isso nada sai do aparelho, e o repositório só recebe dados de teste anonimizados.
- Dados de teste em `tests/dados/`: **só dados fictícios**, gerados por script com semente fixa (`tests/gerar_dados.py`): `vendas.*` (pedidos de uma loja) e `chamados.*` (atendimentos de suporte), nos formatos da etapa 7. Nenhum relatório real entra no repositório.

**Critérios**
- CA-80: carregar o mesmo arquivo duas vezes (`Carregar relatório`, R-02) → contagem não muda (conferida no arquivo de `Baixar backup`, R-15).
- CA-81: arquivo A (código, cliente) + arquivo B (código, prioridade), ambos por `Carregar relatório` (R-02) → registros com os dois campos; campo vazio em B não apaga valor de A (conferido no arquivo de `Baixar backup`, R-15).
- CA-82: 72 mil registros no histórico → painel abre em ≤ 5 s em notebook comum (medido no Playwright, máquina de CI).
- CA-83: todos os arquivos de `tests/dados/` são gerados pelo `gerar_dados.py` (rodar de novo dá o mesmo conteúdo).

---

## 9. Estrutura reaproveitada do protótipo (regressão)

O código atual é um protótipo feito para um caso específico. **Nada do conteúdo dele entra no produto** (nomes, regras de negócio, frases, abas e indicadores próprios daquele caso). Entra só a **estrutura**, que vira peça genérica e não pode quebrar:

- CA-90: leitor de CSV acha a linha de cabeçalho sozinho, aceita `;` `,` e tab, UTF-8 e Windows-1252 (arquivo escolhido por `Carregar relatório`, R-02).
- CA-91: importador que aprende: formato novo → "Esta coluna é o quê?" (R-21, botões `Confirmar`/`Cancelar`, R-22) uma vez; o formato fica lembrado (Config → `Formatos lembrados` → "Esquecer", R-23/R-24).
- CA-92: junção por código, campo a campo (CA-80/81), guardada no IndexedDB, com backup/restaurar/apagar: `Baixar backup` (R-15) baixa `historico_RaioX_AAAA-MM-DD.json`; `Apagar todos os dados` + `Apagar` (R-17) zera; `Restaurar backup` + `Substituir` (R-16) volta a mesma contagem.
- CA-93: janelas flutuantes: abrir pelo clique em qualquer número (ex.: `Total de registros`, R-07), barra ou mês; arrastar; minimizar para o rodapé (`Minimizar`, R-35); várias abertas; mini painel com chips que filtram a lista; "Limpar seleção" (R-37); imprimir (`Imprimir`, R-38; A4, com a seleção escrita no topo); copiar (`Copiar`, R-39). Os três botões do rodapé da janela ficam visíveis ao abrir.
- CA-94: semelhança de texto (erro de digitação ≥ 80%) usada no pedido escrito e nas frases padrão.
- CA-95: possíveis repetidos: registros abertos com texto parecido (peso por raridade da palavra), mostrados para a pessoa decidir.
- CA-96: tempo entre duas datas em faixas (`Até 1 h` … `Mais de 7 dias`, R-40), mediana (`Mediana:`), % dentro do prazo (`Dentro de N h:`); durações mostradas em "h min".
  **Formato (decisão v1.1, dúvida 1 do Testador; igual ao CA-43):** a mediana usa só os registros com as duas datas; com quantidade par, é a média dos dois do meio. O resultado é arredondado ao **minuto inteiro mais próximo, meio minuto para cima** (sem casas decimais, sem segundos). Abaixo de 1 h: `M min` sem zero à esquerda (ex.: `48 min`, `5 min`, `0 min`). De 1 h em diante: `H h MM min`, horas acumuladas **sem converter em dias**, minutos sempre com 2 dígitos (ex.: `1 h 05 min`, `26 h 00 min`, `200 h 10 min`). Sem dados: `—`. Ex.: 1.565 min → `26 h 05 min`; 29,5 min → `30 min`. A mesma regra vale para toda duração mostrada na tela, nas janelas e no Excel.
- CA-97: meta configurável por indicador percentual (padrão 90%, campo `Meta dos indicadores em % (padrão 90)`, R-41): acima da meta em verde, "faltam X para a meta".
- CA-98: Excel (botão `Gerar Excel`, R-18) com capa, faixa de números, período real, filtros, rodapé, configuração de impressão; período tudo / mês / de–até (R-30); formatos uma planilha por relatório / tudo numa / arquivos separados (`Formato`, R-19).
  **Nome do arquivo (decisão v1.1, dúvida 2 do Testador):** `RaioX_<relatório>_<data>.xlsx`, com `<data>` = **AAAA-MM-DD**, a data do aparelho no momento em que o arquivo é gerado (ex.: `RaioX_VENDAS_2026-11-25.xlsx`). `<relatório>` = nome do conjunto em maiúsculas, sem acentos, com `_` no lugar de espaços; `TUDO` quando há mais de um conjunto num só arquivo; em `Arquivos separados`, um arquivo por conjunto. O backup segue o mesmo formato de data: `historico_RaioX_AAAA-MM-DD.json`. Teste: o nome casa com `^RaioX_[A-Z0-9_]+_\d{4}-\d{2}-\d{2}\.xlsx$` e a data é a de hoje.
- CA-99: filtros começam fechados (`Filtros`, R-28); período e filtros (R-29 a R-34) valem para o painel, as janelas e o Excel.

## 9a. Tela "Esta coluna é o quê?" em prévia (F-80, Galindo 26/11/2026; substitui o desenho da etapa 1 nos CA-24 e R-65)
- Depois de carregar um formato novo, tabela com todas as colunas lado a lado e as 5 primeiras linhas reais. No topo de cada coluna, em ordem: **Aparece?** (Sim por padrão; Não = antigo Ignorar), **Nome** (título do arquivo; sem título "Campo 1", "Campo 2"…), **Tipo**: Número, Data, Grupo (antigo Categoria) ou Texto.
- Duas perguntas únicas embaixo: "Qual coluna identifica cada linha?" (antigo Código; obrigatória, e a coluna precisa aparecer) e "Qual coluna mostra o andamento?" (antigo Situação; opcional).
- Linhas totalmente em branco saem sozinhas, com aviso "N linhas em branco deixadas de fora".
- Cabeçalho errado: botão "O cabeçalho está em outra linha" (tocar na linha dos títulos da prévia) e "O arquivo não tem cabeçalho" (Campo 1, 2, 3…); a escolha é lembrada com o formato.
- Config → Formatos lembrados → Editar reabre a tela (nomes fixos; muda Aparece? e Tipo). Botão visível "Apagar tudo e carregar de novo" perto de "Carregar dados".
- Internamente os tipos continuam os mesmos (codigo, situacao, ignorar, categoria…); só a tela mudou.

## 9b. Versão Excel para baixar (macro)

- Mesma estrutura do app, sem conteúdo de nenhum caso: importar CSV/XLSX (ou .zip), perguntar o que é cada coluna (uma vez por formato), escolher indicadores do catálogo da etapa 2, painel com segmentação por período e categoria, botão "Gerar relatório" com capa.
- CA-110: a macro importa `tests/dados/vendas.csv`, pergunta as colunas e gera o mesmo Total e Por cliente que o app (conferência manual no Excel 2016, roteiro em `docs/03_homologacao/roteiro-excel.md`).
- CA-111: `grep -i` dos termos do CA-03 no `.bas` = 0.

## 9c. Tela Relatório (v2.0, 27/11/2026, F-77 + F-76)

**Princípio (Galindo, 26/11/2026).** O **Painel** serve para *acompanhar*: a pessoa escolhe os indicadores, mexe, filtra; responde "quanto é?". O **Relatório** serve para *entender e comunicar*: o Raio X monta sozinho o que importa e a pessoa só ajusta; responde "o que está acontecendo, onde está o problema e o que merece atenção?". Tudo no navegador, offline, sem servidor, sem IA, sem biblioteca nova pela rede. Nada fixo de um ramo: cada parte nasce do **tipo do campo** (Número, Data, Grupo, andamento), nunca do nome. Sem encaixes nem dublês (regra do projeto): os critérios rodam contra `tests/dados/`.

**Linguagem.** Frases curtas, para quem não sabe Excel: "Metade ficou abaixo de…", "estão em aberto", "fazem 62% do total". Nada de "percentil", "outlier", "desvio padrão", "Pareto" ou "aging" na tela (esses termos só aparecem aqui, na especificação).

### 9c.1 Fluxo

1. A pessoa carrega os dados e usa o Painel como hoje.
2. No fim do Painel, o cartão `Gerar Excel` (R-18) dá lugar ao cartão `Relatório` com o botão **`Gerar relatório`** (R-140). O `Formato` (R-19) sai do Painel e vai para a janela de exportar (R-159).
3. `Gerar relatório` abre, no próprio app, a **tela Relatório** do relatório aberto no Painel (o do filtro `Relatório`, R-29), com os mesmos filtros e período (⚖️ D-64). O Painel fica escondido; `Voltar ao painel` volta sem perder nada.
4. A tela mostra, em ordem: capa → `O que tem neste relatório` → `Resumo executivo` → `Números principais` → `O que o Raio X encontrou` → partes por tipo de dado → `Do seu painel` → `Registros` → `Como ler este relatório` (9c.3).
5. `Editar relatório` liga o modo edição (títulos, textos, observação por parte, esconder/mostrar, ordem, forma do gráfico); `Concluir edição` desliga. O que foi editado fica guardado por relatório (9c.6).
6. `Exportar arquivo` abre a janela para escolher **Excel** (visual da F-76, só valores, 9c.8) ou **PDF** (a mesma cara da tela, 9c.9).

### 9c.2 Nomes na tela (rótulos exatos)

Mesmas regras da 0.1: textos exatos, testes localizam por papel, rótulo ou texto, nunca por `id` ou classe. Números em pt-BR (milhar com ponto, decimal com vírgula; somas, médias e medianas com 2 casas; percentuais com 1 casa).

| Nº | Rótulo exato | Tipo | Onde / observação |
|---|---|---|---|
| R-140 | cartão com título `Relatório`, texto `Monta um relatório pronto para ler, ajustar e exportar.` e botão `Gerar relatório` | cartão e botão | Painel, no fim, no lugar do cartão `Gerar Excel` (R-18), que deixa de existir. Sem registros no relatório aberto, o botão fica desabilitado |
| R-141 | região `<section aria-label="Relatório">` com barra de botões `Voltar ao painel`, `Editar relatório` (vira `Concluir edição`), `Exportar arquivo` | tela | ocupa o lugar do Painel; a barra de abas (R-03/R-04) continua; tocar na aba `Painel` também volta |
| R-142 | **capa**: linha pequena `<Área> · <Cliente>` (só as partes preenchidas na Config; sem nenhuma, a linha não aparece); título (heading nível 2) `Relatório <relatório>` (⚖️ D-82); `Registros de dd/mm/aaaa a dd/mm/aaaa` (regra do período da 0.5, R-87; sem datas: `sem datas`); `Filtros: <texto de filtros do Seu painel>`; `Gerado em: dd/mm/aaaa hh:mm`; `Fonte: <relatório> (<N> registros)` (⚖️ D-83); logo da Config, se houver | capa | primeira coisa da tela; mesma faixa escura do topo do app |
| R-143 | `O que tem neste relatório` | heading + lista | um item por parte **visível**, na ordem: link (`<a href="#…">`) com o título da parte e, depois, uma frase (9c.3, coluna "Frase do índice") |
| R-144 | `Resumo executivo` | heading + `<ol>` | de 1 a 5 frases automáticas (9c.4) |
| R-145 | `Números principais` | heading + cartões | 9c.5 |
| R-146 | `O que o Raio X encontrou` | heading + lista | até 5 achados (9c.7); cada um com título em negrito, frase, linha pequena `Por que apareceu: <regra em palavras>` e botão `Ver os registros`. Sem achado: `O Raio X não encontrou nada fora do comum nestes registros.` |
| R-147 | `Pendências por idade` | parte | faixas `0 a 7 dias`, `8 a 15 dias`, `16 a 30 dias`, `Mais de 30 dias`; texto pequeno `Idade contada até dd/mm/aaaa.` (hoje, ⚖️ D-65) |
| R-148 | `Os 10 mais antigos em aberto` | parte (tabela) | colunas `Código`, `<campo de data>`, `Dias em aberto`, `<campo do andamento>`; do mais antigo ao mais novo |
| R-149 | `Atrasados` | cartão dentro de `Números principais` | texto `<n> atrasados (mais de <prazo> em aberto)`; `<prazo>` = `fmtPrazo` (⚖️ D-66) |
| R-150 | `Entrou e saiu por mês` (com 2 campos de data) ou `Entrou por mês (<campo de data>)` (com 1) | parte | tabela `Mês`, `Entrou`, `Saiu`, `Saldo` (sem a 2ª data: só `Mês`, `Entrou`) + gráfico |
| R-151 | `<Número>: como os valores se distribuem` (ex. `Valor: como os valores se distribuem`) | parte, uma por campo Número (até 3, na ordem dos campos) | cartão `Média`, `Mediana`, `Mínimo`, `Máximo`; frase `Metade dos registros ficou abaixo de <mediana>.`; tabelas `5 maiores` e `5 menores` (colunas `Código`, `<1º Grupo>` se houver, `<Número>`) |
| R-152 | `<Grupo>: quem concentra` (ex. `Cliente: quem concentra`) | parte, uma por campo Grupo (até 3, ⚖️ D-69) | tabela `<Grupo>`, `<medida>`, `% do total`, `% acumulado` (medida = `Soma de <1º Número>` ou `Registros`) + gráfico + frase (9c.4) |
| R-153 | `Tempo entre duas datas` | parte (só com 2 campos de data) | o mesmo conteúdo do bloco do painel (R-40, CA-96) |
| R-154 | `Do seu painel` | parte (só com escolha confirmada em `O que acompanhar`) | os blocos do painel, na ordem do layout (etapa 6), sem os escondidos; é **uma** parte (⚖️ D-75) |
| R-155 | `Registros` | parte | os 100 primeiros na ordem da lista do Painel + `Mostrando 100 de <N> registros. No Excel vão todos.` (com N ≤ 100: `Mostrando os <N> registros.`) (⚖️ D-76) |
| R-156 | `Como ler este relatório` | parte, sempre a última | uma linha por parte visível, no formato do `Seu painel` (0.3): `<título> — <o que mostra>. Período: … . <Filtros>.` (reaproveita `resumoBlocos`) |
| R-157 | comparação: `↑ <p>% em relação a <período anterior>`, `↓ <p>% em relação a <período anterior>`, `= igual a <período anterior>`, `sem base para comparar` | texto pequeno sob o número do cartão | 9c.5; `<período anterior>` = `mm/aaaa` (mês) ou `dd/mm/aaaa a dd/mm/aaaa` |
| R-158 | modo edição: na capa, campo `Título do relatório` (até 80 caracteres); no resumo, caixa `Texto do resumo executivo` (uma frase por linha, até 1.000 caracteres); por parte, grupo `role="group"` com `aria-label` = `Controles de <título original>` contendo `Subir`, `Descer`, `Esconder` (vira `Mostrar`), campo `Título` (até 80), caixa `Observação` (até 500) e select `Forma` (só em parte com gráfico); na barra, `Voltar ao padrão` | controles | capa, `O que tem neste relatório` e `Como ler este relatório` não sobem, não descem e não se escondem. `Voltar ao padrão` pergunta `Voltar ao padrão do relatório?` com `Voltar ao padrão` e `Cancelar` |
| R-159 | janela `Exportar arquivo` com grupo `Tipo de arquivo` (opções `Excel`, marcada, e `PDF`), select `Formato` (opções de R-19, só aparece com `Excel`), botões `Exportar` e `Cancelar`; mensagens `Gerando…`, `Excel gerado.`, `Na janela que abrir, escolha “Salvar como PDF”.` | janela | `PDF` só aparece a partir da E5 |
| R-160 | `Forma` (R-105) ganha `Área`, `Rosca`, `Radar`, `Velocímetro`, `Bolhas`; ordem das opções: `Número`, `Barras`, `Linha`, `Área`, `Pizza`, `Rosca`, `Radar`, `Velocímetro`, `Bolhas`, `Tabela` (só as que o dado permite, 9c.10) | select | vale no Painel (Editar layout) e no Relatório |
| R-161 | avisos: `Rosca com mais de 8 fatias: mostrando barras`; `Radar precisa de 3 a 10 grupos: mostrando barras`; `Bolhas precisam de pelo menos 2 grupos: mostrando barras` | texto | mesma regra do aviso da pizza (R-105) |
| R-162 | velocímetro: texto central `<p>% de <meta>%` (sem meta: `<p>%`) e, abaixo da meta, `faltam X para a meta` (texto atual, CA-97) | texto | 9c.10 |
| R-163 | aviso de texto editado: `Texto editado por você: confira se os números ainda valem.` | texto | sob o resumo ou a observação editada, quando os registros mudaram depois da edição |

**Observação editada.** Aparece logo abaixo do título da parte, em itálico, como `Observação: <texto>`. Texto vindo de arquivo, título ou observação entra sempre por `textContent` (seção 10).

### 9c.3 Partes do relatório e quando aparecem

"Campo de data" = o de `Campo de data` (R-31) ou o 1º campo Data; "2ª data" = o 2º campo do par de `Tempo entre duas datas`; "andamento" = o campo marcado em "Qual coluna mostra o andamento?" (9a); "em aberto" = regra D-09 (0.3). Todas as contas usam os registros **depois de filtros e período** (como o painel).

| Parte | Aparece quando | Frase do índice (R-143) |
|---|---|---|
| `Resumo executivo` | sempre | `As frases principais, para ler em 1 minuto.` |
| `Números principais` | sempre | `Os números do período e a comparação com o período anterior.` |
| `O que o Raio X encontrou` | sempre (com a frase de vazio quando não há achado) | `O que foge do comum e merece atenção.` |
| `Pendências por idade` + `Os 10 mais antigos em aberto` | campo de data + andamento + ≥ 1 em aberto | `Há quanto tempo os registros em aberto esperam.` |
| `Entrou e saiu por mês` / `Entrou por mês (<campo>)` | campo de data | `Quantos entraram (e saíram) em cada mês.` |
| `<Número>: como os valores se distribuem` | campo Número com ≥ 1 valor | `Média, mediana, menores e maiores de <Número>.` |
| `<Grupo>: quem concentra` | campo Grupo com ≥ 2 valores | `Quem responde pela maior parte do total.` |
| `Tempo entre duas datas` | 2 campos de data | `Quanto tempo passa entre <data 1> e <data 2>.` |
| `Do seu painel` | escolha confirmada | `Os indicadores que você escolheu no painel.` |
| `Registros` | sempre | `A lista dos registros considerados.` |
| `Como ler este relatório` | sempre | `Como cada parte foi calculada.` |

Ordem padrão = a da tabela (capa e `O que tem neste relatório` antes de tudo). Relatório só com Código e Texto: capa, resumo com 1 frase, `Números principais` só com o total, `O que o Raio X encontrou`, `Registros`, `Como ler este relatório`, sem erro.

**Contas das partes (regras R-164 a R-169).**
- **R-164 Idade e pendências.** Idade (em dias inteiros, para baixo) = hoje (relógio do aparelho, 00:00 local) − data do registro no campo de data (⚖️ D-65). Data no futuro (idade < 0) fica fora das faixas e vai para o achado A1. Faixas: 0–7, 8–15, 16–30, > 30. `Os 10 mais antigos em aberto`: em aberto com data, ordem crescente de data (empate: código), até 10. Clicar numa faixa ou linha abre a janela com os registros.
- **R-165 Atrasados.** Em aberto há mais que o prazo da Config (`prazoH`, o mesmo do `Dentro de N h`; ⚖️ D-66): hoje (data e hora do aparelho) − data/hora do registro > prazoH horas (data sem hora = 00:00). `fmtPrazo(h)`: múltiplo de 24 e ≥ 48 → `<h/24> dias`; senão `<h> h` (padrão: `24 h`).
- **R-166 Entrou e saiu.** Entrou no mês = registros com o campo de data naquele mês. Saiu no mês = registros com a 2ª data naquele mês. Saldo = Entrou − Saiu. Meses do menor ao maior que aparecem em qualquer das duas datas; mês sem registro vale 0. Gráfico padrão: `Barras` com as duas séries (Entrou e Saiu) lado a lado; formas `Linha`, `Área`, `Tabela`.
- **R-167 Distribuição de um Número.** Média, mediana (regra do CA-96 para quantidade par), mínimo, máximo dos valores numéricos (vazios fora). Frase `Metade dos registros ficou abaixo de <mediana>.`; se média > 1,2 × mediana, mais `A média está acima da mediana porque alguns valores são bem altos.`; se média < 0,8 × mediana, `A média está abaixo da mediana porque alguns valores são bem baixos.` (⚖️ D-70; nada com mediana ≤ 0). `5 maiores`/`5 menores`: empate desempata pelo código.
- **R-168 Quem concentra.** Grupos ordenados pela medida (soma do 1º Número; sem Número, contagem), do maior ao menor, empate por nome. Tabela com todos os grupos até 10 e `Outros` (soma do resto) como o painel. `% do total` e `% acumulado` com 1 casa. Frase: `Os 3 primeiros de <Grupo> fazem <p>% do total.` (com 2 grupos: `Os 2 primeiros…`) e, quando há ≥ 4 grupos, `Para chegar a 80% do total são <k> de <n>.`, onde k = menor quantidade de grupos cujo acumulado ≥ 80% (⚖️ D-69). Gráfico padrão: `Barras`.
- **R-169 Comparação com o período anterior** (⚖️ D-67): `Período` = `Mês` → mês anterior; `De–até` → o mesmo número de dias logo antes de `De`; `Tudo` → compara o **último mês com registros** com o mês antes dele. A conta é refeita com os mesmos filtros de categoria e busca. p = (atual − anterior) / anterior × 100, 1 casa, sem sinal (a seta diz o sentido); anterior = 0 ou sem campo de data → `sem base para comparar`. As setas não têm cor de bom ou ruim (⚖️ D-67); só a meta pinta (9c.5).

### 9c.4 Resumo executivo

Frases automáticas, na ordem abaixo, as que os dados permitirem, **no máximo 5** (⚖️ D-71). Números formatados como na tela.
1. `O relatório tem <N> registros de dd/mm/aaaa a dd/mm/aaaa.` (sem datas: `O relatório tem <N> registros.`) — sempre.
2. `<a> estão em aberto (<p>% do total); <t> estão atrasados e o mais antigo espera há <d> dias.` — com data + andamento.
3. `Em <período atual> entraram <n> registros, <p>% a mais que em <período anterior>.` (ou `a menos`; `o mesmo número que`) — com campo de data e base para comparar.
4. `Atenção: <frase do 1º achado>` — com ≥ 1 achado.
5. `Os 3 primeiros de <Grupo> fazem <p>% do total.` — 1º campo Grupo da R-168.
6. `Metade dos registros ficou abaixo de <mediana> em <Número>; a média é <média>.` — 1º campo Número.

Editado pela pessoa (R-158), o resumo vira o texto dela (uma frase por linha, linha vazia some) e não é mais refeito; `Voltar ao padrão` volta às frases automáticas.

### 9c.5 Números principais

Cartões (fundo claro, fio colorido em cima, rótulo pequeno, número grande), cada um clicável (abre os registros) e com a comparação R-157 quando houver base:
- `Total de registros` — contagem.
- `Em aberto` — contagem e `% do total` (com andamento).
- `Concluídos` — `% do total` dos que não estão em aberto, com a meta da Config (`Meta dos indicadores em %`, R-41): abaixo da meta, número com `data-fora-meta="true"`, cor de alerta e `faltam X para a meta`; na meta ou acima, cor boa (CA-97) (⚖️ D-68).
- `Atrasados` — R-149/R-165 (com data + andamento).
- `Dentro de <prazo>` — o % do bloco de tempo (com 2 datas), com a mesma regra de meta.
- Para cada Número (até 3): `Soma de <Número>` e `Mediana de <Número>`.

### 9c.6 Edição e guarda

- O que se edita (R-158): título do relatório, texto do resumo, título e observação de cada parte, esconder/mostrar, ordem (`Subir`/`Descer`; no computador também arrastar, como a etapa 6), forma do gráfico (só as permitidas, 9c.10). Não se edita número (⚖️ D-74).
- Fora do modo edição, a parte escondida não aparece, não entra em `O que tem neste relatório`, em `Como ler este relatório`, no Excel nem no PDF. Em modo edição aparece esmaecida (`data-escondido="true"`).
- Guarda por relatório no navegador (`localStorage` `raiox_relatorio`): `{ <relatório>: { titulo, resumo, partes: [{ id, titulo, obs, oculto, forma }] } }`, ordem = ordem da lista. Ausente = padrão. Parte nova (dado novo) entra no fim, antes de `Registros`; parte que deixou de existir é ignorada.
- Entra no **backup** (chave `relatorio`, validada como `layout`: formato errado rejeita o arquivo inteiro; textos cortados nos limites de R-158; até 50 partes por relatório). `Substituir` troca; `Somar` só traz o de relatório que ainda não tem (como D-32). `Apagar todos os dados` apaga também.
- Quando os registros mudam depois de editar resumo ou observação, aparece R-163 até a próxima edição daquele texto (⚖️ D-74).

### 9c.7 "O que o Raio X encontrou"

Regras fixas, sem IA, sobre os registros filtrados (⚖️ D-73). Cada regra gera achados `{regra, titulo, frase, porque, codigos}`; o app expõe `window.__achados(<relatório>)` com **todos** os achados (sem corte), na ordem de prioridade, para o teste. Na tela entram **no máximo 2 por regra e 5 no total**, na ordem de prioridade abaixo; dentro da regra, o de mais registros primeiro (⚖️ D-72). Limiares são provisórios (⚖️ D-72).

| Pri. | Regra | Quando aparece (limiar provisório) | Título | Frase | Por que apareceu |
|---|---|---|---|---|---|
| A1 | Data no futuro | ≥ 1 registro com qualquer campo Data depois de hoje (Galindo confirmou 26/11) | `Datas no futuro` | `<n> registros com <campo> depois de hoje; a mais distante é dd/mm/aaaa.` | `data maior que a data de hoje` |
| A2 | Data final antes da inicial | 2 datas; ≥ 1 registro com 2ª data < 1ª data | `Datas fora de ordem` | `<n> registros com <data 2> antes de <data 1>.` | `<data 2> anterior a <data 1>` |
| A3 | Parados há muito tempo | ≥ 1 em aberto com idade > 30 dias (idade de hoje; o histórico de mudanças fica para a V2) | `Parados há muito tempo` | `<n> registros em aberto há mais de 30 dias; o mais antigo há <d> dias.` | `em aberto há mais de 30 dias` |
| A4 | Fora da curva | Número com mediana > 0; ≥ 1 valor > 3 × mediana | `Valores fora da curva em <Número>` | `<n> registros com <Número> acima de 3 vezes a mediana (<3×mediana>); o maior é <máx> (<código>).` | `mais de 3 vezes a mediana` |
| A5 | Pendências crescendo | data + andamento; registros em aberto que entraram em cada um dos 3 últimos meses com registros crescem sempre (m1 < m2 < m3) | `Pendências crescendo` | `Os registros em aberto que entram a cada mês cresceram 3 meses seguidos: <mm/aaaa> <n1>, <mm/aaaa> <n2>, <mm/aaaa> <n3>.` | `3 meses seguidos de alta` |
| A6 | Mudança brusca | andamento ou Grupo; nos 2 últimos meses com registros, ambos com ≥ 20 registros, a parte de um valor muda ≥ 15 pontos percentuais | `Mudança brusca em <campo>` | `<valor> foi de <p1>% em <mm/aaaa> para <p2>% em <mm/aaaa>.` | `mudou 15 pontos ou mais de um mês para o outro` |
| A7 | Concentração escondida | andamento + Grupo; para um valor do andamento com ≥ 10 registros, um valor do Grupo tem ≥ 50% desses registros e essa parte é ≥ 2 × a parte dele no total | `Concentração em <valor do andamento>` | `<Grupo> <valor> responde por <p>% dos registros <valor do andamento>, mas só por <q>% do total.` | `metade ou mais de uma situação num só grupo` |
| A8 | Buracos | (a) campo (não Código) vazio em ≥ 20% dos registros (a 2ª data não conta como vazia em registro em aberto); (b) campo de data com ≥ 30 registros e um intervalo ≥ 14 dias sem registro entre a menor e a maior data | `Campo vazio: <campo>` / `Dias sem registro` | `<campo> está vazio em <p>% dos registros (<n>).` / `Nenhum registro de dd/mm/aaaa a dd/mm/aaaa (<d> dias).` | `vazio em 20% ou mais` / `14 dias ou mais sem registro` |
| A9 | Possíveis repetidos | ≥ 1 par da busca de repetidos atual (CA-95, `Core.repetidos`, mesma base de até 5.000) | `Possíveis repetidos` | `<n> pares de registros parecidos; confira se são o mesmo.` | `texto muito parecido entre registros` |

`Ver os registros` abre a janela de registros (CA-93) com exatamente os registros do achado (A8b: os registros das duas pontas do intervalo; A6/A7: os registros do valor no(s) mês(es)/situação). Achados nunca alteram dados.

### 9c.8 Excel do "Exportar arquivo" (visual da F-76)

Continua **sem fórmula, sem macro e sem gráfico nativo** (D-12; CA-47). Mesmo nome de arquivo (CA-98) e mesmos formatos (R-19). Cores (⚖️ D-84): faixa escura `#0F2A4A` (azul-marinho do topo do app), destaque `#1F6FEB` (azul do botão do app, no lugar do rosa do modelo), fundo de cartão `#EEF3FB`, zebrado `#F4F6FB`, bordas finas `#DFE4EF`, texto apagado `#5B6683`.

**Ordem das planilhas** (⚖️ D-80): `Capa` → `Como ler este relatório` (agora sempre; uma linha por parte visível) → `Resumo` (resumo executivo, números principais, achados) → `Análises` (partes por tipo de dado visíveis, na ordem do relatório, com título e observação editados) → planilhas de painel (`Painel`…; só se a parte `Do seu painel` está visível) → planilhas de registros (como hoje). Com vários relatórios no arquivo (`Tudo numa planilha`), `Resumo - <relatório>` e `Análises - <relatório>` (regra de nome R-80); cada relatório usa o seu relatório editado (ou o padrão).

- **Capa:** sem coluna vazia antes do conteúdo; coluna A com largura entre 14 e 40 (item 12). A1 = `<Área> · <Cliente>` pequeno (fonte 9, cor destaque). A2 = título do relatório, fonte ≥ 18, negrito, branca sobre faixa escura mesclada A2:F2, **altura da linha ≥ 30** para não cortar (item 12). A3 = `Registros de … a …` sobre a faixa. Depois, rótulos `Período`, `Filtros`, `Gerado em`, `Fonte` na coluna A, valores na B (R-87 a R-89 continuam valendo por texto). Depois, `O que tem neste arquivo`: uma linha por planilha, coluna A = nome da planilha com **link interno** (`#'<planilha>'!A1`), coluna B = uma frase (a do índice ou `A lista dos registros considerados.`). Logo continua (CA-11/12).
- **Cada planilha (menos a Capa)** — substitui R-81 (⚖️ D-79): A1 = `<relatório> · <Área> · <Cliente>` (só partes preenchidas), fonte 9, cor destaque; A2 = título (nome da planilha ou da aba), negrito branco sobre faixa escura mesclada até a última coluna usada, altura ≥ 24; A3 = itálico apagado `Período: … · Filtros: … · Gerado em: dd/mm/aaaa hh:mm`; A4 vazia; conteúdo da linha 5 em diante. Cor da aba (`tabColor`): `Capa` escura, `Resumo`/`Análises`/painel destaque, registros apagado.
- **Cartões:** rótulo pequeno (fonte 9) numa linha, número grande (fonte ≥ 14, negrito) na seguinte, fundo `#EEF3FB`, borda de cima média na cor destaque; percentuais na cor destaque. Mesmos rótulos e valores da tela (R-86 continua: rótulo numa linha, valor na de baixo).
- **Tabelas:** cabeçalho com fundo destaque, letra branca negrita; linhas zebradas; bordas finas; nas planilhas de registros, filtro (`autoFilter`) no cabeçalho e cabeçalho congelado.
- **Barra (item 11; muda a 0.5 e D-12 em parte, ⚖️ D-78):** a coluna `Barra` deixa de ter `█`; recebe o número n (o mesmo que fazia a barra) com formato que esconde o número (`;;;`) e **barra de dados** (formatação condicional `dataBar`, cor destaque, sem gradiente) no intervalo da tabela. Formatação condicional não é fórmula de célula.
- **`Como ler este relatório` (item 13):** coluna A com largura fixa 110 e **quebra de texto** em toda célula de texto; nenhuma altura de linha fixa pequena.
- **Datas nos registros (item 14):** campo Data em que **nenhum** registro tem hora → célula data com formato `dd/mm/yyyy`; com hora em algum → `dd/mm/yyyy hh:mm`. Nunca `00:00` inventado.
- **Números nos registros (item 15):** campo Número → célula número com `#,##0.00` (mostra `323,90` e `1.192,30`); vazio continua vazio.
- O Excel mostra os mesmos números da tela para os mesmos filtros; parte escondida não sai; gráfico vira tabela + barra de dados (inclusive rosca, radar, velocímetro, área e bolhas: tabela com as colunas da tela; bolhas com `<Grupo>`, `Registros`, `Média`, `Total`).

### 9c.9 PDF do "Exportar arquivo"

- Sem biblioteca nova (⚖️ D-81): o app monta a tela Relatório no modo impressão (CSS `@media print`, A4 retrato, margens de 12 mm) e chama `window.print()`; a pessoa escolhe `Salvar como PDF` no navegador. Durante a impressão o título do documento é `RaioX_<RELATÓRIO>_<AAAA-MM-DD>` (mesma regra do CA-98, sem extensão), para o nome sugerido do PDF.
- Sai igual à tela fora do modo edição: capa sozinha na 1ª página; cada parte sem quebrar no meio quando couber (`break-inside: avoid`); gráficos em SVG (vetor); sem botões, controles, janelas nem barra de abas; partes escondidas fora.
- Em toda página, rodapé pequeno `<relatório> · Período: … · Filtros: … · Gerado em: … · Fonte: …`.

### 9c.10 Formas de gráfico novas (Painel e Relatório; amplia D-34, ⚖️ D-77)

Todas em SVG próprio (sem biblioteca), com `role="img"` e `aria-label` = `<Forma>: <título>`; cada pedaço (fatia, ponto, bolha) é focável, tem `aria-label` = `<nome>: <valor>` e abre a janela de registros com clique, Enter ou espaço (como as barras). Funcionam em 390 px sem rolagem lateral.

| Tipo de bloco/parte | Formas permitidas |
|---|---|
| Um número só (cartão) | `Número` |
| `% por <andamento>` | `Barras`, `Pizza`, `Rosca`, `Radar`, `Velocímetro`, `Tabela` |
| `Tempo entre duas datas` | `Número`, `Velocímetro` |
| Por Grupo (contagem), pedido com `Agrupar por`, `<Grupo>: quem concentra` | `Barras`, `Pizza`, `Rosca`, `Radar`, `Tabela` |
| `<Número> por <Grupo>` | `Barras`, `Pizza`, `Rosca`, `Radar`, `Bolhas`, `Tabela` |
| Por mês (uma série) | `Barras`, `Linha`, `Área`, `Pizza`, `Rosca`, `Tabela` |
| `Entrou e saiu por mês` (duas séries) | `Barras`, `Linha`, `Área`, `Tabela` |

- **Rosca:** como a pizza, com o total no centro (`<total>`); > 8 fatias → barras com aviso (R-161).
- **Velocímetro:** meio círculo de 0 a 100%, ponteiro no valor e marca na meta da Config. `% por <andamento>` mostra o % de **Concluídos** (não em aberto; ⚖️ D-77); `Tempo entre duas datas` mostra o `Dentro de <prazo>`. Texto R-162. Clicar abre os registros que formam o %.
- **Radar:** um eixo por grupo (3 a 10, sem `Outros`), um polígono com os valores; fora disso → barras com aviso.
- **Área:** como a linha, com a área até o eixo preenchida.
- **Bolhas:** só em `<Número> por <Grupo>`: cada grupo (os 10 maiores pela soma, sem `Outros`) é uma bolha; eixo X = quantidade de registros, eixo Y = média do Número, **área** da bolha proporcional à soma; `aria-label` = `<grupo>: <n> registros, média <m>, total <s>`; < 2 grupos → barras com aviso.
- A forma escolhida fica no layout (Painel) ou no relatório guardado (Relatório) e vai no backup; no Excel não muda nada além da tabela (D-33).

### 9c.11 Critérios de aceite

Dados: `tests/dados/vendas.csv` (500 registros; Código, Data, Cliente, Região, Vendedor, Valor, Situação), `tests/dados/chamados.csv` (300; Código, Abertura, Conclusão, Categoria, Responsável, Situação) e, na E2, `achados.csv` e `sem_achados.csv` (novos, gerados por `tests/gerar_dados.py`, CA-83). Relógio do navegador **fixo em 28/11/2026 12:00** (`page.clock`) em todos os CAs desta seção. "Oráculo" = conta feita em Python sobre o CSV no próprio teste. Simulador: `navegador/` da oficina (Playwright) para tela e PDF; `excel-gerado/` (openpyxl) para o Excel; render do Excel pelo LibreOffice sem tela (CA-271). Cliente `Cliente Teste 01`, área `Área Teste` na Config quando o CA fala da capa.

**E1 — tela, cartões, partes e resumo**
- CA-200: com `vendas.csv` carregado, o Painel tem o botão `Gerar relatório` e nenhum botão ou título `Gerar Excel`.
- CA-201: `Gerar relatório` → aparece a região `Relatório` e o Painel some; capa com `Área Teste · Cliente Teste 01`, heading `Relatório vendas`, `Registros de <min> a <max>` (oráculo do campo Data), `Filtros: sem filtros`, `Gerado em: ` + `\d{2}/\d{2}/\d{4} \d{2}:\d{2}`, `Fonte: vendas (500 registros)`. `Voltar ao painel` → Painel de volta, com os mesmos filtros.
- CA-202: `O que tem neste relatório` lista, na ordem da tela, um link por parte visível (texto = heading da parte; o `href` aponta para um elemento que existe e contém esse heading) seguido da frase da 9c.3.
- CA-203: `Resumo executivo` tem entre 3 e 5 itens; o 1º é exatamente `O relatório tem 500 registros de <min> a <max>.`; o 2º traz `<a> estão em aberto (<p>% do total)` com a = Pendente + Em transporte (oráculo) e p com 1 casa.
- CA-204: `Números principais` (vendas): `Total de registros` = 500; `Soma de Valor` e `Mediana de Valor` = oráculo (2 casas); sob `Total de registros`, comparação R-157 de 11/2026 com 10/2026 com p = oráculo; `Concluídos` = % de Entregue + Cancelado (oráculo) e, com meta 90, `data-fora-meta="true"` e `faltam X para a meta`.
- CA-205: `Pendências por idade` (vendas): as 4 faixas com as contagens do oráculo (idade até 28/11/2026, R-164); soma das faixas = em aberto com data ≤ hoje; `Idade contada até 28/11/2026.`; clicar `Mais de 30 dias` abre a janela com essa contagem.
- CA-206: `Os 10 mais antigos em aberto` (vendas): 10 linhas, códigos e `Dias em aberto` iguais ao oráculo, do mais antigo ao mais novo.
- CA-207: cartão `Atrasados` (chamados, prazo padrão 24) = oráculo R-165; Config com prazo `720` → texto `(mais de 30 dias em aberto)` e contagem = novo oráculo.
- CA-208: chamados → `Entrou e saiu por mês` com `Mês`, `Entrou`, `Saiu`, `Saldo` = oráculo (Abertura e Conclusão); vendas → `Entrou por mês (Data)` só com `Mês` e `Entrou`.
- CA-209: vendas → `Valor: como os valores se distribuem`: `Média`, `Mediana`, `Mínimo`, `Máximo` = oráculo; frase `Metade dos registros ficou abaixo de <mediana>.`; `5 maiores` e `5 menores` com códigos e valores do oráculo (empate pelo código).
- CA-210: vendas → `Cliente: quem concentra`: 10 linhas ordenadas por soma de Valor, `% do total` e `% acumulado` = oráculo (1 casa; última linha 100,0%); frases `Os 3 primeiros de Cliente fazem <p>% do total.` e `Para chegar a 80% do total são <k> de 10.` = oráculo. chamados → `Categoria: quem concentra` com medida `Registros`.
- CA-211: `Filtros` → `Período` = `Mês` 10/2026 → capa `Registros de 01/10/2026 a 31/10/2026` e `Filtros: outubro/2026`; total = registros de outubro (oráculo); comparação com `09/2026`.
- CA-212: `Editar relatório` → em `Controles de Valor: como os valores se distribuem`, `Título` = `Valores do período`, `Observação` = `Observação de teste 01`; `Esconder` em `Pendências por idade`; `Descer` em `Números principais`; `Concluir edição` → o título novo aparece (e no índice), `Observação: Observação de teste 01` em itálico, `Pendências por idade` não aparece (nem no índice, nem em `Como ler este relatório`), `Números principais` vem depois de `O que o Raio X encontrou`. Recarregar a página e `Gerar relatório` → tudo igual.
- CA-213: `Forma` de `Cliente: quem concentra` = `Pizza` → barras com o aviso de pizza (10 grupos); `Região: quem concentra` = `Pizza` → `data-forma="pizza"` com 5 fatias.
- CA-214: editar `Texto do resumo executivo` para 2 linhas → o resumo mostra só essas 2; carregar `vendas_parte2.csv` (junta no mesmo relatório) → o texto fica e aparece R-163; `Voltar ao padrão` + confirmar → as frases automáticas voltam e as edições do CA-212 somem.
- CA-215: depois do CA-212, `Baixar backup` → o `.json` tem `relatorio.vendas`; `Apagar todos os dados` → `Restaurar backup` + `Substituir` → mesmo relatório editado. Backup com `relatorio` em formato errado → rejeitado inteiro, nada muda.
- CA-216: `Exportar arquivo` → janela `Exportar arquivo` com `Excel` marcado e `Formato`; `Exportar` → baixa arquivo com o nome do CA-98. Os CAs antigos que clicavam `Gerar Excel` (CA-01, CA-11, CA-12, CA-41 a CA-50, CA-98) passam a usar `Gerar relatório` → `Exportar arquivo` → `Exportar` (auxiliar do Testador) e continuam verdes até a E4.
- CA-217: offline depois do 1º carregamento, `Gerar relatório` e exportar Excel funcionam; em 390 px a tela Relatório não tem rolagem horizontal; nenhuma requisição a outra origem (CA-02).
- CA-218: CSV de teste com `<img src=x onerror=alert(1)>` no Cliente e na Observação → aparece como texto na capa/partes/observação; nenhum `dialog` de alerta.
- CA-219: CSV só com Código e um campo Texto (gerado no teste) → capa, resumo com 1 frase, `Números principais` só com `Total de registros`, `O que o Raio X encontrou`, `Registros`, `Como ler este relatório`; nenhum erro no console.
- CA-220: `Como ler este relatório` tem uma linha por parte visível, no formato R-156; `Registros` mostra 100 linhas e `Mostrando 100 de 500 registros. No Excel vão todos.`
- CA-221: 72 mil registros (CA-82) → `Gerar relatório` mostra a tela em ≤ 5 s.

**E2 — "O que o Raio X encontrou"**

`achados.csv` (`Código;Abertura;Conclusão;Grupo;Responsável;Valor;Situação`, 240 registros `A00001`…`A00240`, semente fixa) precisa ter, e o teste confere no CSV antes de conferir a tela: P1 exatamente 2 Aberturas em 2027; P2 exatamente 3 registros com Conclusão antes da Abertura; P3 exatamente 4 Valores > 3 × mediana; P4 Responsável vazio em 30% (72); P5 nenhum registro de 01/07/2026 a 24/07/2026, com registros nos dias 30/06 e 25/07; P6 registros `Aberto` que entraram em 08, 09 e 10/2026 em alta (ex.: 5, 9, 14); P7 `Aberto` com ≥ 20 registros em 09 e 10/2026 e parte de `Aberto` subindo ≥ 15 pontos de 09 para 10/2026; P8 ≥ 60% dos `Aberto` em `Grupo Teste 2`, que tem ≤ 25% do total; P9 ≥ 1 em aberto com Abertura antes de 28/10/2026; nenhum campo de texto livre parecido (0 repetidos). Situações: `Aberto`, `Concluido`. `sem_achados.csv`: 60 registros, um por dia de 01/09/2026 a 30/10/2026, todos `Concluido`, Conclusão 1 dia depois, Valor de 100 a 110, nenhum vazio.
- CA-230: `achados.csv` → `O que o Raio X encontrou` mostra 5 achados, nesta ordem de títulos: `Datas no futuro`, `Datas fora de ordem`, `Parados há muito tempo`, `Valores fora da curva em Valor`, `Pendências crescendo`.
- CA-231: `window.__achados("achados")` tem, nesta ordem de regra, A1, A2, A3, A4, A5, A6 (`Situação`), A7, A8 (entre eles `Campo vazio: Responsável` e `Dias sem registro`; nenhum `Campo vazio: Conclusão`, porque os vazios são de registros em aberto) e nenhum A9; as frases batem com o oráculo (ex.: A1 `2 registros com Abertura depois de hoje; a mais distante é dd/mm/2027.`).
- CA-232: cada achado tem `Por que apareceu: <texto da tabela 9c.7>`; `Ver os registros` de A4 abre a janela com os 4 códigos de P3 (e só eles); de A2, os 3 de P2.
- CA-233: `sem_achados.csv` → `O Raio X não encontrou nada fora do comum nestes registros.`; `window.__achados` vazio; o resumo não tem frase `Atenção:`.
- CA-234: `achados.csv` com `Período` = `Mês` 10/2026 → não há `Datas no futuro` (fora do filtro) e os outros achados seguem o oráculo dos registros de outubro.
- CA-235: o 4º item do resumo executivo de `achados.csv` é `Atenção: ` + a frase do 1º achado.
- CA-236: com vendas e chamados, nenhum achado cita valor, nome de campo ou palavra que não venha dos dados ou da tabela 9c.7 (busca dos termos de `tests/termos_proibidos.txt` = 0, CA-03).

**E3 — formas de gráfico novas**
- CA-250: em `Editar layout` (vendas e chamados com todos os indicadores), as opções de `Forma` são exatamente: `Por Cliente` → `Barras, Pizza, Rosca, Radar, Tabela`; `Valor por Região` → `Barras, Pizza, Rosca, Radar, Bolhas, Tabela`; `Evolução por mês (Data)` → `Barras, Linha, Área, Pizza, Rosca, Tabela`; `% por Situação` → `Barras, Pizza, Rosca, Radar, Velocímetro, Tabela`; `Tempo entre duas datas` → `Número, Velocímetro`; `Total de registros` → só `Número`.
- CA-251: `Por Região` em `Rosca` → `role="img"` com nome `Rosca: Por Região`, 5 pedaços com `<Região>: <n>` = oráculo, `500` no centro; clicar num pedaço abre a janela com n registros.
- CA-252: `Por Cliente` (10) em `Rosca` → barras + `Rosca com mais de 8 fatias: mostrando barras`.
- CA-253: `% por Situação` (vendas) em `Velocímetro` → texto `<p>% de 90%` com p = % Entregue + Cancelado (oráculo, 1 casa) e `faltam X para a meta`; meta vazia na Config → `<p>%`.
- CA-254: `Por Região` em `Radar` → 5 eixos com os nomes das regiões e 5 pontos `<Região>: <n>`; com filtro que deixa 2 regiões → barras + `Radar precisa de 3 a 10 grupos: mostrando barras`.
- CA-255: `Evolução por mês (Data)` em `Área` → um ponto por mês com `<mm/aaaa>: <n>` = oráculo.
- CA-256: `Valor por Cliente` em `Bolhas` → 10 bolhas com `<Cliente>: <n> registros, média <m>, total <s>` = oráculo; a ordem dos raios é a ordem das somas (área proporcional); clicar abre a janela com n registros; com filtro de 1 cliente → barras + aviso de bolhas.
- CA-257: forma escolhida no Painel volta igual depois de recarregar e de backup/restaurar (`Substituir`); a planilha `Painel` do Excel continua com a tabela do bloco.
- CA-258: no Relatório, `Forma` de `Região: quem concentra` oferece as mesmas opções de `Por Região`; `Rosca` funciona igual ao CA-251.
- CA-259: com teclado, `Tab` chega a um pedaço do gráfico e `Enter` abre a janela; em 390 px nenhum gráfico novo causa rolagem horizontal.

**E4 — Excel visual (F-76)**
- CA-260: vendas, `Exportar` Excel → planilhas `Capa`, `Como ler este relatório`, `Resumo`, `Análises`, (`Painel`, com escolha confirmada), `vendas`, nessa ordem.
- CA-261: `Capa`: A1 = `Área Teste · Cliente Teste 01`; A2 = `Relatório vendas`, fonte ≥ 18, negrito, cor de fundo `0F2A4A`, altura da linha ≥ 30; nenhuma coluna totalmente vazia antes da última coluna usada; largura da coluna A entre 14 e 40; `Período`, `Filtros`, `Gerado em`, `Fonte` na coluna A com o valor à direita; `O que tem neste arquivo` com uma linha por planilha, cada uma com link interno `#'<planilha>'!A1` para planilha que existe.
- CA-262: em `Resumo`, `Análises` e `Painel`: A1 contém `vendas · Área Teste · Cliente Teste 01`, A2 = nome da planilha com fundo `0F2A4A` e letra branca, A3 itálico começando com `Período: `; nenhum conteúdo antes da linha 5. (Substitui A1/A2 de R-81 nos CAs 41, 45 e 50, que o Testador ajusta.)
- CA-263: `Resumo` tem as frases do resumo da tela (mesmo texto e ordem), os cartões de `Números principais` (rótulo/valor iguais à tela; número com fonte ≥ 14 e negrito; fundo `EEF3FB`; borda de cima na cor `1F6FEB`) e os achados (título e frase). `Análises` tem as partes visíveis com os mesmos títulos (editados, se houver), observação em itálico logo abaixo do título e as tabelas iguais à tela (`Cliente: quem concentra` linha a linha).
- CA-264: nenhuma célula de nenhuma planilha contém `█`; cada coluna `Barra` tem números (os n da regra antiga) e uma regra `dataBar` de formatação condicional cobrindo exatamente esse intervalo; cabeçalhos de tabela com fundo `1F6FEB`; linhas de dados zebradas; planilhas de registros com `autoFilter` no cabeçalho; todas as planilhas com `tabColor`.
- CA-265: `Como ler este relatório`: largura da coluna A = 110 e `wrap_text` verdadeiro em toda célula com texto.
- CA-266: planilha `vendas`: células de `Data` são datas com formato `dd/mm/yyyy` (nenhuma mostra `00:00`); planilha de `chamados`: `Abertura` com `dd/mm/yyyy hh:mm`.
- CA-267: planilha `vendas`: `Valor` é número com formato `#,##0.00` em todas as linhas (o valor `323,9` do CSV vira o número 323.9, exibido `323,90`).
- CA-268: parte escondida no relatório (CA-212) não aparece em `Análises` nem em `Como ler este relatório`; `Do seu painel` escondida → não há planilha `Painel`.
- CA-269: em todos os arquivos desta etapa, nenhuma fórmula (`data_type == 'f'`), nenhum `xl/vbaProject.bin`, nenhum gráfico (`xl/charts/`), e todo link começa com `#` (CA-47 e simulador `excel-gerado/`).
- CA-270: `Tudo numa planilha` com vendas e chamados → `Resumo - vendas`, `Análises - vendas`, `Resumo - chamados`, `Análises - chamados` e o resto como o CA-45.
- CA-271: o `.xlsx` convertido em PDF pelo LibreOffice sem tela (`soffice --headless --convert-to pdf`) tem, na 1ª página, o título `Relatório vendas` inteiro (texto extraído) e nenhuma página em branco entre a capa e o resumo. Fica no roteiro de homologação a olhada humana no Excel real (o LibreOffice não imita 100% barras de dados).

**E5 — PDF**
- CA-280: `Exportar arquivo` → `PDF` → `Exportar` → `window.print` chamado 1 vez (o teste troca por um espião), com o título do documento `RaioX_VENDAS_<AAAA-MM-DD>` durante a chamada; depois volta o título normal e aparece `Na janela que abrir, escolha “Salvar como PDF”.`; o `Formato` não aparece com `PDF`.
- CA-281: `page.pdf()` com mídia de impressão, A4 → a 1ª página tem só a capa; o texto do PDF tem todos os headings das partes visíveis e nenhum de `Voltar ao painel`, `Editar relatório`, `Exportar arquivo`, `Subir`, nem o heading de parte escondida.
- CA-282: toda página do PDF tem o rodapé com `Gerado em:` e `Fonte: vendas (500 registros)`.
- CA-283: os rótulos dos gráficos (ex.: nomes das regiões em `Região: quem concentra`) estão no texto do PDF (gráfico em vetor, não imagem).
- CA-284: offline, o PDF sai igual (CA-281 com contexto offline).

**Fumaça.** Não há encaixe nem serviço real (regra do projeto); não há teste de fumaça. Nada desta seção depende de estrela; `docs/caminho-das-estrelas.md` não muda.

### 9c.12 Etapas de construção (uma por tarefa)

Cada etapa: teste que falha → código → suíte inteira verde → Revisor → `main` → POP. Cada uma deixa o app funcionando sozinha.

| Etapa | O que entra | CAs | Depende de | POP |
|---|---|---|---|---|
| **E1** Tela + cartões + resumo | R-140 a R-158, R-163 a R-169; capa, índice, resumo executivo, números principais com comparação e meta, partes por tipo (pendências, mais antigos, entrou/saiu, distribuição, quem concentra, tempo, do seu painel, registros, como ler) com as formas já existentes; edição e guarda; `Exportar arquivo` só com Excel (gera o Excel de hoje) | CA-200 a CA-221 | — | P-g novo ("Gerar relatório"), ⚖️ D-64 a D-71, D-74 a D-76, D-82, D-83 |
| **E2** O que o Raio X encontrou | 9c.7, `window.__achados`, frase 4 do resumo, `achados.csv` e `sem_achados.csv` no gerador | CA-230 a CA-236 | E1 | ⚖️ D-72, D-73 |
| **E3** Gráficos novos | R-160 a R-162, 9c.10 no Painel e no Relatório | CA-250 a CA-259 | E1 (CA-258) | P-w (Forma), ⚖️ D-77 |
| **E4** Excel visual | 9c.8 (F-76 inteira, itens 11 a 15), planilhas `Resumo` e `Análises`, ajuste dos CAs antigos 41/45/50 | CA-260 a CA-271 | E1 (E2 para os achados no `Resumo`) | P-g, ⚖️ D-78 a D-80, D-84 |
| **E5** PDF | 9c.9, opção `PDF` em R-159 | CA-280 a CA-284 | E1 (E3 opcional) | P-g, ⚖️ D-81 |

Se a E1 ficar grande para uma tarefa, o coordenador pode partir em **E1a** (tela, capa, índice, resumo, números principais, exportar, edição: CA-200 a CA-204, CA-211 a CA-221) e **E1b** (partes por tipo de dado: CA-205 a CA-210).

### 9c.13 Decisões provisórias (⚖️, vão ao quadro do POP)

- **D-64** O relatório é o do relatório aberto no Painel, com os mesmos filtros; o Excel continua com `Formato` e pode levar todos os relatórios, cada um com o seu relatório (editado ou padrão). Motivo: o Painel mostra um relatório por vez.
- **D-65** Idade contada até hoje (relógio do aparelho), não até a data mais recente dos dados (diferente de D-10), porque o Galindo pediu "a idade agora". Data no futuro sai das faixas e vira achado.
- **D-66** Atrasado usa o prazo que já existe na Config (`prazoH`, padrão 24 h), sem campo novo; mostrado em dias quando o prazo é múltiplo de 24 e ≥ 48 h.
- **D-67** Período anterior: mês anterior / mesmo número de dias antes / último mês com registros contra o anterior (com `Tudo`). Setas sem cor de bom ou ruim (o app não sabe se subir é bom).
- **D-68** A meta da Config vale também para `Concluídos` (% que não está em aberto), além do `Dentro de <prazo>`.
- **D-69** Até 3 campos Grupo em `quem concentra`; medida = soma do 1º Número (senão contagem); frase dos 3 primeiros + quantos para chegar a 80%.
- **D-70** Aviso de média puxada quando média > 1,2× ou < 0,8× a mediana.
- **D-71** Resumo executivo: ordem fixa, até 5 frases; com poucos dados pode ter menos de 3.
- **D-72** Limiares dos achados (tabela 9c.7: 3× mediana, 30 dias, 3 meses, 15 pontos com ≥ 20 registros, 50% e 2×, 20% vazio, 14 dias, 1 par), a prioridade e o corte de 2 por regra e 5 no total.
- **D-73** Achados usam os registros filtrados (com filtro de mês, data no futuro não aparece).
- **D-74** Edita-se texto, título, observação, ordem, esconder e forma; número não se edita. Texto editado não é refeito quando os dados mudam, mas ganha o aviso R-163.
- **D-75** `Do seu painel` é uma parte só (a ordem interna é a do Editar layout); escondê-la tira as planilhas de painel do Excel.
- **D-76** Tela e PDF mostram os 100 primeiros registros; o Excel leva todos.
- **D-77** Formas permitidas da 9c.10; o velocímetro de `% por <andamento>` mostra `Concluídos`.
- **D-78** No Excel, a barra em `█` vira barra de dados (formatação condicional, não é fórmula); muda D-12 só nesse ponto (continua sem gráfico nativo, fórmula ou macro).
- **D-79** Nas planilhas, A1/A2/A3 passam a ser linha pequena, faixa de título e linha em itálico (substitui R-81: A1 `Painel`, A2 `Relatório: <conjunto>`).
- **D-80** Planilhas novas `Resumo` e `Análises` entre `Como ler este relatório` e as de painel; `Como ler este relatório` passa a existir sempre.
- **D-81** PDF pela impressão do navegador ("Salvar como PDF"), sem biblioteca nova; arquivo PDF baixado direto fica para a V2.
- **D-82** Título padrão `Relatório <relatório>` (a pessoa troca em `Título do relatório`).
- **D-83** `Fonte` = nome do relatório e quantidade de registros (o app não guarda o nome do arquivo de origem).
- **D-84** Cores do Excel e do relatório: `#0F2A4A` (faixa), `#1F6FEB` (destaque), `#EEF3FB`, `#F4F6FB`, `#DFE4EF`, `#5B6683`.

### 9c.14 Perguntas abertas (PERGUNTAR AO GALINDO, nenhuma trava a linha)

- **P-07** Atrasado pelo prazo de horas da Config (D-66) ou um prazo próprio em dias para pendências? Provisório: o mesmo prazo.
- **P-08** A meta vale para `Concluídos` (D-68)? Provisório: sim.
- **P-09** PDF pela janela de impressão do navegador (D-81) serve, ou precisa baixar o arquivo direto? Provisório: impressão.
- **P-10** Os limiares dos achados (D-72) estão bons para o primeiro teste? Provisório: os da tabela 9c.7.
- **P-11** Comparação com `Tudo` usa o último mês com registros, mesmo que incompleto (D-67)? Provisório: sim, e o texto diz o mês.

### 9c.15 Fontes da pesquisa (relatório gerencial, pendências por idade, concentração)

A pesquisa web não estava disponível na sessão do Especificador (sem ferramenta de busca); as referências abaixo são conhecidas e públicas, citadas de memória. **O Revisor confere se cada link abre** antes de fechar a E1 e troca o que tiver mudado.
- Resumo executivo no início, conclusões primeiro: Wikipedia, "Executive summary" — https://en.wikipedia.org/wiki/Executive_summary
- Notação de relatório gerencial, comparação com período anterior e meta: IBCS (International Business Communication Standards) — https://www.ibcs.com/standards/
- Painéis e relatórios para leitura rápida; crítica ao velocímetro e alternativa do "bullet graph" (por isso o velocímetro é só uma forma, com a meta marcada): Stephen Few, Perceptual Edge — https://www.perceptualedge.com/articles/misc/Bullet_Graph_Design_Spec.pdf
- Idade das pendências por faixas (relatório de "aging"): Investopedia, "Aging Schedule" — https://www.investopedia.com/terms/a/agingschedule.asp
- Idade do item em andamento como medida de fluxo (pendências paradas): The Kanban Guide, "Work Item Age" — https://kanbanguides.org/english/
- Concentração (80/20) e gráfico com % acumulado: ASQ, "What is a Pareto Chart?" — https://asq.org/quality-resources/pareto ; Wikipedia, "Pareto chart" — https://en.wikipedia.org/wiki/Pareto_chart
- Média e mediana juntas (a mediana resiste a valores extremos): Wikipedia, "Median" — https://en.wikipedia.org/wiki/Median
- Valores fora da curva (regra simples baseada na mediana, sem estatística avançada): NIST/SEMATECH e-Handbook, "What are outliers in the data?" — https://www.itl.nist.gov/div898/handbook/prc/section1/prc16.htm

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
- Pedido escrito, Editar layout e OCR na macro Excel (o Excel 2016 não comporta bem).

## 13. Perguntas abertas (PERGUNTAR AO GALINDO) — com decisão provisória
- **P-01** ✅ Decidido (Galindo, 25/11/2026 14h28 e 14h34): a macro Excel fica como **versão para baixar e usar no PC**, com link no app e no README, com a mesma estrutura genérica do app no que couber no Excel 2016 (seção 9b).
- **P-02** ✅ Decidido (Galindo, 25/11/2026 14h25): repositório `gsi-solucoes/raio-x-do-relatorio`, link https://gsi-solucoes.github.io/raio-x-do-relatorio/.
- **P-03** ✅ Decidido (Galindo, 25/11/2026 14h43): meta configurável por indicador percentual, padrão 90%.
- **P-04** ✅ Decidido (Galindo, 25/11/2026 14h34): nada do caso de origem no produto; sem modelo pronto com regras de um ramo. Frases padrão começam vazias e cada cliente cadastra as suas.
- **P-05** ✅ Decidido (Galindo, 25/11/2026 14h43): etapas na ordem 1 → 7.
- **P-06** ⏳ Provisória (coordenador, 26/11/2026; confirmar com o Galindo na F-59, não trava nada): ao restaurar um backup com **"Somar"**, a lista de "Meus indicadores" de cada relatório **junta** a atual com a do backup, sem repetir, até o limite de 50 (o que passar fica de fora com aviso, como nos sinônimos). Motivo: não perde o que o usuário já escolheu. Implementado na F-60 (26/11/2026), com teste.
