"""domains/dialogue/handlers.py — Handlers do domínio dialogue (F5.19)."""
from typing import Any

def create_dialogue_system(*, scene_path: str, parent_node_path: str = ".") -> dict:
    """Cria sistema de diálogo completo na cena."""
    from tools.devsolo_ops import create_dialogue_system as _impl
    return _impl(scene_path=scene_path, parent_node_path=parent_node_path)

def add_dialogue_node(*, scene_path: str, parent_node_path: str = ".", speaker: str = "", text: str = "", node_name: str = "") -> dict:
    """Adiciona um nó de diálogo ao sistema."""
    from tools.devsolo_ops import add_dialogue_node as _impl
    return _impl(scene_path=scene_path, parent_node_path=parent_node_path, speaker=speaker, text=text, node_name=node_name)

def create_dialogue_ui(*, scene_path: str, parent_node_path: str = ".", ui_name: str = "DialogueUI") -> dict:
    """Cria a interface de diálogo (caixa de texto, nome do speaker)."""
    from tools.devsolo_ops import create_dialogue_ui as _impl
    return _impl(scene_path=scene_path, parent_node_path=parent_node_path, ui_name=ui_name)

__all__ = ["create_dialogue_system", "add_dialogue_node", "create_dialogue_ui"]
