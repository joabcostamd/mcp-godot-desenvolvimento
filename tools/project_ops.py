"""project_ops — Operações de criação e gestão de projetos Godot.

Fase 1: validate_godot_version, set_active_project, create_project,
get_project_settings, set_project_setting, set_main_scene.
"""

import json
import os as _os
import re
import subprocess
from pathlib import Path
from typing import Optional

from tools.classdb import get_godot_bin, get_config
from tools.safety import checkpoint

ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT / "config.json"


def _save_config_atomic(cfg: dict) -> None:
    """Salva config.json com escrita atômica (tmp + rename)."""
    tmp = CONFIG_PATH.with_suffix('.json.tmp')
    tmp.write_text(json.dumps(cfg, indent=2), encoding='utf-8')
    _os.replace(str(tmp), str(CONFIG_PATH))

# ── Estado interno ──────────────────────────────────────────────────

_active_project: Optional[Path] = None


def _get_projects_root() -> Path:
    """Retorna a pasta raiz de projetos (lê de config.json).
    
    Se projects_root nao estiver configurado, usa USERPROFILE/GodotProjects.
    A pasta é criada automaticamente se não existir.
    """
    cfg = get_config()
    root_str = cfg.get("projects_root", "")
    if root_str:
        root = Path(root_str)
    else:
        root = Path.home() / "GodotProjects"
    root.mkdir(parents=True, exist_ok=True)
    return root


def _get_active_project() -> Path:
    """Retorna o projeto ativo (lê de config.json se não setado)."""
    global _active_project
    if _active_project is not None:
        return _active_project
    cfg = get_config()
    default = cfg.get("default_project", "example_project")
    proj = Path(default)
    if not proj.is_absolute():
        proj = ROOT / proj
    _active_project = proj
    return proj


def _resolve_project_path(path: str) -> Path:
    """Resolve um path de projeto (absoluto ou relativo à pasta de projetos).
    
    Se o path for relativo, usa _get_projects_root() como base.
    Isso garante que todos os projetos fiquem na pasta fixa GodotProjects.
    """
    p = Path(path)
    if not p.is_absolute():
        p = _get_projects_root() / p
    return p.resolve()


def _check_path_traversal(path: str, project_root: Path) -> Optional[str]:
    """Verifica se um path tenta sair da raiz do projeto (path traversal).

    Returns:
        Mensagem de erro se violação, None se OK.
    """
    # Verificação 1: nenhum componente '..' no path
    parts = Path(path).parts
    if '..' in parts:
        return f"Path contém '..': '{path}' — path traversal bloqueado"

    try:
        full = (project_root / path).resolve()
        proj_resolved = project_root.resolve()
        full.relative_to(proj_resolved)
        return None
    except ValueError:
        return f"Path traversal não permitido: '{path}' tenta acessar fora da raiz do projeto."


# ── API Pública ─────────────────────────────────────────────────────

def validate_godot_version() -> dict:
    """Valida que o Godot instalado é 4.7.x.

    Returns:
        {"status": "success", "version": str, "valid": True}
        ou {"status": "error", "message": str, "found_version": str}
    """
    godot = get_godot_bin()
    try:
        from tools.subprocess_utils import run_subprocess_safe
        result = run_subprocess_safe(
            [godot, "--version"],
            timeout=15,
        )
        version_str = result.stdout.strip() or result.stderr.strip()
        # Ex: "4.7.stable.official.5b4e0cb0f"
        match = re.match(r"(\d+)\.(\d+)", version_str)
        if match:
            major, minor = int(match.group(1)), int(match.group(2))
            if major == 4 and minor == 7:
                return {
                    "status": "success",
                    "version": version_str,
                    "valid": True,
                }
            else:
                return {
                    "status": "error",
                    "message": (
                        f"Godot {major}.{minor}.x encontrado, mas 4.7.x é requerido. "
                        f"Atualize o campo godot_path em config.json para um binário 4.7."
                    ),
                    "found_version": version_str,
                    "valid": False,
                }
        return {
            "status": "error",
            "message": f"Não foi possível determinar a versão do Godot. Output: '{version_str}'",
            "found_version": version_str,
        }
    except FileNotFoundError:
        return {
            "status": "error",
            "message": (
                f"Binário Godot não encontrado em: {godot}. "
                f"Verifique o campo godot_path em config.json."
            ),
        }
    except subprocess.TimeoutExpired:
        return {
            "status": "error",
            "message": "Timeout ao executar Godot --version. Verifique se o binário está correto.",
        }


