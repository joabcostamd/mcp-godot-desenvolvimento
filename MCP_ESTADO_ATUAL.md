# MCP GODOT AGENT — ESTADO ATUAL (12/07/2026)

## DOCUMENTO DE REFERÊNCIA COMPLETO

**Propósito:** Este documento descreve absolutamente tudo que uma IA precisa saber sobre o MCP Godot Agent para usar, expandir ou auditar o sistema. Cobre arquitetura, ferramentas, protocolos, configuração, limitações e histórico de patches.

---

## 1. VISÃO GERAL

| Item | Valor |
|------|-------|
| **Nome** | MCP Godot Agent (godot-mcp-agent) |
| **Versão** | 3.2.1 |
| **Linguagem** | Python 3.12+ (server), GDScript (addons) |
| **Framework MCP** | `mcp.server` (Python MCP SDK, stdio) |
| **Engine** | Godot 4.7 stable |
| **Modelo recomendado** | DeepSeek V4 Pro |
| **Ponto de entrada** | `server.py` (~7400 linhas) |
| **Total de ferramentas** | 191 (27 rollups + 164 named tools) |
| **Módulos Python** | 69 em `tools/` |
| **Perfis** | `--profile core` (31) / `dev` (80) / `full` (191) |
| **Toolsets** | 10 grupos via `--toolsets` |
| **Bugs corrigidos** | 49 em 12 rodadas de auditoria |
| **Repositório** | `c:\Users\joabc\OneDrive\Documentos\VS CODE\mcp-godot-desenvolvimento\` |
| **GitHub** | `https://github.com/joabcostamd/mcp-godot-desenvolvimento` |

---

## 2. ARQUITETURA (3 CAMADAS)

```
┌─────────────────────────────────────────────────┐
│ CAMADA 1 — Server Core (server.py)               │
│ • JSON-RPC 2.0 sobre stdio                       │
│ • Rate limiting (rate_limiter.py)                │
│ • Error codes: 1001(input) 2001(projeto)         │
│   3001(Godot) 4001(conexão) 5000(interno)        │
│ • 2 caches globais: _TOOL_DEFS_CACHE,            │
│   _HANDLERS_CACHE                                 │
├─────────────────────────────────────────────────┤
│ CAMADA 2 — Tool Definitions + Handlers            │
│ • _tool_defs() → lista Tool(schema)              │
│ • _build_handlers() → dict nome→callable         │
│ • TOOLSETS: 10 grupos nomeados                   │
│ • --toolsets <grupo> filtra na inicialização     │
│ • Rollups: Fase 2A/C1 unificam 80+ handlers      │
├─────────────────────────────────────────────────┤
│ CAMADA 3 — Implementações (tools/*.py)            │
│ • 69 módulos Python                             │
│ • Comunicação TCP/WebSocket com Godot            │
│ • Sistema de backup/undo automático              │
│ • Saga Engine + Reconciliation Loop              │
└─────────────────────────────────────────────────┘
```

---

## 3. PROTOCOLOS DE CONEXÃO COM GODOT

| Porta | Protocolo | Propósito | Módulo Python | Arquivo GDScript |
|-------|-----------|-----------|---------------|------------------|
| 9080 | TCP | Editor Bridge (comandos no editor) | `tools/editor_bridge.py` | `addons/mcp_addon/mcp_addon.gd` |
| 9081 | TCP | Game Bridge (jogo rodando) | `tools/game_bridge.py` | (legado, substituído por 8790) |
| 9082 | WebSocket | Addon Bridge (UndoRedo nativo) | `tools/addon_bridge.py` | `addons/mcp_addon/mcp_addon.gd` |
| 8790 | TCP | Runtime Bridge PATCH 12 | `runtime_bridge_client.py` | `addons/mcp_runtime_bridge/runtime_bridge.gd` |
| 6005 | TCP | LSP (Language Server Protocol) | `tools/lsp_ops.py` | — (nativo do Godot) |
| 6006 | TCP | DAP (Debug Adapter Protocol) | `tools/debugger_ops.py` | — (nativo do Godot) |

---

## 4. TOOLSETS (Curadoria PATCH 17)

Flag de inicialização: `python server.py --toolsets <grupo1>,<grupo2>`

```json
{
  "core":          ["ping","health_check","self_test","bootstrap_godot_mcp","read_file","write_file","safe_write_gdscript","compile_test","run_game","stop_game","smart_restart","git_commit_checkpoint","smoke_test","dump_mcp_state","run_verification_pipeline"],
  "scene_ops":     ["scene_manage","node_manage"],
  "script_ops":    ["script_manage","safe_write_gdscript","validate_gdscript_syntax","gdscript_diagnostics","gdscript_references","gdscript_definition"],
  "test_ops":      ["run_gut_tests","effect_probe","godot_exec","get_runtime_state_digest","capture_runtime_errors","run_scripted_tests","smoke_test","regression_test","dump_mcp_state","estimate_tool_tokens","run_verification_pipeline"],
  "runtime_ops":   ["run_game","stop_game","smart_restart","compile_test","execute_gdscript_runtime","capture_game_screenshot","godot_screenshot","godot_runtime_info","godot_custom_command","godot_list_custom_commands","godot_run_project","godot_stop_project","godot_wait_for_bridge"],
  "git_ops":       ["git_commit_checkpoint","safety_manage"],
  "refs_ops":      ["find_missing_references","search_codebase","validate_project_refs","find_usages"],
  "asset_ops":     ["asset_manage","generate_placeholder_sprite","generate_game_art","generate_game_art_flux","import_texture","import_sprite_sheet","import_asset_manifest","create_asset_manifest"],
  "design_ops":    ["analyze_game_structure","suggest_next_steps","validate_game_design","estimate_game_scope","project_status","create_entity","godot_class_ref"],
  "ui_ops":        ["ui_manage","create_main_menu","create_hud_template","create_pause_menu","create_health_bar"]
}
```

---

## 5. CATÁLOGO COMPLETO DE FERRAMENTAS (191)

### 5.1 — CORE / SAÚDE (7)

