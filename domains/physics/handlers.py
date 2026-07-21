"""domains/physics/handlers.py — Handlers do domínio physics (F5.1).

Wrappers keyword-only (*) que delegam para tools/physics_ops.py e tools/devsolo_ops.py.
NÃO conhecem MCP, Tool, nem annotations.
"""

from typing import Any


def add_collision_shape(*, scene_path: str, parent_node_path: str, shape_type: str, dimensions: dict | str) -> dict:
    """Adiciona CollisionShape2D/3D com shape a um nó de física."""
    from tools.physics_ops import add_collision_shape as _impl
    return _impl(scene_path, parent_node_path, shape_type, dimensions)


def set_collision_layer_mask(*, scene_path: str, node_path: str, layer_bits: list[int] | None = None, mask_bits: list[int] | None = None, layer: int | None = None, mask: int | None = None) -> dict:
    """Configura collision_layer e collision_mask de um nó."""
    from tools.physics_ops import set_collision_layer_mask as _impl
    lb = layer_bits if layer_bits is not None else ([layer] if layer is not None else [1])
    mb = mask_bits if mask_bits is not None else ([mask] if mask is not None else [1])
    return _impl(scene_path, node_path, lb, mb)


def set_physics_material(*, scene_path: str, node_path: str, bounce: float | None = None, friction: float | None = None, absorb: float | None = None, rough: bool | None = None) -> dict:
    """Configura PhysicsMaterial com bounce, friction e absorb em um nó."""
    from tools.physics_ops import set_physics_material as _impl
    return _impl(scene_path=scene_path, node_path=node_path, bounce=bounce, friction=friction, absorb=absorb, rough=rough)


def create_joint_2d(*, scene_path: str, node_a_path: str, node_b_path: str, joint_type: str = "pin", softness: float | None = None, bias: float | None = None) -> dict:
    """Cria junta 2D (PinJoint2D/GrooveJoint2D) entre dois nós."""
    from tools.physics_ops import create_joint_2d as _impl
    return _impl(scene_path, node_a_path, node_b_path, joint_type, softness, bias)


def add_raycast_2d(*, scene_path: str, parent_node_path: str, target_position: str | None = None, collision_mask: int = 1, enabled: bool = True, node_name: str = "RayCast2D") -> dict:
    """Adiciona RayCast2D para detecção de linha de visão."""
    from tools.devsolo_ops import add_raycast_2d as _impl
    tp = None
    if target_position:
        import re
        m = re.match(r'Vector2\(([^,]+),\s*([^)]+)\)', target_position)
        if m:
            tp = [float(m.group(1)), float(m.group(2))]
    return _impl(scene_path=scene_path, parent_node_path=parent_node_path, target_position=tp, collision_mask=collision_mask, enabled=enabled, node_name=node_name)


def add_shapecast_2d(*, scene_path: str, parent_node_path: str, shape_type: str = "rectangle", shape_size: str | None = None, target_position: str | None = None, collision_mask: int = 1, node_name: str = "ShapeCast2D") -> dict:
    """Adiciona ShapeCast2D para detecção de área."""
    from tools.devsolo_ops import add_shapecast_2d as _impl
    return _impl(scene_path=scene_path, parent_node_path=parent_node_path, shape_type=shape_type, shape_size=shape_size, target_position=target_position, collision_mask=collision_mask, node_name=node_name)


__all__ = [
    "add_collision_shape",
    "set_collision_layer_mask",
    "set_physics_material",
    "create_joint_2d",
    "add_raycast_2d",
    "add_shapecast_2d",
]
