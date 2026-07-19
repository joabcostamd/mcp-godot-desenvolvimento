"""dynamic_groups.py — Dynamic Tool Groups (Fase 3 / GoPeak).

Grupos dinâmicos de tools: catalog, groups, ativação sob demanda.
Inspirado no HaD0Yun/GoPeak (tool.catalog, tool.groups).

Tools:
    - tool_catalog: busca e lista tools por grupo (scoring ponderado + aliases PT→EN)
    - tool_groups: ativa/desativa grupos de tools
"""

import json
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GROUPS_FILE = ROOT / ".tool_groups.json"

# ── Etapa A1: 5 Namespaces Semânticos ─────────────────────────────
# Substitui os 13 grupos anteriores por 5 namespaces hierárquicos.
# Cada namespace agrupa tools por domínio funcional.
# A IA primeiro vê os 5 namespaces, depois explora as tools de um namespace.

GROUPS = {
    "project": [
        "project_manage", "project_status", "project_map",
        "scene_manage", "node_manage",
        "script_manage", "safe_write_gdscript",
        "file_manage", "read_file", "write_file",
        "ui_manage",
        "create_entity", "create_entities",
        "generate_project_structure",
        "physics_manage", "anim_manage", "camera_manage",
        "tilemap_manage", "navigation_manage",
        "gamestate_manage", "dialogue_manage", "inventory_manage",
        "d3_manage", "config_manage",
        "setup_localization", "add_translation_string",
        "behavior_tree_generate", "behavior_tree_list_templates",
        "world_describe",
        "batch_atomic_edit", "add_nodes_batch", "set_properties_batch",
        "load_scene_async",
        # Templates de gameplay
        "create_gun_system", "create_bullet_template",
        "create_parallax_background", "add_parallax_layer", "create_spritesheet",
        "create_path_2d", "create_patrol_route",
        "loot_table_generate", "create_animation_tree",
        # Operações atômicas (complementam rollups)
        "raycast_manage",
        "add_raycast_2d", "add_shapecast_2d",
        "create_joint_2d",
        "create_light_2d", "create_light_3d",
        "create_navigation_agent_2d", "create_navigation_region_2d",
        "setup_camera_2d",
    ],
    "assets": [
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
        "generate_dungeon_rooms", "dungeon_generate",
        "terrain_generate", "wave_generate",
        "juice_apply", "juice_list_presets",
        # Operações atômicas (complementam rollups)
        "configure_particles_2d", "create_particles_2d", "create_particles_3d",
        "configure_standard_material_3d",
        "generate_shader_2d",
        "import_3d_model",
    ],
    "runtime": [
        "runtime_manage",
        "execute_gdscript_runtime", "capture_game_screenshot", "take_screenshot",
        "godot_run_project", "godot_stop_project", "godot_wait_for_bridge",
        "godot_exec", "godot_runtime_info", "godot_screenshot",
        "godot_custom_command", "godot_list_custom_commands",
        "godot_keep_alive",
        "get_runtime_state_digest", "capture_runtime_errors",
        "freeze_game_clock", "unfreeze_game_clock", "step_game_time", "step_until",
        "effect_probe",
        "debug_manage",
        "debugger_set_breakpoint", "debugger_status", "debugger_step",
        "debugger_get_stack", "debugger_get_variables",
        "test_manage",
        "run_gut_tests", "run_scripted_tests", "regression_test", "smoke_test",
        "run_verification_pipeline", "run_stress_test",
        "assert_node_exists",
        "game_bridge_manage",
        "game_http_request", "game_multiplayer",
        "game_call_method", "game_spawn_node", "game_raycast", "game_get_camera",
        "game_play_animation", "game_find_nodes_by_class", "game_await_signal",
        "game_pause", "game_performance", "game_window", "game_input_state",
        "game_serialize_state",
        "inject_input_event", "simulate_input_sequence",
        "watch_signal", "watch_state_start", "watch_state_collect",
        "record_gameplay_gif", "start_recording", "stop_recording",
        "addon_connect", "addon_disconnect", "addon_ping", "addon_is_available",
        "addon_get_scene_tree", "addon_take_screenshot",
        "addon_create_node", "addon_delete_node", "addon_set_property",
        "addon_duplicate_node", "addon_reparent_node", "addon_batch_edit",
        "read_console_output",
        "profile_frame", "profile_memory", "auto_screenshot",
        "build_csharp", "export_manage",
        "playtest_manage",
    ],
    "analysis": [
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
    ],
    "orchestration": [
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
    ],
}

# ── Hierarquia de Namespaces (para tool_groups list) ──────────────
# Namespace → descrição curta em PT-BR para a IA
NAMESPACE_INFO = {
    "project":       "🏗️ Projeto — Cenas, scripts, arquivos, UI, gameplay estrutural",
    "assets":        "🎨 Assets — Arte, áudio, shaders, VFX, geração procedural",
    "runtime":       "▶️ Runtime — Execução, debug, testes, bridge, jogo rodando",
    "analysis":      "🔍 Analysis — Auditoria, qualidade, referências, introspecção",
    "orchestration": "🎛️ Orchestration — Meta-tools, workflow, governança, segurança",
}

