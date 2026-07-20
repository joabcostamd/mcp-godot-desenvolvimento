# ARSENAL DEFINITIVO DE BEHAVIORS — Catálogo Completo v6.0

**Versão:** 6.0 | **Data:** 2026-07-20
**Local:** `behaviors/` | **Formato:** `behavior.schema.json` v2.0
**Total:** 166 behaviors em 22 categorias + 9 sub-bibliotecas catalogadas
**Pesquisas:** 4 rodadas | **Fontes:** 20+ | **Princípios:** 25

---

## 📚 FONTES DE PESQUISA (3 rodadas)

| Rodada | Fonte | Conteúdo |
|--------|-------|----------|
| 1 | **Nodot** | 113 componentes em 25 categorias |
| 1 | **Game Programming Patterns** | 17 padrões de design (Robert Nystrom) |
| 1 | **Godot Demo Projects** | 41 demos oficiais 2D |
| 1 | **Awesome Godot** | 50+ plugins/addons |
| 2 | **Beehave** | 28 nós BT (GDScript) |
| 2 | **LimboAI** | ~40 tarefas BT+HSM (C++) |
| 2 | **Phantom Camera** | 14 comp. câmera |
| 2 | **Juicee** | 99 efeitos + 12 presets |
| 2 | **Health/Hitbox/Hurtbox** | 7 comp. + 3 resources |
| 2 | **Shaker** | 7 shake types + 7 comp. |
| 2 | **Godot Best Practices** | SOLID, DI, scene org |
| 3 | **Godot Exports Docs** | @export_group, @export_category, @export_storage, @export_tool_button, @export_flags, @export_custom |
| 3 | **Godot Autoload Docs** | Quando usar Autoload vs Regular Node vs Resource vs static |
| 3 | **Godot Data Preferences** | Array vs Dictionary vs Object, Enum int vs string |
| 3 | **Storybook** | Formato ideal de catálogo: Props, Args, Variants, Edge Cases, Stories |
| 3 | **Godot Servers API** | RenderingServer, PhysicsServer2D — bypass nodes para 10k+ objetos |
| 3 | **GDQuest PCG** | RandomWalker, DungeonGen, WorldMap, InfiniteWorld, ModularWeapons |
| 3 | **GPU Instancing** | MultiMeshInstance + vertex shader para milhares de objetos animados |
| 4 | **Data-Oriented Design** | Cache locality, contiguous arrays, packed data, hot/cold splitting, entity-as-ID |
| 4 | **Godex ECS** | Entity Component System nativo para Godot (1.4k stars) |
| 4 | **ECS Patterns** | System processing, component storage, archetype queries, world queries | |

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
17. **@export_group / @export_category** — Agrupar propriedades no inspetor para behaviors complexos
18. **@export_storage** — Propriedades serializadas mas ocultas no editor (evita poluição visual)
19. **@export_tool_button** — Botões clicáveis no inspetor para ações do behavior
20. **Resource > Autoload** — Preferir Resources para dados compartilhados; Autoload só para sistemas de escopo amplo
21. **Cache-friendly data layout** — Arrays contíguos em vez de pointer chasing. Dados processados juntos = armazenados juntos (Data Locality)
22. **Hot/cold splitting** — Separar dados acessados todo frame (hot) dos dados raros (cold). Ex: loot drop info não deve poluir cache da AI
23. **Entity as ID** — Entidade não é classe, é um número. Componentes sabem seu entity ID. Elimina ponteiros e melhora cache
24. **Server API for hot paths** — Behaviors de alta performance (partículas, bullets) usam RenderingServer/PhysicsServer direto, bypassando nós
25. **Branch prediction** — Ordenar entidades por estado ativo (ativas primeiro) para evitar branch misprediction no loop de update

---

## 📐 FORMATO IDEAL DO CATÁLOGO (Storybook-inspired)

Cada behavior no catálogo segue esta estrutura de documentação:

```
## 🏷️ nome_do_behavior
> Categoria | Godot Node | Versão | Status

### 📝 Descrição
PT: ... | EN: ...

### 🎯 Quando Usar
- Cenário 1: ...
- Cenário 2: ...

### ⚡ Quick Start
```gdscript
var comp = NomeBehavior.new()
comp.property = value
add_child(comp)
```

### 🔧 Propriedades
| Nome | Tipo | Range | Default | Descrição |
|------|------|-------|---------|-----------|

### 📡 Sinais
| Nome | Params | Quando Emitido |

### 🔗 Dependências
- behavior_x (obrigatório)
- behavior_y (recomendado)

### ⚠️ Edge Cases
- O que acontece se X for null?
- O que acontece se Y for 0?

### 🧩 Exemplo de Composição
```
Entidade (CharacterBody2D)
  ├── health
  ├── hitbox
  └── enemy_chase
