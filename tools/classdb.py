"""classdb — Validação contra a API real do Godot (extension_api.json).

Carrega o cache de classdb_cache/extension_api.json e expõe funções
de consulta e validação usadas por todas as tools que manipulam nós,
propriedades e sinais.
"""

import json
from difflib import get_close_matches
from pathlib import Path
from functools import lru_cache

ROOT = Path(__file__).resolve().parent.parent
CACHE_PATH = ROOT / "classdb_cache" / "extension_api.json"

# ── Carregamento ────────────────────────────────────────────────────

_cache: dict | None = None
_last_mtime: float = 0.0


def _check_stale() -> None:
    """Invalida cache se extension_api.json foi modificado."""
    global _cache, _last_mtime
    if CACHE_PATH.exists():
        mtime = CACHE_PATH.stat().st_mtime
        if _last_mtime and mtime > _last_mtime:
            _cache = None
            _class_index.cache_clear()
        _last_mtime = mtime


def _load_cache() -> dict:
    """Carrega o cache ClassDB (lazy, com verificação de staleness)."""
    global _cache
    _check_stale()
    if _cache is None:
        with open(CACHE_PATH, encoding="utf-8") as f:
            _cache = json.load(f)
    return _cache


def _reload() -> None:
    """Força recarga do cache (útil após regenerar extension_api.json)."""
    global _cache
    _cache = None


# ── Índices ─────────────────────────────────────────────────────────

@lru_cache(maxsize=1)
def _class_index() -> dict[str, dict]:
    """Índice nome → entrada completa da classe."""
    data = _load_cache()
    return {c["name"]: c for c in data["classes"]}


@lru_cache(maxsize=1)
def _all_class_names() -> list[str]:
    """Lista de nomes de todas as classes (inclui builtin_classes)."""
    data = _load_cache()
    names = [c["name"] for c in data["classes"]]
    names.extend(c["name"] for c in data["builtin_classes"])
    return sorted(names)


@lru_cache(maxsize=1)
def _node_types() -> set[str]:
    """Conjunto de tipos que herdam de Node (podem entrar em cena)."""
    class_index = _class_index()
    node_types = set()

    def _ancestors_contain_node(name: str, visited: set) -> bool:
        if name in visited:
            return False
        visited.add(name)
        if name == "Node":
            return True
        entry = class_index.get(name)
        if entry and entry.get("inherits"):
            return _ancestors_contain_node(entry["inherits"], visited)
        return False

    for name in class_index:
        if _ancestors_contain_node(name, set()):
            node_types.add(name)
    node_types.add("Node")
    return node_types


# ── API Pública ─────────────────────────────────────────────────────

def is_valid_node_type(type_name: str) -> bool:
    """Verifica se type_name é um tipo de nó válido (herda de Node)."""
    return type_name in _node_types()


def is_valid_class(class_name: str) -> bool:
    """Verifica se class_name existe na ClassDB (classes + builtin_classes)."""
    if class_name in _class_index():
        return True
    data = _load_cache()
    return any(c["name"] == class_name for c in data["builtin_classes"])


def is_valid_property(class_name: str, property_name: str) -> bool:
    """Verifica se property_name é uma propriedade válida de class_name.

    Considera propriedades da própria classe e herdadas.
    """
    return property_name in _get_all_properties(class_name)


def list_signals(class_name: str) -> list[dict]:
    """Lista sinais de uma classe (nome + argumentos).

    Retorna lista de {"name": str, "args": [{"name": str, "type": str}]}.
    Considera sinais herdados.
    """
    all_signals: dict[str, dict] = {}
    current = class_name
    class_index = _class_index()

    while current:
        entry = class_index.get(current)
        if not entry:
            break
        for sig in entry.get("signals", []):
            if sig["name"] not in all_signals:
                all_signals[sig["name"]] = {
                    "name": sig["name"],
                    "args": sig.get("arguments", []),
                }
        current = entry.get("inherits", "")

    return list(all_signals.values())


