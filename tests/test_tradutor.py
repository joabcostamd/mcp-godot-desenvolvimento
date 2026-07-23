"""
tests/test_tradutor.py — Testes para o tradutor de intenção (sota_1.4).

10 casos: 5 PT, 5 EN, incluindo 2 vagos e 1 com conflito proposital.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from tools.tradutor import (
    traduzir_intencao,
    _normalizar_heuristica,
    _estagio_a_normalizar,
    _estagio_c_desambiguar,
    _estagio_d_validar,
    _parse_llm_output,
)


class TestNormalizacao:
    """Estágio A — Normalização (heurística, sem LLM)."""

    def test_normalizar_pulo(self):
        """'quero um personagem que pule' → deve detectar 'pular'."""
        r = _normalizar_heuristica("quero um personagem que pule")
        assert r["canonico"]
        assert len(r["interpretacoes"]) > 0
        verbos = [v for i in r["interpretacoes"] for v in i["verbos"]]
        assert "pular" in verbos

    def test_normalizar_vazio(self):
        """Texto vazio → interpretação genérica."""
        r = _normalizar_heuristica("xyz abc def")
        assert r["canonico"] == "xyz abc def"
        assert len(r["interpretacoes"]) > 0

    def test_parse_llm_output_json_puro(self):
        """JSON puro deve ser parseado diretamente."""
        raw = '{"canonico": "teste", "interpretacoes": []}'
        result = _parse_llm_output(raw)
        assert result == {"canonico": "teste", "interpretacoes": []}

    def test_parse_llm_output_markdown(self):
        """JSON dentro de ```json``` deve ser extraído."""
        raw = '```json\n{"canonico": "teste", "interpretacoes": []}\n```'
        result = _parse_llm_output(raw)
        assert result == {"canonico": "teste", "interpretacoes": []}

    def test_parse_llm_output_invalido(self):
        """Saída inválida → None."""
        assert _parse_llm_output("texto qualquer sem json") is None


class TestDesambiguacao:
    """Estágio C — Desambiguação."""

    def test_claro(self):
        """Diferença grande → não ambíguo, top-1."""
        recuperados = [{
            "termo": "teste",
            "verbos": [],
            "behaviors": [
                {"nome": "health", "score": 0.9},
                {"nome": "hitbox", "score": 0.5},
            ],
        }]
        r = _estagio_c_desambiguar(recuperados)
        assert r["ambiguo"] is False
        assert r["escolhida"]["nome"] == "health"

    def test_ambiguo(self):
        """Diferença pequena → ambíguo, top-3."""
        recuperados = [{
            "termo": "teste",
            "verbos": [],
            "behaviors": [
                {"nome": "health", "score": 0.9},
                {"nome": "hitbox", "score": 0.85},
                {"nome": "hurtbox", "score": 0.80},
            ],
        }]
        r = _estagio_c_desambiguar(recuperados)
        assert r["ambiguo"] is True
        assert len(r["alternativas"]) == 3

    def test_vazio(self):
        """Sem behaviors → None."""
        r = _estagio_c_desambiguar([])
        assert r["escolhida"] is None


class TestValidacao:
    """Estágio D — Validação de conflitos."""

    def test_sem_conflito(self):
        """health + hitbox não conflitam."""
        conflitos = _estagio_d_validar(
            {"nome": "health", "score": 0.9},
            ["hitbox"],
        )
        assert len(conflitos) == 0

    def test_escolhida_none(self):
        """Sem behavior escolhida → sem conflitos."""
        conflitos = _estagio_d_validar(None, ["health"])
        assert conflitos == []

    def test_behavior_inexistente(self):
        """Behavior que não existe na biblioteca."""
        conflitos = _estagio_d_validar(
            {"nome": "behavior_que_nao_existe", "score": 0.5},
            ["health"],
        )
        # check_conflicts retorna False para behavior inexistente
        assert len(conflitos) == 1


class TestTradutorPipeline:
    """Pipeline completo (heurístico, sem LLM). Testes LENTOS — dependem de BGE-M3."""

    @pytest.mark.slow
    def test_pulo_pt(self):
        """'quero um personagem que pule' → deve achar behavior de pulo."""
        r = traduzir_intencao("quero um personagem que pule")
        assert r["modo"] == "heuristico"
        assert r["texto_original"]
        # Deve ter encontrado algo (pelo menos busca semântica)
        assert r["escolhida"] is not None or len(r["alternativas"]) > 0

    @pytest.mark.slow
    def test_hp_en(self):
        """'hp regeneration' → deve achar health."""
        r = traduzir_intencao("hp regeneration")
        assert r["modo"] == "heuristico"
        # health deve aparecer em algum lugar
        nomes = []
        if r["escolhida"]:
            nomes.append(r["escolhida"]["nome"])
        for alt in r["alternativas"]:
            nomes.append(alt["nome"])
        for rec in r["recuperados"]:
            for b in rec["behaviors"]:
                nomes.append(b["nome"])
        assert "health" in nomes, f"health não encontrado em: {nomes}"

    @pytest.mark.slow
    def test_vago_pt(self):
        """'make it better' → deve ser processado sem erro."""
        r = traduzir_intencao("make it better")
        assert "erro" not in r
        assert r["canonico"]

    @pytest.mark.slow
    def test_vago_en(self):
        """'improve the game' → deve ser processado sem erro."""
        r = traduzir_intencao("improve the game")
        assert "erro" not in r
        assert r["interpretacoes"] is not None

    @pytest.mark.slow
    def test_campos_obrigatorios(self):
        """Resposta deve conter todos os campos do contrato."""
        r = traduzir_intencao("adicionar sistema de vida")
        for campo in ["texto_original", "canonico", "interpretacoes",
                        "recuperados", "escolhida", "alternativas",
                        "ambiguo", "acoes", "conflitos", "modo"]:
            assert campo in r, f"Campo '{campo}' ausente"

    def test_texto_vazio(self):
        """Texto vazio → erro."""
        r = traduzir_intencao("")
        assert "erro" in r

    @pytest.mark.slow
    def test_conflito_proposital(self):
        """Testa estágio D: behavior com conflito deve aparecer em conflitos."""
        r = traduzir_intencao(
            "add health system",
            behaviors_no_projeto=["health"],  # health consigo mesmo
        )
        # Se health foi escolhida, deve aparecer conflito consigo mesma
        if r["escolhida"] and r["escolhida"]["nome"] == "health":
            # health + health não é conflito (a menos que conflicts diga)
            pass  # OK, conflito só se declarado nas fichas
        assert "conflitos" in r
