# 🤝 HANDOFF — Comunicação entre Agentes

> **Regra:** Ao finalizar cada etapa, o agente ATUALIZA este arquivo
> para que o outro agente saiba o estado do projeto na próxima sessão.

## ⚠️ AVISO AO AGENTE 2 (2026-07-21)

**ONDA 3 em andamento pelo Agente 1. Não interfira em:**
- `tools/playtest_ops.py`
- `tools/personas.py`
- `core/tool_definitions.py`
- `server.py`
- `tests/test_personas.py`
- `tests/test_playtest.py`
- `.roadmap_progress.json`

## Último Handoff (AGENTE 01 — 2026-07-21 — Fatia 3.B)

- **Data:** 2026-07-21
- **De:** AGENTE 01 (Arquitetura & Core)
- **Ação:** Implementação da Fatia 3.B — Playtest camada 2: personas scriptadas [SÊNIOR]

### O que foi feito

- `tools/personas.py` (NOVO, 153 linhas) — 3 personas (apressado/cauteloso/explorador) com KEY_MAP Godot 4
- `tools/playtest_ops.py` — estendido (+180 linhas): `op=persona_run` no rollup `playtest_manage`
- `_send_key_event()` — simula hold com taps a 50ms via runtime bridge (:8790) `input_event`
- Coleta: completed, total_time_s, total_inputs, input_errors, métricas inicial/final
- `core/tool_definitions.py` — schema atualizado com `persona_run` + parâmetro `persona`
- `tests/test_personas.py` — 10 testes (listagem, validação, KEY_MAP, smoke regressão)

### Como usar
- `playtest_manage op=persona_run persona=apressado duration=60`
- Personas: apressado (rush), cauteloso (careful), explorador (explore)
- Requer jogo rodando em debug (F5 no Godot)

### Métricas
- **ONDA 1:** ✅ 17/17
- **ONDA 3:** 2/11 (3.A + 3.B concluídas)
- **Total tools:** 279
- **C1:** PASS (0 breaking)
- **C3:** PASS (smoke_test)
- **Testes:** 47/47 (10 personas + 11 smoke + 26 version_history)

### Próximo passo
- **3.C — Playtest camada 3: agente LLM pontual** [SÊNIOR]

- **Data:** 2026-07-21
- **De:** AGENTE 01 (Arquitetura & Core)
- **Ação:** Implementação da Fatia 3.A — Playtest camada 1: smoke automático [AUTO]

### O que foi feito

- `tools/playtest_ops.py` — estendido (+175 linhas): rollup `playtest_manage(op=smoke)`
- Smoke test do JOGO via runtime bridge (:8790): coleta FPS, draw_calls, memória
- Detecta crash (bridge para de responder), FPS abaixo do threshold
- Valida viewport ativo (screenshot)
- `core/tool_definitions.py` — tool `playtest_manage` registrada
- `server.py` — handler `_handle_playtest_manage` registrado
- `tests/test_playtest.py` — 10 testes pytest

### Como usar
- `playtest_manage op=smoke duration=10 fps_threshold=30` — smoke test do jogo
- Requer jogo rodando em debug (F5 no Godot)
- NÃO usa --headless (R12: não funciona no Windows 4.7)

### Métricas
- **ONDA 1:** ✅ 17/17
- **ONDA 3:** 1/11 (3.A concluída)
- **Total tools:** 279 (+1)
- **C1:** PASS (0 breaking)
- **C3:** PASS (smoke_test)
- **C5:** pre-existente (8 fases overflow)
- **Testes:** 10/10 pytest + regressão 26/26

### Próximo passo
- **3.B — Playtest camada 2: personas scriptadas** [SÊNIOR] — ou continuar ONDA 2 com Agente 2

---

## Handoff anterior (AGENTE 01 — 2026-07-21 — Fatia 1.Q)

- **Data:** 2026-07-21
- **De:** AGENTE 01 (Arquitetura & Core)
- **Ação:** Implementação da Fatia 1.Q — Histórico de versões jogáveis [SÊNIOR]

### O que foi feito

- `tools/version_history_ops.py` (NOVO, 334 linhas) — rollup `version_history_manage(op=save|list|restore|delete|screenshot)`
- Screenshot via `runtime_bridge_client.send_bridge_command({"cmd": "screenshot"})` — comando já existente no addon
- Armazenamento em `<project>/.mcp_versions/` com `index.json` + `manifest.json` + `screenshot.png`
- Save fail-soft: sem jogo rodando, salva sem screenshot com aviso
- Restore: `git checkout <commit> --` com validação de working tree limpo + checkpoint via `safety.checkpoint()`
- Path traversal sanitizado em version_id
- Lock `VERSION_HISTORY_LOCK` em `tools/config_lock.py`
- `core/tool_definitions.py` — tool `version_history_manage` registrada
- `server.py` — handler `_handle_version_history_manage` registrado
- `tests/test_version_history.py` (NOVO) — 26 testes automatizados (pytest)
- Auditoria: 1 bug CRÍTICO encontrado e corrigido (`run_subprocess_safe` kwargs conflitantes)

