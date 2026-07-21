"""domains/physics/handlers.py — Handlers do domínio physics (F5.1).

Re-exporta funções de tools/physics_ops.py e tools/devsolo_ops.py.
NÃO conhecem MCP, Tool, nem annotations.
"""

# ── Handlers de física (tools/physics_ops.py) ──────────────────
from tools.physics_ops import (
    add_collision_shape,
    set_collision_layer_mask,
    set_physics_material,
    create_joint_2d,
)

# ── Handlers de raycast/shape (tools/devsolo_ops.py) ───────────
from tools.devsolo_ops import (
    add_raycast_2d,
    add_shapecast_2d,
)

__all__ = [
    "add_collision_shape",
    "set_collision_layer_mask",
    "set_physics_material",
    "create_joint_2d",
    "add_raycast_2d",
    "add_shapecast_2d",
]
