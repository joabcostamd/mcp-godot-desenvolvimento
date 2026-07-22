"""project_health.py — Dashboard de Saude do Projeto.

Gera um relatorio completo de saude do MCP Godot Agent:
- Behaviors: qualidade, cobertura, .tres, CHANGELOG
- Codigo: linhas, arquivos, tools
- Documentacao: docs/, READMEs
- ONDA progress: fatias concluidas vs pendentes

Uso: python scripts/project_health.py [--json] [--onda N]
"""

import json
import os
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def scan_behaviors() -> dict:
    """Escaneia todos os behaviors e avalia qualidade."""
    bh_dir = ROOT / "behaviors"
    total = 0
    with_json = 0
    with_gd = 0
    with_tres = 0
    with_tscn = 0
    with_changelog = 0
    with_readme = 0
    with_test = 0
    with_tool = 0
    with_warnings = 0
    with_signals = 0
    lines_total = 0
    categories = defaultdict(int)

    for entry in sorted(bh_dir.iterdir()):
        if not entry.is_dir():
            continue
        total += 1

        if (entry / "behavior.json").exists():
            with_json += 1
            try:
                data = json.loads((entry / "behavior.json").read_text(encoding="utf-8"))
                for tag in data.get("tags", []):
                    categories[tag] += 1
            except (json.JSONDecodeError, OSError):
                pass

        if list(entry.glob("*.gd")):
            with_gd += 1
            gd_file = next(entry.glob("*.gd"))
            content = gd_file.read_text(encoding="utf-8", errors="ignore")
            lines_total += len(content.splitlines())
            # Verificar @tool como palavra inteira (nao dentro de comentarios)
            if re.search(r'\b@tool\b', content):
                with_tool += 1
            if "_get_configuration_warnings" in content:
                with_warnings += 1
            if "signal " in content:
                with_signals += 1

        if list(entry.glob("*.tres")):
            with_tres += 1
        if list(entry.glob("*.tscn")):
            with_tscn += 1
        if (entry / "CHANGELOG.md").exists():
            with_changelog += 1
        if (entry / "README.md").exists():
            with_readme += 1
        if list(entry.glob("test_*.gd")):
            with_test += 1

    return {
        "total": total,
        "behavior_json": with_json,
        "gd_script": with_gd,
        "tres_resource": with_tres,
        "tscn_scene": with_tscn,
        "changelog": with_changelog,
        "readme": with_readme,
        "test": with_test,
        "tool_annotation": with_tool,
        "configuration_warnings": with_warnings,
        "signals": with_signals,
        "total_lines": lines_total,
        "avg_lines_per_behavior": round(lines_total / total, 1) if total else 0,
        "categories": dict(sorted(categories.items(), key=lambda x: x[1], reverse=True)[:15]),
    }


def scan_codebase() -> dict:
    """Metricas do codigo Python."""
    tools_dir = ROOT / "tools"
    py_files = list(tools_dir.glob("*.py"))
    total_lines = 0

    for f in py_files:
        try:
            total_lines += len(f.read_text(encoding="utf-8", errors="ignore").splitlines())
        except OSError:
            pass

    server_lines = 0
    server_path = ROOT / "server.py"
    if server_path.exists():
        server_lines = len(server_path.read_text(encoding="utf-8", errors="ignore").splitlines())

    return {
        "tools_modules": len(py_files),
        "tools_lines": total_lines,
        "server_lines": server_lines,
        "total_python_lines": total_lines + server_lines,
    }


def scan_documentation() -> dict:
    """Estado da documentacao."""
    docs = ROOT / "docs"
    doc_files = list(docs.glob("*.md")) if docs.exists() else []

    readmes = list(ROOT.glob("**/README.md"))
    # Excluir behaviors/ (ja contados) e addons/
    readmes = [r for r in readmes if "behaviors/" not in str(r) and "addons/" not in str(r)]

    return {
        "docs_folder": len(doc_files),
        "doc_files": [d.name for d in doc_files],
        "root_readmes": len(readmes),
        "root_readme_files": [str(r.relative_to(ROOT)) for r in readmes],
    }


