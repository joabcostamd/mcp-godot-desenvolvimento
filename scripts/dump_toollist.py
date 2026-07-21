"""scripts/dump_toollist.py — Serializa tools/list de cada fase em JSON.

Usado para comparação byte-a-byte com fc (File Compare).
Determinístico: ordenado por nome.
"""

import json
import sys
import io
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from server import _tool_defs, PHASE_TOOLSETS, PHASE_TOOLS_CORE


def dump_phase(phase: str) -> list[dict]:
    """Retorna lista de tools visíveis na fase, ordenada por nome."""
    phase_tools = PHASE_TOOLSETS.get(phase, set())
    visible_names = PHASE_TOOLS_CORE | phase_tools
    
    # Obtém todas as definições de tool (com pós-processamento)
    all_defs = _tool_defs()
    
    # Filtra pelas visíveis na fase
    phase_defs = [t for t in all_defs if t.name in visible_names]
    
    # Serializa como dict, ordenado por nome
    result = []
    for t in sorted(phase_defs, key=lambda x: x.name):
        result.append({
            "name": t.name,
            "title": getattr(t, "title", None),
            "description": t.description,
        })
    return result


def main():
    phases = ["IDEIA", "DESIGN", "PROTOTIPO", "CONTEUDO", "POLIMENTO", "PRONTO_PARA_LANCAR"]
    
    all_data = {}
    for phase in phases:
        all_data[phase] = dump_phase(phase)
    
    import io
    output = json.dumps(all_data, indent=2, ensure_ascii=False, sort_keys=True)
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    print(output)


if __name__ == "__main__":
    main()
