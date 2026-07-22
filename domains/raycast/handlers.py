"""domains/raycast/handlers.py"""
def add_raycast_2d(*, scene_path: str, parent_node_path: str, target_position=None, collision_mask: int = 1, enabled: bool = True, node_name: str = "RayCast2D") -> dict:
    from tools.devsolo_ops import add_raycast_2d as _impl; return _impl(scene_path=scene_path, parent_node_path=parent_node_path, target_position=target_position, collision_mask=collision_mask, enabled=enabled, node_name=node_name)
def add_shapecast_2d(*, scene_path: str, parent_node_path: str, shape_type: str = "rectangle", shape_size=None, target_position=None, collision_mask: int = 1, node_name: str = "ShapeCast2D") -> dict:
    from tools.devsolo_ops import add_shapecast_2d as _impl; return _impl(scene_path=scene_path, parent_node_path=parent_node_path, shape_type=shape_type, shape_size=shape_size, target_position=target_position, collision_mask=collision_mask, node_name=node_name)
__all__ = ["add_raycast_2d", "add_shapecast_2d"]
