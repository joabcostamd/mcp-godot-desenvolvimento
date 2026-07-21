## test_color_pulse.gd — Testes do behavior ColorPulse | GdUnit4.
##
## Cobre: start, stop, auto_start, amplitude, is_pulsing.
##
## Requer: GdUnit4 instalado como addon.
## Executar: GdUnit4 > Run Tests

extends GdUnitTestSuite


# ── Helpers ───────────────────────────────────────────────────────────────────

func _make_cp(auto := false) -> ColorPulse:
	var cp := ColorPulse.new()
	cp.auto_start = auto
	return cp


# ═══════════════════════════════════════════════════════════════════════════════
# ESTÁTICO — Compilação e defaults
# ═══════════════════════════════════════════════════════════════════════════════

func test_script_compiles() -> void:
	var cp := ColorPulse.new()
	assert_object(cp).is_not_null()
	cp.queue_free()


func test_default_parameters() -> void:
	var cp := ColorPulse.new()
	assert_that(cp.pulse_color).is_equal(Color.RED)
	assert_float(cp.frequency).is_equal(2.0)
	assert_float(cp.amplitude).is_equal(0.5)
	assert_bool(cp.auto_start).is_true()
	cp.queue_free()


func test_parameter_clamping() -> void:
	var cp := ColorPulse.new()
	cp.frequency = 0.0
	assert_float(cp.frequency).is_equal(0.1)
	cp.frequency = 999.0
	assert_float(cp.frequency).is_equal(30.0)
	cp.amplitude = -1.0
	assert_float(cp.amplitude).is_equal(0.0)
	cp.amplitude = 99.0
	assert_float(cp.amplitude).is_equal(1.0)
	cp.queue_free()


# ═══════════════════════════════════════════════════════════════════════════════
# UNITÁRIO — start/stop e estado
# ═══════════════════════════════════════════════════════════════════════════════

func test_start_activates() -> void:
	var cp := _make_cp(false)
	add_child(cp)
	cp.start()
	assert_bool(cp.is_pulsing()).is_true()
	remove_child(cp)
	cp.queue_free()


func test_stop_deactivates() -> void:
	var cp := _make_cp(false)
	add_child(cp)
	cp.start()
	cp.stop()
	assert_bool(cp.is_pulsing()).is_false()
	remove_child(cp)
	cp.queue_free()


func test_stop_restores_modulate() -> void:
	var sprite := Sprite2D.new()
	sprite.modulate = Color.GREEN
	add_child(sprite)
	var cp := _make_cp(false)
	sprite.add_child(cp)
	cp.start()
	cp.stop()
	assert_that(sprite.modulate).is_equal(Color.GREEN)
	remove_child(sprite)
	sprite.queue_free()


func test_is_pulsing_initially_false() -> void:
	var cp := _make_cp(false)
	assert_bool(cp.is_pulsing()).is_false()
	cp.queue_free()


func test_auto_start_activates() -> void:
	var sprite := Sprite2D.new()
	add_child(sprite)
	var cp := _make_cp(true)
	sprite.add_child(cp)
	assert_bool(cp.is_pulsing()).is_true()
	remove_child(sprite)
	sprite.queue_free()


func test_start_emits_pulsing_signal() -> void:
	var cp := _make_cp(false)
	add_child(cp)
	var state := false
	cp.pulsing.connect(func(active: bool): state = active)
	cp.start()
	assert_bool(state).is_true()
	remove_child(cp)
	cp.queue_free()


func test_stop_emits_pulsing_signal() -> void:
	var cp := _make_cp(false)
	add_child(cp)
	cp.start()
	var state := true
	cp.pulsing.connect(func(active: bool): state = active)
	cp.stop()
	assert_bool(state).is_false()
	remove_child(cp)
	cp.queue_free()


func test_amplitude_zero_no_effect() -> void:
	var sprite := Sprite2D.new()
	sprite.modulate = Color.BLUE
	add_child(sprite)
	var cp := _make_cp(false)
	cp.amplitude = 0.0
	sprite.add_child(cp)
	cp.start()
	# Deve manter modulate original
	assert_that(sprite.modulate).is_equal(Color.BLUE)
	remove_child(sprite)
	sprite.queue_free()


# ═══════════════════════════════════════════════════════════════════════════════
# COMPOSIÇÃO — Com outros behaviors
# ═══════════════════════════════════════════════════════════════════════════════

func test_composes_with_health() -> void:
	var parent := Node2D.new()
	add_child(parent)

	var health := Health.new()
	health.max_hp = 100
	parent.add_child(health)

	var cp := _make_cp(false)
	parent.add_child(cp)

	cp.start()
	assert_bool(cp.is_pulsing()).is_true()

	remove_child(parent)
	parent.queue_free()
