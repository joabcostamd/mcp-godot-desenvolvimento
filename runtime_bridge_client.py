"""runtime_bridge_client.py — Cliente TCP para MCPRuntimeBridge (PATCH 12).

Conecta no autoload GDScript que roda dentro do jogo Godot em modo debug.
Protocolo: JSON-por-linha sobre TCP localhost:8790.
"""

import json
import socket

HOST = "127.0.0.1"
PORT = 8790
TIMEOUT_SEC = 5


class BridgeUnavailable(Exception):
    """Levantada quando o bridge nao esta acessivel (jogo nao rodando em debug)."""
    pass


def send_bridge_command(payload: dict, timeout: float = TIMEOUT_SEC) -> dict:
    """Conecta no autoload GDScript e envia um comando JSON-por-linha.

    Args:
        payload: Dicionario com 'cmd' e parametros especificos.
        timeout: Timeout em segundos para a conexao.

    Returns:
        dict com a resposta do bridge.

    Raises:
        BridgeUnavailable: se o jogo nao estiver rodando em debug.
    """
    try:
        with socket.create_connection((HOST, PORT), timeout=timeout) as sock:
            sock.sendall((json.dumps(payload) + "\n").encode("utf-8"))
            sock.settimeout(timeout)
            buffer = b""
            while b"\n" not in buffer:
                chunk = sock.recv(65536)
                if not chunk:
                    break
                buffer += chunk
            line = buffer.split(b"\n", 1)[0]
            return json.loads(line.decode("utf-8"))
    except (ConnectionRefusedError, socket.timeout, OSError) as exc:
        raise BridgeUnavailable(
            f"Nao foi possivel conectar ao MCPRuntimeBridge em {HOST}:{PORT}. "
            f"O jogo esta rodando em modo debug pelo Godot? ({exc})"
        )