def set_active_project(project_path: str) -> dict:
    """Define o projeto Godot ativo para todas as operações subsequentes.

    Args:
        project_path: Caminho absoluto ou relativo ao workspace.

    Returns:
        {"status": "success", "active_project": str}
        ou {"status": "error", "message": str}
    """
    global _active_project
    proj = _resolve_project_path(project_path)

    # Verifica se é um diretório com project.godot
    godot_file = proj / "project.godot" if proj.is_dir() else Path(str(proj) + "/project.godot")
    if proj.is_dir():
        godot_file = proj / "project.godot"
    else:
        # Pode ser o path direto para project.godot
        if proj.name == "project.godot":
            godot_file = proj
            proj = proj.parent
        else:
            return {
                "status": "error",
                "message": (
                    f"'{project_path}' não é um projeto Godot válido. "
                    f"Certifique-se de que o caminho aponta para uma pasta com project.godot. "
                    f"Use create_project para criar um novo projeto."
                ),
            }

    if not godot_file.exists():
        return {
            "status": "error",
            "message": (
                f"project.godot não encontrado em '{proj}'. "
                f"Use create_project para criar um novo projeto ou verifique o caminho."
            ),
        }

    _active_project = proj

    # Atualiza config.json atomicamente
    cfg = get_config()
    cfg["default_project"] = str(proj.resolve())
    _save_config_atomic(cfg)

    return {"status": "success", "active_project": str(proj.resolve())}


def create_project(name: str, path: str, renderer: str = "forward_plus") -> dict:
    """Cria um novo projeto Godot vazio.

    Args:
        name: Nome do projeto.
        path: Caminho onde criar o projeto (absoluto ou relativo ao workspace).
        renderer: "forward_plus", "mobile", ou "compatibility".

    Returns:
        {"status": "success", "project_path": str}
        ou {"status": "error", "message": str}
    """
    proj = _resolve_project_path(path)

    if proj.exists() and any(proj.iterdir()):
        return {
            "status": "error",
            "message": (
                f"O diretório '{proj}' já existe e não está vazio. "
                f"Escolha outro nome ou caminho. Se a intenção era abrir um projeto "
                f"existente, use set_active_project."
            ),
        }

    proj.mkdir(parents=True, exist_ok=True)

    # project.godot mínimo
    renderer_map = {
        "forward_plus": "forward_plus",
        "mobile": "mobile",
        "compatibility": "gl_compatibility",
    }
    rendering_method = renderer_map.get(renderer, "forward_plus")

    project_godot = f"""; Engine configuration file.
; It's best edited using the editor UI and not directly,
; since the parameters that go here are not all obvious.
;
; Format:
;   [section] ; section goes between []
;   param=value ; assign values to parameters

config_version=5

[application]

config/name="{name}"

[rendering]

renderer/rendering_method="{rendering_method}"
"""

    (proj / "project.godot").write_text(project_godot, encoding="utf-8")

    # .gitignore
    (proj / ".gitignore").write_text(
        "# Godot\n.godot/\n.mcp_backups/\n\n# OS\nThumbs.db\n.DS_Store\n",
        encoding="utf-8",
    )

    # Inicializa com Godot headless
    godot = get_godot_bin()
    try:
        from tools.subprocess_utils import run_subprocess_safe
        run_subprocess_safe(
            [godot, "--headless", "--editor", "--quit", "--path", str(proj)],
            timeout=60,
        )
    except subprocess.TimeoutExpired:
        return {
            "status": "error",
            "message": "Timeout ao inicializar projeto. O Godot pode estar travado.",
        }

    # Cria pastas padrão
    for d in ["scenes", "scripts", "assets", "assets/sprites", "assets/audio"]:
        (proj / d).mkdir(parents=True, exist_ok=True)

    # Seta como projeto ativo (apenas estado interno — não persiste em config.json;
    # set_active_project é a tool que persiste a escolha do usuário)
    global _active_project
    _active_project = proj

    return {"status": "success", "project_path": str(proj.resolve())}


