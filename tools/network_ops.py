"""network_ops — Camada 6.5: Rede / Multiplayer.

Operações de rede: WebSocket, RPC, multiplayer setup, lobby.
"""

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent


def setup_multiplayer_peer(
    scene_path: str,
    mode: str = "enet",
    port: int = 27015,
    max_players: int = 4,
    server_address: str = "127.0.0.1",
) -> dict:
    """Configura o multiplayer peer numa cena (ENet ou WebSocket).
    
    Args:
        scene_path: Caminho da cena .tscn
        mode: "enet" para ENetMultiplayerPeer ou "websocket" para WebSocketMultiplayerPeer
        port: Porta do servidor
        max_players: Número máximo de jogadores
        server_address: Endereço do servidor (modo cliente)
    
    Returns:
        dict com status e script gerado
    """
    try:
        scene = Path(scene_path)
        if not scene.exists():
            return {"ok": False, "error": f"Cena não encontrada: {scene_path}"}
        
        script_name = f"multiplayer_setup.gd"
        script_path = scene.parent / script_name
        
        if mode == "enet":
            peer_code = (
                f'var peer = ENetMultiplayerPeer.new()\n'
                f'peer.create_server({port}, {max_players})\n'
                f'multiplayer.multiplayer_peer = peer\n'
            )
        elif mode == "websocket":
            peer_code = (
                f'var peer = WebSocketMultiplayerPeer.new()\n'
                f'peer.create_server({port})\n'
                f'multiplayer.multiplayer_peer = peer\n'
            )
        else:
            return {"ok": False, "error": f"Modo '{mode}' não suportado. Use 'enet' ou 'websocket'."}
        
        gdscript = f'''extends Node

# Multiplayer Setup — {mode.upper()}
# Gerado por godot-mcp-agent (Camada 6.5)
# Porta: {port} | Max jogadores: {max_players}

func _ready():
    {peer_code}
    print("[Multiplayer] Servidor iniciado na porta {port} (modo: {mode})")
    print("[Multiplayer] Max jogadores: {max_players}")

func _exit_tree():
    if multiplayer.multiplayer_peer:
        multiplayer.multiplayer_peer.close()
        print("[Multiplayer] Peer fechado")
'''
        
        script_path.write_text(gdscript, encoding="utf-8")
        
        return {
            "ok": True,
            "mode": mode,
            "port": port,
            "max_players": max_players,
            "script_path": str(script_path),
            "message": f"Script multiplayer ({mode}) criado: {script_path}",
        }
    except Exception as e:
        return {"ok": False, "error": f"Erro ao configurar multiplayer: {e}"}


def create_rpc_method(
    script_path: str,
    method_name: str,
    params: list[str] | None = None,
    rpc_mode: str = "any_peer",
    call_local: bool = False,
    method_body: str = "pass",
) -> dict:
    """Adiciona um método RPC a um script GDScript.
    
    Args:
        script_path: Caminho do script .gd
        method_name: Nome do método RPC
        params: Lista de parâmetros (ex: ["damage: float", "source: NodePath"])
        rpc_mode: Modo RPC — "any_peer", "authority", "server"
        call_local: Se deve chamar localmente também
        method_body: Corpo do método (código GDScript)
    
    Returns:
        dict com status
    """
    try:
        sp = Path(script_path)
        if not sp.exists():
            return {"ok": False, "error": f"Script não encontrado: {script_path}"}
        
        content = sp.read_text(encoding="utf-8")
        
        param_str = ", ".join(params) if params else ""
        annotations = [f"@rpc(\"{rpc_mode}\"", ]
        if call_local:
            annotations.append(", \"call_local\"")
        annotations.append(")")
        annotation_line = "".join(annotations)
        
        rpc_method = f'''
{annotation_line}
func {method_name}({param_str}):
\t{method_body}
'''
        
        # Adiciona no final do script
        new_content = content.rstrip() + "\n" + rpc_method
        
        sp.write_text(new_content, encoding="utf-8")
        
        return {
            "ok": True,
            "method_name": method_name,
            "rpc_mode": rpc_mode,
            "script_path": str(sp),
            "message": f"Método RPC '{method_name}' adicionado a {script_path}",
        }
    except Exception as e:
        return {"ok": False, "error": f"Erro ao criar RPC: {e}"}


