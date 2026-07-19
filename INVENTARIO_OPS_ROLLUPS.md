# Inventário de Ops por Rollup — CORRIGIDO (assinaturas reais)

> **Gerado em:** 17/07/2026  
> **Método:** Extração programática via `inspect.signature()` do Python  
> **Total de rollups:** 32  
> **Total de ops:** 126

---

## Sumário

| Rollup | Qtd Ops | Arquivos Handler |
|--------|---------|------------------|
| scene_manage | 3 | scene_ops.py |
| node_manage | 7 | scene_ops.py |
| script_manage | 6 | script_ops.py |
| file_manage | 3 | file_ops.py |
| project_manage | 5 | project_ops.py |
| asset_manage | 11 | asset_ops.py + placeholder_ops.py + art_ops.py |
| physics_manage | 4 | physics_ops.py |
| anim_manage | 4 | devsolo_ops.py |
| ui_manage | 7 | devsolo_ops.py |
| tilemap_manage | 4 | devsolo_ops.py |
| audio_manage | 6 | devsolo_ops.py |
| export_manage | 3 | export_ops.py |
| d3_manage | 4 | devsolo_ops.py |
| debug_manage | 3 | devsolo_ops.py |
| config_manage | 2 | project_ops.py |
| gamestate_manage | 4 | devsolo_ops.py |
| runtime_manage | 6 | runtime_ops.py |
| camera_manage | 3 | devsolo_ops.py |
| navigation_manage | 3 | devsolo_ops.py |
| dialogue_manage | 3 | devsolo_ops.py |
| inventory_manage | 3 | devsolo_ops.py |
| vfx_manage | 4 | vfx_ops.py + devsolo_ops.py |
| shader_manage | 5 | shader_editor_ops.py + devsolo_ops.py |
| raycast_manage | 2 | devsolo_ops.py |
| test_manage | 2 | playmode_ops.py + stress_test_ops.py |
| analysis_manage | 7 | analyze_ops.py |
| safety_manage | 5 | safety.py |
| vision_manage | 3 | runtime_ops.py + scene_ops.py |
| playtest_manage | 3 | playtest_ops.py |
| localization_manage | 3 | localization_ops.py |

---

## Detalhamento por Rollup

### scene_manage
**Descrição:** Gerencia cenas Godot (.tscn): criar, carregar, instanciar.
**Arquivos fonte:** tools.scene_ops

| op | Handler | Assinatura REAL | Parâmetros |
|----|---------|----------------|------------|
| `create` | `create_scene` | `(name: str, root_type: str, path: str) -> dict` | name, root_type, path |
| `load_tree` | `load_scene_tree` | `(scene_path: str | None = None, max_depth: int | None = None) -> dict` | scene_path=..., max_depth=... |
| `instance` | `instance_scene_as_child` | `(scene_path: str | None = None, parent_node_path: str = '.', instanced_scene_path: str = '', instance_name: str | None = None) -> dict` | scene_path=..., parent_node_path=..., instanced_scene_path=..., instance_name=... |

### node_manage
**Descrição:** Gerencia nós: criar, deletar, propriedades, reparent, sinais.
**Arquivos fonte:** tools.scene_ops

| op | Handler | Assinatura REAL | Parâmetros |
|----|---------|----------------|------------|
| `create` | `add_node` | `(scene_path: str | None = None, parent_node_path: str = '.', node_name: str = '', node_type: str = 'Node') -> dict` | scene_path=..., parent_node_path=..., node_name=..., node_type=... |
| `delete` | `delete_node` | `(scene_path: str | None = None, node_path: str = '') -> dict` | scene_path=..., node_path=... |
| `set_property` | `set_node_property` | `(scene_path: str | None = None, node_path: str = '', property_name: str = '', value: Any = None) -> dict` | scene_path=..., node_path=..., property_name=..., value=... |
| `get_property` | `get_node_property` | `(scene_path: str | None = None, node_path: str = '', property_name: str = '', property: str | None = None) -> dict` | scene_path=..., node_path=..., property_name=..., property=... |
| `reparent` | `reparent_node` | `(scene_path: str | None = None, node_path: str = '', new_parent_path: str = '.') -> dict` | scene_path=..., node_path=..., new_parent_path=... |
| `connect_signal` | `connect_signal` | `(scene_path: str | None = None, from_node_path: str = '', signal_name: str = '', to_node_path: str = '', method_name: str = '') -> dict` | scene_path=..., from_node_path=..., signal_name=..., to_node_path=..., method_name=... |
| `list_signals` | `list_signals_for_node` | `(scene_path: str | None = None, node_path: str | None = None, node_type: str | None = None) -> dict` | scene_path=..., node_path=..., node_type=... |

