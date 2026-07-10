"""flux_ops.py — Geracao de arte para jogos via FLUX.2 API (Black Forest Labs).

Substitui o Playwright/DALL-E fragil por API REST estavel.
Tambem suporta Replicate como fallback.

Requer: pip install requests
"""

import base64
import hashlib
import json
import os
import time
from io import BytesIO
from pathlib import Path
from typing import Any

# requests importado lazy dentro de _generate_flux_bfl() (P1-3)

ROOT = Path(__file__).resolve().parent.parent

# Cache
FLUX_CACHE_DIR = ROOT / "art_cache" / "flux"
FLUX_CACHE_DIR.mkdir(parents=True, exist_ok=True)
FLUX_CACHE_MAX_SIZE_MB = 500
FLUX_CACHE_MAX_AGE_DAYS = 30

# Config via env vars (seguro, sem hardcode de API key)
BFL_API_KEY = os.environ.get("BFL_API_KEY", "")
REPLICATE_API_KEY = os.environ.get("REPLICATE_API_KEY", "")


# ══════════════════════════════════════════════════════════════
# CONFIGURACAO DE TAMANHOS POR CATEGORIA
# ══════════════════════════════════════════════════════════════

DEFAULT_SIZES = {
    "torre": (128, 128),
    "inimigo": (96, 96),
    "personagem": (128, 128),
    "icone": (64, 64),
    "hud": (256, 64),
    "tile": (64, 64),
    "bioma": (512, 512),
    "fundo": (1280, 720),
    "vfx": (128, 128),
    "ui": (256, 128),
    "projetil": (32, 32),
}


# ══════════════════════════════════════════════════════════════
# CACHE
# ══════════════════════════════════════════════════════════════

def _cache_key(category: str, description: str, style: str,
               frames: int, width: int, height: int) -> str:
    raw = f"{category}|{description}|{style}|{frames}|{width}|{height}"
    return hashlib.md5(raw.encode()).hexdigest()


def _check_cache(cache_key: str) -> Path | None:
    cached = FLUX_CACHE_DIR / f"{cache_key}.png"
    return cached if cached.exists() else None


def _save_cache(cache_key: str, image_bytes: bytes):
    (FLUX_CACHE_DIR / f"{cache_key}.png").write_bytes(image_bytes)


def _evict_cache_if_needed():
    """Remove cached files if cache exceeds size or age limits (P1-5)."""
    import time as _time
    files = sorted(FLUX_CACHE_DIR.glob("*.png"), key=lambda f: f.stat().st_mtime)
    total_size = sum(f.stat().st_size for f in files)
    cutoff = _time.time() - FLUX_CACHE_MAX_AGE_DAYS * 86400
    for f in files:
        if total_size < FLUX_CACHE_MAX_SIZE_MB * 1024 * 1024 and f.stat().st_mtime > cutoff:
            break
        total_size -= f.stat().st_size
        try:
            f.unlink()
        except OSError:
            pass


# ══════════════════════════════════════════════════════════════
# GERADOR PRINCIPAL: FLUX.2 Pro (Black Forest Labs)
# ══════════════════════════════════════════════════════════════

