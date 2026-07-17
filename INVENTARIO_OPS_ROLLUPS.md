# Inventário de Ops por Rollup

> **Gerado em:** 17/07/2026  
> **Fonte:** Extraído do dispatch real em `tools/rollups.py` — arquivo `_ROLLUP_BUILDERS` (linhas 722–758) + funções `_build_*`  
> **Total de rollups:** 28  
> **Total de ops:** 116  

---

## Sumário

| Rollup | Qtd Ops | Arquivo Handler |
|--------|---------|-----------------|
| scene_manage | 3 | tools/scene_ops.py |
| node_manage | 7 | tools/scene_ops.py |
| script_manage | 6 | tools/script_ops.py |
| file_manage | 3 | tools/file_ops.py |
| project_manage | 5 | tools/project_ops.py |
| asset_manage | 8 | tools/asset_ops.py + tools/placeholder_ops.py |
| physics_manage | 4 | tools/physics_ops.py |
| anim_manage | 4 | tools/devsolo_ops.py |
| ui_manage | 7 | tools/devsolo_ops.py |
| tilemap_manage | 4 | tools/devsolo_ops.py |
| audio_manage | 2 | tools/devsolo_ops.py |
| export_manage | 3 | tools/export_ops.py |
| d3_manage | 4 | tools/devsolo_ops.py |
| debug_manage | 3 | tools/devsolo_ops.py |
| config_manage | 2 | tools/project_ops.py |
| gamestate_manage | 4 | tools/devsolo_ops.py |
| runtime_manage | 6 | tools/runtime_ops.py |
| camera_manage | 3 | tools/devsolo_ops.py |
| navigation_manage | 3 | tools/devsolo_ops.py |
| dialogue_manage | 3 | tools/devsolo_ops.py |
| inventory_manage | 3 | tools/devsolo_ops.py |
| vfx_manage | 4 | tools/vfx_ops.py + tools/devsolo_ops.py |
| shader_manage | 5 | tools/shader_editor_ops.py + tools/devsolo_ops.py |
| raycast_manage | 2 | tools/devsolo_ops.py |
| test_manage | 2 | tools/playmode_ops.py + tools/stress_test_ops.py |
| analysis_manage | 7 | tools/analyze_ops.py |
| safety_manage | 5 | tools/safety.py |
| vision_manage | 3 | tools/runtime_ops.py + tools/scene_ops.py |

---

## Detalhamento por Rollup

### 1. scene_manage
**Descrição:** Gerencia cenas Godot (.tscn) com operações de criação, carregamento e instanciação.
**Arquivo:** `tools/scene_ops.py`
| op | Handler | Parâmetros |
|----|---------|------------|
| `create` | `create_scene` | root_type, root_name, save_path |
| `load_tree` | `load_scene_tree` | scene_path |
| `instance` | `instance_scene_as_child` | parent_path, scene_path |

### 2. node_manage
**Descrição:** Gerencia nós dentro de cenas Godot: adicionar, remover, ler/definir propriedades, re-parentar, conectar sinais.
**Arquivo:** `tools/scene_ops.py`
| op | Handler | Parâmetros |
|----|---------|------------|
| `create` | `add_node` | parent_path, node_type, node_name, properties |
| `delete` | `delete_node` | node_path |
| `set_property` | `set_node_property` | node_path, property_name, value |
| `get_property` | `get_node_property` | node_path, property_name |
| `reparent` | `reparent_node` | node_path, new_parent_path, keep_global_transform |
| `connect_signal` | `connect_signal` | node_path, signal_name, target_path, method_name |
| `list_signals` | `list_signals_for_node` | node_path |

### 3. script_manage
**Descrição:** Gerencia scripts GDScript: gerar código template, anexar/desanexar, validar sintaxe, adicionar variáveis e sinais.
**Arquivo:** `tools/script_ops.py`
| op | Handler | Parâmetros |
|----|---------|------------|
| `generate` | `generate_gdscript` | template_name, node_path, class_name |
| `attach` | `attach_script` | node_path, script_path |
| `detach` | `detach_script` | node_path |
| `validate` | `validate_gdscript_syntax` | script_path |
| `add_var` | `add_script_variable` | script_path, var_name, var_type, default_value |
| `add_signal` | `add_script_signal` | script_path, signal_name, signal_params |

