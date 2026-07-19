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


# ══════════════════════════════════════════════════════════════════════
# B5 — Segurança Supply-Chain (Fatia 4.5)
# ══════════════════════════════════════════════════════════════════════

def _find_project_root(project_path: str | None = None) -> Path | None:
    """Resolve o diretorio do projeto Godot (compartilhado com code_quality_ops)."""
    if project_path:
        p = Path(project_path)
        if (p / "project.godot").exists():
            return p
        return None
    try:
        from tools.project_ops import _get_active_project
        return _get_active_project()
    except Exception:
        pass
    if (ROOT / "project.godot").exists():
        return ROOT
    return None


# ── Op 1: scan_addon_vulnerabilities ──────────────────────────────

# Padroes de vulnerabilidade conhecidos em addons Godot
VULN_PATTERNS = [
    # eval/execute com input potencialmente nao confiavel
    (r'eval\s*\(', "eval() — execucao dinamica de codigo", "high"),
    (r'OS\.execute\s*\(', "OS.execute() — execucao de comando externo", "high"),
    (r'OS\.shell_open\s*\(', "OS.shell_open() — abre URL/arquivo externo", "medium"),
    # HTTPRequest — verificar se usa TLS (nao detectavel estaticamente)
    (r'HTTPRequest\b', "HTTPRequest — verifique uso de TLS/SSL", "low"),
    (r'http://(?!localhost|127\.0\.0\.1)', "Conexao HTTP (nao-HTTPS) para host externo", "medium"),
    # Escrita em diretorios sensiveis
    (r'FileAccess\.open\s*\(\s*"user://', "FileAccess em user:// — potencial extracao de dados", "low"),
    (r'DirAccess\.(?:copy|rename|remove)', "Manipulacao de diretorios pelo addon", "medium"),
    # Uso de ProjectSettings global
    (r'ProjectSettings\.set_setting\s*\(', "Modifica ProjectSettings globalmente", "low"),
    # Carregamento dinamico de script
    (r'ResourceLoader\.load\s*\(\s*(?:"[^"]*"|\'[^\']*\')', "ResourceLoader.load() com path string", "low"),
    (r'load\s*\(\s*"[^"]+\.(?:gd|tscn|gdshader)"', "load() dinamico de recurso", "low"),
    # Acesso a dados do usuario
    (r'OS\.get_user_data_dir\s*\(', "Acesso ao diretorio de dados do usuario", "medium"),
    (r'OS\.get_unique_id\s*\(', "Acesso ao identificador unico do dispositivo", "medium"),
]


def scan_addon_vulnerabilities(project_path: str | None = None) -> dict:
    """Escaneia addons/ do projeto por vulnerabilidades conhecidas.

    Detecta: eval(), OS.execute(), HTTP inseguro, acesso a dados do usuario,
    escrita em diretorios sensiveis, e ResourceLoader dinamico.

    Args:
        project_path: Caminho do projeto. Se omitido, usa projeto ativo.

    Returns:
        dict com vulnerabilidades encontradas por addon.
    """
    proj = _find_project_root(project_path)
    if proj is None:
        return {"status": "error", "error": "Nenhum projeto Godot encontrado."}

    addons_dir = proj / "addons"
    if not addons_dir.exists():
        return {"status": "passed", "vulnerabilities": [], "addons_scanned": 0,
                "detail": "Diretorio addons/ nao encontrado."}

    vulnerabilities = []
    addons_scanned = 0

    for addon_dir in addons_dir.iterdir():
        if not addon_dir.is_dir():
            continue
        addons_scanned += 1
        addon_name = addon_dir.name

        # Coleta todos os arquivos do addon
        for fpath in addon_dir.rglob("*"):
            if fpath.is_dir():
                continue
            if fpath.suffix not in (".gd", ".cs", ".cpp", ".h", ".py", ".tscn"):
                continue

            try:
                content = fpath.read_text(encoding="utf-8", errors="replace")
            except Exception:
                continue

            rel = str(fpath.relative_to(addon_dir))

            for pattern, desc, severity in VULN_PATTERNS:
                matches = list(re.finditer(pattern, content, re.IGNORECASE))
                for m in matches:
                    line_no = content[:m.start()].count("\n") + 1
                    vulnerabilities.append({
                        "addon": addon_name,
                        "file": rel,
                        "line": line_no,
                        "pattern": desc,
                        "severity": severity,
                        "detail": f"{desc} na linha {line_no}",
                    })

    # Ordena por severidade
    sev_order = {"high": 0, "medium": 1, "low": 2}
    vulnerabilities.sort(key=lambda v: (sev_order.get(v["severity"], 99), v["addon"], v["file"]))

    high_count = sum(1 for v in vulnerabilities if v["severity"] == "high")
    medium_count = sum(1 for v in vulnerabilities if v["severity"] == "medium")

    return {
        "status": "completed",
        "addons_scanned": addons_scanned,
        "total_findings": len(vulnerabilities),
        "high": high_count,
        "medium": medium_count,
        "low": len(vulnerabilities) - high_count - medium_count,
        "safe": len(vulnerabilities) == 0,
        "vulnerabilities": vulnerabilities[:100],
    }


# ── Op 2: check_addon_license ──────────────────────────────────────

