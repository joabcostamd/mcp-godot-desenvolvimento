"""Testes automatizados para personas — Fatia 3.B.

Cobre: listagem de personas, validação de persona_run, erros.
"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tools.playtest_ops import playtest_manage
from tools.personas import list_personas, get_persona, KEY_MAP, PERSONAS


class TestPersonasLib:
    def test_list_personas(self):
        r = list_personas()
        assert r["status"] == "success"
        assert len(r["personas"]) == 3
        ids = [p["id"] for p in r["personas"]]
        assert "apressado" in ids
        assert "cauteloso" in ids
        assert "explorador" in ids

    def test_get_persona_valid(self):
        p = get_persona("apressado")
        assert p is not None
        assert p["name"] == "Apressado"
        assert len(p["inputs"]) > 0

    def test_get_persona_invalid(self):
        p = get_persona("invalido")
        assert p is None

    def test_all_personas_have_inputs(self):
        for pid, pdata in PERSONAS.items():
            assert len(pdata["inputs"]) > 0, f"{pid} sem inputs"
            for step in pdata["inputs"]:
                assert "action" in step, f"{pid}: step sem action"
                assert step["action"] in KEY_MAP, f"{pid}: action '{step['action']}' nao mapeada"

    def test_key_map_has_common_actions(self):
        assert "ui_right" in KEY_MAP
        assert "ui_left" in KEY_MAP
        assert "ui_up" in KEY_MAP
        assert "ui_accept" in KEY_MAP
        assert "space" in KEY_MAP


class TestOpPersonaRun:
    def test_persona_run_without_game(self):
        """Sem jogo rodando, deve retornar erro."""
        r = playtest_manage(op="persona_run", params={"persona": "apressado"})
        assert r["status"] == "error"

    def test_persona_run_missing_persona(self):
        r = playtest_manage(op="persona_run")
        assert r["status"] == "error"
        assert "available_personas" in r

    def test_persona_run_invalid_persona(self):
        r = playtest_manage(op="persona_run", params={"persona": "invalido"})
        assert r["status"] == "error"
        assert "available_personas" in r

    def test_persona_run_invalid_duration(self):
        r = playtest_manage(op="persona_run", params={"persona": "apressado", "duration": 1})
        assert r["status"] == "error"
        assert "duracao" in r["message"].lower()


class TestSmokeRegressao:
    """Garante que smoke ainda funciona apos adicionar persona_run."""

    def test_smoke_still_works(self):
        r = playtest_manage(op="smoke")
        assert r["status"] == "error"  # sem jogo
        assert "debug" in r["message"].lower() or "8790" in r["message"]
