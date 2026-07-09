"""script_ops — Operações de geração e manipulação de scripts GDScript.

Fase 2: generate_gdscript, attach_script, detach_script,
validate_gdscript_syntax, add_script_variable, add_script_signal.
"""

import json
import re
import subprocess
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, TemplateNotFound

from tools.classdb import get_godot_bin, get_config
from tools.project_ops import _get_active_project, _check_path_traversal
from tools.safety import checkpoint

ROOT = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = ROOT / "templates"

# ── GAP #2: Hot Reload Auto-Trigger ──────────────────────────────────

_auto_hot_reload: bool = True  # Pode ser desabilitado com disable_auto_hot_reload


def _trigger_hot_reload(file_path: str) -> None:
    """Dispara hot reload no game bridge se jogo estiver rodando.

    Chamado automaticamente após generate_gdscript, add_script_variable,
    add_script_signal, attach_script. Não bloqueia em caso de falha —
    o hot reload é best-effort.
    """
    if not _auto_hot_reload:
        return
    try:
        from tools.bridge import is_game_connected, reload_resource
        if is_game_connected():
            reload_resource(file_path)
    except Exception:
        pass  # Best-effort: se falhar, o jogo continua rodando


def enable_auto_hot_reload() -> dict:
    """Ativa hot reload automático (padrão)."""
    global _auto_hot_reload
    _auto_hot_reload = True
    return {"status": "success", "auto_hot_reload": True}


def disable_auto_hot_reload() -> dict:
    """Desativa hot reload automático."""
    global _auto_hot_reload
    _auto_hot_reload = False
    return {"status": "success", "auto_hot_reload": False}

# ── Jinja2 ──────────────────────────────────────────────────────────

_jinja_env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))


def _list_templates() -> list[str]:
    """Lista templates disponíveis em templates/."""
    return [p.stem for p in TEMPLATES_DIR.glob("*.gd")]


# ── API Pública ─────────────────────────────────────────────────────

def generate_gdscript(template: str, variables: dict, save_path: str) -> dict:
    """Gera um script GDScript a partir de um template Jinja2.

    Args:
        template: Nome do template (sem extensão .gd).
        variables: Dicionário de variáveis para o template.
        save_path: Caminho relativo ao projeto para salvar.

    Returns:
        {"status": "success", "content": str, "saved_to": str}
        ou {"status": "error", "message": str}
    """
    proj = _get_active_project()

    violation = _check_path_traversal(save_path, proj)
    if violation:
        return {"status": "error", "message": violation}

    try:
        tmpl = _jinja_env.get_template(f"{template}.gd")
    except TemplateNotFound:
        available = _list_templates()
        return {
            "status": "error",
            "message": f"Template '{template}' não encontrado. "
                       f"Templates disponíveis: {available}. "
                       f"Para lógica que nenhum template cobre, escreva GDScript "
                       f"diretamente via write_file e valide com validate_gdscript_syntax.",
        }

    content = tmpl.render(**variables)
    full_path = proj / save_path
    full_path.parent.mkdir(parents=True, exist_ok=True)

    if full_path.exists():
        checkpoint(save_path, proj)

    full_path.write_text(content, encoding="utf-8")

    _trigger_hot_reload(save_path)

    return {"status": "success", "content": content, "saved_to": save_path}


