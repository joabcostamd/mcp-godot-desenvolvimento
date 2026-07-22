#!/usr/bin/env python3
"""generate_doc_headers.py — Gera doc headers ## padronizados para behaviors sem.

Lê behavior.json de cada behavior, extrai metadados, e gera um bloco ##
no topo do arquivo .gd correspondente. Só age em behaviors que AINDA NÃO
têm doc header (não começa com ##).

Uso:
    python scripts/generate_doc_headers.py          # todos os behaviors
    python scripts/generate_doc_headers.py --dry-run  # só preview
    python scripts/generate_doc_headers.py --behavior nome  # um só
"""

import argparse
import json
import os
import sys
from pathlib import Path

BEHAVIORS_DIR = Path(__file__).parent.parent / "behaviors"


def extract_extends(gd_path: Path) -> str:
    """Extrai o extends do .gd."""
    if not gd_path.exists():
        return "Node"
    with open(gd_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip().startswith("extends "):
                return line.strip().split("extends ")[1].strip()
    return "Node"


def has_doc_header(gd_path: Path) -> bool:
    """Verifica se o .gd ja tem doc header (comeca com ##)."""
    if not gd_path.exists():
        return False
    with open(gd_path, "r", encoding="utf-8") as f:
        first_line = f.readline()
    return first_line.strip().startswith("##")


def generate_header(behavior_name: str) -> str | None:
    """Gera o bloco ## para um behavior. Retorna None se ja tem header."""
    gd_path = BEHAVIORS_DIR / behavior_name / f"{behavior_name}.gd"
    json_path = BEHAVIORS_DIR / behavior_name / "behavior.json"

    if has_doc_header(gd_path):
        return None  # ja tem

    if not json_path.exists():
        print(f"  [AVISO] {behavior_name}: behavior.json nao encontrado")
        return None

    with open(json_path, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"  [ERRO] {behavior_name}: JSON invalido: {e}")
            return None

    desc_pt = data.get("description_pt", "").split(".")[0].strip()
    if not desc_pt:
        desc_pt = data.get("description_en", "").split(".")[0].strip()
    if not desc_pt:
        desc_pt = behavior_name.replace("_", " ").title()

    extends_node = extract_extends(gd_path)

    signals = data.get("signals", [])
    signal_names = [s["name"] for s in signals] if signals else []

    deps = data.get("dependencies", [])
    genres = data.get("genres", [])

    # Construir header
    lines = []
    lines.append(f"## {desc_pt}.")

    # Segunda linha: categoria inferida das tags ou genres
    tags = data.get("tags", [])
    if genres:
        lines.append(f"## Generos: {', '.join(genres[:5])}.")
    if tags:
        lines.append(f"## Tags: {', '.join(tags[:5])}.")

    # Linha tecnica
    lines.append(f"## Extends: {extends_node}.")

    if signal_names:
        sig_str = ", ".join(f"{n}()" for n in signal_names[:8])
        lines.append(f"## Sinais: {sig_str}.")

    if deps:
        dep_str = ", ".join(deps[:5])
        lines.append(f"## Dependencias: {dep_str}.")
    else:
        lines.append(f"## Dependencias: nenhuma.")

    lines.append(f"## @behavior: {behavior_name}")
    lines.append("")

    return "\n".join(lines)


def apply_header(behavior_name: str, header: str) -> bool:
    """Aplica o header ao .gd. Retorna True se sucesso."""
    gd_path = BEHAVIORS_DIR / behavior_name / f"{behavior_name}.gd"
    if not gd_path.exists():
        return False

    with open(gd_path, "r", encoding="utf-8") as f:
        original = f.read()

    # Remove @tool se estiver na primeira linha e inserir antes
    new_content = header + original

    with open(gd_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(new_content)
    return True


def main():
    parser = argparse.ArgumentParser(description="Gera doc headers ## para behaviors")
    parser.add_argument("--dry-run", action="store_true", help="Apenas preview, sem escrever")
    parser.add_argument("--behavior", type=str, help="Processar apenas um behavior especifico")
    args = parser.parse_args()

    if args.behavior:
        names = [args.behavior]
    else:
        names = sorted(
            d.name for d in BEHAVIORS_DIR.iterdir()
            if d.is_dir() and (d / "behavior.json").exists()
        )

    generated = 0
    skipped = 0
    errors = 0

    for name in names:
        header = generate_header(name)
        if header is None:
            skipped += 1
            continue

        if args.dry_run:
            print(f"\n--- {name} ---")
            print(header)
            generated += 1
        else:
            if apply_header(name, header):
                print(f"  OK: {name}")
                generated += 1
            else:
                print(f"  FAIL: {name}")
                errors += 1

    print(f"\n{'[DRY RUN] ' if args.dry_run else ''}Gerados: {generated} | Ja tinham: {skipped} | Erros: {errors}")


if __name__ == "__main__":
    main()
