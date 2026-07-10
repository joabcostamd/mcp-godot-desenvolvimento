"""lsp_ops.py — LSP Bridge (Fase 2A / C3).

Conecta na porta 6005 do Godot (LSP built-in) e expõe análises
semânticas como ferramentas MCP: referências, definição, hover,
símbolos, rename, diagnósticos e sync de arquivo.

Baseado no padrão GodotLens (pzalutski-pixel):
Python puro, stdlib apenas — zero dependências externas.

Protocolo: JSON-RPC 2.0 sobre TCP com Content-Length header.
A porta 6005 só fica ativa com o editor Godot ABERTO.
"""

import json
import socket
import threading
import time
from pathlib import Path

# ── Constantes ──────────────────────────────────────────────────────

LSP_HOST = "127.0.0.1"
LSP_PORT = 6005
LSP_TIMEOUT = 5.0  # segundos
MAX_MESSAGE_SIZE = 10 * 1024 * 1024  # 10 MB


# ── Cliente LSP ─────────────────────────────────────────────────────

class LspClient:
    """Cliente JSON-RPC 2.0 para o LSP do Godot.

    Thread-safe. Conexão lazy — só conecta na primeira chamada.
    """

    def __init__(self):
        self._socket: socket.socket | None = None
        self._lock = threading.Lock()
        self._request_id = 0
        self._initialized = False
        self._root_uri: str | None = None

    # ── Conexão ─────────────────────────────────────────────────

    def connect(self, project_root: str | None = None) -> dict:
        """Conecta ao LSP do Godot e faz handshake initialize.

        Args:
            project_root: Caminho raiz do projeto (opcional).

        Returns:
            dict com status da conexão.
        """
        with self._lock:
            if self._is_connected():
                return {"status": "success", "message": "LSP já conectado."}

            try:
                self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self._socket.settimeout(LSP_TIMEOUT)
                self._socket.connect((LSP_HOST, LSP_PORT))
            except (ConnectionRefusedError, socket.timeout, OSError) as e:
                self._socket = None
                return {
                    "status": "error",
                    "message": (
                        f"Não foi possível conectar ao LSP do Godot "
                        f"em {LSP_HOST}:{LSP_PORT}. "
                        f"O editor Godot está aberto? "
                        f"Erro: {e}"
                    ),
                }

            # Handshake initialize
            root_uri = project_root or ""
            if root_uri and not root_uri.startswith("file://"):
                root_uri = Path(root_uri).resolve().as_uri()

            init_params = {
                "processId": None,
                "rootUri": root_uri if root_uri else None,
                "capabilities": {
                    "textDocument": {
                        "hover": {"contentFormat": ["markdown", "plaintext"]},
                        "references": {},
                        "definition": {},
                        "documentSymbol": {},
                        "rename": {},
                        "publishDiagnostics": {},
                    }
                },
            }
            try:
                response = self._send_request("initialize", init_params)
                if response and "result" in response:
                    self._initialized = True
                    self._root_uri = root_uri
                    # Notifica o servidor que estamos prontos
                    self._send_notification("initialized", {})
                    return {
                        "status": "success",
                        "message": f"LSP conectado em {LSP_HOST}:{LSP_PORT}.",
                        "server_info": response["result"].get("serverInfo", {}),
                    }
                return {
                    "status": "error",
                    "message": f"Handshake LSP falhou: {response}",
                }
            except Exception as e:
                self._disconnect()
                return {
                    "status": "error",
                    "message": f"Erro no handshake LSP: {e}",
                }

    def disconnect(self) -> dict:
        """Desconecta do LSP."""
        with self._lock:
            if self._socket:
                try:
                    self._send_notification("shutdown", {})
                    self._send_notification("exit", {})
                except Exception:
                    pass
            self._disconnect()
            return {"status": "success", "message": "LSP desconectado."}

    def is_connected(self) -> bool:
        """Verifica se está conectado (thread-safe)."""
        with self._lock:
            return self._is_connected()

    # ── Operações LSP ────────────────────────────────────────────

    def get_references(
        self, file_path: str, line: int, character: int
    ) -> dict:
        """gdscript_references — achar referências a um símbolo."""
        uri = self._to_uri(file_path)
        params = {
            "textDocument": {"uri": uri},
            "position": {"line": line, "character": character},
            "context": {"includeDeclaration": True},
        }
        return self._lsp_call("textDocument/references", params)

    def get_definition(
        self, file_path: str, line: int, character: int
    ) -> dict:
        """gdscript_definition — navegar para definição."""
        uri = self._to_uri(file_path)
        params = {
            "textDocument": {"uri": uri},
            "position": {"line": line, "character": character},
        }
        return self._lsp_call("textDocument/definition", params)

    def get_hover(
        self, file_path: str, line: int, character: int
    ) -> dict:
        """gdscript_hover — tipo e documentação."""
        uri = self._to_uri(file_path)
        params = {
            "textDocument": {"uri": uri},
            "position": {"line": line, "character": character},
        }
        return self._lsp_call("textDocument/hover", params)

    def get_symbols(self, file_path: str) -> dict:
        """gdscript_symbols — listar símbolos de um arquivo."""
        uri = self._to_uri(file_path)
        params = {"textDocument": {"uri": uri}}
        return self._lsp_call("textDocument/documentSymbol", params)

    def rename_symbol(
        self, file_path: str, line: int, character: int, new_name: str
    ) -> dict:
        """gdscript_rename — renomear símbolo em todo projeto."""
        uri = self._to_uri(file_path)
        params = {
            "textDocument": {"uri": uri},
            "position": {"line": line, "character": character},
            "newName": new_name,
        }
        return self._lsp_call("textDocument/rename", params)

    def get_diagnostics(self, file_path: str) -> dict:
        """gdscript_diagnostics — erros e warnings."""
        uri = self._to_uri(file_path)
        # Força o LSP a re-analisar enviando didOpen + didChange
        try:
            self._send_notification("textDocument/didOpen", {
                "textDocument": {
                    "uri": uri,
                    "languageId": "gdscript",
                    "version": 1,
                    "text": self._read_file_content(file_path),
                }
            })
        except Exception:
            pass

        # Espera um pouco pelos diagnósticos (publicação assíncrona)
        time.sleep(0.3)

        # Tenta ler diagnósticos publicados
        try:
            raw = self._receive_message(timeout=1.0)
            if raw:
                msg = json.loads(raw)
                if msg.get("method") == "textDocument/publishDiagnostics":
                    diags = msg.get("params", {}).get("diagnostics", [])
                    return {
                        "status": "success",
                        "uri": uri,
                        "diagnostics": diags,
                        "count": len(diags),
                    }
        except Exception:
            pass

        return {
            "status": "success",
            "uri": uri,
            "diagnostics": [],
            "count": 0,
            "message": "Nenhum diagnóstico assíncrono recebido. Verifique o arquivo manualmente.",
        }

    def sync_file(self, file_path: str, content: str | None = None) -> dict:
        """gdscript_sync_file — notificar LSP sobre alteração."""
        uri = self._to_uri(file_path)
        text = content if content is not None else self._read_file_content(file_path)
        self._send_notification("textDocument/didChange", {
            "textDocument": {
                "uri": uri,
                "version": int(time.time()),
            },
            "contentChanges": [{"text": text}],
        })
        return {
            "status": "success",
            "uri": uri,
            "message": f"Arquivo sincronizado com LSP: {file_path}",
        }

    # ── Internals ────────────────────────────────────────────────

    def _lsp_call(self, method: str, params: dict) -> dict:
        """Executa uma chamada LSP e retorna resultado formatado."""
        if not self._is_connected():
            return {
                "status": "error",
                "message": (
                    "LSP não conectado. Use gdscript_lsp_connect primeiro "
                    "ou abra o editor Godot."
                ),
            }

        try:
            response = self._send_request(method, params)
            if response and "result" in response:
                return {"status": "success", "result": response["result"]}
            if response and "error" in response:
                return {
                    "status": "error",
                    "message": f"Erro LSP: {response['error']}",
                    "lsp_error": response["error"],
                }
            return {
                "status": "error",
                "message": f"Resposta LSP inesperada: {response}",
            }
        except socket.timeout:
            return {
                "status": "error",
                "message": f"Timeout LSP ao chamar '{method}'. Editor Godot响应?",
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Erro LSP ao chamar '{method}': {e}",
            }

    def _send_request(self, method: str, params: dict) -> dict | None:
        """Envia JSON-RPC request e retorna a resposta."""
        with self._lock:
            self._request_id += 1
            request = {
                "jsonrpc": "2.0",
                "id": self._request_id,
                "method": method,
                "params": params,
            }
            self._send_message(json.dumps(request))
            return self._receive_response()

    def _send_notification(self, method: str, params: dict) -> None:
        """Envia JSON-RPC notification (sem id, sem resposta)."""
        with self._lock:
            notification = {
                "jsonrpc": "2.0",
                "method": method,
                "params": params,
            }
            self._send_message(json.dumps(notification))

    def _send_message(self, data: str) -> None:
        """Envia mensagem com Content-Length header."""
        if not self._socket:
            raise ConnectionError("LSP não conectado.")
        payload = data.encode("utf-8")
        header = f"Content-Length: {len(payload)}\r\n\r\n"
        self._socket.sendall(header.encode("utf-8") + payload)

    def _receive_response(self, timeout: float = LSP_TIMEOUT) -> dict | None:
        """Recebe e parseia uma resposta JSON-RPC."""
        raw = self._receive_message(timeout)
        if raw:
            return json.loads(raw)
        return None

    def _receive_message(self, timeout: float = LSP_TIMEOUT) -> str | None:
        """Recebe uma mensagem LSP completa (Content-Length header + body)."""
        if not self._socket:
            return None

        self._socket.settimeout(timeout)
        try:
            # Lê headers até \r\n\r\n
            header_data = b""
            while b"\r\n\r\n" not in header_data:
                chunk = self._socket.recv(1)
                if not chunk:
                    return None
                header_data += chunk
                if len(header_data) > 8192:  # Safety limit
                    return None

            # Parse Content-Length
            header_str = header_data.decode("utf-8")
            content_length = 0
            for line in header_str.split("\r\n"):
                if line.lower().startswith("content-length:"):
                    content_length = int(line.split(":", 1)[1].strip())
                    break

            if content_length <= 0 or content_length > MAX_MESSAGE_SIZE:
                return None

            # Lê o body
            body = b""
            while len(body) < content_length:
                remaining = content_length - len(body)
                chunk = self._socket.recv(min(remaining, 65536))
                if not chunk:
                    break
                body += chunk

            return body.decode("utf-8")
        except socket.timeout:
            return None
        except Exception:
            return None

    def _is_connected(self) -> bool:
        """Verifica conexão (sem lock — chamar dentro de with self._lock)."""
        if self._socket is None:
            return False
        try:
            # Check if socket is still alive
            self._socket.settimeout(0.001)
            data = self._socket.recv(1, socket.MSG_PEEK)
            self._socket.settimeout(LSP_TIMEOUT)
            return True
        except (socket.timeout, BlockingIOError):
            self._socket.settimeout(LSP_TIMEOUT)
            return True  # Timeout on peek means socket is alive
        except (ConnectionResetError, OSError):
            self._disconnect()
            return False

    def _disconnect(self) -> None:
        """Força desconexão (sem lock)."""
        if self._socket:
            try:
                self._socket.close()
            except Exception:
                pass
            self._socket = None
            self._initialized = False

    @staticmethod
    def _to_uri(file_path: str) -> str:
        """Converte path para URI file://."""
        if file_path.startswith("file://"):
            return file_path
        return Path(file_path).resolve().as_uri()

    @staticmethod
    def _read_file_content(file_path: str) -> str:
        """Lê conteúdo do arquivo para sync."""
        try:
            return Path(file_path).read_text(encoding="utf-8")
        except Exception:
            return ""


