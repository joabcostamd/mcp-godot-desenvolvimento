"""art_ops.py — Sistema Completo de Geracao de Arte para Jogos (Onda 12).

Gera QUALQUER arte de jogo a partir de linguagem natural e aplica
diretamente no Godot via MCP. Fluxo totalmente automatizado e headless.

Categorias cobertas:
    torre, inimigo, personagem, bioma, tile, icone, hud, vfx, fundo, ui

Geradores:
    - ChatGPT/DALL-E (browser headless via Playwright)
    - Pillow procedural (fallback, sempre disponivel)
    - Recraft V4 SVG (via Replicate API, placeholder)
    - Texel Studio (via API local, placeholder)

Pos-processamento:
    - Deteccao automatica de grid da sprite sheet
    - Recorte de frames
    - Redimensionamento
    - Otimizacao PNG
    - Remocao de fundo (opcional)

Cache:
    - Hash do prompt → reusa arte ja gerada
    - Economia de tokens e tempo

Autor: Nucleo / Star Colony
Versao: 1.0.0
Data: 2026-07-09
"""

import base64
import hashlib
import json
import os
import shutil
import struct
import time
import uuid
import zlib
from io import BytesIO
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent

from tools.project_ops import _get_active_project, _check_path_traversal

# Pillow — sempre disponivel no venv
try:
    from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
    _HAS_PILLOW = True
except ImportError:
    _HAS_PILLOW = False

# Playwright — opcional (ChatGPT browser)
try:
    from playwright.sync_api import sync_playwright
    _HAS_PLAYWRIGHT = True
except ImportError:
    _HAS_PLAYWRIGHT = False


# ══════════════════════════════════════════════════════════════════
# CONFIGURACAO
# ══════════════════════════════════════════════════════════════════

CACHE_DIR = ROOT / "art_cache"
CACHE_DIR.mkdir(exist_ok=True)

TEMP_DIR = ROOT / "temp_art"
TEMP_DIR.mkdir(exist_ok=True)

# Sessao do ChatGPT cacheada (login uma vez, reusa sempre)
CHATGPT_SESSION = ROOT / "chatgpt_session.json"

# Tamanhos padrao por categoria
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

# Frames por tipo de animacao (padrao industria)
DEFAULT_FRAMES = {
    "idle": 4,
    "fire": 6,
    "walk": 6,
    "run": 6,
    "death": 6,
    "attack": 6,
    "spawn": 4,
    "hit": 3,
}

# Grid layout por quantidade de frames
GRID_LAYOUTS = {
    2: (2, 1),
    3: (3, 1),
    4: (2, 2),
    5: (5, 1),
    6: (3, 2),
    7: (7, 1),
    8: (4, 2),
    9: (3, 3),
    10: (5, 2),
    12: (4, 3),
    16: (4, 4),
}


# ══════════════════════════════════════════════════════════════════
# PROMPT TEMPLATES (engenharia de prompt por categoria)
# ══════════════════════════════════════════════════════════════════

PROMPT_TEMPLATES = {
    "torre": """Game asset sprite sheet for a tower defense game: {description}.
Grid layout: {cols} columns × {rows} rows ({total_frames} frames of {anim_type} animation).
Style: {style}, clean professional game art, transparent background,
consistent lighting, isometric or top-down view.
Each frame in a SEPARATE equally-sized grid cell. NO overlap between frames.
The grid cells MUST be clearly separated with visible boundaries.
Size: {width}x{height} pixels per frame.
IMPORTANT: Draw ALL {total_frames} frames arranged in a perfect {cols}x{rows} grid.""",

    "inimigo": """Game asset sprite sheet: {description} enemy character.
{cols}x{rows} grid ({total_frames} frames: {anim_desc}).
Style: {style}, professional game art, transparent background,
side-view or isometric, consistent proportions across all frames.
Each frame in a separate grid cell of equal size.
Size: {width}x{height} pixels per frame.
Draw ALL {total_frames} frames in the {cols}x{rows} grid layout with clear separation.""",

    "personagem": """Game character sprite sheet: {description}.
{cols}x{rows} grid with {total_frames} frames ({anim_desc}).
Style: {style}, clean game art, transparent background,
consistent character design and lighting across all frames.
Each frame size: {width}x{height} pixels.
Grid layout: {cols} columns × {rows} rows. Clear cell separation.""",

    "bioma": """Seamless tileable game texture: {description} biome ground.
Style: {style}, top-down view, rich environmental details,
MUST be perfectly seamless when tiled in all directions,
no visible edges or seams, professional game art quality.
Size: {width}x{height} pixels.""",

    "tile": """Game tileset texture: {description}.
Style: {style}, top-down view, clean game art,
consistent grid-aligned design, suitable for tilemap.
Size: {width}x{height} pixels per tile variant.""",

    "icone": """Game icon: {description}.
Style: {style}, clean vector-like design, transparent background,
recognizable at small sizes, professional game UI quality.
Size: {width}x{height} pixels.""",

    "hud": """Game HUD/UI element: {description}.
Style: {style}, clean interface design, game-ready,
transparent or semi-transparent background, consistent with sci-fi theme.
Size: {width}x{height} pixels.""",

    "fundo": """Game background: {description}.
Style: {style}, atmospheric, suitable for game menu or level background,
no UI elements, rich detail, professional quality.
Size: {width}x{height} pixels.""",

    "vfx": """Game visual effect sprite sheet: {description}.
{cols}x{rows} grid ({total_frames} frames of effect animation).
Style: {style}, on dark/transparent background,
bright contrasting colors for visibility, game-ready VFX.
Size: {width}x{height} pixels per frame.""",

    "projetil": """Game projectile/bullet sprite: {description}.
Style: {style}, small but detailed, transparent background,
visible trail or glow effect, game-ready.
Size: {width}x{height} pixels.""",
}

