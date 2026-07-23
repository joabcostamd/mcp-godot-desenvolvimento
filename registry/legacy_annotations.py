"""registry/legacy_annotations.py — Dados legados de hints (ONDA 2.3).

Extraído de server.py. Contém _HINT_RULES usado por _apply_hints().
Congelado como dados estáticos — não adicionar novas regras aqui.
"""

_HINT_RULES = {
    "readOnly": {
        "prefixes": ["get_", "list_", "read_", "query_", "search_", "inspect_",
                     "validate_", "check_", "find_", "suggest_", "analyze_",
                     "capture_", "detect_", "estimate_", "compare_"],
        "suffixes": ["_status", "_info", "_history", "_output", "_map",
                    "_state", "_summary", "_catalog", "_health"],
        "exact": ["ping", "health_check", "self_test", "project_map",
                  "tool_catalog", "tool_groups", "get_project_history",
                  "gdscript_hover", "gdscript_symbols", "gdscript_diagnostics",
                  "gdscript_references", "gdscript_definition",
                  "security_status", "get_audit_log", "get_safety_policy",
                  "get_undo_history", "get_vibe_context",
                  "get_runtime_state_digest", "capture_runtime_errors",
                  "detect_empty_screen", "detect_offscreen_elements"],
    },
    "destructive": {
        "prefixes": ["delete_", "remove_", "destroy_", "clear_", "reset_",
                    "close_", "stop_", "kill_", "wipe_"],
        "exact": ["restore_backup", "undo_last_action", "push_undo",
                  "detach_script", "build_export", "configure_security",
                  "set_safety_policy"],
    },
    "idempotent": {
        "prefixes": ["create_", "set_", "write_", "configure_", "import_",
                    "generate_", "register_", "install_", "add_"],
        "suffixes": ["_checkpoint", "_snapshot"],
        "exact": ["batch_atomic_edit", "attach_script", "connect_signal",
                  "safe_write_gdscript"],
    },
    "openWorld": {
        "prefixes": ["download_", "fetch_", "generate_game_art", "generate_voice",
                    "search_codebase", "web_", "http_"],
        "exact": ["generate_game_art_flux", "generate_audio_sfx",
                  "download_asset", "import_downloaded_asset",
                  "game_http_request", "game_websocket"],
    },
}
