"""deprecated.py — Set unificado de tools depreciadas.

Estas 69 tools foram colapsadas nos 16 <domain>_manage rollups.
As funções subjacentes CONTINUAM existindo — só a definição
da tool individual é removida para reduzir o tool count.

Uso:
    from tools.deprecated import DEPRECATED_TOOLS
    _DEPRECATED = DEPRECATED_TOOLS
    _DEPRECATED_H = DEPRECATED_TOOLS

Gerado em: Sprint 0.5 — Unificação _DEPRECATED + _DEPRECATED_H
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
}
