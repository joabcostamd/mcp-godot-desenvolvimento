"""security_ops.py — Segurança do MCP (Fase 2C / B10).

Auth token, allow-remote toggle. Inspirado no yurineko73 e FunplayAI.

Tools:
    - configure_security: setup de token e permissões
    - security_status: verifica configuração atual
"""

import hashlib
import json
import os
import secrets
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT / "config.json"


def _load_config() -> dict:
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, encoding="utf-8") as f:
            return json.load(f)
    return {}


def _save_config(config: dict) -> None:
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


def configure_security(
    generate_token: bool = True,
    allow_remote: bool = False,
    token: str | None = None,
) -> dict:
    """Configura segurança do MCP: auth token e permissões de acesso.

    Args:
        generate_token: Se True, gera token aleatório de 32 chars.
        allow_remote: Se True, permite conexões de outras máquinas.
        token: Token personalizado (ignorado se generate_token=True).

    Returns:
        dict com configuração aplicada.
    """
    config = _load_config()

    security = config.get("security", {})

    if generate_token:
        new_token = secrets.token_hex(16)  # 32 caracteres hex
        security["auth_token"] = new_token
    elif token:
        security["auth_token"] = token

    security["allow_remote"] = allow_remote
    security["configured_at"] = str(Path(__file__).stat().st_mtime)

    config["security"] = security
    _save_config(config)

    return {
        "status": "success",
        "security": {
            "auth_token_configured": "auth_token" in security,
            "token_preview": security.get("auth_token", "")[:8] + "..." if security.get("auth_token") else None,
            "allow_remote": allow_remote,
        },
        "warning": "Reinicie o Godot Editor após alterar segurança." if allow_remote else None,
    }


def security_status() -> dict:
    """Verifica estado atual da segurança."""
    config = _load_config()
    security = config.get("security", {})

    return {
        "status": "success",
        "security": {
            "auth_token_configured": "auth_token" in security,
            "allow_remote": security.get("allow_remote", False),
            "configured": "configured_at" in security,
        },
        "recommendations": [
            "auth_token NAO configurado — use configure_security" if "auth_token" not in security else None,
            "allow_remote ATIVO — risco de acesso externo" if security.get("allow_remote") else None,
        ],
    }


def get_auth_token() -> str | None:
    """Retorna o auth token configurado (para uso interno do addon bridge)."""
    config = _load_config()
    return config.get("security", {}).get("auth_token")
