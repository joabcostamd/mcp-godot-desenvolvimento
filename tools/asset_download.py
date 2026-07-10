"""asset_download.py — Asset Download Automático (Fase 2C / M7).

Baixa assets CC0 de APIs públicas e importa no projeto Godot.
Inspirado no Gear (wvfp) — Poly Haven, AmbientCG, Kenney.

Fontes suportadas:
    - Poly Haven: texturas PBR, HDRIs, modelos 3D (api.polyhaven.com)
    - Kenney: sprites, tilesets, UI, áudio (kenney.nl/assets)
    - AmbientCG: materiais PBR (ambientcg.com)

Uso:
    download_asset(source="polyhaven", query="metal", category="textures")
    download_asset(source="kenney", query="tower defense")
"""

import json
import os
import shutil
import tempfile
import time
import urllib.request
import urllib.parse
import zipfile
from pathlib import Path

# ── Constantes ──────────────────────────────────────────────────────

POLYHAVEN_API = "https://api.polyhaven.com"
AMBIENTCG_API = "https://ambientcg.com/api/v2"
KENNEY_BASE = "https://kenney.nl/assets"

ASSET_DIR = Path.home() / "AppData" / "Local" / "Temp" / "gdm_assets"
CACHE_FILE = ASSET_DIR / "download_cache.json"

# Domínios permitidos para download
ALLOWED_DOMAINS = ['polyhaven.com', 'api.polyhaven.com', 'cdn.polyhaven.com',
                   'kenney.nl', 'cdn.kenney.nl', 'ambientcg.com', 'cdn.ambientcg.com',
                   'dl.ambientcg.com']


def _validate_domain(url: str) -> bool:
    """Verifica se o domínio da URL está na lista de permitidos."""
    from urllib.parse import urlparse
    parsed = urlparse(url)
    hostname = parsed.hostname or ''
    return any(hostname == d or hostname.endswith('.' + d) for d in ALLOWED_DOMAINS)


# ── Helpers HTTP ────────────────────────────────────────────────────

def _http_get(url: str, timeout: float = 15.0) -> dict | bytes:
    """GET request com User-Agent e timeout."""
    if not _validate_domain(url):
        raise ValueError(f"Domínio não permitido para download: {url}")
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "godot-mcp-agent/3.0 (DeepSeek V4; +https://github.com/joabcostamd)"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        content_type = resp.headers.get("Content-Type", "")
        data = resp.read()
        if "json" in content_type:
            return json.loads(data)
        return data


