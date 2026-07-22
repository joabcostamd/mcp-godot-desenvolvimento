# CATÁLOGO COMPLETO — MCP Godot Agent

> Gerado em 19/07/2026 a partir dos arquivos reais (server.py, tools/*.py).
> **Precisão:** nomes, descrições, handlers, inputSchemas e fases extraídos diretamente do código fonte.

---

## SUMÁRIO EXECUTIVO

| Métrica | Valor |
|---|---|
| **Total de ferramentas únicas** | **212** |
| CORE (sempre visíveis) | 27 |
| Fase IDEIA | 18 exclusivas (+27 CORE = **45** totais visíveis) |
| Fase DESIGN | 21 exclusivas (+27 CORE = **48** totais visíveis) |
| Fase PROTOTIPO | 65 exclusivas (+27 CORE = **92** totais visíveis) |
| Fase CONTEUDO | 35 exclusivas (+27 CORE = **62** totais visíveis) |
| Fase POLIMENTO | 30 exclusivas (+27 CORE = **57** totais visíveis) |
| Fase PRONTO_PARA_LANCAR | 18 exclusivas (+27 CORE = **45** totais visíveis) |
| Em múltiplas fases | 2 (analyze_signal_flow, find_unused_resources) |
| Arquivos de handler | 70+ em `tools/` |
| Linhas do server.py | 6.391 |

### Dependência por Feature da Fase 1

| Feature | Cobertura de tools |
|---|---|
| F01 — Comunicação WebSocket | Bridge: `addon_*`, `bootstrap_godot_mcp`, `godot_*` |
| F02 — Rate Limiting | Transversal (aplica-se a todas as tools) |
| F03 — Operações de Cena | `scene_manage`, `node_manage`, `raycast_manage`, `load_scene_async`, `create_light_2d` |
| F04 — Operações de Script | `script_manage`, `safe_write_gdscript`, `gdscript_*` (9 tools LSP) |
| F05 — Operações de Arquivo | `read_file`, `write_file`, `file_manage` + asset ops |
| F06 — Operações de Runtime | `runtime_manage`, `godot_run_project`, `godot_stop_project`, `game_*`, `capture_*` |
| F07 — Templates | Templates GDScript (não são tools MCP) |
| F08 — Segurança | `safety_manage`, `security_status`, `configure_security`, `set_safety_policy`, `circuit_breaker_status` |
| F09 — Validação | `validate_*` (4 tools), `audit_*` (5 tools), `run_verification_pipeline` |
| F10 — Gravação | `start_recording`, `stop_recording`, `record_gameplay_gif`, `capture_proof`, `verify_proof` |

### Bugs Conhecidos e Resolvidos nesta Sessão

| Bug | Causa | Correção | Status |
|---|---|---|---|
| Dispatch posicional (15 handlers) | `run_in_executor(None, handler, arguments)` passava dict como 1º param posicional | `_smart_call()` com cache de `inspect.signature` por modo (0/1/2) | ✅ Resolvido |
| `wave_generate` | Esperava `enemy_types` como `list[dict]`, recebia `list[str]` | Normalização de entrada (string → dict com defaults) | ✅ Resolvido |
| `run_scripted_tests` | Dispatch posicional antigo passava chaves do dict como cenários | Resolvido pela Opção B (`_smart_call`) | ✅ Resolvido |
| `dump_mcp_state` | Travava por colateral de `smoke_test` ocupando thread pool | Resolvido pela Opção B (dispatch correto) | ✅ Resolvido |
| `MIN_SCORE` inconsistente | Feature 9: `MIN_SCORE=6` mas `release_checklist.ready >= 7` | Alinhado para `MIN_SCORE=7` | ✅ Resolvido |
| `godot_class_ref` | Recebia dict como `class_name` em vez de string | Resolvido pela Opção B (keyword params) | ✅ Resolvido |
| 10 handlers sem teste direto | Opção B corrigiu mas não foram testados individualmente | Testados: 9 saudáveis, 1 com bug real (`wave_generate`) | ✅ Resolvido |
| postMessage (linha 348) | Frágil, depende de thread específica | Pendente para Fase 2 (SSE/Streamable HTTP) | ⏳ Pendente |

---

## ORGANIZAÇÃO POR CATEGORIA FUNCIONAL

### 1. INFRAESTRUTURA E CONEXÃO (CORE + IDEIA)

| # | Tool | Handler | Fase | Testada |
|---|---|---|---|---|
| 1 | `ping` | `_handle_ping` | CORE | ✅ |
| 2 | `self_test` | `_handle_self_test` | CORE | ✅ |
| 3 | `health_check` | `_handle_health_check` | CORE | ✅ |
| 4 | `bootstrap_godot_mcp` | `_handle_bootstrap_godot_mcp` | CORE | ✅ |
| 5 | `dump_mcp_state` | `_handle_dump_mcp_state` | CORE | ✅ |
| 6 | `install_mcp_addon` | `_handle_install_mcp_addon` | IDEIA | ❌ |
| 7 | `setup_mcp_config` | `_handle_setup_mcp_config` | IDEIA | ❌ |
| 8 | `validate_mcp_environment` | `_handle_validate_mcp_environment` | IDEIA | ❌ |
| 9 | `validate_godot_version` | `_handle_validate_godot_version` | IDEIA | ❌ |
| 10 | `validate_mcp_registry` | `_handle_validate_mcp_registry` | IDEIA | ❌ |

### 2. PROJETO E FASE (CORE)

| # | Tool | Handler | Fase | Testada |
|---|---|---|---|---|
| 11 | `project_manage` | `_handle_project_manage` (rollup) | CORE | ✅ |
| 12 | `project_status` | `_handle_project_status` | CORE | ✅ |
| 13 | `get_current_phase` | `tools/phase_ops:get_current_phase` | CORE | ✅ |
| 14 | `advance_phase` | `tools/phase_ops:advance_phase` | CORE | ✅ |
| 15 | `get_phase_history` | `tools/phase_ops:get_phase_history` | CORE | ✅ |
| 16 | `create_milestone_plan` | `tools/milestone_ops:create_milestone_plan` | IDEIA | ❌ |
| 17 | `get_milestone_plan` | `tools/milestone_ops:get_milestone_plan` | IDEIA | ❌ |
| 18 | `advance_milestone` | `tools/milestone_ops:advance_milestone` | IDEIA | ❌ |

### 3. PROJECT BRIEF E DESIGN (IDEIA + DESIGN)

| # | Tool | Handler | Fase | Testada |
|---|---|---|---|---|
| 19 | `set_project_brief` | `tools/project_brief_ops:set_project_brief` | IDEIA | ✅ |
| 20 | `get_project_brief` | `tools/project_brief_ops:get_project_brief` | IDEIA | ❌ |
| 21 | `update_project_brief` | `tools/project_brief_ops:update_project_brief` | IDEIA | ✅ |
| 22 | `gdd_generate` | `tools/decision_engine:gdd_generate` | IDEIA | ❌ |
| 23 | `analysis_manage` | `tools/analyze_ops:analysis_manage` (rollup) | IDEIA | ❌ |
| 24 | `project_map` | `tools/project_map:project_map` | DESIGN | ❌ |
| 25 | `generate_project_structure` | `tools/devsolo_ops:generate_project_structure` | DESIGN | ❌ |
| 26 | `resource_dependency_graph` | `tools/refs_ops:resource_dependency_graph` | DESIGN | ❌ |
| 27 | `list_valid_node_types` | `tools/scene_ops:list_valid_node_types` | DESIGN | ❌ |
| 28 | `world_describe` | `tools/world_gen:world_describe` | DESIGN | ✅ |

### 4. CENAS E NÓS (CORE + DESIGN + PROTOTIPO)

| # | Tool | Handler | Fase | Testada |
|---|---|---|---|---|
| 29 | `scene_manage` | `tools/scene_ops` (rollup, ops: create_scene, load_scene_tree, add_node, delete_node, set_node_property, get_node_property, reparent_node) | CORE | ✅ |
| 30 | `node_manage` | `tools/scene_ops` (rollup, ops: add_node, delete_node, set_property, get_property, reparent, duplicate) | CORE | ✅ |
| 31 | `load_scene_async` | `tools/scene_ops:load_scene_async` | PROTOTIPO | ❌ |
| 32 | `raycast_manage` | `tools/scene_ops` (rollup) | PROTOTIPO | ❌ |
| 33 | `create_light_2d` | `tools/scene_ops:create_light_2d` | PROTOTIPO | ❌ |
| 34 | `batch_atomic_edit` | `tools/batch_ops:batch_atomic_edit` | PROTOTIPO | ❌ |
| 35 | `add_nodes_batch` | `tools/batch_ops:add_nodes_batch` | PROTOTIPO | ❌ |
| 36 | `set_properties_batch` | `tools/batch_ops:set_properties_batch` | PROTOTIPO | ❌ |

### 5. SCRIPTS GDScript (CORE + DESIGN)

| # | Tool | Handler | Fase | Testada |
|---|---|---|---|---|
| 37 | `script_manage` | `tools/script_ops` (rollup, ops: generate, attach, detach, validate, add_var, add_signal) | CORE | ✅ |
| 38 | `safe_write_gdscript` | `tools/validate_write:safe_write_gdscript` | CORE | ✅ |
| 39 | `gdscript_diagnostics` | `tools/lsp_ops:gdscript_diagnostics` | DESIGN | ❌ |
| 40 | `gdscript_references` | `tools/lsp_ops:gdscript_references` | DESIGN | ❌ |
| 41 | `gdscript_definition` | `tools/lsp_ops:gdscript_definition` | DESIGN | ❌ |
| 42 | `gdscript_hover` | `tools/lsp_ops:gdscript_hover` | DESIGN | ❌ |
| 43 | `gdscript_rename` | `tools/lsp_ops:gdscript_rename` | DESIGN | ❌ |
| 44 | `gdscript_symbols` | `tools/lsp_ops:gdscript_symbols` | DESIGN | ❌ |
| 45 | `gdscript_lsp_connect` | `tools/lsp_ops:gdscript_lsp_connect` | DESIGN | ❌ |
| 46 | `gdscript_lsp_disconnect` | `tools/lsp_ops:gdscript_lsp_disconnect` | DESIGN | ❌ |
| 47 | `gdscript_sync_file` | `tools/lsp_ops:gdscript_sync_file` | DESIGN | ❌ |

### 6. ARQUIVOS (CORE)

| # | Tool | Handler | Fase | Testada |
|---|---|---|---|---|
| 48 | `read_file` | `_handle_read_file` | CORE | ✅ |
| 49 | `write_file` | `_handle_write_file` | CORE | ✅ |
| 50 | `file_manage` | `tools/file_ops` (rollup, ops: delete, move, inspect) | CORE | ✅ |

### 7. ENTIDADES (CORE + DESIGN)

| # | Tool | Handler | Fase | Testada |
|---|---|---|---|---|
| 51 | `create_entity` | `tools/orchestrator:create_entity` | CORE | ✅ (após correção) |
| 52 | `create_entities` | `tools/orchestrator:create_entities` | CORE | ✅ |
| 53 | `behavior_tree_generate` | `tools/behavior_ops:behavior_tree_generate` | DESIGN | ❌ |
| 54 | `behavior_tree_list_templates` | `tools/behavior_ops:behavior_tree_list_templates` | DESIGN | ❌ |

### 8. CLASSDB (CORE + DESIGN)

| # | Tool | Handler | Fase | Testada |
|---|---|---|---|---|
| 55 | `godot_class_ref` | `tools/classdb:godot_class_ref` | CORE | ✅ |
| 56 | `query_classdb` | `_handle_query_classdb` (cached) | DESIGN | ❌ |
| 57 | `search_classdb` | `_handle_search_classdb` (cached) | DESIGN | ❌ |

### 9. REFERÊNCIAS E VALIDAÇÃO (CORE + IDEIA)

| # | Tool | Handler | Fase | Testada |
|---|---|---|---|---|
| 58 | `validate_project_refs` | `tools/refs_ops:validate_project_refs` | CORE | ✅ |
| 59 | `find_usages` | `tools/refs_ops:find_usages` | CORE | ❌ |
| 60 | `audit_input_map` | `tools/audit_input_map:audit_input_map` | IDEIA | ❌ |
| 61 | `audit_autoloads` | `tools/audit_autoloads:audit_autoloads` | IDEIA | ❌ |
| 62 | `audit_scene_reachability` | `tools/audit_scene_reachability:audit_scene_reachability` | IDEIA | ❌ |
| 63 | `audit_uid_consistency` | `tools/audit_uid_consistency:audit_uid_consistency` | IDEIA | ❌ |
| 64 | `audit_save_compatibility` | `tools/audit_save_compatibility:audit_save_compatibility` | IDEIA | ❌ |

### 10. RUNTIME E EXECUÇÃO (PROTOTIPO)

| # | Tool | Handler | Fase | Testada |
|---|---|---|---|---|
| 65 | `runtime_manage` | `tools/runtime_ops` (rollup) | PROTOTIPO | ❌ |
| 66 | `godot_run_project` | `_handle_godot_run_project` | PROTOTIPO | ❌ |
| 67 | `godot_stop_project` | `_handle_godot_stop_project` | PROTOTIPO | ❌ |
| 68 | `godot_wait_for_bridge` | `_handle_godot_wait_for_bridge` | PROTOTIPO | ❌ |
| 69 | `godot_screenshot` | `_handle_godot_screenshot` | PROTOTIPO | ❌ |
| 70 | `godot_runtime_info` | `_handle_godot_runtime_info` | PROTOTIPO | ❌ |
| 71 | `godot_custom_command` | `_handle_godot_custom_command` | PROTOTIPO | ❌ |
| 72 | `godot_list_custom_commands` | `_handle_godot_list_custom_commands` | PROTOTIPO | ❌ |
| 73 | `godot_exec` | `_handle_godot_exec` | PROTOTIPO | ❌ |
| 74 | `godot_keep_alive` | `_handle_godot_keep_alive` | PROTOTIPO | ❌ |
| 75 | `capture_game_screenshot` | `tools/runtime_ops:capture_game_screenshot` | PROTOTIPO | ❌ |
| 76 | `capture_runtime_errors` | `tools/runtime_ops:capture_runtime_errors` | PROTOTIPO | ❌ |
| 77 | `get_runtime_state_digest` | `tools/runtime_ops:get_runtime_state_digest` | PROTOTIPO | ❌ |
| 78 | `execute_gdscript_runtime` | `tools/runtime_ops:execute_gdscript_runtime` | PROTOTIPO | ❌ |
| 79 | `effect_probe` | `tools/runtime_ops:effect_probe` | PROTOTIPO | ❌ |

### 11. GAME BRIDGE E CONTROLE DE JOGO (PROTOTIPO)

| # | Tool | Handler | Fase | Testada |
|---|---|---|---|---|
| 80 | `freeze_game_clock` | `tools/game_bridge:freeze_game_clock` | PROTOTIPO | ❌ |
| 81 | `unfreeze_game_clock` | `tools/game_bridge:unfreeze_game_clock` | PROTOTIPO | ❌ |
| 82 | `step_game_time` | `tools/game_bridge:step_game_time` | PROTOTIPO | ❌ |
| 83 | `step_until` | `tools/game_bridge:step_until` | PROTOTIPO | ❌ |
| 84 | `game_await_signal` | `tools/game_bridge:game_await_signal` | PROTOTIPO | ❌ |
| 85 | `game_call_method` | `tools/game_bridge:game_call_method` | PROTOTIPO | ❌ |
| 86 | `game_find_nodes_by_class` | `tools/game_bridge:game_find_nodes_by_class` | PROTOTIPO | ❌ |
| 87 | `game_get_camera` | `tools/game_bridge:game_get_camera` | PROTOTIPO | ❌ |
| 88 | `game_input_state` | `tools/game_bridge:game_input_state` | PROTOTIPO | ❌ |
| 89 | `game_pause` | `tools/game_bridge:game_pause` | PROTOTIPO | ❌ |
| 90 | `game_performance` | `tools/game_bridge:game_performance` | PROTOTIPO | ❌ |
| 91 | `game_play_animation` | `tools/game_bridge:game_play_animation` | PROTOTIPO | ❌ |
| 92 | `game_raycast` | `tools/game_bridge:game_raycast` | PROTOTIPO | ❌ |
| 93 | `game_serialize_state` | `tools/game_bridge:game_serialize_state` | PROTOTIPO | ❌ |
| 94 | `game_spawn_node` | `tools/game_bridge:game_spawn_node` | PROTOTIPO | ❌ |
| 95 | `game_window` | `tools/game_bridge:game_window` | PROTOTIPO | ❌ |
| 96 | `game_http_request` | `tools/game_bridge:game_http_request` | PROTOTIPO | ❌ |
| 97 | `game_multiplayer` | `tools/game_bridge:game_multiplayer` | PROTOTIPO | ❌ |

### 12. INPUT E TESTES DE JOGO (PROTOTIPO)

| # | Tool | Handler | Fase | Testada |
|---|---|---|---|---|
| 98 | `inject_input_event` | `tools/playtest_ops:inject_input_event` | PROTOTIPO | ❌ |
| 99 | `simulate_input_sequence` | `tools/playtest_ops:simulate_input_sequence` | PROTOTIPO | ❌ |
| 100 | `take_screenshot` | `tools/runtime_ops:take_screenshot` | PROTOTIPO | ❌ |

### 13. WATCH E DEPURAÇÃO AO VIVO (PROTOTIPO)

| # | Tool | Handler | Fase | Testada |
|---|---|---|---|---|
| 101 | `watch_signal` | `tools/debugger_ops:watch_signal` | PROTOTIPO | ❌ |
| 102 | `watch_state_start` | `tools/debugger_ops:watch_state_start` | PROTOTIPO | ✅ |
| 103 | `watch_state_collect` | `tools/debugger_ops:watch_state_collect` | PROTOTIPO | ✅ |

### 14. RECORDING (PROTOTIPO)

| # | Tool | Handler | Fase | Testada |
|---|---|---|---|---|
| 104 | `record_gameplay_gif` | `tools/recording_ops:record_gameplay_gif` | PROTOTIPO | ❌ |
| 105 | `start_recording` | `tools/recording_ops:start_recording` | PROTOTIPO | ❌ |
| 106 | `stop_recording` | `tools/recording_ops:stop_recording` | PROTOTIPO | ❌ |

### 15. ASSETS E ARTE (PROTOTIPO + CONTEUDO)

| # | Tool | Handler | Fase | Testada |
|---|---|---|---|---|
| 107 | `asset_manage` | `tools/asset_ops` (rollup) | PROTOTIPO | ❌ |
| 108 | `generate_game_art` | `tools/art_ops:generate_game_art` | PROTOTIPO | ❌ |
| 109 | `generate_game_art_flux` | `tools/art_ops:generate_game_art_flux` | PROTOTIPO | ❌ |
| 110 | `apply_game_art` | `tools/art_ops:apply_game_art` | PROTOTIPO | ❌ |
| 111 | `import_asset_manifest` | `tools/asset_manifest:import_asset_manifest` | CONTEUDO | ❌ |
| 112 | `create_asset_manifest` | `tools/asset_manifest:create_asset_manifest` | CONTEUDO | ❌ |
| 113 | `download_asset` | `tools/asset_download:download_asset` | CONTEUDO | ❌ |
| 114 | `import_downloaded_asset` | `tools/asset_download:import_downloaded_asset` | CONTEUDO | ❌ |
| 115 | `marketplace_search` | `tools/marketplace_ops:marketplace_search` | CONTEUDO | ❌ |
| 116 | `marketplace_download` | `tools/marketplace_ops:marketplace_download` | CONTEUDO | ❌ |

### 16. SPRITES E IMAGENS (CONTEUDO)

| # | Tool | Handler | Fase | Testada |
|---|---|---|---|---|
| 117 | `create_spritesheet` | `tools/art_ops:create_spritesheet` | CONTEUDO | ❌ |
| 118 | `create_parallax_background` | `tools/art_ops:create_parallax_background` | CONTEUDO | ❌ |
| 119 | `add_parallax_layer` | `tools/art_ops:add_parallax_layer` | CONTEUDO | ❌ |
| 120 | `optimize_sprite` | `tools/art_ops:optimize_sprite` | CONTEUDO | ❌ |
| 121 | `remove_background` | `tools/art_ops:remove_background` | CONTEUDO | ❌* |
| 122 | `create_path_2d` | `tools/art_ops:create_path_2d` | CONTEUDO | ❌ |
| 123 | `create_patrol_route` | `tools/art_ops:create_patrol_route` | CONTEUDO | ❌ |

*\* `remove_background` não testável sem `rembg` instalado.*

### 17. SISTEMAS DE ARMAS E BALANCEAMENTO (CONTEUDO)

| # | Tool | Handler | Fase | Testada |
|---|---|---|---|---|
| 124 | `create_gun_system` | `tools/balance_ops:create_gun_system` | CONTEUDO | ❌ |
| 125 | `create_bullet_template` | `tools/balance_ops:create_bullet_template` | CONTEUDO | ❌ |
| 126 | `dps_calculator` | `tools/balance_ops:dps_calculator` | CONTEUDO | ❌ |
| 127 | `balance_analyze` | `tools/balance_ops:balance_analyze` | CONTEUDO | ❌ |
| 128 | `loot_table_generate` | `tools/balance_ops:loot_table_generate` | CONTEUDO | ❌ |
| 129 | `wave_generate` | `tools/balance_ops:wave_generate` | CONTEUDO | ✅ (corrigido) |
| 130 | `terrain_generate` | `tools/world_gen:terrain_generate` | CONTEUDO | ✅ |
| 131 | `dungeon_generate` | `tools/world_gen:dungeon_generate` | CONTEUDO | ❌ |
| 132 | `generate_dungeon_rooms` | `tools/world_gen:generate_dungeon_rooms` | CONTEUDO | ❌ |

### 18. ÁUDIO (PROTOTIPO + CONTEUDO)

| # | Tool | Handler | Fase | Testada |
|---|---|---|---|---|
| 133 | `audio_manage` | `tools/audio_ops` (rollup) | PROTOTIPO | ❌ |
| 134 | `generate_audio_sfx` | `tools/audio_ops:generate_audio_sfx` | PROTOTIPO | ❌ |
| 135 | `generate_voice` | `tools/tts_ops:generate_voice` | CONTEUDO | ❌ |

### 19. ANIMAÇÃO E VFX (PROTOTIPO)

| # | Tool | Handler | Fase | Testada |
|---|---|---|---|---|
| 136 | `anim_manage` | `tools/anim_ops` (rollup) | PROTOTIPO | ❌ |
| 137 | `create_animation_tree` | `tools/anim_ops:create_animation_tree` | PROTOTIPO | ❌ |
| 138 | `vfx_manage` | `tools/vfx_ops` (rollup) | PROTOTIPO | ❌ |

### 20. CÂMERA (PROTOTIPO)

| # | Tool | Handler | Fase | Testada |
|---|---|---|---|---|
| 139 | `camera_manage` | `tools/camera_ops` (rollup) | PROTOTIPO | ❌ |

### 21. SHADERS (PROTOTIPO)

| # | Tool | Handler | Fase | Testada |
|---|---|---|---|---|
| 140 | `shader_manage` | `tools/shader_ops` (rollup) | PROTOTIPO | ❌ |
| 141 | `shader_generate` | `tools/shader_ops:shader_generate` | PROTOTIPO | ✅ |
| 142 | `shader_list_templates` | `tools/shader_ops:shader_list_templates` | PROTOTIPO | ✅ |

### 22. FÍSICA E NAVEGAÇÃO (PROTOTIPO + CONTEUDO)

| # | Tool | Handler | Fase | Testada |
|---|---|---|---|---|
| 143 | `physics_manage` | `tools/physics_ops` (rollup) | PROTOTIPO | ❌ |
| 144 | `navigation_manage` | `tools/navigation_ops` (rollup) | CONTEUDO | ❌ |

### 23. TILEMAP E MUNDO (CONTEUDO)

| # | Tool | Handler | Fase | Testada |
|---|---|---|---|---|
| 145 | `tilemap_manage` | `tools/tilemap_ops` (rollup) | CONTEUDO | ❌ |

### 24. 3D (PROTOTIPO + CONTEUDO)

| # | Tool | Handler | Fase | Testada |
|---|---|---|---|---|
| 146 | `generate_3d_asset` | `tools/threed_gen:generate_3d_asset` | PROTOTIPO | ❌ |
| 147 | `generate_3d_placeholder` | `tools/threed_gen:generate_3d_placeholder` | PROTOTIPO | ❌ |
| 148 | `import_3d_model` | `tools/asset_ops:import_3d_model` | CONTEUDO | ❌ |
| 149 | `d3_manage` | `tools/threed_gen:d3_manage` (rollup) | CONTEUDO | ❌ |

### 25. DIÁLOGO, INVENTÁRIO E GAMESTATE (CONTEUDO)

| # | Tool | Handler | Fase | Testada |
|---|---|---|---|---|
| 150 | `dialogue_manage` | `tools/dialogue_ops` (rollup) | CONTEUDO | ❌ |
| 151 | `inventory_manage` | `tools/inventory_ops` (rollup) | CONTEUDO | ❌ |
| 152 | `gamestate_manage` | `tools/gamestate_ops` (rollup) | CONTEUDO | ❌ |

### 26. JUICE / POLISH (CONTEUDO)

| # | Tool | Handler | Fase | Testada |
|---|---|---|---|---|
| 153 | `juice_apply` | `tools/juice_ops:juice_apply` | CONTEUDO | ❌ |
| 154 | `juice_list_presets` | `tools/juice_ops:juice_list_presets` | CONTEUDO | ❌ |

### 27. LOCALIZAÇÃO E VOZ (CONTEUDO)

| # | Tool | Handler | Fase | Testada |
|---|---|---|---|---|
| 155 | `setup_localization` | `tools/localization_ops:setup_localization` | CONTEUDO | ❌ |
| 156 | `add_translation_string` | `tools/localization_ops:add_translation_string` | CONTEUDO | ❌ |

### 28. UI (DESIGN)

| # | Tool | Handler | Fase | Testada |
|---|---|---|---|---|
| 157 | `ui_manage` | `tools/ui_ops/rollups` (rollup) | DESIGN | ❌ |

### 29. CONFIG (DESIGN)

| # | Tool | Handler | Fase | Testada |
|---|---|---|---|---|
| 158 | `config_manage` | `tools/config_ops` (rollup) | DESIGN | ❌ |

### 30. ANÁLISE E SINAIS (DESIGN + PROTOTIPO)

| # | Tool | Handler | Fase | Testada |
|---|---|---|---|---|
| 159 | `analyze_signal_flow` | `tools/analyze_signal_flow:analyze_signal_flow` | DESIGN, PROTOTIPO | ❌ |

### 31. SEGURANÇA (CORE + POLIMENTO)

| # | Tool | Handler | Fase | Testada |
|---|---|---|---|---|
| 160 | `safety_manage` | `tools/safety:safety_manage` | CORE | ✅ |
| 161 | `set_safety_policy` | `tools/safety_policy:set_safety_policy` | POLIMENTO | ❌ |
| 162 | `security_status` | `tools/security_ops:security_status` | POLIMENTO | ❌ |
| 163 | `configure_security` | `tools/security_ops:configure_security` | POLIMENTO | ❌ |
| 164 | `circuit_breaker_status` | `tools/security_ops:circuit_breaker_status` | POLIMENTO | ❌ |

### 32. PROVA E AUDITORIA (CORE + IDEIA)

| # | Tool | Handler | Fase | Testada |
|---|---|---|---|---|
| 165 | `capture_proof` | `tools/proof_ledger:capture_proof` | CORE | ✅ |
| 166 | `verify_proof` | `tools/proof_ledger:verify_proof` | CORE | ❌ |

### 33. TOOL CATALOG (CORE)

| # | Tool | Handler | Fase | Testada |
|---|---|---|---|---|
| 167 | `tool_catalog` | `tools/dynamic_groups:tool_catalog` | CORE | ✅ |
| 168 | `tool_groups` | `tools/dynamic_groups:tool_groups` | CORE | ❌ |

### 34. TESTES E VERIFICAÇÃO (POLIMENTO)

| # | Tool | Handler | Fase | Testada |
|---|---|---|---|---|
| 169 | `test_manage` | `tools/test_ops` (rollup) | POLIMENTO | ❌ |
| 170 | `run_gut_tests` | `tools/gut_ops:run_gut_tests` | POLIMENTO | ❌ |
| 171 | `run_scripted_tests` | `tools/test_ops:run_scripted_tests` | POLIMENTO | ✅ (após correção) |
| 172 | `regression_test` | `tools/test_ops:regression_test` | POLIMENTO | ❌ |
| 173 | `smoke_test` | `tools/test_ops:smoke_test` | POLIMENTO | ❌ |
| 174 | `run_verification_pipeline` | `tools/verification_ops:run_verification_pipeline` | POLIMENTO | ✅ |
| 175 | `estimate_tool_tokens` | `tools/test_ops:estimate_tool_tokens` | POLIMENTO | ❌ |

### 35. DEBUG (POLIMENTO)

| # | Tool | Handler | Fase | Testada |
|---|---|---|---|---|
| 176 | `debug_manage` | `tools/debugger_ops` (rollup) | POLIMENTO | ❌ |
| 177 | `debugger_set_breakpoint` | `tools/debugger_ops:debugger_set_breakpoint` | POLIMENTO | ❌ |
| 178 | `debugger_status` | `tools/debugger_ops:debugger_status` | POLIMENTO | ❌ |
| 179 | `debugger_step` | `tools/debugger_ops:debugger_step` | POLIMENTO | ❌ |
| 180 | `debugger_get_stack` | `tools/debugger_ops:debugger_get_stack` | POLIMENTO | ❌ |
| 181 | `debugger_get_variables` | `tools/debugger_ops:debugger_get_variables` | POLIMENTO | ❌ |

### 36. PERFORMANCE (POLIMENTO)

| # | Tool | Handler | Fase | Testada |
|---|---|---|---|---|
| 182 | `profile_frame` | `tools/perf_ops:profile_frame` | POLIMENTO | ❌ |
| 183 | `profile_memory` | `tools/perf_ops:profile_memory` | POLIMENTO | ❌ |

### 37. AUDITORIA DE SEGURANÇA (POLIMENTO)

| # | Tool | Handler | Fase | Testada |
|---|---|---|---|---|
| 184 | `get_audit_log` | `tools/security_ops:get_audit_log` | POLIMENTO | ❌ |
| 185 | `get_audit_replay` | `tools/security_ops:get_audit_replay` | POLIMENTO | ❌ |

### 38. VISION / SCREENSHOT AUTOMÁTICO (POLIMENTO)

| # | Tool | Handler | Fase | Testada |
|---|---|---|---|---|
| 186 | `vision_manage` | `tools/vision_ops` (rollup) | POLIMENTO | ❌ |
| 187 | `auto_screenshot` | `tools/screenshot_ops:auto_screenshot` | POLIMENTO | ❌ |
| 188 | `set_auto_dismiss` | `tools/set_auto_dismiss:set_auto_dismiss` | POLIMENTO | ❌* |

*\* `set_auto_dismiss` não testável sem Godot rodando em debug.*

### 39. VIBE CODING (POLIMENTO)

| # | Tool | Handler | Fase | Testada |
|---|---|---|---|---|
| 189 | `vibe_coding_mode` | `tools/vibe_ops:vibe_coding_mode` | POLIMENTO | ❌ |
| 190 | `get_vibe_context` | `tools/vibe_ops:get_vibe_context` | POLIMENTO | ❌ |

### 40. WORKFLOW E CI (POLIMENTO)

| # | Tool | Handler | Fase | Testada |
|---|---|---|---|---|
| 191 | `workflow_snapshot` | `tools/workflow_ops:workflow_snapshot` | POLIMENTO | ✅ |
| 192 | `workflow_handoff` | `tools/workflow_ops:workflow_handoff` | POLIMENTO | ✅ |
| 193 | `generate_ci_snippet` | `tools/workflow_ops:generate_ci_snippet` | POLIMENTO | ❌ |

### 41. ADDON (PRONTO_PARA_LANCAR)

| # | Tool | Handler | Fase | Testada |
|---|---|---|---|---|
| 194 | `addon_connect` | `tools/addon_bridge:addon_connect` | PRONTO_PARA_LANCAR | ❌ |
| 195 | `addon_disconnect` | `tools/addon_bridge:addon_disconnect` | PRONTO_PARA_LANCAR | ❌ |
| 196 | `addon_ping` | `tools/addon_bridge:addon_ping` | PRONTO_PARA_LANCAR | ❌ |
| 197 | `addon_is_available` | `tools/addon_bridge:addon_is_available` | PRONTO_PARA_LANCAR | ❌ |
| 198 | `addon_get_scene_tree` | `tools/addon_bridge:addon_get_scene_tree` | PRONTO_PARA_LANCAR | ❌ |
| 199 | `addon_take_screenshot` | `tools/addon_bridge:addon_take_screenshot` | PRONTO_PARA_LANCAR | ❌ |
| 200 | `addon_create_node` | `tools/addon_bridge:addon_create_node` | PRONTO_PARA_LANCAR | ❌ |
| 201 | `addon_delete_node` | `tools/addon_bridge:addon_delete_node` | PRONTO_PARA_LANCAR | ❌ |
| 202 | `addon_set_property` | `tools/addon_bridge:addon_set_property` | PRONTO_PARA_LANCAR | ❌ |
| 203 | `addon_duplicate_node` | `tools/addon_bridge:addon_duplicate_node` | PRONTO_PARA_LANCAR | ❌ |
| 204 | `addon_reparent_node` | `tools/addon_bridge:addon_reparent_node` | PRONTO_PARA_LANCAR | ❌ |
| 205 | `addon_batch_edit` | `tools/addon_bridge:addon_batch_edit` | PRONTO_PARA_LANCAR | ❌ |

### 42. EXPORTAÇÃO E DEPLOY (PRONTO_PARA_LANCAR)

| # | Tool | Handler | Fase | Testada |
|---|---|---|---|---|
| 206 | `export_manage` | `tools/export_ops` (rollup) | PRONTO_PARA_LANCAR | ✅ (gate testado) |
| 207 | `configure_export_preset` | `tools/export_ops:configure_export_preset` | PRONTO_PARA_LANCAR | ❌ |
| 208 | `release_checklist` | `tools/deploy_ops:release_checklist` | PRONTO_PARA_LANCAR | ✅ |
| 209 | `deploy_itch` | `tools/deploy_ops:deploy_itch` | PRONTO_PARA_LANCAR | ❌ |
| 210 | `build_csharp` | `tools/csharp_build:build_csharp` | PRONTO_PARA_LANCAR | ❌ |
| 211 | `read_console_output` | `tools/console_ops:read_console_output` | PRONTO_PARA_LANCAR | ❌ |

### 43. FIND UNUSED RESOURCES (CONTEUDO + POLIMENTO)

| # | Tool | Handler | Fase | Testada |
|---|---|---|---|---|
| 212 | `find_unused_resources` | `tools/find_unused_resources:find_unused_resources` | CONTEUDO, POLIMENTO | ❌ |

---

## FERRAMENTAS DE SUPORTE (NÃO SÃO TOOLS MCP)

As seguintes funções auxiliam as tools MCP mas não são expostas diretamente:

- `runtime_bridge_client.py` — Bridge TCP para runtime Godot (usado por `game_*` e `godot_*`)
- `tools/bridge.py` — `GodotBridge` (WebSocket para addon Godot)
- `tools/classdb.py` — Cache da API de classes Godot
- `tools/rate_limiter.py` — Rate limiter (Feature 2, aplica-se a todas as tools)
- `tools/validate_write.py` — Validação de escrita GDScript
- `tools/subprocess_utils.py` — Helpers de subprocess
- `tools/cache_utils.py` — Utilitários de cache
- `tools/friendly_errors.py` — Mensagens de erro amigáveis
- `tools/config_loader.py` — Carregamento de configuração
- `tools/config_lock.py` — Lock de configuração
- `tools/fuzzy_suggest.py` — Sugestão fuzzy de ferramentas
- `tools/registry_validation.py` — Validação de registro MCP

---

## ESTATÍSTICAS FINAIS

| Métrica | Valor |
|---|---|
| **Tools MCP** | **212 únicas** |
| CORE | 27 |
| Apenas IDEIA | 18 |
| Apenas DESIGN | 21 |
| Apenas PROTOTIPO | 65 |
| Apenas CONTEUDO | 35 |
| Apenas POLIMENTO | 30 |
| Apenas PRONTO_PARA_LANCAR | 18 |
| Em múltiplas fases | 2 (analyze_signal_flow, find_unused_resources) |
| **Testadas (✅)** | **26 de 212 (~12%)** |
| **Não testadas individualmente** | **186** |
| Arquivos de handler | 70+ em `tools/` |
| Linhas de server.py | 6.391 |
| Rollup tools (manage tools) | 18+ (scene_manage, node_manage, etc.) |
| Handlers diretos em server.py | ~15 (ping, health_check, read_file, write_file, etc.) |

**Arquivo gerado em:** `c:\Users\joabc\OneDrive\Documentos\VS CODE\mcp-godot-desenvolvimento\CATALOGO_COMPLETO_MCP_GODOT.md`