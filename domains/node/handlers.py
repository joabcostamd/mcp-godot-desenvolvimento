"""domains/node/handlers.py"""
def add_node(*, scene_path: str, parent_node_path: str, node_name: str, node_type: str) -> dict:
    from tools.scene_ops import add_node as _impl; return _impl(scene_path, parent_node_path, node_name, node_type)
def delete_node(*, scene_path: str, node_path: str) -> dict:
    from tools.scene_ops import delete_node as _impl; return _impl(scene_path, node_path)
def set_node_property(*, scene_path: str, node_path: str, property_name: str, value) -> dict:
    from tools.scene_ops import set_node_property as _impl; return _impl(scene_path, node_path, property_name, value)
def get_node_property(*, scene_path: str, node_path: str, property_name: str) -> dict:
    from tools.scene_ops import get_node_property as _impl; return _impl(scene_path, node_path, property_name)
def reparent_node(*, scene_path: str, node_path: str, new_parent_path: str) -> dict:
    from tools.scene_ops import reparent_node as _impl; return _impl(scene_path, node_path, new_parent_path)
def connect_signal(*, scene_path: str, source_node: str, signal_name: str, target_node: str, target_method: str) -> dict:
    from tools.scene_ops import connect_signal as _impl; return _impl(scene_path, source_node, signal_name, target_node, target_method)
def list_signals_for_node(*, scene_path: str, node_path: str) -> dict:
    from tools.scene_ops import list_signals_for_node as _impl; return _impl(scene_path, node_path)
__all__ = ["add_node", "delete_node", "set_node_property", "get_node_property", "reparent_node", "connect_signal", "list_signals_for_node"]
