# POP — Como o Raio X do Relatório funciona

*Procedimento Operacional Padrão · primeiro item da homologação (Galindo, 26/11/2026)*

Este POP diz, passo a passo, **como o programa funciona hoje**: o que a pessoa faz, o que o programa faz em resposta,
as regras e os limites. Onde a fábrica tomou uma **decisão importante sem o Galindo** (provisória ou não), aparece o selo ⚖️ com o número.

**Na homologação:** o Galindo lê o POP antes de testar e marca cada ⚖️ no quadro do fim: **Fica** ou **Muda (como)**.
Cada "Muda" vira tarefa com teste. A fábrica atualiza o POP a cada etapa publicada.

## Procedimentos
<!-- F-61 escreve os procedimentos das etapas 1 a 4 (abrir/instalar, Config, importar arquivos, "esta coluna é o quê?",
"O que você quer acompanhar?", "Seu painel"/"Entender este painel", pedido escrito com "É isso?", gerar Excel, backup e restaurar,
apagar dados). Modelo de cada procedimento: -->

### P-x. Fazer backup e restaurar
**Para que serve:** guardar os dados e as escolhas e trazê-los de volta (outro aparelho ou depois de apagar).

**Passo a passo**
| Você faz | O programa faz |
|---|---|
| … | … |
| Escolhe o arquivo de backup e toca em **Somar** | Junta os registros do backup aos atuais. Em "Meus indicadores", junta a lista atual com a do backup, sem repetir, até 50; o que passar fica de fora com aviso ⚖️ D-01 |

**Regras e limites:** …

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
**Para que serve:** quem prefere o Excel no PC importa os arquivos, vê o painel e gera o relatório, com a mesma estrutura do app.

| Você faz | O programa faz |
|---|---|
| Importa os arquivos e diz o que é cada coluna | Junta os registros pelo código |
| No Painel escolhe período, campo de data, campo de categoria, categoria e **campo número** | Mostra o total, a contagem por categoria e a tabela **Indicadores** (soma, média, mediana, mínimo, máximo, sem valor, soma por categoria, registros por mês) |
| Clica em **Gerar relatório** | Cria um arquivo novo com Capa, Resumo, Indicadores e Registros, só com valores ⚖️ D-24 |

**Regras e limites:** ficam de fora da versão Excel: pedido escrito, contas personalizadas, Editar layout, leitura de PDF e imagem, % por situação e tempo entre duas datas (Excel 2016 não comporta bem). O app tem tudo isso.

### P-w. Editar o layout do painel
**Para que serve:** organizar os blocos do painel do seu jeito (ordem, abas, tamanho, forma) sem mexer nos dados. Vale por relatório, entra no backup e no Excel.

| Você faz | O programa faz |
|---|---|
| Toca em **Editar layout** (só aparece quando há blocos escolhidos em "O que acompanhar") | Mostra a barra de abas e os controles em cada bloco; o botão vira **Concluir edição** |
| **Subir** / **Descer** (ou arrasta) um bloco | Muda a ordem na tela, no "Seu painel" e no Excel |
| **Nova aba**, **Renomear aba**, **Aba à esquerda/direita** | Cria e organiza abas (nome até 30 letras, sem repetir) |
| **Mover para…** outra aba | O bloco passa para a aba escolhida |
| **Apagar aba** e confirma | Os blocos dela vão para o fim da primeira aba ⚖️ D-35 |
| **Tamanho** (Pequeno, Médio, Grande) | Muda a largura na tela; o Excel não muda ⚖️ D-33 |
| **Esconder** / **Mostrar** | Bloco escondido some da tela, do "Seu painel" e do Excel |
| **Duplicar** | Cria uma cópia logo depois, na mesma aba ⚖️ D-31 |
| **Forma** | Troca entre Número, Barras, Linha, Pizza e Tabela, só as que o dado permite ⚖️ D-34; pizza com mais de 8 fatias vira barras com aviso |
| **Voltar ao padrão** e confirma | Apaga o layout daquele relatório |

**Regras e limites:** até 20 abas e 200 blocos por relatório. A primeira aba chama **Painel** ⚖️ D-30. O Excel gera uma planilha por aba, na ordem; a tabela de registros só vai na primeira planilha ⚖️ D-36. Restaurar backup com "Somar" só traz o layout de relatório que ainda não tem layout ⚖️ D-32.

## Quadro das decisões (marcar na homologação)
| ⚖️ | Onde (procedimento) | Decisão (como funciona) | Por quê | Se mudar | Provisória? | Galindo: Fica / Muda |
|---|---|---|---|---|---|---|
| D-01 | Backup e restaurar | "Somar" junta "Meus indicadores" (sem repetir, até 50). Espec. seção 13, P-06; implementado na F-60 (26/11/2026, com teste) | Não perde o que o usuário já escolheu | "Troca": tarefa pequena, com teste | Sim | |
| D-20 | Criar conta personalizada | `dias(data1, data2)` devolve a **média** de dias entre as duas datas | A especificação não dizia qual estatística | Trocar por mediana: tarefa pequena, com teste | Sim | |
| D-21 | Criar conta personalizada | Divisão por zero (ou resultado indefinido) mostra "sem dados" em vez de mensagem de erro | Espec. CA-53 pede "sem dados" | Mostrar erro: tarefa pequena | Não | |
| D-22 | Criar conta personalizada | A sugestão de campo no erro sai em minúsculas ('valor'), como no exemplo da especificação | Seguir o CA-52 ao pé da letra | Mostrar o nome exato do campo: troca de texto | Sim | |
| D-23 | Criar conta personalizada | Contas valem por relatório (não são globais); nome repetido substitui a antiga | Campos mudam de um relatório para outro | Contas globais: tarefa maior | Sim | |
| D-24 | Versão Excel | O catálogo na macro é só o que cabe no Excel 2016: total, soma/média/mediana/mínimo/máximo, soma por categoria e registros por mês; o campo número é escolhido no Painel (B11) | Espec. 9b e seção 12 (fora do escopo: pedido escrito, layout, OCR) | Levar também % por situação e tempo entre datas: tarefa média | Sim | |
| D-30 | Editar layout | A primeira aba chama `Painel` | Mesmo nome da planilha do Excel (etapa 4) | Outro nome: trivial | Não | |
| D-31 | Editar layout | Duplicar cria a cópia na mesma aba, logo depois do original | Espec. não dizia onde | Cópia na aba escolhida: tarefa pequena | Sim | |
| D-32 | Editar layout / Backup | Restaurar com "Somar" só traz layout de relatório sem layout | Evita desfazer o arranjo atual | Sobrescrever: trivial | Sim | |
| D-33 | Editar layout | Tamanho não muda o Excel | Planilha não tem largura de bloco | Nenhum efeito possível | Não | |
| D-34 | Editar layout | Formas permitidas por tipo de bloco: número só Número; por categoria Barras/Pizza/Tabela; por mês também Linha | "quando o tipo de dado permite" | Liberar mais formas: tarefa média | Sim | |
| D-35 | Editar layout | A mensagem de apagar aba diz "Os N blocos dela vão para a primeira aba." (inclusive com 1 bloco) | Texto literal da espec. | Singular: trivial | Sim | |
| D-36 | Editar layout / Excel | A tabela de registros só aparece na primeira planilha de painel de cada relatório | Não repetir milhares de linhas em cada aba | Repetir em todas: trivial | Sim | |
