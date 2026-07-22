"""behavior_ops.py — Behavior Trees para IA de jogos (GRATIS, sem API).

Gera codigo GDScript completo de arvore de comportamento a partir
de descricao em linguagem natural (portugues).

Nodos suportados:
    Sequence, Selector (Priority), Parallel, Condition, Action,
    Wait, Loop, Inverter, Succeeder, Repeater
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


_BT_TEMPLATES = {
    "patrol_chase_attack": {
        "description": "Patrulha, persegue ao detectar, ataca quando perto",
        "nodes": ["Sequence"],
        "actions": ["patrol", "check_player_distance", "chase", "attack"],
        "conditions": ["player_detected", "in_attack_range", "health_low"],
    },
    "patrol_chase_attack_flee": {
        "description": "Patrulha, persegue, ataca, foge com pouca vida",
        "nodes": ["Selector"],
        "actions": ["flee", "attack", "chase", "patrol"],
        "conditions": ["health_critical", "in_attack_range", "player_detected"],
    },
    "guard_alert_chase": {
        "description": "Guarda posicao, alerta ao detectar, persegue",
        "nodes": ["Sequence"],
        "actions": ["guard", "alert", "chase", "return_to_post"],
        "conditions": ["player_detected", "player_lost", "at_post"],
    },
    "idle_wander_flee": {
        "description": "NPC pacifico: idle, vagueia, foge de perigo",
        "nodes": ["Selector"],
        "actions": ["flee_from_danger", "wander", "idle"],
        "conditions": ["danger_nearby", "bored"],
    },
    "boss_phases": {
        "description": "Chefao com fases: fase 1 ataques, fase 2 enrage, fase 3 desespero",
        "nodes": ["Sequence"],
        "actions": ["phase1_attack", "phase2_enrage", "phase3_desperate"],
        "conditions": ["health_above_66", "health_above_33", "health_above_0"],
    },
}


def _generate_bt_gdscript(behavior_name, description, actions, conditions, tree_type="Selector"):
    code = f'''# Behavior Tree: {behavior_name}
# Gerado automaticamente pelo MCP Godot
# Descricao: {description}

class_name BT{behavior_name.replace(" ", "")}
extends Node

signal behavior_changed(old_action, new_action)
signal action_completed(action_name)

var current_action: String = ""
var blackboard: Dictionary = {{}}
var owner: Node2D


func _ready():
    owner = get_parent()
    _tick()


func _tick():
    _execute_tree()


func _execute_tree():
'''
    if tree_type == "Selector":
        code += _generate_selector(actions, conditions)
    else:
        code += _generate_sequence(actions, conditions)

    code += "\n# Acoes\n"
    for action in actions:
        code += _generate_action_stub(action)

    code += "\n# Condicoes\n"
    for condition in conditions:
        code += _generate_condition_stub(condition)

    code += '''
# Blackboard (memoria compartilhada)
func bb_set(key: String, value):
    blackboard[key] = value


func bb_get(key: String, default = null):
    return blackboard.get(key, default)


func bb_has(key: String) -> bool:
    return key in blackboard
'''
    return code


def _generate_selector(actions, conditions):
    code = ""
    for i, (action, condition) in enumerate(zip(actions, conditions)):
        kw = "if" if i == 0 else "elif"
        code += f'    {kw} _check_{condition}():\n'
        code += f'        _execute_{action}()\n'
        code += f'        return\n'
    code += '    else:\n        _execute_idle()\n'
    return code


def _generate_sequence(actions, conditions):
    code = ""
    for action, condition in zip(actions, conditions):
        code += f'    if _check_{condition}():\n'
        code += f'        _execute_{action}()\n'
        code += f'    else:\n        _execute_idle()\n        return\n'
    return code


def _generate_action_stub(action):
    label = action.replace("_", " ").title()
    return f'''
func _execute_{action}():
    """{label} — TODO: implementar"""
    if current_action != "{action}":
        behavior_changed.emit(current_action, "{action}")
        current_action = "{action}"
    pass
'''


def _generate_condition_stub(condition):
    label = condition.replace("_", " ").title()
    return f'''
func _check_{condition}() -> bool:
    """Verifica: {label} — TODO: implementar"""
    return false
'''


# ══════════════════════════════════════════════════════════════
# TOOL 1: behavior_tree_generate
# ══════════════════════════════════════════════════════════════

def behavior_tree_generate(
    description: str,
    behavior_name: str = "EnemyAI",
    tree_type: str = "selector",
    save_path: str | None = None,
) -> dict:
    """Gera Behavior Tree completa em GDScript a partir de descricao.

    Args:
        description: Descricao do comportamento em portugues.
            Ex: "patrulha entre 2 pontos, se detectar jogador persegue,
                 se chegar perto ataca, se vida < 30% foge"
        behavior_name: Nome da classe (ex: "EnemyAI", "BossAI").
        tree_type: "selector" = tenta em ordem, primeira condicao verdadeira.
                   "sequence" = executa em ordem, para na primeira falsa.
        save_path: Caminho para salvar o .gd (auto se None).

    Returns:
        {"status": "success", "saved_to": str, "actions": [...], "lines": int}
    """
    from tools.project_ops import _get_active_project, _check_path_traversal

    proj = _get_active_project()

    if not save_path:
        safe_name = behavior_name.lower().replace(" ", "_")
        save_path = f"scripts/ai/{safe_name}.gd"

    violation = _check_path_traversal(save_path, proj)
    if violation:
        return {"status": "error", "message": violation}

    description_lower = description.lower()

    action_keywords = {
        "patrulha": "patrol", "persegue": "chase", "ataca": "attack",
        "foge": "flee", "guarda": "guard", "alerta": "alert",
        "vagueia": "wander", "espera": "idle", "cura": "heal",
        "protege": "defend", "investiga": "investigate", "retorna": "return_to_post",
        "esquiva": "dodge", "atira": "shoot", "invoca": "summon", "enrage": "enrage",
    }

    condition_keywords = {
        "detectar": "player_detected", "perto": "in_attack_range",
        "vida": "health_low", "saude": "health_low", "hp": "health_low",
        "longe": "player_far", "perdeu": "player_lost",
        "sem_municao": "no_ammo", "sozinho": "alone", "cercado": "surrounded",
        "aliado": "ally_nearby", "perigo": "danger_nearby",
        "barulho": "noise_heard", "cooldown": "ability_ready",
    }

    actions = [v for k, v in action_keywords.items() if k in description_lower]
    conditions = [v for k, v in condition_keywords.items() if k in description_lower]

    if not actions:
        actions = ["idle", "patrol", "chase", "attack"]
    if not conditions:
        conditions = ["player_detected", "in_attack_range", "health_low"]

    while len(conditions) < len(actions):
        conditions.append("always_true")
    while len(actions) < len(conditions):
        actions.append("idle")

    tree_type = tree_type.lower()
    if tree_type not in ["selector", "sequence"]:
        tree_type = "selector"

    code = _generate_bt_gdscript(behavior_name, description, actions, conditions, tree_type.capitalize())

    full_path = proj / save_path
    full_path.parent.mkdir(parents=True, exist_ok=True)
    full_path.write_text(code, encoding="utf-8")

    lines = code.count('\n') + 1
    preview = '\n'.join(code.split('\n')[:30])

    return {
        "status": "success",
        "saved_to": save_path,
        "code_preview": preview,
        "actions": actions,
        "conditions": conditions,
        "lines": lines,
        "tree_type": tree_type,
        "message": f"Behavior Tree: {len(actions)} acoes, {len(conditions)} condicoes, {lines} linhas",
    }


# ══════════════════════════════════════════════════════════════
# TOOL 2: behavior_tree_list_templates
# ══════════════════════════════════════════════════════════════

def behavior_tree_list_templates() -> dict:
    """Lista templates de Behavior Tree disponiveis.

    Returns:
        {"status": "success", "templates": [...], "total": 5}
    """
    templates = []
    for key, bt in _BT_TEMPLATES.items():
        templates.append({
            "name": key,
            "description": bt["description"],
            "tree_type": bt["nodes"][0],
            "actions": len(bt["actions"]),
            "conditions": len(bt["conditions"]),
        })

    return {
        "status": "success",
        "templates": templates,
        "total": len(templates),
        "message": "Use behavior_tree_generate() com um template ou descreva seu proprio comportamento.",
    }


# ── Behavior Discovery (FATIA 2.E) ───────────────────────────────

def discover_behaviors(
    query: str = "",
    category: str = "",
    tag: str = "",
    genre: str = "",
    limit: int = 50,
) -> dict:
    """Descobre e lista behaviors do arsenal disponivel.

    Escaneia behaviors/ e le behavior.json de cada um.
    Suporta filtros por nome (query), tag, categoria (genero) e limite.
    Retorna lista de behaviors com metadados essenciais.
    """
    import json
    import os
    from pathlib import Path

    root = Path(__file__).resolve().parent.parent
    behaviors_dir = root / "behaviors"

    if not behaviors_dir.is_dir():
        return {"status": "error", "message": "Diretorio behaviors/ nao encontrado."}

    results = []
    count = 0

    for entry in sorted(behaviors_dir.iterdir()):
        if not entry.is_dir():
            continue
        json_path = entry / "behavior.json"
        if not json_path.exists():
            continue

        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError):
            continue

        name = data.get("name", entry.name)
        desc = data.get("description_pt", "")[:120]
        tags = data.get("tags", [])
        genres = data.get("genres", [])
        signals = [s["name"] for s in data.get("signals", [])]
        deps = data.get("dependencies", [])
        version = data.get("version", "0.0.0")

        # Filtros
        if query and query.lower() not in name.lower() and query.lower() not in desc.lower():
            continue
        if tag and tag.lower() not in [t.lower() for t in tags]:
            continue
        if category and category.lower() not in [g.lower() for g in genres]:
            continue
        if genre and genre.lower() not in [g.lower() for g in genres]:
            continue

        results.append({
            "name": name,
            "version": version,
            "description": desc,
            "tags": tags,
            "genres": genres,
            "signals": signals,
            "dependencies": deps,
            "path": f"behaviors/{name}/",
        })
        count += 1
        if count >= limit:
            break

    return {
        "status": "success",
        "total": len(results),
        "behaviors": results,
        "filters_applied": {
            "query": query or None,
            "tag": tag or None,
            "category": category or None,
            "genre": genre or None,
        },
        "message": f"{len(results)} behavior(s) encontrado(s). Use 'query' para busca textual, 'tag' ou 'genre' para filtrar.",
    }
