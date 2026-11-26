# Raio X do Relatório — Especificação v1.7

Agente 2 (Especificador) · 25/11/2026 · base: `docs/00_concepcao/concepcao.md` (portão 1 aprovado pelo Galindo em 25/11/2026 14h18)

**Histórico de versões**
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
|### 0.8 Nomes e regras — etapa 7a: planilhas, JSON, XML e zip (v1.7, 26/11/2026, F-58)

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

---|---|
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

## 9b. Versão Excel para baixar (macro)

- Mesma estrutura do app, sem conteúdo de nenhum caso: importar CSV/XLSX (ou .zip), perguntar o que é cada coluna (uma vez por formato), escolher indicadores do catálogo da etapa 2, painel com segmentação por período e categoria, botão "Gerar relatório" com capa.
- CA-110: a macro importa `tests/dados/vendas.csv`, pergunta as colunas e gera o mesmo Total e Por cliente que o app (conferência manual no Excel 2016, roteiro em `docs/03_homologacao/roteiro-excel.md`).
- CA-111: `grep -i` dos termos do CA-03 no `.bas` = 0.

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
