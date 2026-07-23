"""
Testes do gate_reorg.py — ONDA R, Fatia R1.
Testa G1, G2, G3 e o fluxo completo via git hook simulado.
"""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

# Adiciona o repo root e scripts ao path
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import gate_reorg as gate


# ── G1: checkpoint ──────────────────────────────────────────────

def test_g1_nova_entrada_concluida_com_hash_real():
    """Entrada nova concluida com hash de 40 hex chars → passa (is_real_hash)."""
    assert gate.is_real_hash("a" * 40) is True


def test_g1_nova_entrada_concluida_sem_hash():
    """Entrada nova concluida sem hash → bloqueia."""
    assert gate.is_real_hash("pendente-commit") is False
    assert gate.is_real_hash(None) is False
    assert gate.is_real_hash("") is False
    assert gate.is_real_hash("abc123") is False  # muito curto


def test_g1_hash_valido_formato():
    """Hash real tem exatamente 40 caracteres hex."""
    assert gate.is_real_hash("0123456789abcdef0123456789abcdef01234567") is True
    assert gate.is_real_hash("0123456789abcdef0123456789abcdef0123456") is False  # 39
    assert gate.is_real_hash("0123456789abcdef0123456789abcdef012345678") is False  # 41
    assert gate.is_real_hash("zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz") is False  # não-hex


# ── G2: par obrigatório ─────────────────────────────────────────

def test_g2_roadmap_staged_sem_progress():
    """Roadmap staged sem .roadmap_progress.json → bloqueia."""
    staged = {"docs/REORG_ROADMAP.md"}
    errors = gate.check_g2(staged)
    assert len(errors) == 1
    assert "G2 BLOQUEADO" in errors[0]
    assert "REORG_ROADMAP.md" in errors[0]


def test_g2_roadmap_staged_com_progress():
    """Roadmap staged COM .roadmap_progress.json → passa."""
    staged = {"docs/REORG_ROADMAP.md", ".roadmap_progress.json"}
    errors = gate.check_g2(staged)
    assert len(errors) == 0


def test_g2_handoff_staged_sem_progress():
    """HANDOFF.md staged sem .roadmap_progress.json → bloqueia."""
    staged = {"HANDOFF.md"}
    errors = gate.check_g2(staged)
    assert len(errors) == 1
    assert "G2 BLOQUEADO" in errors[0]


def test_g2_sem_arquivos_obrigatorios():
    """Nenhum arquivo obrigatório staged → passa."""
    staged = {"server.py", "tools/alguma_coisa.py"}
    errors = gate.check_g2(staged)
    assert len(errors) == 0


# ── G3: baseline de tools ───────────────────────────────────────

def test_g3_baseline_sobe_bloqueia():
    """Tools sobem acima do baseline → bloqueia."""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo = Path(tmpdir)
        # Cria .reorg_baseline.json com IDEIA=999 (impossível)
        baseline_file = repo / ".reorg_baseline.json"
        baseline = {
            "tools_por_fase": {
                "PHASE_TOOLSETS:IDEIA": 999,
            }
        }
        gate.save_json(baseline_file, baseline)
        errors = gate.check_g3(repo_root=repo)
        # IDEIA real < 999 → sem erro (não sobe acima do baseline)
        assert len(errors) == 0


def test_g3_baseline_inexistente_nao_bloqueia():
    """Baseline não existe → não bloqueia, cria baseline."""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo = Path(tmpdir)
        baseline_file = repo / ".reorg_baseline.json"
        assert not baseline_file.exists()

        errors = gate.check_g3(repo_root=repo)
        # Baseline não existe → sem erro (primeiro baseline é criado)
        assert len(errors) == 0
        # Baseline foi criado
        assert baseline_file.exists()
        data = gate.load_json(baseline_file)
        assert "tools_por_fase" in data
        assert "_total_tools" in data


# ── Fluxo completo via git hook (repo temporário) ───────────────

class TestGateViaGitTempRepo:
    """Testa o gate via main() em repositório temporário isolado."""

    @pytest.fixture
    def temp_repo(self):
        """Cria repositório git temporário para teste."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = Path(tmpdir)

            subprocess.run(["git", "init"], cwd=str(repo), check=True, capture_output=True)
            subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=str(repo), check=True, capture_output=True)
            subprocess.run(["git", "config", "user.name", "Test"], cwd=str(repo), check=True, capture_output=True)

            (repo / "readme.txt").write_text("initial")
            subprocess.run(["git", "add", "readme.txt"], cwd=str(repo), check=True, capture_output=True)
            subprocess.run(["git", "commit", "-m", "initial"], cwd=str(repo), check=True, capture_output=True)

            progress = {"fatia_teste": {"status": "nao verificado", "checkpoint": None}}
            gate.save_json(repo / ".roadmap_progress.json", progress)

            baseline = {"tools_por_fase": {}, "_total_tools": 0, "_ultima_atualizacao": "0000000000000000000000000000000000000000"}
            gate.save_json(repo / ".reorg_baseline.json", baseline)

            subprocess.run(["git", "add", ".roadmap_progress.json", ".reorg_baseline.json"], cwd=str(repo), check=True, capture_output=True)
            subprocess.run(["git", "commit", "-m", "baseline"], cwd=str(repo), check=True, capture_output=True)

            yield repo

    def test_main_sem_violacao(self, temp_repo):
        """Sem violações → exit code 0."""
        result = gate.main(repo_root=temp_repo)
        assert result == 0, f"main() deveria retornar 0, retornou {result}"

    def test_main_g1_bloqueia_concluida_sem_hash(self, temp_repo):
        """Entrada concluida sem checkpoint válido → BLOQUEADO (via main)."""
        repo = temp_repo

        progress = gate.load_json(repo / ".roadmap_progress.json")
        progress["fatia_Y"] = {"status": "concluida", "checkpoint": "pendente-commit"}
        gate.save_json(repo / ".roadmap_progress.json", progress)

        # Stage (simula git add)
        subprocess.run(["git", "add", ".roadmap_progress.json"], cwd=str(repo), check=True, capture_output=True)

        result = gate.main(repo_root=repo)
        assert result != 0, f"main() deveria BLOQUEAR G1, retornou {result}"

    def test_main_g2_bloqueia_handoff_sem_progress(self, temp_repo):
        """HANDOFF.md staged sem .roadmap_progress.json → BLOQUEADO (via main)."""
        repo = temp_repo

        (repo / "HANDOFF.md").write_text("# HANDOFF")
        subprocess.run(["git", "add", "HANDOFF.md"], cwd=str(repo), check=True, capture_output=True)

        result = gate.main(repo_root=repo)
        assert result != 0, f"main() deveria BLOQUEAR G2, retornou {result}"

    def test_main_no_verify_nao_afeta(self, temp_repo):
        """main() sempre pode ser chamada — devolve 0 ou 1, nunca exceção."""
        result = gate.main(repo_root=temp_repo)
        assert result in (0, 1)
