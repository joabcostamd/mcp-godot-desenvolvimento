"""proof_ledger.py — Livro-Razão de Prova (Bloco 4).

Ferramentas de coleta e verificação mecânica de evidências.
NUNCA reformata, NUNCA trunca, NUNCA edita output — tudo é
capturado literalmente via subprocess.

Tools:
    capture_proof — coleta evidência de tarefa concluída
    verify_proof  — verifica validade de prova existente
"""

import hashlib
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent

# ── Constantes ──────────────────────────────────────────────────────

PROOF_DIR_NAME = ".mcp_proof"
MAX_EXTRA_COMMANDS = 5


# ══════════════════════════════════════════════════════════════════════
# capture_proof
# ══════════════════════════════════════════════════════════════════════

def capture_proof(
    task_id: str,
    project_path: str | None = None,
    run_tests: bool = True,
    extra_commands: list[str] | None = None,
) -> dict:
    """Coleta mecanicamente a evidência de uma tarefa concluída.

    NENHUM texto vem da IA — tudo é output literal capturado
    via subprocess (git, testes, comandos extras).

    Args:
        task_id: Identificador curto da tarefa (ex: "bloco4-capture-proof").
        project_path: Caminho do repositório. Default: raiz do MCP.
        run_tests: Se roda regression_test como parte da prova.
        extra_commands: Comandos adicionais cujo stdout/stderr
                        devem ser capturados. Máximo 5.

    Returns:
        Dict com status, proof_file, worktree_hash, head_commit, etc.
    """
    # Resolve project_path
    if project_path:
        proj = Path(project_path).resolve()
    else:
        proj = ROOT.resolve()

    if not proj.exists():
        return {
            "status": "error",
            "task_id": task_id,
            "message": f"project_path não existe: {proj}",
        }

    # Valida extra_commands
    if extra_commands is None:
        extra_commands = []
    if len(extra_commands) > MAX_EXTRA_COMMANDS:
        return {
            "status": "error",
            "task_id": task_id,
            "message": f"Máximo de {MAX_EXTRA_COMMANDS} comandos extras. Recebido: {len(extra_commands)}.",
        }

    # 1. Capturar estado do worktree
    head_commit = _git_rev_parse_head(proj)
    git_status = _git_status_porcelain(proj)
    git_diff = _git_diff_no_color(proj)
    untracked_files = _capture_untracked(proj, git_status)

    # 2. Calcular worktree_hash
    worktree_hash = _compute_worktree_hash(
        head_commit, git_status, git_diff, untracked_files
    )

    # 3. Rodar regression_test se solicitado
    regression_result = None
    if run_tests:
        try:
            from tools.test_ops import regression_test
            regression_result = regression_test()
        except Exception as e:
            regression_result = {
                "status": "error",
                "message": f"Falha ao rodar regression_test: {e}",
            }

    # 4. Rodar comandos extras
    extra_results = []
    for cmd in extra_commands:
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',
                errors='replace',
                close_fds=True,
                timeout=120,
                cwd=str(proj),
            )
            extra_results.append({
                "command": cmd,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
            })
        except subprocess.TimeoutExpired:
            extra_results.append({
                "command": cmd,
                "returncode": -1,
                "stdout": "",
                "stderr": "TIMEOUT: comando excedeu 120s",
            })
        except Exception as e:
            extra_results.append({
                "command": cmd,
                "returncode": -1,
                "stdout": "",
                "stderr": f"ERRO: {e}",
            })

    # 5. Montar arquivo de prova
    timestamp_utc = datetime.now(timezone.utc)
    timestamp_str = timestamp_utc.strftime("%Y%m%d_%H%M%S")
    proof_data = {
        "task_id": task_id,
        "timestamp_utc": timestamp_utc.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "project_path": str(proj),
        "head_commit": head_commit,
        "worktree_hash": f"sha256:{worktree_hash}",
        "git_status": git_status,
        "git_diff": git_diff,
        "untracked_files": untracked_files,
        "regression_test": regression_result,
        "extra_commands": extra_results,
    }

    # 6. Gravar em .mcp_proof/
    proof_dir = proj / PROOF_DIR_NAME
    proof_dir.mkdir(parents=True, exist_ok=True)

    safe_task_id = _sanitize_filename(task_id)
    proof_filename = f"{safe_task_id}_{timestamp_str}.json"
    proof_file = proof_dir / proof_filename

    # Usar config_lock para escrita segura
    try:
        from tools.config_lock import CONFIG_FILE_LOCK
        lock = CONFIG_FILE_LOCK
    except ImportError:
        import threading
        lock = threading.Lock()

    with lock:
        tmp_path = proof_file.with_suffix('.json.tmp')
        tmp_path.write_text(
            json.dumps(proof_data, indent=2, ensure_ascii=False),
            encoding='utf-8',
        )
        os.replace(str(tmp_path), str(proof_file))

    # 7. Calcular métricas
    diff_lines = git_diff.count('\n') if git_diff else 0
    files_changed = len([
        line for line in (git_status or "").split('\n')
        if line.strip() and not line.startswith('??')
    ])
    untracked_count = len(untracked_files)

    # Sumário do regression_test
    reg_summary = {"total": 0, "passed": 0, "failed": 0}
    if regression_result and isinstance(regression_result, dict):
        summary = regression_result.get("summary", {})
        if summary:
            reg_summary = {
                "total": summary.get("total", 0),
                "passed": summary.get("passed", 0),
                "failed": summary.get("failed", 0),
            }

    return {
        "status": "ok",
        "task_id": task_id,
        "proof_file": str(proof_file),
        "worktree_hash": f"sha256:{worktree_hash}",
        "head_commit": head_commit,
        "files_changed": files_changed,
        "untracked_captured": untracked_count,
        "diff_lines": diff_lines,
        "regression": reg_summary,
        "extra_commands_run": len(extra_results),
        "note": (
            "Prova coletada mecanicamente pela ferramenta. "
            "O conteúdo do arquivo de prova é output literal de git "
            "e dos testes — não foi escrito nem editado por nenhum modelo."
        ),
        "summary": (
            f"Prova '{task_id}' coletada em {timestamp_str}. "
            f"Commit: {head_commit[:8] if len(head_commit) >= 8 else head_commit}. "
            f"Diff: {diff_lines} linhas, {files_changed} arquivos alterados, "
            f"{untracked_count} untracked capturados. "
            f"Regression: {reg_summary['passed']}/{reg_summary['total']} passaram."
        ),
    }