```

### ✅ Cobertura de Testes
- test_a: ...
- test_b: ...

### 📚 Fonte
- Plugin X, Demo Y, Pattern Z
```

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

### 🤝 INTERAÇÃO

| # | Behavior | Godot Node | Parâmetros Chave | Sinais | Fonte | Status |
|---|----------|------------|------------------|--------|-------|--------|
| 94 | `interactable` | Area2D | prompt_text, interaction_range, hold_duration | interacted, focused, unfocused | — | Nodot Interaction3D | ⬜ |
| 95 | `outline` | Node | color, width, show_on_focus | — | — | Nodot Outline3D | ⬜ |
| 96 | `ladder` | Area2D | climb_speed, top_exit, bottom_exit | climbing_started, climbing_ended | — | Nodot Ladder3D | ⬜ |
| 97 | `burnable` | Node | ignition_time, burn_duration, spread_chance | ignited, extinguished, burned_out | health | Nodot Burnable3D | ⬜ |

### 🌐 MULTIPLAYER

| # | Behavior | Godot Node | Parâmetros Chave | Sinais | Fonte | Status |
|---|----------|------------|------------------|--------|-------|--------|
| 98 | `network_sync` | Node | sync_properties, sync_interval | synced, desync_detected | — | Nodot NetworkManager | ⬜ |
| 99 | `lobby` | Node | max_players, game_mode, map | player_joined, player_left, game_started | network_sync | Multiplayer pattern | ⬜ |
| 100 | `authority` | Node | authority_type, transferable | authority_changed | — | Godot multiplayer | ⬜ |
| 101 | `rpc_bridge` | Node | rpc_methods, reliable, channel | rpc_sent, rpc_received | — | Nodot, Godot RPC | ⬜ |

### 🖥️ UI

| # | Behavior | Godot Node | Parâmetros Chave | Sinais | Fonte | Status |
|---|----------|------------|------------------|--------|-------|--------|
| 102 | `accordion` | Control | sections, collapsed, animation_duration | section_toggled | — | Nodot Accordion | ⬜ |
| 103 | `tooltip` | Control | text, show_delay, position | — | — | Padrão UI | ⬜ |
| 104 | `drag_drop` | Control | drag_data, drop_zone, snap | drag_started, dropped, cancelled | — | Padrão UI Godot | ⬜ |
| 105 | `health_bar` | Node2D | target_health, bar_color, show_text, smooth | — | health | Nodot HealthBar3D | ⬜ |

### 💾 DADOS

| # | Behavior | Godot Node | Parâmetros Chave | Sinais | Fonte | Status |
|---|----------|------------|------------------|--------|-------|--------|
| 106 | `storage` | Node | data, persistent, file_path | data_changed, loaded | save_load | Nodot Storage | ⬜ |
| 107 | `event_bus` | Node | event_registry | event_fired, listener_added | — | Nodot GlobalSignal | ⬜ |
| 108 | `blackboard` | Node | variables, scopes | var_set, var_erased, trigger_activated | — | LimboAI, Beehave | ⬜ |

### ⚡ FÍSICA

| # | Behavior | Godot Node | Parâmetros Chave | Sinais | Fonte | Status |
|---|----------|------------|------------------|--------|-------|--------|
| 109 | `buoyancy` | Area2D | fluid_density, drag_coefficient, surface_level | entered_fluid, exited_fluid | — | Nodot WaterArea3D | ⬜ |
| 110 | `conveyor_belt` | Area2D | direction, speed | — | — | Padrão física Godot | ⬜ |
| 111 | `magnet` | Area2D | force, range, target_group, falloff | attracted | — | Padrão física | ⬜ |
| 112 | `gravity_zone` | Area2D | gravity_direction, gravity_strength, override | entered_zone, exited_zone | — | Padrão física | ⬜ |
| 113 | `wind_zone` | Area2D | wind_direction, wind_strength, turbulence | — | — | Padrão física | ⬜ |
| 114 | `spring_joint` | Node | anchor_a, anchor_b, stiffness, damping, rest_length | — | — | Godot PinJoint2D | ⬜ |

### 🎨 SHADERS / VISUAL