### script_manage
**Descrição:** Gerencia scripts GDScript: gerar, anexar, validar, variáveis, sinais.
**Arquivos fonte:** tools.script_ops

| op | Handler | Assinatura REAL | Parâmetros |
|----|---------|----------------|------------|
| `generate` | `generate_gdscript` | `(template: str, variables: dict, save_path: str) -> dict` | template, variables, save_path |
| `attach` | `attach_script` | `(scene_path: str, node_path: str, script_path: str) -> dict` | scene_path, node_path, script_path |
| `detach` | `detach_script` | `(scene_path: str, node_path: str) -> dict` | scene_path, node_path |
| `validate` | `validate_gdscript_syntax` | `(script_path: str) -> dict` | script_path |
| `add_var` | `add_script_variable` | `(script_path: str, var_name: str, var_type: str = 'Variant', default_value: str | None = None, export: bool = False) -> dict` | script_path, var_name, var_type=..., default_value=..., export=... |
| `add_signal` | `add_script_signal` | `(script_path: str, signal_name: str, args: list[str] | None = None) -> dict` | script_path, signal_name, args=... |

### file_manage
**Descrição:** Gerencia arquivos: deletar, mover, inspecionar.
**Arquivos fonte:** tools.file_ops

| op | Handler | Assinatura REAL | Parâmetros |
|----|---------|----------------|------------|
| `delete` | `delete_file` | `(path: str) -> dict` | path |
| `move` | `move_file` | `(from_path: str, to_path: str) -> dict` | from_path, to_path |
| `inspect` | `inspect_project` | `(filter_type: str = 'all') -> dict` | filter_type=... |

### project_manage
**Descrição:** Gerencia projeto: criar, ativo, settings, main scene.
**Arquivos fonte:** tools.project_ops

| op | Handler | Assinatura REAL | Parâmetros |
|----|---------|----------------|------------|
| `create` | `create_project` | `(name: str, path: str, renderer: str = 'forward_plus') -> dict` | name, path, renderer=... |
| `set_active` | `set_active_project` | `(project_path: str) -> dict` | project_path |
| `get_settings` | `get_project_settings` | `(section: str | None = None) -> dict` | section=... |
| `set_setting` | `set_project_setting` | `(section: str, key: str, value) -> dict` | section, key, value |
| `set_main_scene` | `set_main_scene` | `(scene_path: str) -> dict` | scene_path |

### asset_manage
**Descrição:** Gerencia assets: importar texturas/sprites/áudio, placeholders, animações de sprite, paletas e validação game-ready.
**Arquivos fonte:** tools.asset_ops, tools.placeholder_ops, tools.art_ops

| op | Handler | Assinatura REAL | Parâmetros |
|----|---------|----------------|------------|
| `import_texture` | `import_texture` | `(source_path: str, target_res_path: str) -> dict` | source_path, target_res_path |
| `import_spritesheet` | `import_sprite_sheet` | `(source_path: str, target_res_path: str, frame_width: int, frame_height: int, target_scene_path: str, target_node_path: str, animations: list[dict]) -> dict` | source_path, target_res_path, frame_width, frame_height, target_scene_path, target_node_path, animations |
| `import_audio` | `import_audio` | `(source_path: str, target_res_path: str) -> dict` | source_path, target_res_path |
| `placeholder_sprite` | `generate_placeholder_sprite` | `(name: str, width: int = 64, height: int = 64, color: str = '#3498db', shape: str = 'rectangle', save_path: str | None = None) -> dict` | name, width=..., height=..., color=..., shape=..., save_path=... |
| `placeholder_atlas` | `generate_placeholder_texture_atlas` | `(name: str, frame_width: int = 64, frame_height: int = 64, columns: int = 4, rows: int = 1, color: str = '#e74c3c', shape: str = 'rectangle', variation: str = 'position', save_path: str | None = None) -> dict` | name, frame_width=..., frame_height=..., columns=..., rows=..., color=..., shape=..., variation=..., save_path=... |
| `bg_gradient` | `generate_background_gradient` | `(name: str, width: int = 1280, height: int = 720, color_top: str = '#1a1a2e', color_bottom: str = '#16213e', direction: str = 'vertical', save_path: str | None = None) -> dict` | name, width=..., height=..., color_top=..., color_bottom=..., direction=..., save_path=... |
| `tileset_colors` | `generate_tileset_from_colors` | `(palette_name: str, colors: list[str], tile_width: int = 16, tile_height: int = 16, save_texture_path: str | None = None, save_tileset_path: str | None = None) -> dict` | palette_name, colors, tile_width=..., tile_height=..., save_texture_path=..., save_tileset_path=... |
| `palette` | `suggest_color_palette` | `(genre: str) -> dict` | genre |
| `validate_game_ready` | `validate_asset_game_ready` | `(asset_path: str, asset_type: str = 'texture') -> dict` | asset_path, asset_type=... |
| `sprite_animation` | `generate_sprite_animation` | `(category: str = 'character', anim_type: str = 'idle', num_frames: int = 4, scene_path: str \| None = None, parent_node_path: str = '.', node_name: str = '', fps: float = 8.0, loop: bool = True, frame_width: int = 64, frame_height: int = 64, output_dir: str = 'assets/animations', style_desc: str = '') -> dict` | category=..., anim_type=..., num_frames=..., scene_path=..., parent_node_path=..., node_name=..., fps=..., loop=..., frame_width=..., frame_height=..., output_dir=..., style_desc=... |
| `license_audit` | `audit_asset_license` | `(asset_path: str, license_str: str = '', project_license: str = 'commercial') -> dict` | asset_path, license_str="CC0"\|"MIT"\|"CC-BY"\|..., project_license="commercial"\|"open_source"\|"personal" |

