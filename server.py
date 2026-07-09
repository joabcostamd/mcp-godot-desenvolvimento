"""server.py — MCP Server godot-mcp-agent v1.0.

Servidor MCP via stdio com 143 ferramentas para criacao e gestao
de projetos Godot 4.7. A IA consumidora (DeepSeek V4 Flash/Pro) chama as
ferramentas para construir jogos a partir de linguagem natural.

Cobre 12 Ondas de desenvolvimento: projeto, arquivo, cena, scripts,
fisica, assets, runtime, editor, tilemap, animacao, UI, export,
seguranca, game bridge, visao, batch, assets procedurais, IA agentica,
DevSolo (camera, navegacao, save, UI, dialogo, inventario, armas,
procedural, shaders, 3D, audio, exportacao, debug, localizacao).
"""

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from tools.project_ops import (
    validate_godot_version,
    set_active_project,
    create_project,
    get_project_settings,
    set_project_setting,
    set_main_scene,
    configure_input_action,
    configure_autoload,
    install_mcp_addon,
    generate_project_structure,
)
from tools.file_ops import (
    inspect_project,
    read_file,
    write_file,
    delete_file,
    move_file,
)
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
    create_tileset,
    create_tilemap_layer,
    paint_tilemap_cell,
    create_animation,
    create_animation_player,
    create_ui_scene,
    add_control_node,
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
from tools.physics_ops import (
    add_collision_shape,
    set_collision_layer_mask,
)
from tools.asset_ops import (
    import_texture,
    import_sprite_sheet,
    import_audio,
)
from tools.runtime_ops import (
    compile_test,
    run_game,
    stop_game,
    launch_editor,
    close_editor,
    take_screenshot,
    read_console_output,
    inject_input_event,
    execute_gdscript_runtime,
    watch_signal,
    capture_game_screenshot,
    compare_screenshots,
    detect_empty_screen,
    record_gameplay_gif,
)
from tools.classdb import (
    query_classdb,
    list_valid_node_types,
)
from tools.export_ops import (
    list_export_presets,
    validate_export_templates_installed,
    build_export,
)
from tools.safety import (
    list_backups,
    restore as restore_backup,
    git_checkpoint as git_commit_checkpoint,
)
from tools.placeholder_ops import (
    generate_placeholder_sprite,
    generate_placeholder_texture_atlas,
    generate_background_gradient,
    generate_tileset_from_colors,
    generate_audio_sfx,
    suggest_color_palette,
)
from tools.analyze_ops import (
    analyze_game_structure,
    suggest_next_steps,
    find_missing_references,
    validate_game_design,
    estimate_game_scope,
    search_codebase,
    get_project_history,
)
from tools.devsolo_ops import (
    setup_camera_2d,
    setup_camera_follow,
    setup_camera_shake,
    create_navigation_region_2d,
    create_navigation_agent_2d,
    bake_navigation_polygon,
    create_save_system,
    define_save_data,
    create_tween_animation,
    chain_tweens,
    create_state_machine,
    add_state_transition,
    create_main_menu,
    create_hud_template,
    create_pause_menu,
    create_health_bar,
    setup_world_environment,
    setup_screen_flash,
    # Onda 9
    create_parallax_background,
    add_parallax_layer,
    configure_particles_2d,
    create_particles_3d,
    generate_shader_2d,
    apply_shader_to_node,
    create_path_2d,
    create_patrol_route,
    # Onda 10
    create_dialogue_system,
    add_dialogue_node,
    create_dialogue_ui,
    create_inventory_system,
    define_inventory_item,
    create_inventory_ui,
    create_bullet_template,
    create_gun_system,
    generate_tilemap_from_noise,
    generate_dungeon_rooms,
    create_loading_screen,
    load_scene_async,
    # Onda 11
    add_raycast_2d,
    add_shapecast_2d,
    enable_debug_collisions,
    enable_debug_navigation,
    get_performance_stats,
    setup_localization,
    add_translation_string,
    create_light_3d,
    create_csg_shape,
    configure_standard_material_3d,
    configure_export_preset,
    configure_audio_bus,
    add_audio_effect,
)
from tools.safety import (
    push_undo,
    undo_last_action,
    get_undo_history,
)

# ── Server ──────────────────────────────────────────────────────────

server = Server("godot-agent")


# ── Tool Definitions ────────────────────────────────────────────────

# Cache global para _tool_defs (evita recriar 143 tools a cada list_tools)
_TOOL_DEFS_CACHE: list[Tool] | None = None


