"""tests/test_invariants.py — Testes para INV-01 a INV-15 (Seção 15 do roadmap).

Cada invariante tem um teste. Invariantes não implementadas usam @pytest.mark.xfail
com reason= documentando qual fase deveria tê-las criado.
"""

import pytest


def _run_invariant(inv_id: str) -> tuple[bool, str]:
    """Executa uma invariante específica de registry/invariants.py."""
    from registry.invariants import check_all
    results = check_all("F5")
    for rid, passed, detail in results:
        if rid == inv_id:
            return passed, detail
    return False, f"Invariante {inv_id} não encontrada em check_all()"


# ── INV-01: Toda tool em tools/list tem handler ────────────────────

def test_inv_01():
    """INV-01: Toda tool em _tool_defs() tem handler em _build_handlers()."""
    passed, detail = _run_invariant("INV-01")
    assert passed, f"INV-01 FALHOU: {detail}"


# ── INV-02: Todo handler tem tool em tools/list ────────────────────

def test_inv_02():
    """INV-02: Todo handler em _build_handlers() tem tool em _tool_defs()."""
    passed, detail = _run_invariant("INV-02")
    assert passed, f"INV-02 FALHOU: {detail}"


# ── INV-03: Todas as tools têm namespace ───────────────────────────

def test_inv_03():
    """INV-03: Toda tool pertence a pelo menos um namespace em TOOLSETS."""
    try:
        from server import TOOLSETS
        from registry.invariants import _get_tool_names
        from tools.deprecated import DEPRECATED_TOOLS
        tools = _get_tool_names()
        all_ns_tools: set[str] = set()
        for names in TOOLSETS.values():
            all_ns_tools.update(names)
        # Depreciadas são intencionalmente sem namespace
        missing = tools - all_ns_tools - DEPRECATED_TOOLS
        assert not missing, f"Tools sem namespace (excluindo depreciadas): {sorted(missing)}"
    except ImportError:
        pytest.skip("TOOLSETS não disponível")


# ── INV-04: Todas as tools têm fase ────────────────────────────────

@pytest.mark.xfail(reason="NAO_IMPLEMENTADA — Deveria ser criada na Fase 1 (registry). INV-04 verifica que toda tool pertence a pelo menos uma fase em PHASE_TOOLSETS ou CORE.")
def test_inv_04():
    pytest.xfail("INV-04 não implementada em registry/invariants.py")


# ── INV-05: Nomes seguem convenção §6.1 ────────────────────────────

@pytest.mark.xfail(reason="NAO_IMPLEMENTADA — Deveria ser criada na Fase 1 (registry). INV-05 valida que nomes de tools seguem snake_case e rollups terminam em _manage.")
def test_inv_05():
    pytest.xfail("INV-05 não implementada em registry/invariants.py")


# ── INV-06: Descrições seguem template §6.2 ────────────────────────

@pytest.mark.xfail(reason="NAO_IMPLEMENTADA — Deveria ser criada na Fase 1 (registry). INV-06 valida que descrições incluem QUANDO USAR/QUANDO NÃO USAR.")
def test_inv_06():
    pytest.xfail("INV-06 não implementada em registry/invariants.py")


# ── INV-07: Annotations são ToolAnnotations (não dict) ─────────────

@pytest.mark.xfail(reason="NAO_IMPLEMENTADA — Deveria ser criada na Fase 2 (conformidade MCP). INV-07 verifica que toda tool.annotations é instância de ToolAnnotations.")
def test_inv_07():
    pytest.xfail("INV-07 não implementada em registry/invariants.py")


# ── INV-08: Schema é JSON Schema válido ────────────────────────────

@pytest.mark.xfail(reason="NAO_IMPLEMENTADA — Deveria ser criada na Fase 2 (conformidade). INV-08 valida inputSchema contra meta-schema JSON Schema.")
def test_inv_08():
    pytest.xfail("INV-08 não implementada em registry/invariants.py")


# ── INV-09: Hints são booleanos ────────────────────────────────────

@pytest.mark.xfail(reason="NAO_IMPLEMENTADA — Deveria ser criada na Fase 2 (conformidade). INV-09 verifica que hints (readOnlyHint etc.) são booleanos.")
def test_inv_09():
    pytest.xfail("INV-09 não implementada em registry/invariants.py")


# ── INV-10: PHASE_TOOLSETS → tools/list ────────────────────────────

def test_inv_10():
    """INV-10: Todo nome em PHASE_TOOLSETS existe em _tool_defs()."""
    passed, detail = _run_invariant("INV-10")
    assert passed, f"INV-10 FALHOU: {detail}"


# ── INV-11: TOOLSETS → tools/list ──────────────────────────────────

def test_inv_11():
    """INV-11: Todo nome em TOOLSETS existe em _tool_defs()."""
    passed, detail = _run_invariant("INV-11")
    assert passed, f"INV-11 FALHOU: {detail}"


# ── INV-12: Sem duplicação de namespace ────────────────────────────

def test_inv_12():
    """INV-12: Nenhum nome de tool aparece em 2+ namespaces."""
    passed, detail = _run_invariant("INV-12")
    assert passed, f"INV-12 FALHOU: {detail}"


# ── INV-13: Sem colisão de registro ────────────────────────────────

def test_inv_13():
    """INV-13: Sem colisão de registro (placeholder até F3)."""
    passed, detail = _run_invariant("INV-13")
    assert passed, f"INV-13 FALHOU: {detail}"


# ── INV-14: Sem duplicação de descrições ───────────────────────────

@pytest.mark.xfail(reason="NAO_IMPLEMENTADA — Deveria ser criada na Fase 4 (descoberta progressiva). INV-14 verifica similaridade < 0.80 entre descrições.")
def test_inv_14():
    pytest.xfail("INV-14 não implementada em registry/invariants.py")


# ── INV-15: Domínios migrados têm paridade com legado ──────────────

@pytest.mark.xfail(reason="NAO_IMPLEMENTADA — Deveria ser criada na Fase 5 (migração de domínios). INV-15 verifica test_paridade_com_legado em todos os domínios migrados.")
def test_inv_15():
    pytest.xfail("INV-15 não implementada em registry/invariants.py")
