"""deprecated.py — Set unificado de tools depreciadas.

Estas ~112 tools foram colapsadas em <domain>_manage rollups.
As funções subjacentes CONTINUAM existindo — só a definição
da tool individual é removida para reduzir o tool count.

Uso:
    from tools.deprecated import DEPRECATED_TOOLS, ALIAS_MAP
    _DEPRECATED = DEPRECATED_TOOLS
    _DEPRECATED_H = DEPRECATED_TOOLS

Gerado em: Sprint 0.5 — Unificação _DEPRECATED + _DEPRECATED_H
Expandido em: F5 (reorg) + Estabilizacao K2 (aliases)
Origem: server.py linhas ~4600 e ~4996 (duplicados)
"""

from __future__ import annotations

DEPRECATED_TOOLS: set[str] = {
    "add_audio_effect", "add_collision_shape", "add_control_node",
    "add_node", "add_script_signal", "add_script_variable",
    "add_state_transition", "attach_script", "build_export",
    "chain_tweens", "configure_audio_bus", "configure_autoload",
    "configure_input_action", "configure_standard_material_3d",
    "connect_signal", "create_animation", "create_animation_player",
    "create_csg_shape", "create_health_bar", "create_hud_template",
    "create_joint_2d", "create_light_3d", "create_loading_screen",
    "create_main_menu", "create_particles_3d", "create_pause_menu",
    "create_project", "create_save_system", "create_scene",
    "create_state_machine", "create_tilemap_layer", "create_tileset",
    "create_tween_animation", "create_ui_scene", "define_save_data",
    "delete_file", "delete_node", "detach_script",
    "enable_debug_collisions", "enable_debug_navigation",
    "generate_background_gradient", "generate_gdscript",
    "generate_placeholder_sprite", "generate_placeholder_texture_atlas",
    "generate_tilemap_from_noise", "generate_tileset_from_colors",
    "get_node_property", "get_performance_stats",
    "get_project_settings", "import_audio", "import_sprite_sheet",
    "import_texture", "inspect_project", "instance_scene_as_child",
    "list_export_presets", "list_signals", "load_scene_tree",
    "move_file", "paint_tilemap_cell", "reparent_node",
    "set_active_project", "set_collision_layer_mask",
    "set_main_scene", "set_node_property", "set_physics_material",
    "set_project_setting", "suggest_color_palette",
    "validate_export_templates_installed", "validate_gdscript_syntax",
    # Onda Extra
    "compile_test", "run_game", "stop_game", "smart_restart",
    "launch_editor", "close_editor",
    "setup_camera_2d", "setup_camera_follow", "setup_camera_shake",
    "create_navigation_region_2d", "create_navigation_agent_2d",
    "bake_navigation_polygon",
    "create_dialogue_system", "add_dialogue_node", "create_dialogue_ui",
    "create_inventory_system", "define_inventory_item", "create_inventory_ui",
    "configure_particles_2d", "create_particles_2d", "create_light_2d",
    "setup_screen_flash", "setup_world_environment",
    "generate_shader_2d", "apply_shader_to_node", "create_shader_material",
    "analyze_game_structure", "suggest_next_steps",
    "find_missing_references", "validate_game_design",
    "estimate_game_scope", "search_codebase", "get_project_history",
    "list_backups", "restore_backup", "git_commit_checkpoint",
    "undo_last_action", "get_undo_history",
    "compare_screenshots", "detect_empty_screen", "detect_offscreen_elements",
    # ── F5: atômicas consolidadas em rollups ──
    # gdscript_* → lsp_manage
    "gdscript_definition", "gdscript_diagnostics", "gdscript_hover",
    "gdscript_lsp_connect", "gdscript_lsp_disconnect", "gdscript_references",
    "gdscript_rename", "gdscript_symbols", "gdscript_sync_file",
    # skeleton_* → skeleton_manage
    "skeleton_create_bone", "skeleton_create_ik_chain",
    "skeleton_get_bone_pose", "skeleton_get_info",
    "skeleton_list_bones", "skeleton_set_bone_pose",
    # ui_* → ui_manage (ops adicionados)
    "ui_configure_focus_nav", "ui_create_tab_with_content",
    "ui_create_widget", "ui_set_anchor_preset", "ui_set_tooltip",
    # godot_* → godot_manage
    "godot_run_project", "godot_stop_project", "godot_wait_for_bridge",
    "godot_exec", "godot_runtime_info",
    # debugger_* → debug_manage
    "debugger_set_breakpoint", "debugger_status", "debugger_step",
    "debugger_get_stack", "debugger_get_variables",
    # network_* → network_manage
    "network_setup_multiplayer", "network_create_rpc",
    "network_create_websocket", "network_configure_dedicated_server",
    "network_create_lobby",
    # render_* → render_manage
    "render_get_settings", "render_set_antialiasing",
    "render_set_scaling", "render_set_quality",
    # shader atomics → shader_manage (F5.3)
    "read_shader", "edit_shader", "get_shader_params",
    # raycast atomics → physics_manage (F5.1)
    "add_raycast_2d", "add_shapecast_2d",
    # vfx atomics → vfx_manage (F5.6)
    "create_particles_2d", "configure_particles_2d",
    # test/verify atomics → test_manage (F5.14)
    "run_gut_tests", "run_scripted_tests", "regression_test",
    "smoke_test", "run_verification_pipeline",
}