| Ferramenta | Descrição | Parâmetros |
|------------|-----------|------------|
| `ping` | Verifica se servidor MCP está vivo | `{}` |
| `health_check` | Saúde de todos os componentes (config, Godot, ClassDB, templates) | `{}` |
| `self_test` | Suite de testes internos (ping, ClassDB, parser, Jinja2, Pillow) | `{}` |
| `validate_godot_version` | Verifica se Godot é 4.7.x | `{}` |
| `validate_mcp_environment` | Verifica Python, dependências, server.py | `{}` |
| `bootstrap_godot_mcp` | 🚀 Bootstrap: conecta VS Code→MCP→Godot em 1 chamada | `target` (full/connect_only/validate_only), `project_path`, `godot_path`, `launch_editor`, `timeout_godot`, `timeout_addon` |
| `godot_keep_alive` | Garante editor Godot aberto (NÃO fecha) | `project_path`, `godot_path` |

### 5.2 — PROJETO (8)

| Ferramenta | Descrição | Parâmetros |
|------------|-----------|------------|
| `set_active_project` | Define projeto alvo | `project_path`* |
| `create_project` | Cria projeto 4.7 com pastas padrão | `name`*, `path`*, `renderer` (forward_plus/mobile/compatibility) |
| `get_project_settings` | Lê project.godot | `section` |
| `set_project_setting` | Define config no project.godot | `section`*, `key`*, `value`* |
| `set_main_scene` | Define cena principal | `scene_path`* |
| `inspect_project` | Lista arquivos por categoria | `filter` (scenes/scripts/assets/all) |
| `generate_project_structure` | Estrutura completa de pastas/arquivos | `template` (2d/3d/mobile), `project_path` |
| `project_status` | Status: cenas, scripts, sprites, assets, sugestões | `{}` |

### 5.3 — ARQUIVOS (4)

| Ferramenta | Descrição | Parâmetros |
|------------|-----------|------------|
| `read_file` | Lê conteúdo (com range de linhas) | `path`*, `start_line`, `end_line` |
| `write_file` | Cria/modifica arquivo | `path`*, `content`*, `mode` (create/overwrite/append) |
| `delete_file` | Remove com backup automático | `path`* |
| `move_file` | Move/renomeia, atualiza referências | `from_path`*, `to_path`* |

### 5.4 — CENAS (11)

| Ferramenta | Descrição | Parâmetros |
|------------|-----------|------------|
| `create_scene` | Cria .tscn com nó raiz | `name`*, `root_type`*, `path`* |
| `load_scene_tree` | Árvore hierárquica de nós | `scene_path`*, `max_depth` |
| `add_node` | Adiciona nó a cena | `scene_path`*, `parent_node_path`*, `node_name`*, `node_type`* |
| `delete_node` | Remove nó com descendentes | `scene_path`*, `node_path`* |
| `set_node_property` | Define propriedade de nó | `scene_path`*, `node_path`*, `property_name`*, `value`* |
| `get_node_property` | Lê propriedade de nó | `scene_path`*, `node_path`*, `property_name`* |
| `reparent_node` | Move nó para novo pai | `scene_path`*, `node_path`*, `new_parent_path`* |
| `instance_scene_as_child` | Instancia sub-cena | `scene_path`*, `parent_node_path`*, `instanced_scene_path`*, `instance_name` |
| `connect_signal` | Conecta sinal → método | `scene_path`*, `from_node_path`*, `signal_name`*, `to_node_path`*, `method_name`* |
| `list_signals` | Sinais de tipo de nó | `node_type`, `scene_path`, `node_path` |
| `list_valid_node_types` | Todos os tipos de nó válidos | `{}` |

### 5.5 — CLASSDB (3)

| Ferramenta | Descrição | Parâmetros |
|------------|-----------|------------|
| `query_classdb` | Consulta COMPLETA com paginação | `class_name`*, `section` (all/properties/methods/signals/enums/constants), `include_inherited`, `offset`, `limit` |
| `search_classdb` | Busca fuzzy por nome de classe | `query`*, `limit` |
| `godot_class_ref` | Métodos, props, sinais, enums, consts Nativos (extension_api.json) | `class_name`* |

### 5.6 — SCRIPTS (9)

| Ferramenta | Descrição | Parâmetros |
|------------|-----------|------------|
| `generate_gdscript` | Template Jinja2 → GDScript | `template`*, `save_path`*, `variables` |
| `attach_script` | Anexa script a nó | `scene_path`*, `node_path`*, `script_path`* |
| `detach_script` | Remove script de nó | `scene_path`*, `node_path`* |
| `validate_gdscript_syntax` | Validação via compilador Godot | `script_path`* |
| `add_script_variable` | @export var em script | `script_path`*, `var_name`*, `var_type`, `default_value`, `export` |
| `add_script_signal` | Signal declaration | `script_path`*, `signal_name`*, `args` |
| `safe_write_gdscript` | Escreve .gd COM validação | `file_path`*, `content`*, `project_path`, `strict` |
| `create_state_machine` | FSM (enum + enter/update/exit) | `script_path`*, `states`*, `initial_state`* |
| `add_state_transition` | Transição condicional na FSM | `script_path`*, `from_state`*, `to_state`*, `condition_code`* |

### 5.7 — LSP BRIDGE (9)

| Ferramenta | Descrição | Parâmetros |
|------------|-----------|------------|
| `gdscript_lsp_connect` | Conecta ao LSP (porta 6005) | `project_root` |
| `gdscript_lsp_disconnect` | Desconecta do LSP | `{}` |
| `gdscript_references` | Find all references | `file_path`*, `line`*, `character`* |
| `gdscript_definition` | Go to definition | `file_path`*, `line`*, `character`* |
| `gdscript_hover` | Tipo/documentação de símbolo | `file_path`*, `line`*, `character`* |
| `gdscript_symbols` | Símbolos do arquivo | `file_path`* |
| `gdscript_rename` | Renomeia símbolo semântico | `file_path`*, `line`*, `character`*, `new_name`* |
| `gdscript_diagnostics` | Erros/warnings em tempo real | `file_path`* |
| `gdscript_sync_file` | Notifica LSP de alterações | `file_path`*, `content` |

