"""registry/discovery.py — Descoberta de domínios (Fase 1.3).

Varre domains/ em busca de manifest.py e agrega os DomainManifest.
Enquanto domains/ está vazio, delega ao legacy_adapter.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from mcp.types import Tool
from .types import DomainManifest

# Cache
_manifests: list[DomainManifest] | None = None


def discover() -> list[DomainManifest]:
    """Varre domains/ e retorna todos os manifestos encontrados.

    Ordem: primeiro os manifestos reais (domains/<x>/manifest.py),
    depois o adaptador de legado (ferramentas ainda não migradas).
    """
    global _manifests
    if _manifests is not None:
        return _manifests

    manifests: list[DomainManifest] = []

    # 1. Domínios migrados
    domains_dir = ROOT / "domains"
    if domains_dir.exists():
        for manifest_file in sorted(domains_dir.glob("*/manifest.py")):
            domain_dir = manifest_file.parent
            if domain_dir.name.startswith("_") or domain_dir.name.startswith("__"):
                continue
            try:
                # Importa o módulo de manifesto
                import importlib.util
                spec = importlib.util.spec_from_file_location(
                    f"domains.{domain_dir.name}.manifest",
                    str(manifest_file)
                )
                if spec and spec.loader:
                    mod = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(mod)
                    if hasattr(mod, "MANIFEST"):
                        manifests.append(mod.MANIFEST)
            except Exception:
                # Manifesto quebrado não deve travar o sistema
                pass

    # 2. Legado (ferramentas ainda não migradas)
    # O legado não produz DomainManifest — é tratado separadamente
    # pelo legacy_adapter.build_tool_defs_legacy()

    _manifests = manifests
    return manifests


def build_tool_defs(phase: str | None = None) -> list[Tool]:
    """Constrói a lista final de Tool definitions.

    Combina ferramentas de domínios migrados (via manifestos)
    com ferramentas legadas (via legacy_adapter).

    Args:
        phase: Fase atual. Se None, usa _get_phase_tools() do legado.

    Returns:
        Lista de Tool objects pronta para tools/list.
    """
    from .legacy_adapter import build_tool_defs_legacy

    # Por enquanto, 100% legado — comportamento byte-idêntico
    return build_tool_defs_legacy(phase)


def build_handlers() -> dict[str, Callable[[dict], dict]]:
    """Constrói o dicionário de handlers.

    Combina handlers de domínios migrados com legados.

    Returns:
        Dict {tool_name: handler_fn}.
    """
    from .legacy_adapter import build_handlers_legacy
    return build_handlers_legacy()


def invalidate_caches() -> None:
    """Invalida todos os caches do registry."""
    global _manifests
    _manifests = None
    # Também invalida o cache legado
    import server
    server._TOOL_DEFS_CACHE = None
    server._HANDLERS_CACHE = None
