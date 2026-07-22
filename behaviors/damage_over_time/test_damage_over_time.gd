## test_damage_over_time.gd — Testes do behavior DamageOverTime | GdUnit4.
##
## Cobre: start, stop, ticks, sinais, health inválido, warnings.

extends GdUnitTestSuite


# ── start ────────────────────────────────────────────────────────────────────

func test_start_applies_damage_on_tick() -> void:
	var dot := _make_dot(10, 0.1, 5.0)
	var health := _make_health(100)

	add_child(dot)
	add_child(health)

	dot.start(health)
	# Espera um tick
	await get_tree().create_timer(0.15).timeout

	assert_int(health.current_hp).is_less(100)
	assert_bool(dot.is_active()).is_true()


func test_start_null_health_returns_false() -> void:
	var dot := _make_dot(10, 1.0, 5.0)
	var result := dot.start(null)
	assert_bool(result).is_false()


func test_start_dead_health_returns_false() -> void:
	var dot := _make_dot(10, 1.0, 5.0)
	var health := _make_health(0)  # já morto
	health.take_damage(100)  # garante que está morto
	add_child(health)

	var result := dot.start(health)
	assert_bool(result).is_false()


func test_start_while_active_restarts() -> void:
	var dot := _make_dot(10, 1.0, 0.3)
	var health := _make_health(100)
	add_child(dot)
	add_child(health)

	dot.start(health)
	var result := dot.start(health)  # restart
	assert_bool(result).is_true()


# ── stop ─────────────────────────────────────────────────────────────────────

func test_stop_ends_dot() -> void:
	var dot := _make_dot(10, 1.0, 99.0)
	var health := _make_health(100)
	add_child(dot)
	add_child(health)

	dot.start(health)
	dot.stop()

	assert_bool(dot.is_active()).is_false()


# ── Sinais ───────────────────────────────────────────────────────────────────

func test_dot_tick_emitted() -> void:
	var dot := _make_dot(10, 0.1, 5.0)
	var health := _make_health(100)
	add_child(dot)
	add_child(health)

	var signal_fired := false
	var captured_damage := 0
	dot.dot_tick.connect(func(dmg):
		signal_fired = true
		captured_damage = dmg
	)

	dot.start(health)
	await get_tree().create_timer(0.15).timeout

	assert_bool(signal_fired).is_true()
	assert_int(captured_damage).is_equal(10)


func test_dot_ended_emitted_on_stop() -> void:
	var dot := _make_dot(10, 1.0, 99.0)
	var health := _make_health(100)
	add_child(dot)
	add_child(health)

	var signal_fired := false
	dot.dot_ended.connect(func(): signal_fired = true)

	dot.start(health)
	dot.stop()

	assert_bool(signal_fired).is_true()


# ── Setters ──────────────────────────────────────────────────────────────────

func test_damage_clamped() -> void:
	var dot := _make_dot(10, 1.0, 5.0)
	dot.damage_per_tick = 0
	assert_int(dot.damage_per_tick).is_equal(1)


# ── Warnings ─────────────────────────────────────────────────────────────────

func test_warning_tick_gt_duration() -> void:
	var dot := _make_dot(10, 10.0, 1.0)  # tick > duration
	var warnings := dot._get_configuration_warnings()
	assert_bool(warnings.size() > 0).is_true()


# ── Robustez ─────────────────────────────────────────────────────────────────

func test_stop_safe_before_ready() -> void:
	var dot := DamageOverTime.new()
	dot.stop()  # não deve crashar
	assert_bool(dot.is_active()).is_false()


# ── Helpers ──────────────────────────────────────────────────────────────────

func _make_dot(dmg: int, interval: float, dur: float) -> DamageOverTime:
	var dot := DamageOverTime.new()
	dot.damage_per_tick = dmg
	dot.tick_interval = interval
	dot.duration = dur
	return dot


func _make_health(hp: int) -> Health:
	var h := Health.new()
	h.max_hp = hp
	h.current_hp = hp
	return h
