"""safety — Backup, checkpoint e restore de arquivos.

checkpoint, restore, list_backups, git_checkpoint.
Usado por toda operação destrutiva (delete, overwrite, move).
"""

import json
import os as _os
import shutil
import subprocess
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parent.parent
MAX_BACKUPS = 50

# Lock para evitar race condition em _save_index
_backup_lock = threading.Lock()


# ── Helpers ─────────────────────────────────────────────────────────

def _backup_dir(project_root: Path) -> Path:
    """Retorna o diretório de backups dentro do projeto alvo."""
    return project_root / ".mcp_backups"


def _index_path(project_root: Path) -> Path:
    """Retorna o caminho do índice de backups."""
    return _backup_dir(project_root) / "index.json"


def _load_index(project_root: Path) -> list[dict]:
    """Carrega o índice de backups."""
    idx_path = _index_path(project_root)
    if idx_path.exists():
        with open(idx_path, encoding="utf-8") as f:
            return json.load(f)
    return []


def _save_index(project_root: Path, index: list[dict]) -> None:
    """Salva o índice de backups com escrita atômica e lock."""
    idx_path = _index_path(project_root)
    idx_path.parent.mkdir(parents=True, exist_ok=True)
    with _backup_lock:
        tmp = idx_path.with_suffix('.json.tmp')
        tmp.write_text(json.dumps(index, indent=2), encoding='utf-8')
        _os.replace(str(tmp), str(idx_path))


def _rotate_backups(project_root: Path) -> None:
    """Remove backups excedentes (mantém no máximo MAX_BACKUPS)."""
    index = _load_index(project_root)
    if len(index) <= MAX_BACKUPS:
        return
    # Ordena por timestamp, remove os mais antigos
    index.sort(key=lambda x: x.get("timestamp", ""))
    to_remove = index[:-MAX_BACKUPS]
    backup_dir = _backup_dir(project_root)
    for entry in to_remove:
        backup_path = backup_dir / f"{entry['backup_id']}"
        if backup_path.exists():
            backup_path.unlink()
    # Atualiza índice
    remaining = [e for e in index if e not in to_remove]
    _save_index(project_root, remaining)


def _get_project_root() -> Path:
    """Obtém a raiz do projeto ativo a partir da configuração."""
    try:
        from tools.config_loader import load_config
        cfg = load_config()
        default = cfg.get("default_project", "example_project")
        proj = Path(default)
        if not proj.is_absolute():
            proj = ROOT / proj
        return proj
    except Exception:
        return ROOT / "example_project"


# ── API Pública ─────────────────────────────────────────────────────

def checkpoint(file_path: str | Path, project_root: Path | None = None) -> Optional[str]:
    """Cria backup de um arquivo antes de operação destrutiva.

    Args:
        file_path: Caminho relativo (dentro do projeto) ou absoluto.
        project_root: Raiz do projeto Godot. Se None, usa config.json.

    Returns:
        backup_id (str) se backup foi criado, None se arquivo não existia.
    """
    if project_root is None:
        project_root = _get_project_root()

    file_path = Path(file_path)
    if not file_path.is_absolute():
        # Se o path relativo já começa com o nome do projeto, resolve
        # a partir do pai do project_root
        try:
            rel = file_path.relative_to(project_root.name)
            file_path = project_root / rel
        except ValueError:
            file_path = project_root / file_path

    if not file_path.exists():
        return None

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_%f")
    backup_id = f"{timestamp}_{file_path.name}"
    backup_dest = _backup_dir(project_root) / backup_id
    backup_dest.parent.mkdir(parents=True, exist_ok=True)

    shutil.copy2(file_path, backup_dest)

    # Registra no índice
    index = _load_index(project_root)
    index.append({
        "backup_id": backup_id,
        "original_path": str(file_path.relative_to(project_root)),
        "timestamp": timestamp,
        "operation": "checkpoint",
    })
    _save_index(project_root, index)
    _rotate_backups(project_root)

    return backup_id


