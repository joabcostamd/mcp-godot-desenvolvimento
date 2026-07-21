"""domains/ui/handlers.py — Handlers do domínio ui (F5.2).

Re-exporta funções de tools/ (scene_ops, devsolo_ops, ui_ops).
"""

from tools.scene_ops import create_ui_scene, add_control_node
from tools.devsolo_ops import (
    create_main_menu,
    create_hud_template,
    create_pause_menu,
    create_health_bar,
    create_loading_screen,
    create_ui_widget,
    create_tab_with_content,
    configure_ui_focus_and_nav,
    set_tooltip,
    set_anchor_preset,
)

__all__ = [
    "create_ui_scene",
    "add_control_node",
    "create_main_menu",
    "create_hud_template",
    "create_pause_menu",
    "create_health_bar",
    "create_loading_screen",
    "create_ui_widget",
    "create_tab_with_content",
    "configure_ui_focus_and_nav",
    "set_tooltip",
    "set_anchor_preset",
]
