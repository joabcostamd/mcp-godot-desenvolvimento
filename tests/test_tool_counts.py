"""
Testes de contagem de tools — FASE 8 (Autogovernança).

Garantem que nenhuma tool nova entra no sistema sem revisão
consciente. Inspirado nos testes de contagem do MCP Servers
(toHaveBeenCalledTimes).

Se um destes testes quebrar:
1. A ferramenta nova foi intencional? → Atualize a constante.
2. Foi acidental? → Remova a definição indesejada.
3. É rollup válido? → Atualize EXPECTED_ROLLUPS.
"""

import pytest


# ── Constantes de baseline ─────────────────────────────────────
# Atualize estas constantes quando adicionar/remover tools intencionalmente.

EXPECTED_TOTAL_TOOLS = 209
EXPECTED_ROLLUPS = 44
EXPECTED_DEPRECATED = 205
EXPECTED_ALIASES = 90
EXPECTED_CORE = 25
EXPECTED_QUARENTENA = 19


def test_total_tool_count():
    """Garante que nenhuma tool nova entra sem revisão."""
    from server import _tool_defs
    actual = len(_tool_defs())
    assert actual == EXPECTED_TOTAL_TOOLS, (
        f"Contagem de tools mudou: {EXPECTED_TOTAL_TOOLS} → {actual}. "
        f"Se intencional, atualize EXPECTED_TOTAL_TOOLS em tests/test_tool_counts.py. "
        f"Se acidental, remova a definição indesejada."
    )


def test_rollup_count():
    """Garante que rollups não são adicionados/removidos sem revisão."""
    from tools.rollups import get_rollup_tool_defs
    actual = len(get_rollup_tool_defs())
    assert actual == EXPECTED_ROLLUPS, (
        f"Contagem de rollups mudou: {EXPECTED_ROLLUPS} → {actual}. "
        f"Se intencional, atualize EXPECTED_ROLLUPS."
    )


def test_no_gaps():
    """Garante zero gaps de organização (SEM_FASE, FANTASMAS, COLISÕES)."""
    from server import _tool_defs
    from core.legacy_data import PHASE_TOOLSETS, PHASE_TOOLS_CORE, TOOLSETS
    from tools.deprecated import DEPRECATED_TOOLS
    from collections import Counter

    tools = {t.name for t in _tool_defs()}
    all_phased = set(PHASE_TOOLS_CORE)
    for v in PHASE_TOOLSETS.values():
        all_phased |= v
    all_ns = set()
    for v in TOOLSETS.values():
        all_ns.update(v)

    sem_fase = tools - all_phased - DEPRECATED_TOOLS
    assert not sem_fase, f"SEM_FASE: {sorted(sem_fase)}"

    fantasmas = all_phased - tools - DEPRECATED_TOOLS
    assert not fantasmas, f"FANTASMAS: {sorted(fantasmas)}"

    dups = {n: c for n, c in Counter([t.name for t in _tool_defs()]).items() if c > 1}
    assert not dups, f"COLISÕES: {list(dups.keys())}"


def test_lean_mode_all_phases_within_ceiling():
    """Garante que modo lean mantém todas as fases ≤ 30 tools."""
    from server import _tool_defs
    from core.legacy_data import PHASE_TOOLS_CORE, PHASE_TOOLS_TOP
    from tools.deprecated import DEPRECATED_TOOLS

    tools = {t.name for t in _tool_defs()}
    core = PHASE_TOOLS_CORE - DEPRECATED_TOOLS
    teto = 30

    for phase, top_set in PHASE_TOOLS_TOP.items():
        lean = len(((top_set - DEPRECATED_TOOLS) & tools) | (core & tools))
        assert lean <= teto, (
            f"Lean mode: {phase} tem {lean} tools (teto: {teto}, +{lean - teto})"
        )


def test_quarentena_handlers_exist():
    """Garante que toda tool em quarentena tem handler de fallback."""
    import json
    from pathlib import Path

    qpath = Path("experimental/quarentena.json")
    if qpath.exists():
        quarentena = set(json.loads(qpath.read_text(encoding="utf-8"))["tools"])

        from experimental.quarentena_defs import QUARENTENA_HANDLERS

        missing = quarentena - set(QUARENTENA_HANDLERS.keys())
        assert not missing, f"Quarentena sem handler: {sorted(missing)}"


def test_skills_exist():
    """Garante que as skills estão registradas e geram prompts válidos."""
    from skills import list_skills, skill_to_prompt

    skills = list_skills()
    assert len(skills) >= 14, f"Apenas {len(skills)} skills"

    for s in skills:
        prompt = skill_to_prompt(s["name"])
        assert prompt is not None, f"Skill {s['name']} sem prompt"
        assert len(prompt) > 100, f"Skill {s['name']} prompt muito curto ({len(prompt)} chars)"