### 4. file_manage
**Descrição:** Gerencia arquivos do projeto Godot: deletar, mover/renomear e inspecionar.
**Arquivo:** `tools/file_ops.py`
| op | Handler | Parâmetros |
|----|---------|------------|
| `delete` | `delete_file` | path |
| `move` | `move_file` | source, destination |
| `inspect` | `inspect_project` | category, path |

### 5. project_manage
**Descrição:** Gerencia o projeto Godot ativo: criar, definir ativo, configurar settings, cena principal, input actions, autoloads.
**Arquivo:** `tools/project_ops.py`
| op | Handler | Parâmetros |
|----|---------|------------|
| `create` | `create_project` | project_name, project_path |
| `set_active` | `set_active_project` | project_path |
| `get_settings` | `get_project_settings` | |
| `set_setting` | `set_project_setting` | key, value |
| `set_main_scene` | `set_main_scene` | scene_path |

### 6. asset_manage
**Descrição:** Gerencia assets: importar texturas, spritesheets, áudio; gerar placeholders; sugerir paletas.
**Arquivo:** `tools/asset_ops.py` + `tools/placeholder_ops.py`
| op | Handler | Parâmetros |
|----|---------|------------|
| `import_texture` | `import_texture` | source_path, dest_path |
| `import_spritesheet` | `import_sprite_sheet` | source_path, dest_path, h_frames, v_frames |
| `import_audio` | `import_audio` | source_path, dest_path |
| `placeholder_sprite` | `generate_placeholder_sprite` | width, height, color, shape, save_path |
| `placeholder_atlas` | `generate_placeholder_texture_atlas` | tile_size, cols, rows, colors, save_path |
| `bg_gradient` | `generate_background_gradient` | width, height, top_color, bottom_color, save_path |
| `tileset_colors` | `generate_tileset_from_colors` | tile_size, cols, rows, colors, save_path |
| `palette` | `suggest_color_palette` | base_color, style |

### 7. physics_manage
**Descrição:** Gerencia física 2D/3D: colisões, camadas, materiais e juntas.
**Arquivo:** `tools/physics_ops.py`
| op | Handler | Parâmetros |
|----|---------|------------|
| `add_collision` | `add_collision_shape` | node_path, shape_type, extents |
| `set_layers` | `set_collision_layer_mask` | node_path, layer, mask |
| `set_material` | `set_physics_material` | node_path, friction, bounce |
| `create_joint` | `create_joint_2d` | joint_type, node_a_path, node_b_path, anchor |

### 8. anim_manage
**Descrição:** Gerencia animações: AnimationPlayer, clipes, tweens e encadeamento.
**Arquivo:** `tools/devsolo_ops.py`
| op | Handler | Parâmetros |
|----|---------|------------|
| `create_player` | `create_animation_player` | node_path, anim_name |
| `create_clip` | `create_animation` | anim_player_path, clip_name, length |
| `create_tween` | `create_tween_animation` | target_path, property, from, to, duration, ease_type |
| `chain_tweens` | `chain_tweens` | tweens_list |

### 9. ui_manage
**Descrição:** Gerencia interfaces: criar UI, adicionar controles, menus, HUD, loading screen.
**Arquivo:** `tools/devsolo_ops.py`
| op | Handler | Parâmetros |
|----|---------|------------|
| `create_root` | `create_ui_scene` | root_type, save_path |
| `add_control` | `add_control_node` | parent_path, control_type, name, layout |
| `main_menu` | `create_main_menu` | save_path, title, buttons |
| `hud` | `create_hud_template` | save_path, health_bar, score_label |
| `pause_menu` | `create_pause_menu` | save_path |
| `health_bar` | `create_health_bar` | parent_path, name, max_health, width, height |
| `loading_screen` | `create_loading_screen` | save_path, bg_color, show_progress |

### 10. tilemap_manage
**Descrição:** Gerencia tilemaps: criar tileset, camadas, pintar células e gerar por noise.
**Arquivo:** `tools/devsolo_ops.py`
| op | Handler | Parâmetros |
|----|---------|------------|
| `create_tileset` | `create_tileset` | tile_size, tiles_path, save_path |
| `create_layer` | `create_tilemap_layer` | tileset_path, layer_name, parent_path |
| `paint_cell` | `paint_tilemap_cell` | layer_path, coords, source_id, atlas_coords |
| `from_noise` | `generate_tilemap_from_noise` | layer_path, noise_params, tile_mapping |

