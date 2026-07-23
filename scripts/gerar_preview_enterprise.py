#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Pipeline Enterprise v2.1 — gifski encoder + 10 templates completos.

Wrapper sobre gerar_preview_visual.py (156+ mapeamentos, 10 cenas).
Renderiza frames com Pillow e codifica com gifski (GIF) e FFmpeg (MP4).

Uso: python scripts/gerar_preview_enterprise.py [--all] [--format gif,mp4]
"""

import json, math, os, shutil, subprocess, sys, tempfile
from pathlib import Path
from PIL import Image

# ── Importa cenas e mapeamento do script visual ─────────────
sys.path.insert(0, os.path.dirname(__file__))
from gerar_preview_visual import (
    get_template as _base_get_template,
    SCENE_FUNCTIONS, TEMPLATE_MAP,
    W, H, FPS, DURATION, N_FRAMES,
    get_behavior_dirs, load_behavior, save_behavior,
    # Primitivas e utilidades para template adaptativo
    _get_font, _alpha, _pulse, _blend, _ease_in_out,
    draw_text_label, draw_badge, draw_ground, draw_character,
    draw_health_bar, draw_projectile, draw_particle, draw_dialog_box,
    C_BG, C_GROUND, C_GROUND_LINE, C_PLAYER, C_ENEMY,
    C_HEALTH_BG, C_HEALTH, C_DAMAGE, C_PROJECTILE, C_PARTICLE,
    C_TEXT, C_SUBTEXT, C_ACCENT, C_WHITE, C_ITEM,
)

# ── Adiciona mapeamentos críticos faltantes ─────────────────
EXTRA_MAPPINGS = {
    # Animação
    "animation_blender": "system", "animation_curve_table": "system",
    "animation_layer": "system", "animation_state_machine": "system",
    "blend_space_1d": "system", "blend_space_2d": "system",
    "sprite_animator": "feedback", "one_shot_animation": "feedback",
    "skeleton_ik": "movement", "root_motion_controller": "movement",
    # UI / Menu
    "main_menu": "dialogue", "pause_menu": "dialogue",
    "scene_transition": "system", "tutorial_overlay": "dialogue",
    "tooltip": "dialogue", "flexible_text_entry": "dialogue",
    # Sistema
    "day_night_cycle": "system", "time_scale": "system",
    "game_speed_control": "system", "debug_console": "system",
    "fps_counter": "system", "performance_monitor": "system",
    "profiler_hook": "system", "hot_reload": "system",
    "undo_redo": "system", "dirty_flag": "system",
    "crash_reporter": "system", "logger": "system",
    "migration_runner": "system", "patch_system": "system",
    "autoload_manager": "system", "storage": "system",
    "event_bus": "system", "resource_factory": "system",
    "data_table": "system", "curve_table": "system",
    "noise_generator": "system", "l_system": "system",
    "object_pool": "system", "analytics_tracker": "system",
    "behavior_analytics": "system", "behavior_registry": "system",
    "behavior_sandbox": "system", "custom_node": "system",
    "deprecation_watcher": "system", "error_boundary": "system",
    "bypass_gate": "system", "button_mash_protection": "system",
    "localization": "system", "network_sync": "system",
    "rpc_bridge": "system", "lobby": "system", "leaderboard": "system",
    "profile_manager": "system", "mod_config": "system",
    "mod_loader": "system", "mod_sandbox": "system", "mod_store": "system",
    "resource_override": "system", "plugin_creator": "system",
    "editor_dock": "system", "sub_plugin": "system",
    "save_integrity": "system", "save_migration": "system",
    "encrypted_save": "system", "save_slots": "system",
    "auto_save": "system", "cloud_save": "system", "cross_save": "system",
    "audio_manager": "system", "audio_visualizer": "system",
    "input_manager": "system", "settings": "system",
    "authority": "system", "steam_input": "system",
    # Audio → system (não é efeito visual)
    "ambience_zone": "system", "sfx_player": "system", "music_playlist": "system",
    # Feedback extra
    "sfx_player": "system", "music_playlist": "system",
    "ambience_zone": "system", "screen_shake_toggle": "feedback",
    "freeze_frame": "feedback", "hit_stop": "feedback",
    "floating_text": "feedback", "screen_flash": "feedback",
    "color_pulse": "feedback", "chromatic_aberration": "feedback",
    "vignette": "feedback", "glitch": "feedback", "lens_flare": "feedback",
    "outline": "feedback", "outline_shader": "feedback",
    "dissolve": "feedback", "trail": "feedback",
    "tween_player": "feedback", "lerp_smooth": "feedback",
    # Câmera extra
    "parallax_background": "camera", "camera_sequence": "camera",
    "look_at_target": "camera", "camera_zoom_range": "camera",
    # Acessibilidade → system
    "assist_mode": "system", "color_blind_mode": "system",
    "high_contrast": "system", "screenreader_support": "system",
    "subtitle": "system", "text_size": "system",
    "font_size_global": "system", "interface_resize": "system",
    "interface_rearrange": "system", "controller_remap": "system",
    "virtual_joystick": "movement", "touch_gestures": "movement",
    "input_buffer": "system", "input_cooldown": "system",
    "dead_zone_config": "system", "gyro_aim": "system",
    "haptic_manager": "system", "blood_gore_toggle": "system",
    "safe_space": "system", "stereo_to_mono": "system",
    "quick_time_alternative": "system", "practice_mode": "system",
    "hold_alternative": "movement",
    # Outros
    "pathfinding": "ai_enemy", "avoidance": "movement",
    "stealth": "movement", "blackboard": "ai_enemy",
    "difficulty_curve": "ai_enemy", "difficulty_adjust": "ai_enemy",
    "state_machine": "ai_enemy", "behavior_tree": "ai_enemy",
    "spawner_wave": "ai_enemy", "wave_system": "ai_enemy",
    "round_timer": "system", "victory_condition": "system",
    "defeat_condition": "system", "score": "collectable",
    "checkpoint": "system", "quest": "collectable",
    "achievement": "collectable", "achievement_tracker": "collectable",
    "unlockable": "collectable", "daily_reward": "collectable",
    "random_loot": "collectable", "magnet": "collectable",
    "shop": "collectable", "crafting": "collectable",
    "equipment_slot": "collectable", "character_stats": "collectable",
    "character_creator": "collectable", "skill_tree": "collectable",
    "upgrade": "collectable", "xp_level": "collectable",
    "deck": "collectable", "card": "collectable",
    "farming_plot": "collectable", "fishing_cast": "collectable",
    "counter": "collectable", "timer_behavior": "collectable",
    "currency": "collectable", "inventory": "collectable",
    "collectable": "collectable",
    "interactable": "dialogue", "dialogue": "dialogue",
    "cutscene": "dialogue", "narrative_replay": "dialogue",
    "scene_transition": "system", "accordion": "system",
    # Desenho / render
    "draw_call_optimizer": "system", "batch_renderer": "system",
    "lod_controller": "system", "spatial_hash": "system",
    "server_physics": "system", "server_sprite": "system",
    "physics_tick_optimizer": "system",
    "tilemap_layer_manager": "system", "terrain_autotiler": "system",
    "tile_pattern_stamper": "system", "dungeon_generator": "system",
    "world_map_generator": "system", "infinite_world": "system",
    "random_walker": "system",
    "destructible": "combat", "burnable": "combat",
    "lava_surface": "combat", "water_surface": "movement",
    "trigger_zone": "system", "racing_lap": "movement",
    "match3_grid": "system", "rhythm_timing": "system",
    "drag_drop": "dialogue", "screen_shake": "feedback",
}

TEMPLATE_MAP.update(EXTRA_MAPPINGS)

def get_template(name):
    return TEMPLATE_MAP.get(name, "abstract")

# ── TEMPLATE SYSTEM ADAPTATIVO ──────────────────────────────
# Sobrescreve o scene_system genérico com versão que detecta subtipo

def _system_subtype(data):
    """Detecta o subtipo do behavior system pela descrição e nome."""
    name = data.get("name","")
    desc = (data.get("description_pt","") + " " + data.get("description_en","")).lower()
    
    # Prioridade: nome > descrição > tags
    audio_names = {"audio_manager","sfx_player","music_playlist","ambience_zone","audio_visualizer"}
    save_names = {"save_load","auto_save","save_slots","save_integrity","save_migration","encrypted_save","cloud_save","cross_save","checkpoint"}
    network_names = {"network_sync","rpc_bridge","lobby","leaderboard"}
    debug_names = {"debug_console","fps_counter","logger","crash_reporter","performance_monitor","profiler_hook"}
    config_names = {"settings","input_manager","controller_remap","localization","profile_manager","mod_config"}
    
    if name in audio_names: return "audio"
    if name in save_names: return "save"
    if name in network_names: return "network"
    if name in debug_names: return "debug"
    if name in config_names: return "config"
    
    # Fallback por keywords na descrição
    audio_kw = ["audio","som","sound","music","volume","sfx"]
    save_kw = ["save","load","salvar","carregar","checkpoint","persistência"]
    network_kw = ["network","sync","rpc","multiplayer","server"]
    debug_kw = ["debug","console","log","crash","profiler","trace"]
    
    if any(kw in desc for kw in audio_kw) and name not in config_names: return "audio"
    if any(kw in desc for kw in save_kw): return "save"
    if any(kw in desc for kw in network_kw): return "network"
    if any(kw in desc for kw in debug_kw): return "debug"
    
    return "generic"

def scene_system_adaptive(data, frame_idx, n_frames):
    """Template SYSTEM adaptativo — visual customizado por subtipo."""
    from PIL import Image, ImageDraw
    t = frame_idx / n_frames
    img = Image.new("RGB", (W, H), C_BG)
    draw = ImageDraw.Draw(img)
    font_sm = _get_font(11)
    font_md = _get_font(14)
    font_lg = _get_font(20)
    font_xl = _get_font(26)

    subtype = _system_subtype(data)
    name = data.get("name", "?").replace("_", " ").title()
    cx, cy = W//2, H//2 - 20

    # ── Cabeçalho comum ──
    draw_text_label(draw, name, cx, 8, font_xl, C_ACCENT)
    verb_line = "%s / %s" % (data.get("verbo_pt",""), data.get("verbo_en",""))
    draw_text_label(draw, verb_line, cx, 40, font_sm, C_SUBTEXT)

    # Badges
    custo = data.get("custo", "leve")
    nivel = data.get("nivel", "basico")
    custo_c = {"leve": (80,200,120), "medio": (220,180,60), "pesado": (220,80,80)}.get(custo, C_SUBTEXT)
    nivel_c = {"basico": (140,200,255), "intermediario": (180,160,255), "avancado": (255,180,100)}.get(nivel, C_SUBTEXT)
    draw_badge(draw, custo.upper(), cx-100, 55, custo_c, font_sm)
    draw_badge(draw, nivel.upper(), cx+30, 55, nivel_c, font_sm)

    # ── Visual por subtipo ──
    if subtype == "audio":
        # Background pulsante para garantir variacao entre frames
        bg_pulse = int(5 * _pulse(t, 2))
        draw.rectangle([0, 0, W, H], fill=(C_BG[0]+bg_pulse, C_BG[1]+bg_pulse, C_BG[2]+bg_pulse))

        # Ondas de áudio + ícone speaker com animacao forte
        speaker_x, speaker_y = cx-80, cy+20
        speaker_color = _alpha(C_ACCENT, 0.7 + 0.3*_pulse(t, 3))
        draw.rectangle([speaker_x, speaker_y-10, speaker_x+16, speaker_y+10], fill=speaker_color)
        draw.polygon([(speaker_x+16, speaker_y-16), (speaker_x+36, speaker_y-30),
                      (speaker_x+36, speaker_y+30), (speaker_x+16, speaker_y+16)], fill=speaker_color)
        # Ondas sonoras com amplitude forte e variada
        for w in range(4):
            wave_x = speaker_x + 50 + w*28
            amp = 10 + int(16 * abs(math.sin(t*math.pi*4 + w*1.5)))
            wave_alpha = 0.4 + 0.6*_pulse(t, 5+w)
            wave_color = _alpha(C_ACCENT, wave_alpha)
            draw.arc([wave_x, speaker_y-amp, wave_x+22, speaker_y+amp],
                     0, int(math.pi*2), fill=wave_color, width=2+w)
        # Texto pulsante indicando audio
        freq_text = "~%dHz" % int(200 + 800*_pulse(t, 3))
        draw_text_label(draw, freq_text, speaker_x+140, speaker_y, font_md, _alpha(C_TEXT, _pulse(t,2)))

    elif subtype == "save":
        # Disco de save + progresso circular
        disk_r = 35
        draw.ellipse([cx-disk_r, cy+10-disk_r, cx+disk_r, cy+10+disk_r],
                     outline=C_ACCENT, width=3)
        arc_angle = 360 * ((t * 1.5) % 1.0)
        if arc_angle > 3:
            draw.arc([cx-disk_r+4, cy+10-disk_r+4, cx+disk_r-4, cy+10+disk_r-4],
                     0, min(360, arc_angle), fill=(80,220,120), width=4)
        # "SAVE" label piscando
        if _pulse(t, 2) > 0.5:
            draw_text_label(draw, "SAVE", cx, cy+60, font_md, (80,220,120))

    elif subtype == "network":
        # Nós de rede conectados
        nodes = [(cx-60, cy-10), (cx+60, cy-10), (cx, cy+50), (cx-40, cy+50), (cx+40, cy+50)]
        # Conexões
        for i, (x1, y1) in enumerate(nodes):
            for j, (x2, y2) in enumerate(nodes):
                if i < j:
                    alpha = 0.15 + 0.1 * _pulse(t, 3+i+j)
                    draw.line([x1, y1, x2, y2], fill=_alpha(C_ACCENT, alpha), width=1)
        # Nós pulsando
        for i, (nx, ny) in enumerate(nodes):
            r = 6 + int(3*_pulse(t, 2+i))
            draw.ellipse([nx-r, ny-r, nx+r, ny+r], fill=C_ACCENT)
        # Pacotes viajando
        pkg_t = (t * 2) % 1.0
        pkg_idx = int(pkg_t * 4)
        if pkg_idx < 4:
            nx1, ny1 = nodes[pkg_idx]
            nx2, ny2 = nodes[(pkg_idx+1)%4]
            frac = (pkg_t * 4) % 1.0
            px = int(nx1 + (nx2-nx1)*frac)
            py = int(ny1 + (ny2-ny1)*frac)
            draw.ellipse([px-4, py-4, px+4, py+4], fill=(255,220,80))

    elif subtype == "debug":
        # Console com linhas de log
        console_x, console_y = cx-140, cy
        draw.rounded_rectangle([console_x, console_y, console_x+280, console_y+120],
                               radius=6, fill=(15,18,22), outline=C_ACCENT, width=1)
        log_lines = [
            ("[INFO]", "system initialized", (80,200,120)),
            ("[DEBUG]", "processing data_%d" % int(t*10), C_ACCENT),
            ("[WARN]", "threshold接近 limite", (220,180,60)),
            ("[INFO]", "cycle complete in %.1fms" % (0.5+_pulse(t,3)*2), C_SUBTEXT),
        ]
        for i, (tag, msg, color) in enumerate(log_lines):
            ly = console_y + 15 + i*24
            draw_text_label(draw, tag, console_x+12, ly, font_sm, color, center=False)
            draw_text_label(draw, msg, console_x+80, ly, font_sm, C_TEXT, center=False)
        # Cursor piscando
        if _pulse(t, 4) > 0.5:
            draw.rectangle([console_x+270, console_y+107, console_x+278, console_y+117],
                          fill=C_ACCENT)

    elif subtype == "config":
        # Sliders e toggles
        configs = [
            ("Master Vol", 0.8, (80,200,120)),
            ("Music Vol", 0.6, C_ACCENT),
            ("SFX Vol", 0.9, (180,160,255)),
            ("Fullscreen", 1.0 if _pulse(t, 1) > 0.5 else 0.0, (255,180,100)),
        ]
        for i, (label, val, color) in enumerate(configs):
            cy_i = cy - 20 + i*35
            draw_text_label(draw, label, cx-150, cy_i, font_sm, C_TEXT, center=False)
            # Slider track
            track_x, track_y = cx-40, cy_i+6
            draw.rectangle([track_x, track_y, track_x+180, track_y+6], fill=C_HEALTH_BG)
            # Slider fill
            fill_w = int(180 * (0.3 + 0.7*abs(math.sin(t*2+i))))
            draw.rectangle([track_x, track_y, track_x+fill_w, track_y+6], fill=color)
            # Knob
            knob_x = track_x + fill_w
            draw.ellipse([knob_x-5, track_y-2, knob_x+5, track_y+8], fill=color)

    else:  # generic
        # Visualização de dados padrão
        for i in range(4):
            bar_y = 85 + i*40
            bar_w = 200 + int(150 * math.sin(t*2 + i))
            draw.rectangle([cx-150, bar_y, cx-150+bar_w, bar_y+20],
                          fill=_alpha(C_ACCENT, 0.2+i*0.05))
            draw.rectangle([cx-150, bar_y, cx-150+bar_w, bar_y+20],
                          outline=C_ACCENT, width=1)
            draw_text_label(draw, "data_%d" % i, cx-160, bar_y+3, font_sm, C_SUBTEXT, center=False)
        # Círculo central pulsante
        pulse_r = 25 + int(8*_pulse(t, 3))
        draw.ellipse([cx-pulse_r, cy+50-pulse_r, cx+pulse_r, cy+50+pulse_r],
                     outline=_alpha(C_ACCENT, _pulse(t,2)*0.5), width=2)
        draw.text((cx-15, cy+38), data.get("verbo_pt","..."), fill=C_TEXT, font=font_md)

    # Gêneros no rodapé
    genres = data.get("genres", [])[:5]
    if genres:
        genre_text = " Â· ".join(genres)
        draw_text_label(draw, genre_text, cx, H-25, font_sm, C_SUBTEXT)

    return img

# Sobrescreve o scene_system genérico
SCENE_FUNCTIONS["system"] = scene_system_adaptive

# ── Encoders ────────────────────────────────────────────────
FRAME_MS = 1000 // FPS

def _find_bin(name):
    found = shutil.which(name)
    if found: return found
    for base in [os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\WinGet\Packages")]:
        if os.path.isdir(base):
            for root, dirs, files in os.walk(base):
                if name + ".exe" in files:
                    return os.path.join(root, name + ".exe")
    return name

def encode_gifski(frame_dir, output):
    gifski = _find_bin("gifski")
    frames = sorted(Path(frame_dir).glob("frame_*.png"))
    cmd = [gifski, "-o", output, "-r", str(FPS),
           "--width", str(W), "--height", str(H), "--quality", "90"]
    cmd += [str(f) for f in frames]
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=120)
        return os.path.getsize(output) / 1024
    except: return 0

def encode_mp4(frame_dir, output):
    ffmpeg = _find_bin("ffmpeg")
    cmd = [ffmpeg, "-y", "-framerate", str(FPS),
           "-i", os.path.join(frame_dir, "frame_%04d.png"),
           "-c:v", "libx264", "-pix_fmt", "yuv420p",
           "-preset", "medium", "-crf", "23",
           "-movflags", "+faststart", output]
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=120)
        return os.path.getsize(output) / 1024
    except: return 0

# ── Geração ─────────────────────────────────────────────────
BEHAVIORS_ROOT = os.path.join(os.path.dirname(__file__), "..", "behaviors")

def generate_one(name, data, formats, tmpdir):
    tpl = get_template(name)
    scene_fn = SCENE_FUNCTIONS.get(tpl, SCENE_FUNCTIONS["abstract"])
    frame_dir = os.path.join(tmpdir, name)
    os.makedirs(frame_dir, exist_ok=True)

    for i in range(N_FRAMES):
        frame = scene_fn(data, i, N_FRAMES)
        frame.save(os.path.join(frame_dir, "frame_%04d.png" % i), "PNG")

    r = {"template": tpl}
    if "gif" in formats:
        sz = encode_gifski(frame_dir, os.path.join(BEHAVIORS_ROOT, name, "preview.gif"))
        r["gif_kb"] = sz; r["gif_ok"] = sz > 0
    if "mp4" in formats:
        sz = encode_mp4(frame_dir, os.path.join(BEHAVIORS_ROOT, name, "preview.mp4"))
        r["mp4_kb"] = sz; r["mp4_ok"] = sz > 0
        if sz > 0: data["preview_mp4"] = "preview.mp4"

    data["preview_gif"] = "preview.gif"
    data["preview_type"] = "visual"
    save_behavior(name, data)
    shutil.rmtree(frame_dir, ignore_errors=True)
    return r

def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--all", action="store_true")
    p.add_argument("--format", default="gif,mp4")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()
    formats = [f.strip() for f in args.format.split(",")]
    batch = get_behavior_dirs() if args.all else get_behavior_dirs()[:5]

    print("=" * 60)
    print("PIPELINE ENTERPRISE v2.1 — %d behaviors" % len(batch))
    print("  Templates: %d cenas, %d mapeados" % (len(SCENE_FUNCTIONS), len(TEMPLATE_MAP)))
    from collections import Counter
    c = Counter(get_template(d) for d in get_behavior_dirs())
    print("  Distribuicao: %s" % dict(c))
    print("  Formatos: %s | %dx%d @ %dfps" % (",".join(formats), W, H, FPS))
    print("=" * 60)

    if args.dry_run:
        for name in batch:
            print("  [DRY] %-35s -> %s" % (name, get_template(name)))
        return

    with tempfile.TemporaryDirectory() as td:
        ok = er = 0; gk = mk = 0.0; td_map = {}
        for name in batch:
            try:
                data = load_behavior(name)
                r = generate_one(name, data, formats, td)
                tpl = r["template"]; td_map[tpl] = td_map.get(tpl, 0) + 1
                gs = r.get("gif_kb", 0); ms = r.get("mp4_kb", 0)
                status = "PASS" if r.get("gif_ok") else "FAIL"
                print("  %-35s %-12s GIF:%5.0fKB MP4:%5.0fKB [%s]" % (name, tpl, gs, ms, status))
                ok += 1; gk += gs; mk += ms
            except Exception as e:
                print("  [ERRO] %s: %s" % (name, e)); er += 1

        n = max(ok, 1)
        print("\nRESUMO: %d OK, %d erros" % (ok, er))
        if "gif" in formats: print("  GIF  medio: %.0fKB" % (gk/n))
        if "mp4" in formats: print("  MP4  medio: %.0fKB" % (mk/n))
        print("  Templates usados: %s" % dict(td_map))

if __name__ == "__main__":
    main()
