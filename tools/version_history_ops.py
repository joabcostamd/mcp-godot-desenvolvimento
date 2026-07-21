"""version_history_ops.py — Histórico de versões jogáveis (Fatia 1.Q).

Rollup version_history_manage(op=save|list|restore|delete|screenshot).
Salva versões jogáveis com screenshot, data e commit git.
Navegação visual: escolher por screenshot e data, não por hash.

Armazenamento: <project>/.mcp_versions/
  index.json
  <version_id>/
    screenshot.png
    manifest.json

Uso:
    version_history_manage op=save description="Antes de refatorar IA"
    version_history_manage op=list
    version_history_manage op=restore version_id="20260721_143022"
    version_history_manage op=delete version_id="20260721_143022"
    version_history_manage op=screenshot
"""

import base64
import json
from datetime import datetime, timezone
from pathlib import Path

from tools.config_lock import VERSION_HISTORY_LOCK
from tools.subprocess_utils import run_subprocess_safe

ROOT = Path(__file__).resolve().parent.parent

# ── Constantes ──────────────────────────────────────────────────────

VERSIONS_DIRNAME = ".mcp_versions"
INDEX_FILE = "index.json"
MANIFEST_FILE = "manifest.json"
SCREENSHOT_FILE = "screenshot.png"


# ── Helpers de caminho ──────────────────────────────────────────────

def _get_active_project() -> Path:
    """Retorna a raiz do projeto Godot ativo.

    Raises:
        RuntimeError: Se não houver projeto ativo configurado.
    """
    from tools.project_ops import _get_active_project as _gap
    proj = _gap()
    if proj is None or not proj.exists():
        raise RuntimeError(
            "Nenhum projeto Godot ativo. "
            "Use bootstrap_godot_mcp para configurar um projeto primeiro."
        )
    return proj


def _versions_dir(project: Path | None = None) -> Path:
    """Retorna o diretório .mcp_versions dentro do projeto."""
    proj = project or _get_active_project()
    return proj / VERSIONS_DIRNAME


