# ARSENAL DEFINITIVO DE BEHAVIORS — Catálogo Completo v3.0

**Versão:** 3.0 | **Data:** 2026-07-20
**Local:** `behaviors/` | **Formato:** `behavior.schema.json` v2.0

---

## 📚 FONTES DE PESQUISA (2 rodadas)

| Rodada | Fonte | Conteúdo |
|--------|-------|----------|
| 1 | **Nodot** | 113 componentes em 25 categorias (biblioteca referência) |
| 1 | **Game Programming Patterns** | 17 padrões de design (Robert Nystrom) |
| 1 | **Godot Demo Projects** | 41 demos oficiais 2D (cada um = um sistema) |
| 1 | **Awesome Godot** | 50+ plugins/addons com componentes reutilizáveis |
| 2 | **Beehave** | 28 nós de Behavior Tree (GDScript) |
| 2 | **LimboAI** | ~40 tarefas BT + HSM (C++/GDExtension) |
| 2 | **Phantom Camera** | 14 comportamentos de câmera (Cinemachine-like) |
| 2 | **Juicee** | 99 efeitos de game-feel + 12 presets |
| 2 | **Health/Hitbox/Hurtbox** | 7 componentes + 3 resources (cluttered-code) |
| 2 | **Shaker** | 7 tipos de shake + 7 componentes (Emitter/Receiver) |
| 2 | **Godot Best Practices** | SOLID, DI, scene organization (docs oficial) |

---

## 🏗️ PRINCÍPIOS DE DESIGN (16 regras)

### Regra de Ouro
Composição > Herança. Todo behavior é um **nó filho independente**.

### Estrutura canônica
```
behaviors/<nome>/
  behavior.json     — metadados (schema validado)
  <nome>.gd         — @tool, @export, class_name
  <nome>.tscn       — cena plugável
  test_<nome>.gd    — GdUnit4
  README.md         — busca semântica
```

### Regras
1. Parâmetro sem `range` declarado = proibido
2. Nome distinguível (Levenshtein < 75%)
3. Teste obrigatório (sem teste = `auditar.py` falha)
4. Um por fatia (nunca em lote)
5. Dependência explícita no `behavior.json`
6. Sinais documentados com `description_pt` e `params` tipados
7. **Booleans de controle** — `damageable`, `healable`, `killable`, `revivable`
8. **HealthAction como Resource** — Dano/cura não é `int`, é Resource com type+multiplier
9. **HitBox ≠ HurtBox** — Arma causa dano, corpo recebe
10. **Presets** — `preset_hit`, `preset_explosion` prontos para usar
11. **Emitter/Receiver** — Emissores criam, receptores reagem com atenuação
12. **_get_configuration_warnings()** — Auto-documentação no editor ⚠️
13. **Dependency Injection via signals** — Zero hard references
14. **Single Responsibility (SOLID)** — Um behavior = UMA responsabilidade
15. **Scenes > Scripts** — `.tscn` carrega mais rápido
16. **BT como sub-biblioteca** — 28+ nós com Blackboard

---

## 📋 CATÁLOGO MASTER — 100+ Behaviors (especificação completa)

> **Legenda:** ✅ = implementado | 🔨 = em progresso | ⬜ = planejado | 📋 = catalogado (fonte externa)

### 🏃 MOVIMENTO