def get_project_settings(section: str | None = None) -> dict:
    """Lê configurações do project.godot do projeto ativo.

    Args:
        section: Seção específica (ex: "application", "rendering") ou None para todas.

    Returns:
        {"status": "success", "settings": dict}
    """
    proj = _get_active_project()
    godot_file = proj / "project.godot"

    if not godot_file.exists():
        return {
            "status": "error",
            "message": f"project.godot não encontrado em '{proj}'.",
        }

    content = godot_file.read_text(encoding="utf-8")
    parsed = _parse_project_godot(content)

    if section:
        return {"status": "success", "settings": {section: parsed.get(section, {})}}

    return {"status": "success", "settings": parsed}


def set_project_setting(section: str, key: str, value) -> dict:
    """Define uma configuração no project.godot (edição linha a linha).

    Args:
        section: Seção (ex: "application", "rendering").
        key: Chave dentro da seção.
        value: Valor (str, int, float, bool).

    Returns:
        {"status": "success"}
        ou {"status": "error", "message": str}
    """
    proj = _get_active_project()
    godot_file = proj / "project.godot"

    if not godot_file.exists():
        return {
            "status": "error",
            "message": f"project.godot não encontrado em '{proj}'.",
        }

    # Checkpoint antes de editar
    checkpoint(str(godot_file.relative_to(proj)), proj)

    content = godot_file.read_text(encoding="utf-8")
    lines = content.splitlines(keepends=True)

    # Formata o valor
    if isinstance(value, bool):
        val_str = "true" if value else "false"
    elif isinstance(value, str):
        val_str = f'"{value}"'
    else:
        val_str = str(value)

    section_header = f"[{section}]"
    target_line = f"{key}="
    in_section = False
    section_start = -1
    section_end = -1
    key_line_idx = -1

    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("[") and stripped.endswith("]"):
            if in_section:
                section_end = i
                break
            if stripped == section_header:
                in_section = True
                section_start = i
        elif in_section and stripped.startswith(target_line):
            key_line_idx = i
            break

    if key_line_idx >= 0:
        # Substitui linha existente
        lines[key_line_idx] = f"{key}={val_str}\n"
    elif section_start >= 0:
        # Seção existe mas chave não — insere após última entrada da seção
        insert_at = section_end if section_end >= 0 else len(lines)
        # Encontra fim real da seção
        for i in range(section_start + 1, len(lines)):
            if lines[i].strip().startswith("[") and lines[i].strip().endswith("]"):
                insert_at = i
                break
        else:
            insert_at = len(lines)
        lines.insert(insert_at, f"{key}={val_str}\n")
    else:
        # Seção não existe — cria no final
        if lines and not lines[-1].endswith("\n"):
            lines.append("\n")
        lines.append(f"\n{section_header}\n{key}={val_str}\n")

    godot_file.write_text("".join(lines), encoding="utf-8")
    return {"status": "success"}


def set_main_scene(scene_path: str) -> dict:
    """Define a cena principal do projeto (application/run/main_scene).

    Args:
        scene_path: Caminho da cena relativo ao projeto (ex: "scenes/main.tscn").

    Returns:
        {"status": "success", "main_scene": str}
        ou {"status": "error", "message": str}
    """
    proj = _get_active_project()

    # Verifica que a cena existe
    full_path = proj / scene_path
    if not full_path.exists():
        # Lista cenas disponíveis
        scenes = list(proj.glob("**/*.tscn"))
        scene_list = [str(s.relative_to(proj)) for s in scenes]
        return {
            "status": "error",
            "message": (
                f"Cena '{scene_path}' não encontrada no projeto. "
                f"Cenas disponíveis: {scene_list if scene_list else 'nenhuma'}. "
                f"Use create_scene para criar uma cena primeiro."
            ),
        }

    return set_project_setting("application", "run/main_scene", scene_path)


# ── Helpers internos ────────────────────────────────────────────────

