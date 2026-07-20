---
description: "Use when: planejar a próxima fatia do roadmap, verificar suposições contra o código real, montar plano com critérios de aceite. Este é o comando /plan — NÃO edita arquivos, só lê, verifica e planeja."
---
# /plan — Preparar a próxima fatia

**Modo: Planejamento.** Neste comando você **não escreve nenhum arquivo de código** — só lê, verifica e planeja. Use o modo Plan do Copilot quando disponível.

Execute os passos abaixo em ordem.

---

## Passo 1 — Ler o estado atual

1. Ler `.roadmap_progress.json` (se existir). **Isto vem primeiro, sempre.**
2. Se a fatia atual já foi tentada: listar o que já falhou. **Abordagem que já falhou não se repete.**
3. Ler `.clinerules/00-mestre.md` (se existir no projeto) ou `.github/copilot-instructions.md` — seções de teto, segurança, governador, critérios, fluxo.
4. Identificar a próxima fatia não concluída, seguindo a ordem do roadmap.
5. Ler o documento da camada correspondente (ex: `.clinerules/01-camada-0-*.md`) e localizar o bloco daquela fatia.

## Passo 2 — Checar a marcação antes de qualquer coisa

- **[MARGINAL]** → **NÃO planeje.** Apresente a fatia, o "questionar" dela, e use `vscode_askQuestions` para perguntar ao humano se deve ser feita. Pare aqui.
- **[SÊNIOR]** → planeje normalmente, mas registre que esta fatia **não fecha sozinha** no `/act`.
- **[AUTO]** → planeje normalmente.

## Passo 3 — Verificar suposições contra o código real

Este passo é obrigatório e é o que evita a falha mais comum: planejar em cima de suposição errada.

1. Os "arquivos prováveis" citados no documento da camada são **palpite**, não fato. Use `read_file` ou `grep_search` para confirmar cada um.
2. Confirmar que as funções/tools/estruturas citadas existem mesmo, com o nome citado.
3. Confirmar que o que a fatia quer criar **ainda não existe** (especialmente ops dentro de rollups — pode já estar lá).
4. Listar explicitamente: **o que eu supus que se confirmou** e **o que caiu**.
5. Se algo essencial caiu: dizer isso claramente no plano e propor o ajuste. Não conserte em silêncio.

## Passo 4 — Definir "pronto" ANTES de planejar como fazer

"Pronto" não pode ser redefinido depois para caber no que foi feito.

1. Escrever os critérios de aceite objetivos desta fatia: os testes concretos que vão provar que ficou certo.
2. Para cada um dos 6 critérios de autoauditoria, declarar **qual nível será usado**:
   - **Completo** — ferramental existe (`auditar.py`, smoke_test, etc.)
   - **Reduzido** — ferramental ainda não existe, fazer verificação manual
   - **Via `auditar.py`** — se o script existir e cobrir este critério
3. Declarar as 2–3 chamadas canary: entrada fixa e saída esperada, escritas **agora**, antes de implementar.

### Os 6 Critérios de Autoauditoria

| # | Nome | O que verifica |
|---|---|---|
| C1 | Contrato | Schema não driftou (só a tool/op nova aparece no diff) |
| C2 | Canary | 2-3 chamadas conhecidas com entrada/saída esperada |
| C3 | Regressão | `smoke_test` — nada que passava antes quebrou |
| C4 | Segurança | Checklist binária (loopback, idempotência, segredos, rollup path) |
| C5 | Orçamento | Teto de tools ≤40/fase, ≤70 total |
| C6 | Distinguibilidade | Tool nova não se confunde com nenhuma existente |

## Passo 5 — Montar o plano

1. Passos concretos de implementação, na ordem.
2. Arquivos que serão tocados (confirmados no Passo 3).
3. Se a fatia toca código de feature já aprovada: marcar **reteste de regressão obrigatório** e dizer qual.
4. Confirmar o caminho do rollup: a capacidade nova entra como **op de rollup**, não tool de topo. Se precisar ser tool de topo, justificar.
5. Estimar: quantos passos, qual o orçamento desta fatia.
6. Se o plano tiver mais de ~8 passos de implementação: **propor dividir a fatia em duas**, com critérios próprios cada. Fatia grande demais falha exponencialmente.

## Passo 6 — Apresentar e PARAR

Apresentar ao humano, nesta ordem:

1. **Fatia e marcação** — qual é, [AUTO]/[SÊNIOR]/[MARGINAL]
2. **Suposições** — confirmadas e caídas
3. **Critérios de "pronto"** — como saber que acabou
4. **Canaries declaradas** — entradas e saídas esperadas
5. **Plano de implementação** — passos em ordem
6. **Reteste de regressão** — se houver
7. **Orçamento estimado** — passos e arquivos

Terminar **exatamente** com esta frase, e nada depois dela:

> **"Plano pronto. Digite `/act` para implementar."**

**NÃO implemente. NÃO edite arquivo.** Seu turno acaba aqui.

---

## Regras que valem o tempo todo neste comando

- Você **não decide sozinho** que uma fatia está pronta — isso é o `/act` + o portão de auditoria.
- Se em qualquer passo você não tiver certeza se pode prosseguir: **pare e use `vscode_askQuestions`.**
- Nunca planeje duas fatias de uma vez.
- Se não existir `.roadmap_progress.json` no projeto: informe o humano e pergunte se deve criar um novo ou se este projeto não segue o sistema de fatias.
