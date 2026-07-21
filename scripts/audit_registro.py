"""audit_registro.py — Medicao do registro de tools (FATIA T1-R).

NAO altera, NAO deleta, NAO renomeia nada. So mede e imprime.
"""

import sys
import json
from pathlib import Path

# Garantir que a raiz do projeto está no path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

# ── Imports do server ─────────────────────────────────────────────
from server import _tool_defs, _build_handlers
from server import TOOLSETS, PHASE_TOOLSETS, PHASE_TOOLS_CORE, TOOL_PROFILES

# ── Imports do rollup ─────────────────────────────────────────────
from tools.rollups import get_rollup_tool_defs, get_rollup_handlers

# ── raw tool defs (sem filtro) ────────────────────────────────────
from core.tool_definitions import _raw_tool_defs


def main():
    # Coletar dados
    raw_defs = _raw_tool_defs()
    defs = _tool_defs()
    rollup_defs = get_rollup_tool_defs()
    handlers = _build_handlers()
    rollup_handlers = get_rollup_handlers()

    raw_names = {t.name for t in raw_defs}
    defs_names = {t.name for t in defs}
    rollup_names = {t.name for t in rollup_defs}
    handlers_names = set(handlers.keys())
    rollup_handlers_names = set(rollup_handlers.keys())

    # ── Contagens ─────────────────────────────────────────────────
    print("=" * 60)
    print("CONTAGENS")
    print("=" * 60)
    
    print(f"defs_total = {len(defs)}")
    print(f"defs_raw = {len(raw_defs)}")
    print(f"defs_rollup = {len(rollup_defs)}")
    print(f"handlers_total = {len(handlers)}")
    print(f"handlers_rollup = {len(rollup_handlers)}")

    manage_raw = sorted([n for n in raw_names if n.endswith("_manage")])
    manage_rollup = sorted([n for n in rollup_names if n.endswith("_manage")])
    print(f"manage_em_raw = {manage_raw}")
    print(f"manage_em_rollup = {manage_rollup}")

    toolsets_soma = sum(len(v) for v in TOOLSETS.values())
    print(f"toolsets_entradas_soma = {toolsets_soma}")

    all_toolset_names = set()
    for ns, names in TOOLSETS.items():
        all_toolset_names.update(names)
    print(f"toolsets_nomes_unicos = {len(all_toolset_names)}")

    all_phase_names = set()
    for phase, names in PHASE_TOOLSETS.items():
        all_phase_names.update(names)
    all_phase_names.update(PHASE_TOOLS_CORE)
    print(f"phase_nomes_unicos = {len(all_phase_names)}")

    # ── Listas de divergencia ─────────────────────────────────────
    print()
    print("=" * 60)
    print("DIVERGENCIAS")
    print("=" * 60)

    sem_handler = sorted(defs_names - handlers_names)
    print(f"\n--- SEM_HANDLER (em _tool_defs() mas NAO em _build_handlers()) ---")
    print(f"Total: {len(sem_handler)}")
    for n in sem_handler:
        print(f"  {n}")

    sem_def = sorted(handlers_names - defs_names)
    print(f"\n--- SEM_DEF (em _build_handlers() mas NAO em _tool_defs()) ---")
    print(f"Total: {len(sem_def)}")
    for n in sem_def:
        print(f"  {n}")

    # Duplicados em namespaces
    ns_map = {}
    for ns, names in TOOLSETS.items():
        for n in names:
            if n not in ns_map:
                ns_map[n] = []
            ns_map[n].append(ns)

    duplicados_ns = {n: nss for n, nss in ns_map.items() if len(nss) > 1}
    print(f"\n--- DUPLICADOS_NS (nome em 2+ namespaces) ---")
    print(f"Total: {len(duplicados_ns)}")
    for n, nss in sorted(duplicados_ns.items()):
        print(f"  {n} -> {nss}")

    ns_fantasma = sorted(all_toolset_names - defs_names)
    print(f"\n--- NS_FANTASMA (em TOOLSETS mas NAO em _tool_defs()) ---")
    print(f"Total: {len(ns_fantasma)}")
    for n in ns_fantasma:
        print(f"  {n}")

    phase_fantasma = sorted(all_phase_names - defs_names)
    print(f"\n--- PHASE_FANTASMA (em PHASE_TOOLSETS mas NAO em _tool_defs()) ---")
    print(f"Total: {len(phase_fantasma)}")
    for n in phase_fantasma:
        print(f"  {n}")

    sem_namespace = sorted(defs_names - all_toolset_names)
    print(f"\n--- SEM_NAMESPACE (em _tool_defs() mas NAO em TOOLSETS) ---")
    print(f"Total: {len(sem_namespace)}")
    for n in sem_namespace:
        print(f"  {n}")

    # Orfas de fase = em defs mas nao em PHASE_TOOLSETS nem CORE
    sem_fase = sorted(defs_names - all_phase_names)
    print(f"\n--- SEM_FASE (em _tool_defs() mas NAO em PHASE_TOOLSETS nem CORE) ---")
    print(f"Total: {len(sem_fase)}")
    for n in sem_fase:
        print(f"  {n}")

    colisao_rollup = sorted(raw_names & rollup_names)
    print(f"\n--- COLISAO_ROLLUP (em _raw_tool_defs() E em get_rollup_tool_defs()) ---")
    print(f"Total: {len(colisao_rollup)}")
    for n in colisao_rollup:
        print(f"  {n}")

    # ── Tools visiveis por fase ───────────────────────────────────
    print()
    print("=" * 60)
    print("TOOLS VISIVEIS POR FASE (CORE + fase)")
    print("=" * 60)
    for phase in ["IDEIA", "DESIGN", "PROTOTIPO", "CONTEUDO", "POLIMENTO", "PRONTO_PARA_LANCAR"]:
        phase_set = PHASE_TOOLSETS.get(phase, set())
        visible = PHASE_TOOLS_CORE | phase_set
        print(f"  {phase}: {len(visible)} tools visiveis (CORE={len(PHASE_TOOLS_CORE)} + fase={len(phase_set)})")

    # ── JSON de 3 tools ───────────────────────────────────────────
    print()
    print("=" * 60)
    print("JSON DE 3 TOOLS (pos-processadas)")
    print("=" * 60)

    def find_tool(name):
        for t in defs:
            if t.name == name:
                return t
        return None

    for target in ["read_file", "scene_manage", "godot_exec"]:
        tool = find_tool(target)
        if tool:
            print(f"\n--- {target} ---")
            print(tool.model_dump_json(indent=2))
        else:
            print(f"\n--- {target}: NAO ENCONTRADA em _tool_defs() ---")


if __name__ == "__main__":
    main()
