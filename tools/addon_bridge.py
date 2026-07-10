"""addon_bridge.py — WebSocket Bridge para Addon GDScript (Fase 2B / A2).

Conecta no WebSocket server do addon GDScript (porta 9082) e traduz
chamadas de tool MCP em comandos JSON-RPC 2.0 para o editor Godot.

Fallback automático para file-based se o addon estiver offline.
Implementação stdlib pura — zero dependências externas.

Protocolo: WebSocket (RFC 6455) + JSON-RPC 2.0 simplificado.
Porta: ws://127.0.0.1:9082
"""

import hashlib
import json
import socket
import struct
import threading
import time
from base64 import b64encode

# ── Constantes ──────────────────────────────────────────────────────

WS_HOST = "127.0.0.1"
WS_PORT = 9082
WS_TIMEOUT = 5.0  # segundos
WS_ORIGIN = "http://localhost"

# Opcodes WebSocket
OP_TEXT = 0x1
OP_CLOSE = 0x8


# ── Exceções ────────────────────────────────────────────────────────

class AddonBridgeError(Exception):
    """Erro de comunicação com o addon GDScript."""
    pass


class AddonNotConnectedError(AddonBridgeError):
    """Addon não está conectado/respondendo."""
    pass


# ── WebSocket Client (stdlib puro) ──────────────────────────────────

class _WsClient:
    """Cliente WebSocket minimalista (RFC 6455) usando apenas stdlib."""

    def __init__(self):
        self._socket: socket.socket | None = None

    def __del__(self):
        """Garante cleanup do socket no garbage collection."""
        try:
            self.close()
        except Exception:
            pass

    def connect(self, host: str = WS_HOST, port: int = WS_PORT,
                timeout: float = WS_TIMEOUT) -> None:
        """Conecta e faz handshake WebSocket."""
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.settimeout(timeout)
        self._socket.connect((host, port))

        # Handshake HTTP Upgrade
        key = b64encode(hashlib.sha1(
            str(time.time()).encode()
        ).digest()).decode()

        request = (
            f"GET / HTTP/1.1\r\n"
            f"Host: {host}:{port}\r\n"
            f"Upgrade: websocket\r\n"
            f"Connection: Upgrade\r\n"
            f"Sec-WebSocket-Key: {key}\r\n"
            f"Sec-WebSocket-Version: 13\r\n"
            f"Origin: {WS_ORIGIN}\r\n"
            f"\r\n"
        )
        self._socket.sendall(request.encode())

        # Lê resposta do handshake
        response = b""
        while b"\r\n\r\n" not in response:
            chunk = self._socket.recv(1)
            if not chunk:
                raise AddonBridgeError("Handshake WebSocket falhou: conexão fechada.")
            response += chunk

        if b"101" not in response:
            raise AddonBridgeError(
                f"Handshake WebSocket falhou. Resposta: {response[:200]}"
            )

    def send_text(self, message: str) -> None:
        """Envia frame de texto WebSocket."""
        if not self._socket:
            raise AddonNotConnectedError("WebSocket não conectado.")
        payload = message.encode("utf-8")
        self._send_frame(OP_TEXT, payload)

    def recv_text(self, timeout: float = WS_TIMEOUT) -> str | None:
        """Recebe frame de texto WebSocket."""
        if not self._socket:
            return None
        self._socket.settimeout(timeout)
        try:
            opcode, payload = self._recv_frame()
            if opcode == OP_TEXT:
                return payload.decode("utf-8")
            elif opcode == OP_CLOSE:
                return None
            return None
        except socket.timeout:
            return None

    def close(self) -> None:
        """Fecha conexão WebSocket."""
        if self._socket:
            try:
                self._send_frame(OP_CLOSE, b"")
            except Exception:
                pass
            try:
                self._socket.close()
            except Exception:
                pass
            self._socket = None

    def is_connected(self) -> bool:
        """Verifica se está conectado."""
        if not self._socket:
            return False
        try:
            self._socket.settimeout(0.001)
            self._socket.recv(1, socket.MSG_PEEK)
            self._socket.settimeout(WS_TIMEOUT)
            return True
        except (socket.timeout, BlockingIOError):
            self._socket.settimeout(WS_TIMEOUT)
            return True
        except Exception:
            return False

    def _send_frame(self, opcode: int, payload: bytes) -> None:
        """Monta e envia frame WebSocket."""
        if not self._socket:
            raise AddonNotConnectedError("WebSocket não conectado.")

        frame = bytearray()
        frame.append(0x80 | opcode)  # FIN + opcode

        length = len(payload)
        if length < 126:
            frame.append(length)
        elif length < 65536:
            frame.append(126)
            frame.extend(struct.pack(">H", length))
        else:
            frame.append(127)
            frame.extend(struct.pack(">Q", length))

        frame.extend(payload)
        self._socket.sendall(bytes(frame))

    def _recv_frame(self) -> tuple[int, bytes]:
        """Recebe e parseia frame WebSocket."""
        if not self._socket:
            raise AddonNotConnectedError("WebSocket não conectado.")

        # Lê header (2 bytes mínimos)
        header = self._recv_exact(2)
        if len(header) < 2:
            raise AddonBridgeError("Frame WebSocket truncado.")

        opcode = header[0] & 0x0F
        masked = (header[1] & 0x80) != 0
        length = header[1] & 0x7F

        if length == 126:
            length = struct.unpack(">H", self._recv_exact(2))[0]
        elif length == 127:
            length = struct.unpack(">Q", self._recv_exact(8))[0]

        # Máscara (cliente→servidor, servidor NÃO mascara respostas)
        if masked:
            mask_key = self._recv_exact(4)
        else:
            mask_key = None

        # Payload
        payload = self._recv_exact(length)

        # Desmascara se necessário
        if mask_key:
            payload = bytes(
                payload[i] ^ mask_key[i % 4] for i in range(length)
            )

        return opcode, payload

    def _recv_exact(self, n: int) -> bytes:
        """Recebe exatamente n bytes."""
        data = b""
        while len(data) < n:
            chunk = self._socket.recv(n - len(data))
            if not chunk:
                break
            data += chunk
        return data


