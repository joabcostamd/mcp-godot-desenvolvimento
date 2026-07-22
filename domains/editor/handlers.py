"""domains/editor/handlers.py — F6.2."""
def addon_connect(**kwargs) -> dict:
    from tools.addon_bridge import addon_connect as _impl; return _impl(**kwargs)
def addon_disconnect() -> dict:
    from tools.addon_bridge import addon_disconnect as _impl; return _impl()
def addon_is_available() -> dict:
    from tools.addon_bridge import addon_is_available as _impl; return _impl()
def addon_ping() -> dict:
    from tools.addon_bridge import addon_ping as _impl; return _impl()
def addon_create_node(*, parent_path: str = ".", node_type: str = "Node", node_name: str = "", properties: dict | None = None) -> dict:
    from tools.addon_bridge import addon_create_node as _impl; return _impl(parent_path, node_type, node_name, properties)
def addon_delete_node(*, node_path: str) -> dict:
    from tools.addon_bridge import addon_delete_node as _impl; return _impl(node_path)
def addon_set_property(*, node_path: str, property_name: str, value) -> dict:
    from tools.addon_bridge import addon_set_property as _impl; return _impl(node_path, property_name, value)
def addon_reparent_node(*, node_path: str, new_parent: str) -> dict:
    from tools.addon_bridge import addon_reparent_node as _impl; return _impl(node_path, new_parent)
def addon_duplicate_node(*, node_path: str, new_name: str = "") -> dict:
    from tools.addon_bridge import addon_duplicate_node as _impl; return _impl(node_path, new_name)
def addon_batch_edit(*, operations: list[dict]) -> dict:
    from tools.addon_bridge import addon_batch_edit as _impl; return _impl(operations)
def addon_take_screenshot(*, file_path: str = "") -> dict:
    from tools.addon_bridge import addon_take_screenshot as _impl; return _impl(file_path)
def addon_get_scene_tree() -> dict:
    from tools.addon_bridge import addon_get_scene_tree as _impl; return _impl()
__all__ = ["addon_connect", "addon_disconnect", "addon_is_available", "addon_ping", "addon_create_node", "addon_delete_node", "addon_set_property", "addon_reparent_node", "addon_duplicate_node", "addon_batch_edit", "addon_take_screenshot", "addon_get_scene_tree"]
