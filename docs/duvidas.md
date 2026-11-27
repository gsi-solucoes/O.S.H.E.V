
## F-83 (Testador, E1 da 9c): dúvidas da especificação
- Rótulo do campo de prazo na Config (`prazoH`) não está na especificação; o teste CA-207 localiza por `get_by_label(/prazo/i)`.
- Formato da coluna `Mês` (R-150/9c.3) não é dado; o teste aceita `mm/aaaa` ou `aaaa-mm`.
- `faltam X para a meta`: X (unidade e conta) não definido; testes só exigem o texto `faltam … para a meta`.
- Cartão de comparação R-157: o teste procura `↑|↓ <p>% em relação a <mm/aaaa>` no texto do cartão `Total de registros`.
- `Como ler este relatório` inclui a si mesma? Teste exige linha para toda parte visível menos ela.
- Índice (R-143): `Pendências por idade` e `Os 10 mais antigos em aberto` têm 1 ou 2 links? Teste aceita ambos (mesma frase).
- Janela de registros (CA-205): como mostra a contagem não está definido; teste só exige o número na janela.
- Hierarquia: cada parte precisa ter heading de nível >= ao seu agrupador; capa h2 e partes h2/h3 (o teste isola a parte pelo heading).
- `data-forma="pizza"` (CA-213): o teste assume fatias com `aria-label="<Região>: <n>"` dentro do elemento `data-forma="pizza"`.
