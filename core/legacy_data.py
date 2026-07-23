"""Dados legados de curadoria — ONDA 1.3.

Extraidos de server.py. Importados por server.py e registry/.
Serao substituidos pelo registry quando dominios tiverem manifestos.
"""

TOOLSETS = {
    # ── 5 Namespaces Semânticos (Etapa A1) ──
    # Reduz ~60 tools visíveis → ≤20 por namespace.
    # A IA primeiro vê os 5 namespaces, depois explora um por vez.
    "project": [
        # Fundação — projeto, cenas, scripts, arquivos, UI
        "project_manage", "project_status", "project_map",
        "scene_manage", "node_manage",
        "script_manage", "safe_write_gdscript",
        "file_manage", "read_file", "write_file",
        "ui_manage",
        "create_entity", "create_entities",
        "generate_project_structure",
        # Gameplay estrutural
        "physics_manage", "anim_manage", "camera_manage",
        "tilemap_manage", "navigation_manage",
        "gamestate_manage", "dialogue_manage", "inventory_manage",
        "d3_manage",
        # Configuração
        "config_manage",
        "setup_localization", "add_translation_string",
        "create_animation_tree",
        "behavior_tree_generate", "behavior_tree_list_templates",
        "world_describe",
        # Batch/atômico
        "batch_atomic_edit", "add_nodes_batch", "set_properties_batch",
        "load_scene_async",
        # Templates de gameplay
        "create_gun_system", "create_bullet_template",
        "create_parallax_background", "add_parallax_layer", "create_spritesheet",
        "create_path_2d", "create_patrol_route",
        "loot_table_generate",
        # Operações atômicas de cena (complementam os rollups)
        "raycast_manage",
        # Camada 5 (Gameplay): project
        "create_achievement_system", "cloud_save_configure",
        "mod_manifest_generate",
        "cutscene_create_timeline", "cutscene_add_camera_shot", "cutscene_add_dialogue_event",
        "quest_generate",
        "dialogue_generate_npc_lines", "dialogue_generate_personality",
        "accessibility_apply_colorblind_filter", "accessibility_add_subtitles", "accessibility_remap_controls",
        "onboarding_create_tutorial_step", "onboarding_create_guided_tour",
    
        "skeleton_manage",
        "csg_create_node",
        "gi_create_node",
        "scene_fx_create_node",
        "sky_create_procedural",
        "camera_configure_attributes",
        "multimesh_create_instance",
        "physics_create_joint",
        "physics_configure_body",

        "network_manage",
        "render_manage",
        "csharp_scaffold_project",
        "csharp_generate_script",
        "csharp_build_project",
],
    "assets": [
        # Assets, arte, áudio, shaders, VFX
        "asset_manage",
        "generate_game_art", "generate_game_art_flux", "apply_game_art",
        "generate_3d_asset", "generate_3d_placeholder",
        "import_asset_manifest", "create_asset_manifest",
        "download_asset", "import_downloaded_asset",
        "audio_manage", "music_manage",
        "generate_audio_sfx", "generate_voice",
        "shader_manage", "shader_generate", "shader_list_templates",
        "vfx_manage",
        "optimize_sprite", "remove_background",
        "marketplace_search", "marketplace_download",
        # Geração procedural de conteúdo
        "generate_dungeon_rooms", "dungeon_generate",
        "terrain_generate", "wave_generate",
        # Juice/Polimento visual
        "juice_apply", "juice_list_presets",
        # Camada 5 (Gameplay): assets
        "trailer_capture_clip", "trailer_render_sequence", "capsule_generate_store_image",
        "import_3d_model",
    ],
    "runtime": [
        # Execução, debug, testes, bridge, jogo rodando
        "runtime_manage",
        "godot_manage",
        "screenshot_manage",
        "godot_custom_command", "godot_list_custom_commands",
        "godot_keep_alive",
        "get_runtime_state_digest", "capture_runtime_errors",
        "freeze_game_clock", "unfreeze_game_clock", "step_game_time", "step_until",
        "effect_probe",
        # Debug
        "debug_manage",
        # Testes
        "test_manage",
        "run_stress_test",
        "assert_node_exists",
        # Bridge
        "game_bridge_manage",
        # Input/Recording
        "inject_input_event", "simulate_input_sequence",
        "watch_signal", "watch_state_start", "watch_state_collect",
        "record_gameplay_gif", "start_recording", "stop_recording",
        # Editor ao vivo
        "editor_manage",
        "read_console_output",
        # Performance
        "profile_frame", "profile_memory",
        "auto_screenshot",
        # Build/Export
        "build_csharp", "export_manage",
        # Playtest
        "playtest_manage",
    
        "physics_query_area_overlap",
        "physics_raycast_query",
        "runtime_connect_signal",
        "runtime_disconnect_signal",
        "runtime_emit_signal",
],
    "analysis": [
        # Análise, auditoria, qualidade, referências, introspecção
        "analysis_manage",
        "query_classdb", "search_classdb", "godot_class_ref",
        "list_valid_node_types",
        "validate_project_refs", "find_usages",
        "audit_input_map", "audit_autoloads", "audit_scene_reachability",
        "audit_uid_consistency", "audit_save_compatibility",
        "analyze_signal_flow",
        "lsp_manage",
        "resource_dependency_graph",
        "find_unused_resources",
        "estimate_tool_tokens",
        "dps_calculator", "balance_analyze",
        "vision_manage",
        "localization_manage",
        # Camada 5 (Gameplay): analysis
        "validate_achievement_config", "validate_mod_compatibility",
        "telemetry_track_event", "telemetry_get_funnel", "telemetry_session_summary", "telemetry_heatmap",
        "adaptive_difficulty_adjust",
        "accessibility_audit_scene", "accessibility_certification_checklist",
        "onboarding_check_first_experience",
    
        "runtime_list_signals",
        "runtime_watch_signal",
        # ── F3: _manage órfãos ganham namespace ──
        "complexity_gate_manage", "fun_report_manage",
        "reviewer_manage", "scope_manage", "teacher_manage",
],
    "orchestration": [
        # Meta-tools, workflow, governança, fase, segurança, bootstrap
        "godot",
        "ping", "health_check", "self_test", "bootstrap_godot_mcp",
        "dump_mcp_state",
        "capture_proof", "verify_proof",
        "validate_mcp_registry", "validate_mcp_environment", "validate_godot_version",
        "tool_catalog", "tool_groups",
        "catalog_search", "describe_tool", "invoke_by_name",
        "safety_manage",
        "set_safety_policy", "configure_security", "security_status",
        "circuit_breaker_status",
        "get_current_phase", "advance_phase", "get_phase_history",
        "get_next_step", "resume_session",
        "get_audit_log", "get_audit_replay",
        "workflow_handoff", "workflow_snapshot",
        "set_auto_dismiss",
        "vibe_coding_mode", "get_vibe_context",
        "project_progress",
        "generate_ci_snippet",
        "install_mcp_addon", "setup_mcp_config",
        "create_milestone_plan", "get_milestone_plan", "advance_milestone",
        "set_project_brief", "get_project_brief", "update_project_brief",
        "gdd_generate",
        "release_checklist", "deploy_itch",
        "configure_export_preset",
        # Camada 5 (Gameplay): orchestration
        "remote_balance_config",
        # ── F3: _manage órfãos ganham namespace ──
        "budget_manage", "mcp_telemetry_manage", "quickstart_manage",
        "version_history_manage", "publish_manage", "community_manage",
        "polish_manage",
    ],
}