### physics_manage
**Descrição:** Gerencia física: colisões, camadas, materiais, juntas.
**Arquivos fonte:** tools.physics_ops

| op | Handler | Assinatura REAL | Parâmetros |
|----|---------|----------------|------------|
| `add_collision` | `add_collision_shape` | `(scene_path: str, parent_node_path: str, shape_type: str, dimensions: dict | str) -> dict` | scene_path, parent_node_path, shape_type, dimensions |
| `set_layers` | `set_collision_layer_mask` | `(scene_path: str, node_path: str, layer_bits: list[int], mask_bits: list[int]) -> dict` | scene_path, node_path, layer_bits, mask_bits |
| `set_material` | `set_physics_material` | `(scene_path: str, node_path: str, bounce: float | None = None, friction: float | None = None, absorb: float | None = None, rough: bool | None = None) -> dict` | scene_path, node_path, bounce=..., friction=..., absorb=..., rough=... |
| `create_joint` | `create_joint_2d` | `(scene_path: str, node_a_path: str, node_b_path: str, joint_type: str = 'pin', softness: float = 0.0, bias: float = 0.0) -> dict` | scene_path, node_a_path, node_b_path, joint_type=..., softness=..., bias=... |

### anim_manage
**Descrição:** Gerencia animações: AnimationPlayer, clipes, tweens.
**Arquivos fonte:** tools.devsolo_ops, tools.scene_ops

| op | Handler | Assinatura REAL | Parâmetros |
|----|---------|----------------|------------|
| `create_player` | `create_animation_player` | `(scene_path: str, parent_node_path: str, player_name: str = 'AnimationPlayer') -> dict` | scene_path, parent_node_path, player_name=... |
| `create_clip` | `create_animation` | `(scene_path: str, anim_player_path: str, anim_name: str, track_path: str, track_type: str, keyframes: list[dict], fps: float = 10.0) -> dict` | scene_path, anim_player_path, anim_name, track_path, track_type, keyframes, fps=... |
| `create_tween` | `create_tween_animation` | `(scene_path: str, node_path: str, property_name: str, final_value: Any, duration: float = 0.5, easing: str = 'out_quad', transition: str = 'ease_out', loops: int = 0, auto_play: bool = True) -> dict` | scene_path, node_path, property_name, final_value, duration=..., easing=..., transition=..., loops=..., auto_play=... |
| `chain_tweens` | `chain_tweens` | `(scene_path: str, node_path: str, steps: list[dict]) -> dict` | scene_path, node_path, steps |

### ui_manage
**Descrição:** Gerencia UI: cenas, controles, menus, HUD, pause, loading.
**Arquivos fonte:** tools.devsolo_ops, tools.scene_ops

