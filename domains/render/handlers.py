"""domains/render/handlers.py — Handlers do domínio render (F5.7).

Wrappers keyword-only (*) que delegam para tools/render_ops.py.
NÃO conhecem MCP, Tool, nem annotations.
"""

from typing import Any


def get_render_settings(*, project_path: str | None = None) -> dict:
    """Obtém as configurações de rendering do projeto (project.godot)."""
    from tools.render_ops import get_render_settings as _impl
    return _impl(project_path=project_path)


def set_antialiasing(
    *,
    project_path: str | None = None,
    msaa: str | None = None,
    fxaa: bool | None = None,
    taa: bool | None = None,
    screen_space_aa: str | None = None,
) -> dict:
    """Configura antialiasing: MSAA (disabled/2x/4x/8x), FXAA, TAA."""
    from tools.render_ops import set_antialiasing as _impl
    return _impl(
        project_path=project_path,
        msaa=msaa,
        fxaa=fxaa,
        taa=taa,
        screen_space_aa=screen_space_aa,
    )


def set_scaling_mode(
    *,
    project_path: str | None = None,
    mode: str | None = None,
    scale: float | None = None,
    stretch_mode: str | None = None,
    stretch_aspect: str | None = None,
) -> dict:
    """Configura modo de scaling/resolução da janela."""
    from tools.render_ops import set_scaling_mode as _impl
    return _impl(
        project_path=project_path,
        mode=mode,
        scale=scale,
        stretch_mode=stretch_mode,
        stretch_aspect=stretch_aspect,
    )


def set_render_quality(
    *,
    project_path: str | None = None,
    preset: str = "balanced",
    shadows: str | None = None,
    gi: str | None = None,
    reflections: str | None = None,
    particles: str | None = None,
) -> dict:
    """Configura qualidade de rendering (low/balanced/high/ultra)."""
    from tools.render_ops import set_render_quality as _impl
    return _impl(
        project_path=project_path,
        preset=preset,
        shadows=shadows,
        gi=gi,
        reflections=reflections,
        particles=particles,
    )


__all__ = [
    "get_render_settings",
    "set_antialiasing",
    "set_scaling_mode",
    "set_render_quality",
]