# Estilos pre-definidos
STYLES = {
    "scifi": "sci-fi digital art, futuristic, glowing neon accents, metallic surfaces, clean lines",
    "fantasia": "fantasy art, medieval, magical glow, stone and wood textures, hand-painted feel",
    "cartoon": "colorful cartoon style, bold outlines, flat shading, playful and vibrant",
    "realista": "photorealistic, detailed textures, natural lighting, high fidelity",
    "pixel": "pixel art, retro 16-bit style, crisp pixels, limited color palette, game boy aesthetic",
    "minimalista": "minimalist flat design, clean geometric shapes, limited colors, modern",
}


# ══════════════════════════════════════════════════════════════════
# CACHE
# ══════════════════════════════════════════════════════════════════

def _cache_key(**kwargs) -> str:
    """Gera chave de cache unica baseada nos parametros."""
    raw = json.dumps(kwargs, sort_keys=True, ensure_ascii=False)
    return hashlib.md5(raw.encode()).hexdigest()[:16]


def _check_cache(key: str) -> str | None:
    """Retorna path do arquivo em cache ou None."""
    cached = CACHE_DIR / f"{key}.png"
    if cached.exists():
        return str(cached)
    return None


def _save_cache(key: str, image_path: str):
    """Salva uma copia no cache."""
    cached = CACHE_DIR / f"{key}.png"
    shutil.copy2(image_path, cached)


# ══════════════════════════════════════════════════════════════════
# GERACAO PRINCIPAL
# ══════════════════════════════════════════════════════════════════

def generate_game_art(
    description: str,
    category: str = "torre",
    style: str = "scifi",
    anim_type: str = "idle",
    frames: int | None = None,
    grid_cols: int | None = None,
    grid_rows: int | None = None,
    width: int | None = None,
    height: int | None = None,
    save_dir: str | None = None,
    ip_force: bool = False,
    ip_reason: str = "",
) -> dict:
    """Gera arte de jogo a partir de descricao em linguagem natural.

    FUNCAO MESTRA do sistema. Analisa o pedido, gera a arte, pos-processa
    e retorna metadados. A aplicacao no Godot e feita por apply_game_art().

    Args:
        description: Descricao em linguagem natural (ex: "torre railgun com
                     trilhos eletromagneticos e glow azul").
        category: Tipo de artefato (torre, inimigo, personagem, bioma, tile,
                  icone, hud, vfx, fundo, projetil, ui).
        style: Estilo visual (scifi, fantasia, cartoon, realista, pixel,
               minimalista).
        anim_type: Tipo de animacao (idle, fire, walk, run, death, attack,
                   spawn, hit).
        frames: Quantidade de frames. Se None, usa DEFAULT_FRAMES[anim_type].
        grid_cols: Colunas do grid. Se None, calcula automatico.
        grid_rows: Linhas do grid. Se None, calcula automatico.
        width: Largura por frame. Se None, usa DEFAULT_SIZES[category].
        height: Altura por frame. Se None, usa DEFAULT_SIZES[category].
        save_dir: Diretorio relativo no projeto. Se None, gera automatico.

    Returns:
        {"status": "success", "frames": [...], "sprite_sheet": str,
         "category": str, "cache_hit": bool}
    """
    # ── Fatia 0.K: Verificar PI de terceiros no prompt de arte ──
    try:
        from tools.ip_guard import check_ip_concern, is_ip_previously_accepted, record_ip_decision
        from tools.project_ops import _get_active_project
        ip_result = check_ip_concern(description)
        if ip_result["flagged"]:
            proj = _get_active_project()
            term = ip_result["match"]
            if ip_force and ip_reason:
                record_ip_decision(str(proj), term, True, ip_reason)
            elif not is_ip_previously_accepted(str(proj), term):
                return {
                    "status": "error",
                    "ip_concern": True,
                    "match": term,
                    "message": ip_result["message"],
                    "alternative": ip_result["alternative"],
                    "hint": (
                        f"Para prosseguir mesmo assim, chame esta tool novamente "
                        f"com ip_force=True e ip_reason='sua justificativa'."
                    ),
                }
    except Exception:
        pass  # fail-open
    proj = _get_active_project()

    # Normalizar
    category = category.lower()
    style = style.lower()
    anim_type = anim_type.lower()

    # ── Fatia 3.6: Style lock injection ──────────────────────
    # Injeta automaticamente o contrato de estilo do project_brief
    style_context = {}
    try:
        from tools.project_brief_ops import get_project_brief
        br = get_project_brief()
        if br.get("configured") and br.get("brief"):
            sl = br["brief"].get("style_lock", {})
            if sl:
                style_context["style_lock"] = sl
                # Se o style nao foi passado explicitamente, usa o do brief
                if not style or style == "scifi":
                    style = sl.get("art_type", style)
                # Injeta paleta no contexto de geracao
                if sl.get("palette"):
                    style_context["palette"] = sl["palette"]
                if sl.get("reference"):
                    style_context["reference"] = sl["reference"]
                if sl.get("detail_level"):
                    style_context["detail_level"] = sl["detail_level"]
                # Fonte por categoria de asset
                if sl.get("asset_sources", {}).get(category):
                    style_context["asset_source"] = sl["asset_sources"][category]
    except Exception:
        pass  # style_lock e opcional — nao quebra se nao existir

    # Calcular parametros
    if frames is None:
        frames = DEFAULT_FRAMES.get(anim_type, 4)
    if grid_cols is None or grid_rows is None:
        cols, rows = _calc_grid(frames) if (grid_cols is None and grid_rows is None) else (
            grid_cols or 1, grid_rows or 1
        )
    else:
        cols, rows = grid_cols, grid_rows
    total_frames = cols * rows

    if width is None or height is None:
        w, h = DEFAULT_SIZES.get(category, (128, 128))
        if width is not None:
            w = width
        if height is not None:
            h = height
    else:
        w, h = width, height
    width, height = w, h

    if save_dir is None:
        save_dir = f"assets/sprites/{category}s/"

    # Estilo expandido
    style_desc = STYLES.get(style, STYLES["scifi"])

    # Descricao da animacao
    anim_desc = _anim_description(category, anim_type, frames)

    # Verificar cache
    cache_kwargs = {
        "description": description, "category": category, "style": style,
        "anim_type": anim_type, "frames": total_frames,
        "width": width, "height": height,
    }
    key = _cache_key(**cache_kwargs)
    cached = _check_cache(key)
    if cached:
        # Cache hit — ainda precisa recortar frames
        base_name = description.lower().replace(" ", "_")[:30]
        frame_paths = _crop_sprite_sheet(cached, cols, rows, proj, save_dir, base_name)
        return {
            "status": "success",
            "cache_hit": True,
            "category": category,
            "frames": frame_paths,
            "sprite_sheet": cached,
            "message": f"Arte recuperada do cache ({frame_paths[0] if frame_paths else 'sem frames'})",
        }

    # Construir prompt
    prompt = _build_prompt(
        description=description, category=category, style_desc=style_desc,
        anim_type=anim_type, anim_desc=anim_desc,
        cols=cols, rows=rows, total_frames=total_frames,
        width=width, height=height,
    )

    # Gerar imagem
    raw_path = TEMP_DIR / f"art_{key}.png"

    # Tentar ChatGPT primeiro
    result = None
    if _HAS_PLAYWRIGHT:
        try:
            result = _generate_via_chatgpt(prompt, str(raw_path))
        except Exception as e:
            result = {"status": "error", "message": f"ChatGPT falhou: {e}"}

    # Fallback: Pillow procedural
    if result is None or result.get("status") != "success":
        result = _generate_via_pillow(
            description=description, category=category, style=style,
            cols=cols, rows=rows, width=width, height=height,
            save_path=str(raw_path),
        )

    if result.get("status") != "success":
        return result

    # Salvar no cache
    _save_cache(key, str(raw_path))

    # Pos-processar: recortar frames
    base_name = description.lower().replace(" ", "_")[:30]
    base_name = "".join(c for c in base_name if c.isalnum() or c == "_")
    frame_paths = _crop_sprite_sheet(str(raw_path), cols, rows, proj, save_dir, base_name)

    # Otimizar cada frame
    for fp in frame_paths:
        _optimize_png(fp)

    return {
        "status": "success",
        "cache_hit": False,
        "category": category,
        "frames": frame_paths,
        "frame_count": len(frame_paths),
        "sprite_sheet": str(raw_path),
        "grid": f"{cols}x{rows}",
        "message": f"Arte gerada: {len(frame_paths)} frames em {save_dir}",
    }