def _generate_flux_bfl(
    prompt: str,
    width: int = 1024,
    height: int = 1024,
    model: str = "flux-2-pro-preview",
) -> dict:
    """Gera imagem via API direta do Black Forest Labs.

    Documentacao: https://docs.bfl.ml/
    Preco: ~$0.03 por imagem 1024x1024 (flux-2-pro)
           ~$0.015 por imagem (flux-2-klein-9b)
    """
    if not BFL_API_KEY:
        return {"status": "error", "message": "BFL_API_KEY nao configurada. Defina a variavel de ambiente."}

    import requests  # P1-3: lazy import

    # 1. Submeter job
    resp = requests.post(
        f"https://api.bfl.ai/v1/{model}",
        headers={
            "accept": "application/json",
            "x-key": BFL_API_KEY,
            "Content-Type": "application/json",
        },
        json={
            "prompt": prompt,
            "width": width,
            "height": height,
        },
        timeout=30,
    )

    if resp.status_code != 200:
        return {"status": "error", "message": f"BFL API error {resp.status_code}: {resp.text}"}

    data = resp.json()

    if "polling_url" not in data:
        return {"status": "error", "message": f"BFL resposta inesperada: {data}"}

    # 2. Polling ate completar
    polling_url = data["polling_url"]
    max_wait = 120  # segundos
    start = time.time()

    while True:
        if time.time() - start > max_wait:
            return {"status": "error", "message": "Timeout: geracao excedeu 120s"}

        time.sleep(1.0)
        poll = requests.get(
            polling_url,
            headers={"accept": "application/json", "x-key": BFL_API_KEY},
            timeout=10,
        )

        if poll.status_code != 200:
            continue

        result = poll.json()

        if result.get("status") == "Ready":
            image_url = result["result"]["sample"]
            # 3. Baixar imagem
            img_resp = requests.get(image_url, timeout=30)
            img_resp.raise_for_status()
            return {
                "status": "success",
                "image_bytes": img_resp.content,
                "width": width,
                "height": height,
                "generator": f"FLUX.2 ({model})",
            }

        elif result.get("status") in ("Error", "Failed", "Task not found", "Cancelled"):
            return {"status": "error", "message": f"Geracao falhou: {result}"}
        elif result.get("status") not in ("Pending", "Ready", "Processing", "In Progress"):
            return {"status": "error", "message": f"Status desconhecido: {result.get('status')}"}

    return {"status": "error", "message": "Polling esgotado sem resultado"}


# ══════════════════════════════════════════════════════════════
# FALLBACK: Replicate (FLUX, Stable Diffusion, Recraft)
# ══════════════════════════════════════════════════════════════

def _generate_replicate(
    prompt: str,
    model: str = "black-forest-labs/flux-schnell",
    width: int = 1024,
    height: int = 1024,
) -> dict:
    """Fallback via Replicate API quando BFL nao disponivel."""
    if not REPLICATE_API_KEY:
        return {"status": "error", "message": "REPLICATE_API_KEY nao configurada"}

    try:
        import replicate
    except ImportError:
        return {"status": "error", "message": "Instale replicate: pip install replicate"}

    try:
        output = replicate.run(
            model,
            input={
                "prompt": prompt,
                "width": width,
                "height": height,
                "num_outputs": 1,
            },
        )
        # output é um iterator ou lista de URLs/file objects
        if isinstance(output, list) and output:
            url_or_file = output[0]
            if isinstance(url_or_file, str):
                img_resp = requests.get(url_or_file, timeout=30)
                return {"status": "success", "image_bytes": img_resp.content,
                        "width": width, "height": height, "generator": f"Replicate ({model})"}
        return {"status": "error", "message": f"Replicate output inesperado: {type(output)}"}
    except Exception as e:
        import sys as _sys
        print(f"[MCP] Replicate fallback falhou: {e}", file=_sys.stderr)
        return {"status": "error", "message": f"Replicate error: {e}"}


# ══════════════════════════════════════════════════════════════
# TOOL PRINCIPAL: generate_game_art_flux
# ══════════════════════════════════════════════════════════════

