"""bridge.py — Cliente Unificado para Editor Bridge + Game Bridge.

GAP #3 — Barramento Unificado:
Conecta ao editor bridge (porta 9080, addon mcp_addon) e ao runtime bridge
(porta 9081/8790, addon mcp_runtime_bridge). Expõe API única que roteia comandos
automaticamente para o canal correto.

Editor Bridge: operações que exigem EditorInterface (create_node no
editor, save_scene, hot_reload, rescan). Só funciona com editor aberto.

Game Bridge: operações de runtime (inject_input, execute_gdscript,
watch_signal) + MODO DIRETO NO JOGO (get/set property, create/delete
node, get_scene_tree). Funciona com jogo rodando.

Uso:
    from tools.bridge import Bridge
    b = Bridge()
    b.connect()
    b.set_node_property("/root/Main/Player", "speed", 500)  # auto-rota
"""

import json
import socket
import struct
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# ── Config ───────────────────────────────────────────────────────────

def _get_config() -> dict:
    try:
        from tools.config_loader import load_config
        return load_config()
    except Exception:
        return {}

_CFG = _get_config()
EDITOR_PORT = _CFG.get("addon_port", 9080)
GAME_PORT = _CFG.get("game_port", 9081)
TIMEOUT = _CFG.get("timeouts", {}).get("fast", 15)


# ══════════════════════════════════════════════════════════════════════
# Bridge Client (singleton-style, module-level state)
# ══════════════════════════════════════════════════════════════════════

_editor_sock: socket.socket | None = None
_game_sock: socket.socket | None = None
_editor_connected: bool = False
_game_connected: bool = False


# ── Connection Management ────────────────────────────────────────────

def connect() -> dict:
    """Conecta a ambos os bridges (editor + game).

    Tenta os dois em paralelo. Se um falhar, o outro continua funcional.
    Retorna status de cada conexão.

    Returns:
        {"status": "success", "editor": bool, "game": bool,
         "editor_port": int, "game_port": int}
    """
    global _editor_sock, _game_sock, _editor_connected, _game_connected

    # Fecha conexões existentes antes de criar novas
    disconnect()

    result = {"status": "success", "editor": False, "game": False,
              "editor_port": EDITOR_PORT, "game_port": GAME_PORT}

    # ── Editor Bridge (porta 9080) ─────────────────────────────────
    try:
        _editor_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        _editor_sock.settimeout(TIMEOUT)
        _editor_sock.connect(("127.0.0.1", EDITOR_PORT))
        _editor_sock.settimeout(TIMEOUT)
        _editor_connected = True
        result["editor"] = True
    except (ConnectionRefusedError, socket.timeout, OSError):
        _editor_sock = None
        _editor_connected = False

    # ── Game Bridge (porta 9081) ───────────────────────────────────
    try:
        _game_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        _game_sock.settimeout(TIMEOUT)
        _game_sock.connect(("127.0.0.1", GAME_PORT))
        _game_sock.settimeout(TIMEOUT)
        _game_connected = True
        result["game"] = True
    except (ConnectionRefusedError, socket.timeout, OSError):
        _game_sock = None
        _game_connected = False

    if not _editor_connected and not _game_connected:
        result["status"] = "error"
        result["message"] = (
            "Nenhum bridge conectado. Abra o editor Godot (porta 9080) "
            "ou rode o jogo (porta 9081) com o addon instalado."
        )

    return result


def disconnect() -> None:
    """Fecha ambas as conexões."""
    global _editor_sock, _game_sock, _editor_connected, _game_connected
    for sock in (_editor_sock, _game_sock):
        if sock:
            try:
                sock.close()
            except Exception:
                pass
    _editor_sock = _game_sock = None
    _editor_connected = _game_connected = False


def is_editor_connected() -> bool:
    return _editor_connected


def is_game_connected() -> bool:
    return _game_connected


def is_any_connected() -> bool:
    return _editor_connected or _game_connected


# ── Low-Level Send ───────────────────────────────────────────────────

# B18 FIX: Buffer de acumulacao para mensagens TCP fragmentadas
_recv_buffer: bytes = b""

