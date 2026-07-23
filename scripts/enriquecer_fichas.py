#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""sota_1.1 — Enriquecer as fichas dos 249 behaviors.

Lê behavior.json + .gd de cada behavior e propõe 4 campos novos:
  combina_bem, custo, verbo_pt, verbo_en, nivel

Grava as propostas em behaviors/_enriquecimento_proposto.json
NUNCA sobrescreve os behavior.json diretamente.

Uso: python scripts/enriquecer_fichas.py
"""

import json
import os
import re
import sys

BEHAVIORS_ROOT = os.path.join(os.path.dirname(__file__), "..", "behaviors")
OUTPUT_FILE = os.path.join(BEHAVIORS_ROOT, "_enriquecimento_proposto.json")

# ---------------------------------------------------------------------------
# MAPA DE VERBOS CANÔNICOS (name → (verbo_pt, verbo_en))
# Derivado do CATALOGO_COMPLETO.md + nome do behavior + primeiro sinônimo.
# ---------------------------------------------------------------------------
VERB_MAP = {
    # MOVIMENTO
    "player_controller": ("mover", "move"),
    "player_topdown": ("mover", "move"),
    "player_vehicle": ("dirigir", "drive"),
    "moving_platform": ("deslocar", "move"),
    "dash": ("impulsionar", "dash"),
    "double_jump": ("pular", "jump"),
    "wall_slide": ("escorregar", "slide"),
    "grid_movement": ("movimentar", "move"),
    "follow_path": ("seguir", "follow"),
    "patrol_route": ("patrulhar", "patrol"),
    "teleport": ("teletransportar", "teleport"),
    "conveyor_belt": ("transportar", "convey"),
    "ladder": ("escalar", "climb"),
    "buoyancy": ("flutuar", "float"),
    "wind_zone": ("soprar", "blow"),
    "gravity_zone": ("atrair", "attract"),
    "water_surface": ("flutuar", "float"),
    "spring_joint": ("conectar", "connect"),
    "avoidance": ("desviar", "avoid"),
    "root_motion_controller": ("animar", "animate"),
    "flee": ("fugir", "flee"),
    "flocking": ("agrupar", "flock"),
    "hold_alternative": ("segurar", "hold"),

    # COMBATE
    "health": ("gerenciar_vida", "manage_health"),
    "projectile": ("atirar", "shoot"),
    "hitbox": ("causar_dano", "deal_damage"),
    "hurtbox": ("receber_dano", "receive_damage"),
    "fire_rate": ("disparar", "fire"),
    "knockback": ("empurrar", "knockback"),
    "critical_hit": ("critar", "crit"),
    "damage_over_time": ("envenenar", "damage_over_time"),
    "area_damage": ("explodir", "explode"),
    "homing_projectile": ("perseguir", "home"),
    "beam_laser": ("emitir_raio", "beam"),
    "hitscan": ("atingir", "hitscan"),
    "recoil": ("recuar", "recoil"),
    "spread": ("dispersar", "spread"),
    "fire_mode": ("disparar", "fire"),
    "crosshair": ("mirar", "aim"),
    "turret_aim": ("mirar", "aim"),
    "auto_aim": ("mirar", "aim"),
    "aim_assist": ("auxiliar_mira", "assist_aim"),
    "hit_stop": ("pausar", "pause"),
    "element_system": ("elementar", "elemental"),
    "status_effect": ("aplicar_efeito", "apply_effect"),
    "combo_detector": ("combar", "combo"),

    # INIMIGO / AI
    "enemy_chase": ("perseguir", "chase"),
    "enemy_patrol": ("patrulhar", "patrol"),
    "line_of_sight": ("avistar", "spot"),
    "spawner_wave": ("gerar_inimigos", "spawn"),
    "state_machine": ("gerenciar_estado", "manage_state"),
    "behavior_tree": ("decidir", "decide"),
    "stealth": ("esconder", "hide"),
    "blackboard": ("compartilhar_dados", "share_data"),

    # PROGRESSÃO
    "inventory": ("gerenciar_inventario", "manage_inventory"),
    "collectable": ("coletar", "collect"),
    "xp_level": ("evoluir", "level_up"),
    "upgrade": ("melhorar", "upgrade"),
    "currency": ("gerenciar_moedas", "manage_currency"),
    "quest": ("rastrear_missao", "track_quest"),
    "achievement": ("desbloquear_conquista", "unlock_achievement"),
    "unlockable": ("desbloquear", "unlock"),
    "crafting": ("criar", "craft"),
    "shop": ("comprar", "shop"),
    "equipment_slot": ("equipar", "equip"),
    "character_stats": ("gerenciar_atributos", "manage_stats"),
    "character_creator": ("criar_personagem", "create_character"),
    "skill_tree": ("evoluir_skill", "upgrade_skill"),
    "card": ("jogar_carta", "play_card"),
    "deck": ("gerenciar_deck", "manage_deck"),
    "farming_plot": ("cultivar", "farm"),
    "fishing_cast": ("pescar", "fish"),
    "daily_reward": ("resgatar", "claim"),
    "random_loot": ("dropar", "drop_loot"),
    "idle_generator": ("gerar_recurso", "generate_resource"),
    "difficulty_curve": ("ajustar_dificuldade", "adjust_difficulty"),
    "difficulty_adjust": ("ajustar_dificuldade", "adjust_difficulty"),
    "round_timer": ("cronometrar", "time"),
    "victory_condition": ("definir_vitoria", "define_victory"),
    "defeat_condition": ("definir_derrota", "define_defeat"),
    "score": ("pontuar", "score"),
    "wave_system": ("gerenciar_ondas", "manage_waves"),
    "racing_lap": ("correr", "race"),

    # SISTEMA
    "save_load": ("salvar", "save"),
    "encrypted_save": ("criptografar_save", "encrypt_save"),
    "auto_save": ("salvar_automatico", "auto_save"),
    "save_slots": ("gerenciar_slots", "manage_slots"),
    "save_integrity": ("verificar_integridade", "verify_integrity"),
    "save_migration": ("migrar_save", "migrate_save"),
    "cloud_save": ("salvar_nuvem", "cloud_save"),
    "cross_save": ("sincronizar", "sync_save"),
    "pause_menu": ("pausar", "pause"),
    "main_menu": ("navegar_menu", "navigate_menu"),
    "settings": ("configurar", "configure"),
    "scene_transition": ("transicionar", "transition"),
    "audio_manager": ("gerenciar_audio", "manage_audio"),
    "input_manager": ("gerenciar_input", "manage_input"),
    "time_scale": ("controlar_tempo", "control_time"),
    "checkpoint": ("salvar_progresso", "save_progress"),
    "object_pool": ("reutilizar_objetos", "pool_objects"),
    "event_bus": ("transmitir_evento", "broadcast_event"),
    "autoload_manager": ("gerenciar_autoloads", "manage_autoloads"),
    "storage": ("armazenar", "store"),
    "resource_factory": ("criar_resource", "create_resource"),
    "undo_redo": ("desfazer", "undo"),
    "dirty_flag": ("marcar_sujo", "mark_dirty"),
    "custom_node": ("criar_no", "create_node"),
    "hot_reload": ("recarregar", "reload"),
    "migration_runner": ("migrar", "migrate"),
    "deprecation_watcher": ("alertar_depreciacao", "warn_deprecation"),
    "error_boundary": ("capturar_erro", "catch_error"),
    "patch_system": ("aplicar_patch", "apply_patch"),
    "crash_reporter": ("reportar_crash", "report_crash"),
    "profiler_hook": ("perfilar", "profile"),
    "performance_monitor": ("monitorar", "monitor"),
    "logger": ("registrar_log", "log"),
    "bypass_gate": ("ignorar_gate", "bypass_gate"),
    "analytics_tracker": ("rastrear_analytics", "track_analytics"),
    "behavior_analytics": ("analisar_behaviors", "analyze_behaviors"),
    "behavior_registry": ("registrar_behavior", "register_behavior"),
    "behavior_sandbox": ("testar_behavior", "sandbox_behavior"),
    "mod_config": ("configurar_mod", "configure_mod"),
    "mod_loader": ("carregar_mod", "load_mod"),
    "mod_sandbox": ("testar_mod", "sandbox_mod"),
    "mod_store": ("baixar_mod", "download_mod"),
    "resource_override": ("sobrescrever_recurso", "override_resource"),
    "plugin_creator": ("criar_plugin", "create_plugin"),
    "editor_dock": ("ancorar_dock", "dock"),
    "sub_plugin": ("registrar_subplugin", "register_subplugin"),
    "profile_manager": ("gerenciar_perfil", "manage_profile"),
    "network_sync": ("sincronizar_rede", "sync_network"),
    "rpc_bridge": ("preencher_rpc", "bridge_rpc"),
    "lobby": ("criar_sala", "create_lobby"),
    "leaderboard": ("ranquear", "rank"),
    "steam_input": ("gerenciar_steam", "manage_steam"),
    "button_mash_protection": ("proteger_botao", "protect_button"),
    "game_speed_control": ("controlar_velocidade", "control_speed"),
    "match3_grid": ("combinar_pecas", "match_gems"),
    "rhythm_timing": ("sincronizar_ritmo", "sync_rhythm"),
    "drag_drop": ("arrastar", "drag"),
    "interactable": ("interagir", "interact"),
    "flexible_text_entry": ("digitar", "type"),
    "quick_time_alternative": ("simplificar_quicktime", "simplify_qte"),
    "practice_mode": ("praticar", "practice"),

    # FEEDBACK / GAME FEEL
    "screen_shake": ("tremer", "shake"),
    "floating_text": ("exibir_texto", "display_text"),
    "particle_impact": ("emitir_particula", "emit_particle"),
    "screen_flash": ("piscar_tela", "flash_screen"),
    "camera_zoom": ("zoom", "zoom"),
    "color_pulse": ("pulsar_cor", "pulse_color"),
    "trail": ("deixar_rastro", "leave_trail"),
    "tween_player": ("animar_propriedade", "tween"),
    "chromatic_aberration": ("distorcer_cor", "aberrate"),
    "vignette": ("escurecer_bordas", "vignette"),
    "freeze_frame": ("congelar_frame", "freeze_frame"),
    "glitch": ("glitchar", "glitch"),
    "outline": ("contornar", "outline"),
    "outline_shader": ("contornar", "outline"),
    "dissolve": ("dissolver", "dissolve"),
    "sprite_animator": ("animar_sprite", "animate_sprite"),
    "one_shot_animation": ("tocar_animacao", "play_animation"),
    "lens_flare": ("brilhar", "flare"),
    "sfx_player": ("tocar_som", "play_sfx"),
    "music_playlist": ("tocar_musica", "play_music"),
    "ambience_zone": ("ambientar", "ambience"),
    "audio_visualizer": ("visualizar_audio", "visualize_audio"),
    "tooltip": ("exibir_dica", "show_tooltip"),
    "fps_counter": ("medir_fps", "measure_fps"),
    "debug_arrow": ("desenhar_seta", "draw_arrow"),
    "debug_position": ("exibir_posicao", "show_position"),
    "debug_overlay": ("exibir_debug", "show_debug"),
    "debug_console": ("registrar_console", "log_console"),
    "lerp_smooth": ("suavizar", "smooth"),
    "tile_pattern_stamper": ("carimbar_tile", "stamp_tile"),

    # CÂMERA
    "camera_follow": ("seguir_camera", "follow_camera"),
    "camera_shake": ("tremer_camera", "shake_camera"),
    "camera_framed": ("enquadrar", "frame"),
    "camera_priority": ("priorizar_camera", "prioritize_camera"),
    "camera_path": ("percorrer_camera", "path_camera"),
    "camera_lookat": ("olhar_para", "look_at"),
    "camera_zoom_range": ("zoom_range", "zoom_range"),
    "parallax_background": ("paralaxe", "parallax"),
    "animation_blender": ("misturar_animacao", "blend_animation"),
    "animation_curve_table": ("interpolar_curva", "interpolate_curve"),
    "animation_layer": ("sobrepor_animacao", "layer_animation"),
    "animation_state_machine": ("gerenciar_animacao", "manage_animation"),
    "blend_space_1d": ("interpolar_1d", "blend_1d"),
    "blend_space_2d": ("interpolar_2d", "blend_2d"),
    "batch_renderer": ("renderizar_lote", "batch_render"),
    "draw_call_optimizer": ("otimizar_draw", "optimize_draw"),
    "lod_controller": ("controlar_lod", "control_lod"),
    "spatial_hash": ("indexar_espaco", "hash_space"),
    "physics_tick_optimizer": ("otimizar_fisica", "optimize_physics"),
    "server_physics": ("servidor_fisica", "physics_server"),
    "server_sprite": ("servidor_sprite", "sprite_server"),
    "noise_generator": ("gerar_ruido", "generate_noise"),
    "l_system": ("gerar_lsystem", "generate_lsystem"),

    # GERAÇÃO DE CONTEÚDO
    "dungeon_generator": ("gerar_masmorra", "generate_dungeon"),
    "random_walker": ("caminhar_aleatorio", "random_walk"),
    "world_map_generator": ("gerar_mapa", "generate_map"),
    "infinite_world": ("gerar_mundo_infinito", "generate_infinite"),
    "terrain_autotiler": ("auto_tile", "autotile"),
    "tilemap_layer_manager": ("gerenciar_tilemap", "manage_tilemap"),
    "modular_weapon": ("montar_arma", "assemble_weapon"),

    # ACESSIBILIDADE
    "assist_mode": ("auxiliar", "assist"),
    "color_blind_mode": ("corrigir_cor", "correct_color"),
    "high_contrast": ("aumentar_contraste", "increase_contrast"),
    "screenreader_support": ("narrar", "narrate"),
    "subtitle": ("legendar", "subtitle"),
    "text_size": ("ajustar_texto", "adjust_text"),
    "font_size_global": ("ajustar_fonte", "adjust_font"),
    "interface_resize": ("redimensionar_ui", "resize_ui"),
    "interface_rearrange": ("reorganizar_ui", "rearrange_ui"),
    "controller_remap": ("remapear_controle", "remap_controller"),
    "virtual_joystick": ("joystick_virtual", "virtual_joystick"),
    "touch_gestures": ("detectar_gesto", "detect_gesture"),
    "input_buffer": ("buffer_input", "buffer_input"),
    "input_cooldown": ("cooldown_input", "cooldown_input"),
    "dead_zone_config": ("configurar_zona_morta", "configure_deadzone"),
    "gyro_aim": ("mirar_giroscopio", "gyro_aim"),
    "haptic_manager": ("vibrar", "haptic"),
    "blood_gore_toggle": ("desativar_gore", "disable_gore"),
    "safe_space": ("zona_segura", "safe_zone"),
    "stereo_to_mono": ("converter_mono", "convert_mono"),

    # UI / INTERFACE
    "health_bar": ("exibir_vida", "display_health"),
    "counter": ("contar", "count"),
    "timer_behavior": ("cronometrar", "time"),
    "tutorial_overlay": ("ensinar", "teach"),
    "narrative_replay": ("reproduzir_narrativa", "replay_narrative"),
    "cutscene": ("tocar_cutscene", "play_cutscene"),
    "dialogue": ("dialogar", "dialogue"),
    "localization": ("traduzir", "translate"),

    # FÍSICA
    "destructible": ("destruir", "destroy"),
    "burnable": ("queimar", "burn"),
    "lava_surface": ("queimar", "burn"),
    "trigger_zone": ("detectar", "detect"),
    "magnet": ("atrair", "attract"),
    "pushable": ("empurrar", "push"),
    "conveyor": ("transportar", "convey"),
    "ice_physics": ("deslizar", "slide"),

    # MISC
    "day_night_cycle": ("ciclo_dia_noite", "day_night_cycle"),
    "data_table": ("tabela_dados", "data_table"),
    "curve_table": ("tabela_curva", "curve_table"),
    "hand": ("segurar", "hold"),
    "accordion": ("expandir", "expand"),
    "authority": ("autorizar", "authorize"),
    "achievement_tracker": ("rastrear_conquista", "track_achievement"),

    # FALTANTES (adicionados na auditoria de 23/07)
    "camera_sequence": ("sequenciar", "sequence"),
    "look_at_target": ("olhar_para", "look_at"),
    "pathfinding": ("navegar", "navigate"),
    "screen_shake_toggle": ("alternar_tremer", "toggle_shake"),
    "skeleton_ik": ("animar_ik", "animate_ik"),
}

# ---------------------------------------------------------------------------
# HEURÍSTICAS
# ---------------------------------------------------------------------------

# Pares conhecidos de sinais complementares (emissor → receptor)
# Formato: (emitter_signal, receiver_behavior_condition)
KNOWN_COMPATIBLE_PAIRS = {
    # health emite → vários ouvem
    "died": ["enemy_chase", "enemy_patrol", "spawner_wave", "score", "floating_text",
             "achievement", "quest", "xp_level", "screen_shake", "particle_impact",
             "freeze_frame", "hit_stop", "destructible", "sfx_player"],
    "damage_taken": ["health_bar", "floating_text", "screen_shake", "particle_impact",
                     "hit_stop", "sfx_player", "color_pulse", "screen_flash",
                     "trail", "knockback", "status_effect"],
    "healed": ["health_bar", "floating_text", "sfx_player"],
    "hp_changed": ["health_bar", "analytics_tracker"],

    # projectile emite
    "hit": ["health", "particle_impact", "screen_shake", "sfx_player", "floating_text",
            "freeze_frame", "hit_stop", "knockback"],

    # player_controller emite
    "player_died": ["defeat_condition", "screen_shake", "particle_impact", "sfx_player",
                    "floating_text", "scene_transition"],

    # collectable emite
    "collected": ["inventory", "score", "currency", "sfx_player", "floating_text",
                  "achievement", "quest"],

    # wave_system / spawner_wave
    "wave_started": ["floating_text", "sfx_player"],
    "wave_cleared": ["score", "currency", "floating_text", "achievement"],

    # round_timer
    "time_up": ["defeat_condition", "scene_transition", "floating_text"],

    # interactable
    "interacted": ["dialogue", "sfx_player", "quest", "scene_transition",
                   "inventory", "checkpoint"],
}

# Behaviors que naturalmente combinam com muitos outros (utility)
UNIVERSAL_COMBINE = {
    "health": "health",
    "health_bar": "health_bar",
    "hitbox": "hitbox",
    "hurtbox": "hurtbox",
    "sfx_player": "sfx_player",
    "floating_text": "floating_text",
    "particle_impact": "particle_impact",
    "screen_shake": "screen_shake",
    "object_pool": "object_pool",
    "state_machine": "state_machine",
    "save_load": "save_load",
    "tween_player": "tween_player",
    "sprite_animator": "sprite_animator",
    "status_effect": "status_effect",
}

# Behaviors que NÃO devem aparecer em combina_bem (muito genéricos ou internos)
SKIP_COMBINE = {
    "behavior_registry", "behavior_analytics", "behavior_sandbox",
    "autoload_manager", "event_bus", "logger", "crash_reporter",
    "performance_monitor", "profiler_hook", "deprecation_watcher",
    "error_boundary", "bypass_gate", "analytics_tracker",
    "plugin_creator", "editor_dock", "sub_plugin", "mod_config",
    "mod_loader", "mod_sandbox", "mod_store", "patch_system",
    "migration_runner", "hot_reload", "undo_redo", "dirty_flag",
    "custom_node", "resource_factory", "resource_override",
    "storage", "debug_arrow", "debug_position", "debug_overlay",
    "debug_console", "fps_counter", "behavior_tree", "blackboard",
}


def get_behavior_dirs():
    """Retorna lista de diretórios de behavior (têm behavior.json)."""
    dirs = []
    for entry in sorted(os.listdir(BEHAVIORS_ROOT)):
        path = os.path.join(BEHAVIORS_ROOT, entry)
        if not os.path.isdir(path):
            continue
        bjson = os.path.join(path, "behavior.json")
        if os.path.isfile(bjson):
            dirs.append(entry)
    return dirs


def load_behavior(name):
    """Carrega o behavior.json de um behavior. Retorna dict ou None."""
    path = os.path.join(BEHAVIORS_ROOT, name, "behavior.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"  [AVISO] Não foi possível carregar {name}/behavior.json: {e}")
        return None


def load_gdscript(name):
    """Carrega o conteúdo do .gd do behavior. Retorna string ou ''."""
    gd_path = os.path.join(BEHAVIORS_ROOT, name, f"{name}.gd")
    if os.path.isfile(gd_path):
        with open(gd_path, "r", encoding="utf-8") as f:
            return f.read()
    return ""


def infer_custo(data, gd_content):
    """Infere custo de performance.

    Heuristica refinada (auditoria 23/07):
    - pesado: tree-level scan, server bypass, raycast em _process, loops grandes
    - medio: _process, fisica, custom draw, particulas, node-level group scan
    - leve: sem _process, logica pura
    """
    name = data.get("name", "")

    if gd_content:
        has_process = "_process(" in gd_content or "_physics_process(" in gd_content

        # PESADO: server bypass, raycast em _process, full-tree-scan em _process
        has_server_bypass = any(token in gd_content for token in [
            "RenderingServer",                 # server bypass
            "PhysicsServer",                   # server bypass
            "PhysicsDirectBodyState",          # direct physics
        ])
        has_raycast = ("RayCast" in gd_content or "raycast" in gd_content)
        has_tree_scan = "get_tree().get_nodes_in_group" in gd_content
        has_heavy_loop = bool(re.search(r"for.*range.*\d{3,}", gd_content))

        # So e pesado se: server bypass, OU raycast+_process, OU tree-scan+_process
        if has_server_bypass:
            return "pesado"
        if has_raycast and has_process:
            return "pesado"
        if has_tree_scan and has_process:
            return "pesado"
        if has_heavy_loop:
            return "pesado"

        # MEDIO: _process, fisica, custom draw, particulas, group scan (tree ou node)
        has_moderate = any(token in gd_content for token in [
            "move_and_slide", "move_and_collide",
            "get_overlapping_bodies", "get_overlapping_areas",
            "test_move",
            "draw_circle", "draw_rect", "draw_line", "draw_polygon",
            "draw_string", "draw_texture",
            "particles", "Particles",
            "get_nodes_in_group",          # node-level group scan
            "get_tree().get_nodes_in_group",  # tree-level, mas sem _process = pontual
        ])

        if has_process or has_moderate:
            return "medio"

        return "leve"

    # Fallback: inferir do CATALOGO pelo tipo de nó e nome
    extends_node = data.get("extends_node", "Node")
    heavy_nodes = {"RigidBody2D"}
    moderate_nodes = {"CharacterBody2D", "Area2D"}

    if extends_node in heavy_nodes:
        return "pesado"
    if extends_node in moderate_nodes:
        return "medio"

    # Heurística por nome
    heavy_names = {"beam_laser", "flocking", "dungeon_generator", "infinite_world",
                   "world_map_generator", "terrain_autotiler", "l_system",
                   "batch_renderer", "server_physics", "server_sprite",
                   "spatial_hash", "match3_grid", "behavior_tree"}
    if name in heavy_names:
        return "pesado"

    moderate_names = {"player_controller", "player_topdown", "enemy_chase",
                      "projectile", "homing_projectile", "area_damage",
                      "line_of_sight", "turret_aim", "grid_movement",
                      "moving_platform", "dash", "wall_slide",
                      "pathfinding", "avoidance", "day_night_cycle",
                      "parallax_background", "camera_follow", "camera_path",
                      "animation_state_machine", "trail", "one_shot_animation"}
    if name in moderate_names:
        return "medio"

    return "leve"


def infer_verbo(name, synonyms):
    """Infere verbo_pt e verbo_en do nome + sinônimos."""
    if name in VERB_MAP:
        return VERB_MAP[name]

    # Fallback: deriva do primeiro sinônimo em cada língua
    pt = synonyms.get("pt", [])
    en = synonyms.get("en", [])

    verbo_pt = pt[0] if pt else name.replace("_", " ")
    verbo_en = en[0] if en else name.replace("_", " ")

    # Garantir que está no infinitivo (PT: termina em -ar/-er/-ir)
    if not any(verbo_pt.endswith(sufixo) for sufixo in ("ar", "er", "ir", "or")):
        verbo_pt = verbo_pt.lower()

    return (verbo_pt, verbo_en)


def infer_nivel(data, gd_content):
    """Infere nível de complexidade."""
    params = data.get("parameters", [])
    deps = data.get("dependencies", [])
    signals = data.get("signals", [])
    control_bools = data.get("control_booleans", [])

    total_params = len(params) + len(control_bools)
    total_deps = len(deps)

    # Avançado: 7+ parâmetros, ou 3+ dependências, ou sinais complexos
    if total_params >= 7 or total_deps >= 3:
        return "avancado"
    if len(signals) >= 5:
        return "avancado"

    # Básico: até 3 parâmetros, sem dependências, sem sinais complexos
    if total_params <= 3 and total_deps == 0 and len(signals) <= 1:
        return "basico"

    # Se .gd tem _get_configuration_warnings ou @export_group → intermediário+
    if gd_content and ("_get_configuration_warnings" in gd_content
                       or "@export_group" in gd_content
                       or "@export_category" in gd_content):
        if total_params <= 5:
            return "intermediario"
        return "avancado"

    return "intermediario"


def infer_combina_bem(name, data, all_data):
    """Infere behaviors que combinam bem com este.

    Heurística baseada em:
    1. Sinais compatíveis (emissor→receptor)
    2. Mesmo gênero + dependências compartilhadas
    3. Pares universais (health, sfx_player, etc.)
    """
    candidates = set()
    genres = set(data.get("genres", []))
    my_signals = {s["name"] for s in data.get("signals", [])}
    my_deps = set(data.get("dependencies", []))
    my_conflicts = set(data.get("conflicts", []))

    for other_name, other in all_data.items():
        if other_name == name:
            continue
        if other_name in SKIP_COMBINE:
            continue
        if other_name in my_conflicts:
            continue

        other_genres = set(other.get("genres", []))
        other_signals = {s["name"] for s in other.get("signals", [])}
        other_deps = set(other.get("dependencies", []))

        score = 0

        # 1. Sinal compatível: eu emito X, outro escuta X?
        for sig in my_signals:
            if sig in KNOWN_COMPATIBLE_PAIRS:
                if other_name in KNOWN_COMPATIBLE_PAIRS[sig]:
                    score += 10
            # Se o outro behavior tem o mesmo sinal (compartilham conceito)
            if sig in other_signals and sig not in ("state_changed",):
                score += 3

        # 2. Outro emite sinal que eu escuto?
        for sig in other_signals:
            if sig in KNOWN_COMPATIBLE_PAIRS:
                if name in KNOWN_COMPATIBLE_PAIRS[sig]:
                    score += 10

        # 3. Compartilham gênero
        shared_genres = genres & other_genres
        if shared_genres:
            score += len(shared_genres) * 2

        # 4. Compartilham dependências
        shared_deps = my_deps & other_deps
        if shared_deps:
            score += len(shared_deps) * 5

        # 5. Um depende do outro
        if other_name in my_deps:
            score += 15
        if name in other_deps:
            score += 15

        # 6. Universal combine
        if other_name in UNIVERSAL_COMBINE:
            score += 5
        if name in UNIVERSAL_COMBINE:
            score += 5

        if score >= 5:
            candidates.add((other_name, score))

    # Ordena por score decrescente, limita a 8
    sorted_candidates = sorted(candidates, key=lambda x: -x[1])
    return [c[0] for c in sorted_candidates[:8]]


def main():
    print("=" * 60)
    print("sota_1.1 — Enriquecer fichas dos behaviors")
    print("=" * 60)

    dirs = get_behavior_dirs()
    print(f"\nBehaviors encontrados: {len(dirs)}")

    # Carrega todos os behavior.json primeiro (precisa para combina_bem)
    all_data = {}
    for name in dirs:
        data = load_behavior(name)
        if data:
            all_data[name] = data

    print(f"Behaviors carregados: {len(all_data)}")

    # Gera propostas
    propostas = {}
    stats = {"leve": 0, "medio": 0, "pesado": 0,
             "basico": 0, "intermediario": 0, "avancado": 0,
             "sem_gd": 0, "com_gd": 0}

    for name in sorted(all_data.keys()):
        data = all_data[name]
        gd_content = load_gdscript(name)

        if gd_content:
            stats["com_gd"] += 1
        else:
            stats["sem_gd"] += 1

        custo = infer_custo(data, gd_content)
        stats[custo] += 1

        verbo_pt, verbo_en = infer_verbo(name, data.get("synonyms", {}))
        nivel = infer_nivel(data, gd_content)
        stats[nivel] += 1

        combina_bem = infer_combina_bem(name, data, all_data)

        propostas[name] = {
            "custo": custo,
            "verbo_pt": verbo_pt,
            "verbo_en": verbo_en,
            "nivel": nivel,
            "combina_bem": combina_bem,
        }

    # Grava o arquivo de propostas
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(propostas, f, ensure_ascii=False, indent=2)

    print(f"\nPropostas gravadas em: {OUTPUT_FILE}")
    print(f"\nDistribuição de custo:")
    print(f"  leve:          {stats['leve']}")
    print(f"  medio:         {stats['medio']}")
    print(f"  pesado:        {stats['pesado']}")
    print(f"\nDistribuição de nível:")
    print(f"  basico:        {stats['basico']}")
    print(f"  intermediario: {stats['intermediario']}")
    print(f"  avancado:      {stats['avancado']}")
    print(f"\nBehaviors com .gd: {stats['com_gd']}")
    print(f"Behaviors sem  .gd: {stats['sem_gd']}")

    # Mostra alguns exemplos
    print("\n--- Exemplos ---")
    for name in ["health", "dash", "beam_laser", "save_load", "enemy_chase",
                 "screen_shake", "dialogue", "camera_follow"]:
        if name in propostas:
            p = propostas[name]
            print(f"\n{name}:")
            print(f"  custo={p['custo']}, nivel={p['nivel']}")
            print(f"  verbo_pt={p['verbo_pt']}, verbo_en={p['verbo_en']}")
            print(f"  combina_bem={p['combina_bem'][:5]}{'...' if len(p['combina_bem']) > 5 else ''}")

    # Estatística de combina_bem
    empty_cb = sum(1 for p in propostas.values() if not p["combina_bem"])
    print(f"\nBehaviors com combina_bem vazio: {empty_cb}")
    avg_cb = sum(len(p["combina_bem"]) for p in propostas.values()) / max(len(propostas), 1)
    print(f"Média de combina_bem por behavior: {avg_cb:.1f}")

    return propostas


if __name__ == "__main__":
    main()
