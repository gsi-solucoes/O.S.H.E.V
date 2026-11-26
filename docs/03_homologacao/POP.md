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

## Quadro das decisões (marcar na homologação)
| ⚖️ | Onde (procedimento) | Decisão (como funciona) | Por quê | Se mudar | Provisória? | Galindo: Fica / Muda |
|---|---|---|---|---|---|---|
| D-01 | Backup e restaurar | "Somar" junta "Meus indicadores" (sem repetir, até 50). Espec. seção 13, P-06; implementado na F-60 (26/11/2026, com teste) | Não perde o que o usuário já escolheu | "Troca": tarefa pequena, com teste | Sim | |
| D-20 | Criar conta personalizada | `dias(data1, data2)` devolve a **média** de dias entre as duas datas | A especificação não dizia qual estatística | Trocar por mediana: tarefa pequena, com teste | Sim | |
| D-21 | Criar conta personalizada | Divisão por zero (ou resultado indefinido) mostra "sem dados" em vez de mensagem de erro | Espec. CA-53 pede "sem dados" | Mostrar erro: tarefa pequena | Não | |
| D-22 | Criar conta personalizada | A sugestão de campo no erro sai em minúsculas ('valor'), como no exemplo da especificação | Seguir o CA-52 ao pé da letra | Mostrar o nome exato do campo: troca de texto | Sim | |
| D-23 | Criar conta personalizada | Contas valem por relatório (não são globais); nome repetido substitui a antiga | Campos mudam de um relatório para outro | Contas globais: tarefa maior | Sim | |
