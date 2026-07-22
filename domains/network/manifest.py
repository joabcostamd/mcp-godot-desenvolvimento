"""domains/network/manifest.py — Manifesto do domínio network (F5.12)."""

from registry.types import DomainManifest, OpSpec, Phase
from . import handlers

MANIFEST = DomainManifest(
    domain="network",
    tool_name="network_manage",
    title="Gerenciar Rede",
    namespace="project",
    version="1.0.0",
    description=(
        "Gerencia rede multiplayer: configurar peer, criar RPCs, WebSocket client, "
        "servidor dedicado e sistema de lobby.\n"
        "QUANDO USAR: para adicionar multiplayer, sincronização e rede ao jogo.\n"
        "QUANDO NÃO USAR: para salvar/carregar (use gamestate_manage), para HTTP (use game_http_request).\n"
        "PRÉ-CONDIÇÕES: projeto com suporte a multiplayer, portas disponíveis.\n"
        "ERRO COMUM: porta em uso — verifique se não há outro processo na porta escolhida."
    ),
    phases=[Phase.CONTEUDO],
    annotations={"readOnlyHint": False, "destructiveHint": True, "idempotentHint": False, "openWorldHint": True},
    ops=[
        OpSpec(name="setup_peer", fn=handlers.setup_multiplayer_peer, summary="Configura o peer multiplayer (ENet ou WebSocket)",
               schema={"peer_type": {"type": "string", "required": False}, "port": {"type": "integer", "required": False}, "max_players": {"type": "integer", "required": False}},
               examples=[{"peer_type": "ENetMultiplayerPeer", "port": 10567, "max_players": 4}], rollback=None),
        OpSpec(name="create_rpc", fn=handlers.create_rpc_method, summary="Cria um método RPC em um script GDScript",
               schema={"script_path": {"type": "string", "required": True}, "method_name": {"type": "string", "required": True}, "params": {"type": "array", "required": False}, "mode": {"type": "string", "required": False}},
               examples=[{"script_path": "res://scripts/player.gd", "method_name": "sync_position", "mode": "any_peer"}], rollback=None),
        OpSpec(name="create_ws", fn=handlers.create_websocket_client, summary="Cria/configura WebSocket client",
               schema={"url": {"type": "string", "required": False}, "autoconnect": {"type": "boolean", "required": False}},
               examples=[{"url": "ws://127.0.0.1:9080", "autoconnect": True}], rollback=None),
        OpSpec(name="config_server", fn=handlers.configure_dedicated_server, summary="Configura o projeto para servidor dedicado (headless)",
               schema={"port": {"type": "integer", "required": False}, "max_players": {"type": "integer", "required": False}, "headless": {"type": "boolean", "required": False}},
               examples=[{"port": 10567, "max_players": 32, "headless": True}], rollback=None),
        OpSpec(name="create_lobby", fn=handlers.create_lobby_system, summary="Cria sistema de lobby básico",
               schema={"scene_path": {"type": "string", "required": True}, "max_players": {"type": "integer", "required": False}, "use_steam": {"type": "boolean", "required": False}},
               examples=[{"scene_path": "scenes/lobby.tscn", "max_players": 4}], rollback=None),
    ],
    tags=["network", "multiplayer", "rpc", "websocket"],
)