### 5.8 — FÍSICA (4)

| Ferramenta | Descrição | Parâmetros |
|------------|-----------|------------|
| `add_collision_shape` | CollisionShape2D/3D com shape | `scene_path`*, `parent_node_path`*, `shape_type`* (rectangle/circle/capsule), `dimensions`* |
| `set_collision_layer_mask` | Layers/masks de colisão | `scene_path`*, `node_path`*, `layer_bits`*, `mask_bits`* |
| `set_physics_material` | PhysicsMaterial (bounce, friction) | `scene_path`*, `node_path`*, `bounce`, `friction`, `absorb`, `rough` |
| `create_joint_2d` | PinJoint2D/GrooveJoint2D | `scene_path`*, `node_a_path`*, `node_b_path`*, `joint_type` (pin/groove) |

### 5.9 — INPUT / AUTOLOAD (3)

| Ferramenta | Descrição | Parâmetros |
|------------|-----------|------------|
| `configure_input_action` | Configura InputMap | `action_name`*, `keys`*, `joypad_buttons` |
| `configure_autoload` | Singleton global | `name`*, `script_path`*, `singleton` |
| `install_mcp_addon` | Instala addon MCP Addon + Runtime Bridge | `project_path` |

### 5.10 — RUNTIME / EDITOR (8)

| Ferramenta | Descrição | Parâmetros |
|------------|-----------|------------|
| `compile_test` | Verificação de compilação | `{}` |
| `run_game` | Inicia jogo como processo | `scene_path` |
| `stop_game` | Encerra jogo + console | `{}` |
| `smart_restart` | Reinício inteligente (mata→addons→compila→inicia→conecta) | `project_path` |
| `launch_editor` | Abre editor Godot | `scene_path` |
| `close_editor` | Fecha editor | `{}` |
| `take_screenshot` | Screenshot do viewport 2D | `{}` |
| `read_console_output` | Últimas linhas do console | `since_timestamp` |

### 5.11 — TILEMAP (3)

| Ferramenta | Descrição | Parâmetros |
|------------|-----------|------------|
| `create_tileset` | TileSet .tres | `tileset_name`*, `save_path`*, `tile_width`, `tile_height` |
| `create_tilemap_layer` | TileMapLayer em cena | `scene_path`*, `parent_node_path`*, `layer_name`*, `tileset_path`* |
| `paint_tilemap_cell` | Marca célula pintada | `scene_path`*, `layer_node_path`*, `cell_x`*, `cell_y`* |

### 5.12 — ANIMAÇÃO (3)

| Ferramenta | Descrição | Parâmetros |
|------------|-----------|------------|
| `create_animation_player` | AnimationPlayer | `scene_path`*, `parent_node_path`*, `player_name` |
| `create_animation` | Animação com keyframes | `scene_path`*, `anim_player_path`*, `anim_name`*, `track_path`*, `track_type`*, `keyframes`*, `fps` |
| `create_animation_tree` | AnimationTree (blend trees) | `scene_path`*, `parent_node_path`*, `player_name`, `root_type` |

### 5.13 — UI (6)

| Ferramenta | Descrição | Parâmetros |
|------------|-----------|------------|
| `create_ui_scene` | Cena UI com CanvasLayer+Control | `name`*, `path`* |
| `add_control_node` | Nó UI (Label, Button, Panel...) | `scene_path`*, `parent_node_path`*, `node_name`*, `node_type`*, `properties` |
| `create_main_menu` | Menu principal completo | `scene_name`*, `game_title`*, `buttons`, `style` (modern/retro/cartoon/dark_fantasy/sci_fi) |
| `create_hud_template` | HUD (score/health/ammo/wave/timer) | `scene_name`, `elements`, `position` |
| `create_pause_menu` | Menu pausa overlay+script ESC | `scene_name`, `overlay_alpha` |
| `create_health_bar` | Barra de vida com animação | `scene_path`*, `parent_node_path`, `max_health`, `fill_color`, `bg_color`, `show_text` |

### 5.14 — EXPORT / SEGURANÇA / BACKUP (8)

| Ferramenta | Descrição |
|------------|-----------|
| `list_export_presets` | Lista presets |
| `validate_export_templates_installed` | Verifica templates |
| `build_export` | Exporta para executável |
| `list_backups` | Lista backups |
| `restore_backup` | Restaura backup |
| `git_commit_checkpoint` | Commit git |
| `configure_security` | Token de segurança |
| `security_status` | Status de segurança |

### 5.15 — GAME BRIDGE (runtime, 15)

| Ferramenta | Descrição |
|------------|-----------|
| `inject_input_event` | Injeta input no jogo |
| `execute_gdscript_runtime` | Executa GDScript no jogo |
| `watch_signal` | Observa sinal |
| `game_call_method` | Chama método em nó |
| `game_spawn_node` | Cria nó dinâmico |
| `game_raycast` | Ray cast 2D/3D |
| `game_get_camera` | Posição da câmera |
| `game_play_animation` | Controla AnimationPlayer |
| `game_find_nodes_by_class` | Find nodes |
| `game_await_signal` | Espera sinal com timeout |
| `game_pause` | Pausa/despausa |
| `game_performance` | FPS, memória, draw calls |
| `game_window` | Controle de janela |
| `game_input_state` | Estado de input |
| `game_serialize_state` | Save/load state JSON |

### 5.16 — VISÃO / SCREENSHOTS (6)

| Ferramenta | Descrição |
|------------|-----------|
| `capture_game_screenshot` | Screenshot off-screen |
| `compare_screenshots` | Compara screenshots |
| `detect_empty_screen` | Detecta tela vazia |
| `detect_offscreen_elements` | Nós fora da viewport |
| `record_gameplay_gif` | Grava GIF animado |
| `auto_screenshot` | Screenshots para loja |

### 5.17 — BATCH (3)

| Ferramenta | Descrição |
|------------|-----------|
| `add_nodes_batch` | Múltiplos nós |
| `set_properties_batch` | Múltiplas props |
| `batch_atomic_edit` | ⚛️ Edição atômica com rollback |

