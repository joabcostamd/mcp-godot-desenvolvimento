## test_flee.gd — Testes do Flee | GdUnit4.
##
## Cobre: fuga direcional, safe_distance, condições,
##        state_machine, edge cases, warnings.
##
## Requer: GdUnit4 instalado como addon.

extends GdUnitTestSuite


# ── Movimento ─────────────────────────────────────────────────────────────────

func test_flees_away_from_threat() -> void:
	var flee := _make_flee(200.0, 400.0, "always")
	var parent := CharacterBody2D.new()
	parent.add_child(flee)
	add_child(parent)

	var threat := Node2D.new()
	threat.global_position = Vector2(100, 0)
	add_child(threat)
	flee.set_threat(threat)

	var start := parent.global_position
	flee._physics_process(0.016)
	assert_float(parent.global_position.x).is_less(start.x)


func test_stops_at_safe_distance() -> void:
	var flee := _make_flee(200.0, 400.0, "always")
	var parent := CharacterBody2D.new()
	parent.global_position = Vector2(-500, 0)
	parent.add_child(flee)
	add_child(parent)

	var threat := Node2D.new()
	threat.global_position = Vector2(0, 0)
	add_child(threat)
	flee.set_threat(threat)

	flee._physics_process(0.016)
	assert_str(flee._state).is_equal("safe")


# ── Condições ─────────────────────────────────────────────────────────────────

func test_condition_always_flees() -> void:
	var flee := _make_flee(200.0, 400.0, "always")
	var parent := CharacterBody2D.new()
	parent.add_child(flee)
	add_child(parent)

	var threat := Node2D.new()
	threat.global_position = Vector2(50, 0)
	add_child(threat)
	flee.set_threat(threat)

	flee._evaluate_condition()
	assert_str(flee._state).is_equal("flee")


func test_condition_health_below_threshold() -> void:
	var flee := _make_flee(200.0, 400.0, "health_below_30%")
	flee.health_threshold_pct = 0.3
	var health := Health.new()
	health.max_hp = 100
	health.current_hp = 20  # 20% — abaixo de 30%
	var parent := CharacterBody2D.new()
	parent.add_child(health)
	parent.add_child(flee)
	add_child(parent)
	flee._find_health()

	flee._evaluate_condition()
	assert_str(flee._state).is_equal("flee")


func test_condition_health_above_threshold() -> void:
	var flee := _make_flee(200.0, 400.0, "health_below_30%")
	flee.health_threshold_pct = 0.3
	var health := Health.new()
	health.max_hp = 100
	health.current_hp = 80  # 80% — acima de 30%
	var parent := CharacterBody2D.new()
	parent.add_child(health)
	parent.add_child(flee)
	add_child(parent)
	flee._find_health()
	flee._state = "flee"

	flee._evaluate_condition()
	assert_str(flee._state).is_equal("safe")


func test_condition_on_damage() -> void:
	var flee := _make_flee(200.0, 400.0, "on_damage")
	add_child(flee)

	flee._on_damage_taken(10, 90)
	assert_str(flee._state).is_equal("flee")


# ── Sinais ────────────────────────────────────────────────────────────────────

func test_fleeing_signal() -> void:
	var flee := _make_flee(200.0, 400.0, "always")
	add_child(flee)
	var threat := Node2D.new()
	threat.global_position = Vector2(50, 0)
	add_child(threat)
	flee.set_threat(threat)

	var emitted := false
	flee.fleeing.connect(func(): emitted = true)
	flee._evaluate_condition()
	assert_bool(emitted).is_true()


func test_safe_signal() -> void:
	var flee := _make_flee(200.0, 400.0, "always")
	var parent := CharacterBody2D.new()
	parent.global_position = Vector2(-500, 0)
	parent.add_child(flee)
	add_child(parent)
	var threat := Node2D.new()
	add_child(threat)
	flee.set_threat(threat)

	var emitted := false
	flee.safe.connect(func(): emitted = true)
	flee._physics_process(0.016)
	assert_bool(emitted).is_true()


# ── Edge cases ────────────────────────────────────────────────────────────────

func test_threat_null_no_crash() -> void:
	var flee := _make_flee(200.0, 400.0, "always")
	flee._state = "flee"
	add_child(flee)

	flee._physics_process(0.016)
	assert_bool(true)


func test_parent_not_character_body() -> void:
	var flee := _make_flee(200.0, 400.0, "always")
	var parent := Node2D.new()
	parent.add_child(flee)
	add_child(parent)
	var threat := Node2D.new()
	threat.global_position = Vector2(50, 0)
	add_child(threat)
	flee.set_threat(threat)

	flee._physics_process(0.016)
	assert_bool(true)


# ── State machine ─────────────────────────────────────────────────────────────

func test_syncs_state_machine() -> void:
	var sm := StateMachine.new()
	sm.configure(["flee", "safe"], [], "safe")
	var flee := _make_flee(200.0, 400.0, "always")
	var parent := CharacterBody2D.new()
	parent.add_child(sm)
	parent.add_child(flee)
	add_child(parent)
	flee._find_state_machine()

	var threat := Node2D.new()
	threat.global_position = Vector2(50, 0)
	add_child(threat)
	flee.set_threat(threat)
	flee._evaluate_condition()

	assert_str(sm.get_state()).is_equal("flee")


# ── Warnings ──────────────────────────────────────────────────────────────────

func test_warning_no_health() -> void:
	var flee := _make_flee(200.0, 400.0, "health_below_30%")
	add_child(flee)

	var found := false
	for w in flee._get_configuration_warnings():
		if "Health" in w:
			found = true
	assert_bool(found).is_true()


func test_warning_parent_not_character_body() -> void:
	var flee := _make_flee(200.0, 400.0, "always")
	var parent := Node2D.new()
	parent.add_child(flee)
	add_child(parent)

	var found := false
	for w in flee._get_configuration_warnings():
		if "CharacterBody2D" in w:
			found = true
	assert_bool(found).is_true()


# ── Helpers ──────────────────────────────────────────────────────────────────

func _make_flee(speed: float, safe_dist: float, condition: String) -> Flee:
	var f := Flee.new()
	f.flee_speed = speed
	f.safe_distance = safe_dist
	f.flee_condition = condition
	return f
