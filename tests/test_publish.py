"""test_publish.py — Testes para publish_ops (Fatia 4.A).

Testa as 4 operacoes do rollup publish_manage:
  - package: gera .zip valido
  - validate: detecta problemas estruturais
  - metadata: gera JSON de metadados
  - preview: pre-visualiza sem gerar arquivo
"""

import json
import os
import sys
import tempfile
import zipfile
from pathlib import Path

import pytest

# Garante que ROOT esta no path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tools.publish_ops import (
    ADDONS,
    DIST_DIR,
    publish_manage,
    _list_addon_files,
    _read_plugin_cfg,
    _validate_addon,
    _package_addon,
    _generate_metadata,
    _preview_addon,
)


# ── Fixtures ────────────────────────────────────────────────────────

@pytest.fixture
def cleanup_dist():
    """Remove dist/ apos cada teste."""
    yield
    if DIST_DIR.exists():
        import shutil
        shutil.rmtree(DIST_DIR, ignore_errors=True)


# ── Testes: listagem e leitura ──────────────────────────────────────

def test_list_addon_files_real():
    """Arquivos reais do mcp_addon existem."""
    files = _list_addon_files("mcp_addon")
    assert len(files) >= 1, "mcp_addon deveria ter pelo menos plugin.cfg"
    assert "plugin.cfg" in files, "plugin.cfg deve estar na lista"


def test_read_plugin_cfg_real():
    """Leitura do plugin.cfg real do mcp_addon."""
    cfg = _read_plugin_cfg("mcp_addon")
    assert cfg.get("plugin.name") == "MCP Addon", f"Nome errado: {cfg}"
    assert cfg.get("plugin.version") == "3.2.1", f"Versao errada: {cfg}"
    assert cfg.get("plugin.author") == "joabcostamd", f"Autor errado: {cfg}"


def test_list_addon_files_all():
    """Todos os addons tem arquivos."""
    for name in ADDONS:
        files = _list_addon_files(name)
        assert len(files) >= 1, f"{name} deveria ter arquivos"


def test_read_plugin_cfg_all():
    """Todos os addons com plugin.cfg tem ele legivel."""
    for name, meta in ADDONS.items():
        if not meta.get("has_plugin_cfg", True):
            continue  # Autoloads como mcp_runtime_bridge nao tem plugin.cfg
        cfg = _read_plugin_cfg(name)
        assert cfg, f"{name} plugin.cfg vazio ou ausente"
        assert "plugin.name" in cfg, f"{name} sem plugin.name"
        assert "plugin.version" in cfg, f"{name} sem plugin.version"


# ── Testes: validate ────────────────────────────────────────────────

def test_validate_mcp_addon():
    """mcp_addon deve passar na validacao."""
    result = _validate_addon("mcp_addon")
    assert result["valid"] is True, f"Issues: {result.get('issues')}"
    assert len(result["issues"]) == 0, f"Issues inesperados: {result['issues']}"


def test_validate_via_rollup():
    """validate via rollup publish_manage."""
    result = publish_manage("validate", {"addon": "mcp_addon"})
    assert result.get("valid") is True, f"Falhou: {result}"


def test_validate_addon_inexistente():
    """Addon inexistente deve falhar validacao."""
    result = _validate_addon("addon_que_nao_existe")
    assert result["valid"] is False
    assert len(result["issues"]) >= 1


# ── Testes: metadata ────────────────────────────────────────────────

def test_metadata_mcp_addon():
    """Metadados do mcp_addon tem campos obrigatorios."""
    result = _generate_metadata("mcp_addon")
    assert result["status"] == "success"
    meta = result["metadata"]
    assert meta["name"] == "MCP Godot Agent"
    assert meta["license"] == "MIT"
    assert meta["category"] == "Tools"
    assert meta["godot_version"] == "4.7"
    assert "tags" in meta
    assert len(meta["tags"]) >= 3


def test_metadata_addon_desconhecido():
    """Addon desconhecido retorna erro."""
    result = _generate_metadata("addon_fantasma")
    assert result["status"] == "error"


def test_metadata_via_rollup():
    """metadata via rollup publish_manage."""
    result = publish_manage("metadata", {"addon": "mcp_addon"})
    assert result["status"] == "success"
    assert "metadata" in result


# ── Testes: preview ─────────────────────────────────────────────────

def test_preview_mcp_addon():
    """Preview do mcp_addon mostra informacoes basicas."""
    result = _preview_addon("mcp_addon")
    assert result["status"] == "success"
    assert result["addon"] == "mcp_addon"
    assert result["file_count"] >= 1
    assert "validation" in result


def test_preview_via_rollup():
    """Preview via rollup publish_manage."""
    result = publish_manage("preview", {"addon": "mcp_addon"})
    assert result["status"] == "success"


# ── Testes: package ─────────────────────────────────────────────────

def test_package_mcp_addon(cleanup_dist):
    """Empacota mcp_addon e verifica .zip."""
    result = _package_addon("mcp_addon")
    assert result["status"] == "success", f"Falhou: {result}"
    zip_path = Path(result["zip_path"])
    assert zip_path.exists(), f"ZIP nao criado: {zip_path}"
    assert zip_path.stat().st_size > 0, "ZIP vazio"
    assert result["file_count"] >= 2, f"Poucos arquivos: {result['file_count']}"

    # Verifica conteudo do .zip
    with zipfile.ZipFile(zip_path, 'r') as zf:
        names = zf.namelist()
        # Deve ter addons/mcp_addon/plugin.cfg
        assert "addons/mcp_addon/plugin.cfg" in names, f"plugin.cfg ausente: {names}"
        # Deve ter LICENSE
        assert "LICENSE" in names, f"LICENSE ausente: {names}"


def test_package_via_rollup(cleanup_dist):
    """Package via rollup publish_manage."""
    result = publish_manage("package", {"addon": "mcp_addon", "include_license": True})
    assert result["status"] == "success"
    zip_path = Path(result["zip_path"])
    assert zip_path.exists()


def test_package_addon_inexistente(cleanup_dist):
    """Addon inexistente retorna erro ao empacotar."""
    result = publish_manage("package", {"addon": "addon_fantasma"})
    assert result["status"] == "error"


def test_package_all_addons(cleanup_dist):
    """Todos os addons conhecidos empacotam sem erro."""
    for name in ADDONS:
        result = _package_addon(name)
        assert result["status"] == "success", f"{name} falhou: {result}"
        zip_path = Path(result["zip_path"])
        assert zip_path.exists(), f"ZIP nao criado para {name}"


# ── Testes: rollup dispatch ─────────────────────────────────────────

def test_rollup_op_invalida():
    """Operacao invalida retorna erro."""
    result = publish_manage("op_que_nao_existe")
    assert result["status"] == "error"


def test_rollup_addon_invalido():
    """Addon invalido retorna erro em qualquer op."""
    for op in ["package", "validate", "metadata", "preview"]:
        result = publish_manage(op, {"addon": "fantasma"})
        assert result["status"] == "error", f"{op} deveria falhar com addon invalido"
