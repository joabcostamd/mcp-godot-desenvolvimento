"""networking_ops.py — Networking Runtime (Fase 3 / tugcantopaloglu).

Ferramentas de rede para o jogo em execução: HTTP requests,
WebSocket client, ENet multiplayer, RPC calls.

Inspirado no tugcantopaloglu/godot-mcp (game_http_request,
game_websocket, game_multiplayer, game_rpc).

Tools:
    - game_http_request: HTTP GET/POST/PUT/DELETE
    - game_websocket: WebSocket client connect/send/close
    - game_multiplayer: ENet multiplayer host/join
    - game_rpc: RPC calls e configuração
"""

import json
import time


# ── HTTP ─────────────────────────────────────────────────────────────

def game_http_request(
    url: str,
    method: str = "GET",
    headers: dict | None = None,
    body: str | None = None,
    timeout: float = 10.0,
) -> dict:
    """Executa HTTP request no jogo em execução via GDScript.

    Args:
        url: URL completa (ex: "https://api.example.com/data").
        method: GET, POST, PUT, DELETE.
        headers: Dicionário de headers opcionais.
        body: Corpo da requisição (string).
        timeout: Timeout em segundos.

    Returns:
        dict com resposta ou erro.
    """
    headers_str = json.dumps(headers or {})
    body_str = json.dumps(body) if body else '""'

    code = f"""
    var http = HTTPRequest.new()
    get_tree().root.add_child(http)
    http.request_completed.connect(func(r,s,h,b):
        http.queue_free()
    )
    
    var err = http.request("{url}", {_gd_headers(headers)}, {method})
    if err != OK:
        return {{"error": "HTTP request failed", "code": err}}
    
    var result = await http.request_completed
    return {{
        "status": result[1],
        "headers": str(result[2]),
        "body": result[3].get_string_from_utf8()
    }}
    """

    return _execute_gdscript(code)


# ── WebSocket ────────────────────────────────────────────────────────

def game_websocket(
    action: str,
    url: str = "",
    message: str | None = None,
) -> dict:
    """Gerencia WebSocket client no jogo em execução.

    Args:
        action: "connect", "send", "close".
        url: URL do WebSocket (ws:// ou wss://).
        message: Mensagem a enviar (para action="send").

    Returns:
        dict com resultado.
    """
    if action == "connect":
        code = f"""
        var ws = WebSocketPeer.new()
        var err = ws.connect_to_url("{url}")
        if err != OK:
            return {{"status": "error", "message": "Falha ao conectar: " + str(err)}}
        return {{"status": "success", "message": "Conectando..."}}
        """
    elif action == "send":
        msg = message or ""
        code = f"""
        var ws = get_tree().root.get_node_or_null("_mcp_ws_client")
        if not ws:
            return {{"status": "error", "message": "WebSocket nao conectado"}}
        ws.send_text("{msg}")
        return {{"status": "success"}}
        """
    elif action == "close":
        code = """
        var ws = get_tree().root.get_node_or_null("_mcp_ws_client")
        if ws:
            ws.close()
            ws.queue_free()
        return {"status": "success"}
        """
    else:
        return {"status": "error", "message": f"Acao desconhecida: {action}"}

    return _execute_gdscript(code)


# ── Multiplayer ──────────────────────────────────────────────────────