| # | Behavior | Godot Node | Parâmetros Chave | Sinais | Fonte | Status |
|---|----------|------------|------------------|--------|-------|--------|
| 115 | `outline_shader` | Node | color, width, pattern | — | — | Nodot outline3d.gdshader | ⬜ |
| 116 | `water_surface` | Node2D | wave_speed, wave_amplitude, color, distortion | — | — | Nodot water.gdshader | ⬜ |
| 117 | `lava_surface` | Node2D | flow_speed, glow_intensity, color | — | — | Nodot lava.gdshader | ⬜ |
| 118 | `dissolve` | Node | progress, edge_width, edge_color, noise_texture | dissolve_finished | — | Shader pattern | ⬜ |
| 119 | `parallax_background` | Node2D | layers, scroll_speed, auto_scroll | — | — | Demo platformer | ⬜ |
| 120 | `lens_flare` | Node2D | flare_texture, intensity, sun_position | — | — | Nodot lens_flare | ⬜ |

### 🎮 GÊNEROS ESPECÍFICOS

| # | Behavior | Godot Node | Parâmetros Chave | Sinais | Fonte | Status |
|---|----------|------------|------------------|--------|-------|--------|
| 121 | `card` | Node | card_data, face_up, draggable, deck_ref | played, drawn, discarded, flipped | deck | Card games | ⬜ |
| 122 | `deck` | Node | cards, shuffle_on_init, draw_pile, discard_pile | shuffled, card_drawn, empty | card | Card games | ⬜ |
| 123 | `hand` | Node | max_cards, fan_angle, card_spacing | card_added, card_removed | card, deck | Card games | ⬜ |
| 124 | `dialogue` | Node | dialogue_tree, speaker, text_speed, choices | line_shown, choice_made, dialogue_ended | — | Dialogic, Dialogue Manager | ⬜ |
| 125 | `shop` | Node | items, prices, discount, restock_interval | item_bought, item_sold, insufficient_funds | currency, inventory | Shop pattern | ⬜ |
| 126 | `crafting` | Node | recipes, ingredients, output | crafted, missing_ingredients, recipe_unlocked | inventory | Crafting pattern | ⬜ |
| 127 | `rhythm_timing` | Node | bpm, tolerance, input_action, beat_offset | perfect, good, miss, beat | audio_manager | Rhythm games | ⬜ |
| 128 | `idle_generator` | Node | resource_per_second, max_storage, upgrade_cost | generated, storage_full, upgraded | currency, upgrade | Idle/clicker | ⬜ |
| 129 | `stealth` | Node | visibility, noise_radius, detection_level | detected, alerted, hidden, suspicious | line_of_sight | Stealth games | ⬜ |
| 130 | `match3_grid` | Node | grid_width, grid_height, gem_types, min_match | match_found, grid_settled, combo | grid_movement | Match-3 games | ⬜ |
| 131 | `racing_lap` | Node | total_laps, checkpoints, best_time | lap_completed, race_finished, checkpoint_passed | — | Racing games | ⬜ |
| 132 | `fishing_cast` | Node | cast_power, lure_type, minigame_difficulty | cast, bite, caught, line_broke | — | Fishing games | ⬜ |
| 133 | `farming_plot` | Node2D | growth_time, stages, water_needed, harvest_yield | planted, stage_changed, ready, harvested | inventory | Farming/life sim | ⬜ |

### 🐛 DEBUG

| # | Behavior | Godot Node | Parâmetros Chave | Sinais | Fonte | Status |
|---|----------|------------|------------------|--------|-------|--------|
| 134 | `debug_position` | Node2D | color, size, show_label, label_text | — | — | Nodot DebugPosition | ⬜ |
| 135 | `debug_arrow` | Node2D | color, length, direction | — | — | Nodot DebugArrowMesh | ⬜ |
| 136 | `debug_console` | Control | max_lines, auto_scroll, command_history | command_entered | — | Developer Console | ⬜ |
| 137 | `fps_counter` | Control | show_min, show_max, show_avg, update_interval | — | — | Padrão debug | ⬜ |

### 👤 PERSONAGEM / CUSTOMIZAÇÃO

