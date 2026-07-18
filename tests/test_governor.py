"""tests/test_governor.py — Testes de confirmacao dos freios do Governador (Fatia 0.14).

Prova que cada guardrail do mestre secao 4 funciona.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tools.governor import AutonomyGovernor


def test_iteration_cap():
    """Prova que o teto de 8 iteracoes bloqueia a 9a."""
    gov = AutonomyGovernor(max_iterations=8, hard_stop=True, enabled=True)
    for i in range(8):
        gov.record_after(f"tool_{i}", {"step": i}, success=True, progress_marker=f"step_{i}")
    allowed, reason = gov.check_before("tool_9", {"step": 9})
    assert not allowed, f"Esperado bloqueio, mas passou. Iteracoes: {gov.state.iteration_count}"
    assert "iterações" in reason or "Limite" in reason, f"Motivo errado: {reason}"
    print(f"✅ TETO ITERACAO: Bloqueou apos {gov.state.iteration_count} iteracoes — '{reason[:80]}'")


def test_anti_spiral():
    """Prova que 2 falhas identicas disparam anti-spiral."""
    gov = AutonomyGovernor(spiral_threshold=2, hard_stop=True, enabled=True)
    # 1a falha
    gov.record_after("broken_tool", {"x": 1}, success=False, error_message="erro")
    # 2a falha identica
    gov.record_after("broken_tool", {"x": 1}, success=False, error_message="erro")
    # A 3a chamada identica deve ser bloqueada
    allowed, reason = gov.check_before("broken_tool", {"x": 1})
    assert not allowed, f"Esperado bloqueio anti-spiral, mas passou"
    assert gov.state.stopped, "Governador deveria estar stopped"
    print(f"✅ ANTI-SPIRAL: Bloqueou apos 2 falhas identicas — '{reason[:80]}'")


def test_no_progress():
    """Prova que 3 passagens sem progresso sao detectadas."""
    gov = AutonomyGovernor(no_progress_threshold=3, hard_stop=True, enabled=True)
    for i in range(3):
        gov.record_after("stuck_tool", {"x": i}, success=False, error_message="stuck")
    assert gov.state.no_progress_count >= 3, f"Esperado >=3 sem progresso, obteve {gov.state.no_progress_count}"
    assert gov.state.stopped, "Governador deveria estar stopped"
    print(f"✅ NAO-PROGRESSO: Detectou apos {gov.state.no_progress_count} passagens sem progresso — '{gov.state.stop_reason[:80]}'")


def test_budget_exceeded():
    """Prova que orcamento excedido bloqueia."""
    gov = AutonomyGovernor(budget_calls=5, max_iterations=999, hard_stop=True, enabled=True)
    for i in range(5):
        gov.record_after(f"tool_{i}", {"step": i}, success=True)
    allowed, reason = gov.check_before("tool_6", {"step": 6})
    assert not allowed, f"Esperado bloqueio por orcamento, mas passou. Budget: {gov.state.budget_used}"
    print(f"✅ ORCAMENTO: Bloqueou apos {gov.state.budget_used} chamadas — '{reason[:80]}'")


def test_reset():
    """Prova que reset limpa o estado."""
    gov = AutonomyGovernor(max_iterations=2, hard_stop=True, enabled=True)
    gov.record_after("tool_1", {"x": 1}, success=True)
    gov.record_after("tool_2", {"x": 2}, success=True)
    assert gov.state.iteration_count == 2
    gov.reset()
    assert gov.state.iteration_count == 0
    assert not gov.state.stopped
    print(f"✅ RESET: Estado zerado corretamente")


def test_always_allowed():
    """Prova que tools de infra nunca sao bloqueadas."""
    gov = AutonomyGovernor(budget_calls=0, hard_stop=True, enabled=True)  # orcamento zero
    gov.state.budget_used = 999  # ja estourou
    allowed, reason = gov.check_before("ping", {})
    assert allowed, f"Ping deveria ser always-allowed, mas foi bloqueado: {reason}"
    print(f"✅ ALWAYS-ALLOWED: Ping passou mesmo com orcamento estourado")


def test_escalation_package():
    """Prova que o pacote de escalacao contem os campos obrigatorios."""
    gov = AutonomyGovernor(max_iterations=1, hard_stop=True, enabled=True)
    gov.record_after("failed_tool", {"x": 1}, success=False, error_message="falhou")
    gov.record_after("failed_tool", {"x": 1}, success=False, error_message="falhou de novo")
    pkg = gov.build_escalation_package("Teste de fatia X")
    assert "task" in pkg
    assert "attempts" in pkg
    assert "output" in pkg
    assert "hypothesis" in pkg
    assert "state_preserved" in pkg
    print(f"✅ PACOTE ESCALACAO: {pkg['hypothesis'][:80]}")


def run_all():
    tests = [
        ("Teto de iteracao (8)", test_iteration_cap),
        ("Anti-spiral (2 falhas identicas)", test_anti_spiral),
        ("Nao-progresso (3 passagens)", test_no_progress),
        ("Orcamento excedido", test_budget_exceeded),
        ("Reset", test_reset),
        ("Always-allowed", test_always_allowed),
        ("Pacote de escalacao", test_escalation_package),
    ]
    failed = 0
    for name, fn in tests:
        try:
            fn()
        except Exception as e:
            print(f"❌ {name}: {e}")
            failed += 1
    print(f"\n{'='*40}")
    print(f"Resultado: {len(tests) - failed}/{len(tests)} passaram, {failed} falharam")
    return failed


if __name__ == "__main__":
    sys.exit(run_all())