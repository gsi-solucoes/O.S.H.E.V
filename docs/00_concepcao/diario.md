# Diário de criação — Raio X do Relatório

- **19–24/11/2026** · Protótipo interno feito em conversa: leitor de arquivos, janelas clicáveis, Excel com capa, histórico no navegador, importador de CSV que aprende as colunas.
- **25/11/2026** · Galindo decide transformar a estrutura num produto genérico: **Raio X do Relatório**, PWA offline, "O que você quer acompanhar?", pedido escrito com "É isso?", contas personalizadas, Editar layout, todos os formatos.
- **25/11/2026 14h08** · Galindo: "vamos fazer ele pela fábrica" e "não precisa criar o esqueleto fake, já temos tudo". Projeto registrado na Fábrica sem dublês. Etapa 1 já codificada na conversa, aguardando testes.
- **25/11/2026 14h13** · Galindo: documento genérico (o app é para todo mundo) e ler todo tipo de arquivo possível, inclusive imagem com OCR. Concepção, como-funciona e doc do cliente atualizados.
- **25/11/2026 14h18** · ✋ Portão 1 aprovado pelo Galindo. Especificação v1.0 escrita (`docs/01_especificacao/especificacao.md`, CA-01 a CA-100, perguntas P-01 a P-05); esperando portão 2.
- **25/11/2026 14h34** · Galindo: nada do caso de origem no produto nem na macro; do protótipo vem só a estrutura. Dados de teste só fictícios. Macro = versão Excel para baixar, com a mesma estrutura genérica.
- **25/11/2026 14h43** · ✋ Portão 2 aprovado (especificação v1.0; P-01 a P-05 decididas). Próximo: etapa 1 com Construtor + Testador.
- **25/11/2026 14h45** · Ideia do Galindo (entra na etapa 2): depois da escolha, mostrar em texto o que foi criado ("Seu painel" / "Entender este painel") e a mesma explicação no Excel (CA-26 a CA-29).
- **25/11/2026 15h10** · Especificação v1.1 (F-43): tabela "Nomes na tela" com 41 rótulos exatos da etapa 1 (textos que o app já usa) e dúvidas do Testador decididas: mediana em "H h MM min" arredondada ao minuto (como o CA-43), data AAAA-MM-DD no nome do Excel, e 7 ajustes do teste (D-01 a D-07). Nenhuma regra de negócio mudou.
