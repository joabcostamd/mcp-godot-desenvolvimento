"""editor_safety.py — Protocolo anti-conflito MCP ↔ editor Godot (Fatia 0.H).

Antes de qualquer escrita em .tscn, .tres ou .gd, verifica se o arquivo
tem alterações não salvas no editor do Godot.

3 cenários:
  - Bridge disponível, arquivo limpo → escrita permitida
  - Bridge disponível, arquivo sujo → escrita BLOQUEADA com mensagem
  - Bridge indisponível (Godot fechado) → escrita permitida com aviso (fail-open)
"""

import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger("mcp-godot.editor_safety")

# Extensões de arquivo que o Godot edita e que podem ter conflito
EDITABLE_EXTENSIONS = {".tscn", ".tres", ".gd", ".gdshader", ".resource"}

# Timeout para verificação (não bloquear o servidor)
CHECK_TIMEOUT = 2.0


def _is_godot_editable_file(filepath: str) -> bool:
    """Verifica se o arquivo é do tipo que o Godot edita."""
    return Path(filepath).suffix.lower() in EDITABLE_EXTENSIONS


def _check_bridge_availability() -> tuple[bool, Any]:
    """Verifica se o addon bridge está conectado.

    Returns:
        (available, bridge) — se available=False, bridge é None.
    """
    try:
        from tools.addon_bridge import get_bridge
        bridge = get_bridge()
        if bridge.is_available():
            return True, bridge
        return False, None
    except Exception:
        return False, None


def check_editor_conflict(filepath: str) -> dict:
    """Verifica se o arquivo tem alterações não salvas no editor Godot.

    Deve ser chamada ANTES de qualquer operação de escrita.

    Args:
        filepath: Caminho do arquivo que será escrito.

    Returns:
        dict com:
            - safe: bool — True se pode escrever
            - blocked: bool — True se bloqueado por conflito
            - message: str — mensagem explicativa
            - bridge_available: bool — se o bridge respondeu
    """
    # Só verifica arquivos que o Godot edita
    if not _is_godot_editable_file(filepath):
        return {
            "safe": True,
            "blocked": False,
            "message": "Arquivo não é editável pelo Godot — verificação pulada.",
            "bridge_available": False,
        }

    available, bridge = _check_bridge_availability()

    if not available or bridge is None:
        # Godot fechado ou bridge caído — fail-open com aviso
        logger.warning(
            "Bridge indisponível — escrita em %s prossegue sem verificação de conflito.",
            filepath,
        )
        return {
            "safe": True,
            "blocked": False,
            "message": (
                "Godot não está conectado. Escrita permitida, mas "
                "certifique-se de que o arquivo não está aberto no editor."
            ),
            "bridge_available": False,
        }

    # Bridge disponível — verificar estado do arquivo
    try:
        result = bridge.call(
            "check_file_modified",
            {"path": filepath},
            timeout=CHECK_TIMEOUT,
        )

        if isinstance(result, dict):
            is_modified = result.get("modified", False)
            if is_modified:
                logger.warning(
                    "CONFLITO: %s tem alterações não salvas no Godot. Escrita BLOQUEADA.",
                    filepath,
                )
                return {
                    "safe": False,
                    "blocked": True,
                    "message": (
                        f"O arquivo '{filepath}' está aberto no Godot com "
                        f"alterações não salvas. Salve (Ctrl+S) no Godot "
                        f"e tente novamente."
                    ),
                    "bridge_available": True,
                }
            else:
                return {
                    "safe": True,
                    "blocked": False,
                    "message": "Arquivo sem alterações no editor — escrita permitida.",
                    "bridge_available": True,
                }
    except Exception as e:
        # Erro na comunicação — fail-open com aviso
        logger.warning(
            "Erro ao verificar arquivo %s via bridge: %s. Escrita prossegue.",
            filepath, e,
        )
        return {
            "safe": True,
            "blocked": False,
            "message": (
                f"Não foi possível verificar o arquivo no Godot "
                f"(erro: {e}). Escrita permitida com aviso."
            ),
            "bridge_available": True,
        }

    # Fallback (não deve chegar aqui)
    return {
        "safe": True,
        "blocked": False,
        "message": "Verificação inconclusiva — escrita permitida (fail-open).",
        "bridge_available": available,
    }
