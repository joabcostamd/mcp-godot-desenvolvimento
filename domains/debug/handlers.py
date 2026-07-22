"""domains/debug/handlers.py — Handlers do domínio debug (F5.9).

Wrappers keyword-only (*) que delegam para tools/debugger_ops.py, tools/devsolo_ops.py e tools/perf_ops.py.
NÃO conhecem MCP, Tool, nem annotations.
"""

from typing import Any


def get_performance_stats() -> dict:
    """Obtém estatísticas de performance (FPS, memória, draw calls)."""
    from tools.devsolo_ops import get_performance_stats as _impl
    return _impl()


def enable_debug_collisions(*, enabled: bool = True) -> dict:
    """Ativa/desativa visualização de debug de colisões no editor."""
    from tools.devsolo_ops import enable_debug_collisions as _impl
    return _impl(enabled=enabled)


def enable_debug_navigation(*, enabled: bool = True) -> dict:
    """Ativa/desativa visualização de debug de navegação no editor."""
    from tools.devsolo_ops import enable_debug_navigation as _impl
    return _impl(enabled=enabled)


def perf_regression_track(*, args: dict | None = None) -> dict:
    """Registra métricas de performance para detecção de regressão."""
    from tools.perf_ops import perf_regression_track as _impl
    return _impl(args=args)


def debugger_set_breakpoint(
    *, script_path: str, line: int, condition: str | None = None
) -> dict:
    """Define um breakpoint em um script GDScript."""
    from tools.debugger_ops import debugger_set_breakpoint as _impl
    return _impl(script_path=script_path, line=line, condition=condition)


def debugger_status() -> dict:
    """Verifica estado do debugger (disponível, host, porta)."""
    from tools.debugger_ops import debugger_status as _impl
    return _impl()


def debugger_step(*, step_type: str = "over") -> dict:
    """Avança execução: over (próxima linha), into (entrar), out (sair)."""
    from tools.debugger_ops import debugger_step as _impl
    return _impl(step_type=step_type)


def debugger_get_stack() -> dict:
    """Obtém stack trace atual do debugger."""
    from tools.debugger_ops import debugger_get_stack as _impl
    return _impl()


def debugger_get_variables(*, variable_name: str | None = None) -> dict:
    """Inspeciona variáveis no escopo atual do debugger."""
    from tools.debugger_ops import debugger_get_variables as _impl
    return _impl(variable_name=variable_name)


__all__ = [
    "get_performance_stats",
    "enable_debug_collisions",
    "enable_debug_navigation",
    "perf_regression_track",
    "debugger_set_breakpoint",
    "debugger_status",
    "debugger_step",
    "debugger_get_stack",
    "debugger_get_variables",
]
