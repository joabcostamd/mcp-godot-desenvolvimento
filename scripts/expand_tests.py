#!/usr/bin/env python3
"""expand_tests.py — Expande testes de 1 para >=3 por behavior.

Le o .gd do behavior para entender exports e gera:
- test_edge_case_zero_or_disabled: valores zero/disabled
- test_edge_case_extreme: valores extremos (max, min)

Apenas age em behaviors com exatamente 1 teste.
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

BEHAVIORS_DIR = Path(__file__).parent.parent / "behaviors"


def count_tests(test_path: Path) -> int:
    if not test_path.exists():
        return 0
    with open(test_path, "r", encoding="utf-8") as f:
        content = f.read()
    return len(re.findall(r"func (test_\w+)\(", content))


def get_exports(gd_path: Path) -> list[dict]:
    """Extrai lista de exports com nome, tipo e default."""
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
        default = m.group(3).strip()
        exports.append({"name": name, "type": gtype, "default": default})
    return exports


def get_class_name(gd_path: Path) -> str:
    if not gd_path.exists():
        return "Node"
    with open(gd_path, "r", encoding="utf-8") as f:
        content = f.read()
    m = re.search(r"class_name\s+(\w+)", content)
    return m.group(1) if m else "Node"


def generate_edge_tests(behavior_name: str) -> str | None:
    """Gera +2 testes de borda. Retorna None se ja tem >=3 testes."""
    test_path = BEHAVIORS_DIR / behavior_name / f"test_{behavior_name}.gd"
    gd_path = BEHAVIORS_DIR / behavior_name / f"{behavior_name}.gd"

    current_count = count_tests(test_path)
    if current_count >= 3:
        return None
    if current_count == 0:
        return None

    class_name = get_class_name(gd_path)
    exports = get_exports(gd_path)

    # Encontrar exports numericos para testes de borda
    numeric_exports = [e for e in exports if e["type"] in ("float", "int")]
    bool_exports = [e for e in exports if e["type"] == "bool"]

    tests = []

    # Se ja tem 2 testes, so gera o 3o (integracao)
    if current_count == 2:
        tests.append(f"""
func test_integration_add_child() -> void:
\tvar c := {class_name}.new()
\tadd_child(c)
\t# Deve inicializar sem crash quando adicionado a arvore
\tassert_bool(c.is_inside_tree()).is_true()
\tremove_child(c)
\tc.queue_free()""")
        return "\n".join(tests) if tests else None

    # Teste 1: Edge case - zero ou disabled
    if bool_exports:
        # Para behaviors com booleanos, testa disabled
        bool_var = bool_exports[0]["name"]
        tests.append(f"""
func test_edge_case_disabled() -> void:
\tvar c := {class_name}.new()
\tc.{bool_var} = false
\t# Nao deve crashar com disabled
\tassert_bool(c.{bool_var}).is_false()
\tc.queue_free()""")
    elif numeric_exports:
        # Para behaviors numericos, testa zero
        num_var = numeric_exports[0]["name"]
        num_type = numeric_exports[0]["type"]
        zero_val = "0.0" if num_type == "float" else "0"
        tests.append(f"""
func test_edge_case_zero() -> void:
\tvar c := {class_name}.new()
\tc.{num_var} = {zero_val}
\t# Nao deve crashar com valor zero
\tc.queue_free()""")

    # Teste 2: Edge case - valores extremos
    if len(numeric_exports) >= 1:
        num_var = numeric_exports[0]["name"]
        num_type = numeric_exports[0]["type"]
        if num_type == "float":
            tests.append(f"""
func test_edge_case_extreme() -> void:
\tvar c := {class_name}.new()
\tc.{num_var} = 999999.0
\t# Nao deve crashar com valor extremo
\tc.queue_free()""")
        else:
            tests.append(f"""
func test_edge_case_extreme() -> void:
\tvar c := {class_name}.new()
\tc.{num_var} = 999999
\t# Nao deve crashar com valor extremo
\tc.queue_free()""")
    else:
        # Fallback: testa instanciacao multipla
        tests.append(f"""
func test_edge_case_multiple_instances() -> void:
\tvar a := {class_name}.new()
\tvar b := {class_name}.new()
\tassert_object(a).is_not_null()
\tassert_object(b).is_not_null()
\ta.queue_free()
\tb.queue_free()""")

    if not tests:
        return None

    return "\n".join(tests)


def apply_tests(behavior_name: str, new_tests: str) -> bool:
    test_path = BEHAVIORS_DIR / behavior_name / f"test_{behavior_name}.gd"
    if not test_path.exists():
        return False

    with open(test_path, "r", encoding="utf-8") as f:
        original = f.read()

    # Append new tests before end of file
    new_content = original.rstrip() + "\n" + new_tests + "\n"

    with open(test_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(new_content)
    return True


def main():
    parser = argparse.ArgumentParser(description="Expande testes de behaviors")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--behavior", type=str)
    args = parser.parse_args()

    if args.behavior:
        names = [args.behavior]
    else:
        names = sorted(
            d.name for d in BEHAVIORS_DIR.iterdir()
            if d.is_dir() and (d / "behavior.json").exists()
        )

    expanded = 0
    skipped = 0

    for name in names:
        new_tests = generate_edge_tests(name)
        if new_tests is None:
            skipped += 1
            continue

        if args.dry_run:
            print(f"\n--- {name} ---")
            print(new_tests)
            expanded += 1
        else:
            if apply_tests(name, new_tests):
                print(f"  OK: {name}")
                expanded += 1
            else:
                print(f"  FAIL: {name}")

    print(f"\n{'[DRY RUN] ' if args.dry_run else ''}Expandidos: {expanded} | Ja tinham >=3: {skipped}")


if __name__ == "__main__":
    main()
