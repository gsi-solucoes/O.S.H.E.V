# POP — Como o Raio X do Relatório funciona

*Procedimento Operacional Padrão · primeiro item da homologação (Galindo, 26/11/2026)*

Este POP diz, passo a passo, **como o programa funciona hoje**: o que a pessoa faz, o que o programa faz em resposta,
as regras e os limites. Onde a fábrica tomou uma **decisão importante sem o Galindo** (provisória ou não), aparece o selo ⚖️ com o número.

**Na homologação:** o Galindo lê o POP antes de testar e marca cada ⚖️ no quadro do fim: **Fica** ou **Muda (como)**.
Cada "Muda" vira tarefa com teste. A fábrica atualiza o POP a cada etapa publicada.

## Procedimentos
Ordem de uso: abrir e configurar (P-a, P-b), carregar e dizer o que é cada coluna (P-c), escolher o que acompanhar e entender o painel (P-d), usar o painel e os filtros (P-e), pedir por escrito (P-f), gerar o Excel (P-g), backup e apagar (P-x, P-h); depois os recursos das etapas 5 a 7 (P-y em diante).
*P-a a P-h e P-x conferidos no app em 26/11/2026 (navegador da oficina, `vendas.csv` de teste), F-61.*

### P-a. Abrir, instalar e usar sem internet
**Para que serve:** usar o Raio X no celular ou no computador como um aplicativo, mesmo sem internet.

| Você faz | O programa faz |
|---|---|
| Abre o link https://gsi-solucoes.github.io/raio-x-do-relatorio/ | Mostra "Raio X do Relatório", o botão **Carregar dados** e as abas **Painel** e **Config** |
| Escolhe "Adicionar à tela inicial" (celular) ou "Instalar" (computador) no navegador | Vira um ícone, como um app |
| Abre de novo sem internet | Funciona igual (tudo foi guardado na 1ª abertura); só a leitura de foto precisa de internet uma vez (P-t) |
| Abre com internet depois de uma atualização | Baixa a versão nova por trás; na próxima abertura aparece "Versão nova instalada" |

**Regras e limites:** nada sai do aparelho: sem login, sem servidor, sem envio de dados. Os dados ficam só naquele navegador daquele aparelho; para levar a outro, use o backup (P-x).

### P-b. Pôr o nome do cliente, a área e o logo (Config)
**Para que serve:** o relatório sair com a cara do cliente, sem nada fixo no programa.

| Você faz | O programa faz |
|---|---|
| Abre **Config** (em quatro seções com título e linha: **Aparência**, **Regras dos números**, **Pedido escrito e cálculos**, **Dados deste aparelho** ⚖️ nomes provisórios) → **Empresa e logo** e escreve **Cliente** e **Área** | Salva sozinho a cada letra, sem botão Salvar ⚖️ D-02; o topo passa a mostrar "Raio X do Relatório · Área · Cliente" |
| Toca em **Escolher logo** e escolhe uma imagem | Reduz a imagem e mostra no topo, na impressão e na capa do Excel ⚖️ D-03 |
| Toca em **Apagar logo** | Tira o logo do topo e da capa |
| Em **Metas**, muda a meta (padrão 90%) e o prazo "dentro do prazo" (padrão 24 h) | O bloco **Tempo entre duas datas** (só ele) mostra "Dentro de 24 h: X%" e, embaixo, "Acima da meta de 90%" ou "faltam X pontos para a meta de 90%"; o prazo novo muda o "dentro de". Sem esse bloco, a meta não aparece. Meta vazia: some a frase da meta |

**Linguagem simples (F-82):** o **Seu painel** e o ⓘ de cada bloco falam em palavras do dia a dia (ex.: "Quantas linhas o arquivo tem. Período: de 03/01/2026 a 27/11/2026. Sem filtros."; "valor do meio (metade das linhas fica abaixo dele)" no lugar de mediana). Só as contas suas e os indicadores pedidos por escrito mostram "Conta: …". A janela de registros também tem ⓘ (o que fazem _, □ e ×, e os botões Limpar seleção, Imprimir e Copiar).
**Regras e limites:** logo até 2 MB (vira imagem de até 240 px). Config fica só neste aparelho e entra no backup.
**Ajuda ⓘ (F-78):** ao lado de cada caixa da Config, dos botões do painel, dos filtros, da faixa Total/Mais antigo/Mais novo, das telas "Esta coluna é o quê?", "Conferir leitura" e "Seu painel" e de cada bloco do painel há um **ⓘ**. Toque (celular) ou passe o mouse (computador): abre uma caixinha com **O que é**, **Como faz** e **Exemplo**; toque fora ou **Esc** fecha. Nomes novos: "Meus cálculos" (antes Contas personalizadas), "Apelidos para o pedido escrito" (antes Sinônimos), "Palavras que significam a mesma coisa (para achar repetidos)" (antes Palavras parecidas). O cartão "Versão Excel para o PC" ficou escondido até a versão 2 (a macro). O traço solto ao lado de "Escolher logo" sumiu.

