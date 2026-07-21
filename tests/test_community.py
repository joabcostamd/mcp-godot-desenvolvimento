"""test_community.py — Testes para community_ops (Gaps ONDA 4).

Testa as 4 operacoes do rollup community_manage:
  - changelog: gera CHANGELOG.md
  - release_notes: gera notas de release
  - roadmap_public: gera ROADMAP.md
  - badge: retorna snippet Markdown/HTML
"""

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tools.community_ops import (
    community_manage,
    _classify_commit,
    _get_badge_snippet,
    _generate_changelog,
    _generate_release_notes,
    _generate_roadmap_public,
)


# ── Testes: classify_commit ──────────────────────────────────────────

def test_classify_feat():
    assert _classify_commit("feat(onda-4): 4.A publish_manage") == "added"


def test_classify_fix():
    assert _classify_commit("fix: corrige bug no bridge") == "fixed"


def test_classify_docs():
    assert _classify_commit("docs: atualiza README") == "docs"


def test_classify_test():
    assert _classify_commit("test: adiciona testes de comunidade") == "tests"


def test_classify_refactor():
    assert _classify_commit("refactor: extrai helper") == "changed"


def test_classify_perf():
    assert _classify_commit("perf: otimiza loop") == "perf"


def test_classify_breaking():
    assert _classify_commit("feat!: breaking change") == "breaking"


def test_classify_default():
    assert _classify_commit("chore: atualiza deps") == "changed"


# ── Testes: badge ────────────────────────────────────────────────────

def test_badge_returns_markdown():
    result = _get_badge_snippet()
    assert result["status"] == "success"
    assert "markdown" in result
    assert "html" in result
    assert "![Made with MCP Godot Agent]" in result["markdown"]
    assert "badge.svg" in result["badge_url"]


def test_badge_via_rollup():
    result = community_manage("badge")
    assert result["status"] == "success"
    assert "markdown" in result


# ── Testes: changelog ────────────────────────────────────────────────

def test_changelog_returns_success():
    result = _generate_changelog()
    assert result["status"] == "success"
    assert "total_commits" in result


def test_changelog_via_rollup():
    result = community_manage("changelog")
    assert result["status"] == "success"


# ── Testes: release_notes ────────────────────────────────────────────

def test_release_notes_returns_success():
    result = _generate_release_notes(version="v1.0.0")
    assert result["status"] == "success"
    assert "release_notes" in result
    assert "v1.0.0" in result["release_notes"]


def test_release_notes_auto_version():
    result = _generate_release_notes()
    # Pode ser success ou error se nao houver commits
    assert result["status"] in ("success", "error")


def test_release_notes_via_rollup():
    result = community_manage("release_notes", {"version": "v1.0.0"})
    assert result["status"] == "success"


# ── Testes: roadmap_public ───────────────────────────────────────────

def test_roadmap_public_creates_file():
    result = _generate_roadmap_public()
    assert result["status"] == "success"
    assert result["total_fatias"] > 0
    roadmap_path = ROOT / "ROADMAP.md"
    assert roadmap_path.exists(), "ROADMAP.md nao foi criado"


def test_roadmap_public_via_rollup():
    result = community_manage("roadmap_public")
    assert result["status"] == "success"
    assert result["total_fatias"] > 0


# ── Testes: rollup dispatch ──────────────────────────────────────────

def test_invalid_op():
    result = community_manage("op_invalida")
    assert result["status"] == "error"


def test_params_none():
    result = community_manage("badge", None)
    assert result["status"] == "success"
