"""rag_ops.py — RAG Local para Memoria Semantica (FATIA 2.AE).

Indexa GDD, decisoes de design e codigo fonte do projeto para busca
semantica local. Elimina o ritual de colar documentos no prompt.

Implementacao: TF-IDF + cosine similarity (zero dependencias externas).
Armazena indices em .mcp_rag_index.json no projeto.

Fonte: pesquisa em tecnicas de Information Retrieval (TF-IDF, 1972).
"""

import json
import math
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent

# Stopwords PT-BR para filtragem
_STOPWORDS = {
    "o", "a", "os", "as", "um", "uma", "uns", "umas",
    "de", "da", "do", "das", "dos", "em", "no", "na", "nos", "nas",
    "para", "por", "com", "sem", "que", "se", "nao", "e", "ou",
    "mas", "como", "quando", "onde", "qual", "quais", "isso", "isto",
    "aquele", "aquela", "este", "esta", "esse", "essa", "ele", "ela",
    "the", "a", "an", "is", "are", "was", "were", "be", "been",
    "have", "has", "had", "do", "does", "did", "will", "would",
    "can", "could", "should", "may", "might", "shall", "to", "of",
    "in", "on", "at", "by", "for", "with", "about", "this", "that",
    "it", "its", "and", "or", "not", "but", "if", "then", "else",
}


def _tokenize(text: str) -> list[str]:
    """Tokeniza e normaliza texto para indexacao."""
    # Remove pontuacao e normaliza
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)
    tokens = text.split()
    # Remove stopwords e tokens curtos
    return [t for t in tokens if t not in _STOPWORDS and len(t) > 1]


def _compute_tf(tokens: list[str]) -> dict[str, float]:
    """Calcula Term Frequency normalizada."""
    tf = defaultdict(float)
    for t in tokens:
        tf[t] += 1
    # Normaliza pelo maximo
    max_freq = max(tf.values()) if tf else 1
    return {t: f / max_freq for t, f in tf.items()}


def _compute_idf(documents: list[list[str]]) -> dict[str, float]:
    """Calcula Inverse Document Frequency."""
    N = len(documents)
    if N == 0:
        return {}
    df = defaultdict(int)
    for doc in documents:
        for token in set(doc):
            df[token] += 1
    return {t: math.log(N / (df[t] + 1)) + 1 for t in df}


def _cosine_similarity(vec1: dict[str, float], vec2: dict[str, float]) -> float:
    """Calcula similaridade de cosseno entre dois vetores esparsos."""
    dot = sum(vec1.get(k, 0) * vec2.get(k, 0) for k in set(vec1) | set(vec2))
    norm1 = math.sqrt(sum(v ** 2 for v in vec1.values()))
    norm2 = math.sqrt(sum(v ** 2 for v in vec2.values()))
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return dot / (norm1 * norm2)


def index_project(project_path: str = ".", force_rebuild: bool = False) -> dict:
    """Indexa o projeto para busca semantica.

    Le GDD (.md), decisoes (decisions.md, decisoes.md), e codigo (.gd).

    Args:
        project_path: Caminho do projeto.
        force_rebuild: Se True, reconstroi o indice mesmo se ja existir.

    Returns:
        dict com status e numero de documentos indexados.
    """
    project_dir = Path(project_path).resolve()
    index_file = project_dir / ".mcp_rag_index.json"

    if index_file.exists() and not force_rebuild:
        return {"status": "already_indexed", "index_file": str(index_file)}

    documents = []
    doc_sources = []

    # Indexa arquivos .md (GDD, decisoes, docs)
    for md_file in project_dir.rglob("*.md"):
        try:
            text = md_file.read_text(encoding="utf-8")
            if len(text) > 50:  # Ignora arquivos muito curtos
                documents.append(text)
                doc_sources.append(str(md_file.relative_to(project_dir)))
        except (OSError, UnicodeDecodeError):
            continue

    # Indexa arquivos .gd (codigo fonte)
    for gd_file in project_dir.rglob("*.gd"):
        try:
            text = gd_file.read_text(encoding="utf-8")
            if len(text) > 50:
                documents.append(text)
                doc_sources.append(str(gd_file.relative_to(project_dir)))
        except (OSError, UnicodeDecodeError):
            continue

    if not documents:
        return {"status": "empty", "message": "Nenhum documento encontrado para indexar."}

    # Tokeniza e computa TF-IDF
    tokenized = [_tokenize(doc) for doc in documents]
    idf = _compute_idf(tokenized)
    tfidf_vectors = []
    for tokens in tokenized:
        tf = _compute_tf(tokens)
        vec = {t: tf[t] * idf.get(t, 0) for t in tf}
        tfidf_vectors.append(vec)

    # Salva indice
    index_data = {
        "sources": doc_sources,
        "idf": idf,
        "vectors": [{t: round(v, 6) for t, v in vec.items()} for vec in tfidf_vectors],
        "doc_count": len(documents),
    }
    index_file.write_text(json.dumps(index_data, ensure_ascii=False, indent=2), encoding="utf-8")

    return {
        "status": "indexed",
        "index_file": str(index_file),
        "documents": len(documents),
        "sources": doc_sources[:10],
        "message": f"{len(documents)} documentos indexados. Use search_project() para buscar.",
    }


def search_project(query: str, project_path: str = ".", top_k: int = 5) -> dict:
    """Busca semantica no projeto indexado.

    Args:
        query: Texto da busca em portugues ou ingles.
        project_path: Caminho do projeto.
        top_k: Numero de resultados.

    Returns:
        dict com resultados ranqueados por relevancia.
    """
    project_dir = Path(project_path).resolve()
    index_file = project_dir / ".mcp_rag_index.json"

    if not index_file.exists():
        return {"status": "not_indexed", "message": "Projeto nao indexado. Execute index_project() primeiro."}

    try:
        with open(index_file, "r", encoding="utf-8") as f:
            index = json.load(f)
    except (json.JSONDecodeError, OSError):
        return {"status": "error", "message": "Indice corrompido. Reconstrua com force_rebuild=True."}

    # Tokeniza a query e computa TF-IDF
    query_tokens = _tokenize(query)
    query_tf = _compute_tf(query_tokens)
    idf = index["idf"]
    query_vec = {t: query_tf[t] * idf.get(t, 0) for t in query_tf if t in idf}

    if not query_vec:
        return {"status": "no_match", "message": "Nenhum termo relevante encontrado na query."}

    # Calcula similaridade com cada documento
    scores = []
    for i, vec in enumerate(index["vectors"]):
        sim = _cosine_similarity(query_vec, vec)
        if sim > 0:
            scores.append((sim, index["sources"][i]))

    scores.sort(reverse=True)
    top_results = scores[:top_k]

    return {
        "status": "success",
        "query": query,
        "results": [
            {"score": round(score, 4), "source": source}
            for score, source in top_results
        ],
        "total_indexed": index["doc_count"],
        "message": f"{len(top_results)} resultado(s) para '{query}'.",
    }
