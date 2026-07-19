"""gamestate_ops.py — Save Schema + Migracao (Fatia 4.7 / Etapa B7).

Gera schema de save a partir da estrutura de dados do jogo e
realiza migracao de saves antigos para novas versoes.
"""

import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _find_project_root(project_path: str | None = None) -> Path | None:
    if project_path:
        p = Path(project_path)
        if (p / "project.godot").exists():
            return p
        return None
    try:
        from tools.project_ops import _get_active_project
        return _get_active_project()
    except Exception:
        pass
    if (ROOT / "project.godot").exists():
        return ROOT
    return None


def _read_gd_safe(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        return ""


# ══════════════════════════════════════════════════════════════════════
# Op 1: generate_save_schema
# ══════════════════════════════════════════════════════════════════════

def generate_save_schema(project_path: str | None = None) -> dict:
    """Gera schema de save a partir das definicoes de dados do jogo.

    Analisa scripts .gd em busca de:
      - Variaveis exportadas (@export var) — dados que persistem
      - Dicionarios de save (var save_data = {...})
      - Funcoes save_game/load_game
      - Resource files (.tres) com definicoes de dados

    Args:
        project_path: Caminho do projeto Godot.

    Returns:
        dict com schema estruturado e versao.
    """
    proj = _find_project_root(project_path)
    if proj is None:
        return {"status": "error", "error": "Nenhum projeto Godot encontrado."}

    schema = {
        "version": "1.0.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "project": str(proj),
        "fields": [],
        "save_functions": [],
        "resources": [],
    }

    # Padroes de extracao
    export_var = re.compile(r'@export\s+(?:var\s+)?(\w+)\s*(?::\s*(\w+(?:/\w+)*))?\s*(?:=\s*(.+))?')
    save_func = re.compile(r'func\s+(save_\w+|load_\w+|serialize\w*|deserialize\w*)\s*\(')
    resource_ext = re.compile(r'\[ext_resource[^\]]*path="([^"]+)"[^\]]*type="([^"]+)"')

    gd_files = []
    for f in proj.rglob("*.gd"):
        parts = f.parts
        if "addons" in parts or ".godot" in parts:
            continue
        gd_files.append(f)

    for fpath in gd_files:
        content = _read_gd_safe(fpath)
        rel = str(fpath.relative_to(proj))

        # Export vars
        for m in export_var.finditer(content):
            name = m.group(1)
            vtype = m.group(2) or "Variant"
            default = m.group(3)
            if default:
                default = default.strip().rstrip(",")
            schema["fields"].append({
                "name": name,
                "type": vtype,
                "default": default,
                "source": rel,
                "line": content[:m.start()].count("\n") + 1,
            })

        # Save/load functions
        for m in save_func.finditer(content):
            schema["save_functions"].append({
                "function": m.group(1),
                "source": rel,
            })

    # Resource files (.tres)
    for fpath in proj.rglob("*.tres"):
        content = _read_gd_safe(fpath)
        for m in resource_ext.finditer(content):
            schema["resources"].append({
                "path": m.group(1),
                "type": m.group(2),
            })

    # Remove duplicatas de export vars
    seen = set()
    unique_fields = []
    for f in schema["fields"]:
        key = f["name"]
        if key not in seen:
            seen.add(key)
            unique_fields.append(f)
    schema["fields"] = unique_fields

    schema["total_fields"] = len(schema["fields"])
    schema["total_resources"] = len(schema["resources"])

    return {
        "status": "completed",
        "schema": schema,
    }


# ══════════════════════════════════════════════════════════════════════
# Op 2: migrate_save
# ══════════════════════════════════════════════════════════════════════

def migrate_save(
    save_data: dict,
    from_version: str = "1.0.0",
    to_version: str = "2.0.0",
    migrations: list[dict] | None = None,
) -> dict:
    """Migra dados de save de uma versao antiga para uma nova.

    Aplica transformacoes descritas em 'migrations' sequencialmente.
    Cada migracao e um dict com:
      - version: versao alvo
      - description: descricao da mudanca
      - rename: {old_key: new_key} — renomeia campos
      - add: {key: default_value} — adiciona campos com default
      - remove: [keys] — remove campos
      - transform: {key: "expression"} — transforma valores (ex: "int(x) * 100")

    Args:
        save_data: Dados do save original (dict).
        from_version: Versao de origem.
        to_version: Versao de destino.
        migrations: Lista de migracoes a aplicar (default: migracoes built-in).

    Returns:
        dict com dados migrados e log de alteracoes.
    """
    if migrations is None:
        migrations = _default_migrations()

    # Filtra migracoes entre from_version e to_version
    applicable = [
        m for m in migrations
        if _version_gte(m["version"], from_version) and _version_lte(m["version"], to_version)
    ]
    applicable.sort(key=lambda m: _version_tuple(m["version"]))

    migrated = dict(save_data)  # shallow copy
    log = []
    current_version = from_version

    for mig in applicable:
        # Renomeia
        for old_key, new_key in mig.get("rename", {}).items():
            if old_key in migrated:
                migrated[new_key] = migrated.pop(old_key)
                log.append(f"Renomeado: {old_key} -> {new_key}")

        # Adiciona
        for key, default in mig.get("add", {}).items():
            if key not in migrated:
                migrated[key] = default
                log.append(f"Adicionado: {key} = {default}")

        # Remove
        for key in mig.get("remove", []):
            if key in migrated:
                del migrated[key]
                log.append(f"Removido: {key}")

        # Transforma
        for key, expression in mig.get("transform", {}).items():
            if key in migrated:
                try:
                    old_val = migrated[key]
                    # Expressoes seguras: int(x), float(x), str(x), x * N, x + N
                    new_val = _safe_eval(expression, old_val)
                    migrated[key] = new_val
                    log.append(f"Transformado: {key}: {old_val} -> {new_val} ({expression})")
                except Exception as e:
                    log.append(f"Erro ao transformar {key}: {e}")

        current_version = mig["version"]

    return {
        "status": "completed",
        "from_version": from_version,
        "to_version": current_version,
        "changes_applied": len(log),
        "log": log,
        "data": migrated,
    }


def _version_tuple(v: str) -> tuple:
    try:
        return tuple(int(x) for x in v.split("."))
    except Exception:
        return (0,)


def _version_gte(a: str, b: str) -> bool:
    return _version_tuple(a) >= _version_tuple(b)


def _version_lte(a: str, b: str) -> bool:
    return _version_tuple(a) <= _version_tuple(b)


def _safe_eval(expression: str, value) -> any:
    """Avalia expressao simples de transformacao de forma segura."""
    x = value
    allowed = {"int": int, "float": float, "str": str, "bool": bool, "x": x, "abs": abs, "round": round}
    try:
        return eval(expression, {"__builtins__": {}}, allowed)
    except Exception:
        return value


def _default_migrations() -> list[dict]:
    """Migracoes padrao de exemplo."""
    return [
        {
            "version": "1.1.0",
            "description": "Adiciona timestamp e version aos saves",
            "add": {"_timestamp": 0, "_version": "1.1.0"},
        },
        {
            "version": "2.0.0",
            "description": "Renomeia score para points, adiciona level",
            "rename": {"score": "points"},
            "add": {"level": 1, "xp": 0},
            "remove": ["_deprecated_field"],
        },
    ]
