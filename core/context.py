"""core/context.py — ExecutionContext (Etapa A2).

Fornece contexto de execução injetado automaticamente ANTES de cada
invocação de tool. Similar ao padrão Flask "request context" — um
objeto thread-local acessível por qualquer handler.

Motivação: a IA nunca mais precisa digitar `scene_path` ou `project_path`
— o contexto resolve automaticamente.

Cache: `scene_tree` tem TTL de 5 segundos para evitar re-resolução
a cada chamada consecutiva.

Uso:
    from core.context import get_execution_context

    ctx = get_execution_context()
    scene = ctx.active_scene  # str | None
    proj = ctx.active_project  # Path
"""

from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class ExecutionContext:
    """Contexto completo disponível durante a execução de uma tool.

    Resolvido UMA vez por invocação e cacheado com TTL de 5s para
    propriedades caras (scene_tree).
    """

    # ── Resolvidos na criação ──
    active_project: Path | None = None
    """Projeto Godot ativo (resolve de _get_active_project)."""

    active_scene: str | None = None
    """Cena atualmente em foco (Vibe Coding Mode ou último acesso)."""

    phase: str = "IDEIA"
    """Fase atual do projeto (IDEIA → DESIGN → PROTOTIPO → ...)."""

    vibe_enabled: bool = False
    """Se o Vibe Coding Mode está ativo."""

    vibe_focus_node: str | None = None
    """Nó em foco no Vibe Coding Mode."""

    # ── Cache TTL ──
    _scene_tree_cache: dict[str, Any] | None = field(default=None, repr=False)
    _scene_tree_ts: float = field(default=0.0, repr=False)

    # ── Metadados ──
    created_at: float = field(default_factory=time.time)
    tool_name: str = ""

    @property
    def project_path_str(self) -> str:
        """Caminho do projeto como string (para compatibilidade)."""
        return str(self.active_project) if self.active_project else ""

    def get_scene_tree(self, ttl: float = 5.0) -> dict[str, Any] | None:
        """Retorna a árvore de cenas do projeto com cache TTL.

        Args:
            ttl: Tempo de vida do cache em segundos (default 5s).

        Returns:
            Dict com a árvore de cenas ou None se indisponível.
        """
        now = time.time()
        if self._scene_tree_cache is not None and (now - self._scene_tree_ts) < ttl:
            return self._scene_tree_cache

        try:
            from tools.scene_ops import load_scene_tree
            result = load_scene_tree()
            if isinstance(result, dict) and result.get("status") == "success":
                self._scene_tree_cache = result
                self._scene_tree_ts = now
                return result
        except Exception:
            pass
        return None

    def invalidate_cache(self) -> None:
        """Invalida todos os caches (útil após mutações na cena)."""
        self._scene_tree_cache = None
        self._scene_tree_ts = 0.0


# ══════════════════════════════════════════════════════════════
# Thread-local storage (similar ao Flask `_app_ctx_stack`)
# ══════════════════════════════════════════════════════════════

_local = threading.local()


def get_execution_context() -> ExecutionContext | None:
    """Retorna o ExecutionContext da thread atual.

    Retorna None se chamado fora de um call_tool (ex: durante import).
    """
    return getattr(_local, "execution_context", None)


def set_execution_context(ctx: ExecutionContext | None) -> None:
    """Define o ExecutionContext da thread atual."""
    _local.execution_context = ctx


def resolve_execution_context(tool_name: str = "") -> ExecutionContext:
    """Cria um ExecutionContext com todos os campos resolvidos.

    Deve ser chamado UMA vez por invocação de tool, dentro de call_tool().

    Args:
        tool_name: Nome da tool sendo invocada (para logging).

    Returns:
        ExecutionContext populado com projeto ativo, cena, fase, etc.
    """
    ctx = ExecutionContext(tool_name=tool_name)

    # ── Projeto ativo ──
    try:
        from tools.project_ops import _get_active_project
        ctx.active_project = _get_active_project()
    except Exception:
        pass

    # ── Cena ativa (Vibe Coding Mode) ──
    try:
        from tools.vibe_ops import get_vibe_context
        vibe = get_vibe_context()
        vibe_cfg = vibe.get("vibe_coding", {}) if isinstance(vibe, dict) else {}
        ctx.vibe_enabled = vibe_cfg.get("enabled", False)
        if ctx.vibe_enabled:
            ctx.active_scene = vibe_cfg.get("scene_path")
            ctx.vibe_focus_node = vibe_cfg.get("focus_node")
    except Exception:
        pass

    # ── Fase atual ──
    try:
        from tools.phase_ops import get_current_phase
        phase_result = get_current_phase()
        if isinstance(phase_result, dict):
            ctx.phase = phase_result.get("current_phase", "IDEIA")
    except Exception:
        pass

    return ctx