def get_class_hierarchy(class_name: str) -> list[str]:
    """Retorna a cadeia de herança de class_name (da classe até Node ou topo)."""
    hierarchy = [class_name]
    current = class_name
    class_index = _class_index()
    while current:
        entry = class_index.get(current)
        if not entry:
            break
        parent = entry.get("inherits", "")
        if parent:
            hierarchy.append(parent)
        current = parent
    return hierarchy


def suggest_similar(name: str, limit: int = 5) -> list[str]:
    """Sugere nomes de classes próximos (fuzzy, para mensagens de erro)."""
    return get_close_matches(name, _all_class_names(), n=limit, cutoff=0.4)


def suggest_similar_method(class_name: str, method_name: str, limit: int = 3) -> list[str]:
    """Sugere métodos com nome próximo em class_name (considera herança)."""
    all_names = [m["name"] for m in list_methods(class_name)]
    return get_close_matches(method_name, all_names, n=limit, cutoff=0.5)


def is_valid_method(class_name: str, method_name: str) -> bool:
    """Verifica se method_name existe em class_name ou em qualquer ancestral.

    Sobe a cadeia inherits até encontrar o método. Usa o mesmo padrão
    de list_methods(), list_signals() e _get_all_properties().
    """
    current = class_name
    class_index = _class_index()

    while current:
        entry = class_index.get(current)
        if not entry:
            break
        for method in entry.get("methods", []):
            if method["name"] == method_name:
                return True
        current = entry.get("inherits", "")

    return False


def is_valid_signal(class_name: str, signal_name: str) -> bool:
    """Verifica se signal_name existe em class_name ou em qualquer ancestral.

    Sobe a cadeia inherits até encontrar o sinal. Usa o mesmo padrão
    de list_signals(), list_methods() e _get_all_properties().
    """
    current = class_name
    class_index = _class_index()

    while current:
        entry = class_index.get(current)
        if not entry:
            break
        for sig in entry.get("signals", []):
            if sig["name"] == signal_name:
                return True
        current = entry.get("inherits", "")

    return False


def suggest_similar_node_type(name: str, limit: int = 5) -> list[str]:
    """Sugere tipos de nó próximos (apenas classes que herdam de Node)."""
    node_types = sorted(_node_types())
    return get_close_matches(name, node_types, n=limit, cutoff=0.4)


def _get_all_properties(class_name: str) -> dict[str, dict]:
    """Retorna dicionário nome → info de todas as propriedades (inclui herdadas)."""
    all_props: dict[str, dict] = {}
    current = class_name
    class_index = _class_index()

    while current:
        entry = class_index.get(current)
        if not entry:
            break
        for prop in entry.get("properties", []):
            if prop["name"] not in all_props:
                all_props[prop["name"]] = prop
        current = entry.get("inherits", "")

    return all_props


def get_property_info(class_name: str, property_name: str) -> dict | None:
    """Retorna info completa de uma propriedade (tipo, setter, getter)."""
    props = _get_all_properties(class_name)
    return props.get(property_name)


def list_methods(class_name: str) -> list[dict]:
    """Lista métodos de uma classe (nome + args + retorno)."""
    all_methods: dict[str, dict] = {}
    current = class_name
    class_index = _class_index()

    while current:
        entry = class_index.get(current)
        if not entry:
            break
        for method in entry.get("methods", []):
            if method["name"] not in all_methods:
                all_methods[method["name"]] = method
        current = entry.get("inherits", "")

    return list(all_methods.values())


def get_godot_bin() -> str:
    """Retorna o caminho do binário Godot (config + auto-detecção)."""
    try:
        from tools.config_loader import load_config
        cfg = load_config()
        path = cfg.get("godot_console_path") or cfg.get("godot_path", "")
        if path and Path(path).exists():
            return path
    except Exception:
        pass

    # Auto-detecção: procura em paths comuns (Windows + Linux + Mac)
    import platform
    system = platform.system()

    if system == "Windows":
        common = [
            Path("C:/Godot/Godot_v4.7-stable_win64.exe"),
            Path("C:/Godot/Godot_v4.7-stable_win64_console.exe"),
            Path.home() / "Godot" / "Godot_v4.7-stable_win64.exe",
        ]
    elif system == "Darwin":
        common = [
            Path("/Applications/Godot.app/Contents/MacOS/Godot"),
            Path.home() / "Godot" / "Godot_v4.7-stable_macos.universal",
        ]
    else:  # Linux
        common = [
            Path("/usr/bin/godot"),
            Path("/usr/local/bin/godot"),
            Path.home() / ".local/bin/godot",
        ]

    for p in common:
        if p.exists():
            return str(p)

    # PATH fallback
    import shutil
    for name in ["godot", "godot4", "Godot"]:
        result = shutil.which(name)
        if result:
            return result

    return "godot"


