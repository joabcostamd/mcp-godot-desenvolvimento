"""server.py — MCP Server godot-mcp-agent v3.0.

Servidor MCP via stdio com 134 ferramentas para criacao e gestao
de projetos Godot 4.7. A IA consumidora (DeepSeek V4 Flash/Pro) chama as
ferramentas para construir jogos a partir de linguagem natural.

Cobre 12 Ondas de desenvolvimento: projeto, arquivo, cena, scripts,
fisica, assets, runtime, editor, tilemap, animacao, UI, export,
seguranca, game bridge, visao, batch, assets procedurais, IA agentica,
DevSolo (camera, navegacao, save, UI, dialogo, inventario, armas,
procedural, shaders, 3D, audio, exportacao, debug, localizacao).
"""

import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool, Resource, ResourceTemplate

# ══════════════════════════════════════════════════════════════
# PATCH 17: Curadoria de Toolset (--toolsets)
# ══════════════════════════════════════════════════════════════

TOOLSETS = {
    "core": [
        "ping", "health_check", "self_test", "bootstrap_godot_mcp",
        "read_file", "write_file", "safe_write_gdscript",
        "compile_test", "run_game", "stop_game", "smart_restart",
        "git_commit_checkpoint",
    ],
    "scene_ops": [
        "scene_manage", "node_manage",
    ],
    "script_ops": [
        "script_manage", "safe_write_gdscript", "validate_gdscript_syntax",
        "gdscript_diagnostics", "gdscript_references", "gdscript_definition",
    ],
    "test_ops": [
        "run_gut_tests", "effect_probe", "godot_exec",
        "get_runtime_state_digest", "capture_runtime_errors",
    ],
    "runtime_ops": [
        "run_game", "stop_game", "smart_restart", "compile_test",
        "execute_gdscript_runtime", "capture_game_screenshot",
        "godot_screenshot", "godot_runtime_info",
        "godot_custom_command", "godot_list_custom_commands",
        "godot_run_project", "godot_stop_project", "godot_wait_for_bridge",
    ],
    "git_ops": [
        "git_commit_checkpoint", "safety_manage",
    ],
    "refs_ops": [
        "find_missing_references", "search_codebase",
    ],
    "asset_ops": [
        "asset_manage", "generate_placeholder_sprite",
        "generate_game_art", "generate_game_art_flux",
        "import_texture", "import_sprite_sheet",
    ],
    "design_ops": [
        "analyze_game_structure", "suggest_next_steps",
        "validate_game_design", "estimate_game_scope",
        "project_status", "create_entity",
        "godot_class_ref",
    ],
    "ui_ops": [
        "ui_manage", "create_main_menu", "create_hud_template",
        "create_pause_menu", "create_health_bar",
    ],
}

def parse_toolset_arg() -> set[str] | None:
    """Parse --toolsets argument. Returns None if all tools should be enabled."""
    import argparse
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--toolsets", default="all", type=str)
    args, _ = parser.parse_known_args()

    if args.toolsets.strip().lower() == "all":
        return None  # None = no filtering, all tools enabled

    enabled_sets = [t.strip() for t in args.toolsets.split(",")]
    enabled_tools: set[str] = set()
    for name in enabled_sets:
        if name not in TOOLSETS:
            print(f"Aviso: toolset desconhecido ignorado: {name}", file=sys.stderr)
            continue
        enabled_tools.update(TOOLSETS[name])
    return enabled_tools

# Resolve toolsets uma vez no import
_ENABLED_TOOLS: set[str] | None = parse_toolset_arg()
if _ENABLED_TOOLS is not None:
    print(f"[MCP] Toolsets ativos: {sorted(_ENABLED_TOOLS)}", file=sys.stderr)

# ── PATCH 12: Runtime Bridge ─────────────────────────────────
from runtime_bridge_client import send_bridge_command, BridgeUnavailable
import base64 as _base64


def _handle_godot_screenshot(**kwargs) -> str:
    """Captura screenshot do jogo rodando via bridge TCP."""
    try:
        result = send_bridge_command({"cmd": "screenshot"})
    except BridgeUnavailable as e:
        return json.dumps({"ok": False, "error": str(e)})
    if not result.get("ok"):
        return json.dumps(result)
    # Salva screenshot em disco e retorna caminho + base64
    png_data = _base64.b64decode(result["image_base64"])
    out_path = os.path.join(tempfile.gettempdir(), f"godot_screenshot_{int(time.time())}.png")
    with open(out_path, "wb") as f:
        f.write(png_data)
    result["saved_to"] = out_path
    return json.dumps(result)


def _handle_godot_runtime_info(**kwargs) -> str:
    """Obtem FPS, draw calls, memoria do jogo rodando."""
    try:
        result = send_bridge_command({"cmd": "runtime_info"})
    except BridgeUnavailable as e:
        return json.dumps({"ok": False, "error": str(e)})
    return json.dumps(result)


def _handle_godot_custom_command(name: str = "", args: dict | None = None, **kwargs) -> str:
    """Chama comando customizado registrado no bridge do jogo."""
    try:
        result = send_bridge_command({"cmd": "custom", "name": name, "args": args or {}})
    except BridgeUnavailable as e:
        return json.dumps({"ok": False, "error": str(e)})
    return json.dumps(result)


def _handle_godot_list_custom_commands(**kwargs) -> str:
    """Lista comandos customizados registrados no bridge."""
    try:
        result = send_bridge_command({"cmd": "list_commands"})
    except BridgeUnavailable as e:
        return json.dumps({"ok": False, "error": str(e)})
    return json.dumps(result)


# ── PATCH 12.1: Process Lifecycle ────────────────────────────
_running_godot_processes: dict[str, subprocess.Popen] = {}


def _handle_godot_run_project(project_path: str = "", godot_executable: str = "", **kwargs) -> str:
    """Lanca o jogo direto via CLI, sem editor."""
    if not project_path or not godot_executable:
        return json.dumps({"ok": False, "error": "project_path e godot_executable obrigatorios"})
    try:
        proc = subprocess.Popen(
            [godot_executable, "--path", project_path],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        _running_godot_processes[str(proc.pid)] = proc
        return json.dumps({"ok": True, "pid": proc.pid})
    except Exception as exc:
        return json.dumps({"ok": False, "error": str(exc)})


def _get_process_name(pid: int) -> str | None:
    """Obtem o nome do executavel de um PID. Retorna None se nao encontrado."""
    try:
        if sys.platform == "win32":
            result = subprocess.run(
                ["tasklist", "/FI", f"PID eq {pid}", "/FO", "CSV", "/NH"],
                capture_output=True, text=True, timeout=5,
            )
            if result.returncode == 0 and result.stdout.strip():
                line = result.stdout.strip()
                # Detecta mensagens de "nenhum resultado" em varios idiomas
                if any(phrase in line.lower() for phrase in (
                    "nenhuma tarefa", "no tasks", "aucune t", "keine",
                )):
                    return None
                parts = line.split(",")
                if len(parts) >= 2:
                    name = parts[0].strip('"')
                    # Nome de processo valido tipicamente termina com .exe
                    if name.lower().endswith(".exe") or name.lower().endswith(".scr"):
                        return name
                    # Fallback: se nao terminar com .exe, suspeito
                    return None
        else:
            try:
                import psutil
                return psutil.Process(pid).name()
            except ImportError:
                pass
    except Exception:
        pass
    return None


def _handle_godot_stop_project(pid: int = 0, **kwargs) -> str:
    """Encerra um processo de jogo iniciado por godot_run_project.
    Antes de matar, tenta salvar a cena atual via bridge (timeout 2s).
    Mata diretamente pelo PID (taskkill no Windows, SIGKILL no Unix),
    NAO depende do dicionario _running_godot_processes.
    Antes de matar, verifica que o nome do processo contem 'godot'."""
    killed = False
    was_tracked = False
    save_attempted = False
    save_result = None

    # ── Save-before-kill: tentar salvar via bridge (timeout 2s) ──
    try:
        save_attempted = True
        save_result = send_bridge_command(
            {"cmd": "custom", "name": "save_current_scene", "args": {}},
            timeout=2.0,
        )
    except BridgeUnavailable:
        save_result = {"error": "bridge unavailable"}
    except Exception as exc:
        save_result = {"error": str(exc)}

    # Tentativa 1: processo rastreado (terminate graceful)
    proc = _running_godot_processes.get(str(pid))
    if proc is not None:
        was_tracked = True
        try:
            proc.terminate()
            proc.wait(timeout=5)
            killed = True
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=5)
            killed = True
        except Exception:
            pass
        finally:
            _running_godot_processes.pop(str(pid), None)

    # Tentativa 2: matar diretamente pelo PID (fallback)
    if not killed:
        # Protecao: verificar nome do processo antes de matar
        pname = _get_process_name(pid)
        if pname is None:
            return json.dumps({"ok": False, "error": f"pid {pid} nao encontrado no sistema"})
        if "godot" not in pname.lower():
            return json.dumps({
                "ok": False,
                "error": f"pid {pid} pertence a '{pname}', nao a um processo Godot. Recusado por seguranca.",
            })

        try:
            if sys.platform == "win32":
                result = subprocess.run(
                    ["taskkill", "/F", "/PID", str(pid)],
                    capture_output=True, text=True, timeout=10,
                )
                if result.returncode != 0 and "não encontrado" not in result.stderr.lower():
                    return json.dumps({
                        "ok": False,
                        "error": f"taskkill falhou (rc={result.returncode}): {result.stderr.strip()}",
                    })
            else:
                import signal
                os.kill(pid, signal.SIGKILL)
            killed = True
        except ProcessLookupError:
            return json.dumps({"ok": False, "error": f"pid {pid} nao encontrado no sistema"})
        except Exception as exc:
            return json.dumps({"ok": False, "error": f"falha ao matar pid {pid}: {exc}"})

    return json.dumps({
        "ok": True, "pid": pid, "was_tracked": was_tracked,
        "save_attempted": save_attempted, "save_result": save_result,
    })


def _handle_godot_wait_for_bridge(timeout_sec: int = 10, **kwargs) -> str:
    """Espera ate o MCPRuntimeBridge responder via runtime_info."""
    start = time.time()
    while time.time() - start < timeout_sec:
        try:
            result = send_bridge_command({"cmd": "runtime_info"})
            return json.dumps(result)
        except BridgeUnavailable:
            time.sleep(0.3)
    return json.dumps({"ok": False, "error": f"bridge nao respondeu em {timeout_sec}s"})


# ── PATCH 13: Introspecção ClassDB ─────────────────────────────
def _handle_godot_class_ref(class_name: str = "", **kwargs) -> str:
    """Consulta metodos, propriedades e sinais reais de uma classe Godot.
    Cobre APENAS classes nativas do Godot (extension_api.json).
    NAO retorna classes custom do projeto (class_name em scripts .gd)."""
    from tools.classdb import (suggest_similar, _class_index, _all_class_names,
                                list_methods, list_signals, get_class_hierarchy)

    try:
        all_names = _all_class_names()
    except Exception:
        all_names = []

    if not class_name:
        return json.dumps({"ok": False, "error": "class_name obrigatorio"})
    if class_name not in all_names:
        suggestions = suggest_similar(class_name, limit=5)
        return json.dumps({
            "ok": False,
            "error": f"classe '{class_name}' nao encontrada na ClassDB",
            "suggestions": suggestions,
        })

    # Metodos e sinais com heranca (classdb.py ja faz merge)
    methods = list_methods(class_name)
    signals_list = list_signals(class_name)

    # Propriedades, enums, constantes — walking inheritance manualmente
    all_props: dict[str, dict] = {}
    all_enums: dict[str, dict] = {}
    all_constants: dict[str, dict] = {}
    current = class_name
    class_index = _class_index()
    while current:
        e = class_index.get(current, {})
        for p in e.get("properties", []):
            if p["name"] not in all_props:
                all_props[p["name"]] = p
        for en in e.get("enums", []):
            if en["name"] not in all_enums:
                all_enums[en["name"]] = en
        for c in e.get("constants", []):
            if c["name"] not in all_constants:
                all_constants[c["name"]] = c
        current = e.get("inherits", "")

    hierarchy = get_class_hierarchy(class_name)

    return json.dumps({
        "ok": True,
        "class_name": class_name,
        "parent_class": hierarchy[1] if len(hierarchy) > 1 else None,
        "hierarchy": hierarchy,
        "method_count": len(methods),
        "methods": [m["name"] for m in methods[:50]],
        "property_count": len(all_props),
        "properties": sorted(all_props.keys())[:50],
        "signal_count": len(signals_list),
        "signals": [s["name"] for s in signals_list[:50]],
        "enum_count": len(all_enums),
        "enums": sorted(all_enums.keys())[:50],
        "constant_count": len(all_constants),
        "constants": sorted(all_constants.keys())[:50],
    }, indent=2)


from tools.project_ops import (
    _get_active_project,
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
from tools.bootstrap_ops import bootstrap_godot_mcp, godot_keep_alive
from tools.batch_ops import batch_atomic_edit
from tools.asset_download import download_asset, import_downloaded_asset
from tools.workflow_ops import (
    workflow_snapshot, workflow_handoff,
)
from tools.project_map import generate_project_map
from tools.security_ops import configure_security, security_status
from tools.gut_ops import run_gut_tests
from tools.playmode_ops import assert_node_exists, simulate_input_sequence
from tools.vibe_ops import vibe_coding_mode, get_vibe_context
from tools.debugger_ops import debugger_set_breakpoint, debugger_status, debugger_step, debugger_get_stack, debugger_get_variables
from tools.networking_ops import game_http_request, game_multiplayer
from tools.safety_policy import set_safety_policy, get_audit_log, get_audit_replay
from tools.validate_write import safe_write_gdscript
from tools.dynamic_groups import tool_catalog, tool_groups
from tools.recording_ops import start_recording, stop_recording, game_serialize_state
from tools.runtime_rich import (
    game_call_method,
    game_spawn_node,
    game_raycast, game_get_camera,
    game_play_animation,
    game_find_nodes_by_class,
    game_await_signal, game_pause,
)
from tools.runtime_ui import game_performance, game_window, game_input_state
from tools.infra_ops import generate_ci_snippet, resource_dependency_graph, build_csharp
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
    search_classdb,
    list_valid_node_types,
    list_methods,
    get_class_hierarchy,
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
from tools.art_ops import (
    generate_game_art,
    apply_game_art,
)
from tools.flux_ops import generate_game_art_flux
from tools.art_postprocess import remove_background, optimize_sprite, create_spritesheet
from tools.tts_ops import generate_voice
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
    undo_last_action,
    get_undo_history,
)

# ── LSP Bridge (Fase 2A / C3) ───────────────────────────────────
from tools.lsp_ops import (
    gdscript_lsp_connect,
    gdscript_lsp_disconnect,
    gdscript_references,
    gdscript_definition,
    gdscript_hover,
    gdscript_symbols,
    gdscript_rename,
    gdscript_diagnostics,
    gdscript_sync_file,
)

# ── Addon Bridge (Fase 2B / A2) ─────────────────────────────────
from tools.addon_bridge import (
    addon_connect,
    addon_disconnect,
    addon_is_available,
    addon_ping,
    addon_create_node,
    addon_delete_node,
    addon_set_property,
    addon_reparent_node,
    addon_duplicate_node,
    addon_batch_edit,
    addon_take_screenshot,
    addon_get_scene_tree,
)

# ── Playtest (Fase 2B / A3+A4+A5) ───────────────────────────────
from tools.playtest_ops import (
    freeze_game_clock,
    unfreeze_game_clock,
    step_game_time,
    step_until,
    get_runtime_state_digest,
    capture_runtime_errors,
    watch_state_start, watch_state_collect,
    godot_exec, effect_probe,
)

# ── Balance (Onda 1) ──────────────────────────────────────────
from tools.balance_ops import (
    balance_analyze, wave_generate,
    dps_calculator, loot_table_generate,
    gdd_generate,
)

# ── Behavior Trees (Onda 2) ───────────────────────────────────
from tools.behavior_ops import (
    behavior_tree_generate, behavior_tree_list_templates,
)

# ── Performance Profiler (Onda 2) ──────────────────────────────
from tools.perf_ops import profile_frame, profile_memory

# ── Auto-Config (Fase 2C) ───────────────────────────────────────
from tools.vscode_config import (
    validate_environment as _validate_env,
    auto_config as _auto_config,
)

# ── Shader NL (Onda 3) ─────────────────────────────────────────
from tools.shader_ops import shader_generate, shader_list_templates

