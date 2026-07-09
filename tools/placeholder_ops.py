"""placeholder_ops — Geração procedural de assets (sprites, áudio, tilesets).

Onda 3: Permite à IA criar assets visuais e sonoros sem depender de artista.
Usa Pillow (PIL) para imagens e wave/math para áudio.

Funções:
    generate_placeholder_sprite — PNG com forma geométrica colorida
    generate_placeholder_texture_atlas — sprite sheet procedural com N frames
    generate_background_gradient — PNG com gradiente
    generate_tileset_from_colors — tileset .tres + textura com paleta de cores
    generate_audio_sfx — WAV com síntese procedural (beep, noise, sweep)
    suggest_color_palette — paleta de cores por gênero de jogo
"""

import math
import struct
import wave
from pathlib import Path

# Pillow é opcional — fallback para geração raw de PNG se não instalado
try:
    from PIL import Image, ImageDraw, ImageFont
    _HAS_PILLOW = True
except ImportError:
    _HAS_PILLOW = False

from tools.project_ops import _get_active_project, _check_path_traversal

ROOT = Path(__file__).resolve().parent.parent


# ═══════════════════════════════════════════════════════════════════════
# 🎨 Geração de Sprites
# ═══════════════════════════════════════════════════════════════════════

def generate_placeholder_sprite(
    name: str,
    width: int = 64,
    height: int = 64,
    color: str = "#3498db",
    shape: str = "rectangle",
    save_path: str | None = None,
) -> dict:
    """Gera um sprite placeholder (PNG) com forma geométrica colorida.

    Args:
        name: Nome base do arquivo.
        width: Largura em pixels.
        height: Altura em pixels.
        color: Cor em hex (#RRGGBB) ou nome (red, blue, green).
        shape: "rectangle", "circle", "triangle", "diamond", "star".
        save_path: Caminho relativo no projeto (opcional).

    Returns:
        {"status": "success", "image_base64": str, "saved_to": str}
    """
    proj = _get_active_project()

    if not save_path:
        save_path = f"assets/sprites/{name}.png"

    violation = _check_path_traversal(save_path, proj)
    if violation:
        return {"status": "error", "message": violation}

    # Parse cor
    from PIL.ImageColor import getrgb as _parse_color
    try:
        rgb = _parse_color(color)
    except Exception:
        rgb = (52, 152, 219)  # default blue

    if _HAS_PILLOW:
        return _generate_sprite_pillow(proj, save_path, name, width, height, rgb, shape)
    else:
        return _generate_sprite_raw(proj, save_path, name, width, height, rgb, shape)


