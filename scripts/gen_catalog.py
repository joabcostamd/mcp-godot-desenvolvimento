"""gen_catalog.py — Gera catálogo de tools a partir do registry (ONDA 1.4).

Lê registry.build_tool_defs() e gera documentação Markdown.
Duas execuções devem produzir saída idêntica (determinismo).
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from registry import build_tool_defs
from core.legacy_data import PHASE_TOOLSETS, PHASE_TOOLS_CORE, TOOLSETS


def _resolve_phase(name: str) -> str:
    """Retorna a(s) fase(s) de uma tool."""
    phases = []
    if name in PHASE_TOOLS_CORE:
        phases.append("CORE")
    for phase, tools in PHASE_TOOLSETS.items():
        if name in tools:
            phases.append(phase)
    return ",".join(phases) if phases else "-"


def _resolve_namespace(name: str) -> str:
    """Retorna o namespace de uma tool."""
    for ns, tools in TOOLSETS.items():
        if name in tools:
            return ns
    return "-"


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
        phase = _resolve_phase(name)
        ns = _resolve_namespace(name)
        lines.append(f"| {i} | `{name}` | {phase} | {ns} |")
    
    lines.append("")
    lines.append("*Gerado por gen_catalog.py*")
    return "\n".join(lines)


if __name__ == "__main__":
    print(generate())