### Como usar
- `version_history_manage op=save description="Antes de refatorar IA"` — salva versão jogável
- `version_history_manage op=list` — lista versões salvas
- `version_history_manage op=restore version_id="20260721_143022"` — restaura versão (git checkout)
- `version_history_manage op=delete version_id="20260721_143022"` — remove versão
- `version_history_manage op=screenshot` — captura screenshot avulso (jogo precisa estar rodando)

### Métricas
- **ONDA 1:** ✅ 17/17 CONCLUÍDA
- **Total tools:** 278 (+1)
- **Total handlers:** 299 (+1)
- **C1:** PASS (0 breaking)
- **C3:** PASS (smoke_test)
- **C5:** pre-existente (8 fases overflow)
- **Testes:** 26/26 pytest + 10/10 manuais

### Próximo passo
- **ONDA 2 — O FOSSO** — `.github/roadmap/ONDA_2_fosso.md`. Fatia 2.A. Rode `/plan`.

---

## Handoff anterior (AGENTE 01 — 2026-07-21 — Fatia 1.P)

- **Data:** 2026-07-21
- **De:** AGENTE 01 (Arquitetura & Core)
- **Ação:** Implementação da Fatia 1.P — Telemetria opt-in do próprio MCP

### O que foi feito

- `tools/mcp_telemetry_ops.py` (NOVO, 574 linhas) — rollup `mcp_telemetry_manage(op=status|enable|disable|export|reset)`
- Hook `track_mcp_event()` em `server.py::call_tool()` — fail-open, mesmo padrão de `budget_ops`
- Hook `track_phase_transition()` integrado no `advance_phase`
- `core/tool_definitions.py` — tool `mcp_telemetry_manage` registrada
- `docs/PESQUISA_EXTERNA.md` — Seção 6: pesquisa de 8 fontes sobre telemetria de ferramentas

### Como usar
- `mcp_telemetry_manage op=enable` ativa coleta (consentimento explícito)
- `mcp_telemetry_manage op=status` mostra métricas
- `mcp_telemetry_manage op=export` gera relatório JSON
- Dados 100% locais (.mcp_telemetry_events.jsonl)

### Métricas
- **ONDA 1:** 16/17 concluídas
- **Total tools:** 277
- **C1:** PASS (0 breaking)
- **C3:** PASS (smoke_test)
- **C5:** pre-existente (8 fases overflow)

### Próximo passo
- **1.Q — Histórico de versões jogáveis** [SÊNIOR] — última fatia da ONDA 1

---

## Handoff anterior (AGENTE 01 — 2026-07-20 — Comando /pesquise)

- **Data:** 2026-07-20
- **De:** AGENTE 01 (Arquitetura & Core)
- **Ação:** Implementação do comando `/pesquise` + protocolo de pesquisa

### O que foi feito

- `.github/instructions/pesquisa.instructions.md` (NOVO) — protocolo canônico de 9 fases
- `%USERPROFILE%/AppData/Roaming/Code/User/prompts/pesquise.prompt.md` (NOVO) — prompt VS Code
- `.github/instructions/fontes.instructions.md` — referência ao protocolo
- `docs/PESQUISA_EXTERNA.md` — índice de pesquisas + referência ao protocolo

### Como usar
- Digite `/pesquise` no chat → auto-detecta contexto (fatia atual, fase) e pesquisa até saturação
- `/pesquise [tema]` → pesquisa tema específico
- O protocolo evolui com o projeto: edite `pesquisa.instructions.md` para refinar

### Próximo passo
- **1.F — Erro amigável universal** [AUTO] (plano já apresentado, aguardando aprovação)

---

## Handoff anterior (AGENTE 01 — 2026-07-20 — ONDA 1: 1/17)

- **Data:** 2026-07-20
- **De:** AGENTE 01 (Arquitetura & Core)
- **Ação:** ONDA 0 (12/12) + Fatia 1.A — Instalador de 1 comando

### 1.A — init.py (760+ linhas, NOVO)

Instalador standalone (só stdlib): detecta Godot/Python/VS Code, cria venv,
gera `.vscode/mcp.json` com merge, cria projeto Godot + addon, abre editor,
faz bridge polling (LSP :6005 + WS :9082, timeout 30s). Idempotente.
Mensagens em português. `--silent`, `--no-verify`, `--verbose`.

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
- **Novos arquivos:** init.py, cloud_sync_detector.py, name_utils.py, ip_guard.py
- **Arquivos expandidos:** server.py, project_ops.py, project_brief_ops.py, art_ops.py, tool_definitions.py, scene_ops.py
- **ONDA 0:** ✅ 12/12
- **ONDA 1:** 1/17 (1.A concluída)

### ⚠️ Pontos de atenção

- init.py é standalone (só stdlib) — não importa tools/
- mcp.json usa merge: servidores existentes preservados
- Bridge WS :9082 timeout se outro projeto Godot já ocupa a porta
- C1/C5 do auditar.py: pré-existentes (7 breaking, 8 fases overflow)

### Próximo passo
- **1.B — Instalar templates de export** [AUTO]

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
