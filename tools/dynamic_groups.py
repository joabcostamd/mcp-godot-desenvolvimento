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

GROUPS = {
    "core": ["ping","health_check","bootstrap_godot_mcp","read_file","write_file"],
    "scene": ["scene_manage","node_manage","batch_atomic_edit","add_nodes_batch"],
    "script": ["script_manage","safe_write_gdscript","gdscript_diagnostics"],
    "runtime": ["runtime_manage","freeze_game_clock","get_runtime_state_digest"],
    "lsp": ["gdscript_lsp_connect","gdscript_references","gdscript_definition"],
    "dap": ["debugger_set_breakpoint","debugger_status"],
    "art": ["generate_game_art","apply_game_art","create_parallax_background"],
    "audio": ["audio_manage","generate_audio_sfx"],
    "networking": ["game_http_request","game_multiplayer"],
    "testing": ["run_gut_tests","assert_node_exists","simulate_input_sequence"],
    "assets": ["download_asset", "import_downloaded_asset", "asset_manage",
               "import_asset_manifest", "create_asset_manifest"],
    "security": ["set_safety_policy","configure_security"],
    "refs_ops": [
        "find_missing_references", "search_codebase",
        "validate_project_refs", "find_usages",
    ],
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


def tool_catalog(query: str = "", group: str = "", limit: int = 20) -> dict:
    """Busca tools no catálogo por nome ou grupo.

    Usa scoring ponderado (nome 3pts, ops 2pts, descrição 1pt)
    com aliases PT→EN para buscas em português e bônus de +1
    para rollups (ferramentas agregadoras recomendadas).

    Args:
        query: Texto para buscar. Aceita português ou inglês.
        group: Filtrar por grupo (core, scene, runtime, lsp, etc.).
        limit: Máximo de resultados.

    Returns:
        dict com tools encontradas e grupos disponíveis.
    """
    from server import _tool_defs
    tools = _tool_defs()
    import re as _re

    # ── Expansão PT→EN ──
    if query:
        query = _expand_query(query)

    # ── Scoring por token ──
    # 3 pts → nome, 2 pts → ops, 1 pt → descrição/params.
    # +1 bônus para rollups (ferramentas agregadoras recomendadas).
    # Soma ponderada, depois ordenada desc.
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

    results = []
    query_tokens = _re.split(r'[\s_]+', query.lower()) if query else []
    for t in tools:
        name = t.name
        desc = (t.description or "")[:100]

        # Filtro por query: exige que pelo menos metade dos tokens casem
        # Matching por token exato (não substring), igual ao scoring.
        if query_tokens:
            combined_tokens = set(_re.split(r'[\s_]+', name.lower()))
            combined_tokens.update(_re.split(r'[\s_]+', desc.lower()))
            combined_tokens.update(_re.split(r'[\s_]+', ' '.join(_rollup_ops.get(t.name, [])).lower()))
            matched = sum(1 for tok in query_tokens if tok in combined_tokens)
            if matched < max(1, len(query_tokens) // 2):
                continue

        # Filtro por grupo
        if group:
            found = False
            for gname, gtools in GROUPS.items():
                if (gname == group or group in gname) and name in gtools:
                    found = True
                    break
            if not found:
                continue

        results.append({
            "name": name,
            "description": desc,
            "groups": [g for g, gt in GROUPS.items() if name in gt],
        })

        if len(results) >= limit:
            break

    return {
        "status": "success",
        "query": query,
        "group": group,
        "results": results,
        "total": len(results),
        "available_groups": list(GROUPS.keys()),
    }


def tool_groups(action: str = "list", group: str = "", enabled: bool = True) -> dict:
    """Gerencia grupos de tools dinâmicos.

    Args:
        action: "list", "activate", "deactivate", "status".
        group: Nome do grupo.
        enabled: Estado de ativação.

    Returns:
        dict com estado dos grupos.
    """
    config = {}
    if GROUPS_FILE.exists():
        with open(GROUPS_FILE, encoding="utf-8") as f:
            config = json.load(f)

    groups_state = config.get("groups", {})

    if action == "list":
        return {
            "status": "success",
            "available_groups": list(GROUPS.keys()),
            "active_groups": [g for g, v in groups_state.items() if v],
            "groups_detail": {g: {"active": groups_state.get(g, True), "tools": GROUPS.get(g, [])} for g in GROUPS},
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
