"""domains/ui/examples.py — Exemplos do domínio ui (F5.2)."""
EXAMPLES = {
    "create_widget": {"scene_path": "scenes/ui.tscn", "parent_node_path": ".", "widget_type": "Slider"},
    "create_tab": {"scene_path": "scenes/ui.tscn", "tab_container_path": "./Tabs", "tab_title": "Opções"},
    "config_focus": {"scene_path": "scenes/ui.tscn", "node_path": "./PlayBtn"},
    "set_tooltip": {"scene_path": "scenes/ui.tscn", "node_path": "./PlayBtn", "tooltip_text": "Iniciar jogo"},
    "set_anchor": {"scene_path": "scenes/ui.tscn", "node_path": "./Panel", "preset": "full_rect"},
}