# ── Aliases PT→EN para buscas em português ──
# Chaves e valores normalizados (sem acento, lowercase).
# "no"/"nó" NÃO está mapeado → risco de falso positivo sistemático
# (contração comum "em"+"o" apareceria em qualquer frase PT).
QUERY_ALIASES = {
    "criar": "create",
    "cena": "scene",
    "compilar": "compile build",
    "gerar": "generate create",
    "sprite": "sprite",
    "adicionar": "create",
    "sinal": "signal",
    "conectar": "connect",
    "remover": "delete remove",
    "salvar": "save",
    "carregar": "load",
    "executar": "run",
    "projeto": "project",
    "arquivo": "file",
    "script": "script",
    "audio": "audio",
    "som": "audio sound",
    "textura": "texture",
    "animacao": "animation",
    "fisica": "physics",
    "colisao": "collision",
    "camera": "camera",
    "ui": "ui interface",
    "interface": "ui interface",
    "menu": "menu",
    "inimigo": "enemy",
    "jogador": "player",
    "mapa": "map tilemap",
    "exportar": "export build",
    "importar": "import",
    "testar": "test",
    "depurar": "debug",
    "otimizar": "optimize",
    "configurar": "configure setup",
    "instalar": "install",
    "validar": "validate",
    "buscar": "search find",
    "procurar": "search find",
}

# Aliases que só aplicam quando o token original tem acento.
# Chave = forma normalizada (sem acento). Evita que "no" (contração)
# seja expandido para "node", mas permite "nó" → "node".
QUERY_ALIASES_ACCENT_ONLY = {
    "no": "node",       # "nó" → "node"
}


def _normalize(text: str) -> str:
    """Remove acentos e normaliza para lowercase ASCII."""
    nfkd = unicodedata.normalize('NFKD', text)
    return ''.join(c for c in nfkd if not unicodedata.combining(c)).lower()


def _expand_query(query: str) -> str:
    """Expande query PT com aliases → EN. Termos sem alias passam normalizados."""
    tokens = query.split()
    expanded = []
    for token in tokens:
        norm = _normalize(token)
        # 1) Alias padrão (chave normalizada)
        alias = QUERY_ALIASES.get(norm, "")
        if alias:
            expanded.append(alias)
        # 2) Alias com acento obrigatório (token original != normalizado)
        elif token != norm:
            alias_acc = QUERY_ALIASES_ACCENT_ONLY.get(norm, "")
            if alias_acc:
                expanded.append(alias_acc)
            else:
                expanded.append(norm)
        else:
            expanded.append(norm)
    return ' '.join(expanded)


def _get_rollup_ops_map() -> dict[str, list[str]]:
    """Extrai as ops keys (em ingles) dos rollups em tools/rollups.py.

    Ex: {"scene_manage": ["create", "load_tree", "instance"], ...}
    Cacheado em memória após a primeira chamada.
    """
    if _get_rollup_ops_map._cache is not None:
        return _get_rollup_ops_map._cache
    result = {}
    try:
        import re as _re2
        rollup_text = Path(__file__).resolve().parent / "rollups.py"
        if rollup_text.exists():
            text = rollup_text.read_text(encoding='utf-8')
            for block in text.split('def _build_'):
                tn_match = _re2.search(r'tool_name="(\w+)"', block)
                if not tn_match:
                    continue
                tool_name = tn_match.group(1)
                # Extrair chaves do dict ops={...}
                ops_match = _re2.search(r'ops=\{\s*\n((?:\s*"[^"]+":\s*\w+,?\s*\n?)*)\s*\}', block)
                if ops_match:
                    result[tool_name] = _re2.findall(r'"(\w+)"', ops_match.group(1))
    except Exception:
        pass
    _get_rollup_ops_map._cache = result
    return result
_get_rollup_ops_map._cache = None


