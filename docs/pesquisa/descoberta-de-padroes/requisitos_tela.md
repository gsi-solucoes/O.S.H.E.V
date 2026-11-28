# Requisitos da tela de perguntas (Galindo, 27/11/2026)
1. Mostrar a planilha sendo montada na hora, enquanto as perguntas são respondidas (como já faz hoje).
2. Perguntar grupo por grupo: "Este grupo é o quê?" com exemplos reais; tipos incluem Valor (R$) e Tempo (duração);
   campo opcional para descrever com as próprias palavras.
3. Mostrar dentro de cada grupo as células marcadas "não pertence?", e perguntar: vai para grupo existente (qual?) ou grupo novo.
4. Datas: separar "é data" (formato) de "qual data é" (abertura, início, fim, baixa); perguntar quando não der para saber.
5. Colunas vazias ou só com sujeira (traço, asterisco, pontuação, um caractere repetido): NÃO listar uma por uma.
   Juntar numa caixa que abre para baixo (lista com caixinhas de marcar), com "selecionar todas" e "excluir" num clique.
   Pensar em outros agrupamentos parecidos (ex.: colunas com o mesmo valor em todas as linhas).
6. IA opcional (Galindo, 27/11/2026): o app funciona normal para todos. O app verifica sozinho se o computador/navegador aguenta
   (WebGPU + memória). SÓ para quem aguenta aparece o botão "Ativar relatórios mais inteligentes", com texto ao lado:
   IA que roda só neste computador, relatórios não saem daqui, funciona offline, download único (~1 GB), opcional.
   Quem não aguenta não vê o botão. Se o app guardar o que aprendeu, dizer que fica no navegador e ter botão "apagar o que aprendeu".
   Só entra no Raio X se a IA passar no teste contra os gabaritos (1ª rodada: IA 7/20 × regras 20/20).
   Casos (Galindo, 27/11/2026): já ativou → nada; aguenta e não ativou → botão "Ativar relatórios mais inteligentes";
   computador parece aguentar mas navegador antigo/sem WebGPU → "Para relatórios mais inteligentes, atualize seu navegador
   (Chrome ou Edge)" com link (é sugestão, não promessa); não aguenta → nada.
7. Contexto em cada pergunta (Galindo, 27/11/2026, sobre "Dt. Execução": "não dá pra saber, precisa de mais informação"):
   mostrar, para 2-3 exemplos, as palavras que vêm ANTES e DEPOIS na mesma linha e a linha de CIMA e de BAIXO, como no arquivo.
Respostas do Galindo (gabarito humano): resumidas "Marca" = Descrição (Texto); resumidas "Equipamento" = Código do setor (Categoria);
   detalhadas "Solicitante" = Categoria; detalhadas "Dt. Execução" = precisa de contexto para decidir.
   Formato aprovado (Galindo, 27/11/2026): moldura 5-2-2-5 — linha de cima: 5 células centradas na palavra; meio: 2 antes,
   a PALAVRA DESTACADA, 2 depois; linha de baixo: 5 células. Pula linha vazia. 3 exemplos por grupo. No celular, cada célula até 3 linhas.
8. (Galindo, 27/11/2026) SUBSTITUI a moldura 5-2-2-5: ao perguntar sobre uma célula, mostrar o REGISTRO INTEIRO (a OS toda):
   todas as linhas que a fórmula identificou como parte daquele registro, cada célula na sua posição, com o cabeçalho em cima
   e o contexto (ex.: Setor/Oficina) que vale para ele; a célula perguntada destacada. Não é mais 5, 3 nem 7: é tudo que pertence ao registro.
   Data do pedido = data da compra (mesma coisa): juntar numa opção só "Abertura / pedido / compra".
9. (Galindo, 27/11/2026) Mostrar em MINIATURA (folha reduzida que cabe na tela, com "ampliar"), e o formato da vista depende do arquivo:
   ficha/agrupado (registro em várias linhas) → miniatura da OS inteira; tabela (1 linha por registro) → cabeçalho + a linha + 2 vizinhas
   de cada lado apagadas; sem cabeçalho → a linha + vizinhas; tabela larga (>12 colunas) → vista deitada "cabeçalho → valor".
   Ajuste (Galindo): "do jeito que vem dá pra ter noção" → sem vista deitada; sempre a miniatura no desenho original do arquivo.
   Ajuste (Galindo): NUNCA abreviar o texto na miniatura; letra pequena, texto inteiro, abre centrado na célula perguntada
   e a pessoa ARRASTA a folha (dedo ou mouse, "mãozinha") para ver o resto.
   Validação (Galindo): com a OS inteira em miniatura, "dá pra ver nitidamente que é a data final" (NAO_ATENDIDAS "Data Final").
   Ajuste (Galindo): a miniatura abre com a OS INTEIRA (reduzida até caber na tela) + LUPA (🔍+ / 🔍− / "ver a OS inteira");
   aproximando, centra na célula perguntada e a pessoa arrasta para andar pela folha.