| # | Behavior | Godot Node | Parâmetros Chave | Sinais | Dependências | Fonte | Status |
|---|----------|------------|------------------|--------|-------------|-------|--------|
| 1 | `player_controller` | CharacterBody2D | speed, jump_velocity, gravity | player_died | — | Template existente | 📋 |
| 2 | `player_topdown` | CharacterBody2D | speed, acceleration, friction | — | — | Demo 2D | ⬜ |
| 3 | `player_vehicle` | CharacterBody2D | acceleration, max_speed, turn_rate, drift | — | — | Demo physics | ⬜ |
| 4 | `moving_platform` | AnimatableBody2D | path, speed, loop, pause_at_ends | — | — | Demo platformer | ⬜ |
| 5 | `dash` | Node | dash_speed, dash_duration, cooldown | dashed, dash_ready | player_controller | Celeste, GDQuest | ⬜ |
| 6 | `double_jump` | Node | jump_count, coyote_time | jumped, jump_used | player_controller | Plataforma | ⬜ |
| 7 | `wall_slide` | Node | slide_speed, wall_jump_force | wall_sliding, wall_jumped | player_controller | Metroidvania | ⬜ |
| 8 | `grid_movement` | Node | grid_size, move_duration, snap | moved, arrived | — | Roguelike, puzzle | ⬜ |

### ⚔️ COMBATE

| # | Behavior | Godot Node | Parâmetros Chave | Sinais | Dependências | Fonte | Status |
|---|----------|------------|------------------|--------|-------------|-------|--------|
| 9 | `health` | Node | max_hp, current_hp, invulnerable_time, damageable, healable, killable, revivable | died, damage_taken, healed, hp_changed, first_hit, full, damage_blocked, heal_blocked | — | Health/Hitbox/Hurtbox, Nodot | ✅ v1.1 |
| 10 | `projectile` | Area2D | speed, damage, lifetime, max_distance, piercing | hit, expired | health | Nodot Projectile3D | ✅ v1.0 |
| 11 | `hitbox` | Area2D | damage, knockback_force, hit_type, active | hit_dealt | health | cluttered-code, Nodot | 🔨 |
| 12 | `hurtbox` | Area2D | damage_multiplier, hurt_type | hit_received | health | cluttered-code | 🔨 |
| 13 | `fire_rate` | Node | fire_interval, burst_count, burst_delay | fired, ready | projectile | Nodot Magazine | ⬜ |
| 14 | `knockback` | Node | force, duration, damping | knocked_back | health | Padrão combate | ⬜ |
| 15 | `critical_hit` | Node | crit_chance, crit_multiplier | crit_landed | health | RPG pattern | ⬜ |
| 16 | `damage_over_time` | Node | damage_per_tick, tick_interval, duration, type | dot_tick, dot_ended | health | RPG pattern | ⬜ |
| 17 | `area_damage` | Area2D | damage, radius, falloff, explosion_force | exploded | health, knockback | Nodot Explosion3D | ⬜ |
| 18 | `homing_projectile` | Area2D | speed, turn_rate, lock_range | hit, expired | projectile | Bullet hell | ⬜ |
| 19 | `beam_laser` | RayCast2D | damage_per_second, beam_width, max_range | hitting, stopped | health | Nodot Laser3D | ⬜ |
| 20 | `hitscan` | RayCast2D | damage, range, fire_method | fired, hit | health | cluttered-code Hitscan | ⬜ |

### 👾 INIMIGO / AI

| # | Behavior | Godot Node | Parâmetros Chave | Sinais | Dependências | Fonte | Status |
|---|----------|------------|------------------|--------|-------------|-------|--------|
| 21 | `enemy_chase` | Node | speed, chase_range, lose_range | target_lost, target_acquired | — | Template existente | 📋 |
| 22 | `enemy_patrol` | Node | waypoints, wait_time, loop, ping_pong | waypoint_reached, patrol_complete | state_machine | Nodot, LimboAI | ⬜ |
| 23 | `line_of_sight` | Area2D | view_angle, view_range, ray_count | target_spotted, target_lost | — | Nodot ViewCone3D | ⬜ |
| 24 | `spawner_wave` | Node | spawn_table, wave_interval, max_active, spawn_area | wave_started, wave_cleared, all_waves_done | object_pool | Nodot Spawner3D | ⬜ |
| 25 | `state_machine` | Node | states, transitions, default_state | state_changed, state_entered, state_exited | — | Nodot, Beehave, LimboAI | ⬜ |
| 26 | `behavior_tree` | Node | tree_resource, tick_rate | tree_started, tree_stopped | blackboard | LimboAI, Beehave | ⬜ |
| 27 | `flee` | Node | flee_speed, safe_distance, flee_condition | fleeing, safe | health, state_machine | Padrão IA | ⬜ |
| 28 | `flocking` | Node | separation, alignment, cohesion, neighbor_radius | — | — | Padrão IA (boids) | ⬜ |
| 29 | `turret_aim` | Node2D | rotation_speed, range, predict_movement | target_locked, target_lost, fired | fire_rate, projectile | Tower defense | ⬜ |

