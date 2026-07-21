"""publish_ops.py — Publicacao na AssetLib (Fatia 4.A).

Rollup publish_manage(op=package|validate|metadata|preview).
Empacota addons do MCP Godot Agent em .zip pronto para submissao
na AssetLib oficial do Godot (godotengine.org/asset-library).

A AssetLib requer:
  - .zip com addons/<nome>/plugin.cfg na raiz
  - plugin.cfg com [plugin] name, description, author, version, script
  - Licenca compativel (MIT)
  - Categoria: Tools, 2D Tools, 3D Tools, Scripts, Misc
  - Submissao via formulario web (nao tem API programatica)

Uso:
    publish_manage op=package addon=mcp_addon
    publish_manage op=validate addon=mcp_addon
    publish_manage op=metadata addon=mcp_addon
    publish_manage op=preview addon=mcp_addon
"""

import json
import os
import re
import zipfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# ── Constantes ──────────────────────────────────────────────────────

# Addons publicaveis
ADDONS = {
    "mcp_addon": {
        "name": "MCP Godot Agent",
        "category": "Tools",
        "godot_version": "4.7",
        "description_pt": (
            "Plugin editor que conecta o Godot Engine 4.7 ao VS Code Copilot "
            "via servidor MCP. WebSocket bridge na porta 9082 com dock visual "
            "integrado (3 zonas: progresso, diagnosticos, botoes). "
            "Operacoes no editor com UndoRedo nativo. "
            "Parte do ecossistema MCP Godot Agent — o unico MCP que gerencia "
            "o ciclo completo de desenvolvimento de um jogo, da ideia ao lancamento."
        ),
        "description_en": (
            "Editor plugin connecting Godot Engine 4.7 to VS Code Copilot "
            "via MCP server. WebSocket bridge on port 9082 with integrated "
            "visual dock (3 zones: progress, diagnostics, buttons). "
            "Editor operations with native UndoRedo. "
            "Part of the MCP Godot Agent ecosystem — the only MCP that manages "
            "the full game development cycle, from idea to release."
        ),
        "tags": ["mcp", "copilot", "ai", "editor", "bridge", "websocket"],
        "version": "3.2.1",
        "include_dock": True,
        "has_plugin_cfg": True,
    },
    "mcp_dock": {
        "name": "MCP Dock",
        "category": "Tools",
        "godot_version": "4.7",
        "description_pt": (
            "Painel visual de estado, erros e acoes rapidas do MCP Godot Agent. "
            "3 zonas: progresso da fase, diagnosticos em tempo real, botoes de acao. "
            "Depende do MCP Addon (WebSocket bridge)."
        ),
        "description_en": (
            "Visual panel for state, errors, and quick actions of MCP Godot Agent. "
            "3 zones: phase progress, real-time diagnostics, action buttons. "
            "Requires MCP Addon (WebSocket bridge)."
        ),
        "tags": ["mcp", "ui", "dock", "diagnostics"],
        "version": "1.0.0",
        "include_dock": False,
        "has_plugin_cfg": True,
    },
    "mcp_runtime_bridge": {
        "name": "MCP Runtime Bridge",
        "category": "Tools",
        "godot_version": "4.7",
        "description_pt": (
            "Bridge TCP (porta 8790) para comunicacao com jogos em execucao. "
            "Permite ao MCP Godot Agent coletar metricas (FPS, draw_calls, memoria), "
            "enviar inputs simulados e capturar screenshots durante o jogo. "
            "Essencial para playtest automatizado e smoke tests."
        ),
        "description_en": (
            "TCP bridge (port 8790) for communication with running games. "
            "Enables MCP Godot Agent to collect metrics (FPS, draw_calls, memory), "
            "send simulated inputs, and capture screenshots during gameplay. "
            "Essential for automated playtesting and smoke tests."
        ),
        "tags": ["mcp", "runtime", "bridge", "playtest", "metrics", "tcp"],
        "version": "1.0.0",
        "include_dock": False,
        "has_plugin_cfg": False,  # Autoload — nao tem plugin.cfg proprio
    },
}

# Categorias validas da AssetLib
VALID_CATEGORIES = [
    "2D Tools", "3D Tools", "Scripts", "Tools", "Misc",
    "Demos", "Materials", "Projects", "Tutorials",
]

# Distribuicao
DIST_DIR = ROOT / "dist"


# ── Helpers ─────────────────────────────────────────────────────────

def _get_addon_dir(addon_name: str) -> Path:
    """Retorna o diretorio do addon."""
    return ROOT / "addons" / addon_name


def _get_plugin_cfg(addon_name: str) -> Path:
    """Retorna o caminho do plugin.cfg."""
    return _get_addon_dir(addon_name) / "plugin.cfg"


