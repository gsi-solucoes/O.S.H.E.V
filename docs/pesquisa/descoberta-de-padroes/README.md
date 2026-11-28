# Descoberta de padrões — retomada (conversa de 26 a 28/11/2026)

Pesquisa feita com o Galindo **fora do app e fora da fila da fábrica** (a trava estava com o robô). Nada disto está no `main`
nem na fila ainda: passa para a fábrica quando o Galindo disser ("antes de passar para a fábrica, testamos aqui").

## A ideia (do Galindo)
O app não pode ter modelo fixo de relatório. Ele **descobre sozinho o padrão** de qualquer CSV (tudo vira CSV; imagem vai
por OCR), junta as células em grupos e **pergunta só o que tem dúvida** — mostrando o registro inteiro e a conclusão pronta,
para a pessoa só confirmar ou corrigir. Nunca deixar a pessoa "fazer conta" para responder.

## O que existe aqui
| Arquivo | O que é |
|---|---|
| `prototipo/formula.py` | A fórmula única: regras R1–R23 (lista no topo do arquivo) |
| `prototipo/cruzar.py` | R22/R22b: cruza vários relatórios pelo número do registro (datas e nomes) |
| `prototipo/vista.py` | Monta o "registro inteiro" (miniatura da OS, todas as linhas dela) |
| `prototipo/tela.py` + `tela_modelo.html` | Tela de perguntas ("Preciso da sua ajuda" / "Já identifiquei sozinho" / planilha sendo montada) |
| `prototipo/teste_datas*.py` + `teste_datas_modelo.html` | Telas do teste às cegas das datas |
| `prototipo/conferir.py`, `checar_datas.py`, `todos.py` | Oráculos: gabarito de registros/grupos, gabarito das datas, contagem de todos os arquivos |
| `prototipo/ia_teste.py` | Teste da IA pequena (Qwen3) decidindo "qual data é" pedindo informação ao script |
| `requisitos_tela.md` | **28 requisitos** da tela, cada um com a fala do Galindo que o originou |
| `analise_manual.md` | Como cada formato foi identificado à mão (base das regras) |
| `respostas_galindo_*.txt` | Respostas do Galindo nas telas (gabarito humano) |
| `dados-ficticios/` | Arquivos inventados: lote1 (5 formatos + datas sem rótulo + ficha + estoque), lote-serio (5 assuntos), família (Excel → CSV) |

**Fora do repositório (regra: nenhum relatório real aqui):** os CSV/XLS reais do Marcus e as amostras dos gabaritos que
têm nomes de pessoas. Os arquivos reais estão no Gmail do Galindo, e-mails de `marcus.vicente@…` (Arquivos 13/11, arquivos
13/11, Arquivo Solicitado 23/11, Documento solicitado 24/09, Relatórios 01/03/2024). Para rodar os testes: baixar os anexos
para uma pasta `csv/` fora do repo (o `.zip` traz o `geraldetalhada.csv`; os `.xls/.xlsx` convertidos com pandas).

## Como rodar
```
python3 -I prototipo/conferir.py PASTA        # PASTA/csv = arquivos do Marcus; PASTA/cegas/arq = dados-ficticios/lote1
python3 -I prototipo/checar_datas.py PASTA/csv
python3 -I prototipo/tela.py PASTA/csv saida.html [arquivo.csv "Nome da aba" ...]
```
Estado na última rodada: **11 de 11** gabaritos, **19 de 19** datas (com cruzamento), geral 72.293 registros, concluídas 755,
detalhado 904, resumido 904, formulário vazio 0. Lote sério (5 assuntos novos): 3 de 5 de primeira; depois do conserto de
leitura, 5 de 5 (mas esses 5 já não valem como prova).

## Resultados que importam
- **Cruzamento entre relatórios (R22)** descobriu sozinho: detalhado "Dt. Execução" = ficha "Data Término" (754/754) →
  **encerramento** (o rótulo enganava); resumido "Dt Programada" = mesmo dia da abertura (753/753) → **abertura**;
  resumido "Marca" = "Servico" (901/901) → nome certo apesar do cabeçalho deslocado; sinônimos Tipo = Tipo de OS etc.
- **IA pequena** (Qwen3 1,7B: 5/20; 4B: 8/20, Apache 2.0) **não serve** para decidir sozinha; as regras acertam tudo.
  Gemini Nano (vem no Chrome): página de teste mandada ao Galindo (`teste-gemini-nano.html`, gerada a partir das 19 perguntas
  de data) — **aguardando o resultado dele**. Desenho combinado: script = cérebro (junta pistas), IA = neurônio (decide e
  pede informação ao script), porteiro confere a resposta contra a evidência; app funciona sem IA.
- Botão "Ativar relatórios mais inteligentes" só aparece para quem tem computador que aguenta (requisito 6).

## Combinados com o Galindo
- Teste é **resultado de primeira passada**, sem eu ajustar antes de mostrar. Erro de tipo/nome a pessoa corrige na tela;
  eu só conserto o motor quando é defeito de leitura que a tela não resolve, e **aviso antes**.
- Toda regra nova passa por teste às cegas em arquivo de outro ramo (ex.: R23 provada no `8_estoque_loja.csv`).
- Relatório do Diego fora dos testes.
- ⚖️ Decisões tomadas pela fábrica (conferir na homologação): números todos diferentes (plaqueta, patrimônio, série) = Código;
  campos quase vazios (5 de ~900) vão para a caixa "Quase vazios".

## Próximos passos (em ordem)
1. Receber o resultado do **teste do Gemini Nano** no Chrome do Galindo.
2. **Novo lote às cegas** (5 arquivos novos), rodar uma vez, mandar como sair.
3. Pendências de requisito: grupos "(2)" nomeados pelo título do trecho ("Tipo (OS relacionada)"); hora ao lado de data =
   hora do dia (não duração); nome digitado longo vira explicação; aviso de consistência entre relatórios (req. 25);
   enxugar perguntas do cabeçalho deslocado.
4. Quando o Galindo liberar: levar para a fábrica — especificação a partir de `requisitos_tela.md`, fórmula para `core.js`,
   testes Playwright a partir dos oráculos, e as tarefas: selo de versão (pedido em 26/11), melhorias da tela de colunas,
   ideia nova "IA própria da GSI para mini aplicativos" (registrar na Diretoria).