### 📦 PROGRESSÃO

| # | Behavior | Godot Node | Parâmetros Chave | Sinais | Dependências | Fonte | Status |
|---|----------|------------|------------------|--------|-------------|-------|--------|
| 30 | `inventory` | Node | slot_count, max_stack, items | item_added, item_removed, inventory_full | — | Nodot CollectableInventory | ⬜ |
| 31 | `collectable` | Area2D | item_id, quantity, auto_pickup, magnet_range | collected | inventory | Nodot Collectable | ⬜ |
| 32 | `xp_level` | Node | xp_table, current_xp, current_level | leveled_up, xp_gained | — | RPG pattern | ⬜ |
| 33 | `upgrade` | Node | upgrade_options, max_level | upgraded, upgrade_available | xp_level | Survivors-like | ⬜ |
| 34 | `currency` | Node | currency_type, amount | gained, spent, insufficient | — | Padrão universal | ⬜ |
| 35 | `quest` | Node | quests, progress, rewards | quest_started, quest_completed, quest_failed | inventory, currency | Quest Manager | ⬜ |
| 36 | `achievement` | Node | achievements, conditions | unlocked, progress_updated | — | Padrão plataforma | ⬜ |
| 37 | `unlockable` | Node | unlocks, conditions | unlocked | save_load | Metaprogression | ⬜ |

### 💾 SISTEMA

| # | Behavior | Godot Node | Parâmetros Chave | Sinais | Dependências | Fonte | Status |
|---|----------|------------|------------------|--------|-------------|-------|--------|
| 38 | `save_load` | Node | save_slot, auto_save_interval | saved, loaded, save_error | — | Nodot SaveManager | ⬜ |
| 39 | `pause` | Node | pause_mode, time_scale_on_pause | paused, resumed | — | Nodot Pause | ⬜ |
| 40 | `main_menu` | Control | scene_refs, transition_type | play_pressed, settings_pressed, quit_pressed | scene_transition | Template menu_main.tscn | 📋 |
| 41 | `settings` | Control | audio_bus, resolution, fullscreen, language | setting_changed | save_load, audio_manager | Padrão Godot | ⬜ |
| 42 | `scene_transition` | Node | transition_type, duration, loading_screen | transition_started, transition_finished | — | Padrão Godot | ⬜ |
| 43 | `audio_manager` | Node | music_bus, sfx_bus, master_volume | — | — | Nodot AudioManager | ⬜ |
| 44 | `input_manager` | Node | action_map, device_type | device_changed, action_rebound | — | Nodot InputManager | ⬜ |
| 45 | `time_scale` | Node | scale, duration, easing | scale_changed | — | Nodot TimeScale | ⬜ |
| 46 | `checkpoint` | Area2D | spawn_scene, active | checkpoint_activated, player_respawned | save_load | Padrão plataforma | ⬜ |
| 47 | `object_pool` | Node | pool_size, prefab, expandable | object_taken, object_returned, pool_empty | — | Nodot NodePool | ⬜ |

### 🎬 FEEDBACK / GAME FEEL