# ── Addon Bridge ────────────────────────────────────────────────────

class AddonBridge:
    """Ponte JSON-RPC 2.0 para o addon GDScript via WebSocket.

    Thread-safe. Faz fallback automático para file-based se o addon
    não estiver disponível.

    Uso:
        bridge = AddonBridge()
        if bridge.connect():
            result = bridge.call("create_node", {...})
        else:
            # usar file-based fallback
    """

    def __init__(self):
        self._ws = _WsClient()
        self._lock = threading.Lock()
        self._request_id = 0
        self._connected = False
        self._fallback_enabled = True

    # ── Conexão ─────────────────────────────────────────────────

    def connect(self, timeout: float = WS_TIMEOUT) -> bool:
        """Conecta ao addon GDScript via WebSocket.

        Returns:
            True se conectado, False caso contrário.
        """
        with self._lock:
            try:
                self._ws.connect(timeout=timeout)
                self._connected = True
                return True
            except Exception:
                self._connected = False
                return False

    def disconnect(self) -> None:
        """Desconecta do addon."""
        with self._lock:
            self._ws.close()
            self._connected = False

    def is_available(self) -> bool:
        """Verifica se addon está conectado e respondendo."""
        with self._lock:
            if not self._connected:
                return False
            if not self._ws.is_connected():
                self._connected = False
                return False
            return True

    # ── Chamadas JSON-RPC ───────────────────────────────────────

    def call(self, method: str, params: dict | None = None,
             timeout: float = WS_TIMEOUT) -> dict:
        """Faz chamada JSON-RPC ao addon.

        Args:
            method: Nome do método (ex: 'create_node').
            params: Parâmetros do método.
            timeout: Timeout em segundos.

        Returns:
            dict com 'status' e dados da resposta, ou erro.
        """
        if not self.is_available():
            if self._fallback_enabled:
                return {
                    "status": "fallback",
                    "message": (
                        f"Addon GDScript não disponível em "
                        f"{WS_HOST}:{WS_PORT}. Usando file-based fallback."
                    ),
                }
            return {
                "status": "error",
                "message": "Addon GDScript não conectado. Abra o Godot com o addon instalado.",
            }

        with self._lock:
            self._request_id += 1
            request = {
                "jsonrpc": "2.0",
                "id": self._request_id,
                "method": method,
                "params": params or {},
            }

            try:
                self._ws.send_text(json.dumps(request))
                response_raw = self._ws.recv_text(timeout)
                if response_raw is None:
                    return {
                        "status": "error",
                        "message": f"Timeout ao chamar '{method}'. Addon não respondeu.",
                    }

                response = json.loads(response_raw)
                if "result" in response:
                    result = response["result"]
                    if isinstance(result, dict) and "status" not in result:
                        result["status"] = "success"
                    return result
                if "error" in response:
                    err = response["error"]
                    return {
                        "status": "error",
                        "message": err.get("message", "Erro desconhecido do addon."),
                        "code": err.get("code", -1),
                        "addon_error": err,
                    }
                return {
                    "status": "error",
                    "message": f"Resposta inesperada do addon: {response}",
                }

            except AddonNotConnectedError:
                self._connected = False
                return {
                    "status": "error",
                    "message": "Conexão com addon perdida durante a chamada.",
                }
            except Exception as e:
                return {
                    "status": "error",
                    "message": f"Erro ao chamar '{method}': {e}",
                }

    @property
    def fallback_enabled(self) -> bool:
        return self._fallback_enabled

    @fallback_enabled.setter
    def fallback_enabled(self, value: bool) -> None:
        self._fallback_enabled = value