def game_multiplayer(
    action: str,
    port: int = 9090,
    address: str = "127.0.0.1",
    max_players: int = 4,
) -> dict:
    """Gerencia multiplayer ENet no jogo em execução.

    Args:
        action: "create_server", "create_client", "disconnect", "status".
        port: Porta (default 9090).
        address: Endereço do servidor (para client).
        max_players: Máximo de jogadores (para servidor).

    Returns:
        dict com resultado.
    """
    if action == "create_server":
        code = f"""
        var peer = ENetMultiplayerPeer.new()
        var err = peer.create_server({port}, {max_players})
        if err != OK:
            return {{"status": "error", "message": "Falha ao criar servidor"}}
        get_tree().get_multiplayer().multiplayer_peer = peer
        return {{"status": "success", "peer_id": peer.get_unique_id()}}
        """

    elif action == "create_client":
        code = f"""
        var peer = ENetMultiplayerPeer.new()
        var err = peer.create_client("{address}", {port})
        if err != OK:
            return {{"status": "error", "message": "Falha ao conectar"}}
        get_tree().get_multiplayer().multiplayer_peer = peer
        return {{"status": "success", "message": "Conectando..."}}
        """

    elif action == "disconnect":
        code = """
        var peer = get_tree().get_multiplayer().multiplayer_peer
        if peer:
            peer.close()
        get_tree().get_multiplayer().multiplayer_peer = null
        return {"status": "success"}
        """

    elif action == "status":
        code = """
        var mp = get_tree().get_multiplayer()
        var peer = mp.multiplayer_peer
        return {
            "has_peer": peer != null,
            "is_server": mp.is_server(),
            "peer_id": str(mp.get_unique_id()),
            "peers": str(mp.get_peers())
        }
        """

    else:
        return {"status": "error", "message": f"Acao desconhecida: {action}"}

    return _execute_gdscript(code)


# ── RPC ──────────────────────────────────────────────────────────────

def game_rpc(
    node_path: str,
    method: str = "",
    args: list | None = None,
    mode: str = "call",
    config: str = "",
) -> dict:
    """Executa/configura RPC em nó multiplayer.

    Args:
        node_path: Path do nó (ex: "./Player").
        method: Método a chamar via RPC.
        args: Argumentos da chamada.
        mode: "call" (chama), "config" (configura).
        config: Modo de RPC: "any_peer", "authority", "disabled".

    Returns:
        dict com resultado.
    """
    if mode == "config":
        code = f"""
        var node = get_node("{node_path}")
        if not node:
            return {{"status": "error", "message": "No nao encontrado"}}
        
        var fn = node.get("{method}")
        if fn:
            if "{config}" == "authority":
                fn.rpc_mode = MultiplayerAPI.RPC_MODE_AUTHORITY
            elif "{config}" == "any_peer":
                fn.rpc_mode = MultiplayerAPI.RPC_MODE_ANY_PEER
            else:
                fn.rpc_mode = MultiplayerAPI.RPC_MODE_DISABLED
            fn.rpc_config()
            return {{"status": "success", "method": "{method}", "mode": "{config}"}}
        
        return {{"status": "error", "message": "Metodo nao encontrado"}}
        """

    elif mode == "call":
        args_str = json.dumps(args or [])
        code = f"""
        var node = get_node("{node_path}")
        if not node:
            return {{"status": "error", "message": "No nao encontrado"}}
        
        node.rpc("{method}", {args_str})
        return {{"status": "success", "method": "{method}"}}
        """

    else:
        return {"status": "error", "message": f"Modo desconhecido: {mode}"}

    return _execute_gdscript(code)


# ── Helpers ──────────────────────────────────────────────────────────

def _gd_headers(headers: dict | None) -> str:
    """Converte headers Python para array GDScript."""
    if not headers:
        return "[]"
    items = [f'"{k}: {v}"' for k, v in headers.items()]
    return "[" + ", ".join(items) + "]"


def _execute_gdscript(code: str) -> dict:
    """Executa GDScript no jogo em execução."""
    try:
        from tools.runtime_ops import execute_gdscript_runtime
        result = execute_gdscript_runtime(code)
        return {"status": "success", "result": result} if result else {"status": "error", "message": "Sem resposta"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


# ── Network Status ──────────────────────────────────────────────────

def game_network_status() -> dict:
    """Verifica status de rede do jogo em execução."""
    code = """
    var mp = get_tree().get_multiplayer()
    return {
        "multiplayer_active": mp.multiplayer_peer != null,
        "is_server": mp.is_server() if mp.multiplayer_peer else false,
        "peer_id": str(mp.get_unique_id()),
        "connected_peers": str(mp.get_peers()),
        "online": OS.has_feature("web") or true
    }
    """
    return _execute_gdscript(code)
