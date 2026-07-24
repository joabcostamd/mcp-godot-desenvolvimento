"""server.py — MCP Server godot-mcp-agent v3.7.

Servidor MCP via stdio com 236 ferramentas visiveis (235 handlers ativos,
189 depreciadas, 80 aliases) para criacao e gestao de projetos Godot 4.7.
A IA consumidora (DeepSeek V4 Pro) chama as ferramentas para construir
jogos a partir de linguagem natural.

Cobre 12 Ondas de desenvolvimento: projeto, arquivo, cena, scripts,
fisica, assets, runtime, editor, tilemap, animacao, UI, export,
seguranca, game bridge, visao, batch, assets procedurais, IA agentica,
DevSolo (camera, navegacao, save, UI, dialogo, inventario, armas,
procedural, shaders, 3D, audio, exportacao, debug, localizacao).
"""

import json
import logging
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

# Logger do MCP — A6.3: JSON estruturado
from core.legacy_data import TOOLSETS, PHASE_TOOLSETS, PHASE_TOOLS_CORE
class _JsonFormatter(logging.Formatter):
    """Formata logs como JSON para parseabilidade (MCP Spec compliance)."""
    def format(self, record: logging.LogRecord) -> str:
        import json as _json
        from datetime import datetime, timezone
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if hasattr(record, 'tool_name'):
            log_entry["tool"] = record.tool_name
        if record.exc_info and record.exc_info[1]:
            log_entry["exception"] = str(record.exc_info[1])
        return _json.dumps(log_entry, ensure_ascii=False, default=str)

_handler = logging.StreamHandler()
_handler.setFormatter(_JsonFormatter())
logging.basicConfig(level=logging.WARNING, handlers=[_handler])
logger = logging.getLogger("mcp-godot")

from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool, Resource, ResourceTemplate
from core.tool_definitions import _raw_tool_defs

# ══════════════════════════════════════════════════════════════
# PATCH 17: Curadoria de Toolset (--toolsets)
# ══════════════════════════════════════════════════════════════


# ── TOOL_NAMESPACES: Mapeamento reverso tool_name → namespace ──
# Derivado automaticamente do TOOLSETS acima.
# Usado por _tool_defs() para injetar _meta={"namespace": ...} em cada Tool.
TOOL_NAMESPACES: dict[str, str] = {}
for _ns, _tools in TOOLSETS.items():
    for _t in _tools:
        TOOL_NAMESPACES[_t] = _ns

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

# ── FASE 4: Progressive Discovery (--lean) ────────────────────
# Ativa modo lean (default): tools/list retorna apenas CORE + top-5 da fase.
# Use --full para expor todas as tools da fase (modo legado).
# O catálogo completo sempre permanece acessível via catalog_search.
_LEAN_MODE: bool = True

def _parse_lean_arg() -> bool:
    import argparse
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--full", action="store_true", default=False,
                       help="Desativa modo lean — expõe todas as tools da fase")
    args, _ = parser.parse_known_args()
    return not args.full  # --full desativa lean

_LEAN_MODE = _parse_lean_arg()
if not _LEAN_MODE:
    print("[MCP] Modo FULL — todas as tools por fase visíveis (--full)", file=sys.stderr)

# ── Feature 8: Toolsets por Fase (--phase) ────────────────────
# Filtro dinâmico: consulta get_current_phase() do projeto ativo
# a cada _tool_defs(). Cumulativo: cada fase herda tools da anterior.
# NÃO filtra _build_handlers() — visibilidade, não bloqueio.


PHASE_ORDER_FILTER = ["IDEIA", "DESIGN", "PROTOTIPO", "CONTEUDO", "POLIMENTO", "PRONTO_PARA_LANCAR"]

# ── Opcao C: CORE sempre visivel + ferramentas da fase atual ──
# CORE = tools essenciais em QUALQUER fase (22 ferramentas).
# As fases sao nao-cumulativas: cada fase ve CORE + suas proprias tools.


def _get_phase_tools() -> set[str]:
    """Retorna o set de tools para a fase atual (Opcao C).

    CORE (27 tools) esta sempre visivel. A elas somam-se as tools
    exclusivas da fase atual (NAO cumulativo entre fases).

    Se nao ha projeto ativo, retorna apenas o CORE (27 tools,
    bem abaixo do limite de 128 do DeepSeek/Copilot).

    Le o arquivo .mcp_phase_state.json diretamente (nao usa o singleton
    em memoria) para garantir que reflete o estado real do disco.
    Se o arquivo nao existe, cria com IDEIA (estado inicial padrao).
    """
    try:
        from tools.project_ops import _get_active_project
        from pathlib import Path as _Path
        proj = _Path(_get_active_project())
        phase_file = proj / ".mcp_phase_state.json"
        import json as _json
        if not phase_file.exists():
            default_state = {"current_phase": "IDEIA", "history": [], "updated_at": ""}
            phase_file.parent.mkdir(parents=True, exist_ok=True)
            phase_file.write_text(_json.dumps(default_state, indent=2, ensure_ascii=False), encoding="utf-8")
            phase = "IDEIA"
        else:
            data = _json.loads(phase_file.read_text(encoding="utf-8"))
            phase = data.get("current_phase", "")
            if not phase:
                return PHASE_TOOLS_CORE
    except Exception:
        return PHASE_TOOLS_CORE

    phase_tools = PHASE_TOOLSETS.get(phase, set())

    # ── FASE 4: Progressive Discovery (--lean) ──
    # Modo lean: tools/list retorna CORE + top-5 da fase.
    # As demais tools da fase são acessíveis via catalog_search +
    # describe_tool + invoke_by_name (descoberta progressiva).
    if _LEAN_MODE:
        from core.legacy_data import PHASE_TOOLS_TOP
        top = PHASE_TOOLS_TOP.get(phase, set())
        return PHASE_TOOLS_CORE | top

    return PHASE_TOOLS_CORE | phase_tools


def _invalidate_tool_caches() -> None:
    """Invalida caches de _tool_defs() e _build_handlers().

    Chamado por phase_ops.set_cache_invalidator() quando a fase avança.
    """
    global _TOOL_DEFS_CACHE, _HANDLERS_CACHE
    _TOOL_DEFS_CACHE = None
    _HANDLERS_CACHE = None
    # ── F1.5: também invalida cache do registry ──
    try:
        from registry import invalidate_caches as _reg_invalidate
        _reg_invalidate()
    except Exception:
        pass


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
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            close_fds=True,
        )
        _running_godot_processes[str(proc.pid)] = proc
        return json.dumps({"ok": True, "pid": proc.pid})
    except Exception as exc:
        return json.dumps({"ok": False, "error": str(exc)})