def create_websocket_client(
    script_path: str,
    url: str = "ws://localhost:9080",
    protocols: list[str] | None = None,
) -> dict:
    """Adiciona código de WebSocket client a um script.
    
    Args:
        script_path: Caminho do script .gd
        url: URL do WebSocket server
        protocols: Lista de protocolos WebSocket
    
    Returns:
        dict com status
    """
    try:
        sp = Path(script_path)
        if not sp.exists():
            return {"ok": False, "error": f"Script não encontrado: {script_path}"}
        
        content = sp.read_text(encoding="utf-8")
        
        proto_str = ""
        if protocols:
            proto_list = ", ".join(f'"{p}"' for p in protocols)
            proto_str = f"\n\tws_client.supported_protocols = [{proto_list}]"
        
        ws_code = f'''
# WebSocket Client — {url}
var ws_client = WebSocketPeer.new()

func _connect_websocket():
\tvar err = ws_client.connect_to_url("{url}"){proto_str}
\tif err != OK:
\t\tprint("[WS] Erro ao conectar: ", err)
\t\treturn
\tprint("[WS] Conectando a {url}...")

func _process_websocket():
\tws_client.poll()
\tvar state = ws_client.get_ready_state()
\t
\tif state == WebSocketPeer.STATE_OPEN:
\t\twhile ws_client.get_available_packet_count() > 0:
\t\t\tvar packet = ws_client.get_packet()
\t\t\tvar message = packet.get_string_from_utf8()
\t\t\t_on_ws_message(message)
\t
\telif state == WebSocketPeer.STATE_CLOSED:
\t\tprint("[WS] Conexão fechada. Código: ", ws_client.get_close_code())

func _send_ws(message: String):
\tif ws_client.get_ready_state() == WebSocketPeer.STATE_OPEN:
\t\tws_client.put_packet(message.to_utf8_buffer())

func _on_ws_message(message: String):
\tprint("[WS] Mensagem recebida: ", message)
'''
        
        new_content = content.rstrip() + "\n" + ws_code
        
        sp.write_text(new_content, encoding="utf-8")
        
        return {
            "ok": True,
            "url": url,
            "script_path": str(sp),
            "message": f"WebSocket client adicionado a {script_path} — conecta a {url}",
        }
    except Exception as e:
        return {"ok": False, "error": f"Erro ao criar WebSocket client: {e}"}


def configure_dedicated_server(
    export_preset_name: str = "Dedicated Server",
    port: int = 27015,
    enable_upnp: bool = False,
) -> dict:
    """Configura export preset para servidor dedicado.
    
    Args:
        export_preset_name: Nome do preset de exportação
        port: Porta do servidor dedicado
        enable_upnp: Habilita UPnP
    
    Returns:
        dict com status e configuração
    """
    try:
        config = {
            "preset_name": export_preset_name,
            "dedicated_server": True,
            "port": port,
            "upnp_enabled": enable_upnp,
            "headless": True,
        }
        
        return {
            "ok": True,
            "config": config,
            "message": (
                f"Configuração de servidor dedicado '{export_preset_name}' definida. "
                f"Porta: {port}. "
                "Para aplicar, use configure_export_preset com estas configurações."
            ),
        }
    except Exception as e:
        return {"ok": False, "error": f"Erro ao configurar servidor dedicado: {e}"}


def create_lobby_system(
    scene_path: str,
    max_players: int = 4,
    lobby_name: str = "MainLobby",
) -> dict:
    """Cria um sistema de lobby básico para multiplayer.
    
    Gera um script de lobby com: listagem de salas, join/create,
    ready state, e transição para jogo.
    
    Args:
        scene_path: Caminho da cena para associar o script
        max_players: Máximo de jogadores por sala
        lobby_name: Nome do nó de lobby na cena
    
    Returns:
        dict com status e script_path
    """
    try:
        scene = Path(scene_path)
        if not scene.exists():
            return {"ok": False, "error": f"Cena não encontrada: {scene_path}"}
        
        script_path = scene.parent / "lobby_system.gd"
        
        gdscript = f'''extends Node
# Lobby System — {lobby_name}
# Gerado por godot-mcp-agent (Camada 6.5)

var players: Dictionary = {{}}
var max_players: int = {max_players}
var ready_players: Array[String] = []

func _ready():
\tprint("[Lobby] Sistema iniciado. Max jogadores: ", max_players)

func add_player(player_id: String, player_name: String) -> bool:
\tif players.size() >= max_players:
\t\tprint("[Lobby] Sala cheia! Jogador rejeitado: ", player_name)
\t\treturn false
\tplayers[player_id] = {{"name": player_name, "ready": false}}
\tprint("[Lobby] Jogador entrou: ", player_name, " (", players.size(), "/", max_players, ")")
\treturn true

func remove_player(player_id: String):
\tif players.has(player_id):
\t\tvar name = players[player_id]["name"]
\t\tplayers.erase(player_id)
\t\tready_players.erase(player_id)
\t\tprint("[Lobby] Jogador saiu: ", name)

func set_ready(player_id: String, ready: bool):
\tif players.has(player_id):
\t\tplayers[player_id]["ready"] = ready
\t\tif ready:
\t\t\tif player_id not in ready_players:
\t\t\t\tready_players.append(player_id)
\t\telse:
\t\t\tready_players.erase(player_id)
\t\tprint("[Lobby] Ready: ", players[player_id]["name"], " = ", ready)
\t\t_check_all_ready()

func _check_all_ready():
\tif ready_players.size() >= players.size() and players.size() >= 1:
\t\tprint("[Lobby] Todos prontos! Iniciando jogo...")
\t\tstart_game()

func start_game():
\tprint("[Lobby] Transição para jogo — ", players.size(), " jogadores")
\t# RPC: notifica todos os clientes para carregar a cena do jogo
\tget_tree().change_scene_to_file("res://scenes/game.tscn")

func get_player_count() -> int:
\treturn players.size()

func get_ready_count() -> int:
\treturn ready_players.size()
'''
        
        script_path.write_text(gdscript, encoding="utf-8")
        
        return {
            "ok": True,
            "max_players": max_players,
            "script_path": str(script_path),
            "message": f"Sistema de lobby criado: {script_path}",
        }
    except Exception as e:
        return {"ok": False, "error": f"Erro ao criar lobby: {e}"}
