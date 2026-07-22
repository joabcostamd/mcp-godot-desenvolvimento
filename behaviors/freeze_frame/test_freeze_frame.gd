## test_freeze_frame.gd — Testes do behavior FreezeFrame | GdUnit4.
##
## Cobre: freeze, restore, ignora duplo, tree_exiting, sinais.
##
## Requer: GdUnit4 instalado como addon.
## Executar: GdUnit4 > Run Tests

extends GdUnitTestSuite


# ── Helpers ───────────────────────────────────────────────────────────────────

func _make_ff(dur := 0.3, restore := 0.0) -> FreezeFrame:
	var ff := FreezeFrame.new()
	ff.default_duration = dur
	ff.restore_duration = restore
	return ff


# ═══════════════════════════════════════════════════════════════════════════════
# ESTÁTICO — Compilação e defaults
# ═══════════════════════════════════════════════════════════════════════════════

func test_script_compiles() -> void:
	var ff := FreezeFrame.new()
	assert_object(ff).is_not_null()
	ff.queue_free()


func test_default_parameters() -> void:
	var ff := FreezeFrame.new()
	assert_float(ff.default_duration).is_equal(0.3)
	assert_float(ff.restore_duration).is_equal(0.1)
	ff.queue_free()


func test_parameter_clamping() -> void:
	var ff := FreezeFrame.new()
	ff.default_duration = 0.0
	assert_float(ff.default_duration).is_equal(0.01)
	ff.default_duration = 99.0
	assert_float(ff.default_duration).is_equal(5.0)
	ff.restore_duration = -1.0
	assert_float(ff.restore_duration).is_equal(0.0)
	ff.queue_free()


# ═══════════════════════════════════════════════════════════════════════════════
# UNITÁRIO — freeze e estado
# ═══════════════════════════════════════════════════════════════════════════════

func test_freeze_sets_time_scale_to_zero() -> void:
	var saved := Engine.time_scale
	var ff := _make_ff()
	add_child(ff)
	ff.freeze(0.05)
	assert_float(Engine.time_scale).is_equal(0.0)
	Engine.time_scale = saved
	remove_child(ff)
	ff.queue_free()


func test_freeze_emits_frozen() -> void:
	var saved := Engine.time_scale
	var ff := _make_ff()
	add_child(ff)
	var emitted := false
	ff.frozen.connect(func(): emitted = true)
	ff.freeze(0.05)
	assert_bool(emitted).is_true()
	Engine.time_scale = saved
	remove_child(ff)
	ff.queue_free()


func test_freeze_activates() -> void:
	var saved := Engine.time_scale
	var ff := _make_ff()
	add_child(ff)
	ff.freeze(0.05)
	assert_bool(ff.is_active()).is_true()
	Engine.time_scale = saved
	remove_child(ff)
	ff.queue_free()


func test_freeze_ignored_when_active() -> void:
	var saved := Engine.time_scale
	var ff := _make_ff(0.5)
	add_child(ff)
	ff.freeze()
	ff.freeze(0.1)
	assert_float(Engine.time_scale).is_equal(0.0)
	Engine.time_scale = saved
	remove_child(ff)
	ff.queue_free()


func test_is_active_initially_false() -> void:
	var ff := _make_ff()
	assert_bool(ff.is_active()).is_false()
	ff.queue_free()


func test_freeze_restores_instant() -> void:
	var saved := Engine.time_scale
	var ff := _make_ff(0.02, 0.0)
	add_child(ff)
	var resumed := false
	ff.resumed.connect(func(): resumed = true)
	ff.freeze()
	await get_tree().create_timer(0.1).timeout
	assert_bool(resumed).is_true()
	assert_float(Engine.time_scale).is_equal(1.0)
	Engine.time_scale = saved
	remove_child(ff)
	ff.queue_free()


func test_timer_has_ignore_time_scale() -> void:
	var ff := _make_ff()
	add_child(ff)
	ff.freeze(0.05)
	var timer := ff.get_node_or_null("FreezeFrameTimer")
	assert_object(timer).is_not_null()
	if timer:
		assert_bool(timer.ignore_time_scale).is_true()
	Engine.time_scale = 1.0
	remove_child(ff)
	ff.queue_free()


# ═══════════════════════════════════════════════════════════════════════════════
# CENA — Comportamento em árvore
# ═══════════════════════════════════════════════════════════════════════════════

func test_tree_exiting_restores_scale() -> void:
	var saved := Engine.time_scale
	var ff := _make_ff()
	add_child(ff)
	ff.freeze(0.5)
	remove_child(ff)
	assert_float(Engine.time_scale).is_equal(1.0)
	Engine.time_scale = saved
	ff.queue_free()


# ═══════════════════════════════════════════════════════════════════════════════
# COMPOSIÇÃO — Com outros behaviors
# ═══════════════════════════════════════════════════════════════════════════════

func test_composes_with_time_scale() -> void:
	var saved := Engine.time_scale
	var parent := Node2D.new()
	add_child(parent)

	var ts := TimeScale.new()
	parent.add_child(ts)

	var ff := _make_ff()
	parent.add_child(ff)

	ff.freeze(0.05)
	assert_float(Engine.time_scale).is_equal(0.0)

	Engine.time_scale = saved
	remove_child(parent)
	parent.queue_free()


func test_composes_with_hit_stop() -> void:
	var saved := Engine.time_scale
	var parent := Node2D.new()
	add_child(parent)

	var hs := HitStop.new()
	parent.add_child(hs)

	var ff := _make_ff()
	parent.add_child(ff)

	ff.freeze(0.05)
	assert_float(Engine.time_scale).is_equal(0.0)

	Engine.time_scale = saved
	remove_child(parent)
	parent.queue_free()