def _read_plugin_cfg(addon_name: str) -> dict[str, str]:
    """Le plugin.cfg e retorna dict de propriedades."""
    path = _get_plugin_cfg(addon_name)
    if not path.exists():
        return {}
    cfg = {}
    current_section = None
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith("[") and line.endswith("]"):
            current_section = line[1:-1]
            continue
        if "=" in line and current_section:
            key, _, value = line.partition("=")
            cfg[f"{current_section}.{key.strip()}"] = value.strip()
    return cfg


def _list_addon_files(addon_name: str) -> list[str]:
    """Lista todos os arquivos de um addon (caminhos relativos ao addon)."""
    addon_dir = _get_addon_dir(addon_name)
    if not addon_dir.exists():
        return []
    files = []
    for root, _dirs, filenames in os.walk(addon_dir):
        for f in filenames:
            full = Path(root) / f
            rel = full.relative_to(addon_dir)
            # Exclui arquivos ocultos e .pyc
            if f.startswith(".") or f.endswith(".pyc"):
                continue
            files.append(str(rel).replace("\\", "/"))
    return sorted(files)


def _sanitize_filename(name: str) -> str:
    """Remove caracteres invalidos de nome de arquivo."""
    return re.sub(r'[<>:"/\\|?*\s]+', '_', name).strip("_")


# ── Validacao ───────────────────────────────────────────────────────

def _validate_addon(addon_name: str) -> dict:
    """Valida estrutura do addon para AssetLib.

    Retorna dict com "valid" (bool), "issues" (list[str]), "warnings" (list[str]).
    """
    issues = []
    warnings = []
    addon_dir = _get_addon_dir(addon_name)

    # Addons sem plugin.cfg (autoloads) sao validos mas nao publicaveis separadamente
    meta = ADDONS.get(addon_name, {})
    if not meta.get("has_plugin_cfg", True):
        return {
            "valid": True,
            "issues": [],
            "warnings": [f"{addon_name} e autoload (sem plugin.cfg proprio). "
                         "Empacote junto com o addon principal (mcp_addon)."],
        }

    # 1. plugin.cfg existe
    cfg_path = _get_plugin_cfg(addon_name)
    if not cfg_path.exists():
        issues.append(f"plugin.cfg nao encontrado em addons/{addon_name}/")
        return {"valid": False, "issues": issues, "warnings": warnings}

    # 2. plugin.cfg tem campos obrigatorios
    cfg = _read_plugin_cfg(addon_name)
    required = ["plugin.name", "plugin.description", "plugin.author", "plugin.version"]
    for field in required:
        if field not in cfg or not cfg[field]:
            issues.append(f"plugin.cfg: campo '{field}' ausente ou vazio")

    # 3. Versao semantica
    version = cfg.get("plugin.version", "")
    if version and not re.match(r'^\d+\.\d+\.\d+$', version):
        issues.append(f"plugin.cfg: versao '{version}' nao e semantica (X.Y.Z)")

    # 4. script referenciado existe
    script = cfg.get("plugin.script", "")
    if script and not (addon_dir / script).exists():
        issues.append(f"plugin.cfg: script '{script}' referenciado mas nao encontrado")

    # 5. LICENSE na raiz do projeto
    license_path = ROOT / "LICENSE"
    if not license_path.exists():
        issues.append("LICENSE nao encontrado na raiz do projeto")

    # 6. .gdignore existe? (warning, nao erro)
    if not (addon_dir / ".gdignore").exists():
        warnings.append(f".gdignore ausente em addons/{addon_name}/ "
                        "(recomendado para evitar importacao indevida)")

    # 7. Nome do addon bate com pasta?
    expected_folder = cfg.get("plugin.name", "").lower().replace(" ", "_")
    if expected_folder and addon_name.lower() != expected_folder:
        warnings.append(f"Nome da pasta '{addon_name}' difere do nome no plugin.cfg "
                        f"'{cfg.get('plugin.name', '')}' -> pasta esperada: '{expected_folder}'")

    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "warnings": warnings,
    }


# ── Empacotamento ───────────────────────────────────────────────────

