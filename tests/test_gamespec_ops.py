"""
tests/test_gamespec_ops.py — Testes para tools/gamespec_ops.py (sota_1.6).
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from tools.gamespec_ops import (
    check_conflicts,
    listar_conflitos_do_projeto,
    _carregar_fichas,
    invalidar_cache,
    compile_gamespec,
    validate_gamespec,
)


class TestCheckConflicts:
    """sota_1.6: Matriz de conflito executável."""

    def test_sem_conflitos(self):
        """health + hurtbox não têm conflitos declarados."""
        ok, msg = check_conflicts("health", ["hurtbox"])
        assert ok is True
        assert msg == ""

    def test_behavior_inexistente(self):
        """Behavior que não existe na biblioteca deve ser recusado."""
        ok, msg = check_conflicts("behavior_que_nao_existe", [])
        assert ok is False
        assert "não encontrado" in msg.lower()

    def test_behavior_sozinho_sem_conflito(self):
        """Behavior sem conflitos, sem behaviors existentes."""
        ok, msg = check_conflicts("health", [])
        assert ok is True

    def test_listar_conflitos_vazio(self):
        """Projeto sem behaviors não tem conflitos."""
        conflitos = listar_conflitos_do_projeto([])
        assert conflitos == []

    def test_listar_conflitos_sem_conflitos_reais(self):
        """Behaviors que não conflitam entre si."""
        conflitos = listar_conflitos_do_projeto(["health", "hitbox", "hurtbox"])
        # health, hitbox, hurtbox não têm conflicts declarados entre si
        # (só 8 behaviors têm conflicts no total)
        assert len(conflitos) == 0

    def test_mensagem_pt(self):
        """Mensagem de erro deve estar em português."""
        ok, msg = check_conflicts("inexistente", [])
        assert "não encontrado" in msg.lower() or "não encontrada" in msg.lower()


class TestCache:
    """Thread-safe cache de fichas."""

    def test_cache_carrega_249_behaviors(self):
        """Cache deve carregar os 249 behaviors."""
        fichas = _carregar_fichas()
        assert len(fichas) == 249

    def test_cache_invalidar_recarrega(self):
        """invalidar_cache() deve forçar recarga."""
        fichas1 = _carregar_fichas()
        invalidar_cache()
        fichas2 = _carregar_fichas()
        assert len(fichas1) == len(fichas2)
        assert fichas1 is not fichas2  # Objeto diferente após recarga


class TestGameSpecStubs:
    """Stubs de sota_1.5 devem ser explícitos sobre não estarem prontos."""

    def test_compile_gamespec_levanta_not_implemented(self):
        """compile_gamespec deve levantar NotImplementedError, não retornar False."""
        with pytest.raises(NotImplementedError):
            compile_gamespec("teste.json", ".")

    def test_validate_gamespec_json_valido(self):
        """validate_gamespec com JSON válido retorna True."""
        ok, erros = validate_gamespec("behaviors/behavior.schema.json")
        # behavior.schema.json é JSON válido
        assert ok is True
        assert erros == []

    def test_validate_gamespec_arquivo_inexistente(self):
        """validate_gamespec com arquivo inexistente retorna False."""
        ok, erros = validate_gamespec("arquivo_que_nao_existe.json")
        assert ok is False
        assert len(erros) > 0
