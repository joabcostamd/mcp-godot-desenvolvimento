#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Pipeline Enterprise de Geração de Previews — v2.0.

Multi-formato, multi-encoder, com validação automática de qualidade.

Pipeline:
  1. Render frames PNG com Cairo (antialiasing nativo, gradientes, curvas)
  2. Encoder GIF: gifski (qualidade máxima, pngquant palette)
  3. Encoder MP4: FFmpeg libx264 (menor tamanho, melhor qualidade)
  4. Encoder WebP: FFmpeg libwebp (alternativa moderna)
  5. Validador automático de qualidade

Uso: python scripts/gerar_preview_enterprise.py [--batch N] [--all] [--format gif,mp4,webp]
"""

import json
import math
import os
import subprocess
import sys
import tempfile
import shutil
from pathlib import Path
from PIL import Image

BEHAVIORS_ROOT = os.path.join(os.path.dirname(__file__), "..", "behaviors")

# ── CONFIG ──────────────────────────────────────────────────
W, H = 640, 360
FPS = 15
DURATION = 4
N_FRAMES = FPS * DURATION  # 60

# ── PALETA ──────────────────────────────────────────────────
C_BG        = (18, 22, 28)
C_GROUND    = (40, 48, 56)
C_GROUND_LINE = (60, 70, 82)
C_PLAYER    = (80, 180, 255)
C_ENEMY     = (255, 90, 90)
C_HEALTH_BG = (50, 50, 55)
C_HEALTH    = (80, 200, 100)
C_DAMAGE    = (255, 70, 70)
C_PROJECTILE = (255, 220, 80)
C_PARTICLE  = (255, 200, 100)
C_TEXT      = (230, 235, 240)
C_SUBTEXT   = (140, 150, 165)
C_ACCENT    = (80, 180, 255)
C_WHITE     = (255, 255, 255)
C_ITEM      = (255, 215, 0)


def _blend(c1, c2, t):
    return tuple(int(c1[i] + (c2[i]-c1[i])*t) for i in range(3))

def _alpha(c, a):
    return tuple(int(c[i]*a + C_BG[i]*(1-a)) for i in range(3))

def _ease_in_out(t):
    return t*t*(3 - 2*t)

def _pulse(t, speed=2):
    return 0.5 + 0.5 * math.sin(t * math.pi * speed)

# ── RENDERIZAÇÃO COM CAIRO (tenta, fallback para Pillow) ────

try:
    import cairo
    HAS_CAIRO = True
except ImportError:
    HAS_CAIRO = False


def create_surface():
    """Cria superfície de renderização. Cairo se disponível, senão Pillow."""
    if HAS_CAIRO:
        surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
        ctx = cairo.Context(surf)
        # Fundo
        ctx.set_source_rgb(C_BG[0]/255, C_BG[1]/255, C_BG[2]/255)
        ctx.paint()
        return surf, ctx, True
    else:
        img = Image.new("RGB", (W, H), C_BG)
        from PIL import ImageDraw as ID
        draw = ID.Draw(img)
        return (img, draw), None, False


def finish_frame(surf_ctx, is_cairo):
    """Finaliza frame: Cairo → PNG bytes; Pillow → Image."""
    if is_cairo:
        surf, ctx = surf_ctx
        surf.flush()
        return surf  # Cairo ImageSurface, será convertido depois
    else:
        return surf_ctx[0]  # Pillow Image


# ── PRIMITIVAS DE DESENHO (Cairo + Pillow) ──────────────────

def _get_font(size):
    for fp in ["C:/Windows/Fonts/consola.ttf", "C:/Windows/Fonts/segoeui.ttf",
               "C:/Windows/Fonts/arial.ttf"]:
        if os.path.isfile(fp):
            return fp
    return None


def draw_ground(ctx, is_cairo, y=None):
    gy = y if y else H - 50
    if is_cairo:
        ctx.set_source_rgb(C_GROUND[0]/255, C_GROUND[1]/255, C_GROUND[2]/255)
        ctx.rectangle(0, gy, W, H-gy)
        ctx.fill()
        ctx.set_source_rgb(C_GROUND_LINE[0]/255, C_GROUND_LINE[1]/255, C_GROUND_LINE[2]/255)
        ctx.set_line_width(2)
        ctx.move_to(0, gy)
        ctx.line_to(W, gy)
        ctx.stroke()
    else:
        img, draw = ctx
        draw.rectangle([0, gy, W, H], fill=C_GROUND)
        draw.line([0, gy, W, gy], fill=C_GROUND_LINE, width=2)


def draw_character(ctx, is_cairo, x, y, color, scale=1.0, facing_right=True):
    s = int(16 * scale)
    r, g, b = color[0]/255, color[1]/255, color[2]/255

    if is_cairo:
        # Corpo
        bx, by = x - s//2, y - s*2
        ctx.set_source_rgb(r, g, b)
        _cairo_roundrect(ctx, bx, by, s, s*2, s//3)
        ctx.fill()
        # Cabeça
        head_r = s * 0.7
        ctx.set_source_rgb(*_blend(color, C_WHITE, 0.15))
        ctx.set_source_rgb(r*1.1, g*1.1, b*1.1)
        ctx.arc(x, by - head_r*1.5, head_r, 0, math.pi*2)
        ctx.fill()
        # Olhos
        eye_r = max(2, int(head_r//3))
        ctx.set_source_rgb(C_BG[0]/255, C_BG[1]/255, C_BG[2]/255)
        eye_y = int(by - head_r*1.5)
        if facing_right:
            ctx.arc(x+3, eye_y-eye_r, eye_r, 0, math.pi*2)
        else:
            ctx.arc(x-3, eye_y-eye_r, eye_r, 0, math.pi*2)
        ctx.fill()
    else:
        img, draw = ctx
        bx, by = x - s//2, y - s*2
        draw.rounded_rectangle([bx, by, bx+s, by+s*2], radius=s//3, fill=color)
        head_r = int(s * 0.7)
        lighter = _blend(color, C_WHITE, 0.15)
        draw.ellipse([x-head_r, int(by-head_r*2+2), x+head_r, by+2], fill=lighter)
        eye_r = max(2, head_r//3)
        eye_y = by - head_r
        if facing_right:
            draw.ellipse([x+2, eye_y-eye_r, x+2+eye_r*2, eye_y+eye_r], fill=C_BG)
        else:
            draw.ellipse([x-2-eye_r*2, eye_y-eye_r, x-2, eye_y+eye_r], fill=C_BG)


def _cairo_roundrect(ctx, x, y, w, h, r):
    """Retângulo arredondado em Cairo."""
    ctx.new_path()
    ctx.arc(x+w-r, y+r, r, -math.pi/2, 0)
    ctx.arc(x+w-r, y+h-r, r, 0, math.pi/2)
    ctx.arc(x+r, y+h-r, r, math.pi/2, math.pi)
    ctx.arc(x+r, y+r, r, math.pi, math.pi*3/2)
    ctx.close_path()


def draw_health_bar(ctx, is_cairo, x, y, w_bar, current, maximum):
    h = 8
    pct = max(0, min(1, current/maximum))
    bar_w = int(w_bar * pct)
    color = C_HEALTH if pct > 0.5 else C_DAMAGE if pct > 0.25 else (255, 50, 50)

    if is_cairo:
        ctx.set_source_rgb(C_HEALTH_BG[0]/255, C_HEALTH_BG[1]/255, C_HEALTH_BG[2]/255)
        ctx.rectangle(x, y, w_bar, h)
        ctx.fill()
        if bar_w > 0:
            ctx.set_source_rgb(color[0]/255, color[1]/255, color[2]/255)
            ctx.rectangle(x, y, bar_w, h)
            ctx.fill()
        ctx.set_source_rgb(0.39, 0.43, 0.49)
        ctx.set_line_width(1)
        ctx.rectangle(x, y, w_bar, h)
        ctx.stroke()
    else:
        img, draw = ctx
        draw.rectangle([x, y, x+w_bar, y+h], fill=C_HEALTH_BG)
        if bar_w > 0:
            draw.rectangle([x, y, x+bar_w, y+h], fill=color)
        draw.rectangle([x, y, x+w_bar, y+h], outline=(100, 110, 125), width=1)


def draw_projectile(ctx, is_cairo, x, y, color=C_PROJECTILE, size=5):
    if is_cairo:
        ctx.set_source_rgba(color[0]/255, color[1]/255, color[2]/255, 0.9)
        ctx.arc(x, y, size, 0, math.pi*2)
        ctx.fill()
        # Rastro
        for i in range(3):
            alpha = 0.4 - i*0.12
            if alpha > 0:
                ctx.set_source_rgba(color[0]/255, color[1]/255, color[2]/255, alpha)
                tx = x - (i+1)*size
                ctx.arc(tx, y, size//2, 0, math.pi*2)
                ctx.fill()
    else:
        img, draw = ctx
        draw.ellipse([x-size, y-size//2, x+size, y+size//2], fill=color)
        for i in range(3):
            alpha = 1 - i*0.3
            tx = x - (i+1)*size
            c = _alpha(color, alpha*0.5)
            draw.ellipse([tx-size//2, y-size//4, tx+size//2, y+size//4], fill=c)


def draw_particle(ctx, is_cairo, x, y, color, size, alpha):
    if is_cairo:
        ctx.set_source_rgba(color[0]/255, color[1]/255, color[2]/255, alpha)
        ctx.arc(x, y, size, 0, math.pi*2)
        ctx.fill()
    else:
        img, draw = ctx
        c = _alpha(color, alpha)
        draw.ellipse([x-size, y-size, x+size, y+size], fill=c)


def draw_text(ctx, is_cairo, text, x, y, font_path, size, color=C_TEXT):
    if is_cairo and font_path and os.path.isfile(font_path):
        ctx.set_source_rgb(color[0]/255, color[1]/255, color[2]/255)
        ctx.select_font_face(font_path.split("/")[-1].replace(".ttf",""),
                             cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(size)
        # Centralizar
        extents = ctx.text_extents(text)
        ctx.move_to(x - extents.width/2, y + extents.height)
        ctx.show_text(text)
    elif not is_cairo:
        img, draw = ctx
        from PIL import ImageFont
        font = None
        if font_path:
            try:
                font = ImageFont.truetype(font_path, size)
            except:
                font = ImageFont.load_default()
        else:
            font = ImageFont.load_default()
        bbox = draw.textbbox((0, 0), text, font=font)
        tw = bbox[2] - bbox[0]
        draw.text((x-tw//2, y), text, fill=color, font=font)


def draw_badge(ctx, is_cairo, text, x, y, color, font_path, font_size=11):
    if is_cairo:
        ctx.set_font_size(font_size)
        ext = ctx.text_extents(text)
        tw, th = ext.width, ext.height
        pad = 6
        ctx.set_source_rgb(color[0]/255, color[1]/255, color[2]/255)
        _cairo_roundrect(ctx, x-pad, y-th, tw+pad*2, th+8, 4)
        ctx.fill()
        ctx.set_source_rgb(C_BG[0]/255, C_BG[1]/255, C_BG[2]/255)
        ctx.move_to(x, y)
        ctx.show_text(text)
    else:
        img, draw = ctx
        from PIL import ImageFont
        font = ImageFont.truetype(font_path, font_size) if font_path else ImageFont.load_default()
        bbox = draw.textbbox((0, 0), text, font=font)
        tw, th = bbox[2]-bbox[0], bbox[3]-bbox[1]
        pad = 6
        draw.rounded_rectangle([x-pad, y-2, x+tw+pad, y+th+4], radius=4, fill=color)
        draw.text((x, y), text, fill=C_BG, font=font)


# ── SCENE TEMPLATES (adaptados para dual Cairo/Pillow) ──────

def scene_combat(data, frame_idx):
    t = frame_idx / N_FRAMES
    is_cairo = HAS_CAIRO
    if is_cairo:
        surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
        ctx = cairo.Context(surf)
        ctx.set_source_rgb(C_BG[0]/255, C_BG[1]/255, C_BG[2]/255)
        ctx.paint()
        sc = (surf, ctx)
    else:
        img = Image.new("RGB", (W, H), C_BG)
        from PIL import ImageDraw as ID
        sc = (img, ID.Draw(img))

    font_path = _get_font(12)
    draw_ground(sc, is_cairo)
    ground_y = H - 50

    px = 140 + int(5*math.sin(t*math.pi*2))
    draw_character(sc, is_cairo, px, ground_y, C_PLAYER, 1.0, True)
    ex = 500 + int(3*math.sin(t*math.pi*2.3))
    draw_character(sc, is_cairo, ex, ground_y, C_ENEMY, 0.9, False)

    draw_health_bar(sc, is_cairo, px-30, ground_y-60, 60, int(100*(1-t*0.7)), 100)
    draw_health_bar(sc, is_cairo, ex-30, ground_y-60, 60, int(100*(0.4+t*0.3)), 100)

    if 0.2 < t < 0.6:
        dmg_y = int(ground_y - 80 - 30*(t-0.2))
        alpha_dmg = 1 - abs(t-0.4)*3
        if alpha_dmg > 0:
            c = _alpha(C_DAMAGE, alpha_dmg)
            draw_text(sc, is_cairo, "-15", px-10, dmg_y, font_path, 20, c)

    name = data.get("name", "?").replace("_", " ").title()
    draw_text(sc, is_cairo, name, W//2, 18, font_path, 20, C_ACCENT)
    draw_text(sc, is_cairo, "%s / %s" % (data.get("verbo_pt",""), data.get("verbo_en","")),
              W//2, 42, font_path, 11, C_SUBTEXT)

    custo = data.get("custo", "leve")
    nivel = data.get("nivel", "basico")
    custo_c = {"leve": (80,200,120), "medio": (220,180,60), "pesado": (220,80,80)}.get(custo, C_SUBTEXT)
    nivel_c = {"basico": (140,200,255), "intermediario": (180,160,255), "avancado": (255,180,100)}.get(nivel, C_SUBTEXT)
    draw_badge(sc, is_cairo, custo.upper(), W//2-90, 56, custo_c, font_path)
    draw_badge(sc, is_cairo, nivel.upper(), W//2+20, 56, nivel_c, font_path)

    return sc, is_cairo


def scene_movement(data, frame_idx):
    t = frame_idx / N_FRAMES
    is_cairo = HAS_CAIRO
    if is_cairo:
        surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
        ctx = cairo.Context(surf)
        ctx.set_source_rgb(C_BG[0]/255, C_BG[1]/255, C_BG[2]/255)
        ctx.paint()
        sc = (surf, ctx)
    else:
        img = Image.new("RGB", (W, H), C_BG)
        from PIL import ImageDraw as ID
        sc = (img, ID.Draw(img))

    font_path = _get_font(12)
    draw_ground(sc, is_cairo)
    ground_y = H - 50

    progress = _ease_in_out((t * 1.5) % 1.0)
    px = 80 + int(progress * 480)
    for i in range(5):
        rx = px - (i+1)*20
        alpha = 0.3 - i*0.05
        if alpha > 0 and rx > 60:
            draw_character(sc, is_cairo, rx, ground_y, _alpha(C_PLAYER, alpha), 0.7, True)
    draw_character(sc, is_cairo, px, ground_y, C_PLAYER, 1.0, True)

    name = data.get("name", "?").replace("_", " ").title()
    draw_text(sc, is_cairo, name, W//2, 18, font_path, 20, C_ACCENT)
    draw_text(sc, is_cairo, "%s / %s" % (data.get("verbo_pt",""), data.get("verbo_en","")),
              W//2, 42, font_path, 11, C_SUBTEXT)

    return sc, is_cairo


def scene_projectile(data, frame_idx):
    t = frame_idx / N_FRAMES
    is_cairo = HAS_CAIRO
    if is_cairo:
        surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
        ctx = cairo.Context(surf)
        ctx.set_source_rgb(C_BG[0]/255, C_BG[1]/255, C_BG[2]/255)
        ctx.paint()
        sc = (surf, ctx)
    else:
        img = Image.new("RGB", (W, H), C_BG)
        from PIL import ImageDraw as ID
        sc = (img, ID.Draw(img))

    font_path = _get_font(12)
    draw_ground(sc, is_cairo)
    ground_y = H - 50

    draw_character(sc, is_cairo, 120, ground_y, C_PLAYER, 1.0, True)
    draw_character(sc, is_cairo, 520, ground_y, C_ENEMY, 0.8, False)

    proj_t = (t * 1.2) % 1.0
    proj_x = 130 + int(proj_t * 380)
    proj_y = ground_y - 40 - int(30 * math.sin(proj_t * math.pi))
    if proj_t < 0.95:
        draw_projectile(sc, is_cairo, proj_x, proj_y, C_PROJECTILE, 5)

    if proj_t >= 0.85:
        impact_t = (proj_t - 0.85) / 0.15
        for i in range(8):
            angle = i * math.pi/4
            dist = impact_t * 25
            pxi = 520 + int(math.cos(angle)*dist)
            pyi = ground_y - 30 + int(math.sin(angle)*dist)
            alpha_i = (1-impact_t) * 0.8
            if alpha_i > 0:
                draw_particle(sc, is_cairo, pxi, pyi, C_PROJECTILE, 3, alpha_i)

    hp = 100 if proj_t < 0.85 else 100 - int(40 * (proj_t-0.85)/0.15)
    draw_health_bar(sc, is_cairo, 490, ground_y-60, 60, max(0, hp), 100)

    name = data.get("name", "?").replace("_", " ").title()
    draw_text(sc, is_cairo, name, W//2, 18, font_path, 20, C_ACCENT)

    return sc, is_cairo


def scene_abstract(data, frame_idx):
    t = frame_idx / N_FRAMES
    is_cairo = HAS_CAIRO
    if is_cairo:
        surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
        ctx = cairo.Context(surf)
        ctx.set_source_rgb(C_BG[0]/255, C_BG[1]/255, C_BG[2]/255)
        ctx.paint()
        sc = (surf, ctx)
    else:
        img = Image.new("RGB", (W, H), C_BG)
        from PIL import ImageDraw as ID
        sc = (img, ID.Draw(img))

    font_path = _get_font(12)
    cx, cy = W//2, H//2 - 10

    for i in range(3):
        angle = t * math.pi * 2 + i * math.pi * 2/3
        r = 80 + int(10*math.sin(t*math.pi*3 + i))
        ox = cx + int(math.cos(angle)*r)
        oy = cy + int(math.sin(angle)*r)
        size = 6 + i*2
        draw_particle(sc, is_cairo, ox, oy, C_ACCENT, size, 0.4+i*0.2)

    name = data.get("name", "?").replace("_", " ").title()
    draw_text(sc, is_cairo, name, cx, cy-10, font_path, 28, C_ACCENT)
    verb_line = "%s / %s" % (data.get("verbo_pt",""), data.get("verbo_en",""))
    draw_text(sc, is_cairo, verb_line, cx, cy+30, font_path, 14, C_SUBTEXT)

    return sc, is_cairo


# ── MAPEAMENTO ──────────────────────────────────────────────

TEMPLATE_MAP = {
    "health": "combat", "hitbox": "combat", "hurtbox": "combat",
    "knockback": "combat", "critical_hit": "combat", "damage_over_time": "combat",
    "area_damage": "combat", "status_effect": "combat",
    "projectile": "projectile", "homing_projectile": "projectile",
    "beam_laser": "projectile", "hitscan": "projectile",
    "fire_rate": "projectile", "fire_mode": "projectile",
    "spread": "projectile", "recoil": "projectile",
    "turret_aim": "projectile", "auto_aim": "projectile", "crosshair": "projectile",
    "player_controller": "movement", "player_topdown": "movement",
    "dash": "movement", "double_jump": "movement", "wall_slide": "movement",
    "grid_movement": "movement", "moving_platform": "movement",
    "follow_path": "movement", "teleport": "movement",
    "enemy_chase": "movement", "enemy_patrol": "movement",
    "line_of_sight": "movement", "spawner_wave": "movement",
    "camera_follow": "movement", "camera_shake": "movement",
    "screen_shake": "movement", "particle_impact": "movement",
    "dialogue": "movement", "interactable": "movement",
    "collectable": "movement", "inventory": "movement",
    "save_load": "abstract", "settings": "abstract",
    "audio_manager": "abstract", "input_manager": "abstract",
}

SCENE_FNS = {
    "combat": scene_combat,
    "movement": scene_movement,
    "projectile": scene_projectile,
    "abstract": scene_abstract,
}


def get_template(name):
    return TEMPLATE_MAP.get(name, "abstract")


# ── ENCODERS ────────────────────────────────────────────────

def encode_gifski(frames_dir, output_path, fps=FPS):
    """Encoder gifski: máxima qualidade GIF."""
    gifski_bin = shutil.which("gifski") or "gifski"
    frame_files = sorted(Path(frames_dir).glob("frame_*.png"))

    # gifski: arquivos POSICIONAIS, não -f
    cmd = [
        gifski_bin,
        "-o", output_path,
        "-r", str(fps),
        "--width", str(W),
        "--height", str(H),
        "--quality", "90",
    ] + [str(f) for f in frame_files]

    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=120)
        return True
    except subprocess.CalledProcessError as e:
        print("    gifski error: %s" % (e.stderr[:200] if e.stderr else str(e)))
        return False
    except FileNotFoundError:
        print("    gifski nao encontrado")
        return False


def _find_bin(name, fallback=None):
    """Encontra binário no PATH ou em locais conhecidos."""
    found = shutil.which(name)
    if found:
        return found
    # Winget paths
    for base in [os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\WinGet\Packages"),
                 r"C:\Program Files", r"C:\ProgramData"]:
        if os.path.isdir(base):
            for root, dirs, files in os.walk(base):
                if name + ".exe" in files:
                    return os.path.join(root, name + ".exe")
    return fallback or name


def encode_mp4(frames_dir, output_path, fps=FPS):
    """Encoder MP4 via FFmpeg libx264."""
    ffmpeg = _find_bin("ffmpeg")
    cmd = [
        ffmpeg, "-y",
        "-framerate", str(fps),
        "-i", os.path.join(frames_dir, "frame_%04d.png"),
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-preset", "medium",
        "-crf", "23",
        "-movflags", "+faststart",
        output_path
    ]
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=120)
        return True
    except subprocess.CalledProcessError as e:
        print("    ffmpeg mp4 error: %s" % (e.stderr[:200] if e.stderr else str(e)))
        return False
    except FileNotFoundError:
        print("    ffmpeg nao encontrado")
        return False


def encode_webp(frames_dir, output_path, fps=FPS):
    """Encoder WebP animado via FFmpeg."""
    ffmpeg = _find_bin("ffmpeg")
    cmd = [
        ffmpeg, "-y",
        "-framerate", str(fps),
        "-i", os.path.join(frames_dir, "frame_%04d.png"),
        "-c:v", "libwebp",
        "-lossless", "0",
        "-quality", "85",
        "-loop", "0",
        output_path
    ]
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=120)
        return True
    except subprocess.CalledProcessError as e:
        print("    ffmpeg webp error: %s" % (e.stderr[:200] if e.stderr else str(e)))
        return False
    except FileNotFoundError:
        print("    ffmpeg nao encontrado")
        return False


def encode_gif_pillow_fallback(frames_dir, output_path, fps=FPS):
    """Fallback: Pillow GIF (quando gifski falha)."""
    from PIL import Image as PILImg
    frame_files = sorted(Path(frames_dir).glob("frame_*.png"))
    if not frame_files:
        return False
    images = [PILImg.open(str(f)) for f in frame_files]
    duration = 1000 // fps
    images[0].save(
        output_path, save_all=True, append_images=images[1:],
        duration=duration, loop=0, optimize=True
    )
    size_kb = os.path.getsize(output_path) / 1024
    return True


# ── VALIDADOR AUTOMÁTICO ────────────────────────────────────

def validate_output(gif_path, expected_frames=N_FRAMES, max_size_kb=500):
    """Valida qualidade do GIF gerado."""
    results = {}
    try:
        img = Image.open(gif_path)
        results["formato"] = img.format == "GIF"
        results["resolucao"] = img.size == (W, H)
        results["frames"] = img.n_frames >= expected_frames * 0.95
        results["loop"] = img.info.get("loop", 1) == 0
        results["tamanho_kb"] = os.path.getsize(gif_path) / 1024 < max_size_kb
        results["arquivo_existe"] = True
    except Exception as e:
        return {"erro": str(e)}

    return results


# ── GERAÇÃO PRINCIPAL ───────────────────────────────────────

def get_behavior_dirs():
    return sorted([d for d in os.listdir(BEHAVIORS_ROOT)
                   if os.path.isdir(os.path.join(BEHAVIORS_ROOT, d))
                   and os.path.isfile(os.path.join(BEHAVIORS_ROOT, d, "behavior.json"))])


def load_behavior(name):
    with open(os.path.join(BEHAVIORS_ROOT, name, "behavior.json"), "r", encoding="utf-8") as f:
        return json.load(f)


def save_behavior(name, data):
    with open(os.path.join(BEHAVIORS_ROOT, name, "behavior.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def generate_preview(name, data, formats=("gif",), tmpdir=None):
    """Gera previews multi-formato para um behavior."""
    tpl = get_template(name)
    if tpl not in SCENE_FNS:
        tpl = "abstract"
    scene_fn = SCENE_FNS[tpl]

    # Fase 1: Renderizar frames PNG
    frame_dir = os.path.join(tmpdir, name)
    os.makedirs(frame_dir, exist_ok=True)

    for i in range(N_FRAMES):
        sc, is_cairo = scene_fn(data, i)
        frame_path = os.path.join(frame_dir, "frame_%04d.png" % i)
        if is_cairo:
            surf, ctx = sc
            surf.write_to_png(frame_path)
        else:
            sc[0].save(frame_path, "PNG")

    results = {}

    # Fase 2: Encoders
    if "gif" in formats:
        gif_path = os.path.join(BEHAVIORS_ROOT, name, "preview.gif")
        gif_ok = encode_gifski(frame_dir, gif_path)
        if not gif_ok:
            gif_ok = encode_gif_pillow_fallback(frame_dir, gif_path)
        results["gif"] = {"ok": gif_ok, "size_kb": os.path.getsize(gif_path)/1024 if gif_ok else 0}

    if "mp4" in formats:
        mp4_path = os.path.join(BEHAVIORS_ROOT, name, "preview.mp4")
        mp4_ok = encode_mp4(frame_dir, mp4_path)
        results["mp4"] = {"ok": mp4_ok, "size_kb": os.path.getsize(mp4_path)/1024 if mp4_ok else 0}
        if mp4_ok:
            data["preview_mp4"] = "preview.mp4"

    if "webp" in formats:
        webp_path = os.path.join(BEHAVIORS_ROOT, name, "preview.webp")
        webp_ok = encode_webp(frame_dir, webp_path)
        results["webp"] = {"ok": webp_ok, "size_kb": os.path.getsize(webp_path)/1024 if webp_ok else 0}
        if webp_ok:
            data["preview_webp"] = "preview.webp"

    # Fase 3: Validação
    if "gif" in formats and results.get("gif", {}).get("ok"):
        gif_path = os.path.join(BEHAVIORS_ROOT, name, "preview.gif")
        results["validation"] = validate_output(gif_path)

    # Atualizar metadata
    data["preview_gif"] = "preview.gif"
    data["preview_type"] = "visual"
    save_behavior(name, data)

    # Limpar frames temporários
    shutil.rmtree(frame_dir, ignore_errors=True)

    return results


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Pipeline Enterprise de Previews v2.0")
    parser.add_argument("--batch", type=int, default=0)
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--format", default="gif", help="gif,mp4,webp (separados por vírgula)")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    formats = [f.strip() for f in args.format.split(",")]

    all_names = get_behavior_dirs()
    if args.batch > 0:
        batch_size = 20
        start = (args.batch - 1) * batch_size
        end = min(start + batch_size, len(all_names))
        batch = all_names[start:end]
    else:
        batch = all_names

    print("=" * 60)
    print("PIPELINE ENTERPRISE v2.0 — %d behaviors" % len(batch))
    print("  Cairo: %s | gifski: %s | FFmpeg: %s" % (
        "SIM" if HAS_CAIRO else "NAO",
        "SIM" if shutil.which("gifski") else "NAO",
        "SIM" if shutil.which("ffmpeg") else "NAO"))
    print("  Formatos: %s | %dx%d @ %dfps" % (",".join(formats), W, H, FPS))
    print("=" * 60)

    if args.dry_run:
        for name in batch:
            print("  [DRY] %-35s → %s" % (name, get_template(name)))
        return

    with tempfile.TemporaryDirectory() as tmpdir:
        stats = {"ok": 0, "erro": 0, "gif_total_kb": 0, "mp4_total_kb": 0, "webp_total_kb": 0}
        for name in batch:
            try:
                data = load_behavior(name)
                results = generate_preview(name, data, formats=formats, tmpdir=tmpdir)
                gif_sz = results.get("gif", {}).get("size_kb", 0)
                mp4_sz = results.get("mp4", {}).get("size_kb", 0)
                webp_sz = results.get("webp", {}).get("size_kb", 0)
                val = results.get("validation", {})
                vstatus = "PASS" if all(val.values()) else "FAIL" if val else "N/A"

                parts = ["%-35s" % name]
                if "gif" in formats:
                    parts.append("GIF:%.0fKB" % gif_sz)
                if "mp4" in formats:
                    parts.append("MP4:%.0fKB" % mp4_sz)
                if "webp" in formats:
                    parts.append("WEBP:%.0fKB" % webp_sz)
                parts.append("[%s]" % vstatus)

                print("  " + " ".join(parts))
                stats["ok"] += 1
                stats["gif_total_kb"] += gif_sz
                stats["mp4_total_kb"] += mp4_sz
                stats["webp_total_kb"] += webp_sz
            except Exception as e:
                print("  [ERRO] %s: %s" % (name, e))
                stats["erro"] += 1

        print("\nRESUMO: %d OK, %d erros" % (stats["ok"], stats["erro"]))
        if stats["ok"] > 0 and "gif" in formats:
            print("  GIF  medio: %.0fKB" % (stats["gif_total_kb"]/stats["ok"]))
        if stats["ok"] > 0 and "mp4" in formats:
            print("  MP4  medio: %.0fKB" % (stats["mp4_total_kb"]/stats["ok"]))
        if stats["ok"] > 0 and "webp" in formats:
            print("  WebP medio: %.0fKB" % (stats["webp_total_kb"]/stats["ok"]))


if __name__ == "__main__":
    main()
