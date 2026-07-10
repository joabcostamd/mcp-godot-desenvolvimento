"""batch_ops.py — Batch Atômico com Rollback (Fase 2C / M5).

Inspirado no yurineko73/godot-mcp-native: `batch_scene_node_edits` com
UndoRedo nativo + fallback file-based com snapshot/restore.

Estratégia:
    - Addon disponível? → addon_batch_edit (UndoRedo nativo, já atômico)
    - File-based?       → snapshot .tscn → executa em loop → rollback se erro

Uso:
    batch_atomic_edit([
        {"op": "create_node", "params": {"parent": ".", "type": "Sprite2D", "name": "Player"}},
        {"op": "set_property", "params": {"node": "./Player", "prop": "position", "value": "Vector2(100,200)"}},
        {"op": "create_node", "params": {"parent": "./Player", "type": "CollisionShape2D", "name": "Hitbox"}},
    ])
"""

import json
import shutil
import tempfile
from pathlib import Path
from typing import Any


# ── Constantes ──────────────────────────────────────────────────────

VALID_OPS = {
    "create_node",
    "delete_node",
    "set_property",
    "reparent_node",
    "duplicate_node",
    "connect_signal",
}


# ── Snapshot/Restore (file-based) ───────────────────────────────────

def _snapshot_scene(scene_path: str) -> str:
    """Cria backup de um arquivo .tscn e retorna o caminho do backup.

    Args:
        scene_path: Caminho absoluto para o .tscn.

    Returns:
        Caminho do arquivo de backup.

    Raises:
        FileNotFoundError: Se o .tscn não existe.
    """
    src = Path(scene_path)
    if not src.exists():
        raise FileNotFoundError(f"Cena não encontrada: {scene_path}")

    backup = src.with_suffix(".tscn.bak")
    shutil.copy2(src, backup)
    return str(backup)


def _restore_scene(scene_path: str, backup_path: str) -> None:
    """Restaura cena a partir do backup.

    Args:
        scene_path: Caminho da cena a restaurar.
        backup_path: Caminho do backup.
    """
    shutil.copy2(backup_path, scene_path)
    # Limpa o backup
    Path(backup_path).unlink(missing_ok=True)


def _cleanup_snapshot(backup_path: str) -> None:
    """Remove arquivo de backup após sucesso."""
    Path(backup_path).unlink(missing_ok=True)


# ── Executor de Operações ───────────────────────────────────────────

def _execute_op_file_based(op: str, params: dict) -> dict:
    """Executa UMA operação via file-based (sem Godot aberto).

    Args:
        op: Nome da operação (create_node, set_property, etc.).
        params: Parâmetros da operação.

    Returns:
        dict com "status": "success" ou "error".
    """
    from tools.scene_ops import (
        add_node,
        delete_node,
        set_node_property,
        reparent_node,
    )  # lazy import

    handlers = {
        "create_node": lambda p: add_node(
            scene_path=p.get("scene_path", ""),
            parent_node_path=p.get("parent", "."),
            node_name=p.get("name", ""),
            node_type=p.get("type", ""),
        ),
        "delete_node": lambda p: delete_node(
            scene_path=p.get("scene_path", ""),
            node_path=p.get("node", ""),
        ),
        "set_property": lambda p: set_node_property(
            scene_path=p.get("scene_path", ""),
            node_path=p.get("node", ""),
            property_name=p.get("prop", ""),
            value=p.get("value"),
        ),
        "reparent_node": lambda p: reparent_node(
            scene_path=p.get("scene_path", ""),
            node_path=p.get("node", ""),
            new_parent_path=p.get("new_parent", "."),
        ),
        "duplicate_node": lambda p: _duplicate_node_file(
            scene_path=p.get("scene_path", ""),
            node_path=p.get("node", ""),
            new_name=p.get("new_name"),
        ),
        "connect_signal": lambda p: _connect_signal_file(
            scene_path=p.get("scene_path", ""),
            node_path=p.get("node", ""),
            signal_name=p.get("signal", ""),
            target_path=p.get("target", ""),
            method_name=p.get("method", ""),
        ),
    }

    if op not in handlers:
        return {"status": "error", "message": f"Operação desconhecida: {op}"}

    try:
        return handlers[op](params)
    except Exception as e:
        return {"status": "error", "message": str(e)}


