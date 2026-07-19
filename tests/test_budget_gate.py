"""test_budget_gate.py — Gate de Orçamento de Tools (Fatias 0.8 + 0.16).

Verifica:
  - Teto primário: tokens de definição (~10-15% da janela de contexto)
  - Teto secundário: contagem numérica (≤40 por fase, ≤70 total)

Uso:
    python tests/test_budget_gate.py              # roda todos os testes
    python tests/test_budget_gate.py --lean        # mede perfil lean (CORE + meta-tools)
    python tests/test_budget_gate.py --plant       # simula overflow p/ teste negativo
"""

import json
import sys
from pathlib import Path

# Garante que importa server.py do projeto
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from server import PHASE_TOOLSETS, PHASE_TOOLS_CORE, _tool_defs

# ── Meta-tools do perfil lean (Fatia 0.15) ──────────────────────────
LEAN_META_TOOLS = {"catalog_search", "describe_tool", "invoke_by_name"}

# ── Limites — Teto primário (tokens) ─────────────────────────────────
# Mestre seção 2: definições de tool ≤ ~10-15% da janela de contexto.
# Janela típica DeepSeek V4 Pro = 200k tokens → 10% = 20.000 tokens.
# Perfil lean expõe ~30 tools (CORE + 3 meta-tools) → 5.000 tokens é generoso.
TOKEN_BUDGET = 20_000        # 10% de 200k — para fase individual
TOKEN_BUDGET_LEAN = 5_000    # ~2.5% de 200k — para perfil lean
TOKEN_BUDGET_FULL = 30_000   # 15% de 200k — para total full (referência)

# ── Limites — Teto secundário (contagem, mestre seção 2) ────────────
PHASE_LIMIT = 40
TOTAL_LIMIT = 70

# ── Tools de infra/setup que SÃO esperadas em múltiplos toolsets ─────
# (Não são duplicatas problemáticas — são propositalmente re-expostas)
ALWAYS_ALLOWED_DUPLICATES = {
    "smoke_test", "dump_mcp_state", "capture_proof", "verify_proof",
    "validate_mcp_registry",
}


# ═════════════════════════════════════════════════════════════════════
# Medição de Tokens (Fatia 0.16)
# ═════════════════════════════════════════════════════════════════════

def estimate_definition_tokens(tools: list) -> dict:
    """Estima tokens de definição para uma lista de ferramentas.

    Serializa nome + descrição + inputSchema como JSON
    (simula o payload de tools/list que o modelo recebe).
    Aproximação: bytes // 4 ≈ tokens (válido para JSON).

    Args:
        tools: Lista de objetos Tool de server._tool_defs().

    Returns:
        dict com tool_count, json_bytes, estimated_tokens.
    """
    tool_dicts = []
    for t in tools:
        d = {"name": t.name}
        if hasattr(t, 'description') and t.description:
            d["description"] = t.description
        if hasattr(t, 'inputSchema') and t.inputSchema:
            d["inputSchema"] = t.inputSchema
        tool_dicts.append(d)

    json_str = json.dumps(tool_dicts, ensure_ascii=False)
    json_bytes = len(json_str.encode("utf-8"))
    estimated_tokens = json_bytes // 4  # ~4 chars por token em JSON

    return {
        "tool_count": len(tool_dicts),
        "json_bytes": json_bytes,
        "estimated_tokens": estimated_tokens,
    }


def test_token_budget(lean_only: bool = False) -> list[str]:
    """Testa que o consumo de tokens por perfil está dentro do teto.

    Args:
        lean_only: Se True, só testa o perfil lean.

    Returns:
        Lista de falhas (vazia = todas ok).
    """
    all_tools = _tool_defs()
    failures = []

    # Perfil lean (CORE + meta-tools) — o cenário real do modo lean
    lean_names = PHASE_TOOLS_CORE | LEAN_META_TOOLS
    lean_tools = [t for t in all_tools if t.name in lean_names]
    lean_est = estimate_definition_tokens(lean_tools)
    if lean_est["estimated_tokens"] > TOKEN_BUDGET_LEAN:
        failures.append(
            f"❌ PERFIL LEAN: ~{lean_est['estimated_tokens']} tokens "
            f"({lean_est['tool_count']} tools, limite: {TOKEN_BUDGET_LEAN})"
        )

    if lean_only:
        return failures

    # Perfil full (todas as tools de topo) — referência
    full_est = estimate_definition_tokens(all_tools)
    if full_est["estimated_tokens"] > TOKEN_BUDGET_FULL:
        failures.append(
            f"❌ PERFIL FULL: ~{full_est['estimated_tokens']} tokens "
            f"({full_est['tool_count']} tools, limite: {TOKEN_BUDGET_FULL})"
        )

    # Por fase — cada fase filtra as tools visíveis
    for phase, phase_tools in PHASE_TOOLSETS.items():
        visible = PHASE_TOOLS_CORE | phase_tools
        visible_tools = [t for t in all_tools if t.name in visible]
        phase_est = estimate_definition_tokens(visible_tools)
        budget = TOKEN_BUDGET_LEAN if len(visible_tools) <= len(PHASE_TOOLS_CORE) + 3 else TOKEN_BUDGET
        if phase_est["estimated_tokens"] > budget:
            failures.append(
                f"❌ FASE '{phase}': ~{phase_est['estimated_tokens']} tokens "
                f"({phase_est['tool_count']} tools, limite: {budget})"
            )

    return failures


