"""workflow_ops.py — AI Workflow Log (Fase 2C / M8).

Diário de bordo automático para IA agêntica. Resolve o problema de
"IA esquece o que fez entre chamadas". Inspirado no Gear (wvfp).

Tools:
    - workflow_snapshot: salva estado atual do projeto
    - workflow_log_decision: registra uma decisão da IA
    - workflow_summary: resume tudo que foi feito
    - workflow_handoff: prepara resumo para próxima sessão
"""

import json
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WORKFLOW_DIR = ROOT / "workflow_logs"
MAX_LOG_FILES = 50


def _ensure_dir():
    WORKFLOW_DIR.mkdir(parents=True, exist_ok=True)
    # Rotação: remove logs mais antigos se excedeu limite
    log_files = sorted(WORKFLOW_DIR.glob('*.json'), key=lambda p: p.stat().st_mtime)
    while len(log_files) > MAX_LOG_FILES:
        log_files[0].unlink()
        log_files.pop(0)


def _session_id() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def _log_file(session_id: str) -> Path:
    return WORKFLOW_DIR / f"session_{session_id}.json"


# ── Snapshot ────────────────────────────────────────────────────────

def workflow_snapshot(description: str = "", project_path: str | None = None) -> dict:
    """Salva um snapshot do estado atual do projeto.

    Args:
        description: Descrição do momento (ex: "Antes de refatorar movimento").
        project_path: Caminho do projeto (auto-detecta se None).

    Returns:
        dict com ID da sessão e caminho do log.
    """
    _ensure_dir()
    sid = _session_id()

    # Detecta projeto
    if not project_path:
        try:
            from tools.project_ops import get_project_settings
            settings = get_project_settings()
            project_path = settings.get("project_path", "desconhecido")
        except Exception:
            project_path = "desconhecido"

    snapshot = {
        "session_id": sid,
        "timestamp": datetime.now().isoformat(),
        "type": "snapshot",
        "description": description,
        "project": project_path,
        "tool_count": _get_tool_count(),
    }

    _write_log(sid, snapshot)
    return {
        "status": "success",
        "session_id": sid,
        "snapshot": snapshot,
        "log_file": str(_log_file(sid)),
    }


# ── Decision Log ────────────────────────────────────────────────────

def workflow_log_decision(
    decision: str,
    context: str = "",
    alternatives: list[str] | None = None,
    session_id: str | None = None,
) -> dict:
    """Registra uma decisão da IA no log de workflow.

    Args:
        decision: A decisão tomada.
        context: Contexto que levou à decisão.
        alternatives: Alternativas consideradas.
        session_id: ID da sessão (usa a mais recente se None).

    Returns:
        dict com confirmação.
    """
    _ensure_dir()
    sid = session_id or _get_latest_session()

    entry = {
        "session_id": sid,
        "timestamp": datetime.now().isoformat(),
        "type": "decision",
        "decision": decision,
        "context": context,
        "alternatives": alternatives or [],
    }

    _write_log(sid, entry)
    return {"status": "success", "session_id": sid, "decision": decision}


# ── Summary ─────────────────────────────────────────────────────────

def workflow_summary(session_id: str | None = None) -> dict:
    """Gera um resumo de tudo que foi feito na sessão.

    Args:
        session_id: ID da sessão. Se None, usa a mais recente.

    Returns:
        dict com resumo estruturado.
    """
    _ensure_dir()
    sid = session_id or _get_latest_session()
    entries = _read_log(sid)

    if not entries:
        return {"status": "error", "message": f"Nenhum log encontrado para sessão {sid}"}

    snapshots = [e for e in entries if e.get("type") == "snapshot"]
    decisions = [e for e in entries if e.get("type") == "decision"]
    actions = [e for e in entries if e.get("type") == "action"]

    return {
        "status": "success",
        "session_id": sid,
        "summary": {
            "started_at": snapshots[0]["timestamp"] if snapshots else "desconhecido",
            "total_decisions": len(decisions),
            "total_actions": len(actions),
            "total_entries": len(entries),
            "key_decisions": [d["decision"] for d in decisions[-5:]],
            "project": snapshots[0].get("project", "desconhecido") if snapshots else "desconhecido",
        },
        "entries": entries,
    }


# ── Handoff ─────────────────────────────────────────────────────────

def workflow_handoff(
    next_steps: list[str] | None = None,
    notes: str = "",
    session_id: str | None = None,
) -> dict:
    """Prepara resumo de handoff para a próxima sessão.

    Use no FINAL de cada sessão. Gera um arquivo que a IA da
    próxima sessão pode ler para retomar o contexto.

    Args:
        next_steps: Lista de próximos passos.
        notes: Notas adicionais.
        session_id: ID da sessão.

    Returns:
        dict com resumo de handoff.
    """
    _ensure_dir()
    sid = session_id or _get_latest_session()

    # Gera resumo primeiro
    summary = workflow_summary(sid)

    handoff = {
        "session_id": sid,
        "timestamp": datetime.now().isoformat(),
        "type": "handoff",
        "summary": summary.get("summary", {}),
        "next_steps": next_steps or [],
        "notes": notes,
    }

    # Salva como arquivo separado para fácil leitura
    handoff_file = WORKFLOW_DIR / "NEXT_SESSION.json"
    with open(handoff_file, "w", encoding="utf-8") as f:
        json.dump(handoff, f, indent=2, ensure_ascii=False)

    _write_log(sid, handoff)

    return {
        "status": "success",
        "session_id": sid,
        "handoff": handoff,
        "handoff_file": str(handoff_file),
    }


# ── Action Log ──────────────────────────────────────────────────────

def workflow_log_action(
    action: str,
    tool_used: str = "",
    result: str = "success",
    details: str = "",
    session_id: str | None = None,
) -> dict:
    """Registra uma ação executada pela IA.

    Args:
        action: Descrição da ação.
        tool_used: Tool MCP utilizada.
        result: "success" ou "error".
        details: Detalhes adicionais.
        session_id: ID da sessão.
    """
    _ensure_dir()
    sid = session_id or _get_latest_session()

    entry = {
        "session_id": sid,
        "timestamp": datetime.now().isoformat(),
        "type": "action",
        "action": action,
        "tool": tool_used,
        "result": result,
        "details": details,
    }

    _write_log(sid, entry)
    return {"status": "success", "session_id": sid}


# ── Helpers ─────────────────────────────────────────────────────────

def _get_tool_count() -> int:
    try:
        from server import _tool_defs
        return len(_tool_defs())
    except Exception:
        return 0


def _get_latest_session() -> str:
    """Encontra a sessão mais recente."""
    _ensure_dir()
    files = sorted(WORKFLOW_DIR.glob("session_*.json"), reverse=True)
    if files:
        return files[0].stem.replace("session_", "")
    return _session_id()


def _write_log(session_id: str, entry: dict) -> None:
    """Adiciona entrada ao arquivo de log da sessão."""
    entries = _read_log(session_id)
    entries.append(entry)
    with open(_log_file(session_id), "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2, ensure_ascii=False)


def _read_log(session_id: str) -> list[dict]:
    """Lê todas as entradas do log da sessão."""
    log_file = _log_file(session_id)
    if log_file.exists():
        with open(log_file, encoding="utf-8") as f:
            return json.load(f)
    return []
