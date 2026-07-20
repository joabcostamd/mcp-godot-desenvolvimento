"""
budget_ops.py — Orcamento de tokens por sessao (Fatia 1.D)

Rastreia custo estimado da sessao em reais (BRL), com aviso aos 80%
e teto configuravel. Exposto como rollup budget_manage(op, ...).

Estado: <project_root>/.mcp_budget_state.json (por projeto)
Precos: DeepSeek V4 (~R$0.003/1K input, ~R$0.010/1K output)
"""

from __future__ import annotations

import json
import threading
import time
from pathlib import Path
from typing import Any

# ── Constantes ──────────────────────────────────────────────────────

STATE_FILE = ".mcp_budget_state.json"

# Precificacao estimada (DeepSeek V4, valores aproximados em BRL)
PRICE_INPUT_PER_1K = 0.003   # R$ por 1000 tokens de input
PRICE_OUTPUT_PER_1K = 0.010  # R$ por 1000 tokens de output

# Estimativa: ~4 chars = 1 token (heuristica)
CHARS_PER_TOKEN = 4

# Aviso e teto
WARN_PCT = 80   # % do teto para avisar
DEFAULT_LIMIT_BRL = 5.00  # teto padrao: R$ 5,00

# Tools que NAO contam para o orcamento (gerenciamento)
_BUDGET_EXEMPT_TOOLS = {"budget_manage", "ping", "validate_godot_version"}

# Cache em memoria + lock para evitar I/O excessivo e race conditions
_state_cache: dict | None = None
_state_cache_root: str | None = None
_lock = threading.Lock()


# ── Helpers ─────────────────────────────────────────────────────────

def _get_project_root() -> Path | None:
    """Obtem a raiz do projeto ativo."""
    try:
        from tools.project_ops import _get_active_project
        return _get_active_project()
    except Exception:
        return None


def _load_state() -> dict:
    """Carrega o estado de orcamento do projeto ativo (com cache)."""
    global _state_cache, _state_cache_root
    root = _get_project_root()
    root_str = str(root) if root else None

    # Cache hit: mesmo projeto
    if _state_cache is not None and _state_cache_root == root_str:
        return _state_cache

    # Cache miss: carrega do disco
    if root is None:
        return _default_state()

    state_path = root / STATE_FILE
    if state_path.exists():
        try:
            state = json.loads(state_path.read_text(encoding="utf-8"))
            _state_cache = state
            _state_cache_root = root_str
            return state
        except Exception:
            pass

    state = _default_state()
    _state_cache = state
    _state_cache_root = root_str
    return state


def _save_state(state: dict) -> None:
    """Salva o estado de orcamento no disco (thread-safe)."""
    global _state_cache
    _state_cache = state  # atualiza cache
    root = _get_project_root()
    if root is None:
        return
    state_path = root / STATE_FILE
    with _lock:
        state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")


def _default_state() -> dict:
    return {
        "session_tokens_input": 0,
        "session_tokens_output": 0,
        "limit_brl": DEFAULT_LIMIT_BRL,
        "session_cost_brl": 0.0,
        "warnings_sent": 0,
        "started_at": time.time(),
    }


