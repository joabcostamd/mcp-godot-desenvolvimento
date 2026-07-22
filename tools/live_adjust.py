"""live_adjust.py — Ajuste ao Vivo com Aprovacao (FATIA 2.AI).

Captura parametros alterados durante o jogo, acumula mudancas,
apresenta ao humano para aprovacao, e so entao aplica no .tres.

Fluxo seguro:
  1. Capturar — jogo rodando, usuario ajusta valores
  2. Acumular — fila de mudancas pendentes
  3. Mostrar — diff claro do que vai mudar
  4. Humano aprova — gate explicito
  5. Parar o jogo — seguranca (nunca escrever com jogo rodando)
  6. Checkpoint — git commit antes de aplicar
  7. Escrever no .tres — persistir a mudanca
  8. Verificar — reload e teste

Fonte: Godot 4.7 docs — Resource, .tres, @export, EditorFileSystem.
"""

import json
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
PENDING_FILE = ROOT / ".mcp_live_adjust_pending.json"


def capture_change(behavior_name: str, param_name: str, old_value: Any, new_value: Any) -> dict:
    """Registra uma mudanca pendente para aprovacao.

    Args:
        behavior_name: Nome do behavior (ex: 'health').
        param_name: Nome do parametro (ex: 'max_hp').
        old_value: Valor antes da mudanca.
        new_value: Valor depois da mudanca.

    Returns:
        dict com status.
    """
    pending = _load_pending()
    key = f"{behavior_name}.{param_name}"

    pending[key] = {
        "behavior": behavior_name,
        "parameter": param_name,
        "old_value": str(old_value),
        "new_value": str(new_value),
        "timestamp": time.time(),
    }

    _save_pending(pending)

    return {
        "status": "captured",
        "change": f"{behavior_name}.{param_name}: {old_value} → {new_value}",
        "total_pending": len(pending),
        "message": f"Mudanca capturada. {len(pending)} alteracoes pendentes de aprovacao.",
    }


def get_pending_changes() -> dict:
    """Lista todas as mudancas pendentes de aprovacao.

    Returns:
        dict com lista de mudancas.
    """
    pending = _load_pending()
    return {
        "status": "success",
        "pending_count": len(pending),
        "changes": [
            {
                "key": k,
                "behavior": v["behavior"],
                "parameter": v["parameter"],
                "old_value": v["old_value"],
                "new_value": v["new_value"],
            }
            for k, v in pending.items()
        ],
    }


def approve_changes(project_path: str = ".") -> dict:
    """Aplica todas as mudancas pendentes apos aprovacao humana.

    ATENCAO: Este metodo assume que o jogo JA FOI PARADO.
    Nunca chame com o jogo rodando.

    Args:
        project_path: Caminho do projeto.

    Returns:
        dict com resultado da aplicacao.
    """
    pending = _load_pending()
    if not pending:
        return {"status": "empty", "message": "Nenhuma mudanca pendente."}

    project_dir = Path(project_path)
    applied = []
    failed = []

    for key, change in pending.items():
        behavior = change["behavior"]
        param = change["parameter"]
        new_val = change["new_value"]

        tres_path = project_dir / "behaviors" / behavior / f"{behavior}.tres"
        if not tres_path.exists():
            failed.append(f"{key}: .tres nao encontrado em {tres_path}")
            continue

        try:
            content = tres_path.read_text(encoding="utf-8")
            # Atualiza o valor do parametro no .tres
            import re
            pattern = rf"^{param}\s*=\s*.+$"
            replacement = f"{param} = {new_val}"
            new_content = re.sub(pattern, replacement, content, flags=re.MULTILINE)

            if new_content != content:
                tres_path.write_text(new_content, encoding="utf-8")
                applied.append(key)
            else:
                failed.append(f"{key}: parametro nao encontrado no .tres")
        except OSError as e:
            failed.append(f"{key}: erro ao escrever — {e}")

    # Limpa pendentes
    _save_pending({})

    return {
        "status": "success" if not failed else "partial",
        "applied": applied,
        "failed": failed,
        "message": f"{len(applied)} mudancas aplicadas, {len(failed)} falhas.",
    }


def clear_pending() -> dict:
    """Descarta todas as mudancas pendentes."""
    _save_pending({})
    return {"status": "cleared", "message": "Todas as mudancas pendentes foram descartadas."}


def _load_pending() -> dict:
    if PENDING_FILE.exists():
        try:
            return json.loads(PENDING_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {}


def _save_pending(data: dict) -> None:
    PENDING_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