# ── Singleton ───────────────────────────────────────────────────────

_bridge: AddonBridge | None = None


def get_bridge() -> AddonBridge:
    """Retorna o singleton da ponte addon."""
    global _bridge
    if _bridge is None:
        _bridge = AddonBridge()
    return _bridge


# ── Tool Functions ──────────────────────────────────────────────────

def addon_connect() -> dict:
    """Conecta ao addon GDScript via WebSocket (porta 9082).

    Use após abrir o Godot com o addon MCP instalado.
    Pré-condições: Godot editor ABERTO com addon MCP ativo.
    """
    bridge = get_bridge()
    if bridge.connect():
        return {
            "status": "success",
            "message": f"Conectado ao addon GDScript em {WS_HOST}:{WS_PORT}.",
        }
    return {
        "status": "error",
        "message": (
            f"Não foi possível conectar ao addon em {WS_HOST}:{WS_PORT}. "
            f"Verifique se o Godot está aberto com o addon MCP instalado."
        ),
    }


def addon_disconnect() -> dict:
    """Desconecta do addon GDScript."""
    get_bridge().disconnect()
    return {"status": "success", "message": "Desconectado do addon GDScript."}


def addon_is_available() -> dict:
    """Verifica se o addon GDScript está conectado e respondendo."""
    available = get_bridge().is_available()
    return {
        "status": "success",
        "available": available,
        "message": (
            "Addon GDScript conectado e respondendo."
            if available
            else "Addon GDScript não disponível."
        ),
    }


def addon_create_node(
    parent_path: str,
    node_type: str,
    node_name: str,
    properties: dict | None = None,
    scene_path: str | None = None,
) -> dict:
    """Cria um nó na cena atual do editor com UndoRedo nativo.

    Args:
        parent_path: Path do nó pai (ex: '/root/Main/Grid').
        node_type: Tipo Godot do nó (ex: 'Sprite2D').
        node_name: Nome do novo nó.
        properties: Propriedades iniciais (opcional).
        scene_path: Cena alvo (opcional, default: cena aberta).
    """
    params = {
        "parent_path": parent_path,
        "node_type": node_type,
        "node_name": node_name,
    }
    if properties:
        params["properties"] = properties
    if scene_path:
        params["scene_path"] = scene_path

    return get_bridge().call("create_node", params)


def addon_delete_node(node_path: str) -> dict:
    """Remove um nó da cena com UndoRedo nativo.

    Args:
        node_path: Path absoluto do nó (ex: '/root/Main/Player').
    """
    return get_bridge().call("delete_node", {"node_path": node_path})


def addon_set_property(
    node_path: str, property_name: str, value
) -> dict:
    """Define propriedade de um nó com UndoRedo nativo.

    Args:
        node_path: Path do nó.
        property_name: Nome da propriedade.
        value: Valor (tipos Godot serializados como JSON).
    """
    return get_bridge().call("set_node_property", {
        "node_path": node_path,
        "property_name": property_name,
        "value": value,
    })


def addon_reparent_node(node_path: str, new_parent_path: str) -> dict:
    """Re-parenta um nó com UndoRedo nativo.

    Args:
        node_path: Path do nó a mover.
        new_parent_path: Path do novo pai.
    """
    return get_bridge().call("reparent_node", {
        "node_path": node_path,
        "new_parent_path": new_parent_path,
    })


def addon_duplicate_node(node_path: str, new_name: str | None = None) -> dict:
    """Duplica um nó com UndoRedo nativo.

    Args:
        node_path: Path do nó a duplicar.
        new_name: Nome para a cópia (opcional).
    """
    params = {"node_path": node_path}
    if new_name:
        params["new_name"] = new_name
    return get_bridge().call("duplicate_node", params)


def addon_batch_edit(operations: list[dict]) -> dict:
    """Executa múltiplas operações em 1 ação UndoRedo.

    Todas as operações são agrupadas — 1 Ctrl+Z desfaz tudo.

    Args:
        operations: Lista de operações no formato:
            [{"method": "create_node", "params": {...}}, ...]
    """
    return get_bridge().call("batch_edit", {"operations": operations})


def addon_take_screenshot(viewport: str = "editor") -> dict:
    """Captura screenshot via addon (viewport do editor).

    Args:
        viewport: 'editor' (padrão) ou caminho de viewport específico.
    """
    return get_bridge().call("take_screenshot", {"viewport": viewport})


def addon_get_scene_tree() -> dict:
    """Obtém a árvore da cena atual do editor via addon."""
    return get_bridge().call("get_scene_tree", {})


def addon_ping() -> dict:
    """Verifica se o addon está respondendo (ping)."""
    return get_bridge().call("ping", {})