# ══════════════════════════════════════════════════════════════════════
# verify_proof
# ══════════════════════════════════════════════════════════════════════

def verify_proof(
    task_id: str | None = None,
    project_path: str | None = None,
    max_age_minutes: int = 60,
) -> dict:
    """Verifica se uma prova é válida e se corresponde ao estado ATUAL do código.

    Args:
        task_id: Se passado, verifica a prova mais recente desse task_id.
                 Se omitido, verifica a prova mais recente de qualquer task.
        project_path: Caminho do repositório. Default: raiz do MCP.
        max_age_minutes: Prova mais velha que isso é considerada obsoleta.

    Returns:
        Dict com status (valid|stale|mismatch|missing|failed_tests),
        proof_file, age_minutes, hash_match, regression_passed, reason, summary.
    """
    # Resolve project_path
    if project_path:
        proj = Path(project_path).resolve()
    else:
        proj = ROOT.resolve()

    proof_dir = proj / PROOF_DIR_NAME

    # 1. Localizar arquivo de prova
    if not proof_dir.exists():
        return {
            "status": "missing",
            "proof_file": None,
            "task_id": task_id,
            "age_minutes": 0,
            "hash_match": False,
            "regression_passed": False,
            "reason": f"Diretório de provas não existe: {proof_dir}",
            "summary": "Nenhuma prova encontrada.",
        }

    proof_files = sorted(proof_dir.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)

    if task_id:
        safe_task_id = _sanitize_filename(task_id)
        proof_files = [p for p in proof_files if p.stem.startswith(safe_task_id)]

    if not proof_files:
        return {
            "status": "missing",
            "proof_file": None,
            "task_id": task_id,
            "age_minutes": 0,
            "hash_match": False,
            "regression_passed": False,
            "reason": (
                f"Nenhuma prova encontrada para task_id='{task_id}'."
                if task_id else "Nenhuma prova encontrada no diretório."
            ),
            "summary": "Nenhuma prova encontrada.",
        }

    proof_file = proof_files[0]

    # 2. Carregar prova
    try:
        proof_data = json.loads(proof_file.read_text(encoding='utf-8'))
    except Exception as e:
        return {
            "status": "missing",
            "proof_file": str(proof_file),
            "task_id": task_id,
            "age_minutes": 0,
            "hash_match": False,
            "regression_passed": False,
            "reason": f"Erro ao ler arquivo de prova: {e}",
            "summary": "Arquivo de prova corrompido ou ilegível.",
        }

    recorded_hash = proof_data.get("worktree_hash", "")
    if recorded_hash.startswith("sha256:"):
        recorded_hash = recorded_hash[7:]

    # 3. Verificar idade
    try:
        proof_mtime = datetime.fromtimestamp(proof_file.stat().st_mtime, tz=timezone.utc)
        now_utc = datetime.now(timezone.utc)
        age_minutes = round((now_utc - proof_mtime).total_seconds() / 60, 1)
    except Exception:
        age_minutes = 0

    # 4. Recalcular worktree_hash do estado ATUAL
    current_head = _git_rev_parse_head(proj)
    current_status = _git_status_porcelain(proj)
    current_diff = _git_diff_no_color(proj)
    current_untracked = _capture_untracked(proj, current_status)
    current_hash = _compute_worktree_hash(
        current_head, current_status, current_diff, current_untracked
    )

    hash_match = (current_hash == recorded_hash)

    # 5. Verificar regression_test
    regression_passed = True
    reg_result = proof_data.get("regression_test")
    if reg_result and isinstance(reg_result, dict):
        summary = reg_result.get("summary", {})
        if summary:
            regression_passed = summary.get("failed", 0) == 0

    # 6. Determinar status
    if not hash_match:
        status = "mismatch"
        reason = (
            "O código mudou depois da coleta da prova (hash diferente). "
            "Isso significa que a prova não vale mais. "
            "Rode capture_proof antes de commitar."
        )
        summary = f"Hash mismatch. Prova: {recorded_hash[:16]}..., Atual: {current_hash[:16]}..."
    elif not regression_passed:
        status = "failed_tests"
        reason = "Prova existe e é recente, mas o regression_test dentro dela falhou."
        summary = "Regression test falhou na prova."
    elif age_minutes > max_age_minutes:
        status = "stale"
        reason = (
            f"Prova existe e o hash bate, mas passou de {max_age_minutes} minutos "
            f"(idade: {age_minutes}min)."
        )
        summary = f"Prova obsoleta ({age_minutes}min > {max_age_minutes}min)."
    else:
        status = "valid"
        reason = ""
        summary = (
            f"Prova válida. Task: {proof_data.get('task_id', 'N/A')}. "
            f"Idade: {age_minutes}min. Hash: {current_hash[:16]}..."
        )

    return {
        "status": status,
        "proof_file": str(proof_file),
        "task_id": proof_data.get("task_id", task_id),
        "age_minutes": age_minutes,
        "hash_match": hash_match,
        "regression_passed": regression_passed,
        "reason": reason,
        "summary": summary,
    }


