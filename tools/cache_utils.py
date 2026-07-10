"""cache_utils.py — Cache de respostas de tools para performance (Onda 5).

TTL por tool: classdb=sessao inteira, project=30s-5min, analysis=5min.
"""

import hashlib
import json
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

_cache: dict = {}
_cache_hits = 0
_cache_misses = 0
_MAX_CACHE_ENTRIES = 500

_TTL_MAP = {
    "query_classdb": 999999, "search_classdb": 999999,
    "list_valid_node_types": 999999, "tool_catalog": 999999,
    "analyze_game_structure": 300, "inspect_project": 60,
    "get_project_settings": 30, "project_map": 120,
    "read_console_output": 5, "get_runtime_state_digest": 2,
    "capture_runtime_errors": 5, "list_backups": 30,
    "get_audit_log": 30, "get_project_history": 60,
}


def cached_tool(tool_name: str, func):
    """Wrapper que adiciona cache com TTL a uma tool handler."""
    ttl = _TTL_MAP.get(tool_name, 0)
    if ttl <= 0:
        return func

    def wrapper(*args, **kwargs):
        global _cache_hits, _cache_misses
        key_data = tool_name + ":" + json.dumps(args, sort_keys=True, default=str) + json.dumps(kwargs, sort_keys=True, default=str)
        cache_key = hashlib.md5(key_data.encode()).hexdigest()
        now = time.time()
        if cache_key in _cache:
            expiry, result = _cache[cache_key]
            if now < expiry:
                _cache_hits += 1
                return result
        _cache_misses += 1
        result = func(*args, **kwargs)
        _cache[cache_key] = (now + ttl, result)
        # LRU eviction: remove entrada mais antiga se excedeu limite
        if len(_cache) > _MAX_CACHE_ENTRIES:
            oldest = min(_cache.keys(), key=lambda k: _cache[k][0])
            del _cache[oldest]
        return result

    wrapper._original = func
    return wrapper


def invalidate_cache(tool_prefix: str | None = None):
    """Invalida cache por prefixo de tool. None = tudo."""
    global _cache
    if tool_prefix is None:
        _cache.clear()
    else:
        _cache = {k: v for k, v in _cache.items() if not k.startswith(tool_prefix)}


def on_project_file_changed():
    """Limpa cache de analise quando arquivos mudam."""
    for prefix in ["analyze_game_structure", "inspect_project", "get_project_settings", "project_map"]:
        invalidate_cache(prefix)


def cache_stats() -> dict:
    """Retorna estatisticas do cache."""
    total = _cache_hits + _cache_misses
    return {"entries": len(_cache), "hits": _cache_hits, "misses": _cache_misses,
            "hit_rate": f"{round(_cache_hits/total*100,1)}%" if total > 0 else "0%"}