| # | Behavior | Godot Node | Parâmetros Chave | Sinais | Dependências | Fonte | Status |
|---|----------|------------|------------------|--------|-------------|-------|--------|
| 48 | `screen_shake` | Node | amplitude, frequency, duration, decay | shake_started, shake_finished | — | Nodot, Juicee, Shaker | ⬜ |
| 49 | `floating_text` | Node2D | text, color, speed, lifetime, fade | text_shown | — | Nodot TextEmitter, Juicee | ⬜ |
| 50 | `particle_impact` | Node2D | particle_scene, count, spread | played | — | Padrão universal | ⬜ |
| 51 | `hit_stop` | Node | duration, time_scale_target | hit_stopped, resumed | time_scale | Juicee | ⬜ |
| 52 | `screen_flash` | ColorRect | color, duration, fade_in, fade_out | flashed | — | Padrão universal | ⬜ |
| 53 | `camera_zoom` | Node | zoom_target, duration, easing | zoomed | — | Juicee | ⬜ |
| 54 | `color_pulse` | Node | color, frequency, amplitude | pulsing | — | Nodot shader | ⬜ |
| 55 | `trail` | Node2D | length, width, color, fade | — | — | Godot trail system | ⬜ |
| 56 | `tween_player` | Node | property, target, duration, easing, delay | tween_finished | — | Easing patterns | ⬜ |
| 57 | `chromatic_aberration` | Node | intensity, duration | — | — | Juicee | ⬜ |
| 58 | `vignette` | Node | intensity, color, smoothness | — | — | Juicee | ⬜ |
| 59 | `freeze_frame` | Node | duration, time_scale | frozen, resumed | time_scale | Juicee | ⬜ |
| 60 | `glitch` | Node | intensity, interval | — | — | Juicee | ⬜ |

### 🏆 ESTRUTURA DE JOGO

| # | Behavior | Godot Node | Parâmetros Chave | Sinais | Dependências | Fonte | Status |
|---|----------|------------|------------------|--------|-------------|-------|--------|
| 61 | `round_timer` | Node | duration, countdown, pause_on_end | tick, round_started, round_ended, time_up | pause | Padrão arcade | ⬜ |
| 62 | `victory_condition` | Node | condition_type, target_value | victory_achieved | — | Padrão universal | ⬜ |
| 63 | `defeat_condition` | Node | condition_type, target_value | defeat_triggered | — | Padrão universal | ⬜ |
| 64 | `score` | Node | initial_score, combo_multiplier | score_changed, new_high_score, combo_reached | — | Padrão arcade | ⬜ |
| 65 | `wave_system` | Node | waves, spawn_interval, difficulty_ramp | wave_started, wave_cleared | spawner_wave | Survivors-like | ⬜ |
| 66 | `difficulty_curve` | Node | curve_resource, current_point | difficulty_changed | — | Padrão design | ⬜ |
| 67 | `random_loot` | Node | loot_table, rarity_weights | loot_dropped, rare_drop | inventory | RPG pattern | ⬜ |
| 68 | `day_night_cycle` | Node | day_duration, night_duration, start_time | dawn, dusk, time_changed | — | Demo/plugin Godot | ⬜ |

### 🎥 CÂMERA (Phantom Camera + Godot)

| # | Behavior | Godot Node | Parâmetros Chave | Sinais | Fonte | Status |
|---|----------|------------|------------------|--------|-------|--------|
| 69 | `camera_follow` | Node | target, offset, damping, look_ahead | — | Phantom Camera Glued/Simple | ⬜ |
| 70 | `camera_shake` | Node | amplitude, frequency, duration, decay | shake_started, shake_finished | Juicee, Shaker | ⬜ |
| 71 | `camera_framed` | Node | dead_zone, soft_zone, damping | target_entered_dead_zone | Phantom Camera Framed | ⬜ |
| 72 | `camera_priority` | Node | priority, transition_duration, easing | camera_activated | Phantom Camera | ⬜ |
| 73 | `camera_path` | Node | path, speed, look_ahead | waypoint_reached | Phantom Camera Path | ⬜ |
| 74 | `camera_lookat` | Node | target, offset, damping | — | Phantom Camera LookAt | ⬜ |
| 75 | `camera_zoom` | Node | zoom_min, zoom_max, zoom_speed | zoomed | Phantom Camera Zoom | ⬜ |

