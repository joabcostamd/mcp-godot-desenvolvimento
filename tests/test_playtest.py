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
