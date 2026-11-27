
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

## F-84 (Testador, E2 achados, 27/11/2026)
- 9c.7 A5/A6: "meses com registros" inclui os 2 registros de 2027 do `achados.csv` (P1)? Os testes supõem que NÃO (data no futuro fica fora, R-164); se entrassem, A5 deixaria de aparecer e o CA-230 seria impossível com P1+P6.
- 9c.7 A6: com 2 valores de Situação a mudança é simétrica (Aberto +16,7 e Concluido -16,7): gera 1 ou 2 achados? Os testes aceitam os dois casos.
- 9c.7 A8b: o buraco de 01/07 a 24/07 existe em Abertura e em Conclusão (2 campos de data): um achado "Dias sem registro" por campo (frases iguais) ou um só? Testes aceitam os dois.
- 9c.7 A7: `<Grupo> <valor>` = nome do campo + valor ("Grupo Grupo Teste 2")? Teste aceita com ou sem o prefixo; `<valor do andamento>` aceito em qualquer caixa.
- Formato dos números nas frases (casas decimais de % e valores): testes aceitam 1 ou 2 casas (e sem decimais quando exato), com ou sem ponto de milhar.