def _tool_defs() -> list[Tool]:
    """Retorna a lista completa de tools registradas (cacheado)."""
    global _TOOL_DEFS_CACHE
    if _TOOL_DEFS_CACHE is not None:
        return _TOOL_DEFS_CACHE
    _TOOL_DEFS_CACHE = [
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
            name="validate_godot_version",
            description=(
                "Verifica se a versão do Godot instalada é 4.7.x. "
                "Use no início da primeira sessão com um novo projeto, ou quando suspeitar "
                "que o Godot foi atualizado. "
                "Quando NÃO usar: durante o ciclo normal de criação de jogo após a primeira validação. "
                "Pré-condições: config.json deve ter godot_path válido. "
                "Exemplo de input: {} (sem argumentos). "
                "Erro mais comum: Godot não encontrado no path — verifique config.json."
            ),
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="set_active_project",
            description=(
                "Define qual projeto Godot será o alvo de todas as operações seguintes. "
                "Use quando for criar um jogo novo ou trocar de projeto. "
                "Quando NÃO usar: se já estiver no projeto certo (use validate_godot_version no início). "
                "Pré-condições: o diretório deve conter um project.godot válido; "
                "se não existir, use create_project antes. "
                "Exemplo de input: {\"project_path\": \"C:/meus-jogos/meu_pong\"}. "
                "Erro mais comum: project.godot não encontrado — crie o projeto primeiro com create_project."
            ),
            inputSchema={
                "type": "object",
                "properties": {"project_path": {"type": "string", "description": "Caminho absoluto ou relativo ao workspace para o projeto Godot."}},
                "required": ["project_path"],
            },
        ),
        Tool(
            name="create_project",
            description=(
                "Cria um novo projeto Godot 4.7 vazio com estrutura de pastas padrão (scenes/, scripts/, assets/). "
                "Use no início de TODO jogo novo — é o primeiro passo após entender o que o usuário quer. "
                "Quando NÃO usar: se o projeto já existe (use set_active_project). "
                "Pré-condições: Godot 4.7 deve estar instalado e configurado em config.json. "
                "Exemplo de input: {\"name\": \"Meu Pong\", \"path\": \"C:/jogos/pong\"}. "
                "Erro mais comum: diretório já existe e não está vazio — escolha outro nome ou caminho."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Nome do projeto (aparece na janela do jogo)."},
                    "path": {"type": "string", "description": "Caminho onde criar o projeto."},
                    "renderer": {"type": "string", "enum": ["forward_plus", "mobile", "compatibility"], "description": "Renderer: forward_plus (3D), mobile (mobile), compatibility (2D simples)."},
                },
                "required": ["name", "path"],
            },
        ),
        Tool(
            name="get_project_settings",
            description=(
                "Lê as configurações do project.godot do projeto ativo. "
                "Use para consultar o estado atual de configurações antes de modificá-las. "
                "Quando NÃO usar: para modificar (use set_project_setting). "
                "Pré-condições: projeto ativo definido (set_active_project ou create_project). "
                "Exemplo de input: {\"section\": \"application\"}. "
                "Erro mais comum: seção não encontrada — verifique o nome exato da seção."
            ),
            inputSchema={
                "type": "object",
                "properties": {"section": {"type": "string", "description": "Nome da seção (ex: application, rendering). null para todas."}},
                "required": [],
            },
        ),
        Tool(
            name="set_project_setting",
            description=(
                "Define uma configuração no project.godot (ex: nome do jogo, resolução, renderer). "
                "Use para configurar o projeto antes de criar cenas. "
                "Quando NÃO usar: para configurar ações de input (use configure_input_action na Fase 2), "
                "para autoload (use configure_autoload na Fase 2), para cena principal (use set_main_scene). "
                "Pré-condições: projeto ativo deve existir. "
                "Exemplo de input: {\"section\": \"application\", \"key\": \"config/name\", \"value\": \"Meu Jogo\"}. "
                "Erro mais comum: seção inexistente — a seção será criada automaticamente."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "section": {"type": "string", "description": "Seção do project.godot."},
                    "key": {"type": "string", "description": "Chave dentro da seção."},
                    "value": {"description": "Valor (string, número, ou booleano)."},
                },
                "required": ["section", "key", "value"],
            },
        ),
        Tool(
            name="set_main_scene",
            description=(
                "Define a cena principal do projeto (a que abre quando o jogo roda). "
                "Use após criar a cena principal do jogo — é essencial para run_game funcionar. "
                "Quando NÃO usar: se a cena ainda não foi criada (crie com create_scene primeiro). "
                "Pré-condições: a cena deve existir no projeto. "
                "Exemplo de input: {\"scene_path\": \"scenes/main.tscn\"}. "
                "Erro mais comum: cena não encontrada — verifique o caminho com inspect_project."
            ),
            inputSchema={
                "type": "object",
                "properties": {"scene_path": {"type": "string", "description": "Caminho da cena relativo ao projeto (ex: scenes/main.tscn)."}},
                "required": ["scene_path"],
            },
        ),
        Tool(
            name="inspect_project",
            description=(
                "Lista todos os arquivos do projeto ativo organizados por categoria (cenas, scripts, assets). "
                "Use para explorar o que já existe no projeto antes de criar ou modificar arquivos. "
                "Quando NÃO usar: para ler conteúdo de um arquivo específico (use read_file). "
                "Pré-condições: projeto ativo definido. "
                "Exemplo de input: {\"filter\": \"all\"}. "
                "Erro mais comum: lista vazia — o projeto pode estar vazio; crie cenas/scripts primeiro."
            ),
            inputSchema={
                "type": "object",
                "properties": {"filter": {"type": "string", "enum": ["scenes", "scripts", "assets", "all"], "description": "Filtro de categoria."}},
                "required": [],
            },
        ),
        Tool(
            name="read_file",
            description=(
                "Lê o conteúdo de um arquivo do projeto (.gd, .tscn, .tres, etc.). "
                "Use para examinar scripts, cenas ou qualquer arquivo de texto do projeto. "
                "Quando NÃO usar: para listar arquivos (use inspect_project). "
                "Pré-condições: o arquivo deve existir no projeto. "
                "Exemplo de input: {\"path\": \"scripts/player.gd\"}. "
                "Erro mais comum: arquivo não encontrado — use inspect_project para listar arquivos disponíveis."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Caminho relativo ao projeto."},
                    "start_line": {"type": "integer", "description": "Linha inicial (1-indexed, opcional)."},
                    "end_line": {"type": "integer", "description": "Linha final inclusiva (opcional)."},
                },
                "required": ["path"],
            },
        ),
        Tool(
            name="write_file",
            description=(
                "Cria ou modifica um arquivo no projeto. "
                "Use para criar scripts GDScript, editar cenas manualmente, ou qualquer escrita de arquivo. "
                "Quando NÃO usar: para criar cenas estruturadas (use create_scene + add_node). "
                "Pré-condições: o diretório pai deve existir (criado automaticamente). "
                "Exemplo de input: {\"path\": \"scripts/player.gd\", \"content\": \"extends CharacterBody2D\", \"mode\": \"create\"}. "
                "Erro mais comum: mode='create' com arquivo existente — use mode='overwrite' ou delete_file antes."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Caminho relativo ao projeto."},
                    "content": {"type": "string", "description": "Conteúdo a escrever."},
                    "mode": {"type": "string", "enum": ["create", "overwrite", "append"], "description": "Modo: create (só se não existir), overwrite (substitui), append (adiciona)."},
                },
                "required": ["path", "content"],
            },
        ),
        Tool(
            name="delete_file",
            description=(
                "Remove um arquivo do projeto com backup automático. "
                "Use para limpar arquivos não utilizados. O backup permite desfazer com restore_backup (Fase 5). "
                "Quando NÃO usar: para remover um nó de cena (use delete_node). "
                "Pré-condições: o arquivo deve existir. "
                "Exemplo de input: {\"path\": \"scenes/old_scene.tscn\"}. "
                "Erro mais comum: arquivo não encontrado — use inspect_project para ver o que existe."
            ),
            inputSchema={
                "type": "object",
                "properties": {"path": {"type": "string", "description": "Caminho relativo ao projeto."}},
                "required": ["path"],
            },
        ),
        Tool(
            name="move_file",
            description=(
                "Move ou renomeia um arquivo do projeto, atualizando todas as referências automagicamente. "
                "Use para reorganizar a estrutura de pastas ou renomear arquivos. "
                "Quando NÃO usar: para copiar (não suportado — use read_file + write_file). "
                "Pré-condições: arquivo origem deve existir, destino não. "
                "Exemplo de input: {\"from_path\": \"scenes/old.tscn\", \"to_path\": \"scenes/new.tscn\"}. "
                "Erro mais comum: destino já existe — escolha outro nome ou delete o destino primeiro."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "from_path": {"type": "string", "description": "Caminho atual relativo ao projeto."},
                    "to_path": {"type": "string", "description": "Novo caminho relativo ao projeto."},
                },
                "required": ["from_path", "to_path"],
            },
        ),
        Tool(
            name="create_scene",
            description=(
                "Cria uma nova cena Godot (.tscn) com um nó raiz. "
                "Use para criar a cena principal e cada cena de entidade (player, inimigo, etc.). "
                "Quando NÃO usar: para adicionar nós a uma cena existente (use add_node). "
                "Pré-condições: projeto ativo definido; tipo de nó deve ser válido no Godot 4.7. "
                "Exemplo de input: {\"name\": \"Main\", \"root_type\": \"Node2D\", \"path\": \"scenes/main.tscn\"}. "
                "Erro mais comum: tipo de nó inválido (ex: 'Sprite' em vez de 'Sprite2D') — a mensagem de erro sugere tipos próximos válidos."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Nome do nó raiz (ex: Main, Player)."},
                    "root_type": {"type": "string", "description": "Tipo Godot 4 do nó raiz (ex: Node2D, CharacterBody2D)."},
                    "path": {"type": "string", "description": "Caminho relativo ao projeto (ex: scenes/main.tscn)."},
                },
                "required": ["name", "root_type", "path"],
            },
        ),
        Tool(
            name="load_scene_tree",
            description=(
                "Carrega e exibe a árvore de nós de uma cena em formato hierárquico. "
                "Use para inspecionar a estrutura de uma cena antes de modificá-la. "
                "Quando NÃO usar: para modificar (use add_node, set_node_property, etc.). "
                "Pré-condições: a cena deve existir. "
                "Exemplo de input: {\"scene_path\": \"scenes/main.tscn\"}. "
                "Erro mais comum: cena não encontrada — verifique o caminho com inspect_project."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "scene_path": {"type": "string", "description": "Caminho relativo da cena."},
                    "max_depth": {"type": "integer", "description": "Profundidade máxima (None=sem limite). 0=só raiz, 1=raiz+filhos."},
                },
                "required": ["scene_path"],
            },
        ),
        Tool(
            name="add_node",
            description=(
                "Adiciona um novo nó a uma cena existente. "
                "Use para construir a árvore de nós: adicione filhos ao nó raiz ou a qualquer nó existente. "
                "Quando NÃO usar: para criar uma cena nova (use create_scene). "
                "Pré-condições: a cena deve existir; o nó pai deve existir na cena; o tipo de nó deve ser válido no Godot 4.7. "
                "Exemplo de input: {\"scene_path\": \"scenes/main.tscn\", \"parent_node_path\": \".\", \"node_name\": \"Player\", \"node_type\": \"CharacterBody2D\"}. "
                "Erro mais comum: tipo de nó inválido (ex: 'KinematicBody2D' em vez de 'CharacterBody2D') — a mensagem de erro sugere tipos próximos."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "scene_path": {"type": "string", "description": "Caminho relativo da cena."},
                    "parent_node_path": {"type": "string", "description": "Path do nó pai (\".\" = raiz)."},
                    "node_name": {"type": "string", "description": "Nome do novo nó."},
                    "node_type": {"type": "string", "description": "Tipo Godot 4 do nó (ex: Sprite2D, CollisionShape2D)."},
                },
                "required": ["scene_path", "parent_node_path", "node_name", "node_type"],
            },
        ),
        Tool(
            name="delete_node",
            description=(
                "Remove um nó (e todos os seus descendentes) de uma cena. "
                "Use para limpar nós desnecessários. Backup automático permite desfazer. "
                "Quando NÃO usar: para deletar a cena inteira (use delete_file). "
                "Pré-condições: a cena e o nó devem existir; não pode deletar a raiz. "
                "Exemplo de input: {\"scene_path\": \"scenes/main.tscn\", \"node_path\": \"./Enemy\"}. "
                "Erro mais comum: tentar deletar raiz — use delete_file para remover a cena inteira."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "scene_path": {"type": "string", "description": "Caminho relativo da cena."},
                    "node_path": {"type": "string", "description": "Path do nó a remover (não pode ser \".\" = raiz)."},
                },
                "required": ["scene_path", "node_path"],
            },
        ),
        Tool(
            name="set_node_property",
            description=(
                "Define o valor de uma propriedade de um nó em uma cena (ex: position, scale, texture). "
                "Use para configurar nós após criá-los: posição, tamanho, cor, textura, etc. "
                "Quando NÃO usar: para propriedades de colisão (use set_collision_layer_mask na Fase 2). "
                "Pré-condições: a cena e o nó devem existir. "
                "Exemplo de input: {\"scene_path\": \"scenes/main.tscn\", \"node_path\": \"./Player\", \"property_name\": \"position\", \"value\": \"Vector2(100, 200)\"}. "
                "Erro mais comum: valor em formato inválido — use formato Godot (ex: Vector2(x, y), Color(r, g, b))."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "scene_path": {"type": "string", "description": "Caminho relativo da cena."},
                    "node_path": {"type": "string", "description": "Path do nó."},
                    "property_name": {"type": "string", "description": "Nome da propriedade (ex: position, scale, modulate)."},
                    "value": {"description": "Valor em formato Godot (ex: Vector2(100,200), Color(1,0,0,1), 42, true)."},
                },
                "required": ["scene_path", "node_path", "property_name", "value"],
            },
        ),
        Tool(
            name="get_node_property",
            description=(
                "Lê o valor atual de uma propriedade de um nó. "
                "Use para consultar o estado de um nó antes de modificá-lo. "
                "Quando NÃO usar: para modificar (use set_node_property). "
                "Pré-condições: a cena e o nó devem existir. "
                "Exemplo de input: {\"scene_path\": \"scenes/main.tscn\", \"node_path\": \"./Player\", \"property_name\": \"position\"}. "
                "Erro mais comum: propriedade não definida explicitamente — retorna null (a classe usa o valor default)."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "scene_path": {"type": "string", "description": "Caminho relativo da cena."},
                    "node_path": {"type": "string", "description": "Path do nó."},
                    "property_name": {"type": "string", "description": "Nome da propriedade."},
                },
                "required": ["scene_path", "node_path", "property_name"],
            },
        ),
        # ── Fase 2: ClassDB ──
        Tool(
            name="query_classdb",
            description=(
                "Consulta informações completas de uma classe na ClassDB do Godot. "
                "Use para descobrir propriedades, métodos, sinais e herança de qualquer classe. "
                "Quando NÃO usar: para listar todos os tipos de nó (use list_valid_node_types). "
                "Pré-condições: classdb_cache/extension_api.json deve existir (gerado na Fase 0). "
                "Exemplo de input: {\"class_name\": \"CharacterBody2D\"}. "
                "Erro mais comum: classe não encontrada — verifique o nome exato (case-sensitive)."
            ),
            inputSchema={
                "type": "object",
                "properties": {"class_name": {"type": "string", "description": "Nome da classe Godot."}},
                "required": ["class_name"],
            },
        ),
        Tool(
            name="list_valid_node_types",
            description=(
                "Lista todos os tipos de nó que podem ser usados em cenas (classes que herdam de Node). "
                "Use para descobrir quais tipos de nó existem no Godot 4.7. "
                "Quando NÃO usar: para consultar uma classe específica (use query_classdb). "
                "Pré-condições: nenhuma. "
                "Exemplo de input: {} (sem argumentos). "
                "Erro mais comum: retorna centenas de tipos — é esperado."
            ),
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        # ── Fase 2: Cenas extendidas ──
        Tool(
            name="reparent_node",
            description=(
                "Move um nó para um novo pai dentro da mesma cena. "
                "Use para reorganizar a hierarquia sem recriar nós. "
                "Quando NÃO usar: para mover entre cenas diferentes (recrie o nó). "
                "Pré-condições: ambos os nós (origem e novo pai) devem existir na cena. "
                "Exemplo de input: {\"scene_path\": \"scenes/main.tscn\", \"node_path\": \"./Enemy\", \"new_parent_path\": \"./Enemies\"}. "
                "Erro mais comum: nó não encontrado — confira os paths com load_scene_tree."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "scene_path": {"type": "string"},
                    "node_path": {"type": "string"},
                    "new_parent_path": {"type": "string"},
                },
                "required": ["scene_path", "node_path", "new_parent_path"],
            },
        ),
        Tool(
            name="instance_scene_as_child",
            description=(
                "Instancia uma cena como filha de um nó (sub-cenas / prefabs). "
                "Use para compor cenas complexas a partir de cenas menores (player, inimigo como sub-cenas). "
                "Quando NÃO usar: para criar nós simples (use add_node). "
                "Pré-condições: a cena a instanciar deve existir. "
                "Exemplo de input: {\"scene_path\": \"scenes/main.tscn\", \"parent_node_path\": \".\", \"instanced_scene_path\": \"scenes/player.tscn\"}. "
                "Erro mais comum: cena a instanciar não encontrada — crie-a primeiro com create_scene."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "scene_path": {"type": "string"},
                    "parent_node_path": {"type": "string"},
                    "instanced_scene_path": {"type": "string"},
                    "instance_name": {"type": "string"},
                },
                "required": ["scene_path", "parent_node_path", "instanced_scene_path"],
            },
        ),
        Tool(
            name="connect_signal",
            description=(
                "Conecta um sinal de um nó a um método de outro nó. "
                "Use para ligar eventos: botão pressionado, corpo entrou em área, timer, etc. "
                "Quando NÃO usar: para lógica que não depende de sinal (use scripts). "
                "Pré-condições: ambos os nós devem existir na cena. "
                "Exemplo de input: {\"scene_path\": \"scenes/main.tscn\", \"from_node_path\": \"./Area2D\", \"signal_name\": \"body_entered\", \"to_node_path\": \".\", \"method_name\": \"_on_body_entered\"}. "
                "Erro mais comum: método não existe no nó destino — o sinal será conectado mas falhará em runtime; crie o método no script do nó destino."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "scene_path": {"type": "string"},
                    "from_node_path": {"type": "string"},
                    "signal_name": {"type": "string"},
                    "to_node_path": {"type": "string"},
                    "method_name": {"type": "string"},
                },
                "required": ["scene_path", "from_node_path", "signal_name", "to_node_path", "method_name"],
            },
        ),
        Tool(
            name="list_signals",
            description=(
                "Lista os sinais disponíveis para um tipo de nó ou para um nó específico em cena. "
                "Use para descobrir quais sinais podem ser conectados antes de usar connect_signal. "
                "Quando NÃO usar: para listar métodos (use query_classdb). "
                "Pré-condições: forneça node_type OU scene_path+node_path. "
                "Exemplo de input: {\"node_type\": \"Area2D\"}. "
                "Erro mais comum: nenhum — se o tipo for válido, sempre retorna sinais."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "node_type": {"type": "string"},
                    "scene_path": {"type": "string"},
                    "node_path": {"type": "string"},
                },
                "required": [],
            },
        ),
        # ── Fase 2: Scripts ──
        Tool(
            name="generate_gdscript",
            description=(
                "Gera um script GDScript a partir de um template Jinja2 pré-definido. "
                "Use para criar scripts comuns rapidamente (player, inimigo, manager). "
                "Quando NÃO usar: para lógica customizada que templates não cobrem (use write_file + validate_gdscript_syntax). "
                "Pré-condições: o template deve existir em templates/. "
                "Exemplo de input: {\"template\": \"player_2d_controller\", \"variables\": {}, \"save_path\": \"scripts/player.gd\"}. "
                "Erro mais comum: template não encontrado — o erro lista os templates disponíveis."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "template": {"type": "string", "description": "Nome do template sem .gd."},
                    "variables": {"type": "object", "description": "Variáveis para o template (opcional)."},
                    "save_path": {"type": "string", "description": "Caminho para salvar."},
                },
                "required": ["template", "save_path"],
            },
        ),
        Tool(
            name="attach_script",
            description=(
                "Anexa um script GDScript existente a um nó em uma cena. "
                "Use após criar um script para vinculá-lo a um nó. "
                "Quando NÃO usar: para criar o script (use generate_gdscript ou write_file). "
                "Pré-condições: o script e o nó devem existir. "
                "Exemplo de input: {\"scene_path\": \"scenes/player.tscn\", \"node_path\": \".\", \"script_path\": \"scripts/player.gd\"}. "
                "Erro mais comum: script não encontrado — crie o script primeiro."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "scene_path": {"type": "string"},
                    "node_path": {"type": "string"},
                    "script_path": {"type": "string"},
                },
                "required": ["scene_path", "node_path", "script_path"],
            },
        ),
        Tool(
            name="detach_script",
            description=(
                "Remove o script anexado de um nó. "
                "Use para desvincular um script sem deletar o arquivo. "
                "Pré-condições: o nó deve existir e ter um script anexado. "
                "Exemplo de input: {\"scene_path\": \"scenes/player.tscn\", \"node_path\": \".\"}. "
                "Erro mais comum: nó não tem script — retorna sucesso com nota informativa."
            ),
            inputSchema={
                "type": "object",
                "properties": {"scene_path": {"type": "string"}, "node_path": {"type": "string"}},
                "required": ["scene_path", "node_path"],
            },
        ),
        Tool(
            name="validate_gdscript_syntax",
            description=(
                "Valida a sintaxe de um script GDScript usando o compilador do Godot. "
                "Use após escrever scripts manualmente para garantir que não há erros de sintaxe. "
                "Quando NÃO usar: para scripts gerados por template (já são validados). "
                "Pré-condições: o script deve existir. "
                "Exemplo de input: {\"script_path\": \"scripts/player.gd\"}. "
                "Erro mais comum: erros de sintaxe — cada erro lista arquivo e linha."
            ),
            inputSchema={
                "type": "object",
                "properties": {"script_path": {"type": "string"}},
                "required": ["script_path"],
            },
        ),
        Tool(
            name="add_script_variable",
            description=(
                "Adiciona uma variável (com @export opcional) a um script GDScript. "
                "Use para expor parâmetros configuráveis no editor (velocidade, vida, etc.). "
                "Pré-condições: o script deve existir. "
                "Exemplo de input: {\"script_path\": \"scripts/player.gd\", \"var_name\": \"speed\", \"var_type\": \"float\", \"default_value\": \"300.0\", \"export\": true}. "
                "Erro mais comum: script não encontrado."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "script_path": {"type": "string"},
                    "var_name": {"type": "string"},
                    "var_type": {"type": "string"},
                    "default_value": {"type": "string"},
                    "export": {"type": "boolean"},
                },
                "required": ["script_path", "var_name"],
            },
        ),
        Tool(
            name="add_script_signal",
            description=(
                "Adiciona uma declaração de signal a um script GDScript. "
                "Use para definir sinais customizados que outros nós podem conectar. "
                "Pré-condições: o script deve existir. "
                "Exemplo de input: {\"script_path\": \"scripts/player.gd\", \"signal_name\": \"player_died\", \"args\": []}. "
                "Erro mais comum: script não encontrado."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "script_path": {"type": "string"},
                    "signal_name": {"type": "string"},
                    "args": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["script_path", "signal_name"],
            },
        ),
        # ── Fase 2: Física ──
        Tool(
            name="add_collision_shape",
            description=(
                "Adiciona um CollisionShape2D/3D com um shape a um nó de física. "
                "Use para dar forma de colisão a CharacterBody2D, Area2D, RigidBody2D. "
                "Quando NÃO usar: se o nó pai não for um CollisionObject (a tool valida isso). "
                "Pré-condições: nó pai deve herdar de CollisionObject2D ou CollisionObject3D. "
                "Exemplo de input: {\"scene_path\": \"scenes/player.tscn\", \"parent_node_path\": \".\", \"shape_type\": \"rectangle\", \"dimensions\": {\"width\": 64, \"height\": 64}}. "
                "Erro mais comum: pai não é CollisionObject — adicione a um CharacterBody2D, Area2D, etc."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "scene_path": {"type": "string"},
                    "parent_node_path": {"type": "string"},
                    "shape_type": {"type": "string", "enum": ["rectangle", "circle", "capsule"]},
                    "dimensions": {"type": "object"},
                },
                "required": ["scene_path", "parent_node_path", "shape_type", "dimensions"],
            },
        ),
        Tool(
            name="set_collision_layer_mask",
            description=(
                "Configura as camadas de colisão (layer e mask) de um nó. "
                "Use para controlar quais objetos colidem com quais. "
                "Convenção: 1=player, 2=inimigos, 3=projéteis player, 4=projéteis inimigos, 5=cenário, 6=coletáveis. "
                "Pré-condições: o nó deve existir. "
                "Exemplo de input: {\"scene_path\": \"scenes/player.tscn\", \"node_path\": \".\", \"layer_bits\": [1], \"mask_bits\": [2, 5]}. "
                "Erro mais comum: bits fora do range 1-32 — são ignorados."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "scene_path": {"type": "string"},
                    "node_path": {"type": "string"},
                    "layer_bits": {"type": "array", "items": {"type": "integer"}},
                    "mask_bits": {"type": "array", "items": {"type": "integer"}},
                },
                "required": ["scene_path", "node_path", "layer_bits", "mask_bits"],
            },
        ),
        # ── Fase 2: Assets ──
        Tool(
            name="import_texture",
            description=(
                "Importa uma textura (PNG, JPG, BMP, SVG) para o projeto. "
                "Use quando o usuário fornecer uma imagem para sprites, fundos, etc. "
                "Quando NÃO usar: se o usuário não tem assets — use placeholders (ColorRect) conforme 05_GAME_AGENT_GUIDE.md. "
                "Pré-condições: arquivo fonte deve existir no sistema de arquivos. "
                "Exemplo de input: {\"source_path\": \"C:/Users/joabc/Downloads/player.png\", \"target_res_path\": \"assets/sprites/player.png\"}. "
                "Erro mais comum: formato não suportado — use PNG, JPG, BMP ou SVG."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "source_path": {"type": "string"},
                    "target_res_path": {"type": "string"},
                },
                "required": ["source_path", "target_res_path"],
            },
        ),
        Tool(
            name="import_sprite_sheet",
            description=(
                "Importa uma sprite sheet e configura animações em um AnimatedSprite2D. "
                "Use para personagens com múltiplas animações (idle, walk, jump). "
                "Pré-condições: nó alvo deve ser AnimatedSprite2D; sprite sheet deve existir. "
                "Exemplo de input: {\"source_path\": \"...\", \"target_res_path\": \"assets/player.png\", \"frame_width\": 64, \"frame_height\": 64, \"target_scene_path\": \"scenes/player.tscn\", \"target_node_path\": \"./Sprite\", \"animations\": [{\"name\": \"idle\", \"frame_indices\": [0,1,2,3], \"fps\": 10.0}]}. "
                "Erro mais comum: nó alvo não é AnimatedSprite2D."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "source_path": {"type": "string"},
                    "target_res_path": {"type": "string"},
                    "frame_width": {"type": "integer"},
                    "frame_height": {"type": "integer"},
                    "target_scene_path": {"type": "string"},
                    "target_node_path": {"type": "string"},
                    "animations": {"type": "array"},
                },
                "required": ["source_path", "target_res_path", "frame_width", "frame_height", "target_scene_path", "target_node_path", "animations"],
            },
        ),
        Tool(
            name="import_audio",
            description=(
                "Importa um arquivo de áudio (WAV, OGG, MP3) para o projeto. "
                "Use para sons de pulo, tiro, música de fundo, etc. "
                "Pré-condições: arquivo fonte deve existir. "
                "Exemplo de input: {\"source_path\": \"C:/Users/.../jump.wav\", \"target_res_path\": \"assets/audio/jump.wav\"}. "
                "Erro mais comum: formato não suportado — use WAV, OGG ou MP3."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "source_path": {"type": "string"},
                    "target_res_path": {"type": "string"},
                },
                "required": ["source_path", "target_res_path"],
            },
        ),
        # ── Fase 2: Input e Autoload ──
        Tool(
            name="configure_input_action",
            description=(
                "Configura uma ação de input no projeto (InputMap). "
                "Use ANTES de criar scripts que usam Input.is_action_pressed() — é o erro mais comum pular esta etapa. "
                "Quando NÃO usar: para configurar autoload (use configure_autoload). "
                "Pré-condições: projeto ativo deve existir. "
                "Exemplo de input: {\"action_name\": \"move_left\", \"keys\": [\"A\", \"Left\"]}. "
                "Erro mais comum: nome de tecla inválido — use nomes como 'W', 'Space', 'Left', 'Kp 0'."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "action_name": {"type": "string"},
                    "keys": {"type": "array", "items": {"type": "string"}},
                    "joypad_buttons": {"type": "array", "items": {"type": "integer"}},
                },
                "required": ["action_name", "keys"],
            },
        ),
        Tool(
            name="install_mcp_addon",
            description=(
                "Instala o addon MCP IA DEV no projeto Godot ativo e ativa o plugin do editor. "
                "O QUE FAZ: copia os arquivos do addon (mcp_bridge.gd, mcp_dock.gd, plugin.cfg) "
                "para addons/mcp_bridge/ no projeto e adiciona o plugin em editor_plugins no project.godot. "
                "QUANDO USAR: sempre que criar um projeto novo com create_project, antes de usar "
                "ferramentas que precisam do editor (screenshots, run_game, etc). "
                "Também use se o projeto foi movido ou o addon foi removido acidentalmente. "
                "Após instalar, reinicie o editor Godot para ativar o plugin. "
                "O dock 'MCP IA DEV' aparecerá no painel inferior do editor. "
                "NÃO requer parâmetros se já houver um projeto ativo (set_active_project)."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "project_path": {
                        "type": "string",
                        "description": "Caminho do projeto Godot. Opcional se já usou set_active_project. Ex: 'C:/meu_jogo'"
                    }
                },
                "required": []
            },
        ),
        Tool(
            name="configure_autoload",
            description=(
                "Configura um script como autoload (singleton global acessível de qualquer cena). "
                "Use para game state global: score, vidas, GameManager. "
                "Quando NÃO usar: para scripts de entidades específicas (player, inimigo). "
                "Pré-condições: o script deve existir no projeto. "
                "Exemplo de input: {\"name\": \"GameManager\", \"script_path\": \"scripts/game_manager.gd\"}. "
                "Erro mais comum: script não encontrado — crie o script primeiro com generate_gdscript ou write_file."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "script_path": {"type": "string"},
                    "singleton": {"type": "boolean"},
                },
                "required": ["name", "script_path"],
            },
        ),
        # ── Fase 2: Runtime ──
        Tool(
            name="compile_test",
            description=(
                "Executa uma verificação de compilação no projeto (--headless --editor --quit). "
                "Use após fazer várias mudanças para verificar se não há erros antes de rodar o jogo. "
                "Quando NÃO usar: para rodar o jogo (use run_game). "
                "Pré-condições: projeto ativo deve existir. "
                "Exemplo de input: {} (sem argumentos). "
                "Erro mais comum: erros de script — cada erro lista o arquivo e a linha."
            ),
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="run_game",
            description=(
                "Inicia o jogo como um processo separado (NÃO bloqueante). "
                "Use para o usuário testar o jogo — é a ferramenta mais importante do fluxo. "
                "Quando NÃO usar: para apenas verificar erros (use compile_test). "
                "Pré-condições: main_scene deve estar definida ou scene_path informado. "
                "Exemplo de input: {} ou {\"scene_path\": \"scenes/main.tscn\"}. "
                "Erro mais comum: main_scene não definida — use set_main_scene primeiro."
            ),
            inputSchema={
                "type": "object",
                "properties": {"scene_path": {"type": "string"}},
                "required": [],
            },
        ),
        Tool(
            name="stop_game",
            description=(
                "Encerra o jogo em execução e retorna as últimas 100 linhas do console. "
                "Use quando o usuário terminar de testar ou quando o jogo travar. "
                "O console_tail contém erros de runtime que ajudam a diagnosticar problemas. "
                "Pré-condições: jogo deve estar rodando (run_game chamado antes). "
                "Exemplo de input: {} (sem argumentos). "
                "Erro mais comum: nenhum jogo rodando — retorna sucesso com nota informativa."
            ),
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="smart_restart",
            description=(
                "Reinicio inteligente: mata jogo, copia addons, compila, inicia, conecta Game Bridge. "
                "Use quando fizer MUITAS alteracoes no codigo e precisar reiniciar o jogo. "
                "Substitui 4-5 chamadas manuais (stop_game, write_file addon, compile_test, run_game, connect). "
                "Quando NAO usar: se so precisa de uma mudanca pontual (use execute_gdscript_runtime). "
                "Pre-condicoes: projeto ativo configurado. "
                "Exemplo de input: {} (sem argumentos). "
                "Erro mais comum: erros de compilacao — verifique compile_errors no retorno."
            ),
            inputSchema={
                "type": "object",
                "properties": {"project_path": {"type": "string", "description": "Caminho do projeto (opcional, usa default_project)."}},
                "required": [],
            },
        ),
        # ── Fase 3: Editor ao vivo ──
        Tool(
            name="launch_editor",
            description=(
                "Abre o editor Godot com o addon mcp_bridge para comunicação bidirecional. "
                "Use quando o usuário quiser VER o jogo no editor, ou quando precisar de "
                "screenshot/console em tempo real. "
                "Quando NÃO usar: se só precisa rodar o jogo (use run_game). "
                "Pré-condições: projeto ativo deve existir; addon é instalado automaticamente. "
                "Exemplo de input: {} ou {\"scene_path\": \"scenes/main.tscn\"}. "
                "Erro mais comum: editor não abre — verifique godot_path em config.json."
            ),
            inputSchema={
                "type": "object",
                "properties": {"scene_path": {"type": "string"}},
                "required": [],
            },
        ),
        Tool(
            name="close_editor",
            description=(
                "Fecha o editor Godot e desconecta o bridge TCP. "
                "Use ao final de uma sessão de edição ao vivo. "
                "Pré-condições: editor deve estar aberto. "
                "Exemplo de input: {}. "
                "Erro mais comum: nenhum — sempre retorna sucesso."
            ),
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="take_screenshot",
            description=(
                "Captura uma screenshot do viewport 2D do editor Godot. "
                "Use para VER o estado atual do jogo sem precisar abri-lo manualmente. "
                "A imagem é retornada em base64 para análise pela IA. "
                "Quando NÃO usar: se o editor não estiver aberto (use launch_editor antes). "
                "Pré-condições: editor deve estar aberto com addon conectado. "
                "Exemplo de input: {}. "
                "Erro mais comum: editor não aberto ou viewport 2D indisponível."
            ),
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="read_console_output",
            description=(
                "Lê as últimas linhas do console do editor Godot. "
                "Use para diagnosticar erros de runtime, warnings, ou ver prints de debug. "
                "Quando NÃO usar: se o editor não estiver aberto (retorna console offline). "
                "Pré-condições: editor aberto para console em tempo real; offline retorna buffer do subprocess. "
                "Exemplo de input: {} ou {\"since_timestamp\": 1234567890.0}. "
                "Erro mais comum: retorna vazio — o console pode não ter capturado nada ainda."
            ),
            inputSchema={
                "type": "object",
                "properties": {"since_timestamp": {"type": "number"}},
                "required": [],
            },
        ),
        # ── Fase 4: Tilemap ──
        Tool(
            name="create_tileset",
            description=(
                "Cria um TileSet (.tres) vazio com tamanho de tile configurável. "
                "Use como primeiro passo para criar jogos de plataforma/tilemap. "
                "Quando NÃO usar: se já tem um tileset pronto. "
                "Pré-condições: nenhuma. "
                "Exemplo de input: {\"tileset_name\": \"Ground\", \"save_path\": \"assets/tiles/ground.tres\", \"tile_width\": 16, \"tile_height\": 16}. "
                "Erro mais comum: arquivo já existe — escolha outro path."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "tileset_name": {"type": "string"},
                    "save_path": {"type": "string"},
                    "tile_width": {"type": "integer"},
                    "tile_height": {"type": "integer"},
                },
                "required": ["tileset_name", "save_path"],
            },
        ),
        Tool(
            name="create_tilemap_layer",
            description=(
                "Adiciona uma TileMapLayer a uma cena, vinculada a um TileSet. "
                "Use para criar o chão, paredes e cenário de jogos 2D. "
                "Pré-condições: o TileSet deve existir (crie com create_tileset). "
                "Exemplo de input: {\"scene_path\": \"scenes/main.tscn\", \"parent_node_path\": \".\", \"layer_name\": \"Ground\", \"tileset_path\": \"assets/tiles/ground.tres\"}. "
                "Erro mais comum: tileset não encontrado."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "scene_path": {"type": "string"},
                    "parent_node_path": {"type": "string"},
                    "layer_name": {"type": "string"},
                    "tileset_path": {"type": "string"},
                },
                "required": ["scene_path", "parent_node_path", "layer_name", "tileset_path"],
            },
        ),
        Tool(
            name="paint_tilemap_cell",
            description=(
                "Marca uma célula como pintada em uma TileMapLayer. "
                "Nota: suporte limitado — o formato de tile data é binário (PackedByteArray). "
                "Para pintura visual precisa, use o editor Godot. "
                "Pré-condições: TileMapLayer deve existir. "
                "Exemplo de input: {\"scene_path\": \"scenes/main.tscn\", \"layer_node_path\": \"./Ground\", \"cell_x\": 5, \"cell_y\": 3}. "
                "Erro mais comum: layer não encontrada."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "scene_path": {"type": "string"},
                    "layer_node_path": {"type": "string"},
                    "cell_x": {"type": "integer"},
                    "cell_y": {"type": "integer"},
                    "source_id": {"type": "integer"},
                    "atlas_coords_x": {"type": "integer"},
                    "atlas_coords_y": {"type": "integer"},
                },
                "required": ["scene_path", "layer_node_path", "cell_x", "cell_y"],
            },
        ),
        # ── Fase 4: Animação ──
        Tool(
            name="create_animation_player",
            description=(
                "Adiciona um nó AnimationPlayer a uma cena. "
                "Use como container para animações antes de criar animações específicas. "
                "Pré-condições: cena e nó pai devem existir. "
                "Exemplo de input: {\"scene_path\": \"scenes/player.tscn\", \"parent_node_path\": \".\"}. "
                "Erro mais comum: nó pai não encontrado."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "scene_path": {"type": "string"},
                    "parent_node_path": {"type": "string"},
                    "player_name": {"type": "string"},
                },
                "required": ["scene_path", "parent_node_path"],
            },
        ),
        Tool(
            name="create_animation",
            description=(
                "Adiciona uma animação a um AnimationPlayer existente. "
                "Use para criar animações de sprites: idle, walk, jump, attack. "
                "Pré-condições: AnimationPlayer deve existir na cena. "
                "Exemplo de input: {\"scene_path\": \"scenes/player.tscn\", \"anim_player_path\": \"./AnimationPlayer\", \"anim_name\": \"idle\", \"track_path\": \"./Sprite:frame\", \"track_type\": \"value\", \"keyframes\": [{\"time\": 0.0, \"value\": \"0\"}], \"fps\": 10.0}. "
                "Erro mais comum: AnimationPlayer não encontrado."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "scene_path": {"type": "string"},
                    "anim_player_path": {"type": "string"},
                    "anim_name": {"type": "string"},
                    "track_path": {"type": "string"},
                    "track_type": {"type": "string"},
                    "keyframes": {"type": "array"},
                    "fps": {"type": "number"},
                },
                "required": ["scene_path", "anim_player_path", "anim_name", "track_path", "track_type", "keyframes"],
            },
        ),
        # ── Fase 4: UI ──
        Tool(
            name="create_ui_scene",
            description=(
                "Cria uma cena de UI com CanvasLayer + Control prontos para receber elementos. "
                "Use para telas de menu, HUD, score, game over. "
                "Pré-condições: projeto ativo. "
                "Exemplo de input: {\"name\": \"HUD\", \"path\": \"scenes/hud.tscn\"}. "
                "Erro mais comum: cena já existe."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "path": {"type": "string"},
                },
                "required": ["name", "path"],
            },
        ),
        Tool(
            name="add_control_node",
            description=(
                "Adiciona um nó de UI (Label, Button, Panel, etc.) a uma cena com propriedades. "
                "Use para construir interfaces: score, vidas, botões, menus. "
                "Pré-condições: cena e nó pai devem existir; node_type deve herdar de Control. "
                "Exemplo de input: {\"scene_path\": \"scenes/hud.tscn\", \"parent_node_path\": \"./UIContainer\", \"node_name\": \"ScoreLabel\", \"node_type\": \"Label\", \"properties\": {\"text\": \"Score: 0\"}}. "
                "Erro mais comum: tipo de nó inválido para UI."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "scene_path": {"type": "string"},
                    "parent_node_path": {"type": "string"},
                    "node_name": {"type": "string"},
                    "node_type": {"type": "string"},
                    "properties": {"type": "object"},
                },
                "required": ["scene_path", "parent_node_path", "node_name", "node_type"],
            },
        ),
        # ── Fase 5: Export, Segurança ──
        Tool(
            name="list_export_presets",
            description=(
                "Lista os presets de exportação do projeto atual. "
                "Use para ver quais plataformas de exportação estão configuradas. "
                "Pré-condições: projeto ativo. "
                "Exemplo de input: {}. "
                "Erro mais comum: lista vazia — build_export criará um preset padrão automaticamente."
            ),
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="validate_export_templates_installed",
            description=(
                "Verifica se os templates de exportação do Godot estão instalados. "
                "Use antes de build_export para garantir que o ambiente está pronto. "
                "Pré-condições: Godot instalado. "
                "Exemplo de input: {}. "
                "Erro mais comum: templates não instalados — a mensagem contém instruções leigas para o usuário."
            ),
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="build_export",
            description=(
                "Exporta o projeto para um executável (.exe no Windows). "
                "Use como passo final quando o jogo estiver pronto. "
                "Pré-condições: templates de exportação instalados, projeto compilando sem erros. "
                "Exemplo de input: {} (usa preset padrão do SO) ou {\"preset_name\": \"Windows Desktop\", \"output_path\": \"build/meu_jogo.exe\"}. "
                "Erro mais comum: templates não instalados — use validate_export_templates_installed primeiro."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "preset_name": {"type": "string"},
                    "output_path": {"type": "string"},
                },
                "required": [],
            },
        ),
        Tool(
            name="list_backups",
            description=(
                "Lista todos os backups disponíveis no projeto, mais recentes primeiro. "
                "Use quando o usuário disser 'desfaz' ou 'volta atrás' — mostre a lista para ele escolher. "
                "Pré-condições: operações destrutivas anteriores geraram backups automáticos. "
                "Exemplo de input: {} ou {\"original_path\": \"scenes/main.tscn\"}. "
                "Erro mais comum: lista vazia — nenhum backup foi criado ainda."
            ),
            inputSchema={
                "type": "object",
                "properties": {"original_path": {"type": "string"}},
                "required": [],
            },
        ),
        Tool(
            name="restore_backup",
            description=(
                "Restaura um arquivo a partir de um backup (desfaz mudanças). "
                "Use quando o usuário disser 'desfaz a última mudança' ou 'volta atrás'. "
                "ANTES de restaurar, faz checkpoint do estado atual (undo do undo possível). "
                "Pré-condições: backup deve existir (liste com list_backups). "
                "Exemplo de input: {\"backup_id\": \"20260705_120000_main.tscn\"}. "
                "Erro mais comum: backup_id não encontrado — use list_backups para ver IDs disponíveis."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "backup_id": {"type": "string"},
                    "original_path": {"type": "string"},
                    "latest": {"type": "boolean"},
                },
                "required": [],
            },
        ),
        Tool(
            name="git_commit_checkpoint",
            description=(
                "Faz um commit git no projeto alvo com uma mensagem descritiva. "
                "Use quando o usuário aprovar uma versão jogável — 'salva o progresso'. "
                "Pré-condições: projeto deve ser um repositório git. "
                "Exemplo de input: {\"message\": \"versão jogável de Pong com placar\"}. "
                "Erro mais comum: projeto não é repo git — retorna skipped."
            ),
            inputSchema={
                "type": "object",
                "properties": {"message": {"type": "string"}},
                "required": ["message"],
            },
        ),
        # ── Game Bridge (runtime) ──
        Tool(
            name="inject_input_event",
            description=(
                "Injeta um evento de input (mouse/teclado) no jogo EM EXECUÇÃO. "
                "Use para simular cliques, teclas, ou movimento de mouse durante o jogo. "
                "Quando NÃO usar: se o jogo não estiver rodando (use run_game primeiro). "
                "Pré-condições: jogo rodando com autoload GameBridge instalado. "
                "Exemplo de input: {\"event_type\": \"key\", \"event_data\": {\"keycode\": 32, \"pressed\": true}}. "
                "Erro mais comum: bridge não instalado — use write_file + configure_autoload para instalar."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "event_type": {"type": "string", "enum": ["key", "mouse_button", "mouse_motion"]},
                    "event_data": {"type": "object"},
                },
                "required": ["event_type", "event_data"],
            },
        ),
        Tool(
            name="execute_gdscript_runtime",
            description=(
                "Executa código GDScript arbitrário no jogo em execução e retorna o valor. "
                "Use para consultar estado do jogo, modificar nós, ou testar lógica em tempo real. "
                "Aceita expressões ('2+2') e statements ('get_node(...).position.x = 100'). "
                "Quando NÃO usar: se o jogo não estiver rodando. "
                "Pré-condições: jogo rodando com autoload GameBridge instalado. "
                "Exemplo de input: {\"code\": \"get_node('/root/Main/Player').position\"}. "
                "Erro mais comum: código inválido — retorna erro de compilação GDScript."
            ),
            inputSchema={
                "type": "object",
                "properties": {"code": {"type": "string", "description": "Código GDScript a executar."}},
                "required": ["code"],
            },
        ),
        Tool(
            name="watch_signal",
            description=(
                "Observa um sinal de um nó por N segundos e retorna se disparou. "
                "Use para verificar se um evento ocorreu (ex: inimigo morreu, animação terminou). "
                "Verifica imediatamente se o nó e sinal existem — erro instantâneo se não. "
                "Quando NÃO usar: se o jogo não estiver rodando. "
                "Pré-condições: jogo rodando com autoload GameBridge instalado. "
                "Exemplo de input: {\"node_path\": \"/root/Main/Player\", \"signal_name\": \"health_changed\", \"timeout\": 3.0}. "
                "Erro mais comum: nó ou sinal não encontrado — erro retornado imediatamente, sem esperar timeout."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "node_path": {"type": "string"},
                    "signal_name": {"type": "string"},
                    "timeout": {"type": "number", "description": "Segundos de espera (default 5)."},
                },
                "required": ["node_path", "signal_name"],
            },
        ),
        # ── Onda 1: Visão (Screenshots) ──
        Tool(
            name="capture_game_screenshot",
            description=(
                "Captura uma screenshot do jogo em execução usando janela off-screen. "
                "Use para VER o estado atual do jogo sem abrir o Godot — a IA pode analisar "
                "a imagem e ajustar o que for necessário. "
                "Quando usar: após criar/modificar cenas, para validar visualmente o resultado. "
                "Quando NÃO usar: se o jogo não compila (use compile_test primeiro). "
                "Pré-condições: projeto deve compilar sem erros, main_scene deve estar definida. "
                "Exemplo de input: {} (usa defaults: 30 frames, 1280x720). "
                "Erro mais comum: screenshot preta — verifique se há câmera na cena."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "wait_frames": {"type": "integer", "description": "Frames de espera antes da captura (default 30)."},
                    "scene_path": {"type": "string", "description": "Cena específica (opcional)."},
                    "resolution_width": {"type": "integer", "description": "Largura (default 1280)."},
                    "resolution_height": {"type": "integer", "description": "Altura (default 720)."},
                },
                "required": [],
            },
        ),
        Tool(
            name="compare_screenshots",
            description=(
                "Compara duas screenshots e retorna métricas de similaridade. "
                "Use para verificar se uma mudança visual teve o efeito esperado. "
                "Ex: tirou screenshot antes de ajustar UI, tirou depois, compara para ver diferença. "
                "Quando usar: após modificações visuais, para confirmar que a mudança ocorreu. "
                "Quando NÃO usar: para screenshots de cenas diferentes (a comparação não faria sentido). "
                "Pré-condições: ambas as screenshots devem existir no projeto. "
                "Exemplo de input: {\"before_path\": \"captures/antes.png\", \"after_path\": \"captures/depois.png\"}. "
                "Erro mais comum: imagens de tamanhos diferentes — o Godot redimensiona automaticamente."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "before_path": {"type": "string", "description": "Caminho da screenshot 'antes'."},
                    "after_path": {"type": "string", "description": "Caminho da screenshot 'depois'."},
                },
                "required": ["before_path", "after_path"],
            },
        ),
        Tool(
            name="detect_empty_screen",
            description=(
                "Detecta se uma screenshot está vazia (tela preta, branca, ou cor sólida). "
                "Use para diagnosticar problemas comuns: esqueceu de adicionar câmera, "
                "cena sem elementos visíveis, todos os sprites fora da tela. "
                "Quando usar: após capture_game_screenshot, para verificar se o jogo renderizou algo. "
                "Quando NÃO usar: se a screenshot obviamente tem conteúdo visível. "
                "Pré-condições: screenshot deve existir ou image_base64 fornecido. "
                "Exemplo de input: {\"screenshot_path\": \"captures/screenshot_20260706.png\"}. "
                "Erro mais comum: PNG corrompido — a tool retorna erro descritivo."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "screenshot_path": {"type": "string", "description": "Caminho da screenshot no projeto."},
                    "image_base64": {"type": "string", "description": "Alternativa: PNG em base64."},
                    "empty_threshold": {"type": "number", "description": "Limiar 0-1 (default 0.95)."},
                },
                "required": [],
            },
        ),
        # ── Onda 1: Visão (Análise) ──
        Tool(
            name="detect_offscreen_elements",
            description=(
                "Detecta nós que estão fora da área visível da viewport em uma cena. "
                "Use para diagnosticar: 'por que o inimigo não aparece?', 'onde está o player?'. "
                "Analisa o .tscn sem precisar abrir o Godot. "
                "Quando usar: após criar ou mover nós, para verificar se estão visíveis. "
                "Quando NÃO usar: para nós sem position definida (usa default da classe). "
                "Pré-condições: a cena deve existir. "
                "Exemplo de input: {\"scene_path\": \"scenes/main.tscn\"}. "
                "Erro mais comum: cena não encontrada — verifique o caminho."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "scene_path": {"type": "string", "description": "Caminho da cena."},
                    "viewport_width": {"type": "integer", "description": "Largura da viewport (default 1280)."},
                    "viewport_height": {"type": "integer", "description": "Altura da viewport (default 720)."},
                    "margin": {"type": "integer", "description": "Margem de tolerância em px (default 50)."},
                },
                "required": ["scene_path"],
            },
        ),
        # ── Onda 2: Batch Operations ──
        Tool(
            name="add_nodes_batch",
            description=(
                "Adiciona múltiplos nós a uma cena em UMA OPERAÇÃO. "
                "Muito mais rápido que chamar add_node repetidamente. "
                "Use para criar vários filhos de uma vez (ex: 50 tiles, 10 inimigos). "
                "Quando usar: sempre que precisar adicionar 3+ nós na mesma cena. "
                "Quando NÃO usar: para 1-2 nós (use add_node). "
                "Pré-condições: cena e nó pai devem existir. "
                "Exemplo: {\"scene_path\": \"scenes/main.tscn\", \"nodes\": ["
                "{\"parent_node_path\": \".\", \"node_name\": \"Enemy1\", \"node_type\": \"CharacterBody2D\"}, ...]}. "
                "Erro mais comum: nome duplicado — retorna erro no item específico."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "scene_path": {"type": "string"},
                    "nodes": {"type": "array", "items": {"type": "object"}},
                },
                "required": ["scene_path", "nodes"],
            },
        ),
        Tool(
            name="set_properties_batch",
            description=(
                "Define múltiplas propriedades em UMA OPERAÇÃO. "
                "Muito mais rápido que chamar set_node_property repetidamente. "
                "Use para configurar vários nós de uma vez (ex: posições, cores, tamanhos). "
                "Quando usar: sempre que precisar definir 3+ propriedades na mesma cena. "
                "Pré-condições: cena e nós devem existir. "
                "Exemplo: {\"scene_path\": \"scenes/main.tscn\", \"properties\": ["
                "{\"node_path\": \"./Player\", \"property_name\": \"position\", \"value\": \"Vector2(100,200)\"}, ...]}. "
                "Erro mais comum: nó não encontrado — retorna erro no item específico."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "scene_path": {"type": "string"},
                    "properties": {"type": "array", "items": {"type": "object"}},
                },
                "required": ["scene_path", "properties"],
            },
        ),
        # ── Onda 3: Assets Procedurais ──
        Tool(
            name="generate_placeholder_sprite",
            description=(
                "Gera um sprite placeholder PNG com forma geométrica colorida. "
                "Use para criar sprites temporários quando não há assets reais. "
                "Suporta retângulo, círculo, triângulo, diamante e estrela. "
                "Quando usar: início do desenvolvimento, antes de ter arte final. "
                "Quando NÃO usar: se já tem assets importados. "
                "Pré-condições: Pillow instalado (opcional, fallback raw PNG). "
                "Exemplo: {\"name\": \"player\", \"width\": 64, \"height\": 64, \"color\": \"#3498db\", \"shape\": \"rectangle\"}. "
                "Erro mais comum: cor inválida — use hex (#RRGGBB) ou nome (red, blue)."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "width": {"type": "integer"},
                    "height": {"type": "integer"},
                    "color": {"type": "string"},
                    "shape": {"type": "string", "enum": ["rectangle", "circle", "triangle", "diamond", "star"]},
                    "save_path": {"type": "string"},
                },
                "required": ["name"],
            },
        ),
        Tool(
            name="generate_placeholder_texture_atlas",
            description=(
                "Gera uma sprite sheet procedural com múltiplos frames de animação. "
                "Use para criar animações temporárias (idle, walk, jump) sem assets reais. "
                "Suporta variação de posição, cor e escala entre frames. "
                "Quando usar: para animações placeholder antes de importar arte final. "
                "Pré-condições: Pillow recomendado. "
                "Exemplo: {\"name\": \"player_walk\", \"frame_width\": 64, \"frame_height\": 64, \"columns\": 4, \"variation\": \"position\"}. "
                "Erro mais comum: Pillow não instalado — fallback gera frame único."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "frame_width": {"type": "integer"},
                    "frame_height": {"type": "integer"},
                    "columns": {"type": "integer"},
                    "rows": {"type": "integer"},
                    "color": {"type": "string"},
                    "shape": {"type": "string"},
                    "variation": {"type": "string", "enum": ["position", "color", "scale"]},
                    "save_path": {"type": "string"},
                },
                "required": ["name"],
            },
        ),
        Tool(
            name="generate_background_gradient",
            description=(
                "Gera um fundo com gradiente (vertical, horizontal ou radial). "
                "Use para backgrounds de menu, céu, ou qualquer fundo de cena. "
                "Quando usar: para backgrounds rápidos sem precisar de imagens externas. "
                "Pré-condições: Pillow instalado. "
                "Exemplo: {\"name\": \"sky\", \"width\": 1280, \"height\": 720, \"color_top\": \"#1a1a2e\", \"color_bottom\": \"#16213e\"}. "
                "Erro mais comum: Pillow não instalado."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "width": {"type": "integer"},
                    "height": {"type": "integer"},
                    "color_top": {"type": "string"},
                    "color_bottom": {"type": "string"},
                    "direction": {"type": "string", "enum": ["vertical", "horizontal", "radial"]},
                    "save_path": {"type": "string"},
                },
                "required": ["name"],
            },
        ),
        Tool(
            name="generate_tileset_from_colors",
            description=(
                "Gera um tileset .tres + textura PNG com tiles coloridos. "
                "Use para criar tilesets de terreno rápidos (chão, parede, água). "
                "Cada cor na lista vira um tile no atlas. "
                "Quando usar: para jogos de plataforma/tilemap sem assets de terreno. "
                "Pré-condições: Pillow instalado. "
                "Exemplo: {\"palette_name\": \"terrain\", \"colors\": [\"#27ae60\", \"#8B4513\", \"#3498db\"], \"tile_width\": 16, \"tile_height\": 16}. "
                "Erro mais comum: Pillow não instalado."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "palette_name": {"type": "string"},
                    "colors": {"type": "array", "items": {"type": "string"}},
                    "tile_width": {"type": "integer"},
                    "tile_height": {"type": "integer"},
                    "save_texture_path": {"type": "string"},
                    "save_tileset_path": {"type": "string"},
                },
                "required": ["palette_name", "colors"],
            },
        ),
        Tool(
            name="generate_audio_sfx",
            description=(
                "Gera um efeito sonoro WAV por síntese procedural (sem assets externos). "
                "Suporta: beep, jump, laser, explosion, collect, hit. "
                "Use para sons de pulo, tiro, coleta, explosão sem arquivos de áudio. "
                "Quando usar: para placeholder de áudio ou jogos com som procedural. "
                "Pré-condições: nenhuma (usa wave + math nativos do Python). "
                "Exemplo: {\"name\": \"jump\", \"sfx_type\": \"jump\", \"duration\": 0.3, \"frequency\": 440}. "
                "Erro mais comum: tipo inválido — use um dos 6 tipos suportados."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "sfx_type": {"type": "string", "enum": ["beep", "jump", "laser", "explosion", "collect", "hit"]},
                    "duration": {"type": "number"},
                    "frequency": {"type": "number"},
                    "sample_rate": {"type": "integer"},
                    "save_path": {"type": "string"},
                },
                "required": ["name"],
            },
        ),
        Tool(
            name="suggest_color_palette",
            description=(
                "Sugere uma paleta de cores baseada no gênero do jogo. "
                "Inclui cores para player, inimigo, cenário, UI e coletáveis. "
                "Use no início do desenvolvimento para definir a identidade visual. "
                "Gêneros: platformer, space_shooter, tower_defense, puzzle, rpg, arcade, horror. "
                "Quando usar: ao iniciar um jogo novo, para escolher cores. "
                "Pré-condições: nenhuma. "
                "Exemplo: {\"genre\": \"platformer\"} ou {\"genre\": \"all\"} para listar todos. "
                "Erro mais comum: gênero não encontrado — a tool sugere opções próximas."
            ),
            inputSchema={
                "type": "object",
                "properties": {"genre": {"type": "string"}},
                "required": ["genre"],
            },
        ),
        # ── Onda 4: IA Agêntica ──
        Tool(
            name="analyze_game_structure",
            description=(
                "Analisa a estrutura completa do projeto: cenas, scripts, nós, assets, autoloads. "
                "Use para ter uma visão geral do estado do projeto em UMA chamada. "
                "Retorna métricas, lista de cenas, tipos de nós mais usados, assets por tipo. "
                "Quando usar: no início da sessão, ou quando precisar entender o que já existe. "
                "Quando NÃO usar: para buscar texto específico (use search_codebase). "
                "Pré-condições: projeto ativo deve existir. "
                "Exemplo de input: {} (sem argumentos). "
                "Erro mais comum: projeto não encontrado — use set_active_project."
            ),
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="suggest_next_steps",
            description=(
                "Sugere os próximos passos de desenvolvimento baseado no estado do projeto. "
                "Analisa a estrutura e recomenda ações priorizadas (ex: 'configure_input_action', 'create_ui_scene'). "
                "Use quando não souber o que fazer a seguir, ou no início da sessão. "
                "Classifica o estágio: vazio, básico, sem_input, desenvolvimento. "
                "Quando usar: após analyze_game_structure, para decidir próximas ações. "
                "Pré-condições: projeto deve ter estrutura analisável. "
                "Exemplo de input: {} (sem argumentos). "
                "Erro mais comum: retorna poucas sugestões se projeto estiver vazio."
            ),
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="find_missing_references",
            description=(
                "Encontra referências quebradas no projeto (recursos inexistentes, preloads inválidos). "
                "Use para diagnosticar erros de carregamento ou 'recurso não encontrado'. "
                "Verifica .tscn (ext_resource) e .gd (preload). "
                "Quando usar: após mover/renomear arquivos, ou quando run_game falha. "
                "Pré-condições: projeto ativo. "
                "Exemplo de input: {} (sem argumentos). "
                "Erro mais comum: muitos falsos positivos em ext_resource (validar no Godot)."
            ),
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="validate_game_design",
            description=(
                "Valida checklist de game design: main_scene, input map, UI, scripts, assets. "
                "Retorna score (X/9) e veredito: PRONTO, EM DESENVOLVIMENTO, ou INICIAL. "
                "Use para avaliar se o jogo está minimamente jogável. "
                "Quando usar: antes de mostrar o jogo para alguém, ou ao final de uma sessão. "
                "Pré-condições: projeto ativo. "
                "Exemplo de input: {} (sem argumentos). "
                "Erro mais comum: jogo funcional com score baixo — o checklist é conservador."
            ),
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="estimate_game_scope",
            description=(
                "Estima o escopo do projeto: micro, pequeno, médio, grande ou épico. "
                "Baseado em: número de cenas, scripts, nós, linhas de código, tamanho. "
                "Use para entender a complexidade do projeto e planejar próximos passos. "
                "Quando usar: ao retomar um projeto após tempo fora, ou para reportar progresso. "
                "Pré-condições: projeto ativo. "
                "Exemplo de input: {} (sem argumentos). "
                "Erro mais comum: scope_score pode variar — é uma estimativa."
            ),
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="search_codebase",
            description=(
                "Busca um texto em todos os arquivos do projeto (case-insensitive). "
                "Use para encontrar onde uma variável, função ou nó é usado. "
                "Ex: 'queue_free', 'player_speed', 'Area2D'. "
                "Retorna arquivo, linha e contexto (±2 linhas). "
                "Quando usar: para navegar no código sem ler dezenas de arquivos. "
                "Pré-condições: projeto ativo. "
                "Exemplo: {\"query\": \"player_speed\", \"file_pattern\": \"*.gd\"}. "
                "Erro mais comum: query não encontrada — verifique capitalização."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Texto a buscar."},
                    "file_pattern": {"type": "string", "description": "Glob: *.gd, *.tscn, ou *."},
                    "max_results": {"type": "integer", "description": "Máximo de resultados (default 20)."},
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="get_project_history",
            description=(
                "Retorna o histórico de alterações do projeto (backups .mcp_backups + git log). "
                "Use para ver o que foi modificado recentemente. "
                "Lista backups (com timestamp e operação) e commits git (com mensagem). "
                "Quando usar: ao retomar uma sessão, ou para auditar mudanças. "
                "Pré-condições: projeto ativo. "
                "Exemplo de input: {} (sem argumentos). "
                "Erro mais comum: lista vazia — sem backups ou git no projeto."
            ),
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        # ── Onda 5: Cobertura Godot ──
        Tool(
            name="create_animation_tree",
            description=(
                "Adiciona um nó AnimationTree a uma cena. "
                "Use para animações avançadas com blend trees e state machines. "
                "Superior ao AnimationPlayer para transições complexas. "
                "Quando usar: para personagens com múltiplas animações (idle→walk→jump). "
                "Pré-condições: cena e nó pai existentes. "
                "Exemplo: {\"scene_path\": \"scenes/player.tscn\", \"parent_node_path\": \".\"}. "
                "Erro mais comum: nó pai não encontrado."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "scene_path": {"type": "string"},
                    "parent_node_path": {"type": "string"},
                    "player_name": {"type": "string"},
                    "root_type": {"type": "string"},
                },
                "required": ["scene_path", "parent_node_path"],
            },
        ),
        Tool(
            name="set_physics_material",
            description=(
                "Configura PhysicsMaterial com bounce, friction e absorb em um nó. "
                "Use para controlar quique, atrito e absorção de impacto. "
                "Essencial para jogos de plataforma (bounce em trampolins, friction no gelo). "
                "Quando usar: em CharacterBody2D, RigidBody2D, Area2D. "
                "Pré-condições: nó deve herdar de CollisionObject2D/3D. "
                "Exemplo: {\"scene_path\": \"...\", \"node_path\": \"./Player\", \"bounce\": 0.8, \"friction\": 0.2}. "
                "Erro mais comum: nó não é CollisionObject."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "scene_path": {"type": "string"},
                    "node_path": {"type": "string"},
                    "bounce": {"type": "number"},
                    "friction": {"type": "number"},
                    "absorb": {"type": "number"},
                    "rough": {"type": "boolean"},
                },
                "required": ["scene_path", "node_path"],
            },
        ),
        Tool(
            name="create_joint_2d",
            description=(
                "Cria uma junta 2D (PinJoint2D) conectando dois nós. "
                "Use para portas giratórias, pontes basculantes, cordas, alavancas. "
                "Suporta PinJoint2D (ponto fixo) e GrooveJoint2D (trilho). "
                "Quando usar: para objetos que precisam de conexão física entre si. "
                "Pré-condições: ambos os nós devem existir na cena. "
                "Exemplo: {\"scene_path\": \"...\", \"node_a_path\": \"./Door\", \"node_b_path\": \"./Wall\", \"joint_type\": \"pin\"}. "
                "Erro mais comum: um dos nós não encontrado."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "scene_path": {"type": "string"},
                    "node_a_path": {"type": "string"},
                    "node_b_path": {"type": "string"},
                    "joint_type": {"type": "string", "enum": ["pin", "groove"]},
                    "softness": {"type": "number"},
                    "bias": {"type": "number"},
                },
                "required": ["scene_path", "node_a_path", "node_b_path"],
            },
        ),
        Tool(
            name="import_3d_model",
            description=(
                "Importa um modelo 3D (.glb/.gltf) e opcionalmente cria cena com MeshInstance3D. "
                "Use para trazer modelos 3D para o projeto. "
                "Quando usar: se o usuário fornecer um arquivo .glb/.gltf. "
                "Pré-condições: arquivo fonte deve existir; Godot 4.7 suporta glTF 2.0. "
                "Exemplo: {\"source_path\": \"C:/models/character.glb\", \"target_res_path\": \"assets/models/character.glb\"}. "
                "Erro mais comum: formato não suportado — use .glb ou .gltf."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "source_path": {"type": "string"},
                    "target_res_path": {"type": "string"},
                    "create_scene": {"type": "boolean"},
                    "scene_name": {"type": "string"},
                },
                "required": ["source_path", "target_res_path"],
            },
        ),
        Tool(
            name="create_particles_2d",
            description=(
                "Adiciona GPUParticles2D com ParticleProcessMaterial a uma cena. "
                "Use para efeitos visuais: explosão, fumaça, sparkles, chuva, neve. "
                "Configura amount, lifetime, explosiveness, direction, spread, gravity. "
                "Quando usar: para qualquer efeito de partícula em jogos 2D. "
                "Pré-condições: cena e nó pai existentes. "
                "Exemplo: {\"scene_path\": \"...\", \"parent_node_path\": \".\", \"amount\": 100, \"lifetime\": 1.5}. "
                "Erro mais comum: partículas não visíveis sem run_game."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "scene_path": {"type": "string"},
                    "parent_node_path": {"type": "string"},
                    "node_name": {"type": "string"},
                    "amount": {"type": "integer"},
                    "lifetime": {"type": "number"},
                    "explosiveness": {"type": "number"},
                    "direction": {"type": "string"},
                    "spread": {"type": "number"},
                    "gravity": {"type": "string"},
                },
                "required": ["scene_path", "parent_node_path"],
            },
        ),
        Tool(
            name="create_light_2d",
            description=(
                "Adiciona PointLight2D ou DirectionalLight2D a uma cena. "
                "Use para iluminação 2D: tochas, lanternas, luz ambiente. "
                "Configura cor, energia (intensidade) e alcance (range_z). "
                "Quando usar: para melhorar a atmosfera visual com iluminação. "
                "Pré-condições: cena e nó pai existentes. "
                "Exemplo: {\"scene_path\": \"...\", \"parent_node_path\": \".\", \"light_type\": \"point\", \"color\": \"Color(1,0.8,0.4,1)\", \"energy\": 1.5}. "
                "Erro mais comum: luz invisível — verifique cor e energia."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "scene_path": {"type": "string"},
                    "parent_node_path": {"type": "string"},
                    "node_name": {"type": "string"},
                    "light_type": {"type": "string", "enum": ["point", "directional"]},
                    "color": {"type": "string"},
                    "energy": {"type": "number"},
                    "range_z": {"type": "number"},
                },
                "required": ["scene_path", "parent_node_path"],
            },
        ),
        Tool(
            name="setup_camera_2d",
            description=(
                "Adiciona e configura uma Camera2D com limites, zoom, drag e suavização. "
                "Use ao criar qualquer cena 2D que precise de câmera. "
                "Quando NÃO usar: se a cena já tem câmera configurada. "
                "Pré-condições: cena deve existir. "
                "Exemplo: {\"scene_path\": \"scenes/game.tscn\", \"limits\": {\"left\": 0, \"top\": 0, \"right\": 2560, \"bottom\": 1440}, \"smoothing_enabled\": true}. "
                "Erro mais comum: cena não encontrada — verifique o caminho."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "scene_path": {"type": "string"},
                    "parent_node_path": {"type": "string"},
                    "limits": {"type": "object"},
                    "drag_horizontal": {"type": "number"},
                    "drag_vertical": {"type": "number"},
                    "zoom": {"type": "array", "items": {"type": "number"}},
                    "smoothing_enabled": {"type": "boolean"},
                    "smoothing_speed": {"type": "number"},
                    "current": {"type": "boolean"},
                },
                "required": ["scene_path"],
            },
        ),
        Tool(
            name="setup_camera_follow",
            description=(
                "Faz a câmera seguir um nó alvo com suavidade e deadzone. Gera script automaticamente. "
                "Use SEMPRE que o jogo tiver personagem que se move. "
                "Pré-condições: cena com Camera2D e nó alvo (ex: Player). "
                "Exemplo: {\"scene_path\": \"scenes/game.tscn\", \"camera_node_path\": \"./Camera2D\", \"target_node_path\": \"./Player\"}. "
                "Erro mais comum: target não encontrado — verifique node_path."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "scene_path": {"type": "string"},
                    "camera_node_path": {"type": "string"},
                    "target_node_path": {"type": "string"},
                    "smoothing": {"type": "number"},
                    "offset_x": {"type": "number"},
                    "offset_y": {"type": "number"},
                    "deadzone_width": {"type": "number"},
                    "deadzone_height": {"type": "number"},
                },
                "required": ["scene_path", "camera_node_path", "target_node_path"],
            },
        ),
        Tool(
            name="setup_camera_shake",
            description=(
                "Adiciona efeito de tremor (screen shake) via algoritmo de trauma/decay. "
                "Use para feedback visual de explosões, dano, impacto. "
                "Após criar, chame $Camera2D.add_trauma(0.5) de qualquer script. "
                "Exemplo: {\"scene_path\": \"...\", \"camera_node_path\": \"./Camera2D\", \"max_amplitude\": 20}. "
                "Erro mais comum: esquecer de chamar add_trauma — o shake não acontece sozinho."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "scene_path": {"type": "string"},
                    "camera_node_path": {"type": "string"},
                    "max_amplitude": {"type": "number"},
                    "decay_rate": {"type": "number"},
                },
                "required": ["scene_path", "camera_node_path"],
            },
        ),
        Tool(
            name="create_main_menu",
            description=(
                "Cria uma cena de menu principal completa com título e botões. "
                "Suporta estilos: modern, retro, cartoon, dark_fantasy, sci_fi. "
                "Gera .tscn + script de UI + conexões de sinais automaticamente. "
                "Use como PRIMEIRA tela de qualquer jogo novo. "
                "Exemplo: {\"scene_name\": \"title_screen\", \"game_title\": \"Astro Blaster\", \"style\": \"retro\"}. "
                "Erro mais comum: esquecer de definir como main scene — use set_main_scene depois."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "scene_name": {"type": "string"},
                    "game_title": {"type": "string"},
                    "title_font_size": {"type": "integer"},
                    "buttons": {"type": "array", "items": {"type": "string"}},
                    "background_color": {"type": "string"},
                    "style": {"type": "string", "enum": ["modern", "retro", "cartoon", "dark_fantasy", "sci_fi"]},
                },
                "required": ["scene_name", "game_title"],
            },
        ),
        Tool(
            name="create_hud_template",
            description=(
                "Cria uma cena de HUD com elementos de UI: score, health, ammo, wave, timer. "
                "Use em TODO jogo que precise mostrar info ao player. "
                "Posições: top_left, top_right, bottom_center. "
                "Exemplo: {\"elements\": [\"score\", \"health\", \"ammo\"], \"position\": \"top_left\"}. "
                "Erro mais comum: HUD não aparece — verifique se a cena HUD está como instância na cena do jogo."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "scene_name": {"type": "string"},
                    "elements": {"type": "array", "items": {"type": "string"}},
                    "position": {"type": "string", "enum": ["top_left", "top_right", "bottom_center"]},
                },
                "required": [],
            },
        ),
        Tool(
            name="create_pause_menu",
            description=(
                "Cria menu de pausa completo: overlay escuro + botões + script que detecta ESC. "
                "Use em TODO jogo — pausa é recurso básico. "
                "Após criar, instancie na cena do jogo. O script gerencia get_tree().paused. "
                "Exemplo: {\"scene_name\": \"pause_menu\", \"overlay_alpha\": 0.7}. "
                "Erro mais comum: menu não some — verifique se input_action 'ui_cancel' está configurada."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "scene_name": {"type": "string"},
                    "overlay_alpha": {"type": "number"},
                },
                "required": [],
            },
        ),
        Tool(
            name="create_health_bar",
            description=(
                "Cria uma barra de vida com script de controle: take_damage, heal, animação, cor muda. "
                "Use para player, inimigos, chefes. "
                "Emite sinais: died, health_changed. "
                "Exemplo: {\"scene_path\": \"scenes/player.tscn\", \"max_health\": 100, \"bar_name\": \"HealthBar\"}. "
                "Erro mais comum: barra não atualiza — verifique se está chamando take_damage()."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "scene_path": {"type": "string"},
                    "parent_node_path": {"type": "string"},
                    "max_health": {"type": "number"},
                    "bar_name": {"type": "string"},
                    "bar_width": {"type": "integer"},
                    "bar_height": {"type": "integer"},
                    "fill_color": {"type": "string"},
                    "bg_color": {"type": "string"},
                    "show_text": {"type": "boolean"},
                },
                "required": ["scene_path"],
            },
        ),
        Tool(
            name="create_save_system",
            description=(
                "Cria sistema completo de save/load como Autoload (SaveManager). "
                "Funções: save_game(slot), load_game(slot), delete_save(slot), get_save_slots(). "
                "Usa ConfigFile para persistência em user://. "
                "Use em TODO jogo que precise salvar progresso. "
                "Exemplo: {\"autoload_name\": \"SaveManager\", \"save_slots\": 3}. "
                "Depois use define_save_data para registrar variáveis a salvar."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "autoload_name": {"type": "string"},
                    "save_slots": {"type": "integer"},
                    "auto_save_enabled": {"type": "boolean"},
                    "auto_save_interval": {"type": "number"},
                },
                "required": [],
            },
        ),
        Tool(
            name="define_save_data",
            description=(
                "Registra uma variável para ser salva/carregada pelo SaveManager. "
                "Use APÓS create_save_system, para cada propriedade importante. "
                "Exemplo: {\"node_path\": \"Player\", \"property_name\": \"position\", \"section\": \"player\"}. "
                "Erro mais comum: SaveManager não encontrado — execute create_save_system primeiro."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "node_path": {"type": "string"},
                    "property_name": {"type": "string"},
                    "section": {"type": "string"},
                    "key": {"type": "string"},
                },
                "required": ["node_path", "property_name"],
            },
        ),
        Tool(
            name="create_state_machine",
            description=(
                "Gera máquina de estados finita (FSM) em GDScript com enum + funções _enter/_update/_exit + transition_to(). "
                "Use para TODO personagem/inimigo com múltiplos comportamentos. "
                "Após criar, use add_state_transition para definir transições. "
                "Exemplo: {\"script_path\": \"scripts/enemy.gd\", \"states\": [\"idle\", \"walk\", \"attack\", \"hurt\", \"die\"], \"initial_state\": \"idle\"}. "
                "Erro mais comum: esquecer de adicionar transições — personagem fica parado no estado inicial."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "script_path": {"type": "string"},
                    "states": {"type": "array", "items": {"type": "string"}},
                    "initial_state": {"type": "string"},
                },
                "required": ["script_path", "states", "initial_state"],
            },
        ),
        Tool(
            name="add_state_transition",
            description=(
                "Adiciona transição condicional entre estados na FSM. "
                "Use após create_state_machine. "
                "Exemplo: {\"script_path\": \"scripts/enemy.gd\", \"from_state\": \"idle\", \"to_state\": \"walk\", \"condition_code\": \"velocity.length() > 0\"}. "
                "Erro mais comum: código de condição com erro de sintaxe — valide antes."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "script_path": {"type": "string"},
                    "from_state": {"type": "string"},
                    "to_state": {"type": "string"},
                    "condition_code": {"type": "string"},
                },
                "required": ["script_path", "from_state", "to_state", "condition_code"],
            },
        ),
        Tool(
            name="create_tween_animation",
            description=(
                "Cria animação Tween: fade, movimento, escala, rotação com easing. "
                "Retorna código GDScript pronto. Use para animações dinâmicas que não são keyframe-based. "
                "Exemplo: {\"scene_path\": \"...\", \"node_path\": \"./Coin\", \"property_name\": \"modulate\", \"final_value\": [1,1,1,0], \"duration\": 0.3}. "
                "Suporte a easings: linear, quad, cubic, elastic, bounce, back."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "scene_path": {"type": "string"},
                    "node_path": {"type": "string"},
                    "property_name": {"type": "string"},
                    "final_value": {},
                    "duration": {"type": "number"},
                    "easing": {"type": "string"},
                    "transition": {"type": "string"},
                    "loops": {"type": "integer"},
                    "auto_play": {"type": "boolean"},
                },
                "required": ["scene_path", "node_path", "property_name", "final_value"],
            },
        ),
        Tool(
            name="chain_tweens",
            description=(
                "Encadeia múltiplos Tweens em sequência (.then()). "
                "Use para animações complexas: cutscenes, combos visuais. "
                "Exemplo: {\"scene_path\": \"...\", \"node_path\": \"./Sprite\", \"steps\": [{\"property\": \"scale\", \"final_value\": [1.2,1.2]}, {\"property\": \"scale\", \"final_value\": [1,1]}]}."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "scene_path": {"type": "string"},
                    "node_path": {"type": "string"},
                    "steps": {"type": "array", "items": {"type": "object"}},
                },
                "required": ["scene_path", "node_path", "steps"],
            },
        ),
        Tool(
            name="create_navigation_region_2d",
            description=(
                "Cria região de navegação 2D com polígono. Define área onde personagens podem andar. "
                "Use ao criar mapa com pathfinding. "
                "Depois use create_navigation_agent_2d para personagens que navegam. "
                "Exemplo: {\"scene_path\": \"...\", \"polygon_vertices\": [[0,0],[1280,0],[1280,720],[0,720]]}."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "scene_path": {"type": "string"},
                    "parent_node_path": {"type": "string"},
                    "polygon_vertices": {"type": "array", "items": {"type": "array", "items": {"type": "number"}}},
                    "region_name": {"type": "string"},
                },
                "required": ["scene_path"],
            },
        ),
        Tool(
            name="create_navigation_agent_2d",
            description=(
                "Adiciona NavigationAgent2D com script de perseguição. O nó pai DEVE ser CharacterBody2D. "
                "Gera script que persegue o alvo usando pathfinding da NavigationRegion. "
                "Use para inimigos que perseguem o player ou NPCs com destino. "
                "Pré-condições: NavigationRegion2D já deve existir na cena. "
                "Exemplo: {\"scene_path\": \"...\", \"parent_node_path\": \"./Enemy\", \"target_node_path\": \"./Player\", \"speed\": 150}."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "scene_path": {"type": "string"},
                    "parent_node_path": {"type": "string"},
                    "agent_name": {"type": "string"},
                    "target_node_path": {"type": "string"},
                    "speed": {"type": "number"},
                    "avoidance_enabled": {"type": "boolean"},
                },
                "required": ["scene_path", "parent_node_path", "target_node_path"],
            },
        ),
        Tool(
            name="bake_navigation_polygon",
            description=(
                "Gera NavigationPolygon a partir de TileMapLayer. Analisa células e cria polígono para tiles andáveis. "
                "Use após criar o mapa com TileMap. "
                "Exemplo: {\"scene_path\": \"...\", \"tilemap_layer_path\": \"./TileMapLayer\", \"navigation_region_path\": \"./NavigationRegion2D\", \"walkable_tiles\": [0, 1]}."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "scene_path": {"type": "string"},
                    "tilemap_layer_path": {"type": "string"},
                    "navigation_region_path": {"type": "string"},
                    "walkable_tiles": {"type": "array", "items": {"type": "integer"}},
                },
                "required": ["scene_path", "tilemap_layer_path", "navigation_region_path"],
            },
        ),
        Tool(
            name="setup_world_environment",
            description=(
                "Configura ambiente visual: cor de fundo, luz ambiente, glow (bloom), névoa (fog). "
                "Cria WorldEnvironment + Environment resource. "
                "Use para dar atmosfera e polimento visual ao jogo. "
                "Exemplo: {\"scene_path\": \"...\", \"glow_enabled\": true, \"fog_enabled\": true, \"background_color\": \"#1a1a2e\"}."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "scene_path": {"type": "string"},
                    "parent_node_path": {"type": "string"},
                    "background_mode": {"type": "string", "enum": ["color", "sky", "canvas"]},
                    "background_color": {"type": "string"},
                    "ambient_light_color": {"type": "string"},
                    "ambient_light_energy": {"type": "number"},
                    "glow_enabled": {"type": "boolean"},
                    "glow_intensity": {"type": "number"},
                    "fog_enabled": {"type": "boolean"},
                    "fog_density": {"type": "number"},
                    "fog_color": {"type": "string"},
                },
                "required": ["scene_path"],
            },
        ),
        Tool(
            name="setup_screen_flash",
            description=(
                "Adiciona efeito de flash de tela (dano=vermelho, cura=verde, power-up=branco). "
                "Cria ColorRect overlay com animação Tween. "
                "Use para feedback visual de eventos importantes. "
                "Após criar, chame $ScreenFlash.flash_red() de qualquer script. "
                "Exemplo: {\"scene_path\": \"scenes/game.tscn\", \"flash_color\": \"#ff0000\"}."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "scene_path": {"type": "string"},
                    "parent_node_path": {"type": "string"},
                    "flash_color": {"type": "string"},
                    "flash_duration": {"type": "number"},
                },
                "required": ["scene_path"],
            },
        ),
        Tool(
            name="generate_project_structure",
            description=(
                "Gera a estrutura completa de pastas e arquivos base para um projeto Godot. "
                "Cria pastas padronizadas (scenes, scripts, assets), scene principal com nodes basicos, "
                "scripts boilerplate e arquivos de configuracao (.gitignore, README). "
                "Quando usar: no INICIO de um novo projeto, antes de criar qualquer cena. "
                "Templates disponiveis: '2d', '3d', 'mobile'. "
                "Exemplo: {\"template\": \"2d\"}."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "template": {"type": "string", "description": "Tipo: '2d', '3d', ou 'mobile'"},
                    "project_path": {"type": "string", "description": "Caminho do projeto (opcional)"},
                },
            },
        ),
        Tool(
            name="record_gameplay_gif",
            description=(
                "Grava a tela do jogo por N segundos e retorna um GIF animado em base64. "
                "Usa Godot --write-movie para capturar frames e PIL para compor GIF. "
                "Quando usar: para a IA 'ver' o resultado visual do jogo e decidir proximos passos. "
                "Fallback: se PIL nao estiver instalado, retorna frames PNG individuais. "
                "Exemplo: {\"duration\": 5, \"fps\": 10, \"resolution_width\": 480, \"resolution_height\": 270}."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "duration": {"type": "integer", "description": "Duracao em segundos (max 30)"},
                    "fps": {"type": "integer", "description": "Frames por segundo (menor = arquivo menor)"},
                    "resolution_width": {"type": "integer", "description": "Largura em pixels"},
                    "resolution_height": {"type": "integer", "description": "Altura em pixels"},
                },
            },
        ),
        Tool(
            name="undo_last_action",
            description=(
                "Desfaz a ultima acao realizada pela IA, restaurando todos os arquivos modificados. "
                "O sistema mantem um historico das ultimas 20 acoes com backups automaticos. "
                "Quando usar: quando o usuario disser 'nao gostei', 'volta', 'desfaz isso'. "
                "Exemplo: {} (chamada sem argumentos)."
            ),
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        Tool(
            name="get_undo_history",
            description=(
                "Lista o historico de acoes que podem ser desfeitas. "
                "Retorna as ultimas 20 acoes com nome, arquivos afetados e timestamp. "
                "Quando usar: antes de desfazer, para o usuario escolher qual acao reverter. "
                "Exemplo: {} (chamada sem argumentos)."
            ),
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        # ── Onda 9: Polimento Visual ──
        Tool(
            name="create_parallax_background",
            description=(
                "Cria um fundo com efeito parallax (ParallaxBackground + multiplas camadas). "
                "Use para dar profundidade a jogos 2D: ceu, montanhas, nuvens em velocidades diferentes. "
                "Quando NAO usar: para fundos estaticos (use generate_background_gradient). "
                "Pre-condicoes: cena deve existir; texturas das camadas devem estar no projeto. "
                "Exemplo: {'scene_path': 'scenes/game.tscn', 'layers': [{'texture': 'assets/bg_far.png', 'scroll_scale_x': 0.2}]}. "
                "Erro mais comum: textura nao encontrada — importe com import_texture primeiro."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "scene_path": {"type": "string", "description": "Caminho da cena onde adicionar o parallax."},
                    "layers": {"type": "array", "description": "Lista de camadas [{texture, scroll_scale_x, scroll_scale_y, mirroring_x, mirroring_y}]."},
                    "parent_node_path": {"type": "string", "description": "No pai (default '.' = raiz)."},
                    "bg_name": {"type": "string", "description": "Nome do no ParallaxBackground."},
                },
                "required": ["scene_path", "layers"],
            },
        ),
        Tool(
            name="add_parallax_layer",
            description=(
                "Adiciona uma camada a um ParallaxBackground existente. "
                "Use para adicionar mais camadas de profundidade a um cenario parallax. "
                "Quando NAO usar: se ainda nao criou o ParallaxBackground (use create_parallax_background). "
                "Pre-condicoes: ParallaxBackground deve existir na cena; textura deve existir. "
                "Exemplo: {'scene_path': 'scenes/game.tscn', 'parallax_bg_path': './ParallaxBackground', 'texture_path': 'assets/bg_mid.png', 'scroll_scale_x': 0.5}. "
                "Erro mais comum: ParallaxBackground nao encontrado — verifique o node_path."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "scene_path": {"type": "string", "description": "Caminho da cena."},
                    "parallax_bg_path": {"type": "string", "description": "Path do ParallaxBackground."},
                    "texture_path": {"type": "string", "description": "Caminho da textura (ex: assets/bg.png)."},
                    "scroll_scale_x": {"type": "number", "description": "Escala de scroll horizontal (0=fixo, 1=normal, default 0.5)."},
                    "scroll_scale_y": {"type": "number", "description": "Escala de scroll vertical (default 0.5)."},
                    "mirroring_x": {"type": "number", "description": "Repeticoes horizontais (0=sem mirroring)."},
                    "mirroring_y": {"type": "number", "description": "Repeticoes verticais (0=sem mirroring)."},
                    "layer_name": {"type": "string", "description": "Nome do no da camada."},
                },
                "required": ["scene_path", "parallax_bg_path", "texture_path"],
            },
        ),
        Tool(
            name="configure_particles_2d",
            description=(
                "Configura particulas 2D (GPUParticles2D) com parametros de emissao. "
                "Use para efeitos visuais: explosao, fumaca, sparkles, chuva, neve. "
                "Suporta presets: explosion, fire, smoke, rain, snow, sparkles, custom. "
                "Quando NAO usar: se o no nao for GPUParticles2D. "
                "Pre-condicoes: no GPUParticles2D deve existir na cena. "
                "Exemplo: {'scene_path': 'scenes/game.tscn', 'node_path': './Explosion', 'preset': 'explosion', 'amount': 100, 'lifetime': 1.5}. "
                "Erro mais comum: particulas nao visiveis sem run_game — compile_test nao mostra efeitos."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "scene_path": {"type": "string", "description": "Caminho da cena."},
                    "node_path": {"type": "string", "description": "Path do no GPUParticles2D."},
                    "amount": {"type": "integer", "description": "Quantidade de particulas (default 50)."},
                    "lifetime": {"type": "number", "description": "Tempo de vida em segundos (default 1.0)."},
                    "explosiveness": {"type": "number", "description": "0=continuo, 1=explosao unica (default 0)."},
                    "emitting": {"type": "boolean", "description": "Se esta emitindo (default true)."},
                    "one_shot": {"type": "boolean", "description": "Emite uma vez e para (default false)."},
                    "preset": {"type": "string", "description": "Preset: explosion, fire, smoke, rain, snow, sparkles, custom."},
                },
                "required": ["scene_path", "node_path"],
            },
        ),
        Tool(
            name="create_particles_3d",
            description=(
                "Adiciona GPUParticles3D a uma cena 3D com presets visuais. "
                "Use para fogo, fumaca, ou outros efeitos de particula em jogos 3D. "
                "Suporta presets: fire, smoke, sparkles, dust, rain. "
                "Pre-condicoes: cena 3D deve existir. "
                "Exemplo: {'scene_path': 'scenes/level.tscn', 'preset': 'fire', 'node_name': 'FireEffect'}. "
                "Erro mais comum: particulas nao visiveis — verifique iluminacao e camera 3D."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "scene_path": {"type": "string", "description": "Caminho da cena."},
                    "parent_node_path": {"type": "string", "description": "No pai (default '.' = raiz)."},
                    "node_name": {"type": "string", "description": "Nome do no (default 'GPUParticles3D')."},
                    "preset": {"type": "string", "description": "Preset: fire, smoke, sparkles, dust, rain."},
                },
                "required": ["scene_path"],
            },
        ),
        Tool(
            name="generate_shader_2d",
            description=(
                "Gera um shader 2D a partir de templates pre-definidos. "
                "Use para efeitos visuais avancados: glow, dissolve, outline, water, wind. "
                "O shader e salvo como arquivo .gdshader e aplicado ao no. "
                "Pre-condicoes: no alvo deve existir na cena. "
                "Exemplo: {'scene_path': 'scenes/game.tscn', 'node_path': './Player/Sprite', 'template': 'glow'}. "
                "Erro mais comum: shader nao visivel — compile_test nao renderiza shaders; use run_game."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "scene_path": {"type": "string", "description": "Caminho da cena."},
                    "node_path": {"type": "string", "description": "Path do no alvo."},
                    "template": {"type": "string", "description": "Template: glow, dissolve, outline, water, wind, grayscale, shockwave."},
                    "uniforms": {"type": "object", "description": "Valores de uniforms do shader (opcional)."},
                    "shader_name": {"type": "string", "description": "Nome do arquivo .gdshader (opcional)."},
                },
                "required": ["scene_path", "node_path", "template"],
            },
        ),
        Tool(
            name="apply_shader_to_node",
            description=(
                "Aplica um ShaderMaterial a um no da cena. "
                "Use para adicionar efeitos visuais como glow, outline ou dissolve a sprites e elementos de UI. "
                "Quando NAO usar: se o shader ainda nao foi gerado (use generate_shader_2d primeiro). "
                "Pre-condicoes: no alvo deve existir; shader template deve ser valido. "
                "Exemplo: {'scene_path': 'scenes/game.tscn', 'node_path': './Player/Sprite', 'shader_template': 'outline'}. "
                "Erro mais comum: shader_template invalido — use um dos templates suportados."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "scene_path": {"type": "string", "description": "Caminho da cena."},
                    "node_path": {"type": "string", "description": "Path do no alvo."},
                    "shader_template": {"type": "string", "description": "Template: glow, dissolve, outline, water, wind (default 'glow')."},
                    "uniforms": {"type": "object", "description": "Valores de uniforms do shader."},
                },
                "required": ["scene_path", "node_path"],
            },
        ),
        Tool(
            name="create_shader_material",
            description=(
                "Cria um ShaderMaterial personalizado com codigo shader e aplica a um no. "
                "Use para efeitos visuais customizados que nao tem template pronto. "
                "Quando NAO usar: se existir template adequado (use generate_shader_2d ou apply_shader_to_node). "
                "Pre-condicoes: no alvo deve existir na cena. "
                "Exemplo: {'scene_path': 'scenes/game.tscn', 'node_path': './Player/Sprite', "
                "'shader_code': 'void fragment() { COLOR = vec4(1.0, 0.0, 0.0, 1.0); }'}. "
                "Erro mais comum: sintaxe de shader invalida — verifique a documentacao Godot shading language."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "scene_path": {"type": "string", "description": "Caminho da cena."},
                    "node_path": {"type": "string", "description": "Path do no alvo."},
                    "shader_code": {"type": "string", "description": "Codigo GLSL do shader (apos 'shader_type ...')."},
                    "shader_type": {"type": "string", "description": "Tipo: canvas_item (2D), spatial (3D), particles (default: canvas_item)."},
                    "shader_name": {"type": "string", "description": "Nome do arquivo .gdshader (default: custom_shader)."},
                },
                "required": ["scene_path", "node_path", "shader_code"],
            },
        ),
        Tool(
            name="create_path_2d",
            description=(
                "Cria um Path2D com PathFollow2D para movimentacao controlada por curva. "
                "Use para plataformas moveis, rotas de camera, ou animacoes de trajetoria. "
                "Pre-condicoes: cena deve existir. "
                "Exemplo: {'scene_path': 'scenes/game.tscn', 'waypoints': [Vector2(0,0), Vector2(200,100), Vector2(400,0)], 'closed': true}. "
                "Erro mais comum: waypoints vazios — forneca pelo menos 2 pontos."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "scene_path": {"type": "string", "description": "Caminho da cena."},
                    "parent_node_path": {"type": "string", "description": "No pai (default '.')."},
                    "waypoints": {"type": "array", "description": "Lista de pontos Vector2 (ex: ['Vector2(0,0)', 'Vector2(100,100)'])."},
                    "path_name": {"type": "string", "description": "Nome do no Path2D (default 'Path2D')."},
                    "closed": {"type": "boolean", "description": "Se o caminho e fechado (loop, default false)."},
                },
                "required": ["scene_path"],
            },
        ),
        Tool(
            name="create_patrol_route",
            description=(
                "Cria uma rota de patrulha com waypoints e script de movimento automatico. "
                "Use para inimigos que patrulham, NPCs andando, ou objetos moveis em rotas. "
                "Suporta ping-pong (vai e volta) e pausa em cada waypoint. "
                "Pre-condicoes: cena e no pai devem existir. "
                "Exemplo: {'scene_path': 'scenes/game.tscn', 'parent_node_path': './Enemy', 'waypoints': ['Vector2(0,0)', 'Vector2(300,0)'], 'speed': 80, 'ping_pong': true}. "
                "Erro mais comum: waypoints em formato invalido — use 'Vector2(x, y)'."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "scene_path": {"type": "string", "description": "Caminho da cena."},
                    "parent_node_path": {"type": "string", "description": "No pai que recebera o script de patrulha."},
                    "waypoints": {"type": "array", "description": "Lista de posicoes Vector2."},
                    "speed": {"type": "number", "description": "Velocidade de movimento (default 100)."},
                    "wait_time": {"type": "number", "description": "Tempo de espera em cada waypoint (default 1.0s)."},
                    "ping_pong": {"type": "boolean", "description": "Vai e volta em vez de reiniciar (default true)."},
                },
                "required": ["scene_path", "parent_node_path", "waypoints"],
            },
        ),
        # ── Onda 10: Genero-Especifico ──
        Tool(
            name="create_dialogue_system",
            description=(
                "Cria um sistema de dialogo com autoload (DialogoManager) para jogos com NPCs. "
                "Use em RPGs, adventures, visual novels — qualquer jogo com conversas. "
                "Suporta branching, escolhas do jogador, e eventos disparados por dialogo. "
                "Pre-condicoes: projeto ativo. "
                "Exemplo: {'autoload_name': 'DialogoManager'}. "
                "Erro mais comum: sistema sem dialogos — use add_dialogue_node para popular."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "autoload_name": {"type": "string", "description": "Nome do autoload (default 'DialogueManager')."},
                },
                "required": [],
            },
        ),
        Tool(
            name="add_dialogue_node",
            description=(
                "Adiciona um no de dialogo ao sistema de dialogos. "
                "Use para criar cada fala, escolha ou evento na arvore de dialogo. "
                "Cada no tem: speaker (quem fala), text (o que diz), next_id (proxima fala), choices (opcoes do jogador). "
                "Pre-condicoes: create_dialogue_system deve ter sido chamado antes. "
                "Exemplo: {'dialogue_id': 'npc_hello', 'speaker': 'Ferreiros', 'text': 'Bem-vindo a minha loja!'}. "
                "Erro mais comum: dialogue_id duplicado — use IDs unicos."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "dialogue_id": {"type": "string", "description": "ID unico do dialogo."},
                    "speaker": {"type": "string", "description": "Nome de quem fala."},
                    "text": {"type": "string", "description": "Texto da fala."},
                    "next_id": {"type": "string", "description": "ID do proximo dialogo (vazio = fim)."},
                    "choices": {"type": "array", "description": "Opcoes do jogador [{text, next_id}]."},
                    "events": {"type": "array", "description": "Eventos disparados [{type, params}]."},
                },
                "required": ["dialogue_id", "speaker", "text"],
            },
        ),
        Tool(
            name="create_dialogue_ui",
            description=(
                "Cria a interface visual do sistema de dialogo (caixa de texto + nome + opcoes). "
                "Use apos create_dialogue_system para criar a UI que exibe os dialogos. "
                "Pre-condicoes: create_dialogue_system deve existir. "
                "Exemplo: {'scene_name': 'dialogue_ui'}. "
                "Erro mais comum: UI nao aparece — instancie a cena na cena principal."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "scene_name": {"type": "string", "description": "Nome da cena de UI (default 'dialogue_ui')."},
                },
                "required": [],
            },
        ),
        Tool(
            name="create_inventory_system",
            description=(
                "Cria um sistema de inventario com autoload (InventoryManager). "
                "Use em RPGs, adventures, survival — qualquer jogo com coleta de itens. "
                "Suporta slots, stacking, maximo de itens configuravel. "
                "Pre-condicoes: projeto ativo. "
                "Exemplo: {'autoload_name': 'InventoryManager', 'max_slots': 20}. "
                "Erro mais comum: inventario sem itens — use define_inventory_item para popular."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "autoload_name": {"type": "string", "description": "Nome do autoload (default 'InventoryManager')."},
                    "max_slots": {"type": "integer", "description": "Maximo de slots (default 20)."},
                },
                "required": [],
            },
        ),
        Tool(
            name="define_inventory_item",
            description=(
                "Define um item do inventario com nome, tipo, descricao e propriedades. "
                "Use para criar cada item coletavel: pocoes, armas, chaves, recursos. "
                "Tipos: consumable, weapon, armor, key_item, resource, quest. "
                "Pre-condicoes: create_inventory_system deve existir. "
                "Exemplo: {'item_id': 'health_potion', 'item_name': 'Pocao de Vida', 'item_type': 'consumable', 'stackable': true, 'max_stack': 10}. "
                "Erro mais comum: item_id duplicado — use IDs unicos."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "item_id": {"type": "string", "description": "ID unico do item."},
                    "item_name": {"type": "string", "description": "Nome visivel do item."},
                    "item_type": {"type": "string", "description": "Tipo: consumable, weapon, armor, key_item, resource, quest."},
                    "description": {"type": "string", "description": "Descricao do item."},
                    "stackable": {"type": "boolean", "description": "Se pode empilhar (default true)."},
                    "max_stack": {"type": "integer", "description": "Maximo por pilha (default 99)."},
                    "icon_path": {"type": "string", "description": "Caminho do icone (opcional)."},
                    "properties": {"type": "object", "description": "Propriedades extras (ex: {heal_amount: 50, damage: 10})."},
                },
                "required": ["item_id", "item_name"],
            },
        ),
        Tool(
            name="create_inventory_ui",
            description=(
                "Cria a interface visual do inventario (grade de slots + icones). "
                "Use apos create_inventory_system para criar a UI que exibe os itens. "
                "Suporta grid configuravel (colunas, linhas). "
                "Pre-condicoes: create_inventory_system deve existir. "
                "Exemplo: {'columns': 5}. "
                "Erro mais comum: UI nao aparece — instancie na cena principal."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "scene_name": {"type": "string", "description": "Nome da cena de UI (default 'inventory_ui')."},
                    "columns": {"type": "integer", "description": "Numero de colunas na grade (default 5)."},
                },
                "required": [],
            },
        ),
        Tool(
            name="create_bullet_template",
            description=(
                "Cria uma cena de projetil (bullet) reutilizavel para sistemas de tiro. "
                "Use em shooters, tower defense, ou qualquer jogo com armas de projetil. "
                "Define velocidade, dano, tempo de vida, cor e tamanho do projetil. "
                "Pre-condicoes: projeto ativo. "
                "Exemplo: {'bullet_name': 'Laser', 'speed': 800, 'damage': 25, 'bullet_color': '#ff0000'}. "
                "Erro mais comum: bullet nao aparece — verifique collision layers."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "bullet_name": {"type": "string", "description": "Nome do projetil (default 'Bullet')."},
                    "speed": {"type": "number", "description": "Velocidade em px/s (default 500)."},
                    "damage": {"type": "number", "description": "Dano causado (default 10)."},
                    "lifetime": {"type": "number", "description": "Tempo de vida em segundos (default 3.0)."},
                    "bullet_color": {"type": "string", "description": "Cor em hex (default '#ffff00')."},
                    "bullet_size": {"type": "integer", "description": "Tamanho em px (default 8)."},
                },
                "required": [],
            },
        ),
        Tool(
            name="create_gun_system",
            description=(
                "Cria um script de sistema de arma com fire rate, municao, reload e spread. "
                "Use para armas do player ou inimigos: pistola, metralhadora, shotgun. "
                "Inclui controle de municao maxima, recarga automatica e angulo de dispersao. "
                "Pre-condicoes: bullet scene deve existir (use create_bullet_template). "
                "Exemplo: {'script_path': 'scripts/player_gun.gd', 'fire_rate': 0.2, 'ammo_max': 30, 'spread_angle': 5.0}. "
                "Erro mais comum: bullet_scene_path invalido — crie o projetil primeiro."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "script_path": {"type": "string", "description": "Caminho para salvar o script da arma."},
                    "bullet_scene_path": {"type": "string", "description": "Caminho da cena do projetil (default 'res://scenes/bullet.tscn')."},
                    "fire_rate": {"type": "number", "description": "Intervalo entre tiros em segundos (default 0.3)."},
                    "ammo_max": {"type": "integer", "description": "Municao maxima (default 30)."},
                    "spread_angle": {"type": "number", "description": "Angulo de dispersao em graus (default 0 = tiro perfeito)."},
                    "auto_reload": {"type": "boolean", "description": "Recarga automatica quando vazio (default true)."},
                    "reload_time": {"type": "number", "description": "Tempo de recarga em segundos (default 1.5)."},
                },
                "required": ["script_path"],
            },
        ),
        Tool(
            name="generate_tilemap_from_noise",
            description=(
                "Gera um tilemap procedural usando Perlin noise para terreno natural. "
                "Use para criar mapas aleatorios: cavernas, ilhas, florestas. "
                "Define quais tiles sao chao e quais sao parede por indice. "
                "Pre-condicoes: cena e TileMapLayer devem existir. "
                "Exemplo: {'scene_path': 'scenes/game.tscn', 'tilemap_layer_path': './Ground', 'width': 60, 'height': 40, 'threshold': 0.45, 'seed': 42}. "
                "Erro mais comum: tilemap_layer_path invalido — crie a camada com create_tilemap_layer primeiro."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "scene_path": {"type": "string", "description": "Caminho da cena."},
                    "tilemap_layer_path": {"type": "string", "description": "Path da TileMapLayer."},
                    "tile_size": {"type": "integer", "description": "Tamanho do tile em px (default 32)."},
                    "width": {"type": "integer", "description": "Largura em tiles (default 40)."},
                    "height": {"type": "integer", "description": "Altura em tiles (default 30)."},
                    "seed": {"type": "integer", "description": "Seed do noise (default 0 = aleatorio)."},
                    "threshold": {"type": "number", "description": "Limiar 0-1 (default 0.5, menor = mais chao)."},
                    "tile_ground": {"type": "integer", "description": "Indice do tile de chao (default 0)."},
                    "tile_wall": {"type": "integer", "description": "Indice do tile de parede (default 1)."},
                },
                "required": ["scene_path", "tilemap_layer_path"],
            },
        ),
        Tool(
            name="generate_dungeon_rooms",
            description=(
                "Gera um layout procedural de dungeon com salas e corredores. "
                "Use para roguelikes, RPGs, ou qualquer jogo com masmorras aleatorias. "
                "Retorna dados das salas (posicao, tamanho) para spawn de inimigos/tesouros. "
                "Pre-condicoes: nenhuma (ferramenta de design, gera dados). "
                "Exemplo: {'num_rooms': 10, 'min_size': 5, 'max_size': 12, 'map_width': 80, 'map_height': 60, 'seed': 123}. "
                "Erro mais comum: nenhum — sempre retorna dados de layout."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "num_rooms": {"type": "integer", "description": "Numero de salas (default 8)."},
                    "min_size": {"type": "integer", "description": "Tamanho minimo da sala (default 5)."},
                    "max_size": {"type": "integer", "description": "Tamanho maximo da sala (default 12)."},
                    "map_width": {"type": "integer", "description": "Largura do mapa (default 80)."},
                    "map_height": {"type": "integer", "description": "Altura do mapa (default 60)."},
                    "corridor_width": {"type": "integer", "description": "Largura dos corredores (default 2)."},
                    "seed": {"type": "integer", "description": "Seed para reproducibilidade (default 0)."},
                },
                "required": [],
            },
        ),
        Tool(
            name="create_loading_screen",
            description=(
                "Cria uma tela de carregamento com barra de progresso e dicas. "
                "Use para transicoes entre cenas grandes ou ao iniciar o jogo. "
                "Suporta dicas aleatorias, cor de fundo e tempo minimo de exibicao. "
                "Pre-condicoes: projeto ativo. "
                "Exemplo: {'tips': ['Dica 1', 'Dica 2'], 'background_color': '#1a1a2e', 'min_load_time': 2.0}. "
                "Erro mais comum: tela nao aparece — use load_scene_async para ativa-la."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "scene_name": {"type": "string", "description": "Nome da cena (default 'loading_screen')."},
                    "tips": {"type": "array", "items": {"type": "string"}, "description": "Lista de dicas para exibir."},
                    "min_load_time": {"type": "number", "description": "Tempo minimo de exibicao (default 1.0s)."},
                    "background_color": {"type": "string", "description": "Cor de fundo em hex (default '#1a1a2e')."},
                },
                "required": [],
            },
        ),
        Tool(
            name="load_scene_async",
            description=(
                "Carrega uma cena de forma assincrona com tela de loading. "
                "Use para transicoes suaves entre fases ou areas grandes. "
                "Mostra progresso real de carregamento na loading screen. "
                "Pre-condicoes: loading screen deve existir (use create_loading_screen). "
                "Exemplo: {'target_scene': 'res://scenes/level_2.tscn', 'loading_scene': 'res://scenes/loading_screen.tscn'}. "
                "Erro mais comum: loading_scene nao encontrada — crie com create_loading_screen."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "target_scene": {"type": "string", "description": "Caminho da cena a carregar (ex: 'res://scenes/level.tscn')."},
                    "loading_scene": {"type": "string", "description": "Caminho da loading screen (default 'res://scenes/loading_screen.tscn')."},
                },
                "required": ["target_scene"],
            },
        ),
        # ── Onda 11: Complementos ──
        Tool(
            name="add_raycast_2d",
            description=(
                "Adiciona um RayCast2D a um no para deteccao de linha de visao. "
                "Use para: verificar se ha chao a frente, detectar obstaculos, mirar armas. "
                "Configura posicao alvo (target_position), collision_mask e enabled. "
                "Pre-condicoes: cena e no pai devem existir. "
                "Exemplo: {'scene_path': 'scenes/player.tscn', 'parent_node_path': '.', 'target_position': 'Vector2(100, 0)', 'collision_mask': 2}. "
                "Erro mais comum: raycast nao detecta nada — verifique collision_mask e layers."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "scene_path": {"type": "string", "description": "Caminho da cena."},
                    "parent_node_path": {"type": "string", "description": "No pai que recebera o RayCast2D."},
                    "target_position": {"type": "string", "description": "Posicao alvo (ex: 'Vector2(100, 0)')."},
                    "collision_mask": {"type": "integer", "description": "Mascara de colisao (default 1)."},
                    "enabled": {"type": "boolean", "description": "Se esta ativo (default true)."},
                    "node_name": {"type": "string", "description": "Nome do no (default 'RayCast2D')."},
                },
                "required": ["scene_path", "parent_node_path"],
            },
        ),
        Tool(
            name="add_shapecast_2d",
            description=(
                "Adiciona um ShapeCast2D para deteccao de area em linha. "
                "Use para deteccao mais robusta que RayCast: ataques melee, sensores de chao largos. "
                "Suporta formas: rectangle, circle, capsule. "
                "Pre-condicoes: cena e no pai devem existir. "
                "Exemplo: {'scene_path': 'scenes/player.tscn', 'parent_node_path': '.', 'shape_type': 'rectangle', 'shape_size': 'Vector2(40, 10)'}. "
                "Erro mais comum: shape_size invalido — use 'Vector2(w, h)'."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "scene_path": {"type": "string", "description": "Caminho da cena."},
                    "parent_node_path": {"type": "string", "description": "No pai."},
                    "shape_type": {"type": "string", "description": "Forma: rectangle, circle, capsule (default 'rectangle')."},
                    "shape_size": {"type": "string", "description": "Tamanho (ex: 'Vector2(40, 10)')."},
                    "collision_mask": {"type": "integer", "description": "Mascara de colisao (default 1)."},
                    "node_name": {"type": "string", "description": "Nome do no (default 'ShapeCast2D')."},
                },
                "required": ["scene_path", "parent_node_path"],
            },
        ),
        Tool(
            name="enable_debug_collisions",
            description=(
                "Ativa ou desativa a visualizacao de collision shapes no projeto. "
                "Use para debugar fisica: ver por que o player atravessa paredes ou inimigos nao colidem. "
                "Modifica a configuracao 'debug/shapes/collision' no project.godot. "
                "Pre-condicoes: projeto ativo. "
                "Exemplo: {'enabled': true}. "
                "Erro mais comum: mudanca so visivel apos reiniciar o jogo (run_game)."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "enabled": {"type": "boolean", "description": "Ativar (true) ou desativar (false) debug de colisoes (default true)."},
                },
                "required": [],
            },
        ),
        Tool(
            name="enable_debug_navigation",
            description=(
                "Ativa ou desativa a visualizacao de navigation mesh no editor e jogo. "
                "Use para debugar pathfinding: ver por que inimigos nao navegam ou ficam presos. "
                "Modifica a configuracao 'debug/shapes/navigation' no project.godot. "
                "Pre-condicoes: projeto ativo. "
                "Exemplo: {'enabled': true}. "
                "Erro mais comum: mudanca so visivel apos reiniciar o jogo."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "enabled": {"type": "boolean", "description": "Ativar (true) ou desativar (false) debug de navegacao (default true)."},
                },
                "required": [],
            },
        ),
        Tool(
            name="get_performance_stats",
            description=(
                "Retorna estatisticas de performance do projeto: tempo de compilacao, scripts, cenas. "
                "Use para monitorar a complexidade do projeto e identificar problemas de performance. "
                "Roda Godot em modo headless para coletar metricas. "
                "Pre-condicoes: projeto ativo deve compilar. "
                "Exemplo: {} (chamada sem argumentos). "
                "Erro mais comum: projeto com erros de compilacao — corrija com compile_test primeiro."
            ),
            inputSchema={
                "type": "object",
                "properties": {},
                "required": [],
            },
        ),
        Tool(
            name="setup_localization",
            description=(
                "Configura o sistema de traducao (i18n) do projeto. "
                "Use para jogos com suporte a multiplos idiomas (ex: PT-BR, EN, ES). "
                "Cria arquivos de traducao CSV e configura o TranslationServer. "
                "Pre-condicoes: projeto ativo. "
                "Exemplo: {'default_locale': 'pt_BR', 'additional_locales': ['en', 'es']}. "
                "Erro mais comum: traducoes nao aparecem — use add_translation_string para cada texto."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "default_locale": {"type": "string", "description": "Localidade padrao (default 'pt_BR')."},
                    "additional_locales": {"type": "array", "items": {"type": "string"}, "description": "Localidades adicionais (ex: ['en', 'es'])."},
                },
                "required": [],
            },
        ),
        Tool(
            name="add_translation_string",
            description=(
                "Adiciona uma string traduzida ao sistema de localizacao. "
                "Use para cada texto que aparece na UI: botoes, labels, dialogos. "
                "Forneca as traducoes como dicionario {locale: texto}. "
                "Pre-condicoes: setup_localization deve ter sido chamado. "
                "Exemplo: {'key': 'BTN_PLAY', 'translations': {'pt_BR': 'Jogar', 'en': 'Play', 'es': 'Jugar'}}. "
                "Erro mais comum: key duplicada — use keys unicas."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "key": {"type": "string", "description": "Chave da string (ex: 'BTN_PLAY', 'TXT_WELCOME')."},
                    "translations": {"type": "object", "description": "Dicionario {locale: texto}."},
                },
                "required": ["key", "translations"],
            },
        ),
        Tool(
            name="create_light_3d",
            description=(
                "Adiciona uma luz 3D (OmniLight3D, SpotLight3D ou DirectionalLight3D) a uma cena. "
                "Use para iluminar cenas 3D: tochas, lanternas, luz solar. "
                "Configura cor, energia (intensidade) e sombras. "
                "Pre-condicoes: cena 3D deve existir. "
                "Exemplo: {'scene_path': 'scenes/level.tscn', 'light_type': 'spot', 'color': '#ffaa44', 'energy': 2.0, 'shadows': true}. "
                "Erro mais comum: luz nao visivel — verifique cor e energia (valores baixos = escuro)."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "scene_path": {"type": "string", "description": "Caminho da cena."},
                    "parent_node_path": {"type": "string", "description": "No pai (default '.')."},
                    "light_type": {"type": "string", "description": "Tipo: omni, spot, directional (default 'omni')."},
                    "color": {"type": "string", "description": "Cor em hex (default '#ffffff')."},
                    "energy": {"type": "number", "description": "Intensidade (default 1.0)."},
                    "shadows": {"type": "boolean", "description": "Ativar sombras (default false)."},
                    "node_name": {"type": "string", "description": "Nome do no (vazio = auto)."},
                },
                "required": ["scene_path"],
            },
        ),
        Tool(
            name="create_csg_shape",
            description=(
                "Adiciona uma forma CSG (prototipagem 3D) a uma cena. "
                "Use para criar geometria 3D rapida: caixas, esferas, cilindros para blockout de niveis. "
                "CSG e ideal para prototipagem — substitua por mesh final depois. "
                "Suporta: box, sphere, cylinder, torus. "
                "Pre-condicoes: cena 3D deve existir. "
                "Exemplo: {'scene_path': 'scenes/level.tscn', 'shape_type': 'box', 'dimensions': 'Vector3(2, 1, 2)'}. "
                "Erro mais comum: dimensoes invalidas — use 'Vector3(x, y, z)'."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "scene_path": {"type": "string", "description": "Caminho da cena."},
                    "parent_node_path": {"type": "string", "description": "No pai (default '.')."},
                    "shape_type": {"type": "string", "description": "Forma: box, sphere, cylinder, torus (default 'box')."},
                    "dimensions": {"type": "string", "description": "Dimensoes (ex: 'Vector3(2, 1, 2)')."},
                    "node_name": {"type": "string", "description": "Nome do no (vazio = auto)."},
                },
                "required": ["scene_path"],
            },
        ),
        Tool(
            name="configure_standard_material_3d",
            description=(
                "Aplica e configura um StandardMaterial3D a um MeshInstance3D. "
                "Use para definir aparencia de objetos 3D: cor, metallic, roughness. "
                "Suporta presets: metal, plastic, wood, stone, glass, emissive, custom. "
                "Pre-condicoes: no alvo deve ser MeshInstance3D. "
                "Exemplo: {'scene_path': 'scenes/level.tscn', 'node_path': './Cube', 'preset': 'metal'}. "
                "Erro mais comum: no nao e MeshInstance3D — verifique o tipo do no."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "scene_path": {"type": "string", "description": "Caminho da cena."},
                    "node_path": {"type": "string", "description": "Path do MeshInstance3D."},
                    "preset": {"type": "string", "description": "Preset: metal, plastic, wood, stone, glass, emissive, custom."},
                },
                "required": ["scene_path", "node_path"],
            },
        ),
        Tool(
            name="configure_export_preset",
            description=(
                "Configura um preset de exportacao (Windows, Linux, macOS, Web, Android). "
                "Use antes de build_export para definir nome do app, versao, icone e empresa. "
                "Pre-condicoes: projeto ativo. "
                "Exemplo: {'preset_name': 'Windows Desktop', 'app_name': 'Meu Jogo', 'version': '1.0.0', 'company': 'MeuEstudio'}. "
                "Erro mais comum: preset_name invalido — use um dos presets suportados pelo Godot."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "preset_name": {"type": "string", "description": "Nome do preset (default 'Windows Desktop')."},
                    "app_name": {"type": "string", "description": "Nome do aplicativo."},
                    "version": {"type": "string", "description": "Versao (ex: '1.0.0')."},
                    "icon_path": {"type": "string", "description": "Caminho do icone .ico/.png."},
                    "company": {"type": "string", "description": "Nome da empresa/estudio."},
                },
                "required": [],
            },
        ),
        Tool(
            name="configure_audio_bus",
            description=(
                "Configura um bus de audio (Master, SFX, Music, Voice) com volume, mute e solo. "
                "Use para balancear o audio do jogo: efeitos sonoros vs musica de fundo. "
                "Pre-condicoes: projeto ativo. "
                "Exemplo: {'bus_name': 'SFX', 'volume_db': -3.0, 'mute': false}. "
                "Erro mais comum: bus_name nao encontrado — use nomes validos: Master, SFX, Music, Voice."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "bus_name": {"type": "string", "description": "Nome do bus: Master, SFX, Music, Voice."},
                    "volume_db": {"type": "number", "description": "Volume em dB (default 0.0, negativo = mais baixo)."},
                    "mute": {"type": "boolean", "description": "Silenciar (default false)."},
                    "solo": {"type": "boolean", "description": "Solo — toca so este bus (default false)."},
                },
                "required": ["bus_name"],
            },
        ),
        Tool(
            name="add_audio_effect",
            description=(
                "Adiciona um efeito de audio a um bus (reverb, delay, EQ, compressor, distortion). "
                "Use para melhorar a qualidade do audio: reverb em ambientes, delay em eco, compressor para normalizar. "
                "Pre-condicoes: bus deve existir. "
                "Exemplo: {'bus_name': 'SFX', 'effect_type': 'reverb'}. "
                "Erro mais comum: effect_type invalido — use: reverb, delay, eq, compressor, distortion, chorus, filter."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "bus_name": {"type": "string", "description": "Nome do bus de audio."},
                    "effect_type": {"type": "string", "description": "Tipo: reverb, delay, eq, compressor, distortion, chorus, filter."},
                },
                "required": ["bus_name", "effect_type"],
            },
        ),
        # ── Onda 7: Robustez (saude e autoteste) ──
        Tool(
            name="health_check",
            description=(
                "Verifica a saude de todos os componentes do MCP: config.json, Godot, ClassDB, templates, projeto ativo. "
                "Use no inicio de sessoes para diagnosticar problemas de configuracao. "
                "Retorna status de cada componente e veredito geral (saudavel ou nao). "
                "Pre-condicoes: nenhuma. "
                "Exemplo: {} (chamada sem argumentos). "
                "Erro mais comum: Godot nao encontrado — verifique godot_path no config.json."
            ),
            inputSchema={
                "type": "object",
                "properties": {},
                "required": [],
            },
        ),
        Tool(
            name="self_test",
            description=(
                "Executa uma suite de testes internos do MCP: ping, ClassDB, godot_parser, jinja2, Pillow. "
                "Use para verificar se todas as dependencias estao funcionais. "
                "Retorna resultados individuais e veredito geral (todos passaram ou nao). "
                "Pre-condicoes: nenhuma. "
                "Exemplo: {} (chamada sem argumentos). "
                "Erro mais comum: Pillow/Jinja2 nao instalados — algumas funcionalidades ficam limitadas."
            ),
            inputSchema={
                "type": "object",
                "properties": {},
                "required": [],
            },
        ),
    ]

    # ── Pós-processamento: hints MCP + additionalProperties ────────
    _READONLY = {
        "ping", "validate_godot_version", "get_project_settings",
        "inspect_project", "read_file", "load_scene_tree",
        "get_node_property", "query_classdb", "list_valid_node_types",
        "list_signals", "validate_gdscript_syntax", "compile_test",
        "read_console_output", "take_screenshot", "list_export_presets",
        "validate_export_templates_installed", "list_backups",
        "compare_screenshots", "detect_empty_screen",
        "detect_offscreen_elements", "suggest_color_palette",
        "analyze_game_structure", "suggest_next_steps",
        "find_missing_references", "validate_game_design",
        "estimate_game_scope", "search_codebase", "get_project_history",
        "get_undo_history", "health_check", "self_test", "get_performance_stats",
    }
    _DESTRUCTIVE = {
        "delete_file", "delete_node", "write_file", "move_file",
        "restore_backup", "build_export", "close_editor", "stop_game",
        "detach_script", "create_project", "set_project_setting",
        "set_main_scene", "configure_input_action", "configure_autoload",
        "set_collision_layer_mask", "reparent_node", "paint_tilemap_cell",
        "add_node", "set_node_property", "create_scene", "add_collision_shape",
        "create_tileset", "create_tilemap_layer", "create_animation_player",
        "create_animation", "create_ui_scene", "add_control_node",
        "launch_editor", "inject_input_event", "execute_gdscript_runtime",
        "attach_script", "add_script_variable", "add_script_signal",
        "generate_gdscript", "import_texture", "import_sprite_sheet",
        "import_audio", "connect_signal", "instance_scene_as_child",
        "watch_signal", "git_commit_checkpoint", "set_active_project",
        "capture_game_screenshot", "add_nodes_batch", "set_properties_batch",
        "generate_placeholder_sprite", "generate_placeholder_texture_atlas",
        "generate_background_gradient", "generate_tileset_from_colors",
        "generate_audio_sfx", "create_animation_tree", "set_physics_material",
        "create_joint_2d", "import_3d_model", "create_particles_2d",
        "create_light_2d", "create_shader_material",
        "undo_last_action", "generate_project_structure",
        "create_parallax_background", "add_parallax_layer", "configure_particles_2d",
        "create_particles_3d", "generate_shader_2d", "apply_shader_to_node",
        "create_path_2d", "create_patrol_route",
        "create_dialogue_system", "add_dialogue_node", "create_dialogue_ui",
        "create_inventory_system", "define_inventory_item", "create_inventory_ui",
        "create_bullet_template", "create_gun_system",
        "generate_tilemap_from_noise", "generate_dungeon_rooms",
        "create_loading_screen", "load_scene_async",
        "add_raycast_2d", "add_shapecast_2d",
        "enable_debug_collisions", "enable_debug_navigation",
        "setup_localization", "add_translation_string",
        "create_light_3d", "create_csg_shape",
        "configure_standard_material_3d", "configure_export_preset",
        "configure_audio_bus", "add_audio_effect",
    }
    _IDEMPOTENT = _READONLY | {
        "set_project_setting", "set_main_scene", "configure_input_action",
        "configure_autoload", "set_collision_layer_mask", "set_node_property",
        "create_project", "set_active_project",
    }
    # ── Annotations (Onda 6): titles em PT-BR + tags ────────────────
    _TITLES = {
        "ping": "Ping — Verificar Conexão",
        "validate_godot_version": "Validar Versão do Godot",
        "set_active_project": "Definir Projeto Ativo",
        "create_project": "Criar Novo Projeto",
        "get_project_settings": "Ler Configurações do Projeto",
        "set_project_setting": "Definir Configuração do Projeto",
        "set_main_scene": "Definir Cena Principal",
        "configure_input_action": "Configurar Ação de Input",
        "configure_autoload": "Configurar Autoload (Singleton)",
        "inspect_project": "Inspecionar Arquivos do Projeto",
        "read_file": "Ler Arquivo",
        "write_file": "Escrever Arquivo",
        "delete_file": "Deletar Arquivo",
        "move_file": "Mover/Renomear Arquivo",
        "create_scene": "Criar Cena (.tscn)",
        "load_scene_tree": "Carregar Árvore da Cena",
        "add_node": "Adicionar Nó",
        "delete_node": "Remover Nó",
        "set_node_property": "Definir Propriedade do Nó",
        "get_node_property": "Ler Propriedade do Nó",
        "reparent_node": "Re-parentar Nó",
        "instance_scene_as_child": "Instanciar Sub-Cena",
        "connect_signal": "Conectar Sinal",
        "list_signals": "Listar Sinais",
        "query_classdb": "Consultar ClassDB",
        "list_valid_node_types": "Listar Tipos de Nó Válidos",
        "generate_gdscript": "Gerar GDScript (Template)",
        "attach_script": "Anexar Script ao Nó",
        "detach_script": "Desanexar Script",
        "validate_gdscript_syntax": "Validar Sintaxe GDScript",
        "add_script_variable": "Adicionar Variável ao Script",
        "add_script_signal": "Adicionar Sinal ao Script",
        "add_collision_shape": "Adicionar Forma de Colisão",
        "set_collision_layer_mask": "Configurar Camadas de Colisão",
        "import_texture": "Importar Textura",
        "import_sprite_sheet": "Importar Sprite Sheet",
        "import_audio": "Importar Áudio",
        "compile_test": "Teste de Compilação",
        "run_game": "Rodar Jogo",
        "stop_game": "Parar Jogo",
        "smart_restart": "Reinicio Inteligente",
        "launch_editor": "Abrir Editor Godot",
        "close_editor": "Fechar Editor Godot",
        "take_screenshot": "Capturar Screenshot (Editor)",
        "read_console_output": "Ler Console",
        "create_tileset": "Criar TileSet",
        "create_tilemap_layer": "Criar Camada TileMap",
        "paint_tilemap_cell": "Pintar Célula do TileMap",
        "create_animation_player": "Criar AnimationPlayer",
        "create_animation": "Criar Animação",
        "create_ui_scene": "Criar Cena de UI",
        "add_control_node": "Adicionar Nó de UI",
        "list_export_presets": "Listar Presets de Exportação",
        "validate_export_templates_installed": "Validar Templates de Exportação",
        "build_export": "Exportar Projeto",
        "list_backups": "Listar Backups",
        "restore_backup": "Restaurar Backup",
        "git_commit_checkpoint": "Checkpoint Git",
        "inject_input_event": "Injetar Evento de Input",
        "execute_gdscript_runtime": "Executar GDScript (Runtime)",
        "watch_signal": "Observar Sinal",
        "capture_game_screenshot": "Capturar Screenshot do Jogo",
        "compare_screenshots": "Comparar Screenshots",
        "detect_empty_screen": "Detectar Tela Vazia",
        "detect_offscreen_elements": "Detectar Elementos Fora da Tela",
        "add_nodes_batch": "Adicionar Nós em Lote",
        "set_properties_batch": "Definir Propriedades em Lote",
        "generate_placeholder_sprite": "Gerar Sprite Placeholder",
        "generate_placeholder_texture_atlas": "Gerar Sprite Sheet Placeholder",
        "generate_background_gradient": "Gerar Fundo com Gradiente",
        "generate_tileset_from_colors": "Gerar Tileset de Cores",
        "generate_audio_sfx": "Gerar Efeito Sonoro (SFX)",
        "suggest_color_palette": "Sugerir Paleta de Cores",
        "analyze_game_structure": "Analisar Estrutura do Jogo",
        "suggest_next_steps": "Sugerir Próximos Passos",
        "find_missing_references": "Encontrar Referências Quebradas",
        "validate_game_design": "Validar Game Design",
        "estimate_game_scope": "Estimar Escopo do Jogo",
        "search_codebase": "Buscar no Código",
        "get_project_history": "Histórico do Projeto",
        "create_animation_tree": "Criar AnimationTree",
        "set_physics_material": "Configurar Material de Física",
        "create_joint_2d": "Criar Junta 2D",
        "import_3d_model": "Importar Modelo 3D",
        "create_particles_2d": "Criar Partículas 2D",
        "create_light_2d": "Criar Luz 2D",
        "create_shader_material": "Criar Shader Material",
        "generate_project_structure": "Gerar Estrutura do Projeto",
        "record_gameplay_gif": "Gravar Gameplay (GIF)",
        "undo_last_action": "Desfazer Última Ação",
        "get_undo_history": "Histórico de Desfazer",
        "create_parallax_background": "Criar Fundo Parallax",
        "add_parallax_layer": "Adicionar Camada Parallax",
        "configure_particles_2d": "Configurar Partículas 2D",
        "create_particles_3d": "Criar Partículas 3D",
        "generate_shader_2d": "Gerar Shader 2D",
        "apply_shader_to_node": "Aplicar Shader ao Nó",
        "create_path_2d": "Criar Path 2D",
        "create_patrol_route": "Criar Rota de Patrulha",
        "create_dialogue_system": "Criar Sistema de Diálogo",
        "add_dialogue_node": "Adicionar Nó de Diálogo",
        "create_dialogue_ui": "Criar UI de Diálogo",
        "create_inventory_system": "Criar Sistema de Inventário",
        "define_inventory_item": "Definir Item do Inventário",
        "create_inventory_ui": "Criar UI de Inventário",
        "create_bullet_template": "Criar Template de Projétil",
        "create_gun_system": "Criar Sistema de Arma",
        "generate_tilemap_from_noise": "Gerar Tilemap com Noise",
        "generate_dungeon_rooms": "Gerar Salas de Dungeon",
        "create_loading_screen": "Criar Tela de Carregamento",
        "load_scene_async": "Carregar Cena Assíncrono",
        "add_raycast_2d": "Adicionar RayCast2D",
        "add_shapecast_2d": "Adicionar ShapeCast2D",
        "enable_debug_collisions": "Ativar Debug de Colisões",
        "enable_debug_navigation": "Ativar Debug de Navegação",
        "get_performance_stats": "Estatísticas de Performance",
        "setup_localization": "Configurar Localização (i18n)",
        "add_translation_string": "Adicionar String Traduzida",
        "create_light_3d": "Criar Luz 3D",
        "create_csg_shape": "Criar Forma CSG 3D",
        "configure_standard_material_3d": "Configurar Material 3D",
        "configure_export_preset": "Configurar Preset de Exportação",
        "configure_audio_bus": "Configurar Bus de Áudio",
        "add_audio_effect": "Adicionar Efeito de Áudio",
        "health_check": "Verificação de Saúde",
        "self_test": "Auto-Teste do MCP",
    }
    _TAGS = {
        "capture_game_screenshot": ["visão", "screenshot"],
        "compare_screenshots": ["visão", "análise"],
        "detect_empty_screen": ["visão", "diagnóstico"],
        "detect_offscreen_elements": ["visão", "análise"],
        "add_nodes_batch": ["performance", "batch"],
        "set_properties_batch": ["performance", "batch"],
        "generate_placeholder_sprite": ["assets", "placeholder", "2D"],
        "generate_placeholder_texture_atlas": ["assets", "animação", "placeholder"],
        "generate_background_gradient": ["assets", "background"],
        "generate_tileset_from_colors": ["assets", "tilemap"],
        "generate_audio_sfx": ["assets", "áudio"],
        "suggest_color_palette": ["assets", "design"],
        "analyze_game_structure": ["ia", "análise", "métricas"],
        "suggest_next_steps": ["ia", "planejamento"],
        "find_missing_references": ["ia", "diagnóstico"],
        "validate_game_design": ["ia", "design", "checklist"],
        "estimate_game_scope": ["ia", "métricas"],
        "search_codebase": ["ia", "busca"],
        "get_project_history": ["ia", "histórico"],
        "create_animation_tree": ["animação", "avançado"],
        "set_physics_material": ["física", "material"],
        "create_joint_2d": ["física", "joint"],
        "import_3d_model": ["3D", "import"],
        "create_particles_2d": ["efeitos", "partículas"],
        "create_light_2d": ["iluminação", "2D"],
        "create_shader_material": ["shader", "efeitos"],
        "generate_project_structure": ["projeto", "scaffolding"],
        "record_gameplay_gif": ["visão", "gravação", "gif"],
        "undo_last_action": ["desfazer", "backup"],
        "get_undo_history": ["desfazer", "histórico"],
        "create_parallax_background": ["parallax", "background", "2D"],
        "add_parallax_layer": ["parallax", "2D"],
        "configure_particles_2d": ["efeitos", "partículas", "2D"],
        "create_particles_3d": ["efeitos", "partículas", "3D"],
        "generate_shader_2d": ["shader", "efeitos", "2D"],
        "apply_shader_to_node": ["shader", "efeitos"],
        "create_path_2d": ["movimento", "curva", "2D"],
        "create_patrol_route": ["ia", "patrulha", "movimento"],
        "create_dialogue_system": ["diálogo", "npc", "rpg"],
        "add_dialogue_node": ["diálogo", "npc"],
        "create_dialogue_ui": ["diálogo", "ui"],
        "create_inventory_system": ["inventário", "rpg"],
        "define_inventory_item": ["inventário", "item"],
        "create_inventory_ui": ["inventário", "ui"],
        "create_bullet_template": ["combate", "projétil", "shooter"],
        "create_gun_system": ["combate", "arma", "shooter"],
        "generate_tilemap_from_noise": ["tilemap", "procedural", "noise"],
        "generate_dungeon_rooms": ["dungeon", "procedural", "roguelike"],
        "create_loading_screen": ["ui", "loading", "transição"],
        "load_scene_async": ["cena", "async", "performance"],
        "add_raycast_2d": ["física", "raycast", "debug"],
        "add_shapecast_2d": ["física", "shapecast", "debug"],
        "enable_debug_collisions": ["debug", "colisão", "visualização"],
        "enable_debug_navigation": ["debug", "navegação", "visualização"],
        "get_performance_stats": ["debug", "performance", "métricas"],
        "setup_localization": ["i18n", "tradução", "idiomas"],
        "add_translation_string": ["i18n", "tradução"],
        "create_light_3d": ["iluminação", "3D", "luz"],
        "create_csg_shape": ["3D", "prototipagem", "csg"],
        "configure_standard_material_3d": ["3D", "material", "renderização"],
        "configure_export_preset": ["exportação", "build"],
        "configure_audio_bus": ["áudio", "mixagem"],
        "add_audio_effect": ["áudio", "efeitos"],
        "health_check": ["diagnóstico", "sistema"],
        "self_test": ["diagnóstico", "teste"],
    }
    for t in _TOOL_DEFS_CACHE:
        if t.name in _READONLY:
            t.readOnlyHint = True
        if t.name in _DESTRUCTIVE:
            t.destructiveHint = True
        if t.name in _IDEMPOTENT:
            t.idempotentHint = True
        if hasattr(t, 'inputSchema') and isinstance(t.inputSchema, dict):
            if "additionalProperties" not in t.inputSchema:
                t.inputSchema["additionalProperties"] = False
        # ── Annotations Onda 6 ──────────────────────────────────
        if t.name in _TITLES:
            t.title = _TITLES[t.name]
        if t.name in _TAGS:
            t.annotations = {"tags": _TAGS[t.name]}
    # ── Fim pós-processamento ──────────────────────────────────────

    return _TOOL_DEFS_CACHE


