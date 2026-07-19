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


# ── Comandos de Áudio em Runtime (Fase 6) ───────────────────────

def play_audio(node_path: str, audio_file: str = "", bus: str = "Master",
               volume_db: float = 0.0, loop: bool = False) -> dict:
    """Toca um áudio em runtime via AudioStreamPlayer.

    Cria ou reutiliza um AudioStreamPlayer no nó especificado e inicia
    a reprodução. Útil para tocar SFX ou música durante testes.

    Args:
        node_path: Caminho do nó onde criar o player (ex: "/root/Game/SFX").
        audio_file: Caminho do arquivo de áudio (res://). Se vazio, usa
                    stream já configurado no player existente.
        bus: Nome do bus de áudio (default: "Master").
        volume_db: Volume em dB (default: 0.0).
        loop: Se True, faz loop.

    Returns:
        {"ok": True, "node_path": "...", "action": "play"}
    """
    return send_bridge_command({
        "cmd": "custom",
        "name": "play_audio",
        "args": {
            "node_path": node_path,
            "audio_file": audio_file,
            "bus": bus,
            "volume_db": volume_db,
            "loop": loop,
        },
    })


def set_volume(node_path: str = "", bus_name: str = "Master",
               volume_db: float = 0.0) -> dict:
    """Ajusta volume de um AudioStreamPlayer ou bus de áudio em runtime.

    Args:
        node_path: Caminho do AudioStreamPlayer (se vazio, ajusta o bus).
        bus_name: Nome do bus de áudio (default: "Master").
        volume_db: Volume em dB.

    Returns:
        {"ok": True, "target": "...", "volume_db": float}
    """
    return send_bridge_command({
        "cmd": "custom",
        "name": "set_volume",
        "args": {
            "node_path": node_path,
            "bus_name": bus_name,
            "volume_db": volume_db,
        },
    })


def stop_audio(node_path: str = "") -> dict:
    """Para a reprodução de áudio em um nó específico ou todos.

    Args:
        node_path: Caminho do AudioStreamPlayer. Se vazio, para TODOS
                   os AudioStreamPlayers na árvore.

    Returns:
        {"ok": True, "stopped": int}
    """
    return send_bridge_command({
        "cmd": "custom",
        "name": "stop_audio",
        "args": {"node_path": node_path},
    })