# ── World Generation (Onda 3) ───────────────────────────────────
from tools.world_gen import terrain_generate, dungeon_generate, world_describe

# ── 3D Asset Generation (Onda 3) ────────────────────────────────
from tools.threed_gen import generate_3d_placeholder, generate_3d_asset

# ── Deploy + Marketplace (Onda 4 — FINAL) ──────────────────────
from tools.deploy_ops import deploy_itch, release_checklist, auto_screenshot
from tools.marketplace_ops import marketplace_search, marketplace_download

# ── Juice (Onda 5) ────────────────────────────────────────────
from tools.juice_ops import juice_apply, juice_list_presets

# ── Pipeline Executor (Onda 7) ──────────────────────────────────
from tools.pipeline_ops import project_status

# ── Orquestrador Genius (Onda 7) ────────────────────────────────
from tools.orchestrator import create_entity, circuit_breaker_status

# ── Onda 6: Server Instructions (system prompt do MCP) ──────────────

MCP_INSTRUCTIONS = """Voce e um designer de jogos Godot 4.7. O usuario fala em portugues simples e NAO e programador.

REGRAS DE OURO:
1. Gere o artefato INTEIRO de uma vez. Use batch_atomic_edit para multiplas operacoes.
2. Antes de criar algo complexo, CONFIRME em 1-2 linhas.
3. Apos cada mudanca visivel, DESCREVA o resultado.
4. Se algo falhar, explique EM PORTUGUES SIMPLES. Nao mostre stack trace.
5. Consulte o estado atual ANTES de criar (analyze_game_structure ou load_scene_tree).
6. Se o pedido for vago, pergunte so o essencial com opcoes curtas (A/B/C).
7. Use compile_test + run_game apos cada bloco de mudancas.

PADROES (implemente automaticamente):
- 'cria um personagem' -> CharacterBody2D + CollisionShape2D + Sprite2D + script WASD
- 'mais dificil' -> ajusta dano/HP/velocidade nos scripts
- 'muda cor' -> set_node_property
- 'adiciona som' -> generate_audio_sfx + referencia no script
- 'fase nova' -> create_scene + TileMap + spawn points
- 'faz menu' -> CanvasLayer + VBoxContainer + botoes
- 'muito facil/dificil' -> balance_analyze + ajusta numeros

NUNCA FACA:
- Use jargao tecnico sem explicar
- Crie arquivos 'para o futuro'
- Modifique sem ler estado atual
- Deixe usuario esperando sem feedback
- Input.is_action_pressed() sem configure_input_action
- CollisionObject2D sem CollisionShape2D
- Assuma que o projeto esta configurado

ANTES DE ENTREGAR:
1. compile_test passou? 2. run_game iniciou? 3. CollisionShape2D nos CollisionObjects?
4. Input Map completo? 5. Main scene definida? 6. Condicao de vitoria E derrota?"""


# ── Server ──────────────────────────────────────────────────────────

server = Server("godot-agent")


# ── Tool Definitions ────────────────────────────────────────────────

# ── B6: Read/Write Split ────────────────────────────────────────────

_READ_PREFIXES = (
    "read_", "get_", "query_", "list_", "search_", "ping", "health",
    "status", "validate_", "inspect_", "check_", "detect_", "find_",
    "compare_", "suggest_", "analyze_", "estimate_", "summary",
    "handoff", "map", "take_", "capture_",
)
_WRITE_PREFIXES = (
    "create_", "delete_", "set_", "write_", "generate_", "build_",
    "install_", "configure_", "import_", "apply_", "paint_", "bake_",
    "launch_", "close_", "compile", "run_", "stop_", "restart",
    "freeze_", "unfreeze_", "step_", "inject_", "record_", "download_",
    "duplicate_", "reparent_", "add_", "remove_",
)


def _classify_operation(tool_name: str) -> str:
    """Classifica tool como 'read', 'write' ou 'read+write'."""
    is_read = tool_name.startswith(_READ_PREFIXES)
    is_write = tool_name.startswith(_WRITE_PREFIXES)
    if tool_name.endswith("_manage") or tool_name == "addon_batch_edit":
        return "read+write"
    if is_read and is_write:
        return "read+write"
    if is_read:
        return "read"
    if is_write:
        return "write"
    has_read = any(w in tool_name for w in ("read", "get", "query", "list", "search", "ping", "health", "check", "status", "snapshot", "symbols", "references", "definition", "hover", "diagnostics"))
    has_write = any(w in tool_name for w in ("create", "delete", "set", "write", "generate", "build", "install", "config", "import", "apply", "edit", "batch"))
    if has_read and has_write:
        return "read+write"
    if has_read:
        return "read"
    if has_write:
        return "write"
    return "read+write"


def _validate_coord(value, name: str) -> str | None:
    """Valida coordenadas numéricas para game_raycast e similares."""
    import math
    if not isinstance(value, (int, float)):
        return f"{name} deve ser número, recebeu {type(value).__name__}"
    if math.isnan(value) or math.isinf(value):
        return f"{name} não pode ser NaN ou infinito"
    if abs(value) > 100000:
        return f"{name} fora do range permitido (-100000 a 100000)"
    return None


# Cache global para _tool_defs (evita recriar 143 tools a cada list_tools)
_TOOL_DEFS_CACHE: list[Tool] | None = None


# ══════════════════════════════════════════════════════════════
# PÓS-PROCESSADOR: garantir 4 hints em 100% das tools
# ══════════════════════════════════════════════════════════════

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

        tool.annotations = ann

    return tools


# ══════════════════════════════════════════════════════════════
# Onda 5: compactar descricoes (-80% tokens)
# ══════════════════════════════════════════════════════════════

def _compact_description(description: str, max_chars: int = 120) -> str:
    """Encurta descricao mantendo a informacao essencial."""
    import re
    if not description or len(description) <= max_chars:
        return description
    first_sentence = re.split(r'[.]\s+(?:Quando|Pré|Pre|Exemplo|Erro)', description)[0].strip()
    if len(first_sentence) > max_chars:
        parts = first_sentence.split('. ')
        result = ''
        for part in parts:
            if len(result) + len(part) < max_chars:
                result += part + '. '
            else:
                break
        first_sentence = result.strip()
    if first_sentence and first_sentence[-1] not in '.!?':
        first_sentence += '.'
    return first_sentence[:max_chars]


