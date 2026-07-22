"""domains/network/handlers.py — Handlers do domínio network (F5.12).

Wrappers keyword-only (*) que delegam para tools/network_ops.py.
"""

from typing import Any


def setup_multiplayer_peer(*, peer_type: str = "ENetMultiplayerPeer", port: int = 10567, max_players: int = 4) -> dict:
    """Configura o peer multiplayer (ENet ou WebSocket)."""
    from tools.network_ops import setup_multiplayer_peer as _impl
    return _impl(peer_type=peer_type, port=port, max_players=max_players)


def create_rpc_method(*, script_path: str, method_name: str, params: list[str] | None = None, mode: str = "any_peer") -> dict:
    """Cria um método RPC em um script GDScript."""
    from tools.network_ops import create_rpc_method as _impl
    return _impl(script_path=script_path, method_name=method_name, params=params, mode=mode)


def create_websocket_client(*, url: str = "ws://127.0.0.1:9080", autoconnect: bool = True) -> dict:
    """Cria/configura WebSocket client."""
    from tools.network_ops import create_websocket_client as _impl
    return _impl(url=url, autoconnect=autoconnect)


def configure_dedicated_server(*, port: int = 10567, max_players: int = 32, headless: bool = True) -> dict:
    """Configura o projeto para servidor dedicado."""
    from tools.network_ops import configure_dedicated_server as _impl
    return _impl(port=port, max_players=max_players, headless=headless)


def create_lobby_system(*, scene_path: str, max_players: int = 4, use_steam: bool = False) -> dict:
    """Cria sistema de lobby básico."""
    from tools.network_ops import create_lobby_system as _impl
    return _impl(scene_path=scene_path, max_players=max_players, use_steam=use_steam)


__all__ = [
    "setup_multiplayer_peer",
    "create_rpc_method",
    "create_websocket_client",
    "configure_dedicated_server",
    "create_lobby_system",
]
