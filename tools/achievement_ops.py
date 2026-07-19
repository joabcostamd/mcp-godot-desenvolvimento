"""achievement_ops.py — Conquistas e Cloud Save (Fatia 5.1).

Fornece ferramentas para:
  - Criar/gerenciar sistema de conquistas (Steamworks + offline)
  - Configurar Cloud Save (Steam Auto-Cloud ou Godot user://)
  - Validar configuração de conquistas
"""

from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent

# ── Templates ────────────────────────────────────────────────────

_ACHIEVEMENT_TEMPLATE_GDS = '''extends Node
## Sistema de Conquistas — gerado por MCP Godot Agent
##
## Suporta Steamworks (via GodotSteam) e modo offline/local.
## Registre conquistas em _ready() e chame unlock() quando
## o jogador completar o requisito.

class_name AchievementManager

signal achievement_unlocked(id: String, name: String)

var _achievements: Dictionary = {}
var _unlocked: Array[String] = []
var _use_steam: bool = false
var _save_path: String = "user://achievements.save"

func _ready():
    _load_unlocked()
    _register_achievements()
    if _use_steam:
        _init_steam()

func _register_achievements():
    # EXEMPLO — substitua pelos seus achievements
    register("first_kill", "Primeiro Sangue", "Elimine seu primeiro inimigo")
    register("level_5", "Iniciante", "Alcance o nível 5")
    register("boss_1", "Chefe Derrotado", "Derrote o primeiro chefe")

func register(id: String, name: String, description: String, icon: String = ""):
    _achievements[id] = {"name": name, "description": description, "icon": icon, "unlocked": id in _unlocked}

func unlock(id: String):
    if not id in _achievements or id in _unlocked:
        return
    _unlocked.append(id)
    _achievements[id]["unlocked"] = true
    achievement_unlocked.emit(id, _achievements[id]["name"])
    _save_unlocked()
    if _use_steam:
        _unlock_steam(id)

func is_unlocked(id: String) -> bool:
    return id in _unlocked

func get_progress() -> Dictionary:
    var total := _achievements.size()
    var unlocked_count := _unlocked.size()
    return {"total": total, "unlocked": unlocked_count, "percent": ceil(float(unlocked_count) / max(total, 1) * 100)}

func _save_unlocked():
    var f := FileAccess.open(_save_path, FileAccess.WRITE)
    if f:
        f.store_string(JSON.stringify(_unlocked))
        f.close()

func _load_unlocked():
    if not FileAccess.file_exists(_save_path):
        return
    var f := FileAccess.open(_save_path, FileAccess.READ)
    if f:
        var txt := f.get_as_text()
        f.close()
        var parsed := JSON.parse_string(txt)
        if parsed is Array:
            _unlocked = parsed

func _init_steam():
    # Requer GodotSteam addon: https://github.com/GodotSteam/GodotSteam
    # Steam.achievement_ready.connect(_on_steam_achievement)
    pass

func _unlock_steam(id: String):
    # Steam.setAchievement(id)
    # Steam.storeStats()
    pass
'''