def _compact_all_tool_descriptions(tools: list) -> list:
    """Encurta descricoes de todas as tools."""
    for tool in tools:
        original = tool.description or ""
        compact = _compact_description(original)
        if len(compact) < len(original):
            tool.description = compact
    return tools


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
                "Consulta informações COMPLETAS de uma classe na ClassDB do Godot com "
                "PAGINAÇÃO, FILTROS e DETALHES. Retorna propriedades (com tipo, descrição, default), "
                "métodos (com args, retorno, descrição), sinais, enums e constantes. "
                "Use para descobrir TUDO sobre qualquer classe do Godot 4.7. "
                "Parâmetros de filtro: 'section' escolhe a seção (properties, methods, signals, enums, constants, all), "
                "'include_inherited' inclui membros da classe pai, 'offset' e 'limit' controlam paginação. "
                "QUANDO USAR: para consultar uma classe específica com riqueza de detalhes. "
                "QUANDO NÃO USAR: para listar tipos de nó (use list_valid_node_types) ou buscar por nome parcial (use search_classdb). "
                "Exemplo: {'class_name': 'CharacterBody2D', 'section': 'methods', 'limit': 10}."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "class_name": {"type": "string", "description": "Nome da classe (ex: 'Node2D', 'CharacterBody2D'). Case-sensitive."},
                    "section": {
                        "type": "string",
                        "enum": ["all", "properties", "methods", "signals", "enums", "constants"],
                        "description": "Seção a retornar. 'all' retorna todas. Default: 'all'."
                    },
                    "include_inherited": {
                        "type": "boolean",
                        "description": "Incluir membros herdados da classe pai. Default: false."
                    },
                    "offset": {
                        "type": "integer",
                        "description": "Offset para paginação. Default: 0."
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Máximo de itens por seção. Default: 50."
                    },
                },
                "required": ["class_name"],
            },
        ),
        Tool(
            name="search_classdb",
            description=(
                "🔍 Busca classes na ClassDB do Godot por nome PARCIAL. "
                "Diferente de query_classdb (que exige nome exato), esta tool faz busca fuzzy: "
                "'Body' encontra CharacterBody2D, StaticBody2D, RigidBody3D, etc. "
                "Use para descobrir classes quando você não sabe o nome exato. "
                "QUANDO USAR: 'tem alguma classe de luz?', 'quais classes têm Body no nome?'. "
                "QUANDO NÃO USAR: se já sabe o nome exato (use query_classdb). "
                "Exemplo: {'query': 'Light', 'limit': 10}."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Texto parcial para buscar (ex: 'Body', 'Light', 'Camera'). Case-insensitive."
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Máximo de resultados. Default: 20."
                    },
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="download_asset",
            description=(
                "Baixa assets GRATUITOS (CC0) de APIs publicas. "
                "Fontes: Poly Haven (texturas PBR, HDRIs, modelos 3D), Kenney (sprites, tilesets, UI, audio), "
                "AmbientCG (materiais PBR). Use para prototipagem rapida. "
                "Exemplo: {'source': 'polyhaven', 'query': 'metal', 'category': 'textures'}."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "source": {"type": "string", "enum": ["polyhaven", "kenney", "ambientcg"]},
                    "query": {"type": "string"},
                    "category": {"type": "string"},
                    "asset_id": {"type": "string"},
                    "resolution": {"type": "string"},
                    "limit": {"type": "integer"},
                },
                "required": ["source", "query"],
            },
        ),
        Tool(
            name="import_downloaded_asset",
            description=(
                "Importa um asset baixado para o projeto Godot ativo. "
                "Use APOS download_asset. "
                "Exemplo: {'asset_path': 'C:/.../gdm_assets/...', 'target_dir': 'assets/textures'}."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "asset_path": {"type": "string"},
                    "target_dir": {"type": "string"},
                },
                "required": ["asset_path"],
            },
        ),
        Tool(
            name="workflow_snapshot",
            description=(
                "Salva snapshot do estado atual do projeto no workflow log. "
                "Use ANTES de operações grandes para ter ponto de restauração."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "description": {"type": "string"},
                    "project_path": {"type": "string"},
                },
                "required": [],
            },
        ),
        Tool(
            name="workflow_handoff",
            description=(
                "Prepara resumo para proxima sessao. Use no FINAL de cada sessao."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "next_steps": {"type": "array", "items": {"type": "string"}},
                    "notes": {"type": "string"},
                },
                "required": [],
            },
        ),
        Tool(
            name="project_map",
            description="Gera mapa do projeto: cenas, scripts, funcoes, assets. Formatos: json ou html.",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_path": {"type": "string"},
                    "format": {"type": "string", "enum": ["json", "html", "both"]},
                },
                "required": [],
            },
        ),
        Tool(name="configure_security", description="Configura token de seguranca para o addon MCP.",
            inputSchema={"type":"object","properties":{"generate_token":{"type":"boolean"},"allow_remote":{"type":"boolean"}},"required":[]}),
        Tool(name="security_status", description="Verifica configuracao de seguranca atual.",
            inputSchema={"type":"object","properties":{},"required":[]}),
        Tool(name="run_gut_tests", description="Executa testes GUT via Godot headless. Ex: {'test_dir': 'res://tests'}.",
            inputSchema={"type":"object","properties":{"project_path":{"type":"string"},"test_dir":{"type":"string"},"timeout":{"type":"integer"}},"required":[]}),
        Tool(name="assert_node_exists", description="Verifica se no existe na cena. Ex: {'scene_path':'...','node_path':'./Player'}.",
            inputSchema={"type":"object","properties":{"scene_path":{"type":"string"},"node_path":{"type":"string"},"node_type":{"type":"string"}},"required":["scene_path","node_path"]}),
        Tool(name="simulate_input_sequence", description="Simula sequencia de inputs. Ex: {'actions':[{'type':'key','key':32}]}.",
            inputSchema={"type":"object","properties":{"actions":{"type":"array","items":{"type":"object"}},"delay_ms":{"type":"integer"}},"required":["actions"]}),
        Tool(name="vibe_coding_mode", description="Ativa/desativa Vibe Coding Mode. Foco automatico na cena configurada.",
            inputSchema={"type":"object","properties":{"enabled":{"type":"boolean"},"scene_path":{"type":"string"},"focus_node":{"type":"string"}},"required":[]}),
        Tool(name="get_vibe_context", description="Retorna contexto atual do Vibe Coding Mode.",
            inputSchema={"type":"object","properties":{},"required":[]}),
        Tool(name="game_http_request", description="HTTP request no jogo. Ex: {'url':'https://api.ex.com','method':'GET'}.",
            inputSchema={"type":"object","properties":{"url":{"type":"string"},"method":{"type":"string"},"headers":{"type":"object"},"body":{"type":"string"}},"required":["url"]}),
        Tool(name="game_multiplayer", description="Multiplayer ENet. Ex: {'action':'create_server','port':9090}.",
            inputSchema={"type":"object","properties":{"action":{"type":"string","enum":["create_server","create_client","disconnect","status"]},"port":{"type":"integer"},"address":{"type":"string"}},"required":["action"]}),
        Tool(name="set_safety_policy", description="Configura politica de seguranca (allowlist/blocklist).",
            inputSchema={"type":"object","properties":{"enabled":{"type":"boolean"},"allowlist":{"type":"array","items":{"type":"string"}},"blocklist":{"type":"array","items":{"type":"string"}},"confirm_destructive":{"type":"boolean"}},"required":[]}),
        Tool(name="get_audit_log", description="Historico de auditoria das acoes da IA.",
            inputSchema={"type":"object","properties":{"limit":{"type":"integer"}},"required":[]}),
        Tool(name="get_audit_replay", description="Replay do historico de auditoria.",
            inputSchema={"type":"object","properties":{"steps":{"type":"integer"}},"required":[]}),
        Tool(name="safe_write_gdscript", description="Escreve .gd COM validacao. Recusa codigo invalido! Ex: {'file_path':'res://x.gd','content':'...'}.",
            inputSchema={"type":"object","properties":{"file_path":{"type":"string"},"content":{"type":"string"},"project_path":{"type":"string"},"strict":{"type":"boolean"}},"required":["file_path","content"]}),
        Tool(name="tool_catalog", description="Catalogo de tools por grupo. Ex: {'query':'scene','group':'core'}.",
            inputSchema={"type":"object","properties":{"query":{"type":"string"},"group":{"type":"string"},"limit":{"type":"integer"}},"required":[]}),
        Tool(name="tool_groups", description="Gerencia grupos dinamicos de tools. Ex: {'action':'activate','group':'art'}.",
            inputSchema={"type":"object","properties":{"action":{"type":"string","enum":["list","activate","deactivate"]},"group":{"type":"string"}},"required":["action"]}),
        Tool(name="game_serialize_state", description="Salva/restaura estado completo do jogo como JSON.",
            inputSchema={"type":"object","properties":{"action":{"type":"string","enum":["save","load"]},"file_name":{"type":"string"}},"required":["action"]}),
        Tool(name="start_recording", description="Inicia gravacao de sessao (inputs/estados).",
            inputSchema={"type":"object","properties":{"session_name":{"type":"string"}},"required":[]}),
        Tool(name="stop_recording", description="Para gravacao e retorna resumo.",
            inputSchema={"type":"object","properties":{"session_name":{"type":"string"}},"required":["session_name"]}),
        Tool(name="game_call_method", description="Chama metodo em no no jogo rodando.",
            inputSchema={"type":"object","properties":{"node_path":{"type":"string"},"method":{"type":"string"},"args":{"type":"array"}},"required":["node_path","method"]}),
        Tool(name="game_spawn_node", description="Cria no dinamicamente no jogo.",
            inputSchema={"type":"object","properties":{"parent_path":{"type":"string"},"node_type":{"type":"string"},"node_name":{"type":"string"},"properties":{"type":"object"}},"required":["parent_path","node_type"]}),
        Tool(name="game_raycast", description="Ray cast 2D/3D no jogo.",
            inputSchema={"type":"object","properties":{"origin_x":{"type":"number"},"origin_y":{"type":"number"},"target_x":{"type":"number"},"target_y":{"type":"number"},"collision_mask":{"type":"integer"},"mode":{"type":"string"}},"required":["origin_x","origin_y","target_x","target_y"]}),
        Tool(name="game_get_camera", description="Obtem posicao da camera ativa.",
            inputSchema={"type":"object","properties":{"mode":{"type":"string"}},"required":[]}),
        Tool(name="game_play_animation", description="Controla AnimationPlayer no jogo.",
            inputSchema={"type":"object","properties":{"node_path":{"type":"string"},"action":{"type":"string"},"animation_name":{"type":"string"}},"required":["node_path","action"]}),
        Tool(name="game_find_nodes_by_class", description="Encontra nos por classe no jogo.",
            inputSchema={"type":"object","properties":{"class_name":{"type":"string"},"limit":{"type":"integer"}},"required":["class_name"]}),
        Tool(name="game_await_signal", description="Espera sinal com timeout.",
            inputSchema={"type":"object","properties":{"node_path":{"type":"string"},"signal_name":{"type":"string"},"timeout_ms":{"type":"integer"}},"required":["node_path","signal_name"]}),
        Tool(name="game_pause", description="Pausa/despausa o jogo.",
            inputSchema={"type":"object","properties":{"action":{"type":"string","enum":["toggle","pause","unpause"]}},"required":[]}),
        Tool(name="game_performance", description="Metricas: FPS, memoria, objetos, draw calls.",
            inputSchema={"type":"object","properties":{},"required":[]}),
        Tool(name="game_window", description="Controle de janela: size, fullscreen, title.",
            inputSchema={"type":"object","properties":{"action":{"type":"string"},"width":{"type":"integer"},"height":{"type":"integer"},"fullscreen":{"type":"boolean"},"title":{"type":"string"}},"required":[]}),
        Tool(name="game_input_state", description="Estado de input: teclas, mouse, gamepad.",
            inputSchema={"type":"object","properties":{},"required":[]}),
        Tool(name="generate_ci_snippet", description="Gera GitHub Actions / GitLab CI para export.",
            inputSchema={"type":"object","properties":{"project_path":{"type":"string"},"target_platforms":{"type":"string"}},"required":[]}),
        Tool(name="resource_dependency_graph", description="Grafo de dependencias de recursos.",
            inputSchema={"type":"object","properties":{"project_path":{"type":"string"}},"required":[]}),
        Tool(name="build_csharp", description="Compila projeto C# e retorna erros estruturados.",
            inputSchema={"type":"object","properties":{"project_path":{"type":"string"}},"required":[]}),
        Tool(name="debugger_set_breakpoint", description="Define breakpoint. Ex: {'script_path':'res://player.gd','line':42}.",
            inputSchema={"type":"object","properties":{"script_path":{"type":"string"},"line":{"type":"integer"},"condition":{"type":"string"}},"required":["script_path","line"]}),
        Tool(name="debugger_status", description="Verifica estado do debugger do Godot (porta 6006).",
            inputSchema={"type":"object","properties":{},"required":[]}),
        Tool(name="debugger_step", description="Avança uma linha no debugger. Ex: {'step_type':'over'}.",
            inputSchema={"type":"object","properties":{"step_type":{"type":"string","enum":["over","into","out"]}},"required":[]}),
        Tool(name="debugger_get_stack", description="Obtem stack trace atual do debugger.",
            inputSchema={"type":"object","properties":{},"required":[]}),
        Tool(name="debugger_get_variables", description="Inspeciona variaveis no escopo do debugger. Ex: {'variable_name':'health'}.",
            inputSchema={"type":"object","properties":{"variable_name":{"type":"string","description":"Nome da variavel (null = todas)."}},"required":[]}),
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
                    "animations": {"type": "array", "items": {"type": "object"}},
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
            name="bootstrap_godot_mcp",
            description=(
                "🚀 BOOTSTRAP AUTOMÁTICO: conecta VS Code → MCP → Godot em UMA chamada. "
                "Substitui 12+ passos manuais (validar, configurar, abrir Godot, esperar LSP, "
                "esperar addon, conectar tudo). A IA agêntica deve chamar ESTA tool primeiro, "
                "sempre que iniciar uma sessão de desenvolvimento Godot. "
                "QUANDO USAR: primeira tool de toda sessão Godot. "
                "QUANDO NÃO USAR: se já rodou bootstrap nesta sessão (use health_check para verificar). "
                "Exemplo: {'target': 'full'} para bootstrap completo com auto-detecção. "
                "Use target='validate_only' para só checar o ambiente sem abrir Godot. "
                "Use target='connect_only' se Godot já estiver aberto."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "target": {
                        "type": "string",
                        "enum": ["full", "connect_only", "validate_only"],
                        "description": "full=tudo, connect_only=só conexão (Godot já aberto), validate_only=só checar ambiente"
                    },
                    "project_path": {
                        "type": "string",
                        "description": "Caminho do projeto Godot. Auto-detecta se omitido."
                    },
                    "godot_path": {
                        "type": "string",
                        "description": "Caminho do executável Godot. Auto-detecta do config.json se omitido."
                    },
                    "launch_editor": {
                        "type": "boolean",
                        "description": "Abrir Godot Editor se não estiver aberto. Default: true."
                    },
                    "timeout_godot": {
                        "type": "integer",
                        "description": "Segundos máximos esperando Godot abrir (default 30)."
                    },
                    "timeout_addon": {
                        "type": "integer",
                        "description": "Segundos máximos esperando addon iniciar (default 15)."
                    },
                },
                "required": []
            },
        ),
        Tool(
            name="godot_keep_alive",
            description="Garante que o Godot Editor esta aberto. Se nao estiver, abre. "
                        "NAO fecha o Godot em hipotese alguma. Chame no inicio de toda sessao. "
                        "Use quando suspeitar que o Godot foi fechado.",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_path": {"type": "string", "description": "Caminho do projeto (auto se omitido)."},
                    "godot_path": {"type": "string", "description": "Caminho do Godot (auto se omitido)."},
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
                    "keyframes": {"type": "array", "items": {"type": "object"}},
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
        Tool(
            name="batch_atomic_edit",
            description=(
                "⚛️ Edição ATÔMICA em lote com ROLLBACK automático. "
                "Executa múltiplas operações (criar nó, definir propriedade, deletar, "
                "reparentar, duplicar, conectar sinal) em UMA ação. "
                "Se QUALQUER operação falhar, TODAS as anteriores são DESFEITAS. "
                "Modo addon (Godot aberto): UndoRedo nativo — 1 Ctrl+Z desfaz tudo. "
                "Modo file-based (Godot fechado): snapshot .tscn + restore se erro. "
                "QUANDO USAR: SEMPRE que for fazer 2+ operações que precisam ser atômicas. "
                "QUANDO NÃO USAR: para 1 operação isolada (use node_manage direto). "
                "Exemplo: [{\"op\": \"create_node\", \"params\": {\"parent\": \".\", \"type\": \"Sprite2D\", \"name\": \"Icon\"}}, "
                "{\"op\": \"set_property\", \"params\": {\"node\": \"./Icon\", \"prop\": \"position\", \"value\": \"Vector2(100,200)\"}}]. "
                "Ops válidas: create_node, delete_node, set_property, reparent_node, duplicate_node, connect_signal."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "operations": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "op": {
                                    "type": "string",
                                    "enum": ["create_node", "delete_node", "set_property", "reparent_node", "duplicate_node", "connect_signal"],
                                },
                                "params": {"type": "object"},
                            },
                            "required": ["op"],
                        },
                        "description": "Lista de operações atômicas. Se uma falhar, todas são desfeitas."
                    },
                    "scene_path": {
                        "type": "string",
                        "description": "Caminho da cena .tscn. Obrigatório para file-based. Opcional se addon conectado."
                    },
                    "mode": {
                        "type": "string",
                        "enum": ["auto", "addon", "file"],
                        "description": "auto=detecta addon, addon=força WebSocket, file=força file-based."
                    },
                },
                "required": ["operations"],
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
                "Gera um efeito sonoro WAV por sintese procedural com 23 tipos. "
                "Suporta: beep, jump, laser, explosion, collect, hit, "
                "coin, ui_click, ui_hover, ui_error, ui_notification, "
                "wind, rain, footsteps, gunshot, engine, electricity, "
                "magic, powerup, damage, door, fire, water, string. "
                "Use para sons de pulo, tiro, coleta, explosao, UI, ambiente "
                "e muito mais — sem assets externos. "
                "Pre-condicoes: nenhuma (usa NumPy + SciPy + wave nativos). "
                "Exemplo: {\"name\": \"magic_spell\", \"sfx_type\": \"magic\", \"duration\": 0.5, \"style\": \"fantasia\"}. "
                "Erro mais comum: tipo invalido — use um dos 23 tipos suportados."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "sfx_type": {"type": "string", "enum": [
                        "beep", "jump", "laser", "explosion", "collect", "hit",
                        "coin", "ui_click", "ui_hover", "ui_error", "ui_notification",
                        "wind", "rain", "footsteps", "gunshot", "engine", "electricity",
                        "magic", "powerup", "damage", "door", "fire", "water", "string"
                    ]},
                    "duration": {"type": "number"},
                    "frequency": {"type": "number"},
                    "sample_rate": {"type": "integer"},
                    "style": {"type": "string", "enum": ["scifi", "fantasia", "retro", "realista"]},
                    "save_path": {"type": "string"},
                },
                "required": ["name"],
            },
        ),
        Tool(
            name="generate_voice",
            description=(
                "Gera narracao/fala a partir de texto (TTS). "
                "Usa Kokoro TTS local (82M params, Apache 2.0, offline) ou "
                "Edge TTS gratuito como fallback. "
                "Ideal para dialogos de NPCs, narracao, voice acting. "
                "Suporta pt-BR via Edge TTS (Antonio, Francisca)."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "Texto para converter em fala (max 500 chars)"},
                    "voice": {"type": "string", "description": "Voz: af_heart, af_bella, am_adam, pt-BR-AntonioNeural..."},
                    "speed": {"type": "number", "description": "Velocidade (0.5 lento a 2.0 rapido)"},
                    "language": {"type": "string", "enum": ["pt", "en", "ja", "zh", "kr", "fr"],
                                "description": "Idioma do texto"},
                    "save_path": {"type": "string", "description": "Caminho no projeto (auto se None)"},
                },
                "required": ["text"],
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
        # ── Onda 12: Arte IA ──
        Tool(
            name="generate_game_art",
            description=(
                "Gera arte de jogo a partir de descricao em linguagem natural usando IA "
                "(ChatGPT/DALL-E via navegador headless). Gera QUALQUER artefato: torres, "
                "inimigos, personagens, biomas, tiles, icones, HUD, VFX, tudo. "
                "Sprite sheets com multiplos frames para animacao automatica. "
                "Cache inteligente: mesma descricao = reusa arte (zero custo). "
                "Use para criar assets visuais completos sem sair do chat. "
                "Quando usar: SEMPRE que precisar de arte nova no jogo. "
                "Quando NAO usar: para placeholder rapido (use generate_placeholder_sprite). "
                "Pré-condicoes: projeto ativo, ChatGPT logado (primeira vez). "
                "Categorias: torre, inimigo, personagem, bioma, tile, icone, hud, vfx, fundo, projetil, ui. "
                "Estilos: scifi, fantasia, cartoon, realista, pixel, minimalista. "
                "Animacoes: idle, fire, walk, run, death, attack, spawn, hit. "
                "Grid automatico: 4 frames = 2x2, 6 frames = 3x2, etc. "
                "Exemplo: {\"description\": \"torre railgun com trilhos eletromagneticos azuis\", "
                "\"category\": \"torre\", \"style\": \"scifi\", \"frames\": 6, \"anim_type\": \"fire\"}. "
                "Retorna lista de frames recortados e prontos para apply_game_art."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "description": {"type": "string", "description": "Descricao da arte em portugues (ex: 'torre laser com cristal flutuante')."},
                    "category": {"type": "string", "enum": ["torre", "inimigo", "personagem", "bioma", "tile", "icone", "hud", "vfx", "fundo", "projetil", "ui"], "description": "Categoria do artefato."},
                    "style": {"type": "string", "enum": ["scifi", "fantasia", "cartoon", "realista", "pixel", "minimalista"], "description": "Estilo visual."},
                    "anim_type": {"type": "string", "enum": ["idle", "fire", "walk", "run", "death", "attack", "spawn", "hit"], "description": "Tipo de animacao."},
                    "frames": {"type": "integer", "description": "Quantidade de frames (4-16). Se omitido, usa padrao por animacao."},
                    "grid_cols": {"type": "integer", "description": "Colunas do grid (opcional, calculado automaticamente)."},
                    "grid_rows": {"type": "integer", "description": "Linhas do grid (opcional, calculado automaticamente)."},
                    "width": {"type": "integer", "description": "Largura por frame em pixels."},
                    "height": {"type": "integer", "description": "Altura por frame em pixels."},
                    "save_dir": {"type": "string", "description": "Diretorio relativo no projeto (ex: 'assets/sprites/towers/')."},
                },
                "required": ["description"],
            },
        ),
        Tool(
            name="apply_game_art",
            description=(
                "Aplica arte gerada (frames recortados) num AnimatedSprite2D do Godot. "
                "Importa frames, cria SpriteFrames .tres, configura animacao com FPS e loop. "
                "Use SEMPRE apos generate_game_art para colocar a arte no jogo. "
                "Quando usar: apos generate_game_art retornar os frames. "
                "Pré-condicoes: generate_game_art concluido, cena e no existirem. "
                "Exemplo: {\"frame_paths\": [\"assets/sprites/towers/railgun_f1.png\", ...], "
                "\"scene_path\": \"scenes/main.tscn\", \"node_path\": \"Grid/Towers/Torre_0\", "
                "\"anim_name\": \"fire\", \"fps\": 10, \"loop\": true}. "
                "Erro mais comum: frame nao encontrado — verifique se generate_game_art rodou antes."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "frame_paths": {"type": "array", "items": {"type": "string"}, "description": "Lista de caminhos relativos dos frames."},
                    "scene_path": {"type": "string", "description": "Caminho da cena .tscn."},
                    "node_path": {"type": "string", "description": "Caminho do no AnimatedSprite2D."},
                    "anim_name": {"type": "string", "description": "Nome da animacao (ex: 'idle', 'fire')."},
                    "fps": {"type": "number", "description": "Frames por segundo. Default: 10."},
                    "loop": {"type": "boolean", "description": "Se a animacao faz loop. Default: true."},
                },
                "required": ["frame_paths", "scene_path", "node_path"],
            },
        ),
        # ── Pacote C: Pipeline de Arte FLUX.2 + Pós-processamento ──
        Tool(
            name="generate_game_art_flux",
            description=(
                "Gera arte de jogo via FLUX.2 API (Black Forest Labs). "
                "Substitui o DALL-E/Playwright. Suporta: torre, inimigo, "
                "personagem, bioma, tile, icone, hud, vfx, fundo, projetil, ui. "
                "Cache automatico por hash do prompt. Fallback para Replicate "
                "e Pillow procedural se APIs offline. "
                "Use esta tool como PRIMEIRA OPCAO para gerar assets visuais. "
                "A tool generate_game_art (DALL-E) e o fallback legado."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "description": {"type": "string", "description": "Descricao em portugues do que gerar"},
                    "category": {"type": "string", "enum": ["torre","inimigo","personagem","bioma","tile","icone","hud","vfx","fundo","projetil","ui"],
                                 "description": "Tipo de artefato"},
                    "style": {"type": "string", "enum": ["scifi","fantasia","cartoon","realista","pixel","minimalista"],
                              "description": "Estilo visual"},
                    "frames": {"type": "integer", "description": "Numero de frames (1 = imagem unica)"},
                    "width": {"type": "integer", "description": "Largura (auto por categoria se omitido)"},
                    "height": {"type": "integer", "description": "Altura (auto por categoria se omitido)"},
                    "save_path": {"type": "string", "description": "Caminho relativo no projeto Godot"},
                },
                "required": ["description", "category"],
            },
        ),
        Tool(
            name="remove_background",
            description=(
                "Remove o fundo de uma imagem usando IA (rembg/birefnet). "
                "Use para sprites gerados por IA que vieram com fundo. "
                "Suporta PNG, JPG, WebP. Retorna PNG com transparencia."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "image_path": {"type": "string", "description": "Caminho da imagem com fundo"},
                    "output_path": {"type": "string", "description": "Caminho de saida (auto: _nobg)"},
                },
                "required": ["image_path"],
            },
        ),
        Tool(
            name="optimize_sprite",
            description=(
                "Otimiza/compacta sprite PNG usando oxipng (lossless, 10-30% reducao). "
                "Use antes de exportar o jogo para reduzir tamanho final."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "image_path": {"type": "string", "description": "Caminho da imagem PNG a otimizar"},
                    "lossless": {"type": "boolean", "description": "True=oxipng sem perda, False=pngquant (default true)"},
                },
                "required": ["image_path"],
            },
        ),
        Tool(
            name="create_spritesheet",
            description=(
                "Cria sprite sheet a partir de frames individuais. "
                "Use para juntar frames de animacao em uma unica imagem."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "frame_paths": {"type": "array", "items": {"type": "string"}, "description": "Lista de caminhos dos frames"},
                    "output_path": {"type": "string", "description": "Caminho de saida da sprite sheet"},
                    "frame_width": {"type": "integer", "description": "Largura de cada frame (default 64)"},
                    "frame_height": {"type": "integer", "description": "Altura de cada frame (default 64)"},
                    "columns": {"type": "integer", "description": "Numero de colunas (default 4)"},
                    "gap": {"type": "integer", "description": "Espaco entre frames em px (default 0)"},
                },
                "required": ["frame_paths", "output_path"],
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
            name="godot_class_ref",
            description="Consulta metodos, propriedades, sinais, enums e constantes nativos do Godot via ClassDB (extension_api.json). "
                        "Cobre APENAS classes nativas do engine; NAO retorna classes custom do projeto (class_name em scripts .gd). "
                        "Evita alucinacao de API desatualizada. Use antes de gerar codigo contra uma classe desconhecida.",
            inputSchema={
                "type": "object",
                "properties": {
                    "class_name": {"type": "string", "description": "Nome exato da classe nativa (ex: Node2D, CharacterBody2D). Nao funciona com classes custom de projetos."},
                },
                "required": ["class_name"],
            },
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
                    "layers": {"type": "array", "items": {"type": "object"}, "description": "Lista de camadas [{texture, scroll_scale_x, scroll_scale_y, mirroring_x, mirroring_y}]."},
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
                    "waypoints": {"type": "array", "items": {"type": "string"}, "description": "Lista de pontos Vector2 (ex: ['Vector2(0,0)', 'Vector2(100,100)'])."},
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
                    "waypoints": {"type": "array", "items": {"type": "string"}, "description": "Lista de posicoes Vector2."},
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
                    "choices": {"type": "array", "items": {"type": "object"}, "description": "Opcoes do jogador [{text, next_id}]."},
                    "events": {"type": "array", "items": {"type": "object"}, "description": "Eventos disparados [{type, params}]."},
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
        # ── LSP Bridge (Fase 2A / C3) ──────────────────────────
        Tool(
            name="gdscript_lsp_connect",
            description=(
                "Conecta ao Language Server do Godot na porta 6005. "
                "Use no início da sessão, após abrir o editor Godot com o projeto. "
                "Quando NÃO usar: se o editor não estiver aberto (a conexão falhará). "
                "Pré-condições: Godot editor ABERTO com o projeto carregado. "
                "Exemplo: {\"project_root\": \"C:/meu-jogo\"}. "
                "Erro mais comum: conexão recusada — verifique se o Godot está aberto."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "project_root": {"type": "string", "description": "Caminho raiz do projeto (opcional)."},
                },
                "required": [],
            },
        ),
        Tool(
            name="gdscript_lsp_disconnect",
            description=(
                "Desconecta do Language Server do Godot. "
                "Use ao finalizar a sessão ou antes de fechar o editor."
            ),
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="gdscript_references",
            description=(
                "Encontra todas as referências a um símbolo GDScript (variável, função, classe). "
                "Use para rastrear usos antes de renomear ou refatorar. "
                "Pré-condições: LSP conectado via gdscript_lsp_connect. "
                "Exemplo: {\"file_path\": \"scripts/player.gd\", \"line\": 10, \"character\": 5}."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "Caminho do arquivo .gd."},
                    "line": {"type": "integer", "description": "Linha (0-indexed)."},
                    "character": {"type": "integer", "description": "Posição do caractere (0-indexed)."},
                },
                "required": ["file_path", "line", "character"],
            },
        ),
        Tool(
            name="gdscript_definition",
            description=(
                "Navega para a definição de um símbolo GDScript. "
                "Use para encontrar onde uma variável, função ou classe foi declarada. "
                "Pré-condições: LSP conectado."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "Caminho do arquivo .gd."},
                    "line": {"type": "integer", "description": "Linha (0-indexed)."},
                    "character": {"type": "integer", "description": "Posição do caractere (0-indexed)."},
                },
                "required": ["file_path", "line", "character"],
            },
        ),
        Tool(
            name="gdscript_hover",
            description=(
                "Exibe tipo e documentação de um símbolo GDScript sob o cursor. "
                "Use para inspecionar tipo de variável ou assinatura de função. "
                "Pré-condições: LSP conectado."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "Caminho do arquivo .gd."},
                    "line": {"type": "integer", "description": "Linha (0-indexed)."},
                    "character": {"type": "integer", "description": "Posição do caractere (0-indexed)."},
                },
                "required": ["file_path", "line", "character"],
            },
        ),
        Tool(
            name="gdscript_symbols",
            description=(
                "Lista símbolos (funções, classes, variáveis) de um arquivo GDScript. "
                "Use para obter índice estrutural do código. "
                "Pré-condições: LSP conectado."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "Caminho do arquivo .gd."},
                },
                "required": ["file_path"],
            },
        ),
        Tool(
            name="gdscript_rename",
            description=(
                "Renomeia um símbolo GDScript em TODO o projeto com segurança semântica. "
                "Diferente de grep/replace, o LSP entende escopo e não quebra referências. "
                "Quando NÃO usar: se não tiver certeza do escopo (use gdscript_references antes). "
                "Pré-condições: LSP conectado."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "Caminho do arquivo .gd."},
                    "line": {"type": "integer", "description": "Linha (0-indexed)."},
                    "character": {"type": "integer", "description": "Posição do caractere (0-indexed)."},
                    "new_name": {"type": "string", "description": "Novo nome para o símbolo."},
                },
                "required": ["file_path", "line", "character", "new_name"],
            },
        ),
        Tool(
            name="gdscript_diagnostics",
            description=(
                "Retorna erros e warnings do compilador GDScript via LSP. "
                "Mais preciso que validate_gdscript_syntax (tempo real, contextual). "
                "Pré-condições: LSP conectado."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "Caminho do arquivo .gd."},
                },
                "required": ["file_path"],
            },
        ),
        Tool(
            name="gdscript_sync_file",
            description=(
                "Notifica o LSP sobre alterações em um arquivo GDScript. "
                "Use após write_file para manter o LSP sincronizado. "
                "Pré-condições: LSP conectado."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "Caminho do arquivo .gd."},
                    "content": {"type": "string", "description": "Conteúdo atualizado (se omitido, lê do disco)."},
                },
                "required": ["file_path"],
            },
        ),
        # ── Addon Bridge (Fase 2B / A2) ────────────────────────
        Tool(
            name="addon_connect",
            description=(
                "Conecta ao addon GDScript via WebSocket na porta 9082. "
                "Use após abrir o Godot com o addon MCP instalado. "
                "Pré-condições: Godot editor ABERTO com addon MCP ativo."
            ),
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="addon_disconnect",
            description="Desconecta do addon GDScript.",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="addon_is_available",
            description=(
                "Verifica se o addon GDScript está conectado e respondendo. "
                "Use para decidir entre modo editor (addon) ou file-based."
            ),
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="addon_ping",
            description="Verifica se o addon GDScript está respondendo (ping/pong).",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="addon_create_node",
            description=(
                "Cria um nó na cena atual do editor Godot com UndoRedo NATIVO (Ctrl+Z funciona). "
                "Use para adicionar nós visualmente no editor — é a versão ao vivo de node_manage.create. "
                "Quando NÃO usar: se o addon não estiver disponível (use node_manage.create para file-based). "
                "Pré-condições: addon conectado via addon_connect. "
                "Exemplo: {\"parent_path\": \"/root/Main\", \"node_type\": \"Sprite2D\", \"node_name\": \"Player\"}."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "parent_path": {"type": "string", "description": "Path do nó pai (ex: /root/Main)."},
                    "node_type": {"type": "string", "description": "Tipo Godot (ex: Sprite2D)."},
                    "node_name": {"type": "string", "description": "Nome do novo nó."},
                    "properties": {"type": "object", "description": "Propriedades iniciais (opcional)."},
                    "scene_path": {"type": "string", "description": "Cena alvo (opcional)."},
                },
                "required": ["parent_path", "node_type", "node_name"],
            },
        ),
        Tool(
            name="addon_delete_node",
            description=(
                "Remove um nó da cena do editor com UndoRedo nativo. "
                "Pré-condições: addon conectado."
            ),
            inputSchema={
                "type": "object",
                "properties": {"node_path": {"type": "string", "description": "Path absoluto do nó."}},
                "required": ["node_path"],
            },
        ),
        Tool(
            name="addon_set_property",
            description=(
                "Define uma propriedade de nó no editor com UndoRedo nativo. "
                "Use para ajustar posição, escala, cor, etc. com feedback visual imediato. "
                "Pré-condições: addon conectado."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "node_path": {"type": "string", "description": "Path do nó."},
                    "property_name": {"type": "string", "description": "Nome da propriedade."},
                    "value": {"type": "string", "description": "Valor (tipos Godot serializados como JSON)."},
                },
                "required": ["node_path", "property_name", "value"],
            },
        ),
        Tool(
            name="addon_reparent_node",
            description=(
                "Move um nó para outro pai no editor com UndoRedo nativo. "
                "Pré-condições: addon conectado."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "node_path": {"type": "string", "description": "Path do nó a mover."},
                    "new_parent_path": {"type": "string", "description": "Path do novo pai."},
                },
                "required": ["node_path", "new_parent_path"],
            },
        ),
        Tool(
            name="addon_duplicate_node",
            description=(
                "Duplica um nó no editor com UndoRedo nativo. "
                "Pré-condições: addon conectado."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "node_path": {"type": "string", "description": "Path do nó a duplicar."},
                    "new_name": {"type": "string", "description": "Nome da cópia (opcional)."},
                },
                "required": ["node_path"],
            },
        ),
        Tool(
            name="addon_batch_edit",
            description=(
                "Executa MÚLTIPLAS operações no editor em UMA ação UndoRedo. "
                "1 Ctrl+Z desfaz TUDO. Ideal para criar estruturas complexas. "
                "Exemplo: [{\"method\": \"create_node\", \"params\": {...}}, ...]. "
                "Pré-condições: addon conectado."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "operations": {
                        "type": "array",
                        "description": "Lista de operações [{method, params}, ...].",
                        "items": {"type": "object"},
                    },
                },
                "required": ["operations"],
            },
        ),
        Tool(
            name="addon_take_screenshot",
            description=(
                "Captura screenshot do viewport do editor Godot via addon. "
                "Alternativa ao take_screenshot (TCP bridge) — funciona via WebSocket. "
                "Pré-condições: addon conectado."
            ),
            inputSchema={
                "type": "object",
                "properties": {"viewport": {"type": "string", "description": "'editor' (padrão) ou path."}},
                "required": [],
            },
        ),
        Tool(
            name="addon_get_scene_tree",
            description=(
                "Obtém a árvore da cena atual do editor via addon. "
                "Retorna estrutura hierárquica completa com tipos e paths. "
                "Pré-condições: addon conectado."
            ),
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        # ── Playtest (Fase 2B / A3+A4+A5) ──────────────────────
        Tool(
            name="freeze_game_clock",
            description="Congela o relogio do jogo. Use antes de step_game_time para playtesting deterministico.",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="unfreeze_game_clock",
            description="Descongela o relogio do jogo (retoma execucao normal).",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="step_game_time",
            description="Avanca o jogo em N ms e congela novamente. Ex: 500ms = meio segundo de jogo processado.",
            inputSchema={
                "type": "object",
                "properties": {"ms": {"type": "integer", "description": "Milissegundos (default: 16)."}},
                "required": [],
            },
        ),
        Tool(
            name="step_until",
            description="Avanca o jogo ate que uma condicao GDScript seja verdadeira. Com timeout.",
            inputSchema={
                "type": "object",
                "properties": {
                    "condition": {"type": "string", "description": "Expressao GDScript que retorna bool."},
                    "timeout_ms": {"type": "integer", "description": "Timeout em ms (default: 5000)."},
                },
                "required": ["condition"],
            },
        ),
        Tool(
            name="get_runtime_state_digest",
            description="Retorna estado do jogo como JSON: posicao, velocidade, grupos de todas as entidades.",
            inputSchema={
                "type": "object",
                "properties": {"groups": {"type": "array", "items": {"type": "string"}, "description": "Grupos a filtrar."}},
                "required": [],
            },
        ),
        Tool(
            name="capture_runtime_errors",
            description="Captura informacoes de runtime: FPS, contagem de objetos, estado da arvore.",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        # ── Playtest Onda 1 (watch_state, godot_exec, effect_probe) ──
        Tool(
            name="watch_state_start",
            description="Comeca a observar propriedades de nos do jogo a cada step. "
                        "Use para monitorar HP, posicao, velocidade durante playtesting. "
                        "Depois colete com watch_state_collect().",
            inputSchema={
                "type": "object",
                "properties": {
                    "targets": {"type": "array", "items": {"type": "object"}},
                    "interval_steps": {"type": "integer"},
                },
                "required": ["targets"],
            },
        ),
        Tool(
            name="watch_state_collect",
            description="Coleta o historico de estados observados desde watch_state_start(). "
                        "Retorna array de snapshots com timestamp e valores das propriedades.",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="godot_exec",
            description="Executa codigo GDScript DENTRO do jogo rodando. "
                        "Use para setup de cenarios de teste: spawnar inimigos, modificar estado. "
                        "Use 'return' para obter valores.",
            inputSchema={
                "type": "object",
                "properties": {"code": {"type": "string", "description": "Codigo GDScript a executar no jogo"}},
                "required": ["code"],
            },
        ),
        Tool(
            name="effect_probe",
            description="Verifica se uma acao no jogo produziu o efeito esperado. "
                        "Avalia expressao antes, executa acao, avalia depois, compara. "
                        "Ideal para testar: 'o dano reduziu o HP?', 'o pulo aumentou a posicao Y?'",
            inputSchema={
                "type": "object",
                "properties": {
                    "before": {"type": "string", "description": "Expressao GDScript antes da acao"},
                    "action": {"type": "string", "description": "Codigo GDScript da acao"},
                    "after": {"type": "string", "description": "Expressao GDScript depois da acao"},
                    "wait_ms": {"type": "integer", "description": "ms de espera entre acao e verificacao"},
                },
                "required": ["before", "action", "after"],
            },
        ),
        # ── Balance Onda 1 ──────────────────────────────────────
        Tool(
            name="balance_analyze",
            description="Analisa o balanceamento do jogo e sugere ajustes. "
                        "Calcula DPS necessario, verifica se o jogo eh 'vencivel', "
                        "detecta torres com custo-beneficio ruim, inimigos desbalanceados.",
            inputSchema={
                "type": "object",
                "properties": {
                    "game_type": {"type": "string", "enum": ["tower_defense", "rpg", "platformer", "shooter"]},
                    "towers": {"type": "array", "items": {"type": "object"}},
                    "enemies": {"type": "array", "items": {"type": "object"}},
                    "waves": {"type": "integer"},
                    "target_duration_minutes": {"type": "integer"},
                },
                "required": [],
            },
        ),
        Tool(
            name="wave_generate",
            description="Gera composicao de ondas para tower defense. "
                        "Curva de dificuldade (linear, exponential, staircase). "
                        "Chefoes a cada N waves. Use para planejar as waves do jogo.",
            inputSchema={
                "type": "object",
                "properties": {
                    "wave_count": {"type": "integer"},
                    "enemy_types": {"type": "array", "items": {"type": "object"}},
                    "difficulty_curve": {"type": "string", "enum": ["linear", "exponential", "staircase"]},
                    "boss_every": {"type": "integer"},
                },
                "required": [],
            },
        ),
        Tool(
            name="dps_calculator",
            description="Calcula DPS efetivo de uma torre/arma considerando criticos, "
                        "dano em area e dano continuo (DoT). Retorna Time-To-Kill para HPs de referencia.",
            inputSchema={
                "type": "object",
                "properties": {
                    "damage": {"type": "number"},
                    "fire_rate": {"type": "number"},
                    "crit_chance": {"type": "number"},
                    "crit_multiplier": {"type": "number"},
                    "aoe_radius": {"type": "number"},
                    "aoe_targets": {"type": "integer"},
                    "damage_over_time": {"type": "number"},
                    "dot_duration": {"type": "number"},
                },
                "required": ["damage", "fire_rate"],
            },
        ),
        Tool(
            name="loot_table_generate",
            description="Gera tabela de loot balanceada com chances de drop por raridade. "
                        "Suporta temas: scifi, fantasy, modern, post_apocalyptic.",
            inputSchema={
                "type": "object",
                "properties": {
                    "rarity_levels": {"type": "array", "items": {"type": "string"}},
                    "items_per_rarity": {"type": "integer"},
                    "game_theme": {"type": "string", "enum": ["scifi", "fantasy", "modern", "post_apocalyptic"]},
                },
                "required": [],
            },
        ),
        # ── GDD Generator (Onda 2) ──────────────────────────────
        Tool(
            name="gdd_generate",
            description="Gera Game Design Document (GDD) completo a partir de uma ideia. "
                        "Suporta: tower_defense, platformer, rpg, shooter, puzzle, roguelike. "
                        "Niveis de detalhe: brief (1 pagina) ou full (completo com historia, "
                        "monetizacao, marketing e roadmap). GRATIS — sem API externa.",
            inputSchema={
                "type": "object",
                "properties": {
                    "concept": {"type": "string", "description": "Ideia do jogo em uma frase"},
                    "game_type": {"type": "string", "enum": ["tower_defense","platformer","rpg","shooter","puzzle","roguelike"]},
                    "target_platform": {"type": "string", "enum": ["pc","mobile","web"]},
                    "detail_level": {"type": "string", "enum": ["brief","full"]},
                },
                "required": ["concept"],
            },
        ),
        # ── Behavior Trees (Onda 2) ─────────────────────────────
        Tool(
            name="behavior_tree_generate",
            description="Gera Behavior Tree completa em GDScript a partir de descricao em portugues. "
                        "Analisa texto como 'patrulha, detecta, persegue, ataca, foge' e gera codigo "
                        "com Selector/Sequence, acoes e condicoes. Zero custo — puro Python.",
            inputSchema={
                "type": "object",
                "properties": {
                    "description": {"type": "string", "description": "Comportamento em portugues"},
                    "behavior_name": {"type": "string", "description": "Nome da classe (ex: EnemyAI)"},
                    "tree_type": {"type": "string", "enum": ["selector","sequence"]},
                    "save_path": {"type": "string"},
                },
                "required": ["description"],
            },
        ),
        Tool(
            name="behavior_tree_list_templates",
            description="Lista templates de Behavior Tree disponiveis: patrol_chase_attack, "
                        "patrol_chase_attack_flee, guard_alert_chase, idle_wander_flee, boss_phases.",
            inputSchema={"type": "object", "properties": {}},
        ),
        # ── Performance Profiler (Onda 2) ───────────────────────
        Tool(
            name="profile_frame",
            description="Analisa performance do jogo rodando: FPS medio/min/max, draw calls, "
                        "uso de memoria e nos na cena. Sugere otimizacoes especificas. "
                        "Nota A (otimo) ate D (critico). GRATIS — sem API externa.",
            inputSchema={
                "type": "object",
                "properties": {"sample_frames": {"type": "integer", "description": "Frames para amostrar (default 60)"}},
                "required": [],
            },
        ),
        Tool(
            name="profile_memory",
            description="Analisa uso de memoria do jogo (estatica + video) e detecta objetos. "
                        "GRATIS — sem API externa.",
            inputSchema={
                "type": "object",
                "properties": {"track_objects": {"type": "boolean", "description": "Contar objetos por tipo"}},
                "required": [],
            },
        ),
        # ── Shader NL (Onda 3) ──────────────────────────────────
        Tool(
            name="shader_generate",
            description="Gera arquivo .gdshader a partir de descricao em portugues. "
                        "15 templates 2D: glow, dissolve, water, wind, hologram, forcefield, "
                        "outline, pixelate, chromatic_aberration, heat_distortion, toon, "
                        "grayscale, neon_pulse, frost, invisibility. GRATIS — sem API.",
            inputSchema={
                "type": "object",
                "properties": {
                    "description": {"type": "string", "description": "Efeito visual desejado. Ex: 'holograma azul com scanlines'"},
                    "shader_type": {"type": "string", "enum": ["canvas_item","spatial","particles","sky"]},
                    "save_path": {"type": "string"},
                },
                "required": ["description"],
            },
        ),
        Tool(
            name="shader_list_templates",
            description="Lista 15 templates de shader 2D disponiveis com palavras-chave.",
            inputSchema={"type": "object", "properties": {}},
        ),
        # ── World Generation (Onda 3) ───────────────────────────
        Tool(
            name="terrain_generate",
            description="Gera terreno procedural com biomas por altura/umidade. "
                        "Usa FastNoiseLite (built-in Godot). Retorna JSON com seed, "
                        "distribuicao de biomas e parametros de noise. GRATIS.",
            inputSchema={
                "type": "object",
                "properties": {
                    "width": {"type": "integer"}, "height": {"type": "integer"},
                    "seed": {"type": "integer"}, "biomes": {"type": "array", "items": {"type": "string"}},
                    "water_level": {"type": "number"}, "mountain_level": {"type": "number"},
                    "save_path": {"type": "string"},
                },
                "required": [],
            },
        ),
        Tool(
            name="dungeon_generate",
            description="Gera dungeon procedural com salas e corredores (algoritmo BSP). "
                        "Salas classificadas como combat, treasure, boss, start, empty. GRATIS.",
            inputSchema={
                "type": "object",
                "properties": {
                    "rooms": {"type": "integer"}, "min_room_size": {"type": "integer"},
                    "max_room_size": {"type": "integer"}, "seed": {"type": "integer"},
                    "save_path": {"type": "string"},
                },
                "required": [],
            },
        ),
        Tool(
            name="world_describe",
            description="Analisa um mundo gerado e sugere melhorias e pontos de interesse. "
                        "Detecta biomas e recomenda elementos de gameplay.",
            inputSchema={
                "type": "object",
                "properties": {"terrain_path": {"type": "string"}},
                "required": [],
            },
        ),
        # ── 3D Asset Generation (Onda 3) ────────────────────────
        Tool(
            name="generate_3d_placeholder",
            description="Gera placeholder 3D procedural (box, sphere, cylinder, cone, pyramid). "
                        "Preview PNG + codigo de cena Godot .tscn. GRATIS — Pillow.",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string"}, "shape": {"type": "string", "enum": ["box","sphere","cylinder","cone","pyramid"]},
                    "color": {"type": "string"}, "size": {"type": "number"}, "save_path": {"type": "string"},
                },
                "required": ["name"],
            },
        ),
        Tool(
            name="generate_3d_asset",
            description="Gera asset 3D via API Hyper3D Rodin (⚠️💰 ~$0.05/modelo) ou placeholder GRATIS. "
                        "SEM custo se HYPER3D_API_KEY nao configurada. Categorias: prop, character, vehicle, building, weapon.",
            inputSchema={
                "type": "object",
                "properties": {
                    "description": {"type": "string"}, "category": {"type": "string", "enum": ["prop","character","vehicle","building","weapon"]},
                    "style": {"type": "string", "enum": ["scifi","fantasy","modern","realistic"]}, "save_path": {"type": "string"},
                },
                "required": ["description"],
            },
        ),
        # ── Deploy + Marketplace (Onda 4 — FINAL) ────────────────
        Tool(
            name="deploy_itch",
            description="Exporta e envia o jogo para itch.io via butler CLI. "
                        "Suporta Windows, Linux, Web, macOS, Android. GRATIS.",
            inputSchema={
                "type": "object",
                "properties": {"itch_username": {"type": "string"}, "itch_game": {"type": "string"},
                    "platforms": {"type": "array", "items": {"type": "string"}},
                    "version": {"type": "string"}, "dry_run": {"type": "boolean"}},
                "required": [],
            },
        ),
        Tool(
            name="release_checklist",
            description="Verifica se o projeto esta pronto para lancamento (nota 0-10): "
                        "project.godot, main scene, scripts, assets, audio, export presets, "
                        "gitignore, readme, license, tamanho. GRATIS.",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="auto_screenshot",
            description="Gera screenshots automaticas do jogo rodando para loja (itch.io/Steam). GRATIS.",
            inputSchema={
                "type": "object",
                "properties": {"count": {"type": "integer"}, "delay_between": {"type": "number"}, "save_dir": {"type": "string"}},
                "required": [],
            },
        ),
        Tool(
            name="marketplace_search",
            description="Busca assets em marketplaces gratuitos: Kenney.nl (CC0, 300+ packs), "
                        "Godot Asset Library, OpenGameArt, Poly Haven. GRATIS.",
            inputSchema={
                "type": "object",
                "properties": {"query": {"type": "string"},
                    "source": {"type": "string", "enum": ["kenney","godot_assets","opengameart","polyhaven"]},
                    "category": {"type": "string"}},
                "required": [],
            },
        ),
        Tool(
            name="marketplace_download",
            description="Baixa asset gratuito do marketplace. Kenney.nl (ZIP direto, CC0). GRATIS.",
            inputSchema={
                "type": "object",
                "properties": {"source": {"type": "string", "enum": ["kenney","godot_assets","polyhaven"]},
                    "slug": {"type": "string"}, "save_to": {"type": "string"}},
                "required": ["slug"],
            },
        ),
        # ── Juice (Onda 5) ─────────────────────────────────────
        Tool(
            name="juice_apply",
            description="Aplica tecnicas de game feel/polish profissional: coyote time, "
                        "input buffer, hit-stop, screen shake, squash & stretch, easing. "
                        "Presets: full, platformer, action, minimal. Gera script GDScript pronto. GRATIS.",
            inputSchema={
                "type": "object",
                "properties": {"preset": {"type": "string", "enum": ["full","platformer","action","minimal"]},
                              "save_to_script": {"type": "string"}},
                "required": [],
            },
        ),
        Tool(
            name="juice_list_presets",
            description="Lista presets de juice disponiveis com tecnicas incluidas.",
            inputSchema={"type": "object", "properties": {}},
        ),
        # ── Auto-Config (Fase 2C) ───────────────────────────────
        Tool(
            name="validate_mcp_environment",
            description="Verifica se o ambiente MCP esta pronto: Python, dependencias, server.py.",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="setup_mcp_config",
            description="Gera arquivo de configuracao MCP para VS Code Copilot, Claude ou Cursor.",
            inputSchema={
                "type": "object",
                "properties": {
                    "target": {"type": "string", "enum": ["vscode", "claude", "cursor", "all"],
                               "description": "Cliente alvo (default: vscode)."},
                },
                "required": [],
            },
        ),
        # ── Pipeline Executor (Onda 7) ──────────────────────────
        Tool(
            name="create_entity",
            description="Cria uma entidade COMPLETA: cena + collider + script + sprite + audio. "
                        "Decide automaticamente o que gerar. Use para inimigos, players, NPCs, itens. "
                        "Exemplo: {'name': 'Slime', 'entity_type': 'enemy', 'behavior': 'patrol'}.",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Nome da entidade (ex: Slime, Player, Turret)."},
                    "entity_type": {"type": "string", "enum": ["enemy", "player", "tower", "npc", "item", "projectile"],
                                    "description": "Tipo de entidade."},
                    "description": {"type": "string", "description": "Descricao do comportamento."},
                    "behavior": {"type": "string", "enum": ["patrol", "chase", "idle", "none"],
                                 "description": "Comportamento IA."},
                    "generate_art": {"type": "boolean", "description": "Forcar geracao de arte (null=auto)."},
                    "generate_audio": {"type": "boolean", "description": "Forcar geracao de audio (null=auto)."},
                    "art_style": {"type": "string", "enum": ["scifi", "fantasy", "pixel", "cartoon"],
                                  "description": "Estilo visual."},
                    "save_path": {"type": "string", "description": "Caminho para salvar a cena."},
                },
                "required": ["name"],
            },
        ),
        Tool(
            name="project_status",
            description="Status completo do projeto: cenas, scripts, sprites, audio, assets faltantes, "
                        "sugestoes do que criar a seguir. Use para diagnosticar o estado do jogo.",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        # ── Orquestrador Genius (Onda 7) ──────────────────────
        Tool(
            name="circuit_breaker_status",
            description="Status dos circuit breakers das APIs externas (FLUX, Replicate, Edge TTS). "
                        "Use para verificar se alguma API está temporariamente bloqueada.",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        # ── PATCH 12: Runtime Bridge ──────────────────────────
        Tool(
            name="godot_screenshot",
            description="Captura screenshot do jogo rodando via MCPRuntimeBridge. Jogo precisa estar em execucao (debug).",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="godot_runtime_info",
            description="FPS, draw calls, memoria estatica e tempo de fisica do jogo rodando agora.",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="godot_custom_command",
            description="Chama comando customizado registrado no jogo (ex: get_puzzle_state).",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Nome do comando registrado no jogo."},
                    "args": {"type": "object", "description": "Argumentos do comando (opcional)."},
                },
                "required": ["name"],
            },
        ),
        Tool(
            name="godot_list_custom_commands",
            description="Lista comandos customizados registrados no bridge do jogo.",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="godot_run_project",
            description="Lanca o jogo direto via CLI (godot --path <projeto>), sem abrir o editor. Retorna pid.",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_path": {"type": "string", "description": "Caminho absoluto da pasta do projeto."},
                    "godot_executable": {"type": "string", "description": "Caminho absoluto do executavel do Godot."},
                },
                "required": ["project_path", "godot_executable"],
            },
        ),
        Tool(
            name="godot_stop_project",
            description="Encerra um processo de jogo iniciado por godot_run_project.",
            inputSchema={
                "type": "object",
                "properties": {
                    "pid": {"type": "integer", "description": "PID retornado por godot_run_project."},
                },
                "required": ["pid"],
            },
        ),
        Tool(
            name="godot_wait_for_bridge",
            description="Espera ate o MCPRuntimeBridge responder (polling de runtime_info).",
            inputSchema={
                "type": "object",
                "properties": {
                    "timeout_sec": {"type": "integer", "description": "Timeout em segundos (default 10)."},
                },
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
        # LSP Bridge (C3)
        "gdscript_references", "gdscript_definition",
        "gdscript_hover", "gdscript_symbols", "gdscript_diagnostics",
        # Orquestrador Genius (Onda 7)
        "circuit_breaker_status",
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
        "generate_game_art", "apply_game_art",
        # LSP Bridge (C3)
        "gdscript_rename",
        # Addon Bridge (Fase 2B / A2)
        "addon_create_node", "addon_delete_node", "addon_set_property",
        "addon_reparent_node", "addon_duplicate_node", "addon_batch_edit",
    }
    _IDEMPOTENT = _READONLY | {
        "set_project_setting", "set_main_scene", "configure_input_action",
        "configure_autoload", "set_collision_layer_mask", "set_node_property",
        "create_project", "set_active_project",
        # LSP Bridge (C3)
        "gdscript_sync_file",
        # Orquestrador Genius (Onda 7)
        "circuit_breaker_status",
    }
    # ── Annotations (Onda 6): titles em PT-BR + tags ────────────────
    _TITLES = {
        "ping": "Ping — Verificar Conexão",
        "validate_godot_version": "Validar Versão do Godot",
        "read_file": "Ler Arquivo",
        "write_file": "Escrever Arquivo",
        "query_classdb": "Consultar ClassDB",
        "list_valid_node_types": "Listar Tipos de Nó Válidos",
        "take_screenshot": "Capturar Screenshot (Editor)",
        "read_console_output": "Ler Console",
        "inject_input_event": "Injetar Evento de Input",
        "execute_gdscript_runtime": "Executar GDScript (Runtime)",
        "watch_signal": "Observar Sinal",
        "capture_game_screenshot": "Capturar Screenshot do Jogo",
        "add_nodes_batch": "Adicionar Nós em Lote",
        "set_properties_batch": "Definir Propriedades em Lote",
        "generate_audio_sfx": "Gerar Efeito Sonoro (SFX)",
        "create_animation_tree": "Criar AnimationTree",
        "create_joint_2d": "Criar Junta 2D",
        "import_3d_model": "Importar Modelo 3D",
        "create_particles_2d": "Criar Partículas 2D",
        "create_light_2d": "Criar Luz 2D",
        "generate_project_structure": "Gerar Estrutura do Projeto",
        "record_gameplay_gif": "Gravar Gameplay (GIF)",
        "create_parallax_background": "Criar Fundo Parallax",
        "add_parallax_layer": "Adicionar Camada Parallax",
        "configure_particles_2d": "Configurar Partículas 2D",
        "create_particles_3d": "Criar Partículas 3D",
        "generate_shader_2d": "Gerar Shader 2D",
        "create_path_2d": "Criar Path 2D",
        "create_patrol_route": "Criar Rota de Patrulha",
        "create_bullet_template": "Criar Template de Projétil",
        "create_gun_system": "Criar Sistema de Arma",
        "generate_dungeon_rooms": "Gerar Salas de Dungeon",
        "load_scene_async": "Carregar Cena Assíncrono",
        "add_raycast_2d": "Adicionar RayCast2D",
        "add_shapecast_2d": "Adicionar ShapeCast2D",
        "setup_localization": "Configurar Localização (i18n)",
        "add_translation_string": "Adicionar String Traduzida",
        "create_light_3d": "Criar Luz 3D",
        "configure_standard_material_3d": "Configurar Material 3D",
        "configure_export_preset": "Configurar Preset de Exportação",
        "health_check": "Verificação de Saúde",
        "self_test": "Auto-Teste do MCP",
        "generate_game_art": "Gerar Arte do Jogo (IA)",
        "apply_game_art": "Aplicar Arte no Jogo",
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
        "generate_game_art": ["arte", "ia", "assets", "dalle"],
        "apply_game_art": ["arte", "godot", "animação"],
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
        # LSP Bridge (C3)
        "gdscript_lsp_connect": ["lsp", "conexão", "godot"],
        "gdscript_lsp_disconnect": ["lsp", "conexão"],
        "gdscript_references": ["lsp", "análise", "gdscript"],
        "gdscript_definition": ["lsp", "análise", "gdscript"],
        "gdscript_hover": ["lsp", "análise", "gdscript"],
        "gdscript_symbols": ["lsp", "análise", "gdscript"],
        "gdscript_rename": ["lsp", "refatoração", "gdscript"],
        "gdscript_diagnostics": ["lsp", "diagnóstico", "gdscript"],
        "gdscript_sync_file": ["lsp", "sync", "gdscript"],
        # Addon Bridge (Fase 2B)
        "addon_connect": ["addon", "conexão", "websocket"],
        "addon_disconnect": ["addon", "conexão"],
        "addon_is_available": ["addon", "diagnóstico"],
        "addon_ping": ["addon", "diagnóstico"],
        "addon_create_node": ["addon", "editor", "undo"],
        "addon_delete_node": ["addon", "editor", "undo"],
        "addon_set_property": ["addon", "editor", "undo"],
        "addon_reparent_node": ["addon", "editor", "undo"],
        "addon_duplicate_node": ["addon", "editor", "undo"],
        "addon_batch_edit": ["addon", "editor", "batch", "undo"],
        "addon_take_screenshot": ["addon", "screenshot", "visão"],
        "addon_get_scene_tree": ["addon", "cena", "debug"],
        # Playtest (Fase 2B)
        "freeze_game_clock": ["playtest", "clock", "debug"],
        "unfreeze_game_clock": ["playtest", "clock"],
        "step_game_time": ["playtest", "clock", "deterministico"],
        "step_until": ["playtest", "clock", "condicional"],
        "get_runtime_state_digest": ["playtest", "state", "json"],
        "capture_runtime_errors": ["playtest", "debug", "diagnostico"],
    }
    # ── Hints: openWorldHint (Fase 2A / C4) ─────────────────────
    # Tools que NÃO são puro servidor interagem com mundo externo.
    _SERVER_ONLY = {"ping", "health_check", "self_test"}
    _CORE_TOOLS = {
        "ping", "health_check", "self_test", "bootstrap_godot_mcp",
        "query_classdb", "read_file", "write_file",
        "project_manage", "scene_manage", "node_manage", "script_manage",
        "file_manage", "runtime_manage", "take_screenshot",
    }
    for t in _TOOL_DEFS_CACHE:
        if t.name in _READONLY:
            t.readOnlyHint = True
        if t.name in _DESTRUCTIVE:
            t.destructiveHint = True
        if t.name in _IDEMPOTENT:
            t.idempotentHint = True
        if t.name not in _SERVER_ONLY:
            t.openWorldHint = True
        if hasattr(t, 'inputSchema') and isinstance(t.inputSchema, dict):
            if "additionalProperties" not in t.inputSchema:
                t.inputSchema["additionalProperties"] = False
        # ── Annotations Onda 6 ──────────────────────────────────
        if t.name in _TITLES:
            t.title = _TITLES[t.name]
        if t.name in _TAGS:
            t.annotations = {"tags": _TAGS[t.name]}
        # ── B6: Read/Write Split ────────────────────────────────
        cat = _classify_operation(t.name)
        if t.annotations:
            t.annotations["operationCategory"] = cat
        else:
            t.annotations = {"operationCategory": cat}
        # ── M3: Defer Loading ───────────────────────────────────
        if t.name not in _CORE_TOOLS:
            t.annotations["deferLoading"] = True
    # ── Fim pós-processamento ──────────────────────────────────────

    # ── Rollups Fase 2A / C1 ───────────────────────────────────────
    # Domain rollups: colapsam múltiplas tools em <domain>_manage.
    # Adicionados APÓS o pós-processamento pois já trazem seus próprios hints.
    try:
        from tools.rollups import get_rollup_tool_defs
        _TOOL_DEFS_CACHE.extend(get_rollup_tool_defs())
    except Exception:
        pass  # Rollups são bônus — se falhar, server ainda funciona sem eles

    # ── B6: Read/Write Split para rollups ───────────────────────────
    for t in _TOOL_DEFS_CACHE:
        cat = _classify_operation(t.name)
        if t.annotations:
            t.annotations["operationCategory"] = cat
        else:
            t.annotations = {"operationCategory": cat}

    # ── M3: Defer Loading para rollups ─────────────────────────────
    for t in _TOOL_DEFS_CACHE:
        if t.name not in _CORE_TOOLS:
            if t.annotations:
                t.annotations["deferLoading"] = True
            else:
                t.annotations = {"deferLoading": True}

    # ── Output Schema (Fase 2A / C5) ────────────────────────────────
    # Schema padrão para 90%+ das tools. Ferramentas com formato
    # específico são sobrescritas pelo dict _OUTPUT_SCHEMAS.
    _STANDARD_OUTPUT = {
        "type": "object",
        "properties": {
            "status": {
                "type": "string",
                "enum": ["success", "error"],
                "description": (
                    "Resultado da operação: 'success' para sucesso, "
                    "'error' para falha."
                ),
            },
            "message": {
                "type": "string",
                "description": (
                    "Mensagem descritiva. Presente em caso de erro "
                    "ou informação adicional."
                ),
            },
            "error_code": {
                "type": "integer",
                "description": "Código numérico do erro (apenas quando status='error').",
            },
        },
        "required": ["status"],
        "additionalProperties": True,
    }
    _OUTPUT_SCHEMAS: dict[str, dict] = {
        "ping": {
            "type": "object",
            "properties": {
                "status": {"type": "string", "enum": ["success"]},
                "server": {"type": "string", "description": "Nome do servidor MCP."},
                "version": {"type": "string", "description": "Versão do servidor."},
                "tools_count": {"type": "integer", "description": "Número de ferramentas disponíveis."},
                "message": {"type": "string"},
            },
            "required": ["status", "server", "version", "tools_count"],
        },
        "take_screenshot": {
            "type": "object",
            "properties": {
                "status": {"type": "string", "enum": ["success", "error"]},
                "path": {"type": "string", "description": "Caminho do arquivo PNG salvo."},
                "width": {"type": "integer", "description": "Largura em pixels."},
                "height": {"type": "integer", "description": "Altura em pixels."},
                "message": {"type": "string"},
            },
            "required": ["status"],
        },
        "read_file": {
            "type": "object",
            "properties": {
                "status": {"type": "string", "enum": ["success", "error"]},
                "content": {"type": "string", "description": "Conteúdo do arquivo."},
                "path": {"type": "string", "description": "Caminho do arquivo lido."},
                "message": {"type": "string"},
            },
            "required": ["status"],
        },
        "read_console_output": {
            "type": "object",
            "properties": {
                "status": {"type": "string", "enum": ["success", "error"]},
                "output": {"type": "string", "description": "Texto da saída do console."},
                "lines": {"type": "integer", "description": "Número de linhas retornadas."},
                "message": {"type": "string"},
            },
            "required": ["status"],
        },
        "capture_game_screenshot": {
            "type": "object",
            "properties": {
                "status": {"type": "string", "enum": ["success", "error"]},
                "path": {"type": "string", "description": "Caminho do arquivo PNG."},
                "message": {"type": "string"},
            },
            "required": ["status"],
        },
        "generate_game_art": {
            "type": "object",
            "properties": {
                "status": {"type": "string", "enum": ["success", "error"]},
                "frame_paths": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Lista de caminhos dos frames gerados.",
                },
                "prompt": {"type": "string", "description": "Prompt usado para geração."},
                "message": {"type": "string"},
            },
            "required": ["status"],
        },
        "query_classdb": {
            "type": "object",
            "properties": {
                "status": {"type": "string", "enum": ["success", "error"]},
                "results": {
                    "type": "array",
                    "items": {"type": "object"},
                    "description": "Lista de classes encontradas.",
                },
                "count": {"type": "integer", "description": "Número de resultados."},
                "message": {"type": "string"},
            },
            "required": ["status"],
        },
        "inspect_project": {
            "type": "object",
            "properties": {
                "status": {"type": "string", "enum": ["success", "error"]},
                "scenes": {"type": "array", "items": {"type": "string"}},
                "scripts": {"type": "array", "items": {"type": "string"}},
                "assets": {"type": "array", "items": {"type": "string"}},
                "message": {"type": "string"},
            },
            "required": ["status"],
        },
    }
    for t in _TOOL_DEFS_CACHE:
        if t.name in _OUTPUT_SCHEMAS:
            t.outputSchema = _OUTPUT_SCHEMAS[t.name]

    # ── Depreciação: tools substituídas por rollups (Fase 2A) ──
    # Estas 69 tools foram colapsadas nos 16 <domain>_manage rollups.
    # As funções subjacentes CONTINUAM existindo — só a definição
    # da tool individual é removida para reduzir o tool count.
    _DEPRECATED = {
        "add_audio_effect", "add_collision_shape", "add_control_node",
        "add_node", "add_script_signal", "add_script_variable",
        "add_state_transition", "attach_script", "build_export",
        "chain_tweens", "configure_audio_bus", "configure_autoload",
        "configure_input_action", "configure_standard_material_3d",
        "connect_signal", "create_animation", "create_animation_player",
        "create_csg_shape", "create_health_bar", "create_hud_template",
        "create_joint_2d", "create_light_3d", "create_loading_screen",
        "create_main_menu", "create_particles_3d", "create_pause_menu",
        "create_project", "create_save_system", "create_scene",
        "create_state_machine", "create_tilemap_layer", "create_tileset",
        "create_tween_animation", "create_ui_scene", "define_save_data",
        "delete_file", "delete_node", "detach_script",
        "enable_debug_collisions", "enable_debug_navigation",
        "generate_background_gradient", "generate_gdscript",
        "generate_placeholder_sprite", "generate_placeholder_texture_atlas",
        "generate_tilemap_from_noise", "generate_tileset_from_colors",
        "get_node_property", "get_performance_stats",
        "get_project_settings", "import_audio", "import_sprite_sheet",
        "import_texture", "inspect_project", "instance_scene_as_child",
        "list_export_presets", "list_signals", "load_scene_tree",
        "move_file", "paint_tilemap_cell", "reparent_node",
        "set_active_project", "set_collision_layer_mask",
        "set_main_scene", "set_node_property", "set_physics_material",
        "set_project_setting", "suggest_color_palette",
        "validate_export_templates_installed", "validate_gdscript_syntax",
        # Onda Extra
        "compile_test", "run_game", "stop_game", "smart_restart",
        "launch_editor", "close_editor",
        "setup_camera_2d", "setup_camera_follow", "setup_camera_shake",
        "create_navigation_region_2d", "create_navigation_agent_2d",
        "bake_navigation_polygon",
        "create_dialogue_system", "add_dialogue_node", "create_dialogue_ui",
        "create_inventory_system", "define_inventory_item", "create_inventory_ui",
        "configure_particles_2d", "create_particles_2d", "create_light_2d",
        "setup_screen_flash", "setup_world_environment",
        "generate_shader_2d", "apply_shader_to_node", "create_shader_material",
        "analyze_game_structure", "suggest_next_steps",
        "find_missing_references", "validate_game_design",
        "estimate_game_scope", "search_codebase", "get_project_history",
        "list_backups", "restore_backup", "git_commit_checkpoint",
        "undo_last_action", "get_undo_history",
        "compare_screenshots", "detect_empty_screen", "detect_offscreen_elements",
    }
    _TOOL_DEFS_CACHE = [t for t in _TOOL_DEFS_CACHE if t.name not in _DEPRECATED]

    # ── PATCH 17: Filtrar por --toolsets se ativo ──
    if _ENABLED_TOOLS is not None:
        _TOOL_DEFS_CACHE = [t for t in _TOOL_DEFS_CACHE if t.name in _ENABLED_TOOLS]

    # ── Pós-processador: garantir 4 hints em 100% das tools ──
    _TOOL_DEFS_CACHE = _apply_hints(_TOOL_DEFS_CACHE)

    # ── Onda 5: compactar descricoes ────────────────────────
    _TOOL_DEFS_CACHE = _compact_all_tool_descriptions(_TOOL_DEFS_CACHE)

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

    # Onda 5: cache wrappers para handlers de leitura pesada
    from tools.cache_utils import cached_tool

    _HANDLERS_CACHE = {
        "ping": _handle_ping,
        "validate_godot_version": _handle_validate_godot_version,
        "read_file": _handle_read_file,
        "write_file": _handle_write_file,
        # Fase 2: ClassDB (com cache Onda 5)
        "query_classdb": cached_tool("query_classdb", _handle_query_classdb),
        "search_classdb": cached_tool("search_classdb", _handle_search_classdb),
        "download_asset": _handle_download_asset,
        "import_downloaded_asset": _handle_import_downloaded_asset,
        "workflow_snapshot": _handle_workflow_snapshot,
        "workflow_handoff": _handle_workflow_handoff,
        "project_map": _handle_project_map,
        "configure_security": _handle_configure_security,
        "security_status": _handle_security_status,
        "run_gut_tests": _handle_run_gut_tests,
        "assert_node_exists": _handle_assert_node_exists,
        "simulate_input_sequence": _handle_simulate_input_sequence,
        "vibe_coding_mode": _handle_vibe_coding_mode,
        "get_vibe_context": _handle_get_vibe_context,
        "debugger_set_breakpoint": _handle_debugger_set_breakpoint,
        "debugger_status": _handle_debugger_status,
        "debugger_step": _handle_debugger_step,
        "debugger_get_stack": _handle_debugger_get_stack,
        "debugger_get_variables": _handle_debugger_get_variables,
        "game_http_request": _handle_game_http_request,
        "game_multiplayer": _handle_game_multiplayer,
        "set_safety_policy": _handle_set_safety_policy,
        "get_audit_log": _handle_get_audit_log,
        "get_audit_replay": _handle_get_audit_replay,
        "safe_write_gdscript": _handle_safe_write_gdscript,
        "tool_catalog": _handle_tool_catalog,
        "tool_groups": _handle_tool_groups,
        "game_serialize_state": _handle_game_serialize_state,
        "start_recording": _handle_start_recording,
        "stop_recording": _handle_stop_recording,
        "game_call_method": _handle_game_call_method,
        "game_spawn_node": _handle_game_spawn_node,
        "game_raycast": _handle_game_raycast,
        "game_get_camera": _handle_game_get_camera,
        "game_play_animation": _handle_game_play_animation,
        "game_find_nodes_by_class": _handle_game_find_nodes_by_class,
        "game_await_signal": _handle_game_await_signal,
        "game_pause": _handle_game_pause,
        "game_performance": _handle_game_performance,
        "game_window": _handle_game_window,
        "game_input_state": _handle_game_input_state,
        "generate_ci_snippet": _handle_generate_ci_snippet,
        "resource_dependency_graph": _handle_resource_dependency_graph,
        "build_csharp": _handle_build_csharp,
        "list_valid_node_types": _handle_list_valid_node_types,
        # Fase 2: Cenas extendidas
        # Fase 2: Scripts
        # Fase 2: Física
        # Fase 2: Assets
        # Fase 2: Input e Autoload
        "install_mcp_addon": _handle_install_mcp_addon,
        "bootstrap_godot_mcp": _handle_bootstrap_godot_mcp,
        "godot_keep_alive": godot_keep_alive,
        # Fase 2: Runtime
        # Fase 3: Editor
        "take_screenshot": _handle_take_screenshot,
        "read_console_output": _handle_read_console_output,
        # Fase 4: Tilemap, Animação, UI
        # Fase 5: Export, Segurança
        # Game Bridge
        "inject_input_event": _handle_inject_input_event,
        "execute_gdscript_runtime": _handle_execute_gdscript_runtime,
        "watch_signal": _handle_watch_signal,
        # Onda 1: Visão
        "capture_game_screenshot": _handle_capture_game_screenshot,
        # Onda 2: Batch
        "add_nodes_batch": _handle_add_nodes_batch,
        "set_properties_batch": _handle_set_properties_batch,
        "batch_atomic_edit": _handle_batch_atomic_edit,
        # Onda 12: Arte IA (ChatGPT/DALL-E + Pillow procedural)
        "generate_game_art": _handle_generate_game_art,
        "apply_game_art": _handle_apply_game_art,
        # Pacote C: Pipeline FLUX.2 + Pós-processamento
        "generate_game_art_flux": generate_game_art_flux,
        "remove_background": remove_background,
        "optimize_sprite": optimize_sprite,
        "create_spritesheet": create_spritesheet,
        # Onda 3: Assets
        "generate_audio_sfx": _handle_generate_audio_sfx,
        # Pacote D: TTS Kokoro/Edge
        "generate_voice": generate_voice,
        # Onda 4: IA Agêntica
        # Onda 5: Cobertura Godot
        "create_animation_tree": _handle_create_animation_tree,
        "create_joint_2d": _handle_create_joint_2d,
        "import_3d_model": _handle_import_3d_model,
        "create_particles_2d": _handle_create_particles_2d,
        "create_light_2d": _handle_create_light_2d,
        # Onda 7: Robustez
        "health_check": _handle_health_check,
        "self_test": _handle_self_test,
        # Onda 8: DevSolo Crítico
        "setup_camera_2d": _handle_setup_camera_2d,
        "create_navigation_region_2d": _handle_create_navigation_region_2d,
        "create_navigation_agent_2d": _handle_create_navigation_agent_2d,
        # Onda 9: Polimento Visual
        "create_parallax_background": _handle_create_parallax_background,
        "add_parallax_layer": _handle_add_parallax_layer,
        "configure_particles_2d": _handle_configure_particles_2d,
        "create_particles_3d": _handle_create_particles_3d,
        "generate_shader_2d": _handle_generate_shader_2d,
        "create_path_2d": _handle_create_path_2d,
        "create_patrol_route": _handle_create_patrol_route,
        # Onda 10: Gênero-Específico
        "create_bullet_template": _handle_create_bullet_template,
        "create_gun_system": _handle_create_gun_system,
        "generate_dungeon_rooms": _handle_generate_dungeon_rooms,
        "load_scene_async": _handle_load_scene_async,
        # Onda 11: Complementos
        "add_raycast_2d": _handle_add_raycast_2d,
        "add_shapecast_2d": _handle_add_shapecast_2d,
        "setup_localization": _handle_setup_localization,
        "add_translation_string": _handle_add_translation_string,
        "create_light_3d": _handle_create_light_3d,
        "configure_standard_material_3d": _handle_configure_standard_material_3d,
        "configure_export_preset": _handle_configure_export_preset,
        # Novas tools (refinamento)
        "generate_project_structure": _handle_generate_project_structure,
        "record_gameplay_gif": _handle_record_gameplay_gif,
        # Undo/Desfazer
        # LSP Bridge (Fase 2A / C3)
        "gdscript_lsp_connect": _handle_gdscript_lsp_connect,
        "gdscript_lsp_disconnect": _handle_gdscript_lsp_disconnect,
        "gdscript_references": _handle_gdscript_references,
        "gdscript_definition": _handle_gdscript_definition,
        "gdscript_hover": _handle_gdscript_hover,
        "gdscript_symbols": _handle_gdscript_symbols,
        "gdscript_rename": _handle_gdscript_rename,
        "gdscript_diagnostics": _handle_gdscript_diagnostics,
        "gdscript_sync_file": _handle_gdscript_sync_file,
        # Addon Bridge (Fase 2B / A2)
        "addon_connect": _handle_addon_connect,
        "addon_disconnect": _handle_addon_disconnect,
        "addon_is_available": _handle_addon_is_available,
        "addon_ping": _handle_addon_ping,
        "addon_create_node": _handle_addon_create_node,
        "addon_delete_node": _handle_addon_delete_node,
        "addon_set_property": _handle_addon_set_property,
        "addon_reparent_node": _handle_addon_reparent_node,
        "addon_duplicate_node": _handle_addon_duplicate_node,
        "addon_batch_edit": _handle_addon_batch_edit,
        "addon_take_screenshot": _handle_addon_take_screenshot,
        "addon_get_scene_tree": _handle_addon_get_scene_tree,
        # Playtest (Fase 2B / A3+A4+A5)
        "freeze_game_clock": _handle_freeze_game_clock,
        "unfreeze_game_clock": _handle_unfreeze_game_clock,
        "step_game_time": _handle_step_game_time,
        "step_until": _handle_step_until,
        "get_runtime_state_digest": _handle_get_runtime_state_digest,
        "capture_runtime_errors": _handle_capture_runtime_errors,
        # Playtest Onda 1 (watch_state, godot_exec, effect_probe)
        "watch_state_start": watch_state_start,
        "watch_state_collect": watch_state_collect,
        "godot_exec": godot_exec,
        "effect_probe": effect_probe,
        # Balance Onda 1
        "balance_analyze": balance_analyze,
        "wave_generate": wave_generate,
        "dps_calculator": dps_calculator,
        "loot_table_generate": loot_table_generate,
        "gdd_generate": gdd_generate,
        # Behavior Trees (Onda 2)
        "behavior_tree_generate": behavior_tree_generate,
        "behavior_tree_list_templates": behavior_tree_list_templates,
        # Performance Profiler (Onda 2)
        "profile_frame": profile_frame,
        "profile_memory": profile_memory,
        # Shader NL (Onda 3)
        "shader_generate": shader_generate,
        "shader_list_templates": shader_list_templates,
        # World Generation (Onda 3)
        "terrain_generate": terrain_generate,
        "dungeon_generate": dungeon_generate,
        "world_describe": world_describe,
        # 3D Asset Generation (Onda 3)
        "generate_3d_placeholder": generate_3d_placeholder,
        "generate_3d_asset": generate_3d_asset,
        # Deploy + Marketplace (Onda 4 — FINAL)
        "deploy_itch": deploy_itch,
        "release_checklist": release_checklist,
        "auto_screenshot": auto_screenshot,
        "marketplace_search": marketplace_search,
        "marketplace_download": marketplace_download,
        # Juice (Onda 5)
        "juice_apply": juice_apply,
        "juice_list_presets": juice_list_presets,
        # Auto-Config (Fase 2C)
        "validate_mcp_environment": _handle_validate_mcp_environment,
        "setup_mcp_config": _handle_setup_mcp_config,
        # Pipeline Executor (Onda 7)
        "create_entity": create_entity,
        "project_status": project_status,
        # Orquestrador Genius (Onda 7)
        "circuit_breaker_status": circuit_breaker_status,
        # PATCH 13: ClassDB Introspecção
        "godot_class_ref": _handle_godot_class_ref,
        # PATCH 12: Runtime Bridge
        "godot_screenshot": _handle_godot_screenshot,
        "godot_runtime_info": _handle_godot_runtime_info,
        "godot_custom_command": _handle_godot_custom_command,
        "godot_list_custom_commands": _handle_godot_list_custom_commands,
        # PATCH 12.1: Process Lifecycle
        "godot_run_project": _handle_godot_run_project,
        "godot_stop_project": _handle_godot_stop_project,
        "godot_wait_for_bridge": _handle_godot_wait_for_bridge,
    }

    # ── Rollups Fase 2A / C1 ───────────────────────────────────────
    try:
        from tools.rollups import get_rollup_handlers
        _HANDLERS_CACHE.update(get_rollup_handlers())
    except Exception:
        pass  # Rollups são bônus — se falhar, server ainda funciona sem eles

    # ── Depreciação: handlers substituídos por rollups ──────────
    _DEPRECATED_H = {
        "add_audio_effect", "add_collision_shape", "add_control_node",
        "add_node", "add_script_signal", "add_script_variable",
        "add_state_transition", "attach_script", "build_export",
        "chain_tweens", "configure_audio_bus", "configure_autoload",
        "configure_input_action", "configure_standard_material_3d",
        "connect_signal", "create_animation", "create_animation_player",
        "create_csg_shape", "create_health_bar", "create_hud_template",
        "create_joint_2d", "create_light_3d", "create_loading_screen",
        "create_main_menu", "create_particles_3d", "create_pause_menu",
        "create_project", "create_save_system", "create_scene",
        "create_state_machine", "create_tilemap_layer", "create_tileset",
        "create_tween_animation", "create_ui_scene", "define_save_data",
        "delete_file", "delete_node", "detach_script",
        "enable_debug_collisions", "enable_debug_navigation",
        "generate_background_gradient", "generate_gdscript",
        "generate_placeholder_sprite", "generate_placeholder_texture_atlas",
        "generate_tilemap_from_noise", "generate_tileset_from_colors",
        "get_node_property", "get_performance_stats",
        "get_project_settings", "import_audio", "import_sprite_sheet",
        "import_texture", "inspect_project", "instance_scene_as_child",
        "list_export_presets", "list_signals", "load_scene_tree",
        "move_file", "paint_tilemap_cell", "reparent_node",
        "set_active_project", "set_collision_layer_mask",
        "set_main_scene", "set_node_property", "set_physics_material",
        "set_project_setting", "suggest_color_palette",
        "validate_export_templates_installed", "validate_gdscript_syntax",
        # Onda Extra
        "compile_test", "run_game", "stop_game", "smart_restart",
        "launch_editor", "close_editor",
        "setup_camera_2d", "setup_camera_follow", "setup_camera_shake",
        "create_navigation_region_2d", "create_navigation_agent_2d",
        "bake_navigation_polygon",
        "create_dialogue_system", "add_dialogue_node", "create_dialogue_ui",
        "create_inventory_system", "define_inventory_item", "create_inventory_ui",
        "configure_particles_2d", "create_particles_2d", "create_light_2d",
        "setup_screen_flash", "setup_world_environment",
        "generate_shader_2d", "apply_shader_to_node", "create_shader_material",
        "analyze_game_structure", "suggest_next_steps",
        "find_missing_references", "validate_game_design",
        "estimate_game_scope", "search_codebase", "get_project_history",
        "list_backups", "restore_backup", "git_commit_checkpoint",
        "undo_last_action", "get_undo_history",
        "compare_screenshots", "detect_empty_screen", "detect_offscreen_elements",
    }
    _HANDLERS_CACHE = {k: v for k, v in _HANDLERS_CACHE.items() if k not in _DEPRECATED_H}

    # ── PATCH 17: Filtrar handlers por --toolsets ──
    if _ENABLED_TOOLS is not None:
        _HANDLERS_CACHE = {k: v for k, v in _HANDLERS_CACHE.items() if k in _ENABLED_TOOLS}

    return _HANDLERS_CACHE


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Roteia chamadas de tool para o handler correspondente."""
    import asyncio

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
            # P1-1: Despachar handlers para thread pool (evita bloquear event loop)
            loop = asyncio.get_running_loop()
            result = await loop.run_in_executor(None, handler, arguments)
            # Garante status sempre presente (outputSchema exige)
            if isinstance(result, dict) and "status" not in result:
                result["status"] = "success"
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


def _handle_read_file(args: dict) -> dict:
    return read_file(
        path=args["path"],
        start_line=args.get("start_line"),
        end_line=args.get("end_line"),
    )


def _handle_write_file(args: dict) -> dict:
    path = args["path"]
    if path.endswith(".gd"):
        # Redireciona para o caminho validado. Reusa a lógica de
        # safe_write_gdscript em vez de duplicá-la.
        from tools.project_ops import _get_active_project
        proj = _get_active_project()
        result = safe_write_gdscript(
            file_path=path,
            content=args["content"],
            project_path=str(proj),
            strict=True,
        )
    else:
        result = write_file(
            path=path,
            content=args["content"],
            mode=args.get("mode", "create"),
        )
    if result.get("status") == "success":
        try:
            from tools.editor_config import _notify_godot_file_changed
            _notify_godot_file_changed(path)
        except Exception:
            pass
    return result


# ── Fase 2 Handlers ─────────────────────────────────────────────────

def _handle_query_classdb(args: dict) -> dict:
    return query_classdb(
        class_name=args["class_name"],
        section=args.get("section", "all"),
        include_inherited=args.get("include_inherited", False),
        offset=args.get("offset", 0),
        limit=args.get("limit", 50),
    )


def _handle_search_classdb(args: dict) -> dict:
    return search_classdb(args["query"], args.get("limit", 20))


def _handle_download_asset(args: dict) -> dict:
    return download_asset(
        source=args["source"],
        query=args.get("query", ""),
        category=args.get("category", "all"),
        asset_id=args.get("asset_id"),
        resolution=args.get("resolution", "2k"),
        limit=args.get("limit", 10),
    )


def _handle_import_downloaded_asset(args: dict) -> dict:
    return import_downloaded_asset(
        args["asset_path"],
        args.get("target_dir", "assets"),
    )


def _handle_workflow_snapshot(args: dict) -> dict:
    return workflow_snapshot(args.get("description", ""), args.get("project_path"))


def _handle_workflow_handoff(args: dict) -> dict:
    return workflow_handoff(args.get("next_steps"), args.get("notes", ""))


def _handle_project_map(args: dict) -> dict:
    return generate_project_map(
        args.get("project_path"),
        args.get("format", "json"),
        args.get("output_path"),
    )


def _handle_configure_security(args: dict) -> dict:
    return configure_security(
        generate_token=args.get("generate_token", True),
        allow_remote=args.get("allow_remote", False),
    )


def _handle_security_status(args: dict) -> dict:
    return security_status()


def _handle_run_gut_tests(args: dict) -> dict:
    return run_gut_tests(
        args.get("project_path"),
        args.get("test_dir", "res://tests"),
        args.get("godot_path"),
        args.get("timeout", 60),
    )


def _handle_assert_node_exists(args: dict) -> dict:
    return assert_node_exists(args["scene_path"], args["node_path"], args.get("node_type"))


def _handle_simulate_input_sequence(args: dict) -> dict:
    return simulate_input_sequence(args["actions"], args.get("delay_ms", 100))


def _handle_vibe_coding_mode(args: dict) -> dict:
    return vibe_coding_mode(
        args.get("enabled", True),
        args.get("scene_path"),
        args.get("focus_node"),
    )


def _handle_get_vibe_context(args: dict) -> dict:
    return get_vibe_context()


def _handle_debugger_set_breakpoint(args: dict) -> dict:
    return debugger_set_breakpoint(args["script_path"], args["line"], args.get("condition"))


def _handle_debugger_status(args: dict) -> dict:
    return debugger_status()


def _handle_debugger_step(args: dict) -> dict:
    return debugger_step(args.get("step_type","over"))


def _handle_debugger_get_stack(args: dict) -> dict:
    return debugger_get_stack()


def _handle_debugger_get_variables(args: dict) -> dict:
    return debugger_get_variables(args.get("variable_name"))


def _handle_game_http_request(args: dict) -> dict:
    return game_http_request(args["url"], args.get("method","GET"), args.get("headers"), args.get("body"))


def _handle_game_multiplayer(args: dict) -> dict:
    return game_multiplayer(args["action"], args.get("port",9090), args.get("address","127.0.0.1"))


def _handle_set_safety_policy(args: dict) -> dict:
    return set_safety_policy(args.get("enabled"), args.get("allowlist"), args.get("blocklist"), args.get("confirm_destructive"))


def _handle_get_audit_log(args: dict) -> dict:
    return get_audit_log(args.get("limit", 50))


def _handle_get_audit_replay(args: dict) -> dict:
    return get_audit_replay(args.get("steps", 10))


def _handle_safe_write_gdscript(args: dict) -> dict:
    result = safe_write_gdscript(args["file_path"], args["content"], args.get("project_path"), args.get("strict", True))
    if isinstance(result, dict) and result.get("status") == "success":
        try: from tools.editor_config import _notify_godot_file_changed; _notify_godot_file_changed(args["file_path"])
        except Exception: pass
    return result


def _handle_tool_catalog(args: dict) -> dict:
    return tool_catalog(args.get("query",""), args.get("group",""), args.get("limit",20))


def _handle_tool_groups(args: dict) -> dict:
    return tool_groups(args["action"], args.get("group",""), args.get("enabled",True))


def _handle_game_serialize_state(args: dict) -> dict:
    return game_serialize_state(args["action"], args.get("file_name","game_state.json"))


def _handle_start_recording(args: dict) -> dict:
    return start_recording(args.get("session_name",""))


def _handle_stop_recording(args: dict) -> dict:
    return stop_recording(args["session_name"])


def _handle_game_call_method(args: dict) -> dict:
    return game_call_method(args["node_path"], args["method"], args.get("args"))


def _handle_game_spawn_node(args: dict) -> dict:
    return game_spawn_node(args["parent_path"], args["node_type"], args.get("node_name",""), args.get("properties"))


def _handle_game_raycast(args: dict) -> dict:
    return game_raycast(args["origin_x"], args["origin_y"], args["target_x"], args["target_y"], args.get("collision_mask",1), args.get("mode","2d"))


def _handle_game_get_camera(args: dict) -> dict:
    return game_get_camera(args.get("mode","2d"))


def _handle_game_play_animation(args: dict) -> dict:
    return game_play_animation(args["node_path"], args["action"], args.get("animation_name",""))


def _handle_game_find_nodes_by_class(args: dict) -> dict:
    return game_find_nodes_by_class(args["class_name"], args.get("limit",20))


def _handle_game_await_signal(args: dict) -> dict:
    return game_await_signal(args["node_path"], args["signal_name"], args.get("timeout_ms",5000))


def _handle_game_pause(args: dict) -> dict:
    return game_pause(args.get("action","toggle"))


def _handle_game_performance(args: dict) -> dict:
    return game_performance()


def _handle_game_window(args: dict) -> dict:
    return game_window(args.get("action","get"), args.get("width",0), args.get("height",0), args.get("fullscreen"), args.get("title",""))


def _handle_game_input_state(args: dict) -> dict:
    return game_input_state()


def _handle_generate_ci_snippet(args: dict) -> dict:
    return generate_ci_snippet(args.get("project_path",""), args.get("target_platforms","windows,linux,macos"))


def _handle_resource_dependency_graph(args: dict) -> dict:
    return resource_dependency_graph(args.get("project_path",""))


def _handle_build_csharp(args: dict) -> dict:
    return build_csharp(args.get("project_path",""))


def _handle_list_valid_node_types(args: dict) -> dict:
    return list_valid_node_types()


def _handle_install_mcp_addon(args: dict) -> dict:
    return install_mcp_addon(args.get("project_path"))


def _handle_bootstrap_godot_mcp(args: dict) -> dict:
    """Handler para bootstrap_godot_mcp — conexão automática completa."""
    return bootstrap_godot_mcp(
        target=args.get("target", "full"),
        project_path=args.get("project_path"),
        godot_path=args.get("godot_path"),
        launch_editor=args.get("launch_editor", True),
        timeout_godot=args.get("timeout_godot", 30),
        timeout_addon=args.get("timeout_addon", 15),
    )


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


# ── Fase 3 Handlers ─────────────────────────────────────────────────

def _handle_take_screenshot(args: dict) -> dict:
    return take_screenshot()


def _handle_read_console_output(args: dict) -> dict:
    return read_console_output(args.get("since_timestamp"))


# ── Fase 4 Handlers ─────────────────────────────────────────────────

# ── Fase 5 Handlers ─────────────────────────────────────────────────

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


def _handle_batch_atomic_edit(args: dict) -> dict:
    """Handler para batch_atomic_edit — operações atômicas com rollback."""
    return batch_atomic_edit(
        operations=args.get("operations", []),
        scene_path=args.get("scene_path"),
        mode=args.get("mode", "auto"),
    )


# ── Onda 3: Assets Handlers ─────────────────────────────────────────

def _handle_generate_audio_sfx(args: dict) -> dict:
    return generate_audio_sfx(
        name=args["name"],
        sfx_type=args.get("sfx_type", "beep"),
        duration=args.get("duration", 0.3),
        frequency=args.get("frequency", 440.0),
        sample_rate=args.get("sample_rate", 44100),
        save_path=args.get("save_path"),
    )


# ── Onda 4: IA Agêntica Handlers ────────────────────────────────────

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


def _handle_create_joint_2d(args: dict) -> dict:
    """Cria Joint2D via add_node + configuração."""
    sp = args["scene_path"]
    jt = args.get("joint_type", "pin")
    joint_type = {"pin": "PinJoint2D", "groove": "GrooveJoint2D", "damped_spring": "DampedSpringJoint2D"}.get(jt, "PinJoint2D")
    r = add_node(sp, args["node_a_path"] if "node_a_path" in args else ".", f"{jt}_joint", joint_type)
    if r["status"] != "success":
        return r
    np = f"./{jt}_joint"
    if args.get("node_a_path"):
        set_node_property(sp, np, "node_a", f'NodePath("{args["node_a_path"]}")')
    if args.get("node_b_path"):
        set_node_property(sp, np, "node_b", f'NodePath("{args["node_b_path"]}")')
    if args.get("softness"):
        set_node_property(sp, np, "softness", float(args["softness"]))
    if args.get("bias"):
        set_node_property(sp, np, "bias", float(args["bias"]))
    return {"status": "success", "node_path": r["node_path"], "joint_type": jt, "note": "Joint 2D criada. Configure node_a e node_b se necessario."}


def _handle_import_3d_model(args: dict) -> dict:
    """Importa modelo 3D (.glb/.gltf) copiando para o projeto + criando MeshInstance3D."""
    import shutil
    from pathlib import Path

    source = args["source_path"]
    target = args["target_res_path"]
    should_create_scene = args.get("create_scene", True)  # renomeado para evitar shadowing
    scene_name = args.get("scene_name")

    # Valida arquivo fonte
    src_path = Path(source)
    if not src_path.exists():
        return {"status": "error", "message": f"Arquivo fonte nao encontrado: {source}"}
    if src_path.suffix.lower() not in (".glb", ".gltf"):
        return {"status": "error", "message": f"Formato nao suportado: {src_path.suffix}. Use .glb ou .gltf."}

    # Copia para o projeto
    try:
        target_path = Path(target) if Path(target).is_absolute() else Path.cwd() / target
        target_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, str(target_path))
        imported_res = str(target_path)
    except Exception as e:
        return {"status": "error", "message": f"Falha ao copiar modelo: {e}"}

    result = {"status": "success", "imported": imported_res}

    # Cria cena opcionalmente
    if should_create_scene:  # usa a variável renomeada
        scene_file = scene_name or f"{Path(target).stem}.tscn"
        scene_path = args.get("scene_path", f"scenes/{scene_file}")
        r = create_scene(scene_file, "MeshInstance3D", scene_path)
        if r.get("status") == "success":
            result["scene"] = r.get("path", scene_file)
            result["note"] = "Modelo importado e cena criada. Adicione o mesh no MeshInstance3D manualmente."

    return result


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
    try:
        from tools.project_ops import get_project_settings
        settings = get_project_settings()
        proj = settings.get("project_path", ".")
    except Exception:
        proj = "."
    full = Path(proj) / sp if proj else Path(sp)
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

    # 1. config
    try:
        from tools.config_loader import load_config
        cfg = load_config()
        godot_path = cfg.get("godot_path", "não configurado")
    except Exception:
        godot_path = None
    checks.append({"component": "config",
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

# ══════════════════════════════════════════════════════════════════
# Onda 12: Handlers de Arte IA
# ══════════════════════════════════════════════════════════════════

def _handle_generate_game_art(args: dict) -> dict:
    return generate_game_art(
        description=args["description"],
        category=args.get("category", "torre"),
        style=args.get("style", "scifi"),
        anim_type=args.get("anim_type", "idle"),
        frames=args.get("frames"),
        grid_cols=args.get("grid_cols"),
        grid_rows=args.get("grid_rows"),
        width=args.get("width"),
        height=args.get("height"),
        save_dir=args.get("save_dir"),
    )


def _handle_apply_game_art(args: dict) -> dict:
    return apply_game_art(
        frame_paths=args["frame_paths"],
        scene_path=args["scene_path"],
        node_path=args["node_path"],
        anim_name=args.get("anim_name", "default"),
        fps=args.get("fps", 10.0),
        loop=args.get("loop", True),
    )


# ── LSP Bridge Handlers (Fase 2A / C3) ──────────────────────────────

def _handle_gdscript_lsp_connect(args: dict) -> dict:
    return gdscript_lsp_connect(args.get("project_root"))


def _handle_gdscript_lsp_disconnect(args: dict) -> dict:
    return gdscript_lsp_disconnect()


def _handle_gdscript_references(args: dict) -> dict:
    return gdscript_references(
        file_path=args["file_path"],
        line=args["line"],
        character=args["character"],
    )


def _handle_gdscript_definition(args: dict) -> dict:
    return gdscript_definition(
        file_path=args["file_path"],
        line=args["line"],
        character=args["character"],
    )


def _handle_gdscript_hover(args: dict) -> dict:
    return gdscript_hover(
        file_path=args["file_path"],
        line=args["line"],
        character=args["character"],
    )


def _handle_gdscript_symbols(args: dict) -> dict:
    return gdscript_symbols(args["file_path"])


def _handle_gdscript_rename(args: dict) -> dict:
    return gdscript_rename(
        file_path=args["file_path"],
        line=args["line"],
        character=args["character"],
        new_name=args["new_name"],
    )


def _handle_gdscript_diagnostics(args: dict) -> dict:
    return gdscript_diagnostics(args["file_path"])


def _handle_gdscript_sync_file(args: dict) -> dict:
    return gdscript_sync_file(
        file_path=args["file_path"],
        content=args.get("content"),
    )


# ── Addon Bridge Handlers (Fase 2B / A2) ────────────────────────────

def _handle_addon_connect(args: dict) -> dict:
    return addon_connect()


def _handle_addon_disconnect(args: dict) -> dict:
    return addon_disconnect()


def _handle_addon_is_available(args: dict) -> dict:
    return addon_is_available()


def _handle_addon_ping(args: dict) -> dict:
    return addon_ping()


def _handle_addon_create_node(args: dict) -> dict:
    return addon_create_node(
        parent_path=args["parent_path"],
        node_type=args["node_type"],
        node_name=args["node_name"],
        properties=args.get("properties"),
        scene_path=args.get("scene_path"),
    )


def _handle_addon_delete_node(args: dict) -> dict:
    return addon_delete_node(args["node_path"])


def _handle_addon_set_property(args: dict) -> dict:
    return addon_set_property(
        node_path=args["node_path"],
        property_name=args["property_name"],
        value=args["value"],
    )


def _handle_addon_reparent_node(args: dict) -> dict:
    return addon_reparent_node(
        node_path=args["node_path"],
        new_parent_path=args["new_parent_path"],
    )


def _handle_addon_duplicate_node(args: dict) -> dict:
    return addon_duplicate_node(
        node_path=args["node_path"],
        new_name=args.get("new_name"),
    )


def _handle_addon_batch_edit(args: dict) -> dict:
    return addon_batch_edit(args["operations"])


def _handle_addon_take_screenshot(args: dict) -> dict:
    return addon_take_screenshot(args.get("viewport", "editor"))


def _handle_addon_get_scene_tree(args: dict) -> dict:
    return addon_get_scene_tree()


# ── Playtest Handlers (Fase 2B / A3+A4+A5) ──────────────────────────

def _handle_freeze_game_clock(args: dict) -> dict:
    return freeze_game_clock()


def _handle_unfreeze_game_clock(args: dict) -> dict:
    return unfreeze_game_clock()


def _handle_step_game_time(args: dict) -> dict:
    return step_game_time(args.get("ms", 16))


def _handle_step_until(args: dict) -> dict:
    return step_until(
        condition=args["condition"],
        timeout_ms=args.get("timeout_ms", 5000),
    )


def _handle_get_runtime_state_digest(args: dict) -> dict:
    return get_runtime_state_digest(args.get("groups"))


def _handle_capture_runtime_errors(args: dict) -> dict:
    return capture_runtime_errors()


# ── Auto-Config Handlers (Fase 2C) ──────────────────────────────────

def _handle_validate_mcp_environment(args: dict) -> dict:
    return _validate_env()


def _handle_setup_mcp_config(args: dict) -> dict:
    target = args.get("target", "vscode")
    return _auto_config(target)


# ══════════════════════════════════════════════════════════════════════
# ── MCP Resources (Fase 2A / C2) + Game Patterns (Onda 6) ──────────
# CONSOLIDADO: um único @server.list_resources() + @server.read_resource()
# para evitar que o segundo par sobrescreva o primeiro (bug PATCH 9).
# ══════════════════════════════════════════════════════════════════════

@server.list_resources()
async def list_resources() -> list:
    """Lista os resources godot:// disponíveis + game patterns."""
    all_resources = []

    # 1. Resources godot:// originais
    try:
        from resources import get_resources
        all_resources.extend(get_resources())
    except Exception:
        pass

    # 2. Game Patterns (Onda 6)
    try:
        from mcp.types import Resource, ResourceTemplate
        from resources.game_patterns import get_game_patterns
        patterns = get_game_patterns()
        all_resources.extend([
            Resource(uri="godot://game-patterns", name="Padroes de Jogos",
                     description=f"{len(patterns)} generos com estruturas tecnicas Godot",
                     mimeType="application/json"),
            ResourceTemplate(uriTemplate="godot://game-patterns/{name}",
                     name="Padrao Especifico",
                     description="Estrutura completa para um genero",
                     mimeType="application/json"),
        ])
    except Exception:
        pass

    return all_resources