def _parse_project_godot(content: str) -> dict:
    """Parseia project.godot em dicionário de seções.

    Returns:
        dict como {"section_name": {"key": "value", ...}, ...}
    """
    result: dict = {}
    current_section: str | None = None

    for line in content.splitlines():
        stripped = line.strip()
        # Ignora comentários e linhas vazias
        if not stripped or stripped.startswith(";"):
            continue
        # Cabeçalho de seção
        if stripped.startswith("[") and stripped.endswith("]"):
            current_section = stripped[1:-1]
            if current_section not in result:
                result[current_section] = {}
            continue
        # Chave=valor
        if "=" in stripped and current_section is not None:
            key, _, value = stripped.partition("=")
            key = key.strip()
            value = value.strip()
            # Remove aspas
            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]
            result[current_section][key] = value

    return result


# ── Fase 2: Input e Autoload ───────────────────────────────────────

# Lista de teclas válidas do Godot 4 (enum Key)
_VALID_KEYS = {
    "Space", "Enter", "Escape", "Tab", "Backspace", "Insert", "Delete",
    "Home", "End", "PageUp", "PageDown", "Left", "Right", "Up", "Down",
    "F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12",
    "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M",
    "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z",
    "0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
    "Shift", "Ctrl", "Alt", "Meta",
    "Kp 0", "Kp 1", "Kp 2", "Kp 3", "Kp 4", "Kp 5", "Kp 6", "Kp 7", "Kp 8", "Kp 9",
    "Kp Add", "Kp Subtract", "Kp Multiply", "Kp Divide", "Kp Period", "Kp Enter",
}

# Mapeamento nome da tecla → keycode Godot 4 (inteiro)
_KEY_NAME_TO_KEYCODE = {
    # Letras A-Z (ASCII)
    **{chr(c): c for c in range(65, 91)},
    # Números 0-9 (ASCII)
    **{str(d): 48 + d for d in range(10)},
    # Teclas especiais (KEY_* enum values do Godot 4)
    "Space": 32,
    "Enter": 4194309,
    "Escape": 4194305,
    "Tab": 4194306,
    "Backspace": 4194307,
    "Insert": 4194310,
    "Delete": 4194311,
    "Home": 4194316,
    "End": 4194318,
    "PageUp": 4194314,
    "PageDown": 4194315,
    "Left": 4194319,
    "Right": 4194321,
    "Up": 4194320,
    "Down": 4194322,
    **{f"F{i}": 4194231 + i for i in range(1, 13)},
    "Shift": 4194325,
    "Ctrl": 4194327,
    "Alt": 4194328,
    "Meta": 4194329,
    **{f"Kp {i}": 4194329 + i + 1 for i in range(10)},
    "Kp Add": 4194342,
    "Kp Subtract": 4194343,
    "Kp Multiply": 4194336,
    "Kp Divide": 4194337,
    "Kp Period": 4194340,
    "Kp Enter": 4194341,
}


