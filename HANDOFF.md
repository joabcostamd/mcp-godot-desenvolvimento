# 🤝 HANDOFF — Comunicacao entre Agentes

> **Regra:** Ao finalizar cada etapa, o agente ATUALIZA este arquivo.

## ULTIMO HANDOFF (AGENTE 02 — 2026-07-22 — ENCERRAMENTO: TERRITORIO COMPLETO)

- **Data:** 2026-07-22
- **De:** AGENTE 02 (Conteudo)
- **Branch:** `agente2/behaviors-onda2`
- **Acao:** 14 commits. Territorio AGENTE 02 COMPLETO nas ONDAS 0-4.

### RESUMO EXECUTIVO

Sessao de ~12 horas. Partimos de ONDA 2 com 29/50 (58%).
Entregamos +13 fatias. Placar final: ONDA 2: 42/50 (84%) · ONDA 3: 10/11 (91%) · ONDA 4: 6/7 (86%).
Territorio Agente 02 ESGOTADO — todas as fatias restantes sao Agente 01 (reorganizacao de tools/server.py).

### COMMITS (14)

`9b1fa62` 2.AV: Editor Visual BT (~2620 linhas GDScript, 16 features)
`f846c0c` 2.AW: AssetLib Prep (plugin.cfg, README PT/EN, LICENSE, CHANGELOG)
`af1bcda` Auditoria #1: 11 bugs corrigidos
`62e4e16` 2.AX: +4 Jogos-Exemplo (33 arquivos)
`e2732dd` Auditoria #2: 3 bugs + 2 TODOs (graph->inspetor wiring)
`291e0e0` 2.AL+2.AM: Style Kit (290 linhas) + Asset Security (280 linhas)
`622cd58` 2.AE+2.AF+2.AK+2.AS: +4 fatias (RAG, Entity, Recipes, Seeds)
`e946f6f` 4 modulos registrados + 5 templates de projeto
`766a222` 3 bloqueantes: .tres cross_save + bridge client + docs/
`6792f17` ONDA 3+4: playtest personas, modo professor, revisor adversarial, terreno
`8b27776` Dashboard saude + Grafo dependencias + Guia migracao + Seed
`bbf58e8` Qualidade enterprise: Score 7/7 confirmado, fixer script, limpeza
`00e0fe8` NEXT_STEP atualizado + handoff
`[HEAD]`  Documentacao completa + README + CHANGELOG

### ARQUIVOS NOVOS (~60)

addons/mcp_bt_editor/ (10) · tools/style_kit.py · tools/asset_security.py
tools/fix_recipes.py · tools/reproducibility_seed.py
example_project/ (33) · templates/ (6) · seeds/survivors_like.json
docs/ (5 novos) · scripts/ (4 novos) · .github/ (3 novos)
addons/mcp_runtime_bridge/runtime_bridge_client.gd
behaviors/cross_save/cross_save.tres · tests/playtest_personas.json
BRAND.md · .github/FUNDING.yml

### INDICADORES FINAIS

Behaviors: 249/249 Score 7/7 · Tools MCP: 285+
Jogos-exemplo: 4 · Templates: 5 · Seeds: 4 · Blueprints: 3
Docs: 7 arquivos · Scripts: 9 · validate_gdscript: ALL PASS
3 auditorias: 25 bugs -> 25 corrigidos

### PARA O AGENTE 01

8 fatias ONDA 2 pendentes (2.C, 2.AH, 2.AI, 2.AJ, 2.AN, 2.AO, 2.AT, 2.AU).
Todas tocam server.py ou reorganizacao de tools.
4 escaladas ONDA 3 (musica 3.1-3.4).
README.md e CHANGELOG.md atualizados com numeros reais.

### PASSO O BASTAO



### RESUMO EXECUTIVO

Editor Visual de Behavior Trees 100% GDScript implementado.
10 arquivos em `addons/mcp_bt_editor/` — ~2.600 linhas GDScript total.
16 features implementadas conforme ficha em `.github/roadmap/ONDA_2_fosso.md`.
Integracao com 5 sistemas existentes: discover_behaviors, mcp_dock WebSocket 9082,
.tres Resource, behavior.json, e behavior_tree.gd executor.

### ARQUIVOS NOVOS (10)

addons/mcp_bt_editor/: plugin.cfg, README.md, generate_icons.gd
bt_editor_plugin.gd (318 linhas), bt_editor_node.gd (210 linhas),
bt_editor_palette.gd (369 linhas), bt_editor_graph.gd (578 linhas),
bt_editor_inspector.gd (340 linhas), bt_editor_serializer.gd (311 linhas),
bt_editor_debugger.gd (458 linhas), bt_tree_resource.gd (25 linhas)

