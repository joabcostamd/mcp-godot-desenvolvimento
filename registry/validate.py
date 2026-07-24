"""
ToolRegistry.validate() — Validação unificada fail-fast.

FASE 8: Autogovernança. Roda todas as invariantes + gates + regras
em uma única chamada. Inspirado no Builder.Build() do GitHub MCP Server.

Uso:
    from registry.validate import validate_all
    errors = validate_all()
    if errors:
        for e in errors:
            print(f"FAIL: {e}")
        sys.exit(1)
"""

import sys
from collections import Counter


def validate_all(phase: str | None = None, fail_fast: bool = True) -> list[str]:
    """Executa TODAS as validações e retorna lista de erros.

    Args:
        phase: Fase opcional para filtrar (None = todas).
        fail_fast: Se True, retorna na primeira falha grave.

    Returns:
        Lista de strings de erro. Lista vazia = tudo OK.
    """
    errors: list[str] = []

    # ── 1. Importabilidade ──
    try:
        import server  # noqa: F401
    except Exception as e:
        errors.append(f"FATAL: server.py não importa: {e}")
        return errors

    from server import _tool_defs, _build_handlers
    from core.legacy_data import PHASE_TOOLSETS, PHASE_TOOLS_CORE, PHASE_TOOLS_TOP, TOOLSETS
    from tools.deprecated import DEPRECATED_TOOLS, ALIAS_MAP

    tools = {t.name for t in _tool_defs()}
    handlers = set(_build_handlers().keys())
    all_phased = set(PHASE_TOOLS_CORE)
    for v in PHASE_TOOLSETS.values():
        all_phased |= v
    all_ns = set()
    for v in TOOLSETS.values():
        all_ns.update(v)
    core = PHASE_TOOLS_CORE - DEPRECATED_TOOLS

    # ── 2. Invariantes fundamentais ─────────────────────────────
    # INV-01: SEM_HANDLER
    sem_handler = tools - handlers
    if sem_handler:
        errors.append(f"INV-01: {len(sem_handler)} tools sem handler: {sorted(sem_handler)[:10]}")
        if fail_fast:
            return errors

    # INV-02: SEM_DEF
    sem_def = handlers - tools
    if sem_def:
        errors.append(f"INV-02: {len(sem_def)} handlers sem tool: {sorted(sem_def)[:10]}")
        if fail_fast:
            return errors

    # INV-04: SEM_FASE
    sem_fase = tools - all_phased - DEPRECATED_TOOLS
    if sem_fase:
        errors.append(f"INV-04: {len(sem_fase)} tools sem fase: {sorted(sem_fase)[:10]}")
        if fail_fast:
            return errors

    # INV-10: FANTASMAS em PHASE_TOOLSETS
    fantasmas_fase = all_phased - tools - DEPRECATED_TOOLS
    if fantasmas_fase:
        errors.append(f"INV-10: {len(fantasmas_fase)} fantasmas em fases: {sorted(fantasmas_fase)[:10]}")

    # INV-11: FANTASMAS em TOOLSETS
    fantasmas_ns = all_ns - tools - DEPRECATED_TOOLS
    if fantasmas_ns:
        errors.append(f"INV-11: {len(fantasmas_ns)} fantasmas em namespaces: {sorted(fantasmas_ns)[:10]}")

    # INV-12: COLISOES
    dups = {n: c for n, c in Counter([t.name for t in _tool_defs()]).items() if c > 1}
    if dups:
        errors.append(f"INV-12: {len(dups)} colisões de nome: {list(dups.keys())}")

    # INV-13: COLISAO de registro (agora implementado!)
    # Verifica se há tool registrada em _raw_tool_defs E em rollups
    try:
        from core.tool_definitions import _raw_tool_defs
        raw_names = {t.name for t in _raw_tool_defs()}
        from tools.rollups import get_rollup_tool_defs
        rollup_names = {t.name for t in get_rollup_tool_defs()}
        colisao_registro = raw_names & rollup_names
        if colisao_registro:
            errors.append(
                f"INV-13: {len(colisao_registro)} tools em raw_defs E rollups: "
                f"{sorted(colisao_registro)}"
            )
    except Exception as e:
        errors.append(f"INV-13: erro ao verificar: {e}")

    # ── 3. Gate de teto (G3) — modo lean (default) ────────────
    # Verifica se alguma fase excede o teto em modo lean (o padrão).
    # O modo full (--full) é legado e não é verificado aqui.
    teto_lean = 30
    for p in ["IDEIA", "DESIGN", "PROTOTIPO", "CONTEUDO", "POLIMENTO", "PRONTO_PARA_LANCAR"]:
        top = PHASE_TOOLS_TOP.get(p, set())
        lean = len(((top - DEPRECATED_TOOLS) & tools) | (core & tools))
        if lean > teto_lean:
            errors.append(f"G3-lean: {p} tem {lean} tools (teto: {teto_lean}, +{lean - teto_lean})")

    # ── 4. Rollup-first (aviso, não erro) ───────────────────────
    # Lista tools atômicas fora do top-5. Aviso de oportunidade
    # de colapso, não erro bloqueante.
    try:
        import json
        from pathlib import Path
        qpath = Path("experimental/quarentena.json")
        quarentena = set(json.loads(qpath.read_text(encoding="utf-8"))["tools"]) if qpath.exists() else set()
    except Exception:
        quarentena = set()

    all_top = set()
    for ts in PHASE_TOOLS_TOP.values():
        all_top.update(ts)

    atomicas_fora_top = []
    for t in sorted(tools - DEPRECATED_TOOLS - quarentena):
        if not t.endswith("_manage") and t not in core and t not in all_top:
            if t not in ALIAS_MAP:
                atomicas_fora_top.append(t)

    if len(atomicas_fora_top) > 100:  # Só avisa se MUITAS (baseline atual)
        errors.append(
            f"ROLLUP-FIRST (aviso): {len(atomicas_fora_top)} tools atômicas fora do top-5. "
            f"Sem bloqueio — oportunidade de colapso futuro."
        )

    # ── 5. Consistência ALIAS_MAP ───────────────────────────────
    for alias, (target, op_name) in ALIAS_MAP.items():
        if target not in tools:
            errors.append(f"ALIAS: '{alias}' → '{target}' mas target não existe")
        if target not in rollup_names:
            errors.append(f"ALIAS: '{alias}' → '{target}' mas target não é rollup")

    # ── 6. Consistência TOP tools ───────────────────────────────
    for p, ts in PHASE_TOOLS_TOP.items():
        missing_top = [t for t in ts if t not in tools and t not in DEPRECATED_TOOLS]
        if missing_top:
            errors.append(f"TOP-{p}: {len(missing_top)} tools do top-5 não existem: {missing_top}")

    return errors


if __name__ == "__main__":
    errors = validate_all()
    if errors:
        print(f"❌ {len(errors)} erro(s) encontrado(s):")
        for e in errors:
            print(f"  • {e}")
        sys.exit(1)
    else:
        print("✅ Todas as validações passaram — sistema autogovernante OK")
