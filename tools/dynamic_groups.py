"""dynamic_groups.py — Dynamic Tool Groups (Fase 3 / GoPeak).

Grupos dinâmicos de tools: catalog, groups, ativação sob demanda.
Inspirado no HaD0Yun/GoPeak (tool.catalog, tool.groups).

Tools:
    - tool_catalog: busca e lista tools por grupo
    - tool_groups: ativa/desativa grupos de tools
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GROUPS_FILE = ROOT / ".tool_groups.json"

GROUPS = {
    "core": ["ping","health_check","bootstrap_godot_mcp","read_file","write_file"],
    "scene": ["scene_manage","node_manage","batch_atomic_edit","add_nodes_batch"],
    "script": ["script_manage","safe_write_gdscript","gdscript_diagnostics"],
    "runtime": ["runtime_manage","freeze_game_clock","get_runtime_state_digest"],
    "lsp": ["gdscript_lsp_connect","gdscript_references","gdscript_definition"],
    "dap": ["debugger_set_breakpoint","debugger_status"],
    "art": ["generate_game_art","apply_game_art","create_parallax_background"],
    "audio": ["audio_manage","generate_audio_sfx"],
    "networking": ["game_http_request","game_multiplayer"],
    "testing": ["run_gut_tests","assert_node_exists","simulate_input_sequence"],
    "assets": ["download_asset","import_downloaded_asset","asset_manage"],
    "security": ["set_safety_policy","configure_security"],
    "refs_ops": [
        "find_missing_references", "search_codebase",
        "validate_project_refs", "find_usages",
    ],
}


def tool_catalog(query: str = "", group: str = "", limit: int = 20) -> dict:
    """Busca tools no catálogo por nome ou grupo.

    Args:
        query: Texto para buscar no nome da tool.
        group: Filtrar por grupo (core, scene, runtime, lsp, etc.).
        limit: Máximo de resultados.

    Returns:
        dict com tools encontradas e grupos disponíveis.
    """
    from server import _tool_defs
    tools = _tool_defs()

    results = []
    for t in tools:
        name = t.name
        desc = (t.description or "")[:100]

        # Filtro por query
        if query and query.lower() not in name.lower() and query.lower() not in desc.lower():
            continue

        # Filtro por grupo
        if group:
            found = False
            for gname, gtools in GROUPS.items():
                if (gname == group or group in gname) and name in gtools:
                    found = True
                    break
            if not found:
                continue

        results.append({
            "name": name,
            "description": desc,
            "groups": [g for g, gt in GROUPS.items() if name in gt],
        })

        if len(results) >= limit:
            break

    return {
        "status": "success",
        "query": query,
        "group": group,
        "results": results,
        "total": len(results),
        "available_groups": list(GROUPS.keys()),
    }


def tool_groups(action: str = "list", group: str = "", enabled: bool = True) -> dict:
    """Gerencia grupos de tools dinâmicos.

    Args:
        action: "list", "activate", "deactivate", "status".
        group: Nome do grupo.
        enabled: Estado de ativação.

    Returns:
        dict com estado dos grupos.
    """
    config = {}
    if GROUPS_FILE.exists():
        with open(GROUPS_FILE, encoding="utf-8") as f:
            config = json.load(f)

    groups_state = config.get("groups", {})

    if action == "list":
        return {
            "status": "success",
            "available_groups": list(GROUPS.keys()),
            "active_groups": [g for g, v in groups_state.items() if v],
            "groups_detail": {g: {"active": groups_state.get(g, True), "tools": GROUPS.get(g, [])} for g in GROUPS},
        }

    elif action in ("activate", "deactivate"):
        if group not in GROUPS:
            return {"status": "error", "message": f"Grupo '{group}' não existe. Disponíveis: {list(GROUPS.keys())}"}

        groups_state[group] = (action == "activate")
        config["groups"] = groups_state
        with open(GROUPS_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)

        return {
            "status": "success",
            "action": action,
            "group": group,
            "tools_affected": len(GROUPS[group]),
            "active_groups": [g for g, v in groups_state.items() if v],
        }

    return {"status": "error", "message": f"Ação desconhecida: {action}"}
