"""marketplace_ops.py — Busca e download de assets gratuitos (GRATIS).

Fontes: Kenney.nl (CC0), Godot Asset Library, OpenGameArt, Poly Haven.
Todas gratuitas. Nenhuma API paga necessaria.
"""

import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

_SOURCES = {
    "kenney": {"name": "Kenney.nl", "license": "CC0 (Dominio Publico)",
               "url_template": "https://kenney.nl/data/packs/{slug}.zip",
               "search_url": "https://kenney.nl/assets",
               "categories": ["2D","3D","UI","Audio","Pixel","Textures","VFX","Modular","Retro"],
               "description": "300+ packs CC0. Uso comercial sem restricoes."},
    "godot_assets": {"name": "Godot Asset Library", "license": "MIT/CC0/etc",
                     "search_url": "https://godotengine.org/asset-library/asset",
                     "categories": ["2D Tools","3D Tools","Shaders","Scripts","Plugins","Demos"],
                     "description": "Biblioteca oficial de assets para Godot."},
    "opengameart": {"name": "OpenGameArt.org", "license": "CC0/CC-BY/CC-BY-SA/GPL",
                    "search_url": "https://opengameart.org/art-search-advanced",
                    "categories": ["2D","3D","Textures","Music","Sound Effects","Fonts"],
                    "description": "Milhares de assets gratuitos. Verificar licenca individual."},
    "polyhaven": {"name": "Poly Haven", "license": "CC0",
                  "search_url": "https://polyhaven.com",
                  "categories": ["HDRI","Textures","3D Models"],
                  "description": "Texturas PBR, HDRIs e modelos 3D CC0."},
}

_POPULAR = {
    "kenney": [
        {"name": "Platformer Pack", "slug": "platformer-pack", "category": "2D"},
        {"name": "Tiny Farm", "slug": "tiny-farm", "category": "2D"},
        {"name": "Sci-Fi Sounds", "slug": "sci-fi-sounds", "category": "Audio"},
        {"name": "Modular Cave Kit", "slug": "modular-cave-kit", "category": "Modular"},
        {"name": "Pixel Adventure", "slug": "pixel-adventure", "category": "Pixel"},
        {"name": "UI Pack", "slug": "ui-pack", "category": "UI"},
        {"name": "Tower Defense Kit", "slug": "tower-defense-kit", "category": "2D"},
        {"name": "Space Shooter", "slug": "space-shooter", "category": "2D"},
        {"name": "VFX Pack", "slug": "vfx-pack", "category": "VFX"},
        {"name": "Retro Fonts", "slug": "retro-fonts", "category": "UI"},
    ],
    "godot_assets": [
        {"name": "Dialogic", "description": "Sistema de dialogo", "category": "2D Tools"},
        {"name": "Phantom Camera", "description": "Camera avancada", "category": "2D Tools"},
        {"name": "Shader Vault", "description": "Colecao de shaders", "category": "Shaders"},
    ],
    "polyhaven": [
        {"name": "Rusty Metal", "type": "Texture"},
        {"name": "Rocky Terrain", "type": "Texture"},
        {"name": "Sky HDRI", "type": "HDRI"},
    ],
}


def marketplace_search(query: str = "", source: str = "kenney", category: str = "") -> dict:
    """Busca assets em marketplaces gratuitos (Kenney, Godot Assets, OpenGameArt, Poly Haven).

    Returns:
        {"status": "success", "source": str, "results": [...], "total": int, "license": str}
    """
    info = _SOURCES.get(source, _SOURCES["kenney"])
    assets = _POPULAR.get(source, [])

    if query:
        q = query.lower()
        assets = [a for a in assets if q in a.get("name","").lower() or q in a.get("description","").lower() or q in a.get("category","").lower()]

    if category:
        cat = category.lower()
        assets = [a for a in assets if cat in a.get("category","").lower()]

    return {"status": "success", "source": info["name"], "source_url": info["search_url"],
            "license": info["license"], "results": assets, "total": len(assets),
            "download_hint": f"use marketplace_download(source='{source}', slug='...')"}


def marketplace_download(source: str = "kenney", slug: str = "", save_to: str = "assets/marketplace") -> dict:
    """Baixa asset gratuito do marketplace (Kenney.nl ZIP direto, CC0)."""
    import requests
    from tools.project_ops import _get_active_project, _check_path_traversal
    proj = _get_active_project()

    violation = _check_path_traversal(save_to, proj)
    if violation:
        return {"status": "error", "message": violation}

    if not slug:
        return {"status": "error", "message": "Forneca o slug. Use marketplace_search() para encontrar."}

    if source == "kenney":
        url = f"https://kenney.nl/data/packs/{slug}.zip"
    elif source == "polyhaven":
        return {"status": "info", "message": "Poly Haven requer API. Visite: https://polyhaven.com",
                "search_url": _SOURCES["polyhaven"]["search_url"]}
    else:
        return {"status": "error", "message": f"Download automatico indisponivel para {source}. Visite: {_SOURCES.get(source,{}).get('search_url','')}"}

    target_dir = proj / save_to / slug
    target_dir.mkdir(parents=True, exist_ok=True)

    try:
        resp = requests.get(url, stream=True, timeout=60)
        resp.raise_for_status()
        zip_path = target_dir / f"{slug}.zip"
        with open(zip_path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(target_dir)
        files = [str(f.relative_to(target_dir)) for f in target_dir.rglob("*") if f.is_file() and f.name != f"{slug}.zip"]
        zip_path.unlink()
        return {"status": "success", "saved_to": str(target_dir.relative_to(proj)),
                "files": files[:50], "total_files": len(files), "source": source,
                "license": _SOURCES["kenney"]["license"], "message": f"{len(files)} arquivos de {source} ({slug})"}
    except requests.RequestException as e:
        return {"status": "error", "message": f"Erro ao baixar: {e}"}
    except zipfile.BadZipFile:
        return {"status": "error", "message": f"Arquivo corrompido ou URL invalida: {url}"}
