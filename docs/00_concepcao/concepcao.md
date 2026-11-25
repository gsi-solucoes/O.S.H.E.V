# Raio X do Relatório — Concepção & Escopo

Agente 1 (Conceptor) · versão 1.0 · 25/11/2026 · aguardando portão 1

## 1. Origem
A estrutura nasceu num protótipo interno de leitura de relatórios feito em conversa de 19 a 24/11/2026 (leitor de arquivos, janelas clicáveis, Excel com capa, histórico, importador que aprende as colunas). Em 25/11/2026 o Galindo decidiu transformá-lo num produto genérico: **Raio X do Relatório**. Do protótipo vem só a estrutura; nenhum conteúdo, regra ou nome do caso de origem.

**Definição (Galindo, 25/11/2026):** O Raio X do Relatório lê os dados extraídos de qualquer sistema (relatórios em CSV, Excel, PDF e imagem) e monta sozinho o painel e os relatórios que a pessoa escolher. Funciona no navegador, sem API e sem custo por uso, e serve para qualquer cliente.

## 2. Dor
- Os relatórios dos sistemas saem como CSV, planilha ou PDF crus; montar indicadores no Excel toma horas todo mês.
- Cada cliente quer indicadores diferentes, e quem pede não sabe fórmula.
- Muita empresa tem computador travado (Excel antigo, sem instalar nada, internet limitada).

## 3. O que quero
1. Abrir o link (ou o app instalado), escolher um ou vários arquivos e ver na hora o que dá para tirar deles.
2. Reconhecer sozinho o relatório; se não conhecer, perguntar **"Esta coluna é o quê?"** uma vez e lembrar.
3. Tela **"O que você quer acompanhar?"** só com os indicadores que os dados permitem, com número de exemplo; o que for marcado vira bloco do dashboard; lista de registros sempre embaixo.
4. **Pedido escrito** ("quantos pedidos entregues por vendedor em outubro") entendido por regras, com **"É isso?"** e prévia antes de entrar.
5. **Contas personalizadas** na Config.
6. **Editar layout:** arrastar blocos, mover entre abas, criar/renomear/apagar abas, tamanho, esconder, duplicar, tipo de gráfico, voltar ao padrão.
7. **Excel** gerado seguindo o layout do usuário (capa, período, filtros).
8. Guardar o histórico no próprio aparelho, juntando os arquivos novos pelo número do registro.
9. Funcionar **offline** depois do primeiro acesso (PWA instalável).
10. Ler todo tipo de arquivo que der: CSV/TXT, Excel (.xlsx, .xls, .ods), JSON/XML, PDF com texto, PDF escaneado e **imagem (foto ou print, JPG/PNG) com OCR no aparelho**, e .zip com qualquer mistura. O que vem por OCR aparece para conferir antes de entrar (Galindo, 25/11/2026).
11. Reaproveitar a **estrutura** do protótipo (leitor, importador que aprende, janelas, Excel com capa, histórico, semelhança de texto, tempos entre datas, metas), sem nenhum conteúdo do caso de origem.
12. **Versão Excel para baixar** (macro) com a mesma estrutura, para quem prefere usar no PC.

## 4. O que NÃO quero
- Nada de cliente, ramo ou caso de origem no código (nomes, regras, frases, indicadores fixos): tudo nasce dos dados e da Config.
- Servidor, banco, login, VM, porta ou mensalidade de infraestrutura.
- IA paga ou API externa para entender o pedido.
- Enviar os dados do cliente para qualquer lugar: tudo fica no navegador.
- Perder a estrutura que já funciona (regressão).

## 5. Serviços externos e dublês: nenhum (caminho direto, Método 1.8.4)
**Nenhum.** O app não fala com nenhum serviço externo, então não há encaixe `_MODO=simulado|real` nem dublê (decisão do Galindo, 25/11/2026: "não precisa criar o esqueleto fake"). Bibliotecas (JSZip, ExcelJS; depois leitor de planilhas, de PDF e OCR) ficam copiadas dentro do repositório, em `vendor/`, para funcionar offline. Dados de teste: só fictícios, gerados por script.

## 6. Armazenamento (Método 2.1)
Porte: ferramenta local, dados do próprio usuário. Configuração e layouts no `localStorage`; histórico no `IndexedDB`; backup é um arquivo que o usuário baixa. Nada no Supabase/R2.

## 7. Público e onde roda
Qualquer pessoa ou empresa que tira relatórios de um sistema e precisa de indicadores: quem monta, quem recebe o Excel, quem apresenta. Celular e computador; a versão Excel para quem prefere usar no PC.

## 8. Fases
| Etapa | Conteúdo |
|---|---|
| 1 | Nome Raio X do Relatório, nada do caso de origem no código, PWA offline, versão Excel para baixar |
| 2 | "O que você quer acompanhar?" + dashboard montado pelos itens marcados |
| 3 | Pedido escrito com "É isso?" |
| 4 | Excel seguindo o layout |
| 5 | Contas personalizadas |
| 6 | Editar layout |
| 7 | Ler Excel, JSON/XML, PDF e imagem (OCR) |

## 9. Riscos
- Repositório é **público** (GitHub Pages grátis). O código não tem segredo nem dado; dados de teste só fictícios.
- O pedido escrito por regras entende frases comuns, não qualquer frase: quando não entender, mostra exemplos e não inventa.
- Macro Excel ainda não testada num Excel 2016 real.