def generate_game_art_flux(
    description: str,
    category: str = "torre",
    style: str = "scifi",
    frames: int = 1,
    width: int | None = None,
    height: int | None = None,
    save_path: str | None = None,
) -> dict:
    """Gera arte de jogo via FLUX.2 API com cache automatico.

    Args:
        description: Descricao em portugues do que gerar.
            Ex: "torre de defesa railgun estilo sci-fi com canhao azul brilhante"
        category: Tipo de artefato (torre, inimigo, personagem, bioma, tile,
            icone, hud, vfx, fundo, projetil, ui)
        style: Estilo visual (scifi, fantasia, cartoon, realista, pixel, minimalista)
        frames: Numero de frames para sprite sheet (1 = imagem unica)
        width: Largura em pixels (auto por categoria se None)
        height: Altura em pixels (auto por categoria se None)
        save_path: Caminho relativo no projeto Godot (auto se None)

    Returns:
        {"status": "success", "saved_to": str, "image_base64": str,
         "cache": "hit"|"miss", "generator": str, "size": [w, h]}
    """
    from tools.project_ops import _get_active_project, _check_path_traversal

    proj = _get_active_project()

    # Resolver tamanho
    default = DEFAULT_SIZES.get(category, (128, 128))
    w = width or default[0]
    h = height or default[1]

    # Resolver path
    if not save_path:
        save_path = f"assets/art/{category}/{description[:30].replace(' ', '_')}.png"

    violation = _check_path_traversal(save_path, proj)
    if violation:
        return {"status": "error", "message": violation}

    # Evict old cache entries periodically (P1-5)
    _evict_cache_if_needed()

    # Verificar cache
    ck = _cache_key(category, description, style, frames, w, h)
    cached = _check_cache(ck)
    if cached:
        return {
            "status": "success",
            "saved_to": save_path,
            "image_base64": base64.b64encode(cached.read_bytes()).decode("ascii"),
            "cache": "hit",
            "generator": "cache",
            "size": [w, h],
            "message": "Arte recuperada do cache (geracao anterior)",
        }

    # Montar prompt otimizado para FLUX
    style_keywords = {
        "scifi": "sci-fi, futuristic, neon lights, metallic, technology",
        "fantasia": "fantasy, medieval, magic, mystical, hand-painted",
        "cartoon": "cartoon, colorful, cel-shaded, vibrant, stylized",
        "realista": "photorealistic, detailed, 8k, high quality",
        "pixel": "pixel art, 32-bit, retro game, sharp pixels, no anti-aliasing",
        "minimalista": "minimalist, flat design, clean lines, simple shapes",
    }
    style_suffix = style_keywords.get(style, style)

    if frames > 1:
        prompt = (
            f"Game sprite sheet, {frames} animation frames arranged in a horizontal row, "
            f"{category} sprite, {style_suffix}, "
            f"each frame exactly {w}x{h} pixels, transparent or solid dark background, "
            f"consistent character design across all frames, game asset. "
            f"Description: {description}"
        )
    else:
        prompt = (
            f"Game asset: {category}, {style_suffix}, "
            f"{w}x{h} pixels, transparent or solid dark background, "
            f"game ready. Description: {description}"
        )

    # Tentar FLUX.2 API primeiro
    result = _generate_flux_bfl(prompt, width=w, height=h)

    # Fallback: Replicate
    if result["status"] != "success":
        result = _generate_replicate(prompt, model="black-forest-labs/flux-schnell",
                                     width=w, height=h)

    # Fallback final: Pillow procedural (do art_ops existente)
    if result["status"] != "success":
        try:
            from tools.placeholder_ops import generate_placeholder_sprite
            ph = generate_placeholder_sprite(
                name=description[:20].replace(" ", "_"),
                width=w, height=h,
                shape="rectangle",
                save_path=save_path,
            )
            return {
                **ph,
                "cache": "miss",
                "generator": "pillow-fallback",
                "message": f"FLUX e Replicate falharam. Usando placeholder procedural. Erro: {result.get('message')}",
            }
        except Exception:
            return result  # sem saida, retorna o erro

    # Salvar
    img_bytes = result["image_bytes"]
    _save_cache(ck, img_bytes)

    full_path = proj / save_path
    full_path.parent.mkdir(parents=True, exist_ok=True)
    full_path.write_bytes(img_bytes)

    return {
        "status": "success",
        "saved_to": save_path,
        "image_base64": base64.b64encode(img_bytes).decode("ascii"),
        "cache": "miss",
        "generator": result["generator"],
        "size": [w, h],
    }
