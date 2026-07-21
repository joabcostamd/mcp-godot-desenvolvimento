"""domains/ui/manifest.py — Manifesto do domínio ui (F5.2)."""

from registry.types import DomainManifest, OpSpec, Phase
from . import handlers

MANIFEST = DomainManifest(
    domain="ui",
    tool_name="ui_manage",
    title="Gerenciar UI",
    namespace="project",
    version="1.0.0",
    description=(
        "Gerencia interfaces de usuário: criar cenas UI, adicionar controles, "
        "menus, HUD, loading screen, widgets, tabs, foco, tooltips e anchors.\n"
        "QUANDO USAR: construir qualquer interface 2D.\n"
        "QUANDO NÃO USAR: para lógica de jogo (use script_manage).\n"
        "PRÉ-CONDIÇÕES: cena com raiz Control.\n"
        "ERRO COMUM: esquecer de definir anchors — use set_anchor."
    ),
    phases=[Phase.DESIGN, Phase.PROTOTIPO, Phase.CONTEUDO],
    annotations={
        "readOnlyHint": False,
        "destructiveHint": True,
        "idempotentHint": False,
        "openWorldHint": False,
    },
    ops=[
        OpSpec(name="create_root", fn=handlers.create_ui_scene, summary="Cria cena raiz com Control", schema={"scene_path": {"type": "string", "required": True}}, examples=[{"scene_path": "scenes/ui.tscn"}], rollback="safety_manage(op=undo)"),
        OpSpec(name="add_control", fn=handlers.add_control_node, summary="Adiciona nó de controle UI", schema={"scene_path": {"type": "string", "required": True}, "parent_node_path": {"type": "string", "required": True}, "control_type": {"type": "string", "required": True}}, examples=[{"scene_path": "scenes/ui.tscn", "parent_node_path": ".", "control_type": "Button"}], rollback="safety_manage(op=undo)"),
        OpSpec(name="main_menu", fn=handlers.create_main_menu, summary="Cria menu principal", schema={"scene_path": {"type": "string", "required": True}}, examples=[{"scene_path": "scenes/menu.tscn"}], rollback="safety_manage(op=undo)"),
        OpSpec(name="hud", fn=handlers.create_hud_template, summary="Cria template de HUD", schema={"scene_path": {"type": "string", "required": True}}, examples=[{"scene_path": "scenes/hud.tscn"}], rollback="safety_manage(op=undo)"),
        OpSpec(name="pause_menu", fn=handlers.create_pause_menu, summary="Cria menu de pausa", schema={"scene_path": {"type": "string", "required": True}}, examples=[{"scene_path": "scenes/pause.tscn"}], rollback="safety_manage(op=undo)"),
        OpSpec(name="health_bar", fn=handlers.create_health_bar, summary="Cria barra de vida", schema={"scene_path": {"type": "string", "required": True}, "parent_node_path": {"type": "string"}}, examples=[{"scene_path": "scenes/ui.tscn", "parent_node_path": "."}], rollback="safety_manage(op=undo)"),
        OpSpec(name="loading_screen", fn=handlers.create_loading_screen, summary="Cria tela de carregamento", schema={"scene_path": {"type": "string", "required": True}}, examples=[{"scene_path": "scenes/loading.tscn"}], rollback="safety_manage(op=undo)"),
        OpSpec(name="create_widget", fn=handlers.create_ui_widget, summary="Cria widget de UI (Tree, Slider, etc)", schema={"scene_path": {"type": "string", "required": True}, "parent_node_path": {"type": "string", "required": True}, "widget_type": {"type": "string", "required": True}}, examples=[{"scene_path": "scenes/ui.tscn", "parent_node_path": ".", "widget_type": "Slider"}], rollback="safety_manage(op=undo)"),
        OpSpec(name="create_tab", fn=handlers.create_tab_with_content, summary="Adiciona tab a TabContainer", schema={"scene_path": {"type": "string", "required": True}, "tab_container_path": {"type": "string", "required": True}, "tab_title": {"type": "string"}}, examples=[{"scene_path": "scenes/ui.tscn", "tab_container_path": "./Tabs", "tab_title": "Opções"}], rollback="safety_manage(op=undo)"),
        OpSpec(name="config_focus", fn=handlers.configure_ui_focus_and_nav, summary="Configura navegação por foco", schema={"scene_path": {"type": "string", "required": True}, "node_path": {"type": "string", "required": True}}, examples=[{"scene_path": "scenes/ui.tscn", "node_path": "./PlayBtn"}], rollback="safety_manage(op=undo)"),
        OpSpec(name="set_tooltip", fn=handlers.set_tooltip, summary="Define tooltip de nó Control", schema={"scene_path": {"type": "string", "required": True}, "node_path": {"type": "string", "required": True}, "tooltip_text": {"type": "string", "required": True}}, examples=[{"scene_path": "scenes/ui.tscn", "node_path": "./PlayBtn", "tooltip_text": "Iniciar jogo"}], rollback="safety_manage(op=undo)"),
        OpSpec(name="set_anchor", fn=handlers.set_anchor_preset, summary="Define anchor preset para layout responsivo", schema={"scene_path": {"type": "string", "required": True}, "node_path": {"type": "string", "required": True}, "preset": {"type": "string", "required": True}}, examples=[{"scene_path": "scenes/ui.tscn", "node_path": "./Panel", "preset": "full_rect"}], rollback="safety_manage(op=undo)"),
    ],
    aliases=["ui_create_widget", "ui_create_tab_with_content", "ui_configure_focus_nav",
             "ui_set_tooltip", "ui_set_anchor_preset", "create_ui_widget",
             "create_tab_with_content", "configure_ui_focus_and_nav",
             "set_tooltip", "set_anchor_preset"],
    tags=["ui", "interface", "menu", "hud", "widget"],
)
