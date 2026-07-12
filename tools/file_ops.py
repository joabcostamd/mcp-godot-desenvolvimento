"""file_ops — Operações de leitura, escrita e manipulação de arquivos.

Fase 1: inspect_project, read_file, write_file, delete_file, move_file.
"""

from pathlib import Path
from typing import Optional

from tools.project_ops import _get_active_project, _check_path_traversal
from tools.safety import checkpoint, push_undo


# ── API Pública ─────────────────────────────────────────────────────

def inspect_project(filter_type: str = "all") -> dict:
    """Lista arquivos do projeto ativo por categoria.

    Args:
        filter_type: "scenes", "scripts", "assets", ou "all".

    Returns:
        {"status": "success", "scenes": [...], "scripts": [...], "assets": [...]}
    """
    proj = _get_active_project()

    scenes = sorted([str(p.relative_to(proj)) for p in proj.glob("**/*.tscn")])
    scripts = sorted([str(p.relative_to(proj)) for p in proj.glob("**/*.gd")])
    assets = sorted([
        str(p.relative_to(proj))
        for p in proj.glob("**/*")
        if p.suffix.lower() in (".png", ".jpg", ".jpeg", ".bmp", ".svg",
                                 ".wav", ".ogg", ".mp3", ".tres", ".res",
                                 ".glb", ".gltf", ".obj")
    ])

    result = {"status": "success"}
    if filter_type in ("scenes", "all"):
        result["scenes"] = scenes
    if filter_type in ("scripts", "all"):
        result["scripts"] = scripts
    if filter_type in ("assets", "all"):
        result["assets"] = assets

    return result


def read_file(path: str, start_line: int | None = None, end_line: int | None = None) -> dict:
    """Lê o conteúdo de um arquivo do projeto.

    Args:
        path: Caminho relativo ao projeto.
        start_line: Linha inicial (1-indexed, opcional).
        end_line: Linha final inclusiva (1-indexed, opcional).

    Returns:
        {"status": "success", "content": str, "lines": [int, int]}
        ou {"status": "error", "message": str}
    """
    proj = _get_active_project()

    violation = _check_path_traversal(path, proj)
    if violation:
        return {"status": "error", "message": violation}

    full_path = proj / path
    if not full_path.exists():
        return {
            "status": "error",
            "message": f"Arquivo '{path}' não encontrado no projeto. "
                       f"Use inspect_project para listar arquivos disponíveis.",
        }

    if not full_path.is_file():
        return {
            "status": "error",
            "message": f"'{path}' é um diretório, não um arquivo.",
        }

    try:
        content = full_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return {
            "status": "error",
            "message": f"'{path}' não é um arquivo de texto (binário detectado).",
        }

    all_lines = content.splitlines()
    total = len(all_lines)

    if start_line is not None or end_line is not None:
        s = max(1, (start_line or 1)) - 1  # 0-indexed
        e = min(total, (end_line or total))
        selected = all_lines[s:e]
        content = "\n".join(selected)
        return {
            "status": "success",
            "content": content,
            "lines": [s + 1, e],
            "total_lines": total,
        }

    return {"status": "success", "content": content, "total_lines": total}