### P-c. Carregar um relatório e dizer o que é cada coluna
*(F-79: o botão agora se chama **Carregar dados**; o texto "Nenhum arquivo escolhido" do navegador não aparece mais; o campo Número é mostrado sempre com 2 casas e milhar, ex.: 1.841,60; o card **Gerar Excel** fica antes da lista Registros; o link "Baixar versão Excel para o PC" do rodapé ficou escondido até a versão 2; sem logo não sobra espaço no topo.)*
**Para que serve:** trazer os registros de um arquivo extraído de qualquer sistema (aqui, CSV; outros formatos em P-v, P-u e P-t).

| Você faz | O programa faz |
|---|---|
| Toca em **Carregar dados** e escolhe um ou vários arquivos | Acha a linha do cabeçalho sozinho e lê cada arquivo no aparelho |
| (formato que ele nunca viu) | Abre **Esta coluna é o quê?** em forma de **prévia** (F-80): as colunas lado a lado com as primeiras linhas reais do arquivo. No alto de cada coluna: **Aparece?** (Sim; Não = a coluna não é guardada), **Nome** (o título do arquivo, ou "Campo 1", "Campo 2"… se não houver; dá para trocar) e **Tipo** (com ⓘ): **Número** (para somar ou fazer média), **Data**, **Grupo** (valores que se repetem, para separar: região, cliente, setor) ou **Texto** (escrita livre) ⚖️ D-16. Embaixo, duas perguntas: **Qual coluna identifica cada linha?** (obrigatória) e **Qual coluna mostra o andamento?** (opcional). Mostra também o **Nome do relatório** |
| Confere a prévia, responde as duas perguntas e toca em **Confirmar** | Guarda os registros e lembra o formato: da próxima vez, o mesmo conjunto de colunas não pergunta de novo. **Linhas totalmente em branco** saem sozinhas, com o aviso "N linhas em branco deixadas de fora" |
| Carrega o mesmo arquivo outra vez (ou uma versão nova) | Não duplica: registro com o mesmo código é atualizado campo a campo; valor vazio no arquivo novo não apaga o que já havia ⚖️ D-06. No topo: "vendas: 500 lidos, 0 novos" |
| Carrega outro arquivo com o mesmo campo código e códigos que já existem | Junta no relatório que já tem esses códigos, somando os campos novos ⚖️ D-05 |
| Em **Config → Formatos lembrados**, toca em **Esquecer** | Na próxima carga desse formato, pergunta de novo |
| (cabeçalho errado) Toca em **O cabeçalho está em outra linha** e toca na linha dos títulos (ou em **O arquivo não tem cabeçalho**: os nomes viram Campo 1, 2, 3…) | A prévia se refaz com a linha escolhida; o programa lembra a escolha para esse formato |
| Em **Config → Formatos lembrados**, toca em **Editar** | Reabre a mesma tela (os nomes não mudam; dá para trocar Aparece? e Tipo) |
| Toca em **Apagar tudo e carregar de novo** (ao lado de Carregar dados) | O mesmo da Config: pergunta "Apagar mesmo?" antes de limpar |

**Regras e limites:** linha sem código é deixada de fora, sem aviso ⚖️ D-04. Categoria é sugerida quando a coluna tem até 30 valores diferentes e muita repetição; Situação, quando o nome lembra "situação", "status" ou "estado" ⚖️ D-08. O arquivo original não é guardado, só os registros. Cada arquivo até 50 MB.

### P-d. Escolher "O que você quer acompanhar?" e ler "Seu painel"
**Para que serve:** montar o painel só com o que interessa, a partir do que os dados permitem calcular.

| Você faz | O programa faz |
|---|---|
| (logo depois de carregar um relatório novo) | Abre sozinho **O que você quer acompanhar?**: só os indicadores que dá para calcular com os seus campos, cada um com o resultado real como exemplo (ex.: "Total de registros — 500 registros", "% por Situação — Cancelado: 28,4%") |
| Marca os que quer (nada vem marcado ⚖️ D-07) e toca em **Confirmar** | Cria um bloco por indicador: primeiro os números, depois os gráficos, a lista **Registros** sempre no fim; e abre **Seu painel** |
| Confirma sem marcar nada | "Marque pelo menos um indicador." |
| Toca em **Cancelar** | Mantém o painel padrão (todos os blocos automáticos) e não salva nada |
| Lê **Seu painel** (ou toca depois em **Entender este painel**) | Uma linha por bloco: o que mostra, a conta em palavras ("soma do campo Valor, separada por Região"), os campos, o período e os filtros do momento |
| Toca em **O que acompanhar** | Reabre a lista com as marcas atuais, para tirar ou pôr indicadores |

