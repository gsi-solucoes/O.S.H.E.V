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

## Quadro das decisões (marcar na homologação)
| ⚖️ | Onde (procedimento) | Decisão (como funciona) | Por quê | Se mudar | Provisória? | Galindo: Fica / Muda |
|---|---|---|---|---|---|---|
| D-01 | Backup e restaurar | "Somar" junta "Meus indicadores" (sem repetir, até 50). Espec. seção 13, P-06; F-60 implementa | Não perde o que o usuário já escolheu | "Troca": tarefa pequena, com teste | Sim | |
