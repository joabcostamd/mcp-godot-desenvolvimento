"""vibe_ops.py — Vibe Coding Mode (Fase 2C / B11).

Toggle que filtra contexto automaticamente para a cena ativa.
Inspirado no yurineko73/godot-mcp-native.

Tools:
    - vibe_coding_mode: ativa/desativa modo vibe
    - get_vibe_context: retorna contexto atual da cena
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT / "config.json"


def _load_config() -> dict:
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, encoding="utf-8") as f:
            return json.load(f)
    return {}


def _save_config(config: dict) -> None:
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


def vibe_coding_mode(
    enabled: bool = True,
    scene_path: str | None = None,
    focus_node: str | None = None,
) -> dict:
    """Ativa/desativa o Vibe Coding Mode.

    Quando ativo, a IA foca AUTOMATICAMENTE na cena configurada,
    reduzindo necessidade de especificar scene_path em cada tool.

    Args:
        enabled: True para ativar, False para desativar.
        scene_path: Cena foco (ex: "scenes/main.tscn").
        focus_node: Nó foco dentro da cena (ex: "./Player").

    Returns:
        dict com estado atual do modo.
    """
    config = _load_config()
    vibe = config.get("vibe_coding", {})

    if enabled:
        vibe["enabled"] = True
        if scene_path:
            vibe["scene_path"] = scene_path
        if focus_node:
            vibe["focus_node"] = focus_node
    else:
        vibe["enabled"] = False

    config["vibe_coding"] = vibe
    _save_config(config)

    return {
        "status": "success",
        "vibe_coding": vibe,
        "tip": "Modo vibe ativado! Tools de cena usarão a cena configurada como default." if enabled else "Modo vibe desativado.",
    }


def get_vibe_context() -> dict:
    """Retorna o contexto atual do Vibe Coding Mode.

    Se ativo, retorna scene_path e focus_node configurados.
    Outras tools podem usar isso como default.
    """
    config = _load_config()
    vibe = config.get("vibe_coding", {})

    if not vibe.get("enabled"):
        return {"status": "success", "vibe_coding": {"enabled": False}}

    scene_path = vibe.get("scene_path", "")
    focus_node = vibe.get("focus_node", "")

    context = {"enabled": True, "scene_path": scene_path, "focus_node": focus_node}

    # Se tem cena, carrega árvore
    if scene_path:
        try:
            from tools.scene_ops import load_scene_tree
            tree = load_scene_tree(scene_path)
            if tree.get("status") == "success":
                nodes = tree.get("nodes", [])
                context["total_nodes"] = len(nodes)
                context["root_type"] = nodes[0].get("type", "?") if nodes else "?"
                # Foco no nó
                if focus_node:
                    for n in nodes:
                        if focus_node in n.get("path", "") or focus_node in n.get("name", ""):
                            context["focus"] = {
                                "name": n.get("name"),
                                "type": n.get("type"),
                                "path": n.get("path"),
                            }
                            break
        except Exception:
            pass

    return {"status": "success", "vibe_coding": context}