TOOL_PROFILES = {
    "core": [
        "ping", "health_check", "self_test", "bootstrap_godot_mcp",
        "read_file", "write_file", "safe_write_gdscript",
        "compile_test", "run_game", "stop_game", "smart_restart",
        "git_commit_checkpoint", "smoke_test", "dump_mcp_state",
        "project_manage",
    ],
    "dev": [
        "godot",
        "ping", "health_check", "self_test", "bootstrap_godot_mcp",
        "read_file", "write_file", "safe_write_gdscript",
        "compile_test", "run_game", "stop_game", "smart_restart",
        "git_commit_checkpoint", "smoke_test", "dump_mcp_state",
        "project_manage", "scene_manage", "node_manage", "script_manage",
        "file_manage", "asset_manage", "runtime_manage",
        "validate_gdscript_syntax", "validate_project_refs", "find_usages",
        "run_scripted_tests", "regression_test",
        "run_gut_tests", "godot_class_ref", "godot_exec", "effect_probe",
        "take_screenshot", "capture_runtime_errors", "get_runtime_state_digest",
        "import_asset_manifest", "create_asset_manifest",
        # ── Phase management (Feature 8: tool_list_changed) ──
        "get_current_phase", "advance_phase", "get_phase_history",
        "get_next_step", "resume_session",
    ],
    "lean": [
        "godot",
        "ping", "health_check", "self_test", "bootstrap_godot_mcp",
        "read_file", "write_file", "safe_write_gdscript",
        # ── Meta-tools (Fatia 0.15) ──
        "catalog_search", "describe_tool", "invoke_by_name",
        # ── Phase management ──
        "get_current_phase", "advance_phase", "get_phase_history",
        "get_next_step", "resume_session",
    ],
    "full": [],  # vazio = sem filtro (todas as tools)
}