| op | Handler | Assinatura REAL | Parâmetros |
|----|---------|----------------|------------|
| `create_root` | `create_ui_scene` | `(name: str, path: str) -> dict` | name, path |
| `add_control` | `add_control_node` | `(scene_path: str, parent_node_path: str, node_name: str, node_type: str, properties: dict | None = None) -> dict` | scene_path, parent_node_path, node_name, node_type, properties=... |
| `main_menu` | `create_main_menu` | `(scene_name: str, game_title: str, title_font_size: int = 64, buttons: list[str] | None = None, background_color: str = '#1a1a2e', style: str = 'modern') -> dict` | scene_name, game_title, title_font_size=..., buttons=..., background_color=..., style=... |
| `hud` | `create_hud_template` | `(scene_name: str = 'hud', elements: list[str] | None = None, position: str = 'top_left') -> dict` | scene_name=..., elements=..., position=... |
| `pause_menu` | `create_pause_menu` | `(scene_name: str = 'pause_menu', overlay_alpha: float = 0.7) -> dict` | scene_name=..., overlay_alpha=... |
| `health_bar` | `create_health_bar` | `(scene_path: str, parent_node_path: str = '.', max_health: float = 100.0, bar_name: str = 'HealthBar', bar_width: int = 250, bar_height: int = 25, fill_color: str = '#2ecc71', bg_color: str = '#333333', show_text: bool = True) -> dict` | scene_path, parent_node_path=..., max_health=..., bar_name=..., bar_width=..., bar_height=..., fill_color=..., bg_color=..., show_text=... |
| `loading_screen` | `create_loading_screen` | `(scene_name: str = 'loading_screen', tips: list[str] | None = None, min_load_time: float = 1.0, background_color: str = '#1a1a2e') -> dict` | scene_name=..., tips=..., min_load_time=..., background_color=... |

### tilemap_manage
**Descrição:** Gerencia tilemaps: tileset, camadas, pintar, noise.
**Arquivos fonte:** tools.devsolo_ops, tools.scene_ops

| op | Handler | Assinatura REAL | Parâmetros |
|----|---------|----------------|------------|
| `create_tileset` | `create_tileset` | `(tileset_name: str, save_path: str, tile_width: int = 16, tile_height: int = 16) -> dict` | tileset_name, save_path, tile_width=..., tile_height=... |
| `create_layer` | `create_tilemap_layer` | `(scene_path: str, parent_node_path: str, layer_name: str, tileset_path: str) -> dict` | scene_path, parent_node_path, layer_name, tileset_path |
| `paint_cell` | `paint_tilemap_cell` | `(scene_path: str, layer_node_path: str, cell_x: int, cell_y: int, source_id: int = 0, atlas_coords_x: int = 0, atlas_coords_y: int = 0) -> dict` | scene_path, layer_node_path, cell_x, cell_y, source_id=..., atlas_coords_x=..., atlas_coords_y=... |
| `from_noise` | `generate_tilemap_from_noise` | `(scene_path: str, tilemap_layer_path: str, tile_size: int = 32, width: int = 40, height: int = 30, seed: int = 0, threshold: float = 0.5, tile_ground: int = 0, tile_wall: int = 1) -> dict` | scene_path, tilemap_layer_path, tile_size=..., width=..., height=..., seed=..., threshold=..., tile_ground=..., tile_wall=... |

### audio_manage
**Descrição:** Gerencia áudio: buses, roteamento, efeitos, áudio espacial 3D, varredura de SFX por cena e geração de SFX procedural em lote.
**Arquivos fonte:** tools.devsolo_ops

| op | Handler | Assinatura REAL | Parâmetros |
|----|---------|----------------|------------|
| `config_bus` | `configure_audio_bus` | `(bus_name: str, volume_db: float = 0.0, mute: bool = False, solo: bool = False) -> dict` | bus_name, volume_db=..., mute=..., solo=... |
| `add_effect` | `add_audio_effect` | `(bus_name: str, effect_type: str = 'reverb', **kwargs) -> dict` | bus_name, effect_type="reverb"\|"eq"\|"compressor"\|"delay"\|"chorus"\|"distortion", +kwargs específicos (room_size, damping, wet, bands, threshold, ratio, etc.) |
| `route_bus` | `route_audio_bus` | `(bus_name: str, send_to: str = 'Master', send_db: float = 0.0) -> dict` | bus_name, send_to=..., send_db=... |
| `spatial_player` | `create_spatial_audio_player` | `(scene_path: str, parent_node_path: str = '.', node_name: str = 'AudioStreamPlayer3D', audio_file: str = '', unit_size: float = 10.0, attenuation_model: str = 'inverse_distance', max_distance: float = 30.0, max_db: float = 3.0, panning_strength: float = 1.0, autoplay: bool = False, db_volume: float = 0.0) -> dict` | scene_path, parent_node_path=..., node_name=..., audio_file=..., unit_size=..., attenuation_model="inverse_distance"\|"logarithmic"\|"disabled", max_distance=..., max_db=..., panning_strength=..., autoplay=..., db_volume=... |
| `scan_sfx_events` | `scan_scene_for_sfx_events` | `(scene_path: str) -> dict` | scene_path |
| `generate_sfx_batch` | `generate_sfx_batch` | `(events: list[dict] \| None = None, scene_path: str \| None = None, style: str = 'scifi', output_dir: str = 'assets/sfx', max_sfx: int = 50) -> dict` | events=..., scene_path=..., style=..., output_dir=..., max_sfx=... |