### 🎯 MIRA / ARMA

| # | Behavior | Godot Node | Parâmetros Chave | Sinais | Fonte | Status |
|---|----------|------------|------------------|--------|-------|--------|
| 76 | `crosshair` | Node2D | style, color, size, show_on_aim | — | Nodot CrossHair | ⬜ |
| 77 | `recoil` | Node | recoil_amount, recovery_speed, max_spread | — | Padrão FPS | ⬜ |
| 78 | `spread` | Node | base_spread, spread_per_shot, max_spread, recovery | — | Padrão shooter | ⬜ |
| 79 | `fire_mode` | Node | mode (auto/burst/semi), burst_count, rpm | mode_changed | fire_rate | Nodot Magazine | ⬜ |

### 📐 NAVEGAÇÃO

| # | Behavior | Godot Node | Parâmetros Chave | Sinais | Fonte | Status |
|---|----------|------------|------------------|--------|-------|--------|
| 80 | `pathfinding` | Node | target, speed, avoidance_enabled | path_found, path_lost, arrived | NavigationAgent2D | Godot | ⬜ |
| 81 | `avoidance` | Node | radius, priority, max_speed | — | pathfinding | Godot | ⬜ |
| 82 | `patrol_route` | Node | waypoints, loop, wait_time | waypoint_reached | pathfinding | LimboAI | ⬜ |

### 🔊 ÁUDIO

| # | Behavior | Godot Node | Parâmetros Chave | Sinais | Fonte | Status |
|---|----------|------------|------------------|--------|-------|--------|
| 83 | `sfx_player` | Node | audio_stream, volume_db, pitch_scale, bus | played, finished | audio_manager | Nodot SFXPlayer | ⬜ |
| 84 | `music_playlist` | Node | playlist, shuffle, crossfade_duration | track_changed, playlist_finished | audio_manager | Nodot AudioManager | ⬜ |
| 85 | `ambience_zone` | Area2D | audio_stream, volume, attenuation | entered_zone, exited_zone | audio_manager | Nodot AmbienceArea3D | ⬜ |

### 🧩 UTILITÁRIOS

| # | Behavior | Godot Node | Parâmetros Chave | Sinais | Fonte | Status |
|---|----------|------------|------------------|--------|-------|--------|
| 86 | `timer` | Node | duration, one_shot, auto_start, paused | timeout, tick | Padrão universal | ⬜ |
| 87 | `counter` | Node | initial_value, min, max, step | value_changed, min_reached, max_reached | Nodot Counter | ⬜ |
| 88 | `follow_path` | Node | path, speed, loop, look_along | path_finished | Padrão Godot | ⬜ |
| 89 | `look_at_target` | Node | target, rotation_speed, offset | — | Padrão universal | ⬜ |
| 90 | `trigger_zone` | Area2D | trigger_once, trigger_group | entered, exited | Padrão Godot | ⬜ |
| 91 | `destructible` | Node2D | hits_to_break, destroy_effect, drop_table | damaged, destroyed | health | Nodot Breakable | ⬜ |
| 92 | `teleport` | Area2D | target_position, target_scene, transition | teleported | scene_transition | Nodot Teleport3D | ⬜ |
| 93 | `lerp_smooth` | Node | property, target_value, duration, easing | completed | Padrão universal | ⬜ |

---

## 🧠 BEHAVIOR TREE — Sub-biblioteca (Beehave + LimboAI)

### Composites (8)
| Nó | Beehave | LimboAI | Propósito |
|----|---------|---------|-----------|
| Sequence | ✅ | ✅ | Executa filhos em ordem, para no primeiro FAILURE |
| Selector | ✅ | ✅ | Tenta cada filho até o primeiro SUCCESS (fallback) |
| Parallel | ✅ Simple | ✅ Real | Executa filhos simultaneamente |
| Random Sequence | ✅ | ✅ | Ordem aleatória dos filhos |
| Random Selector | ✅ | ✅ | Seleção aleatória |
| Dynamic Sequence | Reactive | ✅ | Reavalia condições anteriores a cada tick |
| Dynamic Selector | Reactive | ✅ | Reavalia condições anteriores a cada tick |
| Probability | ❌ | ✅ | Selector ponderado por probabilidades |

