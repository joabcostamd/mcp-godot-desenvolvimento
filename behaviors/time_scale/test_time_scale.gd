## test_time_scale.gd — Testes do behavior TimeScale | GdUnit4.
##
## Cobre: set_scale, reset, clamping, tree_exiting, sinal, transição.
##
## Requer: GdUnit4 instalado como addon.
## Executar: GdUnit4 > Run Tests

extends GdUnitTestSuite


# ── Helpers ───────────────────────────────────────────────────────────────────

func _make_ts(def := 1.0, dur := 0.3) -> TimeScale:
	var ts := TimeScale.new()
	ts.default_scale = def
	ts.transition_duration = dur
	return ts


func _save_and_restore_engine_scale() -> float:
	return Engine.time_scale


# ═══════════════════════════════════════════════════════════════════════════════
# ESTÁTICO — Compilação e defaults
# ═══════════════════════════════════════════════════════════════════════════════

func test_script_compiles() -> void:
	var ts := TimeScale.new()
	assert_object(ts).is_not_null()
	ts.queue_free()


func test_default_parameters() -> void:
	var ts := TimeScale.new()
	assert_float(ts.default_scale).is_equal(1.0)
	assert_float(ts.transition_duration).is_equal(0.3)
	assert_float(ts.min_scale).is_equal(0.05)
	assert_float(ts.max_scale).is_equal(10.0)
	ts.queue_free()


func test_parameter_clamping() -> void:
	var ts := TimeScale.new()
	ts.default_scale = 999.0
	assert_float(ts.default_scale).is_equal(10.0)
	ts.min_scale = 0.0
	assert_float(ts.min_scale).is_equal(0.01)
	ts.max_scale = 9999.0
	assert_float(ts.max_scale).is_equal(100.0)
	ts.queue_free()


# ═══════════════════════════════════════════════════════════════════════════════
# UNITÁRIO — set_scale e estado
# ═══════════════════════════════════════════════════════════════════════════════

func test_set_scale_instant() -> void:
	var saved := Engine.time_scale
	var ts := _make_ts()
	add_child(ts)
	ts.set_scale(0.5, 0.0)  # instantâneo
	assert_float(Engine.time_scale).is_equal(0.5)
	Engine.time_scale = saved
	remove_child(ts)
	ts.queue_free()


func test_set_scale_rejects_zero() -> void:
	var saved := Engine.time_scale
	var ts := _make_ts()
	add_child(ts)
	ts.set_scale(0.0, 0.0)
	assert_float(Engine.time_scale).is_equal(ts.default_scale)
	Engine.time_scale = saved
	remove_child(ts)
	ts.queue_free()


func test_set_scale_rejects_negative() -> void:
	var saved := Engine.time_scale
	var ts := _make_ts()
	add_child(ts)
	ts.set_scale(-1.0, 0.0)
	assert_float(Engine.time_scale).is_equal(ts.default_scale)
	Engine.time_scale = saved
	remove_child(ts)
	ts.queue_free()


func test_set_scale_clamps_to_min() -> void:
	var saved := Engine.time_scale
	var ts := _make_ts()
	ts.min_scale = 0.1
	add_child(ts)
	ts.set_scale(0.01, 0.0)
	assert_float(Engine.time_scale).is_equal(0.1)
	Engine.time_scale = saved
	remove_child(ts)
	ts.queue_free()


func test_set_scale_clamps_to_max() -> void:
	var saved := Engine.time_scale
	var ts := _make_ts()
	ts.max_scale = 5.0
	add_child(ts)
	ts.set_scale(50.0, 0.0)
	assert_float(Engine.time_scale).is_equal(5.0)
	Engine.time_scale = saved
	remove_child(ts)
	ts.queue_free()


func test_reset_restores_default() -> void:
	var saved := Engine.time_scale
	var ts := _make_ts(2.0)
	add_child(ts)
	ts.set_scale(0.5, 0.0)
	ts.reset(0.0)
	assert_float(Engine.time_scale).is_equal(2.0)
	Engine.time_scale = saved
	remove_child(ts)
	ts.queue_free()


func test_get_current_scale() -> void:
	var saved := Engine.time_scale
	var ts := _make_ts()
	add_child(ts)
	ts.set_scale(0.75, 0.0)
	assert_float(ts.get_current_scale()).is_equal(0.75)
	Engine.time_scale = saved
	remove_child(ts)
	ts.queue_free()


func test_is_not_transitioning_initially() -> void:
	var ts := _make_ts()
	assert_bool(ts.is_transitioning()).is_false()
	ts.queue_free()


# ═══════════════════════════════════════════════════════════════════════════════
# CENA — Comportamento em árvore
# ═══════════════════════════════════════════════════════════════════════════════

func test_tree_exiting_restores_scale() -> void:
	var saved := Engine.time_scale
	var ts := _make_ts()
	add_child(ts)
	ts.set_scale(0.3, 0.0)
	remove_child(ts)
	assert_float(Engine.time_scale).is_equal(1.0)
	Engine.time_scale = saved
	ts.queue_free()


func test_scale_changed_emitted_after_instant() -> void:
	var saved := Engine.time_scale
	var ts := _make_ts()
	add_child(ts)
	var emitted := 0.0
	ts.scale_changed.connect(func(s: float): emitted = s)
	ts.set_scale(0.5, 0.0)
	assert_float(emitted).is_equal(0.5)
	Engine.time_scale = saved
	remove_child(ts)
	ts.queue_free()


func test_multiple_set_scale_cancels_previous() -> void:
	var saved := Engine.time_scale
	var ts := _make_ts(1.0, 10.0)  # transição longa
	add_child(ts)
	ts.set_scale(0.5, 5.0)   # inicia transição longa
	ts.set_scale(2.0, 0.0)   # cancela e vai instantâneo para 2.0
	assert_float(Engine.time_scale).is_equal(2.0)
	assert_bool(ts.is_transitioning()).is_false()
	Engine.time_scale = saved
	remove_child(ts)
	ts.queue_free()


# ═══════════════════════════════════════════════════════════════════════════════
# COMPOSIÇÃO — Com outros behaviors
# ═══════════════════════════════════════════════════════════════════════════════

func test_composes_with_pause_menu() -> void:
	var saved := Engine.time_scale
	var parent := Node2D.new()
	add_child(parent)

	var ts := _make_ts()
	parent.add_child(ts)

	var pm := PauseMenu.new()
	parent.add_child(pm)

	ts.set_scale(0.5, 0.0)
	assert_float(Engine.time_scale).is_equal(0.5)

	Engine.time_scale = saved
	remove_child(parent)
	parent.queue_free()


func test_composes_with_screen_shake() -> void:
	var saved := Engine.time_scale
	var parent := Node2D.new()
	add_child(parent)

	var ts := _make_ts()
	parent.add_child(ts)

	var shake := ScreenShake.new()
	parent.add_child(shake)

	ts.set_scale(0.2, 0.0)
	assert_float(Engine.time_scale).is_equal(0.2)

	Engine.time_scale = saved
	remove_child(parent)
	parent.queue_free()
