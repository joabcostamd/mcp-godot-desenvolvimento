"""resources — MCP Resources (Fase 2A / C2).

Registra 6 URIs godot:// como MCP Resources. Resources NÃO contam
contra o tool cap — são ideais para leituras baratas e frequentes.

URIs registradas:
  godot://editor/state        — Estado atual do editor Godot
  godot://scene/{path}         — Árvore hierárquica da cena (template)
  godot://node/{path}/props    — Propriedades de um nó (template)
  godot://project/settings     — Configurações do projeto
  godot://console/output       — Saída do console do Godot
  godot://screenshot/latest    — Último screenshot capturado

Baseado no padrão hi-godot/godot-ai (src/godot_ai/resources/).
"""

import json
import os
from pathlib import Path
from urllib.parse import unquote

from mcp.types import Resource, ResourceTemplate

# ── MIME Types ──────────────────────────────────────────────────────

MIME_JSON = "application/json"
MIME_TEXT = "text/plain"


# ── Resource Definitions ────────────────────────────────────────────

_FIXED_RESOURCES: list[Resource] = [
    Resource(
        uri="godot://editor/state",
        name="Estado do Editor",
        description=(
            "Estado atual do editor Godot: cena aberta, nós selecionados, "
            "modo de edição. Depende do editor bridge (TCP 9080)."
        ),
        mimeType=MIME_JSON,
    ),
    Resource(
        uri="godot://project/settings",
        name="Configurações do Projeto",
        description=(
            "Configurações do project.godot do projeto ativo. "
            "Funciona offline (file-based)."
        ),
        mimeType=MIME_JSON,
    ),
    Resource(
        uri="godot://console/output",
        name="Saída do Console",
        description=(
            "Últimas linhas da saída do console do Godot (editor ou jogo). "
            "Depende do editor bridge (TCP 9080) ou game bridge (TCP 9081)."
        ),
        mimeType=MIME_TEXT,
    ),
    Resource(
        uri="godot://screenshot/latest",
        name="Último Screenshot",
        description=(
            "Caminho e metadados do último screenshot capturado "
            "(editor ou jogo). O conteúdo binário da imagem NÃO é "
            "retornado — use take_screenshot para obter a imagem."
        ),
        mimeType=MIME_JSON,
    ),
]

_TEMPLATE_RESOURCES: list[ResourceTemplate] = [
    ResourceTemplate(
        uriTemplate="godot://scene/{path}",
        name="Árvore da Cena",
        description=(
            "Árvore hierárquica de nós da cena especificada por {path}. "
            "Ex: godot://scene/scenes/main.tscn. "
            "Funciona offline (file-based)."
        ),
        mimeType=MIME_JSON,
    ),
    ResourceTemplate(
        uriTemplate="godot://node/{path}/props",
        name="Propriedades do Nó",
        description=(
            "Propriedades de um nó específico. {path} no formato: "
            "cena.tscn::caminho/do/nó. "
            "Ex: godot://node/scenes/main.tscn::Player/props."
        ),
        mimeType=MIME_JSON,
    ),
]

# Lista combinada para serialização e busca
_ALL_URIS: list[str] = [
    str(r.uri) for r in _FIXED_RESOURCES
] + [
    str(rt.uriTemplate) for rt in _TEMPLATE_RESOURCES
]


# ── Resource Listing ────────────────────────────────────────────────

def get_resources() -> list[Resource | ResourceTemplate]:
    """Retorna a lista combinada de Resources e ResourceTemplates.

    Chamado por @server.list_resources().
    """
    return list(_FIXED_RESOURCES) + list(_TEMPLATE_RESOURCES)


# ── Resource Reading ────────────────────────────────────────────────

