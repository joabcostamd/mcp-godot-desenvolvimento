"""
ml/embed_service.py — Serviço de embeddings BGE-M3 para busca semântica (sota_1.2).

Roda NO venv_ml (Python 3.12 + FlagEmbedding), chamado por subprocess do MCP.

Modos:
    index  — Lê todos os behavior.json, gera embeddings.npz + ids.json
    query  — Lê consulta da stdin, imprime JSON com top-10 por cosine similarity

Fonte: BGE-M3 (BAAI, 2024) — https://github.com/FlagOpen/FlagEmbedding
       SOTA_01_FUNDACAO_CEREBRO.md, seção sota_1.2.

Uso:
    .venv_ml/Scripts/python.exe ml/embed_service.py index
    .venv_ml/Scripts/python.exe ml/embed_service.py query "texto da consulta"
"""

import json
import os
import sys
import numpy as np
from typing import List, Dict

# --- Constantes (paths absolutos via __file__) ---
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.normpath(os.path.join(_SCRIPT_DIR, ".."))
BEHAVIORS_DIR = os.path.join(_REPO_ROOT, "behaviors")
INDEX_DIR = os.path.join(BEHAVIORS_DIR, "_index")
EMBEDDINGS_FILE = os.path.join(INDEX_DIR, "embeddings.npz")
IDS_FILE = os.path.join(INDEX_DIR, "ids.json")
MODEL_NAME = "BAAI/bge-m3"


# ═══════════════════════════════════════════════════════════════
# Indexação
# ═══════════════════════════════════════════════════════════════

def _montar_texto(ficha: dict) -> str:
    """Monta o texto de um behavior para embedding (multilíngue)."""
    partes = []

    name = ficha.get("name", "")
    if name:
        partes.append(name)

    verbo_pt = ficha.get("verbo_pt", "")
    if verbo_pt:
        partes.append(verbo_pt)

    verbo_en = ficha.get("verbo_en", "")
    if verbo_en:
        partes.append(verbo_en)

    desc_pt = ficha.get("description_pt", "")
    if desc_pt:
        partes.append(desc_pt)

    desc_en = ficha.get("description_en", "")
    if desc_en:
        partes.append(desc_en)

    sinonimos = ficha.get("sinônimos", [])
    if isinstance(sinonimos, list):
        partes.extend(sinonimos)

    tags = ficha.get("tags", [])
    if isinstance(tags, list):
        partes.extend(tags)

    return " ".join(partes)


def _carregar_fichas() -> List[tuple]:
    """Carrega todos os behavior.json. Retorna [(id, ficha, texto), ...]."""
    import glob
    resultados = []
    pattern = os.path.join(BEHAVIORS_DIR, "*", "behavior.json")

    for path in sorted(glob.glob(pattern)):
        name = os.path.basename(os.path.dirname(path))
        if name.startswith("_"):
            continue
        try:
            with open(path, encoding="utf-8") as f:
                ficha = json.load(f)
        except (json.JSONDecodeError, OSError):
            continue

        texto = _montar_texto(ficha)
        if not texto.strip():
            texto = name  # fallback: só o nome

        resultados.append((name, ficha, texto))

    return resultados