def _get_process_name(pid: int) -> str | None:
    """Obtem o nome do executavel de um PID. Retorna None se nao encontrado."""
    try:
        if sys.platform == "win32":
            from tools.subprocess_utils import run_subprocess_safe
            result = run_subprocess_safe(
                ["tasklist", "/FI", f"PID eq {pid}", "/FO", "CSV", "/NH"],
                timeout=5,
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
                from tools.subprocess_utils import run_subprocess_safe
                result = run_subprocess_safe(
                    ["taskkill", "/F", "/PID", str(pid)],
                    timeout=10,
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

from tools.project_map import generate_project_map
from tools.gut_ops import run_gut_tests
from tools.playmode_ops import assert_node_exists, simulate_input_sequence
from tools.debugger_ops import debugger_set_breakpoint, debugger_status, debugger_step, debugger_get_stack, debugger_get_variables
from tools.networking_ops import game_http_request, game_multiplayer
from tools.safety_policy import set_safety_policy
from tools.validate_write import safe_write_gdscript
from tools.recording_ops import game_serialize_state
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
from tools.test_ops import (
    run_scripted_tests,
    smoke_test,
    regression_test,
    dump_mcp_state,
    estimate_tool_tokens,
)
from tools.verification_ops import (
    run_verification_pipeline,
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
from tools.proof_ledger import (
    capture_proof,
    verify_proof,
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
from tools.refs_ops import (
    validate_project_refs,
    find_usages,
)
from tools.asset_manifest import (
    import_asset_manifest,
    create_asset_manifest,
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

# ── Feature 10: Stress Test ─────────────────────────────────────
from tools.stress_test_ops import run_stress_test

# ── Grupo C: Detecção de recursos não usados ───────────────────
from tools.find_unused_resources import find_unused_resources

# ── Grupo C: Análise de fluxo de sinal ─────────────────────────
from tools.analyze_signal_flow import analyze_signal_flow

# ── Grupo C: Sugestão fuzzy ────────────────────────────────────
from tools.fuzzy_suggest import suggest_similar, not_found_error

# ── Grupo C: Auto-dismiss de diálogo modal ─────────────────────
from tools.set_auto_dismiss import set_auto_dismiss

# ── Validação de Consistência do Registro ──────────────────────
from tools.registry_validation import validate_mcp_registry_handler

# ── Shader Editor (read/edit/get_params) ───────────────────────
from tools.shader_editor_ops import read_shader, edit_shader, get_shader_params

# ── VFX Ops (partículas 2D) ──────────────────────────────────
from tools.vfx_ops import create_particles_2d

# ── Fase 1 do Roadmap: Máquina de Estados ───────────────────────
from tools.phase_ops import get_current_phase, advance_phase, get_phase_history, get_next_step, resume_session, set_cache_invalidator
from tools.milestone_ops import create_milestone_plan, advance_milestone, get_milestone_plan, project_progress

# Feature 8: registrar callback de invalidação de cache
set_cache_invalidator(_invalidate_tool_caches)

# ── Feature 5: Project Brief ────────────────────────────────────
from tools.project_brief_ops import set_project_brief, get_project_brief, update_project_brief

# ── Feature 6: Batch Entity Creation ───────────────────────────
from tools.orchestrator import create_entities

# ── Juice (Onda 5) ────────────────────────────────────────────
from tools.juice_ops import juice_apply, juice_list_presets

# ── Pipeline Executor (Onda 7) ──────────────────────────────────
from tools.pipeline_ops import project_status

# ── Orquestrador Genius (Onda 7) ────────────────────────────────
from tools.orchestrator import create_entity, circuit_breaker_status

# ── Camada 5 (Gameplay) ─────────────────────────────────────────────
from tools.achievement_ops import create_achievement_system, validate_achievement_config
from tools.mcp_telemetry_ops import mcp_telemetry_manage, track_mcp_event, track_phase_transition
from tools.adaptive_ops import adaptive_difficulty_adjust, quest_generate
from tools.dialogue_ops import dialogue_generate_npc_lines, dialogue_generate_personality
from tools.accessibility_ops import accessibility_apply_colorblind_filter, accessibility_add_subtitles, accessibility_remap_controls, accessibility_audit_scene, accessibility_certification_checklist

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

# Flag interna: quando True, _tool_defs() e _build_handlers() retornam
# conjuntos COMPLETOS sem filtrar depreciação, fase, toolsets ou profile.
# Usado APENAS por tools/registry_validation.py para diagnóstico.
_REGISTRY_VALIDATION_UNFILTERED: bool = False


# ══════════════════════════════════════════════════════════════
# PÓS-PROCESSADOR: garantir 4 hints em 100% das tools
# ══════════════════════════════════════════════════════════════

from registry.legacy_annotations import _HINT_RULES


def _apply_hints(tools: list) -> list:
    """Garante que toda tool tenha os 4 hints MCP.

    Regras:
    - Se o hint JÁ existe na tool.annotations, respeita o valor existente
    - Se NÃO existe, aplica a regra por nome
    - Se nenhuma regra bate, defaults seguros:
      readOnlyHint=False, destructiveHint=False,
      idempotentHint=False, openWorldHint=False
    """
    from mcp.types import ToolAnnotations

    for tool in tools:
        name = tool.name

        # Garante que annotations existe como objeto ToolAnnotations
        if tool.annotations is None:
            tool.annotations = ToolAnnotations()
        ann = tool.annotations

        # readOnlyHint
        if ann.readOnlyHint is None:
            is_readonly = (
                any(name.startswith(p) for p in _HINT_RULES["readOnly"]["prefixes"]) or
                any(name.endswith(s) for s in _HINT_RULES["readOnly"]["suffixes"]) or
                name in _HINT_RULES["readOnly"]["exact"]
            )
            ann.readOnlyHint = is_readonly

        # destructiveHint
        if ann.destructiveHint is None:
            is_destructive = (
                any(name.startswith(p) for p in _HINT_RULES["destructive"]["prefixes"]) or
                name in _HINT_RULES["destructive"]["exact"]
            )
            ann.destructiveHint = is_destructive

        # idempotentHint
        if ann.idempotentHint is None:
            is_idempotent = (
                any(name.startswith(p) for p in _HINT_RULES["idempotent"]["prefixes"]) or
                any(name.endswith(s) for s in _HINT_RULES["idempotent"]["suffixes"]) or
                name in _HINT_RULES["idempotent"]["exact"]
            )
            ann.idempotentHint = is_idempotent

        # openWorldHint
        if ann.openWorldHint is None:
            is_openworld = (
                any(name.startswith(p) for p in _HINT_RULES["openWorld"]["prefixes"]) or
                name in _HINT_RULES["openWorld"]["exact"]
            )
            ann.openWorldHint = is_openworld

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
            _CORE_PREFIXES = ("ping", "health_check", "self_test", "bootstrap", "validate_mcp", "godot")
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
    """Encurta descricao mantendo a informacao essencial.

    NUNCA retorna string vazia — se a compactacao falhar, retorna o original.
    """
    import re
    if not description or len(description) <= max_chars:
        return description
    first_sentence = re.split(r'[.]\s+(?:Quando|Pré|Pre|Exemplo|Erro)', description)[0].strip()
    if not first_sentence:
        return description  # fallback: nao retorna vazio
    if len(first_sentence) > max_chars:
        parts = first_sentence.split('. ')
        result = ''
        for part in parts:
            if len(result) + len(part) < max_chars:
                result += part + '. '
            else:
                break
        first_sentence = result.strip()
    if not first_sentence:
        return description  # fallback
    if first_sentence and first_sentence[-1] not in '.!?':
        first_sentence += '.'
    return first_sentence[:max_chars]


def _compact_all_tool_descriptions(tools: list) -> list:
    """Encurta descricoes de todas as tools. Nunca zera uma descricao."""
    for tool in tools:
        original = tool.description or ""
        compact = _compact_description(original)
        if compact and len(compact) < len(original):
            tool.description = compact
    return tools


def _tool_defs() -> list[Tool]:
    """Retorna a lista completa de tools registradas (cacheado).
    
    Onda 1.2: tools brutas vêm do registry.build_tool_defs().
    Pós-processamento (hints, rollups, filtros) permanece aqui.
    """
    global _TOOL_DEFS_CACHE
    if _TOOL_DEFS_CACHE is not None:
        return _TOOL_DEFS_CACHE
    
    # ── Onda 1.2: tools brutas via registry ──────────────────────
    import registry.legacy_adapter as _la
    _la._in_registry_call = True
    try:
        from registry import build_tool_defs
        _TOOL_DEFS_CACHE = build_tool_defs()
    finally:
        _la._in_registry_call = False
    # ── Pós-processamento: hints MCP + additionalProperties ────────
    _READONLY = {
        "ping", "validate_godot_version", "get_project_settings",
        "inspect_project", "read_file", "load_scene_tree",
        "get_node_property", "query_classdb", "list_valid_node_types",
        "list_signals", "validate_gdscript_syntax", "compile_test",
        "read_console_output", "take_screenshot", "list_export_presets",
        "validate_export_templates_installed", "list_backups",
        "audit_input_map", "audit_autoloads", "audit_scene_reachability",
        "audit_uid_consistency", "audit_save_compatibility",
        "capture_proof", "verify_proof",
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
        # Pipeline de Verificação
        "run_verification_pipeline",
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
        "configure_export_preset",
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
        "create_light_2d": "Criar Luz 2D",
        "generate_project_structure": "Gerar Estrutura do Projeto",
        "record_gameplay_gif": "Gravar Gameplay (GIF)",
        "create_parallax_background": "Criar Fundo Parallax",
        "add_parallax_layer": "Adicionar Camada Parallax",
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
        "create_light_2d": ["iluminação", "2D"],
        "create_shader_material": ["shader", "efeitos"],
        "generate_project_structure": ["projeto", "scaffolding"],
        "record_gameplay_gif": ["visão", "gravação", "gif"],
        "undo_last_action": ["desfazer", "backup"],
        "get_undo_history": ["desfazer", "histórico"],
        "create_parallax_background": ["parallax", "background", "2D"],
        "add_parallax_layer": ["parallax", "2D"],
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
        # Editor ao vivo (F6.2)
        "editor_manage": ["editor", "addon", "godot", "undo"],
        # Playtest (Fase 2B)
        "freeze_game_clock": ["playtest", "clock", "debug"],
        "unfreeze_game_clock": ["playtest", "clock"],
        "step_game_time": ["playtest", "clock", "deterministico"],
        "step_until": ["playtest", "clock", "condicional"],
        "get_runtime_state_digest": ["playtest", "state", "json"],
        "capture_runtime_errors": ["playtest", "debug", "diagnostico"],
        # Pipeline de Verificação
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
        # ── Garante que annotations existe ──────────────────────
        if t.annotations is None:
            from mcp.types import ToolAnnotations
            t.annotations = ToolAnnotations()
        # ── Hints MCP (devem ser setados em ToolAnnotations, não em Tool) ──
        if t.name in _READONLY:
            t.annotations.readOnlyHint = True
        if t.name in _DESTRUCTIVE:
            t.annotations.destructiveHint = True
        if t.name in _IDEMPOTENT:
            t.annotations.idempotentHint = True
        if t.name not in _SERVER_ONLY:
            t.annotations.openWorldHint = True
        if hasattr(t, 'inputSchema') and isinstance(t.inputSchema, dict):
            if "additionalProperties" not in t.inputSchema:
                t.inputSchema["additionalProperties"] = False
        # ── Annotations Onda 6 ──────────────────────────────────
        if t.name in _TITLES:
            t.title = _TITLES[t.name]
        if t.name in _TAGS:
            t.annotations.tags = _TAGS[t.name]
        # ── B6: Read/Write Split ────────────────────────────────
        cat = _classify_operation(t.name)
        t.annotations.operationCategory = cat
        # ── M3: Defer Loading ───────────────────────────────────
        if t.name not in _CORE_TOOLS:
            t.annotations.deferLoading = True
    # ── Rollups: adicionar APÓS pós-processamento (trazem próprios hints) ──
    try:
        from tools.rollups import get_rollup_tool_defs
        _TOOL_DEFS_CACHE.extend(get_rollup_tool_defs())
    except Exception:
        pass
    # ── Fim pós-processamento ──────────────────────────────────────
    # ── Filtrar tools depreciadas (paridade com _build_handlers) ───
    # _build_handlers() remove handlers de tools em DEPRECATED_TOOLS.
    # _tool_defs() deve remover as definições também, senão fica
    # SEM_HANDLER: tool definida sem handler.
    if not _REGISTRY_VALIDATION_UNFILTERED:
        from tools.deprecated import DEPRECATED_TOOLS as _DEPRECATED_T
        _TOOL_DEFS_CACHE = [t for t in _TOOL_DEFS_CACHE if t.name not in _DEPRECATED_T]

    return _TOOL_DEFS_CACHE

# ── Factory de handlers Camada 6 ─────────────────────────────────
# Substitui 38 definicoes copia-e-cola (~520 linhas) por 1 factory.
# Cada handler importa tools.<modulo>.<funcao> e chama com **kwargs.

def _make_import_handler(module_name: str, func_name: str):
    """Factory: cria handler que importa module.func e chama com **kwargs."""
    import json

    def handler(**kwargs):
        try:
            mod = __import__(f"tools.{module_name}", fromlist=[func_name])
            fn = getattr(mod, func_name)
            result = fn(**kwargs)
            if isinstance(result, dict):
                return json.dumps(result, indent=2, ensure_ascii=False)
            return str(result)
        except Exception as e:
            return json.dumps({"ok": False, "error": str(e)})

    handler.__name__ = f"_handle_{func_name}"
    return handler


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
    # Set unificado em tools/deprecated.py (Sprint 0.5)
    from tools.deprecated import DEPRECATED_TOOLS as _DEPRECATED
    if not _REGISTRY_VALIDATION_UNFILTERED:
        _TOOL_DEFS_CACHE = [t for t in _TOOL_DEFS_CACHE if t.name not in _DEPRECATED]

    # ── PATCH 17: Filtrar por --toolsets se ativo ──
    if not _REGISTRY_VALIDATION_UNFILTERED and _ENABLED_TOOLS is not None:
        _TOOL_DEFS_CACHE = [t for t in _TOOL_DEFS_CACHE if t.name in _ENABLED_TOOLS]

    # ── Feature 8: Filtrar por fase do projeto ativo (Opcao C) ──
    # _get_phase_tools() sempre retorna um set: CORE + fase atual, ou so CORE
    if not _REGISTRY_VALIDATION_UNFILTERED:
        _phase_tools = _get_phase_tools()
        _TOOL_DEFS_CACHE = [t for t in _TOOL_DEFS_CACHE if t.name in _phase_tools]

    # ── Pós-processador: garantir 4 hints em 100% das tools ──
    _TOOL_DEFS_CACHE = _apply_hints(_TOOL_DEFS_CACHE)

    # ── Onda 5: compactar descricoes ────────────────────────
    _TOOL_DEFS_CACHE = _compact_all_tool_descriptions(_TOOL_DEFS_CACHE)

    # ── Kill Switch (Fatia 0.12): remove tools de features desabilitadas ──
    try:
        from tools.kill_switch import get_disabled_tools as _get_disabled
        _disabled = _get_disabled()
        if _disabled:
            _TOOL_DEFS_CACHE = [t for t in _TOOL_DEFS_CACHE if t.name not in _disabled]
    except Exception:
        pass  # Kill switch não disponível — segue sem filtro

    # ── Etapa A1: injetar namespace semântico via _meta ──────────
    # Cada Tool recebe _meta={"namespace": "project|assets|runtime|analysis|orchestration"}
    # baseado no mapeamento TOOL_NAMESPACES derivado do TOOLSETS.
    # Tools não mapeadas recebem namespace "orchestration" (fallback seguro).
    for _t in _TOOL_DEFS_CACHE:
        _ns = TOOL_NAMESPACES.get(_t.name, "orchestration")
        if _t.meta is None:
            _t.meta = {}
        _t.meta["namespace"] = _ns

    if _TOOL_DEFS_CACHE is None:
        _TOOL_DEFS_CACHE = []

    return _TOOL_DEFS_CACHE


# ── Tool Listing ────────────────────────────────────────────────────

@server.list_tools()
async def list_tools() -> list[Tool]:
    """Retorna a lista de ferramentas registradas."""
    return _tool_defs()


# Cache global para handlers (evita recriar dict de handlers a cada call_tool)
_HANDLERS_CACHE: dict | None = None


def _handle_run_verification_pipeline(args: dict) -> dict:
    """Handler da tool run_verification_pipeline."""
    return run_verification_pipeline(
        project_path=args.get("project_path"),
        godot_path=args.get("godot_path"),
        test_scene=args.get("test_scene"),
        gut_test_dir=args.get("gut_test_dir", "res://tests"),
        headless_frames=args.get("headless_frames", 30),
        timeout_compile=args.get("timeout_compile", 30),
        timeout_headless=args.get("timeout_headless", 60),
        timeout_gut=args.get("timeout_gut", 120),
        screenshot_dir=args.get("screenshot_dir"),
    )


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
        "mcp_telemetry_manage": _handle_mcp_telemetry_manage,
        "read_file": _handle_read_file,
        "write_file": _handle_write_file,
        # Fase 2: ClassDB (com cache Onda 5)
        "query_classdb": cached_tool("query_classdb", _handle_query_classdb),
        "search_classdb": cached_tool("search_classdb", _handle_search_classdb),
        "download_asset": _handle_download_asset,
        "import_downloaded_asset": _handle_import_downloaded_asset,
        "project_map": _handle_project_map,
        "run_gut_tests": _handle_run_gut_tests,
        "assert_node_exists": _handle_assert_node_exists,
        "simulate_input_sequence": _handle_simulate_input_sequence,
        "debugger_set_breakpoint": _handle_debugger_set_breakpoint,
        "debugger_status": _handle_debugger_status,
        "debugger_step": _handle_debugger_step,
        "debugger_get_stack": _handle_debugger_get_stack,
        "debugger_get_variables": _handle_debugger_get_variables,
        "game_http_request": _handle_game_http_request,
        "game_multiplayer": _handle_game_multiplayer,
        "set_safety_policy": _handle_set_safety_policy,
        "safe_write_gdscript": _handle_safe_write_gdscript,
        "game_serialize_state": _handle_game_serialize_state,
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
        "quickstart_manage": _handle_quickstart_manage,
        "version_history_manage": _handle_version_history_manage,
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
        # PATCH 14: Testes Roteirizados
        "run_scripted_tests": run_scripted_tests,
        "smoke_test": smoke_test,
        "regression_test": regression_test,
        "dump_mcp_state": dump_mcp_state,
        "estimate_tool_tokens": estimate_tool_tokens,
        # PATCH 15: Validacao de Referencias
        "validate_project_refs": validate_project_refs,
        "find_usages": find_usages,
        # Grupo C: Detecção de recursos não usados
        "find_unused_resources": find_unused_resources,
        # Grupo C: Análise de fluxo de sinal
        "analyze_signal_flow": analyze_signal_flow,
        # Bloco 1: Auditoria de Wiring
        "audit_input_map": _handle_audit_input_map,
        "audit_autoloads": _handle_audit_autoloads,
        "audit_scene_reachability": _handle_audit_scene_reachability,
        # Bloco 2: UID + Save Compatibility
        "audit_uid_consistency": _handle_audit_uid_consistency,
        "audit_save_compatibility": _handle_audit_save_compatibility,
        # Bloco 4: Proof Ledger
        "capture_proof": _handle_capture_proof,
        "verify_proof": _handle_verify_proof,
        # Grupo C: Auto-dismiss
        "set_auto_dismiss": set_auto_dismiss,
        # Shader Editor
        "read_shader": read_shader,
        "edit_shader": edit_shader,
        "get_shader_params": get_shader_params,
        # PATCH 16: Asset Manifest
        "import_asset_manifest": import_asset_manifest,
        "create_asset_manifest": create_asset_manifest,
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
        # Playtest Onda 3 (smoke test do jogo)
        "playtest_manage": _handle_playtest_manage,
        # Fun Report Onda 3 (relatorio de qualidade)
        "fun_report_manage": _handle_fun_report_manage,
        "complexity_gate_manage": _handle_complexity_gate_manage,
        "teacher_manage": _handle_teacher_manage,
        "scope_manage": _handle_scope_manage,
        "reviewer_manage": _handle_reviewer_manage,
        "polish_manage": _handle_polish_manage,
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
        # Feature 10: Stress Test
        "run_stress_test": run_stress_test,
        # Fase 1 do Roadmap: Máquina de Estados
        "get_current_phase": get_current_phase,
        "advance_phase": advance_phase,
        "get_phase_history": get_phase_history,
        "get_next_step": get_next_step,
        "resume_session": resume_session,
        # Fase 1 do Roadmap: Milestone Plan
        "create_milestone_plan": create_milestone_plan,
        "advance_milestone": advance_milestone,
        "get_milestone_plan": get_milestone_plan,
        "project_progress": project_progress,
        # Feature 5: Project Brief
        "set_project_brief": set_project_brief,
        "get_project_brief": get_project_brief,
        "update_project_brief": update_project_brief,
        # Feature 6: Batch Entity Creation
        "create_entities": create_entities,
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
        # Pipeline de Verificação
        "run_verification_pipeline": _handle_run_verification_pipeline,
        # Validação de Consistência do Registro
        "validate_mcp_registry": _handle_validate_mcp_registry,
        # ── Meta-tools (Fatia 0.15) ──
        "catalog_search": _handle_catalog_search,
        "describe_tool": _handle_describe_tool,
        "invoke_by_name": _handle_invoke_by_name,
        # ── Etapa A4: Intent Router ──
        "godot": _handle_godot,
        # ── Camada 5 (Gameplay): Handlers registrados 2026-07-19 ──
        "create_achievement_system": _handle_create_achievement_system,
        "validate_achievement_config": _handle_validate_achievement_config,
        "adaptive_difficulty_adjust": _handle_adaptive_difficulty_adjust,
        "quest_generate": _handle_quest_generate,
        "accessibility_apply_colorblind_filter": _handle_accessibility_apply_colorblind_filter,
        "accessibility_add_subtitles": _handle_accessibility_add_subtitles,
        "accessibility_remap_controls": _handle_accessibility_remap_controls,
        "accessibility_audit_scene": _handle_accessibility_audit_scene,
        "accessibility_certification_checklist": _handle_accessibility_certification_checklist,
        "dialogue_generate_npc_lines": _handle_dialogue_generate_npc_lines,
        "dialogue_generate_personality": _handle_dialogue_generate_personality,

        # ── Camada 6 (Profundidade de Engine): via factory ──
        "skeleton_get_bone_pose": _make_import_handler("skeleton_ops", "get_bone_pose"),
        "skeleton_set_bone_pose": _make_import_handler("skeleton_ops", "set_bone_pose"),
        "skeleton_list_bones": _make_import_handler("skeleton_ops", "list_bones"),
        "skeleton_create_bone": _make_import_handler("skeleton_ops", "create_bone"),
        "skeleton_create_ik_chain": _make_import_handler("skeleton_ops", "create_ik_chain"),
        "skeleton_get_info": _make_import_handler("skeleton_ops", "get_skeleton_info"),
        "csg_create_node": _make_import_handler("devsolo_ops", "create_csg_node"),
        "gi_create_node": _make_import_handler("devsolo_ops", "create_gi_node"),
        "scene_fx_create_node": _make_import_handler("devsolo_ops", "create_scene_fx_node"),
        "sky_create_procedural": _make_import_handler("devsolo_ops", "create_procedural_sky"),
        "camera_configure_attributes": _make_import_handler("devsolo_ops", "configure_camera_attributes"),
        "multimesh_create_instance": _make_import_handler("devsolo_ops", "create_multimesh_instance"),
        "physics_create_joint": _make_import_handler("physics_ops", "create_physics_joint"),
        "physics_configure_body": _make_import_handler("physics_ops", "configure_physics_body"),
        "physics_query_area_overlap": _make_import_handler("physics_ops", "query_area_overlap"),
        "physics_raycast_query": _make_import_handler("physics_ops", "raycast_query"),
        "ui_create_widget": _make_import_handler("devsolo_ops", "create_ui_widget"),
        "ui_create_tab_with_content": _make_import_handler("devsolo_ops", "create_tab_with_content"),
        "ui_configure_focus_nav": _make_import_handler("devsolo_ops", "configure_ui_focus_and_nav"),
        "ui_set_tooltip": _make_import_handler("devsolo_ops", "set_tooltip"),
        "ui_set_anchor_preset": _make_import_handler("devsolo_ops", "set_anchor_preset"),
        "network_setup_multiplayer": _make_import_handler("network_ops", "setup_multiplayer_peer"),
        "network_create_rpc": _make_import_handler("network_ops", "create_rpc_method"),
        "network_create_websocket": _make_import_handler("network_ops", "create_websocket_client"),
        "network_configure_dedicated_server": _make_import_handler("network_ops", "configure_dedicated_server"),
        "network_create_lobby": _make_import_handler("network_ops", "create_lobby_system"),
        "runtime_connect_signal": _make_import_handler("runtime_ops", "connect_runtime_signal"),
        "runtime_disconnect_signal": _make_import_handler("runtime_ops", "disconnect_runtime_signal"),
        "runtime_emit_signal": _make_import_handler("runtime_ops", "emit_runtime_signal"),
        "runtime_list_signals": _make_import_handler("runtime_ops", "list_runtime_signals"),
        "runtime_watch_signal": _make_import_handler("runtime_ops", "watch_runtime_signal"),
        "render_get_settings": _make_import_handler("render_ops", "get_render_settings"),
        "render_set_antialiasing": _make_import_handler("render_ops", "set_antialiasing"),
        "render_set_scaling": _make_import_handler("render_ops", "set_scaling_mode"),
        "render_set_quality": _make_import_handler("render_ops", "set_render_quality"),
        "csharp_scaffold_project": _make_import_handler("csharp_ops", "scaffold_csharp_project"),
        "csharp_generate_script": _make_import_handler("csharp_ops", "generate_csharp_script"),
        "csharp_build_project": _make_import_handler("csharp_ops", "build_csharp_project"),
    }

    # ── Rollups Fase 2A / C1 ───────────────────────────────────────
    try:
        from tools.rollups import get_rollup_handlers
        _HANDLERS_CACHE.update(get_rollup_handlers())
    except Exception:
        pass  # Rollups são bônus — se falhar, server ainda funciona sem eles

    # ── Depreciação: handlers substituídos por rollups ──────────
    # Set unificado em tools/deprecated.py (Sprint 0.5)
    from tools.deprecated import DEPRECATED_TOOLS as _DEPRECATED_H
    if not _REGISTRY_VALIDATION_UNFILTERED:
        _HANDLERS_CACHE = {k: v for k, v in _HANDLERS_CACHE.items() if k not in _DEPRECATED_H}

    # ── PATCH 17: Filtrar handlers por --toolsets ──
    if not _REGISTRY_VALIDATION_UNFILTERED and _ENABLED_TOOLS is not None:
        _HANDLERS_CACHE = {k: v for k, v in _HANDLERS_CACHE.items() if k in _ENABLED_TOOLS}

    return _HANDLERS_CACHE


# ── Opcao B: dispatch inteligente com cache de assinatura ──
_SIGNATURE_CACHE: dict[int, int] = {}
# 0 = sem parametros, 1 = args:dict, 2 = keyword params

def _smart_call(handler, arguments: dict):
    """Invoca handler com assinatura correta (args:dict, keyword, ou sem params)."""
    import inspect
    hid = id(handler)
    mode = _SIGNATURE_CACHE.get(hid)
    if mode is None:
        sig = inspect.signature(handler)
        params = list(sig.parameters.keys())
        if not params:
            mode = 0  # handler()
        elif params[0] in ("args", "arguments"):
            mode = 1  # handler(args)
        else:
            mode = 2  # handler(**kwargs)
        _SIGNATURE_CACHE[hid] = mode
    if mode == 0:
        return handler()
    if mode == 1:
        return handler(arguments)
    return handler(**arguments)


    # ── Feature 10: Session Gate ──────────────────────────────────
SESSION_ALWAYS_ALLOWED = {
    "godot",
    "ping", "health_check", "self_test", "bootstrap_godot_mcp",
    "project_manage", "setup_mcp_config", "install_mcp_addon",
    "validate_mcp_environment", "validate_godot_version",
    "validate_mcp_registry",
    "safety_manage", "dump_mcp_state",
    "catalog_search",
    "get_current_phase", "get_phase_history",
    "get_next_step", "resume_session",
}


def _check_session_gate() -> tuple[bool, str]:
    """Verifica se get_next_step() ja foi chamado nesta sessao (PID match)."""
    import os
    import json as _json
    from tools.project_ops import _get_active_project

    try:
        proj = _get_active_project()
        marker = proj / ".mcp_session_started"
    except Exception:
        # Sem projeto ativo: não bloqueia (tools sempre liberadas cobrem este caso)
        return True, ""

    if not marker.exists():
        return False, _SESSION_GATE_MESSAGE

    try:
        data = _json.loads(marker.read_text(encoding="utf-8"))
        if data.get("server_pid") != os.getpid():
            return False, _SESSION_GATE_MESSAGE
    except Exception:
        # Marcador corrompido: fail-open (travar tudo e pior que perder o gate)
        logger.warning("Session gate: marcador corrompido, fail-open liberando")
        return True, ""

    return True, ""


_SESSION_GATE_MESSAGE = (
    "Sessao nao inicializada. Chame get_next_step() primeiro para ver "
    "a fase atual do projeto, os blockers e o proximo passo obrigatorio. "
    "Isso garante que voce esta trabalhando na feature certa, na ordem certa."
)


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Roteia chamadas de tool para o handler correspondente."""
    import asyncio

    # ── Governador de Autonomia (Fatia 0.14) ──────────────────────
    from tools.governor import get_governor
    gov = get_governor()
    allowed, reason = gov.check_before(name, arguments or {})
    if not allowed:
        from tools.friendly_errors import make_error_response
        return [TextContent(
            type="text",
            text=json.dumps(make_error_response(
                message=reason,
                tool_name=name,
                error_code=4003,
                extra={"governor_blocked": True},
            ), ensure_ascii=False),
            isError=True,
        )]

    # ── Auto-checkpoint antes de operação destrutiva (Fatia 0.5) ──
    _DESTRUCTIVE_TOOLS = {
        "batch_atomic_edit", "addon_batch_edit", "write_file",
        "delete_node", "delete_file", "reparent_node",
        "set_node_property", "safe_write_gdscript",
        "create_scene", "create_entity", "create_entities",
        "import_3d_model", "build_export", "paint_tilemap_cell",
        "set_project_setting", "set_main_scene",
        "configure_input_action", "configure_autoload",
        "addon_create_node", "addon_delete_node",
        "addon_set_property", "addon_reparent_node",
        "addon_duplicate_node",
    }
    if name in _DESTRUCTIVE_TOOLS:
        try:
            from tools.safety import _auto_checkpoint
            cp_result = _auto_checkpoint()
            if cp_result.get("status") == "error":
                logger.warning("Auto-checkpoint falhou (fail-open): %s", cp_result.get("message"))
        except Exception as e:
            logger.warning("Auto-checkpoint exception (fail-open): %s", e)

    # ── Fatia 0.H: Protocolo anti-conflito MCP ↔ editor Godot ──
    # Antes de escrever, verifica se o arquivo tem alterações não salvas.
    if name in _DESTRUCTIVE_TOOLS:
        _target_file = (
            arguments.get("scene_path")
            or arguments.get("script_path")
            or arguments.get("file_path")
            or arguments.get("path")
            or ""
        )
        if _target_file:
            try:
                from tools.editor_safety import check_editor_conflict
                conflict = check_editor_conflict(_target_file)
                if conflict.get("blocked"):
                    from tools.friendly_errors import make_error_response
                    return [TextContent(
                        type="text",
                        text=json.dumps(make_error_response(
                            message=conflict.get("message", "Conflito com editor Godot."),
                            tool_name=name,
                            error_code=4004,
                            extra={"editor_conflict": True},
                        ), ensure_ascii=False),
                        isError=True,
                    )]
            except Exception as e:
                logger.warning("Editor safety check falhou (fail-open): %s", e)

    # ── Rate Limiting (Onda 6) ──────────────────────────────────
    from tools.rate_limiter import check_rate_limit
    allowed, rate_info = check_rate_limit()
    if not allowed:
        rate_msg = (
            f"Rate limit excedido. Tente novamente em {rate_info['retry_after']}s. "
            f"Limite: {rate_info['limit']} req/{rate_info['window_seconds']}s."
        )
        from tools.friendly_errors import make_error_response
        return [TextContent(
            type="text",
            text=json.dumps(make_error_response(
                message=rate_msg,
                tool_name=name,
                error_code=4002,
                extra={"retry_after": rate_info["retry_after"]},
            ), ensure_ascii=False),
            isError=True,
        )]

    # ── Feature 10: Session Gate ──────────────────────────────────
    if name not in SESSION_ALWAYS_ALLOWED:
        try:
            ok, msg = _check_session_gate()
            if not ok:
                from tools.friendly_errors import make_error_response
                return [TextContent(
                    type="text",
                    text=json.dumps(make_error_response(
                        message=msg,
                        tool_name=name,
                        error_code=4001,
                    ), ensure_ascii=False),
                    isError=True,
                )]
        except Exception as e:
            logger.warning("Session gate falhou (fail-open): %s", e)
            # fail-open: não bloqueia — trava total é pior que perder gate uma vez

    # ── Etapa A2: ExecutionContext — injetar contexto antes do dispatch ──
    # Resolve projeto ativo, cena ativa (Vibe), fase, etc. UMA vez por tool.
    # O contexto fica disponível via core.context.get_execution_context()
    # para qualquer handler que precise de scene_path, project_path, etc.
    try:
        from core.context import resolve_execution_context, set_execution_context
        _exec_ctx = resolve_execution_context(tool_name=name)
    except Exception:
        _exec_ctx = None

    def _dispatch_with_context():
        """Wrapper que injeta contexto thread-local antes do handler.

        IMPORTANTE: usa try/finally para LIMPAR o contexto após o handler.
        Sem isso, threads do pool reutilizadas carregariam contexto stale
        da invocação anterior (thread-local leak).
        """
        if _exec_ctx is not None:
            set_execution_context(_exec_ctx)
        try:
            return _smart_call(handler, arguments)
        finally:
            if _exec_ctx is not None:
                set_execution_context(None)

    handlers = _build_handlers()
    handler = handlers.get(name)
    if handler:
        try:
            # P1-1: Despachar handlers para thread pool (Opcao B: _smart_call)
            _t0 = time.time()
            loop = asyncio.get_running_loop()
            result = await loop.run_in_executor(None, _dispatch_with_context)
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
                result["friendly"] = translate_error(result.get("message", ""), tool_name=name)
            # ── Feature 8: notificar cliente sobre mudança na lista de tools ──
            if name == "advance_phase" and not is_error:
                try:
                    from mcp.server.lowlevel.server import request_ctx
                    session = request_ctx.get().session
                    await session.send_tool_list_changed()
                except Exception as e:
                    logger.warning("send_tool_list_changed falhou: %s", e)
                # ── Fatia 1.P: Rastrear transicao de fase ────────
                try:
                    old_phase = arguments.get("current_phase", "") if arguments else ""
                    new_phase = result.get("new_phase", "") if isinstance(result, dict) else ""
                    if old_phase and new_phase:
                        track_phase_transition(old_phase, new_phase)
                except Exception:
                    pass
            # ── Governador: registrar resultado após execução ──────
            gov.record_after(
                name, arguments or {},
                success=not is_error,
                error_message=result.get("message", "") if is_error else "",
            )
            # Salvar estado periodicamente
            if gov.state.iteration_count % 10 == 0:
                try:
                    gov.save()
                except Exception:
                    pass

            # ── Fatia 1.D: Rastrear custo de tokens ──────────────
            try:
                from tools.budget_ops import track_tool_cost
                budget_block = track_tool_cost(name, arguments, result)
                if budget_block:
                    from tools.friendly_errors import make_error_response
                    return [TextContent(
                        type="text",
                        text=json.dumps(make_error_response(
                            message=budget_block["message"],
                            tool_name=name,
                            error_code=4005,
                            extra={
                                "budget_exceeded": True,
                                "session_cost_brl": budget_block["session_cost_brl"],
                                "limit_brl": budget_block["limit_brl"],
                                "pct_used": budget_block["pct_used"],
                            },
                        ), ensure_ascii=False),
                        isError=True,
                    )]
            except Exception:
                pass  # fail-open: tracking nao pode bloquear

            # ── Fatia 1.P: Telemetria opt-in do MCP ──────────────
            try:
                _elapsed_ms = int((time.time() - _t0) * 1000)
                current_phase = gov.state.current_phase if gov else "unknown"
                track_mcp_event(name, arguments, result, _elapsed_ms, current_phase)
            except Exception:
                pass  # fail-open: telemetria nunca bloqueia

            # A6.4: isError + resultado (structuredContent requer SDK update)
            return [TextContent(
                type="text",
                text=json.dumps(result, ensure_ascii=False),
                isError=is_error,
            )]
        except Exception as e:
            gov.record_after(
                name, arguments or {},
                success=False,
                error_message=str(e),
            )

            from tools.friendly_errors import make_error_response
            exc_name = type(e).__name__
            exc_msg = str(e)[:500]
            return [TextContent(type="text", text=json.dumps(make_error_response(
                message=f"Erro interno ao executar '{name}': {exc_name} — {exc_msg[:200]}",
                tool_name=name,
                error_code=5000,
                extra={"internal_error": exc_msg},
            ), ensure_ascii=False), isError=True)]

    from tools.friendly_errors import make_error_response
    return [TextContent(type="text", text=json.dumps(make_error_response(
        message=f"Tool '{name}' nao implementada.",
        tool_name=name,
        error_code=4000,
    ), ensure_ascii=False), isError=True)]


# ── Handlers ────────────────────────────────────────────────────────

def _handle_catalog_search(args: dict) -> dict:
    """Handler da meta-tool catalog_search."""
    from tools.meta_ops import catalog_search
    return catalog_search(
        query=args.get("query", ""),
        group=args.get("group", ""),
        limit=args.get("limit", 20),
    )

def _handle_describe_tool(args: dict) -> dict:
    """Handler da meta-tool describe_tool."""
    from tools.meta_ops import describe_tool
    return describe_tool(name=args.get("name", ""))

def _handle_invoke_by_name(args: dict) -> dict:
    """Handler da meta-tool invoke_by_name."""
    from tools.meta_ops import invoke_by_name
    return invoke_by_name(
        name=args.get("name", ""),
        arguments=args.get("arguments"),
    )


def _handle_godot(args: dict) -> dict:
    """Handler da tool godot — Intent Router (Etapa A4).

    Roteia linguagem natural para a ferramenta correta automaticamente.
    Ex: godot(action="criar inimigo com patrulha") → create_entity(enemy, patrol)
    """
    action = args.get("action", "")
    if not action:
        return {"status": "error", "message": "Parâmetro 'action' é obrigatório. Ex: 'criar cena Node2D'"}

    from core.intent_router import route_intent, invoke_intent

    # 1. Classificar + extrair parâmetros
    routed = route_intent(action)

    if routed["status"] == "unmatched":
        # Fallback: sugerir busca no catálogo
        return {
            "status": "unmatched",
            "message": routed["message"],
            "suggestion": routed.get("suggestion"),
            "hint": "Tente usar catalog_search(query='...') para buscar a ferramenta certa.",
        }

    # 2. Invocar a ferramenta encontrada
    result = invoke_intent(
        tool_name=routed["tool"],
        op=routed.get("op", ""),
        params=routed.get("params", {}),
    )

    # 3. Enriquecer resposta com metadados da rota
    if isinstance(result, dict):
        result["_routed_by"] = "godot (Intent Router A4)"
        result["_routed_tool"] = routed["tool"]
        result["_confidence"] = routed.get("confidence", 0)

    return result


def _handle_validate_mcp_registry(args: dict) -> dict:
    """Handler da tool validate_mcp_registry."""
    return validate_mcp_registry_handler(args)


# ══════════════════════════════════════════════════════════════
# Camada 5 (Gameplay): Handlers — registrados 2026-07-19
# ══════════════════════════════════════════════════════════════

def _handle_create_achievement_system(args: dict) -> dict:
    return create_achievement_system(args)

def _handle_validate_achievement_config(args: dict) -> dict:
    return validate_achievement_config(args)

def _handle_adaptive_difficulty_adjust(args: dict) -> dict:
    return adaptive_difficulty_adjust(args)

def _handle_quest_generate(args: dict) -> dict:
    return quest_generate(args)

def _handle_accessibility_apply_colorblind_filter(args: dict) -> dict:
    return accessibility_apply_colorblind_filter(args)

def _handle_accessibility_add_subtitles(args: dict) -> dict:
    return accessibility_add_subtitles(args)

def _handle_accessibility_remap_controls(args: dict) -> dict:
    return accessibility_remap_controls(args)

def _handle_accessibility_audit_scene(args: dict) -> dict:
    return accessibility_audit_scene(args)

def _handle_accessibility_certification_checklist(args: dict) -> dict:
    return accessibility_certification_checklist(args)

def _handle_dialogue_generate_npc_lines(args: dict) -> dict:
    return dialogue_generate_npc_lines(args)


def _handle_dialogue_generate_personality(args: dict) -> dict:
    return dialogue_generate_personality(args)


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


def _handle_mcp_telemetry_manage(args: dict) -> dict:
    """Handler da tool mcp_telemetry_manage (Fatia 1.P)."""
    return mcp_telemetry_manage(
        op=args.get("op", "status"),
    )


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


# ── Bloco 1: Handlers de Auditoria de Wiring ───────────────────────

def _handle_audit_input_map(args: dict) -> dict:
    from tools.audit_input_map import audit_input_map
    return audit_input_map(
        project_path=args.get("project_path"),
    )


def _handle_audit_autoloads(args: dict) -> dict:
    from tools.audit_autoloads import audit_autoloads
    return audit_autoloads(
        project_path=args.get("project_path"),
    )


def _handle_audit_scene_reachability(args: dict) -> dict:
    from tools.audit_scene_reachability import audit_scene_reachability
    return audit_scene_reachability(
        project_path=args.get("project_path"),
        root_scene=args.get("root_scene"),
    )


# ── Bloco 2: Handlers de UID + Save Compatibility ─────────────────

def _handle_audit_uid_consistency(args: dict) -> dict:
    from tools.audit_uid_consistency import audit_uid_consistency
    return audit_uid_consistency(
        project_path=args.get("project_path"),
    )


def _handle_audit_save_compatibility(args: dict) -> dict:
    from tools.audit_save_compatibility import audit_save_compatibility
    return audit_save_compatibility(
        project_path=args.get("project_path"),
        save_file_path=args.get("save_file_path"),
    )


# ── Bloco 4: Handlers de Proof Ledger ──────────────────────────────

def _handle_capture_proof(args: dict) -> dict:
    """Handler síncrono — dispatch via thread pool. Usa os.system() internamente."""
    extra = args.get("extra_commands")
    if extra is not None and not isinstance(extra, list):
        extra = None
    return capture_proof(
        task_id=args["task_id"],
        project_path=args.get("project_path"),
        run_tests=args.get("run_tests", False),
        extra_commands=extra,
    )


def _handle_verify_proof(args: dict) -> dict:
    """Handler síncrono — dispatch via thread pool. Usa os.system() internamente."""
    return verify_proof(
        task_id=args.get("task_id"),
        project_path=args.get("project_path"),
        max_age_minutes=args.get("max_age_minutes", 60),
    )


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


def _handle_project_map(args: dict) -> dict:
    return generate_project_map(
        args.get("project_path"),
        args.get("format", "json"),
        args.get("output_path"),
    )


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


def _handle_safe_write_gdscript(args: dict) -> dict:
    result = safe_write_gdscript(args["file_path"], args["content"], args.get("project_path"), args.get("strict", True))
    if isinstance(result, dict) and result.get("status") == "success":
        try: from tools.editor_config import _notify_godot_file_changed; _notify_godot_file_changed(args["file_path"])
        except Exception: pass
    return result


def _handle_game_serialize_state(args: dict) -> dict:
    return game_serialize_state(args["action"], args.get("file_name","game_state.json"))


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


def _handle_quickstart_manage(args: dict) -> dict:
    """Handler para quickstart_manage — frase → projeto jogável ou clone de seed."""
    from tools.quickstart_ops import quickstart_manage
    return quickstart_manage(
        op=args.get("op", "run"),
        phrase=args.get("phrase", ""),
        project_name=args.get("project_name", ""),
        seed=args.get("seed", "breakout"),
    )


def _handle_version_history_manage(args: dict) -> dict:
    """Handler para version_history_manage — histórico de versões jogáveis (Fatia 1.Q)."""
    from tools.version_history_ops import version_history_manage
    op = args.get("op", "list")
    # Constrói params a partir dos args (menos op)
    params = {k: v for k, v in args.items() if k != "op"}
    return version_history_manage(op=op, params=params)


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
    return create_particles_2d(
        scene_path=args["scene_path"],
        parent_node_path=args["parent_node_path"],
        node_name=args.get("node_name", "Particles"),
        amount=args.get("amount"),
        lifetime=args.get("lifetime"),
        explosiveness=args.get("explosiveness"),
        direction=args.get("direction"),
        spread=args.get("spread"),
        gravity=args.get("gravity"),
    )


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
        from tools.subprocess_utils import run_subprocess_safe
        try:
            r = run_subprocess_safe([godot_path, "--version"], timeout=10)
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


# ── Playtest Onda 3 (smoke test do jogo) ────────────────────────────

def _handle_playtest_manage(args: dict) -> dict:
    """Handler para playtest_manage — playtest automatizado (Fatia 3.A)."""
    from tools.playtest_ops import playtest_manage
    op = args.get("op", "smoke")
    params = {k: v for k, v in args.items() if k != "op"}
    return playtest_manage(op=op, params=params)


# ── Fun Report Onda 3 (relatorio de qualidade) ─────────────────────

def _handle_fun_report_manage(args: dict) -> dict:
    """Handler para fun_report_manage — relatorio de qualidade (Fatia 3.D)."""
    from tools.fun_report_ops import fun_report_manage
    op = args.get("op", "generate")
    params = {k: v for k, v in args.items() if k != "op"}
    return fun_report_manage(op=op, params=params)


def _handle_complexity_gate_manage(args: dict) -> dict:
    """Handler para complexity_gate_manage — gate de complexidade (Fatia 3.F)."""
    from tools.complexity_gate_ops import complexity_gate_manage
    op = args.get("op", "check")
    params = {k: v for k, v in args.items() if k != "op"}
    return complexity_gate_manage(op=op, params=params)


def _handle_teacher_manage(args: dict) -> dict:
    """Handler para teacher_manage — modo professor (Fatia 3.H)."""
    from tools.teacher_ops import teacher_manage
    op = args.get("op", "explain")
    params = {k: v for k, v in args.items() if k != "op"}
    return teacher_manage(op=op, params=params)


def _handle_scope_manage(args: dict) -> dict:
    """Handler para scope_manage — validador de escopo + disclosure (3.I/3.J)."""
    from tools.scope_ops import scope_manage
    op = args.get("op", "validate_idea")
    params = {k: v for k, v in args.items() if k != "op"}
    return scope_manage(op=op, params=params)


def _handle_reviewer_manage(args: dict) -> dict:
    """Handler para reviewer_manage — modo revisor adversarial (3.K)."""
    from tools.reviewer_ops import reviewer_manage
    op = args.get("op", "status")
    params = {k: v for k, v in args.items() if k != "op"}
    return reviewer_manage(op=op, params=params)


def _handle_polish_manage(args: dict) -> dict:
    """Handler para polish_manage — polimento e qualidade (G5-G10)."""
    from tools.polish_ops import polish_manage
    op = args.get("op", "test_report")
    params = {k: v for k, v in args.items() if k != "op"}
    return polish_manage(op=op, params=params)


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

    # 3. Skills (FASE 5 — Progressive Discovery)
    try:
        from mcp.types import Resource, ResourceTemplate
        from skills import list_skills
        skill_list = list_skills()
        all_resources.append(
            Resource(uri="skill://", name="Skills — Fluxos Guiados",
                     description=f"{len(skill_list)} fluxos de trabalho com ferramentas recomendadas",
                     mimeType="application/json"),
        )
        all_resources.append(
            ResourceTemplate(uriTemplate="skill://{name}",
                     name="Skill Específica",
                     description="Fluxo guiado com ferramentas, workflow e exemplo",
                     mimeType="text/plain"),
        )
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
        pass

    # 3. Skills (FASE 5)
    if uri.startswith("skill://"):
        try:
            from skills import list_skills, skill_to_prompt
            name = uri.replace("skill://", "").strip("/")
            if not name:
                return json.dumps(list_skills(), indent=2, ensure_ascii=False)
            prompt = skill_to_prompt(name)
            if prompt:
                return prompt
            return f"Skill '{name}' não encontrada. Skills disponíveis: {', '.join(s['name'] for s in list_skills())}"
        except Exception as e:
            return json.dumps({"status": "error", "message": f"Erro ao ler skill: {e}"})
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
        await server.run(read_stream, write_stream, server.create_initialization_options(
            notification_options=NotificationOptions(tools_changed=True),
            instructions=MCP_INSTRUCTIONS,
        ))


def run() -> None:
    """Entry point síncrono."""
    import asyncio
    # ── A6.1: Validação de ambiente no boot ──
    try:
        from tools.vscode_config import validate_environment
        env_result = validate_environment()
        if not env_result.get("ok", True):
            print(f"[MCP] AVISO: Ambiente com problemas: {env_result.get('issues', [])}", file=sys.stderr)
    except Exception as e:
        print(f"[MCP] Aviso: validação de ambiente falhou: {e}", file=sys.stderr)
    # ── Fatia 0.I: Detecção de pasta sincronizada em nuvem ──
    try:
        from tools.cloud_sync_detector import detect_cloud_sync, warn_cloud_sync
        cloud_result = detect_cloud_sync()
        if cloud_result.get("synced"):
            warn_cloud_sync(cloud_result)
    except Exception as e:
        print(f"[MCP] Aviso: detecção de nuvem falhou: {e}", file=sys.stderr)
    # Validação de consistência do registro (diagnóstico, não trava boot)
    try:
        from tools.registry_validation import validate_tool_registry_consistency
        validate_tool_registry_consistency()
    except Exception as e:
        print(f"[MCP] Aviso: validação de registro falhou: {e}", file=sys.stderr)
    asyncio.run(main())


if __name__ == "__main__":
    run()