PHASE_TOOLSETS: dict[str, set[str]] = {
    "IDEIA": {
        "ping", "health_check", "self_test", "bootstrap_godot_mcp",
        "read_file", "write_file", "dump_mcp_state",
        "project_manage", "project_status",
        "tool_catalog", "tool_groups",
        "get_current_phase", "advance_phase", "get_phase_history",
        "create_milestone_plan", "get_milestone_plan", "advance_milestone",
        "set_project_brief", "get_project_brief", "update_project_brief",
        "gdd_generate",
        "analysis_manage",
        "godot_class_ref",
        "validate_mcp_environment", "validate_godot_version",
        "setup_mcp_config", "install_mcp_addon",
        "safety_manage",
        "capture_proof", "verify_proof",
        "audit_input_map", "audit_autoloads", "audit_scene_reachability",
        "audit_uid_consistency", "audit_save_compatibility",
        "validate_mcp_registry",
        "project_progress",
    },
    "DESIGN": {
        "scene_manage", "node_manage",
        "script_manage", "safe_write_gdscript",
        "lsp_manage",
        "file_manage",
        "create_entity", "create_entities",
        "ui_manage",
        "config_manage",
        "project_map",
        "resource_dependency_graph",
        "query_classdb", "search_classdb",
        "list_valid_node_types",
        "validate_project_refs", "find_usages",
        "analyze_signal_flow",
        "behavior_tree_generate", "behavior_tree_list_templates",
        "generate_project_structure",
        "world_describe",
        "skeleton_manage",
        "ui_manage",
        "config_manage",
        "project_map",
        "resource_dependency_graph",
        "query_classdb", "search_classdb",
        "list_valid_node_types",
        "validate_project_refs", "find_usages",
        "analyze_signal_flow",
        "behavior_tree_generate", "behavior_tree_list_templates",
        "generate_project_structure",
        "world_describe",
        "render_manage",
        "csharp_scaffold_project",
        "csharp_generate_script",
        # ── Movidos do PROTOTIPO (F5 prep) ──
        "physics_create_joint", "physics_configure_body",
        "physics_create_joint", "physics_configure_body",
        "physics_query_area_overlap", "physics_raycast_query",
        "camera_configure_attributes",
        "runtime_connect_signal", "runtime_disconnect_signal",
        "runtime_emit_signal", "runtime_watch_signal",
        "shader_generate", "shader_list_templates",
        # ── Movidos do PROTOTIPO (F5 prep) ──
        "create_animation_tree", "generate_audio_sfx",
        "load_scene_async",
        "godot_custom_command", "godot_list_custom_commands",
        "godot_keep_alive",
        # ── Movidos do PROTOTIPO (F5 final) ──
        "execute_gdscript_runtime", "raycast_manage",
},
    "PROTOTIPO": {
        # ── Execução runtime (core do prototipar) ──
        "runtime_manage",
        "godot_manage",
        "editor_manage",
        # ── Game bridge ──
        "game_bridge_manage",
        # ── Rollups de prototipagem rápida ──
        "physics_manage",
        "asset_manage",
        "audio_manage",
        "anim_manage",
        "camera_manage",
        "vfx_manage",
        "shader_manage",
        # ── Movidos para DESIGN: execute_gdscript_runtime, raycast_manage
        # ── Movidos para DESIGN: create_animation_tree, generate_audio_sfx,
        #     load_scene_async, godot_custom_command, godot_list_custom_commands,
        #     godot_keep_alive
        # ── Movidos para POLIMENTO: capture_game_screenshot, godot_screenshot,
        #     take_screenshot, get_runtime_state_digest, capture_runtime_errors,
        #     effect_probe
},
    "CONTEUDO": {
        "tilemap_manage",
        "navigation_manage",
        "editor_manage",
        "create_parallax_background", "add_parallax_layer", "create_spritesheet",
        "optimize_sprite", "remove_background",
        "create_path_2d", "create_patrol_route",
        "create_gun_system", "create_bullet_template",
        "dialogue_manage", "inventory_manage",
        "d3_manage",
        "gamestate_manage",
        "import_3d_model", "import_asset_manifest",
        "create_asset_manifest",
        "download_asset", "import_downloaded_asset",
        "marketplace_search", "marketplace_download",
        "generate_dungeon_rooms", "dungeon_generate",
        "terrain_generate", "wave_generate",
        "dps_calculator", "balance_analyze",
        "loot_table_generate",
        "juice_apply", "juice_list_presets",
        "setup_localization", "add_translation_string",
        "generate_voice",
        "find_unused_resources",
        "network_manage",
        "render_manage",
        # ── F5 prep: assets generation moved from PROTOTIPO ──
        "generate_game_art", "generate_game_art_flux",
        "apply_game_art",
        "generate_3d_asset", "generate_3d_placeholder",
        "skeleton_manage",
        "csg_create_node", "gi_create_node",
        "scene_fx_create_node", "sky_create_procedural",
        "multimesh_create_instance",
        "batch_atomic_edit", "add_nodes_batch",
        "set_properties_batch",
},
    "POLIMENTO": {
        "debug_manage",
        "vision_manage",
        "profile_frame", "profile_memory",
        "set_safety_policy",
        "security_status",
        "configure_security",
        "circuit_breaker_status",
        "get_audit_log", "get_audit_replay",
        "auto_screenshot",
        "estimate_tool_tokens",
        "workflow_handoff", "workflow_snapshot",
        "generate_ci_snippet",
        "find_unused_resources",
        "set_auto_dismiss",
        "test_manage",
        "vibe_coding_mode", "get_vibe_context",
    
        "runtime_list_signals",
        # ── F5 prep: recording moved from PROTOTIPO ──
        "record_gameplay_gif", "start_recording", "stop_recording",
        # ── Movidos do PROTOTIPO (F5 prep) ──
        "freeze_game_clock", "unfreeze_game_clock",
        "step_game_time", "step_until",
        "watch_signal", "watch_state_start", "watch_state_collect",
        "inject_input_event", "simulate_input_sequence",
        # ── Screenshots e debug ──
        "screenshot_manage",
        "get_runtime_state_digest", "capture_runtime_errors",
        "effect_probe",
},
    "PRONTO_PARA_LANCAR": {
        "export_manage",
        "build_csharp",
        "configure_export_preset",
        "deploy_itch",
        "release_checklist",
        "editor_manage",
        "read_console_output",
    
        "csharp_build_project",
},
}

PHASE_TOOLS_CORE = {
    "godot",
    "ping", "health_check", "self_test", "bootstrap_godot_mcp",
    "get_current_phase", "advance_phase", "get_phase_history",
    "get_next_step", "resume_session",
    "read_file", "write_file", "file_manage",
    "safe_write_gdscript", "script_manage",
    "safety_manage", "capture_proof", "verify_proof",
    "scene_manage", "node_manage",
    # ── F4.1: Descoberta progressiva (padrão MCP 3 camadas) ──
    "catalog_search", "describe_tool", "invoke_by_name",
}

