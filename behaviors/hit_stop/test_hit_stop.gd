## test_hit_stop.gd — Testes do behavior HitStop | GdUnit4.
##
## Cobre: trigger, freeze, restore, ignora duplo, tree_exiting.
##
## Requer: GdUnit4 instalado como addon.
## Executar: GdUnit4 > Run Tests

extends GdUnitTestSuite


# ── Helpers ───────────────────────────────────────────────────────────────────

func _make_hs(freeze := 0.05, dur := 0.1, restore := 0.0) -> HitStop:
	var hs := HitStop.new()
	hs.freeze_scale = freeze
	hs.default_duration = dur
	hs.restore_duration = restore
	return hs


# ═══════════════════════════════════════════════════════════════════════════════
# ESTÁTICO — Compilação e defaults
# ═══════════════════════════════════════════════════════════════════════════════

func test_script_compiles() -> void:
	var hs := HitStop.new()
	assert_object(hs).is_not_null()
	hs.queue_free()


func test_default_parameters() -> void:
	var hs := HitStop.new()
	assert_float(hs.freeze_scale).is_equal(0.05)
	assert_float(hs.default_duration).is_equal(0.1)
	assert_float(hs.restore_duration).is_equal(0.05)
	hs.queue_free()


func test_parameter_clamping() -> void:
	var hs := HitStop.new()
	hs.freeze_scale = 0.0
	assert_float(hs.freeze_scale).is_equal(0.01)
	hs.freeze_scale = 1.0
	assert_float(hs.freeze_scale).is_equal(0.5)
	hs.default_duration = 0.0
	assert_float(hs.default_duration).is_equal(0.01)
	hs.queue_free()


# ═══════════════════════════════════════════════════════════════════════════════
# UNITÁRIO — trigger e estado
# ═══════════════════════════════════════════════════════════════════════════════

func test_trigger_sets_time_scale() -> void:
	var saved := Engine.time_scale
	var hs := _make_hs()
	add_child(hs)
	hs.trigger(0.05)
	assert_float(Engine.time_scale).is_equal(0.05)
	Engine.time_scale = saved
	remove_child(hs)
	hs.queue_free()


func test_trigger_emits_hit_stopped() -> void:
	var saved := Engine.time_scale
	var hs := _make_hs()
	add_child(hs)
	var stopped := false
	hs.hit_stopped.connect(func(): stopped = true)
	hs.trigger(0.05)
	assert_bool(stopped).is_true()
	Engine.time_scale = saved
	remove_child(hs)
	hs.queue_free()


func test_trigger_activates() -> void:
	var saved := Engine.time_scale
	var hs := _make_hs()
	add_child(hs)
	hs.trigger(0.05)
	assert_bool(hs.is_active()).is_true()
	Engine.time_scale = saved
	remove_child(hs)
	hs.queue_free()


func test_trigger_ignored_when_active() -> void:
	var saved := Engine.time_scale
	var hs := _make_hs(0.05, 0.5)
	add_child(hs)
	hs.trigger()
	hs.trigger(0.2)  # deve ser ignorado
	assert_float(Engine.time_scale).is_equal(0.05)
	Engine.time_scale = saved
	remove_child(hs)
	hs.queue_free()


func test_is_active_initially_false() -> void:
	var hs := _make_hs()
	assert_bool(hs.is_active()).is_false()
	hs.queue_free()


func test_trigger_restores_instant() -> void:
	var saved := Engine.time_scale
	var hs := _make_hs(0.05, 0.02, 0.0)  # restore instantâneo
	add_child(hs)
	var resumed := false
	hs.resumed.connect(func(): resumed = true)
	hs.trigger()
	# Timer de 0.02s → deve disparar rapidamente
	await get_tree().create_timer(0.1).timeout
	assert_bool(resumed).is_true()
	assert_float(Engine.time_scale).is_equal(1.0)
	Engine.time_scale = saved
	remove_child(hs)
	hs.queue_free()


# ═══════════════════════════════════════════════════════════════════════════════
# CENA — Comportamento em árvore
# ═══════════════════════════════════════════════════════════════════════════════

func test_tree_exiting_restores_scale() -> void:
	var saved := Engine.time_scale
	var hs := _make_hs()
	add_child(hs)
	hs.trigger(0.5)
	remove_child(hs)
	assert_float(Engine.time_scale).is_equal(1.0)
	Engine.time_scale = saved
	hs.queue_free()


# ═══════════════════════════════════════════════════════════════════════════════
# COMPOSIÇÃO — Com outros behaviors
# ═══════════════════════════════════════════════════════════════════════════════

func test_composes_with_time_scale() -> void:
	var saved := Engine.time_scale
	var parent := Node2D.new()
	add_child(parent)

	var ts := TimeScale.new()
	parent.add_child(ts)

	var hs := _make_hs()
	parent.add_child(hs)

	hs.trigger(0.05)
	assert_float(Engine.time_scale).is_equal(0.05)

	Engine.time_scale = saved
	remove_child(parent)
	parent.queue_free()


func test_composes_with_health() -> void:
	var saved := Engine.time_scale
	var parent := Node2D.new()
	add_child(parent)

	var health := Health.new()
	health.max_hp = 100
	parent.add_child(health)

	var hs := _make_hs()
	parent.add_child(hs)

	hs.trigger(0.05)
	assert_bool(hs.is_active()).is_true()

	Engine.time_scale = saved
	remove_child(parent)
	parent.queue_free()
