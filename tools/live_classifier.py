"""live_classifier.py — Classificador Editar-ao-Vivo (FATIA 2.AH).

Decide se uma mudanca pode ser aplicada sem reiniciar o jogo
(valor → arvore remota) ou se exige reinicializacao (estrutura).

Regra: parametros (@export) e propriedades de nos existentes
podem ser alterados ao vivo. Adicionar/remover nos, mudar
scripts ou cenas exige reiniciar.

Fonte: Godot 4.7 docs — @export, EditorDebuggerPlugin, remote scene tree.
"""

from enum import Enum
from typing import Any


class EditCategory(Enum):
    LIVE = "live"               # Pode ser aplicado sem reiniciar
    RESTART = "restart"         # Exige reinicializacao
    UNKNOWN = "unknown"         # Nao foi possivel determinar


# Operacoes que podem ser feitas ao vivo (arvore remota)
_LIVE_OPERATIONS = {
    "set_node_property",
    "set_properties_batch",
    "addon_set_property",
    "game_call_method",
    "inject_input_event",
    "configure_particles_2d",
    "set_physics_material",
    "set_collision_layer_mask",
    "configure_audio_bus",
    "add_audio_effect",
}

# Operacoes que exigem reinicializacao (mudanca estrutural)
_RESTART_OPERATIONS = {
    "add_node",
    "delete_node",
    "create_scene",
    "attach_script",
    "detach_script",
    "add_nodes_batch",
    "create_entity",
    "create_entities",
    "reparent_node",
    "addon_create_node",
    "addon_delete_node",
    "addon_reparent_node",
    "addon_duplicate_node",
    "generate_gdscript",
    "safe_write_gdscript",
    "script_manage",
    "create_project",
    "configure_autoload",
    "set_main_scene",
    "configure_input_action",
    "create_tileset",
    "create_tilemap_layer",
    "paint_tilemap_cell",
    "create_animation_player",
    "create_animation",
    "create_animation_tree",
    "import_texture",
    "import_sprite_sheet",
    "import_audio",
    "import_3d_model",
    "create_light_2d",
    "create_light_3d",
    "create_particles_2d",
    "create_particles_3d",
    "create_shader_material",
    "add_collision_shape",
    "create_joint_2d",
    "create_navigation_agent_2d",
    "create_navigation_region_2d",
    "add_raycast_2d",
    "add_shapecast_2d",
    "setup_camera_2d",
    "create_parallax_background",
    "add_parallax_layer",
    "create_path_2d",
    "create_patrol_route",
    "create_gun_system",
    "create_bullet_template",
    "create_ui_scene",
    "add_control_node",
    "create_dialogue_system",
    "add_dialogue_node",
    "create_dialogue_ui",
    "create_inventory_system",
    "define_inventory_item",
    "create_inventory_ui",
    "generate_tilemap_from_noise",
    "generate_dungeon_rooms",
    "create_loading_screen",
    "create_achievement_system",
    "cutscene_create_timeline",
    "cutscene_add_camera_shot",
    "cutscene_add_dialogue_event",
    "mod_manifest_generate",
    "generate_project_structure",
}


def classify_tool(tool_name: str) -> dict:
    """Classifica se uma tool pode ser aplicada ao vivo ou exige restart.

    Args:
        tool_name: Nome da tool MCP.

    Returns:
        dict com categoria e explicacao.
    """
    if tool_name in _LIVE_OPERATIONS:
        return {
            "tool": tool_name,
            "category": EditCategory.LIVE.value,
            "message": "Pode ser aplicado sem reiniciar — altera valores na arvore remota.",
        }
    if tool_name in _RESTART_OPERATIONS:
        return {
            "tool": tool_name,
            "category": EditCategory.RESTART.value,
            "message": "Exige reinicializacao — altera a estrutura da cena ou scripts.",
        }
    return {
        "tool": tool_name,
        "category": EditCategory.UNKNOWN.value,
        "message": "Categoria desconhecida. Assuma restart por seguranca.",
    }


def should_restart(tool_calls: list[str]) -> dict:
    """Analisa uma sequencia de chamadas e decide se restart e necessario.

    Args:
        tool_calls: Lista de nomes de tools chamadas.

    Returns:
        dict com decisao e resumo.
    """
    categories = [classify_tool(t)["category"] for t in tool_calls]
    live_count = categories.count("live")
    restart_count = categories.count("restart")
    unknown_count = categories.count("unknown")

    needs_restart = restart_count > 0 or unknown_count > 0

    return {
        "needs_restart": needs_restart,
        "total_calls": len(tool_calls),
        "live": live_count,
        "restart": restart_count,
        "unknown": unknown_count,
        "message": (
            "Reinicializacao necessaria — ha mudancas estruturais."
            if needs_restart
            else "Sem necessidade de reinicializar — apenas mudancas de valor."
        ),
    }