def configure_input_action(action_name: str, keys: list[str], joypad_buttons: list[int] | None = None) -> dict:
    """Configura uma ação de input no projeto (InputMap).

    Args:
        action_name: Nome da ação (ex: 'move_left', 'jump').
        keys: Lista de teclas (ex: ['A', 'Left']).
        joypad_buttons: Lista de botões de controle (opcional).

    Returns:
        {"status": "success", "action_name": str}
    """
    proj = _get_active_project()
    godot_file = proj / "project.godot"

    if not godot_file.exists():
        return {"status": "error", "message": "project.godot não encontrado."}

    # Valida teclas
    for k in keys:
        if k not in _VALID_KEYS:
            examples = list(_VALID_KEYS)[:10]
            return {
                "status": "error",
                "message": f"Tecla inválida: '{k}'. Exemplos de teclas válidas: {examples}. "
                           f"Use nomes como 'W', 'Space', 'Left', 'Kp 0'.",
            }

    checkpoint("project.godot", proj)

    # Constrói eventos como string compacta (uma linha por ação)
    events_parts = []
    for k in keys:
        keycode = _KEY_NAME_TO_KEYCODE[k]
        ev = (f'Object(InputEventKey,"resource_local_to_scene":false,'
              f'"resource_name":"","device":-1,"window_id":0,'
              f'"alt_pressed":false,"shift_pressed":false,'
              f'"ctrl_pressed":false,"meta_pressed":false,'
              f'"pressed":false,"keycode":{keycode},"physical_keycode":{keycode},'
              f'"key_label":0,"unicode":{keycode if keycode < 128 else 0},"echo":false,"script":null)')
        events_parts.append(ev)

    if joypad_buttons:
        for btn in joypad_buttons:
            ev = (f'Object(InputEventJoypadButton,"resource_local_to_scene":false,'
                  f'"resource_name":"","device":-1,"button_index":{btn},'
                  f'"pressure":0.0,"pressed":false,"script":null)')
            events_parts.append(ev)

    events_str = ", ".join(events_parts)
    action_line = f'{action_name}={{\n"deadzone": 0.5,\n"events": [{events_str}]\n}}'

    content = godot_file.read_text(encoding="utf-8")

    # Verifica se ação já existe
    if f"{action_name}=" in content:
        lines = content.splitlines(keepends=True)
        for i, line in enumerate(lines):
            if line.strip().startswith(f"{action_name}="):
                lines[i] = action_line + "\n"
                break
        godot_file.write_text("".join(lines), encoding="utf-8")
        return {"status": "success", "action_name": action_name}

    # Adiciona na seção [input] ou cria
    if "[input]" in content:
        lines = content.splitlines(keepends=True)
        in_input = False
        insert_at = len(lines)
        for i, line in enumerate(lines):
            if line.strip() == "[input]":
                in_input = True
            elif in_input and line.strip().startswith("[") and line.strip().endswith("]"):
                insert_at = i
                break
        lines.insert(insert_at, action_line + "\n")
        godot_file.write_text("".join(lines), encoding="utf-8")
    else:
        godot_file.write_text(content + f"\n[input]\n{action_line}\n")

    return {"status": "success", "action_name": action_name}


def configure_autoload(name: str, script_path: str, singleton: bool = True) -> dict:
    """Configura um script como autoload (singleton global).

    Args:
        name: Nome do autoload.
        script_path: Caminho do script .gd (relativo ao projeto ou com prefixo res://).
        singleton: Se True, é singleton global.

    Returns:
        {"status": "success"}
    """
    proj = _get_active_project()
    godot_file = proj / "project.godot"

    if not godot_file.exists():
        return {"status": "error", "message": "project.godot não encontrado."}

    # Normaliza: remove prefixo res:// se presente
    clean_path = script_path
    if clean_path.startswith("res://"):
        clean_path = clean_path[6:]

    script_full = proj / clean_path
    if not script_full.exists():
        return {
            "status": "error",
            "message": f"Script '{clean_path}' não encontrado no projeto. "
                       f"Use generate_gdscript ou write_file para criar o script primeiro. "
                       f"Verifique se o caminho está correto com inspect_project.",
        }

    content = godot_file.read_text(encoding="utf-8")
    checkpoint("project.godot", proj)

    autoload_line = f'{name}="*res://{clean_path}"\n'

    if "[autoload]" in content:
        lines = content.splitlines(keepends=True)
        in_section = False
        replaced = False
        insert_at = len(lines)
        for i, line in enumerate(lines):
            if line.strip() == "[autoload]":
                in_section = True
            elif in_section:
                # Verifica se autoload já existe com este nome
                if line.strip().startswith(f'{name}="'):
                    lines[i] = autoload_line
                    replaced = True
                    break
                if line.strip().startswith("[") and line.strip().endswith("]"):
                    insert_at = i
                    break
        if not replaced:
            lines.insert(insert_at, autoload_line)
        godot_file.write_text("".join(lines), encoding="utf-8")
    else:
        godot_file.write_text(content + f"\n[autoload]\n{autoload_line}")

    return {"status": "success", "name": name, "script_path": f"res://{clean_path}"}


