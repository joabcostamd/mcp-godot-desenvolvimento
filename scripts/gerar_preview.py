#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""sota_1.3 — Gerador de preview.gif para behaviors.

Gera GIFs animados de 3 segundos (24 frames, 8fps, 320x180) com overlay
de texto identificando o behavior. Para behaviors sem efeito visual próprio
(a maioria), usa preview_type: "abstract".

Uso: python scripts/gerar_preview.py [--batch N] [--all]

Sem argumentos: gera lote 1 (behaviors #1-20).
--batch N: gera lote N (20 behaviors).
--all: gera todos os 249.
"""

import json
import os
import sys
import math
from PIL import Image, ImageDraw, ImageFont

BEHAVIORS_ROOT = os.path.join(os.path.dirname(__file__), "..", "behaviors")

# Configuração do GIF
WIDTH = 320
HEIGHT = 180
FPS = 8
DURATION_SEC = 3
NUM_FRAMES = FPS * DURATION_SEC  # 24
FRAME_DURATION_MS = 1000 // FPS  # 125ms

# Cores
BG_COLOR = (30, 30, 40)           # fundo escuro
ACCENT_COLOR = (80, 180, 255)     # azul destaque
TEXT_COLOR = (220, 220, 230)      # texto claro
DIM_COLOR = (120, 120, 140)       # texto secundário
LEVE_COLOR = (80, 200, 120)       # verde
MEDIO_COLOR = (220, 180, 60)      # amarelo
PESADO_COLOR = (220, 80, 80)      # vermelho
BASICO_COLOR = (140, 200, 255)    # azul claro
INTERM_COLOR = (180, 160, 255)    # lavanda
AVANCADO_COLOR = (255, 180, 100)  # laranja


def get_behavior_dirs():
    """Retorna lista ordenada de diretórios de behavior."""
    return sorted([d for d in os.listdir(BEHAVIORS_ROOT)
                   if os.path.isdir(os.path.join(BEHAVIORS_ROOT, d))
                   and os.path.isfile(os.path.join(BEHAVIORS_ROOT, d, "behavior.json"))])


def load_behavior(name):
    """Carrega o behavior.json."""
    path = os.path.join(BEHAVIORS_ROOT, name, "behavior.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_behavior(name, data):
    """Salva o behavior.json."""
    path = os.path.join(BEHAVIORS_ROOT, name, "behavior.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def _get_font(size):
    """Tenta carregar uma fonte, com fallback para default."""
    font_paths = [
        "C:/Windows/Fonts/consola.ttf",
        "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]
    for fp in font_paths:
        if os.path.isfile(fp):
            try:
                return ImageFont.truetype(fp, size)
            except Exception:
                continue
    return ImageFont.load_default()


def _draw_text_box(draw, text, x, y, max_w, font, fill):
    """Desenha texto centralizado em uma caixa, com quebra se necessário."""
    if not text:
        return
    # Simplifica: desenha centralizado, sem quebra
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    cx = x + (max_w - tw) // 2
    cy = y + (30 - th) // 2
    draw.text((cx, cy), text, fill=fill, font=font)


def generate_frame(behavior_name, data, frame_idx, total_frames):
    """Gera um frame do GIF com informações do behavior."""
    img = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)

    progress = frame_idx / total_frames  # 0.0 a 1.0

    # Fontes
    font_large = _get_font(22)
    font_medium = _get_font(14)
    font_small = _get_font(11)
    font_badge = _get_font(10)

    # --- Nome do behavior (pulsando) ---
    pulse = 1.0 + 0.05 * math.sin(progress * math.pi * 4)  # 2 ciclos completos
    name = data.get("name", behavior_name).replace("_", " ").title()
    bbox = draw.textbbox((0, 0), name, font=font_large)
    tw = bbox[2] - bbox[0]
    draw.text(((WIDTH - tw) // 2, 8), name, fill=ACCENT_COLOR, font=font_large)

    # --- Verbos ---
    verbo_pt = data.get("verbo_pt", "")
    verbo_en = data.get("verbo_en", "")
    verb_line = "%s / %s" % (verbo_pt, verbo_en) if verbo_pt and verbo_en else verbo_pt or verbo_en
    bbox = draw.textbbox((0, 0), verb_line, font=font_medium)
    tw = bbox[2] - bbox[0]
    draw.text(((WIDTH - tw) // 2, 42), verb_line, fill=DIM_COLOR, font=font_medium)

    # --- Badges: custo + nível ---
    custo = data.get("custo", "leve")
    nivel = data.get("nivel", "basico")

    custo_color = {"leve": LEVE_COLOR, "medio": MEDIO_COLOR, "pesado": PESADO_COLOR}.get(custo, DIM_COLOR)
    nivel_color = {"basico": BASICO_COLOR, "intermediario": INTERM_COLOR, "avancado": AVANCADO_COLOR}.get(nivel, DIM_COLOR)

    # Badge custo
    badge_y = 68
    custo_text = custo.upper()
    bbox = draw.textbbox((0, 0), custo_text, font=font_badge)
    ctw = bbox[2] - bbox[0]
    cth = bbox[3] - bbox[1]
    cx = WIDTH // 2 - ctw - 12
    draw.rounded_rectangle([cx - 6, badge_y - 2, cx + ctw + 6, badge_y + cth + 4], radius=4, fill=custo_color)
    draw.text((cx, badge_y), custo_text, fill=BG_COLOR, font=font_badge)

    # Badge nível
    nivel_text = nivel.upper()
    bbox = draw.textbbox((0, 0), nivel_text, font=font_badge)
    ntw = bbox[2] - bbox[0]
    nx = WIDTH // 2 + 12
    draw.rounded_rectangle([nx - 6, badge_y - 2, nx + ntw + 6, badge_y + cth + 4], radius=4, fill=nivel_color)
    draw.text((nx, badge_y), nivel_text, fill=BG_COLOR, font=font_badge)

    # --- Descrição PT (truncada, animada) ---
    desc = data.get("description_pt", "")
    if len(desc) > 80:
        desc = desc[:77] + "..."
    # Animação: fade in/out suave
    alpha = 0.6 + 0.4 * math.sin(progress * math.pi * 2)
    # Renderiza texto com wrap simples
    lines = _wrap_text(desc, font_small, WIDTH - 20)
    desc_y = 100
    for i, line in enumerate(lines[:3]):  # máximo 3 linhas
        bbox = draw.textbbox((0, 0), line, font=font_small)
        lw = bbox[2] - bbox[0]
        # Aplica alpha via cor interpolada
        r, g, b = TEXT_COLOR
        faded = (int(r * alpha), int(g * alpha), int(b * alpha))
        draw.text(((WIDTH - lw) // 2, desc_y + i * 18), line, fill=faded, font=font_small)

    # --- Linha decorativa animada na base ---
    bar_width = int(WIDTH * progress)
    bar_y = HEIGHT - 6
    draw.rectangle([0, bar_y, bar_width, HEIGHT], fill=ACCENT_COLOR)

    # --- Rodapé: gêneros ---
    genres = data.get("genres", [])
    if genres:
        genre_text = " · ".join(genres[:4])
        bbox = draw.textbbox((0, 0), genre_text, font=font_small)
        gw = bbox[2] - bbox[0]
        draw.text(((WIDTH - gw) // 2, HEIGHT - 24), genre_text, fill=DIM_COLOR, font=font_small)

    return img


def _wrap_text(text, font, max_width):
    """Quebra texto em múltiplas linhas."""
    words = text.split()
    lines = []
    current = ""
    for word in words:
        test = current + (" " if current else "") + word
        bbox = ImageDraw.Draw(Image.new("RGB", (1, 1))).textbbox((0, 0), test, font=font)
        if bbox[2] - bbox[0] <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines if lines else [text]


def generate_gif(behavior_name, data):
    """Gera o GIF de preview e salva no diretório do behavior."""
    frames = []
    for i in range(NUM_FRAMES):
        frame = generate_frame(behavior_name, data, i, NUM_FRAMES)
        frames.append(frame)

    output_path = os.path.join(BEHAVIORS_ROOT, behavior_name, "preview.gif")
    frames[0].save(
        output_path,
        save_all=True,
        append_images=frames[1:],
        duration=FRAME_DURATION_MS,
        loop=0,
        optimize=True,
    )

    file_size = os.path.getsize(output_path)
    return output_path, file_size


def process_batch(behavior_names, dry_run=False):
    """Processa um lote de behaviors, gerando GIFs e atualizando JSON."""
    results = []
    for name in behavior_names:
        try:
            data = load_behavior(name)
        except Exception as e:
            print("  [ERRO] %s: falha ao carregar behavior.json — %s" % (name, e))
            results.append((name, "erro_load", str(e)))
            continue

        if dry_run:
            print("  [DRY] %s: seria gerado GIF (%s / %s, %s, %s)" % (
                name, data.get("verbo_pt", "?"), data.get("verbo_en", "?"),
                data.get("custo", "?"), data.get("nivel", "?")))
            results.append((name, "dry_run", ""))
            continue

        try:
            gif_path, gif_size = generate_gif(name, data)
        except Exception as e:
            print("  [ERRO] %s: falha ao gerar GIF — %s" % (name, e))
            results.append((name, "erro_gif", str(e)))
            continue

        # Atualizar behavior.json
        data["preview_gif"] = "preview.gif"
        data["preview_type"] = "abstract"

        try:
            save_behavior(name, data)
        except Exception as e:
            print("  [ERRO] %s: GIF gerado mas falha ao salvar JSON — %s" % (name, e))
            results.append((name, "erro_save_json", str(e)))
            continue

        size_kb = gif_size / 1024.0
        status = "OK" if gif_size < 300 * 1024 else "GRANDE"
        print("  [%s] %s: %s — %.1fKB, %dx%d, %dframes" % (
            status, name, gif_path, size_kb, WIDTH, HEIGHT, NUM_FRAMES))
        results.append((name, "ok", "%.1fKB" % size_kb))

    return results


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Gera GIFs de preview para behaviors")
    parser.add_argument("--batch", type=int, default=1, help="Número do lote (1-13)")
    parser.add_argument("--all", action="store_true", help="Gerar todos os 249")
    parser.add_argument("--dry-run", action="store_true", help="Apenas listar, sem gerar")
    args = parser.parse_args()

    all_names = get_behavior_dirs()
    batch_size = 20

    if args.all:
        batch = all_names
        label = "TODOS (%d)" % len(batch)
    else:
        start = (args.batch - 1) * batch_size
        end = min(start + batch_size, len(all_names))
        batch = all_names[start:end]
        label = "Lote %d (%d behaviors: %s...%s)" % (args.batch, len(batch), batch[0] if batch else "?", batch[-1] if batch else "?")

    print("=" * 60)
    print("GERAR PREVIEW GIFs — %s" % label)
    print("  Resolução: %dx%d, %dfps, %ds (%d frames)" % (WIDTH, HEIGHT, FPS, DURATION_SEC, NUM_FRAMES))
    print("  Tamanho alvo: <300KB por GIF")
    print("=" * 60)

    results = process_batch(batch, dry_run=args.dry_run)

    # Resumo
    ok = sum(1 for r in results if r[1] == "ok")
    erros = sum(1 for r in results if r[1].startswith("erro"))
    grandes = sum(1 for r in results if r[1] == "ok" and r[2].replace("KB", "").replace(".", "").isdigit() and float(r[2].replace("KB", "")) > 300)

    print()
    print("RESUMO: %d processados, %d OK, %d erros, %d acima de 300KB" % (
        len(results), ok, erros, grandes))

    if erros > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
