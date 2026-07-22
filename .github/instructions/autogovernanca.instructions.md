---
applyTo: '**/*.py'
---

# Protocolo de Autogovernança — Regras Mecânicas

> Extraído do extinto `PROTOCOLO_AUTOGOVERNANCA.md`.
> Regras curtas/universais foram para `copilot-instructions.md`.
> Aqui ficam os checklists mecânicos extensos.

---

## AUTO-CHECKPOINT (AC1-AC9) — rodar antes de TODO commit

```
AC1 — ESTADO: O .roadmap_progress.json reflete a fatia que EU ACABEI
     de fazer, não a que eu pretendia fazer?

AC2 — NÚMEROS ANTES E DEPOIS: Rodei audit_registro.py ANTES e DEPOIS.
     Tenho os dois outputs.

AC3 — O QUE EU ESCONDI VERSUS O QUE EU CORRIGI: Se um número "melhorou",
     foi por correção real ou por ocultação de métrica?

AC4 — COBERTURA REAL: Se substituí/consolidei capacidade, EU EXECUTEI
     o substituto e colei o resultado literal.

AC5 — EFEITOS COLATERAIS EM GATES: Testei pelo menos 1 caminho que
     passa por CADA gate afetado.

AC6 — REGRESSÃO COMPLETA: Rodei a suite INTEIRA depois da última mudança.

AC7 — ALEGAÇÃO DE PRÉ-EXISTÊNCIA: Provei com git blame/log antes de
     aceitar "isso já estava assim".

AC8 — O QUE EU NÃO TESTEI: Liste explicitamente como "NÃO TESTADO: motivo".

AC9 — COMPARAÇÃO COM O ROADMAP: Conferi cada critério de aceite, item
     por item, com prova específica.
```

Se qualquer AC falhar, a fatia não está pronta.

---

## GATE DE FASE (GF1-GF5) — obrigatório em consolidação/rename/migração

```
GF1. Liste fases da(s) tool(s) ANTIGA(s) em PHASE_TOOLSETS.
GF2. Liste fases do rollup/substituto NOVO.
GF3. Toda fase do GF1 está coberta pelo GF2?
     SIM → documentar. NÃO → é regressão, corrigir.
GF4. Se GF1 = nenhuma fase (órfã): isso é bug ou é genuinamente auxiliar?
     Se não for óbvio → BACKLOG, não decida sozinho.
GF5. Teste o caminho completo: chame a tool pelo nome antigo (alias) ou
     novo, na fase atual, e confirme que o erro é de pré-condição, não
     de gate/registro.
```

---

## SINAIS DE ESCALAÇÃO (S1-S4) — objetivos, mecânicos

```
S1 — Substituiu script/mecanismo de auditoria sem commit dedicado → ESCALAR.
S2 — Métrica caiu a 0 ou perto de 0 em uma fatia (>10 itens) → rodar
     AUTO-CHECKPOINT completo antes de reportar sucesso.
S3 — Precisou de 2+ tentativas para fechar fatia verde → documentar no
     relatório (não omitir).
S4 — Dois arquivos de estado/progresso divergem → PARE, investigue ambos
     antes de decidir qual é fonte de verdade.
```

---

## RELATÓRIO DE FIM DE FASE — 9 seções obrigatórias

```
1. NÚMEROS (antes → depois, medidos)
2. QUEDAS GRANDES (>5 itens) — resultado P1/P2/P3 para cada
3. AUTO-CHECKPOINT — último AC1-AC9
4. GATE-FASE — GF1-GF5 para cada grupo consolidado
5. NÃO TESTADO — lista explícita
6. TENTATIVAS_FALHAS — fatias com 2+ tentativas
7. DECISÕES E IMPROVISOS — tudo fora do roadmap
8. AUDITORIA FORMAL — última linha de audit_fase.py
9. PRÓXIMA FASE — qual é + itens de BACKLOG gerados
```

---

## HIERARQUIA DE PROVA

```
NÍVEL 1 (mais forte) — Execução real, output colado literal
NÍVEL 2 — Teste automatizado rodando, output colado literal
NÍVEL 3 — Leitura de código com prova de que está no caminho ativo
NÍVEL 4 (mais fraco) — Leitura de código isolada (só com etiqueta
         "NÃO EXECUTADO — leitura estática")
```

Nunca reportar Nível 3/4 com confiança de Nível 1.
