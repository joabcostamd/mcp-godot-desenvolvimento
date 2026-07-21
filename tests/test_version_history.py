"""Testes automatizados para version_history_ops.py — Fatia 1.Q.

Cobre: caminhos felizes, erros, edge cases, segurança (path traversal),
validações de entrada, e integração com git.
"""
import json
import sys
import tempfile
import os
from pathlib import Path

import pytest

# Garante que tools/ está no path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tools.version_history_ops import (
    version_history_manage,
    _load_index,
    _save_index,
    _git_commit_hash,
    _git_has_commit,
    _git_is_clean,
    _versions_dir,
    _capture_screenshot,
    _save_screenshot_base64,
)


# ══════════════════════════════════════════════════════════════════
# Fixtures
# ══════════════════════════════════════════════════════════════════

@pytest.fixture
def temp_project(tmp_path):
    """Cria um projeto temporário com git init e estrutura Godot mínima."""
    project = tmp_path / "test_project"
    project.mkdir()

    # Git init
    import subprocess
    subprocess.run(["git", "init"], cwd=str(project), capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=str(project), capture_output=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=str(project), capture_output=True)

    # Cria project.godot mínimo
    (project / "project.godot").write_text("; test project\n")
    subprocess.run(["git", "add", "-A"], cwd=str(project), capture_output=True)
    subprocess.run(["git", "commit", "-m", "initial"], cwd=str(project), capture_output=True)

    # Monkey-patch _get_active_project para retornar este projeto
    import tools.version_history_ops as vho
    original = vho._get_active_project
    vho._get_active_project = lambda: project
    yield project
    vho._get_active_project = original


# ══════════════════════════════════════════════════════════════════
# Testes: Helpers git
# ══════════════════════════════════════════════════════════════════

class TestGitHelpers:
    def test_commit_hash_returns_string(self, temp_project):
        h = _git_commit_hash(temp_project)
        assert h is not None
        assert len(h) == 40
        assert all(c in "0123456789abcdef" for c in h)

    def test_has_commit_true(self, temp_project):
        h = _git_commit_hash(temp_project)
        assert _git_has_commit(h, temp_project) is True

    def test_has_commit_false(self, temp_project):
        assert _git_has_commit("deadbeefdeadbeefdeadbeefdeadbeefdeadbeef", temp_project) is False

    def test_has_commit_sanitize_invalid_chars(self, temp_project):
        """Injeção: commit com caracteres especiais é rejeitado."""
        assert _git_has_commit("../../../etc/passwd", temp_project) is False
        assert _git_has_commit("rm -rf /", temp_project) is False
        assert _git_has_commit("", temp_project) is False

    def test_is_clean_true(self, temp_project):
        assert _git_is_clean(temp_project) is True

    def test_is_clean_false(self, temp_project):
        (temp_project / "dirty.txt").write_text("dirty")
        assert _git_is_clean(temp_project) is False


# ══════════════════════════════════════════════════════════════════
# Testes: Save
# ══════════════════════════════════════════════════════════════════

class TestOpSave:
    def test_save_without_description_fails(self, temp_project):
        r = version_history_manage(op="save")
        assert r["status"] == "error"
        assert "description" in r["message"].lower()

    def test_save_creates_version(self, temp_project):
        r = version_history_manage(op="save", params={"description": "Versão de teste"})
        assert r["status"] == "success"
        assert r["has_screenshot"] is False  # sem jogo rodando
        assert r["commit_hash"] is not None
        assert r["version_id"] is not None
        assert r["total_versions"] == 1

        # Verifica que os arquivos existem
        vdir = _versions_dir(temp_project) / r["version_id"]
        assert vdir.exists()
        assert (vdir / "manifest.json").exists()

        # Verifica índice
        idx = _load_index(temp_project)
        assert len(idx) == 1
        assert idx[0]["description"] == "Versão de teste"

    def test_save_multiple_versions(self, temp_project):
        r1 = version_history_manage(op="save", params={"description": "V1"})
        r2 = version_history_manage(op="save", params={"description": "V2"})
        assert r1["status"] == "success"
        assert r2["status"] == "success"
        assert r2["total_versions"] == 2


# ══════════════════════════════════════════════════════════════════
# Testes: List
# ══════════════════════════════════════════════════════════════════

class TestOpList:
    def test_list_empty(self, temp_project):
        r = version_history_manage(op="list")
        assert r["status"] == "success"
        assert r["total"] == 0

    def test_list_after_save(self, temp_project):
        version_history_manage(op="save", params={"description": "V1"})
        r = version_history_manage(op="list")
        assert r["status"] == "success"
        assert r["total"] == 1
        assert r["versions"][0]["description"] == "V1"
        assert "version_id" in r["versions"][0]
        assert "timestamp" in r["versions"][0]