### 11. audio_manage
**Descrição:** Gerencia áudio: configurar buses e adicionar efeitos.
**Arquivo:** `tools/devsolo_ops.py`
| op | Handler | Parâmetros |
|----|---------|------------|
| `config_bus` | `configure_audio_bus` | bus_name, volume_db, mute |
| `add_effect` | `add_audio_effect` | bus_name, effect_type |

### 12. export_manage
**Descrição:** Gerencia exportação: listar presets, validar templates, build.
**Arquivo:** `tools/export_ops.py`
| op | Handler | Parâmetros |
|----|---------|------------|
| `list_presets` | `list_export_presets` | |
| `validate_templates` | `validate_export_templates_installed` | |
| `build` | `build_export` | preset_name, output_path |

### 13. d3_manage
**Descrição:** Gerencia 3D: luzes, CSG, materiais e partículas.
**Arquivo:** `tools/devsolo_ops.py`
| op | Handler | Parâmetros |
|----|---------|------------|
| `create_light` | `create_light_3d` | light_type, parent_path, name, color, energy |
| `create_csg` | `create_csg_shape` | shape_type, parent_path, name, material |
| `config_material` | `configure_standard_material_3d` | mesh_path, albedo_color, metallic, roughness |
| `create_particles` | `create_particles_3d` | parent_path, name, material |

### 14. debug_manage
**Descrição:** Gerencia debug: performance, visualização de colisões e navegação.
**Arquivo:** `tools/devsolo_ops.py`
| op | Handler | Parâmetros |
|----|---------|------------|
| `perf_stats` | `get_performance_stats` | |
| `collision_debug` | `enable_debug_collisions` | enabled |
| `nav_debug` | `enable_debug_navigation` | enabled |

### 15. config_manage
**Descrição:** Gerencia configurações: input actions e autoloads.
**Arquivo:** `tools/project_ops.py`
| op | Handler | Parâmetros |
|----|---------|------------|
| `input_action` | `configure_input_action` | action_name, key, deadzone |
| `autoload` | `configure_autoload` | script_path, autoload_name, singleton |

### 16. gamestate_manage
**Descrição:** Gerencia estado do jogo: save system, state machine e transições.
**Arquivo:** `tools/devsolo_ops.py`
| op | Handler | Parâmetros |
|----|---------|------------|
| `create_save` | `create_save_system` | save_path, auto_load |
| `define_save` | `define_save_data` | slot, data_structure |
| `create_fsm` | `create_state_machine` | name, initial_state |
| `add_transition` | `add_state_transition` | fsm_path, from_state, to_state, event |

### 17. runtime_manage
**Descrição:** Gerencia execução do Godot: compilar, rodar, parar, reiniciar, abrir/fechar editor.
**Arquivo:** `tools/runtime_ops.py`
| op | Handler | Parâmetros |
|----|---------|------------|
| `compile` | `compile_test` | |
| `run` | `run_game` | scene_path, flags |
| `stop` | `stop_game` | |
| `restart` | `smart_restart` | |
| `launch_editor` | `launch_editor` | scene_path |
| `close_editor` | `close_editor` | |

### 18. camera_manage
**Descrição:** Gerencia câmera 2D: setup, follow e shake.
**Arquivo:** `tools/devsolo_ops.py`
| op | Handler | Parâmetros |
|----|---------|------------|
| `setup_2d` | `setup_camera_2d` | parent_path, name, zoom, limits |
| `follow` | `setup_camera_follow` | camera_path, target_path, smoothing |
| `shake` | `setup_camera_shake` | camera_path, intensity, duration |

### 19. navigation_manage
**Descrição:** Gerencia navegação 2D: regiões, agentes e bake.
**Arquivo:** `tools/devsolo_ops.py`
| op | Handler | Parâmetros |
|----|---------|------------|
| `create_region` | `create_navigation_region_2d` | parent_path, name, polygon |
| `create_agent` | `create_navigation_agent_2d` | parent_path, name, radius |
| `bake` | `bake_navigation_polygon` | region_path |

### 20. dialogue_manage
**Descrição:** Gerencia sistema de diálogo: criar, adicionar nós e UI.
**Arquivo:** `tools/devsolo_ops.py`
| op | Handler | Parâmetros |
|----|---------|------------|
| `create_system` | `create_dialogue_system` | save_path |
| `add_node` | `add_dialogue_node` | dialogue_system_path, node_id, text, choices |
| `create_ui` | `create_dialogue_ui` | parent_path, dialogue_system_path |

