# 🔄 PRÓXIMA SESSÃO — Agente 2

## Resumo
11 behaviors implementados (inventory, collectable, currency, xp_level, upgrade, quest, save_load, achievement, unlockable, pause_menu, screen_shake). 32/224 total. Grupo Progressão COMPLETO (10/10). 10 bugs corrigidos na sessão.

## Estado
- Versão: 0.2.0 | Módulos: 32 behaviors | Progresso: 14.3%
- Branch: agente2/behaviors-onda2 | Commit: 36ffa83

## Última tarefa
- #40 screen_shake v1.0.0 — Camera2D offset, trigger/duration/decay, 7 testes

## Pendências
- [ ] #41 floating_text (Feedback) — alta
- [ ] #42 impact_particles (Feedback) — média
- [ ] #43 hit_stop (Feedback) — média
- [ ] #44 main_menu (Sistema) — média
- [ ] 8+ behaviors sem .uid — baixa (Godot aberto regenera)

## Arquivos-chave
- .roadmap_progress_a2.json
- behaviors/CATALOGO_COMPLETO.md
- .github/roadmap/ONDA_2_fosso.md

## Fluxo sugerido
1. Leia HANDOFF.md e .roadmap_progress_a2.json
2. Rode validate_gdscript.py nos 11 behaviors novos
3. Continue de #41 floating_text (/plan → /act)

## Decisões da sessão
- Commit automático após /act → /memories/user_preferences.md
- Cooldown 0.5s anti-flood em sinais de falha
- Magnet autodetect via get_overlapping_bodies()

## ⚠️ Atenção
- merge-tree conflitos pré-existentes em .session/ e HANDOFF.md
- auditar.py C1/C5 falham (bug pré-existente, Agente 1)

## Estado
- Versão: 0.2.0 | Branch: agente2/behaviors-onda2 | Commit: 601b97b
- Progresso: 21/224 behaviors (9.4%)
- Grupos completos: Combate (8/8), IA/Mundo (7/7)

## Última tarefa
- spawner_wave (#24) — concluído, auditado, commitado, pushed

## Pendências
- [ ] inventory (#30) — Node, slot_count, max_stack (alta)
- [ ] collectable (#31) — Area2D, item_id, auto_pickup (alta)
- [ ] Restante do grupo Progressão (#32-#35)

## Arquivos-chave
- behaviors/ — 21 behaviors implementados
- .roadmap_progress_a2.json
- /memories/repo/padroes-de-bugs-behaviors.md — 23 padrões, 22 itens

## Fluxo sugerido
1. Leia NEXT_SESSION.md e HANDOFF.md
2. Rode validação (validate_gdscript.py nos behaviors/)
3. /plan para inventory (#30)
4. /act para implementar

## Decisões da sessão
- `_initialized` como padrão para `_ready()` em @tool
- Setters devem atualizar dependentes (Timer, Shape)
- `process_mode = DISABLED` suficiente para pooling
- Sinais declarados devem ter `.emit()` correspondente

## ⚠️ Atenção
- `_find_health` tem 8 variantes — inconsistência leve, aceitável v1
- C1 e C5 do auditar.py falham (pré-existentes, servidor)
- Godot 4.7 `--headless --script` não funciona no Windows (R12)