def generate_project_structure(
    template: str = "2d",
    project_path: str | None = None,
) -> dict:
    """Gera a estrutura completa de pastas e arquivos base para um projeto Godot.

    Cria pastas padronizadas, scene principal com nodes basicos, scripts boilerplate
    e arquivos de configuracao (.gitignore, README).

    Args:
        template: Tipo de projeto - "2d", "3d", ou "mobile".
        project_path: Caminho do projeto (opcional, usa o ativo).

    Returns:
        {"status": "success", "structure": dict, "files_created": list}
    """
    if project_path:
        result = set_active_project(project_path)
        if result.get("status") == "error":
            return result

    proj = _get_active_project()
    created = []

    # Estrutura de pastas
    dirs = {
        "2d": ["scenes", "scripts", "assets/sprites", "assets/audio", "assets/fonts"],
        "3d": ["scenes", "scripts", "assets/models", "assets/textures", "assets/audio", "assets/fonts"],
        "mobile": ["scenes", "scripts", "assets/sprites", "assets/audio", "assets/fonts", "export"],
    }

    for d in dirs.get(template, dirs["2d"]):
        full = proj / d
        full.mkdir(parents=True, exist_ok=True)
        created.append(str(full.relative_to(proj)))

    # .gitignore
    gitignore = proj / ".gitignore"
    gitignore.write_text(
        "# Godot\n.godot/\n.mcp_backups/\n\n# OS\nThumbs.db\n.DS_Store\n\n# Export\nexport/\n*.exe\n*.apk\n",
        encoding="utf-8",
    )
    created.append(".gitignore")

    # README
    readme = proj / "README.md"
    readme_text = f"""# {proj.name}

Projeto Godot 4.7 criado com MCP Godot Agent.

## Estrutura
```
{"/".join(dirs.get(template, dirs["2d"]))}
```

## Como abrir
1. Abra o Godot 4.7
2. Importe este projeto
3. Ative o plugin MCP Addon em Project → Project Settings → Plugins
"""
    readme.write_text(readme_text, encoding="utf-8")
    created.append("README.md")

    # Main scene boilerplate
    main_scene = proj / "scenes" / "main.tscn"
    if template == "2d":
        main_content = _generate_main_scene_2d()
    elif template == "3d":
        main_content = _generate_main_scene_3d()
    else:
        main_content = _generate_main_scene_2d()

    main_scene.write_text(main_content, encoding="utf-8")
    created.append("scenes/main.tscn")

    # Script principal (referenciado pela cena)
    main_script = proj / "scripts" / "main.gd"
    main_script.write_text(_generate_main_script(template), encoding="utf-8")
    created.append("scripts/main.gd")

    # Define main scene
    godot_file = proj / "project.godot"
    content = godot_file.read_text(encoding="utf-8")
    if 'run/main_scene="scenes/main.tscn"' not in content:
        content = content.replace(
            "[application]",
            '[application]\n\nrun/main_scene="scenes/main.tscn"',
        )
        godot_file.write_text(content, encoding="utf-8")

    return {
        "status": "success",
        "template": template,
        "project": str(proj.resolve()),
        "structure": dirs.get(template, dirs["2d"]),
        "files_created": created,
    }


def _generate_main_script(template: str) -> str:
    """Gera script GDScript principal."""
    if template == "3d":
        return """extends Node3D
## Script principal do jogo 3D.
## Gerado pelo MCP Godot Agent.

func _ready() -> void:
    print("Jogo 3D iniciado!")

func _process(delta: float) -> void:
    pass
"""
    return """extends Node2D
## Script principal do jogo 2D.
## Gerado pelo MCP Godot Agent.

func _ready() -> void:
    print("Jogo 2D iniciado!")

func _process(delta: float) -> void:
    pass
"""


def _generate_main_scene_2d() -> str:
    """Gera boilerplate de cena 2D."""
    return """[gd_scene load_steps=2 format=3 uid="uid://main2d00000000000001"]

[ext_resource type="Script" path="res://scripts/main.gd" id="1_main"]

[node name="Main" type="Node2D"]
script = ExtResource("1_main")

[node name="Camera2D" type="Camera2D" parent="."]

[node name="Player" type="CharacterBody2D" parent="."]
"""


def _generate_main_scene_3d() -> str:
    """Gera boilerplate de cena 3D."""
    return """[gd_scene load_steps=2 format=3 uid="uid://main3d00000000000001"]

[ext_resource type="Script" path="res://scripts/main.gd" id="1_main"]

[node name="Main" type="Node3D"]
script = ExtResource("1_main")

[node name="Camera3D" type="Camera3D" parent="."]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 5, 10)

[node name="DirectionalLight3D" type="DirectionalLight3D" parent="."]
transform = Transform3D(1, 0, 0, 0, 0.707107, 0.707107, 0, -0.707107, 0.707107, 0, 5, 0)
"""


