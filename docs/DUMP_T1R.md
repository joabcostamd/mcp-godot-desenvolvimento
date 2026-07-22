# DUMP_T1R.md — Medicao do Registro de Tools (FATIA T1-R)
# Gerado em: 2026-07-21

======================================================================
SECAO 4a — tools/rollups.py (completo)
======================================================================
ARQUIVO: tools/rollups.py

"""rollups.py — Domain Rollups (Fase 2A / C1).

Define rollups <domain>_manage com dispatch por `op`.
Cada rollup colapsa múltiplas tools individuais em 1 tool com Literal enum.

Onda 1 (piloto): scene_manage, node_manage, script_manage — 16 → 3
Onda 2 (assets):  file_manage, project_manage, asset_manage   — 17 → 3
Total acumulado: 33 tools → 6 rollups (economia de 27 slots).

Importado por server.py para registrar automaticamente em _tool_defs()
e _build_handlers().
"""

from _meta_tool import create_manage_tool

# ── Imports das funções alvo ────────────────────────────────────────

from tools.scene_ops import (
    create_scene,
    load_scene_tree,
    add_node,
    delete_node,
    set_node_property,
    get_node_property,
    reparent_node,
    instance_scene_as_child,
    connect_signal,
    list_signals_for_node,
    create_animation,
    create_animation_player,
    create_ui_scene,
    add_control_node,
    create_tileset,
    create_tilemap_layer,
    paint_tilemap_cell,
    detect_offscreen_elements,
)
from tools.script_ops import (
    generate_gdscript,
    attach_script,
    detach_script,
    validate_gdscript_syntax,
    add_script_variable,
    add_script_signal,
)

# ── Onda 2: file, project, asset ───────────────────────────────

from tools.file_ops import (
    delete_file,
    move_file,
    inspect_project,
)
from tools.project_ops import (
    create_project,
    set_active_project,
    get_project_settings,
    set_project_setting,
    set_main_scene,
    configure_input_action,
    configure_autoload,
)
from tools.asset_ops import (
    import_texture,
    import_sprite_sheet,
    import_audio,
    validate_asset_game_ready,
    audit_asset_license,
)
from tools.art_ops import (
    generate_sprite_animation,
)
from tools.placeholder_ops import (
    generate_placeholder_sprite,
    generate_placeholder_texture_atlas,
    generate_background_gradient,
    generate_tileset_from_colors,
    suggest_color_palette,
)

# ── Ondas 3-5: physics, anim, UI, tilemap, audio, export, 3D, debug, config, gamestate

from tools.physics_ops import (
    add_collision_shape,
    set_collision_layer_mask,
    set_physics_material,
    create_joint_2d,
)
from tools.export_ops import (
    list_export_presets,
    validate_export_templates_installed,
    build_export,
)
from tools.devsolo_ops import (
    create_tween_animation,
    chain_tweens,
    create_main_menu,
    create_hud_template,
    create_pause_menu,
    create_health_bar,
    create_loading_screen,
    generate_tilemap_from_noise,
    create_light_3d,
    create_csg_shape,
    configure_standard_material_3d,
    create_particles_3d,
    enable_debug_collisions,
    enable_debug_navigation,
    get_performance_stats,
    create_save_system,
    define_save_data,
    create_state_machine,
    add_state_transition,
    configure_audio_bus,
    add_audio_effect,
    route_audio_bus,
    create_spatial_audio_player,
    scan_scene_for_sfx_events,
    generate_sfx_batch,
    setup_camera_2d,
    setup_camera_follow,
    setup_camera_shake,
    create_navigation_region_2d,
    create_navigation_agent_2d,
    bake_navigation_polygon,
    create_dialogue_system,
    add_dialogue_node,
    create_dialogue_ui,
    create_inventory_system,
    define_inventory_item,
    create_inventory_ui,
    setup_screen_flash,
    setup_world_environment,
    generate_shader_2d,
    apply_shader_to_node,
    configure_particles_2d,
)

# ── Shader Editor ─────────────────────────────────────────────

from tools.shader_editor_ops import (
    read_shader,
    edit_shader,
    get_shader_params,
)

# ── VFX ───────────────────────────────────────────────────────

from tools.vfx_ops import create_particles_2d

# ── DevSolo (raycast) ─────────────────────────────────────────

from tools.devsolo_ops import add_raycast_2d, add_shapecast_2d

# ── Stress Test ───────────────────────────────────────────────

from tools.stress_test_ops import run_stress_test
from tools.test_ops import test_coverage_report, generate_test_cases_from_gdd, run_canary_queries
from tools.perf_ops import perf_regression_track
from tools.music_ops import generate_music, make_seamless_loop, place_and_normalize, bind_to_event
from tools.playtest_ops import self_play, regression_from_recording, difficulty_curve
from tools.localization_ops import find_missing_translations, detect_text_overflow, check_text_contrast

# ── Playmode (assert) ─────────────────────────────────────────

from tools.playmode_ops import assert_node_exists

# ── Runtime, Analysis, Safety ──────────────────────────────────

from tools.runtime_ops import (
    compile_test, run_game, stop_game, smart_restart, launch_editor, close_editor,
    compare_screenshots, detect_empty_screen, visual_regression,
)
# detect_offscreen_elements está em scene_ops (já importado acima)
from tools.analyze_ops import (
    analyze_game_structure,
    suggest_next_steps,
    find_missing_references,
    validate_game_design,
    estimate_game_scope,
    search_codebase,
    get_project_history,
)
from tools.safety import (
    list_backups,
    restore as restore_backup,
    git_checkpoint as git_commit_checkpoint,
    undo_last_action,
    get_undo_history,
)


# ── Rollup Builders ─────────────────────────────────────────────────

def _build_scene_manage():
    """scene_manage: 3 operações de cena."""
    return create_manage_tool(
        tool_name="scene_manage",
        description=(
            "Gerencia cenas Godot (.tscn) com operações de criação, "
            "carregamento e instanciação. "
            "Use para criar uma cena nova (com nó raiz e tipo), "
            "carregar a árvore hierárquica de uma cena existente, "
            "ou instanciar uma sub-cena como filha de um nó. "
            "Quando NÃO usar: para operações em nós individuais "
            "(use node_manage). "
            "Pré-condições: projeto ativo definido com set_active_project."
        ),
        ops={
            "create": create_scene,
            "load_tree": load_scene_tree,
            "instance": instance_scene_as_child,
        },
        tool_hints={"destructiveHint": True, "idempotentHint": False, "openWorldHint": True},
        title="Gerenciar Cenas",
        tags=["cena", "godot", "tscn"],
    )


def _build_node_manage():
    """node_manage: 7 operações de nó."""
    return create_manage_tool(
        tool_name="node_manage",
        description=(
            "Gerencia nós dentro de cenas Godot: adicionar, remover, "
            "ler/definir propriedades, re-parentar, conectar sinais e listar sinais. "
            "Use para construir a árvore de nós de uma cena — é a ferramenta "
            "principal de edição de cena. "
            "Quando NÃO usar: para criar a cena em si (use scene_manage.create). "
            "Pré-condições: a cena alvo deve existir no projeto. "
            "Erro mais comum: tipo de nó inválido (ex: 'Sprite' em vez de 'Sprite2D') "
            "— a mensagem de erro sugere tipos próximos válidos."
        ),
        ops={
            "create": add_node,
            "delete": delete_node,
            "set_property": set_node_property,
            "get_property": get_node_property,
            "reparent": reparent_node,
            "connect_signal": connect_signal,
            "list_signals": list_signals_for_node,
        },
        tool_hints={"destructiveHint": True, "idempotentHint": False, "openWorldHint": True},
        title="Gerenciar Nós",
        tags=["nó", "godot", "cena"],
    )