### Decorators (10)
| Nó | Propósito |
|----|-----------|
| Inverter | Inverte SUCCESS ↔ FAILURE |
| AlwaysSucceed | Sempre retorna SUCCESS |
| AlwaysFail | Sempre retorna FAILURE |
| Delay | Atrasa execução por N segundos |
| Cooldown | Bloqueia re-execução por N segundos |
| Repeater | Repete N vezes |
| RepeatUntilFailure | Repete até FAILURE |
| RepeatUntilSuccess | Repete até SUCCESS (LimboAI) |
| Limiter | Limita a N execuções totais |
| TimeLimiter | Limita a N segundos de execução |

### Leaves / Tasks (15)
| Nó | Propósito |
|----|-----------|
| BTWait | Aguarda N segundos |
| BTRandomWait | Aguarda tempo aleatório |
| BTCallMethod | Chama método no agente |
| BTEvaluateExpression | Avalia expressão como condição |
| BTCheckVar / BTCheckAgentProperty | Verifica variável/propriedade |
| BTSetVar / BTSetAgentProperty | Atribui variável/propriedade |
| BTPlayAnimation | Toca animação |
| BTAwaitAnimation | Aguarda animação terminar |
| BTCheckTrigger | Aguarda trigger no Blackboard |
| BTSubtree | Executa outra BT como subárvore |
| BTForEach | Itera sobre array do Blackboard |
| BTConsolePrint | Debug |
| BTFail | Sempre falha |
| BTComment | Nó de comentário |

---

## 🧃 JUICEE — Catálogo de Efeitos (99 efeitos)

| Categoria | Efeitos |
|-----------|---------|
| **Screen (18)** | Chromatic, Vignette, Blur, Pixelate, Glitch, Color Grade, Screen Tint, Screen Wipe, Bloom, Tonemap, Shockwave, Cinematic Bars, Scan Lines, Speed Lines, Film Grain, Radial Blur, Lens Distortion, Depth of Field |
| **Camera (9)** | Shake 2D/3D, Zoom, FOV 3D, Follow, Directional Shake, Camera Bob, Zoom Pulse, Dutch Tilt |
| **Object (37)** | Flash, Modulate, Bounce, Jiggle, Position 2D/3D, Rotation 2D/3D, Trail, Burst, Confetti, Light Flash, Spring, Ambient Flash, Strobe, Recoil, Outline, Color Cycle, Spin, Wiggle, Sprite Bob, Pop In, Shake Control, Pulse, Shader Param, Flicker, Scale To, Particle Control, Light 3D Flash, Material 3D, Fade, Flip, Instantiate, Size Delta, Impact Ring, Sway, Scale 3D |
| **Text (7)** | Damage Number (crit), Floating Text, Button Punch, Typewriter, Number Count, Text Wobble, Text Scramble |
| **Time (5)** | Hit Stop, Time Scale Ramp, Delay, Freeze Frame, Stutter |
| **Audio (8)** | Sound, Music Duck, Rumble, Reverb, Pitch Shift, Low-Pass, Audio Source 3D, Distortion |
| **Flow (12)** | Sequence, Property Tween, Animation Player, Set Active, Chain, Beat Sync, Wait For Input, Emit Signal, Debug Log, Animation Tree, Set Property, Auto Destruct |

### Presets Juicee (12)
`preset_hit`, `preset_hit_crit`, `preset_explosion`, `preset_level_up`, `preset_damage_taken`, `preset_death`, `preset_combo`, `preset_dash`, `preset_pickup`, `preset_boss_intro`, `preset_low_health_pulse`, `preset_victory`