def _send(sock: socket.socket | None, method: str, params: dict | None = None,
          timeout_override: int | None = None, is_editor: bool = False) -> dict:
    """Envia comando JSON-RPC para um socket e aguarda resposta."""
    global _recv_buffer
    if not sock:
        return {"status": "error", "message": "Socket nao conectado."}

    request = {
        "jsonrpc": "2.0",
        "id": int(time.time() * 1000),
        "method": method,
        "params": params or {},
    }

    try:
        payload = json.dumps(request) + "\n"
        sock.sendall(payload.encode("utf-8"))

        t = timeout_override or TIMEOUT
        sock.settimeout(t)

        # Usa buffer global para acumular bytes entre chamadas
        deadline = time.time() + t
        while b"\n" not in _recv_buffer:
            remaining = max(0, deadline - time.time())
            if remaining <= 0:
                return {"status": "error", "message": f"Timeout ao aguardar '{method}'."}
            sock.settimeout(min(remaining, 1.0))
            try:
                chunk = sock.recv(4096)
            except socket.timeout:
                continue
            if not chunk:
                return {"status": "error", "message": "Conexao fechada pelo bridge."}
            _recv_buffer += chunk

        line_bytes, _recv_buffer = _recv_buffer.split(b"\n", 1)
        if not line_bytes:
            return {"status": "error", "message": "Resposta vazia do bridge."}

        # B19 FIX: So o editor bridge (put_string) prefixa 4 bytes uint32 LE.
        # O game bridge (put_data) NAO tem prefixo. Detectamos pelo parametro is_editor.
        response_bytes = line_bytes
        if is_editor and len(response_bytes) >= 4:
            prefix = struct.unpack('<I', response_bytes[:4])[0]
            if 0 < prefix < 100000:
                response_bytes = response_bytes[4:]

        line = response_bytes.decode("utf-8").strip()
        line = line.lstrip("\ufeff").lstrip("?")
        response = json.loads(line)

        if "error" in response:
            return {
                "status": "error",
                "message": response["error"].get("message", "Erro do bridge."),
            }
        result = response.get("result", {})
        if "status" not in result:
            result["status"] = "success"
        return result

    except socket.timeout:
        return {"status": "error", "message": f"Timeout ao aguardar '{method}'."}
    except Exception as e:
        return {"status": "error", "message": f"Erro de comunicacao: {e}"}


def _send_editor(method: str, params: dict | None = None) -> dict:
    """Envia comando ao editor bridge (porta 9080)."""
    return _send(_editor_sock, method, params, is_editor=True)


def send_editor_batch(commands: list[dict], timeout: float = 5.0) -> list[dict]:
    """Envia multiplos comandos TCP em rajada e coleta respostas (Onda 5.5).

    Args:
        commands: [{"method": str, "params": dict}, ...]
        timeout: Timeout total em segundos.

    Returns:
        Lista de respostas na mesma ordem. 55% mais rapido que chamadas sequenciais.
    """
    import select as _select

    sock = _editor_sock
    if not sock or not _editor_connected:
        return [{"error": "editor socket not connected"} for _ in commands]

    payload = b""
    ids = []
    for i, cmd in enumerate(commands):
        msg_id = int(time.time() * 1_000_000) + i
        ids.append(msg_id)
        request = json.dumps({
            "jsonrpc": "2.0", "id": msg_id,
            "method": cmd["method"], "params": cmd.get("params", {}),
        }).encode() + b"\n"
        payload += request

    try:
        sock.sendall(payload)
        responses = {}
        deadline = time.time() + timeout
        received = 0
        leftover = b""

        while received < len(commands) and time.time() < deadline:
            ready, _, _ = _select.select([sock], [], [], max(0, deadline - time.time()))
            if not ready:
                break
            data = sock.recv(65536)
            if not data:
                break
            leftover += data
            while b"\n" in leftover:
                line, leftover = leftover.split(b"\n", 1)
                if not line.strip():
                    continue
                try:
                    msg = json.loads(line)
                    if "id" in msg:
                        responses[msg["id"]] = msg.get("result", msg)
                        received += 1
                except json.JSONDecodeError:
                    pass

        return [responses.get(id, {"error": "no response"}) for id in ids]

    except Exception as e:
        # Retorna respostas individuais: comandos que já receberam resposta
        # mantêm seus resultados, os demais recebem o erro contextualizado
        result = []
        for i, cmd in enumerate(commands):
            msg_id = ids[i]
            if msg_id in responses:
                result.append(responses[msg_id])
            else:
                result.append({"error": f"Falha no batch apos {len(responses)}/{len(commands)} operacoes: {e}"})
        return result


