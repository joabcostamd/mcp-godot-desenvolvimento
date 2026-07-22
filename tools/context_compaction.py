"""context_compaction.py — Compactacao Automatica de Contexto (FATIA 2.AQ).

Mantem um resumo rolante do historico da sessao para evitar
degradacao em projetos longos (mais de um mes de desenvolvimento).

Estrategia:
  - Resumo progressivo: cada novo evento e incorporado
  - Janela deslizante: mantem os N eventos mais recentes
  - Compressao: eventos antigos sao resumidos em paragrafos
  - Token budget: estima tokens e alerta quando passar do limite

Fonte: Pesquisa em tecnicas de summarization (TextRank, 2004)
e sliding window context management.
"""

import json
import time
from collections import deque
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
CONTEXT_FILE = ROOT / ".mcp_context_log.json"

# Configuracoes
MAX_DETAIL_EVENTS = 50     # Eventos mantidos em detalhe
MAX_SUMMARY_AGE = 10        # Eventos com mais de N ciclos viram resumo
TOKEN_BUDGET = 8000         # Alerta quando estimativa passar disso
CHARS_PER_TOKEN = 4         # Estimativa grosseira


def log_event(event_type: str, description: str, tool_name: str = "", tokens_used: int = 0) -> dict:
    """Registra um evento no log de contexto.

    Args:
        event_type: Tipo do evento ('tool_call', 'error', 'decision', 'phase_change').
        description: Descricao curta do evento.
        tool_name: Nome da tool (se aplicavel).
        tokens_used: Tokens estimados consumidos.

    Returns:
        dict com status e alertas.
    """
    context = _load_context()

    event = {
        "type": event_type,
        "description": description,
        "tool": tool_name,
        "tokens": tokens_used,
        "timestamp": time.time(),
    }

    context["events"].append(event)
    context["total_events"] += 1
    context["total_tokens"] += tokens_used

    # Compacta eventos antigos
    _compact(context)

    _save_context(context)

    alerts = []
    if context["total_tokens"] > TOKEN_BUDGET:
        alerts.append(f"ATENCAO: {context['total_tokens']} tokens estimados — acima do orcamento de {TOKEN_BUDGET}.")

    return {
        "status": "logged",
        "total_events": context["total_events"],
        "estimated_tokens": context["total_tokens"],
        "token_budget": TOKEN_BUDGET,
        "alerts": alerts,
    }


def get_context_summary() -> dict:
    """Retorna o resumo do contexto atual.

    Returns:
        dict com resumo, eventos recentes e metricas.
    """
    context = _load_context()

    recent = context["events"][-MAX_DETAIL_EVENTS:]
    summary = context.get("summary", "")

    return {
        "status": "success",
        "summary": summary,
        "recent_events": [
            {
                "type": e["type"],
                "description": e["description"][:120],
                "tool": e.get("tool", ""),
            }
            for e in recent[-10:]  # ultimos 10
        ],
        "metrics": {
            "total_events": context["total_events"],
            "estimated_tokens": context["total_tokens"],
            "token_budget": TOKEN_BUDGET,
            "usage_pct": round(context["total_tokens"] / TOKEN_BUDGET * 100, 1),
        },
    }


def estimate_tokens(text: str) -> int:
    """Estima numero de tokens em um texto (aproximacao)."""
    return len(text) // CHARS_PER_TOKEN


def _compact(context: dict) -> None:
    """Compacta eventos antigos em resumo."""
    events = context["events"]
    if len(events) <= MAX_DETAIL_EVENTS:
        return

    # Pega eventos antigos (fora da janela)
    old_events = events[:-MAX_DETAIL_EVENTS]
    recent = events[-MAX_DETAIL_EVENTS:]

    # Gera resumo dos antigos
    summaries = []
    for e in old_events[-MAX_SUMMARY_AGE:]:
        summaries.append(f"- [{e['type']}] {e['description'][:100]}")

    context["summary"] = (
        f"Sessao com {context['total_events']} eventos. "
        + "Ultimas acoes resumidas:\n"
        + "\n".join(summaries)
    )
    context["events"] = recent


def _load_context() -> dict:
    if CONTEXT_FILE.exists():
        try:
            return json.loads(CONTEXT_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {"events": [], "total_events": 0, "total_tokens": 0, "summary": ""}


def _save_context(data: dict) -> None:
    CONTEXT_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