def _download_file(url: str, dest: str, timeout: float = 60.0) -> bool:
    """Baixa arquivo para disco."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "godot-mcp-agent/3.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            with open(dest, "wb") as f:
                f.write(resp.read())
        return True
    except Exception:
        return False


def _cache_get(key: str) -> str | None:
    """Recupera path do cache."""
    ASSET_DIR.mkdir(parents=True, exist_ok=True)
    if CACHE_FILE.exists():
        with open(CACHE_FILE, encoding="utf-8") as f:
            cache = json.load(f)
        return cache.get(key)
    return None


def _cache_set(key: str, value: str) -> None:
    """Salva no cache."""
    cache = {}
    if CACHE_FILE.exists():
        with open(CACHE_FILE, encoding="utf-8") as f:
            cache = json.load(f)
    cache[key] = value
    ASSET_DIR.mkdir(parents=True, exist_ok=True)
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2)


# ── Poly Haven ──────────────────────────────────────────────────────

def _polyhaven_search(query: str, category: str = "all", limit: int = 10) -> dict:
    """Busca assets no Poly Haven.

    Args:
        query: Termo de busca.
        category: "textures", "hdris", "models", "all".
        limit: Máximo de resultados.
    """
    try:
        params = {}
        if category != "all":
            params["type"] = category

        url = f"{POLYHAVEN_API}/v1/assets?{urllib.parse.urlencode(params)}"
        data = _http_get(url)

        # Filtro local por query
        results = []
        query_lower = query.lower()
        for asset_id, asset in data.items():
            name = asset.get("name", asset_id).lower()
            if query_lower in name or query_lower in asset_id.lower():
                results.append({
                    "id": asset_id,
                    "name": asset.get("name", asset_id),
                    "type": asset.get("type", ""),
                    "categories": asset.get("categories", []),
                    "thumbnail": asset.get("thumbnails", {}).get("small", ""),
                    "download_count": asset.get("download_count", 0),
                })
                if len(results) >= limit:
                    break

        return {
            "status": "success",
            "source": "polyhaven",
            "results": results,
            "total": len(results),
        }
    except Exception as e:
        return {"status": "error", "source": "polyhaven", "message": str(e)}


def _polyhaven_download(asset_id: str, resolution: str = "2k", file_type: str = "zip") -> dict:
    """Baixa um asset do Poly Haven."""
    try:
        # Verifica cache
        cache_key = f"polyhaven/{asset_id}/{resolution}"
        cached = _cache_get(cache_key)
        if cached and os.path.exists(cached):
            return {"status": "success", "path": cached, "cached": True}

        # Obtém info do asset para pegar os files
        info_url = f"{POLYHAVEN_API}/v1/files/{asset_id}"
        files_data = _http_get(info_url)

        # Encontra o download adequado
        download_url = None
        for category, res_data in files_data.items():
            if isinstance(res_data, dict) and resolution in res_data:
                formats = res_data[resolution]
                if isinstance(formats, dict):
                    if file_type in formats:
                        download_url = formats[file_type].get("url", "")
                    elif "zip" in formats:
                        download_url = formats["zip"].get("url", "")
                    break

        if not download_url:
            return {"status": "error", "message": f"Resolução {resolution} não disponível"}

        # Baixa
        dest_dir = ASSET_DIR / "polyhaven" / asset_id
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest_file = dest_dir / f"{asset_id}_{resolution}.zip"

        if not _download_file(download_url, str(dest_file)):
            return {"status": "error", "message": "Falha no download"}

        # Extrai
        extract_dir = dest_dir / resolution
        extract_dir.mkdir(exist_ok=True)
        with zipfile.ZipFile(dest_file, "r") as zf:
            zf.extractall(extract_dir)

        _cache_set(cache_key, str(extract_dir))
        return {"status": "success", "path": str(extract_dir), "cached": False}
    except Exception as e:
        return {"status": "error", "message": str(e)}


# ── Kenney ──────────────────────────────────────────────────────────

_KENNEY_CATALOG = {
    "tower defense": "https://kenney.nl/assets/tower-defense-top-down",
    "pixel platformer": "https://kenney.nl/assets/pixel-platformer",
    "roguelike": "https://kenney.nl/assets/roguelike-rpg-pack",
    "sci-fi": "https://kenney.nl/assets/sci-fi-sounds",
    "ui": "https://kenney.nl/assets/ui-pack",
    "particles": "https://kenney.nl/assets/particle-pack",
    "tanks": "https://kenney.nl/assets/tanks-top-down",
    "space shooter": "https://kenney.nl/assets/space-shooter-redux",
    "casino": "https://kenney.nl/assets/board-game-pack",
    "fantasy": "https://kenney.nl/assets/fantasy-town",
    "farm": "https://kenney.nl/assets/farming-crops",
    "sports": "https://kenney.nl/assets/sports-pack",
}

def _kenney_search(query: str, limit: int = 10) -> dict:
    """Busca assets no catálogo Kenney."""
    query_lower = query.lower()
    results = []
    for name, url in _KENNEY_CATALOG.items():
        if query_lower in name:
            results.append({"name": name, "url": url, "author": "Kenney.nl", "license": "CC0"})
            if len(results) >= limit:
                break

    return {
        "status": "success",
        "source": "kenney",
        "results": results,
        "total": len(results),
        "note": "Kenney assets precisam ser baixados manualmente do site. A URL está disponível.",
    }


# ── AmbientCG ───────────────────────────────────────────────────────

def _ambientcg_search(query: str, limit: int = 10) -> dict:
    """Busca materiais PBR no AmbientCG."""
    try:
        url = f"{AMBIENTCG_API}/full_json?type=Material&sort=Popular&include=displayData"
        data = _http_get(url)

        results = []
        query_lower = query.lower()
        for item in data.get("foundAssets", data if isinstance(data, list) else []):
            if isinstance(item, dict):
                name = item.get("displayName", item.get("name", "")).lower()
                asset_id = item.get("assetId", item.get("id", ""))
            else:
                name = str(item).lower()
                asset_id = item

            if query_lower in name:
                results.append({
                    "id": str(asset_id),
                    "name": name.title(),
                    "url": f"https://ambientcg.com/view?id={asset_id}",
                })
                if len(results) >= limit:
                    break

        return {
            "status": "success",
            "source": "ambientcg",
            "results": results,
            "total": len(results),
            "note": "AmbientCG requer download manual do site. Formatos: JPG, PNG, ZIP (PBR). Licença: CC0.",
        }
    except Exception as e:
        return {"status": "error", "source": "ambientcg", "message": str(e)}


# ── API Principal ───────────────────────────────────────────────────

def download_asset(
    source: str = "polyhaven",
    query: str = "",
    category: str = "all",
    asset_id: str | None = None,
    resolution: str = "2k",
    limit: int = 10,
) -> dict:
    """Busca e baixa assets CC0 de fontes públicas.

    Args:
        source: "polyhaven", "kenney", "ambientcg".
        query: Termo de busca (ex: "metal", "wood", "tower defense").
        category: Categoria (para Poly Haven: textures, hdris, models, all).
        asset_id: ID específico para download direto (Poly Haven).
        resolution: Resolução (para Poly Haven: 1k, 2k, 4k, 8k).
        limit: Máximo de resultados na busca.

    Returns:
        dict com resultados da busca ou download.
    """
    if source == "polyhaven":
        if asset_id:
            return _polyhaven_download(asset_id, resolution)
        return _polyhaven_search(query, category, limit)

    elif source == "kenney":
        return _kenney_search(query, limit)

    elif source == "ambientcg":
        return _ambientcg_search(query, limit)

    else:
        return {
            "status": "error",
            "message": f"Fonte desconhecida: {source}. Use: polyhaven, kenney, ambientcg.",
        }


def import_downloaded_asset(asset_path: str, target_dir: str = "assets") -> dict:
    """Importa asset baixado para o projeto Godot.

    Args:
        asset_path: Caminho local do asset (pasta ou arquivo).
        target_dir: Diretório de destino no projeto (ex: "assets/textures").

    Returns:
        dict com status e arquivos importados.
    """
    try:
        # Detecta projeto ativo
        from tools.project_ops import get_project_settings
        settings = get_project_settings()
        project_path = settings.get("project_path", "")

        if not project_path:
            return {"status": "error", "message": "Nenhum projeto ativo. Use project_manage set_active."}

        dest = Path(project_path) / target_dir
        dest.mkdir(parents=True, exist_ok=True)

        imported = []
        src = Path(asset_path)
        if src.is_dir():
            for f in src.rglob("*"):
                if f.is_file():
                    rel = f.relative_to(src)
                    target = dest / rel
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(f, target)
                    imported.append(str(target.relative_to(project_path)))
        else:
            target = dest / src.name
            shutil.copy2(src, target)
            imported.append(str(target.relative_to(project_path)))

        return {
            "status": "success",
            "imported": imported,
            "count": len(imported),
            "target_dir": str(dest),
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