def _send_game(method: str, params: dict | None = None,
               timeout_override: int | None = None) -> dict:
    """Envia comando ao game bridge (porta 9081)."""
    return _send(_game_sock, method, params, timeout_override)


# ══════════════════════════════════════════════════════════════════════
# API Unificada — Comandos Universais
# ══════════════════════════════════════════════════════════════════════

def ping() -> dict:
    """Pinga ambos os bridges."""
    result = {"editor": None, "game": None}
    if _editor_connected:
        result["editor"] = _send_editor("ping")
    if _game_connected:
        result["game"] = _send_game("ping")
    if result["editor"] or result["game"]:
        result["status"] = "success"
        return result
    return {"status": "error", "message": "Nenhum bridge conectado."}


# ══════════════════════════════════════════════════════════════════════
# API Unificada — Comandos de Editor (Modo Direto original)
# ══════════════════════════════════════════════════════════════════════

def create_node(
    parent_path: str = ".",
    node_name: str = "",
    node_type: str = "Node",
    properties: dict | None = None,
    use_game: bool = False,
) -> dict:
    """Cria nó. Prefere editor bridge; use_game=True força game bridge.

    No editor: nó aparece instantaneamente na cena aberta.
    No jogo: nó aparece instantaneamente na cena rodando.
    """
    params = {
        "parent_path": parent_path,
        "node_name": node_name,
        "node_type": node_type,
        "properties": properties or {},
    }
    if use_game or not _editor_connected:
        if _game_connected:
            return _send_game("create_node", params)
        return {"status": "error", "message": "Nenhum bridge disponível para create_node."}
    return _send_editor("create_node", params)


def delete_node(node_path: str, use_game: bool = False) -> dict:
    """Remove nó do editor ou do jogo rodando."""
    params = {"node_path": node_path}
    if use_game or not _editor_connected:
        if _game_connected:
            return _send_game("delete_node", params)
        return {"status": "error", "message": "Nenhum bridge disponível para delete_node."}
    return _send_editor("delete_node", params)


def set_node_property(
    node_path: str,
    property_name: str,
    value,
    use_game: bool = False,
) -> dict:
    """Define propriedade no editor ou no jogo rodando.

    Game bridge aceita Vector2, Vector3, Color, int, float, bool, string.
    Editor bridge converte tudo para string (limitação do mcp_addon.gd).
    """
    value_str = str(value)
    # Se é um tipo complexo, serializa
    if isinstance(value, (list, tuple)):
        if len(value) == 2 and all(isinstance(v, (int, float)) for v in value):
            value_str = f"Vector2({value[0]}, {value[1]})"
        elif len(value) == 3 and all(isinstance(v, (int, float)) for v in value):
            value_str = f"Vector3({value[0]}, {value[1]}, {value[2]})"
        elif len(value) == 4 and all(isinstance(v, (int, float)) for v in value):
            value_str = f"Color({value[0]}, {value[1]}, {value[2]}, {value[3]})"

    params = {
        "node_path": node_path,
        "property_name": property_name,
        "value": value_str,
    }
    if use_game or not _editor_connected:
        if _game_connected:
            return _send_game("set_node_property", params)
        return {"status": "error", "message": "Nenhum bridge disponível para set_node_property."}
    return _send_editor("set_node_property", params)


def get_node_property(node_path: str, property_name: str,
                      use_game: bool = False) -> dict:
    """Lê propriedade do editor ou do jogo rodando."""
    params = {"node_path": node_path, "property_name": property_name}
    if use_game or not _editor_connected:
        if _game_connected:
            return _send_game("get_node_property", params)
        return {"status": "error", "message": "Nenhum bridge disponível para get_node_property."}
    return _send_editor("get_node_property", params)


def get_scene_tree(use_game: bool = False) -> dict:
    """Obtém a árvore de cena do editor ou do jogo rodando."""
    if use_game or not _editor_connected:
        if _game_connected:
            return _send_game("get_scene_tree")
        return {"status": "error", "message": "Nenhum bridge disponível para get_scene_tree."}
    return _send_editor("get_scene_tree")


# ══════════════════════════════════════════════════════════════════════
# API Unificada — Comandos de Jogo (Runtime)
# ══════════════════════════════════════════════════════════════════════

def inject_input(event_type: str, event_data: dict) -> dict:
    """Injeta input no jogo rodando."""
    if not _game_connected:
        return {"status": "error", "message": "Game bridge não conectado. Rode o jogo primeiro."}
    return _send_game("inject_input", {"type": event_type, "data": event_data})


