"""editor_config.py — Godot Editor fluido para MCP (Onda 5.5).

Configura o editor para operacao em background:
- Auto-reload de scripts modificados pelo MCP
- Baixo consumo quando minimizado (2 FPS)
- Auto-save para evitar dialogos 'unsaved changes'
- Import de assets mesmo sem foco
"""

from tools.bridge import send_editor_batch


def configure_editor_for_mcp() -> dict:
    """Configura o Godot Editor para operacao fluida com MCP."""
    settings = [
        ("text_editor/behavior/files/auto_reload_scripts_on_external_change", True),
        ("interface/editor/behavior/import_resources_when_unfocused", True),
        ("interface/editor/timers/unfocused_low_processor_mode_sleep_usec", 500000),
        ("interface/editor/behavior/save_on_focus_loss", True),
        ("interface/editor/display/vsync_mode", 0),
        ("interface/editor/display/update_continuously", False),
    ]

    commands = [{"method": "set_editor_setting", "params": {"setting": s, "value": v}} for s, v in settings]

    try:
        results = send_editor_batch(commands)
        applied = sum(1 for r in results if "error" not in str(r))
    except Exception:
        applied = 0
        results = []

    return {
        "status": "success",
        "settings_applied": applied,
        "total": len(settings),
        "message": f"Editor configurado para MCP: {applied}/{len(settings)}. Godot pronto para background.",
    }


def _notify_godot_file_changed(file_path: str):
    """Notifica o Godot que um arquivo mudou. Forca reload e mostra toast (Onda 5.5)."""
    try:
        from tools.bridge import _send_editor
        _send_editor("update_file", {"path": file_path})
        if file_path.endswith('.tscn'):
            _send_editor("reload_scene", {"path": file_path})
        _send_editor("toast", {"level": "info", "message": f"MCP: {file_path.split('/')[-1]} atualizado"})
    except Exception:
        pass


def _auto_save_before_edit():
    """Salva todas as cenas antes de editar (evita 'unsaved changes')."""
    try:
        from tools.bridge import _send_editor
        _send_editor("save_all_scenes", {})
    except Exception:
        pass