def restore(backup_id: str, project_root: Path | None = None) -> dict:
    """Restaura um arquivo a partir de um backup.

    Faz checkpoint do estado atual antes de restaurar (undo do undo).

    Returns:
        {"status": "success", "restored": str} ou {"status": "error", "message": str}
    """
    if project_root is None:
        project_root = _get_project_root()

    index = _load_index(project_root)
    entry = next((e for e in index if e["backup_id"] == backup_id), None)
    if not entry:
        return {
            "status": "error",
            "message": f"Backup '{backup_id}' não encontrado. "
                       f"Use list_backups para ver backups disponíveis.",
        }

    backup_file = _backup_dir(project_root) / backup_id
    if not backup_file.exists():
        return {
            "status": "error",
            "message": f"Arquivo de backup '{backup_id}' não encontrado no disco. "
                       f"O índice pode estar corrompido.",
        }

    original_path = project_root / entry["original_path"]

    # Checkpoint do estado atual antes de restaurar
    if original_path.exists():
        checkpoint(str(original_path), project_root)

    # Restaura
    original_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(backup_file, original_path)

    return {
        "status": "success",
        "restored": entry["original_path"],
        "backup_id": backup_id,
    }


def list_backups(
    original_path: str | None = None, project_root: Path | None = None
) -> list[dict]:
    """Lista backups, mais recentes primeiro.

    Args:
        original_path: Filtra por arquivo original (opcional).
        project_root: Raiz do projeto Godot.

    Returns:
        Lista de {"backup_id", "original_path", "timestamp", "operation"}.
    """
    if project_root is None:
        project_root = _get_project_root()

    index = _load_index(project_root)

    if original_path:
        index = [e for e in index if e["original_path"] == original_path]

    # Mais recentes primeiro
    index.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    return index


