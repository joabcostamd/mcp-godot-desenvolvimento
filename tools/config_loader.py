"""config_loader.py — Carregador de configuração multi-máquina (PATCH 10).

Carrega config.local.json se existir; senão config.json;
senão monta a partir de variáveis de ambiente; senão erro amigável.

Substitui todas as leituras diretas de config.json no repositório.
"""

import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load_config() -> dict:
    """Carrega config.local.json se existir; senão config.json;
    senão monta a partir de variáveis de ambiente; senão erro amigável."""
    local = ROOT / "config.local.json"
    default = ROOT / "config.json"

    cfg = {}

    # 1. config.local.json (prioridade máxima)
    if local.exists():
        cfg = json.loads(local.read_text(encoding="utf-8"))
    # 2. config.json (fallback)
    elif default.exists():
        cfg = json.loads(default.read_text(encoding="utf-8"))
    else:
        # Tenta construir a partir de env vars
        pass

    # 3. Sobrescreve com env vars se presentes (permite override sem editar arquivo)
    env_map = {
        "GODOT_MCP_GODOT_PATH": "godot_path",
        "GODOT_MCP_GODOT_CONSOLE_PATH": "godot_console_path",
        "GODOT_MCP_PYTHON_PATH": "python_path",
        "GODOT_MCP_PROJECTS_ROOT": "projects_root",
        "GODOT_MCP_DEFAULT_PROJECT": "default_project",
        "GODOT_MCP_ADDON_PORT": "addon_port",
        "GODOT_MCP_GAME_PORT": "game_port",
    }
    for env_var, config_key in env_map.items():
        val = os.environ.get(env_var)
        if val:
            # Converter portas para int
            if config_key.endswith("_port"):
                try:
                    val = int(val)
                except ValueError:
                    pass
            cfg[config_key] = val

    # 4. Validação: campos obrigatórios
    missing = []
    for key in ["godot_path"]:
        if not cfg.get(key):
            missing.append(key)

    if missing:
        # Não lança exceção — retorna cfg incompleto para que o chamador
        # possa dar erro amigável no contexto certo
        cfg["_config_incomplete"] = True
        cfg["_missing_keys"] = missing
        cfg["_help"] = (
            "Crie config.local.json (copie de config.json.example e ajuste os paths) "
            "ou defina as variáveis de ambiente:\n"
            "  GODOT_MCP_GODOT_PATH=C:\\Godot\\Godot_v4.7-stable_win64.exe\n"
            "  GODOT_MCP_PROJECTS_ROOT=C:\\meus-projetos\n"
            "  GODOT_MCP_DEFAULT_PROJECT=C:\\meus-projetos\\meu-jogo"
        )

    return cfg


def get_config_value(key: str, default=None):
    """Helper: obtém um valor específico da config."""
    cfg = load_config()
    return cfg.get(key, default)
