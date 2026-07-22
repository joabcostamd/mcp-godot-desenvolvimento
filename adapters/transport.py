"""adapters/transport.py — Seletor de transporte por capacidade (F6.1).

O modelo NUNCA escolhe transporte. Este módulo registra capacidades
com seus backends disponíveis em ordem de preferência e seleciona
automaticamente o primeiro backend vivo para cada operação.

Uso:
    from adapters.transport import pick, Backend

    backend = pick("scene.write")
    result = backend.execute({"op": "create_node", ...})
"""

from __future__ import annotations

import socket
import time
from dataclasses import dataclass, field
from typing import Any, Callable

# ══════════════════════════════════════════════════════════════════════
# Backend
# ══════════════════════════════════════════════════════════════════════


@dataclass
class Backend:
    """Um backend de transporte concreto."""
    name: str
    host: str = "127.0.0.1"
    port: int = 0
    protocol: str = "tcp"  # tcp, ws, cli
    check_fn: Callable[[], bool] | None = None
    execute_fn: Callable[[str, dict], dict] | None = None

    def is_available(self) -> bool:
        """Verifica se o backend está respondendo."""
        if self.check_fn:
            try:
                return self.check_fn()
            except Exception:
                return False

        if self.protocol == "cli":
            return True  # CLI está sempre disponível (fallback)

        # Teste básico de socket
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            sock.connect((self.host, self.port))
            sock.close()
            return True
        except (ConnectionRefusedError, socket.timeout, OSError):
            return False

    def execute(self, params: dict) -> dict:
        """Executa uma operação neste backend."""
        if self.execute_fn:
            return self.execute_fn(self.name, params)
        return {"status": "error", "message": f"Backend '{self.name}' sem execute_fn"}


# ══════════════════════════════════════════════════════════════════════
# Registro de Backends
# ══════════════════════════════════════════════════════════════════════


def _check_addon_ws() -> bool:
    """Verifica se o addon WebSocket (9082) está respondendo."""
    try:
        from tools.addon_bridge import is_connected, connect
        if is_connected():
            return True
        result = connect()
        return result.get("status") == "success"
    except Exception:
        return False


def _check_runtime_bridge() -> bool:
    """Verifica se o runtime bridge (8790) está respondendo."""
    try:
        from tools.game_bridge import is_connected, connect
        if is_connected():
            return True
        result = connect(retries=1, backoff=0.2)
        return result.get("status") == "success"
    except Exception:
        return False


def _check_editor_tcp() -> bool:
    """Verifica se o editor TCP (9080) está respondendo."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.5)
        sock.connect(("127.0.0.1", 9080))
        sock.close()
        return True
    except Exception:
        return False


def _check_game_tcp() -> bool:
    """Verifica se o jogo TCP (9081) está respondendo."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.5)
        sock.connect(("127.0.0.1", 9081))
        sock.close()
        return True
    except Exception:
        return False


def _exec_headless_cli(_name: str, params: dict) -> dict:
    """Executa via Godot headless CLI."""
    from tools.runtime_ops import compile_test
    return compile_test()


def _exec_addon_ws(_name: str, params: dict) -> dict:
    """Executa via addon WebSocket."""
    from tools.addon_bridge import send_command
    return send_command(params)


def _exec_runtime_bridge(_name: str, params: dict) -> dict:
    """Executa via runtime bridge TCP."""
    from tools.game_bridge import send_command
    return send_command(params.get("cmd", ""), params.get("args", {}))


# ══════════════════════════════════════════════════════════════════════
# Registro de Backends (instâncias)
# ══════════════════════════════════════════════════════════════════════

BACKENDS: dict[str, Backend] = {
    "addon_ws": Backend(
        name="addon_ws",
        host="127.0.0.1", port=9082, protocol="ws",
        check_fn=_check_addon_ws,
        execute_fn=_exec_addon_ws,
    ),
    "headless_cli": Backend(
        name="headless_cli",
        protocol="cli",
        execute_fn=_exec_headless_cli,
    ),
    "runtime_bridge": Backend(
        name="runtime_bridge",
        host="127.0.0.1", port=8790, protocol="tcp",
        check_fn=_check_runtime_bridge,
        execute_fn=_exec_runtime_bridge,
    ),
    "game_tcp": Backend(
        name="game_tcp",
        host="127.0.0.1", port=9081, protocol="tcp",
        check_fn=_check_game_tcp,
    ),
    "editor_tcp": Backend(
        name="editor_tcp",
        host="127.0.0.1", port=9080, protocol="tcp",
        check_fn=_check_editor_tcp,
    ),
}


# ══════════════════════════════════════════════════════════════════════
# Mapa de Capacidades → Backends (ordem = preferência)
# ══════════════════════════════════════════════════════════════════════

CAPABILITIES: dict[str, list[str]] = {
    "scene.write":   ["addon_ws", "headless_cli"],
    "node.create":   ["addon_ws", "headless_cli"],
    "node.edit":     ["addon_ws", "headless_cli"],
    "screenshot":    ["addon_ws", "runtime_bridge", "editor_tcp"],
    "runtime.exec":  ["runtime_bridge", "game_tcp"],
    "editor.query":  ["addon_ws", "editor_tcp"],
    "editor.command":["addon_ws", "editor_tcp"],
    "compile":       ["headless_cli"],
}


# ══════════════════════════════════════════════════════════════════════
# Cache de disponibilidade (curta duração)
# ══════════════════════════════════════════════════════════════════════

_cache: dict[str, tuple[bool, float]] = {}
CACHE_TTL: float = 5.0  # segundos


def _cached_available(backend_name: str) -> bool:
    """Verifica disponibilidade com cache curto."""
    now = time.time()
    if backend_name in _cache:
        available, timestamp = _cache[backend_name]
        if now - timestamp < CACHE_TTL:
            return available

    backend = BACKENDS.get(backend_name)
    if backend is None:
        _cache[backend_name] = (False, now)
        return False

    available = backend.is_available()
    _cache[backend_name] = (available, now)
    return available


def clear_cache() -> None:
    """Limpa o cache de disponibilidade."""
    _cache.clear()


# ══════════════════════════════════════════════════════════════════════
# API Pública
# ══════════════════════════════════════════════════════════════════════


def pick(capability: str, prefer: str | None = None) -> Backend | None:
    """Seleciona o melhor backend disponível para uma capacidade.

    Args:
        capability: Nome da capacidade (ex: "scene.write", "node.create").
        prefer: Se fornecido, tenta este backend primeiro.

    Returns:
        Backend disponível ou None se nenhum estiver ativo.
    """
    backends = CAPABILITIES.get(capability, [])

    if not backends:
        return None

    # Se tem preferência, move para o topo
    if prefer and prefer in backends:
        backends = [prefer] + [b for b in backends if b != prefer]

    for name in backends:
        if _cached_available(name):
            return BACKENDS[name]

    return None


def pick_or_fallback(capability: str) -> Backend:
    """pick() com fallback garantido para headless_cli."""
    result = pick(capability)
    if result is None:
        return BACKENDS["headless_cli"]
    return result


def status() -> dict:
    """Retorna status de todos os backends."""
    result = {}
    for name, backend in BACKENDS.items():
        available = _cached_available(name) if name != "headless_cli" else True
        result[name] = {
            "available": available,
            "host": backend.host,
            "port": backend.port,
            "protocol": backend.protocol,
        }
    return result