def _build_script_manage():
    """script_manage: 6 operações de script."""
    return create_manage_tool(
        tool_name="script_manage",
        description=(
            "Gerencia scripts GDScript: gerar código template, anexar/desanexar "
            "scripts a nós, validar sintaxe, adicionar variáveis e sinais. "
            "Use para criar e configurar a lógica do jogo. "
            "Quando NÃO usar: para ler/escrever arquivos de script manualmente "
            "(use read_file/write_file para edição direta). "
            "Pré-condições: projeto ativo definido. Para attach/detach, "
            "a cena e o nó alvo devem existir. "
            "Erro mais comum: script_path não encontrado — verifique com "
            "inspect_project antes de anexar."
        ),
        ops={
            "generate": generate_gdscript,
            "attach": attach_script,
            "detach": detach_script,
            "validate": validate_gdscript_syntax,
            "add_var": add_script_variable,
            "add_signal": add_script_signal,
        },
        tool_hints={"destructiveHint": True, "idempotentHint": False, "openWorldHint": True},
        title="Gerenciar Scripts",
        tags=["gdscript", "script", "código"],
    )


# ── Onda 2: File, Project, Asset ───────────────────────────────────

def _build_file_manage():
    """file_manage: 3 operações de arquivo."""
    return create_manage_tool(
        tool_name="file_manage",
        description=(
            "Gerencia arquivos do projeto Godot: deletar, mover/renomear "
            "e inspecionar/listar arquivos por categoria. "
            "Use para organizar a estrutura de pastas e localizar arquivos. "
            "Quando NÃO usar: para ler/escrever conteúdo (use read_file/write_file "
            "— são named tools de alto tráfego). "
            "Pré-condições: projeto ativo definido. "
            "Erro mais comum: arquivo não encontrado — use inspect antes."
        ),
        ops={
            "delete": delete_file,
            "move": move_file,
            "inspect": inspect_project,
        },
        tool_hints={"destructiveHint": True, "idempotentHint": False, "openWorldHint": True},
        title="Gerenciar Arquivos",
        tags=["arquivo", "projeto", "fs"],
    )


def _build_project_manage():
    """project_manage: 5 operações de projeto."""
    return create_manage_tool(
        tool_name="project_manage",
        description=(
            "Gerencia o projeto Godot ativo: criar novo projeto, definir "
            "projeto ativo, ler/definir configurações do project.godot e "
            "definir a cena principal. "
            "Use no início de todo jogo novo e para ajustar configurações. "
            "Quando NÃO usar: para input actions (use configure_input_action) "
            "ou autoloads (use configure_autoload). "
            "Pré-condições: Godot 4.7 instalado. Para set_active, "
            "o diretório deve conter project.godot. "
            "Erro mais comum: project.godot não encontrado — crie o projeto "
            "antes com project_manage.create."
        ),
        ops={
            "create": create_project,
            "set_active": set_active_project,
            "get_settings": get_project_settings,
            "set_setting": set_project_setting,
            "set_main_scene": set_main_scene,
        },
        tool_hints={"destructiveHint": True, "idempotentHint": False, "openWorldHint": True},
        title="Gerenciar Projeto",
        tags=["projeto", "godot", "config"],
    )


def _build_asset_manage():
    """asset_manage: 11 operações de assets."""
    return create_manage_tool(
        tool_name="asset_manage",
        description=(
            "Gerencia assets do jogo: importar texturas, spritesheets e áudio, "
            "gerar placeholders procedurais (sprites, fundos, tilesets), "
            "criar animações de sprite com esqueleto consistente (sprite_animation), "
            "auditar licenças de assets (license_audit — gate automático), "
            "sugerir paletas de cores e validar se um asset importado está "
            "game-ready (escala, colisão, material, polycount, rig). "
        ),
        ops={
            "import_texture": import_texture,
            "import_spritesheet": import_sprite_sheet,
            "import_audio": import_audio,
            "placeholder_sprite": generate_placeholder_sprite,
            "placeholder_atlas": generate_placeholder_texture_atlas,
            "bg_gradient": generate_background_gradient,
            "tileset_colors": generate_tileset_from_colors,
            "palette": suggest_color_palette,
            "validate_game_ready": validate_asset_game_ready,
            "sprite_animation": generate_sprite_animation,
            "license_audit": audit_asset_license,
        },
        tool_hints={"destructiveHint": True, "idempotentHint": False, "openWorldHint": True},
        title="Gerenciar Assets",
        tags=["asset", "textura", "áudio", "placeholder", "animação", "sprite", "licença"],
    )


# ── Ondas 3-5: Physics, Anim, UI, Tilemap, Audio, Export, 3D, Debug, Config, Gamestate

def _build_physics_manage():
    """physics_manage: 4 operações de física."""
    return create_manage_tool(
        tool_name="physics_manage",
        description="Gerencia física 2D/3D: colisões, camadas, materiais e juntas.",
        ops={
            "add_collision": add_collision_shape,
            "set_layers": set_collision_layer_mask,
            "set_material": set_physics_material,
            "create_joint": create_joint_2d,
        },
        tool_hints={"destructiveHint": True, "idempotentHint": False, "openWorldHint": True},
        title="Gerenciar Física",
        tags=["física", "colisão", "2D"],
    )


def _build_anim_manage():
    """anim_manage: 4 operações de animação."""
    return create_manage_tool(
        tool_name="anim_manage",
        description="Gerencia animações: AnimationPlayer, clipes, tweens e encadeamento.",
        ops={
            "create_player": create_animation_player,
            "create_clip": create_animation,
            "create_tween": create_tween_animation,
            "chain_tweens": chain_tweens,
        },
        tool_hints={"destructiveHint": True, "idempotentHint": False, "openWorldHint": True},
        title="Gerenciar Animações",
        tags=["animação", "tween", "godot"],
    )


def _build_ui_manage():
    """ui_manage: 7 operações de interface."""
    return create_manage_tool(
        tool_name="ui_manage",
        description="Gerencia interfaces: criar UI, adicionar controles, menus, HUD, loading screen.",
        ops={
            "create_root": create_ui_scene,
            "add_control": add_control_node,
            "main_menu": create_main_menu,
            "hud": create_hud_template,
            "pause_menu": create_pause_menu,
            "health_bar": create_health_bar,
            "loading_screen": create_loading_screen,
        },
        tool_hints={"destructiveHint": True, "idempotentHint": False, "openWorldHint": True},
        title="Gerenciar UI",
        tags=["ui", "interface", "menu", "hud"],
    )


