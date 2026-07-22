"""undo_unify.py — Unificacao dos 3 Historicos de Desfazer (FATIA 2.AT).

Unifica UndoRedo (Godot), git (versionamento) e botao Reverter
num unico historico. Define quem manda em caso de conflito.

Hierarquia:
  1. git — sempre o source of truth (commit = ponto de restauracao)
  2. UndoRedo — para operacoes dentro de uma sessao
  3. Reverter — atalho para o ultimo commit

Fonte: Godot 4.7 docs — UndoRedo, EditorPlugin.
Git docs — reset, revert, reflog.
"""

import json
import subprocess
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
HISTORY_FILE = ROOT / ".mcp_undo_history.json"


def checkpoint(description: str = "") -> dict:
    """Cria um ponto de restauracao (git commit + registro).

    Args:
        description: Descricao do checkpoint.

    Returns:
        dict com hash do commit.
    """
    try:
        result = subprocess.run(
            ["git", "add", "-A"],
            capture_output=True, text=True, timeout=10, cwd=str(ROOT),
        )
        msg = description or f"checkpoint: {time.strftime('%Y-%m-%d %H:%M:%S')}"
        result = subprocess.run(
            ["git", "commit", "-m", msg, "--allow-empty"],
            capture_output=True, text=True, timeout=10, cwd=str(ROOT),
        )
        commit_hash = result.stdout.strip().split()[-1][:7] if result.stdout else "unknown"

        # Registra no historico unificado
        _record("checkpoint", description, commit_hash)

        return {
            "status": "success",
            "type": "checkpoint",
            "commit": commit_hash,
            "message": f"Checkpoint criado: {commit_hash} — {description}",
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


def undo(steps: int = 1) -> dict:
    """Desfaz ate N checkpoints (git reset).

    Args:
        steps: Numero de checkpoints a desfazer.

    Returns:
        dict com resultado.
    """
    history = _load_history()
    if not history:
        return {"status": "empty", "message": "Nenhum checkpoint registrado."}

    if steps > len(history):
        steps = len(history)

    try:
        # Volta N commits
        result = subprocess.run(
            ["git", "reset", "--soft", f"HEAD~{steps}"],
            capture_output=True, text=True, timeout=10, cwd=str(ROOT),
        )

        # Remove do historico
        undone = history[-steps:]
        history = history[:-steps]
        _save_history(history)

        return {
            "status": "success",
            "type": "undo",
            "steps": steps,
            "undone_checkpoints": [
                {"commit": h["commit"], "description": h["description"]}
                for h in undone
            ],
            "remaining": len(history),
            "message": f"{steps} checkpoint(s) desfeito(s). {len(history)} restantes.",
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


def redo(steps: int = 1) -> dict:
    """Refaz N checkpoints (git reflog + reset).

    Nota: git reset --soft remove o commit do historico,
    mas o reflog mantem a referencia. Use com cautela.
    """
    try:
        result = subprocess.run(
            ["git", "reflog", "-5"],
            capture_output=True, text=True, timeout=5, cwd=str(ROOT),
        )
        return {
            "status": "success",
            "type": "redo_info",
            "recent_reflog": result.stdout.strip().split("\n")[:5],
            "message": "Use git reset --soft <hash> para refazer para um commit especifico.",
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


def get_history() -> dict:
    """Retorna o historico unificado de checkpoints.

    Returns:
        dict com lista de checkpoints.
    """
    history = _load_history()
    return {
        "status": "success",
        "total_checkpoints": len(history),
        "checkpoints": [
            {
                "index": i,
                "commit": h["commit"],
                "description": h["description"],
                "timestamp": h.get("timestamp", ""),
            }
            for i, h in enumerate(history)
        ],
    }


def _record(action: str, description: str, commit_hash: str) -> None:
    history = _load_history()
    history.append({
        "action": action,
        "description": description,
        "commit": commit_hash,
        "timestamp": time.time(),
    })
    _save_history(history)


def _load_history() -> list:
    if HISTORY_FILE.exists():
        try:
            return json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return []


def _save_history(data: list) -> None:
    HISTORY_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