def read_resource(uri: str) -> str:
    """Lê o conteúdo de um resource godot://.

    Args:
        uri: URI do resource (ex: godot://project/settings).

    Returns:
        String JSON ou texto com o conteúdo do resource.
    """
    # ── Roteamento por prefixo ─────────────────────────────────
    if uri == "godot://editor/state":
        return _read_editor_state()

    if uri.startswith("godot://scene/"):
        scene_path = _extract_param(uri, prefix="godot://scene/")
        return _read_scene_tree(scene_path)

    if uri.startswith("godot://node/") and uri.endswith("/props"):
        # Formato: godot://node/{scene}::{node_path}/props
        inner = uri[len("godot://node/"):-len("/props")]
        return _read_node_props(inner)

    if uri == "godot://project/settings":
        return _read_project_settings()

    if uri == "godot://console/output":
        return _read_console_output()

    if uri == "godot://screenshot/latest":
        return _read_screenshot_info()

    return json.dumps({
        "status": "error",
        "message": f"Resource desconhecido: {uri}",
        "valid_uris": _ALL_URIS,
    })


# ── Helpers ─────────────────────────────────────────────────────────

def _extract_param(uri: str, prefix: str) -> str:
    """Extrai parâmetro de path de uma URI template."""
    return unquote(uri[len(prefix):])


# ── Resource Handlers ───────────────────────────────────────────────

def _read_editor_state() -> str:
    """godot://editor/state — Estado do editor."""
    try:
        from tools.editor_bridge import get_scene_tree_in_editor, get_selection
        tree = get_scene_tree_in_editor()
        selection = get_selection() if hasattr(
            __import__("tools.editor_bridge", fromlist=["get_selection"]),
            "get_selection"
        ) else None
        return json.dumps({
            "status": "success",
            "scene": tree.get("scene", "") if isinstance(tree, dict) else str(tree),
            "selection": selection,
            "bridge": "connected",
        })
    except Exception:
        return json.dumps({
            "status": "unavailable",
            "message": "Editor bridge não conectado. Abra o Godot e inicie o editor bridge na porta 9080.",
            "bridge": "disconnected",
        })


def _read_scene_tree(scene_path: str) -> str:
    """godot://scene/{path} — Árvore da cena."""
    try:
        from tools.scene_ops import load_scene_tree
        result = load_scene_tree(scene_path=scene_path)
        return json.dumps(result)
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"Erro ao ler cena '{scene_path}': {e}",
            "scene_path": scene_path,
        })


def _read_node_props(inner: str) -> str:
    """godot://node/{scene}::{node_path}/props — Propriedades do nó."""
    try:
        parts = inner.split("::", 1)
        if len(parts) != 2:
            return json.dumps({
                "status": "error",
                "message": (
                    f"Formato inválido: '{inner}'. "
                    f"Use: cena.tscn::caminho/do/nó"
                ),
            })
        scene_path, node_path = parts
        from tools.scene_ops import get_node_property
        # Tenta ler propriedades comuns
        props = {}
        for prop in ["position", "rotation", "scale", "visible", "name", "type"]:
            try:
                r = get_node_property(scene_path, node_path, prop)
                if r.get("status") == "success":
                    props[prop] = r.get("value")
            except Exception:
                pass
        return json.dumps({
            "status": "success" if props else "partial",
            "scene": scene_path,
            "node": node_path,
            "properties": props,
        })
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"Erro ao ler propriedades: {e}",
        })


def _read_project_settings() -> str:
    """godot://project/settings — Configurações do projeto."""
    try:
        from tools.project_ops import get_project_settings
        result = get_project_settings(section=None)
        return json.dumps(result)
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"Erro ao ler configurações: {e}. Projeto ativo definido?",
        })


def _read_console_output() -> str:
    """godot://console/output — Saída do console."""
    try:
        from tools.runtime_ops import read_console_output
        result = read_console_output(lines=50)
        return json.dumps(result)
    except Exception:
        return json.dumps({
            "status": "unavailable",
            "message": "Console não disponível. O Godot precisa estar rodando (editor ou jogo).",
        })


def _read_screenshot_info() -> str:
    """godot://screenshot/latest — Info do último screenshot."""
    temp_dir = Path(__file__).resolve().parent.parent / "temp_art"
    screenshots = sorted(
        temp_dir.glob("screenshot_*.png"),
        key=os.path.getmtime,
        reverse=True,
    )
    if screenshots:
        latest = screenshots[0]
        return json.dumps({
            "status": "success",
            "path": str(latest),
            "size_bytes": latest.stat().st_size,
            "timestamp": latest.stat().st_mtime,
        })
    return json.dumps({
        "status": "empty",
        "message": "Nenhum screenshot encontrado. Use take_screenshot primeiro.",
    })