def modo_index() -> None:
    """Indexa todos os behaviors e salva embeddings.npz + ids.json."""
    from FlagEmbedding import BGEM3FlagModel

    print(f"[index] Carregando modelo {MODEL_NAME}...", file=sys.stderr)
    model = BGEM3FlagModel(MODEL_NAME, use_fp16=False)

    print("[index] Lendo behaviors...", file=sys.stderr)
    dados = _carregar_fichas()
    print(f"[index] {len(dados)} behaviors encontrados", file=sys.stderr)

    ids_list = []
    textos = []
    for name, ficha, texto in dados:
        ids_list.append({"id": name, "name": name})
        textos.append(texto)

    print(f"[index] Gerando embeddings para {len(textos)} textos...", file=sys.stderr)
    output = model.encode(
        textos,
        batch_size=32,
        max_length=512,
        return_dense=True,
        return_sparse=False,  # Só denso para manter o índice pequeno
    )

    dense_vecs = output["dense_vecs"]
    print(f"[index] Embeddings gerados: {dense_vecs.shape}", file=sys.stderr)

    os.makedirs(INDEX_DIR, exist_ok=True)

    # Salva embeddings
    np.savez_compressed(EMBEDDINGS_FILE, dense_vecs=dense_vecs)
    print(f"[index] Embeddings salvos em {EMBEDDINGS_FILE}", file=sys.stderr)

    # Salva ids
    with open(IDS_FILE, "w", encoding="utf-8") as f:
        json.dump(ids_list, f, ensure_ascii=False, indent=2)
    print(f"[index] IDs salvos em {IDS_FILE}", file=sys.stderr)

    # Reporta tamanho
    size_mb = os.path.getsize(EMBEDDINGS_FILE) / (1024 * 1024)
    print(f"[index] Tamanho do índice: {size_mb:.1f} MB", file=sys.stderr)
    print("[index] OK", file=sys.stderr)


# ═══════════════════════════════════════════════════════════════
# Consulta
# ═══════════════════════════════════════════════════════════════

def _cosine_similarity(query_vec: np.ndarray, index_vecs: np.ndarray) -> np.ndarray:
    """Calcula cosine similarity entre vetor de consulta e matriz de índice."""
    # Normaliza
    query_norm = query_vec / (np.linalg.norm(query_vec) + 1e-10)
    index_norm = index_vecs / (np.linalg.norm(index_vecs, axis=1, keepdims=True) + 1e-10)
    return np.dot(index_norm, query_norm)


def modo_query(query_text: str) -> None:
    """Embeda a consulta e retorna JSON com top-10 behaviors."""
    from FlagEmbedding import BGEM3FlagModel
    import time

    if not os.path.exists(EMBEDDINGS_FILE) or not os.path.exists(IDS_FILE):
        print(json.dumps({"error": "Índice não encontrado. Rode 'index' primeiro."}))
        sys.exit(1)

    t0 = time.time()

    # Carrega modelo (lento na primeira vez)
    model = BGEM3FlagModel(MODEL_NAME, use_fp16=False)

    # Carrega índice
    data = np.load(EMBEDDINGS_FILE)
    dense_vecs = data["dense_vecs"]

    with open(IDS_FILE, encoding="utf-8") as f:
        ids_list = json.load(f)

    # Embeda consulta
    output = model.encode(
        [query_text],
        batch_size=1,
        max_length=512,
        return_dense=True,
        return_sparse=False,
    )
    query_vec = output["dense_vecs"][0]

    # Cosine similarity
    scores = _cosine_similarity(query_vec, dense_vecs)

    # Top-10
    top_indices = np.argsort(scores)[::-1][:10]

    resultados = []
    for idx in top_indices:
        score = float(scores[idx])
        if score < 0.3:  # Corte mínimo de relevância
            continue
        entry = ids_list[idx]
        resultados.append({
            "id": entry["id"],
            "nome": entry["name"],
            "score": round(score, 4),
        })

    elapsed = time.time() - t0
    output = {
        "query": query_text,
        "resultados": resultados,
        "tempo_s": round(elapsed, 2),
    }
    print(json.dumps(output, ensure_ascii=False))


# ═══════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: embed_service.py index|query <texto>", file=sys.stderr)
        sys.exit(1)

    mode = sys.argv[1]

    if mode == "index":
        modo_index()
    elif mode == "query":
        if len(sys.argv) < 3:
            print("Uso: embed_service.py query <texto>", file=sys.stderr)
            sys.exit(1)
        query_text = " ".join(sys.argv[2:])
        modo_query(query_text)
    else:
        print(f"Modo desconhecido: {mode}", file=sys.stderr)
        sys.exit(1)