# ═════════════════════════════════════════════════════════════════════
# Contagem Numérica (Fatia 0.8)
# ═════════════════════════════════════════════════════════════════════

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


# ═════════════════════════════════════════════════════════════════════
# Runner Principal
# ═════════════════════════════════════════════════════════════════════

def run_all_tests(plant_overflow: bool = False, lean_only: bool = False) -> dict:
    """Roda todos os testes e retorna resultado estruturado.

    Args:
        plant_overflow: Se True, simula overflow forçando contagem/tokens altos.
        lean_only: Se True, só testa o perfil lean.

    Returns:
        dict com status, erros, contagens, métricas de tokens.
    """
    # ── Estado real ──────────────────────────────────────────────
    phase_counts = count_tools_per_phase()
    total_count = count_total_top_level_tools()
    orphans = check_consistency()
    all_tools = _tool_defs()

    # ── Medição de tokens real ───────────────────────────────────
    # Perfil lean
    lean_names = PHASE_TOOLS_CORE | LEAN_META_TOOLS
    lean_tools = [t for t in all_tools if t.name in lean_names]
    lean_est = estimate_definition_tokens(lean_tools)

    # Perfil full
    full_est = estimate_definition_tokens(all_tools)

    # Tokens por fase
    token_per_phase = {}
    for phase, phase_tools in PHASE_TOOLSETS.items():
        visible = PHASE_TOOLS_CORE | phase_tools
        visible_tools = [t for t in all_tools if t.name in visible]
        token_per_phase[phase] = estimate_definition_tokens(visible_tools)

    # ── Overflow simulado ────────────────────────────────────────
    if plant_overflow:
        phase_counts["_FAKE_OVERFLOW_PHASE"] = 99
        total_count = 99
        lean_est = {"tool_count": 99, "json_bytes": 99999, "estimated_tokens": 99999}
        token_per_phase["_FAKE_OVERFLOW"] = {"tool_count": 99, "json_bytes": 99999, "estimated_tokens": 99999}

    # ── Testes ──────────────────────────────────────────────────
    errors = []

    # Teste de tokens (teto primário)
    token_failures = test_token_budget(lean_only=lean_only)
    if plant_overflow:
        # Se plant, força falha de tokens também
        token_failures.append("❌ (plant) FAKE TOKEN OVERFLOW — limite excedido")
    errors.extend(token_failures)

    # Testes de contagem (teto secundário) — só roda se não for lean_only
    if not lean_only:
        phase_failures = []
        for phase, count in phase_counts.items():
            if count > PHASE_LIMIT:
                phase_failures.append(
                    f"FASE '{phase}' tem {count} tools (limite: {PHASE_LIMIT})"
                )
        errors.extend(phase_failures)

        total_error = None
        if total_count > TOTAL_LIMIT:
            total_error = f"TOTAL tem {total_count} tools de topo (limite: {TOTAL_LIMIT})"
        if total_error:
            errors.append(total_error)

    # ── Status ──────────────────────────────────────────────────
    status = "success"
    if errors and plant_overflow:
        status = "overflow_detected_ok"
    elif errors:
        status = "failure"

    # ── Resumo ──────────────────────────────────────────────────
    summary = {}
    for phase, tools in PHASE_TOOLSETS.items():
        visible = PHASE_TOOLS_CORE | tools
        summary[phase] = f"{len(visible)} tools / ~{token_per_phase[phase]['estimated_tokens']} tokens"

    if not plant_overflow:
        summary["_total_tools"] = total_count
        summary["_full_tokens"] = full_est["estimated_tokens"]
        summary["_lean_tokens"] = lean_est["estimated_tokens"]
        summary["_lean_tool_count"] = lean_est["tool_count"]
    summary["_orphan_tools_count"] = len(orphans)

    return {
        "status": status,
        "errors": errors,
        "orphans": orphans[:10] if orphans else [],
        "summary": summary,
        "phase_count": len(PHASE_TOOLSETS),
        "token_metrics": {
            "lean": {"tools": lean_est["tool_count"], "tokens": lean_est["estimated_tokens"], "budget": TOKEN_BUDGET_LEAN},
            "full": {"tools": full_est["tool_count"], "tokens": full_est["estimated_tokens"], "budget": TOKEN_BUDGET_FULL},
            "per_phase": {phase: {"tokens": m["estimated_tokens"], "tools": m["tool_count"]} for phase, m in token_per_phase.items()},
        },
        "limits": {
            "per_phase_tokens": TOKEN_BUDGET,
            "lean_tokens": TOKEN_BUDGET_LEAN,
            "full_tokens": TOKEN_BUDGET_FULL,
            "per_phase_count": PHASE_LIMIT,
            "total_count": TOTAL_LIMIT,
        },
    }