### export_manage
**Descrição:** Gerencia exportação: listar presets, validar templates, build.
**Arquivos fonte:** tools.export_ops

| op | Handler | Assinatura REAL | Parâmetros |
|----|---------|----------------|------------|
| `list_presets` | `list_export_presets` | `() -> dict` | (sem parâmetros) |
| `validate_templates` | `validate_export_templates_installed` | `() -> dict` | (sem parâmetros) |
| `build` | `build_export` | `(preset_name: str | None = None, output_path: str | None = None) -> dict` | preset_name=..., output_path=... |

### d3_manage
**Descrição:** Gerencia 3D: luzes, CSG, materiais, partículas.
**Arquivos fonte:** tools.devsolo_ops

| op | Handler | Assinatura REAL | Parâmetros |
|----|---------|----------------|------------|
| `create_light` | `create_light_3d` | `(scene_path: str, parent_node_path: str = '.', light_type: str = 'omni', color: str = '#ffffff', energy: float = 1.0, shadows: bool = False, node_name: str = '') -> dict` | scene_path, parent_node_path=..., light_type=..., color=..., energy=..., shadows=..., node_name=... |
| `create_csg` | `create_csg_shape` | `(scene_path: str, parent_node_path: str = '.', shape_type: str = 'box', dimensions: list[float] | None = None, node_name: str = '') -> dict` | scene_path, parent_node_path=..., shape_type=..., dimensions=..., node_name=... |
| `config_material` | `configure_standard_material_3d` | `(scene_path: str, node_path: str, albedo_color: str = '#ffffff', metallic: float = 0.0, roughness: float = 0.5, emission_color: str = '#000000', emission_energy: float = 0.0, preset: str = 'custom') -> dict` | scene_path, node_path, albedo_color=..., metallic=..., roughness=..., emission_color=..., emission_energy=..., preset=... |
| `create_particles` | `create_particles_3d` | `(scene_path: str, parent_node_path: str = '.', node_name: str = 'GPUParticles3D', preset: str = 'fire') -> dict` | scene_path, parent_node_path=..., node_name=..., preset=... |

### debug_manage
**Descrição:** Gerencia debug: performance, colisão, navegação.
**Arquivos fonte:** tools.devsolo_ops

| op | Handler | Assinatura REAL | Parâmetros |
|----|---------|----------------|------------|
| `perf_stats` | `get_performance_stats` | `() -> dict` | (sem parâmetros) |
| `collision_debug` | `enable_debug_collisions` | `(enabled: bool = True) -> dict` | enabled=... |
| `nav_debug` | `enable_debug_navigation` | `(enabled: bool = True) -> dict` | enabled=... |

### config_manage
**Descrição:** Gerencia config: input actions e autoloads.
**Arquivos fonte:** tools.project_ops

| op | Handler | Assinatura REAL | Parâmetros |
|----|---------|----------------|------------|
| `input_action` | `configure_input_action` | `(action_name: str, keys: list[str], joypad_buttons: list[int] | None = None) -> dict` | action_name, keys, joypad_buttons=... |
| `autoload` | `configure_autoload` | `(name: str, script_path: str, singleton: bool = True) -> dict` | name, script_path, singleton=... |

### gamestate_manage
**Descrição:** Gerencia estado do jogo: save, FSM, transições.
**Arquivos fonte:** tools.devsolo_ops

| op | Handler | Assinatura REAL | Parâmetros |
|----|---------|----------------|------------|
| `create_save` | `create_save_system` | `(autoload_name: str = 'SaveManager', save_slots: int = 3, auto_save_enabled: bool = False, auto_save_interval: float = 60.0) -> dict` | autoload_name=..., save_slots=..., auto_save_enabled=..., auto_save_interval=... |
| `define_save` | `define_save_data` | `(node_path: str, property_name: str, section: str = 'default', key: str = '') -> dict` | node_path, property_name, section=..., key=... |
| `create_fsm` | `create_state_machine` | `(script_path: str, states: list[str], initial_state: str) -> dict` | script_path, states, initial_state |
| `add_transition` | `add_state_transition` | `(script_path: str, from_state: str, to_state: str, condition_code: str) -> dict` | script_path, from_state, to_state, condition_code |

### runtime_manage
**Descrição:** Gerencia runtime do Godot: compilar, rodar, parar, editor.
**Arquivos fonte:** tools.runtime_ops