| # | Behavior | Godot Node | Parâmetros Chave | Sinais | Fonte | Status |
|---|----------|------------|------------------|--------|-------|--------|
| 138 | `character_stats` | Node | strength, dexterity, intelligence, vitality | stat_changed, stats_loaded | save_load | RPG pattern | ⬜ |
| 139 | `skill_tree` | Node | nodes, connections, unlock_cost, points | node_unlocked, tree_reset, points_changed | character_stats, currency | RPG, Path of Exile | ⬜ |
| 140 | `status_effect` | Node | effect_type, duration, stacks, tick_interval | applied, tick, expired, refreshed | health, character_stats | RPG buff/debuff | ⬜ |
| 141 | `element_system` | Node | elements, weaknesses, resistances, multipliers | damage_modified | health | RPG element wheel | ⬜ |
| 142 | `equipment_slot` | Node | slot_type, equipped_item, slot_bonus | equipped, unequipped, bonus_applied | inventory, character_stats | RPG gear | ⬜ |
| 143 | `character_creator` | Control | customizable_parts, color_palette, presets | part_changed, saved, loaded | save_load | Char creation | ⬜ |

### 🏪 SOCIAL / ONLINE

| # | Behavior | Godot Node | Parâmetros Chave | Sinais | Fonte | Status |
|---|----------|------------|------------------|--------|-------|--------|
| 144 | `leaderboard` | Node | entries, score_type, time_scope | score_submitted, rankings_loaded | network_sync | Online pattern | ⬜ |
| 145 | `daily_reward` | Node | rewards, streak_bonus, reset_time | claimed, streak_updated, missed | save_load | Mobile/gacha | ⬜ |
| 146 | `achievement_tracker` | Node | achievements, secret_flags, progress | unlocked, progress_updated, all_completed | save_load | Xbox/Steam style | ⬜ |

### 🎬 CINEMÁTICA / NARRATIVA

| # | Behavior | Godot Node | Parâmetros Chave | Sinais | Fonte | Status |
|---|----------|------------|------------------|--------|-------|--------|
| 147 | `cutscene` | Node | timeline, skippable, pause_game | started, finished, skipped | input_manager | Godot AnimationPlayer | ⬜ |
| 148 | `camera_sequence` | Node | shots, transitions, duration | shot_changed, sequence_finished | camera_follow, cutscene | Cinemachine | ⬜ |

### ♿ ACESSIBILIDADE

| # | Behavior | Godot Node | Parâmetros Chave | Sinais | Fonte | Status |
|---|----------|------------|------------------|--------|-------|--------|
| 149 | `color_blind_mode` | Node | mode (protanopia/deuteranopia/tritanopia), intensity | mode_changed | — | GATO toolkit | ⬜ |
| 150 | `subtitle` | Node | text, speaker, duration, style | shown, hidden | dialogue | AAA accessibility | ⬜ |
| 151 | `controller_remap` | Control | actions, rebindable, presets | rebound, reset, preset_loaded | input_manager | Godot Input Map | ⬜ |

### 🌍 LOCALIZAÇÃO

| # | Behavior | Godot Node | Parâmetros Chave | Sinais | Fonte | Status |
|---|----------|------------|------------------|--------|-------|--------|
| 152 | `localization` | Node | locale, fallback, csv_file, auto_detect | locale_changed | — | Godot TranslationServer | ⬜ |
| 153 | `tutorial_overlay` | Control | steps, highlights, skip_enabled | step_completed, tutorial_finished, skipped | input_manager, save_load | Mobile/console | ⬜ |

### 🎲 GERAÇÃO PROCEDURAL

| # | Behavior | Godot Node | Parâmetros Chave | Sinais | Fonte | Status |
|---|----------|------------|------------------|--------|-------|--------|
| 154 | `random_walker` | Node | grid_size, steps, room_templates, seed | generation_started, step_placed, generation_finished | — | GDQuest PCG, Spelunky | ⬜ |
| 155 | `dungeon_generator` | Node | room_count, min_size, max_size, corridor_width, seed | generation_started, room_placed, corridors_done, finished | — | GDQuest PCG | ⬜ |
| 156 | `world_map_generator` | Node | width, height, biomes, rivers, seed | biome_generated, river_placed, map_finished | — | GDQuest PCG | ⬜ |
| 157 | `infinite_world` | Node | chunk_size, view_distance, noise_params, seed | chunk_loaded, chunk_unloaded | object_pool | GDQuest PCG, Minecraft-like | ⬜ |
| 158 | `modular_weapon` | Node | barrel, stock, magazine, scope, modifier | weapon_assembled, stat_recalculated | inventory | Binding of Isaac, Gungeon | ⬜ |
| 159 | `l_system` | Node2D | axiom, rules, iterations, angle, length | generation_finished | — | L-System (plantas, fractais) | ⬜ |
| 160 | `noise_generator` | Node | noise_type, frequency, amplitude, seed, octaves | — | — | Perlin, Simplex, Voronoi | ⬜ |

### ⚡ PERFORMANCE / OTIMIZAÇÃO

