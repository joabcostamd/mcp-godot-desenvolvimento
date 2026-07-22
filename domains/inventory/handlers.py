"""domains/inventory/handlers.py — F5.20."""
from typing import Any

def create_inventory_system(*, scene_path: str, parent_node_path: str = ".") -> dict:
    """Cria sistema de inventário completo na cena."""
    from tools.devsolo_ops import create_inventory_system as _impl
    return _impl(scene_path=scene_path, parent_node_path=parent_node_path)

def define_inventory_item(*, scene_path: str, item_id: str, item_name: str = "", item_type: str = "generic", stackable: bool = False, max_stack: int = 99) -> dict:
    """Define um item no sistema de inventário."""
    from tools.devsolo_ops import define_inventory_item as _impl
    return _impl(scene_path=scene_path, item_id=item_id, item_name=item_name, item_type=item_type, stackable=stackable, max_stack=max_stack)

def create_inventory_ui(*, scene_path: str, parent_node_path: str = ".", ui_name: str = "InventoryUI") -> dict:
    """Cria a interface de inventário (grid de slots)."""
    from tools.devsolo_ops import create_inventory_ui as _impl
    return _impl(scene_path=scene_path, parent_node_path=parent_node_path, ui_name=ui_name)

__all__ = ["create_inventory_system", "define_inventory_item", "create_inventory_ui"]
