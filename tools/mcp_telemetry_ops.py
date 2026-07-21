"""
mcp_telemetry_ops.py — Telemetria opt-in do proprio MCP (Fatia 1.P)

Rastreia uso do MCP como ferramenta: quais tools sao chamadas, em qual fase,
quanto tempo levam, quais falham. Telemetria 100% local, consentimento
explicito, NUNCA ligado por padrao.

DIFERENTE de telemetry_ops.py (Fatia 5.4) que e telemetria DE JOGO
(eventos do jogador: level_start, enemy_kill, etc.).

Estado:
  .mcp_telemetry_consent.json  — consentimento (por projeto)
  .mcp_telemetry_events.jsonl  — eventos (JSON Lines, append-only)
  .mcp_telemetry_summary.json  — agregados da sessao atual
"""

from __future__ import annotations

import json
import threading
import time
import uuid
from pathlib import Path
from typing import Any

# ── Constantes ──────────────────────────────────────────────────────

CONSENT_FILE = ".mcp_telemetry_consent.json"
EVENTS_FILE = ".mcp_telemetry_events.jsonl"
SUMMARY_FILE = ".mcp_telemetry_summary.json"

# Eventos validos de telemetria do MCP
_TELEMETRY_EVENT_TYPES = {
    "tool_call",
    "session_start",
    "phase_transition",
    "error",
}

# Tools que NAO entram na telemetria (gerenciamento, telemetria dela mesma)
_TELEMETRY_EXEMPT_TOOLS = {
    "mcp_telemetry_manage",
    "budget_manage",
    "ping",
    "validate_godot_version",
}

# Cache em memoria + lock para evitar I/O excessivo e race conditions
_consent_cache: dict | None = None
_consent_cache_root: str | None = None
_session_id: str | None = None
_lock = threading.Lock()

# Versao do MCP (lida do server.py ou fallback)
_MCP_VERSION = "3.5.0"


# ── Helpers ─────────────────────────────────────────────────────────

def _get_project_root() -> Path | None:
    """Obtem a raiz do projeto ativo."""
    try:
        from tools.project_ops import _get_active_project
        return _get_active_project()
    except Exception:
        return None


def _load_consent() -> dict:
    """Carrega o estado de consentimento do projeto ativo (com cache)."""
    global _consent_cache, _consent_cache_root
    root = _get_project_root()
    root_str = str(root) if root else None

    if _consent_cache is not None and _consent_cache_root == root_str:
        return _consent_cache

    default = {"consent": False, "consent_date": None, "session_id": None}
    if root is None:
        return default

    consent_path = root / CONSENT_FILE
    if consent_path.exists():
        try:
            state = json.loads(consent_path.read_text(encoding="utf-8"))
            _consent_cache = state
            _consent_cache_root = root_str
            return state
        except Exception:
            pass

    _consent_cache = default
    _consent_cache_root = root_str
    return default