**Catálogo possível:** Total de registros; Por <categoria>; <Número> (soma, média e mediana); <Número> por <categoria>; Evolução por mês; Tempo entre duas datas (só com 2 datas); % por <situação>; Sem valor em <campo>; Mais antigos em aberto (data + situação). "Em aberto" é a situação que não começa com conclu-, finaliz-, encerr-, fechad-, entreg-, cancel-, resolvid- ou pag- ⚖️ D-09.
**Regras e limites:** a escolha vale por relatório, fica guardada e entra no backup. Gráfico por categoria mostra os 10 maiores e junta o resto em "Outros". Acima dos blocos fica sempre a faixa com Total, Mais antigo e Mais novo ⚖️ D-15.

### P-e. Usar o painel: filtros e números clicáveis
**Para que serve:** olhar um recorte (um mês, uma região) e ver os registros por trás de qualquer número.

| Você faz | O programa faz |
|---|---|
| Abre **Filtros** e escolhe **Relatório**, **Período** (Tudo, Mês ou De–até), **Campo de data**, **Campo categoria** e **Valor**, ou escreve em **Buscar texto** | Recalcula todos os blocos, o "Seu painel" e o Excel com o recorte |
| Toca em qualquer número ou barra, em **Mais antigo** / **Mais novo** (registros daquele dia) ou no **título** de um bloco (ele traz um ›: todos os registros do bloco) | Abre uma janela com os registros por trás dele: dá para arrastar, **Minimizar**, **Maximizar (□)** e voltar, filtrar, **Imprimir**, **Copiar** ("Copiado.") e **Limpar seleção** |
| Na janela, toca nos botões de uma fileira (ex.: Região "Centro") | As outras fileiras se ajustam, como a segmentação do Excel: a contagem passa a valer só para a seleção e o que ficou com 0 aparece apagado. Cada fileira mostra os 8 maiores e **mais…** mostra todos; os selecionados não somem |
| Chega ao fim da lista da janela | **Mostrar mais** traz mais 100 registros |

**Regras e limites:** a lista Registros mostra os 50 mais novos primeiro; **Mostrar mais** traz mais 100 de cada vez; o Excel leva todos.

### P-f. Pedir um indicador por escrito ("É isso?")
**Para que serve:** criar um bloco que não está no catálogo, escrevendo como se fala.

| Você faz | O programa faz |
|---|---|
| Escreve em **Peça um indicador** (ex.: "soma do valor por cliente em outubro") e toca em **Pedir** (ou Enter) | Mostra **Entendi assim: Soma de Valor · por Cliente · outubro/2026**, a **Prévia** já calculada e pergunta **É isso?** |
| Toca em **Sim** | O bloco entra em **Meus indicadores** no painel, no "Seu painel" e no Excel; aviso "Indicador adicionado ao painel." |
| Toca em **Não** | Aparecem os botões **Medida**, **Campo**, **Agrupar por**, **Filtro**, **Período**; cada um abre as opções reais dos dados; **Aplicar** atualiza o resumo e a prévia |
| Escreve algo que ele não entende (ex.: "bom dia") | "não entendi: bom dia" e **Tente um destes:** com 3 frases montadas com os seus campos (ex.: "soma de Valor por Cliente"); tocar numa já pede. Nada entra no painel |
| Em **Config → Sinônimos**, cadastra um **Apelido** e o que ele **Significa** (ex.: "fat" = Valor) | Passa a entender "fat por cliente" como soma de Valor por cliente |

**Entende:** medida (quantidade, soma, média, mediana, mínimo, máximo, percentual), campo, agrupar por (campo ou mês), filtros por valor e período (mês pelo nome, ano, "este mês", "mês passado", "este ano", "de dd/mm a dd/mm", "últimos N dias").
**Regras e limites:** nunca chuta: o que não entendeu aparece como "não entendi: <trecho>". Aceita erro de digitação, sem acento e no plural, com semelhança de 80% ou mais ⚖️ D-11. "Este mês", "mês passado" e "últimos N dias" contam a partir da data mais recente dos registros, não do relógio ⚖️ D-10; "outubro" sem ano é o outubro mais recente dos dados. Até 50 indicadores pedidos por relatório; até 200 sinônimos.

### P-g. Gerar o Excel
**Para que serve:** levar o painel da tela para uma planilha, para guardar, imprimir ou mandar.

| Você faz | O programa faz |
|---|---|
| No fim do Painel, em **Gerar Excel**, escolhe o **Formato**: Uma planilha por relatório, Tudo numa planilha ou Arquivos separados | — |
| Toca em **Gerar Excel** | Baixa `RaioX_<RELATÓRIO>_<data>.xlsx` com: **Capa** (título, área, cliente, logo, total, mais antigo e mais novo, relatório, período, filtros e "Gerado em"), **Como ler este relatório** (o texto do "Seu painel", só se houver escolha confirmada), **Painel** (os blocos na ordem da tela, depois Meus indicadores, depois todos os registros do recorte) e a planilha de registros |

