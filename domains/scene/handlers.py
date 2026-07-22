"""domains/scene/handlers.py"""
def create_scene(*, scene_name: str, root_node_type: str = "Node2D", project_path: str | None = None) -> dict:
    from tools.scene_ops import create_scene as _impl; return _impl(scene_name, root_node_type, project_path)
def load_scene_tree(*, scene_path: str) -> dict:
    from tools.scene_ops import load_scene_tree as _impl; return _impl(scene_path)
def instance_scene_as_child(*, scene_path: str, parent_node_path: str, instance_path: str) -> dict:
    from tools.scene_ops import instance_scene_as_child as _impl; return _impl(scene_path, parent_node_path, instance_path)
__all__ = ["create_scene", "load_scene_tree", "instance_scene_as_child"]