| op | Handler | Assinatura REAL | Parâmetros |
|----|---------|----------------|------------|
| `compile` | `compile_test` | `() -> dict` | (sem parâmetros) |
| `run` | `run_game` | `(scene_path: str | None = None, wait_for_bridge: bool = True) -> dict` | scene_path=..., wait_for_bridge=... |
| `stop` | `stop_game` | `() -> dict` | (sem parâmetros) |
| `restart` | `smart_restart` | `(project_path: str | None = None) -> dict` | project_path=... |
| `launch_editor` | `launch_editor` | `(scene_path: str | None = None) -> dict` | scene_path=... |
| `close_editor` | `close_editor` | `() -> dict` | (sem parâmetros) |

### camera_manage
**Descrição:** Gerencia câmera 2D: setup, follow, shake.
**Arquivos fonte:** tools.devsolo_ops

| op | Handler | Assinatura REAL | Parâmetros |
|----|---------|----------------|------------|
| `setup_2d` | `setup_camera_2d` | `(scene_path: str, parent_node_path: str = '.', limits: dict | None = None, drag_horizontal: float = 0.0, drag_vertical: float = 0.0, zoom: list[float] | None = None, smoothing_enabled: bool = True, smoothing_speed: float = 5.0, current: bool = True) -> dict` | scene_path, parent_node_path=..., limits=..., drag_horizontal=..., drag_vertical=..., zoom=..., smoothing_enabled=..., smoothing_speed=..., current=... |
| `follow` | `setup_camera_follow` | `(scene_path: str, camera_node_path: str, target_node_path: str, smoothing: float = 5.0, offset_x: float = 0.0, offset_y: float = 0.0, deadzone_width: float = 0.0, deadzone_height: float = 0.0) -> dict` | scene_path, camera_node_path, target_node_path, smoothing=..., offset_x=..., offset_y=..., deadzone_width=..., deadzone_height=... |
| `shake` | `setup_camera_shake` | `(scene_path: str, camera_node_path: str, max_amplitude: float = 20.0, decay_rate: float = 2.0) -> dict` | scene_path, camera_node_path, max_amplitude=..., decay_rate=... |

### navigation_manage
**Descrição:** Gerencia navegação 2D: regiões, agentes, bake.
**Arquivos fonte:** tools.devsolo_ops

| op | Handler | Assinatura REAL | Parâmetros |
|----|---------|----------------|------------|
| `create_region` | `create_navigation_region_2d` | `(scene_path: str, parent_node_path: str = '.', polygon_vertices: list[list[float]] | None = None, region_name: str = 'NavigationRegion2D') -> dict` | scene_path, parent_node_path=..., polygon_vertices=..., region_name=... |
| `create_agent` | `create_navigation_agent_2d` | `(scene_path: str, parent_node_path: str, agent_name: str = 'NavigationAgent2D', target_node_path: str = 'root/Player', speed: float = 200.0, avoidance_enabled: bool = True) -> dict` | scene_path, parent_node_path, agent_name=..., target_node_path=..., speed=..., avoidance_enabled=... |
| `bake` | `bake_navigation_polygon` | `(scene_path: str, tilemap_layer_path: str, navigation_region_path: str, walkable_tiles: list[int] | None = None) -> dict` | scene_path, tilemap_layer_path, navigation_region_path, walkable_tiles=... |

### dialogue_manage
**Descrição:** Gerencia sistema de diálogo: criar, nós, UI.
**Arquivos fonte:** tools.devsolo_ops

| op | Handler | Assinatura REAL | Parâmetros |
|----|---------|----------------|------------|
| `create_system` | `create_dialogue_system` | `(autoload_name: str = 'DialogueManager') -> dict` | autoload_name=... |
| `add_node` | `add_dialogue_node` | `(dialogue_id: str, speaker: str, text: str, next_id: str = '', choices: list[dict] | None = None, events: list[dict] | None = None) -> dict` | dialogue_id, speaker, text, next_id=..., choices=..., events=... |
| `create_ui` | `create_dialogue_ui` | `(scene_name: str = 'dialogue_ui') -> dict` | scene_name=... |

### inventory_manage
**Descrição:** Gerencia inventário: sistema, itens, UI.
**Arquivos fonte:** tools.devsolo_ops

| op | Handler | Assinatura REAL | Parâmetros |
|----|---------|----------------|------------|
| `create_system` | `create_inventory_system` | `(autoload_name: str = 'InventoryManager', max_slots: int = 20) -> dict` | autoload_name=..., max_slots=... |
| `define_item` | `define_inventory_item` | `(item_id: str, item_name: str, item_type: str = 'consumable', description: str = '', stackable: bool = True, max_stack: int = 99, icon_path: str = '', properties: dict | None = None) -> dict` | item_id, item_name, item_type=..., description=..., stackable=..., max_stack=..., icon_path=..., properties=... |
| `create_ui` | `create_inventory_ui` | `(scene_name: str = 'inventory_ui', columns: int = 5) -> dict` | scene_name=..., columns=... |