# ══════════════════════════════════════════════════════════════════
# APLICACAO NO GODOT
# ══════════════════════════════════════════════════════════════════

# ── Fatia 3.9: Asset placement inteligente ────────────

CATEGORY_NODE_MAP: dict[str, str] = {
    # Personagens e entidades animadas
    "personagem": "AnimatedSprite2D",
    "character": "AnimatedSprite2D",
    "inimigo": "AnimatedSprite2D",
    "enemy": "AnimatedSprite2D",
    "boss": "AnimatedSprite2D",
    "npc": "AnimatedSprite2D",
    # Torres/estruturas
    "torre": "Sprite2D",
    "tower": "Sprite2D",
    "estrutura": "Sprite2D",
    "structure": "Sprite2D",
    # Ambiente e tiles
    "bioma": "TileMapLayer",
    "biome": "TileMapLayer",
    "tile": "TileMapLayer",
    "ambiente": "TileMapLayer",
    "environment": "TileMapLayer",
    "chao": "TileMapLayer",
    "ground": "TileMapLayer",
    # UI / HUD
    "ui": "TextureRect",
    "hud": "TextureRect",
    "menu": "TextureRect",
    "icon": "TextureRect",
    "icone": "TextureRect",
    "botao": "TextureButton",
    "button": "TextureButton",
    # Projéteis / VFX
    "projetil": "Sprite2D",
    "projectile": "Sprite2D",
    "vfx": "Sprite2D",
    "particula": "GPUParticles2D",
    # Fundo
    "fundo": "TextureRect",
    "background": "TextureRect",
}


def _resolve_asset_node(category: str) -> str:
    """Retorna o tipo de no Godot para uma categoria de asset (Fatia 3.9).

    Args:
        category: Categoria do asset (personagem, torre, ui, etc).

    Returns:
        Nome do tipo de no Godot (ex: 'AnimatedSprite2D', 'Sprite2D').
        Default: 'Sprite2D' para categorias nao mapeadas.
    """
    cat = category.strip().lower().replace(" ", "_").replace("-", "_")
    return CATEGORY_NODE_MAP.get(cat, "Sprite2D")