### 5.18 — ASSETS PROCEDURAIS (5)

| Ferramenta | Descrição |
|------------|-----------|
| `generate_placeholder_sprite` | PNG geométrico |
| `generate_placeholder_texture_atlas` | Sprite sheet procedural |
| `generate_background_gradient` | Fundo gradiente |
| `generate_tileset_from_colors` | Tileset + PNG |
| `suggest_color_palette` | Paleta por gênero |

### 5.19 — ÁUDIO (4)

| Ferramenta | Descrição |
|------------|-----------|
| `generate_audio_sfx` | 24 tipos de SFX (beep, jump, laser...) |
| `generate_voice` | TTS offline (Kokoro/Edge) |
| `configure_audio_bus` | Bus de áudio |
| `add_audio_effect` | Efeito (reverb, delay, EQ) |

### 5.20 — ARTE IA (10)

| Ferramenta | Descrição |
|------------|-----------|
| `generate_game_art` | DALL-E via Playwright |
| `apply_game_art` | Aplica em AnimatedSprite2D |
| `generate_game_art_flux` | FLUX.2 API |
| `remove_background` | rembg/birefnet |
| `optimize_sprite` | oxipng/pngquant |
| `create_spritesheet` | Junta frames |
| `import_texture` | Importa textura |
| `import_sprite_sheet` | Importa + animações |
| `import_audio` | Importa WAV/OGG/MP3 |
| `import_3d_model` | Importa .glb/.gltf |

### 5.21 — IA AGÊNTICA (8)

| Ferramenta | Descrição |
|------------|-----------|
| `analyze_game_structure` | Métricas do projeto |
| `suggest_next_steps` | Próximos passos |
| `find_missing_references` | Refs quebradas |
| `validate_game_design` | Checklist (score /9) |
| `estimate_game_scope` | micro→épico |
| `search_codebase` | Busca texto |
| `get_project_history` | Backups + git log |
| `project_map` | Mapa JSON/HTML |

### 5.22 — UNDO / WORKFLOW (4)

| Ferramenta | Descrição |
|------------|-----------|
| `undo_last_action` | Desfaz (histórico 20) |
| `get_undo_history` | Lista histórico |
| `workflow_snapshot` | Salva snapshot |
| `workflow_handoff` | Resumo próxima sessão |

### 5.23 — ADDON BRIDGE (Editor Ao Vivo, 12)

| Ferramenta | Descrição |
|------------|-----------|
| `addon_connect` | Conecta WebSocket 9082 |
| `addon_disconnect` | Desconecta |
| `addon_is_available` | Ping |
| `addon_ping` | Ping/pong |
| `addon_create_node` | Cria nó com UndoRedo nativo |
| `addon_delete_node` | Remove com UndoRedo |
| `addon_set_property` | Define com UndoRedo |
| `addon_reparent_node` | Move com UndoRedo |
| `addon_duplicate_node` | Duplica com UndoRedo |
| `addon_batch_edit` | Múltiplas ops em 1 UndoRedo |
| `addon_take_screenshot` | Screenshot via WebSocket |
| `addon_get_scene_tree` | Árvore da cena do editor |

### 5.24 — PLAYTEST (10)

| Ferramenta | Descrição |
|------------|-----------|
| `freeze_game_clock` | Congela relógio |
| `unfreeze_game_clock` | Descongela |
| `step_game_time` | Avança N ms |
| `step_until` | Avança até condição |
| `get_runtime_state_digest` | Estado como JSON |
| `capture_runtime_errors` | Métricas + erros |
| `watch_state_start` | Observa propriedades |
| `watch_state_collect` | Coleta histórico |
| `godot_exec` | Executa código no jogo |
| `effect_probe` | Antes/depois de ação |

### 5.25 — BALANCE (4)

| Ferramenta | Descrição |
|------------|-----------|
| `balance_analyze` | Análise de balanceamento |
| `wave_generate` | Ondas de inimigos |
| `dps_calculator` | DPS + TTK |
| `loot_table_generate` | Tabela de loot |

### 5.26 — GDD / BEHAVIOR / PERF / SHADER (8)

| Ferramenta | Descrição |
|------------|-----------|
| `gdd_generate` | Game Design Document |
| `behavior_tree_generate` | Behavior Tree NL→GDScript |
| `behavior_tree_list_templates` | Lista templates BT |
| `profile_frame` | Perfil de performance |
| `profile_memory` | Uso de memória |
| `shader_generate` | .gdshader de NL (15 templates) |
| `shader_list_templates` | Lista 15 templates |

### 5.27 — WORLD GEN (3)

| Ferramenta | Descrição |
|------------|-----------|
| `terrain_generate` | Terreno procedural (FastNoiseLite) |
| `dungeon_generate` | Dungeon BSP |
| `world_describe` | Análise de mundo |

### 5.28 — 3D (5)

| Ferramenta | Descrição |
|------------|-----------|
| `generate_3d_placeholder` | Box/sphere/cylinder |
| `generate_3d_asset` | Hyper3D Rodin |
| `create_light_3d` | Omni/Spot/Directional |
| `create_csg_shape` | CSG (box/sphere/cylinder/torus) |
| `configure_standard_material_3d` | Presets (metal/plastic/wood...) |

### 5.29 — DEPLOY / MARKETPLACE (7)

| Ferramenta | Descrição |
|------------|-----------|
| `deploy_itch` | itch.io via butler |
| `release_checklist` | Checklist /10 |
| `marketplace_search` | Kenney, Godot Assets, Poly Haven |
| `marketplace_download` | Baixa asset |
| `download_asset` | Poly Haven, Kenney, AmbientCG |
| `import_downloaded_asset` | Importa asset baixado |
| `configure_export_preset` | Preset de exportação |

### 5.30 — JUICE (2)

| Ferramenta | Descrição |
|------------|-----------|
| `juice_apply` | Game feel (coyote time, buffer, shake...) |
| `juice_list_presets` | Lista presets |

### 5.31 — DEVSOLO COMPLETO (18)

**Câmera:** `setup_camera_2d`, `setup_camera_follow`, `setup_camera_shake`

