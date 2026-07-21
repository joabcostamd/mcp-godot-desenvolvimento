"""domains/vfx/handlers.py — Handlers do domínio vfx (F5.6).

Wrappers keyword-only (*) que delegam para tools/vfx_ops.py e tools/devsolo_ops.py.
NÃO conhecem MCP, Tool, nem annotations.
"""

from typing import Any


def create_particles_2d(
    *,
    scene_path: str,
    parent_node_path: str,
    node_name: str = "Particles",
    amount: int | None = None,
    lifetime: float | None = None,
    explosiveness: float | None = None,
    direction: str | None = None,
    spread: float | None = None,
    gravity: str | None = None,
) -> dict:
    """Cria GPUParticles2D com ParticleProcessMaterial em uma cena."""
    from tools.vfx_ops import create_particles_2d as _impl
    return _impl(
        scene_path=scene_path,
        parent_node_path=parent_node_path,
        node_name=node_name,
        amount=amount,
        lifetime=lifetime,
        explosiveness=explosiveness,
        direction=direction,
        spread=spread,
        gravity=gravity,
    )


def configure_particles_2d(
    *,
    scene_path: str,
    node_path: str,
    amount: int = 50,
    lifetime: float = 1.0,
    explosiveness: float = 0.0,
    emitting: bool = True,
    one_shot: bool = False,
    preset: str = "custom",
) -> dict:
    """Configura partículas 2D existentes com parâmetros visuais e presets."""
    from tools.devsolo_ops import configure_particles_2d as _impl
    return _impl(
        scene_path=scene_path,
        node_path=node_path,
        amount=amount,
        lifetime=lifetime,
        explosiveness=explosiveness,
        emitting=emitting,
        one_shot=one_shot,
        preset=preset,
    )


def create_particles_3d(
    *,
    scene_path: str,
    parent_node_path: str = ".",
    node_name: str = "GPUParticles3D",
    preset: str = "fire",
) -> dict:
    """Cria partículas 3D com predefinição visual (fire, smoke, sparkles)."""
    from tools.devsolo_ops import create_particles_3d as _impl
    return _impl(
        scene_path=scene_path,
        parent_node_path=parent_node_path,
        node_name=node_name,
        preset=preset,
    )


def setup_screen_flash(
    *,
    scene_path: str,
    parent_node_path: str = ".",
    color: str = "#ffffff",
    duration: float = 0.15,
    fade_out: float = 0.1,
) -> dict:
    """Cria efeito de flash de tela (ex: ao tomar dano)."""
    from tools.devsolo_ops import setup_screen_flash as _impl
    return _impl(
        scene_path=scene_path,
        parent_node_path=parent_node_path,
        color=color,
        duration=duration,
        fade_out=fade_out,
    )


def setup_world_environment(
    *,
    scene_path: str,
    parent_node_path: str = ".",
    background_mode: str = "color",
    background_color: str = "#1a1a2e",
    ambient_light_color: str = "#333344",
    ambient_light_energy: float = 1.0,
    glow_enabled: bool = False,
    glow_intensity: float = 0.8,
    fog_enabled: bool = False,
    fog_density: float = 0.01,
    fog_color: str = "#1a1a2e",
) -> dict:
    """Configura o ambiente visual da cena (WorldEnvironment)."""
    from tools.devsolo_ops import setup_world_environment as _impl
    return _impl(
        scene_path=scene_path,
        parent_node_path=parent_node_path,
        background_mode=background_mode,
        background_color=background_color,
        ambient_light_color=ambient_light_color,
        ambient_light_energy=ambient_light_energy,
        glow_enabled=glow_enabled,
        glow_intensity=glow_intensity,
        fog_enabled=fog_enabled,
        fog_density=fog_density,
        fog_color=fog_color,
    )


__all__ = [
    "create_particles_2d",
    "configure_particles_2d",
    "create_particles_3d",
    "setup_screen_flash",
    "setup_world_environment",
]