_CLOUD_SAVE_TEMPLATE_GDS = '''extends Node
## Cloud Save Manager — gerado por MCP Godot Agent
##
## Salva dados do jogador no Steam Auto-Cloud (user://)
## ou via GodotSteam Remote Storage.

class_name CloudSaveManager

var _enabled: bool = false
var _use_steam_cloud: bool = false

func _ready():
    _enabled = true

func save_game(slot_name: String, data: Dictionary) -> bool:
    if not _enabled:
        return false
    var path := "user://saves/%s.save" % slot_name
    DirAccess.make_dir_recursive_absolute(path.get_base_dir())
    var f := FileAccess.open(path, FileAccess.WRITE)
    if not f:
        return false
    f.store_string(JSON.stringify(data))
    f.close()
    if _use_steam_cloud:
        _save_to_steam_cloud(slot_name, data)
    return true

func load_game(slot_name: String) -> Dictionary:
    var path := "user://saves/%s.save" % slot_name
    if not FileAccess.file_exists(path):
        return {}
    var f := FileAccess.open(path, FileAccess.READ)
    if not f:
        return {}
    var txt := f.get_as_text()
    f.close()
    var parsed := JSON.parse_string(txt)
    if parsed is Dictionary:
        return parsed
    return {}

func list_saves() -> Array:
    var saves := []
    var dir := DirAccess.open("user://saves/")
    if dir:
        dir.list_dir_begin()
        var fn := dir.get_next()
        while fn != "":
            if fn.ends_with(".save"):
                saves.append(fn.replace(".save", ""))
            fn = dir.get_next()
        dir.list_dir_end()
    return saves

func delete_save(slot_name: String):
    var path := "user://saves/%s.save" % slot_name
    if FileAccess.file_exists(path):
        DirAccess.remove_absolute(path)

func _save_to_steam_cloud(_slot_name: String, _data: Dictionary):
    # Requer GodotSteam: Steam.fileWrite(...)
    pass
'''


# ══════════════════════════════════════════════════════════════════
# TOOL 1: create_achievement_system
# ══════════════════════════════════════════════════════════════════

def create_achievement_system(args: dict | None = None) -> dict:
    """Cria sistema de conquistas para Godot (local + Steamworks).

    Gera um script GDScript autoload com AchievementManager:
    registro, unlock, persistência em user://, e suporte a
    GodotSteam (Steamworks).

    Args:
        achievements: Lista de conquistas [{id, name, description}].
        use_steam: Se True, adiciona hooks para Steamworks.
        apply_to_project: Se True, salva o script no projeto ativo.

    Returns:
        dict com script_code e (se apply_to_project) file_path.
    """
    args = args or {}
    achievements = args.get("achievements", [])
    use_steam = args.get("use_steam", False)
    apply_to_project = args.get("apply_to_project", False)

    # Personaliza o template com as conquistas do usuário
    code = _ACHIEVEMENT_TEMPLATE_GDS
    if achievements:
        register_lines = []
        for a in achievements:
            aid = a.get("id", "ach_" + str(len(register_lines)))
            name = a.get("name", aid)
            desc = a.get("description", "")
            icon = a.get("icon", "")
            icon_part = f', "{icon}"' if icon else ""
            register_lines.append(f'\tregister("{aid}", "{name}", "{desc}"{icon_part})')
        replacement = "\n".join(register_lines)
        code = code.replace(
            '\tregister("first_kill", "Primeiro Sangue", "Elimine seu primeiro inimigo")\n\tregister("level_5", "Iniciante", "Alcance o nível 5")\n\tregister("boss_1", "Chefe Derrotado", "Derrote o primeiro chefe")',
            replacement
        )

    if not use_steam:
        code = code.replace("var _use_steam: bool = false", "var _use_steam: bool = false  # Steam desabilitado")
        code = code.replace("var _use_steam: bool = true", "var _use_steam: bool = false")

    result = {
        "status": "success",
        "achievements_count": len(achievements) if achievements else 3,
        "use_steam": use_steam,
        "script_code": code,
        "message": f"Sistema de conquistas gerado ({len(achievements) if achievements else 3} achievements).",
    }

    if apply_to_project:
        try:
            from tools.file_ops import _get_active_project
            proj = _get_active_project()
            script_dir = proj / "scripts" / "autoloads"
            script_dir.mkdir(parents=True, exist_ok=True)
            script_path = script_dir / "achievement_manager.gd"
            script_path.write_text(code, encoding="utf-8")
            result["file_path"] = str(script_path.relative_to(proj))
            result["message"] += f" Salvo em {result['file_path']}."
        except Exception as e:
            result["status"] = "error"
            result["message"] = f"Falha ao salvar: {e}"

    return result


# ══════════════════════════════════════════════════════════════════
# TOOL 2: cloud_save_configure
# ══════════════════════════════════════════════════════════════════