**Navegação:** `create_navigation_region_2d`, `create_navigation_agent_2d`, `bake_navigation_polygon`

**Save:** `create_save_system`, `define_save_data`

**Diálogo:** `create_dialogue_system`, `add_dialogue_node`, `create_dialogue_ui`

**Inventário:** `create_inventory_system`, `define_inventory_item`, `create_inventory_ui`

**Armas:** `create_bullet_template`, `create_gun_system`

**Partículas:** `create_particles_2d`, `configure_particles_2d`, `create_particles_3d`

**Iluminação:** `create_light_2d`

### 5.32 — RUNTIME BRIDGE (PATCH 12, 7 ferramentas)

| Ferramenta | Descrição | Parâmetros |
|------------|-----------|------------|
| `godot_screenshot` | Screenshot via bridge TCP (8790) | `{}` |
| `godot_runtime_info` | FPS, draw calls, memória, física | `{}` |
| `godot_custom_command` | Comando customizado no jogo | `name`*, `args` |
| `godot_list_custom_commands` | Lista comandos registrados | `{}` |
| `godot_run_project` | Lança jogo via CLI (retorna PID) | `project_path`*, `godot_executable`* |
| `godot_stop_project` | Encerra processo (save-before-kill) | `pid`* |
| `godot_wait_for_bridge` | Polling até bridge responder | `timeout_sec` |

### 5.33 — TESTES ROTEIRIZADOS (PATCH 14, 5 ferramentas)

| Ferramenta | Descrição | Parâmetros |
|------------|-----------|------------|
| `smoke_test` | Teste de fumaça: verifica saúde de todos os componentes | `{}` |
| `regression_test` | Teste de regressão: compara estado atual com baseline | `{}` |
| `run_scripted_tests` | Executa suite de testes scriptados (input sintético + screenshot + dump) | `test_suite`*, `project_path` |
| `dump_mcp_state` | Snapshot completo do estado do MCP (config, ClassDB, templates, tools, imports) | `{}` |
| `estimate_tool_tokens` | Estima consumo de tokens do tools/list por perfil (core/dev/full) | `profile` (core/dev/full) |

### 5.34 — VALIDAÇÃO DE REFERÊNCIAS (PATCH 15, 2 ferramentas)

| Ferramenta | Descrição | Parâmetros |
|------------|-----------|------------|
| `validate_project_refs` | Escaneia projeto por referências quebradas (.tscn, .gd, recursos) | `project_path`, `full_report` |
| `find_usages` | Busca estática de usos de um recurso/alvo no projeto (offline) | `target`*, `project_path`, `search_type` (auto/scene/script/resource), `max_results` |

### 5.35 — ASSET MANIFEST (PATCH 16, 2 ferramentas)

| Ferramenta | Descrição | Parâmetros |
|------------|-----------|------------|
| `import_asset_manifest` | Importa assets em lote via manifest JSON (5 fontes: local, URL, Poly Haven, Kenney, AmbientCG) | `manifest_path`*, `project_path` |
| `create_asset_manifest` | Gera template de asset_manifest.json para preenchimento manual | `output_path`, `template_type` (full/minimal) |

### 5.36 — VERIFICAÇÃO / PIPELINE (Item 1 do plano de evolução, 1 ferramenta)

| Ferramenta | Descrição | Parâmetros |
|------------|-----------|------------|
| `run_verification_pipeline` | Pipeline completo: compile → headless run → screenshot → GUT. Relatório JSON consolidado com status de cada etapa. Early exit na primeira falha. NÃO commita — para no relatório. | `project_path`, `godot_path`, `test_scene`, `gut_test_dir` (default: `"res://tests"`), `headless_frames` (default: 30), `timeout_compile` (default: 30s), `timeout_headless` (default: 60s), `timeout_gut` (default: 120s), `screenshot_dir` |

**Fluxo das 4 etapas:**
1. **Compile Check:** `godot --headless --quit --path <proj>` força parse de todos os scripts (substituto do `--check-only` quebrado no Windows Godot 4.7 — bug R12)
2. **Headless Run:** `godot --headless --quit-after N --path <proj> <cena>` executa cena de teste, captura stdout/stderr e detecta crash
3. **Screenshot:** `--write-movie` (sem `--headless`, usa SW_HIDE no Windows) captura PNG após N frames em `<proj>/verification_screenshots/`
4. **GUT Tests:** Chama `run_gut_tests()` existente (opcional — `skipped` se `res://tests/` não existir, não derruba o pipeline)

**Comportamento de early exit:**
- Etapa 1 falha → pipeline PARA, etapas 2-4 não executam
- Etapa 2 crasha → etapa 3 = `skipped_due_to_crash`, etapa 4 não executa
- Screenshot falha → NÃO interrompe (informativo)
- GUT `skipped` (sem testes) → NÃO derruba status geral

**Ambiguidade de cena:** Se `test_scene` não for passado e `run/main_scene` não estiver definido no `project.godot`, retorna `status: "ambiguous"` pedindo qual cena usar — não adivinha.

**Relatório JSON de saída:**
```json
{
  "status": "PASSOU" | "FALHOU",
  "overall": "PASSOU" | "FALHOU",
  "stopped_at_step": null | 1 | 2,
  "summary": "Compile: PASS (0 erros) | Headless Run: PASS | Screenshot: OK | GUT: SKIPPED (sem testes)",
  "steps": {
    "1_compile":      {"status": "passed"|"failed", "errors": [...], "error_count": N},
    "2_headless_run": {"status": "passed"|"failed", "crashed": bool, "stacktrace": [...]},
    "3_screenshot":   {"status": "success"|"failed"|"skipped_due_to_crash", "image_path": "...", "image_base64": "..."},
    "4_gut_tests":    {"status": "success"|"tests_failed"|"skipped"|"error", "results": {...}}
  }
}
```

**Uso típico:**
```
run_verification_pipeline com project_path="C:\...\star-colony"
```

---

## 6. MCPRuntimeBridge (PATCH 12)

### 6.1 — GDScript (`addons/mcp_runtime_bridge/runtime_bridge.gd`)

