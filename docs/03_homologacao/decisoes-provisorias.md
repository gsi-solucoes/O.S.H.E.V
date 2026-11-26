# Decisões provisórias — Raio X do Relatório

Dúvidas de produto que a fábrica decidiu sozinha para não parar a linha (regra "Decisão de produto não para", Galindo, 26/11/2026).
**Este documento abre a homologação:** antes de testar o app, o Galindo lê esta lista e diz, em cada linha, **Fica** ou **Muda (como)**.
O que mudar vira tarefa com teste. Cada decisão também fica na seção 13 da especificação.

| # | Data | Dúvida | Decisão provisória (como o app está) | Por quê | Se mudar | Galindo |
|---|---|---|---|---|---|---|
| P-06 | 26/11/2026 | Ao restaurar um backup com **"Somar"**, a lista de "Meus indicadores" junta ou troca? | **Junta** a lista atual com a do backup, sem repetir, até 50 (o que passar fica de fora com aviso) | Não perde o que o usuário já escolheu | "Troca": tarefa pequena, com teste (F-60 implementa a provisória) | ⏳ |
