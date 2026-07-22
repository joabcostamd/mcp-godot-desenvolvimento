"""domains/d3/handlers.py — Handlers do domínio d3 (F5.15).

Wrappers keyword-only (*) que delegam para tools/devsolo_ops.py.
NÃO conhecem MCP, Tool, nem annotations.
"""

from typing import Any


def create_light_3d(
    *, scene_path: str, parent_node_path: str = ".", light_type: str = "omni",
    color: str = "#ffffff", energy: float = 1.0, shadows: bool = False,
    node_name: str = "",
) -> dict:
    """Cria luz 3D (OmniLight3D, SpotLight3D, DirectionalLight3D)."""
    from tools.devsolo_ops import create_light_3d as _impl
    return _impl(scene_path=scene_path, parent_node_path=parent_node_path, light_type=light_type,
                 color=color, energy=energy, shadows=shadows, node_name=node_name)


def create_csg_shape(
    *, scene_path: str, parent_node_path: str = ".", shape_type: str = "box",
    dimensions: list[float] | None = None, node_name: str = "",
) -> dict:
    """Cria geometria CSG 3D para blockout rápido (box, sphere, cylinder)."""
    from tools.devsolo_ops import create_csg_shape as _impl
    return _impl(scene_path=scene_path, parent_node_path=parent_node_path, shape_type=shape_type,
                 dimensions=dimensions, node_name=node_name)


def configure_standard_material_3d(
    *, scene_path: str, node_path: str, albedo_color: str = "#ffffff",
    metallic: float = 0.0, roughness: float = 0.5, emission_color: str = "#000000",
    emission_energy: float = 0.0, preset: str = "custom",
) -> dict:
    """Configura StandardMaterial3D com presets (metal, wood, plastic, glass, emissive)."""
    from tools.devsolo_ops import configure_standard_material_3d as _impl
    return _impl(scene_path=scene_path, node_path=node_path, albedo_color=albedo_color,
                 metallic=metallic, roughness=roughness, emission_color=emission_color,
                 emission_energy=emission_energy, preset=preset)


def create_particles_3d(
    *, scene_path: str, parent_node_path: str = ".", node_name: str = "GPUParticles3D",
    preset: str = "fire",
) -> dict:
    """Cria partículas 3D com predefinição visual (fire, smoke, sparkles)."""
    from tools.devsolo_ops import create_particles_3d as _impl
    return _impl(scene_path=scene_path, parent_node_path=parent_node_path,
                 node_name=node_name, preset=preset)


__all__ = [
    "create_light_3d", "create_csg_shape",
    "configure_standard_material_3d", "create_particles_3d",
]
