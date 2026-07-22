"""behavior_deps.py — Gera grafo de dependencias entre behaviors.

Analisa todos os behavior.json e constroi um mapa de dependencias.
Util para:
- Entender quais behaviors sao mais "fundamentais" (muito referenciados)
- Detectar dependencias circulares
- Planejar ordem de implementacao

Uso: python scripts/behavior_deps.py [--format mermaid|json|text]
"""

import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def build_dependency_graph() -> dict:
    """Constroi grafo de dependencias."""
    bh_dir = ROOT / "behaviors"
    graph = defaultdict(list)       # behavior -> [dependencias]
    reverse = defaultdict(list)     # behavior -> [quem depende dele]
    all_behaviors = set()

    for entry in sorted(bh_dir.iterdir()):
        if not entry.is_dir():
            continue
        json_path = entry / "behavior.json"
        if not json_path.exists():
            continue

        try:
            data = json.loads(json_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue

        name = data.get("name", entry.name)
        all_behaviors.add(name)

        deps = data.get("dependencies", [])
        for dep in deps:
            graph[name].append(dep)
            reverse[dep].append(name)

    # Behaviors sem dependencias
    independent = [b for b in all_behaviors if not graph[b]]

    # Mais referenciados (fundamentais)
    most_referenced = sorted(reverse.items(), key=lambda x: len(x[1]), reverse=True)

    # Mais dependentes (complexos)
    most_dependent = sorted(graph.items(), key=lambda x: len(x[1]), reverse=True)

    return {
        "total_behaviors": len(all_behaviors),
        "independent": independent[:20],
        "independent_count": len(independent),
        "most_referenced": [(name, len(refs)) for name, refs in most_referenced[:15]],
        "most_dependent": [(name, len(deps)) for name, deps in most_dependent[:15]],
        "graph": dict(graph),
        "reverse": dict(reverse),
    }


def format_mermaid(graph_data: dict) -> str:
    """Formata como diagrama Mermaid."""
    lines = ["```mermaid", "graph TD"]
    graph = graph_data["graph"]
    for behavior, deps in sorted(graph.items()):
        for dep in deps:
            lines.append(f"    {behavior}[{behavior}] --> {dep}[{dep}]")
    lines.append("```")
    return "\n".join(lines)


def format_text(graph_data: dict) -> str:
    """Formato texto legivel."""
    lines = []
    lines.append("=" * 60)
    lines.append("  🔗 GRAFO DE DEPENDENCIAS — Behaviors")
    lines.append("=" * 60)

    lines.append(f"\n📊 Total: {graph_data['total_behaviors']} behaviors")
    lines.append(f"🆓 Independentes: {graph_data['independent_count']}")

    lines.append(f"\n⭐ MAIS REFERENCIADOS (fundamentais):")
    for name, count in graph_data['most_referenced']:
        bar = "█" * min(count, 20)
        lines.append(f"  {name:<25} {bar} ({count})")

    lines.append(f"\n🔗 MAIS DEPENDENTES (complexos):")
    for name, count in graph_data['most_dependent']:
        bar = "█" * min(count, 20)
        lines.append(f"  {name:<25} {bar} ({count})")

    lines.append(f"\n🆓 INDEPENDENTES (exemplos):")
    for name in graph_data['independent'][:10]:
        lines.append(f"  - {name}")

    return "\n".join(lines)


if __name__ == "__main__":
    graph = build_dependency_graph()
    fmt = sys.argv[1] if len(sys.argv) > 1 else "text"

    if fmt == "mermaid":
        print(format_mermaid(graph))
    elif fmt == "json":
        print(json.dumps(graph, indent=2, ensure_ascii=False))
    else:
        print(format_text(graph))