10. (Galindo) Nada de "OS" fixo: a tela fala em REGISTRO (uma solicitação com várias informações: OS, pedido de compra, venda...).
    O nome mostrado vem do arquivo: rótulo do identificador + valor (ex.: "Pedido 9100", "Nr.OS 277378"); sem rótulo → "Registro N".
   Nota (Galindo): em VENDA, data do pedido = data da compra. Em OS, "compra de material" é outra data. Regra de contexto, não global.
11. (Galindo) "Para a pessoa dar a informação correta, tem que mostrar TODAS as informações": a pergunta mostra o registro inteiro
    no arquivo dela E o mesmo registro (mesmo identificador) em TODOS os outros arquivos carregados, inteiros, em miniatura;
    datas iguais à perguntada ficam destacadas em verde. Se não aparece em outro arquivo, dizer isso.
    Regra R22 (cruzar pelo identificador): data igual (≥80% dos registros em comum) a uma data de nome conhecido em outro
    arquivo herda o significado. Achados: detalhado "Dt. Execução" = ficha "Data Término" (754/754) → ENCERRAMENTO (não fim do
    serviço); resumido "Dt Programada" = mesmo dia de "Dt. Pedido" (902/902) → ABERTURA.
   Ajuste (Galindo): a LUPA aproxima/afasta a FOLHA INTEIRA (registro + os mesmos registros dos outros arquivos, numa janela só),
   como foto/mapa — não cada pedaço separado. Abre afastada (tudo cabendo na janela); aproximou, arrasta para qualquer lado.
12. Teste humano das datas (Galindo, 27/11/2026): concordou com as regras+R22 em 5 de 6 com rótulo. Gabarito corrigido:
    detalhado "Dt. Execução" = Encerramento / baixa. Em aberto: resumido "Dt Programada" (Galindo: início do serviço;
    R22: mesmo dia da abertura em 902/902, sem hora). Sem rótulo ("não dá para saber"): a tela deve mostrar o raciocínio da
    linha do tempo (vem X dias depois de A, ~1h30 antes de B) para a pessoa poder confirmar.
13. Exemplos que DESEMPATAM (27/11/2026): escolher para mostrar registros em que a data perguntada bate com UMA só data dos
    outros arquivos (registro em que tudo aconteceu no mesmo dia não ajuda a decidir).
    Resolvido: resumido "Dt Programada" = mesmo dia da Data Pedido em 753/753 (início só 48%, término 9%) → ABERTURA (sem hora).
14. Conferência resposta × evidência (27/11/2026): se a resposta da pessoa contradiz evidência forte (ex.: Galindo respondeu
    "Dt Programada" = início do serviço; dado: mesmo dia da abertura em 753/753, do início em 48%), o app mostra a evidência e
    pergunta "Quer manter mesmo assim?" [Manter minha resposta] [Usar a sugestão]. Decisão final é da pessoa, mas informada.
15. (Galindo) Regra geral da tela: SEMPRE mostrar o que faz a pessoa conseguir ver. A pessoa sobe TODOS os relatórios juntos;
    o app junta pelo identificador e mostra o registro em todos; se algum arquivo tem cabeçalho, a pessoa vê o nome ali.
    Se nenhum tiver, mostrar o raciocínio da linha do tempo. Carregar vários arquivos de uma vez é parte do fluxo, não exceção.