def get_config() -> dict:
    """Retorna a configuração completa. Cria com defaults se não existir."""
    try:
        from tools.config_loader import load_config
        cfg = load_config()
        if not cfg.get("_config_incomplete"):
            return cfg
    except Exception:
        pass
    # Cria config.json com defaults se nada funcionar
    default_cfg = {
        "godot_path": "godot",
        "default_project": "example_project",
        "projects_root": str(Path.home() / "GodotProjects"),
        "addon_port": 9080,
        "game_port": 9081,
        "timeouts": {"fast": 15, "compile": 30, "slow": 120},
    }
    config_path = ROOT / "config.json"
    config_path.write_text(json.dumps(default_cfg, indent=2), encoding='utf-8')
    return default_cfg


def query_classdb(
    class_name: str,
    section: str = "all",
    include_inherited: bool = False,
    offset: int = 0,
    limit: int = 50,
) -> dict:
    """Consulta informações completas de uma classe na ClassDB.

    Args:
        class_name: Nome da classe (ex: 'Node2D', 'CharacterBody2D').
        section: Seção a retornar: "all", "properties", "methods",
                 "signals", "enums", "constants".
        include_inherited: Se True, inclui membros herdados da classe pai.
        offset: Offset para paginação (começa em 0).
        limit: Máximo de itens por seção (default 50).

    Returns:
        dict com status, dados da classe, metadados de paginação.
    """
    class_index = _class_index()
    entry = class_index.get(class_name)
    if not entry:
        suggestions = suggest_similar(class_name)
        return {
            "status": "error",
            "message": f"Classe '{class_name}' não encontrada na ClassDB. "
                       f"Classes próximas: {suggestions}.",
            "suggestions": suggestions,
        }

    result = {
        "status": "success",
        "class": {
            "name": entry["name"],
            "inherits": entry.get("inherits", ""),
            "api_type": entry.get("api_type", ""),
            "hierarchy": get_class_hierarchy(class_name),
        },
    }

    cls = result["class"]

    # ── Seções com detalhes completos ──
    sections = {
        "properties": _format_properties(entry, include_inherited, class_index),
        "methods": _format_methods(entry, include_inherited, class_index),
        "signals": _format_signals(entry, include_inherited, class_index),
        "enums": _format_enums(entry, include_inherited, class_index),
        "constants": _format_constants(entry, include_inherited, class_index),
    }

    if section == "all":
        for key, items in sections.items():
            total = len(items)
            page = items[offset:offset + limit]
            cls[key] = page
            cls[f"{key}_count"] = total
            cls[f"{key}_offset"] = offset
            cls[f"{key}_limit"] = limit
            cls[f"{key}_has_more"] = (offset + limit) < total
    elif section in sections:
        items = sections[section]
        total = len(items)
        cls[section] = items[offset:offset + limit]
        cls["count"] = total
        cls["offset"] = offset
        cls["limit"] = limit
        cls["has_more"] = (offset + limit) < total

    return result


def search_classdb(query: str, limit: int = 20) -> dict:
    """Busca classes na ClassDB por nome parcial.

    Args:
        query: Texto parcial para buscar (ex: 'Body', 'Light').
        limit: Máximo de resultados (default 20).

    Returns:
        dict com status, resultados e contagem total.
    """
    class_index = _class_index()
    query_lower = query.lower()

    matches = [
        {
            "name": name,
            "inherits": entry.get("inherits", ""),
            "api_type": entry.get("api_type", ""),
        }
        for name, entry in class_index.items()
        if query_lower in name.lower()
    ]

    matches.sort(key=lambda m: (not m["name"].lower().startswith(query_lower), m["name"]))

    total = len(matches)
    page = matches[:limit]

    return {
        "status": "success",
        "query": query,
        "results": page,
        "total": total,
        "returned": len(page),
        "has_more": total > limit,
    }


