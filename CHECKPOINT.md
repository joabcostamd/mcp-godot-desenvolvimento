# CHECKPOINT.md — Auditoria de Reorganização de Tools

> Gerado: 2026-07-21 | Commit: 3673903 | Branch: main
> **Este arquivo não deve ser commitado. Aguarda revisão externa.**

=====================================================================
C1 — ONDE VOCE ESTA
=====================================================================

Conteúdo literal de .reorg_progress.json:

```
{\" "fase_atual\:\F2\,\fatia_atual\:\2.3\,\fases_fechadas\:[\F0\],\bloqueado\:false,\motivo_bloqueio\:null} 
```

⚠️ O arquivo .reorg_progress.json está CORROMPIDO — contém escapes literais
(\") em vez de JSON válido. Parseamento automático falha.

Interpretação manual do conteúdo danificado:
  FASE_ATUAL = F2
  FATIA_ATUAL = 2.3
  FASES_FECHADAS = ["F0"]
  BLOQUEADO = nao
  MOTIVO_BLOQUEIO = (vazio)

NOTA: Este arquivo está desatualizado em relação ao estado real do código.
O .roadmap_progress.json (que é a fonte mantida ativamente) mostra F5.1 a F5.5
concluídas (domínios physics, ui, shader, camera, navigation migrados).

=====================================================================
C2 — HISTORICO REAL (nao o que voce lembra)
=====================================================================

COMANDO: cmd /c "git log --oneline -40"

```
3673903 (HEAD -> main, origin/main) docs-atualiza-roadmap-F5.2-corrigida
f260f3f fix-F5.2-kwonly-wrappers-ui-handlers
4c62e8d docs-handoff-completo-prompt-mestre-encerramento
a742ee2 docs-encerramento-F5.3-F5.5-snapshot-handoff
a82c8ef feat-F5.3-F5.4-F5.5-shader-camera-navigation
5781fa1 fix-F5.1-F5.2-kwonly-handlers-aliases
126047c feat-F5.2-ui-domain
ac6292b feat-F5.1-physics-domain
dc342ca docs-changelog-v3.8.0-reorg-F0-F5
00dd96e cleanup-temp-files
b42e4e0 audit-fix-rollup-integration-145-tests-green
0666eb2 reorg-F5-render-manage-rollup
fa6441b reorg-F5-network-debug-rollups-CONTEUDO-77-POLIMENTO-67
5dddc13 reorg-fix-deprecated-list-and-audit-for-consolidated-atomics
4fe3451 reorg-F5-ui-skeleton-rollups-DESIGN-63-CONTEUDO-81
68ffd1d reorg-F5-lsp-manage-rollup-DESIGN-78-to-70
fd7c5ad reorg-F5-godot-manage-rollup-PROTOTIPO-35-to-33
2217a75 reorg-F5-PROTOTIPO-62-to-50-second-rebalance
f05f9c2 reorg-F3-assign-namespaces-to-12-orphan-manage-tools
bd19caf reorg-F5-phase-rebalance-PROTOTIPO-100-to-62
4c23502 reorg-F4-F5-phase-rebalance-and-experimental-readme
eda8016 reorg-F4.1-discovery-tools-to-core
e0df78c reorg-F1.5-wire-registry-to-server
ceb78b1 reorg-F1.1-a-F1.4-registry-foundation
1c699b4 reorg-F2.3-fix-annotations-meta-tool
c1f6aa0 bootstrap-scripts-and-config
22f0803 docs-add-roadmap
a7d952b (tag: reorg-baseline) chore(session): snapshot final 2026-07-21
c4a3872 chore: sync GitHub — auditoria de tools (934 linhas), HANDOFF, NEXT_SESSION, .roadmap_progress, pesquisa ONDA 4 + tools
762f188 chore: limpeza interna — B5 warnings corrigidos (return→assert), budget limits atualizados (287 tools), CHANGELOG + docs_sync
4f3d463 chore(onda-4): .gitignore ROADMAP.md + guia de ativacao GitHub Discussions (4.F)
e2d333e feat(onda-4): infraestrutura de comunidade — community_manage (changelog, release_notes, roadmap_public, badge) + templates Issue/PR
b9a1824 feat(onda-4): 4.A publish_manage + pesquisa externa ONDA 4 completa
702de23 docs: sync CHANGELOG (v3.7.0 ONDA 3), llms.txt (285 tools), pyproject.toml (3.7.0)
73abc6e chore(session): snapshot e NEXT_SESSION 2026-07-21 — ONDA 3 concluida
4076041 fix(onda-3): registrar 3.H-3.K como concluidas + 9 testes de qualidade. 285 tools
1138e7b feat(onda-3): G5-G10 — polimento final (version_diff, record_gif, accessibility, productivity, test_report, visual_diff). 285 tools
24e6a97 feat(onda-3): 3.H+3.I+3.J+3.K — modo professor, primeiro nao, disclosure IA, revisor adversarial. 284 tools
3a0d07c feat(onda-3): G2+G3 — 5o sinal (densidade de eventos/vale de tedio) no fun_report
7eb2510 feat(onda-3): G1+G4 — dashboard de gates (gate_status) + suite completa (full_suite)
```

COMANDO: cmd /c "git tag --list reorg-*"

```
reorg-baseline
```

COMANDO: cmd /c "git status --short"

```
(sem saída — working tree limpo)
```

COMANDO: cmd /c "git diff --stat reorg-baseline HEAD"

```
 .gitignore                             |  Bin 1090 -> 1113 bytes
 .roadmap_progress.json                 |   40 +
 .session/NEXT_SESSION.md               |   95 +-
 .session/PROMPT_MESTRE.md              |   67 ++
 .session/SNAPSHOT_2026-07-21.json      |   83 +-
 CHANGELOG.md                           |   38 +
 DUMP_T1R.md                            | 1549 +++++++++++++++++++++++++++
 HANDOFF.md                             |   16 +-
 MASTER_IMPLEMENTATION_ROADMAP.md       | 1781 ++++++++++++++++++++++++++++++++
 _check.py                              |    5 +
 _cnt.py                                |    4 +
 _meta_tool.py                          |   31 +-
 audit_out.txt                          |  320 ++++++
 audit_out_f2.txt                       |  305 ++++++
 audit_out_f5.txt                       |   36 +
 core/tool_definitions.py               |  298 +-----
 domains/__init__.py                    |   11 +
 domains/_template/examples.py          |   11 +
 domains/_template/handlers.py          |   16 +
 domains/_template/manifest.py          |   46 +
 domains/_template/schemas.py           |   23 +
 domains/camera/handlers.py             |   16 +
 domains/camera/manifest.py             |   37 +
 domains/navigation/handlers.py         |   16 +
 domains/navigation/manifest.py         |   37 +
 domains/physics/examples.py            |   40 +
 domains/physics/handlers.py            |   61 ++
 domains/physics/manifest.py            |  121 +++
 domains/physics/schemas.py             |    8 +
 domains/physics/test_physics_domain.py |   93 ++
 domains/shader/handlers.py             |   25 +
 domains/shader/manifest.py             |   53 +
 domains/ui/examples.py                 |    8 +
 domains/ui/handlers.py                 |  186 ++++
 domains/ui/manifest.py                 |   46 +
 domains/ui/schemas.py                  |    2 +
 domains/ui/test_ui_domain.py           |  133 +++
 experimental/README.md                 |   75 ++
 metrics.csv                            |   12 +
 registry/__init__.py                   |   23 +
 registry/annotations.py                |   68 ++
 registry/discovery.py                  |  103 ++
 registry/invariants.py                 |  129 +++
 registry/legacy_adapter.py             |   68 ++
 registry/types.py                      |   76 ++
 scripts/audit_fase.py                  |  265 +++++
 scripts/audit_registro.py              |  164 +++
 scripts/dump_toollist.py               |   54 +
 server.py                              |  193 ++--
 tests/test_budget_gate.py              |   33 +-
 tools/deprecated.py                    |   25 +
 tools/rollups.py                       |  277 ++++-
 52 files changed, 6676 insertions(+), 546 deletions(-)
```

=====================================================================
C3 — NUMEROS MEDIDOS AGORA (nao os de antes)
=====================================================================

COMANDO: cmd /c ".venv\Scripts\python scripts/audit_registro.py > check_now.txt 2>&1"
seguido de: cmd /c "type check_now.txt"

```
C:\Users\joabc\OneDrive\Documentos\VSCODE\NUCLEO\projetos\mcp-godot-desenvolvimento\.venv\Lib\site-packages\pydantic\main.py:542: UserWarning: Pydantic serializer warnings:
  PydanticSerializationUnexpectedValue(Expected `ToolAnnotations` - serialized value may not be as expected [field_name='annotations', input_value={'operationCategory': 'read'}, input_type=dict])
  return self.__pydantic_serializer__.to_json(
C:\Users\joabc\OneDrive\Documentos\VSCODE\NUCLEO\projetos\mcp-godot-desenvolvimento\.venv\Lib\site-packages\pydantic\main.py:542: UserWarning: Pydantic serializer warnings:
  PydanticSerializationUnexpectedValue(Expected `ToolAnnotations` - serialized value may not be as expected [field_name='annotations', input_value={'operationCategory': 're...', 'deferLoading': True}, input_type=dict])
  return self.__pydantic_serializer__.to_json(
============================================================
CONTAGENS
============================================================
defs_total = 309
defs_raw = 272
defs_rollup = 37
handlers_total = 273
handlers_rollup = 37
manage_em_raw = ['budget_manage', 'community_manage', 'complexity_gate_manage', 'fun_report_manage', 'mcp_telemetry_manage', 'playtest_manage', 'polish_manage', 'publish_manage', 'quickstart_manage', 'reviewer_manage', 'scope_manage', 'teacher_manage', 'version_history_manage']
manage_em_rollup = ['analysis_manage', 'anim_manage', 'asset_manage', 'audio_manage', 'camera_manage', 'config_manage', 'd3_manage', 'debug_manage', 'dialogue_manage', 'export_manage', 'file_manage', 'game_bridge_manage', 'gamestate_manage', 'godot_manage', 'inventory_manage', 'localization_manage', 'lsp_manage', 'music_manage', 'navigation_manage', 'network_manage', 'node_manage', 'physics_manage', 'playtest_manage', 'project_manage', 'raycast_manage', 'render_manage', 'runtime_manage', 'safety_manage', 'scene_manage', 'script_manage', 'shader_manage', 'skeleton_manage', 'test_manage', 'tilemap_manage', 'ui_manage', 'vfx_manage', 'vision_manage']
toolsets_entradas_soma = 323
toolsets_nomes_unicos = 323
phase_nomes_unicos = 210

============================================================
DIVERGENCIAS
============================================================

--- SEM_HANDLER (em _tool_defs() mas NAO em _build_handlers()) ---
Total: 40
  configure_particles_2d
  configure_standard_material_3d
  create_light_2d
  create_light_3d
  create_particles_2d
  create_particles_3d
  debugger_get_stack
  debugger_get_variables
  debugger_set_breakpoint
  debugger_status
  debugger_step
  gdscript_definition
  gdscript_diagnostics
  gdscript_hover
  gdscript_lsp_connect
  gdscript_lsp_disconnect
  gdscript_references
  gdscript_rename
  gdscript_symbols
  gdscript_sync_file
  godot_exec
  godot_run_project
  godot_runtime_info
  godot_stop_project
  godot_wait_for_bridge
  network_configure_dedicated_server
  network_create_lobby
  network_create_rpc
  network_create_websocket
  network_setup_multiplayer
  render_get_settings
  render_set_antialiasing
  render_set_quality
  render_set_scaling
  skeleton_create_bone
  skeleton_create_ik_chain
  skeleton_get_bone_pose
  skeleton_get_info
  skeleton_list_bones
  skeleton_set_bone_pose

--- SEM_DEF (em _build_handlers() mas NAO em _tool_defs()) ---
Total: 5
  add_raycast_2d
  add_shapecast_2d
  edit_shader
  get_shader_params
  read_shader

--- DUPLICADOS_NS (nome em 2+ namespaces) ---
Total: 0

--- NS_FANTASMA (em TOOLSETS mas NAO em _tool_defs()) ---
Total: 15
  add_raycast_2d
  add_shapecast_2d
  create_joint_2d
  create_navigation_agent_2d
  create_navigation_region_2d
  edit_shader
  generate_shader_2d
  get_shader_params
  read_shader
  setup_camera_2d
  ui_configure_focus_nav
  ui_create_tab_with_content
  ui_create_widget
  ui_set_anchor_preset
  ui_set_tooltip

--- PHASE_FANTASMA (em PHASE_TOOLSETS mas NAO em _tool_defs()) ---
Total: 0

--- SEM_NAMESPACE (em _tool_defs() mas NAO em TOOLSETS) ---
Total: 0

--- SEM_FASE (em _tool_defs() mas NAO em PHASE_TOOLSETS nem CORE) ---
Total: 98
  accessibility_add_subtitles
  accessibility_apply_colorblind_filter
  accessibility_audit_scene
  accessibility_certification_checklist
  accessibility_remap_controls
  adaptive_difficulty_adjust
  assert_node_exists
  budget_manage
  capsule_generate_store_image
  cloud_save_configure
  community_manage
  complexity_gate_manage
  configure_particles_2d
  configure_standard_material_3d
  create_achievement_system
  create_light_3d
  create_particles_2d
  create_particles_3d
  cutscene_add_camera_shot
  cutscene_add_dialogue_event
  cutscene_create_timeline
  debugger_get_stack
  debugger_get_variables
  debugger_set_breakpoint
  debugger_status
  debugger_step
  dialogue_generate_npc_lines
  dialogue_generate_personality
  fun_report_manage
  game_await_signal
  game_call_method
  game_find_nodes_by_class
  game_get_camera
  game_http_request
  game_input_state
  game_multiplayer
  game_pause
  game_performance
  game_play_animation
  game_raycast
  game_serialize_state
  game_spawn_node
  game_window
  gdscript_definition
  gdscript_diagnostics
  gdscript_hover
  gdscript_lsp_connect
  gdscript_lsp_disconnect
  gdscript_references
  gdscript_rename
  gdscript_symbols
  gdscript_sync_file
  godot_exec
  godot_run_project
  godot_runtime_info
  godot_stop_project
  godot_wait_for_bridge
  localization_manage
  mcp_telemetry_manage
  mod_manifest_generate
  music_manage
  network_configure_dedicated_server
  network_create_lobby
  network_create_rpc
  network_create_websocket
  network_setup_multiplayer
  onboarding_check_first_experience
  onboarding_create_guided_tour
  onboarding_create_tutorial_step
  playtest_manage
  polish_manage
  publish_manage
  quest_generate
  quickstart_manage
  remote_balance_config
  render_get_settings
  render_set_antialiasing
  render_set_quality
  render_set_scaling
  reviewer_manage
  run_stress_test
  scope_manage
  skeleton_create_bone
  skeleton_create_ik_chain
  skeleton_get_bone_pose
  skeleton_get_info
  skeleton_list_bones
  skeleton_set_bone_pose
  teacher_manage
  telemetry_get_funnel
  telemetry_heatmap
  telemetry_session_summary
  telemetry_track_event
  trailer_capture_clip
  trailer_render_sequence
  validate_achievement_config
```

=====================================================================
C4 — INVARIANTES
=====================================================================

COMANDO: cmd /c ".venv\Scripts\python -m pytest tests/test_invariants.py -v > inv.txt 2>&1"
seguido de: cmd /c "type inv.txt"

```
============================= test session starts =============================
platform win32 -- Python 3.14.6, pytest-9.1.1, pluggy-1.6.0
cachedir: .pytest_cache
rootdir: C:\Users\joabc\OneDrive\Documentos\VSCODE\NUCLEO\projetos\mcp-godot-desenvolvimento
configfile: pyproject.toml
plugins: anyio-4.14.2
collecting ... ERROR: file or directory not found: tests/test_invariants.py

collected 0 items

============================ no tests ran in 0.02s ============================
```

tests/test_invariants.py NAO EXISTE. As invariantes existem apenas como funções
em registry/invariants.py, sem wrapper pytest. Executei check_all() diretamente:

COMANDO: Python snippet — registry.invariants.check_all("F5")

Resultado:

  INV-01 = FALHA
    ERRO: SEM_HANDLER: ['configure_particles_2d', 'configure_standard_material_3d', 'create_light_2d', 'create_light_3d', 'create_particles_2d', 'create_particles_3d', 'debugger_get_stack', 'debugger_get_variables', 'debugger_set_breakpoint', 'debugger_status', 'debugger_step', 'gdscript_definition', 'gdscript_diagnostics', 'gdscript_hover', 'gdscript_lsp_connect', 'gdscript_lsp_disconnect', 'gdscript_references', 'gdscript_rename', 'gdscript_symbols', 'gdscript_sync_file', 'godot_exec', 'godot_run_project', 'godot_runtime_info', 'godot_stop_project', 'godot_wait_for_bridge', 'network_configure_dedicated_server', 'network_create_lobby', 'network_create_rpc', 'network_create_websocket', 'network_setup_multiplayer', 'render_get_settings', 'render_set_antialiasing', 'render_set_quality', 'render_set_scaling', 'skeleton_create_bone', 'skeleton_create_ik_chain', 'skeleton_get_bone_pose', 'skeleton_get_info', 'skeleton_list_bones', 'skeleton_set_bone_pose'] (40 tools)
  INV-02 = FALHA
    ERRO: SEM_DEF: ['add_raycast_2d', 'add_shapecast_2d', 'edit_shader', 'get_shader_params', 'read_shader'] (5 handlers)
  INV-10 = PASSA
  INV-11 = FALHA
    ERRO: NS_FANTASMA: ['add_raycast_2d', 'add_shapecast_2d', 'create_joint_2d', 'create_navigation_agent_2d', 'create_navigation_region_2d', 'edit_shader', 'generate_shader_2d', 'get_shader_params', 'read_shader', 'setup_camera_2d', 'ui_configure_focus_nav', 'ui_create_tab_with_content', 'ui_create_widget', 'ui_set_anchor_preset', 'ui_set_tooltip'] (15 tools)
  INV-12 = PASSA
  INV-13 = PASSA

Lista INV-01 a INV-15:

  INV-01 = FALHA — 40 tools em _tool_defs() sem handler em _build_handlers()
  INV-02 = FALHA — 5 handlers em _build_handlers() sem tool em _tool_defs()
  INV-03 = NAO_IMPLEMENTADA — Deveria ter sido criada na Fase 1 (registry)
  INV-04 = NAO_IMPLEMENTADA — Deveria ter sido criada na Fase 1 (registry)
  INV-05 = NAO_IMPLEMENTADA — Deveria ter sido criada na Fase 1 (registry)
  INV-06 = NAO_IMPLEMENTADA — Deveria ter sido criada na Fase 1 (registry)
  INV-07 = NAO_IMPLEMENTADA — Deveria ter sido criada na Fase 2 (conformidade)
  INV-08 = NAO_IMPLEMENTADA — Deveria ter sido criada na Fase 2 (conformidade)
  INV-09 = NAO_IMPLEMENTADA — Deveria ter sido criada na Fase 2 (conformidade)
  INV-10 = PASSA — OK — 210 nomes de fase, todos em tools/list
  INV-11 = FALHA — 15 nomes em TOOLSETS que não existem em _tool_defs() (são as atômicas removidas na migração de domínios F5)
  INV-12 = PASSA — OK — 0 duplicados
  INV-13 = PASSA — placeholder
  INV-14 = NAO_IMPLEMENTADA — Deveria ter sido criada na Fase 4 (descoberta)
  INV-15 = NAO_IMPLEMENTADA — Deveria ter sido criada na Fase 5 (domínios)

ANÁLISE: As falhas INV-01 (SEM_HANDLER) afetam 40 tools dos domínios ainda não
migrados (render, skeleton, particles, lights, debugger, LSP, Godot runtime,
network). São esperadas na F5 — essas tools serão movidas para rollups nos
respectivos domínios.

As falhas INV-02 e INV-11 são EFEITO COLATERAL da migração F5: 5 handlers
órfãos (add_raycast_2d, add_shapecast_2d, edit_shader, get_shader_params,
read_shader) e 15 nomes fantasmas em TOOLSETS (as atômicas que foram removidas
do wire mas ainda constam nos TOOLSETS). Isso indica que o cleanup de TOOLSETS
não foi concluído após a migração dos domínios.

=====================================================================
C5 — ULTIMA AUDITORIA DE FASE
=====================================================================

COMANDO: cmd /c "dir audit_F*.txt"

```
Arquivo não encontrado
```

Nenhum arquivo audit_F*.txt existe. Os arquivos de auditoria disponíveis são:

```
21/07/2026  18:12             9.297 audit_out.txt
21/07/2026  18:12             8.229 audit_out_f2.txt
21/07/2026  18:57             1.190 audit_out_f5.txt
21/07/2026  19:21             1.180 audit_result.json
```

Conteúdo INTEIRO do audit_out_f5.txt (mais recente, 18:57):

```json
{
  "fatia": "F5.3-F5.4-F5.5",
  "timestamp": "2026-07-21T21:57:30.182944+00:00",
  "exit_code": 0,
  "criteria": {
    "C1_contrato": {
      "status": "pass",
      "detail": "308 mudancas: 0 breaking, 308 warning, 0 cosmetic"
    },
    "C2_canary": {
      "status": "skipped",
      "detail": "Nenhuma canary fornecida (--canary ausente)"
    },
    "C3_regressao": {
      "status": "pass",
      "detail": "smoke_test concluido — status: success ({'status': 'success', 'scenarios': [{'name': 'SMOKE-01: Pipeline core', 'description': 'Valida que ping, health_check, self_test e ClassDB respondem c)"
    },
    "C4_seguranca": {
      "status": "skipped",
      "detail": "Nenhuma checklist fornecida (--c4-checklist ausente)"
    },
    "C5_orcamento": {
      "status": "pre_existente",
      "detail": "Pulado (--skip-c5). Problema pre-existente documentado no commit f056aed8. Responsabilidade da fatia 0.7."
    },
    "C6_distinguibilidade": {
      "status": "skipped",
      "detail": "Nenhum nome de tool fornecido (--tool-name ausente)"
    },
    "C7_visual": {
      "status": "skipped",
      "detail": ""
    }
  },
  "errors": []
}
```

Conteúdo INTEIRO do audit_out_f2.txt (18:12, mais completo com contagens):

```
============================================================
CONTAGENS
============================================================
defs_total = 287
defs_raw = 287
defs_rollup = 32
handlers_total = 307
handlers_rollup = 32
manage_em_raw = ['budget_manage', 'community_manage', 'complexity_gate_manage', 'fun_report_manage', 'mcp_telemetry_manage', 'playtest_manage', 'polish_manage', 'publish_manage', 'quickstart_manage', 'reviewer_manage', 'scope_manage', 'teacher_manage', 'version_history_manage']
manage_em_rollup = ['analysis_manage', 'anim_manage', 'asset_manage', 'audio_manage', 'camera_manage', 'config_manage', 'd3_manage', 'debug_manage', 'dialogue_manage', 'export_manage', 'file_manage', 'game_bridge_manage', 'gamestate_manage', 'inventory_manage', 'localization_manage', 'music_manage', 'navigation_manage', 'node_manage', 'physics_manage', 'playtest_manage', 'project_manage', 'raycast_manage', 'runtime_manage', 'safety_manage', 'scene_manage', 'script_manage', 'shader_manage', 'test_manage', 'tilemap_manage', 'ui_manage', 'vfx_manage', 'vision_manage']
toolsets_entradas_soma = 306
toolsets_nomes_unicos = 306
phase_nomes_unicos = 241

============================================================
DIVERGENCIAS
============================================================

--- SEM_HANDLER (em _tool_defs() mas NAO em _build_handlers()) ---
Total: 11
  configure_particles_2d
  configure_standard_material_3d
  create_joint_2d
  create_light_2d
  create_light_3d
  create_navigation_agent_2d
  create_navigation_region_2d
  create_particles_2d
  create_particles_3d
  generate_shader_2d
  setup_camera_2d

--- SEM_DEF (em _build_handlers() mas NAO em _tool_defs()) ---
Total: 31
  analysis_manage
  anim_manage
  asset_manage
  audio_manage
  camera_manage
  config_manage
  d3_manage
  debug_manage
  dialogue_manage
  export_manage
  file_manage
  game_bridge_manage
  gamestate_manage
  inventory_manage
  localization_manage
  music_manage
  navigation_manage
  node_manage
  physics_manage
  project_manage
  raycast_manage
  runtime_manage
  safety_manage
  scene_manage
  script_manage
  shader_manage
  test_manage
  tilemap_manage
  ui_manage
  vfx_manage
  vision_manage

--- DUPLICADOS_NS (nome em 2+ namespaces) ---
Total: 0

--- NS_FANTASMA (em TOOLSETS mas NAO em _tool_defs()) ---
Total: 31
  analysis_manage
  anim_manage
  asset_manage
  audio_manage
  camera_manage
  config_manage
  d3_manage
  debug_manage
  dialogue_manage
  export_manage
  file_manage
  game_bridge_manage
  gamestate_manage
  inventory_manage
  localization_manage
  music_manage
  navigation_manage
  node_manage
  physics_manage
  project_manage
  raycast_manage
  runtime_manage
  safety_manage
  scene_manage
  script_manage
  shader_manage
  test_manage
  tilemap_manage
  ui_manage
  vfx_manage
  vision_manage
```

=====================================================================
C6 — REGRESSAO AGORA
=====================================================================

COMANDO: cmd /c ".venv\Scripts\python -m pytest tests/ -q > pytest_all.txt 2>&1"
seguido de: cmd /c "type pytest_all.txt"

```
........................................................................ [ 48%]
...........................................F.F.......................... [ 97%]
....                                                                     [100%]
================================== FAILURES ===================================
_____________________________ test_remix_success ______________________________

    def test_remix_success():
        """C1: remix do breakout funciona."""
        r = quickstart_manage(op="remix", seed="breakout", project_name="teste_remix")
>       assert r.get("status") == "success", f"Remix falhou: {r}"
E       AssertionError: Remix falhou: {'status': 'error', 'message': "O diretório 'C:\\Users\\joabc\\OneDrive\\Documentos\\VSCODE\\NUCLEO\\projetos\\teste_remix' já existe e não está vazio. Escolha outro nome ou caminho. Se a intenção era abrir um projeto existente, use set_active_project."}
E       assert 'error' == 'success'
E         
E         - success
E         + error

tests\test_remix.py:8: AssertionError
____________________________ test_run_still_works _____________________________

    def test_run_still_works():
        """C5: op=run continua funcionando."""
        r = quickstart_manage(op="run", phrase="jogo de plataforma", project_name="teste_run_pos_remix")
>       assert r.get("status") == "success", f"Run falhou apos remix: {r}"
E       AssertionError: Run falhou apos remix: {'status': 'error', 'message': "O diretório 'C:\\Users\\joabc\\OneDrive\\Documentos\\VSCODE\\NUCLEO\\projetos\\teste_run_pos_remix' já existe e não está vazio. Escolha outro nome ou caminho. Se a intenção era abrir um projeto existente, use set_active_project."}
E       assert 'error' == 'success'
E         
E         - success
E         + error

tests\test_remix.py:23: AssertionError
============================== warnings summary ===============================
.venv\Lib\site-packages\godot_parser\values.py:29
  PyparsingDeprecationWarning: 'escChar' argument is deprecated, use 'esc_char'

.venv\Lib\site-packages\godot_parser\values.py:49
  PyparsingDeprecationWarning: 'escChar' argument is deprecated, use 'esc_char'

.venv\Lib\site-packages\godot_parser\structure.py:18
  PyparsingDeprecationWarning: 'escChar' argument is deprecated, use 'esc_char'

=========================== short test summary info ===========================
FAILED tests/test_remix.py::test_remix_success - AssertionError: Remix falhou...
FAILED tests/test_remix.py::test_run_still_works - AssertionError: Run falhou...
2 failed, 146 passed, 3 warnings in 73.83s (0:01:13)
```

Nota: smoke_test, regression_test, validate_mcp_registry não existem como
comandos standalone. O smoke_test é um op dentro do playtest_manage e aparece
na auditoria C3 como pass.

=====================================================================
C7 — SUPERFICIE POR FASE (o objetivo do projeto inteiro)
=====================================================================

COMANDO: Python snippet — server._tool_defs() + PHASE_TOOLSETS + PHASE_TOOLS_CORE

```
IDEIA | tools_distintas=48 | tokens=19841
DESIGN | tools_distintas=63 | tokens=27525
PROTOTIPO | tools_distintas=33 | tokens=20103
CONTEUDO | tools_distintas=75 | tokens=32796
POLIMENTO | tools_distintas=67 | tokens=22910
PRONTO_PARA_LANCAR | tools_distintas=42 | tokens=15885

Meta: <=33 tools, <=12000 tokens por fase
```

Número alvo: <=33 tools e <=12000 tokens por fase.

Fases dentro do alvo (tools <=33): 1 de 6 — PROTOTIPO (33 tools, exatamente no limite).

Fases dentro do alvo (tokens <=12000): 0 de 6 — nenhuma fase está dentro do teto de tokens.

Métrica de tokens é estimativa bruta: sum(len(description) + len(name)*3).
O teto de 12000 tokens é para a descrição completa das tools visíveis na fase.

=====================================================================
C8 — DIVERGENCIA ENTRE PLANO E REALIDADE
=====================================================================

Comparação entre o executado (git log) e o MASTER_IMPLEMENTATION_ROADMAP.md:

O MASTER_IMPLEMENTATION_ROADMAP.md define 10 fases (F0 a F10). O que foi executado:

  F0 (MEDIR): CONCLUÍDA — scripts/audit_registro.py e scripts/dump_toollist.py
      criados. Medições iniciais coletadas.

  F1 (REGISTRY): CONCLUÍDA — registry/ foundation criado (types.py, annotations.py,
      discovery.py, invariants.py, legacy_adapter.py). Wire do registry em server.py.

  F2 (CONFORMIDADE MCP): CONCLUÍDA — annotations nos rollups, _meta_tool.py
      atualizado com ToolAnnotations.

  F3 (UNIFICAR ROLLUPS): PARCIAL — 12 orphan manage tools receberam namespaces.
      A unificação completa dos 3 caminhos de rollup ainda não foi concluída.

  F4 (DESCOBERTA PROGRESSIVA): PARCIAL — discovery.py e catalog_search criados.
      A descoberta progressiva por fase não está totalmente implementada.

  F5 (MIGRAR DOMÍNIOS): EM ANDAMENTO — 5 domínios migrados (physics, ui, shader,
      camera, navigation). Restam ~8 domínios não migrados.

  F6 a F10: NÃO INICIADAS.

DESVIOS:
  F5.2 ui: O handlers.py original usava re-exports. Foi corrigido hoje
  (commit f260f3f) para KW-only wrappers, alinhando com o padrão physics.
  Motivo: re-exports não tinham type hints, contrato KW-only, nem lazy import.
  Desvio do plano original que aceitava re-exports como "concluído".

  Ordem de F5: Os domínios foram migrados na ordem physics→ui→shader→camera→
  navigation, que difere da priorização sugerida no roadmap (que recomendava
  começar pelos domínios com mais ferramentas órfãs). Motivo: physics foi
  escolhido como gold standard por ser o domínio mais maduro.

PULOS:
  F3 completa: A unificação dos 3 caminhos de rollup (_meta_tool.py,
  tools/rollups.py, e os manage_em_raw) não foi concluída. 13 ferramentas
  ainda usam o caminho "raw" (manage_em_raw).

  Cleanup de TOOLSETS pós-F5: As atômicas removidas do wire (ex: create_joint_2d,
  setup_camera_2d, ui_create_widget) ainda constam em TOOLSETS como NS_FANTASMA
  (15 entradas). Isso viola INV-11.

GATES:
  G1 (defs_total <= 150): NÃO SATISFEITO — defs_total = 309
  G2 (SEM_HANDLER == 0): NÃO SATISFEITO — 40 ferramentas sem handler
  G3 (SEM_DEF == 0): NÃO SATISFEITO — 5 handlers sem definição
  G4 (tools por fase <= 33): PARCIAL — só PROTOTIPO (33) atende
  G5 (tokens por fase <= 12000): NÃO SATISFEITO — nenhuma fase
  G6 (rollups >= 80%): NÃO MEDIDO

DECISOES:
  NENHUMA decisão D-01..D-14 foi reaberta ou contornada.

IMPROVISOS:
  A correção de hoje (KW-only wrappers no domínio ui) foi uma decisão de
  qualidade não prevista explicitamente no roadmap. O roadmap da F5 diz
  "migrar domínio" mas não especifica o padrão interno dos handlers.

  O arquivo .reorg_progress.json está corrompido (JSON com escapes literais).
  Não foi previsto no roadmap um mecanismo de validação desse arquivo.

=====================================================================
C9 — O QUE ESTA TRAVANDO
=====================================================================

  TENTATIVAS_FALHAS:
    F5.2 ui: 2 tentativas. A primeira (commit 126047c) usava re-exports;
    a segunda (commit f260f3f) converteu para KW-only wrappers.
    Motivo: re-exports não atendiam ao padrão de qualidade dos outros domínios.

  PARIDADE:
    test_paridade_com_legado em domains/ui/test_ui_domain.py: FALHOU na
    tentativa 2 porque o teste original usava identity check (is), que só
    funciona com re-exports. Foi reescrito para verificar equivalência
    comportamental. Agora PASSA.

  FC:
    Nenhum fc (File Compare) foi executado nesta sessão. Os arquivos de
    baseline para fc não foram localizados.

  PESQUISA:
    Nenhum item marcado como NAO ENCONTRADO NA DOCUMENTACAO OFICIAL nesta sessão.

  PROXIMO_PASSO:
    A próxima fatia lógica seria continuar a F5 com a migração dos domínios
    restantes (render, skeleton, particles, lights, debugger, LSP, Godot
    runtime, network). Porém, antes disso, é necessário:
    1. Fazer o cleanup de TOOLSETS (15 NS_FANTASMA das atômicas removidas)
    2. Corrigir os 5 SEM_DEF (handlers órfãos de shader, raycast, shapecast)
    3. Atualizar .reorg_progress.json (está corrompido e desatualizado)

    A fatia não rodou ainda porque a sessão atual foi dedicada à correção
    da F5.2 (KW-only wrappers) e à geração deste CHECKPOINT.

=====================================================================
ENTREGA
=====================================================================
