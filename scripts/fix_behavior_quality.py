"""fix_behavior_quality.py — Corrige qualidade dos behaviors.

Adiciona @tool e _get_configuration_warnings() onde faltam.
NAO modifica behaviors que ja estao corretos.
Gera relatorio do que foi corrigido.

Uso: python scripts/fix_behavior_quality.py [--dry-run] [--target <behavior>]
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BEHAVIORS_DIR = ROOT / "behaviors"

WARNINGS_TEMPLATE = '''
func _get_configuration_warnings() -> PackedStringArray:
\tvar warnings: PackedStringArray = []
\treturn warnings
'''


def fix_behavior(gd_path: Path, dry_run: bool = False) -> dict:
    """Corrige um arquivo .gd de behavior."""
    content = gd_path.read_text(encoding="utf-8")
    original = content
    fixes = []

    # 1. Adicionar @tool se faltar
    if "@tool" not in content:
        # Procura a primeira linha de codigo (apos comentarios)
        lines = content.split("\n")
        insert_at = 0
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped and not stripped.startswith("##"):
                insert_at = i
                break

        if insert_at > 0:
            lines.insert(insert_at, "@tool")
            content = "\n".join(lines)
            fixes.append("added @tool")
        else:
            # Fallback: adicionar apos a primeira linha de comentario
            for i, line in enumerate(lines):
                if line.startswith("##") and "@behavior:" in line:
                    lines.insert(i + 1, "@tool")
                    content = "\n".join(lines)
                    fixes.append("added @tool")
                    break

    # 2. Adicionar _get_configuration_warnings() se faltar
    if "_get_configuration_warnings" not in content:
        # Adicionar antes da ultima linha
        content = content.rstrip() + "\n" + WARNINGS_TEMPLATE
        fixes.append("added _get_configuration_warnings()")

    # 3. Verificar se class_name ja existe (nao duplicar)
    # Isso eh tratado pelo proprio Godot — se ja tem, nao adicionamos de novo

    if not dry_run and fixes:
        gd_path.write_text(content, encoding="utf-8")
    elif not fixes:
        pass  # Ja esta correto

    return {
        "file": str(gd_path.relative_to(ROOT)),
        "fixes": fixes,
        "status": "fixed" if fixes else "ok",
    }


def fix_all(dry_run: bool = False) -> dict:
    """Corrige todos os behaviors."""
    results = []
    total_fixed = 0
    total_ok = 0

    for entry in sorted(BEHAVIORS_DIR.iterdir()):
        if not entry.is_dir():
            continue

        gd_files = list(entry.glob("*.gd"))
        # Pega o .gd principal (nao test_*.gd)
        main_gd = [f for f in gd_files if not f.name.startswith("test_")]
        if not main_gd:
            continue

        result = fix_behavior(main_gd[0], dry_run)
        results.append(result)
        if result["fixes"]:
            total_fixed += 1
        else:
            total_ok += 1

    return {
        "total": len(results),
        "fixed": total_fixed,
        "ok": total_ok,
        "results": results,
        "dry_run": dry_run,
    }


if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv
    target = None

    for i, arg in enumerate(sys.argv):
        if arg == "--target" and i + 1 < len(sys.argv):
            target = sys.argv[i + 1]

    if target:
        gd_path = BEHAVIORS_DIR / target / f"{target}.gd"
        if gd_path.exists():
            result = fix_behavior(gd_path, dry_run)
            import json
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(f"Behavior nao encontrado: {target}")
    else:
        report = fix_all(dry_run)
        mode = "[DRY RUN] " if dry_run else ""
        print(f"{mode}Total: {report['total']} | Corrigidos: {report['fixed']} | OK: {report['ok']}")
        if report["fixed"] > 0:
            print(f"\nCorrigidos:")
            for r in report["results"]:
                if r["fixes"]:
                    print(f"  {r['file']}: {', '.join(r['fixes'])}")
