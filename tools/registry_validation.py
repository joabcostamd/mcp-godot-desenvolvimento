"""registry_validation.py — Validação de consistência do registro de tools.

Compara as 3 fontes de verdade:
  1. _tool_defs() — Tool() definitions
  2. _build_handlers() — handlers executáveis
  3. TOOLSETS + PHASE_TOOLSETS — categorização por fase

Detecta 3 categorias de divergência:
  - tools_sem_handler: Tool() existe mas não tem handler (não implementada)
  - handlers_sem_tool_def: handler existe mas não tem Tool() (código morto)
  - tools_sem_categoria: funcional mas ausente de TOOLSETS/PHASE_TOOLSETS

Uso interno (boot) e exposto como tool MCP validate_mcp_registry.
"""

from __future__ import annotations

import sys
from typing import Any


def validate_tool_registry_consistency() -> dict[str, Any]:
    """Executa validação completa de consistência do registro de tools.

    Temporariamente define _REGISTRY_VALIDATION_UNFILTERED = True para
    acessar os conjuntos COMPLETOS (pré-filtro de depreciação, fase,
    toolsets e profile). Restaura o estado original após a coleta.

    Returns:
        dict com keys:
          - tools_sem_handler: list[str] — nomes com Tool() mas sem handler
          - handlers_sem_tool_def: list[str] — nomes com handler mas sem Tool()
          - tools_sem_categoria: list[str] — nomes funcionais mas sem fase
          - counts: dict com contagens de cada categoria
          - totals: dict com totais de cada fonte
    """
    import server

    # ── Salvar estado atual ───────────────────────────────────────
    saved_unfiltered = getattr(server, "_REGISTRY_VALIDATION_UNFILTERED", False)
    saved_enabled = server._ENABLED_TOOLS
    saved_profile = server._PROFILE_TOOLS
    saved_get_phase = server._get_phase_tools

    try:
        # ── Ativar modo unfiltered ────────────────────────────────
        server._REGISTRY_VALIDATION_UNFILTERED = True
        server._ENABLED_TOOLS = None
        server._PROFILE_TOOLS = None
        server._get_phase_tools = lambda: server.PHASE_TOOLS_CORE  # type: ignore[assignment]

        # ── Invalidar caches para forçar rebuild ──────────────────
        server._invalidate_tool_caches()

        # ── Coletar nomes ─────────────────────────────────────────
        tool_def_names: set[str] = {t.name for t in server._tool_defs()}
        handler_names: set[str] = set(server._build_handlers().keys())

        # ── Coletar união de TOOLSETS + PHASE_TOOLSETS ────────────
        categorized: set[str] = set()
        for names in server.TOOLSETS.values():
            categorized.update(names)
        for names in server.PHASE_TOOLSETS.values():
            categorized.update(names)

    finally:
        # ── Restaurar estado original ─────────────────────────────
        server._REGISTRY_VALIDATION_UNFILTERED = saved_unfiltered
        server._ENABLED_TOOLS = saved_enabled
        server._PROFILE_TOOLS = saved_profile
        server._get_phase_tools = saved_get_phase  # type: ignore[assignment]
        server._invalidate_tool_caches()

    # ── Calcular divergências ─────────────────────────────────────
    tools_sem_handler = tool_def_names - handler_names
    handlers_sem_tool_def = handler_names - tool_def_names
    tools_sem_categoria = (tool_def_names & handler_names) - categorized

    result = {
        "tools_sem_handler": sorted(tools_sem_handler),
        "handlers_sem_tool_def": sorted(handlers_sem_tool_def),
        "tools_sem_categoria": sorted(tools_sem_categoria),
        "counts": {
            "tools_sem_handler": len(tools_sem_handler),
            "handlers_sem_tool_def": len(handlers_sem_tool_def),
            "tools_sem_categoria": len(tools_sem_categoria),
        },
        "totals": {
            "tool_defs": len(tool_def_names),
            "handlers": len(handler_names),
            "categorized": len(categorized),
        },
    }

    # ── Logar no stderr (NUNCA stdout — protege protocolo MCP) ───
    _log_report(result)

    return result


def _log_report(result: dict[str, Any]) -> None:
    """Loga relatório formatado no stderr."""
    counts = result["counts"]
    totals = result["totals"]

    print(
        f"\n[MCP] ═══ Validação de Consistência do Registro ═══",
        file=sys.stderr,
    )
    print(
        f"[MCP] Totais: {totals['tool_defs']} tool_defs, "
        f"{totals['handlers']} handlers, "
        f"{totals['categorized']} categorizados (TOOLSETS+PHASE_TOOLSETS)",
        file=sys.stderr,
    )

    # Categoria 1: tools sem handler
    if counts["tools_sem_handler"] > 0:
        print(
            f"[MCP] [WARNING] {counts['tools_sem_handler']} tools com Tool() "
            f"mas SEM handler (não implementadas):",
            file=sys.stderr,
        )
        for name in result["tools_sem_handler"]:
            print(f"[MCP]   - {name}", file=sys.stderr)

    # Categoria 2: handlers sem tool_def
    if counts["handlers_sem_tool_def"] > 0:
        print(
            f"[MCP] [WARNING] {counts['handlers_sem_tool_def']} handlers "
            f"funcionais mas SEM Tool() (código morto/inacessível):",
            file=sys.stderr,
        )
        for name in result["handlers_sem_tool_def"]:
            print(f"[MCP]   - {name}", file=sys.stderr)

    # Categoria 3: tools funcionais sem categoria
    if counts["tools_sem_categoria"] > 0:
        print(
            f"[MCP] [INFO] {counts['tools_sem_categoria']} tools funcionais "
            f"(Tool() + handler) mas NÃO categorizadas em TOOLSETS/PHASE_TOOLSETS:",
            file=sys.stderr,
        )
        for name in result["tools_sem_categoria"]:
            print(f"[MCP]   - {name}", file=sys.stderr)

    if all(counts[k] == 0 for k in counts):
        print("[MCP] ✓ Nenhuma divergência encontrada.", file=sys.stderr)

    print(file=sys.stderr)


def validate_mcp_registry_handler(args: dict) -> dict[str, Any]:
    """Handler da tool MCP validate_mcp_registry.

    Retorna o relatório completo de consistência em JSON.
    Não requer parâmetros — args é ignorado.
    """
    return validate_tool_registry_consistency()