def _package_addon(addon_name: str, include_license: bool = True) -> dict:
    """Empacota addon em .zip pronto para AssetLib.

    Estrutura do .zip:
      addons/<addon_name>/
        plugin.cfg
        *.gd
        ...outros arquivos...
      LICENSE          (se include_license=True)

    Returns:
        dict com "zip_path", "size_bytes", "file_count", "status".
    """
    addon_dir = _get_addon_dir(addon_name)
    if not addon_dir.exists():
        return {"status": "error", "message": f"Addon '{addon_name}' nao encontrado em addons/"}

    # Cria diretorio dist/
    DIST_DIR.mkdir(parents=True, exist_ok=True)

    # Nome do arquivo: <addon>_v<version>.zip
    cfg = _read_plugin_cfg(addon_name)
    version = cfg.get("plugin.version") or ADDONS.get(addon_name, {}).get("version", "0.0.0")
    zip_name = f"{addon_name}_v{version}.zip"
    zip_path = DIST_DIR / zip_name

    files = _list_addon_files(addon_name)
    file_count = 0

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        # Adiciona arquivos do addon com prefixo addons/<nome>/
        for rel_path in files:
            full_path = addon_dir / rel_path
            arcname = f"addons/{addon_name}/{rel_path}"
            zf.write(full_path, arcname)
            file_count += 1

        # Adiciona LICENSE na raiz do .zip
        if include_license:
            license_path = ROOT / "LICENSE"
            if license_path.exists():
                zf.write(license_path, "LICENSE")
                file_count += 1

        # Adiciona README.md
        readme_path = ROOT / "README.md"
        if readme_path.exists():
            zf.write(readme_path, "README.md")
            file_count += 1

    size_bytes = zip_path.stat().st_size

    return {
        "status": "success",
        "zip_path": str(zip_path),
        "zip_name": zip_name,
        "size_bytes": size_bytes,
        "size_kb": round(size_bytes / 1024, 1),
        "file_count": file_count,
        "files": files,
        "version": version,
        "addon_name": addon_name,
    }


# ── Metadados ───────────────────────────────────────────────────────

def _generate_metadata(addon_name: str) -> dict:
    """Gera JSON de metadados para submissao na AssetLib.

    Campos baseados no formulario web da AssetLib:
      - name, description (en), category, godot_version, license, tags
      - version (do plugin.cfg)
      - download_url (a preencher pelo humano apos upload)
    """
    if addon_name not in ADDONS:
        return {"status": "error", "message": f"Addon '{addon_name}' desconhecido. "
                f"Disponiveis: {list(ADDONS.keys())}"}

    meta = ADDONS[addon_name]
    cfg = _read_plugin_cfg(addon_name)
    version = cfg.get("plugin.version", meta["version"])

    return {
        "status": "success",
        "metadata": {
            "name": meta["name"],
            "description_en": meta["description_en"],
            "description_pt": meta["description_pt"],
            "category": meta["category"],
            "godot_version": meta["godot_version"],
            "license": "MIT",
            "version": version,
            "author": cfg.get("plugin.author", "joabcostamd"),
            "tags": meta["tags"],
            "repository_url": "https://github.com/joabcostamd/mcp-godot-desenvolvimento",
            "download_url": "[A PREENCHER — faca upload do .zip e cole a URL aqui]",
            "issues_url": "https://github.com/joabcostamd/mcp-godot-desenvolvimento/issues",
            "documentation_url": "https://github.com/joabcostamd/mcp-godot-desenvolvimento#readme",
        },
    }


def _preview_addon(addon_name: str) -> dict:
    """Pre-visualizacao do que sera publicado, sem gerar .zip."""
    if addon_name not in ADDONS:
        return {"status": "error", "message": f"Addon '{addon_name}' desconhecido."}

    meta = ADDONS[addon_name]
    files = _list_addon_files(addon_name)
    validation = _validate_addon(addon_name)
    total_size = sum(
        (_get_addon_dir(addon_name) / f).stat().st_size
        for f in files
        if (_get_addon_dir(addon_name) / f).exists()
    )

    return {
        "status": "success",
        "addon": addon_name,
        "display_name": meta["name"],
        "version": meta["version"],
        "category": meta["category"],
        "godot_version": meta["godot_version"],
        "file_count": len(files),
        "total_size_kb": round(total_size / 1024, 1),
        "files": files[:20],  # primeiros 20
        "files_truncated": len(files) > 20,
        "validation": validation,
    }


# ── Rollup ──────────────────────────────────────────────────────────

def publish_manage(op: str, params: dict | None = None) -> dict:
    """Rollup publish_manage — gerencia publicacao na AssetLib.

    Args:
        op: Operacao: 'package', 'validate', 'metadata', 'preview'.
        params: Dicionario com parametros da operacao.
            - addon (str): Nome do addon. Default: 'mcp_addon'.
            - include_license (bool): Incluir LICENSE no .zip. Default: True.

    Returns:
        dict com "status" ("success" ou "error").
    """
    if params is None:
        params = {}

    addon = params.get("addon", "mcp_addon")

    if addon not in ADDONS:
        available = ", ".join(ADDONS.keys())
        return {
            "status": "error",
            "message": f"Addon '{addon}' desconhecido. Disponiveis: {available}",
            "suggestion": f"Use um destes: {available}",
        }

    if op == "package":
        include_license = params.get("include_license", True)
        return _package_addon(addon, include_license=include_license)

    elif op == "validate":
        return _validate_addon(addon)

    elif op == "metadata":
        return _generate_metadata(addon)

    elif op == "preview":
        return _preview_addon(addon)

    else:
        return {
            "status": "error",
            "message": f"Operacao '{op}' desconhecida. Use: package, validate, metadata, preview.",
        }