**Regras e limites:** o Excel mostra os mesmos números da tela com os mesmos filtros. Só valores: nenhuma fórmula, nenhuma macro e nenhum gráfico nativo; o gráfico vira tabela Categoria / Valor / Barra, com a barra desenhada em texto (█) ⚖️ D-12. Contagens como número inteiro, somas e médias com 2 casas, percentuais e durações como texto igual à tela. Com abas no painel (P-w), sai uma planilha por aba.

### P-x. Fazer backup e restaurar
**Para que serve:** guardar os dados e as escolhas e trazê-los de volta (outro aparelho ou depois de apagar).

**Passo a passo**
| Você faz | O programa faz |
|---|---|
| Abre **Config → Dados deste aparelho** e toca em **Baixar backup** | Baixa `historico_RaioX_<data>.json` com tudo: registros, Config, formatos lembrados, escolhas do painel, Meus indicadores, sinônimos, contas e layout |
| Toca em **Restaurar backup** e escolhe o arquivo | Confere se é mesmo um backup do Raio X (se não for: "Esse arquivo não é um backup do Raio X… Nada foi alterado.") e pergunta: "O backup tem N registros. Somar aos dados atuais ou substituir tudo?" |
| Toca em **Substituir** | Apaga tudo do aparelho e põe o backup no lugar, Config inclusive |
| Toca em **Somar** | Junta os registros do backup aos atuais (mesmo código: campo a campo, como em P-c). Em "Meus indicadores", junta a lista atual com a do backup, sem repetir, até 50; o que passar fica de fora com aviso ⚖️ D-01. Contas e sinônimos também se juntam. A escolha de "O que acompanhar" e os formatos lembrados do backup valem por cima dos atuais; a Config atual fica ⚖️ D-14 |
| Toca em **Cancelar** | Nada muda |

**Regras e limites:** backup até 200 MB. Ao final: "Backup restaurado.". Layout: ver ⚖️ D-32.

### P-h. Apagar todos os dados
**Para que serve:** limpar o aparelho (troca de dono, teste, dados errados).

| Você faz | O programa faz |
|---|---|
| Abre **Config → Dados deste aparelho** e toca em **Apagar todos os dados** | Pergunta: "Isso apaga os N registros deste aparelho. Baixe um backup antes se quiser guardar. Apagar mesmo?" |
| Toca em **Apagar** | Apaga registros, escolhas do painel, Meus indicadores, contas e layouts; mostra "Dados apagados." |

**Regras e limites:** **ficam** a Config (cliente, área, logo, metas), os formatos lembrados e os sinônimos ⚖️ D-13: assim o próximo relatório do mesmo sistema entra sem perguntar de novo. Não tem volta sem backup.

### P-y. Criar uma conta personalizada
**Para que serve:** ter no painel um número que é uma conta feita com os campos do relatório (ex.: ticket médio = soma do valor ÷ quantidade de registros).

**Passo a passo**
| Você faz | O programa faz |
|---|---|
| Abre **Config → Contas personalizadas** (com um relatório carregado) | Mostra as contas já salvas desse relatório |
| Escreve o **Nome da conta** e a **Fórmula** (`+ - * /`, parênteses, `quantidade()`, `soma(campo)`, `media(campo)`, `mediana(campo)`, `dias(data1, data2)`, `distintos(campo)`; filtro opcional `situação = cancelado`) | Mostra na hora a **Prévia da conta** com os dados; se há erro, diz qual (ex.: "campo 'valr' não existe; você quis dizer 'valor'?") e não deixa salvar |
| Toca em **Salvar conta** | Guarda a conta; ela aparece em **O que acompanhar** e no **Seu painel**. Nome repetido troca a conta antiga ⚖️ D-23 |
| Pede por escrito "ticket médio por região" | Entende a conta pelo nome e calcula a fórmula em cada região |
| Toca em **Remover** | Apaga a conta |

**Regras e limites:** até 50 contas por relatório; nome até 60 e fórmula até 300 caracteres. A fórmula nunca executa código. Divisão por zero ou sem dados mostra "sem dados". `dias` é a média de dias entre as duas datas ⚖️ D-20. Contas valem só para o relatório em que foram criadas ⚖️ D-23. Entram no backup.

### P-z. Usar a versão Excel (macro) e ver os indicadores
*Fica para a versão 2.0 (Galindo, 26/11/2026): não entra na homologação atual.*

**Para que serve:** quem prefere o Excel no PC importa os arquivos, vê o painel e gera o relatório, com a mesma estrutura do app.

| Você faz | O programa faz |
|---|---|
| Importa os arquivos e diz o que é cada coluna | Junta os registros pelo código |
| No Painel escolhe período, campo de data, campo de categoria, categoria e **campo número** | Mostra o total, a contagem por categoria e a tabela **Indicadores** (soma, média, mediana, mínimo, máximo, sem valor, soma por categoria, registros por mês) |
| Clica em **Gerar relatório** | Cria um arquivo novo com Capa, Resumo, Indicadores e Registros, só com valores ⚖️ D-24 |

