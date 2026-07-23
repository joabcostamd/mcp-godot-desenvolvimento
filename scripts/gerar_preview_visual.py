#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""sota_1.3 — Gerador Visual Enterprise de previews para behaviors.

Renderiza animações procedurais de alta qualidade que DEMONSTRAM visualmente
o que cada behavior faz. Usa primitivas de jogo (personagens, projéteis,
partículas, UI, câmera) desenhadas com Pillow.

Qualidade: 640x360, 15fps, 4 segundos (60 frames), alvo <500KB.
Substitui o modo abstract-only por templates visuais por categoria.

Uso: python scripts/gerar_preview_visual.py [--batch N] [--all]
"""

import json
import math
import os
import sys
from PIL import Image, ImageDraw, ImageFont

BEHAVIORS_ROOT = os.path.join(os.path.dirname(__file__), "..", "behaviors")

# ── CONFIG ──────────────────────────────────────────────────
W, H = 640, 360
FPS = 15
DURATION = 4
N_FRAMES = FPS * DURATION  # 60
FRAME_MS = 1000 // FPS     # 66ms

# ── PALETA PROFESSIONAL ─────────────────────────────────────
C_BG        = (18, 22, 28)      # fundo escuro
C_GROUND    = (40, 48, 56)      # chão
C_GROUND_LINE = (60, 70, 82)    # linha do chão
C_PLAYER    = (80, 180, 255)    # azul jogador
C_ENEMY     = (255, 90, 90)     # vermelho inimigo
C_HEALTH_BG = (50, 50, 55)      # fundo barra vida
C_HEALTH    = (80, 200, 100)    # verde vida
C_DAMAGE    = (255, 70, 70)     # vermelho dano
C_PROJECTILE = (255, 220, 80)   # amarelo projétil
C_PARTICLE  = (255, 200, 100)   # laranja partícula
C_SHIELD    = (100, 200, 255)   # azul escudo
C_TEXT      = (230, 235, 240)   # texto claro
C_SUBTEXT   = (140, 150, 165)   # texto secundário
C_ACCENT    = (80, 180, 255)    # destaque
C_WHITE     = (255, 255, 255)
C_ITEM      = (255, 215, 0)     # dourado item
C_XP        = (180, 130, 255)   # roxo XP
C_UI_BG     = (30, 35, 45, 200) # fundo UI semi-transparente
C_DIALOGUE_BG = (20, 25, 35)    # fundo balão
C_DIALOGUE_BORDER = (60, 70, 85) # borda balão

# ── FUNÇÕES AUXILIARES ─────────────────────────────────────

def _blend(c1, c2, t):
    return tuple(int(c1[i] + (c2[i]-c1[i])*t) for i in range(3))

def _alpha(c, a):
    return tuple(int(c[i]*a + C_BG[i]*(1-a)) for i in range(3))

def _ease_out(t):
    return 1 - (1-t)**3

def _ease_in_out(t):
    return t*t*(3 - 2*t)

def _bounce(t):
    return abs(math.sin(t * math.pi * 3) * (1-t))

def _pulse(t, speed=2):
    return 0.5 + 0.5 * math.sin(t * math.pi * speed)

# ── PRIMITIVAS DE DESENHO ──────────────────────────────────

def draw_ground(draw, y=None):
    """Chão com linha de referência."""
    gy = y if y else H - 50
    draw.rectangle([0, gy, W, H], fill=C_GROUND)
    draw.line([0, gy, W, gy], fill=C_GROUND_LINE, width=2)

def draw_character(draw, x, y, color, scale=1.0, facing_right=True):
    """Personagem estilizado: corpo retangular + cabeça circular + olhos."""
    s = int(16 * scale)
    # Corpo
    bx, by = x - s//2, y - s*2
    draw.rounded_rectangle([bx, by, bx+s, by+s*2], radius=s//3, fill=color)
    # Cabeça
    head_r = int(s * 0.7)
    draw.ellipse([x-head_r, by-head_r*2+2, x+head_r, by+2], fill=_blend(color, C_WHITE, 0.15))
    # Olhos
    eye_r = max(2, head_r//3)
    eye_y = by - head_r
    if facing_right:
        draw.ellipse([x+2, eye_y-eye_r, x+2+eye_r*2, eye_y+eye_r], fill=C_BG)
    else:
        draw.ellipse([x-2-eye_r*2, eye_y-eye_r, x-2, eye_y+eye_r], fill=C_BG)

def draw_health_bar(draw, x, y, w, current, maximum, show_text=True):
    """Barra de vida horizontal."""
    h = 8
    draw.rectangle([x, y, x+w, y+h], fill=C_HEALTH_BG)
    pct = max(0, min(1, current/maximum))
    bar_w = int(w * pct)
    if bar_w > 0:
        color = C_HEALTH if pct > 0.5 else C_DAMAGE if pct > 0.25 else (255, 50, 50)
        draw.rectangle([x, y, x+bar_w, y+h], fill=color)
    draw.rectangle([x, y, x+w, y+h], outline=(100,110,125), width=1)

def draw_projectile(draw, x, y, color=C_PROJECTILE, size=5, trail=False):
    """Projétil com rastro opcional."""
    draw.ellipse([x-size, y-size//2, x+size, y+size//2], fill=color)
    if trail:
        for i in range(3):
            alpha = 1 - i*0.3
            tx = x - (i+1)*size
            draw.ellipse([tx-size//2, y-size//4, tx+size//2, y+size//4],
                         fill=_alpha(color, alpha*0.5))

def draw_particle(draw, x, y, color, size, alpha):
    """Partícula com alpha."""
    c = _alpha(color, alpha)
    draw.ellipse([x-size, y-size, x+size, y+size], fill=c)

def draw_text_label(draw, text, x, y, font, color=C_TEXT, center=True):
    """Label de texto centralizado."""
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    if center:
        draw.text((x-tw//2, y), text, fill=color, font=font)
    else:
        draw.text((x, y), text, fill=color, font=font)
    return tw

def draw_badge(draw, text, x, y, color, font):
    """Badge arredondado."""
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2]-bbox[0], bbox[3]-bbox[1]
    pad = 6
    draw.rounded_rectangle([x-pad, y-2, x+tw+pad, y+th+4], radius=4, fill=color)
    draw.text((x, y), text, fill=C_BG, font=font)

def draw_dialog_box(draw, x, y, w, text, font, frame_progress):
    """Balão de diálogo com texto aparecendo."""
    h = 50
    draw.rounded_rectangle([x, y, x+w, y+h], radius=8, fill=C_DIALOGUE_BG, outline=C_DIALOGUE_BORDER, width=2)
    # Triângulo do balão
    draw.polygon([(x+20, y+h), (x+30, y+h+10), (x+40, y+h)], fill=C_DIALOGUE_BG)
    draw.line([(x+20, y+h), (x+30, y+h+10), (x+40, y+h)], fill=C_DIALOGUE_BORDER, width=2)
    # Texto com revelação progressiva
    visible_chars = int(len(text) * min(1, frame_progress * 2))
    visible_text = text[:visible_chars]
    bbox = draw.textbbox((0, 0), visible_text, font=font)
    draw.text((x+12, y+12), visible_text, fill=C_TEXT, font=font)

def _get_font(size):
    for fp in ["C:/Windows/Fonts/consola.ttf", "C:/Windows/Fonts/segoeui.ttf",
               "C:/Windows/Fonts/arial.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]:
        if os.path.isfile(fp):
            try: return ImageFont.truetype(fp, size)
            except: continue
    return ImageFont.load_default()

# ── SCENE TEMPLATES ────────────────────────────────────────

def scene_combat(data, frame_idx, n_frames):
    """Template COMBATE: personagem + inimigo + barras de vida + dano."""
    t = frame_idx / n_frames
    img = Image.new("RGB", (W, H), C_BG)
    draw = ImageDraw.Draw(img)
    font_sm = _get_font(11)
    font_md = _get_font(16)
    font_lg = _get_font(20)

    draw_ground(draw)
    ground_y = H - 50

    # Jogador à esquerda
    px = 140 + int(5*math.sin(t*math.pi*2))
    py = ground_y
    draw_character(draw, px, py, C_PLAYER, 1.0, True)

    # Inimigo à direita
    ex = 500 + int(3*math.sin(t*math.pi*2.3))
    ey = ground_y
    draw_character(draw, ex, ey, C_ENEMY, 0.9, False)

    # Barras de vida
    draw_health_bar(draw, px-30, py-60, 60, int(100*(1-t*0.7)), 100)
    draw_health_bar(draw, ex-30, ey-60, 60, int(100*(0.4+t*0.3)), 100)

    # Dano flutuante
    if 0.2 < t < 0.6:
        dmg_y = py - 80 - int(30*(t-0.2))
        alpha = 1 - abs(t-0.4)*3
        if alpha > 0:
            c = _alpha(C_DAMAGE, alpha)
            draw_text_label(draw, "-15", px-10, int(dmg_y), font_lg, c)

    # Nome + badges no topo
    name = data.get("name", "?").replace("_", " ").title()
    draw_text_label(draw, name, W//2, 8, font_lg, C_ACCENT)
    draw_text_label(draw, "%s / %s" % (data.get("verbo_pt",""), data.get("verbo_en","")),
                    W//2, 34, font_sm, C_SUBTEXT)

    # Badges
    custo = data.get("custo", "leve")
    nivel = data.get("nivel", "basico")
    custo_c = {"leve": (80,200,120), "medio": (220,180,60), "pesado": (220,80,80)}.get(custo, C_SUBTEXT)
    nivel_c = {"basico": (140,200,255), "intermediario": (180,160,255), "avancado": (255,180,100)}.get(nivel, C_SUBTEXT)
    draw_badge(draw, custo.upper(), W//2-90, 55, custo_c, font_sm)
    draw_badge(draw, nivel.upper(), W//2+20, 55, nivel_c, font_sm)

    return img


def scene_movement(data, frame_idx, n_frames):
    """Template MOVIMENTO: personagem se movendo com rastro."""
    t = frame_idx / n_frames
    img = Image.new("RGB", (W, H), C_BG)
    draw = ImageDraw.Draw(img)
    font_sm = _get_font(11)
    font_lg = _get_font(20)

    draw_ground(draw)
    ground_y = H - 50

    # Personagem se move da esquerda para direita com easing
    progress = _ease_in_out((t * 1.5) % 1.0)
    px = 80 + int(progress * 480)
    py = ground_y
    # Rastro
    for i in range(5):
        rx = px - (i+1)*20
        alpha = 0.3 - i*0.05
        if alpha > 0 and rx > 60:
            draw_character(draw, rx, py, _alpha(C_PLAYER, alpha), 0.7, True)
    draw_character(draw, px, py, C_PLAYER, 1.0, True)

    # Partículas de poeira nos pés
    for i in range(3):
        px_i = px - 10 + i*8 + int(5*math.sin(t*20 + i))
        py_i = py + 2 + int(3*math.cos(t*15 + i))
        draw_particle(draw, px_i, py_i, C_GROUND_LINE, 2, 0.6*_pulse(t, 8))

    # Nome + badges
    name = data.get("name", "?").replace("_", " ").title()
    draw_text_label(draw, name, W//2, 8, font_lg, C_ACCENT)
    draw_text_label(draw, "%s / %s" % (data.get("verbo_pt",""), data.get("verbo_en","")),
                    W//2, 34, font_sm, C_SUBTEXT)

    return img


def scene_projectile(data, frame_idx, n_frames):
    """Template PROJÉTIL: disparo cruzando a tela + impacto."""
    t = frame_idx / n_frames
    img = Image.new("RGB", (W, H), C_BG)
    draw = ImageDraw.Draw(img)
    font_sm = _get_font(11)
    font_lg = _get_font(20)

    draw_ground(draw)
    ground_y = H - 50

    # Atirador à esquerda
    draw_character(draw, 120, ground_y, C_PLAYER, 1.0, True)
    # Alvo à direita
    draw_character(draw, 520, ground_y, C_ENEMY, 0.8, False)

    # Projétil voando
    proj_t = (t * 1.2) % 1.0
    proj_x = 130 + int(proj_t * 380)
    proj_y = ground_y - 40 - int(30 * math.sin(proj_t * math.pi))
    if proj_t < 0.95:
        draw_projectile(draw, proj_x, proj_y, C_PROJECTILE, 5, trail=True)

    # Impacto no alvo
    if proj_t >= 0.85:
        impact_t = (proj_t - 0.85) / 0.15
        for i in range(8):
            angle = i * math.pi/4
            dist = impact_t * 25
            px_i = 520 + int(math.cos(angle)*dist)
            py_i = ground_y - 30 + int(math.sin(angle)*dist)
            alpha = (1-impact_t) * 0.8
            if alpha > 0:
                draw_particle(draw, px_i, py_i, C_PROJECTILE, 3, alpha)

    # Barra de vida do alvo (diminui no impacto)
    hp = 100 if proj_t < 0.85 else 100 - int(40 * (proj_t-0.85)/0.15)
    draw_health_bar(draw, 490, ground_y-60, 60, max(0, hp), 100)

    # Nome + badges
    name = data.get("name", "?").replace("_", " ").title()
    draw_text_label(draw, name, W//2, 8, font_lg, C_ACCENT)
    custo = data.get("custo", "leve")
    nivel = data.get("nivel", "basico")
    custo_c = {"leve": (80,200,120), "medio": (220,180,60), "pesado": (220,80,80)}.get(custo, C_SUBTEXT)
    nivel_c = {"basico": (140,200,255), "intermediario": (180,160,255), "avancado": (255,180,100)}.get(nivel, C_SUBTEXT)
    draw_badge(draw, custo.upper(), W//2-90, 55, custo_c, font_sm)
    draw_badge(draw, nivel.upper(), W//2+20, 55, nivel_c, font_sm)

    return img


def scene_ai_enemy(data, frame_idx, n_frames):
    """Template IA/INIMIGO: perseguição, patrulha, detecção."""
    t = frame_idx / n_frames
    img = Image.new("RGB", (W, H), C_BG)
    draw = ImageDraw.Draw(img)
    font_sm = _get_font(11)
    font_lg = _get_font(20)

    draw_ground(draw)
    ground_y = H - 50

    # Jogador se move
    px = 500 - int(t * 350)
    py = ground_y
    draw_character(draw, px, py, C_PLAYER, 0.8, t < 0.5)

    # Inimigo persegue com delay
    chase_t = max(0, t - 0.15)
    ex = 500 - int(chase_t * 300)
    ey = ground_y
    draw_character(draw, ex, ey, C_ENEMY, 0.85, False)

    # Cone de visão (line of sight)
    if t < 0.8:
        los_alpha = _pulse(t, 3) * 0.3
        los_color = _alpha((255,255,100), los_alpha)
        draw.polygon([
            (ex-10, ey-30), (ex-10+60, ey-30-50), (ex-10+60, ey-30+50)
        ], fill=los_color)

    # Nome + badges
    name = data.get("name", "?").replace("_", " ").title()
    draw_text_label(draw, name, W//2, 8, font_lg, C_ACCENT)

    return img


def scene_camera(data, frame_idx, n_frames):
    """Template CÂMERA: viewport com shake, zoom, follow."""
    t = frame_idx / n_frames
    img = Image.new("RGB", (W, H), C_BG)
    draw = ImageDraw.Draw(img)
    font_sm = _get_font(11)
    font_lg = _get_font(20)

    # Viewport simulada (retângulo interno)
    shake_x = int(8 * math.sin(t * math.pi * 8) * (1-t*0.3))
    shake_y = int(6 * math.cos(t * math.pi * 7) * (1-t*0.3))
    vp_margin = 60
    vx, vy = vp_margin + shake_x, 50 + shake_y
    vw, vh = W - vp_margin*2, H - 120

    # Fundo da viewport (céu + gradiente)
    for i in range(vh):
        ratio = i / vh
        color = _blend((40, 50, 70), (20, 25, 35), ratio)
        draw.rectangle([vx, vy+i, vx+vw, vy+i+1], fill=color)

    # Chão na viewport
    draw.rectangle([vx, vy+vh-30, vx+vw, vy+vh], fill=C_GROUND)
    draw.line([vx, vy+vh-30, vx+vw, vy+vh-30], fill=C_GROUND_LINE, width=1)

    # Personagem na viewport
    cx = vx + vw//2 + int(15*math.sin(t*math.pi*3))
    cy = vy + vh - 30
    draw_character(draw, cx, cy, C_PLAYER, 0.7, True)

    # Borda da viewport
    draw.rectangle([vx, vy, vx+vw, vy+vh], outline=(80, 90, 105), width=2)

    # Nome + badges
    name = data.get("name", "?").replace("_", " ").title()
    draw_text_label(draw, name, W//2, 8, font_lg, C_ACCENT)

    return img


def scene_feedback(data, frame_idx, n_frames):
    """Template FEEDBACK: screen shake, flash, partículas."""
    t = frame_idx / n_frames
    img = Image.new("RGB", (W, H), C_BG)
    draw = ImageDraw.Draw(img)
    font_sm = _get_font(11)
    font_lg = _get_font(20)

    # Efeito de flash na tela
    flash_t = (t * 2) % 1.0
    if flash_t < 0.3:
        flash_alpha = (1 - flash_t/0.3) * 0.5
        flash_c = _alpha(C_WHITE, flash_alpha)
        draw.rectangle([0, 0, W, H], fill=flash_c)

    # Partículas explodindo do centro
    center_x, center_y = W//2, H//2
    for i in range(20):
        angle = i * math.pi/10 + t * 2
        dist = 50 + 80 * ((t * 3 + i*0.1) % 1.0)
        px = center_x + int(math.cos(angle) * dist)
        py = center_y + int(math.sin(angle) * dist)
        alpha = max(0, 1 - ((t*3 + i*0.1) % 1.0))
        if alpha > 0:
            draw_particle(draw, px, py, C_PARTICLE, 4, alpha * 0.7)

    # Nome + badges
    name = data.get("name", "?").replace("_", " ").title()
    draw_text_label(draw, name, W//2, 8, font_lg, C_ACCENT)

    return img


def scene_dialogue(data, frame_idx, n_frames):
    """Template DIÁLOGO/UI: balão de fala, interação."""
    t = frame_idx / n_frames
    img = Image.new("RGB", (W, H), C_BG)
    draw = ImageDraw.Draw(img)
    font_sm = _get_font(11)
    font_md = _get_font(14)
    font_lg = _get_font(20)

    draw_ground(draw)
    ground_y = H - 50

    # NPC
    draw_character(draw, 180, ground_y, (150, 120, 200), 1.0, False)
    # Player
    draw_character(draw, 460, ground_y, C_PLAYER, 0.9, True)

    # Balão de diálogo
    dialog_text = data.get("description_pt", "Interagir...")[:80]
    show_progress = min(1, t * 2.5)
    draw_dialog_box(draw, 200, ground_y-120, 240, dialog_text, font_sm, show_progress)

    # Ícone de interação pulsando
    if t > 0.6:
        ico_alpha = _pulse(t, 6)
        ico_y = ground_y - 90 + int(3*math.sin(t*15))
        ico_c = _alpha(C_ACCENT, ico_alpha)
        draw_text_label(draw, "[E]", 320, int(ico_y), font_lg, ico_c)

    # Nome + badges
    name = data.get("name", "?").replace("_", " ").title()
    draw_text_label(draw, name, W//2, 8, font_lg, C_ACCENT)

    return img


def scene_system(data, frame_idx, n_frames):
    """Template SISTEMA: save, load, dados fluindo."""
    t = frame_idx / n_frames
    img = Image.new("RGB", (W, H), C_BG)
    draw = ImageDraw.Draw(img)
    font_sm = _get_font(11)
    font_lg = _get_font(20)

    # Visualização de dados: barras e ícones
    # Disco de save
    disk_x, disk_y = W//2, H//2 - 20
    draw.ellipse([disk_x-30, disk_y-30, disk_x+30, disk_y+30],
                 outline=C_ACCENT, width=3)
    # Animação de progresso circular
    arc_angle = 360 * ((t * 1.5) % 1.0)
    if arc_angle > 5:
        draw.arc([disk_x-25, disk_y-25, disk_x+25, disk_y+25],
                 0, min(360, arc_angle), fill=C_ACCENT, width=4)

    # Barras de dados
    for i in range(4):
        bar_y = 90 + i * 35
        bar_w = 200 + int(150 * math.sin(t*2 + i))
        draw.rectangle([80, bar_y, 80+bar_w, bar_y+18], fill=_blend(C_ACCENT, C_BG, 0.3))
        draw.rectangle([80, bar_y, 80+bar_w, bar_y+18], outline=C_ACCENT, width=1)
        draw_text_label(draw, "data_%d" % i, 70, bar_y+2, font_sm, C_SUBTEXT, center=False)

    # Nome + badges
    name = data.get("name", "?").replace("_", " ").title()
    draw_text_label(draw, name, W//2, 8, font_lg, C_ACCENT)

    return img


def scene_collectable(data, frame_idx, n_frames):
    """Template COLETÁVEL/ITEM: item brilhando sendo coletado."""
    t = frame_idx / n_frames
    img = Image.new("RGB", (W, H), C_BG)
    draw = ImageDraw.Draw(img)
    font_sm = _get_font(11)
    font_lg = _get_font(20)

    draw_ground(draw)
    ground_y = H - 50

    # Item flutuando
    item_x = W//2 + int(20*math.sin(t*math.pi*2))
    item_y = ground_y - 60 + int(10*math.sin(t*math.pi*3))
    # Brilho pulsante
    glow_r = 18 + int(5*_pulse(t, 4))
    glow_c = _alpha(C_ITEM, 0.3*_pulse(t, 4))
    draw.ellipse([item_x-glow_r, item_y-glow_r, item_x+glow_r, item_y+glow_r], fill=glow_c)
    # Item
    draw.ellipse([item_x-10, item_y-10, item_x+10, item_y+10], fill=C_ITEM)

    # Personagem se aproximando
    px = 80 + int(t * 400) if t < 0.7 else item_x - 40
    py = ground_y
    draw_character(draw, px, py, C_PLAYER, 0.8, True)

    # Coleta (t > 0.7)
    if t > 0.7:
        collect_t = (t - 0.7) / 0.3
        for i in range(6):
            angle = i * math.pi/3
            dist = collect_t * 30
            cx = item_x + int(math.cos(angle)*dist)
            cy = item_y + int(math.sin(angle)*dist)
            alpha = (1-collect_t) * 0.8
            if alpha > 0:
                draw_particle(draw, cx, cy, C_ITEM, 3, alpha)

    # Nome + badges
    name = data.get("name", "?").replace("_", " ").title()
    draw_text_label(draw, name, W//2, 8, font_lg, C_ACCENT)

    return img


def scene_abstract(data, frame_idx, n_frames):
    """Template ABSTRATO: fallback elegante para behaviors sem visual claro."""
    t = frame_idx / n_frames
    img = Image.new("RGB", (W, H), C_BG)
    draw = ImageDraw.Draw(img)
    font_sm = _get_font(11)
    font_md = _get_font(14)
    font_lg = _get_font(22)
    font_xl = _get_font(28)

    # Círculos decorativos orbitando
    cx, cy = W//2, H//2 - 10
    for i in range(3):
        angle = t * math.pi * 2 + i * math.pi * 2/3
        r = 80 + int(10*math.sin(t*math.pi*3 + i))
        ox = cx + int(math.cos(angle)*r)
        oy = cy + int(math.sin(angle)*r)
        size = 6 + i*2
        draw.ellipse([ox-size, oy-size, ox+size, oy+size], fill=_alpha(C_ACCENT, 0.4+i*0.2))

    # Nome central grande
    name = data.get("name", "?").replace("_", " ").title()
    draw_text_label(draw, name, cx, cy-10, font_xl, C_ACCENT)

    # Verbos
    verb_line = "%s / %s" % (data.get("verbo_pt",""), data.get("verbo_en",""))
    draw_text_label(draw, verb_line, cx, cy+30, font_md, C_SUBTEXT)

    # Descrição
    desc = data.get("description_pt", "")[:90]
    if desc:
        draw_text_label(draw, desc, cx, cy+55, font_sm, _alpha(C_TEXT, _pulse(t, 2)))

    # Linha inferior com gêneros
    genres = data.get("genres", [])[:5]
    if genres:
        genre_text = " · ".join(genres)
        draw_text_label(draw, genre_text, cx, H-30, font_sm, C_SUBTEXT)

    # Badges
    custo = data.get("custo", "leve")
    nivel = data.get("nivel", "basico")
    custo_c = {"leve": (80,200,120), "medio": (220,180,60), "pesado": (220,80,80)}.get(custo, C_SUBTEXT)
    nivel_c = {"basico": (140,200,255), "intermediario": (180,160,255), "avancado": (255,180,100)}.get(nivel, C_SUBTEXT)
    draw_badge(draw, custo.upper(), cx-100, 8, custo_c, font_sm)
    draw_badge(draw, nivel.upper(), cx+30, 8, nivel_c, font_sm)

    return img


# ── MAPEAMENTO BEHAVIOR → TEMPLATE ─────────────────────────

TEMPLATE_MAP = {
    # COMBATE
    "health": "combat", "hitbox": "combat", "hurtbox": "combat",
    "knockback": "combat", "critical_hit": "combat", "damage_over_time": "combat",
    "area_damage": "combat", "status_effect": "combat", "element_system": "combat",
    "health_bar": "combat", "combo_detector": "combat",
    # PROJÉTEIS
    "projectile": "projectile", "homing_projectile": "projectile",
    "beam_laser": "projectile", "hitscan": "projectile",
    "fire_rate": "projectile", "fire_mode": "projectile",
    "spread": "projectile", "recoil": "projectile",
    "turret_aim": "projectile", "auto_aim": "projectile",
    "crosshair": "projectile", "aim_assist": "projectile",
    "modular_weapon": "projectile",
    # MOVIMENTO
    "player_controller": "movement", "player_topdown": "movement",
    "player_vehicle": "movement", "dash": "movement", "double_jump": "movement",
    "wall_slide": "movement", "grid_movement": "movement",
    "moving_platform": "movement", "follow_path": "movement",
    "patrol_route": "movement", "teleport": "movement",
    "conveyor_belt": "movement", "ladder": "movement",
    "buoyancy": "movement", "wind_zone": "movement",
    "gravity_zone": "movement", "water_surface": "movement",
    "avoidance": "movement", "flee": "movement", "flocking": "movement",
    "root_motion_controller": "movement", "spring_joint": "movement",
    "hold_alternative": "movement",
    # IA / INIMIGO
    "enemy_chase": "ai_enemy", "enemy_patrol": "ai_enemy",
    "line_of_sight": "ai_enemy", "spawner_wave": "ai_enemy",
    "state_machine": "ai_enemy", "behavior_tree": "ai_enemy",
    "stealth": "ai_enemy", "blackboard": "ai_enemy",
    "difficulty_curve": "ai_enemy", "difficulty_adjust": "ai_enemy",
    # CÂMERA
    "camera_follow": "camera", "camera_shake": "camera",
    "camera_framed": "camera", "camera_priority": "camera",
    "camera_path": "camera", "camera_lookat": "camera",
    "camera_zoom": "camera", "camera_zoom_range": "camera",
    "camera_sequence": "camera", "look_at_target": "camera",
    "parallax_background": "camera",
    # FEEDBACK / GAME FEEL
    "screen_shake": "feedback", "floating_text": "feedback",
    "particle_impact": "feedback", "hit_stop": "feedback",
    "screen_flash": "feedback", "freeze_frame": "feedback",
    "color_pulse": "feedback", "glitch": "feedback",
    "chromatic_aberration": "feedback", "vignette": "feedback",
    "trail": "feedback", "tween_player": "feedback",
    "outline": "feedback", "outline_shader": "feedback",
    "dissolve": "feedback", "lens_flare": "feedback",
    # DIÁLOGO / UI
    "dialogue": "dialogue", "interactable": "dialogue",
    "tutorial_overlay": "dialogue", "cutscene": "dialogue",
    "tooltip": "dialogue", "narrative_replay": "dialogue",
    "flexible_text_entry": "dialogue", "quick_time_alternative": "dialogue",
    # COLETÁVEIS / ITENS
    "collectable": "collectable", "inventory": "collectable",
    "currency": "collectable", "item_drop": "collectable",
    "random_loot": "collectable", "magnet": "collectable",
    "shop": "collectable", "daily_reward": "collectable",
    "chest": "collectable",
    # SISTEMA
    "save_load": "system", "encrypted_save": "system",
    "auto_save": "system", "save_slots": "system",
    "save_integrity": "system", "save_migration": "system",
    "cloud_save": "system", "cross_save": "system",
    "checkpoint": "system", "settings": "system",
    "audio_manager": "system", "input_manager": "system",
    "object_pool": "system", "event_bus": "system",
    "storage": "system", "logger": "system",
    "analytics_tracker": "system", "performance_monitor": "system",
    "profiler_hook": "system", "network_sync": "system",
    "rpc_bridge": "system", "lobby": "system",
    "leaderboard": "system", "data_table": "system",
    "curve_table": "system", "mod_config": "system",
    "mod_loader": "system", "profile_manager": "system",
    "undo_redo": "system", "dirty_flag": "system",
    "migration_runner": "system", "patch_system": "system",
    "crash_reporter": "system", "debug_console": "system",
    "fps_counter": "system", "time_scale": "system",
    "game_speed_control": "system",
    # PROGRESSÃO
    "xp_level": "collectable", "upgrade": "collectable",
    "achievement": "collectable", "unlockable": "collectable",
    "quest": "collectable", "score": "collectable",
    "character_stats": "collectable", "skill_tree": "collectable",
    "crafting": "collectable", "equipment_slot": "collectable",
    "character_creator": "collectable", "deck": "collectable",
    "card": "collectable", "farming_plot": "collectable",
    "counter": "collectable", "timer_behavior": "collectable",
    "round_timer": "collectable", "wave_system": "collectable",
}


def get_template(name):
    return TEMPLATE_MAP.get(name, "abstract")

SCENE_FUNCTIONS = {
    "combat": scene_combat,
    "movement": scene_movement,
    "projectile": scene_projectile,
    "ai_enemy": scene_ai_enemy,
    "camera": scene_camera,
    "feedback": scene_feedback,
    "dialogue": scene_dialogue,
    "collectable": scene_collectable,
    "system": scene_system,
    "abstract": scene_abstract,
}


# ── GERAÇÃO ─────────────────────────────────────────────────

def get_behavior_dirs():
    return sorted([d for d in os.listdir(BEHAVIORS_ROOT)
                   if os.path.isdir(os.path.join(BEHAVIORS_ROOT, d))
                   and os.path.isfile(os.path.join(BEHAVIORS_ROOT, d, "behavior.json"))])


def load_behavior(name):
    path = os.path.join(BEHAVIORS_ROOT, name, "behavior.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_behavior(name, data):
    path = os.path.join(BEHAVIORS_ROOT, name, "behavior.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def generate_gif(name, data):
    template = get_template(name)
    scene_fn = SCENE_FUNCTIONS[template]

    frames = []
    for i in range(N_FRAMES):
        frame = scene_fn(data, i, N_FRAMES)
        frames.append(frame)

    output_path = os.path.join(BEHAVIORS_ROOT, name, "preview.gif")
    frames[0].save(
        output_path,
        save_all=True,
        append_images=frames[1:],
        duration=FRAME_MS,
        loop=0,
        optimize=True,
        quality=85,
    )

    size_kb = os.path.getsize(output_path) / 1024.0
    return output_path, size_kb, template


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Gerador Visual Enterprise de previews")
    parser.add_argument("--batch", type=int, default=0, help="Lote N (0=todos)")
    parser.add_argument("--all", action="store_true", help="Todos 249")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    all_names = get_behavior_dirs()

    if args.batch > 0:
        batch_size = 20
        start = (args.batch - 1) * batch_size
        end = min(start + batch_size, len(all_names))
        batch = all_names[start:end]
        label = "Lote %d (%d behaviors)" % (args.batch, len(batch))
    else:
        batch = all_names
        label = "TODOS (%d behaviors)" % len(batch)

    print("=" * 60)
    print("GERADOR VISUAL ENTERPRISE — %s" % label)
    print("  Resolução: %dx%d, %dfps, %ds (%d frames)" % (W, H, FPS, DURATION, N_FRAMES))
    print("  Templates: %d cenas visuais" % len(SCENE_FUNCTIONS))
    print("  Alvo: <500KB por GIF")
    print("=" * 60)

    if args.dry_run:
        for name in batch:
            data = load_behavior(name)
            tpl = get_template(name)
            print("  [DRY] %-35s → %s" % (name, tpl))
        return

    results = []
    for name in batch:
        try:
            data = load_behavior(name)
            gif_path, size_kb, tpl = generate_gif(name, data)
            status = "OK" if size_kb < 500 else "GRANDE"
            print("  [%s] %-35s → %-10s  %6.1fKB" % (status, name, tpl, size_kb))

            data["preview_gif"] = "preview.gif"
            data["preview_type"] = "visual"
            save_behavior(name, data)
            results.append((name, "ok", tpl, size_kb))
        except Exception as e:
            print("  [ERRO] %s: %s" % (name, e))
            results.append((name, "erro", "?", 0))

    ok = sum(1 for r in results if r[1] == "ok")
    erros = sum(1 for r in results if r[1] == "erro")
    grandes = sum(1 for r in results if r[1] == "ok" and r[3] > 500)
    tpls = {}
    for r in results:
        if r[1] == "ok":
            tpls[r[2]] = tpls.get(r[2], 0) + 1

    print("\nRESUMO: %d processados, %d OK, %d erros, %d >500KB" % (len(results), ok, erros, grandes))
    print("Templates usados: %s" % dict(tpls))


if __name__ == "__main__":
    main()
