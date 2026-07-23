"""
tools/semantic_search.py — Busca semântica bilíngue sobre behaviors (sota_1.2).

Bridge entre o MCP (venv principal, Python 3.14) e o embed_service (venv_ml,
Python 3.12 + FlagEmbedding). Chamado via subprocess.run com stdin=DEVNULL.

Fonte: SOTA_01_FUNDACAO_CEREBRO.md, seção sota_1.2.
"""

import json
import os
import glob as gl
import subprocess
from subprocess import DEVNULL
from typing import List, Dict, Optional, Any

# Caminhos absolutos via __file__ (independente de CWD)
_TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.normpath(os.path.join(_TOOLS_DIR, ".."))
_EMBED_SERVICE = os.path.join(_REPO_ROOT, "ml", "embed_service.py")
_VENV_ML_PYTHON = os.path.join(_REPO_ROOT, ".venv_ml", "Scripts", "python.exe")
_INDEX_DIR = os.path.join(_REPO_ROOT, "behaviors", "_index")
_IDS_FILE = os.path.join(_INDEX_DIR, "ids.json")

# Cache em memória por sessão
_QUERY_CACHE: Dict[str, List[Dict[str, Any]]] = {}


def _chamar_embed_service(modo: str, texto: str = "") -> dict:
    """
    Chama o embed_service.py no venv_ml via subprocess.
    Retorna o JSON de saída como dict.
    """
    args = [_VENV_ML_PYTHON, _EMBED_SERVICE, modo]
    if texto:
        args.append(texto)

    try:
        result = subprocess.run(
            args,
            capture_output=True,
            text=True,
            stdin=DEVNULL,
            timeout=120,  # 2 min — primeira chamada carrega modelo
            cwd=os.path.abspath("."),
        )
        if result.returncode != 0:
            return {"error": f"embed_service exit {result.returncode}: {result.stderr[:500]}"}
        return json.loads(result.stdout.strip())
    except subprocess.TimeoutExpired:
        return {"error": "Timeout ao chamar embed_service (120s)"}
    except json.JSONDecodeError as e:
        return {"error": f"JSON inválido do embed_service: {e}"}


def search_behaviors(query: str) -> List[Dict[str, Any]]:
    """
    Busca behaviors por similaridade semântica + léxica.

    Score final = 0.7 * semântico (BGE-M3) + 0.3 * léxico (sinônimos exatos).

    Returns:
        Lista de [{id, nome, score, score_semantico, score_lexico}, ...].
    """
    # Cache
    if query in _QUERY_CACHE:
        return _QUERY_CACHE[query]

    # 1. Busca semântica (BGE-M3)
    raw = _chamar_embed_service("query", query)
    semantic_results = raw.get("resultados", [])

    # 2. Busca léxica (sinônimos exatos nas fichas)
    lexical_scores = _buscar_lexico(query)

    # 3. Fusão: 0.7*semântico + 0.3*léxico
    fused: Dict[str, Dict[str, Any]] = {}
    for r in semantic_results:
        nome = r["nome"]
        fused[nome] = {
            "id": r["id"],
            "nome": nome,
            "score_semantico": r["score"],
            "score_lexico": lexical_scores.get(nome, 0.0),
        }

    # Adiciona matches léxicos que não apareceram na busca semântica
    for nome, lex_score in lexical_scores.items():
        if nome not in fused:
            fused[nome] = {
                "id": nome,
                "nome": nome,
                "score_semantico": 0.0,
                "score_lexico": lex_score,
            }

    # Calcula score final
    for entry in fused.values():
        entry["score"] = round(
            0.7 * entry["score_semantico"] + 0.3 * entry["score_lexico"], 4
        )

    # Ordena por score descendente
    sorted_results = sorted(fused.values(), key=lambda x: x["score"], reverse=True)

    # Cache
    _QUERY_CACHE[query] = sorted_results
    return sorted_results


def _buscar_lexico(query: str) -> Dict[str, float]:
    """
    Busca léxica: match exato de palavras da query nos sinônimos das fichas.
    Retorna {nome_behavior: score_normalizado}.
    """
    query_lower = query.lower()
    palavras_query = set(query_lower.split())

    scores: Dict[str, float] = {}

    pattern = os.path.join(_REPO_ROOT, "behaviors", "*", "behavior.json")
    for path in sorted(gl.glob(pattern)):
        nome = os.path.basename(os.path.dirname(path))
        if nome.startswith("_"):
            continue
        try:
            with open(path, encoding="utf-8") as f:
                ficha = json.load(f)
        except (json.JSONDecodeError, OSError):
            continue

        score = 0.0

        # Match no nome
        if nome in query_lower or query_lower in nome:
            score += 0.5

        # Match em sinônimos
        sinonimos = ficha.get("sinônimos", [])
        if isinstance(sinonimos, list):
            for s in sinonimos:
                s_lower = s.lower()
                if s_lower in query_lower or any(p in s_lower for p in palavras_query):
                    score += 0.3

        # Match em verbos
        for campo in ["verbo_pt", "verbo_en"]:
            verbo = ficha.get(campo, "")
            if verbo and (verbo.lower() in query_lower or query_lower in verbo.lower()):
                score += 0.2

        # Match em tags
        tags = ficha.get("tags", [])
        if isinstance(tags, list):
            for t in tags:
                if t.lower() in query_lower:
                    score += 0.15

        if score > 0:
            scores[nome] = min(score, 1.0)  # Cap em 1.0

    return scores


def reindex() -> dict:
    """
    Reindexa todos os behaviors (regenera embeddings.npz + ids.json).
    Chamado automaticamente quando enriquecer_fichas aplica lote.
    """
    global _QUERY_CACHE
    _QUERY_CACHE.clear()
    return _chamar_embed_service("index")


def indice_existe() -> bool:
    """Verifica se o índice de embeddings existe."""
    return os.path.exists(os.path.join(_INDEX_DIR, "embeddings.npz"))


def ids_disponiveis() -> List[str]:
    """Lista todos os ids de behaviors no índice."""
    if not os.path.exists(_IDS_FILE):
        return []
    with open(_IDS_FILE, encoding="utf-8") as f:
        data = json.load(f)
    return [entry["id"] for entry in data]
