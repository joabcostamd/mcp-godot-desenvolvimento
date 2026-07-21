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
    # ── F5: UI atomics consolidation ──
    create_ui_widget,
    create_tab_with_content,
    configure_ui_focus_and_nav,
    set_tooltip,
    set_anchor_preset,
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
    """ui_manage: 12 operações de interface."""
    return create_manage_tool(
        tool_name="ui_manage",
        description="Gerencia interfaces: criar UI, adicionar controles, menus, HUD, loading screen, widgets, tooltips e navegação por foco.",
        ops={
            "create_root": create_ui_scene,
            "add_control": add_control_node,
            "main_menu": create_main_menu,
            "hud": create_hud_template,
            "pause_menu": create_pause_menu,
            "health_bar": create_health_bar,
            "loading_screen": create_loading_screen,
            "create_widget": create_ui_widget,
            "create_tab": create_tab_with_content,
            "config_focus": configure_ui_focus_and_nav,
            "set_tooltip": set_tooltip,
            "set_anchor": set_anchor_preset,
        },
        tool_hints={"destructiveHint": True, "idempotentHint": False, "openWorldHint": True},
        title="Gerenciar UI",
        tags=["ui", "interface", "menu", "hud", "widget"],
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
    """debug_manage: 9 operações (debug + debugger)."""
    from tools.debugger_ops import (
        debugger_set_breakpoint, debugger_status, debugger_step,
        debugger_get_stack, debugger_get_variables,
    )
    return create_manage_tool(
        tool_name="debug_manage",
        description="Gerencia debug: performance, colisões, navegação, breakpoints, stack e variáveis.",
        ops={
            "perf_stats": get_performance_stats,
            "collision_debug": enable_debug_collisions,
            "nav_debug": enable_debug_navigation,
            "perf_regression": perf_regression_track,
            "set_breakpoint": debugger_set_breakpoint,
            "status": debugger_status,
            "step": debugger_step,
            "get_stack": debugger_get_stack,
            "get_vars": debugger_get_variables,
        },
        tool_hints={"destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
        title="Gerenciar Debug",
        tags=["debug", "diagnóstico", "visualização", "debugger"],
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


def _build_godot_manage():
    """godot_manage: 6 operações de execução Godot (F5 consolidation)."""
    return create_manage_tool(
        tool_name="godot_manage",
        description=(
            "Gerencia a execução do Godot: rodar/parar projeto, executar GDScript, "
            "obter runtime info, esperar bridge. "
            "Use para controlar o ciclo de vida do jogo durante prototipagem."
        ),
        ops={
            "run_project": _godot_run_handler,
            "stop_project": _godot_stop_handler,
            "wait_bridge": _godot_wait_handler,
            "exec_gdscript": _godot_exec_handler,
            "runtime_info": _godot_info_handler,
        },
        tool_hints={"destructiveHint": True, "idempotentHint": False, "openWorldHint": True},
        title="Gerenciar Execução Godot",
        tags=["godot", "runtime", "execução", "prototipo"],
    )


# ── Handlers godot_manage (wrappers) ──────────────────────────────

def _godot_run_handler(**params) -> dict:
    """Lança o projeto Godot. params: project_path, godot_executable."""
    import json as _json, subprocess, sys, os
    pp = params.get("project_path", "")
    ge = params.get("godot_executable", "")
    if not pp or not ge:
        return {"status": "error", "message": "project_path e godot_executable obrigatorios"}
    try:
        proc = subprocess.Popen(
            [ge, "--path", pp],
            stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            close_fds=True,
        )
        return {"status": "success", "pid": proc.pid}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


def _godot_stop_handler(**params) -> dict:
    """Para o processo Godot. params: pid."""
    import json as _json, subprocess, sys, os
    pid = params.get("pid", 0)
    if not pid:
        return {"status": "error", "message": "pid obrigatorio"}
    try:
        if sys.platform == "win32":
            from tools.subprocess_utils import run_subprocess_safe
            result = run_subprocess_safe(["taskkill", "/F", "/PID", str(pid)], timeout=10)
            if result.returncode != 0:
                return {"status": "error", "message": f"taskkill falhou: {result.stderr.strip()}"}
        else:
            import signal
            os.kill(pid, signal.SIGKILL)
        return {"status": "success", "pid": pid}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


def _godot_wait_handler(**params) -> dict:
    """Espera o bridge responder. params: timeout_sec (default 10)."""
    import time, json as _json
    timeout = params.get("timeout_sec", 10)
    try:
        from server import send_bridge_command, BridgeUnavailable
    except ImportError:
        return {"status": "error", "message": "Bridge não disponível neste contexto"}
    start = time.time()
    while time.time() - start < timeout:
        try:
            result = send_bridge_command({"cmd": "runtime_info"})
            return {"status": "success", "data": result}
        except BridgeUnavailable:
            time.sleep(0.3)
    return {"status": "error", "message": f"bridge não respondeu em {timeout}s"}


def _godot_exec_handler(**params) -> dict:
    """Executa GDScript no jogo. params: code."""
    import json as _json
    code = params.get("code", "")
    if not code:
        return {"status": "error", "message": "code obrigatorio"}
    try:
        from tools.playtest_ops import godot_exec
        result = godot_exec(code=code)
        if isinstance(result, str):
            result = _json.loads(result)
        return result if isinstance(result, dict) else {"status": "success", "data": result}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


def _godot_info_handler(**params) -> dict:
    """Obtém FPS, draw calls, memória. Sem params."""
    import json as _json
    try:
        from server import send_bridge_command, BridgeUnavailable
    except ImportError:
        return {"status": "error", "message": "Bridge não disponível"}
    try:
        result = send_bridge_command({"cmd": "runtime_info"})
        return {"status": "success", "data": result}
    except BridgeUnavailable as e:
        return {"status": "error", "message": str(e)}


def _build_lsp_manage():
    """lsp_manage: 9 operações de introspecção GDScript/LSP (F5 consolidation)."""
    from tools.lsp_ops import (
        gdscript_lsp_connect, gdscript_lsp_disconnect, gdscript_sync_file,
        gdscript_definition, gdscript_references, gdscript_hover,
        gdscript_symbols, gdscript_rename, gdscript_diagnostics,
    )
    return create_manage_tool(
        tool_name="lsp_manage",
        description=(
            "Introspecção GDScript via LSP: conecta ao Godot, analisa código, "
            "busca definições, referências, símbolos, diagnósticos e renomeia."
        ),
        ops={
            "connect": gdscript_lsp_connect,
            "disconnect": gdscript_lsp_disconnect,
            "sync": gdscript_sync_file,
            "definition": gdscript_definition,
            "references": gdscript_references,
            "hover": gdscript_hover,
            "symbols": gdscript_symbols,
            "rename": gdscript_rename,
            "diagnostics": gdscript_diagnostics,
        },
        tool_hints={"destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
        title="Introspecção GDScript (LSP)",
        tags=["lsp", "gdscript", "análise", "código"],
    )


def _build_skeleton_manage():
    """skeleton_manage: 6 operações de esqueleto 2D (F5 consolidation)."""
    from tools.skeleton_ops import (
        get_bone_pose, set_bone_pose, list_bones,
        create_bone, create_ik_chain, get_skeleton_info,
    )
    return create_manage_tool(
        tool_name="skeleton_manage",
        description=(
            "Gerencia esqueletos 2D (Skeleton2D): consultar ossos, "
            "obter/definir poses, criar ossos e cadeias IK."
        ),
        ops={
            "get_info": get_skeleton_info,
            "list_bones": list_bones,
            "get_pose": get_bone_pose,
            "set_pose": set_bone_pose,
            "create_bone": create_bone,
            "create_ik": create_ik_chain,
        },
        tool_hints={"destructiveHint": True, "idempotentHint": False, "openWorldHint": True},
        title="Gerenciar Esqueleto 2D",
        tags=["skeleton", "2D", "animação", "bones"],
    )


def _build_network_manage():
    """network_manage: 5 operações de rede (F5 consolidation)."""
    from tools.network_ops import (
        setup_multiplayer_peer, create_rpc_method, create_websocket_client,
        configure_dedicated_server, create_lobby_system,
    )
    return create_manage_tool(
        tool_name="network_manage",
        description=(
            "Gerencia rede multiplayer: configurar peer, criar RPCs, "
            "WebSocket client, servidor dedicado e sistema de lobby."
        ),
        ops={
            "setup_peer": setup_multiplayer_peer,
            "create_rpc": create_rpc_method,
            "create_ws": create_websocket_client,
            "config_server": configure_dedicated_server,
            "create_lobby": create_lobby_system,
        },
        tool_hints={"destructiveHint": True, "idempotentHint": False, "openWorldHint": True},
        title="Gerenciar Rede",
        tags=["network", "multiplayer", "rpc", "websocket"],
    )


def _build_render_manage():
    """render_manage: 4 operações de renderização (F5 consolidation)."""
    from tools.render_ops import (
        get_render_settings, set_antialiasing, set_scaling_mode, set_render_quality,
    )
    return create_manage_tool(
        tool_name="render_manage",
        description="Gerencia renderização: consultar configs, anti-aliasing, scaling e qualidade.",
        ops={
            "get": get_render_settings,
            "set_aa": set_antialiasing,
            "set_scale": set_scaling_mode,
            "set_quality": set_render_quality,
        },
        tool_hints={"destructiveHint": True, "idempotentHint": False, "openWorldHint": False},
        title="Gerenciar Renderização",
        tags=["render", "gráfico", "qualidade"],
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
    # F5: godot execution consolidation
    _build_godot_manage,
    # F5: lsp consolidation
    _build_lsp_manage,
    # F5: skeleton consolidation
    _build_skeleton_manage,
    # F5: network consolidation
    _build_network_manage,
    # F5: render consolidation
    _build_render_manage,
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
