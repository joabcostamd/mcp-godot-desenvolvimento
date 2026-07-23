"""gen_catalog.py — Gera catálogo de tools a partir do registry (ONDA 1.4).

Lê registry.build_tool_defs() e gera documentação Markdown.
Duas execuções devem produzir saída idêntica (determinismo).
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from registry import build_tool_defs


def generate() -> str:
    """Gera catálogo Markdown."""
    tools = build_tool_defs()
    
    lines = []
    lines.append("# Catálogo de Tools — MCP Godot Agent")
    lines.append(f"**Total:** {len(tools)} tools")
    lines.append("")
    lines.append("| # | Tool | Fase | Namespace |")
    lines.append("|---|------|------|-----------|")
    
    for i, tool in enumerate(tools, 1):
        name = tool.name
        phase = getattr(tool, "phase", "-") or "-"
        ns = getattr(tool, "namespace", "-") or "-"
        lines.append(f"| {i} | `{name}` | {phase} | {ns} |")
    
    lines.append("")
    lines.append("*Gerado por gen_catalog.py*")
    return "\n".join(lines)


if __name__ == "__main__":
    print(generate())