def tool_catalog(query: str = "", group: str = "", limit: int = 20, namespace: str = "") -> dict:
    """Busca tools no catálogo por nome, grupo ou namespace.

    Usa scoring ponderado (nome 3pts, ops 2pts, descrição 1pt)
    com aliases PT→EN para buscas em português e bônus de +1
    para rollups (ferramentas agregadoras recomendadas).

    Args:
        query: Texto para buscar. Aceita português ou inglês.
        group: (legado) Filtrar por grupo/namespace.
        limit: Máximo de resultados.
        namespace: Filtrar por namespace semântico (project, assets, runtime, analysis, orchestration).

    Returns:
        dict com tools encontradas, grupos disponíveis e namespaces.
    """
    from server import _tool_defs
    tools = _tool_defs()
    import re as _re

    # ── Expansão PT→EN ──
    if query:
        query = _expand_query(query)

    # ── Scoring por token ──
    _rollup_ops = {}
    if query:
        _rollup_ops = _get_rollup_ops_map()
        expanded_tokens = _re.split(r'[\s_]+', query.lower())
        scored = []
        for t in tools:
            name_lower = t.name.lower()
            name_tokens = _re.split(r'[\s_]+', name_lower)
            ops_terms = _re.split(r'[\s_]+', ' '.join(_rollup_ops.get(t.name, [])).lower())
            desc_lower = (t.description or "").lower()
            desc_tokens = _re.split(r'[\s_]+', desc_lower)
            params_lower = ""
            if hasattr(t, 'inputSchema') and isinstance(t.inputSchema, dict):
                params_lower = ' '.join(t.inputSchema.get("properties", {}).keys()).lower()
            params_tokens = _re.split(r'[\s_]+', params_lower)

            score = 0
            for tok in expanded_tokens:
                if tok in name_tokens:
                    score += 3
                elif tok in ops_terms:
                    score += 2
                elif tok in desc_tokens:
                    score += 1
                elif tok in params_tokens:
                    score += 1
            # Bônus para rollups: +1
            if t.name in _rollup_ops:
                score += 1
            scored.append((t, score))

        # Ordenar por score desc, rollups primeiro em empate
        scored.sort(key=lambda x: (x[1], x[0].name in _rollup_ops), reverse=True)
        tools = [t for t, _ in scored]

    # ── Resolver namespace da tool via _meta ──
    def _get_tool_namespace(t) -> str:
        meta = getattr(t, 'meta', None) or {}
        return meta.get("namespace", "")

    results = []
    query_tokens = _re.split(r'[\s_]+', query.lower()) if query else []
    for t in tools:
        name = t.name
        desc = (t.description or "")[:100]
        ns = _get_tool_namespace(t)

        # Filtro por query: exige que pelo menos metade dos tokens casem
        if query_tokens:
            combined_tokens = set(_re.split(r'[\s_]+', name.lower()))
            combined_tokens.update(_re.split(r'[\s_]+', desc.lower()))
            combined_tokens.update(_re.split(r'[\s_]+', ' '.join(_rollup_ops.get(t.name, [])).lower()))
            matched = sum(1 for tok in query_tokens if tok in combined_tokens)
            if matched < max(1, len(query_tokens) // 2):
                continue

        # Filtro por namespace (prioridade sobre group legado)
        effective_filter = namespace or group
        if effective_filter:
            # Correspondência exata ou parcial com o nome do namespace
            if ns != effective_filter and effective_filter not in ns:
                # Fallback: busca no GROUPS legado
                found_in_group = False
                for gname, gtools in GROUPS.items():
                    if (gname == effective_filter or effective_filter in gname) and name in gtools:
                        found_in_group = True
                        break
                if not found_in_group:
                    continue

        results.append({
            "name": name,
            "description": desc,
            "namespace": ns,
            "groups": [g for g, gt in GROUPS.items() if name in gt],
        })

        if len(results) >= limit:
            break

    return {
        "status": "success",
        "query": query,
        "group": group,
        "namespace": namespace,
        "results": results,
        "total": len(results),
        "available_groups": list(GROUPS.keys()),
        "namespace_info": NAMESPACE_INFO,
    }


def tool_groups(action: str = "list", group: str = "", enabled: bool = True) -> dict:
    """Gerencia grupos de tools dinâmicos (5 namespaces semânticos).

    Args:
        action: "list", "activate", "deactivate", "status", "hierarchy".
        group: Nome do grupo/namespace.
        enabled: Estado de ativação.

    Returns:
        dict com estado dos grupos ou hierarquia de namespaces.
    """
    config = {}
    if GROUPS_FILE.exists():
        with open(GROUPS_FILE, encoding="utf-8") as f:
            config = json.load(f)

    groups_state = config.get("groups", {})

    if action == "hierarchy":
        # ── Visão hierárquica: 5 namespaces → tools ──
        hierarchy = {}
        total_tools = 0
        for ns, tools in GROUPS.items():
            active = groups_state.get(ns, True)
            hierarchy[ns] = {
                "description": NAMESPACE_INFO.get(ns, ""),
                "active": active,
                "tool_count": len(tools),
                "tools": tools if active else [],
            }
            if active:
                total_tools += len(tools)
        return {
            "status": "success",
            "total_namespaces": len(GROUPS),
            "total_tools_visible": total_tools,
            "namespaces": hierarchy,
        }

    if action == "list":
        return {
            "status": "success",
            "available_groups": list(GROUPS.keys()),
            "namespace_info": NAMESPACE_INFO,
            "active_groups": [g for g, v in groups_state.items() if v],
            "groups_detail": {g: {
                "active": groups_state.get(g, True),
                "tool_count": len(GROUPS.get(g, [])),
                "tools": GROUPS.get(g, []),
                "description": NAMESPACE_INFO.get(g, ""),
            } for g in GROUPS},
        }

    elif action in ("activate", "deactivate"):
        if group not in GROUPS:
            return {"status": "error", "message": f"Grupo '{group}' não existe. Disponíveis: {list(GROUPS.keys())}"}

        groups_state[group] = (action == "activate")
        config["groups"] = groups_state
        with open(GROUPS_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)

        return {
            "status": "success",
            "action": action,
            "group": group,
            "tools_affected": len(GROUPS[group]),
            "active_groups": [g for g, v in groups_state.items() if v],
        }

    return {"status": "error", "message": f"Ação desconhecida: {action}"}
