"""safety_policy.py — Safety Policy (Fase 3 / wangdiandao).

Política de segurança por arquivo: allowlist, blocklist, confirm-destructive.
Inspirado no wangdiandao/godot-devtool (set_safety_policy, preview_write_safety).

Tools:
    - set_safety_policy: configura regras de segurança
    - preview_write_safety: preview de operação antes de executar
    - get_safety_policy: lê política atual
    - get_audit_log: histórico de ações
    - get_audit_replay: replay do histórico
"""

import json
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SAFETY_CONFIG = ROOT / ".safety_policy.json"
AUDIT_LOG = ROOT / ".audit_log.json"


def _load_safety() -> dict:
    if SAFETY_CONFIG.exists():
        with open(SAFETY_CONFIG, encoding="utf-8") as f:
            return json.load(f)
    return {
        "enabled": False,
        "allowlist": [],
        "blocklist": [],
        "confirm_destructive": True,
        "max_file_size_kb": 1024,
    }


def _save_safety(config: dict) -> None:
    with open(SAFETY_CONFIG, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


def _load_audit() -> list[dict]:
    if AUDIT_LOG.exists():
        with open(AUDIT_LOG, encoding="utf-8") as f:
            return json.load(f)
    return []


def _save_audit(entries: list[dict]) -> None:
    # Mantém só os últimos 200
    entries = entries[-200:]
    with open(AUDIT_LOG, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2, ensure_ascii=False)


# ── Safety Policy ────────────────────────────────────────────────────

def set_safety_policy(
    enabled: bool | None = None,
    allowlist: list[str] | None = None,
    blocklist: list[str] | None = None,
    confirm_destructive: bool | None = None,
    max_file_size_kb: int | None = None,
) -> dict:
    """Configura política de segurança do projeto.

    Args:
        enabled: Ativa/desativa a política.
        allowlist: Lista de paths/patterns permitidos (glob).
        blocklist: Lista de paths/patterns bloqueados.
        confirm_destructive: Se True, pede confirmação para operações destrutivas.
        max_file_size_kb: Tamanho máximo de arquivo para write.

    Returns:
        dict com política aplicada.
    """
    config = _load_safety()

    if enabled is not None:
        config["enabled"] = enabled
    if allowlist is not None:
        config["allowlist"] = allowlist
    if blocklist is not None:
        config["blocklist"] = blocklist
    if confirm_destructive is not None:
        config["confirm_destructive"] = confirm_destructive
    if max_file_size_kb is not None:
        config["max_file_size_kb"] = max_file_size_kb

    _save_safety(config)

    return {
        "status": "success",
        "safety_policy": config,
        "summary": {
            "active": config["enabled"],
            "allowlist_count": len(config["allowlist"]),
            "blocklist_count": len(config["blocklist"]),
            "confirm_destructive": config["confirm_destructive"],
        },
    }


def get_safety_policy() -> dict:
    """Lê a política de segurança atual."""
    config = _load_safety()
    return {"status": "success", "safety_policy": config}


def preview_write_safety(
    file_paths: list[str],
    operation: str = "write",
) -> dict:
    """Verifica se arquivos podem ser escritos segundo a política.

    Args:
        file_paths: Lista de paths a verificar.
        operation: "write", "delete", "modify".

    Returns:
        dict com permissão por arquivo.
    """
    config = _load_safety()

    if not config["enabled"]:
        return {"status": "success", "allowed": True, "message": "Política de segurança desativada"}

    results = []
    all_allowed = True
    blocked = []

    for fp in file_paths:
        allowed = True
        reason = ""

        # Blocklist tem prioridade
        for pattern in config["blocklist"]:
            if _match_pattern(fp, pattern):
                allowed = False
                reason = f"Bloqueado por pattern: {pattern}"
                break

        # Allowlist (se configurada)
        if allowed and config["allowlist"]:
            in_allowlist = any(_match_pattern(fp, p) for p in config["allowlist"])
            if not in_allowlist:
                allowed = False
                reason = "Fora da allowlist"

        results.append({"path": fp, "allowed": allowed, "reason": reason or "OK"})

        if not allowed:
            all_allowed = False
            blocked.append(fp)

    return {
        "status": "success",
        "all_allowed": all_allowed,
        "operation": operation,
        "results": results,
        "blocked": blocked or None,
        "confirm_required": config["confirm_destructive"] and operation in ("delete", "modify"),
    }


# ── Audit Log ────────────────────────────────────────────────────────

def get_audit_log(limit: int = 50) -> dict:
    """Lê o histórico de auditoria (últimas ações da IA).

    Args:
        limit: Máximo de entradas.
    """
    entries = _load_audit()[-limit:]
    return {
        "status": "success",
        "entries": entries,
        "total_stored": len(_load_audit()),
        "returned": len(entries),
    }


def get_audit_replay(steps: int = 10) -> dict:
    """Gera replay do histórico para a IA entender o que foi feito.

    Args:
        steps: Número de passos a resumir.
    """
    entries = _load_audit()[-steps:]

    replay = []
    for e in entries:
        replay.append({
            "when": e.get("timestamp", ""),
            "tool": e.get("tool", ""),
            "action": e.get("action", ""),
            "result": e.get("result", ""),
        })

    return {
        "status": "success",
        "replay_steps": replay,
        "summary": {
            "total_steps": len(entries),
            "operations": len([e for e in entries if e.get("type") == "operation"]),
            "errors": len([e for e in entries if e.get("result") == "error"]),
        },
    }


def log_audit_entry(tool: str, action: str, result: str = "success", details: str = "") -> dict:
    """Registra uma entrada no audit log (uso interno)."""
    entries = _load_audit()
    entries.append({
        "timestamp": datetime.now().isoformat(),
        "type": "operation",
        "tool": tool,
        "action": action,
        "result": result,
        "details": details,
    })
    _save_audit(entries)
    return {"status": "success", "logged": True}


# ── Helpers ──────────────────────────────────────────────────────────

def _match_pattern(path: str, pattern: str) -> bool:
    """Match simples de glob pattern."""
    import fnmatch
    return fnmatch.fnmatch(path, pattern)
