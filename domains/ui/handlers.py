"""domains/ui/handlers.py — Handlers do domínio ui (F5.2).

Wrappers keyword-only (*) que delegam para tools/scene_ops.py e tools/devsolo_ops.py.
NÃO conhecem MCP, Tool, nem annotations.
"""

from typing import Any


# ── Scene Ops (2 funções) ────────────────────────────────────────────

def create_ui_scene(*, name: str, path: str) -> dict:
    """Cria uma cena de UI com CanvasLayer + Control como raiz."""
    from tools.scene_ops import create_ui_scene as _impl
    return _impl(name, path)


def add_control_node(
    *,
    scene_path: str,
    parent_node_path: str,
    node_name: str,
    node_type: str,
    properties: dict | None = None,
) -> dict:
    """Adiciona um nó de UI (Label, Button, etc.) a uma cena."""
    from tools.scene_ops import add_control_node as _impl
    return _impl(scene_path, parent_node_path, node_name, node_type, properties)


# ── DevSolo Ops — Menus e Templates (5 funções) ──────────────────────

def create_main_menu(
    *,
    scene_name: str,
    game_title: str,
    title_font_size: int = 64,
    buttons: list[str] | None = None,
    background_color: str = "#1a1a2e",
    style: str = "modern",
) -> dict:
    """Cria uma cena de menu principal completa."""
    from tools.devsolo_ops import create_main_menu as _impl
    return _impl(scene_name, game_title, title_font_size, buttons, background_color, style)


def create_hud_template(
    *,
    scene_name: str = "hud",
    elements: list[str] | None = None,
    position: str = "top_left",
) -> dict:
    """Cria uma cena de HUD (Heads-Up Display)."""
    from tools.devsolo_ops import create_hud_template as _impl
    return _impl(scene_name, elements, position)


def create_pause_menu(
    *,
    scene_name: str = "pause_menu",
    overlay_alpha: float = 0.7,
) -> dict:
    """Cria uma cena de menu de pausa."""
    from tools.devsolo_ops import create_pause_menu as _impl
    return _impl(scene_name, overlay_alpha)


def create_health_bar(
    *,
    scene_path: str,
    parent_node_path: str = ".",
    max_health: float = 100.0,
    bar_name: str = "HealthBar",
    bar_width: int = 250,
    bar_height: int = 25,
    fill_color: str = "#2ecc71",
    bg_color: str = "#333333",
    show_text: bool = True,
) -> dict:
    """Cria uma barra de vida com script de controle."""
    from tools.devsolo_ops import create_health_bar as _impl
    return _impl(
        scene_path, parent_node_path, max_health,
        bar_name, bar_width, bar_height, fill_color, bg_color, show_text,
    )


def create_loading_screen(
    *,
    scene_name: str = "loading_screen",
    tips: list[str] | None = None,
    min_load_time: float = 1.0,
    background_color: str = "#1a1a2e",
) -> dict:
    """Cria cena de tela de carregamento com ProgressBar e dicas."""
    from tools.devsolo_ops import create_loading_screen as _impl
    return _impl(scene_name, tips, min_load_time, background_color)


# ── DevSolo Ops — Widgets e Configuração (5 funções) ─────────────────

def create_ui_widget(
    *,
    scene_path: str,
    parent_node_path: str,
    widget_type: str,
    widget_name: str = "",
    properties: dict | None = None,
) -> dict:
    """Cria um widget de UI granular numa cena."""
    from tools.devsolo_ops import create_ui_widget as _impl
    return _impl(scene_path, parent_node_path, widget_type, widget_name, properties)


def create_tab_with_content(
    *,
    scene_path: str,
    tab_container_path: str,
    tab_title: str,
    content_type: str = "Control",
    tab_name: str = "",
) -> dict:
    """Adiciona uma tab com conteúdo a um TabContainer existente."""
    from tools.devsolo_ops import create_tab_with_content as _impl
    return _impl(scene_path, tab_container_path, tab_title, content_type, tab_name)


def configure_ui_focus_and_nav(
    *,
    scene_path: str,
    node_path: str,
    focus_neighbor_top: str = "",
    focus_neighbor_bottom: str = "",
    focus_neighbor_left: str = "",
    focus_neighbor_right: str = "",
    focus_neighbor_next: str = "",
    focus_neighbor_prev: str = "",
    focus_mode: str | None = None,
) -> dict:
    """Configura navegação por foco/controle entre widgets UI."""
    from tools.devsolo_ops import configure_ui_focus_and_nav as _impl
    return _impl(
        scene_path, node_path,
        focus_neighbor_top, focus_neighbor_bottom,
        focus_neighbor_left, focus_neighbor_right,
        focus_neighbor_next, focus_neighbor_prev,
        focus_mode,
    )


def set_tooltip(
    *,
    scene_path: str,
    node_path: str,
    tooltip_text: str,
) -> dict:
    """Define o tooltip de um nó Control."""
    from tools.devsolo_ops import set_tooltip as _impl
    return _impl(scene_path, node_path, tooltip_text)


def set_anchor_preset(
    *,
    scene_path: str,
    node_path: str,
    preset: str = "full_rect",
) -> dict:
    """Define anchor preset de um nó Control."""
    from tools.devsolo_ops import set_anchor_preset as _impl
    return _impl(scene_path, node_path, preset)


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