# ── Singleton ───────────────────────────────────────────────────────

_client: LspClient | None = None


def _get_client() -> LspClient:
    """Retorna o cliente LSP singleton."""
    global _client
    if _client is None:
        _client = LspClient()
    return _client


# ── Tools MCP ───────────────────────────────────────────────────────

def gdscript_lsp_connect(project_root: str | None = None) -> dict:
    """Conecta ao Language Server do Godot na porta 6005.

    Use no início da sessão, após abrir o editor Godot.
    Pré-condições: Godot editor ABERTO com o projeto carregado.
    """
    return _get_client().connect(project_root)


def gdscript_lsp_disconnect() -> dict:
    """Desconecta do Language Server do Godot."""
    return _get_client().disconnect()


def gdscript_references(
    file_path: str, line: int, character: int
) -> dict:
    """Encontra todas as referências a um símbolo no código GDScript.

    Use para rastrear onde uma variável, função ou classe é usada.
    Args:
        file_path: Caminho do arquivo .gd (relativo ao projeto).
        line: Número da linha (0-indexed).
        character: Posição do caractere na linha (0-indexed).
    """
    return _get_client().get_references(file_path, line, character)


def gdscript_definition(
    file_path: str, line: int, character: int
) -> dict:
    """Navega para a definição de um símbolo GDScript.

    Use para encontrar onde uma variável, função ou classe foi definida.
    Args:
        file_path: Caminho do arquivo .gd.
        line: Número da linha (0-indexed).
        character: Posição do caractere (0-indexed).
    """
    return _get_client().get_definition(file_path, line, character)