**Regras e limites:** ficam de fora da versão Excel: pedido escrito, contas personalizadas, Editar layout, leitura de PDF e imagem, % por situação e tempo entre duas datas (Excel 2016 não comporta bem). O app tem tudo isso.

### P-w. Editar o layout do painel
**Para que serve:** organizar os blocos do painel do seu jeito (ordem, abas, tamanho, forma) sem mexer nos dados. Vale por relatório, entra no backup e no Excel.

**Como é a edição (F-79):** ao tocar em **Editar layout** aparece no topo uma faixa que explica ("Arraste um bloco… Toque nele…"; some com **Entendi, não mostrar de novo**). Cada bloco tem uma alça **⠿**. **Tocar** num bloco o seleciona (borda azul grossa) e só ele mostra as opções (Subir, Descer, Esconder, Duplicar, Mover para…, Tamanho, Forma). **Arrastar** deixa o bloco meio apagado, uma sombra azul mostra onde ele cai, a aba sob o dedo acende e o bloco solto pisca. Em edição, tocar no título não abre a janela de registros.

| Você faz | O programa faz |
|---|---|
| Toca em **Editar layout** (só aparece quando há blocos escolhidos em "O que acompanhar") | Mostra a barra de abas e os controles em cada bloco; o botão vira **Concluir edição** |
| **Subir** / **Descer** (ou arrasta) um bloco | Muda a ordem na tela, no "Seu painel" e no Excel |
| **Nova aba**, **Renomear aba**, **Aba à esquerda/direita** | Cria e organiza abas (nome até 30 letras, sem repetir) |
| **Mover para…** outra aba | O bloco passa para a aba escolhida |
| **Apagar aba** e confirma | Os blocos dela vão para o fim da primeira aba; a pergunta diz "O bloco dela vai…" (1 bloco) ou "Os N blocos dela vão…" ⚖️ D-35 |
| **Tamanho** (Pequeno, Médio, Grande) | Muda a largura na tela; o Excel não muda ⚖️ D-33 |
| **Esconder** / **Mostrar** | Bloco escondido some da tela, do "Seu painel" e do Excel |
| **Duplicar** | Cria uma cópia logo depois, na mesma aba ⚖️ D-31 |
| **Forma** | Troca entre Número, Barras, Linha, Pizza e Tabela, só as que o dado permite ⚖️ D-34; pizza com mais de 8 fatias vira barras com aviso |
| **Voltar ao padrão** e confirma | Apaga o layout daquele relatório |

**Regras e limites:** até 20 abas e 200 blocos por relatório. A primeira aba chama **Painel** ⚖️ D-30. O Excel gera uma planilha por aba, na ordem; a tabela de registros só vai na primeira planilha ⚖️ D-36. Restaurar backup com "Somar" só traz o layout de relatório que ainda não tem layout ⚖️ D-32.

### P-v. Carregar relatórios de planilha, JSON, XML ou zip
**Para que serve:** trazer os dados de qualquer arquivo de tabela, sem digitar nada. (PDF e foto com leitura de texto vêm em etapa seguinte.)

| Você faz | O programa faz |
|---|---|
| Toca em **Carregar dados** e escolhe um ou vários arquivos (.csv, .txt, .xlsx, .xls, .ods, .json, .xml, .zip) | Lê cada arquivo no próprio aparelho; nada sai dele |
| (planilha com várias abas) | Cada aba vira um relatório separado, chamado "arquivo - aba" ⚖️ D-40 |
| Responde **Esta coluna é o quê?** na primeira vez | Lembra o formato; o mesmo conjunto de colunas em CSV, planilha, JSON ou XML não pergunta de novo ⚖️ D-41 |
| Escolhe um **.zip** | Abre e lê cada arquivo de dentro; os que não consegue ler ele avisa e segue com os outros |

**Regras e limites:** números saem com vírgula e sem milhar, datas como dd/mm/aaaa ⚖️ D-41; só os valores contam (fórmulas e macros nunca rodam; .xlsm, .xlsb e planilha com senha não são lidos ⚖️ D-42); cada arquivo até 50 MB; zip até 50 arquivos e 200 MB depois de aberto ⚖️ D-43. Mensagens: "Não achei o cabeçalho em <arquivo>.", "Não consegui ler <arquivo>.", "<arquivo>: formato não suportado.".

### P-u. Carregar um relatório em PDF e conferir a leitura
**Para que serve:** trazer os dados de um relatório PDF que tem texto (não escaneado), conferindo antes de guardar.

| Você faz | O programa faz |
|---|---|
| Toca em **Carregar dados** e escolhe o PDF (ou um .zip com PDF dentro) | Lê o texto de cada página no próprio aparelho, acha as colunas pela posição, tira título, rodapé e cabeçalhos repetidos ⚖️ D-52 |
| Vê a janela **Conferir leitura** | Mostra a tabela lida, "Linhas lidas" e "Células marcadas"; células que parecem erradas ficam destacadas ⚖️ D-50 |
| Corrige o que estiver errado direto na tabela | Guarda a correção |
| **Confirmar** | Segue para "Esta coluna é o quê?" (só na primeira vez deste formato) e guarda os registros |
| **Descartar** (ou Esc) | Não guarda nada |