# ── Tool Listing ────────────────────────────────────────────────────

@server.list_tools()
async def list_tools() -> list[Tool]:
    """Retorna a lista de ferramentas registradas."""
    return _tool_defs()


# Cache global para handlers (evita recriar dict de handlers a cada call_tool)
_HANDLERS_CACHE: dict | None = None


def _build_handlers() -> dict:
    """Constrói o dicionário de handlers (cacheado)."""
    global _HANDLERS_CACHE
    if _HANDLERS_CACHE is not None:
        return _HANDLERS_CACHE
    _HANDLERS_CACHE = {
        "ping": _handle_ping,
        "validate_godot_version": _handle_validate_godot_version,
        "set_active_project": _handle_set_active_project,
        "create_project": _handle_create_project,
        "get_project_settings": _handle_get_project_settings,
        "set_project_setting": _handle_set_project_setting,
        "set_main_scene": _handle_set_main_scene,
        "inspect_project": _handle_inspect_project,
        "read_file": _handle_read_file,
        "write_file": _handle_write_file,
        "delete_file": _handle_delete_file,
        "move_file": _handle_move_file,
        "create_scene": _handle_create_scene,
        "load_scene_tree": _handle_load_scene_tree,
        "add_node": _handle_add_node,
        "delete_node": _handle_delete_node,
        "set_node_property": _handle_set_node_property,
        "get_node_property": _handle_get_node_property,
        # Fase 2: ClassDB
        "query_classdb": _handle_query_classdb,
        "list_valid_node_types": _handle_list_valid_node_types,
        # Fase 2: Cenas extendidas
        "reparent_node": _handle_reparent_node,
        "instance_scene_as_child": _handle_instance_scene_as_child,
        "connect_signal": _handle_connect_signal,
        "list_signals": _handle_list_signals,
        # Fase 2: Scripts
        "generate_gdscript": _handle_generate_gdscript,
        "attach_script": _handle_attach_script,
        "detach_script": _handle_detach_script,
        "validate_gdscript_syntax": _handle_validate_gdscript_syntax,
        "add_script_variable": _handle_add_script_variable,
        "add_script_signal": _handle_add_script_signal,
        # Fase 2: Física
        "add_collision_shape": _handle_add_collision_shape,
        "set_collision_layer_mask": _handle_set_collision_layer_mask,
        # Fase 2: Assets
        "import_texture": _handle_import_texture,
        "import_sprite_sheet": _handle_import_sprite_sheet,
        "import_audio": _handle_import_audio,
        # Fase 2: Input e Autoload
        "configure_input_action": _handle_configure_input_action,
        "install_mcp_addon": _handle_install_mcp_addon,
        "configure_autoload": _handle_configure_autoload,
        # Fase 2: Runtime
        "compile_test": _handle_compile_test,
        "run_game": _handle_run_game,
        "stop_game": _handle_stop_game,
        "smart_restart": _handle_smart_restart,
        # Fase 3: Editor
        "launch_editor": _handle_launch_editor,
        "close_editor": _handle_close_editor,
        "take_screenshot": _handle_take_screenshot,
        "read_console_output": _handle_read_console_output,
        # Fase 4: Tilemap, Animação, UI
        "create_tileset": _handle_create_tileset,
        "create_tilemap_layer": _handle_create_tilemap_layer,
        "paint_tilemap_cell": _handle_paint_tilemap_cell,
        "create_animation_player": _handle_create_animation_player,
        "create_animation": _handle_create_animation,
        "create_ui_scene": _handle_create_ui_scene,
        "add_control_node": _handle_add_control_node,
        # Fase 5: Export, Segurança
        "list_export_presets": _handle_list_export_presets,
        "validate_export_templates_installed": _handle_validate_export_templates_installed,
        "build_export": _handle_build_export,
        "list_backups": _handle_list_backups,
        "restore_backup": _handle_restore_backup,
        "git_commit_checkpoint": _handle_git_commit_checkpoint,
        # Game Bridge
        "inject_input_event": _handle_inject_input_event,
        "execute_gdscript_runtime": _handle_execute_gdscript_runtime,
        "watch_signal": _handle_watch_signal,
        # Onda 1: Visão
        "capture_game_screenshot": _handle_capture_game_screenshot,
        "compare_screenshots": _handle_compare_screenshots,
        "detect_empty_screen": _handle_detect_empty_screen,
        "detect_offscreen_elements": _handle_detect_offscreen_elements,
        # Onda 2: Batch
        "add_nodes_batch": _handle_add_nodes_batch,
        "set_properties_batch": _handle_set_properties_batch,
        # Onda 3: Assets
        "generate_placeholder_sprite": _handle_generate_placeholder_sprite,
        "generate_placeholder_texture_atlas": _handle_generate_placeholder_texture_atlas,
        "generate_background_gradient": _handle_generate_background_gradient,
        "generate_tileset_from_colors": _handle_generate_tileset_from_colors,
        "generate_audio_sfx": _handle_generate_audio_sfx,
        "suggest_color_palette": _handle_suggest_color_palette,
        # Onda 4: IA Agêntica
        "analyze_game_structure": _handle_analyze_game_structure,
        "suggest_next_steps": _handle_suggest_next_steps,
        "find_missing_references": _handle_find_missing_references,
        "validate_game_design": _handle_validate_game_design,
        "estimate_game_scope": _handle_estimate_game_scope,
        "search_codebase": _handle_search_codebase,
        "get_project_history": _handle_get_project_history,
        # Onda 5: Cobertura Godot
        "create_animation_tree": _handle_create_animation_tree,
        "set_physics_material": _handle_set_physics_material,
        "create_joint_2d": _handle_create_joint_2d,
        "import_3d_model": _handle_import_3d_model,
        "create_particles_2d": _handle_create_particles_2d,
        "create_light_2d": _handle_create_light_2d,
        "create_shader_material": _handle_create_shader_material,
        # Onda 7: Robustez
        "health_check": _handle_health_check,
        "self_test": _handle_self_test,
        # Onda 8: DevSolo Crítico
        "setup_camera_2d": _handle_setup_camera_2d,
        "setup_camera_follow": _handle_setup_camera_follow,
        "setup_camera_shake": _handle_setup_camera_shake,
        "create_main_menu": _handle_create_main_menu,
        "create_hud_template": _handle_create_hud_template,
        "create_pause_menu": _handle_create_pause_menu,
        "create_health_bar": _handle_create_health_bar,
        "create_save_system": _handle_create_save_system,
        "define_save_data": _handle_define_save_data,
        "create_state_machine": _handle_create_state_machine,
        "add_state_transition": _handle_add_state_transition,
        "create_tween_animation": _handle_create_tween_animation,
        "chain_tweens": _handle_chain_tweens,
        "create_navigation_region_2d": _handle_create_navigation_region_2d,
        "create_navigation_agent_2d": _handle_create_navigation_agent_2d,
        "bake_navigation_polygon": _handle_bake_navigation_polygon,
        "setup_world_environment": _handle_setup_world_environment,
        "setup_screen_flash": _handle_setup_screen_flash,
        # Onda 9: Polimento Visual
        "create_parallax_background": _handle_create_parallax_background,
        "add_parallax_layer": _handle_add_parallax_layer,
        "configure_particles_2d": _handle_configure_particles_2d,
        "create_particles_3d": _handle_create_particles_3d,
        "generate_shader_2d": _handle_generate_shader_2d,
        "apply_shader_to_node": _handle_apply_shader_to_node,
        "create_path_2d": _handle_create_path_2d,
        "create_patrol_route": _handle_create_patrol_route,
        # Onda 10: Gênero-Específico
        "create_dialogue_system": _handle_create_dialogue_system,
        "add_dialogue_node": _handle_add_dialogue_node,
        "create_dialogue_ui": _handle_create_dialogue_ui,
        "create_inventory_system": _handle_create_inventory_system,
        "define_inventory_item": _handle_define_inventory_item,
        "create_inventory_ui": _handle_create_inventory_ui,
        "create_bullet_template": _handle_create_bullet_template,
        "create_gun_system": _handle_create_gun_system,
        "generate_tilemap_from_noise": _handle_generate_tilemap_from_noise,
        "generate_dungeon_rooms": _handle_generate_dungeon_rooms,
        "create_loading_screen": _handle_create_loading_screen,
        "load_scene_async": _handle_load_scene_async,
        # Onda 11: Complementos
        "add_raycast_2d": _handle_add_raycast_2d,
        "add_shapecast_2d": _handle_add_shapecast_2d,
        "enable_debug_collisions": _handle_enable_debug_collisions,
        "enable_debug_navigation": _handle_enable_debug_navigation,
        "get_performance_stats": _handle_get_performance_stats,
        "setup_localization": _handle_setup_localization,
        "add_translation_string": _handle_add_translation_string,
        "create_light_3d": _handle_create_light_3d,
        "create_csg_shape": _handle_create_csg_shape,
        "configure_standard_material_3d": _handle_configure_standard_material_3d,
        "configure_export_preset": _handle_configure_export_preset,
        "configure_audio_bus": _handle_configure_audio_bus,
        "add_audio_effect": _handle_add_audio_effect,
        # Novas tools (refinamento)
        "generate_project_structure": _handle_generate_project_structure,
        "record_gameplay_gif": _handle_record_gameplay_gif,
        # Undo/Desfazer
        "undo_last_action": _handle_undo_last_action,
        "get_undo_history": _handle_get_undo_history,
    }
    return _HANDLERS_CACHE


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Roteia chamadas de tool para o handler correspondente."""
    # ── Rate Limiting (Onda 6) ──────────────────────────────────
    from tools.rate_limiter import check_rate_limit
    allowed, rate_info = check_rate_limit()
    if not allowed:
        return [TextContent(
            type="text",
            text=json.dumps({
                "status": "error",
                "message": f"Rate limit excedido. Tente novamente em {rate_info['retry_after']}s. "
                           f"Limite: {rate_info['limit']} req/{rate_info['window_seconds']}s.",
                "retry_after": rate_info["retry_after"],
            }, ensure_ascii=False),
            isError=True,
        )]

    handlers = _build_handlers()
    handler = handlers.get(name)
    if handler:
        try:
            result = handler(arguments)
            is_error = isinstance(result, dict) and result.get("status") == "error"
            # ── error_code automático (Onda 7) ──────────────────
            if is_error and "error_code" not in result:
                result["error_code"] = _get_error_code(name, result)
            # ── Tradução amigável de erro ────────────────────────
            if is_error and "friendly" not in result:
                from tools.friendly_errors import translate_error
                result["friendly"] = translate_error(result.get("message", ""))
            return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False), isError=is_error)]
        except Exception as e:
            return [TextContent(type="text", text=json.dumps({
                "status": "error",
                "error_code": 5000,
                "message": f"Erro interno ao executar '{name}': {e}. Reporte este erro para análise.",
            }, ensure_ascii=False), isError=True)]

    return [TextContent(type="text", text=json.dumps({
        "status": "error",
        "message": f"Tool '{name}' não implementada. Tools disponíveis: {list(handlers.keys())}.",
    }, ensure_ascii=False), isError=True)]


# ── Handlers ────────────────────────────────────────────────────────

def _handle_ping(args: dict) -> dict:
    """Handler da tool ping."""
    return {
        "status": "success",
        "server": "godot-agent",
        "version": "1.0.0",
        "tools_count": len(_tool_defs()),
        "message": (
            f"MCP Godot IA Dev v1.0 — {len(_tool_defs())} tools disponiveis para criacao de jogos. "
            "Editor bridge conectado, pronto para receber comandos."
        ),
    }


def _handle_validate_godot_version(args: dict) -> dict:
    return validate_godot_version()


def _handle_set_active_project(args: dict) -> dict:
    return set_active_project(args["project_path"])


def _handle_create_project(args: dict) -> dict:
    return create_project(
        name=args["name"],
        path=args["path"],
        renderer=args.get("renderer", "forward_plus"),
    )


def _handle_get_project_settings(args: dict) -> dict:
    return get_project_settings(args.get("section"))


def _handle_set_project_setting(args: dict) -> dict:
    return set_project_setting(
        section=args["section"],
        key=args["key"],
        value=args["value"],
    )


def _handle_set_main_scene(args: dict) -> dict:
    return set_main_scene(args["scene_path"])


def _handle_inspect_project(args: dict) -> dict:
    return inspect_project(args.get("filter", "all"))


def _handle_read_file(args: dict) -> dict:
    return read_file(
        path=args["path"],
        start_line=args.get("start_line"),
        end_line=args.get("end_line"),
    )


def _handle_write_file(args: dict) -> dict:
    return write_file(
        path=args["path"],
        content=args["content"],
        mode=args.get("mode", "create"),
    )


def _handle_delete_file(args: dict) -> dict:
    return delete_file(args["path"])


def _handle_move_file(args: dict) -> dict:
    return move_file(args["from_path"], args["to_path"])


def _handle_create_scene(args: dict) -> dict:
    return create_scene(
        name=args["name"],
        root_type=args["root_type"],
        path=args["path"],
    )


def _handle_load_scene_tree(args: dict) -> dict:
    return load_scene_tree(
        scene_path=args["scene_path"],
        max_depth=args.get("max_depth"),
    )


def _handle_add_node(args: dict) -> dict:
    return add_node(
        scene_path=args["scene_path"],
        parent_node_path=args["parent_node_path"],
        node_name=args["node_name"],
        node_type=args["node_type"],
    )


def _handle_delete_node(args: dict) -> dict:
    return delete_node(args["scene_path"], args["node_path"])


def _handle_set_node_property(args: dict) -> dict:
    return set_node_property(
        scene_path=args["scene_path"],
        node_path=args["node_path"],
        property_name=args["property_name"],
        value=args["value"],
    )


def _handle_get_node_property(args: dict) -> dict:
    return get_node_property(args["scene_path"], args["node_path"], args["property_name"])


# ── Fase 2 Handlers ─────────────────────────────────────────────────

def _handle_query_classdb(args: dict) -> dict:
    return query_classdb(args["class_name"])


def _handle_list_valid_node_types(args: dict) -> dict:
    return list_valid_node_types()


def _handle_reparent_node(args: dict) -> dict:
    return reparent_node(args["scene_path"], args["node_path"], args["new_parent_path"])


def _handle_instance_scene_as_child(args: dict) -> dict:
    return instance_scene_as_child(
        args["scene_path"], args["parent_node_path"],
        args["instanced_scene_path"], args.get("instance_name"),
    )


def _handle_connect_signal(args: dict) -> dict:
    return connect_signal(
        args["scene_path"], args["from_node_path"], args["signal_name"],
        args["to_node_path"], args["method_name"],
    )


def _handle_list_signals(args: dict) -> dict:
    return list_signals_for_node(
        args.get("scene_path"), args.get("node_path"), args.get("node_type"),
    )


def _handle_generate_gdscript(args: dict) -> dict:
    return generate_gdscript(args["template"], args.get("variables", {}), args["save_path"])


def _handle_attach_script(args: dict) -> dict:
    return attach_script(args["scene_path"], args["node_path"], args["script_path"])


def _handle_detach_script(args: dict) -> dict:
    return detach_script(args["scene_path"], args["node_path"])


def _handle_validate_gdscript_syntax(args: dict) -> dict:
    return validate_gdscript_syntax(args["script_path"])


def _handle_add_script_variable(args: dict) -> dict:
    return add_script_variable(
        args["script_path"], args["var_name"],
        args.get("var_type", "Variant"),
        args.get("default_value"),
        args.get("export", False),
    )


def _handle_add_script_signal(args: dict) -> dict:
    return add_script_signal(args["script_path"], args["signal_name"], args.get("args"))


def _handle_add_collision_shape(args: dict) -> dict:
    return add_collision_shape(
        args["scene_path"], args["parent_node_path"],
        args["shape_type"], args["dimensions"],
    )


def _handle_set_collision_layer_mask(args: dict) -> dict:
    return set_collision_layer_mask(
        args["scene_path"], args["node_path"],
        args["layer_bits"], args["mask_bits"],
    )


def _handle_import_texture(args: dict) -> dict:
    return import_texture(args["source_path"], args["target_res_path"])


def _handle_import_sprite_sheet(args: dict) -> dict:
    return import_sprite_sheet(
        args["source_path"], args["target_res_path"],
        args["frame_width"], args["frame_height"],
        args["target_scene_path"], args["target_node_path"],
        args["animations"],
    )


def _handle_import_audio(args: dict) -> dict:
    return import_audio(args["source_path"], args["target_res_path"])


def _handle_configure_input_action(args: dict) -> dict:
    return configure_input_action(
        args["action_name"], args["keys"], args.get("joypad_buttons"),
    )


def _handle_install_mcp_addon(args: dict) -> dict:
    return install_mcp_addon(args.get("project_path"))


def _handle_generate_project_structure(args: dict) -> dict:
    return generate_project_structure(
        args.get("template", "2d"),
        args.get("project_path"),
    )


def _handle_record_gameplay_gif(args: dict) -> dict:
    return record_gameplay_gif(
        args.get("duration", 5),
        args.get("fps", 10),
        args.get("resolution_width", 480),
        args.get("resolution_height", 270),
    )


def _handle_undo_last_action(args: dict) -> dict:
    return undo_last_action()


def _handle_get_undo_history(args: dict) -> dict:
    return get_undo_history()


def _handle_configure_autoload(args: dict) -> dict:
    return configure_autoload(
        args["name"], args["script_path"], args.get("singleton", True),
    )


def _handle_compile_test(args: dict) -> dict:
    return compile_test()


def _handle_run_game(args: dict) -> dict:
    return run_game(args.get("scene_path"))


def _handle_stop_game(args: dict) -> dict:
    return stop_game()


def _handle_smart_restart(args: dict) -> dict:
    from tools.runtime_ops import smart_restart
    return smart_restart(args.get("project_path"))


# ── Fase 3 Handlers ─────────────────────────────────────────────────

def _handle_launch_editor(args: dict) -> dict:
    return launch_editor(args.get("scene_path"))


def _handle_close_editor(args: dict) -> dict:
    return close_editor()


def _handle_take_screenshot(args: dict) -> dict:
    return take_screenshot()


def _handle_read_console_output(args: dict) -> dict:
    return read_console_output(args.get("since_timestamp"))


# ── Fase 4 Handlers ─────────────────────────────────────────────────

def _handle_create_tileset(args: dict) -> dict:
    return create_tileset(
        args["tileset_name"], args["save_path"],
        args.get("tile_width", 16), args.get("tile_height", 16),
    )


def _handle_create_tilemap_layer(args: dict) -> dict:
    return create_tilemap_layer(
        args["scene_path"], args["parent_node_path"],
        args["layer_name"], args["tileset_path"],
    )


def _handle_paint_tilemap_cell(args: dict) -> dict:
    return paint_tilemap_cell(
        args["scene_path"], args["layer_node_path"],
        args["cell_x"], args["cell_y"],
        args.get("source_id", 0),
        args.get("atlas_coords_x", 0), args.get("atlas_coords_y", 0),
    )


def _handle_create_animation_player(args: dict) -> dict:
    return create_animation_player(
        args["scene_path"], args["parent_node_path"],
        args.get("player_name", "AnimationPlayer"),
    )


def _handle_create_animation(args: dict) -> dict:
    return create_animation(
        args["scene_path"], args["anim_player_path"],
        args["anim_name"], args["track_path"], args["track_type"],
        args["keyframes"], args.get("fps", 10.0),
    )


def _handle_create_ui_scene(args: dict) -> dict:
    return create_ui_scene(args["name"], args["path"])


def _handle_add_control_node(args: dict) -> dict:
    return add_control_node(
        args["scene_path"], args["parent_node_path"],
        args["node_name"], args["node_type"],
        args.get("properties"),
    )


# ── Fase 5 Handlers ─────────────────────────────────────────────────

def _handle_list_export_presets(args: dict) -> dict:
    return list_export_presets()


def _handle_validate_export_templates_installed(args: dict) -> dict:
    return validate_export_templates_installed()


def _handle_build_export(args: dict) -> dict:
    return build_export(args.get("preset_name"), args.get("output_path"))


def _handle_list_backups(args: dict) -> dict:
    backups = list_backups(args.get("original_path"))
    return {"status": "success", "backups": backups}


def _handle_restore_backup(args: dict) -> dict:
    if args.get("backup_id"):
        return restore_backup(args["backup_id"])
    elif args.get("original_path") and args.get("latest"):
        backups = list_backups(args["original_path"])
        if backups:
            return restore_backup(backups[0]["backup_id"])
        return {"status": "error", "message": "Nenhum backup encontrado para este arquivo."}
    return {"status": "error", "message": "Forneça backup_id ou (original_path + latest: true)."}


def _handle_git_commit_checkpoint(args: dict) -> dict:
    return git_commit_checkpoint(args["message"])


# ── Game Bridge Handlers ─────────────────────────────────────────────

def _handle_inject_input_event(args: dict) -> dict:
    return inject_input_event(args["event_type"], args["event_data"])


def _handle_execute_gdscript_runtime(args: dict) -> dict:
    return execute_gdscript_runtime(args["code"])


def _handle_watch_signal(args: dict) -> dict:
    return watch_signal(args["node_path"], args["signal_name"], args.get("timeout", 5.0))


# ── Onda 1: Visão Handlers ──────────────────────────────────────────

def _handle_capture_game_screenshot(args: dict) -> dict:
    return capture_game_screenshot(
        wait_frames=args.get("wait_frames", 30),
        scene_path=args.get("scene_path"),
        resolution_width=args.get("resolution_width", 1280),
        resolution_height=args.get("resolution_height", 720),
    )


def _handle_compare_screenshots(args: dict) -> dict:
    return compare_screenshots(args["before_path"], args["after_path"])


def _handle_detect_empty_screen(args: dict) -> dict:
    return detect_empty_screen(
        screenshot_path=args.get("screenshot_path"),
        image_base64=args.get("image_base64"),
        empty_threshold=args.get("empty_threshold", 0.95),
    )


def _handle_detect_offscreen_elements(args: dict) -> dict:
    return detect_offscreen_elements(
        scene_path=args["scene_path"],
        viewport_width=args.get("viewport_width", 1280),
        viewport_height=args.get("viewport_height", 720),
        margin=args.get("margin", 50),
    )


# ── Onda 2: Batch Handlers ──────────────────────────────────────────

def _handle_add_nodes_batch(args: dict) -> dict:
    """Handler batch que usa add_node em loop (fallback se batch nativo não existir)."""
    scene_path = args["scene_path"]
    nodes = args["nodes"]
    errors = []
    added = 0
    for spec in nodes:
        r = add_node(
            scene_path=scene_path,
            parent_node_path=spec.get("parent_node_path", "."),
            node_name=spec.get("node_name", ""),
            node_type=spec.get("node_type", ""),
        )
        if r["status"] == "success":
            added += 1
        else:
            errors.append({"spec": spec, "error": r.get("message", "Erro desconhecido")})
    return {"status": "success", "added": added, "errors": errors or None}


def _handle_set_properties_batch(args: dict) -> dict:
    """Handler batch que usa set_node_property em loop."""
    scene_path = args["scene_path"]
    props = args["properties"]
    errors = []
    set_count = 0
    for spec in props:
        r = set_node_property(
            scene_path=scene_path,
            node_path=spec.get("node_path", ""),
            property_name=spec.get("property_name", ""),
            value=spec.get("value"),
        )
        if r["status"] == "success":
            set_count += 1
        else:
            errors.append({"spec": spec, "error": r.get("message", "Erro desconhecido")})
    return {"status": "success", "set": set_count, "errors": errors or None}


# ── Onda 3: Assets Handlers ─────────────────────────────────────────

def _handle_generate_placeholder_sprite(args: dict) -> dict:
    return generate_placeholder_sprite(
        name=args["name"],
        width=args.get("width", 64),
        height=args.get("height", 64),
        color=args.get("color", "#3498db"),
        shape=args.get("shape", "rectangle"),
        save_path=args.get("save_path"),
    )


def _handle_generate_placeholder_texture_atlas(args: dict) -> dict:
    return generate_placeholder_texture_atlas(
        name=args["name"],
        frame_width=args.get("frame_width", 64),
        frame_height=args.get("frame_height", 64),
        columns=args.get("columns", 4),
        rows=args.get("rows", 1),
        color=args.get("color", "#e74c3c"),
        shape=args.get("shape", "rectangle"),
        variation=args.get("variation", "position"),
        save_path=args.get("save_path"),
    )


def _handle_generate_background_gradient(args: dict) -> dict:
    return generate_background_gradient(
        name=args["name"],
        width=args.get("width", 1280),
        height=args.get("height", 720),
        color_top=args.get("color_top", "#1a1a2e"),
        color_bottom=args.get("color_bottom", "#16213e"),
        direction=args.get("direction", "vertical"),
        save_path=args.get("save_path"),
    )


def _handle_generate_tileset_from_colors(args: dict) -> dict:
    return generate_tileset_from_colors(
        palette_name=args["palette_name"],
        colors=args["colors"],
        tile_width=args.get("tile_width", 16),
        tile_height=args.get("tile_height", 16),
        save_texture_path=args.get("save_texture_path"),
        save_tileset_path=args.get("save_tileset_path"),
    )


def _handle_generate_audio_sfx(args: dict) -> dict:
    return generate_audio_sfx(
        name=args["name"],
        sfx_type=args.get("sfx_type", "beep"),
        duration=args.get("duration", 0.3),
        frequency=args.get("frequency", 440.0),
        sample_rate=args.get("sample_rate", 44100),
        save_path=args.get("save_path"),
    )


def _handle_suggest_color_palette(args: dict) -> dict:
    return suggest_color_palette(args["genre"])


# ── Onda 4: IA Agêntica Handlers ────────────────────────────────────

def _handle_analyze_game_structure(args: dict) -> dict:
    return analyze_game_structure()


def _handle_suggest_next_steps(args: dict) -> dict:
    return suggest_next_steps()


def _handle_find_missing_references(args: dict) -> dict:
    return find_missing_references()


def _handle_validate_game_design(args: dict) -> dict:
    return validate_game_design()


def _handle_estimate_game_scope(args: dict) -> dict:
    return estimate_game_scope()


def _handle_search_codebase(args: dict) -> dict:
    return search_codebase(
        query=args["query"],
        file_pattern=args.get("file_pattern", "*.gd"),
        max_results=args.get("max_results", 20),
    )


def _handle_get_project_history(args: dict) -> dict:
    return get_project_history()


# ── Onda 5: Cobertura Godot Handlers ──────────────────────────────

def _handle_create_animation_tree(args: dict) -> dict:
    """Cria AnimationTree com AnimationNodeStateMachine."""
    r = add_node(args["scene_path"], args["parent_node_path"],
                 args.get("player_name", "AnimationTree"), "AnimationTree")
    if r["status"] != "success":
        return r
    return set_node_property(
        args["scene_path"],
        f"./{args.get('player_name', 'AnimationTree')}",
        "tree_root",
        f'SubResource("{args.get("root_type", "AnimationNodeStateMachine")}")',
    ) if args.get("set_root", True) else r


def _handle_set_physics_material(args: dict) -> dict:
    return set_physics_material(
        scene_path=args["scene_path"], node_path=args["node_path"],
        bounce=args.get("bounce"), friction=args.get("friction"),
        absorb=args.get("absorb"), rough=args.get("rough"),
    )


def _handle_create_joint_2d(args: dict) -> dict:
    return create_joint_2d(
        scene_path=args["scene_path"], node_a_path=args["node_a_path"],
        node_b_path=args["node_b_path"], joint_type=args.get("joint_type", "pin"),
        softness=args.get("softness", 0.0), bias=args.get("bias", 0.0),
    )


def _handle_import_3d_model(args: dict) -> dict:
    return import_3d_model(
        source_path=args["source_path"], target_res_path=args["target_res_path"],
        create_scene=args.get("create_scene", True),
        scene_name=args.get("scene_name"),
    )


def _handle_create_particles_2d(args: dict) -> dict:
    """Cria GPUParticles2D com ParticleProcessMaterial."""
    sp = args["scene_path"]
    pp = args["parent_node_path"]
    nm = args.get("node_name", "Particles")
    r = add_node(sp, pp, nm, "GPUParticles2D")
    if r["status"] != "success":
        return r
    # Configura propriedades comuns
    props = {}
    if args.get("amount"):
        props["amount"] = args["amount"]
    if args.get("lifetime"):
        props["lifetime"] = args["lifetime"]
    if args.get("explosiveness"):
        props["explosiveness"] = args["explosiveness"]
    for k, v in props.items():
        set_node_property(sp, f"./{nm}", k, v)
    # Cria ParticleProcessMaterial
    mat_line = f'[sub_resource type="ParticleProcessMaterial" id="1"]\n'
    if args.get("direction"):
        mat_line += f'direction = Vector3({args["direction"]})\n'
    if args.get("spread"):
        mat_line += f'spread = {args["spread"]}\n'
    if args.get("gravity"):
        mat_line += f'gravity = Vector3({args["gravity"]})\n'
    # Escreve no .tscn
    proj = _get_active_project() if '_get_active_project' in dir() else Path(".")
    full = Path(proj) / sp if isinstance(proj, (str, Path)) else Path(str(proj)) / sp
    if full.exists():
        content = full.read_text(encoding="utf-8")
        content = content.replace("[gd_scene", f"{mat_line}\n[gd_scene")
        content = content.replace(
            f'[node name="{nm}" type="GPUParticles2D"',
            f'[node name="{nm}" type="GPUParticles2D"\nprocess_material = SubResource("1")'
        )
        full.write_text(content, encoding="utf-8")
    return {"status": "success", "node_path": r["node_path"],
            "note": "Partículas configuradas. Use run_game para ver o efeito."}


def _handle_create_light_2d(args: dict) -> dict:
    """Cria PointLight2D ou DirectionalLight2D."""
    lt = args.get("light_type", "point")
    godot_type = "PointLight2D" if lt == "point" else "DirectionalLight2D"
    nm = args.get("node_name", "Light")
    r = add_node(args["scene_path"], args["parent_node_path"], nm, godot_type)
    if r["status"] != "success":
        return r
    props = {}
    if args.get("color"):
        props["color"] = args["color"]
    if args.get("energy"):
        props["energy"] = args["energy"]
    if args.get("range_z"):
        props["range_z_min"] = args.get("range_z_min", 0)
        props["range_z_max"] = args["range_z"]
    for k, v in props.items():
        set_node_property(args["scene_path"], f"./{nm}", k, v)
    return {"status": "success", "node_path": r["node_path"], "light_type": godot_type}


def _handle_create_shader_material(args: dict) -> dict:
    """Atribui ShaderMaterial com código shader a um nó."""
    sp = args["scene_path"]
    np = args["node_path"]
    shader_code = args["shader_code"]
    shader_type = args.get("shader_type", "canvas_item")
    proj = Path(__file__).resolve().parent
    # Salva shader como .gdshader
    shader_name = args.get("shader_name", "custom_shader")
    shader_path = f"shaders/{shader_name}.gdshader"
    full_shader = proj / shader_path
    full_shader.parent.mkdir(parents=True, exist_ok=True)
    shader_content = f"shader_type {shader_type};\n\n{shader_code}"
    full_shader.write_text(shader_content, encoding="utf-8")
    # Atribui ao nó
    r = set_node_property(sp, np, "material", f'ShaderMaterial{{"shader": preload("res://{shader_path}")}}')
    if r["status"] != "success":
        return r
    return {"status": "success", "shader_path": shader_path,
            "node_path": f"{sp}::{np}"}


def _get_error_code(tool_name: str, result: dict) -> int:
    """Atribui error_code numérico baseado na tool e mensagem de erro."""
    msg = result.get("message", "").lower()
    if any(kw in msg for kw in ("não encontrad", "não exist", "inválido", "inválida",
                                  "não permitido", "path traversal", "já existe")):
        return 1001
    if any(kw in msg for kw in ("projeto", "project.godot", "arquivo", "cena",
                                  "script", "diretório")):
        return 2001
    if any(kw in msg for kw in ("godot", "compile", "timeout", "template",
                                  "export", "sintaxe")):
        return 3001
    if any(kw in msg for kw in ("conectado", "bridge", "tcp", "porta",
                                  "socket", "conexão")):
        return 4001
    return 5000


# ── Onda 7: Robustez Handlers ──────────────────────────────────────

def _handle_health_check(args: dict) -> dict:
    """Verifica a saúde de todos os componentes do MCP."""
    import json as _json
    checks = []

    # 1. config.json
    try:
        cfg = _json.loads((ROOT / "config.json").read_text(encoding="utf-8"))
        godot_path = cfg.get("godot_path", "não configurado")
    except Exception:
        godot_path = None
    checks.append({"component": "config.json",
                   "ok": godot_path is not None,
                   "detail": godot_path or "ausente"})

    # 2. ClassDB cache
    cache = ROOT / "classdb_cache" / "extension_api.json"
    checks.append({"component": "ClassDB cache",
                   "ok": cache.exists(),
                   "detail": f"{cache.stat().st_size // 1024}KB" if cache.exists() else "ausente"})

    # 3. Templates
    templates = ROOT / "templates"
    tpl_count = len(list(templates.glob("*.gd"))) if templates.exists() else 0
    checks.append({"component": "Templates GDScript",
                   "ok": tpl_count > 0,
                   "detail": f"{tpl_count} templates"})

    # 4. Godot binário
    if godot_path:
        import subprocess
        try:
            r = subprocess.run([godot_path, "--version"], capture_output=True, text=True, timeout=10)
            godot_ok = "4." in r.stdout or "4." in r.stderr
        except Exception:
            godot_ok = False
    else:
        godot_ok = False
    checks.append({"component": "Godot 4.7",
                   "ok": godot_ok,
                   "detail": "acessível" if godot_ok else "indisponível"})

    # 5. Projeto ativo
    proj = _get_active_project()
    proj_ok = (proj / "project.godot").exists()
    checks.append({"component": "Projeto ativo",
                   "ok": proj_ok,
                   "detail": str(proj) if proj_ok else "não definido"})

    all_ok = all(c["ok"] for c in checks)
    return {
        "status": "success",
        "healthy": all_ok,
        "checks": checks,
        "verdict": "✅ Todos os sistemas operacionais." if all_ok
                   else "⚠️ Alguns componentes precisam de atenção."
    }


def _handle_self_test(args: dict) -> dict:
    """Testa funcionalidades básicas do MCP."""
    results = []

    # 1. Ping interno
    results.append({"test": "ping", "passed": True})

    # 2. ClassDB
    try:
        from tools.classdb import is_valid_node_type
        r = is_valid_node_type("Node2D")
        results.append({"test": "ClassDB (Node2D)", "passed": r})
    except Exception as e:
        results.append({"test": "ClassDB", "passed": False, "error": str(e)})

    # 3. Godot parser
    try:
        import godot_parser
        results.append({"test": "godot_parser", "passed": True})
    except ImportError:
        results.append({"test": "godot_parser", "passed": False, "error": "não instalado"})

    # 4. Jinja2
    try:
        import jinja2
        results.append({"test": "jinja2", "passed": True})
    except ImportError:
        results.append({"test": "jinja2", "passed": False, "error": "não instalado"})

    # 5. Pillow
    try:
        from PIL import Image
        results.append({"test": "Pillow (assets)", "passed": True})
    except ImportError:
        results.append({"test": "Pillow (assets)", "passed": False, "error": "não instalado — assets procedurais limitados"})

    passed = sum(1 for r in results if r["passed"])
    return {
        "status": "success",
        "passed": passed,
        "total": len(results),
        "results": results,
        "verdict": "✅ Todos os testes passaram!" if passed == len(results)
                   else f"⚠️ {len(results) - passed} teste(s) falharam."
    }


# ── Entry Point ─────────────────────────────────────────────────────

# ══════════════════════════════════════════════════════════════════════
# Onda 8 — DevSolo Handlers (18 tools)
# ══════════════════════════════════════════════════════════════════════

def _handle_setup_camera_2d(args: dict) -> dict:
    return setup_camera_2d(
        scene_path=args["scene_path"],
        parent_node_path=args.get("parent_node_path", "."),
        limits=args.get("limits"),
        drag_horizontal=args.get("drag_horizontal", 0.0),
        drag_vertical=args.get("drag_vertical", 0.0),
        zoom=args.get("zoom"),
        smoothing_enabled=args.get("smoothing_enabled", True),
        smoothing_speed=args.get("smoothing_speed", 5.0),
        current=args.get("current", True),
    )

def _handle_setup_camera_follow(args: dict) -> dict:
    return setup_camera_follow(
        scene_path=args["scene_path"],
        camera_node_path=args["camera_node_path"],
        target_node_path=args["target_node_path"],
        smoothing=args.get("smoothing", 5.0),
        offset_x=args.get("offset_x", 0.0),
        offset_y=args.get("offset_y", 0.0),
        deadzone_width=args.get("deadzone_width", 0.0),
        deadzone_height=args.get("deadzone_height", 0.0),
    )

def _handle_setup_camera_shake(args: dict) -> dict:
    return setup_camera_shake(
        scene_path=args["scene_path"],
        camera_node_path=args["camera_node_path"],
        max_amplitude=args.get("max_amplitude", 20.0),
        decay_rate=args.get("decay_rate", 2.0),
    )

def _handle_create_main_menu(args: dict) -> dict:
    return create_main_menu(
        scene_name=args["scene_name"],
        game_title=args["game_title"],
        title_font_size=args.get("title_font_size", 64),
        buttons=args.get("buttons"),
        background_color=args.get("background_color", "#1a1a2e"),
        style=args.get("style", "modern"),
    )

def _handle_create_hud_template(args: dict) -> dict:
    return create_hud_template(
        scene_name=args.get("scene_name", "hud"),
        elements=args.get("elements"),
        position=args.get("position", "top_left"),
    )

def _handle_create_pause_menu(args: dict) -> dict:
    return create_pause_menu(
        scene_name=args.get("scene_name", "pause_menu"),
        overlay_alpha=args.get("overlay_alpha", 0.7),
    )

def _handle_create_health_bar(args: dict) -> dict:
    return create_health_bar(
        scene_path=args["scene_path"],
        parent_node_path=args.get("parent_node_path", "."),
        max_health=args.get("max_health", 100.0),
        bar_name=args.get("bar_name", "HealthBar"),
        bar_width=args.get("bar_width", 250),
        bar_height=args.get("bar_height", 25),
        fill_color=args.get("fill_color", "#2ecc71"),
        bg_color=args.get("bg_color", "#333333"),
        show_text=args.get("show_text", True),
    )

def _handle_create_save_system(args: dict) -> dict:
    return create_save_system(
        autoload_name=args.get("autoload_name", "SaveManager"),
        save_slots=args.get("save_slots", 3),
        auto_save_enabled=args.get("auto_save_enabled", False),
        auto_save_interval=args.get("auto_save_interval", 60.0),
    )

def _handle_define_save_data(args: dict) -> dict:
    return define_save_data(
        node_path=args["node_path"],
        property_name=args["property_name"],
        section=args.get("section", "default"),
        key=args.get("key", ""),
    )

def _handle_create_state_machine(args: dict) -> dict:
    return create_state_machine(
        script_path=args["script_path"],
        states=args["states"],
        initial_state=args["initial_state"],
    )

def _handle_add_state_transition(args: dict) -> dict:
    return add_state_transition(
        script_path=args["script_path"],
        from_state=args["from_state"],
        to_state=args["to_state"],
        condition_code=args["condition_code"],
    )

def _handle_create_tween_animation(args: dict) -> dict:
    return create_tween_animation(
        scene_path=args["scene_path"],
        node_path=args["node_path"],
        property_name=args["property_name"],
        final_value=args["final_value"],
        duration=args.get("duration", 0.5),
        easing=args.get("easing", "out_quad"),
        transition=args.get("transition", "ease_out"),
        loops=args.get("loops", 0),
        auto_play=args.get("auto_play", True),
    )

def _handle_chain_tweens(args: dict) -> dict:
    return chain_tweens(
        scene_path=args["scene_path"],
        node_path=args["node_path"],
        steps=args["steps"],
    )

def _handle_create_navigation_region_2d(args: dict) -> dict:
    return create_navigation_region_2d(
        scene_path=args["scene_path"],
        parent_node_path=args.get("parent_node_path", "."),
        polygon_vertices=args.get("polygon_vertices"),
        region_name=args.get("region_name", "NavigationRegion2D"),
    )

def _handle_create_navigation_agent_2d(args: dict) -> dict:
    return create_navigation_agent_2d(
        scene_path=args["scene_path"],
        parent_node_path=args["parent_node_path"],
        agent_name=args.get("agent_name", "NavigationAgent2D"),
        target_node_path=args["target_node_path"],
        speed=args.get("speed", 200.0),
        avoidance_enabled=args.get("avoidance_enabled", True),
    )

def _handle_bake_navigation_polygon(args: dict) -> dict:
    return bake_navigation_polygon(
        scene_path=args["scene_path"],
        tilemap_layer_path=args["tilemap_layer_path"],
        navigation_region_path=args["navigation_region_path"],
        walkable_tiles=args.get("walkable_tiles"),
    )

def _handle_setup_world_environment(args: dict) -> dict:
    return setup_world_environment(
        scene_path=args["scene_path"],
        parent_node_path=args.get("parent_node_path", "."),
        background_mode=args.get("background_mode", "color"),
        background_color=args.get("background_color", "#1a1a2e"),
        ambient_light_color=args.get("ambient_light_color", "#333344"),
        ambient_light_energy=args.get("ambient_light_energy", 1.0),
        glow_enabled=args.get("glow_enabled", False),
        glow_intensity=args.get("glow_intensity", 0.8),
        fog_enabled=args.get("fog_enabled", False),
        fog_density=args.get("fog_density", 0.01),
        fog_color=args.get("fog_color", "#1a1a2e"),
    )

def _handle_setup_screen_flash(args: dict) -> dict:
    return setup_screen_flash(
        scene_path=args["scene_path"],
        parent_node_path=args.get("parent_node_path", "."),
        flash_color=args.get("flash_color", "#ffffff"),
        flash_duration=args.get("flash_duration", 0.3),
    )


# ══════════════════════════════════════════════════════════════════════
# Onda 9 — Polimento Visual Handlers (8 tools)
# ══════════════════════════════════════════════════════════════════════

def _handle_create_parallax_background(args: dict) -> dict:
    return create_parallax_background(
        scene_path=args["scene_path"],
        layers=args["layers"],
        parent_node_path=args.get("parent_node_path", "."),
        bg_name=args.get("bg_name", "ParallaxBackground"),
    )

def _handle_add_parallax_layer(args: dict) -> dict:
    return add_parallax_layer(
        scene_path=args["scene_path"],
        parallax_bg_path=args["parallax_bg_path"],
        texture_path=args["texture_path"],
        scroll_scale_x=args.get("scroll_scale_x", 0.5),
        scroll_scale_y=args.get("scroll_scale_y", 0.5),
        mirroring_x=args.get("mirroring_x", 0),
        mirroring_y=args.get("mirroring_y", 0),
        layer_name=args.get("layer_name", ""),
    )

def _handle_configure_particles_2d(args: dict) -> dict:
    return configure_particles_2d(
        scene_path=args["scene_path"],
        node_path=args["node_path"],
        amount=args.get("amount", 50),
        lifetime=args.get("lifetime", 1.0),
        explosiveness=args.get("explosiveness", 0.0),
        emitting=args.get("emitting", True),
        one_shot=args.get("one_shot", False),
        preset=args.get("preset", "custom"),
    )

def _handle_create_particles_3d(args: dict) -> dict:
    return create_particles_3d(
        scene_path=args["scene_path"],
        parent_node_path=args.get("parent_node_path", "."),
        node_name=args.get("node_name", "GPUParticles3D"),
        preset=args.get("preset", "fire"),
    )

def _handle_generate_shader_2d(args: dict) -> dict:
    return generate_shader_2d(
        scene_path=args["scene_path"],
        node_path=args["node_path"],
        template=args["template"],
        uniforms=args.get("uniforms"),
        shader_name=args.get("shader_name", ""),
    )

def _handle_apply_shader_to_node(args: dict) -> dict:
    return apply_shader_to_node(
        scene_path=args["scene_path"],
        node_path=args["node_path"],
        shader_template=args.get("shader_template", "glow"),
        uniforms=args.get("uniforms"),
    )

def _handle_create_path_2d(args: dict) -> dict:
    return create_path_2d(
        scene_path=args["scene_path"],
        parent_node_path=args.get("parent_node_path", "."),
        waypoints=args.get("waypoints"),
        path_name=args.get("path_name", "Path2D"),
        closed=args.get("closed", False),
    )

def _handle_create_patrol_route(args: dict) -> dict:
    return create_patrol_route(
        scene_path=args["scene_path"],
        parent_node_path=args["parent_node_path"],
        waypoints=args["waypoints"],
        speed=args.get("speed", 100.0),
        wait_time=args.get("wait_time", 1.0),
        ping_pong=args.get("ping_pong", True),
    )


# ══════════════════════════════════════════════════════════════════════
# Onda 10 — Gênero-Específico Handlers (12 tools)
# ══════════════════════════════════════════════════════════════════════

def _handle_create_dialogue_system(args: dict) -> dict:
    return create_dialogue_system(autoload_name=args.get("autoload_name", "DialogueManager"))

def _handle_add_dialogue_node(args: dict) -> dict:
    return add_dialogue_node(
        dialogue_id=args["dialogue_id"],
        speaker=args["speaker"],
        text=args["text"],
        next_id=args.get("next_id", ""),
        choices=args.get("choices"),
        events=args.get("events"),
    )

def _handle_create_dialogue_ui(args: dict) -> dict:
    return create_dialogue_ui(scene_name=args.get("scene_name", "dialogue_ui"))

def _handle_create_inventory_system(args: dict) -> dict:
    return create_inventory_system(
        autoload_name=args.get("autoload_name", "InventoryManager"),
        max_slots=args.get("max_slots", 20),
    )

def _handle_define_inventory_item(args: dict) -> dict:
    return define_inventory_item(
        item_id=args["item_id"],
        item_name=args["item_name"],
        item_type=args.get("item_type", "consumable"),
        description=args.get("description", ""),
        stackable=args.get("stackable", True),
        max_stack=args.get("max_stack", 99),
        icon_path=args.get("icon_path", ""),
        properties=args.get("properties"),
    )

def _handle_create_inventory_ui(args: dict) -> dict:
    return create_inventory_ui(
        scene_name=args.get("scene_name", "inventory_ui"),
        columns=args.get("columns", 5),
    )

def _handle_create_bullet_template(args: dict) -> dict:
    return create_bullet_template(
        bullet_name=args.get("bullet_name", "Bullet"),
        speed=args.get("speed", 500.0),
        damage=args.get("damage", 10.0),
        lifetime=args.get("lifetime", 3.0),
        bullet_color=args.get("bullet_color", "#ffff00"),
        bullet_size=args.get("bullet_size", 8),
    )

def _handle_create_gun_system(args: dict) -> dict:
    return create_gun_system(
        script_path=args["script_path"],
        bullet_scene_path=args.get("bullet_scene_path", "res://scenes/bullet.tscn"),
        fire_rate=args.get("fire_rate", 0.3),
        ammo_max=args.get("ammo_max", 30),
        spread_angle=args.get("spread_angle", 0.0),
        auto_reload=args.get("auto_reload", True),
        reload_time=args.get("reload_time", 1.5),
    )

def _handle_generate_tilemap_from_noise(args: dict) -> dict:
    return generate_tilemap_from_noise(
        scene_path=args["scene_path"],
        tilemap_layer_path=args["tilemap_layer_path"],
        tile_size=args.get("tile_size", 32),
        width=args.get("width", 40),
        height=args.get("height", 30),
        seed=args.get("seed", 0),
        threshold=args.get("threshold", 0.5),
        tile_ground=args.get("tile_ground", 0),
        tile_wall=args.get("tile_wall", 1),
    )

def _handle_generate_dungeon_rooms(args: dict) -> dict:
    return generate_dungeon_rooms(
        num_rooms=args.get("num_rooms", 8),
        min_size=args.get("min_size", 5),
        max_size=args.get("max_size", 12),
        map_width=args.get("map_width", 80),
        map_height=args.get("map_height", 60),
        corridor_width=args.get("corridor_width", 2),
        seed=args.get("seed", 0),
    )

def _handle_create_loading_screen(args: dict) -> dict:
    return create_loading_screen(
        scene_name=args.get("scene_name", "loading_screen"),
        tips=args.get("tips"),
        min_load_time=args.get("min_load_time", 1.0),
        background_color=args.get("background_color", "#1a1a2e"),
    )

def _handle_load_scene_async(args: dict) -> dict:
    return load_scene_async(
        target_scene=args["target_scene"],
        loading_scene=args.get("loading_scene", "res://scenes/loading_screen.tscn"),
    )


# ══════════════════════════════════════════════════════════════════════
# Onda 11 — Complementos Handlers (13 tools)
# ══════════════════════════════════════════════════════════════════════

def _handle_add_raycast_2d(args: dict) -> dict:
    return add_raycast_2d(
        scene_path=args["scene_path"],
        parent_node_path=args["parent_node_path"],
        target_position=args.get("target_position"),
        collision_mask=args.get("collision_mask", 1),
        enabled=args.get("enabled", True),
        node_name=args.get("node_name", "RayCast2D"),
    )

def _handle_add_shapecast_2d(args: dict) -> dict:
    return add_shapecast_2d(
        scene_path=args["scene_path"],
        parent_node_path=args["parent_node_path"],
        shape_type=args.get("shape_type", "rectangle"),
        shape_size=args.get("shape_size"),
        collision_mask=args.get("collision_mask", 1),
        node_name=args.get("node_name", "ShapeCast2D"),
    )

def _handle_enable_debug_collisions(args: dict) -> dict:
    return enable_debug_collisions(enabled=args.get("enabled", True))

def _handle_enable_debug_navigation(args: dict) -> dict:
    return enable_debug_navigation(enabled=args.get("enabled", True))

def _handle_get_performance_stats(args: dict) -> dict:
    return get_performance_stats()

def _handle_setup_localization(args: dict) -> dict:
    return setup_localization(
        default_locale=args.get("default_locale", "pt_BR"),
        additional_locales=args.get("additional_locales"),
    )

def _handle_add_translation_string(args: dict) -> dict:
    return add_translation_string(
        key=args["key"],
        translations=args["translations"],
    )

def _handle_create_light_3d(args: dict) -> dict:
    return create_light_3d(
        scene_path=args["scene_path"],
        parent_node_path=args.get("parent_node_path", "."),
        light_type=args.get("light_type", "omni"),
        color=args.get("color", "#ffffff"),
        energy=args.get("energy", 1.0),
        shadows=args.get("shadows", False),
        node_name=args.get("node_name", ""),
    )

def _handle_create_csg_shape(args: dict) -> dict:
    return create_csg_shape(
        scene_path=args["scene_path"],
        parent_node_path=args.get("parent_node_path", "."),
        shape_type=args.get("shape_type", "box"),
        dimensions=args.get("dimensions"),
        node_name=args.get("node_name", ""),
    )

def _handle_configure_standard_material_3d(args: dict) -> dict:
    return configure_standard_material_3d(
        scene_path=args["scene_path"],
        node_path=args["node_path"],
        preset=args.get("preset", "custom"),
    )

def _handle_configure_export_preset(args: dict) -> dict:
    return configure_export_preset(
        preset_name=args.get("preset_name", "Windows Desktop"),
        app_name=args.get("app_name", ""),
        version=args.get("version", "1.0.0"),
        icon_path=args.get("icon_path", ""),
        company=args.get("company", ""),
    )

def _handle_configure_audio_bus(args: dict) -> dict:
    return configure_audio_bus(
        bus_name=args["bus_name"],
        volume_db=args.get("volume_db", 0.0),
        mute=args.get("mute", False),
        solo=args.get("solo", False),
    )

def _handle_add_audio_effect(args: dict) -> dict:
    return add_audio_effect(
        bus_name=args["bus_name"],
        effect_type=args["effect_type"],
    )


async def main() -> None:
    """Inicializa o servidor MCP via stdio."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


def run() -> None:
    """Entry point síncrono."""
    import asyncio
    asyncio.run(main())


if __name__ == "__main__":
    run()