def _generate_sprite_pillow(proj, save_path, name, w, h, rgb, shape):
    import base64
    from io import BytesIO

    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    m = 2  # margin
    if shape == "rectangle":
        draw.rectangle([m, m, w - m, h - m], fill=rgb)
    elif shape == "circle":
        draw.ellipse([m, m, w - m, h - m], fill=rgb)
    elif shape == "triangle":
        draw.polygon([(w // 2, m), (m, h - m), (w - m, h - m)], fill=rgb)
    elif shape == "diamond":
        draw.polygon([(w // 2, m), (w - m, h // 2), (w // 2, h - m), (m, h // 2)], fill=rgb)
    elif shape == "star":
        pts = _star_points(w // 2, h // 2, w // 2 - m, w // 4 - m, 5)
        draw.polygon(pts, fill=rgb)
    else:
        draw.rectangle([m, m, w - m, h - m], fill=rgb)

    # Borda sutil
    border = tuple(max(0, c - 40) for c in rgb)
    if shape == "rectangle":
        draw.rectangle([0, 0, w - 1, h - 1], outline=border)

    full = proj / save_path
    full.parent.mkdir(parents=True, exist_ok=True)
    img.save(str(full), "PNG")

    buf = BytesIO()
    img.save(buf, "PNG")
    b64 = base64.b64encode(buf.getvalue()).decode("ascii")

    return {"status": "success", "image_base64": b64, "saved_to": save_path,
            "size": [w, h], "color": f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"}


def _generate_sprite_raw(proj, save_path, name, w, h, rgb, shape):
    """Fallback sem Pillow: gera PNG mínimo (retângulo sólido)."""
    import base64
    import zlib

    # Cria pixels RGBA
    pixels = []
    for y in range(h):
        pixels.append(0)  # filtro None
        for x in range(w):
            margin = 2
            inside = (margin <= x < w - margin and margin <= y < h - margin)
            if inside:
                pixels.extend([rgb[0], rgb[1], rgb[2], 255])
            else:
                # Borda escura
                border = tuple(max(0, c - 50) for c in rgb)
                is_border = (x < margin or x >= w - margin or y < margin or y >= h - margin)
                if is_border and (x == 0 or y == 0 or x == w - 1 or y == h - 1):
                    pixels.extend([border[0], border[1], border[2], 255])
                else:
                    pixels.extend([0, 0, 0, 0])

    raw = bytes(pixels)
    compressed = zlib.compress(raw)

    def chunk(ctype, data):
        c = ctype + data
        return struct.pack(">I", len(data)) + c + struct.pack(">I", zlib.crc32(c) & 0xFFFFFFFF)

    png = b'\x89PNG\r\n\x1a\n'
    png += chunk(b'IHDR', struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0))
    png += chunk(b'IDAT', compressed)
    png += chunk(b'IEND', b'')

    full = proj / save_path
    full.parent.mkdir(parents=True, exist_ok=True)
    full.write_bytes(png)

    b64 = base64.b64encode(png).decode("ascii")
    return {"status": "success", "image_base64": b64, "saved_to": save_path,
            "size": [w, h], "color": f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}",
            "note": "Gerado sem Pillow (fallback raw PNG). Para mais formas, instale: pip install pillow"}


def _star_points(cx, cy, outer_r, inner_r, points):
    pts = []
    for i in range(points * 2):
        angle = math.pi / 2 + i * math.pi / points
        r = outer_r if i % 2 == 0 else inner_r
        pts.append((cx + r * math.cos(angle), cy - r * math.sin(angle)))
    return pts


# ═══════════════════════════════════════════════════════════════════════
# 🎞️ Sprite Sheet / Texture Atlas
# ═══════════════════════════════════════════════════════════════════════

def generate_placeholder_texture_atlas(
    name: str,
    frame_width: int = 64,
    frame_height: int = 64,
    columns: int = 4,
    rows: int = 1,
    color: str = "#e74c3c",
    shape: str = "rectangle",
    variation: str = "position",
    save_path: str | None = None,
) -> dict:
    """Gera uma sprite sheet procedural com múltiplos frames.

    Args:
        name: Nome base.
        frame_width, frame_height: Tamanho de cada frame.
        columns, rows: Grid de frames (ex: 4 colunas × 1 linha = 4 frames).
        color: Cor base.
        shape: Forma do sprite.
        variation: "position" (desloca), "color" (muda cor), "scale" (muda tamanho).
        save_path: Caminho relativo (opcional).

    Returns:
        {"status": "success", "image_base64": str, "saved_to": str, "frames": int}
    """
    proj = _get_active_project()

    if not save_path:
        save_path = f"assets/sprites/{name}_sheet.png"

    violation = _check_path_traversal(save_path, proj)
    if violation:
        return {"status": "error", "message": violation}

    try:
        rgb = _parse_color(color)
    except Exception:
        rgb = (231, 76, 60)

    total_w = frame_width * columns
    total_h = frame_height * rows

    if _HAS_PILLOW:
        return _generate_atlas_pillow(proj, save_path, name, total_w, total_h,
                                       frame_width, frame_height, columns, rows,
                                       rgb, shape, variation)
    else:
        # Fallback: gera frame único
        return generate_placeholder_sprite(
            name + "_atlas", total_w, total_h, color, shape, save_path
        )


def _generate_atlas_pillow(proj, save_path, name, tw, th, fw, fh, cols, rows, rgb, shape, var):
    import base64
    from io import BytesIO

    img = Image.new("RGBA", (tw, th), (0, 0, 0, 0))

    for row in range(rows):
        for col in range(cols):
            frame_idx = row * cols + col
            fx = col * fw
            fy = row * fh

            # Variação por frame
            fr, fg, fb = rgb
            fs = 1.0
            fdx, fdy = 0, 0

            if var == "color":
                hue_shift = frame_idx * 30
                fr = min(255, fr + hue_shift // 2)
                fg = min(255, fg - hue_shift // 3)
                fb = min(255, fb + hue_shift)
            elif var == "position":
                fdx = (frame_idx % 2) * 4 - 2
                fdy = (frame_idx % 3 - 1) * 4
            elif var == "scale":
                fs = 0.7 + (frame_idx % 4) * 0.1

            frame_color = (max(0, min(255, fr)), max(0, min(255, fg)), max(0, min(255, fb)))
            sw = int(fw * fs)
            sh = int(fh * fs)
            sx = fx + (fw - sw) // 2 + fdx
            sy = fy + (fh - sh) // 2 + fdy

            frame_img = Image.new("RGBA", (fw, fh), (0, 0, 0, 0))
            fdraw = ImageDraw.Draw(frame_img)
            m = 2
            if shape == "rectangle":
                fdraw.rectangle([m, m, sw - m, sh - m], fill=frame_color)
            elif shape == "circle":
                fdraw.ellipse([m, m, sw - m, sh - m], fill=frame_color)
            else:
                fdraw.rectangle([m, m, sw - m, sh - m], fill=frame_color)

            img.paste(frame_img, (fx, fy), frame_img)

    full = proj / save_path
    full.parent.mkdir(parents=True, exist_ok=True)
    img.save(str(full), "PNG")

    buf = BytesIO()
    img.save(buf, "PNG")
    b64 = base64.b64encode(buf.getvalue()).decode("ascii")

    return {"status": "success", "image_base64": b64, "saved_to": save_path,
            "frames": cols * rows, "grid": [cols, rows],
            "frame_size": [fw, fh]}


# ═══════════════════════════════════════════════════════════════════════
# 🌈 Background Gradient
# ═══════════════════════════════════════════════════════════════════════

def generate_background_gradient(
    name: str,
    width: int = 1280,
    height: int = 720,
    color_top: str = "#1a1a2e",
    color_bottom: str = "#16213e",
    direction: str = "vertical",
    save_path: str | None = None,
) -> dict:
    """Gera um fundo com gradiente.

    Args:
        name: Nome base.
        width, height: Dimensões.
        color_top, color_bottom: Cores do gradiente.
        direction: "vertical", "horizontal", "radial".
        save_path: Caminho relativo (opcional).

    Returns:
        {"status": "success", "image_base64": str, "saved_to": str}
    """
    proj = _get_active_project()
    if not save_path:
        save_path = f"assets/backgrounds/{name}.png"
    violation = _check_path_traversal(save_path, proj)
    if violation:
        return {"status": "error", "message": violation}

    try:
        c1 = _parse_color(color_top)
        c2 = _parse_color(color_bottom)
    except Exception:
        c1, c2 = (26, 26, 46), (22, 33, 62)

    if _HAS_PILLOW:
        return _generate_gradient_pillow(proj, save_path, width, height, c1, c2, direction)
    else:
        return {"status": "error", "message": "Pillow não instalado. Execute: pip install pillow"}


def _generate_gradient_pillow(proj, save_path, w, h, c1, c2, direction):
    import base64
    from io import BytesIO

    img = Image.new("RGBA", (w, h))
    pixels = img.load()

    for y in range(h):
        for x in range(w):
            if direction == "radial":
                dx = (x - w / 2) / (w / 2)
                dy = (y - h / 2) / (h / 2)
                t = min(1.0, math.sqrt(dx * dx + dy * dy))
            elif direction == "horizontal":
                t = x / w
            else:
                t = y / h
            r = int(c1[0] + (c2[0] - c1[0]) * t)
            g = int(c1[1] + (c2[1] - c1[1]) * t)
            b = int(c1[2] + (c2[2] - c1[2]) * t)
            pixels[x, y] = (r, g, b, 255)

    full = proj / save_path
    full.parent.mkdir(parents=True, exist_ok=True)
    img.save(str(full), "PNG")

    buf = BytesIO()
    img.save(buf, "PNG")
    b64 = base64.b64encode(buf.getvalue()).decode("ascii")
    return {"status": "success", "image_base64": b64, "saved_to": save_path,
            "size": [w, h]}


# ═══════════════════════════════════════════════════════════════════════
# 🧱 Tileset from Colors
# ═══════════════════════════════════════════════════════════════════════

def generate_tileset_from_colors(
    palette_name: str,
    colors: list[str],
    tile_width: int = 16,
    tile_height: int = 16,
    save_texture_path: str | None = None,
    save_tileset_path: str | None = None,
) -> dict:
    """Gera um tileset .tres + textura PNG com tiles coloridos.

    Args:
        palette_name: Nome base.
        colors: Lista de cores hex (ex: ["#27ae60", "#8B4513", "#3498db"]).
        tile_width, tile_height: Tamanho de cada tile.
        save_texture_path: Caminho da textura (opcional).
        save_tileset_path: Caminho do .tres (opcional).

    Returns:
        {"status": "success", "texture_path": str, "tileset_path": str, "tile_count": int}
    """
    proj = _get_active_project()
    if not save_texture_path:
        save_texture_path = f"assets/tiles/{palette_name}.png"
    if not save_tileset_path:
        save_tileset_path = f"assets/tiles/{palette_name}.tres"

    violation = _check_path_traversal(save_texture_path, proj)
    if violation:
        return {"status": "error", "message": violation}

    tiles_per_row = min(len(colors), 8)
    rows = (len(colors) + tiles_per_row - 1) // tiles_per_row
    total_w = tile_width * tiles_per_row
    total_h = tile_height * rows

    if not _HAS_PILLOW:
        return {"status": "error", "message": "Pillow não instalado. Execute: pip install pillow"}

    import base64
    from io import BytesIO

    img = Image.new("RGBA", (total_w, total_h))
    draw = ImageDraw.Draw(img)

    for i, color in enumerate(colors):
        col = i % tiles_per_row
        row = i // tiles_per_row
        x = col * tile_width
        y = row * tile_height
        try:
            rgb = _parse_color(color)
        except Exception:
            rgb = (128, 128, 128)
        draw.rectangle([x, y, x + tile_width - 1, y + tile_height - 1], fill=rgb)
        draw.rectangle([x, y, x + tile_width - 1, y + tile_height - 1],
                       outline=tuple(max(0, c - 30) for c in rgb))

    tex_full = proj / save_texture_path
    tex_full.parent.mkdir(parents=True, exist_ok=True)
    img.save(str(tex_full), "PNG")

    # Gera .tres
    tres_content = f"""[gd_resource type="TileSet" load_steps=1 format=2]

[resource]
tile_size = Vector2i({tile_width}, {tile_height})
"""
    tres_full = proj / save_tileset_path
    tres_full.write_text(tres_content, encoding="utf-8")

    buf = BytesIO()
    img.save(buf, "PNG")
    b64 = base64.b64encode(buf.getvalue()).decode("ascii")

    from tools.runtime_ops import mark_pending_compile
    mark_pending_compile()

    return {"status": "success", "image_base64": b64,
            "texture_path": save_texture_path, "tileset_path": save_tileset_path,
            "tile_count": len(colors), "tile_size": [tile_width, tile_height]}


# ═══════════════════════════════════════════════════════════════════════
# 🔊 Audio SFX (Síntese Procedural)
# ═══════════════════════════════════════════════════════════════════════

def generate_audio_sfx(
    name: str,
    sfx_type: str = "beep",
    duration: float = 0.3,
    frequency: float = 440.0,
    sample_rate: int = 44100,
    save_path: str | None = None,
) -> dict:
    """Gera um efeito sonoro WAV por síntese procedural.

    Args:
        name: Nome base.
        sfx_type: "beep" (tom puro), "jump" (sweep ascendente),
                  "laser" (sweep descendente), "explosion" (ruído),
                  "collect" (dois tons), "hit" (ruído curto).
        duration: Duração em segundos.
        frequency: Frequência base em Hz.
        sample_rate: Sample rate (default 44100).
        save_path: Caminho relativo (opcional).

    Returns:
        {"status": "success", "saved_to": str, "duration": float}
    """
    proj = _get_active_project()
    if not save_path:
        save_path = f"assets/audio/{name}.wav"

    violation = _check_path_traversal(save_path, proj)
    if violation:
        return {"status": "error", "message": violation}

    num_samples = int(sample_rate * duration)
    samples = []

    if sfx_type == "jump":
        # Sweep ascendente: frequência sobe de freq para freq*2
        for i in range(num_samples):
            t = i / sample_rate
            f = frequency * (1.0 + t / duration)
            val = math.sin(2 * math.pi * f * t)
            # Envelope
            env = 1.0 - (i / num_samples)
            samples.append(int(val * env * 32767 * 0.7))
    elif sfx_type == "laser":
        # Sweep descendente
        for i in range(num_samples):
            t = i / sample_rate
            f = frequency * 2 * (1.0 - t / duration) + frequency * 0.2
            val = math.sin(2 * math.pi * f * t)
            samples.append(int(val * 32767 * 0.6))
    elif sfx_type == "explosion":
        # Ruído branco com envelope
        import random
        rng = random.Random(42)
        for i in range(num_samples):
            t = i / sample_rate
            val = rng.uniform(-1, 1)
            env = max(0, 1.0 - t / duration) ** 2
            samples.append(int(val * env * 32767 * 0.8))
    elif sfx_type == "collect":
        # Dois tons rápidos (ding-ding!)
        for i in range(num_samples):
            t = i / sample_rate
            f = 880 if t < duration / 2 else 1320
            val = math.sin(2 * math.pi * f * t)
            env = max(0, 1.0 - abs(t - duration / 2) / (duration / 2))
            samples.append(int(val * env * 32767 * 0.7))
    elif sfx_type == "hit":
        # Ruído curto com decaimento rápido
        import random
        rng = random.Random(99)
        for i in range(num_samples):
            t = i / sample_rate
            tone = math.sin(2 * math.pi * 120 * t)
            noise = rng.uniform(-0.5, 0.5)
            val = tone * 0.3 + noise * 0.7
            env = math.exp(-t * 30)
            samples.append(int(val * env * 32767 * 0.9))
    else:  # beep
        for i in range(num_samples):
            t = i / sample_rate
            val = math.sin(2 * math.pi * frequency * t)
            env = 1.0 - (i / num_samples) ** 0.5
            samples.append(int(val * env * 32767 * 0.5))

    # Escreve WAV
    full = proj / save_path
    full.parent.mkdir(parents=True, exist_ok=True)

    with wave.open(str(full), "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)  # 16-bit
        wf.setframerate(sample_rate)
        wf.writeframes(struct.pack(f"<{len(samples)}h", *samples))

    return {"status": "success", "saved_to": save_path,
            "duration": duration, "type": sfx_type}


# ═══════════════════════════════════════════════════════════════════════
# 🎨 Color Palette Suggester
# ═══════════════════════════════════════════════════════════════════════

# Paletas pré-definidas por gênero (conhecimento interno — não inventado)
_GENRE_PALETTES = {
    "platformer": {
        "name": "Plataforma Clássica",
        "colors": ["#4a90d9", "#27ae60", "#8B4513", "#f39c12", "#2c3e50", "#ecf0f1"],
        "usage": {
            "player": "#4a90d9",
            "ground": "#8B4513",
            "enemy": "#e74c3c",
            "sky": "#87CEEB",
            "collectible": "#f39c12",
        },
    },
    "space_shooter": {
        "name": "Space Shooter",
        "colors": ["#0a0a2e", "#1a1a4e", "#e74c3c", "#3498db", "#f1c40f", "#2ecc71"],
        "usage": {
            "player": "#3498db",
            "enemy": "#e74c3c",
            "bullet": "#f1c40f",
            "background": "#0a0a2e",
            "powerup": "#2ecc71",
        },
    },
    "tower_defense": {
        "name": "Tower Defense",
        "colors": ["#2c3e50", "#27ae60", "#e67e22", "#9b59b6", "#c0392b", "#ecf0f1"],
        "usage": {
            "path": "#e67e22",
            "tower": "#9b59b6",
            "enemy": "#c0392b",
            "ground": "#27ae60",
            "ui": "#ecf0f1",
        },
    },
    "puzzle": {
        "name": "Puzzle Casual",
        "colors": ["#1abc9c", "#3498db", "#9b59b6", "#e74c3c", "#f1c40f", "#2ecc71"],
        "usage": {
            "tiles": ["#1abc9c", "#3498db", "#9b59b6", "#e74c3c", "#f1c40f", "#2ecc71"],
            "background": "#ecf0f1",
        },
    },
    "rpg": {
        "name": "RPG Fantasy",
        "colors": ["#8B4513", "#2ecc71", "#3498db", "#9b59b6", "#e74c3c", "#f39c12"],
        "usage": {
            "player": "#3498db",
            "npc": "#2ecc71",
            "enemy": "#e74c3c",
            "ground": "#8B4513",
            "magic": "#9b59b6",
            "gold": "#f39c12",
        },
    },
    "arcade": {
        "name": "Arcade Retrô",
        "colors": ["#FF0000", "#00FF00", "#0000FF", "#FFFF00", "#FF00FF", "#00FFFF"],
        "usage": {
            "player1": "#FF0000",
            "player2": "#0000FF",
            "enemy": "#FF00FF",
            "score": "#FFFF00",
            "powerup": "#00FF00",
        },
    },
    "horror": {
        "name": "Horror/Suspense",
        "colors": ["#1a1a1a", "#2c3e50", "#8B0000", "#4a4a4a", "#660000", "#ecf0f1"],
        "usage": {
            "background": "#1a1a1a",
            "walls": "#2c3e50",
            "blood": "#8B0000",
            "fog": "#4a4a4a",
            "text": "#ecf0f1",
        },
    },
}


def suggest_color_palette(genre: str) -> dict:
    """Sugere uma paleta de cores baseada no gênero do jogo.

    Args:
        genre: "platformer", "space_shooter", "tower_defense", "puzzle",
               "rpg", "arcade", "horror", ou "all" para listar todos.

    Returns:
        {"status": "success", "palette": {...}} ou {"status": "success", "genres": [...]}
    """
    if genre == "all":
        return {
            "status": "success",
            "genres": [
                {"genre": k, "name": v["name"], "color_count": len(v["colors"])}
                for k, v in _GENRE_PALETTES.items()
            ],
        }

    palette = _GENRE_PALETTES.get(genre)
    if not palette:
        close = [k for k in _GENRE_PALETTES if genre.lower() in k.lower()]
        return {
            "status": "error",
            "message": f"Gênero '{genre}' não encontrado. "
                       f"Gêneros disponíveis: {list(_GENRE_PALETTES.keys())}."
                       + (f" Você quis dizer: {close}?" if close else ""),
        }

    return {"status": "success", "palette": palette}


# Helper para parse de cor (compatível com código sem Pillow)
def _parse_color(color: str) -> tuple:
    """Parse cor hex ou nome para RGB tuple."""
    if color.startswith("#"):
        h = color.lstrip("#")
        if len(h) == 3:
            h = "".join(c * 2 for c in h)
        return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
    # Nomes comuns
    named = {
        "red": (231, 76, 60), "green": (46, 204, 113), "blue": (52, 152, 219),
        "yellow": (241, 196, 15), "orange": (230, 126, 34), "purple": (155, 89, 182),
        "white": (255, 255, 255), "black": (30, 30, 30), "gray": (149, 165, 166),
        "cyan": (0, 255, 255), "magenta": (255, 0, 255), "brown": (139, 69, 19),
        "pink": (255, 105, 180), "lime": (0, 255, 0), "navy": (0, 0, 128),
    }
    if color.lower() in named:
        return named[color.lower()]
    return (128, 128, 128)