| # | Behavior | Godot Node | Parâmetros Chave | Sinais | Fonte | Status |
|---|----------|------------|------------------|--------|-------|--------|
| 161 | `batch_renderer` | Node | max_instances, mesh, material, cull_distance | batch_full, instance_added | — | MultiMeshInstance, GPU instancing | ⬜ |
| 162 | `server_sprite` | Node | texture, position, scale, modulate | — | — | RenderingServer (bypass nodes) | ⬜ |
| 163 | `server_physics` | Node | shape, body_mode, collision_layer | body_moved | — | PhysicsServer2D (bypass nodes) | ⬜ |
| 164 | `lod_controller` | Node | lod_levels, distances, current_lod | lod_changed | — | Level of Detail | ⬜ |
| 165 | `dirty_flag` | Node | tracked_properties | dirty, clean | — | Game Prog Patterns (ch.12) | ⬜ |
| 166 | `spatial_hash` | Node | cell_size, world_bounds | — | — | Spatial partitioning | ⬜ |

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

## 🏛️ ARQUITETURA ECS (Entity Component System)

Nossos behaviors seguem o padrão ECS indiretamente. Documentar isso é crucial:

### ECS vs Nossa Arquitetura

| Conceito ECS | Nosso Equivalente |
|-------------|-------------------|
| **Entity** | Nó Godot (CharacterBody2D, Node2D) — o "dono" dos behaviors |
| **Component** | Behavior (`health`, `projectile`) — nó filho com dados + sinais |
| **System** | Game loop do Godot (`_process`, `_physics_process`) — processa componentes |

### Princípios ECS aplicados
- **Composição sobre Herança** — Entidade ganha comportamento adicionando behaviors como filhos
- **Dados + Comportamento juntos** — Diferente do ECS puro, nossos componentes têm lógica (GDScript)
- **Comunicação por sinais** — Components não se referenciam diretamente; usam signals (Observer pattern)
- **Processamento por domínio** — Systems processam componentes por tipo (AI → Physics → Render)

### Quando usar ECS puro (Godex)
- 10.000+ entidades simultâneas
- Precisam de processamento multithreaded
- Dados precisam de layout cache-friendly extremo

---

## 📅 ROADMAP DE IMPLEMENTAÇÃO

| Fase | Behaviors | Meta | Status |
|------|-----------|------|--------|
| **1. Core Loop** | health, projectile, hitbox, hurtbox, player_controller, enemy_chase, state_machine, fire_rate | 8 | 2/8 ✅ |
| **2. Combate** | knockback, homing_projectile, area_damage, damage_over_time, critical_hit, hitscan | 6 | ⬜ |
| **3. IA/Mundo** | enemy_patrol, line_of_sight, spawner_wave, turret_aim, flee, flocking, stealth | 7 | ⬜ |
| **4. Progressão** | inventory, collectable, currency, xp_level, upgrade, save_load, quest, achievement, shop, crafting | 10 | ⬜ |
| **5. Feedback** | screen_shake, floating_text, particle_impact, hit_stop, screen_flash, camera_follow, camera_shake, trail, tween_player, health_bar | 10 | ⬜ |
| **6. Sistema** | pause, scene_transition, audio_manager, sfx_player, settings, checkpoint, object_pool, timer, time_scale, day_night_cycle, dialogue | 11 | ⬜ |
| **7. PCG + Perf** | random_walker, dungeon_generator, infinite_world, noise_generator, batch_renderer, lod_controller, dirty_flag, spatial_hash, modular_weapon | 9 | ⬜ |
| **8. Gêneros** | card, deck, dialogue, rhythm_timing, idle_generator, match3_grid, racing_lap, fishing_cast, farming_plot, stealth, character_stats, skill_tree, status_effect | 13 | ⬜ |
| **9. Multiplayer + Social** | network_sync, lobby, authority, rpc_bridge, leaderboard, daily_reward, achievement_tracker | 7 | ⬜ |
| **10. Acessibilidade + Localização** | color_blind_mode, subtitle, controller_remap, localization, tutorial_overlay, character_creator, cutscene, camera_sequence | 8 | ⬜ |

---

## 🎯 MÉTRICAS DE SUCESSO

- **30 behaviors → ONDA 2 completa** (taxa de correção < 15%)
- **50 behaviors → 90% dos gêneros 2D**
- **100 behaviors → Biblioteca líder do ecossistema Godot 2D**
- **166 behaviors → Arsenal planetário — produção, performance, gêneros, acessibilidade**