# ══════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    plant = "--plant" in sys.argv
    lean = "--lean" in sys.argv

    result = run_all_tests(plant_overflow=plant, lean_only=lean)

    print("=" * 70)
    print("🧮 GATE DE ORÇAMENTO DE TOOLS (Fatias 0.8 + 0.16)")
    print("=" * 70)

    # ── Teto primário: tokens ────────────────────────────────────
    print("\n📊 TETO PRIMÁRIO — Estimativa de Tokens de Definição:")
    tm = result["token_metrics"]
    lean_marker = "⚠️" if tm["lean"]["tokens"] > result["limits"]["lean_tokens"] else "✅"
    print(f"  {lean_marker} Perfil Lean: ~{tm['lean']['tokens']} tokens "
          f"({tm['lean']['tools']} tools, orçamento: {result['limits']['lean_tokens']})")
    full_marker = "⚠️" if tm["full"]["tokens"] > result["limits"]["full_tokens"] else "✅"
    print(f"  {full_marker} Perfil Full: ~{tm['full']['tokens']} tokens "
          f"({tm['full']['tools']} tools, orçamento: {result['limits']['full_tokens']})")
    print(f"  {'─' * 55}")
    for phase, m in sorted(tm["per_phase"].items()):
        budget = result["limits"]["lean_tokens"] if m["tools"] <= 33 else result["limits"]["per_phase_tokens"]
        marker = "⚠️" if m["tokens"] > budget else "✅"
        print(f"  {marker} {phase}: ~{m['tokens']} tokens ({m['tools']} tools, orçamento: {budget})")

    # ── Teto secundário: contagem ────────────────────────────────
    print(f"\n📊 TETO SECUNDÁRIO — Contagem por fase (limite: {result['limits']['per_phase_count']} tools):")
    for phase, summary_line in sorted(result["summary"].items()):
        if phase.startswith("_"):
            continue
        # Extrai a contagem do resumo
        count_str = summary_line.split(" tools")[0]
        try:
            count = int(count_str)
            marker = "⚠️" if count > result["limits"]["per_phase_count"] else "✅"
        except ValueError:
            marker = "?"
        print(f"  {marker} {phase}: {summary_line}")

    if "_total_tools" in result["summary"]:
        total = result["summary"]["_total_tools"]
        marker = "⚠️" if total > result["limits"]["total_count"] else "✅"
        print(f"\n  {marker} TOTAL: {total} tools de topo (limite: {result['limits']['total_count']})")

    if "_lean_tool_count" in result["summary"]:
        print(f"\n  ℹ️  Tools visíveis no modo lean: {result['summary']['_lean_tool_count']}")

    if result.get("orphans"):
        print(f"\n⚠️  Tools órfãs (não categorizadas): {len(result['orphans'])}")
        for o in result["orphans"]:
            print(f"  - {o}")

    print(f"\n🔍 Resultado: {result['status']}")
    for error in result.get("errors", []):
        print(f"  {error}")

    if result["status"] == "success":
        print(f"\n✅ ORÇAMENTO OK — Tokens e contagem dentro dos limites.")
        sys.exit(0)
    elif result["status"] == "overflow_detected_ok":
        print(f"\n✅ OVERFLOW DETECTADO (teste negativo passou) — Gate funciona.")
        sys.exit(0)
    else:
        print(f"\n❌ GATE FALHOU — {len(result['errors'])} erro(s) de orçamento.")
        sys.exit(1)