```gdscript
extends Node
## Autoload, ativo apenas em debug builds
## Servidor TCP em 127.0.0.1:8790
## Protocolo: JSON-por-linha

const PORT := 8790
const HOST := "127.0.0.1"

# Comandos built-in: screenshot, runtime_info, list_commands, custom, input_event, wait_frames
# Comandos custom registrados via register_command():
#   save_current_scene — PackedScene.pack() + ResourceSaver.save()
#   add_test_marker — adiciona nó SavedMarker para teste de persistência
#   replace_with_runtime_scene — substitui cena por Node() sem scene_file_path
```

### 6.2 — Cliente Python (`runtime_bridge_client.py`)

```python
def send_bridge_command(payload: dict, timeout: float = 5.0) -> dict:
    """Conecta via TCP 127.0.0.1:8790, envia JSON+\\n, recebe resposta."""
    # Timeout de conexão e recv configurável
    # BridgeUnavailable se jogo não está rodando em debug

class BridgeUnavailable(Exception):
    """Jogo não está rodando em debug."""
```

### 6.3 — Save-Before-Kill (PATCH 12.1)

`godot_stop_project` executa o seguinte fluxo antes de matar:

1. **Save via bridge**: `send_bridge_command({"cmd":"custom","name":"save_current_scene"}, timeout=2s)`
2. Se rastreado no dicionário: `proc.terminate()` → `proc.kill()` após 5s
3. Se não rastreado: verifica nome do processo (`_get_process_name`), recusa se não for "Godot", depois `taskkill /F /PID`
4. Retorna `{ok, pid, was_tracked, save_attempted, save_result}`

**Cenários validados:**
- Processo rastreado (was_tracked=true): save funciona, terminate() graceful
- Processo órfão (was_tracked=false): save funciona via bridge, taskkill fallback
- Bridge suspenso (NtSuspendProcess): save timeout 2s, kill executado mesmo assim
- Cena runtime sem arquivo: save retorna erro estruturado, kill não bloqueado
- Arquivo não corrompido em caso de falha de save (hash SHA-256 idêntico)

---

## 7. ClassDB Introspecção (PATCH 13)

`godot_class_ref(class_name)` usa **exclusivamente** `extension_api.json` (cache da API nativa do Godot 4.7).

- **NÃO** consulta o Godot rodando
- **NÃO** lê scripts `.gd` com `class_name` de projetos
- **Cobre**: métodos, propriedades, sinais, enums e constantes com herança
- **Erro tratado**: fuzzy suggestions via `difflib.get_close_matches`
- **1074 classes** no cache

### Limitação documentada:

> Cobre APENAS classes nativas do Godot (extension_api.json). NÃO retorna informação sobre classes custom do projeto (class_name em scripts .gd).

---

## 8. CONFIGURAÇÃO

### 8.1 — Cascata de carregamento (`tools/config_loader.py`)

```
1. config.local.json  (máquina-específico, NÃO commitado, no .gitignore)
2. config.json        (fallback, commitado)
3. Variáveis de ambiente (GODOT_MCP_GODOT_PATH, GODOT_MCP_PROJECTS_ROOT, etc.)
```

### 8.2 — `config.json`

```json
{
  "godot_path": "C:/Godot/Godot_v4.7-stable_win64.exe",
  "godot_console_path": "C:/Godot/Godot_v4.7-stable_win64.exe",
  "python_path": "python",
  "projects_root": "../projetos",
  "default_project": "star-colony",
  "addon_port": 9080,
  "game_port": 9081,
  "timeouts": {
    "fast": 15,
    "compile": 60,
    "export": 300
  },
  "vibe_coding": { "enabled": true },
  "security": { "allow_remote": false }
}
```

---

## 9. ORQUESTRADOR GENIUS (`tools/orchestrator.py`)

### Componentes:

| Componente | Função |
|------------|--------|
| **Saga Engine** | Sequência de passos com compensação (rollback em falha) |
| **Reconciliation Loop** | Verifica se estado real bate com o esperado após cada operação |
| **Circuit Breaker** | Bloqueia APIs externas (FLUX, Replicate, Edge TTS) após 3 falhas consecutivas |
| **Decision Engine** | Decide entre arte placeholder vs FLUX, áudio procedural vs TTS |
| **Pipeline Executor** | `create_entity`: gera entidade completa (cena + script + arte + áudio) |

---

## 10. GDScript Sandbox (`tools/gdscript_sandbox.py`)

Protege `execute_gdscript_runtime` contra código malicioso:
- **80+ padrões bloqueados**: `OS.execute()`, `FileAccess.open()`, `DirAccess`, `ResourceLoader`, `get_tree().quit()`, etc.
- **Rate limiting**: 10 chamadas/segundo
- **Timeout**: 30 segundos por execução

---

## 11. SISTEMA DE BACKUP / UNDO

- **Backup automático**: antes de qualquer escrita, o arquivo original é copiado para `_backups/`
- **Undo**: histórico circular de 20 ações, `undo_last_action` restaura
- **Git checkpoint**: `git_commit_checkpoint` commita com mensagem, valida sintaxe antes (compile gate)
- **Marcador de falha**: `.mcp_gate_failed` escrito quando validação falha, limpo em sucesso

---

## 12. HOOKS DO NUCLEO (`.github/hooks/`)

### 12.1 — `hooks.json`

```json
{
  "hooks": {
    "PreToolUse": [{"type":"command","windows":"powershell ... block-dangerous.ps1","timeoutSec":5}],
    "PostToolUse": [{"type":"command","windows":"powershell ... check-gdscript-syntax.ps1","timeoutSec":15}],
    "Stop": [{"type":"command","windows":"powershell ... block-uncommitted.ps1","timeoutSec":10}]
  }
}
```

### 12.2 — Scripts

| Script | Evento | Função |
|--------|--------|--------|
| `block-dangerous.ps1` | PreToolUse | Bloqueia `rm -rf`, `git reset --hard`, `Remove-Item -Recurse -Force`, `taskkill /F /IM`, `DROP TABLE`, `format X:` |
| `check-gdscript-syntax.ps1` | PostToolUse | Valida .gd via regex PowerShell puro (R1: var duplicada, R2: `:=` com dict, sintaxe quebrada) |
| `block-uncommitted.ps1` | Stop | Bloqueia encerramento com working tree sujo |