**Regras e limites:** se o PDF não tem tabela (um contrato, por exemplo) aparece "Não encontrei uma tabela neste arquivo" e nada é guardado. PDF com senha ou danificado: "Não consegui ler <arquivo>.". Até 200 páginas e 20 mil linhas; acima disso o programa lê só até o limite e avisa "O arquivo foi cortado em 200 páginas." / "O arquivo foi cortado em 20 mil linhas." ⚖️ D-51.

### P-t. Carregar uma foto ou PDF escaneado (leitura por OCR)
**Para que serve:** trazer os dados de uma foto, print ou PDF escaneado de um relatório, sem digitar. Tudo acontece no aparelho, sem enviar nada para a internet.

| Você faz | O programa faz |
|---|---|
| Toca em **Carregar dados** e escolhe uma ou várias fotos (JPG ou PNG), um PDF escaneado ou um .zip com elas | Melhora a imagem (cinza, contraste, endireita) e lê o texto em português; mostra "Lendo a imagem… n%" |
| Escolhe várias fotos do mesmo relatório de uma vez | Junta tudo numa só conferência, com o cabeçalho uma vez ⚖️ D-62 |
| Vê **Conferir leitura** (foto ao lado) | Marca as células em que o leitor tem dúvida e as que ele corrigiu sozinho (O→0 em código e número) ⚖️ D-60 |
| Corrige o que estiver errado e toca em **Confirmar** (ou **Descartar**) | Guarda só o que você confirmou |

**Regras e limites:** a primeira vez precisa de internet **uma vez** para o aparelho guardar o leitor (cerca de 9 MB, uma só vez); depois funciona sem internet. Sem tabela na imagem: "Não encontrei uma tabela neste arquivo". Até 20 imagens por vez e 120 segundos por imagem ⚖️ D-62. Só português ⚖️ D-63. Modelo de idioma leve ⚖️ D-61: erra um pouco mais, por isso a conferência é obrigatória.

## Anotações da leitura com o Galindo (26/11/2026)
**Meta (P-b), corrigida na F-71 (26/11):** campo da meta **vazio = sem meta** (o bloco mostra só o percentual dentro do prazo); **0** vale 0%; quem não mexe continua com 90%.

**Versão 2.0 (mudanças grandes, não entram agora; F-72):**
0. **Macro do Excel (`excel/RaioX_Relatorio.bas`, P-z, D-24, F-49):** inteira para a V2; o Galindo não vai testar no Excel real agora. O botão **Gerar Excel do app** (P-g) continua na versão atual.
1. **Clientes ou contratos separados:** seletor "Cliente ▾" no topo, com "+ Novo cliente"; cada um com relatórios, nome, logo, metas, painel e backup próprios; trocar com um toque, sem misturar (hoje é um cliente por aparelho e códigos iguais de clientes diferentes se juntam, D-05).
2. **Histórico de alterações:** a cada carga, comparar registro a registro com o guardado; onde algum campo mudou, guardar a data da carga, o campo, o valor antigo e o novo. Mostrar ao passar o mouse no registro, botão "Exibir histórico" (todas as versões na lista) e extrair no Excel. Só aparece em registro que teve alteração (D-06, "Se mudar").
3. **Compartilhar aprendizado com a GSI:** janela com campo de texto e print colado com Ctrl+V (só texto e print; nenhum outro arquivo; o app redesenha a imagem antes; aviso para não mandar dado pessoal; quem tem imagem salva abre, tira print e cola). Vai junto um arquivo só com as configurações (formatos de coluna, indicadores, sinônimos, contas), nunca os registros. Envio por e-mail para **solucaogsi@gmail.com**: no celular pelo compartilhar do aparelho (anexo junto); no computador baixa o pacote e abre o e-mail pronto. O app continua sem servidor.
4. **OCR em outros idiomas** (D-63).
5. **Fotos pela câmera, várias de uma vez:** tirar várias fotos seguidas e enviar juntas; na tela das fotos, "Adicionar outra foto", "Retirar" a que não ficou boa e um X no canto para fechar.