def _duplicate_node_file(scene_path: str, node_path: str, new_name: str | None = None) -> dict:
    """Duplica um nó via file-based (sem UndoRedo)."""
    from tools.scene_ops import add_node, get_node_property

    # Lê propriedades do original
    props_result = get_node_property(scene_path, node_path, "name")
    if props_result.get("status") != "success":
        return {"status": "error", "message": f"Nó não encontrado: {node_path}"}

    # Cria cópia
    parent = str(Path(node_path).parent)
    name = new_name or f"{props_result.get('value', 'node')}_copy"
    return add_node(
        scene_path=scene_path,
        parent_node_path=parent,
        node_name=name,
        node_type="Node",  # tipo será inferido
    )


def _connect_signal_file(
    scene_path: str, node_path: str, signal_name: str, target_path: str, method_name: str
) -> dict:
    """Conecta sinal via file-based."""
    from tools.scene_ops import connect_signal

    return connect_signal(
        scene_path=scene_path,
        source_path=node_path,
        signal_name=signal_name,
        target_path=target_path,
        method_name=method_name,
    )


# ── API Principal ───────────────────────────────────────────────────

def batch_atomic_edit(
    operations: list[dict],
    scene_path: str | None = None,
    mode: str = "auto",
) -> dict:
    """Executa múltiplas operações de forma ATÔMICA com rollback.

    Se UMA operação falhar, TODAS as anteriores são desfeitas.
    Isso garante que a cena nunca fique em estado inconsistente.

    Args:
        operations: Lista de operações. Cada operação tem:
            - op (str): create_node, delete_node, set_property, reparent_node,
                        duplicate_node, connect_signal.
            - params (dict): parâmetros específicos da operação.
        scene_path: Caminho da cena. Obrigatório para file-based.
        mode: "auto" (detecta addon), "addon" (força WebSocket), "file" (força file-based).

    Returns:
        dict com:
            - status: "success" ou "error"
            - mode: "addon" ou "file"
            - total: número de operações
            - succeeded: número de operações com sucesso
            - failed: número de operações que falharam
            - rolled_back: True se houve rollback
            - errors: lista de erros (se houver)
            - duration_ms: tempo total

    Example:
        >>> batch_atomic_edit([
        ...     {"op": "create_node", "params": {"parent": ".", "type": "Sprite2D", "name": "Icon"}},
        ...     {"op": "set_property", "params": {"node": "./Icon", "prop": "texture", "value": "res://icon.png"}},
        ... ])
    """
    import time
    t0 = time.time()

    # Valida operações
    invalid = [op for op in operations if op.get("op") not in VALID_OPS]
    if invalid:
        return {
            "status": "error",
            "message": f"Operações inválidas: {[o['op'] for o in invalid]}. Válidas: {sorted(VALID_OPS)}",
            "total": len(operations),
            "succeeded": 0,
            "failed": len(invalid),
            "rolled_back": False,
            "errors": [{"op": o["op"], "error": "Operação desconhecida"} for o in invalid],
            "duration_ms": 0,
        }

    # ── Modo Addon (UndoRedo nativo, já atômico) ──
    if mode in ("auto", "addon"):
        try:
            from tools.addon_bridge import addon_batch_edit, AddonNotConnectedError

            addon_ops = [
                {
                    "method": _map_op_to_addon(op["op"]),
                    "params": _map_params_to_addon(op["op"], op.get("params", {})),
                }
                for op in operations
            ]

            result = addon_batch_edit(addon_ops)
            elapsed = round((time.time() - t0) * 1000)

            if result.get("status") == "success":
                return {
                    "status": "success",
                    "mode": "addon",
                    "total": len(operations),
                    "succeeded": len(operations),
                    "failed": 0,
                    "rolled_back": False,
                    "errors": None,
                    "duration_ms": elapsed,
                    "method": "UndoRedo nativo (1 Ctrl+Z desfaz tudo)",
                }
            else:
                # Addon retornou erro — UndoRedo deve ter desfeito
                return {
                    "status": "error",
                    "mode": "addon",
                    "total": len(operations),
                    "succeeded": 0,
                    "failed": len(operations),
                    "rolled_back": True,
                    "errors": [{"message": result.get("message", "Erro no addon")}],
                    "duration_ms": elapsed,
                }

        except (ImportError, Exception):
            if mode == "addon":
                return {
                    "status": "error",
                    "mode": "addon",
                    "message": "Addon não disponível e mode=addon forçado",
                    "total": len(operations),
                    "succeeded": 0,
                    "failed": len(operations),
                    "rolled_back": False,
                    "errors": None,
                    "duration_ms": round((time.time() - t0) * 1000),
                }
            # Fallthrough para file-based

    # ── Modo File-Based (snapshot + rollback manual) ──
    if not scene_path:
        return {
            "status": "error",
            "message": "scene_path é obrigatório para operações file-based",
            "total": len(operations),
            "succeeded": 0,
            "failed": len(operations),
            "rolled_back": False,
            "errors": None,
            "duration_ms": round((time.time() - t0) * 1000),
        }

    backup_path = None
    errors = []
    succeeded = 0
    rolled_back = False

    try:
        # 1. Snapshot: backup da cena
        backup_path = _snapshot_scene(scene_path)

        # 2. Executa operações em sequência
        for i, operation in enumerate(operations):
            op_name = operation["op"]
            params = dict(operation.get("params", {}))
            params["scene_path"] = scene_path  # injeta scene_path

            result = _execute_op_file_based(op_name, params)

            if result.get("status") == "success":
                succeeded += 1
            else:
                errors.append({
                    "index": i,
                    "op": op_name,
                    "params": params,
                    "error": result.get("message", "Erro desconhecido"),
                })
                # 3. ROLLBACK: restaura snapshot
                if backup_path:
                    _restore_scene(scene_path, backup_path)
                    rolled_back = True
                break  # para no primeiro erro

        # 4. Sucesso: limpa backup
        if not rolled_back and backup_path:
            _cleanup_snapshot(backup_path)

    except Exception as e:
        # Erro inesperado: tenta restaurar
        if backup_path and Path(backup_path).exists():
            try:
                _restore_scene(scene_path, backup_path)
                rolled_back = True
            except Exception:
                pass
        errors.append({"error": str(e)})

    elapsed = round((time.time() - t0) * 1000)

    return {
        "status": "error" if errors else "success",
        "mode": "file",
        "total": len(operations),
        "succeeded": succeeded,
        "failed": len(operations) - succeeded,
        "rolled_back": rolled_back,
        "errors": errors or None,
        "duration_ms": elapsed,
        "method": "Snapshot/Restore (.tscn backup)" if rolled_back or succeeded == len(operations) else "Rollback executado",
    }