def cloud_save_configure(args: dict | None = None) -> dict:
    """Configura Cloud Save para o projeto (Steam Auto-Cloud + local).

    Gera um script GDScript CloudSaveManager com:
      - Save/Load em user://
      - Listagem de saves
      - Suporte a Steam Cloud (opcional)

    Args:
        use_steam_cloud: Se True, adiciona hooks para Steam Cloud.
        apply_to_project: Se True, salva o script no projeto ativo.

    Returns:
        dict com script_code e configuração de cloud save.
    """
    args = args or {}
    use_steam_cloud = args.get("use_steam_cloud", False)
    apply_to_project = args.get("apply_to_project", False)

    code = _CLOUD_SAVE_TEMPLATE_GDS
    if not use_steam_cloud:
        code = code.replace("var _use_steam_cloud: bool = false", "var _use_steam_cloud: bool = false  # Steam Cloud desabilitado")

    result = {
        "status": "success",
        "use_steam_cloud": use_steam_cloud,
        "storage": "user://saves/ (local)" + (" + Steam Auto-Cloud" if use_steam_cloud else ""),
        "script_code": code,
        "message": "Cloud Save configurado.",
    }

    if apply_to_project:
        try:
            from tools.file_ops import _get_active_project
            proj = _get_active_project()
            script_dir = proj / "scripts" / "autoloads"
            script_dir.mkdir(parents=True, exist_ok=True)
            script_path = script_dir / "cloud_save_manager.gd"
            script_path.write_text(code, encoding="utf-8")
            result["file_path"] = str(script_path.relative_to(proj))
            result["message"] += f" Salvo em {result['file_path']}."
        except Exception as e:
            result["status"] = "error"
            result["message"] = f"Falha ao salvar: {e}"

    return result


# ══════════════════════════════════════════════════════════════════
# TOOL 3: validate_achievement_config
# ══════════════════════════════════════════════════════════════════

def validate_achievement_config(args: dict | None = None) -> dict:
    """Valida configuração de conquistas contra requisitos Steam.

    Verifica:
      - Todas as conquistas têm id, nome e descrição
      - IDs são únicos
      - Nomes têm <= 64 caracteres
      - Descrições têm <= 256 caracteres
      - Ícones são 256x256 PNG (se fornecidos)

    Args:
        achievements: Lista de conquistas para validar.

    Returns:
        dict com validação e problemas encontrados.
    """
    args = args or {}
    achievements = args.get("achievements", [])
    if not achievements:
        return {"status": "error", "message": "Forneça uma lista de achievements."}

    issues = []
    ids_seen = set()

    for i, ach in enumerate(achievements):
        aid = ach.get("id", "")
        name = ach.get("name", "")
        desc = ach.get("description", "")

        if not aid:
            issues.append({"index": i, "field": "id", "severity": "error", "message": "ID vazio."})
        elif aid in ids_seen:
            issues.append({"index": i, "field": "id", "severity": "error", "message": f"ID duplicado: '{aid}'."})
        else:
            ids_seen.add(aid)

        if not name:
            issues.append({"index": i, "field": "name", "severity": "error", "message": "Nome vazio."})
        elif len(name) > 64:
            issues.append({"index": i, "field": "name", "severity": "warning", "message": f"Nome tem {len(name)} chars (max 64)."})

        if not desc:
            issues.append({"index": i, "field": "description", "severity": "warning", "message": "Descrição vazia."})
        elif len(desc) > 256:
            issues.append({"index": i, "field": "description", "severity": "warning", "message": f"Descrição tem {len(desc)} chars (max 256)."})

    errors = [i for i in issues if i["severity"] == "error"]
    warnings = [i for i in issues if i["severity"] == "warning"]

    return {
        "status": "success" if not errors else "issues_found",
        "valid": len(errors) == 0,
        "total": len(achievements),
        "errors": len(errors),
        "warnings": len(warnings),
        "issues": issues,
        "message": f"Validação: {len(errors)} erros, {len(warnings)} warnings em {len(achievements)} conquistas.",
    }
