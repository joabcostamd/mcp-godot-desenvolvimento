---
description: Escolhe a próxima fatia do roadmap, verifica suposições contra o código real, e monta o plano com critérios de aceite. Roda no modo PLAN.
---

# /plan — Preparar a próxima fatia

**Modo obrigatório: PLAN.** Se você está em Act, pare e avise o humano para trocar. Neste workflow você **não escreve nenhum arquivo de código** — só lê, verifica e planeja.

Execute os passos abaixo em ordem. Use as caixas para marcar progresso.

---

## Passo 1 — Ler o estado atual

- [ ] Ler `.roadmap_progress.json` (se existir). **Isto vem primeiro, sempre.**
- [ ] Se a fatia atual já foi tentada: listar o que já falhou. **Abordagem que já falhou não se repete** (Governador 4.2).
- [ ] Ler `.clinerules/00-mestre.md` — seções 2 (teto), 3 (segurança), 4 (governador), 6 (critérios), 7 (fluxo).
- [ ] Identificar a próxima fatia não concluída, seguindo a ordem da seção 9 do mestre.
- [ ] Ler o documento da camada correspondente e localizar o bloco daquela fatia.

## Passo 2 — Checar a marcação antes de qualquer coisa

- [ ] **[MARGINAL]** → **NÃO planeje.** Apresente a fatia, o "questionar" dela, e pergunte ao humano se deve ser feita. Pare aqui.
- [ ] **[SÊNIOR]** → planeje normalmente, mas registre que esta fatia **não fecha sozinha** no `/act`.
- [ ] **[AUTO]** → planeje normalmente.

## Passo 3 — Verificar suposições contra o código real

Este passo é obrigatório e é o que evita a falha mais comum do modo Plan: planejar em cima de suposição errada, que só estoura na execução.

- [ ] Os "arquivos prováveis" citados no documento da camada são **palpite**, não fato. Abrir e confirmar cada um.
- [ ] Confirmar que as funções/tools/estruturas citadas existem mesmo, com o nome citado.
- [ ] Confirmar que o que a fatia quer criar **ainda não existe** (especialmente ops dentro de rollups — pode já estar lá).
- [ ] Listar explicitamente: **o que eu supus que se confirmou** e **o que caiu**.
- [ ] Se algo essencial caiu: dizer isso claramente no plano e propor o ajuste. Não conserte em silêncio.

## Passo 4 — Definir "pronto" ANTES de planejar como fazer

(Governador 4.5 — "pronto" não pode ser redefinido depois para caber no que foi feito.)

- [ ] Escrever os critérios de aceite objetivos desta fatia: os testes concretos que vão provar que ficou certo.
- [ ] Para cada critério dos 6 (mestre seção 6), declarar **qual nível será usado**: completo (ferramental existe), reduzido (ferramental ainda não existe), ou via `auditar.py` (se já existir).
- [ ] Declarar as 2–3 chamadas canary: entrada fixa e saída esperada, escritas **agora**, antes de implementar.

## Passo 5 — Montar o plano

- [ ] Passos concretos de implementação, na ordem.
- [ ] Arquivos que serão tocados (confirmados no Passo 3).
- [ ] Se a fatia toca código de feature já aprovada: marcar **reteste de regressão obrigatório** e dizer qual.
- [ ] Confirmar o caminho do rollup: a capacidade nova entra como **op de rollup**, não tool de topo (mestre seção 2, Regra 1). Se precisar ser tool de topo, justificar.
- [ ] Estimar: quantos passos, qual o orçamento desta fatia.
- [ ] Se o plano tiver mais de ~8 passos de implementação: **propor dividir a fatia em duas**, com critérios próprios cada. Fatia grande demais falha exponencialmente.

## Passo 6 — Apresentar e PARAR

- [ ] Apresentar ao humano, nesta ordem: fatia e marcação · suposições confirmadas e caídas · critérios de "pronto" · canaries declaradas · plano de implementação · reteste de regressão (se houver) · orçamento estimado.
- [ ] Terminar **exatamente** com esta frase, e nada depois dela:

> **"Plano pronto. Troque para o modo Act e digite `/act`."**

- [ ] **NÃO implemente. NÃO edite arquivo. NÃO troque de modo sozinha.** Você está em Plan; seu turno acaba aqui.

---

## Regras que valem o tempo todo neste workflow

- Você **não decide sozinha** que uma fatia está pronta — isso é o `/act` + o portão.
- Se em qualquer passo você não tiver certeza se pode prosseguir: **pare e pergunte.** Parar é barato; prosseguir errado com confiança é caro.
- Nunca planeje duas fatias de uma vez.