### 12.3 — Limitação documentada do checker GDScript

> `GDScript.reload()` via `--headless --script` não funciona no Windows Godot 4.7: stdout/stderr/FileAccess.WRITE/exit code todos falham. O hook usa regex PowerShell puro para R1/R2 e sintaxe quebrada. Cobertura total exigiria LSP bridge ou Godot editor.

---

## 13. HISTÓRICO DE PATCHES IMPLEMENTADOS

| Patch | Commit | Descrição |
|-------|--------|-----------|
| 1-11 | `16b6ff1`→`037aa89` | Validação, commit gate, FLUX, portabilidade, etc. (PARTE 1) |
| 12 | `f18bba3`→`8d6f1ac` | Runtime Bridge: TCP server GDScript + cliente Python + 4 tools |
| 12.1 | `19cd51a`→`71f69b2` | Process Lifecycle: run/stop/wait + save-before-kill + proteção PID |
| 13 | `38b8837`→`6a7b039` | ClassDB introspecção: godot_class_ref (extension_api.json) |
| 14 | — | Testes roteirizados: smoke_test, regression_test, run_scripted_tests, dump_mcp_state, estimate_tool_tokens |
| 15 | — | Validação de referências: validate_project_refs, find_usages (estático, offline) |
| 16 | — | Asset manifest: import_asset_manifest (5 fontes), create_asset_manifest |
| 17 | `45a34f7` | Curadoria de toolset: `--toolsets` com 10 grupos nomeados |
| 18 | `ab017c6` | Marcador `.mcp_gate_failed` integrado com hooks |

### Grupos de Auditoria (5 grupos, 43 bugs corrigidos):

| Grupo | Descrição |
|-------|-----------|
| GRUPO 1 | Validação GDScript no write_file + safe_write R9 deep validation |
| GRUPO 2 | git_commit_checkpoint com gates de compilação + GUT |
| GRUPO 3 | --profile (core/dev/full) + MCP_TOOL_PROFILE + estimate_tool_tokens |
| GRUPO 4 | config.local.json + GODOT_MCP_* env vars |
| GRUPO 5 | allow_paid_generation=False + estimated_cost |

---

## 14. COMO USAR O MCP (para uma IA agêntica)

### 14.1 — Inicialização

```bash
cd mcp-godot-desenvolvimento
.venv\Scripts\python.exe server.py --profile dev
```

### 14.2 — Fluxo típico de desenvolvimento

1. `bootstrap_godot_mcp` — conectar a tudo
2. `create_project` ou `set_active_project` — escolher projeto
3. `godot_class_ref("Node2D")` — consultar API antes de gerar código
4. `create_scene` + `add_node` — construir cena
5. `generate_gdscript` ou `safe_write_gdscript` — escrever scripts
6. `compile_test` — validar compilação
7. `godot_run_project` — iniciar jogo
8. `godot_runtime_info` + `godot_screenshot` — inspecionar runtime
9. `godot_stop_project` — encerrar com save automático
10. `git_commit_checkpoint` — versionar
11. `run_verification_pipeline` — validar integridade do projeto (compile + run + screenshot + GUT)

### 14.3 — Dicas para IAs

- **Sempre consulte `godot_class_ref` antes de gerar código** — evita alucinação de API
- **Use `safe_write_gdscript` em vez de `write_file`** — valida sintaxe automaticamente
- **Use `--profile dev` para economizar tokens** — 80 tools (~8K tokens) em vez de 191 (~19K)
- **`--toolsets` reduz o contexto** — use grupos específicos em vez de `all`
- **Use `run_verification_pipeline` após mudanças grandes** — valida compilação, execução, screenshot e testes em 1 chamada
- **O pipeline NÃO commita** — para no relatório. Use `git_commit_checkpoint` separadamente.
- **Se o projeto não tiver `run/main_scene` definido**, passe `test_scene` obrigatoriamente ou o pipeline retorna `ambiguous`.
- **O bridge runtime só funciona em debug builds** — `OS.is_debug_build()` no GDScript
- **`godot_stop_project` salva a cena antes de matar** — timeout de 2s, não bloqueia o kill
- **`godot_class_ref` NÃO cobre classes custom** — apenas API nativa do Godot
- **O LSP bridge requer projeto aberto no editor Godot** — porta 6005
- **O Addon Bridge (9082) oferece UndoRedo nativo** — prefira sobre escrita direta de arquivo

### 14.4 — Fluxo EARS + Pipeline (Padrão de Fechamento de Pendência)

Comportamento documentado no `AGENTS.md` do Star Colony. Ao fechar qualquer pendência:

1. **Receber** descrição em linguagem natural
2. **Traduzir** para formato EARS (`WHEN/IF/THE/SHALL`) — mostrar tradução e aguardar aprovação
3. **Implementar** após aprovação
4. **Chamar `run_verification_pipeline`** automaticamente (sem o usuário pedir)
5. **Relatório** com: `pipeline_status`, `confianca` (alta/média/baixa + justificativa), `risco` (baixo/médio/alto + justificativa)
6. **Fechar** apenas se pipeline retornou `PASSOU`. Se `FALHOU`, reportar onde parou e não fechar.

---

## 15. ESTRUTURA DE DIRETÓRIOS

