# 🤝 HANDOFF — Comunicação entre Agentes

> **Regra:** Ao finalizar cada etapa, o agente ATUALIZA este arquivo
> para que o outro agente saiba o estado do projeto na próxima sessão.

## Último Handoff (AGENTE 02 — 2026-07-21 — ONDA 2: 11 behaviors)

- **Data:** 2026-07-21
- **De:** AGENTE 02 (Conteúdo — behaviors)
- **Branch:** `agente2/behaviors-onda2`
- **Ação:** 11 behaviors implementados na sessão — 32/224 total

### O que foi feito

| # | Behavior | Node | Destaque |
|---|---|---|---|
| 30 | `inventory` | Node | Slots, max_stack, sinais delta, 30 testes v1.0.1 |
| 31 | `collectable` | Area2D | Auto_pickup, magnet autodetect, cooldown, 19 testes v1.0.1 |
| 34 | `currency` | Node | add/spend/can_afford, currency_type, 18 testes |
| 32 | `xp_level` | Node | xp_table, multilevel up, 18 testes |
| 33 | `upgrade` | Node | Survivors-like, XPLevel.leveled_up, 12 testes |
| 35 | `quest` | Node | Objectives collect/spend, auto-track, rewards, 13 testes |
| 38 | `save_load` | Node | ConfigFile, Inventory/Currency/XPLevel, 12 testes v1.0.1 |
| 36 | `achievement` | Node | collect/currency/level conditions, 9 testes |
| 37 | `unlockable` | Node | Metaprogression, achievement/level/currency, 7 testes |
| 39 | `pause_menu` | Node | get_tree().paused, ui_cancel input, 6 testes |
| 40 | `screen_shake` | Node | Camera2D offset, trigger/duration/decay, 7 testes |

### Métricas

- **Total:** 32/224 behaviors
- **Grupos concluídos:** Combate ✅, IA/Mundo ✅, Progressão ✅ (10/10)
- **Grupos em progresso:** Sistema (2/6: save_load, pause_menu), Feedback (1/4: screen_shake)
- **Bugs corrigidos na sessão:** 10 (C1-C2-M3-M4-B5 no inventory, C1-M2-B3-B4 no collectable, M1-B2 no save_load)
- **Commits:** 10

### ⚠️ Pontos de atenção para AGENTE 01