def write_file(path: str, content: str, mode: str = "create",
                skip_gdscript_validation: bool = False) -> dict:
    """Escreve ou modifica um arquivo no projeto.

    Args:
        path: Caminho relativo ao projeto.
        content: Conteúdo a escrever.
        mode: "create" (só se não existir), "overwrite" (substitui), "append" (adiciona ao final).
        skip_gdscript_validation: Se True, pula validação de sintaxe GDScript (apenas emergências).

    Returns:
        {"status": "success", "path": str, "backup_id": str|None}
        ou {"status": "error", "message": str}
    """
    proj = _get_active_project()

    # Limite de tamanho (10MB) para evitar consumo excessivo
    MAX_FILE_SIZE = 10 * 1024 * 1024
    if len(content.encode('utf-8')) > MAX_FILE_SIZE:
        return {"status": "error", "message": f"Conteúdo excede {MAX_FILE_SIZE//1024//1024}MB — abortado"}

    violation = _check_path_traversal(path, proj)
    if violation:
        return {"status": "error", "message": violation}

    # ── GDScript Validation Gate (GRUPO 1 auditoria) ──
    # Todo .gd escrito via write_file passa por validação de sintaxe.
    # Isso fecha a brecha onde a IA podia contornar safe_write_gdscript
    # e salvar código quebrado diretamente.
    if path.endswith(".gd") and not skip_gdscript_validation:
        try:
            from tools.validate_write import validate_gdscript_syntax
            validation = validate_gdscript_syntax(content)
            if not validation.get("valid", True):
                return {
                    "status": "error",
                    "message": "❌ GDScript INVÁLIDO — escrita BLOQUEADA. "
                               "Corrija os erros abaixo ou use safe_write_gdscript para validação completa.",
                    "validation_errors": validation.get("errors"),
                    "hint": "Use skip_gdscript_validation=True apenas em emergências.",
                }
        except Exception:
            pass  # Se validação falhar por infra, não bloqueia

    full_path = proj / path
    full_path.parent.mkdir(parents=True, exist_ok=True)

    backup_id = None

    if mode == "create":
        if full_path.exists():
            return {
                "status": "error",
                "message": f"Arquivo '{path}' já existe. Use mode='overwrite' para sobrescrever "
                           f"ou mode='append' para adicionar conteúdo.",
            }
        # B16 FIX: Checkpoint tambem em create (seguranca se arquivo for recriado)
        if full_path.parent.exists():
            backup_id = checkpoint(path, proj)
    elif mode == "overwrite":
        if full_path.exists():
            backup_id = checkpoint(path, proj)
    elif mode == "append":
        if full_path.exists():
            backup_id = checkpoint(path, proj)
            existing = full_path.read_text(encoding="utf-8")
            content = existing + content
    else:
        return {
            "status": "error",
            "message": f"Mode '{mode}' inválido. Use 'create', 'overwrite', ou 'append'.",
        }

    full_path.write_text(content, encoding="utf-8")
    return {"status": "success", "path": path, "backup_id": backup_id}


def delete_file(path: str) -> dict:
    """Remove um arquivo do projeto (com checkpoint).

    Args:
        path: Caminho relativo ao projeto.

    Returns:
        {"status": "success", "backup_id": str}
        ou {"status": "error", "message": str}
    """
    proj = _get_active_project()

    violation = _check_path_traversal(path, proj)
    if violation:
        return {"status": "error", "message": violation}

    full_path = proj / path

    if not full_path.exists():
        return {
            "status": "error",
            "message": f"Arquivo '{path}' não encontrado. Use inspect_project para listar arquivos.",
        }

    if full_path.is_dir():
        return {
            "status": "error",
            "message": f"'{path}' é um diretório. delete_file só remove arquivos individuais.",
        }

    backup_id = checkpoint(path, proj)
    full_path.unlink()

    return {"status": "success", "backup_id": backup_id or "unknown"}


def move_file(from_path: str, to_path: str) -> dict:
    """Move/renomeia um arquivo e atualiza referências no projeto.

    Varre .tscn/.tres/.gd e project.godot por referências a from_path e as atualiza.

    Args:
        from_path: Caminho relativo atual.
        to_path: Novo caminho relativo.

    Returns:
        {"status": "success", "files_updated": [str]}
        ou {"status": "error", "message": str}
    """
    proj = _get_active_project()

    for p in [from_path, to_path]:
        violation = _check_path_traversal(p, proj)
        if violation:
            return {"status": "error", "message": violation}

    src = proj / from_path
    dst = proj / to_path

    if not src.exists():
        return {
            "status": "error",
            "message": f"Arquivo origem '{from_path}' não encontrado.",
        }

    if dst.exists():
        return {
            "status": "error",
            "message": f"Arquivo destino '{to_path}' já existe. Escolha outro nome.",
        }

    # Checkpoint
    checkpoint(from_path, proj)

    # Cria diretório destino
    dst.parent.mkdir(parents=True, exist_ok=True)

    # Move
    src.rename(dst)

    # Atualiza referências em arquivos de texto do projeto
    from_res = f"res://{from_path}"
    to_res = f"res://{to_path}"
    files_updated = []

    for ext in ["*.tscn", "*.tres", "*.gd"]:
        for f in proj.glob(f"**/{ext}"):
            content = f.read_text(encoding="utf-8")
            if from_res in content or from_path in content:
                checkpoint(str(f.relative_to(proj)), proj)
                new_content = content.replace(from_res, to_res)
                new_content = new_content.replace(from_path, to_path)
                f.write_text(new_content, encoding="utf-8")
                files_updated.append(str(f.relative_to(proj)))

    # project.godot
    godot_file = proj / "project.godot"
    if godot_file.exists():
        content = godot_file.read_text(encoding="utf-8")
        if from_res in content or from_path in content:
            checkpoint("project.godot", proj)
            new_content = content.replace(from_res, to_res).replace(from_path, to_path)
            godot_file.write_text(new_content, encoding="utf-8")
            files_updated.append("project.godot")

    return {"status": "success", "files_updated": files_updated}