def gdscript_hover(
    file_path: str, line: int, character: int
) -> dict:
    """Exibe tipo e documentação de um símbolo GDScript.

    Use para inspecionar o tipo de uma variável ou assinatura de função.
    Args:
        file_path: Caminho do arquivo .gd.
        line: Número da linha (0-indexed).
        character: Posição do caractere (0-indexed).
    """
    return _get_client().get_hover(file_path, line, character)


def gdscript_symbols(file_path: str) -> dict:
    """Lista todos os símbolos (funções, classes, variáveis) de um arquivo.

    Use para obter um índice da estrutura do arquivo.
    Args:
        file_path: Caminho do arquivo .gd.
    """
    return _get_client().get_symbols(file_path)


def gdscript_rename(
    file_path: str, line: int, character: int, new_name: str
) -> dict:
    """Renomeia um símbolo GDScript em todo o projeto com segurança semântica.

    Diferente de grep/replace, o LSP entende escopo e contexto.
    Args:
        file_path: Caminho do arquivo .gd.
        line: Número da linha (0-indexed).
        character: Posição do caractere (0-indexed).
        new_name: Novo nome para o símbolo.
    """
    return _get_client().rename_symbol(file_path, line, character, new_name)


def gdscript_diagnostics(file_path: str) -> dict:
    """Retorna erros e warnings do compilador GDScript para um arquivo.

    Diagnóstico em tempo real via LSP — mais preciso que validate_gdscript_syntax.
    Args:
        file_path: Caminho do arquivo .gd.
    """
    return _get_client().get_diagnostics(file_path)


def gdscript_sync_file(file_path: str, content: str | None = None) -> dict:
    """Notifica o LSP sobre alterações em um arquivo GDScript.

    Use após write_file para manter o LSP atualizado.
    Args:
        file_path: Caminho do arquivo .gd.
        content: Conteúdo atualizado (se None, lê do disco).
    """
    return _get_client().sync_file(file_path, content)