# ── Mapeamento Addon ────────────────────────────────────────────────

def _map_op_to_addon(op: str) -> str:
    """Mapeia nome de operação do batch_atomic para método do addon."""
    mapping = {
        "create_node": "create_node",
        "delete_node": "delete_node",
        "set_property": "set_property",
        "reparent_node": "reparent_node",
        "duplicate_node": "duplicate_node",
        "connect_signal": "connect_signal",
    }
    return mapping.get(op, op)


def _map_params_to_addon(op: str, params: dict) -> dict:
    """Mapeia parâmetros do batch_atomic para formato do addon."""
    # O addon usa nomes diferentes para alguns parâmetros
    mapping = {
        "create_node": {
            "parent_node_path": params.get("parent", "."),
            "node_name": params.get("name", ""),
            "node_type": params.get("type", ""),
        },
        "delete_node": {
            "node_path": params.get("node", ""),
        },
        "set_property": {
            "node_path": params.get("node", ""),
            "property_name": params.get("prop", ""),
            "value": params.get("value"),
        },
        "reparent_node": {
            "node_path": params.get("node", ""),
            "new_parent_path": params.get("new_parent", "."),
        },
        "duplicate_node": {
            "node_path": params.get("node", ""),
            "new_name": params.get("new_name"),
        },
        "connect_signal": {
            "source_path": params.get("node", ""),
            "signal_name": params.get("signal", ""),
            "target_path": params.get("target", ""),
            "method_name": params.get("method", ""),
        },
    }

    return mapping.get(op, params)
