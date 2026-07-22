"""domains/runtime/handlers.py — Handlers do domínio runtime (F5.13).

Wrappers keyword-only (*) que delegam para tools/runtime_ops.py.
NÃO conhecem MCP, Tool, nem annotations.
"""

from typing import Any


def compile_test() -> dict:
    """Executa compile_test no projeto ativo (--headless --quit)."""
    from tools.runtime_ops import compile_test as _impl
    return _impl()


def run_game(*, scene_path: str | None = None, wait_for_bridge: bool = True) -> dict:
    """Inicia o jogo como subprocesso (não bloqueante)."""
    from tools.runtime_ops import run_game as _impl
    return _impl(scene_path=scene_path, wait_for_bridge=wait_for_bridge)


def stop_game() -> dict:
    """Encerra o jogo em execução e retorna tail do console."""
    from tools.runtime_ops import stop_game as _impl
    return _impl()


def smart_restart(*, project_path: str | None = None) -> dict:
    """Reinício inteligente: stop → copia addon → compila → inicia → conecta bridge."""
    from tools.runtime_ops import smart_restart as _impl
    return _impl(project_path=project_path)


def launch_editor(*, scene_path: str | None = None) -> dict:
    """Abre o editor Godot com o addon mcp_addon instalado."""
    from tools.runtime_ops import launch_editor as _impl
    return _impl(scene_path=scene_path)


def close_editor() -> dict:
    """Fecha o editor Godot."""
    from tools.runtime_ops import close_editor as _impl
    return _impl()


__all__ = [
    "compile_test",
    "run_game",
    "stop_game",
    "smart_restart",
    "launch_editor",
    "close_editor",
]