def _estimate_tokens(text: str) -> int:
    """Estima numero de tokens a partir de texto (~4 chars/token)."""
    if not text:
        return 0
    return max(1, len(text) // CHARS_PER_TOKEN)


# ── API publica: budget_manage ─────────────────────────────────────

def budget_manage(
    op: str = "status",
    limit_brl: float = 0,
    force: bool = False,
) -> dict:
    """Gerencia o orcamento de tokens da sessao.

    Args:
        op: "status" (ver custo), "set_limit" (definir teto), "reset" (zerar).
        limit_brl: Valor do teto em reais (para op="set_limit").
        force: Se True, ignora confirmacao para aumentar teto.

    Returns:
        dict com status da operacao.
    """
    state = _load_state()

    if op == "status":
        pct = (state["session_cost_brl"] / state["limit_brl"] * 100) if state["limit_brl"] > 0 else 0
        return {
            "status": "success",
            "session_cost_brl": round(state["session_cost_brl"], 4),
            "session_tokens_input": state["session_tokens_input"],
            "session_tokens_output": state["session_tokens_output"],
            "limit_brl": state["limit_brl"],
            "pct_used": round(pct, 1),
            "warn_at_80": pct >= WARN_PCT,
            "blocked": pct >= 100,
            "note": "Valores sao estimativas. Custo real pode variar.",
        }

    elif op == "set_limit":
        if limit_brl <= 0:
            return {"status": "error", "message": "limit_brl deve ser > 0."}
        old = state["limit_brl"]
        state["limit_brl"] = limit_brl
        _save_state(state)
        return {
            "status": "success",
            "limit_brl": limit_brl,
            "previous_limit_brl": old,
            "message": f"Teto alterado de R$ {old:.2f} para R$ {limit_brl:.2f}.",
        }

    elif op == "reset":
        state = _default_state()
        _save_state(state)
        return {
            "status": "success",
            "message": "Orcamento da sessao zerado.",
            "limit_brl": state["limit_brl"],
        }

    else:
        return {"status": "error", "message": f"Operacao desconhecida: {op}. Use status, set_limit ou reset."}


# ── Hook para call_tool ────────────────────────────────────────────

def track_tool_cost(tool_name: str, arguments: dict, result: dict) -> dict | None:
    """Hook chamado apos cada execucao de tool para rastrear custo.

    Args:
        tool_name: Nome da tool executada.
        arguments: Argumentos da tool (para estimar input tokens).
        result: Resultado da tool (para estimar output tokens).

    Returns:
        None se abaixo do teto, ou dict de erro se teto estourou.
    """
    # Tools de gerenciamento nunca contam para o orcamento (evita deadlock)
    if tool_name in _BUDGET_EXEMPT_TOOLS:
        return None

    try:
        state = _load_state()

        # Estima tokens de input (argumentos serializados)
        input_text = json.dumps(arguments, ensure_ascii=False) if arguments else ""
        input_tokens = _estimate_tokens(input_text)

        # Estima tokens de output (resposta serializada)
        output_text = json.dumps(result, ensure_ascii=False) if result else ""
        output_tokens = _estimate_tokens(output_text)

        # Acumula
        state["session_tokens_input"] += input_tokens
        state["session_tokens_output"] += output_tokens

        # Calcula custo
        cost_input = (input_tokens / 1000) * PRICE_INPUT_PER_1K
        cost_output = (output_tokens / 1000) * PRICE_OUTPUT_PER_1K
        state["session_cost_brl"] += cost_input + cost_output

        # Verifica teto
        pct = (state["session_cost_brl"] / state["limit_brl"] * 100) if state["limit_brl"] > 0 else 0

        blocked = False
        if pct >= 100:
            blocked = True
            state["warnings_sent"] += 1
        elif pct >= WARN_PCT and state["warnings_sent"] == 0:
            state["warnings_sent"] += 1

        _save_state(state)

        if blocked:
            return {
                "budget_exceeded": True,
                "session_cost_brl": round(state["session_cost_brl"], 4),
                "limit_brl": state["limit_brl"],
                "pct_used": round(pct, 1),
                "message": (
                    f"Teto de orcamento atingido: R$ {state['limit_brl']:.2f}. "
                    f"Gasto: R$ {state['session_cost_brl']:.2f}. "
                    f"Use budget_manage op=set_limit para aumentar o teto."
                ),
            }

        return None  # abaixo do teto

    except Exception:
        return None  # fail-open: nunca bloqueia por erro de tracking


# ── Self-test ───────────────────────────────────────────────────────

if __name__ == "__main__":
    # Testa estimativa de tokens
    assert _estimate_tokens("hello world") == 2  # 11 chars / 4 = 2
    assert _estimate_tokens("") == 0
    assert _estimate_tokens("a") == 1  # max(1, 0) = 1

    # Testa status
    r = budget_manage("status")
    assert r["status"] == "success"
    assert "session_cost_brl" in r
    assert "pct_used" in r

    # Testa set_limit
    r = budget_manage("set_limit", limit_brl=10.0)
    assert r["status"] == "success"
    assert r["limit_brl"] == 10.0

    # Restaura default
    budget_manage("set_limit", limit_brl=DEFAULT_LIMIT_BRL)
    budget_manage("reset")

    print("OK — budget_ops self-test passou")