def scan_onda_progress() -> dict:
    """Progresso das ondas pelo .roadmap_progress.json."""
    progress_file = ROOT / ".roadmap_progress.json"
    if not progress_file.exists():
        return {"error": ".roadmap_progress.json nao encontrado"}

    try:
        data = json.loads(progress_file.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {"error": "Erro ao ler .roadmap_progress.json"}

    ondas = {}
    for key, value in data.items():
        if key.startswith("fatia_"):
            onda = key.split("_")[1].split(".")[0]
            if onda.isdigit():
                onda_num = int(onda)
            else:
                continue

            if onda_num not in ondas:
                ondas[onda_num] = {"total": 0, "concluida": 0, "pendente": 0, "escalada": 0}

            ondas[onda_num]["total"] += 1
            status = value.get("status", "pendente")
            if status == "concluida":
                ondas[onda_num]["concluida"] += 1
            elif status == "escalada":
                ondas[onda_num]["escalada"] += 1
            else:
                ondas[onda_num]["pendente"] += 1

    return ondas


def generate_report(json_output: bool = False) -> str | dict:
    """Gera relatorio completo."""
    behaviors = scan_behaviors()
    codebase = scan_codebase()
    docs = scan_documentation()
    ondas = scan_onda_progress()

    report = {
        "project": "MCP Godot Agent",
        "version": "3.2.1",
        "behaviors": behaviors,
        "codebase": codebase,
        "documentation": docs,
        "ondas": ondas,
    }

    if json_output:
        return report

    # Formato texto rico
    lines = []
    lines.append("=" * 60)
    lines.append("  🏥 DASHBOARD DE SAUDE — MCP Godot Agent v3.2.1")
    lines.append("=" * 60)

    # Behaviors
    lines.append(f"\n📦 BEHAVIORS ({behaviors['total']} total)")
    lines.append(f"  behavior.json:  {behaviors['behavior_json']}/{behaviors['total']}")
    lines.append(f"  .gd script:     {behaviors['gd_script']}/{behaviors['total']}")
    lines.append(f"  .tres resource: {behaviors['tres_resource']}/{behaviors['total']}")
    lines.append(f"  .tscn scene:    {behaviors['tscn_scene']}/{behaviors['total']}")
    lines.append(f"  CHANGELOG.md:   {behaviors['changelog']}/{behaviors['total']}")
    lines.append(f"  README.md:      {behaviors['readme']}/{behaviors['total']}")
    lines.append(f"  test_*.gd:      {behaviors['test']}/{behaviors['total']}")
    lines.append(f"  @tool:          {behaviors['tool_annotation']}/{behaviors['total']}")
    lines.append(f"  warnings():     {behaviors['configuration_warnings']}/{behaviors['total']}")
    lines.append(f"  signals:        {behaviors['signals']} behaviors com sinais")
    lines.append(f"  Linhas GDScript: {behaviors['total_lines']:,} (media {behaviors['avg_lines_per_behavior']}/behavior)")

    quality = sum([
        behaviors['behavior_json'] == behaviors['total'],
        behaviors['gd_script'] == behaviors['total'],
        behaviors['changelog'] == behaviors['total'],
        behaviors['readme'] == behaviors['total'],
        behaviors['test'] == behaviors['total'],
        behaviors['tool_annotation'] == behaviors['total'],
        behaviors['configuration_warnings'] == behaviors['total'],
    ])
    lines.append(f"  Score qualidade: {quality}/7 ✅" if quality == 7 else f"  Score qualidade: {quality}/7")

    # Categorias
    lines.append(f"\n  Top categorias:")
    for cat, count in list(behaviors['categories'].items())[:10]:
        lines.append(f"    {cat}: {count}")

    # Codebase
    lines.append(f"\n🐍 CODEBASE")
    lines.append(f"  Modulos tools/:   {codebase['tools_modules']}")
    lines.append(f"  Linhas tools/:    {codebase['tools_lines']:,}")
    lines.append(f"  Linhas server.py: {codebase['server_lines']:,}")
    lines.append(f"  Total Python:     {codebase['total_python_lines']:,}")

    # Documentacao
    lines.append(f"\n📖 DOCUMENTACAO")
    lines.append(f"  docs/: {docs['docs_folder']} arquivos")
    for f in docs['doc_files']:
        lines.append(f"    - {f}")
    lines.append(f"  READMEs raiz: {docs['root_readmes']}")

    # Ondas
    lines.append(f"\n🌊 PROGRESSO DAS ONDAS")
    for onda_num in sorted(ondas.keys()):
        o = ondas[onda_num]
        pct = round(o['concluida'] / o['total'] * 100) if o['total'] else 0
        bar = "█" * (pct // 5) + "░" * (20 - pct // 5)
        lines.append(f"  ONDA {onda_num}: {bar} {o['concluida']}/{o['total']} ({pct}%)")
        if o['escalada']:
            lines.append(f"    ⚠️ {o['escalada']} escalada(s)")

    lines.append(f"\n{'=' * 60}")
    return "\n".join(lines)


if __name__ == "__main__":
    json_mode = "--json" in sys.argv
    result = generate_report(json_output=json_mode)
    if json_mode:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        # Forcar ASCII-safe output para evitar UnicodeEncodeError no Windows
        print(result.encode("ascii", errors="replace").decode("ascii"))