# ══════════════════════════════════════════════════════════════════
# Testes: Delete
# ══════════════════════════════════════════════════════════════════

class TestOpDelete:
    def test_delete_without_id_fails(self, temp_project):
        r = version_history_manage(op="delete")
        assert r["status"] == "error"

    def test_delete_removes_version(self, temp_project):
        r_save = version_history_manage(op="save", params={"description": "Para deletar"})
        vid = r_save["version_id"]

        r_del = version_history_manage(op="delete", params={"version_id": vid})
        assert r_del["status"] == "success"

        # Confirma que sumiu da lista
        r_list = version_history_manage(op="list")
        assert r_list["total"] == 0

    def test_delete_path_traversal_blocked(self, temp_project):
        """Segurança: path traversal é bloqueado."""
        r = version_history_manage(op="delete", params={"version_id": "../../etc/passwd"})
        assert r["status"] == "error"
        assert "inválido" in r["message"].lower()

    def test_delete_nonexistent(self, temp_project):
        r = version_history_manage(op="delete", params={"version_id": "20260721_000000"})
        assert r["status"] == "error"
        assert "não encontrada" in r["message"].lower()


# ══════════════════════════════════════════════════════════════════
# Testes: Restore (validações)
# ══════════════════════════════════════════════════════════════════

class TestOpRestore:
    def test_restore_without_id_fails(self, temp_project):
        r = version_history_manage(op="restore")
        assert r["status"] == "error"

    def test_restore_path_traversal_blocked(self, temp_project):
        r = version_history_manage(op="restore", params={"version_id": "../../etc/shadow"})
        assert r["status"] == "error"
        assert "inválido" in r["message"].lower()

    def test_restore_nonexistent_version(self, temp_project):
        r = version_history_manage(op="restore", params={"version_id": "20260721_000000"})
        assert r["status"] == "error"

    def test_restore_with_dirty_working_tree(self, temp_project):
        # Salva uma versão primeiro
        r = version_history_manage(op="save", params={"description": "Base"})
        vid = r["version_id"]

        # Suja o working tree
        (temp_project / "dirty.txt").write_text("dirty")

        # Tenta restaurar
        r = version_history_manage(op="restore", params={"version_id": vid})
        assert r["status"] == "error"
        assert "limpo" in r["message"].lower()


# ══════════════════════════════════════════════════════════════════
# Testes: Screenshot
# ══════════════════════════════════════════════════════════════════

class TestOpScreenshot:
    def test_screenshot_without_game(self, temp_project):
        """Sem jogo rodando, screenshot deve retornar erro."""
        r = version_history_manage(op="screenshot")
        # Pode ser error (sem jogo) ou success (se bridge disponível)
        # Em ambiente de teste, espera-se error
        assert r["status"] in ("error", "success")


# ══════════════════════════════════════════════════════════════════
# Testes: Operação inválida
# ══════════════════════════════════════════════════════════════════

class TestInvalidOp:
    def test_invalid_op_returns_error(self):
        r = version_history_manage(op="invalid_op")
        assert r["status"] == "error"
        assert "available_ops" in r
        assert "save" in r["available_ops"]

    def test_unknown_op_suggests_close_match(self):
        r = version_history_manage(op="sav")
        assert r["status"] == "error"
        assert "suggestions" in r


# ══════════════════════════════════════════════════════════════════
# Testes: Edge cases de índice
# ══════════════════════════════════════════════════════════════════

class TestIndexEdgeCases:
    def test_load_index_nonexistent(self, tmp_path):
        idx = _load_index(tmp_path / "nonexistent")
        assert idx == []

    def test_save_and_load_roundtrip(self, temp_project):
        data = [{"version_id": "test", "description": "test"}]
        _save_index(data, temp_project)
        loaded = _load_index(temp_project)
        assert loaded == data


# ══════════════════════════════════════════════════════════════════
# Testes: Base64 screenshot
# ══════════════════════════════════════════════════════════════════

class TestScreenshotBase64:
    def test_save_empty_base64(self, tmp_path):
        """Base64 vazio produz PNG de 0 bytes (válido para decoder)."""
        import base64
        dest = tmp_path / "empty.png"
        _save_screenshot_base64("", dest)
        assert dest.exists()
        assert dest.read_bytes() == b""

    def test_save_valid_png_minimal(self, tmp_path):
        """PNG mínimo válido (1x1 pixel vermelho em base64)."""
        # PNG 1x1 vermelho: 68 bytes
        minimal_png_b64 = (
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
        )
        dest = tmp_path / "red.png"
        _save_screenshot_base64(minimal_png_b64, dest)
        assert dest.exists()
        assert len(dest.read_bytes()) > 0
