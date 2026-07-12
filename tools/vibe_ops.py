"""vibe_ops.py — Vibe Coding Mode (Fase 2C / B11).

Toggle que filtra contexto automaticamente para a cena ativa.
Inspirado no yurineko73/godot-mcp-native.

Persistencia: por projeto (.mcp_vibe_state.json no root do projeto ativo).
NAO usa config.local.json para vibe — aquilo e config de MAQUINA.

Tools:
    - vibe_coding_mode: ativa/desativa modo vibe
    - get_vibe_context: retorna contexto atual da cena
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


# ===================================================================
# Config de MAQUINA (paths do Godot, etc.) — SO para isso.
# vibe NAO usa mais este path. Mantido para nao quebrar outros
# modulos que importam _load_config daqui.
# ===================================================================

def _load_config() -> dict:
    """Carrega config de MAQUINA (config.local.json ou config.json)."""
    try:
        from tools.config_loader import load_config
        return load_config()
    except Exception:
        return {}


def _save_config(config: dict) -> None:
    """Salva config de MAQUINA com lock anti-condicao de corrida."""
    from tools.config_loader import ROOT as CONFIG_ROOT
    from tools.config_lock import CONFIG_FILE_LOCK

    config_path = CONFIG_ROOT / "config.local.json"
    if not config_path.exists():
        config_path = CONFIG_ROOT / "config.json"

    with CONFIG_FILE_LOCK:
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)


# ===================================================================
# Vibe State — persistencia POR PROJETO (.mcp_vibe_state.json)
# ===================================================================

def _get_vibe_state_path() -> Path | None:
    """Retorna o caminho do arquivo de estado vibe do projeto ativo."""
    try:
        from tools.project_ops import _get_active_project
        proj = _get_active_project()
        if proj and proj.exists():
            return proj / ".mcp_vibe_state.json"
    except Exception:
        pass
    return None


def _load_vibe_state() -> dict:
    """Carrega o estado vibe do projeto ativo. Retorna dict vazio se nao existir."""
    state_path = _get_vibe_state_path()
    if not state_path or not state_path.exists():
        return {}
    try:
        with open(state_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def _save_vibe_state(state: dict) -> None:
    """Salva o estado vibe no projeto ativo.

    ATENCAO: quem chama deve segurar VIBE_STATE_LOCK (via vibe_coding_mode).
    Esta funcao NAO adquire o lock internamente para evitar deadlock.
    """
    state_path = _get_vibe_state_path()
    if not state_path:
        return
    state_path.parent.mkdir(parents=True, exist_ok=True)
    with open(state_path, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


# ===================================================================
# API Publica
# ===================================================================

def vibe_coding_mode(
    enabled: bool = True,
    scene_path: str | None = None,
    focus_node: str | None = None,
) -> dict:
    """Ativa/desativa o Vibe Coding Mode.

    Quando ativo, a IA foca AUTOMATICAMENTE na cena configurada,
    reduzindo necessidade de especificar scene_path em cada tool.

    Persistencia: estado salvo em <projeto>/.mcp_vibe_state.json
    (UM arquivo por projeto — nao contamina config global do MCP).

    Args:
        enabled: True para ativar, False para desativar.
        scene_path: Cena foco (ex: "scenes/main.tscn").
                    Obrigatorio na primeira ativacao. Validado contra o disco.
        focus_node: No foco dentro da cena (ex: "./Player").

    Returns:
        dict com estado atual do modo.
    """
    from tools.config_lock import VIBE_STATE_LOCK

    with VIBE_STATE_LOCK:
        vibe = _load_vibe_state()

        if enabled:
            # —— Validacao de scene_path (Parte C) ——
            if scene_path:
                # Scene_path NOVO informado → validar existencia
                try:
                    from tools.project_ops import _get_active_project
                    proj = _get_active_project()
                    if proj and not (proj / scene_path).exists():
                        return {
                            "status": "error",
                            "message": (
                                f"Cena '{scene_path}' nao encontrada no projeto. "
                                f"Verifique o caminho antes de ativar o Vibe Coding Mode."
                            ),
                        }
                except Exception:
                    # Se nao conseguir validar, prossegue (modo leniente)
                    pass
                vibe["scene_path"] = scene_path
            elif not vibe.get("scene_path"):
                # Nem informado agora, nem salvo antes → erro
                return {
                    "status": "error",
                    "message": (
                        "scene_path e obrigatorio para ativar o Vibe Coding Mode. "
                        "Informe scene_path='scenes/sua_cena.tscn'."
                    ),
                }

            vibe["enabled"] = True
            if focus_node:
                vibe["focus_node"] = focus_node
        else:
            # —— Desativacao limpa (Parte D) ——
            vibe["enabled"] = False
            vibe["scene_path"] = None
            vibe["focus_node"] = None

        _save_vibe_state(vibe)

    return {
        "status": "success",
        "vibe_coding": vibe,
        "tip": (
            "Modo vibe ativado! Tools de cena usarao a cena configurada como default."
            if enabled
            else "Modo vibe desativado. scene_path e focus_node foram limpos."
        ),
    }


def get_vibe_context() -> dict:
    """Retorna o contexto atual do Vibe Coding Mode.

    Se ativo, retorna scene_path e focus_node configurados.
    Outras tools podem usar isso como default.

    Le do arquivo .mcp_vibe_state.json do projeto ativo.
    Usa VIBE_STATE_LOCK para evitar leitura parcial durante escrita concorrente.
    """
    from tools.config_lock import VIBE_STATE_LOCK

    with VIBE_STATE_LOCK:
        vibe = _load_vibe_state()

        if not vibe.get("enabled"):
            return {"status": "success", "vibe_coding": {"enabled": False}}

        scene_path = vibe.get("scene_path", "")
        focus_node = vibe.get("focus_node", "")

        context = {"enabled": True, "scene_path": scene_path, "focus_node": focus_node}

        # Se tem cena, carrega arvore
        if scene_path:
            try:
                from tools.scene_ops import load_scene_tree
                tree = load_scene_tree(scene_path)
                if tree.get("status") == "success":
                    nodes = tree.get("nodes", [])
                    context["total_nodes"] = len(nodes)
                    context["root_type"] = nodes[0].get("type", "?") if nodes else "?"
                    # Foco no no
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