def apply_game_art(
    frame_paths: list[str],
    scene_path: str,
    node_path: str,
    anim_name: str = "default",
    fps: float = 10.0,
    loop: bool = True,
    category: str = "",
) -> dict:
    """Aplica a arte gerada num AnimatedSprite2D do Godot (Fatia 3.9: placement automatico).

    Importa cada frame, cria/atualiza SpriteFrames e configura a animacao.

    Args:
        frame_paths: Lista de caminhos relativos dos frames no projeto.
        scene_path: Caminho da cena (.tscn).
        node_path: Caminho do no destino.
        anim_name: Nome da animacao.
        fps: Frames por segundo da animacao.
        loop: Se a animacao faz loop.
        category: Categoria do asset (Fatia 3.9). Se informada, _resolve_asset_node()
                  sugere o tipo de no automaticamente (ex: 'personagem' → AnimatedSprite2D).

    Returns:
        {"status": "success", "anim_name": str, "frame_count": int, "suggested_node": str|None}
    """
    from tools.asset_ops import import_texture
    from tools.scene_ops import set_node_property

    proj = _get_active_project()

    # Importar cada frame
    imported = []
    for fp in frame_paths:
        abs_path = proj / fp
        if abs_path.exists():
            imported.append(fp)
        else:
            # Tenta importar do temp
            temp_path = TEMP_DIR / Path(fp).name
            if temp_path.exists():
                r = import_texture(str(temp_path), fp)
                if r.get("status") == "success":
                    imported.append(fp)

    if not imported:
        return {"status": "error", "message": "Nenhum frame importado."}

    # Criar SpriteFrames .tres
    sf_name = Path(imported[0]).stem.rsplit("_f", 1)[0]
    sf_path = str(Path(imported[0]).parent / f"{sf_name}_frames.tres")

    sf_content = _build_sprite_frames_tres(imported, anim_name, fps, loop)
    sf_full = proj / sf_path
    sf_full.write_text(sf_content, encoding="utf-8")

    # Aplicar no no
    set_node_property(scene_path, node_path, "sprite_frames", f'ExtResource("{sf_path}")')
    set_node_property(scene_path, node_path, "animation", anim_name)
    set_node_property(scene_path, node_path, "playing", True)

    result = {
        "status": "success",
        "anim_name": anim_name,
        "frame_count": len(imported),
        "sprite_frames_path": sf_path,
        "message": f"Animacao '{anim_name}' com {len(imported)} frames aplicada em {node_path}",
    }

    # ── Fatia 3.9: sugerir tipo de no ──────────────────
    if category:
        result["suggested_node"] = _resolve_asset_node(category)

    return result


# ══════════════════════════════════════════════════════════════════
# GERADOR: CHATGPT BROWSER (headless Playwright)
# ══════════════════════════════════════════════════════════════════

def _generate_via_chatgpt(prompt: str, save_path: str) -> dict:
    """Gera imagem via ChatGPT/DALL-E usando Playwright headless.

    Abre o ChatGPT no navegador Chromium invisivel, envia o prompt,
    aguarda o DALL-E gerar, faz download da imagem e salva em save_path.

    A sessao e cacheada em chatgpt_session.json — login so na primeira vez.
    """
    if not _HAS_PLAYWRIGHT:
        return {"status": "error", "message": "Playwright nao instalado."}

    with sync_playwright() as p:
        # Usar sessao cacheada se existir
        launch_args = {"headless": True}
        browser = p.chromium.launch(**launch_args)

        context_args = {}
        if CHATGPT_SESSION.exists():
            context_args["storage_state"] = str(CHATGPT_SESSION)

        context = browser.new_context(**context_args)
        page = context.new_page()

        try:
            # Navegar pro ChatGPT
            page.goto("https://chatgpt.com/", wait_until="domcontentloaded", timeout=30000)

            # Verificar se precisa de login
            if "login" in page.url.lower() or "auth" in page.url.lower():
                browser.close()
                return {
                    "status": "error",
                    "message": "ChatGPT requer login. Abra o ChatGPT manualmente uma vez "
                               "para criar a sessao, ou configure a API key do DALL-E.",
                    "error_code": 7001,
                }

            # Aguardar a pagina carregar completamente
            page.wait_for_timeout(3000)

            # Encontrar o campo de texto
            textarea = page.locator("#prompt-textarea, textarea, [contenteditable='true'][role='textbox']").first
            if not textarea or textarea.count() == 0:
                # Tentar clicar no botao "Novo chat" se existir
                new_chat = page.locator("a[href='/']:has-text('Novo'), button:has-text('Novo')").first
                if new_chat and new_chat.count() > 0:
                    new_chat.click()
                    page.wait_for_timeout(2000)

            textarea = page.locator("#prompt-textarea, textarea, [contenteditable='true'][role='textbox']").first
            if not textarea or textarea.count() == 0:
                browser.close()
                return {"status": "error", "message": "Campo de texto do ChatGPT nao encontrado.", "error_code": 7002}

            # Digitar o prompt
            textarea.fill(prompt)
            page.wait_for_timeout(500)

            # Clicar em enviar
            send_btn = page.locator("button[data-testid='send-button'], button:has(svg), [aria-label='Enviar prompt']").first
            if send_btn and send_btn.count() > 0:
                send_btn.click()
            else:
                page.keyboard.press("Enter")

            # Aguardar a geracao (DALL-E leva 10-40s)
            page.wait_for_timeout(5000)

            # Esperar pelo texto "Gerando imagem" ou similar desaparecer
            max_wait = 60  # segundos
            for _ in range(max_wait * 2):
                try:
                    gen_count = page.locator("text=Gerando imagem, text=Creating image, text=Fazendo um esboço").count()
                    if gen_count == 0:
                        break
                except Exception:
                    break
                page.wait_for_timeout(500)

            # Aguardar mais um pouco para garantir
            page.wait_for_timeout(5000)

            # Encontrar a imagem gerada
            img = page.locator("img[alt*='gerada'], img[alt*='Generated'], img[src*='file_']").first
            if not img or img.count() == 0:
                # Scroll up to find the image
                page.evaluate("window.scrollTo(0, 0)")
                page.wait_for_timeout(2000)
                img = page.locator("img[alt*='gerada'], img[alt*='Generated'], img[src*='file_']").first

            if not img or img.count() == 0:
                browser.close()
                return {"status": "error", "message": "Imagem gerada nao encontrada na pagina.", "error_code": 7003}

            img_src = img.get_attribute("src")
            if not img_src:
                browser.close()
                return {"status": "error", "message": "URL da imagem nao encontrada.", "error_code": 7004}

            # Download da imagem via fetch com cookies da sessao
            img_data = page.evaluate("""
                async (url) => {
                    const resp = await fetch(url);
                    const blob = await resp.blob();
                    const buffer = await blob.arrayBuffer();
                    const bytes = Array.from(new Uint8Array(buffer));
                    const binary = bytes.map(b => String.fromCharCode(b)).join('');
                    return btoa(binary);
                }
            """, img_src)

            if img_data and len(img_data) > 100:
                decoded = base64.b64decode(img_data)
                Path(save_path).write_bytes(decoded)

                # Salvar sessao para proximo uso
                context.storage_state(path=str(CHATGPT_SESSION))

                browser.close()
                return {
                    "status": "success",
                    "save_path": save_path,
                    "size_bytes": len(decoded),
                    "generator": "chatgpt_dalle",
                }

            browser.close()
            return {"status": "error", "message": "Falha ao baixar a imagem.", "error_code": 7005}

        except Exception as e:
            import sys as _sys
            print(f"[MCP] ChatGPT browser error: {e}", file=_sys.stderr)
            return {"status": "error", "message": f"Erro no ChatGPT browser: {e}", "error_code": 7000}
        finally:
            try:
                browser.close()
            except Exception:
                pass