# ══════════════════════════════════════════════════════════════════════
# Helpers Internos
# ══════════════════════════════════════════════════════════════════════

def _run_git_cmd(cmd: str, cwd: str, timeout: int = 15) -> str:
    """Executa comando git. stdin=DEVNULL evita herança de pipe do MCP."""
    try:
        result = subprocess.run(
            cmd.split(),
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
            close_fds=True,
            timeout=timeout,
            cwd=cwd,
        )
        return result.stdout
    except subprocess.TimeoutExpired:
        return f"ERRO: timeout ({timeout}s): {cmd}"
    except Exception as e:
        return f"ERRO: {type(e).__name__}: {e}"


def _git_rev_parse_head(proj: Path) -> str:
    """Retorna HEAD commit hash ou string vazia."""
    return _run_git_cmd("git rev-parse HEAD", str(proj), 15).strip()


def _git_status_porcelain(proj: Path) -> str:
    """Retorna output literal de git status --porcelain."""
    return _run_git_cmd("git status --porcelain", str(proj), 15)


def _git_diff_no_color(proj: Path) -> str:
    """Retorna output literal de git diff --no-color HEAD."""
    return _run_git_cmd("git diff --no-color HEAD", str(proj), 30)


def _capture_untracked(proj: Path, git_status: str) -> list[dict]:
    """Captura conteúdo de arquivos untracked relevantes.

    Filtra: .py, .gd, .md, .json, .tscn, .tres
    Ignora: diretórios, binários, .mcp_proof/, .godot/, addons/
    """
    untracked = []
    if not git_status:
        return untracked

    relevant_extensions = {'.py', '.gd', '.md', '.json', '.tscn', '.tres', '.cfg', '.toml'}

    for line in git_status.split('\n'):
        line = line.strip()
        if not line:
            continue
        # Linhas untracked começam com "??"
        if not line.startswith('??'):
            continue
        # Extrai path (após "?? ")
        file_path_str = line[3:].strip()
        # Pula diretórios (terminam com /)
        if file_path_str.endswith('/'):
            continue
        file_path = proj / file_path_str
        if not file_path.exists() or not file_path.is_file():
            continue
        # Pula pastas ignoradas
        parts = file_path.parts
        rel = file_path.relative_to(proj)
        if any(p.startswith('.') and p not in ('.gitignore', '.gitattributes', '.env') for p in rel.parts):
            continue
        if 'addons' in rel.parts or '.godot' in rel.parts or PROOF_DIR_NAME in rel.parts:
            continue

        ext = file_path.suffix.lower()
        if ext not in relevant_extensions:
            continue

        try:
            content = file_path.read_text(encoding='utf-8')
        except Exception:
            try:
                content = file_path.read_text(encoding='latin-1')
            except Exception:
                content = f"[BINÁRIO ou encoding desconhecido: {file_path.stat().st_size} bytes]"

        untracked.append({
            "path": str(rel),
            "content": content,
        })

    return untracked