- Nenhum arquivo do território do Agente 1 foi alterado
- `.roadmap_progress_a2.json` atualizado com 32 behaviors
- 8 behaviors sem `.uid`: enemy_patrol, flee, flocking, inventory, line_of_sight, object_pool, spawner_wave, turret_aim + novos
- Próximo: `floating_text` (#41) — Feedback
- **Padrões registrados:** 23 (em `/memories/repo/padroes-de-bugs-behaviors.md`)
- **Checklist:** 22 itens de verificação pré-implementação
- **Commits:** 9

### ⚠️ Pontos de atenção para AGENTE 01

- Nenhum arquivo do território do Agente 1 foi alterado
- `.roadmap_progress_a2.json` atualizado com 21 behaviors
- `spawner_wave` (#24) destravado após `object_pool` (#47)
- Próximo: `inventory` (#30) — Progressão

---

## Último Handoff (AGENTE 01 — 2026-07-20 — ONDA 0: ✅ 12/12)

- **Data:** 2026-07-20
- **De:** AGENTE 01 (Arquitetura & Core)
- **Ação:** Fatias 0.I, 0.J, 0.K, 0.L + correções cross-cutting + `/auditar` turbinado

### O que foi feito

| Fatia | Descrição | Arquivo |
|---|---|---|
| 0.I | Cloud sync detector (3 camadas) | `tools/cloud_sync_detector.py` (NOVO) |
| 0.J | Name normalizer (NFKD+ASCII) | `tools/name_utils.py` (NOVO) |
| 0.K | IP guard (80+ franquias) | `tools/ip_guard.py` (NOVO) |
| **0.L** | **Bug set/get_node_property** | `tools/scene_ops.py` (FIX) |
| — | Handler factory (38→1) | `server.py` (refactor) |
| — | C1 bug fix (indentação) | `server.py` (fix) |
| — | `/auditar` 12 fases auto | user-level prompt (modificado) |

### 0.L — Detalhe técnico

**Causa raiz:** `set_node_property()` modificava `lines` em memória mas nunca
chamava `full_path.write_text()`. Comparado com `add_node()` e `delete_node()`
que têm o padrão completo: checkpoint → modificar → deduplicar → **write_text**
→ cache.pop → mark_pending_compile.

**Correção:** +7 linhas após `_deduplicate_tscn_lines()`.
**B3 extra:** removidos 2x `import re` redundantes dentro de `_deduplicate_tscn_lines`.

### Métricas

- **Total tools:** 274 (sem alteração)
- **Handlers:** 295 (sem alteração)
- **Novos arquivos:** cloud_sync_detector.py, name_utils.py, ip_guard.py
- **Arquivos expandidos:** server.py, project_ops.py, project_brief_ops.py, art_ops.py, tool_definitions.py, scene_ops.py
- **ONDA 0:** ✅ 12/12 CONCLUÍDA

### ⚠️ Pontos de atenção para AGENTE 02

- `_make_import_handler()` substituiu 38 handlers Camada 6 — se adicionar tool nova nesse domínio, use a factory
- IP guard é fail-open: nunca bloqueia o servidor
- Cloud sync detector integrado em server.py, install.py, launch.py
- C1 do auditar.py mostra 7 breaking (falso positivo da factory)
- **ONDA 0 fechada.** Próximo: ONDA 1 — Acessibilidade (fatia 1.A: instalador de um comando)

### Próximo passo (AGENTE 01)
- **ONDA 1 — 1.A: Instalador de um comando (`init`)** [SÊNIOR]

---

- **Data:** 2026-07-19
- **De:** AGENTE 01 (Arquitetura & Core)
- **Ação:** Implementação COMPLETA da Camada 6 — Profundidade de Engine (8/8 fatias)

### O que foi feito

| Fatia | Descrição | Arquivo |
|---|---|---|
| 6.1 | Skeleton IK / Bone Pose (6 ops) | `tools/skeleton_ops.py` (NOVO) |
| 6.2 | 3D Depth — CSG, GI, Decal, Sky, Camera, MultiMesh (6 ops) | `tools/devsolo_ops.py` (expandido) |
| 6.3 | Física — Joints, Body Config, Area Query, Raycast (4 ops) | `tools/physics_ops.py` (expandido) |
| 6.4 | UI Granular — Widgets, Tabs, Focus Nav, Tooltip, Anchors (5 ops) | `tools/devsolo_ops.py` (expandido) |
| 6.5 | Rede — Multiplayer, RPC, WebSocket, Lobby (5 ops) | `tools/network_ops.py` (NOVO) |
| 6.6 | Runtime Signals — Connect, Disconnect, Emit, List, Watch (5 ops) | `tools/runtime_ops.py` (expandido) |
| 6.7 | Render Settings — AA, Scaling, Quality Presets (4 ops) | `tools/render_ops.py` (NOVO) |
| 6.8 | C#/.NET Scaffold — Project, Script Templates, Build (3 ops) | `tools/csharp_ops.py` (NOVO) |

### Métricas

- **Total tools:** 268 → 274 (+6)
- **Handlers:** 295 → 306 (+11, incluindo rollups)
- **Novos arquivos:** `skeleton_ops.py`, `network_ops.py`, `render_ops.py`, `csharp_ops.py`
- **Arquivos expandidos:** `devsolo_ops.py`, `physics_ops.py`, `runtime_ops.py`
- **Validação:** 274 tools, 306 handlers, 0 inconsistencias (32 extras = rollups)

### Distribuição por namespace
- **project** (31): skeleton (6), 3D depth (6), physics joints/body (2), UI granular (5), network (5), render (4), csharp (3)
- **runtime** (5): physics queries (2), runtime signals connect/disconnect/emit (3)
- **analysis** (2): runtime signal list/watch (2)

### ⚠️ Pontos de atenção para AGENTE 02
- `skeleton_ops.py` opera por parsing de arquivos .tscn — se mudar formato de scene, revise
- `network_ops.py` e `csharp_ops.py` geram código GDScript/C# — templates podem precisar de ajuste
- Handlers usam dispatch dinâmico por prefixo (ex: `skeleton_*` → `skeleton_ops`) — se renomear funções, mantenha consistência
- Camada 6 é [MARGINAL] — risco de scope creep. Documentado como "Campo A" no roadmap.

### Próximo passo (AGENTE 01)
- **Camada 7 (Polimento)**: [MARGINAL] — aguarda aprovação do Joab

---

## Último Handoff (AGENTE 01 — 2026-07-19 — Registro Camada 5)

- **Data:** 2026-07-19
- **De:** AGENTE 01 (Arquitetura & Core)
- **Ação:** Registro de 28 tools da Camada 5 (Gameplay) no pipeline de tools

### O que foi feito

| Fase | Descrição | Arquivo |
|---|---|---|
| 1 | +28 Tool() definitions | `core/tool_definitions.py` |
| 2 | +28 handler wrappers | `server.py` (_build_handlers + _handle_*) |
| 3 | +28 nomes nos namespaces | `server.py` (TOOLSETS), `tools/dynamic_groups.py` (GROUPS) |
| 4 | Validação | `validate_tool_registry_consistency()` → 268/268 = 0 inconsistências |

### Distribuição por namespace
- **project** (16): achievements (2), mods (1), cutscenes (3), quest, dialogue (2), accessibility (3), onboarding (2)
- **analysis** (10): validate_achievement, validate_mod, telemetry (4), adaptive, accessibility_audit, cert, onboarding_check
- **assets** (3): trailer (3)
- **orchestration** (1): remote_balance_config

### ⚠️ Pontos de atenção para AGENTE 02
- **28 tools NÃO estão no PHASE_TOOLSETS** — aparecem apenas via `--profile full` ou `--toolsets` explícito
- Cabe ao AGENTE 02 decidir em quais fases ativar cada tool
- Handlers são wrappers finos que delegam para `tools/*_ops.py` — se renomear funções lá, atualize os wrappers
- `dialogue_generate_npc_lines` e `dialogue_generate_personality` já existiam como funções — foram apenas registradas formalmente

### Próximo passo (AGENTE 01)
- **Camada 6 (Profundidade de Engine)**: [MARGINAL] — aguarda aprovação do Joab
- **Camada 7 (Polimento)**: [MARGINAL] — aguarda aprovação do Joab

---

## Último Handoff (AGENTE 02 — 2026-07-19 — Sessão de Polimento)

- **Data:** 2026-07-19
- **De:** AGENTE 02 (Extensões & Qualidade)
- **Ação:** Polimento completo — 7 fases implementadas

### O que foi feito (resumo)

| Fase | Nome | Resultado |
|---|---|---|
| F1 | Diagnóstico | 51% coverage, 18 tools sem teste |
| F2 | Cobertura Tier-1 | +18 handlers sintéticos → 87.8% (100% excl skip), 0 tools sem cobertura |
| F3 | Regressão Visual | `manage_visual_baselines()`, threshold calibrado, `--visual` no `auditar.py` |
| F4 | Perf Regression | Handler sintético, `perf_regression_track` já existia em `perf_ops.py` |
| F5 | Canary Queries | 14 → 48 queries, 45 tools cobertas |
| F6 | Audio Engine | `tools/audio_ops.py` (fachada unificada), play/set/stop no runtime bridge |
| F7 | Documentação | HANDOFF, NEXT_STEP, roadmap atualizados |

### Arquivos modificados/criados
- `tools/test_ops.py` — +18 handlers sintéticos, +40 `_SYNTHETIC_HANDLERS`
- `tests/canary_queries.json` — 14 → 48 queries
- `tools/runtime_ops.py` — `manage_visual_baselines()`, thresholds documentados
- `auditar.py` — `--visual`, `C7_visual`
- `tools/audio_ops.py` — NOVO, fachada unificada de áudio
- `runtime_bridge_client.py` — `play_audio()`, `set_volume()`, `stop_audio()`
- `addons/mcp_runtime_bridge/runtime_bridge.gd` — comandos de áudio em GDScript

### ⚠️ Pontos de atenção para AGENTE 01
- `_SYNTHETIC_HANDLERS` expandido de 21 → 40 tools — se adicionar tool nova, considere adicionar handler também
- `auditar.py` ganhou C7_visual — se modificar a assinatura de `run_audit()`, inclua os parâmetros `visual*`
- `audio_ops.py` reexporta de `devsolo_ops.py`, `music_ops.py`, `tts_ops.py`, etc. — se renomear funções nesses arquivos, atualize a fachada

### Próximo passo (AGENTE 02)
- **Camada 5 (Gameplay)**: TODAS [MARGINAL] — aguarda aprovação do Joab

---

## Último Handoff (AGENTE 01)
- **Data:** 2026-07-19
- **De:** AGENTE 01 (Arquitetura & Core)
- **Etapas concluídas:** A1 (Namespaces) + A2 (ExecutionContext) + A3 (DATA_CONTRACTS)

### O que foi feito (A3)
- **`DATA_CONTRACTS.md`** (novo): Contrato formal entre agentes — ZERO código
  - **6 seções**: Tool Definition, Handler, Pipeline, Comunicação, Nomenclatura, Validação
  - Documenta o ciclo completo: `Tool()` → filtros → `call_tool` → handler → resposta
  - Inclui contratos das Etapas A1 (5 namespaces, `TOOLSETS`, `TOOL_NAMESPACES`) e A2 (`ExecutionContext`, thread-local, cache TTL)
  - Define regras para AGENTE 02 adicionar tools (onde mexer, onde NÃO mexer)
  - Especifica Zona de Sutura (arquivos congelados)
  - Referência canônica para ambos os agentes

### O que foi feito (A2)
- **`core/context.py`** (novo): `ExecutionContext` dataclass com thread-local storage
  - Campos: `active_project`, `active_scene`, `phase`, `vibe_enabled`, `vibe_focus_node`
  - Cache TTL 5s para `scene_tree` (evita re-resolução a cada chamada)
  - API: `resolve_execution_context()`, `get_execution_context()`, `set_execution_context()`
- **`server.py`**: `_dispatch_with_context` wrapper no `call_tool` injeta contexto antes de cada handler
  - Contexto resolvido UMA vez por tool, disponível via `get_execution_context()`
- **`tools/scene_ops.py`**: `_resolve_scene_path_from_vibe()` estendido para consultar `ExecutionContext`
  - `paint_tilemap_cell` e `detect_offscreen_elements` ganharam fallback (eram as únicas sem)
  - `scene_path` agora é `str | None = None` com resolução automática
- **`tools/code_quality_ops.py`**: SyntaxError corrigido (f-string com escape inválido) — bloqueava `import server`
- **Gate**: `scene_manage(op="create")` funciona SEM parâmetro `scene_path`

### O que foi feito (A1)
- **TOOLSETS reestruturado** em 5 namespaces semânticos (239 tools mapeadas):
  - `project` (51 tools) — Cenas, scripts, arquivos, UI, gameplay estrutural
  - `assets` (37 tools) — Arte, áudio, shaders, VFX, geração procedural
  - `runtime` (77 tools) — Execução, debug, testes, bridge, jogo rodando
  - `analysis` (29 tools) — Auditoria, qualidade, referências, introspecção
  - `orchestration` (45 tools) — Meta-tools, workflow, governança, segurança
- **TOOL_NAMESPACES**: Dicionário reverso (239 tool_name → namespace) derivado do TOOLSETS
- **Injeção de namespace**: Cada `Tool()` recebe `_meta={"namespace": "..."}` via pós-processamento
- **`tools/dynamic_groups.py`**: `GROUPS` sincronizado (239 tools); `NAMESPACE_INFO` com descrições PT-BR; `tool_groups` suporta `action="hierarchy"`; `tool_catalog` suporta `namespace`
- **Auditoria**: 28 problemas encontrados e corrigidos (14 órfãs, 1 rollup não mapeado, 13 inconsistências) — agora 0 problemas
- Arquivos: `server.py`, `tools/dynamic_groups.py`, `ROADMAP_UNIFICADO.md`, `HANDOFF.md`, `NEXT_STEP.md`

### O que NÃO foi feito
- NÃO modifiquei `tools/deprecated.py`, rollups, ou handlers
- NÃO mudei o comportamento de `--profile` ou `--toolsets`
- A duplicação `TOOLSETS` ↔ `GROUPS` é conhecida (239 tools idênticas) — futura refatoração pode unificar

### ⚠️ Pontos de atenção para AGENTE 02
- `GROUPS` antigo (13 grupos) foi substituído por 5 namespaces — se houver referências aos grupos antigos, atualizar
- `tool_catalog` agora retorna `namespace` em cada resultado e `namespace_info` no envelope
- `tool_groups("hierarchy")` retorna visão hierárquica: namespace → descrição → tools
- Novas tools adicionadas ao `TOOLSETS` automaticamente recebem namespace; novas tools também devem ser adicionadas ao `GROUPS` em `dynamic_groups.py`

### Próxima etapa (AGENTE 01)
- **A2 — ExecutionContext**: Criar `core/context.py` com `ExecutionContext` dataclass

---

## Histórico

### AGENTE 02 — B3 (2026-07-19) ✅ Testado com gdtoolkit 4.5.0 real
- Criado `tools/code_quality_ops.py` (~570 linhas) com gdlint + gdformat + gdradon
- `.gdlintrc` reescrito em YAML (formato correto do gdlint 4.5.0)
- Gate integrado no `run_verification_pipeline` (etapa 6)
- 19/19 testes passaram (T1-T6) com projeto real (max-manos-like)
- Gate detectou: 569 violações gdlint, 89 arquivos mal formatados, avg CC=2.2
- 4 bugs de CLI corrigidos (--config, --show-complexity, PATH, SyntaxWarning)
- `tests/test_code_quality_ops.py` criado com 19 testes automatizados

### AGENTE 02 — B2 (2026-07-19)
- Criado `.github/workflows/verification.yml` — CI com 7 jobs
