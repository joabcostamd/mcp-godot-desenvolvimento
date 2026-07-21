"""registry/ — Fonte única de verdade para tools, handlers e curadoria.

Substitui o sistema legado de múltiplos registros (core/tool_definitions.py,
tools/rollups.py, TOOLSETS, PHASE_TOOLSETS, _build_handlers).

Uso:
    from registry import build_tool_defs, build_handlers
    tools = build_tool_defs(phase="PROTOTIPO")
    handlers = build_handlers()
"""

from .discovery import build_tool_defs, build_handlers, discover, invalidate_caches
from .types import DomainManifest, OpSpec, Phase

__all__ = [
    "build_tool_defs",
    "build_handlers",
    "discover",
    "invalidate_caches",
    "DomainManifest",
    "OpSpec",
    "Phase",
]