### vfx_manage
**Descrição:** Gerencia VFX: partículas 2D, screen flash, ambiente.
**Arquivos fonte:** tools.devsolo_ops, tools.vfx_ops

| op | Handler | Assinatura REAL | Parâmetros |
|----|---------|----------------|------------|
| `create_particles` | `create_particles_2d` | `(scene_path: str, parent_node_path: str, node_name: str = 'Particles', amount: int | None = None, lifetime: float | None = None, explosiveness: float | None = None, direction: str | None = None, spread: float | None = None, gravity: str | None = None) -> dict` | scene_path, parent_node_path, node_name=..., amount=..., lifetime=..., explosiveness=..., direction=..., spread=..., gravity=... |
| `config_particles` | `configure_particles_2d` | `(scene_path: str, node_path: str, amount: int = 50, lifetime: float = 1.0, explosiveness: float = 0.0, emitting: bool = True, one_shot: bool = False, preset: str = 'custom') -> dict` | scene_path, node_path, amount=..., lifetime=..., explosiveness=..., emitting=..., one_shot=..., preset=... |
| `screen_flash` | `setup_screen_flash` | `(scene_path: str, parent_node_path: str = '.', flash_color: str = '#ffffff', flash_duration: float = 0.3) -> dict` | scene_path, parent_node_path=..., flash_color=..., flash_duration=... |
| `world_env` | `setup_world_environment` | `(scene_path: str, parent_node_path: str = '.', background_mode: str = 'color', background_color: str = '#1a1a2e', ambient_light_color: str = '#333344', ambient_light_energy: float = 1.0, glow_enabled: bool = False, glow_intensity: float = 0.8, fog_enabled: bool = False, fog_density: float = 0.01, fog_color: str = '#1a1a2e') -> dict` | scene_path, parent_node_path=..., background_mode=..., background_color=..., ambient_light_color=..., ambient_light_energy=..., glow_enabled=..., glow_intensity=..., fog_enabled=..., fog_density=..., fog_color=... |

### shader_manage
**Descrição:** Gerencia shaders: gerar, aplicar, ler, editar, parâmetros.
**Arquivos fonte:** tools.devsolo_ops, tools.shader_editor_ops

| op | Handler | Assinatura REAL | Parâmetros |
|----|---------|----------------|------------|
| `generate` | `generate_shader_2d` | `(scene_path: str, node_path: str, template: str = 'glow', uniforms: dict | None = None, shader_name: str = '') -> dict` | scene_path, node_path, template=..., uniforms=..., shader_name=... |
| `apply` | `apply_shader_to_node` | `(scene_path: str, node_path: str, shader_template: str = 'glow', uniforms: dict | None = None) -> dict` | scene_path, node_path, shader_template=..., uniforms=... |
| `read` | `read_shader` | `(shader_path: str, project_path: str | None = None) -> dict` | shader_path, project_path=... |
| `edit` | `edit_shader` | `(shader_path: str, new_code: str, project_path: str | None = None, validate: bool = True) -> dict` | shader_path, new_code, project_path=..., validate=... |
| `get_params` | `get_shader_params` | `(shader_path: str, project_path: str | None = None) -> dict` | shader_path, project_path=... |

### raycast_manage
**Descrição:** Gerencia raycasts 2D: RayCast2D e ShapeCast2D.
**Arquivos fonte:** tools.devsolo_ops

| op | Handler | Assinatura REAL | Parâmetros |
|----|---------|----------------|------------|
| `add_raycast` | `add_raycast_2d` | `(scene_path: str, parent_node_path: str, target_position: list[float] | None = None, collision_mask: int = 1, enabled: bool = True, node_name: str = 'RayCast2D') -> dict` | scene_path, parent_node_path, target_position=..., collision_mask=..., enabled=..., node_name=... |
| `add_shapecast` | `add_shapecast_2d` | `(scene_path: str, parent_node_path: str, shape_type: str = 'rectangle', shape_size: list[float] | None = None, collision_mask: int = 1, node_name: str = 'ShapeCast2D') -> dict` | scene_path, parent_node_path, shape_type=..., shape_size=..., collision_mask=..., node_name=... |

### test_manage
**Descrição:** Gerencia testes: assert_node e stress test.
**Arquivos fonte:** tools.playmode_ops, tools.stress_test_ops

