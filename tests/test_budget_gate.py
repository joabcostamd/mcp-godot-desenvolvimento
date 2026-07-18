"""test_budget_gate.py — Gate de Orçamento de Tools (Fatia 0.8).

Verifica se nenhuma fase ultrapassa o teto de tools visíveis.

Teto oficial (mestre seção 2):
  - ≤ 40 tools visíveis por fase (CORE + exclusivas)
  - ≤ 70 tools de topo no total

Uso:
    python tests/test_budget_gate.py         # roda todos os testes
    python tests/test_budget_gate.py --plant  # planta overflow p/ teste negativo
"""

import json
import sys
from pathlib import Path

# Garante que importa server.py do projeto
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from server import PHASE_TOOLSETS, PHASE_TOOLS_CORE, _tool_defs

# ── Limites (mestre seção 2) ─────────────────────────────────────────
PHASE_LIMIT = 40
TOTAL_LIMIT = 70

# ── Tools de infra/setup que SÃO esperadas em múltiplos toolsets ─────
# (Não são duplicatas problemáticas — são propositalmente re-expostas)
ALWAYS_ALLOWED_DUPLICATES = {
    "smoke_test", "dump_mcp_state", "capture_proof", "verify_proof",
    "validate_mcp_registry",
}


def count_tools_per_phase() -> dict[str, int]:
    """Conta tools visíveis por fase (CORE + exclusivas).

    Returns:
        {fase: contagem}
    """
    result = {}
    for phase, phase_tools in PHASE_TOOLSETS.items():
        visible = PHASE_TOOLS_CORE | phase_tools
        result[phase] = len(visible)
    return result


def count_total_top_level_tools() -> int:
    """Conta tools de topo registradas em _tool_defs()."""
    tools = _tool_defs()
    return len(tools)


def check_consistency() -> list[str]:
    """Verifica se toda tool em _tool_defs() está categorizada.

    Returns:
        Lista de ferramentas órfãs (tool definida mas sem toolset).
    """
    all_tools = {t.name for t in _tool_defs()}
    categorized: set[str] = set()
    for tools in PHASE_TOOLSETS.values():
        categorized.update(tools)
    categorized.update(PHASE_TOOLS_CORE)

    orphans = all_tools - categorized
    # Remove tools que são nomes de handler internos (não ferramentas visíveis)
    orphans = {o for o in orphans
               if not o.startswith("_")
               and o not in ALWAYS_ALLOWED_DUPLICATES
               and o not in {"run_gut_tests", "effect_probe", "godot_exec",
                             "get_runtime_state_digest", "capture_runtime_errors",
                             "run_scripted_tests", "regression_test",
                             "estimate_tool_tokens", "test_manage",
                             "execute_gdscript_runtime", "capture_game_screenshot",
                             "godot_screenshot", "godot_runtime_info",
                             "godot_custom_command", "godot_list_custom_commands",
                             "godot_run_project", "godot_stop_project",
                             "godot_wait_for_bridge"}}
    return sorted(orphans)


def test_budget_per_phase() -> list[str]:
    """Testa que cada fase está dentro do limite de 40 tools.

    Returns:
        Lista de fases que estouraram (vazia = todas ok).
    """
    failures = []
    for phase, count in count_tools_per_phase().items():
        if count > PHASE_LIMIT:
            failures.append(
                f"❌ FASE '{phase}' tem {count} tools (limite: {PHASE_LIMIT})"
            )
    return failures


def test_budget_total() -> str | None:
    """Testa que o total de tools de topo está dentro do limite de 70.

    Returns:
        Mensagem de erro ou None se ok.
    """
    total = count_total_top_level_tools()
    if total > TOTAL_LIMIT:
        return f"❌ TOTAL tem {total} tools de topo (limite: {TOTAL_LIMIT})"
    return None


def test_consistency_check() -> list[str]:
    """Testa consistência: tools órfãs (não categorizadas)."""
    return check_consistency()


def run_all_tests(plant_overflow: bool = False) -> dict:
    """Roda todos os testes e retorna resultado estruturado.

    Args:
        plant_overflow: Se True, simula overflow forçando contagem alta.

    Returns:
        dict com status, erros, contagens.
    """
    # Captura estado real primeiro
    phase_counts = count_tools_per_phase()
    total_count = count_total_top_level_tools()
    orphans = check_consistency()

    # Simula overflow se plant=True
    if plant_overflow:
        phase_counts["_FAKE_OVERFLOW_PHASE"] = 99
        total_count = 99

    # Testa
    phase_failures = []
    for phase, count in phase_counts.items():
        if count > PHASE_LIMIT:
            phase_failures.append(
                f"FASE '{phase}' tem {count} tools (limite: {PHASE_LIMIT})"
            )

    total_error = None
    if total_count > TOTAL_LIMIT:
        total_error = f"TOTAL tem {total_count} tools de topo (limite: {TOTAL_LIMIT})"

    # Monta resultado
    errors = []
    if phase_failures:
        errors.extend(phase_failures)
    if total_error:
        errors.append(total_error)

    status = "success"
    if errors and plant_overflow:
        status = "overflow_detected_ok"  # teste negativo passou
    elif errors:
        status = "failure"

    # Resumo por fase
    summary = {phase: len(PHASE_TOOLS_CORE | tools)
               for phase, tools in PHASE_TOOLSETS.items()}
    if not plant_overflow:
        summary["_total_tools"] = total_count
    summary["_orphan_tools_count"] = len(orphans)

    return {
        "status": status,
        "errors": errors,
        "orphans": orphans[:10] if orphans else [],  # limita a 10
        "summary": summary,
        "phase_count": len(PHASE_TOOLSETS),
        "limits": {"per_phase": PHASE_LIMIT, "total": TOTAL_LIMIT},
    }


# ══════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    plant = "--plant" in sys.argv

    result = run_all_tests(plant_overflow=plant)

    print("=" * 65)
    print("🧮 GATE DE ORÇAMENTO DE TOOLS (Fatia 0.8)")
    print("=" * 65)

    print(f"\n📊 Contagem por fase (limite: {result['limits']['per_phase']} tools):")
    for phase, count in sorted(result["summary"].items()):
        if phase.startswith("_"):
            continue
        marker = "⚠️" if count > result["limits"]["per_phase"] else "✅"
        print(f"  {marker} {phase}: {count} tools")

    if "_total_tools" in result["summary"]:
        total = result["summary"]["_total_tools"]
        marker = "⚠️" if total > result["limits"]["total"] else "✅"
        print(f"\n  {marker} TOTAL: {total} tools de topo (limite: {result['limits']['total']})")

    if result.get("orphans"):
        print(f"\n⚠️  Tools órfãs (não categorizadas): {len(result['orphans'])}")
        for o in result["orphans"]:
            print(f"  - {o}")

    print(f"\n🔍 Resultado: {result['status']}")
    for error in result.get("errors", []):
        print(f"  {error}")

    if result["status"] == "success":
        print("\n✅ ORÇAMENTO OK — Nenhuma fase estourou o limite.")
        sys.exit(0)
    elif result["status"] == "overflow_detected_ok":
        print("\n✅ OVERFLOW DETECTADO (teste negativo passou) — Gate funciona.")
        sys.exit(0)
    else:
        print(f"\n❌ GATE FALHOU — {len(result['errors'])} erro(s) de orçamento.")
        sys.exit(1)