```
mcp-godot-desenvolvimento/
├── server.py                    # Ponto de entrada (~7100 linhas)
├── _meta_tool.py                # Factory de Domain Rollups
├── runtime_bridge_client.py     # Cliente TCP para Runtime Bridge
├── validate_gdscript.py         # Validador regex standalone
├── install.py                   # Instalador CLI
├── launch.py                    # Lançador CLI
├── config.json                  # Configuração padrão
├── config.json.example          # Template de config
├── config.local.json            # Config local (gitignored)
├── requirements.txt
├── pyproject.toml
├── README.md
├── ARQUITETURA_MCP.md
├── GUIA_CONEXAO.md
├── GUIA_INSTALACAO.md
├── LEARNINGS.md
├── CHANGELOG.md
├── NEXT_SESSION.md
├── AUDITORIA-PENDENCIAS-RESPOSTAS.md
├── .venv/                       # Ambiente virtual Python
├── classdb_cache/
│   └── extension_api.json       # Cache da API nativa Godot 4.7
├── templates/                   # Templates GDScript
│   ├── player_2d_controller.gd
│   ├── enemy_chase_basic.gd
│   └── ...
├── addons/
│   ├── mcp_addon/               # Addon do editor Godot
│   └── mcp_runtime_bridge/      # Autoload do Runtime Bridge
│       └── runtime_bridge.gd
├── tools/                       # 69 módulos Python
    ├── orchestrator.py          # Saga Engine + Circuit Breaker
    ├── classdb.py               # ClassDB via extension_api.json
    ├── config_loader.py         # Cascata config.local > config > env
    ├── scene_ops.py             # Operações de cena
    ├── script_ops.py            # Templates + validação
    ├── safety.py                # Backup + undo + git checkpoint
    ├── editor_bridge.py         # TCP 9080
    ├── addon_bridge.py          # WebSocket 9082
    ├── game_bridge.py           # TCP 9081
    ├── lsp_ops.py               # LSP 6005
    ├── debugger_ops.py          # DAP 6006
    ├── runtime_ops.py           # compile/run/stop/restart
    ├── asset_ops.py             # Import texturas/modelos
    ├── art_ops.py               # DALL-E + procedural
    ├── flux_ops.py              # FLUX.2 API
    ├── placeholder_ops.py       # Sprites/atlas/gradientes/SFX
    ├── juice_ops.py             # Game feel
    ├── balance_ops.py           # Balanceamento
    ├── behavior_ops.py          # Behavior Trees
    ├── shader_ops.py            # Shaders NL→GLSL
    ├── deploy_ops.py            # itch.io
    ├── marketplace_ops.py       # Asset stores
    ├── playtest_ops.py          # Freeze/step/watch
    ├── refs_ops.py              # Validação de referências + find_usages
    ├── test_ops.py              # Testes roteirizados (smoke, regression)
    ├── asset_manifest.py        # Import/export de asset manifests
    ├── bootstrap_ops.py         # Bootstrap multi-passo
    ├── devsolo_ops.py           # Câmera/save/diálogo/inventário
    ├── threed_gen.py            # 3D placeholder + Hyper3D
    ├── tts_ops.py               # TTS offline
    ├── gut_ops.py               # GUT test runner
    ├── rate_limiter.py          # Rate limiting
    ├── cache_utils.py           # Cache de resultados
    ├── validate_write.py        # Validação de escrita
    ├── verification_ops.py      # Pipeline de verificação (compile→run→screenshot→GUT)
    ├── gdscript_sandbox.py      # Sandbox 80+ padrões
    ├── friendly_errors.py       # Erros PT-BR
    ├── rollups.py               # Handlers unificados (Fase 2A)
    ├── pipeline_ops.py          # Pipeline Executor legado
    ├── batch_ops.py             # Operações em lote
    ├── project_ops.py           # Projeto (create/settings)
    ├── project_state.py         # Snapshot em memória
    ├── project_map.py           # Mapa JSON/HTML
    ├── file_ops.py              # Arquivos
    ├── file_watcher.py          # File watcher
    ├── export_ops.py            # Exportação
    ├── physics_ops.py           # Física
    ├── security_ops.py          # Segurança/auditoria
    ├── safety_policy.py         # Allowlist/blocklist
    ├── networking_ops.py        # Multiplayer/HTTP
    ├── recording_ops.py         # Gravação
    ├── vibe_ops.py              # Vibe Coding Mode
    ├── vscode_config.py         # Config VS Code
    ├── workflow_ops.py          # Snapshot/handoff
    ├── dynamic_groups.py        # Grupos dinâmicos
    ├── decision_engine.py       # Decisão arte/áudio
    ├── world_gen.py             # Terreno/dungeon procedural
    ├── live_stream.py           # Live streaming
    ├── asset_download.py        # Download CC0
    ├── art_postprocess.py       # Remove bg/otimiza/sprite sheet
    ├── analyze_ops.py           # Análise estrutural
    ├── infra_ops.py             # health_check/self_test
    ├── perf_ops.py              # Profiler
    ├── playmode_ops.py          # Play mode
    ├── runtime_rich.py          # Runtime rich
    ├── runtime_ui.py            # Runtime UI
    └── editor_config.py         # Config editor
```

---

## 16. LIMITAÇÕES CONHECIDAS

| Limitação | Detalhe |
|-----------|---------|
| `godot_class_ref` não cobre classes custom | Apenas API nativa do extension_api.json |
| `--headless --script` não produz output no Windows Godot 4.7 | stdout/stderr/FileAccess/exit code todos falham |
| `godot_stop_project` usa `taskkill /F` no Windows | TerminateProcess, sem graceful shutdown |
| Bridge runtime só ativo em debug builds | `OS.is_debug_build()` no GDScript |
| Save-before-kill timeout de 2s | Se bridge não responder em 2s, cena não é salva |
| Rollups depreciaram ~80 ferramentas | Listadas mas redirecionadas para handlers unificados |
| `--write-movie` com `--headless` crasha (SIGSEGV) | Renderer DUMMY não suporta texturas. Solução: `--write-movie` sem `--headless` + SW_HIDE no Windows |
| Screenshot via `--write-movie` requer ~500ms (30 frames) para UI renderizar | 10 frames (167ms) pode capturar tela sem elementos visíveis |
| `InputEventKey` não simulável em headless | Testes de input (ex: tecla U de debug) só validáveis com jogo rodando interativamente |
| Headless run sem `--quit-after` = timeout | Jogos com `_process()` em loop infinito nunca saem. Solução: `--quit-after N` |

---

*Documento gerado em 12/07/2026. 191 ferramentas, 69 módulos, 18 patches implementados (1-18), 5 grupos de auditoria, tool run_verification_pipeline (item 1 do plano de evolução).*
