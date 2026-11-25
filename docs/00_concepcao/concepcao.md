# Raio X do Relatório — Concepção & Escopo

Agente 1 (Conceptor) · versão 1.0 · 25/11/2026 · aguardando portão 1

## 1. Origem
Nasceu como gerador de relatórios de OS da manutenção do HEV (O.S.H.E.V), feito em conversa de 19 a 25/11/2026, a partir dos CSVs `R_ORDEM_SERVICO` do MV. Em 25/11 o Galindo decidiu transformá-lo num produto genérico: **Raio X do Relatório**, que serve para qualquer relatório e qualquer empresa, usando o mesmo repositório e o mesmo link.

**Definição (Galindo, 25/11/2026):** O Raio X do Relatório lê os relatórios gerados por qualquer sistema (CSV, Excel e PDF), como os de ordens de serviço, e monta sozinho o painel e os relatórios que a pessoa escolher. Funciona no navegador, sem API e sem custo por uso, e serve para qualquer cliente.

## 2. Dor
- Os relatórios do ERP saem como CSV cru; montar indicadores no Excel toma horas todo mês.
- Cada cliente quer indicadores diferentes, e quem pede não sabe fórmula.
- No hospital o computador é travado (Excel 2016, sem instalar nada, internet limitada).

## 3. O que quero
1. Abrir o link (ou o app instalado), escolher um ou vários arquivos e ver na hora o que dá para tirar deles.
2. Reconhecer sozinho o relatório; se não conhecer, perguntar **"Esta coluna é o quê?"** uma vez e lembrar.
3. Tela **"O que você quer acompanhar?"** só com os indicadores que os dados permitem, com número de exemplo; o que for marcado vira bloco do dashboard; lista de registros sempre embaixo.
4. **Pedido escrito** ("quantas OS concluídas por técnico em outubro") entendido por regras, com **"É isso?"** e prévia antes de entrar.
5. **Contas personalizadas** na Config.
6. **Editar layout:** arrastar blocos, mover entre abas, criar/renomear/apagar abas, tamanho, esconder, duplicar, tipo de gráfico, voltar ao padrão.
7. **Excel** gerado seguindo o layout do usuário (capa, período, filtros).
8. Guardar o histórico no próprio aparelho, juntando os arquivos novos pelo número do registro.
9. Funcionar **offline** depois do primeiro acesso (PWA instalável).
10. Ler também XLSX e PDF com texto; OCR só como último recurso.
11. Manter tudo que já existe no modo OS (dashboard, backlog, tratativas, % fantasma, janelas, repetidas, tempos, histórico) como o **primeiro modelo pronto** ("Ordens de serviço").

## 4. O que NÃO quero
- Nada do hospital no código (nome, logo, nomes de pessoas): tudo na Config.
- Servidor, banco, login, VM, porta ou mensalidade de infraestrutura.
- IA paga ou API externa para entender o pedido.
- Enviar os dados do cliente para qualquer lugar: tudo fica no navegador.
- Perder o que já funciona no modo OS (regressão).
- Somar "aguardando material" com "conserto externo"; mudar as regras aprovadas (realizadas = concluída + material + externo + cancelada; backlog sem terceiros; ≥ 90% verde).

## 5. Serviços externos e dublês: nenhum (caminho direto, Método 1.8.4)
**Nenhum.** O app não fala com nenhum serviço externo, então não há encaixe `_MODO=simulado|real` nem dublê (decisão do Galindo, 25/11/2026: "não precisa criar o esqueleto fake"). Bibliotecas (JSZip, ExcelJS; depois leitor de PDF e OCR) ficam copiadas dentro do repositório, em `vendor/`, para funcionar offline. Dados de teste: CSVs reais do MV anonimizados.

## 6. Armazenamento (Método 2.1)
Porte: ferramenta local, dados do próprio usuário. Configuração e layouts no `localStorage`; histórico no `IndexedDB`; backup é um arquivo que o usuário baixa. Nada no Supabase/R2.

## 7. Público e onde roda
Planejador/controlador de manutenção (primeiro usuário: Galindo), gestores que recebem o Excel, e depois qualquer empresa com relatórios em CSV. Celular e computador; a macro Excel para o computador travado.

## 8. Fases
| Etapa | Conteúdo |
|---|---|
| 1 | Nome Raio X do Relatório, nada do hospital no código, PWA offline (código feito, falta testar) |
| 2 | "O que você quer acompanhar?" + dashboard montado pelos itens marcados |
| 3 | Pedido escrito com "É isso?" |
| 4 | Excel seguindo o layout |
| 5 | Contas personalizadas |
| 6 | Editar layout |
| 7 | Ler XLSX e PDF (OCR por último) |

## 9. Riscos
- Repositório é **público** (GitHub Pages grátis). O código não tem segredo nem dado; os CSVs de teste precisam ser anonimizados antes de entrar.
- O pedido escrito por regras entende frases comuns, não qualquer frase: quando não entender, mostra exemplos e não inventa.
- Macro Excel ainda não testada no Excel real do hospital.