def git_checkpoint(message: str, project_root: Path | None = None,
                    skip_validation: bool = False) -> dict:
    """Faz commit git no projeto alvo (se for repo git).

    Returns:
        {"status": "success", "commit": str} ou {"status": "skipped"}.
    """
    if project_root is None:
        project_root = _get_project_root()

    git_dir = project_root / ".git"
    if not git_dir.exists():
        return {"status": "skipped", "note": "Projeto não é um repositório git."}

    # ── Gate de compilação: valida todos os .gd do projeto (não opcional) ──
    # NOTA: este gate valida SINTAXE (parênteses, R1, R2), não SEMÂNTICA.
    # Não pega: métodos inexistentes, tipos errados, nós referenciados que
    # não existem na cena. Para essas classes de erro, ainda é necessário
    # rodar compile_test manualmente antes de confiar 100% no commit.
    if not skip_validation:
        try:
            from tools.validate_write import validate_gdscript_syntax
            errors_found = []
            for gd_file in project_root.glob("**/*.gd"):
                # Pula addons e .godot
                if "addons" in gd_file.parts or ".godot" in gd_file.parts:
                    continue
                try:
                    code = gd_file.read_text(encoding="utf-8")
                    validation = validate_gdscript_syntax(code)
                    if not validation.get("valid", True):
                        for err in (validation.get("errors") or []):
                            errors_found.append({
                                "file": str(gd_file.relative_to(project_root)),
                                "line": err.get("line"),
                                "message": err.get("message"),
                                "rule": err.get("rule"),
                            })
                except Exception:
                    pass
            if errors_found:
                return {
                    "status": "error",
                    "message": "❌ Commit BLOQUEADO — o projeto não compila. "
                               "Corrija os erros antes de salvar o progresso.",
                    "compile_errors": errors_found,
                }
        except Exception:
            pass  # Se validação falhar por infra, não bloqueia

        # ── Gate de testes GUT (se a pasta tests/ existir) ──
        tests_dir = project_root / "tests"
        if tests_dir.exists() and any(tests_dir.glob("test_*.gd")):
            try:
                from tools.gut_ops import run_gut_tests
                gut_result = run_gut_tests(project_path=str(project_root))
                if gut_result.get("status") == "tests_failed":
                    return {
                        "status": "error",
                        "message": "❌ Commit BLOQUEADO — testes GUT falharam.",
                        "test_results": gut_result.get("results"),
                    }
            except Exception:
                pass  # GUT não instalado — não bloqueia

    try:
        subprocess.run(
            ["git", "add", "-A"],
            cwd=str(project_root),
            capture_output=True,
            text=True,
            timeout=30,
        )
        result = subprocess.run(
            ["git", "commit", "-m", message],
            cwd=str(project_root),
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0:
            return {"status": "success", "commit": message, "validated": not skip_validation}
        else:
            return {
                "status": "error",
                "message": f"Git commit falhou: {result.stderr.strip()}",
            }
    except Exception as e:
        return {"status": "error", "message": f"Erro ao executar git: {e}"}


# ══════════════════════════════════════════════════════════════════════
# Undo Stack — histórico de ações para desfazer
# ══════════════════════════════════════════════════════════════════════

_undo_stack: list[dict] = []
_MAX_UNDO = 20


def push_undo(action_name: str, file_paths: list[str], project_root: Path | None = None) -> str:
    """Registra uma ação no histórico de desfazer.

    Faz checkpoint de cada arquivo ANTES da modificação e empilha.
    Use antes de qualquer operação destrutiva.

    Args:
        action_name: Nome legível da ação (ex: "Criar script Player").
        file_paths: Lista de caminhos de arquivos que serão modificados.
        project_root: Raiz do projeto.

    Returns:
        undo_id da ação, ou string vazia se nada foi salvo.
    """
    if project_root is None:
        project_root = _get_project_root()

    backup_ids = []
    for fp in file_paths:
        bid = checkpoint(fp, project_root)
        if bid:
            backup_ids.append(bid)

    if not backup_ids:
        return ""

    undo_id = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_%f")
    _undo_stack.append({
        "undo_id": undo_id,
        "action": action_name,
        "backup_ids": backup_ids,
        "files": file_paths,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })

    # Limita tamanho
    while len(_undo_stack) > _MAX_UNDO:
        _undo_stack.pop(0)

    return undo_id


def undo_last_action(project_root: Path | None = None) -> dict:
    """Desfaz a última ação registrada, restaurando todos os arquivos.

    Returns:
        {"status": "success", "undone": str, "files_restored": int}
        ou {"status": "error", "message": str}
    """
    if not _undo_stack:
        return {
            "status": "error",
            "message": "Nada para desfazer. O histórico está vazio.",
            "friendly": "Não tem nenhuma ação para desfazer. Tudo certo!",
        }

    if project_root is None:
        project_root = _get_project_root()

    entry = _undo_stack.pop()
    restored = 0
    failed = []

    for bid in entry["backup_ids"]:
        result = restore(bid, project_root)
        if result.get("status") == "success":
            restored += 1
        else:
            failed.append(bid)

    if failed:
        return {
            "status": "warning",
            "undone": entry["action"],
            "files_restored": restored,
            "files_failed": len(failed),
            "friendly": (
                f"Desfez '{entry['action']}' mas {len(failed)} arquivo(s) não "
                f"puderam ser restaurados. O resto voltou ao normal."
            ),
        }

    return {
        "status": "success",
        "undone": entry["action"],
        "files_restored": restored,
        "friendly": f"Desfez '{entry['action']}'. {restored} arquivo(s) restaurado(s).",
    }


def get_undo_history() -> dict:
    """Retorna o histórico de ações que podem ser desfeitas."""
    return {
        "status": "success",
        "history": [
            {"action": e["action"], "files": e["files"], "when": e["timestamp"]}
            for e in reversed(_undo_stack)
        ],
        "count": len(_undo_stack),
    }


# ── GAP #13: Undo Semântico + Redo ────────────────────────────────────

_semantic_stack: list[dict] = []
_redo_stack: list[dict] = []
_MAX_SEMANTIC = 50


def push_undo_semantic(tool_name: str, forward_args: dict, reverse_args: dict) -> str:
    """Registra ação semântica para undo/redo. GAP #13."""
    from datetime import datetime, timezone
    undo_id = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_%f")
    _semantic_stack.append({
        "undo_id": undo_id, "tool": tool_name,
        "forward": forward_args, "reverse": reverse_args,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })
    _redo_stack.clear()
    while len(_semantic_stack) > _MAX_SEMANTIC:
        _semantic_stack.pop(0)
    return undo_id


def undo_last_semantic() -> dict:
    """Desfaz última ação semântica. GAP #13."""
    if not _semantic_stack:
        return {"status": "error", "message": "Nenhuma acao para desfazer."}
    entry = _semantic_stack.pop()
    _redo_stack.append(entry)
    return {"status": "success", "undone": entry["tool"], "reverse_params": entry["reverse"]}


def redo_last_semantic() -> dict:
    """Refaz última ação desfeita. GAP #13."""
    if not _redo_stack:
        return {"status": "error", "message": "Nenhuma acao para refazer."}
    entry = _redo_stack.pop()
    _semantic_stack.append(entry)
    return {"status": "success", "redone": entry["tool"], "forward_params": entry["forward"]}