### 16 FEATURES IMPLEMENTADAS

1. Dock abre/fecha (EditorPlugin) · 2. Paleta com 249 behaviors (DirAccess + JSON)
3. Drag-drop paleta→grafo · 4. 4 tipos de porta coloridos (FLOW/CONDITION/DATA/EVENT)
5. Validacao de conexoes + deteccao de ciclos (DAG) · 6. Reroute nodes
7. Expression nodes (GDScript inline) · 8. Auto-Arrange hierarquico
9. Show Generated Code · 10. Undo/Redo (EditorUndoRedoManager)
11. Preview ao vivo (WebSocket 9082) · 12. Drag-from-Port → Add Node dialog
13. GraphFrame nativo · 14. Minimap ativado · 15. Breakpoints visuais
16. Watch Window (valores de variaveis em tempo real)

### VALIDACAO

validate_gdscript.py: 8/8 arquivos PASS
Regras R1, R2, R9, R19: todas respeitadas
Falsos positivos do analisador (call() com has_method() guard): 3 ocorrencias documentadas

### FONTES CITADAS (12)

Godot 4.7 Docs: GraphEdit, GraphNode, EditorPlugin, EngineDebugger,
EditorUndoRedoManager, GraphFrame, VisualShader · LimboAI v1.8.0 ·
mcp_dock (WebSocket 9082) · behavior.schema.json · discover_behaviors ·
behavior_tree.gd executor

### PROXIMA SESSAO

1. **2.AW** — Preparar estrutura para AssetLib (plugin.cfg, icone, screenshots) [AUTO]
2. **2.AX** — +4 jogos-exemplo [SENIOR]
3. Resolver escaladas ONDA 2 (decisao Joab)

### ARQUIVOS CRITICOS ATUALIZADOS

.roadmap_progress.json (fatia_2.AV: concluida) · HANDOFF.md (este arquivo)
addons/mcp_bt_editor/ (10 arquivos novos)

---

## ULTIMO HANDOFF (AGENTE 02 — 2026-07-21 — ENCERRAMENTO: 15 FATIAS ONDA 2)

- **Data:** 2026-07-21
- **De:** AGENTE 02 (Conteudo — behaviors)
- **Branch:** `agente2/behaviors-onda2`
- **Acao:** 15 fatias ONDA 2 + auditoria completa + pesquisa editor visual (4 niveis)

### RESUMO EXECUTIVO

Sessao dedicada a fechar o maximo possivel da ONDA 2 (O Fosso).
Partimos de 11/47 concluidas. Entregamos +18 fatias. Placar final: 29/50.
249 behaviors em qualidade maxima. +7 modulos de infraestrutura.
+1 tool MCP (discover_behaviors). +3 fatias novas (2.AV, 2.AW, 2.AX).
16 features documentadas para o editor visual — 100% GDScript nativo.

### COMMITS (15)

`a10ebfd` 2.A: class_name · `08e6497` 2.B: exports · `9b9868b` 2.C: doc headers
`bf4efa1` 2.D: bugs+testes · `b2c4791` 2.E: discover_behaviors · `69b2bdd` 2.F: 66 testes
`27ea2e9` auditoria ONDA 2 · `58ffe61` FASE 1 (C8+seed+desc) · `ff5eac4` FASE 2 (.tres+CHANGELOG+seeds)
`bcf01be` +7 modulos (RAG, entity index, live, contexto, modelo, undo)
`57dd0e9` +3 fatias (2.AV, 2.AW, 2.AX) · `8e0b473` fichas expandidas
`b1336f1` pesquisa VisualShader · `607b218` pesquisa Unreal Blueprints · `6ea2a6e` EngineDebugger

### ARQUIVOS NOVOS (14)

scripts/: generate_doc_headers.py, expand_tests.py, generate_tres.py, audit_descriptions.py
tools/: seed_ops.py, rag_ops.py, entity_index.py, live_classifier.py, live_adjust.py,
        context_compaction.py, model_routing.py, undo_unify.py
seeds/: platformer.json, topdown_rpg.json

### INDICADORES FINAIS

@tool 249/249 · warnings 249/249 · signals 0 · class_name 0 · _initialized 0
doc headers 100% · exports c/ setter 100% · >=3 testes 100% · bugs validate 0
.tres 188/249 · CHANGELOG 249/249 · seeds 3 · tools MCP 275