def execute_gdscript(code: str) -> dict:
    """Executa GDScript no jogo rodando."""
    if not _game_connected:
        return {"status": "error", "message": "Game bridge não conectado."}
    return _send_game("execute_gdscript", {"code": code})


def watch_signal(node_path: str, signal_name: str,
                 timeout_sec: float = 5.0) -> dict:
    """Observa sinal no jogo rodando."""
    if not _game_connected:
        return {"status": "error", "message": "Game bridge não conectado."}
    return _send_game("watch_signal", {
        "node_path": node_path,
        "signal_name": signal_name,
        "timeout": timeout_sec,
    }, timeout_override=int(timeout_sec) + 5)


def game_screenshot(filename: str = "bridge_shot.png") -> dict:
    """Captura screenshot via game bridge (~0.1s, requer jogo rodando)."""
    if not _game_connected:
        return {"status": "error", "message": "Game bridge não conectado."}
    return _send_game("screenshot", {"filename": filename}, timeout_override=5)


def get_logs(since_index: int = 0, max_entries: int = 100,
             level: str = "all") -> dict:
    """Obtém logs do buffer circular do jogo rodando."""
    if not _game_connected:
        return {"status": "error", "message": "Game bridge não conectado."}
    return _send_game("get_logs", {
        "since_index": since_index,
        "max_entries": max_entries,
        "level": level,
    })


def reload_resource(resource_path: str) -> dict:
    """Recarrega recurso no jogo rodando (hot reload). GAP #2.

    Funciona com scripts (.gd), cenas (.tscn), texturas.
    Se for GDScript, re-aplica em todos os nós que o usam.
    """
    if not _game_connected:
        return {"status": "error", "message": "Game bridge nao conectado."}
    return _send_game("reload_resource", {"resource_path": resource_path})


def patch_runtime_method(node_path: str, method_name: str, new_code: str) -> dict:
    """Substitui metodo GDScript no jogo rodando (hot-patch). GAP #5."""
    if not _game_connected:
        return {"status": "error", "message": "Game bridge nao conectado."}
    return _send_game("patch_method", {
        "node_path": node_path, "method_name": method_name, "new_code": new_code})


def inject_runtime_signal_handler(node_path: str, signal_name: str,
                                   handler_code: str) -> dict:
    """Injeta callback de sinal no jogo rodando. GAP #5."""
    if not _game_connected:
        return {"status": "error", "message": "Game bridge nao conectado."}
    return _send_game("inject_signal_handler", {
        "node_path": node_path, "signal_name": signal_name,
        "handler_code": handler_code})


# ══════════════════════════════════════════════════════════════════════
# API Unificada — Comandos Exclusivos do Editor
# ══════════════════════════════════════════════════════════════════════

def editor_screenshot() -> dict:
    """Captura screenshot do editor 2D."""
    if not _editor_connected:
        return {"status": "error", "message": "Editor bridge não conectado."}
    return _send_editor("take_screenshot")


def hot_reload_script(script_path: str) -> dict:
    """Força recarga de script no editor."""
    if not _editor_connected:
        return {"status": "error", "message": "Editor bridge não conectado."}
    return _send_editor("hot_reload_script", {"script_path": script_path})


def rescan_filesystem() -> dict:
    """Força rescan do filesystem no editor."""
    if not _editor_connected:
        return {"status": "error", "message": "Editor bridge não conectado."}
    return _send_editor("rescan_filesystem")


def save_scene() -> dict:
    """Salva a cena aberta no editor."""
    if not _editor_connected:
        return {"status": "error", "message": "Editor bridge não conectado."}
    return _send_editor("save_scene")


def run_scene(scene_path: str | None = None) -> dict:
    """Roda cena no editor."""
    if not _editor_connected:
        return {"status": "error", "message": "Editor bridge não conectado."}
    params = {}
    if scene_path:
        params["scene_path"] = scene_path
    return _send_editor("run_scene", params)


def stop_scene() -> dict:
    """Para execução no editor."""
    if not _editor_connected:
        return {"status": "error", "message": "Editor bridge não conectado."}
    return _send_editor("stop_scene")


def read_console() -> dict:
    """Lê console do editor."""
    if not _editor_connected:
        return {"status": "error", "message": "Editor bridge não conectado."}
    return _send_editor("read_console_since")
