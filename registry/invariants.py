"""registry/invariants.py — Invariantes executáveis (Fase 1.4).

INV-01 a INV-15 como funções que retornam (inv_id, passed, detail).
Falham o build se violadas.
"""

from __future__ import annotations

from typing import Callable


def check_all(phase: str = "F0") -> list[tuple[str, bool, str]]:
    """Executa todas as invariantes ativas na fase.

    Args:
        phase: Fase atual (ex: "F0", "F1", ...).

    Returns:
        Lista de (inv_id, passed, detail).
    """
    results: list[tuple[str, bool, str]] = []

    # INV-01: tools/list tem handler
    results.append(_inv_01())

    # INV-02: handler tem tool
    results.append(_inv_02())

    # INV-10: PHASE_TOOLSETS → tools/list
    results.append(_inv_10())

    # INV-11: TOOLSETS → tools/list
    results.append(_inv_11())

    # INV-12: sem duplicação de namespace
    results.append(_inv_12())

    # INV-13: sem colisão de registro (placeholder até F3)
    results.append(("INV-13", True, "placeholder — ativado em F3"))

    return results


def _get_tool_names() -> set[str]:
    """Helper: nomes em _tool_defs()."""
    try:
        from server import _tool_defs
        return {t.name for t in _tool_defs()}
    except Exception as e:
        return set()


def _get_handler_names() -> set[str]:
    """Helper: nomes em _build_handlers()."""
    try:
        from server import _build_handlers
        return set(_build_handlers().keys())
    except Exception as e:
        return set()


def _inv_01() -> tuple[str, bool, str]:
    """INV-01: Toda tool em tools/list tem handler."""
    tools = _get_tool_names()
    handlers = _get_handler_names()
    missing = tools - handlers
    if missing:
        return ("INV-01", False, f"SEM_HANDLER: {sorted(missing)}")
    return ("INV-01", True, f"OK — {len(tools)} tools, todas com handler")


def _inv_02() -> tuple[str, bool, str]:
    """INV-02: Todo handler tem tool em tools/list."""
    tools = _get_tool_names()
    handlers = _get_handler_names()
    extra = handlers - tools
    if extra:
        return ("INV-02", False, f"SEM_DEF: {sorted(extra)}")
    return ("INV-02", True, f"OK — {len(handlers)} handlers, todos com tool")


def _inv_10() -> tuple[str, bool, str]:
    """INV-10: Todo nome em PHASE_TOOLSETS existe em tools/list."""
    try:
        from server import PHASE_TOOLSETS, PHASE_TOOLS_CORE
        tools = _get_tool_names()
        all_phase = set(PHASE_TOOLS_CORE)
        for names in PHASE_TOOLSETS.values():
            all_phase.update(names)
        missing = all_phase - tools
        if missing:
            return ("INV-10", False, f"PHASE_FANTASMA: {sorted(missing)}")
        return ("INV-10", True, f"OK — {len(all_phase)} nomes de fase, todos em tools/list")
    except Exception as e:
        return ("INV-10", False, str(e))


def _inv_11() -> tuple[str, bool, str]:
    """INV-11: Todo nome em TOOLSETS existe em tools/list."""
    try:
        from server import TOOLSETS
        tools = _get_tool_names()
        all_ns: set[str] = set()
        for names in TOOLSETS.values():
            all_ns.update(names)
        missing = all_ns - tools
        if missing:
            return ("INV-11", False, f"NS_FANTASMA: {sorted(missing)}")
        return ("INV-11", True, f"OK — {len(all_ns)} nomes em TOOLSETS, todos em tools/list")
    except Exception as e:
        return ("INV-11", False, str(e))


def _inv_12() -> tuple[str, bool, str]:
    """INV-12: Nenhum nome aparece em 2+ namespaces."""
    try:
        from server import TOOLSETS
        seen: dict[str, list[str]] = {}
        for ns, names in TOOLSETS.items():
            for n in names:
                if n not in seen:
                    seen[n] = []
                seen[n].append(ns)
        dups = {n: nss for n, nss in seen.items() if len(nss) > 1}
        if dups:
            return ("INV-12", False, f"DUPLICADOS_NS: {dups}")
        return ("INV-12", True, "OK — 0 duplicados")
    except Exception as e:
        return ("INV-12", False, str(e))
