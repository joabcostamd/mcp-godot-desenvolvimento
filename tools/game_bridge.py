"""game_bridge — Cliente TCP para comunicação com o jogo em execução.

Conecta ao mcp_runtime_bridge (autoload, runtime_bridge.gd) via TCP localhost:9081/8790.
Protocolo: JSON-RPC 2.0 line-delimited.
Usado por inject_input_event, execute_gdscript_runtime, watch_signal.
"""

import json
import socket
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# ── Estado ──────────────────────────────────────────────────────────

_socket = None
_connected: bool = False
PORT: int = 9081


def _get_port() -> int:
    """Lê a porta do game bridge da configuração."""
    try:
        from tools.config_loader import load_config
        return load_config().get("game_port", 9081)
    except Exception:
        return 9081


def _get_timeout() -> int:
    try:
        from tools.config_loader import load_config
        return load_config().get("timeouts", {}).get("fast", 15)
    except Exception:
        return 15


# ── Conexão ─────────────────────────────────────────────────────────

def connect(port: int | None = None, retries: int = 5, backoff: float = 1.0) -> dict:
    """Conecta ao game bridge com retry e backoff exponencial.

    OPT1: Em vez de falhar imediatamente, tenta até 'retries' vezes
    com delay crescente. Essencial porque o jogo demora ~3s para iniciar
    o TCP server após o processo Godot abrir.

    Args:
        port: Porta do game bridge (default: config.json game_port).
        retries: Número máximo de tentativas (default 5).
        backoff: Delay inicial entre tentativas em segundos (dobra a cada tentativa).
    """
    global _socket, _connected
    if _connected and _socket:
        # Verifica se a conexao ainda esta viva
        try:
            _socket.settimeout(0.5)
            _socket.sendall(b"")
            return {"status": "success", "note": "Ja conectado ao game bridge."}
        except Exception:
            # Conexao morreu, reconecta
            _connected = False
            _socket = None

    port = port or _get_port()
    timeout = _get_timeout()
    last_error = ""

    for attempt in range(1, retries + 1):
        try:
            _socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            _socket.settimeout(timeout)
            _socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            _socket.connect(("127.0.0.1", port))
            _socket.settimeout(timeout)
            _connected = True
            return {"status": "success", "port": port, "attempts": attempt}
        except (ConnectionRefusedError, socket.timeout, OSError) as e:
            _socket = None
            _connected = False
            last_error = str(e)
            if attempt < retries:
                delay = backoff * (2 ** (attempt - 1))
                time.sleep(delay)

    return {
        "status": "error",
        "message": (
            f"Nao foi possivel conectar ao jogo na porta {port} apos {retries} tentativas: {last_error}. "
            f"O jogo esta rodando com o autoload GameBridge instalado? "
            f"Use smart_restart() para reiniciar tudo automaticamente."
        ),
    }


def ensure_connected(port: int | None = None) -> dict:
    """OPT3: Garante conexao ativa, reconectando se necessario.

    Use antes de qualquer chamada execute_gdscript ou inject_input.
    Mais leve que connect() — so tenta reconectar se nao estiver conectado.
    """
    global _connected, _socket
    if _connected and _socket:
        try:
            _socket.settimeout(0.5)
            _socket.sendall(b"")
            return {"status": "success", "note": "Conectado."}
        except Exception:
            _connected = False
            _socket = None
    return connect(port, retries=3, backoff=0.5)


def disconnect() -> None:
    global _socket, _connected
    if _socket:
        try:
            _socket.close()
        except Exception:
            pass
    _socket = None
    _connected = False


def is_connected() -> bool:
    return _connected


# ── Comandos ────────────────────────────────────────────────────────

def _send(method: str, params: dict | None = None, timeout_override: int | None = None) -> dict:
    global _socket
    if not _connected or not _socket:
        return {"status": "error", "message": "Não conectado ao game bridge."}

    request = {
        "jsonrpc": "2.0",
        "id": int(time.time() * 1000),
        "method": method,
        "params": params or {},
    }

    try:
        payload = json.dumps(request) + "\n"
        _socket.sendall(payload.encode("utf-8"))

        t = timeout_override or _get_timeout()
        _socket.settimeout(t)

        response_data = b""
        while True:
            chunk = _socket.recv(4096)
            if not chunk:
                break
            response_data += chunk
            if b"\n" in response_data:
                break

        if not response_data:
            return {"status": "error", "message": "Conexão fechada pelo jogo."}

        line = response_data.decode("utf-8").split("\n")[0]
        # Godot JSON.stringify may prepend BOM (U+FEFF) - strip it
        line = line.lstrip("\ufeff").lstrip("?")
        response = json.loads(line)

        if "error" in response:
            return {
                "status": "error",
                "message": response["error"].get("message", "Erro do game bridge."),
            }
        result = response.get("result", {})
        result["status"] = "success"
        return result

    except socket.timeout:
        return {"status": "error", "message": f"Timeout ao aguardar resposta do jogo para '{method}'."}
    except Exception as e:
        return {"status": "error", "message": f"Erro de comunicação: {e}"}


def ping() -> dict:
    return _send("ping")


def inject_input(event_type: str, event_data: dict) -> dict:
    return _send("inject_input", {"type": event_type, "data": event_data})


def execute_gdscript(code: str) -> dict:
    return _send("execute_gdscript", {"code": code})


def watch_signal(node_path: str, signal_name: str, timeout_sec: float = 5.0) -> dict:
    return _send("watch_signal", {
        "node_path": node_path,
        "signal_name": signal_name,
        "timeout": timeout_sec,
    }, timeout_override=int(timeout_sec) + 5)


def gb_screenshot(filename: str = "bridge_shot.png") -> dict:
    """Captura screenshot via game bridge (modo persistente, ~0.1s)."""
    return _send("screenshot", {"filename": filename}, timeout_override=5)