def _save_consent(state: dict) -> None:
    """Salva o estado de consentimento no disco (thread-safe)."""
    global _consent_cache, _consent_cache_root
    _consent_cache = state
    root = _get_project_root()
    if root is None:
        return
    consent_path = root / CONSENT_FILE
    with _lock:
        consent_path.write_text(
            json.dumps(state, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )


def _get_session_id() -> str:
    """Obtem ou gera o ID da sessao atual."""
    global _session_id
    if _session_id is None:
        consent = _load_consent()
        _session_id = consent.get("session_id") or uuid.uuid4().hex[:12]
    return _session_id


def _is_consented() -> bool:
    """Verifica se o usuario consentiu com a telemetria."""
    consent = _load_consent()
    return consent.get("consent", False) is True


def _append_event(event: dict) -> None:
    """Adiciona um evento ao arquivo JSONL (append-only, thread-safe)."""
    root = _get_project_root()
    if root is None:
        return
    events_path = root / EVENTS_FILE
    line = json.dumps(event, ensure_ascii=False, separators=(",", ":"))
    with _lock:
        try:
            with open(events_path, "a", encoding="utf-8") as f:
                f.write(line + "\n")
        except Exception:
            pass  # fail-open: telemetria nunca bloqueia


def _update_summary(event: dict) -> None:
    """Atualiza o resumo agregado da sessao (thread-safe)."""
    root = _get_project_root()
    if root is None:
        return
    summary_path = root / SUMMARY_FILE

    with _lock:
        try:
            if summary_path.exists():
                summary = json.loads(summary_path.read_text(encoding="utf-8"))
            else:
                summary = _default_summary()

            summary["total_events"] += 1

            et = event.get("event_type", "")
            if et == "tool_call":
                summary["total_tool_calls"] += 1
                if event.get("is_error"):
                    summary["total_errors"] += 1
                    tool = event.get("tool_name", "unknown")
                    summary["errors_by_tool"][tool] = summary["errors_by_tool"].get(tool, 0) + 1
                summary["tools_called"][event.get("tool_name", "unknown")] = \
                    summary["tools_called"].get(event.get("tool_name", "unknown"), 0) + 1
                dur = event.get("duration_ms", 0)
                if dur > 0:
                    summary["total_duration_ms"] += dur
            elif et == "phase_transition":
                summary["phase_transitions"] += 1
            elif et == "session_start":
                summary["sessions_started"] += 1

            summary_path.write_text(
                json.dumps(summary, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
        except Exception:
            pass  # fail-open


def _default_summary() -> dict:
    return {
        "total_events": 0,
        "total_tool_calls": 0,
        "total_errors": 0,
        "total_duration_ms": 0,
        "sessions_started": 0,
        "phase_transitions": 0,
        "tools_called": {},
        "errors_by_tool": {},
        "started_at": time.time(),
    }


# ── API publica: mcp_telemetry_manage ─────────────────────────────

def mcp_telemetry_manage(
    op: str = "status",
) -> dict:
    """Gerencia a telemetria opt-in do MCP.

    Args:
        op: "status" (ver estado), "enable" (ativar consentimento),
            "disable" (desativar), "export" (gerar JSON agregado),
            "reset" (apagar todos os dados).

    Returns:
        dict com status da operacao.
    """
    global _session_id, _consent_cache, _consent_cache_root

    if op == "status":
        consent = _load_consent()
        root = _get_project_root()
        events_count = 0
        summary = _default_summary()
        if root:
            events_path = root / EVENTS_FILE
            if events_path.exists():
                try:
                    events_count = sum(1 for _ in open(events_path, "r", encoding="utf-8"))
                except Exception:
                    pass
            summary_path = root / SUMMARY_FILE
            if summary_path.exists():
                try:
                    summary = json.loads(summary_path.read_text(encoding="utf-8"))
                except Exception:
                    pass

        session_duration = time.time() - summary.get("started_at", time.time())

        return {
            "status": "success",
            "enabled": consent.get("consent", False),
            "consent_date": consent.get("consent_date"),
            "total_events": events_count,
            "total_tool_calls": summary.get("total_tool_calls", 0),
            "total_errors": summary.get("total_errors", 0),
            "total_duration_ms": summary.get("total_duration_ms", 0),
            "session_duration_s": round(session_duration, 1),
            "tools_called": summary.get("tools_called", {}),
            "errors_by_tool": summary.get("errors_by_tool", {}),
            "message": (
                "Telemetria esta LIGADA. Dados ficam no arquivo .mcp_telemetry_events.jsonl "
                "do projeto. Nada sai da sua maquina."
                if consent.get("consent")
                else "Telemetria esta DESLIGADA. Use op=enable para ativar."
            ),
        }

    elif op == "enable":
        import datetime
        state = {
            "consent": True,
            "consent_date": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "session_id": uuid.uuid4().hex[:12],
        }
        _save_consent(state)
        _session_id = state["session_id"]
        # Registra evento de sinalizacao (nao conta como sessao real)
        _append_event({
            "event_type": "session_start",
            "timestamp": state["consent_date"],
            "session_id": state["session_id"],
            "mcp_version": _MCP_VERSION,
        })
        return {
            "status": "success",
            "message": (
                "Telemetria ATIVADA. Dados serao salvos em .mcp_telemetry_events.jsonl "
                "no seu projeto. NADA sai da sua maquina. Use op=export para gerar "
                "um relatorio que voce pode compartilhar manualmente."
            ),
            "consent_date": state["consent_date"],
        }

    elif op == "disable":
        state = {"consent": False, "consent_date": None, "session_id": None}
        _save_consent(state)
        _session_id = None
        return {
            "status": "success",
            "message": (
                "Telemetria DESATIVADA. Nenhum dado novo sera coletado. "
                "Dados existentes foram preservados. Use op=reset para apaga-los."
            ),
        }

    elif op == "export":
        root = _get_project_root()
        if root is None:
            return {"status": "error", "message": "Nenhum projeto ativo."}

        events_path = root / EVENTS_FILE
        summary_path = root / SUMMARY_FILE
        export_path = root / "telemetry_export.json"

        events = []
        if events_path.exists():
            try:
                with open(events_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            events.append(json.loads(line))
            except Exception:
                pass

        summary = {}
        if summary_path.exists():
            try:
                summary = json.loads(summary_path.read_text(encoding="utf-8"))
            except Exception:
                pass

        export_data = {
            "exported_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "mcp_version": _MCP_VERSION,
            "total_events": len(events),
            "summary": summary,
            "events": events,
        }

        export_path.write_text(
            json.dumps(export_data, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        return {
            "status": "success",
            "export_path": str(export_path),
            "total_events": len(events),
            "message": (
                f"Relatorio exportado: {export_path}. "
                f"Contem {len(events)} eventos. "
                "NENHUM dado sai da sua maquina automaticamente — "
                "voce decide se quer compartilhar este arquivo."
            ),
        }

    elif op == "reset":
        root = _get_project_root()
        if root is None:
            return {"status": "error", "message": "Nenhum projeto ativo."}

        events_path = root / EVENTS_FILE
        summary_path = root / SUMMARY_FILE
        consent_path = root / CONSENT_FILE

        deleted = []
        for p in [events_path, summary_path, consent_path]:
            if p.exists():
                p.unlink()
                deleted.append(str(p.name))

        # Reset cache
        _consent_cache = None
        _consent_cache_root = None
        _session_id = None

        return {
            "status": "success",
            "message": (
                f"Todos os dados de telemetria foram APAGADOS: {', '.join(deleted)}. "
                "Consentimento tambem foi removido."
            ),
        }

    else:
        return {
            "status": "error",
            "message": f"Operacao desconhecida: {op}. Use status, enable, disable, export ou reset.",
        }


# ── Hook para call_tool ────────────────────────────────────────────

def track_mcp_event(
    tool_name: str,
    arguments: dict | None,
    result: dict | None,
    duration_ms: int = 0,
    phase: str = "",
) -> None:
    """Hook chamado apos cada execucao de tool para telemetria.

    Args:
        tool_name: Nome da tool executada.
        arguments: Argumentos da tool (NAO sao armazenados).
        result: Resultado da tool (NAO e armazenado, so verificamos isError).
        duration_ms: Duracao da execucao em milissegundos.
        phase: Fase atual do projeto.

    Returns:
        None sempre. Fail-open: telemetria nunca bloqueia.
    """
    # Tools de gerenciamento nunca entram na telemetria
    if tool_name in _TELEMETRY_EXEMPT_TOOLS:
        return

    # Verifica consentimento
    if not _is_consented():
        return

    try:
        is_error = False
        error_code = None
        if isinstance(result, dict):
            is_error = result.get("status") == "error"
            if is_error:
                error_code = result.get("error_code")

        event = {
            "event_type": "tool_call",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "session_id": _get_session_id(),
            "tool_name": tool_name,
            "phase": phase or "unknown",
            "duration_ms": duration_ms,
            "is_error": is_error,
            "error_code": error_code,
            "mcp_version": _MCP_VERSION,
        }

        _append_event(event)
        _update_summary(event)

    except Exception:
        pass  # fail-open: nunca bloqueia por erro de tracking


def track_phase_transition(from_phase: str, to_phase: str) -> None:
    """Registra transicao de fase na telemetria (se consentido).

    Args:
        from_phase: Fase anterior.
        to_phase: Nova fase.
    """
    if not _is_consented():
        return

    try:
        event = {
            "event_type": "phase_transition",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "session_id": _get_session_id(),
            "from_phase": from_phase,
            "to_phase": to_phase,
            "mcp_version": _MCP_VERSION,
        }
        _append_event(event)
        _update_summary(event)
    except Exception:
        pass


# ── Self-test ───────────────────────────────────────────────────────

if __name__ == "__main__":
    import tempfile
    import os

    # Cria projeto temporario para teste de escrita
    tmpdir = tempfile.mkdtemp(prefix="mcp_telemetry_test_")
    project_root_file = os.path.join(tmpdir, "project.godot")
    with open(project_root_file, "w") as f:
        f.write("")

    # Mock _get_active_project para retornar o tempdir
    original_get_active = None
    try:
        from tools.project_ops import _get_active_project
        original_get_active = _get_active_project
    except Exception:
        pass

    # Monkey-patch: faz _get_active_project retornar o tempdir
    import tools.project_ops as po
    po._get_active_project = lambda: Path(tmpdir)

    try:
        # Testa status com telemetria desligada
        r = mcp_telemetry_manage("status")
        print("STATUS (desligado):", json.dumps(r, indent=2, ensure_ascii=False))
        assert r["status"] == "success"
        assert r["enabled"] is False

        # Testa enable
        r = mcp_telemetry_manage("enable")
        print("ENABLE:", json.dumps(r, indent=2, ensure_ascii=False))
        assert r["status"] == "success"

        # Testa status apos enable
        r = mcp_telemetry_manage("status")
        print("STATUS (ligado):", json.dumps(r, indent=2, ensure_ascii=False))
        assert r["enabled"] is True

        # Testa disable
        r = mcp_telemetry_manage("disable")
        print("DISABLE:", json.dumps(r, indent=2, ensure_ascii=False))
        assert r["status"] == "success"

        # Testa export (sem eventos ainda, mas deve funcionar)
        r = mcp_telemetry_manage("export")
        print("EXPORT:", json.dumps(r, indent=2, ensure_ascii=False))
        assert r["status"] == "success"

        # Testa op invalida
        r = mcp_telemetry_manage("invalid_op")
        print("INVALID:", json.dumps(r, indent=2, ensure_ascii=False))
        assert r["status"] == "error"

        # Testa track sem consentimento (nao deve gravar novos eventos)
        events_file = os.path.join(tmpdir, EVENTS_FILE)
        mcp_telemetry_manage("disable")
        events_before = 0
        if os.path.exists(events_file):
            with open(events_file, "r", encoding="utf-8") as f:
                events_before = len(f.readlines())
        track_mcp_event("scene_manage", {}, {"status": "success"}, 150, "PROTOTIPO")
        events_after = 0
        if os.path.exists(events_file):
            with open(events_file, "r", encoding="utf-8") as f:
                events_after = len(f.readlines())
        assert events_after == events_before, f"Eventos gravados sem consentimento! ({events_before} -> {events_after})"
        print("TRACK (sem consent): OK (nao deve ter evento)")

        # Testa track com consentimento
        mcp_telemetry_manage("enable")
        track_mcp_event("scene_manage", {}, {"status": "success"}, 150, "PROTOTIPO")
        track_mcp_event("script_manage", {}, {"status": "error", "error_code": 5000}, 300, "PROTOTIPO")
        print("TRACK (com consent): OK (2 eventos)")

        # Verifica que gravou eventos
        assert os.path.exists(events_file), "Eventos NAO foram gravados!"
        with open(events_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
        assert len(lines) >= 3, f"Esperava >=3 eventos, encontrou {len(lines)}"

        # Verifica status
        r = mcp_telemetry_manage("status")
        print("STATUS FINAL:", json.dumps(r, indent=2, ensure_ascii=False))
        assert r["total_tool_calls"] >= 2, f"Esperava >=2 tool_calls, encontrou {r['total_tool_calls']}"
        assert r["total_errors"] >= 1, f"Esperava >=1 error, encontrou {r['total_errors']}"

        # Testa export com eventos
        r = mcp_telemetry_manage("export")
        print("EXPORT (com eventos):", json.dumps(r, indent=2, ensure_ascii=False))
        assert r["status"] == "success"
        assert r["total_events"] >= 2

        # Testa reset
        r = mcp_telemetry_manage("reset")
        print("RESET:", json.dumps(r, indent=2, ensure_ascii=False))
        assert r["status"] == "success"
        assert not os.path.exists(events_file), "Arquivo de eventos nao foi removido!"

        # Testa track_phase_transition
        mcp_telemetry_manage("enable")
        track_phase_transition("IDEIA", "DESIGN")
        print("PHASE_TRANSITION: OK")

        print("\n=== TODOS OS TESTES PASSARAM ===")

    finally:
        # Restaura mock
        if original_get_active:
            po._get_active_project = original_get_active
        # Limpa tempdir
        import shutil
        shutil.rmtree(tmpdir, ignore_errors=True)