| op | Handler | Assinatura REAL | Parâmetros |
|----|---------|----------------|------------|
| `assert_node` | `assert_node_exists` | `(scene_path: str, node_path: str, node_type: str | None = None) -> dict` | scene_path, node_path, node_type=... |
| `stress_test` | `run_stress_test` | `(project_path: str = '', spawn_scene_path: str = '', spawn_count: int = 10, duration_seconds: int = 5, input_actions: list[str] | None = None, random_seed: int = 42, fps_threshold: float = 30.0, sample_interval_ms: int = 500) -> dict` | project_path=..., spawn_scene_path=..., spawn_count=..., duration_seconds=..., input_actions=..., random_seed=..., fps_threshold=..., sample_interval_ms=... |

### analysis_manage
**Descrição:** Analisa o projeto: estrutura, design, escopo, busca.
**Arquivos fonte:** tools.analyze_ops

| op | Handler | Assinatura REAL | Parâmetros |
|----|---------|----------------|------------|
| `structure` | `analyze_game_structure` | `() -> dict` | (sem parâmetros) |
| `next_steps` | `suggest_next_steps` | `() -> dict` | (sem parâmetros) |
| `missing_refs` | `find_missing_references` | `() -> dict` | (sem parâmetros) |
| `validate_design` | `validate_game_design` | `() -> dict` | (sem parâmetros) |
| `estimate_scope` | `estimate_game_scope` | `() -> dict` | (sem parâmetros) |
| `search` | `search_codebase` | `(query: str, file_pattern: str = '*.gd', max_results: int = 20) -> dict` | query, file_pattern=..., max_results=... |
| `history` | `get_project_history` | `() -> dict` | (sem parâmetros) |

### safety_manage
**Descrição:** Gerencia segurança: backups, checkpoint git, undo.
**Arquivos fonte:** tools.safety

| op | Handler | Assinatura REAL | Parâmetros |
|----|---------|----------------|------------|
| `list_backups` | `list_backups` | `(original_path: str | None = None, project_root: pathlib.Path | None = None) -> list[dict]` | original_path=..., project_root=... |
| `restore` | `restore` | `(backup_id: str, project_root: pathlib.Path | None = None) -> dict` | backup_id, project_root=... |
| `checkpoint` | `git_checkpoint` | `(message: str, project_root: pathlib.Path | None = None, skip_validation: bool = False, skip_proof: bool = False) -> dict` | message, project_root=..., skip_validation=..., skip_proof=... |
| `undo` | `undo_last_action` | `(project_root: pathlib.Path | None = None) -> dict` | project_root=... |
| `undo_history` | `get_undo_history` | `() -> dict` | (sem parâmetros) |

### vision_manage
**Descrição:** Gerencia visão: comparar screenshots, detectar vazio/offscreen.
**Arquivos fonte:** tools.runtime_ops, tools.scene_ops

| op | Handler | Assinatura REAL | Parâmetros |
|----|---------|----------------|------------|
| `compare` | `compare_screenshots` | `(before_path: str, after_path: str) -> dict` | before_path, after_path |
| `detect_empty` | `detect_empty_screen` | `(screenshot_path: str | None = None, image_base64: str | None = None, empty_threshold: float = 0.95) -> dict` | screenshot_path=..., image_base64=..., empty_threshold=... |
| `detect_offscreen` | `detect_offscreen_elements` | `(scene_path: str, viewport_width: int = 1280, viewport_height: int = 720, margin: int = 50) -> dict` | scene_path, viewport_width=..., viewport_height=..., margin=... |


---

### localization_manage
**Descrição:** Testes de internacionalização (i18n): strings faltantes, overflow de texto com locale longo, e contraste texto/fundo (WCAG).
**Arquivos fonte:** tools.localization_ops

| op | Handler | Assinatura REAL | Parâmetros |
|----|---------|----------------|------------|
| `find_missing` | `find_missing_translations` | `(project_path: str \| None = None) -> dict` | project_path=... |
| `detect_overflow` | `detect_text_overflow` | `(scene_path: str, locale: str = "de", project_path: str \| None = None, font_size: int = 14) -> dict` | scene_path, locale=..., project_path=..., font_size=... |
| `check_contrast` | `check_text_contrast` | `(scene_path: str, project_path: str \| None = None) -> dict` | scene_path, project_path=... |


---

## Resumo de Erros

Nenhum erro de resolução de handler.

### playtest_manage
**Descrição:** Playtest autônomo: self_play — agente joga o jogo automaticamente, injeta inputs, captura screenshots e detecta anomalias.
**Arquivos fonte:** tools.playtest_ops

| op | Handler | Assinatura REAL | Parâmetros |
|----|---------|----------------|------------|
| \self_play\ | \self_play\ | \(duration: float = 30.0, inputs: list[dict] \| None = None, max_steps: int = 100, capture_interval: float = 2.0) -> dict\ | duration=..., inputs=..., max_steps=..., capture_interval=... |