def _build_tilemap_manage():
    """tilemap_manage: 4 operações de tilemap."""
    return create_manage_tool(
        tool_name="tilemap_manage",
        description="Gerencia tilemaps: criar tileset, camadas, pintar células e gerar por noise.",
        ops={
            "create_tileset": create_tileset,
            "create_layer": create_tilemap_layer,
            "paint_cell": paint_tilemap_cell,
            "from_noise": generate_tilemap_from_noise,
        },
        tool_hints={"destructiveHint": True, "idempotentHint": False, "openWorldHint": True},
        title="Gerenciar Tilemap",
        tags=["tilemap", "tileset", "2D", "procedural"],
    )


def _build_audio_manage():
    """audio_manage: 6 operações de áudio."""
    return create_manage_tool(
        tool_name="audio_manage",
        description="Gerencia áudio: configurar buses, rotear entre buses, adicionar efeitos (reverb/EQ/compressor/delay/chorus/distortion), criar AudioStreamPlayer3D com áudio espacial, escanear cenas por eventos sem SFX e gerar SFX em lote.",
        ops={
            "config_bus": configure_audio_bus,
            "add_effect": add_audio_effect,
            "route_bus": route_audio_bus,
            "spatial_player": create_spatial_audio_player,
            "scan_sfx_events": scan_scene_for_sfx_events,
            "generate_sfx_batch": generate_sfx_batch,
        },
        tool_hints={"destructiveHint": True, "idempotentHint": False, "openWorldHint": True},
        title="Gerenciar Áudio",
        tags=["áudio", "sfx", "mixagem", "efeitos", "espacial", "3D", "lote"],
    )


def _build_export_manage():
    """export_manage: 3 operações de exportação."""
    return create_manage_tool(
        tool_name="export_manage",
        description="Gerencia exportação: listar presets, validar templates, build.",
        ops={
            "list_presets": list_export_presets,
            "validate_templates": validate_export_templates_installed,
            "build": build_export,
        },
        tool_hints={"destructiveHint": True, "idempotentHint": False, "openWorldHint": True},
        title="Gerenciar Exportação",
        tags=["export", "build", "deploy"],
    )


def _build_3d_manage():
    """d3_manage: 4 operações 3D."""
    return create_manage_tool(
        tool_name="d3_manage",
        description="Gerencia 3D: luzes, CSG, materiais e partículas.",
        ops={
            "create_light": create_light_3d,
            "create_csg": create_csg_shape,
            "config_material": configure_standard_material_3d,
            "create_particles": create_particles_3d,
        },
        tool_hints={"destructiveHint": True, "idempotentHint": False, "openWorldHint": True},
        title="Gerenciar 3D",
        tags=["3D", "luz", "material", "partículas"],
    )