---

## 📷 PHANTOM CAMERA — Catálogo

| Follow Modes (6) | Look At Modes (3) | Features (5) |
|---|---|---|
| Glued, Simple, Group, Path, Framed, Third Person | Mimic, Simple, Group | Priority, Zoom, Tween, Viewfinder, C# |

---

## 🔨 SHAKER — 7 Tipos de Shake

| Tipo | Comportamento |
|------|---------------|
| SineWave, SquareWave, SawtoothWave | Ondas periódicas |
| Random, BrownianShake, NoiseShake | Ruído/aleatoriedade |
| Curve | Arbitrário via Curve resource |

### Componentes Shaker (7)
`ShakerComponent`, `ShakerComponent2D/3D`, `ShakerEmitter2D/3D`, `ShakeReceiver2D/3D`

---

## 🔗 DEPENDÊNCIAS CRÍTICAS

```
health ← hitbox, hurtbox, enemy_chase, spawner_wave, damage_over_time, knockback, critical_hit
projectile ← fire_rate, homing_projectile, beam_laser, turret_aim, hitscan
player_controller ← dash, double_jump, wall_slide
save_load ← inventory, currency, quest, achievement, settings, checkpoint
state_machine ← enemy_patrol, flee, turret_aim
object_pool ← spawner_wave, particle_impact, floating_text
audio_manager ← sfx_player, music_playlist, ambience_zone
time_scale ← hit_stop, freeze_frame, pause
```

---

## 🤖 SISTEMA DE GERAÇÃO AUTOMÁTICA (Behavior Factory)

### Pipeline
1. `behavior.json` validado contra `behavior.schema.json`
2. Template engine (Jinja2) preenche templates base
3. Geração: `.gd` + `.tscn` + `test_*.gd` + `README.md`
4. Validação: `auditar.py` + `validate_gdscript.py` + `contract_snapshot`
5. Aprovação humana → catálogo

### Template Types
- `node_component` → extends Node (health, state_machine, timer)
- `area_component` → extends Area2D (hitbox, hurtbox, trigger_zone)
- `body_component` → extends CharacterBody2D (player_controller, enemy_chase)
- `visual_component` → extends Node2D (floating_text, particle_impact, trail)
- `singleton_component` → autoload (save_load, audio_manager, input_manager)

---

## 📅 ROADMAP DE IMPLEMENTAÇÃO

| Fase | Behaviors | Meta | Status |
|------|-----------|------|--------|
| **1. Core Loop** | health, projectile, hitbox, hurtbox, player_controller, enemy_chase, state_machine, fire_rate | 8 | 2/8 ✅ |
| **2. Combate** | knockback, homing_projectile, area_damage, damage_over_time, critical_hit, hitscan | 6 | ⬜ |
| **3. IA/Mundo** | enemy_patrol, line_of_sight, spawner_wave, turret_aim, flee, flocking | 6 | ⬜ |
| **4. Progressão** | inventory, collectable, currency, xp_level, upgrade, save_load | 6 | ⬜ |
| **5. Sistema/Feedback** | pause, scene_transition, screen_shake, floating_text, hit_stop, particle_impact, camera_follow, camera_shake | 8 | ⬜ |
| **6. BT + Avançado** | behavior_tree, bt_sequence, bt_selector, bt_cooldown, pathfinding, object_pool | 6 | ⬜ |
| **7. Áudio + UI** | audio_manager, sfx_player, music_playlist, settings, crosshair | 5 | ⬜ |
| **8. Polimento** | chromatic_aberration, freeze_frame, recoil, spread, checkpoint, destructible, teleport | 7 | ⬜ |

---

## 🎯 MÉTRICAS DE SUCESSO

- **30 behaviors → ONDA 2 completa** (taxa de correção < 15% em jogo novo)
- **50 behaviors → 90% dos gêneros 2D cobertos**
- **93 behaviors → biblioteca mais completa do ecossistema Godot 2D**