def _configure_game_bridge_autoload(proj: Path) -> None:
    """Configura o GameBridge como autoload no projeto (uso interno)."""
    godot_file = proj / "project.godot"
    content = godot_file.read_text(encoding="utf-8")
    autoload_line = 'MCPRuntimeBridge="*res://addons/mcp_runtime_bridge/runtime_bridge.gd"\n'

    if "MCPRuntimeBridge" in content:
        return  # Já configurado

    if "[autoload]" in content:
        lines = content.splitlines(keepends=True)
        in_section = False
        for i, line in enumerate(lines):
            if line.strip() == "[autoload]":
                in_section = True
            elif in_section and line.strip().startswith("[") and line.strip().endswith("]"):
                lines.insert(i, autoload_line)
                break
        else:
            if in_section:
                lines.append(autoload_line)
        godot_file.write_text("".join(lines), encoding="utf-8")
    else:
        godot_file.write_text(content + f"\n[autoload]\n{autoload_line}")


def install_mcp_addon(project_path: str | None = None) -> dict:
    """Instala o addon MCP no projeto Godot ativo e ativa o plugin.

    Copia os arquivos de addons/mcp_addon/ para addons/mcp_addon/ no projeto
    e adiciona o plugin em editor_plugins no project.godot.

    Args:
        project_path: Caminho do projeto (opcional, usa o ativo).

    Returns:
        {"status": "success", "project": str, "bridge_port": 9082}
        ou {"status": "error", "message": str}
    """
    import shutil

    # Se project_path fornecido, usa-o; senão usa o projeto ativo
    if project_path:
        result = set_active_project(project_path)
        if result.get("status") == "error":
            return result

    proj = _get_active_project()

    # Origem: addons/mcp_addon na raiz do MCP
    source = ROOT / "addons" / "mcp_addon"
    if not source.exists():
        return {
            "status": "error",
            "message": (
                f"Addon MCP não encontrado em '{source}'. "
                f"Verifique se a pasta addons/mcp_addon/ existe na raiz do MCP."
            ),
        }

    # Destino: addons/mcp_addon no projeto
    dest = proj / "addons" / "mcp_addon"
    dest.mkdir(parents=True, exist_ok=True)

    # Copia todos os arquivos .gd e plugin.cfg
    copied = []
    for f in source.glob("*"):
        if f.is_file():
            shutil.copy2(f, dest / f.name)
            copied.append(f.name)

    # ── Runtime Bridge (autoload para runtime) ──────────────────
    gb_source = ROOT / "addons" / "mcp_runtime_bridge"
    if gb_source.exists():
        gb_dest = proj / "addons" / "mcp_runtime_bridge"
        gb_dest.mkdir(parents=True, exist_ok=True)
        for f in gb_source.glob("*"):
            if f.is_file():
                shutil.copy2(f, gb_dest / f.name)
                if f.name not in copied:
                    copied.append(f.name)

        # Configura autoload do RuntimeBridge automaticamente
        _configure_game_bridge_autoload(proj)

    # Ativa o plugin no project.godot
    godot_file = proj / "project.godot"
    content = godot_file.read_text(encoding="utf-8")

    plugin_line = 'enabled=PackedStringArray("res://addons/mcp_addon/plugin.cfg")'

    if "[editor_plugins]" in content:
        # Já tem seção — atualiza
        lines = content.splitlines(keepends=True)
        in_section = False
        for i, line in enumerate(lines):
            if line.strip() == "[editor_plugins]":
                in_section = True
            elif in_section and line.strip().startswith("enabled="):
                lines[i] = plugin_line + "\n"
                break
        else:
            if in_section:
                lines.append(plugin_line + "\n")
        content = "".join(lines)
    else:
        content += f"\n[editor_plugins]\n{plugin_line}\n"

    godot_file.write_text(content, encoding="utf-8")

    return {
        "status": "success",
        "project": str(proj.resolve()),
        "bridge_port": 9080,
        "plugin": "MCP Addon",
        "files_copied": copied,
        "next": (
            "Reinicie o editor Godot (ou abra com --editor --path) para ativar o plugin. "
            "O dock 'MCP Addon' aparecera no painel direito (3 tabs: Status, Log, Tools)."
        ),
    }

