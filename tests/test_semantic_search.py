"""
tests/test_semantic_search.py — Testes para busca semântica (sota_1.2).
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from tools.semantic_search import (
    search_behaviors,
    indice_existe,
    ids_disponiveis,
    _buscar_lexico,
)


class TestIndice:
    """Verifica que o índice existe e tem 249 behaviors."""

    def test_indice_existe(self):
        """Embeddings e IDs foram gerados."""
        assert indice_existe(), "Índice embeddings.npz não encontrado. Rode 'embed_service.py index'."

    def test_ids_249(self):
        """IDs devem ter 249 entradas."""
        ids = ids_disponiveis()
        assert len(ids) == 249, f"Esperado 249, obtido {len(ids)}"


class TestBuscaLexica:
    """Busca léxica por sinônimos e verbos."""

    def test_health_match(self):
        """'health' deve aparecer na busca léxica."""
        scores = _buscar_lexico("health")
        assert "health" in scores, "health não encontrado na busca léxica"
        assert scores["health"] > 0

    def test_jump_match(self):
        """'jump' deve achar player_controller ou double_jump."""
        scores = _buscar_lexico("jump")
        has_jump_related = any(
            name in scores for name in ["player_controller", "double_jump", "coyote_time", "variable_jump"]
        )
        assert has_jump_related, f"Nenhum behavior de pulo encontrado: {list(scores.keys())[:5]}"


class TestBuscaSemantica:
    """Testes das queries de aceite do sota_1.2."""

    def test_pulo_macio(self):
        """'fazer o personagem dar um pulo mais macio' → player_controller ou coyote_time no top-5."""
        resultados = search_behaviors("fazer o personagem dar um pulo mais macio")
        nomes = [b["nome"] for b in resultados[:5]]
        tem = "player_controller" in nomes or "coyote_time" in nomes or "double_jump" in nomes
        assert tem, f"Top-5: {nomes} — esperado player_controller, coyote_time ou double_jump"

    def test_hp_regen(self):
        """'hp regeneration' → health ou regen no top-5."""
        resultados = search_behaviors("hp regeneration")
        nomes = [b["nome"] for b in resultados[:5]]
        tem = "health" in nomes or "regen" in nomes
        assert tem, f"Top-5: {nomes} — esperado health ou regen"

    def test_score_decrescente(self):
        """Resultados devem vir em ordem decrescente de score."""
        resultados = search_behaviors("plataforma")
        if len(resultados) >= 2:
            for i in range(len(resultados) - 1):
                assert resultados[i]["score"] >= resultados[i + 1]["score"], (
                    f"Score não decrescente: {resultados[i]['score']} < {resultados[i+1]['score']}"
                )

    def test_resultados_tem_campos_obrigatorios(self):
        """Cada resultado deve ter id, nome, score, score_semantico, score_lexico."""
        resultados = search_behaviors("teste")
        if resultados:
            r = resultados[0]
            for campo in ["id", "nome", "score", "score_semantico", "score_lexico"]:
                assert campo in r, f"Campo '{campo}' ausente em {r}"


class TestCache:
    """Cache em memória por sessão."""

    def test_cache_retorna_mesmo_resultado(self):
        """Segunda chamada com mesma query deve retornar do cache."""
        r1 = search_behaviors("cache_test_unique_query_xyz")
        r2 = search_behaviors("cache_test_unique_query_xyz")
        assert r1 == r2
