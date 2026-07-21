"""reviewer_ops.py — Modo revisor adversarial (Fatia 3.K).

Rollup reviewer_manage(op=enable|disable|status).
Ativa/desativa modo onde o agente audita em vez de implementar.
Ataca o problema numero um: evidencia fabricada com confianca.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _get_state_file() -> Path:
    from tools.project_ops import _get_active_project
    return _get_active_project() / ".mcp_reviewer_mode.json"


def _load_state() -> dict:
    path = _get_state_file()
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"enabled": False, "activated_at": None, "reason": ""}


def _save_state(data: dict) -> None:
    _get_state_file().write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def _op_enable(params: dict) -> dict:
    """Ativa o modo revisor adversarial.

    Nesse modo, o agente NAO implementa — ele audita, tenta quebrar,
    e verifica se as provas correspondem ao codigo real.
    """
    reason = params.get("reason", "Auditoria solicitada")
    state = {
        "enabled": True,
        "activated_at": __import__("datetime").datetime.now().isoformat(),
        "reason": reason,
    }
    _save_state(state)
    return {
        "status": "success",
        "mode": "reviewer",
        "message": (
            "🔍 Modo revisor ATIVADO. O agente agora audita em vez de implementar. "
            "Use reviewer_manage op=disable para voltar ao modo normal."
        ),
        "rules": [
            "Nao escreva codigo — apenas audite.",
            "Rode auditar.py de forma independente.",
            "Tente QUEBRAR a implementacao, nao confirma-la.",
            "Verifique se as provas coladas correspondem ao codigo real.",
            "Custa metade da velocidade, ataca o problema numero um.",
        ],
    }


def _op_disable(params: dict) -> dict:  # noqa: ARG001
    _save_state({"enabled": False, "activated_at": None, "reason": ""})
    return {"status": "success", "mode": "normal", "message": "Modo revisor DESATIVADO. Implementacao liberada."}


def _op_status(params: dict) -> dict:  # noqa: ARG001
    state = _load_state()
    return {
        "status": "success",
        "enabled": state.get("enabled", False),
        "activated_at": state.get("activated_at"),
        "reason": state.get("reason", ""),
        "message": (
            "🔍 Modo revisor ATIVO — auditoria em andamento."
            if state.get("enabled") else
            "✅ Modo normal — implementacao liberada."
        ),
    }


_REVIEWER_OPS = {"enable": _op_enable, "disable": _op_disable, "status": _op_status}


def reviewer_manage(op: str, params: dict | None = None) -> dict:
    if op not in _REVIEWER_OPS:
        return {"status": "error", "message": f"Operacao '{op}' desconhecida.", "available_ops": list(_REVIEWER_OPS.keys())}
    return _REVIEWER_OPS[op](params or {})
