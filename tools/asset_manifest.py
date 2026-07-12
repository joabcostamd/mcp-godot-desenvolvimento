"""asset_manifest.py — Import automatizado via asset_manifest.json (PATCH 16).

Le um arquivo asset_manifest.json na raiz do projeto e importa/gera
todos os assets listados, usando os geradores existentes (AI, placeholder,
procedural, download CC0, import local).

Formato do manifest:
    {
      "version": "1.0",
      "assets": [
        {"id": "...", "source": "generate|placeholder|sfx|import|download", ...}
      ]
    }

Tools:
    import_asset_manifest — processa asset_manifest.json
    create_asset_manifest — gera template de manifest vazio
"""

import json
from pathlib import Path
from typing import Any

from tools.project_ops import _get_active_project


# ══════════════════════════════════════════════════════════════════════
# import_asset_manifest
# ══════════════════════════════════════════════════════════════════════

def import_asset_manifest(
    manifest_path: str | None = None,
    project_path: str | None = None,
    dry_run: bool = False,
) -> dict:
    """Importa todos os assets listados no asset_manifest.json.

    Suporta 5 fontes (source):
    - "generate":    arte IA (DALL-E/FLUX) via generate_game_art()
    - "placeholder": sprite/textura procedural via placeholder_ops
    - "sfx":         audio procedural (laser, explosao, etc.)
    - "import":      copia arquivo local para o projeto
    - "download":    download CC0 (Poly Haven, Kenney, AmbientCG)

    Args:
        manifest_path: Caminho para o manifest (default: <projeto>/asset_manifest.json).
        project_path: Caminho do projeto (opcional, usa projeto ativo).
        dry_run: Se True, valida o manifest mas nao importa nada.

    Returns:
        {"status": "success", "results": [...], "summary": {...}}
    """
    proj = _resolve_project(project_path)
    if not proj:
        return {"status": "error", "message": "Projeto nao encontrado."}

    # Localiza o manifest
    if manifest_path:
        mf_path = Path(manifest_path)
    else:
        mf_path = proj / "asset_manifest.json"

    if not mf_path.exists():
        return {
            "status": "error",
            "message": f"asset_manifest.json nao encontrado em '{mf_path}'. "
                       f"Use create_asset_manifest para gerar um template.",
        }

    try:
        manifest = json.loads(mf_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return {"status": "error", "message": f"JSON invalido: {e}"}

    assets = manifest.get("assets", [])
    if not assets:
        return {"status": "success", "message": "Manifest vazio — nenhum asset para importar.", "results": []}

    results: list[dict] = []
    ok_count = 0
    fail_count = 0
    skip_count = 0

    for i, asset in enumerate(assets):
        asset_id = asset.get("id", f"asset_{i}")
        source = asset.get("source", "placeholder")

        if dry_run:
            results.append({
                "id": asset_id,
                "source": source,
                "status": "dry_run",
                "message": f"[DRY RUN] Seria processado como '{source}'.",
            })
            skip_count += 1
            continue

        try:
            if source == "generate":
                result = _process_generate(asset, proj)
            elif source == "placeholder":
                result = _process_placeholder(asset, proj)
            elif source == "sfx":
                result = _process_sfx(asset, proj)
            elif source == "import":
                result = _process_import(asset, proj)
            elif source == "download":
                result = _process_download(asset, proj)
            else:
                result = {"status": "error", "message": f"Source '{source}' desconhecido."}

            result["id"] = asset_id
            result["source"] = source
            results.append(result)

            if result.get("status") == "success":
                ok_count += 1
            else:
                fail_count += 1

        except Exception as e:
            results.append({
                "id": asset_id,
                "source": source,
                "status": "error",
                "message": f"Excecao: {e}",
            })
            fail_count += 1

    return {
        "status": "success" if fail_count == 0 else "partial_success",
        "manifest": str(mf_path),
        "dry_run": dry_run,
        "results": results,
        "summary": {
            "total": len(assets),
            "ok": ok_count,
            "failed": fail_count,
            "skipped": skip_count,
        },
    }


# ══════════════════════════════════════════════════════════════════════
# Processadores por source
# ══════════════════════════════════════════════════════════════════════

def _process_generate(asset: dict, proj: Path) -> dict:
    """Gera arte via IA (DALL-E/FLUX) usando generate_game_art()."""
    try:
        from tools.art_ops import generate_game_art
    except ImportError:
        return {"status": "error", "message": "Modulo art_ops nao disponivel."}

    result = generate_game_art(
        description=asset.get("description", asset.get("id", "asset")),
        category=asset.get("category", "personagem"),
        style=asset.get("style", "scifi"),
        anim_type=asset.get("anim_type", "idle"),
        frames=asset.get("frames", 1),
        grid_cols=asset.get("grid_cols", 1),
        grid_rows=asset.get("grid_rows", 1),
        width=asset.get("width", 128),
        height=asset.get("height", 128),
        save_dir=asset.get("save_dir", "assets/generated/"),
    )

    # Se tem cena alvo, aplica a arte
    if result.get("status") == "success" and asset.get("target_scene"):
        try:
            from tools.art_ops import apply_game_art
            frame_paths = result.get("frame_paths", [result.get("output_path")])
            apply_game_art(
                frame_paths=frame_paths,
                scene_path=asset["target_scene"],
                node_path=asset.get("target_node", "."),
                anim_name=asset.get("animation_name", "default"),
                fps=asset.get("fps", 10.0),
                loop=asset.get("loop", True),
            )
            result["applied_to"] = f"{asset['target_scene']}::{asset.get('target_node', '.')}"
        except Exception as e:
            result["apply_error"] = str(e)

    return result


def _process_placeholder(asset: dict, proj: Path) -> dict:
    """Gera sprite/textura procedural via placeholder_ops."""
    category = asset.get("category", "sprite")

    if category == "tileset":
        try:
            from tools.placeholder_ops import generate_tileset_from_colors
            return generate_tileset_from_colors(
                palette_name=asset.get("palette_name", "custom"),
                colors=asset.get("colors", ["#3498db", "#2ecc71", "#e74c3c", "#f1c40f"]),
                tile_width=asset.get("tile_width", 16),
                tile_height=asset.get("tile_height", 16),
                save_texture_path=asset.get("save_texture_path", "assets/tiles/custom.png"),
                save_tileset_path=asset.get("save_tileset_path", "assets/tiles/custom.tres"),
            )
        except ImportError:
            return {"status": "error", "message": "Modulo placeholder_ops nao disponivel."}

    if category == "background":
        try:
            from tools.placeholder_ops import generate_background_gradient
            return generate_background_gradient(
                name=asset.get("id", "bg"),
                width=asset.get("width", 1280),
                height=asset.get("height", 720),
                color_top=asset.get("color_top", "#1a1a2e"),
                color_bottom=asset.get("color_bottom", "#16213e"),
                direction=asset.get("direction", "vertical"),
                save_path=asset.get("save_path"),
            )
        except ImportError:
            return {"status": "error", "message": "Modulo placeholder_ops nao disponivel."}

    # Sprite padrao
    try:
        from tools.placeholder_ops import generate_placeholder_sprite
        return generate_placeholder_sprite(
            name=asset.get("id", "sprite"),
            width=asset.get("width", 64),
            height=asset.get("height", 64),
            color=asset.get("color", "#3498db"),
            shape=asset.get("shape", "rectangle"),
            save_path=asset.get("save_path"),
        )
    except ImportError:
        return {"status": "error", "message": "Modulo placeholder_ops nao disponivel."}


def _process_sfx(asset: dict, proj: Path) -> dict:
    """Gera audio procedural via generate_audio_sfx()."""
    try:
        from tools.placeholder_ops import generate_audio_sfx
        return generate_audio_sfx(
            name=asset.get("id", "sfx"),
            sfx_type=asset.get("sfx_type", "beep"),
            duration=asset.get("duration", 0.3),
            frequency=asset.get("frequency", 440),
            sample_rate=asset.get("sample_rate", 44100),
            style=asset.get("style", "scifi"),
            save_path=asset.get("save_path"),
        )
    except ImportError:
        return {"status": "error", "message": "Modulo placeholder_ops nao disponivel."}


def _process_import(asset: dict, proj: Path) -> dict:
    """Importa arquivo local para o projeto."""
    source_path = asset.get("source_path", "")
    target_path = asset.get("target_res_path", "")

    if not source_path or not target_path:
        return {"status": "error", "message": "source_path e target_res_path sao obrigatorios para import."}

    src = Path(source_path)
    if not src.exists():
        return {"status": "error", "message": f"Arquivo fonte nao encontrado: {source_path}"}

    ext = src.suffix.lower()

    if ext in (".png", ".jpg", ".jpeg", ".bmp", ".svg"):
        try:
            from tools.asset_ops import import_texture
            return import_texture(source_path=str(src), target_res_path=target_path)
        except ImportError:
            pass

    if ext in (".wav", ".ogg", ".mp3"):
        try:
            from tools.asset_ops import import_audio
            return import_audio(source_path=str(src), target_res_path=target_path)
        except ImportError:
            pass

    # Fallback: copia simples
    dest = proj / target_path
    dest.parent.mkdir(parents=True, exist_ok=True)
    import shutil
    shutil.copy2(src, dest)
    return {"status": "success", "res_path": target_path, "method": "copy"}


def _process_download(asset: dict, proj: Path) -> dict:
    """Download de asset CC0 (Poly Haven, Kenney, AmbientCG)."""
    try:
        from tools.asset_download import download_asset, import_downloaded_asset
    except ImportError:
        return {"status": "error", "message": "Modulo asset_download nao disponivel."}

    dl_source = asset.get("download_source", "polyhaven")
    query = asset.get("query", asset.get("id", ""))
    category = asset.get("category", "all")
    asset_id = asset.get("asset_id")
    resolution = asset.get("resolution", "2k")

    # Download
    dl_result = download_asset(
        source=dl_source,
        query=query,
        category=category if category != "all" else "all",
        asset_id=asset_id,
        resolution=resolution,
        limit=1,
    )

    if dl_result.get("status") != "success":
        return {"status": "error", "message": f"Download falhou: {dl_result.get('message', 'erro desconhecido')}"}

    # Importa
    downloaded_path = dl_result.get("downloaded_path") or dl_result.get("path")
    if not downloaded_path:
        return {"status": "error", "message": "Download concluido mas sem path de saida."}

    target_dir = asset.get("target_dir", "assets/downloaded/")
    return import_downloaded_asset(asset_path=downloaded_path, target_dir=target_dir)


# ══════════════════════════════════════════════════════════════════════
# create_asset_manifest
# ══════════════════════════════════════════════════════════════════════

def create_asset_manifest(
    project_path: str | None = None,
    overwrite: bool = False,
) -> dict:
    """Gera um template de asset_manifest.json no projeto.

    Args:
        project_path: Caminho do projeto (opcional).
        overwrite: Se True, sobrescreve manifest existente.

    Returns:
        {"status": "success", "path": str, "created": bool}
    """
    proj = _resolve_project(project_path)
    if not proj:
        return {"status": "error", "message": "Projeto nao encontrado."}

    mf_path = proj / "asset_manifest.json"

    if mf_path.exists() and not overwrite:
        return {
            "status": "error",
            "message": f"asset_manifest.json ja existe em '{mf_path}'. Use overwrite=True para sobrescrever.",
        }

    template = {
        "version": "1.0",
        "project": proj.name,
        "_instructions": (
            "Preencha os assets abaixo. Cada asset tem um 'source':\n"
            "  - generate:    arte IA (DALL-E/FLUX) — requer description, style\n"
            "  - placeholder: sprite/textura procedural — requer width, height, color\n"
            "  - sfx:         audio procedural — requer sfx_type (laser, explosion, ...)\n"
            "  - import:      copia arquivo local — requer source_path, target_res_path\n"
            "  - download:    download CC0 — requer download_source (polyhaven/kenney/ambientcg), query\n"
            "\n"
            "Remova os assets de exemplo e adicione os seus."
        ),
        "assets": [
            {
                "id": "exemplo_sprite",
                "source": "placeholder",
                "category": "sprite",
                "description": "Sprite de exemplo (retangulo azul)",
                "width": 64,
                "height": 64,
                "color": "#3498db",
                "shape": "rectangle",
                "save_path": "assets/sprites/exemplo.png",
            },
            {
                "id": "exemplo_sfx",
                "source": "sfx",
                "sfx_type": "laser",
                "duration": 0.4,
                "style": "scifi",
                "save_path": "assets/audio/sfx/laser.wav",
            },
        ],
    }

    mf_path.write_text(json.dumps(template, indent=2, ensure_ascii=False), encoding="utf-8")

    return {
        "status": "success",
        "path": str(mf_path),
        "created": True,
        "message": f"Template criado em '{mf_path}'. Edite o arquivo e rode import_asset_manifest.",
    }


# ══════════════════════════════════════════════════════════════════════
# Helpers
# ══════════════════════════════════════════════════════════════════════

def _resolve_project(project_path: str | None) -> Path | None:
    """Resolve o caminho do projeto."""
    if project_path:
        proj = Path(project_path)
        if proj.exists():
            return proj
    try:
        return _get_active_project()
    except Exception:
        return None
