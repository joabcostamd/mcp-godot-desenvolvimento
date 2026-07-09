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


def _load_cache() -> dict:
    """Carrega o cache ClassDB (lazy, uma vez)."""
    global _cache
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
    """Retorna o caminho do binário Godot (config.json + auto-detecção)."""
    config_path = ROOT / "config.json"
    if config_path.exists():
        with open(config_path, encoding="utf-8") as f:
            cfg = json.load(f)
        path = cfg.get("godot_console_path") or cfg.get("godot_path", "")
        if path and Path(path).exists():
            return path

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
    """Retorna o config.json completo."""
    config_path = ROOT / "config.json"
    if config_path.exists():
        with open(config_path, encoding="utf-8") as f:
            return json.load(f)
    return {}


def query_classdb(class_name: str) -> dict:
    """Consulta informações completas de uma classe na ClassDB.

    Args:
        class_name: Nome da classe (ex: 'Node2D', 'CharacterBody2D').

    Returns:
        {"status": "success", "class": {...}}
        ou {"status": "error", "message": str}
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

    return {
        "status": "success",
        "class": {
            "name": entry["name"],
            "inherits": entry.get("inherits", ""),
            "api_type": entry.get("api_type", ""),
            "properties": [p["name"] for p in entry.get("properties", [])],
            "methods": [m["name"] for m in entry.get("methods", [])],
            "signals": [s["name"] for s in entry.get("signals", [])],
            "hierarchy": get_class_hierarchy(class_name),
        },
    }


def list_valid_node_types() -> dict:
    """Lista todos os tipos de nó válidos (classes que herdam de Node).

    Returns:
        {"status": "success", "node_types": [str], "count": int}
    """
    types = sorted(_node_types())
    return {"status": "success", "node_types": types, "count": len(types)}

