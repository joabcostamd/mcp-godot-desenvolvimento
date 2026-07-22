#!/usr/bin/env python3
"""generate_tres.py — Gera .tres Resource por behavior (FATIA 2.D).

Le cada .gd de behavior, extrai @export vars com defaults,
e gera um arquivo .tres que expoe esses parametros como Resource.
Isso permite ajuste de parametros sem editar codigo — pre-requisito
do ajuste ao vivo (2.AI).
"""

import os
import re
import sys
from pathlib import Path

BEHAVIORS_DIR = Path(__file__).parent.parent / "behaviors"


def extract_exports(gd_path: Path) -> list[dict]:
    """Extrai @export vars com tipo e default do .gd."""
    if not gd_path.exists():
        return []
    with open(gd_path, "r", encoding="utf-8") as f:
        content = f.read()

    exports = []
    for m in re.finditer(
        r'@export\s+var\s+(\w+)\s*:\s*(\w+)\s*=\s*([^\n:]+)',
        content
    ):
        name = m.group(1)
        gtype = m.group(2)
        default = m.group(3).strip().rstrip(":")
        # Skip complex defaults (arrays, dictionaries, function calls)
        if any(c in default for c in ["[", "{", "("]):
            default = ""
        exports.append({"name": name, "type": gtype, "default": default})
    return exports


def get_class_name(gd_path: Path) -> str:
    if not gd_path.exists():
        return "Node"
    with open(gd_path, "r", encoding="utf-8") as f:
        content = f.read()
    m = re.search(r"class_name\s+(\w+)", content)
    return m.group(1) if m else "Node"


def gdtype_to_tres(gd_type: str, default: str) -> str:
    """Converte tipo GDScript para formato .tres."""
    type_map = {
        "int": ("int", lambda v: v),
        "float": ("float", lambda v: v),
        "bool": ("bool", lambda v: "true" if v.lower() in ("true", "1") else "false"),
        "String": ("string", lambda v: '"' + v.strip("'\"") + '"'),
        "Color": ("color", lambda v: v.replace("Color(", "").replace(")", "").replace(" ", "")),
        "Vector2": ("vector2", lambda v: v.replace("Vector2(", "").replace(")", "").replace(" ", "")),
        "Vector2i": ("vector2i", lambda v: v.replace("Vector2i(", "").replace(")", "").replace(" ", "")),
        "NodePath": ("node_path", lambda v: v.replace("NodePath(", "").replace(")", "").replace('"', "")),
    }
    if gd_type in type_map:
        return type_map[gd_type]
    return ("resource", lambda v: "null")


def generate_tres(behavior_name: str) -> str | None:
    """Gera o conteudo do .tres para um behavior."""
    gd_path = BEHAVIORS_DIR / behavior_name / f"{behavior_name}.gd"
    exports = extract_exports(gd_path)
    if not exports:
        return None

    class_name = get_class_name(gd_path)
    script_path = f"res://behaviors/{behavior_name}/{behavior_name}.gd"

    lines = ['[gd_resource type="Resource" load_steps=2 format=3]', ""]
    lines.append(f'[ext_resource type="Script" path="{script_path}" id="1_{behavior_name}"]')
    lines.append("")
    lines.append('[resource]')
    lines.append(f'script = ExtResource("1_{behavior_name}")')

    for exp in exports:
        name = exp["name"]
        gtype = exp["type"]
        default = exp["default"]

        if not default:
            continue

        tres_type, converter = gdtype_to_tres(gtype, default)
        try:
            value = converter(default)
            if tres_type == "string":
                lines.append(f'{name} = {value}')
            elif tres_type == "int":
                lines.append(f"{name} = {value}")
            elif tres_type == "float":
                lines.append(f"{name} = {value}")
            elif tres_type == "bool":
                lines.append(f"{name} = {value}")
            elif tres_type in ("color", "vector2", "vector2i"):
                lines.append(f"{name} = {tres_type.capitalize()}({value})")
            elif tres_type == "node_path":
                lines.append(f'{name} = NodePath("{value}")')
        except (ValueError, IndexError):
            pass

    return "\n".join(lines) + "\n"


def main():
    dry_run = "--dry-run" in sys.argv
    behavior_filter = None
    for arg in sys.argv[1:]:
        if arg.startswith("--behavior="):
            behavior_filter = arg.split("=")[1]

    if behavior_filter:
        names = [behavior_filter]
    else:
        names = sorted(
            d.name for d in BEHAVIORS_DIR.iterdir()
            if d.is_dir() and (d / "behavior.json").exists()
        )

    generated = 0
    skipped = 0

    for name in names:
        content = generate_tres(name)
        if content is None:
            skipped += 1
            continue

        tres_path = BEHAVIORS_DIR / name / f"{name}.tres"

        if dry_run:
            print(f"\n--- {name} ---")
            print(content[:300])
        else:
            tres_path.write_text(content, encoding="utf-8")
            print(f"  OK: {name}")
        generated += 1

    print(f"\n{'[DRY RUN] ' if dry_run else ''}Gerados: {generated} | Sem exports: {skipped}")


if __name__ == "__main__":
    main()
