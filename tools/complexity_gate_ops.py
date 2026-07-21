"""complexity_gate_ops.py — Gate de divida de complexidade (Fatia 3.F).

Rollup complexity_gate_manage(op=baseline|check).
Mede scripts .gd, linhas de codigo e warnings por fase.
Bloqueia avanco se complexidade crescer sem justificativa.

Estado por projeto: <project>/.mcp_complexity_gate.json
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

STATE_FILE = ".mcp_complexity_gate.json"

# Thresholds
WARN_SCRIPTS_PCT = 0.20   # +20% scripts = warn
BLOCK_SCRIPTS_PCT = 0.50  # +50% scripts = block
WARN_LINES_PCT = 0.30     # +30% lines = warn
BLOCK_LINES_PCT = 0.60    # +60% lines = block


def _get_active_project() -> Path:
    from tools.project_ops import _get_active_project as _gap
    return _gap()


def _count_metrics(project: Path) -> dict:
    """Conta scripts .gd e linhas de codigo no projeto."""
    scripts = list(project.rglob("*.gd"))
    total_lines = 0
    for s in scripts:
        try:
            total_lines += len(s.read_text(encoding="utf-8", errors="replace").splitlines())
        except Exception:
            pass

    return {
        "scripts_count": len(scripts),
        "total_lines": total_lines,
        "timestamp": __import__("datetime").datetime.now().isoformat(),
    }


def _load_state(project: Path) -> dict:
    path = project / STATE_FILE
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def _save_state(project: Path, data: dict) -> None:
    path = project / STATE_FILE
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def _op_baseline(params: dict) -> dict:  # noqa: ARG001
    """Salva o snapshot atual de complexidade como baseline da fase."""
    project = _get_active_project()
    metrics = _count_metrics(project)
    _save_state(project, {"baseline": metrics, "phase": "current"})
    return {
        "status": "success",
        "message": f"Baseline salva: {metrics['scripts_count']} scripts, {metrics['total_lines']} linhas.",
        "baseline": metrics,
    }


def _op_check(params: dict) -> dict:  # noqa: ARG001
    """Compara complexidade atual com a baseline e retorna diagnostico."""
    project = _get_active_project()
    state = _load_state(project)
    baseline = state.get("baseline")

    if not baseline:
        return {
            "status": "error",
            "message": "Nenhuma baseline encontrada. Rode complexity_gate_manage op=baseline primeiro.",
        }

    current = _count_metrics(project)

    scripts_delta = current["scripts_count"] - baseline["scripts_count"]
    scripts_pct = scripts_delta / max(baseline["scripts_count"], 1)

    lines_delta = current["total_lines"] - baseline["total_lines"]
    lines_pct = lines_delta / max(baseline["total_lines"], 1)

    warnings = []
    status = "pass"

    if scripts_pct >= BLOCK_SCRIPTS_PCT or lines_pct >= BLOCK_LINES_PCT:
        status = "block"
        if scripts_pct >= BLOCK_SCRIPTS_PCT:
            warnings.append(
                f"Scripts cresceram {scripts_pct:.0%} "
                f"({baseline['scripts_count']} → {current['scripts_count']}). "
                f"Limite de bloqueio: {BLOCK_SCRIPTS_PCT:.0%}."
            )
        if lines_pct >= BLOCK_LINES_PCT:
            warnings.append(
                f"Linhas cresceram {lines_pct:.0%} "
                f"({baseline['total_lines']} → {current['total_lines']}). "
                f"Limite de bloqueio: {BLOCK_LINES_PCT:.0%}."
            )
    elif scripts_pct >= WARN_SCRIPTS_PCT or lines_pct >= WARN_LINES_PCT:
        status = "warn"

    script_note = f"Scripts: {baseline['scripts_count']} → {current['scripts_count']} ({scripts_pct:+.0%})"
    lines_note = f"Linhas: {baseline['total_lines']} → {current['total_lines']} ({lines_pct:+.0%})"

    return {
        "status": status,
        "current": current,
        "baseline": baseline,
        "deltas": {
            "scripts": scripts_delta,
            "scripts_pct": round(scripts_pct, 2),
            "lines": lines_delta,
            "lines_pct": round(lines_pct, 2),
        },
        "warnings": warnings,
        "message": f"{script_note} | {lines_note}" + (f" | {len(warnings)} alerta(s)" if warnings else ""),
    }


_COMPLEXITY_OPS = {"baseline": _op_baseline, "check": _op_check}


def complexity_gate_manage(op: str, params: dict | None = None) -> dict:
    if op not in _COMPLEXITY_OPS:
        from difflib import get_close_matches
        suggestions = get_close_matches(op, list(_COMPLEXITY_OPS.keys()), n=3)
        return {"status": "error", "message": f"Operacao '{op}' desconhecida.", "available_ops": list(_COMPLEXITY_OPS.keys()), "suggestions": suggestions}
    return _COMPLEXITY_OPS[op](params or {})