KNOWN_LICENSES = [
    # (padrao_regex, nome, compativel, restritivo)
    (r'\bmit\b', "MIT", True, False),
    (r'\bapache\b.*\b2\.?0\b|\bapache-2\.0\b|\bapache license\b', "Apache 2.0", True, False),
    (r'\bbsd[-\s]?2[-\s]?clause\b|\bbsd\b.*\b2\b', "BSD 2-Clause", True, False),
    (r'\bbsd[-\s]?3[-\s]?clause\b|\bbsd\b.*\b3\b', "BSD 3-Clause", True, False),
    (r'\bbsd\b', "BSD", True, False),
    (r'\bgpl[-\s]?3\.?0\b|\bgnu general public license\b.*\bversion 3\b|\bgnu.*gpl.*v3\b', "GPL 3.0", False, True),
    (r'\bgpl[-\s]?2\.?0\b|\bgnu general public license\b.*\bversion 2\b|\bgnu.*gpl.*v2\b', "GPL 2.0", False, True),
    (r'\bgpl\b|\bgnu general public license\b', "GPL", False, True),
    (r'\blgpl\b|\bgnu lesser general public license\b', "LGPL", True, True),
    (r'\bagpl\b|\bgnu affero general public license\b', "AGPL", False, True),
    (r'\bmpl[-\s]?2\.?0\b|\bmozilla public license\b', "MPL 2.0", True, False),
    (r'\bcc0\b|\bcreative commons zero\b|\bpublic domain\b', "CC0", True, False),
    (r'\bcc[-\s]by[-\s]nc\b|\bcreative commons.*attribution[-\s]noncommercial\b', "CC BY-NC", False, True),
    (r'\bcc[-\s]by[-\s]sa\b|\bcreative commons.*attribution[-\s]sharealike\b', "CC BY-SA", False, True),
    (r'\bcc[-\s]by\b|\bcreative commons.*attribution\b', "CC BY", True, False),
    (r'\bunlicense\b', "Unlicense", True, False),
    (r'\bzlib\b|\blibpng\b', "zlib/libpng", True, False),
    (r'\bisc\b|\bisc license\b', "ISC", True, False),
]

LICENSE_FILES = {"LICENSE", "LICENSE.md", "LICENSE.txt", "LICENCE", "COPYING",
                 "COPYING.md", "COPYING.txt", "license.txt", "license.md"}


def check_addon_license(project_path: str | None = None) -> dict:
    """Verifica licencas dos addons no projeto.

    Para cada addon em addons/, verifica se tem arquivo de licenca,
    identifica o tipo, e flagga licencas incompatíveis (ex: GPL/AGPL).

    Args:
        project_path: Caminho do projeto.

    Returns:
        dict com status de licenca por addon.
    """
    proj = _find_project_root(project_path)
    if proj is None:
        return {"status": "error", "error": "Nenhum projeto Godot encontrado."}

    addons_dir = proj / "addons"
    if not addons_dir.exists():
        return {"status": "passed", "addons": [], "detail": "addons/ nao encontrado."}

    results = []
    issues = []

    for addon_dir in sorted(addons_dir.iterdir()):
        if not addon_dir.is_dir():
            continue

        addon_name = addon_dir.name
        entry = {"addon": addon_name, "license": None, "status": "unknown"}

        # Procura arquivo de licenca no addon
        license_file = None
        license_text = None

        for lf_name in LICENSE_FILES:
            candidate = addon_dir / lf_name
            if candidate.exists():
                license_file = lf_name
                try:
                    license_text = candidate.read_text(encoding="utf-8", errors="replace")
                except Exception:
                    license_text = "(arquivo ilegivel)"
                break

        if not license_file:
            entry["status"] = "missing"
            entry["detail"] = "Nenhum arquivo de licenca encontrado"
            issues.append({
                "addon": addon_name,
                "issue": "missing_license",
                "severity": "medium",
                "detail": f"Addon '{addon_name}' nao possui arquivo de licenca (LICENSE, COPYING, etc.)",
            })
            results.append(entry)
            continue

        # Detecta tipo de licenca via regex
        license_lower = license_text.lower() if license_text else ""
        detected = None

        for pattern, name, compatible, restrictive in KNOWN_LICENSES:
            if re.search(pattern, license_lower, re.IGNORECASE):
                detected = name
                entry["license"] = name
                entry["compatible"] = compatible
                entry["restrictive"] = restrictive

                if not compatible:
                    entry["status"] = "incompatible"
                    issues.append({
                        "addon": addon_name,
                        "issue": "incompatible_license",
                        "severity": "high",
                        "license": name,
                        "detail": f"Addon '{addon_name}' usa licenca {name} — "
                                  f"pode impor restricoes de redistribuicao/abertura de codigo.",
                    })
                elif restrictive:
                    entry["status"] = "restrictive"
                    issues.append({
                        "addon": addon_name,
                        "issue": "restrictive_license",
                        "severity": "low",
                        "license": name,
                        "detail": f"Licenca {name} tem restricoes leves. Verifique conformidade.",
                    })
                else:
                    entry["status"] = "ok"
                break

        if detected is None:
            entry["status"] = "unknown"
            entry["detail"] = f"Licenca nao identificada ({license_file})"
            issues.append({
                "addon": addon_name,
                "issue": "unknown_license",
                "severity": "low",
                "detail": f"Tipo de licenca do addon '{addon_name}' nao reconhecido.",
            })

        entry["license_file"] = license_file
        results.append(entry)

    incompatible = sum(1 for i in issues if i["severity"] == "high")

    return {
        "status": "completed" if not incompatible else "issues_found",
        "addons": results,
        "total_addons": len(results),
        "missing_license": sum(1 for r in results if r["status"] == "missing"),
        "incompatible": incompatible,
        "issues": issues,
        "safe": len(issues) == 0,
    }