def _build_debug_manage():
    """debug_manage: 4 operações."""
    return create_manage_tool(
        tool_name="debug_manage",
        description="Gerencia debug: performance, colisões, navegação e regressão de performance.",
        ops={"perf_stats": get_performance_stats, "collision_debug": enable_debug_collisions,
            "nav_debug": enable_debug_navigation, "perf_regression": perf_regression_track},
        tool_hints={"destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
        title="Gerenciar Debug",
        tags=["debug", "diagnóstico", "visualização"],
    )


def _build_config_manage():
    """config_manage: 2 operações de configuração (input + autoload).
    NOTA: connect_signal e list_signals estão em node_manage — evite duplicação."""
    return create_manage_tool(
        tool_name="config_manage",
        description="Gerencia configurações: input actions e autoloads. Para sinais, use node_manage.",
        ops={
            "input_action": configure_input_action,
            "autoload": configure_autoload,
        },
        tool_hints={"destructiveHint": True, "idempotentHint": False, "openWorldHint": True},
        title="Gerenciar Configurações",
        tags=["config", "input", "autoload", "signal"],
    )


def _build_gamestate_manage():
    """gamestate_manage: 4 operações de estado de jogo."""
    return create_manage_tool(
        tool_name="gamestate_manage",
        description="Gerencia estado do jogo: save system, state machine e transições.",
        ops={
            "create_save": create_save_system,
            "define_save": define_save_data,
            "create_fsm": create_state_machine,
            "add_transition": add_state_transition,
        },
        tool_hints={"destructiveHint": True, "idempotentHint": False, "openWorldHint": True},
        title="Gerenciar Game State",
        tags=["save", "fsm", "estado"],
    )


# ── Onda Extra: Runtime, Camera, Nav, Dialogue, Inventory, VFX, Shader, Analysis, Safety, Vision

def _build_runtime_manage():
    return create_manage_tool(
        tool_name="runtime_manage",
        description="Gerencia execução do Godot: compilar, rodar, parar, reiniciar, abrir/fechar editor.",
        ops={
            "compile": compile_test,
            "run": run_game,
            "stop": stop_game,
            "restart": smart_restart,
            "launch_editor": launch_editor,
            "close_editor": close_editor,
        },
        tool_hints={"destructiveHint": True, "idempotentHint": False, "openWorldHint": True},
        title="Gerenciar Runtime",
        tags=["runtime", "godot", "execução"],
    )


def _build_camera_manage():
    return create_manage_tool(
        tool_name="camera_manage",
        description="Gerencia câmera 2D: setup, follow e shake.",
        ops={
            "setup_2d": setup_camera_2d,
            "follow": setup_camera_follow,
            "shake": setup_camera_shake,
        },
        tool_hints={"destructiveHint": True, "idempotentHint": False, "openWorldHint": True},
        title="Gerenciar Câmera",
        tags=["câmera", "2D", "follow"],
    )


def _build_navigation_manage():
    return create_manage_tool(
        tool_name="navigation_manage",
        description="Gerencia navegação 2D: regiões, agentes e bake.",
        ops={
            "create_region": create_navigation_region_2d,
            "create_agent": create_navigation_agent_2d,
            "bake": bake_navigation_polygon,
        },
        tool_hints={"destructiveHint": True, "idempotentHint": False, "openWorldHint": True},
        title="Gerenciar Navegação",
        tags=["navegação", "2D", "pathfinding"],
    )


def _build_dialogue_manage():
    return create_manage_tool(
        tool_name="dialogue_manage",
        description="Gerencia sistema de diálogo: criar, adicionar nós e UI.",
        ops={
            "create_system": create_dialogue_system,
            "add_node": add_dialogue_node,
            "create_ui": create_dialogue_ui,
        },
        tool_hints={"destructiveHint": True, "idempotentHint": False, "openWorldHint": True},
        title="Gerenciar Diálogo",
        tags=["diálogo", "npc", "rpg"],
    )


def _build_inventory_manage():
    return create_manage_tool(
        tool_name="inventory_manage",
        description="Gerencia sistema de inventário: criar, definir itens e UI.",
        ops={
            "create_system": create_inventory_system,
            "define_item": define_inventory_item,
            "create_ui": create_inventory_ui,
        },
        tool_hints={"destructiveHint": True, "idempotentHint": False, "openWorldHint": True},
        title="Gerenciar Inventário",
        tags=["inventário", "item", "rpg"],
    )


def _build_vfx_manage():
    return create_manage_tool(
        tool_name="vfx_manage",
        description="Gerencia efeitos visuais: criar partículas 2D, configurar, screen flash e ambiente.",
        ops={
            "create_particles": create_particles_2d,
            "config_particles": configure_particles_2d,
            "screen_flash": setup_screen_flash,
            "world_env": setup_world_environment,
        },
        tool_hints={"destructiveHint": True, "idempotentHint": False, "openWorldHint": True},
        title="Gerenciar VFX",
        tags=["vfx", "partículas", "luz", "ambiente"],
    )


def _build_shader_manage():
    return create_manage_tool(
        tool_name="shader_manage",
        description="Gerencia shaders: gerar, ler, editar e aplicar shaders 2D.",
        ops={
            "generate": generate_shader_2d,
            "apply": apply_shader_to_node,
            "read": read_shader,
            "edit": edit_shader,
            "get_params": get_shader_params,
        },
        tool_hints={"destructiveHint": True, "idempotentHint": False, "openWorldHint": True},
        title="Gerenciar Shaders",
        tags=["shader", "material", "efeitos"],
    )



def _build_raycast_manage():
    return create_manage_tool(
        tool_name="raycast_manage",
        description="Gerencia raycasts 2D: adicionar RayCast2D e ShapeCast2D para detecção de colisão.",
        ops={
            "add_raycast": add_raycast_2d,
            "add_shapecast": add_shapecast_2d,
        },
        tool_hints={"destructiveHint": True, "idempotentHint": False, "openWorldHint": True},
        title="Gerenciar Raycasts",
        tags=["raycast", "física", "2D", "colisão"],
    )


def _build_test_manage():
    return create_manage_tool(
        tool_name="test_manage",
        description="Gerencia testes: assert_node, stress_test, coverage_report, generate_test_cases, canary.",
        ops={"assert_node": assert_node_exists, "stress_test": run_stress_test,
            "coverage_report": test_coverage_report, "generate_test_cases": generate_test_cases_from_gdd,
            "canary": run_canary_queries},
        tool_hints={"destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
        title="Gerenciar Testes",
        tags=["teste", "assert", "stress", "performance"],
    )


def _build_analysis_manage():
    return create_manage_tool(
        tool_name="analysis_manage",
        description="Analisa o projeto: estrutura, próximos passos, referências, design, escopo e busca.",
        ops={
            "structure": analyze_game_structure,
            "next_steps": suggest_next_steps,
            "missing_refs": find_missing_references,
            "validate_design": validate_game_design,
            "estimate_scope": estimate_game_scope,
            "search": search_codebase,
            "history": get_project_history,
        },
        tool_hints={"destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
        title="Analisar Projeto",
        tags=["análise", "diagnóstico", "métricas"],
    )


def _build_safety_manage():
    return create_manage_tool(
        tool_name="safety_manage",
        description="Gerencia segurança: backups, restore, checkpoint git e undo/redo.",
        ops={
            "list_backups": list_backups,
            "restore": restore_backup,
            "checkpoint": git_commit_checkpoint,
            "undo": undo_last_action,
            "undo_history": get_undo_history,
        },
        tool_hints={"destructiveHint": True, "idempotentHint": False, "openWorldHint": True},
        title="Gerenciar Segurança",
        tags=["backup", "git", "undo", "segurança"],
    )


# ── Game Bridge (consolidação FATIA 0.7a) ─────────────────────────

from tools.runtime_rich import (
    game_call_method,
    game_spawn_node,
    game_raycast,
    game_get_camera,
    game_find_nodes_by_class,
    game_await_signal,
    game_pause,
    game_play_animation,
)
from tools.networking_ops import game_http_request, game_multiplayer
from tools.recording_ops import game_serialize_state
from tools.runtime_ui import game_performance, game_window, game_input_state


def _build_game_bridge_manage():
    """game_bridge_manage: 14 operações de game bridge (consolidação FATIA 0.7a)."""
    return create_manage_tool(
        tool_name="game_bridge_manage",
        description=(
            "Gerencia o jogo em execução via Runtime Bridge: métodos, spawn, "
            "raycast, câmera, busca, sinais, pausa, animação, performance, "
            "janela, input, HTTP, multiplayer e serialização de estado. "
            "Use para controlar o jogo rodando sem precisar de ferramentas "
            "individuais. Quando NÃO usar: para operações de editor/cena "
            "(use scene_manage, node_manage)."
        ),
        ops={
            "call_method": game_call_method,
            "spawn_node": game_spawn_node,
            "raycast": game_raycast,
            "get_camera": game_get_camera,
            "find_by_class": game_find_nodes_by_class,
            "await_signal": game_await_signal,
            "pause": game_pause,
            "play_animation": game_play_animation,
            "performance": game_performance,
            "window": game_window,
            "input_state": game_input_state,
            "http_request": game_http_request,
            "multiplayer": game_multiplayer,
            "serialize_state": game_serialize_state,
        },
        tool_hints={"destructiveHint": True, "idempotentHint": False, "openWorldHint": True},
        title="Gerenciar Game Bridge",
        tags=["game", "runtime", "bridge", "multiplayer", "input"],
    )

def _build_music_manage():
    """music_manage: 4 operações (Fatias 3.1-3.4)."""
    return create_manage_tool(
        tool_name="music_manage",
        description="Gerencia música: generate (API), make_seamless_loop (WAV), place_and_normalize (cena), bind_to_event (eventos).",
        ops={"generate": generate_music, "make_seamless_loop": make_seamless_loop,
            "place_and_normalize": place_and_normalize, "bind_to_event": bind_to_event},
        tool_hints={"destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
        title="Gerenciar Música",
        tags=["música", "áudio", "api", "loop", "cena", "eventos"],
    )

def _build_playtest_manage():
    """playtest_manage: 3 operações (Fatias 3.14-3.16)."""
    return create_manage_tool(
        tool_name="playtest_manage",
        description="Playtest autônomo: self_play, regression_from_recording, difficulty_curve.",
        ops={"self_play": self_play, "regression_from_recording": regression_from_recording,
             "difficulty_curve": difficulty_curve},
        tool_hints={"destructiveHint": False, "idempotentHint": False, "openWorldHint": True},
        title="Playtest Autônomo",
        tags=["playtest", "self-play", "regressão", "dificuldade", "automação"],
    )


def _build_localization_manage():
    """localization_manage: 3 operações (Fatia 4.1)."""
    return create_manage_tool(
        tool_name="localization_manage",
        description="Testes de internacionalização (i18n): strings faltantes, overflow de texto e contraste WCAG.",
        ops={"find_missing": find_missing_translations,
             "detect_overflow": detect_text_overflow,
             "check_contrast": check_text_contrast},
        tool_hints={"destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
        title="Testes de i18n",
        tags=["i18n", "localização", "tradução", "acessibilidade", "wcag"],
    )

def _build_vision_manage():
    return create_manage_tool(
        tool_name="vision_manage",
        description="Gerencia visão: comparar screenshots, detectar tela vazia/offscreen e regressão visual.",
        ops={"compare": compare_screenshots, "detect_empty": detect_empty_screen,
            "detect_offscreen": detect_offscreen_elements, "regression": visual_regression},
        tool_hints={"destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
        title="Gerenciar Visão",
        tags=["visão", "screenshot", "diagnóstico"],
    )


# ── Builders registry ───────────────────────────────────────────────

_ROLLUP_BUILDERS = [
    # Onda 1 (piloto)
    _build_scene_manage,
    _build_node_manage,
    _build_script_manage,
    # Onda 2 (assets)
    _build_file_manage,
    _build_project_manage,
    _build_asset_manage,
    # Onda 3 (game)
    _build_physics_manage,
    _build_anim_manage,
    _build_ui_manage,
    _build_tilemap_manage,
    _build_audio_manage,
    # Onda 4 (system)
    _build_export_manage,
    _build_3d_manage,
    _build_debug_manage,
    _build_config_manage,
    # Onda 5 (state)
    _build_gamestate_manage,
    # Onda Extra (runtime, camera, nav, dialogue, inventory, vfx, shader, analysis, safety, vision)
    _build_runtime_manage,
    _build_camera_manage,
    _build_navigation_manage,
    _build_dialogue_manage,
    _build_inventory_manage,
    _build_vfx_manage,
    _build_shader_manage,
    _build_analysis_manage,
    _build_safety_manage,
    _build_vision_manage,
    # Etapa 4: raycast + test
    _build_raycast_manage,
    _build_test_manage,
    # Etapa 5: game bridge (consolidação FATIA 0.7a)
    _build_game_bridge_manage,
    _build_music_manage,
    _build_playtest_manage,
    # Etapa 6: i18n (FATIA 4.1)
    _build_localization_manage,
]

# Cache interno — garante que cada builder só executa UMA vez.
# Isso evita o bug de criar Tool objects diferentes para tool_defs e handlers.
_cache: dict | None = None


def _ensure_cache():
    """Constrói o cache de rollups na primeira chamada."""
    global _cache
    if _cache is None:
        _cache = {"tool_defs": [], "handlers": {}}
        for builder in _ROLLUP_BUILDERS:
            tool_def, handler = builder()
            _cache["tool_defs"].append(tool_def)
            _cache["handlers"][tool_def.name] = handler


# ── Public API ──────────────────────────────────────────────────────

def get_rollup_tool_defs():
    """Retorna lista de Tool definitions para todos os rollups.

    Chamado por _tool_defs() em server.py após o pós-processamento.
    Retorna uma CÓPIA para evitar mutação acidental do cache.
    """
    _ensure_cache()
    return list(_cache["tool_defs"])


def get_rollup_handlers():
    """Retorna dict {tool_name: handler_fn} para todos os rollups.

    Chamado por _build_handlers() em server.py.
    Retorna uma CÓPIA para evitar mutação acidental do cache.
    """
    _ensure_cache()
    return dict(_cache["handlers"])


======================================================================
SECAO 4b — TOOLSETS (5 namespaces semanticos)
======================================================================
ARQUIVO: server.py — linha 59

TOOLSETS = {
    # ── 5 Namespaces Semânticos (Etapa A1) ──
    # Reduz ~60 tools visíveis → ≤20 por namespace.
    # A IA primeiro vê os 5 namespaces, depois explora um por vez.
    "project": [
        # Fundação — projeto, cenas, scripts, arquivos, UI
        "project_manage", "project_status", "project_map",
        "scene_manage", "node_manage",
        "script_manage", "safe_write_gdscript",
        "file_manage", "read_file", "write_file",
        "ui_manage",
        "create_entity", "create_entities",
        "generate_project_structure",
        # Gameplay estrutural
        "physics_manage", "anim_manage", "camera_manage",
        "tilemap_manage", "navigation_manage",
        "gamestate_manage", "dialogue_manage", "inventory_manage",
        "d3_manage",
        # Configuração
        "config_manage",
        "setup_localization", "add_translation_string",
        "create_animation_tree",
        "behavior_tree_generate", "behavior_tree_list_templates",
        "world_describe",
        # Batch/atômico
        "batch_atomic_edit", "add_nodes_batch", "set_properties_batch",
        "load_scene_async",
        # Templates de gameplay
        "create_gun_system", "create_bullet_template",
        "create_parallax_background", "add_parallax_layer", "create_spritesheet",
        "create_path_2d", "create_patrol_route",
        "loot_table_generate",
        # Operações atômicas de cena (complementam os rollups)
        "raycast_manage",
        "add_raycast_2d", "add_shapecast_2d",
        "create_joint_2d",
        "create_light_2d", "create_light_3d",
        "create_navigation_agent_2d", "create_navigation_region_2d",
        "setup_camera_2d",
        # Camada 5 (Gameplay): project
        "create_achievement_system", "cloud_save_configure",
        "mod_manifest_generate",
        "cutscene_create_timeline", "cutscene_add_camera_shot", "cutscene_add_dialogue_event",
        "quest_generate",
        "dialogue_generate_npc_lines", "dialogue_generate_personality",
        "accessibility_apply_colorblind_filter", "accessibility_add_subtitles", "accessibility_remap_controls",
        "onboarding_create_tutorial_step", "onboarding_create_guided_tour",
    
        "skeleton_get_bone_pose",
        "skeleton_set_bone_pose",
        "skeleton_list_bones",
        "skeleton_create_bone",
        "skeleton_create_ik_chain",
        "skeleton_get_info",
        "csg_create_node",
        "gi_create_node",
        "scene_fx_create_node",
        "sky_create_procedural",
        "camera_configure_attributes",
        "multimesh_create_instance",
        "physics_create_joint",
        "physics_configure_body",
        "ui_create_widget",
        "ui_create_tab_with_content",
        "ui_configure_focus_nav",
        "ui_set_tooltip",
        "ui_set_anchor_preset",
        "network_setup_multiplayer",
        "network_create_rpc",
        "network_create_websocket",
        "network_configure_dedicated_server",
        "network_create_lobby",
        "render_get_settings",
        "render_set_antialiasing",
        "render_set_scaling",
        "render_set_quality",
        "csharp_scaffold_project",
        "csharp_generate_script",
        "csharp_build_project",
],
    "assets": [
        # Assets, arte, áudio, shaders, VFX
        "asset_manage",
        "generate_game_art", "generate_game_art_flux", "apply_game_art",
        "generate_3d_asset", "generate_3d_placeholder",
        "import_asset_manifest", "create_asset_manifest",
        "download_asset", "import_downloaded_asset",
        "audio_manage", "music_manage",
        "generate_audio_sfx", "generate_voice",
        "shader_manage", "shader_generate", "shader_list_templates",
        "read_shader", "edit_shader", "get_shader_params",
        "vfx_manage",
        "optimize_sprite", "remove_background",
        "marketplace_search", "marketplace_download",
        # Geração procedural de conteúdo
        "generate_dungeon_rooms", "dungeon_generate",
        "terrain_generate", "wave_generate",
        # Juice/Polimento visual
        "juice_apply", "juice_list_presets",
        # Camada 5 (Gameplay): assets
        "trailer_capture_clip", "trailer_render_sequence", "capsule_generate_store_image",
        # Operações atômicas de assets (complementam os rollups)
        "configure_particles_2d", "create_particles_2d", "create_particles_3d",
        "configure_standard_material_3d",
        "generate_shader_2d",
        "import_3d_model",
    ],
    "runtime": [
        # Execução, debug, testes, bridge, jogo rodando
        "runtime_manage",
        "execute_gdscript_runtime", "capture_game_screenshot", "take_screenshot",
        "godot_run_project", "godot_stop_project", "godot_wait_for_bridge",
        "godot_exec", "godot_runtime_info", "godot_screenshot",
        "godot_custom_command", "godot_list_custom_commands",
        "godot_keep_alive",
        "get_runtime_state_digest", "capture_runtime_errors",
        "freeze_game_clock", "unfreeze_game_clock", "step_game_time", "step_until",
        "effect_probe",
        # Debug
        "debug_manage",
        "debugger_set_breakpoint", "debugger_status", "debugger_step",
        "debugger_get_stack", "debugger_get_variables",
        # Testes
        "test_manage",
        "run_gut_tests", "run_scripted_tests", "regression_test", "smoke_test",
        "run_verification_pipeline", "run_stress_test",
        "assert_node_exists",
        # Bridge
        "game_bridge_manage",
        "game_http_request", "game_multiplayer",
        "game_call_method", "game_spawn_node", "game_raycast", "game_get_camera",
        "game_play_animation", "game_find_nodes_by_class", "game_await_signal",
        "game_pause", "game_performance", "game_window", "game_input_state",
        "game_serialize_state",
        # Input/Recording
        "inject_input_event", "simulate_input_sequence",
        "watch_signal", "watch_state_start", "watch_state_collect",
        "record_gameplay_gif", "start_recording", "stop_recording",
        # Addon Bridge
        "addon_connect", "addon_disconnect", "addon_ping", "addon_is_available",
        "addon_get_scene_tree", "addon_take_screenshot",
        "addon_create_node", "addon_delete_node", "addon_set_property",
        "addon_duplicate_node", "addon_reparent_node", "addon_batch_edit",
        "read_console_output",
        # Performance
        "profile_frame", "profile_memory",
        "auto_screenshot",
        # Build/Export
        "build_csharp", "export_manage",
        # Playtest
        "playtest_manage",
    
        "physics_query_area_overlap",
        "physics_raycast_query",
        "runtime_connect_signal",
        "runtime_disconnect_signal",
        "runtime_emit_signal",
],
    "analysis": [
        # Análise, auditoria, qualidade, referências, introspecção
        "analysis_manage",
        "query_classdb", "search_classdb", "godot_class_ref",
        "list_valid_node_types",
        "validate_project_refs", "find_usages",
        "audit_input_map", "audit_autoloads", "audit_scene_reachability",
        "audit_uid_consistency", "audit_save_compatibility",
        "analyze_signal_flow",
        "gdscript_diagnostics", "gdscript_references", "gdscript_definition",
        "gdscript_hover", "gdscript_rename", "gdscript_symbols",
        "gdscript_lsp_connect", "gdscript_lsp_disconnect", "gdscript_sync_file",
        "resource_dependency_graph",
        "find_unused_resources",
        "estimate_tool_tokens",
        "dps_calculator", "balance_analyze",
        "vision_manage",
        "localization_manage",
        # Camada 5 (Gameplay): analysis
        "validate_achievement_config", "validate_mod_compatibility",
        "telemetry_track_event", "telemetry_get_funnel", "telemetry_session_summary", "telemetry_heatmap",
        "adaptive_difficulty_adjust",
        "accessibility_audit_scene", "accessibility_certification_checklist",
        "onboarding_check_first_experience",
    
        "runtime_list_signals",
        "runtime_watch_signal",
],
    "orchestration": [
        # Meta-tools, workflow, governança, fase, segurança, bootstrap
        "godot",
        "ping", "health_check", "self_test", "bootstrap_godot_mcp",
        "dump_mcp_state",
        "capture_proof", "verify_proof",
        "validate_mcp_registry", "validate_mcp_environment", "validate_godot_version",
        "tool_catalog", "tool_groups",
        "catalog_search", "describe_tool", "invoke_by_name",
        "safety_manage",
        "set_safety_policy", "configure_security", "security_status",
        "circuit_breaker_status",
        "get_current_phase", "advance_phase", "get_phase_history",
        "get_next_step", "resume_session",
        "get_audit_log", "get_audit_replay",
        "workflow_handoff", "workflow_snapshot",
        "set_auto_dismiss",
        "vibe_coding_mode", "get_vibe_context",
        "project_progress",
        "generate_ci_snippet",
        "install_mcp_addon", "setup_mcp_config",
        "create_milestone_plan", "get_milestone_plan", "advance_milestone",
        "set_project_brief", "get_project_brief", "update_project_brief",
        "gdd_generate",
        "release_checklist", "deploy_itch",
        "configure_export_preset",
        # Camada 5 (Gameplay): orchestration
        "remote_balance_config",
    ],
}

# ── TOOL_NAMESPACES: Mapeamento reverso tool_name → namespace ──


======================================================================
SECAO 4c — PHASE_TOOLSETS (6 fases)
======================================================================
ARQUIVO: server.py — linha 385

PHASE_TOOLSETS: dict[str, set[str]] = {
    "IDEIA": {
        "ping", "health_check", "self_test", "bootstrap_godot_mcp",
        "read_file", "write_file", "dump_mcp_state",
        "project_manage", "project_status",
        "tool_catalog", "tool_groups",
        "get_current_phase", "advance_phase", "get_phase_history",
        "create_milestone_plan", "get_milestone_plan", "advance_milestone",
        "set_project_brief", "get_project_brief", "update_project_brief",
        "gdd_generate",
        "analysis_manage",
        "godot_class_ref",
        "validate_mcp_environment", "validate_godot_version",
        "setup_mcp_config", "install_mcp_addon",
        "safety_manage",
        "capture_proof", "verify_proof",
        "audit_input_map", "audit_autoloads", "audit_scene_reachability",
        "audit_uid_consistency", "audit_save_compatibility",
        "validate_mcp_registry",
    },
    "DESIGN": {
        "scene_manage", "node_manage",
        "script_manage", "safe_write_gdscript",
        "gdscript_diagnostics", "gdscript_references", "gdscript_definition",
        "gdscript_hover", "gdscript_rename", "gdscript_symbols",
        "gdscript_lsp_connect", "gdscript_lsp_disconnect", "gdscript_sync_file",
        "file_manage",
        "create_entity", "create_entities",
        "ui_manage",
        "config_manage",
        "project_map",
        "resource_dependency_graph",
        "query_classdb", "search_classdb",
        "list_valid_node_types",
        "validate_project_refs", "find_usages",
        "analyze_signal_flow",
        "behavior_tree_generate", "behavior_tree_list_templates",
        "generate_project_structure",
        "world_describe",
    
        "skeleton_get_bone_pose",
        "skeleton_list_bones",
        "skeleton_get_info",
        "ui_create_widget",
        "ui_create_tab_with_content",
        "ui_configure_focus_nav",
        "ui_set_tooltip",
        "ui_set_anchor_preset",
        "render_get_settings",
        "csharp_scaffold_project",
        "csharp_generate_script",
},
    "PROTOTIPO": {
        "runtime_manage",
        "godot_run_project", "godot_stop_project", "godot_wait_for_bridge",
        "execute_gdscript_runtime",
        "capture_game_screenshot", "godot_screenshot", "take_screenshot",
        "get_runtime_state_digest", "capture_runtime_errors",
        "godot_exec", "godot_runtime_info",
        "godot_custom_command", "godot_list_custom_commands",
        "godot_keep_alive",
        "effect_probe",
        "freeze_game_clock", "unfreeze_game_clock",
        "step_game_time", "step_until",
        "game_bridge_manage",
        "physics_manage",
        "asset_manage",
        "generate_game_art", "generate_game_art_flux",
        "apply_game_art",
        "generate_3d_asset", "generate_3d_placeholder",
        "audio_manage", "generate_audio_sfx",
        "anim_manage", "create_animation_tree",
        "camera_manage",
        "vfx_manage",
        "shader_manage",
        "shader_generate", "shader_list_templates",
        "raycast_manage",
        "create_light_2d",
        "load_scene_async",
        "batch_atomic_edit", "add_nodes_batch",
        "set_properties_batch",
        "inject_input_event", "simulate_input_sequence",
        "watch_signal", "watch_state_start", "watch_state_collect",
        "record_gameplay_gif", "start_recording", "stop_recording",
        "analyze_signal_flow",
    
        "skeleton_set_bone_pose",
        "skeleton_create_bone",
        "skeleton_create_ik_chain",
        "csg_create_node",
        "gi_create_node",
        "scene_fx_create_node",
        "sky_create_procedural",
        "camera_configure_attributes",
        "multimesh_create_instance",
        "physics_create_joint",
        "physics_configure_body",
        "physics_query_area_overlap",
        "physics_raycast_query",
        "runtime_connect_signal",
        "runtime_disconnect_signal",
        "runtime_emit_signal",
        "runtime_watch_signal",
},
    "CONTEUDO": {
        "tilemap_manage",
        "navigation_manage",
        "create_parallax_background", "add_parallax_layer", "create_spritesheet",
        "optimize_sprite", "remove_background",
        "create_path_2d", "create_patrol_route",
        "create_gun_system", "create_bullet_template",
        "dialogue_manage", "inventory_manage",
        "d3_manage",
        "gamestate_manage",
        "import_3d_model", "import_asset_manifest",
        "create_asset_manifest",
        "download_asset", "import_downloaded_asset",
        "marketplace_search", "marketplace_download",
        "generate_dungeon_rooms", "dungeon_generate",
        "terrain_generate", "wave_generate",
        "dps_calculator", "balance_analyze",
        "loot_table_generate",
        "juice_apply", "juice_list_presets",
        "setup_localization", "add_translation_string",
        "generate_voice",
        "find_unused_resources",
    
        "network_setup_multiplayer",
        "network_create_rpc",
        "network_create_websocket",
        "network_configure_dedicated_server",
        "network_create_lobby",
        "render_set_antialiasing",
        "render_set_scaling",
        "render_set_quality",
},
    "POLIMENTO": {
        "run_gut_tests", "run_scripted_tests",
        "regression_test", "smoke_test",
        "run_verification_pipeline",
        "debug_manage",
        "debugger_set_breakpoint", "debugger_status", "debugger_step",
        "debugger_get_stack", "debugger_get_variables",
        "vision_manage",
        "profile_frame", "profile_memory",
        "set_safety_policy",
        "security_status",
        "configure_security",
        "circuit_breaker_status",
        "get_audit_log", "get_audit_replay",
        "auto_screenshot",
        "estimate_tool_tokens",
        "workflow_handoff", "workflow_snapshot",
        "generate_ci_snippet",
        "find_unused_resources",
        "set_auto_dismiss",
        "test_manage",
        "vibe_coding_mode", "get_vibe_context",
    
        "runtime_list_signals",
},
    "PRONTO_PARA_LANCAR": {
        "export_manage",
        "build_csharp",
        "configure_export_preset",
        "deploy_itch",
        "release_checklist",
        "addon_connect", "addon_disconnect", "addon_ping",
        "addon_is_available", "addon_get_scene_tree",
        "addon_take_screenshot",
        "addon_create_node", "addon_delete_node", "addon_set_property",
        "addon_duplicate_node", "addon_reparent_node",
        "addon_batch_edit",
        "read_console_output",
    
        "csharp_build_project",
},
}

PHASE_ORDER_FILTER = ["IDEIA", "DESIGN", "PROTOTIPO", "CONTEUDO", "POLIMENTO", "PRONTO_PARA_LANCAR"]

# ── Opcao C: CORE sempre visivel + ferramentas da fase atual ──
# CORE = tools essenciais em QUALQUER fase (27 ferramentas).


======================================================================
SECAO 4d — TOOL_PROFILES
======================================================================
ARQUIVO: server.py — linha 328

    "core": [
        "ping", "health_check", "self_test", "bootstrap_godot_mcp",
        "read_file", "write_file", "safe_write_gdscript",
        "compile_test", "run_game", "stop_game", "smart_restart",
        "git_commit_checkpoint", "smoke_test", "dump_mcp_state",
        "project_manage",
    ],
    "dev": [
        "godot",
        "ping", "health_check", "self_test", "bootstrap_godot_mcp",
        "read_file", "write_file", "safe_write_gdscript",
        "compile_test", "run_game", "stop_game", "smart_restart",
        "git_commit_checkpoint", "smoke_test", "dump_mcp_state",
        "project_manage", "scene_manage", "node_manage", "script_manage",
        "file_manage", "asset_manage", "runtime_manage",
        "validate_gdscript_syntax", "validate_project_refs", "find_usages",
        "run_scripted_tests", "regression_test",
        "run_gut_tests", "godot_class_ref", "godot_exec", "effect_probe",
        "take_screenshot", "capture_runtime_errors", "get_runtime_state_digest",
        "import_asset_manifest", "create_asset_manifest",
        # ── Phase management (Feature 8: tool_list_changed) ──
        "get_current_phase", "advance_phase", "get_phase_history",
        "get_next_step", "resume_session",
    ],
    "lean": [
        "godot",
        "ping", "health_check", "self_test", "bootstrap_godot_mcp",
        "read_file", "write_file", "safe_write_gdscript",
        # ── Meta-tools (Fatia 0.15) ──
        "catalog_search", "describe_tool", "invoke_by_name",
        # ── Phase management ──
        "get_current_phase", "advance_phase", "get_phase_history",
        "get_next_step", "resume_session",
    ],
    "full": [],  # vazio = sem filtro (todas as tools)
}

_ACTIVE_PROFILE = _resolve_tool_profile()
if _ACTIVE_PROFILE and _ACTIVE_PROFILE != "full":
    if _ACTIVE_PROFILE in TOOL_PROFILES:
        _PROFILE_TOOLS = set(TOOL_PROFILES[_ACTIVE_PROFILE])
        print(f"[MCP] Profile '{_ACTIVE_PROFILE}': {len(_PROFILE_TOOLS)} tools", file=sys.stderr)
    else:
        print(f"[MCP] Profile '{_ACTIVE_PROFILE}' desconhecido. Use: {sorted(TOOL_PROFILES.keys())}", file=sys.stderr)
        _PROFILE_TOOLS = set(TOOL_PROFILES["dev"])  # fallback seguro
elif _ACTIVE_PROFILE == "full":
    _PROFILE_TOOLS = None  # sem filtro = todas as tools (~134)
else:
    # Default: full profile (sem filtro). Opcao C (CORE + fase) ja limita por fase
    # Mantem maximo de 92 tools (PROTOTIPO), bem abaixo do limite de 128 do DeepSeek V4.
    _PROFILE_TOOLS = None

# ── Feature 8: Toolsets por Fase (--phase) ────────────────────
# Filtro dinâmico: consulta get_current_phase() do projeto ativo
# a cada _tool_defs(). Cumulativo: cada fase herda tools da anterior.
# NÃO filtra _build_handlers() — visibilidade, não bloqueio.


======================================================================
SECAO 4e — _apply_hints() + _HINT_RULES (completo)
======================================================================
ARQUIVO: server.py — linha 1360

_HINT_RULES = {
    "readOnly": {
        "prefixes": ["get_", "list_", "read_", "query_", "search_", "inspect_",
                     "validate_", "check_", "find_", "suggest_", "analyze_",
                     "capture_", "detect_", "estimate_", "compare_"],
        "suffixes": ["_status", "_info", "_history", "_output", "_map",
                    "_state", "_summary", "_catalog", "_health"],
        "exact": ["ping", "health_check", "self_test", "project_map",
                  "tool_catalog", "tool_groups", "get_project_history",
                  "gdscript_hover", "gdscript_symbols", "gdscript_diagnostics",
                  "gdscript_references", "gdscript_definition",
                  "security_status", "get_audit_log", "get_safety_policy",
                  "get_undo_history", "get_vibe_context",
                  "get_runtime_state_digest", "capture_runtime_errors",
                  "detect_empty_screen", "detect_offscreen_elements"],
    },
    "destructive": {
        "prefixes": ["delete_", "remove_", "destroy_", "clear_", "reset_",
                    "close_", "stop_", "kill_", "wipe_"],
        "exact": ["restore_backup", "undo_last_action", "push_undo",
                  "detach_script", "build_export", "configure_security",
                  "set_safety_policy"],
    },
    "idempotent": {
        "prefixes": ["create_", "set_", "write_", "configure_", "import_",
                    "generate_", "register_", "install_", "add_"],
        "suffixes": ["_checkpoint", "_snapshot"],
        "exact": ["batch_atomic_edit", "attach_script", "connect_signal",
                  "safe_write_gdscript"],
    },
    "openWorld": {
        "prefixes": ["download_", "fetch_", "generate_game_art", "generate_voice",
                    "search_codebase", "web_", "http_"],
        "exact": ["generate_game_art_flux", "generate_audio_sfx",
                  "download_asset", "import_downloaded_asset",
                  "game_http_request", "game_websocket"],
    },
}


def _apply_hints(tools: list) -> list:
    """Garante que toda tool tenha os 4 hints MCP.

    Regras:
    - Se o hint JÁ existe na tool, respeita o valor existente
    - Se NÃO existe, aplica a regra por nome
    - Se nenhuma regra bate, defaults seguros:
      readOnlyHint=False, destructiveHint=False,
      idempotentHint=False, openWorldHint=False
    """
    for tool in tools:
        ann = getattr(tool, 'annotations', None) or {}

        name = tool.name

        # readOnlyHint
        if 'readOnlyHint' not in ann:
            is_readonly = (
                any(name.startswith(p) for p in _HINT_RULES["readOnly"]["prefixes"]) or
                any(name.endswith(s) for s in _HINT_RULES["readOnly"]["suffixes"]) or
                name in _HINT_RULES["readOnly"]["exact"]
            )
            ann['readOnlyHint'] = is_readonly

        # destructiveHint
        if 'destructiveHint' not in ann:
            is_destructive = (
                any(name.startswith(p) for p in _HINT_RULES["destructive"]["prefixes"]) or
                name in _HINT_RULES["destructive"]["exact"]
            )
            ann['destructiveHint'] = is_destructive

        # idempotentHint
        if 'idempotentHint' not in ann:
            is_idempotent = (
                any(name.startswith(p) for p in _HINT_RULES["idempotent"]["prefixes"]) or
                any(name.endswith(s) for s in _HINT_RULES["idempotent"]["suffixes"]) or
                name in _HINT_RULES["idempotent"]["exact"]
            )
            ann['idempotentHint'] = is_idempotent

        # openWorldHint
        if 'openWorldHint' not in ann:
            is_openworld = (
                any(name.startswith(p) for p in _HINT_RULES["openWorld"]["prefixes"]) or
                name in _HINT_RULES["openWorld"]["exact"]
            )
            ann['openWorldHint'] = is_openworld

        # intrusiveHint (Fatia 1.6) — default: modo silencioso
        if 'intrusiveHint' not in ann:
            ann['intrusiveHint'] = False

        # ── A6.5: MCP Spec annotations (audience, priority, lastModified) ──
        if 'audience' not in ann:
            # Tools que afetam o runtime são "user", o resto é "assistant"
            is_user_facing = (
                name in ("godot", "run_game", "stop_game", "take_screenshot") or
                any(name.startswith(p) for p in ("export_", "deploy_", "run_", "stop_"))
            )
            ann['audience'] = ["user"] if is_user_facing else ["assistant"]

        if 'priority' not in ann:
            # Core/bootstrap tools = prioridade máxima
            _CORE_PREFIXES = ("ping", "health_check", "self_test", "bootstrap", "validate_mcp", "tool_catalog", "tool_groups", "godot")
            if name.startswith(_CORE_PREFIXES):
                ann['priority'] = 1.0
            elif any(name.startswith(p) for p in ("validate_", "audit_", "debug_")):
                ann['priority'] = 0.3
            else:
                ann['priority'] = 0.7

        if 'lastModified' not in ann:
            ann['lastModified'] = "2026-07-19T00:00:00Z"

        tool.annotations = ann

    return tools


# ══════════════════════════════════════════════════════════════
# Onda 5: compactar descricoes (-80% tokens)
# ══════════════════════════════════════════════════════════════

def _compact_description(description: str, max_chars: int = 120) -> str:


======================================================================
SECAO 4f — core/tool_definitions.py (30 primeiras linhas)
======================================================================
ARQUIVO: core/tool_definitions.py

"""core/tool_definitions.py - Raw Tool Definitions (Etapa A5).

Contem APENAS a lista bruta de objetos Tool().
Extraido de server.py:_tool_defs() para reduzir tamanho.
"""

from __future__ import annotations

from mcp.types import Tool


def _raw_tool_defs() -> list[Tool]:
    """Retorna a lista bruta de ferramentas (SEM filtros)."""
    return [
        Tool(
            name="ping",
            description=(
                "Verifica se o servidor godot-mcp-agent está funcional e conectado. "
                "Use esta tool no início de cada sessão para confirmar que o MCP está vivo. "
                "Quando usar: primeira chamada da sessão, ou quando suspeitar que o servidor caiu. "
                "Quando NÃO usar: durante fluxo normal de criação de jogos (desnecessário). "
                "Pré-condições: nenhuma — o servidor só precisa estar em execução. "
                "Exemplo de input: {} (chamada sem argumentos). "
                "Erro mais comum: timeout ou conexão recusada — significa que o servidor não está rodando; "
                "verifique se server.py está em execução no terminal."
            ),
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="budget_manage",

