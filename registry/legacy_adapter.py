"""registry/legacy_adapter.py — Adaptador de legado (Fase 1.2).

Enquanto os domínios não são migrados, lê o sistema legado
(core/tool_definitions.py, tools/rollups.py, TOOLSETS, PHASE_TOOLSETS)
e produz a mesma saída que o registry produziria com manifestos reais.

IMPORTANTE: O comportamento externo (tools/list) deve ser BYTE-IDÊNTICO
ao sistema legado. Validar com fc (File Compare).
"""

from __future__ import annotations

from typing import Any, Callable
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from mcp.types import Tool


def build_tool_defs_legacy(phase: str | None = None) -> list[Tool]:
    """Constrói tool definitions a partir do sistema legado.

    Wrapper sobre server._tool_defs() que garante compatibilidade
    byte-idêntica durante a transição.

    Args:
        phase: Fase opcional (ignorada — o legado usa _get_phase_tools internamente).

    Returns:
        Lista de Tool objects idêntica à retornada por server._tool_defs().
    """
    from server import _tool_defs
    return _tool_defs()


def build_handlers_legacy() -> dict[str, Callable[[dict], dict]]:
    """Constrói handlers a partir do sistema legado.

    Returns:
        Dict idêntico ao retornado por server._build_handlers().
    """
    from server import _build_handlers
    return _build_handlers()


def get_phase_tools_legacy() -> set[str]:
    """Retorna o set de tools visíveis na fase atual (legado)."""
    from server import _get_phase_tools
    return _get_phase_tools()


def get_toolsets_legacy() -> dict[str, list[str]]:
    """Retorna o TOOLSETS legado."""
    from server import TOOLSETS
    return dict(TOOLSETS)


def get_phase_toolsets_legacy() -> dict[str, set[str]]:
    """Retorna o PHASE_TOOLSETS legado."""
    from server import PHASE_TOOLSETS, PHASE_TOOLS_CORE
    return {
        "CORE": set(PHASE_TOOLS_CORE),
        **{k: set(v) for k, v in PHASE_TOOLSETS.items()},
    }