def _load_index(project: Path | None = None) -> list[dict]:
    """Carrega o index.json. Retorna lista vazia se não existir."""
    idx_path = _versions_dir(project) / INDEX_FILE
    if not idx_path.exists():
        return []
    try:
        return json.loads(idx_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []


def _save_index(data: list[dict], project: Path | None = None) -> None:
    """Salva o index.json com lock para escrita concorrente."""
    idx_path = _versions_dir(project) / INDEX_FILE
    idx_path.parent.mkdir(parents=True, exist_ok=True)
    with VERSION_HISTORY_LOCK:
        idx_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


# ── Helpers git ─────────────────────────────────────────────────────

def _git_commit_hash(project: Path) -> str | None:
    """Retorna o hash do commit atual ou None se não for repo git."""
    try:
        result = run_subprocess_safe(
            ["git", "rev-parse", "HEAD"],
            cwd=str(project),
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (TypeError, OSError, ValueError):
        # TypeError: conflito de kwargs (não deve ocorrer após correção)
        # OSError/ValueError: git não instalado ou path inválido
        pass
    return None


def _git_has_commit(commit: str, project: Path) -> bool:
    """Verifica se um commit existe no repositório."""
    # Sanitiza: commit hash deve ser hex de 40 chars (SHA1)
    if not commit or not all(c in "0123456789abcdef" for c in commit.lower()):
        return False
    if len(commit) < 7 or len(commit) > 40:
        return False
    try:
        result = run_subprocess_safe(
            ["git", "cat-file", "-e", commit],
            cwd=str(project),
        )
        return result.returncode == 0
    except (TypeError, OSError, ValueError):
        return False


def _git_is_clean(project: Path) -> bool:
    """Verifica se working tree está limpo.

    Diferente da versão anterior, NÃO assume limpo em caso de erro —
    para _op_restore (destrutivo), é mais seguro falhar do que assumir.
    """
    try:
        result = run_subprocess_safe(
            ["git", "status", "--porcelain"],
            cwd=str(project),
        )
        return result.stdout.strip() == ""
    except (TypeError, OSError, ValueError):
        return False  # na dúvida, não prossegue com operação destrutiva


# ── Helpers screenshot ──────────────────────────────────────────────

def _capture_screenshot() -> dict:
    """Captura screenshot do jogo rodando via runtime bridge.

    Returns:
        {"status": "success", "image_base64": str, "width": int, "height": int}
        ou {"status": "error", "message": str}
    """
    try:
        from runtime_bridge_client import send_bridge_command, BridgeUnavailable
        result = send_bridge_command({"cmd": "screenshot"}, timeout=5.0)
        if result.get("ok"):
            return {
                "status": "success",
                "image_base64": result.get("image_base64", ""),
                "width": result.get("width", 0),
                "height": result.get("height", 0),
            }
        return {
            "status": "error",
            "message": result.get("error", "Falha ao capturar screenshot."),
        }
    except ImportError:
        return {
            "status": "error",
            "message": "runtime_bridge_client não disponível.",
        }
    except Exception as e:
        # BridgeUnavailable ou OSError → jogo não está rodando
        msg = str(e)
        if "BridgeUnavailable" in type(e).__name__ or "BridgeUnavailable" in msg:
            return {
                "status": "error",
                "message": (
                    "Jogo não está rodando em modo debug. "
                    "Abra o jogo (F5 no Godot) antes de capturar screenshot."
                ),
            }
        return {
            "status": "error",
            "message": f"Erro ao capturar screenshot: {msg}",
        }


def _save_screenshot_base64(base64_str: str, dest: Path) -> None:
    """Decodifica base64 e salva como PNG."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    png_bytes = base64.b64decode(base64_str)
    dest.write_bytes(png_bytes)


# ── Operações ───────────────────────────────────────────────────────

def _op_save(params: dict) -> dict:
    """Salva o estado atual como uma versão jogável.

    Captura screenshot do jogo (se rodando), registra commit git e
    armazena metadados no índice de versões.

    Campos em params:
        description: str — descrição da versão (ex: "Antes de refatorar IA")
    """
    description = params.get("description", "").strip()
    if not description:
        return {
            "status": "error",
            "message": "Campo 'description' é obrigatório. "
                       "Descreva esta versão (ex: 'Antes de refatorar IA').",
        }

    try:
        project = _get_active_project()
    except RuntimeError as e:
        return {"status": "error", "message": str(e)}

    versions = _versions_dir(project)

    # Gera version_id único
    timestamp = datetime.now(timezone.utc)
    version_id = timestamp.strftime("%Y%m%d_%H%M%S")
    version_dir = versions / version_id

    # Captura commit git
    commit_hash = _git_commit_hash(project)

    # Tenta capturar screenshot (fail-soft: versão sem screenshot é válida)
    screenshot_result = _capture_screenshot()
    has_screenshot = screenshot_result.get("status") == "success"

    # Salva screenshot
    screenshot_path = ""
    if has_screenshot:
        screenshot_dest = version_dir / SCREENSHOT_FILE
        try:
            _save_screenshot_base64(screenshot_result["image_base64"], screenshot_dest)
            screenshot_path = str(screenshot_dest.relative_to(project))
        except Exception:
            has_screenshot = False

    # Cria manifest
    manifest = {
        "version_id": version_id,
        "timestamp": timestamp.isoformat(),
        "description": description,
        "commit_hash": commit_hash,
        "has_screenshot": has_screenshot,
        "screenshot_path": screenshot_path,
        "screenshot_width": screenshot_result.get("width", 0) if has_screenshot else 0,
        "screenshot_height": screenshot_result.get("height", 0) if has_screenshot else 0,
    }
    manifest_dest = version_dir / MANIFEST_FILE
    manifest_dest.parent.mkdir(parents=True, exist_ok=True)
    manifest_dest.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")

    # Atualiza índice
    index = _load_index(project)
    index_entry = {
        "version_id": version_id,
        "timestamp": timestamp.isoformat(),
        "description": description,
        "commit_hash": commit_hash,
        "has_screenshot": has_screenshot,
        "screenshot_path": screenshot_path,
    }
    index.append(index_entry)
    _save_index(index, project)

    screenshot_note = ""
    if not has_screenshot:
        screenshot_note = (
            " (sem screenshot — jogo não estava rodando. "
            "Use version_history_manage op=screenshot com o jogo aberto para capturar depois)"
        )

    return {
        "status": "success",
        "version_id": version_id,
        "message": f"Versão '{version_id}' salva: {description}{screenshot_note}",
        "commit_hash": commit_hash,
        "has_screenshot": has_screenshot,
        "total_versions": len(index),
    }


def _op_list(params: dict) -> dict:  # noqa: ARG001
    """Lista todas as versões salvas, da mais recente para a mais antiga.

    Retorna versão_id, data, descrição, commit e se tem screenshot.
    """
    try:
        project = _get_active_project()
    except RuntimeError as e:
        return {"status": "error", "message": str(e)}

    index = _load_index(project)

    if not index:
        return {
            "status": "success",
            "versions": [],
            "total": 0,
            "message": "Nenhuma versão salva ainda. Use version_history_manage op=save para criar a primeira.",
        }

    # Ordena por timestamp decrescente (mais recente primeiro)
    sorted_index = sorted(index, key=lambda e: e.get("timestamp", ""), reverse=True)

    # Enriquece com caminho absoluto da screenshot
    versions_display = []
    for entry in sorted_index:
        disp = dict(entry)
        if entry.get("has_screenshot") and entry.get("screenshot_path"):
            disp["screenshot_absolute"] = str(project / entry["screenshot_path"])
        versions_display.append(disp)

    return {
        "status": "success",
        "versions": versions_display,
        "total": len(versions_display),
    }


def _op_restore(params: dict) -> dict:
    """Restaura o código para uma versão anterior (git checkout).

    ATENÇÃO: operação destrutiva. Cria checkpoint do estado atual antes
    de executar o checkout, permitindo desfazer se necessário.

    Campos em params:
        version_id: str — ID da versão para restaurar
    """
    version_id = params.get("version_id", "").strip()
    if not version_id:
        return {
            "status": "error",
            "message": "Campo 'version_id' é obrigatório. Use version_history_manage op=list para ver as versões.",
        }

    # Sanitiza version_id contra path traversal
    if ".." in version_id or "/" in version_id or "\\" in version_id:
        return {
            "status": "error",
            "message": f"version_id inválido: '{version_id}'. Use op=list para ver IDs válidos.",
        }

    try:
        project = _get_active_project()
    except RuntimeError as e:
        return {"status": "error", "message": str(e)}

    index = _load_index(project)

    # Encontra a versão
    entry = next((e for e in index if e["version_id"] == version_id), None)
    if not entry:
        return {
            "status": "error",
            "message": f"Versão '{version_id}' não encontrada. Use op=list para ver as disponíveis.",
            "available_versions": [e["version_id"] for e in index],
        }

    commit_hash = entry.get("commit_hash")
    if not commit_hash:
        return {
            "status": "error",
            "message": f"Versão '{version_id}' não tem commit associado. "
                       "Foi salva fora de um repositório git?",
        }

    if not _git_has_commit(commit_hash, project):
        return {
            "status": "error",
            "message": f"Commit '{commit_hash}' da versão '{version_id}' não existe mais "
                       "no repositório. Pode ter sido removido por rebase ou garbage collection.",
        }

    # Verifica working tree limpo (não assume limpo em caso de erro)
    if not _git_is_clean(project):
        return {
            "status": "error",
            "message": "Working tree não está limpo. Faça commit ou stash das alterações "
                       "antes de restaurar uma versão.",
        }

    # Salva HEAD atual como checkpoint de segurança
    current_head = _git_commit_hash(project)
    if not current_head:
        return {
            "status": "error",
            "message": "Não foi possível obter o commit atual. O projeto está em um repositório git?",
        }

    # Cria checkpoint do estado atual via safety (arquivos modificados)
    try:
        from tools.safety import checkpoint
        # Faz checkpoint dos arquivos rastreados modificados
        result = run_subprocess_safe(
            ["git", "diff", "--name-only", "HEAD"],
            cwd=str(project),
        )
        if result.returncode == 0:
            for fname in result.stdout.strip().splitlines():
                fname = fname.strip()
                if fname:
                    checkpoint(project / fname, project)
    except Exception:
        pass  # checkpoint é best-effort, não bloqueia restore

    # Tenta checkout (usa -- para evitar ambiguidade com paths)
    try:
        result = run_subprocess_safe(
            ["git", "checkout", commit_hash, "--"],
            cwd=str(project),
        )
        if result.returncode != 0:
            return {
                "status": "error",
                "message": f"Falha ao fazer checkout do commit '{commit_hash}': {result.stderr.strip()}",
                "commit_hash": commit_hash,
                "previous_head": current_head,
            }
    except (TypeError, OSError, ValueError) as e:
        return {
            "status": "error",
            "message": f"Erro ao executar git checkout: {e}",
            "commit_hash": commit_hash,
            "previous_head": current_head,
        }

    return {
        "status": "success",
        "version_id": version_id,
        "description": entry.get("description", ""),
        "commit_hash": commit_hash,
        "previous_head": current_head,
        "message": (
            f"Restaurado para versão '{version_id}': {entry.get('description', '')}. "
            f"HEAD anterior: {current_head[:8]}. "
            "Reabra o projeto no Godot e rode o jogo (F5) para testar."
        ),
    }


def _op_delete(params: dict) -> dict:
    """Remove uma versão do histórico.

    Remove entrada do índice e arquivos associados (screenshot, manifest).

    Campos em params:
        version_id: str — ID da versão para remover
    """
    version_id = params.get("version_id", "").strip()
    if not version_id:
        return {
            "status": "error",
            "message": "Campo 'version_id' é obrigatório.",
        }

    # Sanitiza version_id contra path traversal
    if ".." in version_id or "/" in version_id or "\\" in version_id:
        return {
            "status": "error",
            "message": f"version_id inválido: '{version_id}'.",
        }

    try:
        project = _get_active_project()
    except RuntimeError as e:
        return {"status": "error", "message": str(e)}

    index = _load_index(project)

    entry = next((e for e in index if e["version_id"] == version_id), None)
    if not entry:
        return {
            "status": "error",
            "message": f"Versão '{version_id}' não encontrada.",
            "available_versions": [e["version_id"] for e in index],
        }

    # Remove diretório da versão
    version_dir = _versions_dir(project) / version_id
    if version_dir.exists():
        import shutil
        shutil.rmtree(version_dir, ignore_errors=True)

    # Remove do índice
    index = [e for e in index if e["version_id"] != version_id]
    _save_index(index, project)

    return {
        "status": "success",
        "version_id": version_id,
        "message": f"Versão '{version_id}' removida. {len(index)} versão(ões) restante(s).",
    }


def _op_screenshot(params: dict) -> dict:  # noqa: ARG001
    """Captura um screenshot do jogo rodando e retorna como base64.

    O jogo precisa estar rodando em modo debug (F5 no Godot).

    O screenshot NÃO é associado a uma versão — use op=save para isso.
    """
    try:
        project = _get_active_project()
    except RuntimeError as e:
        return {"status": "error", "message": str(e)}

    result = _capture_screenshot()

    if result.get("status") != "success":
        return result

    # Salva screenshot no diretório de versões (soltas, sem versão associada)
    screenshots_dir = _versions_dir(project) / "_screenshots"
    screenshots_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    dest = screenshots_dir / f"{timestamp}.png"

    try:
        _save_screenshot_base64(result["image_base64"], dest)
    except Exception as e:
        return {
            "status": "error",
            "message": f"Screenshot capturado mas falha ao salvar: {e}",
        }

    return {
        "status": "success",
        "path": str(dest.relative_to(project)),
        "width": result.get("width", 0),
        "height": result.get("height", 0),
        "message": f"Screenshot salvo em {dest.relative_to(project)}",
    }


# ── Rollup ──────────────────────────────────────────────────────────

_OPS = {
    "save": _op_save,
    "list": _op_list,
    "restore": _op_restore,
    "delete": _op_delete,
    "screenshot": _op_screenshot,
}


def version_history_manage(op: str, params: dict | None = None) -> dict:
    """Gerencia histórico de versões jogáveis.

    Args:
        op: Operação (save|list|restore|delete|screenshot).
        params: Parâmetros específicos da operação.

    Returns:
        dict com resultado da operação.
    """
    if op not in _OPS:
        from difflib import get_close_matches
        suggestions = get_close_matches(op, list(_OPS.keys()), n=3)
        return {
            "status": "error",
            "message": f"Operação '{op}' desconhecida.",
            "available_ops": list(_OPS.keys()),
            "suggestions": suggestions,
        }

    return _OPS[op](params or {})