16. Teste das datas 2 (Galindo, 27/11/2026): com o outro relatório junto, acertou as 3 datas que existiam nele (abertura,
    compra, encerramento). As 2 que só tinham linha do tempo (início/fim do serviço): "não dá para saber" — o programa deduziu
    certo. Ajustes: (a) botão próprio "Compra de material" (separado de abertura/pedido; em VENDA podem coincidir);
    (b) quando só há linha do tempo, a tela escreve a CONCLUSÃO ("andam sempre juntas a ~1h30, entre a compra e o encerramento:
    parecem início e fim de um mesmo serviço; esta seria o início. Confere?") e a pessoa só confirma ou corrige.
17. (Galindo) PERGUNTAR SÓ O QUE TEM DÚVIDA. O que o app já sabe com certeza (rótulo claro, igual em 40 de 40 noutro arquivo...)
    ele MOSTRA o que decidiu, numa lista "Já identifiquei sozinho" com "corrigir" em cada item. Perguntas ("Preciso da sua ajuda")
    só para: grupo sem nome, células que não encaixam, data com confiança média/baixa, grupo raro.
18. (Galindo) A tela NÃO pode virar teste de lógica: quem calcula (dias, horas, quem vem antes) é o app. A pessoa vê a
    CONCLUSÃO pronta + a prova curta, e só confirma/corrige. Nunca deixar a pessoa "sair calculando" para encaixar numa opção.
19. R22b (27/11/2026): cruzamento também para NOMES: grupo cujo conteúdo é igual (≥80%; aceita texto cortado) ao de um grupo
    com nome em outro arquivo → sugere esse nome com a prova ("Marca" do resumido = "Servico" do detalhado em 901/901).
    Grupo sem nome resolvido pelo cruzamento deixa de ser pergunta. Descobre sinônimos entre relatórios (Tipo = Tipo de OS,
    Funcionário = Funcionário da Oficina, Nr. do Patrimônio = Nr. da Plaqueta) → base para juntar relatórios numa planilha só.
    Cabeçalho deslocado (dados além do último rótulo do cabeçalho) → os nomes daquele cabeçalho viram pergunta, com aviso.
20. Respostas do Galindo no NAO_ATENDIDAS (gabarito humano: respostas_galindo_NAO_ATENDIDAS.txt). Gostou da tela com a planilha
    montando embaixo. Lições: (a) data com hora cortada ("12/11/2026 10:") é data; (b) grupos de um trecho interno (ex.: "Ordem de
    Serviço Relacionadas") devem ser nomeados com o título do trecho ("Tipo (OS relacionada)"), não "(2)"; (c) tirar espaços dos nomes.
21. (Galindo) Relatório do Diego FORA dos testes ("não foi gerado para isso, tem muita coisa errada"). Testes só com os CSVs do
    Marcus e com arquivos inventados (fake) gerados para teste.
22. (Galindo) Separar "nome no arquivo" de "como entra na planilha": responder "Sim" (é a "Dt Programada" do relatório) e
    ainda poder dizer que ela ENTRA COMO "Data de abertura" (no resumido, a data de abertura vem com o nome "Dt Programada").
    Campo "Entra na planilha como:" sempre visível e editável; em datas vem preenchido pelo significado descoberto.
    A planilha montada e as respostas usam esse nome; o nome original fica guardado (dica ao passar o mouse).
23. (Galindo) Na planilha sendo montada: um × no título de cada coluna para tirar a coluna na hora; em cima, a lista
    "Colunas tiradas" com "voltar" em cada uma.
24. (2ª rodada de respostas) Galindo unificou nomes entre relatórios (ficha "Ordem de Serviço · 1/2" → "Nr.OS"/"Servico", nomes do
    detalhado). O app deve PROPOR o mesmo nome para a mesma informação em relatórios diferentes (sinônimos achados pelo cruzamento),
    para juntar tudo numa planilha só. Confirmou 100% das decisões automáticas do relatório detalhado.
25. (3ª rodada) (a) Nome digitado que é frase longa → app guarda como "explicação" e sugere nome curto; campo de explicação mais visível.
    (b) Consistência entre relatórios: mesma informação com nome/tipo diferente (Servico × Solicitação de serviço; Localidade Texto ×
    Categoria) → avisar "No outro relatório você chamou de X / tratou como Y. Usar o mesmo?". (c) Data sem nome com significado
    definido → nome sugerido pronto ("Início do serviço"), não "Grupo 2". (d) Bug corrigido: R3 (rótulo na célula) só separa quando a
    LINHA inteira é "RÓTULO: valor" (antes "INSTALAÇÕES: VERIFICAR..." virava rótulo).
26. ⚖️ Decisão da fábrica (Galindo: "faça do jeito que achar certo"): número em que cada valor é diferente (plaqueta, patrimônio,
    série) é CÓDIGO (identifica, não se soma). Bem/Plaqueta/Patrimônio/Série vêm preenchidos em só 5 de ~900 OS → ficam na caixa
    "Quase vazios" (disponíveis, sem poluir perguntas nem planilha). Conferir na homologação.
27. R23 (27/11/2026): número que anda sempre com o mesmo texto e vice-versa (≥95% nos dois sentidos) é o CÓDIGO daquela categoria
    (resumido "Equipamento" 46 = UTI ADULTO → "Código do Setor", Categoria — como o Galindo respondeu). Quantidade (Qtde) não entra.
    Prova às cegas da R23 (Galindo perguntou se não era cópia): arquivo inventado de estoque (8_estoque_loja.csv) → achou
    Filial=código da Cidade e Cod Produto=código do Produto; Quantidade ficou Número (armadilha). Regra olha comportamento, não nomes.
28. Teste da família (planilha Excel → CSV com ; e vírgula decimal, 10 pessoas). 1ª passada: 1 registro (nomes viraram rótulos) e
    Altura = Valor (R$). Regras gerais corrigidas: (a) sem repetição, se há cabeçalho claro só ele é rótulo; (b) número com
    decimal é medida (nunca código/identificador); (c) dinheiro só com R$, milhar (1.234,56) ou rótulo de dinheiro; (d) nome
    único por registro = Categoria. Depois: 10 registros, 0 perguntas. Todos os testes anteriores seguem certos.
    COMBINADO (Galindo): nos testes, mostrar primeiro o resultado como saiu (com erros), para ele ver/corrigir na tela;
    eu só conserto o motor quando é defeito de leitura que a tela não resolve, e aviso antes.