@server.read_resource()
async def read_resource(uri: str) -> str:
    """Lê o conteúdo de um resource godot:// ou game-patterns.

    Retorna JSON ou texto puro conforme o MIME type do resource.
    """
    import json

    # 1. Game Patterns
    if uri.startswith("godot://game-patterns"):
        try:
            from urllib.parse import urlparse
            from resources.game_patterns import get_game_patterns, get_game_pattern
            parsed = urlparse(uri)
            name = parsed.path.strip("/")
            if not name:
                return json.dumps(get_game_patterns(), indent=2, ensure_ascii=False)
            pattern = get_game_pattern(name)
            if pattern:
                return json.dumps(pattern, indent=2, ensure_ascii=False)
            return json.dumps({"error": f"Padrao '{name}' nao encontrado"})
        except Exception as e:
            return json.dumps({"status": "error", "message": f"Erro ao ler pattern: {e}"})

    # 2. Resources godot:// originais
    try:
        from resources import read_resource as _read
        return _read(uri)
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"Erro ao ler resource '{uri}': {e}",
        })


# ══════════════════════════════════════════════════════════════
# Onda 6: MCP Prompts (slash commands)
# ══════════════════════════════════════════════════════════════

@server.list_prompts()
async def list_prompts():
    from mcp.types import Prompt, PromptArgument
    from resources.prompts import get_mcp_prompts
    prompts = get_mcp_prompts()
    return [Prompt(name=p["name"], title=p["title"], description=p["description"],
                   arguments=[PromptArgument(name=a["name"], description=a["description"], required=a.get("required", False))
                              for a in p.get("arguments", [])])
            for p in prompts]


@server.get_prompt()
async def get_prompt(name: str, arguments: dict | None = None):
    import re
    from mcp.types import PromptMessage, TextContent
    from resources.prompts import get_prompt_template
    prompt = get_prompt_template(name)
    if not prompt:
        return PromptMessage(role="user", content=TextContent(type="text", text=f"Prompt '{name}' nao encontrado."))
    template = prompt["template"]
    if arguments:
        for key, value in arguments.items():
            template = template.replace("{" + key + "}", str(value))
    template = re.sub(r'\{[^}]+\}', '', template)
    return PromptMessage(role="user", content=TextContent(type="text", text=template.strip()))


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