# ── ALIAS_MAP: old_name → (rollup_name, op_name) ─────────────────
# Secao 11.9 do roadmap: toda tool renomeada leva alias por 1 fase.
# Quando invoke_by_name recebe um nome antigo, redireciona para o
# rollup equivalente e loga "deprecated_alias_used".
# Gerado em: Fechamento da Estabilizacao (K2) — 2026-07-21

ALIAS_MAP: dict[str, tuple[str, str]] = {
    # ── godot_* → godot_manage ──
    "godot_exec": ("godot_manage", "exec_gdscript"),
    "godot_run_project": ("godot_manage", "run_project"),
    "godot_runtime_info": ("godot_manage", "runtime_info"),
    "godot_stop_project": ("godot_manage", "stop_project"),
    "godot_wait_for_bridge": ("godot_manage", "wait_bridge"),
    # ── gdscript_* → lsp_manage ──
    "gdscript_lsp_connect": ("lsp_manage", "connect"),
    "gdscript_lsp_disconnect": ("lsp_manage", "disconnect"),
    "gdscript_sync_file": ("lsp_manage", "sync"),
    "gdscript_definition": ("lsp_manage", "definition"),
    "gdscript_references": ("lsp_manage", "references"),
    "gdscript_hover": ("lsp_manage", "hover"),
    "gdscript_symbols": ("lsp_manage", "symbols"),
    "gdscript_rename": ("lsp_manage", "rename"),
    "gdscript_diagnostics": ("lsp_manage", "diagnostics"),
    # ── debugger_* → debug_manage ──
    "debugger_set_breakpoint": ("debug_manage", "set_breakpoint"),
    "debugger_status": ("debug_manage", "status"),
    "debugger_step": ("debug_manage", "step"),
    "debugger_get_stack": ("debug_manage", "get_stack"),
    "debugger_get_variables": ("debug_manage", "get_vars"),
    # ── network_* → network_manage ──
    "network_setup_multiplayer": ("network_manage", "setup_peer"),
    "network_create_rpc": ("network_manage", "create_rpc"),
    "network_create_websocket": ("network_manage", "create_ws"),
    "network_configure_dedicated_server": ("network_manage", "config_server"),
    "network_create_lobby": ("network_manage", "create_lobby"),
    # ── render_* → render_manage ──
    "render_get_settings": ("render_manage", "get"),
    "render_set_antialiasing": ("render_manage", "set_aa"),
    "render_set_scaling": ("render_manage", "set_scale"),
    "render_set_quality": ("render_manage", "set_quality"),
    # ── skeleton_* → skeleton_manage ──
    "skeleton_get_bone_pose": ("skeleton_manage", "get_pose"),
    "skeleton_set_bone_pose": ("skeleton_manage", "set_pose"),
    "skeleton_list_bones": ("skeleton_manage", "list_bones"),
    "skeleton_create_bone": ("skeleton_manage", "create_bone"),
    "skeleton_create_ik_chain": ("skeleton_manage", "create_ik"),
    "skeleton_get_info": ("skeleton_manage", "get_info"),
    # ── shader atomics → shader_manage ──
    "read_shader": ("shader_manage", "read"),
    "edit_shader": ("shader_manage", "edit"),
    "get_shader_params": ("shader_manage", "get_params"),
    # ── raycast atomics → physics_manage ──
    "add_raycast_2d": ("physics_manage", "add_raycast"),
    "add_shapecast_2d": ("physics_manage", "add_shapecast"),
    # ── vfx atomics → vfx_manage (F5.6) ──
    "create_particles_2d": ("vfx_manage", "create_particles"),
    "configure_particles_2d": ("vfx_manage", "config_particles"),
    "create_particles_3d": ("vfx_manage", "create_particles_3d"),
    # ── test/verify atomics → test_manage (F5.14) ──
    "run_gut_tests": ("test_manage", "gut"),
    "run_scripted_tests": ("test_manage", "scripted"),
    "regression_test": ("test_manage", "regression"),
    "smoke_test": ("test_manage", "smoke"),
    "run_verification_pipeline": ("test_manage", "verify_pipeline"),
}