# ══════════════════════════════════════════════════════════════════
# GERADOR: PILLOW PROCEDURAL (fallback)
# ══════════════════════════════════════════════════════════════════

def _generate_via_pillow(
    description: str,
    category: str,
    style: str,
    cols: int,
    rows: int,
    width: int,
    height: int,
    save_path: str,
) -> dict:
    """Fallback procedural usando Pillow.

    Gera sprite sheet com formas geometricas coloridas organizadas em grid.
    Cada frame tem uma leve variacao para simular animacao.
    """
    if not _HAS_PILLOW:
        return {"status": "error", "message": "Pillow nao instalado."}

    # Paleta por estilo
    palettes = {
        "scifi": ["#00d4ff", "#7b2fbe", "#1a1a2e", "#e94560", "#0f3460"],
        "fantasia": ["#8B4513", "#FFD700", "#228B22", "#8B0000", "#4A0080"],
        "cartoon": ["#FF6B6B", "#4ECDC4", "#FFE66D", "#A8E6CF", "#FF8B94"],
        "realista": ["#556B2F", "#8B7355", "#708090", "#A0522D", "#2F4F4F"],
        "pixel": ["#2D2D2D", "#5C94FC", "#FCFCFC", "#F83800", "#FCA044"],
        "minimalista": ["#2C3E50", "#ECF0F1", "#3498DB", "#E74C3C", "#2ECC71"],
    }
    palette = palettes.get(style, palettes["scifi"])

    sheet_w = cols * width
    sheet_h = rows * height
    img = Image.new("RGBA", (sheet_w, sheet_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Hash deterministico do description pra variacao consistente
    seed = sum(ord(c) for c in description) % 1000

    for row in range(rows):
        for col in range(cols):
            frame_idx = row * cols + col
            x0 = col * width
            y0 = row * height

            # Variacao por frame
            variation = (frame_idx * 37 + seed) % 100
            color_idx = (frame_idx + seed // 100) % len(palette)
            color = palette[color_idx]

            # Desenhar forma base por categoria
            _draw_category_shape(draw, category, x0, y0, width, height,
                                color, palette, variation, frame_idx)

    img.save(save_path, "PNG")
    return {
        "status": "success",
        "save_path": save_path,
        "generator": "pillow_procedural",
        "note": "Arte procedural (placeholder). Use ChatGPT para arte final.",
    }


def _draw_category_shape(draw, category, x0, y0, w, h, color, palette, var, fi):
    """Desenha forma base por categoria de artefato."""
    m = max(2, w // 16)  # margem

    if category == "torre":
        # Base + canhao + cristal
        base_color = palette[(fi + 1) % len(palette)]
        draw.rectangle([x0 + m, y0 + h//2, x0 + w - m, y0 + h - m], fill=base_color)
        draw.rectangle([x0 + w//4, y0 + h//3, x0 + 3*w//4, y0 + h//2], fill=color)
        # Cristal no topo
        crystal_y = y0 + h//4 + var//5
        draw.ellipse([x0 + w//3, crystal_y, x0 + 2*w//3, crystal_y + h//4],
                    fill=palette[(fi + 2) % len(palette)])

    elif category == "inimigo":
        # Corpo + olhos
        body_color = palette[(fi + var//20) % len(palette)]
        draw.ellipse([x0 + m*2, y0 + m, x0 + w - m*2, y0 + h - m], fill=body_color)
        # Olhos
        eye_col = palette[2] if len(palette) > 2 else "#FFFFFF"
        draw.ellipse([x0 + w//3, y0 + h//3, x0 + w//3 + m*2, y0 + h//3 + m*2], fill=eye_col)

    elif category == "personagem":
        # Cabeca + corpo simplificado
        draw.ellipse([x0 + w//4, y0 + m, x0 + 3*w//4, y0 + h//3], fill=color)
        draw.rectangle([x0 + w//3, y0 + h//3, x0 + 2*w//3, y0 + h - m], fill=palette[(fi + 1) % len(palette)])

    elif category == "projetil":
        # Bola com rastro
        glow = palette[(fi + 2) % len(palette)]
        r = min(w, h) // 4
        cx, cy = x0 + w//2, y0 + h//2
        draw.ellipse([cx - r*2, cy - r, cx + r, cy + r], fill=glow)
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color)

    else:
        # Forma generica
        shape_type = (fi + var) % 3
        if shape_type == 0:
            draw.rectangle([x0 + m, y0 + m, x0 + w - m, y0 + h - m], fill=color)
        elif shape_type == 1:
            draw.ellipse([x0 + m, y0 + m, x0 + w - m, y0 + h - m], fill=color)
        else:
            draw.polygon([
                (x0 + w//2, y0 + m),
                (x0 + w - m, y0 + h - m),
                (x0 + m, y0 + h - m),
            ], fill=color)


# ══════════════════════════════════════════════════════════════════
# POS-PROCESSAMENTO
# ══════════════════════════════════════════════════════════════════

def _crop_sprite_sheet(
    image_path: str, cols: int, rows: int,
    proj: Path, save_dir: str, base_name: str,
) -> list[str]:
    """Recorta sprite sheet em frames individuais e salva no projeto.

    Args:
        image_path: Caminho absoluto da sprite sheet.
        cols, rows: Grid de frames.
        proj: Raiz do projeto Godot.
        save_dir: Diretorio relativo (ex: assets/sprites/towers/).
        base_name: Nome base para os arquivos.

    Returns:
        Lista de caminhos relativos dos frames.
    """
    if not _HAS_PILLOW:
        return [image_path]

    img = Image.open(image_path)
    fw = img.width // cols
    fh = img.height // rows

    dest_dir = proj / save_dir
    dest_dir.mkdir(parents=True, exist_ok=True)

    frame_paths = []
    for row in range(rows):
        for col in range(cols):
            frame_idx = row * cols + col
            frame = img.crop((col * fw, row * fh, (col + 1) * fw, (row + 1) * fh))
            frame_name = f"{base_name}_f{frame_idx + 1}.png"
            frame_path = dest_dir / frame_name
            frame.save(str(frame_path), "PNG")
            rel_path = str(frame_path.relative_to(proj)).replace("\\", "/")
            frame_paths.append(rel_path)

    return frame_paths


def _optimize_png(filepath: str, max_size: int = 256):
    """Otimiza PNG: redimensiona se maior que max_size e reduz paleta."""
    if not _HAS_PILLOW:
        return

    img = Image.open(filepath)

    # Redimensionar se necessario
    if img.width > max_size or img.height > max_size:
        ratio = min(max_size / img.width, max_size / img.height)
        new_w = max(1, int(img.width * ratio))
        new_h = max(1, int(img.height * ratio))
        img = img.resize((new_w, new_h), Image.LANCZOS)

    # Converter pra RGB se nao tem alpha (reduz tamanho)
    if img.mode == "RGBA":
        # Verifica se alpha e realmente usado
        alpha = img.getchannel("A")
        if alpha.getextrema()[0] == 255:
            img = img.convert("RGB")

    img.save(filepath, "PNG", optimize=True)


def _calc_grid(frames: int) -> tuple[int, int]:
    """Calcula layout de grid otimo para N frames."""
    if frames in GRID_LAYOUTS:
        return GRID_LAYOUTS[frames]
    # Fallback: encontrar fator mais proximo
    import math
    cols = int(math.ceil(math.sqrt(frames)))
    rows = int(math.ceil(frames / cols))
    return cols, rows


# ══════════════════════════════════════════════════════════════════
# BUILDERS / HELPERS
# ══════════════════════════════════════════════════════════════════

def _build_prompt(**kwargs) -> str:
    """Monta prompt final usando template da categoria."""
    category = kwargs.get("category", "torre")
    template = PROMPT_TEMPLATES.get(category, PROMPT_TEMPLATES["torre"])
    # Normalizar: template usa {style}, kwargs pode ter style_desc
    if "style" not in kwargs and "style_desc" in kwargs:
        kwargs["style"] = kwargs["style_desc"]
    return template.format(**kwargs)


def _anim_description(category: str, anim_type: str, frames: int) -> str:
    """Descreve a animacao para o prompt."""
    descriptions = {
        "idle": f"frames {1}-{frames}: subtle idle animation with gentle bobbing or energy pulse",
        "fire": f"frames {1}-{max(1, frames//3)}: charging energy, frames {max(1, frames//3)+1}-{max(2, 2*frames//3)}: firing sequence, frames {max(2, 2*frames//3)+1}-{frames}: recoil",
        "walk": f"frames {1}-{frames}: walk cycle animation",
        "run": f"frames {1}-{frames}: running animation",
        "death": f"frames {1}-{frames}: death/destruction animation",
        "attack": f"frames {1}-{frames}: attack animation sequence",
        "spawn": f"frames {1}-{frames}: spawn/appear animation",
        "hit": f"frames {1}-{frames}: hit/damage reaction",
    }
    return descriptions.get(anim_type, f"frames {1}-{frames}: animation sequence")


def _build_sprite_frames_tres(
    frame_paths: list[str], anim_name: str, fps: float, loop: bool
) -> str:
    """Constroi arquivo SpriteFrames .tres (Godot 4.x format=3)."""
    lines = ['[gd_resource type="SpriteFrames" load_steps={} format=3 uid=""]'.format(
        len(frame_paths) + 1), ""]

    # ExtResources
    for i, fp in enumerate(frame_paths):
        lines.append(f'[ext_resource type="Texture2D" path="res://{fp}" id="{i + 1}"]')
    lines.append("")

    # Resource
    lines.append("[resource]")
    lines.append("animations = [")
    lines.append("  {")
    lines.append(f'    "frames": [')
    for i in range(len(frame_paths)):
        comma = "," if i < len(frame_paths) - 1 else ""
        lines.append(f'      ExtResource("{i + 1}"){comma}')
    lines.append(f'    ],')
    lines.append(f'    "loop": {"true" if loop else "false"},')
    lines.append(f'    "name": "{anim_name}",')
    lines.append(f'    "speed": {fps}')
    lines.append("  }")
    lines.append("]")

    return "\n".join(lines) + "\n"


def _get_style(category: str) -> str:
    """Estilo visual por categoria."""
    return "scifi"


def generate_sprite_animation(
    category: str = "character",
    anim_type: str = "idle",
    num_frames: int = 4,
    scene_path: str | None = None,
    parent_node_path: str = ".",
    node_name: str = "",
    fps: float = 8.0,
    loop: bool = True,
    frame_width: int = 64,
    frame_height: int = 64,
    output_dir: str = "assets/animations",
    style_desc: str = "",
) -> dict:
    """Gera animação de sprite com frames consistentes (esqueleto).

    Gera N frames de arte mantendo o mesmo personagem/esqueleto entre
    frames, monta spritesheet, cria arquivo .tres de SpriteFrames e
    opcionalmente configura um AnimatedSprite2D na cena.

    Args:
        category: Categoria do asset (character, enemy, torre, etc.).
        anim_type: Tipo de animação (idle, walk, attack, death, fire, run, spawn, hit).
        num_frames: Número de frames (2-16).
        scene_path: Cena onde criar AnimatedSprite2D (None = só gera arquivos).
        parent_node_path: Nó pai na cena.
        node_name: Nome do AnimatedSprite2D (auto-gerado se vazio).
        fps: Frames por segundo da animação.
        loop: Se a animação repete.
        frame_width: Largura de cada frame.
        frame_height: Altura de cada frame.
        output_dir: Diretório de saída relativo ao projeto.
        style_desc: Descrição de estilo visual (usa style_lock se vazio).

    Returns:
        {"status": "success", "spritesheet": str, "tres_file": str,
         "total_frames": int, "node_path": str (se scene_path)}
    """
    from tools.runtime_ops import mark_pending_compile
    from tools.safety import checkpoint
    from tools.art_postprocess import create_spritesheet

    proj = _get_active_project()

    # ── Validar parâmetros ──────────────────────────────────
    if num_frames < 2 or num_frames > 16:
        return {"status": "error", "message": "num_frames deve ser entre 2 e 16."}

    valid_anims = {"idle", "walk", "attack", "death", "fire", "run", "spawn", "hit"}
    if anim_type not in valid_anims:
        return {"status": "error",
                "message": f"anim_type '{anim_type}' inválido. Use: {', '.join(sorted(valid_anims))}."}

    violation = _check_path_traversal(output_dir, proj)
    if violation:
        return {"status": "error", "message": violation}

    # ── Resolver style ──────────────────────────────────────
    if not style_desc:
        try:
            from tools.project_brief_ops import get_project_brief
            br = get_project_brief()
            if br.get("configured") and br.get("brief"):
                sl = br["brief"].get("style_lock", {})
                style_desc = sl.get("reference", "") or sl.get("art_type", "") or ""
        except Exception:
            pass
    if not style_desc:
        style_desc = "pixel art game sprite" if frame_width <= 64 else "2D game art"

    # ── Estilo de arte por anim_type ────────────────────────
    ANIM_PROMPTS = {
        "idle": f"same character, same skeleton, subtle idle pose, gentle motion, frame {{n}} of {num_frames}",
        "walk": f"same character, same skeleton, walk cycle, frame {{n}} of {num_frames}",
        "attack": f"same character, same skeleton, attack swing, frame {{n}} of {num_frames}",
        "death": f"same character, same skeleton, death animation, frame {{n}} of {num_frames}",
        "fire": f"same character, same skeleton, firing weapon, frame {{n}} of {num_frames}",
        "run": f"same character, same skeleton, running cycle, frame {{n}} of {num_frames}",
        "spawn": f"same character, same skeleton, spawn/appear, frame {{n}} of {num_frames}",
        "hit": f"same character, same skeleton, hit reaction, frame {{n}} of {num_frames}",
    }

    uid = uuid.uuid4().hex[:8]
    anim_dir = proj / output_dir / f"{category}_{anim_type}_{uid}"
    anim_dir.mkdir(parents=True, exist_ok=True)
    checkpoint(str(anim_dir), proj)

    # ── Gerar frames ────────────────────────────────────────
    frame_paths = []
    for n in range(1, num_frames + 1):
        frame_prompt = ANIM_PROMPTS.get(anim_type, ANIM_PROMPTS["idle"]).format(n=n)
        full_prompt = f"{style_desc}, {category}, {frame_prompt}"

        # Tentar generate_game_art (API externa)
        try:
            result = generate_game_art(
                category=category,
                description=full_prompt,
                style=style_desc,
                frames=1,
                width=frame_width,
                height=frame_height,
            )
        except Exception:
            result = {"status": "error", "message": "generate_game_art falhou"}

        if result.get("status") == "success":
            # Salvar frame do base64 ou usar placeholder
            saved = _save_frame_from_result(result, anim_dir, n, frame_width, frame_height)
            if saved:
                frame_paths.append(str(saved.relative_to(proj)))
                continue

        # Fallback: placeholder procedural
        placeholder = _generate_placeholder_frame(anim_dir, n, frame_width, frame_height, category)
        frame_paths.append(str(placeholder.relative_to(proj)))

    # ── Montar spritesheet ──────────────────────────────────
    spritesheet_path = f"{output_dir}/{category}_{anim_type}_{uid}/spritesheet.png"
    sheet_result = create_spritesheet(
        frame_paths=frame_paths,
        output_path=spritesheet_path,
        frame_width=frame_width,
        frame_height=frame_height,
        columns=num_frames,
    )

    # ── Gerar .tres de SpriteFrames ─────────────────────────
    tres_path = f"{output_dir}/{category}_{anim_type}_{uid}/sprite_frames.tres"
    tres_content = _build_sprite_frames_tres(
        frame_paths=frame_paths,
        anim_name=anim_type,
        fps=fps,
        loop=loop,
    )
    (proj / tres_path).write_text(tres_content, encoding="utf-8")

    result = {
        "status": "success",
        "spritesheet": spritesheet_path if sheet_result.get("status") == "success" else None,
        "tres_file": tres_path,
        "total_frames": num_frames,
        "frame_paths": frame_paths,
    }

    # ── Criar AnimatedSprite2D na cena (opcional) ───────────
    if scene_path:
        node = node_name or f"Anim{category.title()}{anim_type.title()}"
        try:
            from tools.scene_ops import add_node, set_node_property
            node_result = add_node(
                scene_path=scene_path,
                parent_node_path=parent_node_path,
                node_name=node,
                node_type="AnimatedSprite2D",
            )
            if node_result.get("status") == "success":
                set_node_property(
                    scene_path=scene_path,
                    node_path=node_result.get("node_path", node),
                    property_name="sprite_frames",
                    value=f"res://{tres_path}",
                )
                result["node_path"] = node_result.get("node_path", f"{scene_path}::{node}")
                result["node_name"] = node
        except Exception:
            result["node_note"] = "Falha ao criar AnimatedSprite2D na cena."

    mark_pending_compile()
    return result


def _save_frame_from_result(result: dict, out_dir, n: int, w: int, h: int) -> "Path | None":
    """Salva frame a partir do resultado de generate_game_art."""
    out_dir = Path(out_dir)

    # 1) Tentar base64 (DALL-E direto, Recraft, etc.)
    b64 = result.get("image_base64", "") or result.get("image", "")
    if b64:
        try:
            data = base64.b64decode(b64)
            fp = out_dir / f"frame_{n:03d}.png"
            fp.write_bytes(data)
            return fp
        except Exception:
            pass

    # 2) Tentar frames gerados por generate_game_art (lista de paths)
    frames = result.get("frames", [])
    if frames:
        frame_path = Path(str(frames[0]))
        if frame_path.exists():
            fp = out_dir / f"frame_{n:03d}.png"
            shutil.copy2(str(frame_path), str(fp))
            return fp

    # 3) Tentar sprite_sheet (extrair frame do grid)
    sprite_sheet = result.get("sprite_sheet") or result.get("spritesheet")
    if sprite_sheet and Path(str(sprite_sheet)).exists():
        try:
            from PIL import Image
            grid = result.get("grid", [1, 1])
            fw = result.get("frame_width", w)
            fh = result.get("frame_height", h)
            sheet = Image.open(str(sprite_sheet))
            col = (n - 1) % grid[0]
            row = (n - 1) // grid[0]
            x, y = col * fw, row * fh
            frame = sheet.crop((x, y, x + fw, y + fh))
            fp = out_dir / f"frame_{n:03d}.png"
            frame.save(fp, "PNG")
            return fp
        except Exception:
            pass

    # 4) Tentar saved_to / file_path / save_path (legado)
    for key in ("saved_to", "file_path", "save_path"):
        path_str = result.get(key, "")
        if path_str and Path(str(path_str)).exists():
            fp = out_dir / f"frame_{n:03d}.png"
            shutil.copy2(str(path_str), str(fp))
            return fp

    return None


def _generate_placeholder_frame(out_dir, n: int, w: int, h: int, category: str) -> "Path":
    """Gera frame placeholder procedural via Pillow."""
    out_dir = Path(out_dir)
    try:
        from PIL import Image, ImageDraw
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        colors = [(255, 100, 100), (100, 255, 100), (100, 100, 255), (255, 255, 100)]
        c = colors[(n - 1) % len(colors)]
        margin = 4
        draw.rectangle([margin, margin, w - margin, h - margin], fill=c, outline=(255, 255, 255))
        # Número do frame
        draw.text((w // 2 - 8, h // 2 - 8), str(n), fill=(0, 0, 0))
        fp = out_dir / f"frame_{n:03d}.png"
        img.save(fp, "PNG")
        return fp
    except ImportError:
        # Fallback mínimo sem Pillow
        fp = out_dir / f"frame_{n:03d}.png"
        fp.write_bytes(b"")
        return fp