def attach_script(scene_path: str, node_path: str, script_path: str) -> dict:
    """Anexa um script GDScript a um nó em uma cena.

    Usa [ext_resource] + ExtResource("id") (formato Godot 4), NÃO
    inline script="res://..." que o Godot 4 ignora ao carregar.

    Args:
        scene_path: Cena alvo.
        node_path: Nó que receberá o script.
        script_path: Caminho do script .gd.

    Returns:
        {"status": "success"}
    """
    proj = _get_active_project()
    full_path = proj / scene_path

    if not full_path.exists():
        return {"status": "error", "message": f"Cena '{scene_path}' não encontrada no projeto. Use inspect_project para listar cenas disponíveis no projeto ativo."}

    script_full = proj / script_path
    if not script_full.exists():
        return {"status": "error", "message": f"Script '{script_path}' não encontrado. Crie o script primeiro com generate_gdscript ou write_file, depois use attach_script para vinculá-lo ao nó."}

    content = full_path.read_text(encoding="utf-8")
    lines = content.splitlines(keepends=True)

    # ── Encontra o nó alvo ──────────────────────────────────────
    target_line = -1
    if node_path == ".":
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith("[node ") and 'parent="' not in stripped:
                target_line = i
                break
        if target_line < 0:
            for i, line in enumerate(lines):
                if line.strip().startswith("[node "):
                    target_line = i
                    break
    else:
        search_name = node_path.lstrip("./")
        for i, line in enumerate(lines):
            if f'name="{search_name}"' in line and line.strip().startswith("[node "):
                target_line = i
                break

    if target_line < 0:
        return {"status": "error", "message": f"Nó '{node_path}' não encontrado na cena '{scene_path}'. Use load_scene_tree para ver a hierarquia de nós e confirmar o path correto. Para o nó raiz, use '.'."}

    checkpoint(scene_path, proj)

    # ── Gera ID único para ext_resource ─────────────────────────
    existing_ids = set()
    for line in lines:
        m = re.search(r'id="([^"]+)"', line)
        if m:
            existing_ids.add(m.group(1))
    ext_id = "1_script"
    counter = 1
    while ext_id in existing_ids:
        counter += 1
        ext_id = f"{counter}_script"

    # ── Insere [ext_resource] após a linha do header ───────────
    res_line = f'[ext_resource type="Script" path="res://{script_path}" id="{ext_id}"]\n'
    header_idx = -1
    for i, line in enumerate(lines):
        if line.strip().startswith("[gd_scene"):
            header_idx = i
            break
    if header_idx >= 0:
        lines.insert(header_idx + 1, res_line)
        if target_line > header_idx:
            target_line += 1
    else:
        lines.insert(0, res_line)
        target_line += 1

    # ── Incrementa load_steps ──────────────────────────────────
    for i, line in enumerate(lines):
        m = re.match(r'\[gd_scene\s+.*load_steps=(\d+)', line)
        if m:
            old_steps = int(m.group(1))
            lines[i] = line.replace(f"load_steps={old_steps}", f"load_steps={old_steps + 1}")
            break

    # ── Adiciona/atualiza script no nó ─────────────────────────
    target = lines[target_line].rstrip()
    ext_ref = f'script = ExtResource("{ext_id}")'
    if 'script=' in target:
        # Substitui inline script="..." ou script = ExtResource("...")
        lines[target_line] = re.sub(
            r'script\s*=\s*(ExtResource\("[^"]*"\)|"[^"]*")',
            ext_ref,
            target
        ) + "\n"
    else:
        # Garante que o nó fecha com "] na própria linha
        if not target.endswith("]"):
            target = target + "]"
        lines[target_line] = target + f"\n{ext_ref}\n"

    full_path.write_text("".join(lines), encoding="utf-8")

    # B21 FIX: Deduplica ext_resource e propriedades apos attach
    from tools.scene_ops import _deduplicate_tscn_lines
    current_lines = full_path.read_text(encoding="utf-8").splitlines(keepends=True)
    deduped = _deduplicate_tscn_lines(current_lines)
    full_path.write_text("".join(deduped), encoding="utf-8")

    _trigger_hot_reload(script_path)

    return {"status": "success"}


def detach_script(scene_path: str, node_path: str) -> dict:
    """Remove o script anexado de um nó.

    Remove também a entrada [ext_resource] correspondente e
    decrementa load_steps.

    Args:
        scene_path: Cena alvo.
        node_path: Nó cujo script será removido.

    Returns:
        {"status": "success"}
    """
    proj = _get_active_project()
    full_path = proj / scene_path

    if not full_path.exists():
        return {"status": "error", "message": f"Cena '{scene_path}' não encontrada."}

    lines = full_path.read_text(encoding="utf-8").splitlines(keepends=True)

    # ── Encontra o nó alvo ──────────────────────────────────────
    target_line = -1
    if node_path == ".":
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith("[node ") and 'parent="' not in stripped:
                target_line = i
                break
        if target_line < 0:
            for i, line in enumerate(lines):
                if line.strip().startswith("[node "):
                    target_line = i
                    break
    else:
        search_name = node_path.lstrip("./")
        for i, line in enumerate(lines):
            if f'name="{search_name}"' in line and line.strip().startswith("[node "):
                target_line = i
                break

    if target_line < 0:
        return {"status": "error", "message": f"Nó '{node_path}' não encontrado."}

    # ── Encontra script = ExtResource("...") nas linhas do nó ──
    ext_id = None
    script_line = -1
    # Busca na linha do header e nas linhas seguintes (propriedades do nó)
    for i in range(target_line, len(lines)):
        line = lines[i]
        if line.strip().startswith("[node ") and i > target_line:
            break  # próximo nó, para
        m = re.search(r'script\s*=\s*ExtResource\("([^"]+)"\)', line)
        if m:
            ext_id = m.group(1)
            script_line = i
            break
        if 'script="' in line:
            m2 = re.search(r'script="([^"]*)"', line)
            if m2:
                # script inline — não tem ext_resource separado
                script_line = i
                break

    if script_line < 0:
        return {"status": "success", "note": "Nó não possui script anexado."}

    checkpoint(scene_path, proj)

    # ── Remove a linha do script ───────────────────────────────
    lines.pop(script_line)

    # ── Remove [ext_resource] correspondente ───────────────────
    if ext_id:
        for i, line in enumerate(lines):
            if line.strip().startswith("[ext_resource ") and f'id="{ext_id}"' in line:
                lines.pop(i)
                # Decrementa load_steps
                for j, l2 in enumerate(lines):
                    m2 = re.match(r'\[gd_scene\s+.*load_steps=(\d+)', l2)
                    if m2:
                        old = int(m2.group(1))
                        lines[j] = l2.replace(f"load_steps={old}", f"load_steps={old - 1}")
                        break
                break

    full_path.write_text("".join(lines), encoding="utf-8")

    return {"status": "success"}


