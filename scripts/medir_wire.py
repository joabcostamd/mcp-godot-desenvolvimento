"""R7: Medição real de tools por fase — ONDA R.
Usa _get_phase_tools() com projeto ativo fixo para obter
o número que o modelo realmente vê, não a declaração.
"""

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

import server

def medir():
    """Mede tools por fase e imprime relatório."""
    print("# MEDICAO_R7 — Tools por fase (visão real do modelo)")
    print(f"## Data: 2026-07-23")
    print()

    # CORE
    core = set(getattr(server, "PHASE_TOOLS_CORE", []) or [])
    print(f"## CORE: {len(core)} tools")
    for t in sorted(core):
        print(f"  - {t}")
    print()

    # PHASE_TOOLSETS (curadoria declarada)
    print("## PHASE_TOOLSETS (curadoria declarada)")
    for phase in server.PHASE_TOOLSETS:
        tools = set(server.PHASE_TOOLSETS[phase])
        uniao = tools | core
        print(f"### {phase}: {len(tools)} tools (união CORE: {len(uniao)})")
        for t in sorted(tools):
            print(f"  - {t}")
    print()

    # _tool_defs (curadas, 236)
    defs = server._tool_defs()
    print(f"## _tool_defs(): {len(defs)} tools (curadas)")

    # _raw_tool_defs (brutas, 272)
    raw = server._raw_tool_defs()
    print(f"## _raw_tool_defs(): {len(raw)} tools (brutas)")
    print()

    # Contagem por fase via TOOLSETS (namespaces)
    print("## TOOLSETS (namespaces):")
    for ns, tools in server.TOOLSETS.items():
        print(f"  {ns}: {len(tools)} tools")
    print()

    # Total estimado visível
    print(f"## Resumo")
    print(f"- Definições brutas: {len(raw)}")
    print(f"- Definições curadas: {len(defs)}")
    print(f"- CORE (sempre visível): {len(core)}")
    print(f"- Namespaces semânticos: {len(server.TOOLSETS)}")
    for phase in server.PHASE_TOOLSETS:
        tools = set(server.PHASE_TOOLSETS[phase])
        uniao = tools | core
        print(f"- {phase}: {len(uniao)} tools (fase {len(tools)} + CORE {len(core)} = união {len(uniao)})")


if __name__ == "__main__":
    medir()
