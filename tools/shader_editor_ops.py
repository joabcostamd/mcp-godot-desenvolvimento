"""shader_editor_ops — Leitura, edição e validação de shaders já
existentes no projeto (complementa shader_generate, que só cria do zero).

Feature: Shader — editar shader existente.
"""

import re
import subprocess
from pathlib import Path


def read_shader(shader_path: str, project_path: str | None = None) -> dict:
    """Lê o conteúdo de um .gdshader existente."""
    proj = _resolve_project(project_path)
    if isinstance(proj, dict) and proj.get("status") == "error":
        return proj

    full_path = _resolve_res_path(proj, shader_path)
    if not full_path.exists():
        return {"status": "error", "message": f"Shader não encontrado: {shader_path}"}

    try:
        content = full_path.read_text(encoding="utf-8")
    except Exception as e:
        return {"status": "error", "message": f"Erro ao ler shader: {e}"}

    return {"status": "success", "path": shader_path, "content": content}


def get_shader_params(shader_path: str, project_path: str | None = None) -> dict:
    """Extrai as declarações 'uniform' de um shader, com nome, tipo e hint."""
    read_result = read_shader(shader_path, project_path)
    if read_result.get("status") == "error":
        return read_result

    content = read_result["content"]
    params = []
    pattern = re.compile(
        r'uniform\s+(\w+)\s+(\w+)\s*(?::\s*(\w+)(?:\(([^)]*)\))?)?\s*(?:=\s*([^;]+))?;'
    )
    for m in pattern.finditer(content):
        var_type, var_name, hint, hint_args, default = m.groups()
        params.append({
            "name": var_name,
            "type": var_type,
            "hint": hint,
            "hint_args": hint_args.strip() if hint_args else None,
            "default": default.strip() if default else None,
        })

    return {"status": "success", "path": shader_path, "params": params, "total": len(params)}


def edit_shader(
    shader_path: str,
    new_code: str,
    project_path: str | None = None,
    validate: bool = True,
) -> dict:
    """Escreve novo conteúdo num .gdshader, validando antes se validate=True."""
    proj = _resolve_project(project_path)
    if isinstance(proj, dict) and proj.get("status") == "error":
        return proj

    full_path = _resolve_res_path(proj, shader_path)

    if validate:
        validation = _validate_shader_code(new_code, proj)
        if validation.get("status") == "error":
            return {
                "status": "error",
                "message": "Shader inválido, não foi escrito.",
                "validation_error": validation.get("message"),
                "stderr": validation.get("stderr"),
            }

    full_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        full_path.write_text(new_code, encoding="utf-8")
    except Exception as e:
        return {"status": "error", "message": f"Erro ao escrever shader: {e}"}

    return {"status": "success", "path": shader_path, "validated": validate, "message": "Shader atualizado."}


def _validate_shader_code(code: str, proj: Path) -> dict:
    """Valida sintaxe de shader usando RenderingServer via script headless."""
    from tools.classdb import get_godot_bin
    godot_path = get_godot_bin()

    validator_script = proj / "_shader_validate_tmp.gd"
    escaped_code = code.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")

    validator_content = f'''extends SceneTree

func _init():
    var shader := Shader.new()
    shader.code = "{escaped_code}"
    var rid := RenderingServer.shader_create()
    RenderingServer.shader_set_code(rid, shader.code)
    print("SHADER_VALIDATION_OK")
    quit()
'''
    try:
        validator_script.write_text(validator_content, encoding="utf-8")
        result = subprocess.run(
            [godot_path, "--headless", "--script", str(validator_script), "--path", str(proj)],
            capture_output=True, text=True, timeout=30,
        )
        ok = "SHADER_VALIDATION_OK" in result.stdout and "SCRIPT ERROR" not in result.stderr
        return {
            "status": "success" if ok else "error",
            "message": "Shader válido." if ok else "Shader inválido — ver stderr.",
            "stdout": result.stdout,
            "stderr": result.stderr,
        }
    except subprocess.TimeoutExpired:
        return {"status": "error", "message": "Timeout ao validar shader (30s)."}
    finally:
        if validator_script.exists():
            validator_script.unlink()


def _resolve_project(project_path: str | None = None) -> Path:
    if project_path:
        p = Path(project_path)
        if p.exists():
            return p
        return {"status": "error", "message": f"Projeto não encontrado: {project_path}"}
    try:
        from tools.project_ops import _get_active_project
        return Path(_get_active_project())
    except Exception:
        return {"status": "error", "message": "Nenhum projeto ativo definido."}


def _resolve_res_path(proj: Path, res_path: str) -> Path:
    p = res_path.replace("res://", "")
    full = proj / p
    if not full.is_absolute():
        full = proj / p
    return full