def validate_gdscript_syntax(script_path: str) -> dict:
    """Valida a sintaxe de um script GDScript usando o Godot.

    Args:
        script_path: Caminho relativo do script.

    Returns:
        {"status": "success", "valid": True}
        ou {"status": "error", "valid": False, "errors": [str]}
    """
    proj = _get_active_project()
    full_path = proj / script_path

    if not full_path.exists():
        return {"status": "error", "message": f"Script '{script_path}' não encontrado."}

    godot = get_godot_bin()
    cfg = get_config()
    timeout = cfg.get("timeouts", {}).get("compile", 60)

    # Cria cena temporária com o script anexado para forçar parse
    tmp_scene = proj / ".mcp_validate_temp.tscn"
    scene_content = f"""[gd_scene load_steps=2 format=2]

[node name="Validator" type="Node"]
script = ExtResource("1_validator")

[ext_resource type="Script" path="res://{script_path}" id="1_validator"]
"""
    tmp_scene.write_text(scene_content, encoding="utf-8")

    try:
        result = subprocess.run(
            [godot, "--headless", "--editor", "--quit", "--path", str(proj)],
            capture_output=True, text=True, timeout=timeout,
            stdin=subprocess.DEVNULL,
        )
        combined = result.stdout + "\n" + result.stderr
        errors = []
        for line in combined.splitlines():
            if any(kw in line for kw in ("ERROR", "SCRIPT ERROR", "Parse Error", "error:")):
                errors.append(line.strip())

        if tmp_scene.exists():
            tmp_scene.unlink()

        if errors:
            return {"status": "error", "valid": False, "errors": errors}
        return {"status": "success", "valid": True}
    except subprocess.TimeoutExpired:
        return {"status": "error", "message": "Timeout ao validar script."}
    except Exception as e:
        return {"status": "error", "message": f"Erro ao validar: {e}"}


def add_script_variable(
    script_path: str, var_name: str, var_type: str = "Variant",
    default_value: str | None = None, export: bool = False
) -> dict:
    """Adiciona uma variável a um script GDScript.

    Args:
        script_path: Caminho do script.
        var_name: Nome da variável.
        var_type: Tipo (ex: 'int', 'float', 'String', 'Variant').
        default_value: Valor default como string GDScript.
        export: Se True, usa @export.

    Returns:
        {"status": "success"}
    """
    from tools.project_ops import _check_path_traversal
    proj = _get_active_project()
    full_path = proj / script_path

    violation = _check_path_traversal(script_path, proj)
    if violation:
        return {"status": "error", "message": violation}

    if not full_path.exists():
        return {"status": "error", "message": f"Script '{script_path}' não encontrado."}

    content = full_path.read_text(encoding="utf-8")
    lines = content.splitlines(keepends=True)

    # ── Detecta duplicata ──────────────────────────────────────
    for line in lines:
        stripped = line.strip()
        # Padrão: "var nome" ou "@export var nome"
        if re.match(r'(@export\s+)?var\s+' + re.escape(var_name) + r'\b', stripped):
            return {
                "status": "error",
                "message": f"Variável '{var_name}' já existe no script '{script_path}'. "
                           f"Use outro nome ou edite o valor existente manualmente.",
            }

    insert_at = 0
    for i, line in enumerate(lines):
        if line.strip().startswith("extends "):
            insert_at = i + 1
            break

    for i in range(insert_at, len(lines)):
        stripped = lines[i].strip()
        if stripped.startswith("var ") or stripped.startswith("signal "):
            insert_at = i + 1

    export_prefix = "@export " if export else ""
    var_decl = f"{export_prefix}var {var_name}"
    if var_type and var_type != "Variant":
        var_decl += f": {var_type}"
    if default_value is not None:
        var_decl += f" = {default_value}"
    var_decl += "\n"

    checkpoint(script_path, proj)
    lines.insert(insert_at, var_decl)
    full_path.write_text("".join(lines), encoding="utf-8")

    _trigger_hot_reload(script_path)

    return {"status": "success"}


def add_script_signal(script_path: str, signal_name: str, args: list[str] | None = None) -> dict:
    """Adiciona uma declaração de signal a um script GDScript.

    Args:
        script_path: Caminho do script.
        signal_name: Nome do sinal.
        args: Lista de nomes de argumentos.

    Returns:
        {"status": "success"}
    """
    proj = _get_active_project()
    full_path = proj / script_path

    if not full_path.exists():
        return {"status": "error", "message": f"Script '{script_path}' não encontrado."}

    content = full_path.read_text(encoding="utf-8")
    lines = content.splitlines(keepends=True)

    insert_at = 0
    for i, line in enumerate(lines):
        if line.strip().startswith("extends "):
            insert_at = i + 1
            break

    args_str = ", ".join(args) if args else ""
    signal_decl = f"signal {signal_name}({args_str})\n"

    checkpoint(script_path, proj)
    lines.insert(insert_at, signal_decl)
    full_path.write_text("".join(lines), encoding="utf-8")

    _trigger_hot_reload(script_path)

    return {"status": "success"}
