---
applyTo: '**'
---

# 06 — CAMADA 5 — GAMEPLAY [MARGINAL]

> Lê-se junto com `00-mestre.md`. **Toda esta camada é [MARGINAL].** A auditoria recomenda questionar cada fatia antes de fazer: são features de gameplay que agregam valor, mas competem por tempo com o que realmente diferencia o MCP (Camadas 3 e 4). O critério de parada do projeto (correção manual < 15–20%) já foi atingido — nada aqui é necessário para o núcleo.

**Regra desta camada:** a IA **não implementa nenhuma fatia sem confirmação humana explícita** de que essa fatia específica deve ser feita. Ao chegar aqui, a IA lista as opções e pergunta; não escolhe sozinha.

Estas correspondem à Fase 2 do roadmap original. Formato mais enxuto, coerente com a marcação — quando uma fatia for confirmada para fazer, a spec detalhada é gerada sob demanda, como nas outras camadas.

Lembrete: se confirmada, a fatia segue todas as regras do mestre (rollup-first, autoauditoria de 6 critérios, guardrails, cross-model). Marginal não significa sem rigor — significa "confirmar antes se vale".

---

## FATIA 5.1 — Conquistas + cloud save **[MARGINAL]**
- `create_achievement_system`; `cloud_save_configure` (Steam Cloud).
- **Questionar:** o jogo vai ter conquistas/multiplataforma de save? Se é jogo pequeno/solo local, pode não valer.
- Rollup provável: `gamestate_manage` (ops).

## FATIA 5.2 — Suporte a mods **[MARGINAL]**
- `mod_manifest_generate`, `validate_mod_compatibility`.
- **Questionar:** o jogo é moddable por design? Se não, é escopo morto.
- Rollup provável: novo `mod_ops` ou op em `config_manage`.

## FATIA 5.3 — Sequenciador de cutscene/cinemática **[MARGINAL]**
- `create_cutscene_sequence` com controle de câmera.
- **Questionar:** o jogo tem cinemáticas? Liga à câmera (`camera_manage`) e animação já existentes.
- Rollup provável: op em `anim_manage`/`camera_manage`.

## FATIA 5.4 — Telemetria com opt-in + replay **[MARGINAL]**
- `analytics_event_track`, `funnel_report`; `record_replay`, `playback_replay`.
- **Questionar:** você vai analisar comportamento de jogador? Telemetria exige opt-in de privacidade (liga à conformidade 7.10). Replay pode reusar o recording que já existe.
- Rollup provável: novo `telemetry_ops`.

## FATIA 5.5 — Dificuldade adaptativa + quest/diálogo procedural + balance remoto **[MARGINAL]**
- `adaptive_difficulty_analyze`; `quest_generate`, `dialogue_branch_validate`; `remote_balance_config`.
- **Questionar:** cada um destes é um projeto de semanas se feito "de verdade" (eram Fase 3 do roadmap original). Dificuldade adaptativa liga ao playtest autônomo (3.16). Quest procedural liga ao dead-end validator (4.8). Balance remoto exige backend.
- **Aviso forte:** não fazer os três juntos. Um de cada vez, e só se o jogo justificar.

## FATIA 5.6 — Acessibilidade + certificação de plataforma **[MARGINAL]**
- Modo daltônico, legendas, remapeamento de controle; checklist de certificação (Steam, console, classificação etária).
- **Questionar:** acessibilidade tem valor real e é subestimada — se for lançar comercial, sobe de prioridade. Certificação só importa perto do lançamento.
- Rollup provável: novo `accessibility_ops`; certificação como checklist (op de leitura).

## FATIA 5.7 — Trailer/store capsule + onboarding tutorial **[MARGINAL]**
- `capture_gameplay_trailer`, `generate_store_capsule`; tutorial inicial + checagem de primeira experiência.
- **Questionar:** trailer/capsule importam perto do lançamento e da página de loja (a pesquisa: página de Steam cedo ajuda wishlist). Onboarding importa quando o jogo está jogável.
- Rollup provável: op em `vision_ops` (captura) para trailer; novo `onboarding_ops`.

## FATIA 5.8 — Pré-geração de diálogo de NPC **[MARGINAL]**
- `generate_npc_dialogue_line` (cache, **não** runtime ao vivo).
- **Questionar:** NPC com muita fala se beneficia; jogo sem diálogo, não. Pré-geração + cache (não LLM em runtime dentro do jogo, que é outro escopo).
- Rollup provável: op em `dialogue_manage`.

---

## ORIENTAÇÃO PARA A IA NESTA CAMADA

Ao chegar na Camada 5:
1. **Não implemente nada automaticamente.**
2. Liste as 8 fatias com o "questionar" de cada uma.
3. Pergunte ao humano quais (se alguma) devem ser feitas, na luz do jogo específico que ele está construindo.
4. Só para as confirmadas, gere a spec detalhada e siga o fluxo normal (rollup-first, 6 critérios, cross-model).

Lembre ao humano, se relevante: o critério de parada do projeto já foi atingido. Estas features são expansão, não necessidade. Priorizar Camadas 3 e 4 sobre esta, salvo razão específica do jogo dele.

---

*Fim da Camada 5. Próximo documento: `07-camada-6-profundidade-engine.md`.*
