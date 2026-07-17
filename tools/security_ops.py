"""security_ops.py — Segurança do MCP (Fase 2C / B10).

Auth token, allow-remote toggle. Inspirado no yurineko73 e FunplayAI.

Tools:
    - configure_security: setup de token e permissões
    - security_status: verifica configuração atual
"""

import hashlib
import json
import os
import re
import secrets
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT / "config.json"


def _load_config() -> dict:
    try:
        from tools.config_loader import load_config
        return load_config()
    except Exception:
        return {}


def _save_config(config: dict) -> None:
    from tools.config_loader import ROOT
    from tools.config_lock import CONFIG_FILE_LOCK
    config_path = ROOT / "config.local.json"
    if not config_path.exists():
        config_path = ROOT / "config.json"
    with CONFIG_FILE_LOCK:
        with open(config_path, "w", encoding="utf-8") as f:
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


# ── Scan de segredo vazado (Fatia 0.6) ──────────────────────────────

SECRET_PATTERNS = [
    # Chaves de API cloud
    (r'(?i)(sk-[A-Za-z0-9_-]{20,}|api[_\-]key["\']?\s*[:=]\s*["\'][A-Za-z0-9_\-]{16,})',
     "Chave de API (cloud/IA)"),
    # Tokens de autenticação
    (r'(?i)(gh[opsu]_[A-Za-z0-9]{36,}|ghr_[A-Za-z0-9]{36,}|github_pat_[A-Za-z0-9]{22,})',
     "Token GitHub"),
    (r'(?i)(eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,})',
     "JWT Token"),
    # Senhas (requer atribuição com valor entre aspas)
    (r'(?i)(password|passwd|pwd|secret|auth_token|api_key)\s*[:=]\s*["\'][^"\'\s]{8,}["\']',
     "Senha/segredo hardcoded"),
    # URL com credenciais
    (r'https?://[A-Za-z0-9_\-]+:[A-Za-z0-9_\-]+@',
     "URL com credenciais embutidas"),
]


def scan_secrets(directory: str | None = None) -> dict:
    """Varre o repositório por segredos vazados (chaves de API, tokens, senhas).

    Args:
        directory: Caminho para varrer (default: raiz do MCP).

    Returns:
        dict com status, lista de arquivos suspeitos e contagem.
    """
    root = Path(directory).resolve() if directory else ROOT
    findings = []
    extensions_validas = {".py", ".gd", ".tscn", ".json", ".yaml", ".yml",
                         ".toml", ".cfg", ".ini", ".sh", ".bat", ".md"}

    # Pastas a ignorar (são seguras ou grandes demais)
    skip_dirs = {".git", ".venv", "__pycache__", "art_cache", "classdb_cache",
                 "temp_art", "workflow_logs", "builds", "export", ".vscode",
                 "recordings", ".mcp_proof", "node_modules", ".godot",
                 "assets", "addons/mcp_addon", "addons/mcp_runtime_bridge"}

    for filepath in root.rglob("*"):
        # Pular diretórios ignorados
        rel = filepath.relative_to(root)
        parts = rel.parts
        if any(p in skip_dirs for p in parts):
            continue
        # Só arquivos com extensão relevante
        if filepath.suffix.lower() not in extensions_validas:
            continue
        if not filepath.is_file():
            continue

        try:
            content = filepath.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        for pattern, label in SECRET_PATTERNS:
            for match in re.finditer(pattern, content):
                line_num = content[:match.start()].count("\n") + 1
                # Pular resultados em comentários e docstrings
                line = content.splitlines()[line_num - 1].strip()
                if line.startswith("#") or line.startswith('"""') or line.startswith("'''"):
                    continue
                findings.append({
                    "file": str(rel),
                    "line": line_num,
                    "match_preview": match.group()[:40] + "..." if len(match.group()) > 40 else match.group(),
                    "type": label,
                })
                break  # só um por linha

    return {
        "status": "success",
        "scanned_directory": str(root),
        "total_findings": len(findings),
        "safe": len(findings) == 0,
        "findings": findings if findings else None,
        "recommendation": "Nenhum segredo encontrado. "
                          f"Sempre use variáveis de ambiente ou .env (adicionado ao .gitignore)."
                          if not findings else
                          f"⚠️ {len(findings)} possível(is) segredo(s) encontrado(s). "
                          "Remova do código e use variáveis de ambiente. "
                          "Para remover do histórico: git filter-branch.",
    }
