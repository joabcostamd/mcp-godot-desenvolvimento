"""Testes automatizados para playtest_manage — Fatia 3.A.

Cobre: caminhos felizes, erros, validacoes de parametro,
e smoke test sem jogo rodando.
"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tools.playtest_ops import playtest_manage


class TestOpSmoke:
    def test_smoke_without_game(self):
        """Sem jogo rodando, smoke deve retornar erro claro."""
        r = playtest_manage(op="smoke")
        assert r["status"] == "error"
        assert "debug" in r["message"].lower() or "8790" in r["message"]

    def test_smoke_invalid_duration(self):
        r = playtest_manage(op="smoke", params={"duration": 0})
        assert r["status"] == "error"
        assert "duracao" in r["message"].lower()

    def test_smoke_negative_duration(self):
        r = playtest_manage(op="smoke", params={"duration": -5})
        assert r["status"] == "error"

    def test_smoke_excessive_duration(self):
        """Duration > 300s deve ser rejeitado."""
        r = playtest_manage(op="smoke", params={"duration": 999})
        assert r["status"] == "error"
        assert "300" in r["message"] or "maximo" in r["message"].lower()

    def test_smoke_invalid_fps_threshold(self):
        r = playtest_manage(op="smoke", params={"fps_threshold": 0})
        assert r["status"] == "error"

    def test_smoke_default_params(self):
        """Com parametros default, deve funcionar (erro esperado: sem jogo)."""
        r = playtest_manage(op="smoke", params={})
        # Sem jogo rodando, espera-se erro
        assert r["status"] == "error"


class TestInvalidOp:
    def test_invalid_op(self):
        r = playtest_manage(op="invalid")
        assert r["status"] == "error"
        assert "available_ops" in r
        assert "smoke" in r["available_ops"]

    def test_suggestion_close_match(self):
        r = playtest_manage(op="smok")
        assert r["status"] == "error"
        assert "suggestions" in r


class TestRollupContract:
    """Verifica que o rollup segue o contrato padrao."""

    def test_returns_dict(self):
        r = playtest_manage(op="smoke")
        assert isinstance(r, dict)

    def test_has_status_key(self):
        r = playtest_manage(op="smoke")
        assert "status" in r

    def test_error_has_message(self):
        r = playtest_manage(op="smoke")
        if r["status"] == "error":
            assert "message" in r


class TestAgentObserve:
    def test_observe_without_game(self):
        r = playtest_manage(op="agent_observe")
        assert r["status"] == "error"
        assert "rodando" in r["message"].lower()

    def test_observe_returns_available_actions(self):
        """Mesmo sem jogo, a estrutura de resposta deve ser coerente."""
        r = playtest_manage(op="agent_observe")
        if r["status"] == "success":
            assert "available_actions" in r
            assert "cost_estimate" in r


class TestAgentStep:
    def test_step_without_action(self):
        r = playtest_manage(op="agent_step")
        assert r["status"] == "error"
        assert "action" in r["message"].lower()

    def test_step_invalid_hold(self):
        r = playtest_manage(op="agent_step", params={"action": "ui_right", "hold_ms": 5})
        assert r["status"] == "error"

    def test_step_without_game(self):
        r = playtest_manage(op="agent_step", params={"action": "ui_right", "hold_ms": 200})
        assert r["status"] == "error"


class TestAgentRun:
    def test_run_without_game(self):
        r = playtest_manage(op="agent_run")
        assert r["status"] == "error"
        assert "rodando" in r["message"].lower()

    def test_run_invalid_steps(self):
        r = playtest_manage(op="agent_run", params={"steps": 0})
        assert r["status"] == "error"

    def test_run_too_many_steps(self):
        r = playtest_manage(op="agent_run", params={"steps": 50})
        assert r["status"] == "error"

    def test_run_default_params(self):
        """Sem jogo, mesmo agent_run deve retornar erro claro."""
        r = playtest_manage(op="agent_run", params={"steps": 3})
        assert r["status"] == "error"