def _compute_worktree_hash(
    head_commit: str,
    git_status: str,
    git_diff: str,
    untracked_files: list[dict],
) -> str:
    """Calcula hash SHA-256 do estado do worktree.

    Concatena: HEAD + status + diff + conteúdo dos untracked (ordenados por path).
    Filtra linhas de .mcp_proof/ do status para evitar auto-contaminação.
    """
    # Filtra .mcp_proof/ do git_status para hash determinístico
    filtered_status_lines = []
    for line in (git_status or "").split('\n'):
        if PROOF_DIR_NAME not in line:
            filtered_status_lines.append(line)
    filtered_status = '\n'.join(filtered_status_lines)

    hasher = hashlib.sha256()
    hasher.update((head_commit or "").encode('utf-8'))
    hasher.update(b'\x00')
    hasher.update((filtered_status or "").encode('utf-8'))
    hasher.update(b'\x00')
    hasher.update((git_diff or "").encode('utf-8'))
    hasher.update(b'\x00')

    # Ordena untracked por path para hash determinístico
    sorted_untracked = sorted(untracked_files, key=lambda x: x["path"])
    for f in sorted_untracked:
        hasher.update(f["path"].encode('utf-8'))
        hasher.update(b'\x00')
        hasher.update(f["content"].encode('utf-8'))
        hasher.update(b'\x00')

    return hasher.hexdigest()


def _sanitize_filename(name: str) -> str:
    """Sanitiza nome para uso em filename.

    Substitui caracteres problemáticos por underscore.
    """
    import re
    # Remove ou substitui caracteres que não são seguros para filename
    sanitized = re.sub(r'[<>:"/\\|?*\s]', '_', name)
    # Remove underscores múltiplos
    sanitized = re.sub(r'_+', '_', sanitized)
    # Remove underscore do início/fim
    sanitized = sanitized.strip('_')
    # Limita tamanho
    if len(sanitized) > 100:
        sanitized = sanitized[:100]
    return sanitized or "unnamed"
