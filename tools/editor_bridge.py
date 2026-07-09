"""editor_bridge — Cliente TCP para comunicação com addon in-editor.

Fase 3+: conecta ao addon mcp_bridge no Godot Editor via TCP localhost.
Protocolo: JSON-RPC 2.0 sobre TCP, um JSON por linha (line-delimited).
Nota: Godot 4 put_string() prefixa 4 bytes (uint32 LE length) — removemos ao ler.
"""

import json
import socket
import struct
import time
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parent.parent

# ── Estado ──────────────────────────────────────────────────────────

_editor_process = None
_socket: Optional[socket.socket] = None
_connected: bool = False


def _get_port() -> int:
    """Lê a porta do addon do config.json."""
    cfg_path = ROOT / "config.json"
    if cfg_path.exists():
        with open(cfg_path, encoding="utf-8") as f:
            return json.load(f).get("addon_port", 9080)
    return 9080


def _get_timeout() -> int:
    """Lê timeout fast do config.json."""
    cfg_path = ROOT / "config.json"
    if cfg_path.exists():
        with open(cfg_path, encoding="utf-8") as f:
            return json.load(f).get("timeouts", {}).get("fast", 15)
    return 15


# ── Conexão ─────────────────────────────────────────────────────────

def connect(port: int | None = None) -> dict:
    """Conecta ao addon TCP no editor.

    Returns:
        {"status": "success"} ou {"status": "error", "message": str}
    """
    global _socket, _connected

    if _connected and _socket:
        return {"status": "success", "note": "Já conectado."}

    port = port or _get_port()
    timeout = _get_timeout()

    try:
        _socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        _socket.settimeout(timeout)
        _socket.connect(("127.0.0.1", port))
        _socket.settimeout(timeout)
        _connected = True
        return {"status": "success", "port": port}
    except (ConnectionRefusedError, socket.timeout, OSError) as e:
        _socket = None
        _connected = False
        return {
            "status": "error",
            "message": f"Não foi possível conectar ao editor na porta {port}: {e}. "
                       f"O editor está aberto com o addon mcp_bridge habilitado?",
        }


def disconnect() -> None:
    """Fecha a conexão TCP."""
    global _socket, _connected
    if _socket:
        try:
            _socket.close()
        except Exception:
            pass
    _socket = None
    _connected = False


def is_connected() -> bool:
    """Verifica se está conectado ao addon."""
    return _connected


# ── Comandos ────────────────────────────────────────────────────────

def _send_command(method: str, params: dict | None = None) -> dict:
    """Envia um comando JSON-RPC e aguarda resposta.

    Returns:
        dict com o resultado ou {"status": "error", "message": str}
    """
    global _socket

    if not _connected or not _socket:
        return {"status": "error", "message": "Não conectado ao editor. Use connect() primeiro."}

    request = {
        "jsonrpc": "2.0",
        "id": int(time.time() * 1000),
        "method": method,
        "params": params or {},
    }

    try:
        payload = json.dumps(request) + "\n"
        _socket.sendall(payload.encode("utf-8"))

        # Lê resposta (line-delimited)
        response_data = b""
        _socket.settimeout(_get_timeout())
        while True:
            chunk = _socket.recv(4096)
            if not chunk:
                break
            response_data += chunk
            if b"\n" in response_data:
                break

        if not response_data:
            return {"status": "error", "message": "Conexão fechada pelo editor."}

        # Godot 4 put_string() prefixa 4 bytes (uint32 LE) com o tamanho
        # Ex: b'E\x00\x00\x00{"jsonrpc":"2.0",...}' → strip 4 bytes
        if len(response_data) >= 4:
            prefix = struct.unpack('<I', response_data[:4])[0]
            if 0 < prefix < 100000:  # sanity check
                response_data = response_data[4:]

        # Pega primeira linha JSON
        line = response_data.decode("utf-8").split("\n")[0]
        response = json.loads(line)

        if "error" in response:
            return {
                "status": "error",
                "message": response["error"].get("message", "Erro desconhecido do editor."),
            }
        return response.get("result", {"status": "success"})

    except socket.timeout:
        return {"status": "error", "message": f"Timeout ao aguardar resposta do editor para '{method}'."}
    except Exception as e:
        return {"status": "error", "message": f"Erro de comunicação com editor: {e}"}


def ping() -> dict:
    """Verifica se o addon está respondendo."""
    return _send_command("ping")


def get_editor_state() -> dict:
    """Obtém estado atual do editor."""
    return _send_command("get_editor_state")


def take_screenshot() -> dict:
    """Captura screenshot do editor 2D.

    Returns:
        {"status": "success", "image_path": str, "image_base64": str}
    """
    return _send_command("take_screenshot")


def run_scene(scene_path: str | None = None) -> dict:
    """Roda a cena atual ou uma específica no editor."""
    params = {}
    if scene_path:
        params["scene_path"] = scene_path
    return _send_command("run_scene", params)


def stop_scene() -> dict:
    """Para a execução da cena no editor."""
    return _send_command("stop_scene")


def open_scene_in_editor(scene_path: str) -> dict:
    """Abre uma cena no editor. GAP #12 — Multi-Cena."""
    return _send_command("open_scene", {"scene_path": scene_path})


def read_console_since(since_timestamp: float | None = None) -> dict:
    """Lê linhas do console desde um timestamp."""
    params = {}
    if since_timestamp is not None:
        params["since_timestamp"] = since_timestamp
    return _send_command("read_console_since", params)


def hot_reload_script(script_path: str) -> dict:
    """Força recarga de um script no editor."""
    return _send_command("hot_reload_script", {"script_path": script_path})


def rescan_filesystem() -> dict:
    """Força rescan do sistema de arquivos e recarrega cena aberta."""
    return _send_command("rescan_filesystem")


# ── MODO DIRETO: manipulação em tempo real ──────────────────────────

def create_node_in_editor(
    parent_path: str = ".",
    node_name: str = "",
    node_type: str = "Node",
    properties: dict | None = None,
) -> dict:
    """Cria um nó DIRETAMENTE na cena aberta do editor (tempo real).

    Muito mais rápido que editar .tscn no disco. O nó aparece
    instantaneamente no editor.

    Args:
        parent_path: Path do nó pai ("." = raiz).
        node_name: Nome do novo nó.
        node_type: Tipo Godot (ex: "Sprite2D", "CollisionShape2D").
        properties: Dicionário de propriedades iniciais.
    """
    params = {
        "parent_path": parent_path,
        "node_name": node_name,
        "node_type": node_type,
        "properties": properties or {},
    }
    return _send_command("create_node", params)


def delete_node_in_editor(node_path: str) -> dict:
    """Remove um nó DIRETAMENTE da cena aberta do editor."""
    return _send_command("delete_node", {"node_path": node_path})


def set_node_property_in_editor(
    node_path: str, property_name: str, value
) -> dict:
    """Define propriedade de um nó em tempo real no editor."""
    return _send_command("set_node_property", {
        "node_path": node_path,
        "property_name": property_name,
        "value": str(value),
    })


def get_node_property_in_editor(node_path: str, property_name: str) -> dict:
    """Lê propriedade de um nó no editor."""
    return _send_command("get_node_property", {
        "node_path": node_path,
        "property_name": property_name,
    })


def save_scene_in_editor() -> dict:
    """Salva a cena atualmente aberta no editor."""
    return _send_command("save_scene")


def get_scene_tree_in_editor() -> dict:
    """Retorna a árvore de nós da cena aberta no editor."""
    return _send_command("get_scene_tree")