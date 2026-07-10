"""juice_ops.py — Game feel / juice automatizado (GRATIS, Onda 5).

Gera codigo GDScript com tecnicas de polish profissional:
coyote time, input buffer, hit-stop, screen shake, squash & stretch, easing.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

_JUICE_PRESETS = {
    "platformer": {"description": "Coyote time + input buffer + squash/stretch no pulo",
                   "techniques": ["coyote_time", "input_buffer", "squash_stretch", "particles_land"]},
    "action": {"description": "Hit-stop + screen shake + particulas de impacto",
               "techniques": ["hit_stop", "screen_shake", "particles_impact", "easing_attack"]},
    "full": {"description": "Todas as tecnicas: pacote completo de polish",
             "techniques": ["coyote_time", "input_buffer", "hit_stop", "screen_shake",
                           "squash_stretch", "particles_impact", "particles_land", "easing_all"]},
    "minimal": {"description": "Essencial: coyote time + screen shake",
                "techniques": ["coyote_time", "screen_shake"]},
}

_GDScript_JUICERS = {
    "coyote_time": '''## Coyote Time
var coyote_timer: float = 0.0
const COYOTE_TIME: float = 0.12

func _process(delta: float) -> void:
    if not is_on_floor(): coyote_timer += delta
    else: coyote_timer = 0.0
    if Input.is_action_just_pressed("jump") and (is_on_floor() or coyote_timer < COYOTE_TIME):
        _do_jump(); coyote_timer = COYOTE_TIME
''',
    "input_buffer": '''## Input Buffer
var input_buffer: Dictionary = {}
const BUFFER_WINDOW: float = 0.15

func _unhandled_input(event: InputEvent) -> void:
    if event.is_action_pressed("jump"): input_buffer["jump"] = BUFFER_WINDOW
    elif event.is_action_pressed("attack"): input_buffer["attack"] = BUFFER_WINDOW

func _process(delta: float) -> void:
    for key in input_buffer.keys(): input_buffer[key] = max(0.0, input_buffer[key] - delta)
    if can_attack() and input_buffer.get("attack", 0) > 0:
        _do_attack(); input_buffer["attack"] = 0.0
''',
    "hit_stop": '''## Hit-Stop
func _apply_hit_stop(frames: int = 4) -> void:
    Engine.time_scale = 0.001
    get_tree().create_timer(frames / 60.0).timeout.connect(func(): Engine.time_scale = 1.0)
''',
    "screen_shake": '''## Screen Shake
var shake_trauma: float = 0.0
const SHAKE_DECAY: float = 0.85
const SHAKE_MAX: Vector2 = Vector2(6.0, 4.0)

func add_shake(amount: float = 0.5) -> void:
    shake_trauma = clamp(shake_trauma + amount, 0.0, 1.0)

func _process(delta: float) -> void:
    if shake_trauma > 0.001:
        shake_trauma = max(0.0, shake_trauma - SHAKE_DECAY * delta)
        var i = shake_trauma * shake_trauma
        $Camera.offset = Vector2(randf_range(-1,1)*SHAKE_MAX.x*i, randf_range(-1,1)*SHAKE_MAX.y*i)
''',
    "squash_stretch": '''## Squash & Stretch
func _apply_squash_stretch(sx: float = 1.3, sy: float = 0.7, d: float = 0.1) -> void:
    var tween = create_tween().set_ease(Tween.EASE_OUT).set_trans(Tween.TRANS_BACK)
    tween.tween_property(self, "scale", Vector2(sx, sy), d * 0.3)
    tween.tween_property(self, "scale", Vector2.ONE, d * 0.7)
''',
    "easing_all": '''## Easing
func move_to(target: Vector2, duration: float = 0.3) -> void:
    var tween = create_tween().set_ease(Tween.EASE_OUT).set_trans(Tween.TRANS_QUAD)
    tween.tween_property(self, "position", target, duration)

func fade_in(duration: float = 0.2) -> void:
    modulate.a = 0.0; create_tween().tween_property(self, "modulate:a", 1.0, duration)
''',
    "particles_impact": '''## Impact Particles
func _spawn_impact_particles(at: Vector2, color: Color = Color.WHITE) -> void:
    var p = preload("res://scenes/vfx/impact_particles.tscn").instantiate()
    p.position = at; p.modulate = color; p.emitting = true
    get_parent().add_child(p); p.finished.connect(p.queue_free)
''',
    "particles_land": '''## Land Particles
func _spawn_land_particles() -> void:
    var p = preload("res://scenes/vfx/land_particles.tscn").instantiate()
    p.position = global_position + Vector2(0, 16); p.emitting = true
    get_parent().add_child(p); p.finished.connect(p.queue_free)
''',
    "easing_attack": '''## Attack Lunge
func _attack_lunge(direction: Vector2, distance: float = 32.0, duration: float = 0.15) -> void:
    var target = global_position + direction * distance
    var tween = create_tween()
    tween.tween_property(self, "global_position", target, duration * 0.3)
    tween.tween_property(self, "global_position", global_position, duration * 0.7)
''',
}


def juice_apply(preset: str = "full", save_to_script: str | None = None) -> dict:
    """Aplica tecnicas de juice/polish em um personagem ou cena.

    Presets: full, platformer, action, minimal.
    """
    from tools.project_ops import _get_active_project, _check_path_traversal
    proj = _get_active_project()

    preset_info = _JUICE_PRESETS.get(preset, _JUICE_PRESETS["full"])
    techniques = preset_info["techniques"]

    if not save_to_script:
        save_to_script = f"scripts/juice/juice_{preset}.gd"

    violation = _check_path_traversal(save_to_script, proj)
    if violation:
        return {"status": "error", "message": violation}

    code = f"# Juice / Game Feel — {preset_info['description']}\n# Gerado pelo MCP Godot — anexe ao personagem\n\nclass_name Juice{preset.title().replace('_','')}\nextends Node\n\n"
    for t in techniques:
        if t in _GDScript_JUICERS:
            code += _GDScript_JUICERS[t] + "\n"

    code += '''
func _do_jump(): pass
func _do_attack(): pass
func can_attack() -> bool: return true
'''

    full = proj / save_to_script
    full.parent.mkdir(parents=True, exist_ok=True)
    full.write_text(code, encoding="utf-8")

    return {"status": "success", "saved_to": save_to_script,
            "techniques": techniques, "lines": code.count('\n') + 1, "preset": preset,
            "message": f"Juice '{preset}': {len(techniques)} tecnicas, {code.count(chr(10))+1} linhas. Anexe ao personagem!"}


def juice_list_presets() -> dict:
    """Lista presets de juice disponiveis."""
    return {"status": "success",
            "presets": [{"name": n, "description": i["description"], "techniques": i["techniques"], "count": len(i["techniques"])} for n, i in _JUICE_PRESETS.items()],
            "total": len(_JUICE_PRESETS)}