### 21. inventory_manage
**Descrição:** Gerencia sistema de inventário: criar, definir itens e UI.
**Arquivo:** `tools/devsolo_ops.py`
| op | Handler | Parâmetros |
|----|---------|------------|
| `create_system` | `create_inventory_system` | save_path, max_slots |
| `define_item` | `define_inventory_item` | item_id, name, icon, stackable |
| `create_ui` | `create_inventory_ui` | parent_path, inventory_system_path |

### 22. vfx_manage
**Descrição:** Gerencia efeitos visuais: criar partículas 2D, configurar, screen flash e ambiente.
**Arquivo:** `tools/vfx_ops.py` + `tools/devsolo_ops.py`
| op | Handler | Parâmetros |
|----|---------|------------|
| `create_particles` | `create_particles_2d` | parent_path, name, texture, amount |
| `config_particles` | `configure_particles_2d` | particle_path, lifetime, speed, emission_shape |
| `screen_flash` | `setup_screen_flash` | color, duration, parent_path |
| `world_env` | `setup_world_environment` | bg_color, ambient_light, tonemap |

### 23. shader_manage
**Descrição:** Gerencia shaders: gerar, ler, editar e aplicar shaders 2D.
**Arquivo:** `tools/shader_editor_ops.py` + `tools/devsolo_ops.py`
| op | Handler | Parâmetros |
|----|---------|------------|
| `generate` | `generate_shader_2d` | shader_type, save_path |
| `apply` | `apply_shader_to_node` | node_path, shader_path |
| `read` | `read_shader` | shader_path |
| `edit` | `edit_shader` | shader_path, content |
| `get_params` | `get_shader_params` | shader_path |

### 24. raycast_manage
**Descrição:** Gerencia raycasts 2D: adicionar RayCast2D e ShapeCast2D.
**Arquivo:** `tools/devsolo_ops.py`
| op | Handler | Parâmetros |
|----|---------|------------|
| `add_raycast` | `add_raycast_2d` | parent_path, name, target_position, collide_with_areas |
| `add_shapecast` | `add_shapecast_2d` | parent_path, name, shape_type, extents, collision_mask |

### 25. test_manage
**Descrição:** Gerencia testes automatizados: assert_node_exists e stress test.
**Arquivo:** `tools/playmode_ops.py` + `tools/stress_test_ops.py`
| op | Handler | Parâmetros |
|----|---------|------------|
| `assert_node` | `assert_node_exists` | scene_path, node_path |
| `stress_test` | `run_stress_test` | scene_path, iterations, spawn_interval |

### 26. analysis_manage
**Descrição:** Analisa o projeto: estrutura, próximos passos, referências, design, escopo e busca.
**Arquivo:** `tools/analyze_ops.py`
| op | Handler | Parâmetros |
|----|---------|------------|
| `structure` | `analyze_game_structure` | |
| `next_steps` | `suggest_next_steps` | |
| `missing_refs` | `find_missing_references` | |
| `validate_design` | `validate_game_design` | gdd |
| `estimate_scope` | `estimate_game_scope` | gdd |
| `search` | `search_codebase` | query, path |
| `history` | `get_project_history` | |

### 27. safety_manage
**Descrição:** Gerencia segurança: backups, restore, checkpoint git e undo/redo.
**Arquivo:** `tools/safety.py`
| op | Handler | Parâmetros |
|----|---------|------------|
| `list_backups` | `list_backups` | |
| `restore` | `restore` | identifier |
| `checkpoint` | `git_checkpoint` | message |
| `undo` | `undo_last_action` | |
| `undo_history` | `get_undo_history` | |

### 28. vision_manage
**Descrição:** Gerencia visão computacional: comparar screenshots, detectar tela vazia/offscreen.
**Arquivo:** `tools/runtime_ops.py` + `tools/scene_ops.py`
| op | Handler | Parâmetros |
|----|---------|------------|
| `compare` | `compare_screenshots` | baseline_path, current_path, threshold |
| `detect_empty` | `detect_empty_screen` | screenshot_path |
| `detect_offscreen` | `detect_offscreen_elements` | scene_path |

---

## Estatísticas

| Métrica | Valor |
|---------|-------|
| Total de rollups | 28 |
| Total de ops | 116 |
| Média de ops/rollup | 4.1 |
| Rollup com mais ops | `asset_manage` (8 ops) |
| Rollups com menos ops | `audio_manage`, `config_manage`, `raycast_manage` (2 ops cada) |
| Handler mais reutilizado | `tools/devsolo_ops.py` (14 rollups) |