# ── Formatadores de Seção ───────────────────────────────────────────

def _format_properties(entry: dict, inherited: bool, index: dict) -> list[dict]:
    """Formata propriedades com tipo, descrição e valor default."""
    result = []
    props = list(entry.get("properties", []))
    if inherited:
        props = _merge_inherited(entry, "properties", index)

    for p in props:
        result.append({
            "name": p.get("name", ""),
            "type": p.get("type", ""),
            "description": p.get("description", ""),
            "default": p.get("default_value"),
            "setter": p.get("setter", ""),
            "getter": p.get("getter", ""),
        })
    return result


def _format_methods(entry: dict, inherited: bool, index: dict) -> list[dict]:
    """Formata métodos com argumentos, retorno e descrição."""
    result = []
    methods = list(entry.get("methods", []))
    if inherited:
        methods = _merge_inherited(entry, "methods", index)

    for m in methods:
        args = []
        for a in m.get("arguments", []):
            args.append({
                "name": a.get("name", ""),
                "type": a.get("type", ""),
                "default": a.get("default_value"),
                "description": a.get("description", ""),
            })

        result.append({
            "name": m.get("name", ""),
            "return_type": m.get("return_type", ""),
            "description": m.get("description", ""),
            "arguments": args,
            "is_virtual": m.get("is_virtual", False),
            "is_static": m.get("is_static", False),
            "is_vararg": m.get("is_vararg", False),
            "qualifiers": m.get("qualifiers", ""),
        })
    return result


def _format_signals(entry: dict, inherited: bool, index: dict) -> list[dict]:
    """Formata sinais com argumentos e descrição."""
    result = []
    signals = list(entry.get("signals", []))
    if inherited:
        signals = _merge_inherited(entry, "signals", index)

    for s in signals:
        args = []
        for a in s.get("arguments", []):
            args.append({"name": a.get("name", ""), "type": a.get("type", "")})

        result.append({
            "name": s.get("name", ""),
            "description": s.get("description", ""),
            "arguments": args,
        })
    return result


def _format_enums(entry: dict, inherited: bool, index: dict) -> list[dict]:
    """Formata enums com valores."""
    result = []
    enums = list(entry.get("enums", []))
    if inherited:
        enums = _merge_inherited(entry, "enums", index)

    for e in enums:
        values = []
        for v in e.get("values", []):
            values.append({"name": v.get("name", ""), "value": v.get("value")})

        result.append({
            "name": e.get("name", ""),
            "description": e.get("description", ""),
            "values": values,
        })
    return result


def _format_constants(entry: dict, inherited: bool, index: dict) -> list[dict]:
    """Formata constantes com tipo e valor."""
    result = []
    consts = list(entry.get("constants", []))
    if inherited:
        consts = _merge_inherited(entry, "constants", index)

    for c in consts:
        result.append({
            "name": c.get("name", ""),
            "type": c.get("type", ""),
            "value": c.get("value"),
            "description": c.get("description", ""),
        })
    return result


def _merge_inherited(entry: dict, section: str, index: dict) -> list[dict]:
    """Combina membros próprios + herdados da classe pai."""
    own = list(entry.get(section, []))
    parent_name = entry.get("inherits", "")
    if parent_name and parent_name in index:
        parent = index[parent_name]
        parent_items = _merge_inherited(parent, section, index)
        # Remove duplicatas (filho sobrescreve pai)
        own_names = {item.get("name") for item in own}
        own.extend(item for item in parent_items if item.get("name") not in own_names)
    return own


def list_valid_node_types() -> dict:
    """Lista todos os tipos de nó válidos (classes que herdam de Node).

    Returns:
        {"status": "success", "node_types": [str], "count": int}
    """
    types = sorted(_node_types())
    return {"status": "success", "node_types": types, "count": len(types)}

