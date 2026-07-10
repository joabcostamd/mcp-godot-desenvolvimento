"""debugger_ops.py — DAP Debugger Bridge (Fase 2C / B5).

Conecta ao debugger do Godot e expõe breakpoints, step, continue,
stack trace e inspeção de variáveis. Inspirado no Gear (wvfp).

Protocolo: Godot Debugger Protocol sobre TCP (porta 6006).
Fallback: execução GDScript em runtime via GameBridge.

Tools:
    - debugger_set_breakpoint: define breakpoint em script
    - debugger_continue: continua execução
    - debugger_step: avança uma linha
    - debugger_get_stack: obtém stack trace
    - debugger_get_variables: inspeciona variáveis
"""

import json
import socket
import struct
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEBUGGER_PORT = 6006
DEBUGGER_HOST = "127.0.0.1"

# Conexão persistente (P1-4)
_debugger_socket: socket.socket | None = None
_debugger_lock = threading.Lock()


# ── Conexão Debugger ────────────────────────────────────────────────

def _is_debugger_available() -> bool:
    """Verifica se o debugger do Godot está respondendo."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1.0)
        result = sock.connect_ex((DEBUGGER_HOST, DEBUGGER_PORT))
        sock.close()
        return result == 0
    except Exception:
        return False


def _get_debugger_socket(timeout: float = 5.0) -> socket.socket:
    """Retorna socket persistente, reconectando se necessário (P1-4)."""
    global _debugger_socket
    with _debugger_lock:
        if _debugger_socket is not None:
            try:
                # Testa se ainda está vivo
                _debugger_socket.settimeout(0.1)
                _debugger_socket.recv(1, socket.MSG_PEEK)
            except (ConnectionResetError, BrokenPipeError, OSError, socket.timeout):
                try:
                    _debugger_socket.close()
                except OSError:
                    pass
                _debugger_socket = None

        if _debugger_socket is None:
            _debugger_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            _debugger_socket.settimeout(timeout)
            _debugger_socket.connect((DEBUGGER_HOST, DEBUGGER_PORT))

        _debugger_socket.settimeout(timeout)
        return _debugger_socket


def _send_debugger_command(command: dict, timeout: float = 5.0) -> dict:
    """Envia comando para o debugger do Godot usando socket persistente (P1-4).

    O protocolo usa framing: 4 bytes (uint32) tamanho + payload JSON.
    """
    try:
        sock = _get_debugger_socket(timeout)

        payload = json.dumps(command).encode("utf-8")
        frame = struct.pack("<I", len(payload)) + payload
        sock.sendall(frame)

        # Lê resposta
        size_data = sock.recv(4)
        if len(size_data) < 4:
            return {"status": "error", "message": "Resposta incompleta"}

        size = struct.unpack("<I", size_data)[0]
        response_data = b""
        while len(response_data) < size:
            chunk = sock.recv(min(size - len(response_data), 4096))
            if not chunk:
                break
            response_data += chunk

        if response_data:
            return json.loads(response_data.decode("utf-8"))
        return {"status": "error", "message": "Sem resposta do debugger"}

    except ConnectionRefusedError:
        _close_debugger_socket()
        return {"status": "error", "message": "Debugger não está rodando. Inicie o jogo com --debug."}
    except (ConnectionResetError, BrokenPipeError, OSError):
        _close_debugger_socket()
        return {"status": "error", "message": "Conexão com debugger perdida. Reconecte."}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def _close_debugger_socket():
    """Fecha o socket persistente (chamado em caso de erro)."""
    global _debugger_socket
    with _debugger_lock:
        if _debugger_socket is not None:
            try:
                _debugger_socket.close()
            except OSError:
                pass
            _debugger_socket = None


# ── Ferramentas ─────────────────────────────────────────────────────

def debugger_set_breakpoint(
    script_path: str,
    line: int,
    condition: str | None = None,
) -> dict:
    """Define um breakpoint em um script.

    Args:
        script_path: Caminho do script (ex: "res://scripts/player.gd").
        line: Número da linha.
        condition: Condição opcional (ex: "health < 10").

    Returns:
        dict com resultado.
    """
    if not _is_debugger_available():
        return {
            "status": "error",
            "message": "Debugger não disponível. Rode o jogo com F5 (Play Debug) ou --debug.",
            "fallback": "Use execute_gdscript_runtime para inspecionar variáveis em runtime.",
        }

    command = {
        "method": "set_breakpoint",
        "params": {
            "script": script_path,
            "line": line,
            "condition": condition,
        },
    }

    result = _send_debugger_command(command)
    result["note"] = "Debugger conectado via porta 6006"
    return result


def debugger_continue() -> dict:
    """Continua execução após breakpoint."""
    if not _is_debugger_available():
        return {"status": "error", "message": "Debugger não disponível"}

    return _send_debugger_command({"method": "continue"})


def debugger_step(step_type: str = "over") -> dict:
    """Avança uma linha/stap.

    Args:
        step_type: "over" (próxima linha), "into" (entrar na função),
                   "out" (sair da função).
    """
    if not _is_debugger_available():
        return {"status": "error", "message": "Debugger não disponível"}

    return _send_debugger_command({
        "method": f"step_{step_type}",
        "params": {},
    })


def debugger_get_stack() -> dict:
    """Obtém stack trace atual."""
    if not _is_debugger_available():
        # Fallback: usa GDScript runtime
        return _debugger_fallback("get_stack")

    return _send_debugger_command({"method": "get_stack"})


def debugger_get_variables(variable_name: str | None = None) -> dict:
    """Inspeciona variáveis no escopo atual.

    Args:
        variable_name: Nome da variável específica. Se None, retorna todas.
    """
    if not _is_debugger_available():
        return _debugger_fallback("get_variables", variable_name)

    return _send_debugger_command({
        "method": "get_variables",
        "params": {"name": variable_name} if variable_name else {},
    })


def debugger_status() -> dict:
    """Verifica estado do debugger."""
    available = _is_debugger_available()
    return {
        "status": "success",
        "debugger": {
            "available": available,
            "host": DEBUGGER_HOST,
            "port": DEBUGGER_PORT,
        },
        "instructions": "Rode o jogo com --debug para ativar o debugger na porta 6006."
        if not available else "Debugger conectado e respondendo.",
    }


# ── Fallback GDScript Runtime ───────────────────────────────────────

def _debugger_fallback(method: str, variable_name: str | None = None) -> dict:
    """Fallback: usa execute_gdscript_runtime quando debugger não disponível."""
    try:
        if method == "get_stack":
            code = "return get_stack()"
        elif method == "get_variables":
            if variable_name:
                code = f"return str({variable_name})"
            else:
                code = "return 'Use debugger ou especifique variable_name'"
        else:
            code = "return 'Debugger indisponivel'"

        from server import execute_gdscript_runtime
        result = execute_gdscript_runtime(code)
        return {
            "status": "success",
            "method": method,
            "fallback": True,
            "result": result,
            "note": "Resultado via GDScript runtime (debugger TCP indisponivel)",
        }
    except Exception as e:
        return {"status": "error", "message": str(e), "fallback": True}