### ONDA 2 PLACAR: 29/50 concluidas (58%)
✅ 29 fatias · ⬜ 6 pendentes (2.AN, 2.AV, 2.AW, 2.AX, 2.AC parcial) · 🔴 5 escaladas

### PROXIMA SESSAO — O FOSSO
1. 2.AV Editor visual (16 features, 100% GDScript)
2. 2.AW AssetLib prep · 3. 2.AX +4 jogos-exemplo
4. 2.AN Taxonomia (Agente 1) · 5. Resolver escaladas (decisao Joab)

### ARQUIVOS CRITICOS
.github/roadmap/ONDA_2_fosso.md · .roadmap_progress.json · ROADMAP_DEFINITIVO.md
NEXT_STEP.md · behaviors/CATALOGO_COMPLETO.md

---

## ULTIMO HANDOFF (AGENTE 02 — 2026-07-21 — SESSAO DEFINITIVA: 118→249)

- **Data:** 2026-07-21
- **De:** AGENTE 02 (Conteudo — behaviors)
- **Branch:** `agente2/behaviors-onda2`
- **Acao:** +131 behaviors + 3 auditorias de qualidade + correcoes estruturais

### Metricas

- **Total:** 118 → **249 behaviors** (100%+ do catalogo original de 224)
- **+131 behaviors** na sessao
- **Linhas GDScript:** ~14.053 (media 56/behavior)
- **Todos os grupos do catalogo FECHADOS**
- **84 behavior.json reconstruidos** (JSON invalido corrigido)
- **34 sinais nao emitidos corrigidos** (6 + 28)
- **Indicadores de qualidade: 100%** (249/249)

### Qualidade (249/249 = 100%)

| Indicador | Status |
|---|---|
| `@tool` | ✅ 249/249 |
| `_get_configuration_warnings()` | ✅ 249/249 |
| `_initialized` guard | ✅ 0 faltando |
| `behavior.json` valido | ✅ 249/249 |
| Sinais emitidos | ✅ 0 fantasmas |
| `class_name` unico | ✅ 0 conflitos |
| Arquivos obrigatorios (5) | ✅ 249/249 |
| `validate_gdscript` | ✅ ALL PASS |

### Arquitetura

- **189/249 (76%)** extends Node
- **87% event-driven** (sem `_process` ativo)
- **Mediana: 2 sinais/behavior**
- **Extends:** Node(189), Area2D(18), Control(15), Node2D(14), CanvasLayer(6), Resource(3), RayCast2D(2)

### Commits da sessao (17)

```
0925564 fix(auditoria): reconstroi 84 behavior.json invalidos
ba9c204 fix(auditoria): corrige 28 sinais nao emitidos
df31235 feat: +48 behaviors LIFECYCLE+PERFORMANCE+ANIMACAO+TILEMAP+MISC
ba82e21 feat: +11 MODDING+PLUGIN SYSTEM
f51a45b feat: +6 OBSERVABILIDADE
9047a04 feat: +7 GERACAO PROCEDURAL
1a9b139 fix: 6 sinais nao emitidos
d36d574 feat: +7 SAVE AVANCADO
33dbe8b feat: +5 INPUT AVANCADO
ffc48c8 feat: +6 LOCALIZACAO+INPUT
3613710 feat: camera_zoom_range+racing_lap+fishing_cast+farming_plot
94b85fa fix: _initialized+_get_configuration_warnings+sinais
79a1c19 feat: +11 ACESSIBILIDADE
cca7b0c feat: +4 MULTIPLAYER
2067703 feat: +4 INIMIGO/AI+SHADERS
0925e8a feat: +2 CINEMATICA
9ded80a feat: +3 SOCIAL
7695df8 feat: +3 CAMERA
eb95c53 feat: +3 ESTRUTURA
709336e feat: input_manager — FECHA SISTEMA
805a7cd feat: match3_grid — FECHA GENEROS
f86892f feat: camera_framed
d226176 feat: camera_shake
2aa49e4 feat: idle_generator
86beba1 feat: hand
a98931c feat: character_creator — FECHA PERSONAGEM
```

### Proximo: nenhum — catalogo COMPLETO

Todos os 245+ behaviors do catalogo foram implementados. Trabalho futuro:
- Melhorar documentacao (43% tem doc headers)
- Adicionar testes mais profundos
- Integracao com MCP para descoberta automatica de behaviors
- Performance profiling em behaviors com `_process`

---

## Historico de handoffs anteriores

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