## Quadro das decisões (marcar na homologação)
*Marcado pelo Galindo em 26/11/2026, na leitura com a conversa: 35 Fica, 2 Muda (D-35, D-51 → F-73), 2 V2 (D-24, D-63).*
| ⚖️ | Onde (procedimento) | Decisão (como funciona) | Por quê | Se mudar | Provisória? | Galindo: Fica / Muda |
|---|---|---|---|---|---|---|
| D-01 | Backup e restaurar | "Somar" junta "Meus indicadores" (sem repetir, até 50). Espec. seção 13, P-06; implementado na F-60 (26/11/2026, com teste) | Não perde o que o usuário já escolheu | "Troca": tarefa pequena, com teste | Sim | **Fica** (26/11) |
| D-02 | Config | Config salva sozinha a cada letra; não há botão Salvar | Menos um passo; nada se perde | Pôr botão Salvar: trivial | Não | **Fica** (26/11) |
| D-03 | Config | Logo até 2 MB, reduzido para até 240 px e guardado no aparelho | Não pesar no aparelho nem no Excel | Mudar os números: trivial | Sim | **Fica** (26/11) |
| D-04 | Carregar relatório | Linha sem valor no Código fica de fora sem aviso | Sem código não dá para juntar nem atualizar | Avisar quantas ficaram de fora: tarefa pequena | Sim | **Fica** (26/11) |
| D-05 | Carregar relatório | Arquivo com o mesmo campo código e códigos já guardados entra no relatório que já os tem (mesmo com outro nome de arquivo) | Juntar relatórios complementares do mesmo sistema | Perguntar antes de juntar: tarefa pequena | Sim | **Fica** (26/11) |
| D-06 | Carregar relatório | Mesmo código: valor novo preenchido substitui o antigo; vazio não apaga | Arquivo novo é o mais atual; arquivo parcial não estraga | Guardar histórico de cada mudança: tarefa maior | Não | **Fica** (26/11) |
| D-07 | O que acompanhar | Nada vem marcado; Cancelar mantém o painel padrão sem salvar | A escolha é da pessoa (nada fixo) | Já vir marcado o essencial: trivial | Sim | **Fica** (26/11) |
| D-08 | Esta coluna é o quê? | A coluna do andamento (antigo Situação) é sugerida pelo nome da coluna (situação, status, estado); a pessoa troca | Situação não dá para adivinhar pelos valores | Outras palavras: trivial | Sim | **Fica** (26/11) |
| D-09 | O que acompanhar | "Em aberto" = situação que não começa com conclu-, finaliz-, encerr-, fechad-, entreg-, cancel-, resolvid-, pag- | Sem lista fixa de um ramo; serve para a maioria dos sistemas | Deixar a pessoa marcar quais situações são "fechadas": tarefa média | Sim | **Fica** (26/11) |
| D-10 | Pedido escrito | "Este mês", "mês passado", "últimos N dias" contam a partir da data mais recente dos registros, não de hoje | Relatório antigo continua dando resposta | Usar a data de hoje: trivial | Sim | **Fica** (26/11) |
| D-11 | Pedido escrito | Erro de digitação aceito com semelhança de 80% ou mais | Equilíbrio entre entender e não chutar | Mudar o número: trivial | Sim | **Fica** (26/11) |
| D-12 | Excel | Sem fórmula, macro ou gráfico nativo; gráfico vira tabela com barra em texto (█) | Segurança e Excel igual à tela em qualquer versão | Gráfico nativo do Excel: tarefa média | Sim | **Fica** (26/11) |
| D-13 | Apagar todos os dados | Apagar mantém Config, formatos lembrados e sinônimos | Próximo relatório entra sem perguntar de novo | Apagar tudo mesmo: trivial | Sim | **Fica** (26/11) |
| D-14 | Backup / Somar | No "Somar", escolha do painel e formatos do backup valem por cima dos atuais; Config não muda (só no Substituir) | O backup traz o arranjo mais completo; não troca o cliente do aparelho | Perguntar item a item: tarefa média | Sim | **Fica** (26/11) |
| D-15 | Painel | A faixa Total / Mais antigo / Mais novo fica sempre no topo, mesmo com escolha | Dá o tamanho e o período do relatório de relance | Esconder quando há escolha: trivial | Sim | **Fica** (26/11) |
| D-16 | Esta coluna é o quê? | Tipos reduzidos a 4 (Número, Data, Grupo, Texto) + Aparece? (Sim/Não) + duas perguntas (qual identifica cada linha; qual mostra o andamento). Data com hora é Data (não há "Data e hora" separado) | Linguagem para quem não sabe Excel; menos escolhas (Galindo, 26/11) | Mudar nomes: trivial | Não (decisão do Galindo) | **Fica** |
| D-20 | Criar conta personalizada | `dias(data1, data2)` devolve a **média** de dias entre as duas datas | A especificação não dizia qual estatística | Trocar por mediana: tarefa pequena, com teste | Sim | **Fica** (26/11) |
| D-21 | Criar conta personalizada | Divisão por zero (ou resultado indefinido) mostra "sem dados" em vez de mensagem de erro | Espec. CA-53 pede "sem dados" | Mostrar erro: tarefa pequena | Não | **Fica** (26/11) |
| D-22 | Criar conta personalizada | A sugestão de campo no erro sai em minúsculas ('valor'), como no exemplo da especificação | Seguir o CA-52 ao pé da letra | Mostrar o nome exato do campo: troca de texto | Sim | **Fica** (26/11) |
| D-23 | Criar conta personalizada | Contas valem por relatório (não são globais); nome repetido substitui a antiga | Campos mudam de um relatório para outro | Contas globais: tarefa maior | Sim | **Fica** (26/11) |
| D-24 | Versão Excel | O catálogo na macro é só o que cabe no Excel 2016: total, soma/média/mediana/mínimo/máximo, soma por categoria e registros por mês; o campo número é escolhido no Painel (B11) | Espec. 9b e seção 12 (fora do escopo: pedido escrito, layout, OCR) | Levar também % por situação e tempo entre datas: tarefa média | Sim | **V2** (26/11: macro do Excel inteira fica para a versão 2.0) |
| D-30 | Editar layout | A primeira aba chama `Painel` | Mesmo nome da planilha do Excel (etapa 4) | Outro nome: trivial | Não | **Fica** (26/11) |
| D-31 | Editar layout | Duplicar cria a cópia na mesma aba, logo depois do original | Espec. não dizia onde | Cópia na aba escolhida: tarefa pequena | Sim | **Fica** (26/11) |
| D-32 | Editar layout / Backup | Restaurar com "Somar" só traz layout de relatório sem layout | Evita desfazer o arranjo atual | Sobrescrever: trivial | Sim | **Fica** (26/11) |
| D-33 | Editar layout | Tamanho não muda o Excel | Planilha não tem largura de bloco | Nenhum efeito possível | Não | **Fica** (26/11) |
| D-34 | Editar layout | Formas permitidas por tipo de bloco: número só Número; por categoria Barras/Pizza/Tabela; por mês também Linha | "quando o tipo de dado permite" | Liberar mais formas: tarefa média | Sim | **Fica** (26/11) |
| D-35 | Editar layout | A mensagem de apagar aba diz "Os N blocos dela vão para a primeira aba." (inclusive com 1 bloco) | Texto literal da espec. | Singular: trivial | Sim | **Muda** (26/11), feito na F-73: com 1 bloco, "O bloco dela vai para a primeira aba." |
| D-36 | Editar layout / Excel | A tabela de registros só aparece na primeira planilha de painel de cada relatório | Não repetir milhares de linhas em cada aba | Repetir em todas: trivial | Sim | **Fica** (26/11) |
| D-40 | Carregar planilha | Cada aba da planilha vira um relatório à parte, "arquivo - aba" | Espec. 7: "cada aba vira um conjunto candidato" | Juntar abas num só: tarefa média | Sim | **Fica** (26/11) |
| D-41 | Carregar planilha/JSON/XML | Número com vírgula e sem milhar, data dd/mm/aaaa, para o formato lembrado do CSV servir | Reaproveitar o que o usuário já respondeu | Perguntar de novo por tipo de arquivo: trivial | Sim | **Fica** (26/11) |
| D-42 | Carregar planilha | .xlsm, .xlsb e planilha com senha não são lidos | Segurança (macros) e simplicidade | Aceitar .xlsb: tarefa pequena | Sim | **Fica** (26/11) |
| D-43 | Carregar zip | Até 50 arquivos e 200 MB depois de aberto; acima disso nada do zip entra | Proteção contra arquivo-bomba | Mudar os números: trivial | Sim | **Fica** (26/11) |
| D-50 | Carregar PDF | PDF sempre abre a conferência, mesmo sem nenhuma célula marcada | Espec. 7: tudo de PDF/OCR passa pela conferência | Pular a conferência quando tudo parece certo: tarefa pequena | Não | **Fica** (26/11) |
| D-51 | Carregar PDF | Até 200 páginas e 20 mil linhas; acima disso corta e avisa | Proteção do aparelho | Mudar os números: trivial | Sim | **Muda** (26/11): continua cortando, mas avisa "O arquivo foi cortado em 200 páginas / 20 mil linhas." (feito na F-73) |
| D-52 | Carregar PDF | Colunas achadas pela posição do texto; tabelas desenhadas só por linhas (sem alinhamento de texto) podem não ser lidas | Simplicidade, sem IA | Melhorar a leitura: tarefa maior | Sim | **Fica** (26/11) |
| D-60 | Foto/OCR | Confusões do leitor (O por 0, I por 1…) são corrigidas sozinhas só em colunas de código e número, mas a célula fica marcada | Reduz erro sem esconder a mudança | Não corrigir sozinho: trivial | Sim | **Fica** (26/11) |
| D-61 | Foto/OCR | Modelo de idioma leve (1,4 MB) | Rápido e leve no celular | Modelo completo (6,7 MB): tarefa pequena | Sim | **Fica** (26/11) |
| D-62 | Foto/OCR | Até 20 imagens por vez e 120 s por imagem; fotos do mesmo envio com o mesmo cabeçalho viram uma conferência só | Proteção do aparelho | Mudar os números: trivial | Sim | **Fica** (26/11) |
| D-63 | Foto/OCR | Só português | Espec. 7 | Outros idiomas: tarefa pequena | Não | **V2** (26/11): ler outros idiomas |
