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
    # Feedback extra
    "sfx_player": "feedback", "music_playlist": "feedback",
    "ambience_zone": "feedback", "screen_shake_toggle": "feedback",
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
    "stealth": "ai_enemy", "blackboard": "ai_enemy",
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
    "destructible": "combat", "burnable": "feedback",
    "lava_surface": "feedback", "water_surface": "movement",
    "trigger_zone": "system", "racing_lap": "movement",
    "match3_grid": "system", "rhythm_timing": "system",
    "drag_drop": "system", "screen_shake": "feedback",
}

TEMPLATE_MAP.update(EXTRA_MAPPINGS)

def get_template(name):
    return TEMPLATE_MAP.get(name, "abstract")

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
