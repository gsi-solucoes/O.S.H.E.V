# Raio X do Relatório — instruções para o Claude

Projeto da Fábrica GSI (dono: Galindo). Falar sempre em português do Brasil.
Repositório: `gsi-solucoes/raio-x-do-relatorio` (antes O.S.H.E.V). Link do app: https://gsi-solucoes.github.io/raio-x-do-relatorio/

## O que é
App web **estático e offline** (GitHub Pages + PWA) que lê os dados extraídos de qualquer sistema (CSV, Excel, JSON/XML, PDF e imagem), guarda no navegador e monta dashboards, KPIs e relatórios em Excel. Mais a macro Excel `excel/GeradorOS_HEV.bas` para o computador do hospital.

## Regras deste projeto (Galindo, 25/11/2026)
- **Sem dublês e sem esqueleto simulado:** não há serviço externo. Os dados de teste são CSVs reais do MV anonimizados em `tests/dados/` (nunca dados de paciente).
- **Sem servidor, sem VM, sem porta, sem IA paga, sem API:** tudo roda no navegador; o pedido escrito é entendido por regras.
- **Nada específico do hospital no código:** cliente, área e logo vêm da Config.
- Tudo que for aprovado na versão web vale também para a macro Excel (quando couber no Excel 2016).
- Documentos: `docs/00_concepcao/` (concepção, diário, como-funciona), `docs/caminho-das-estrelas.md`, especificação em `docs/01_especificacao/`, estado em `docs/03_homologacao/estado.md`.
- Build: `app.html` + `core.js` → `index.html` (core injetado em `/*CORE*/`). Testes com Playwright antes de publicar; falhou não sobe.

<!-- Bloco geral da GSI: sincronizado do gsi-infra/modelos/CLAUDE-base.md (Método 5.8). Não editar no projeto; editar a fonte. -->
## Leia primeiro (GSI)
- **Coordenador:** siga a rotina do Método GSI, seções 5.6 a 5.9 (`gsi-solucoes/gsi-infra`): ler o **resumo** `docs/METODO-RESUMO.md` (Método completo só por seção, sob demanda), a linha do projeto no `painel.md`, as tarefas ativas da `fila.md` e o estado do projeto, dizer em que passo está e qual é o próximo, e atualizar a Diretoria ao terminar.
- **Método 1.8:** app construído inteiro com dublês da caixa `gsi-solucoes/gsi-dubles` (copiados, nunca compartilhados); estrelas só no brilho. Documentos do projeto: `docs/00_concepcao/como-funciona.md` e `docs/caminho-das-estrelas.md`.

## Trabalho com a IA (Método GSI, seção 5)
- **Os 4 itens antes de qualquer tarefa:** o que quero, o que NÃO quero, como conferir antes de executar (simulação) e como conferir o resultado (oráculo: teste, contagem, acesso real).
- **Bug corrigido = teste de regressão** em `tests/` (primeiro o teste que falha, depois a correção). Regra de negócio nova = teste novo.
- **Testes rodam antes do deploy**; se falhar, não sobe.
- **IA paga só com liberação do Galindo**; por padrão, dublê de IA.
- **Senhas e chaves só pelo Galindo**, nos Secrets ou no `segredos.env` da VM; nunca pelo chat.
- Em situação crítica (dado de cliente, produção fora, algo sem volta): seguir o plano, inventário antes e conferência depois; desvio só com o Galindo.
<!-- Fim do bloco geral da GSI -->
