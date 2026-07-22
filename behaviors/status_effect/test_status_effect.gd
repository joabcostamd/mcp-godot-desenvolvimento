## test_status_effect.gd — Testes do StatusEffect | GdUnit4.
## Cobre apply, refresh, stacks, tick damage, expire, remove.

extends GdUnitTestSuite

func _make_se() -> StatusEffect:
	return StatusEffect.new()


func test_default_parameters() -> void:
	var se := _make_se()
	assert_str(se.effect_type).is_equal("custom")
	assert_float(se.duration).is_equal(5.0)
	assert_float(se.tick_interval).is_equal(1.0)
	assert_int(se.tick_damage).is_equal(0)
	assert_int(se.max_stacks).is_equal(1)
	se.queue_free()


func test_apply_activates() -> void:
	var se := _make_se()
	se.apply()
	assert_bool(se.is_active()).is_true()
	assert_int(se.get_stacks()).is_equal(1)
	se.queue_free()


func test_apply_stacks_up_to_max() -> void:
	var se := _make_se()
	se.max_stacks = 3
	se.apply()
	se.apply()
	se.apply()
	assert_int(se.get_stacks()).is_equal(3)
	# 4ª chamada deve refresh, não stack
	se.apply()
	assert_int(se.get_stacks()).is_equal(3)
	se.queue_free()


func test_refresh_resets_duration() -> void:
	var se := _make_se()
	se.duration = 5.0
	se.apply()
	se._elapsed = 4.9  # quase expirou
	se.refresh()
	assert_float(se._elapsed).is_equal(0.0)
	assert_bool(se.is_active()).is_true()
	se.queue_free()


func test_remove_deactivates() -> void:
	var se := _make_se()
	se.apply()
	assert_bool(se.is_active()).is_true()
	se.remove()
	assert_bool(se.is_active()).is_false()
	se.queue_free()


func test_expires_after_duration() -> void:
	var se := _make_se()
	se.duration = 1.0
	se.apply()
	se._process(1.1)
	assert_bool(se.is_active()).is_false()
	se.queue_free()


func test_permanent_effect_never_expires() -> void:
	var se := _make_se()
	se.duration = 0.0  # permanente
	se.apply()
	se._process(999.0)
	assert_bool(se.is_active()).is_true()
	se.queue_free()


func test_tick_deals_damage() -> void:
	var parent := Node2D.new()
	add_child(parent)
	var health := Health.new()
	health.max_hp = 100
	parent.add_child(health)
	var se := _make_se()
	se.tick_interval = 0.5
	se.tick_damage = 10
	parent.add_child(se)
	se.apply()

	var hp_before := health.current_hp
	se._process(0.6)  # tick dispara
	assert_int(health.current_hp).is_less(hp_before)

	remove_child(parent)
	parent.queue_free()
	health.queue_free()
	se.queue_free()


func test_tick_heals_with_negative_damage() -> void:
	var parent := Node2D.new()
	add_child(parent)
	var health := Health.new()
	health.max_hp = 100
	health.current_hp = 50
	parent.add_child(health)
	var se := _make_se()
	se.tick_interval = 0.5
	se.tick_damage = -5  # cura
	parent.add_child(se)
	se.apply()

	se._process(0.6)
	assert_int(health.current_hp).is_greater(50)

	remove_child(parent)
	parent.queue_free()
	health.queue_free()
	se.queue_free()


func test_tick_multiplied_by_stacks() -> void:
	var parent := Node2D.new()
	add_child(parent)
	var health := Health.new()
	health.max_hp = 100
	parent.add_child(health)
	var se := _make_se()
	se.tick_interval = 0.5
	se.tick_damage = 5
	se.max_stacks = 3
	parent.add_child(se)
	se.apply()
	se.apply()
	se.apply()  # 3 stacks

	var hp_before := health.current_hp
	se._process(0.6)  # 5 * 3 = 15 dano
	assert_int(health.current_hp).is_equal(hp_before - 15)

	remove_child(parent)
	parent.queue_free()
	health.queue_free()
	se.queue_free()


func test_applied_signal() -> void:
	var se := _make_se()
	var emitted := false
	se.applied.connect(func(): emitted = true)
	se.apply()
	assert_bool(emitted).is_true()
	se.queue_free()


func test_refreshed_signal() -> void:
	var se := _make_se()
	se.apply()
	var emitted := false
	se.refreshed.connect(func(): emitted = true)
	se.refresh()
	assert_bool(emitted).is_true()
	se.queue_free()


func test_expired_signal() -> void:
	var se := _make_se()
	se.duration = 0.5
	se.apply()
	var emitted := false
	se.expired.connect(func(): emitted = true)
	se._process(0.6)
	assert_bool(emitted).is_true()
	se.queue_free()


func test_removed_signal() -> void:
	var se := _make_se()
	se.apply()
	var emitted := false
	se.removed.connect(func(): emitted = true)
	se.remove()
	assert_bool(emitted).is_true()
	se.queue_free()


func test_remaining_time() -> void:
	var se := _make_se()
	se.duration = 10.0
	se.apply()
	se._process(3.0)
	assert_float(se.get_remaining_time()).is_equal(7.0)
	se.queue_free()


func test_permanent_remaining_time() -> void:
	var se := _make_se()
	se.duration = 0.0
	se.apply()
	assert_float(se.get_remaining_time()).is_equal(-1.0)
	se.queue_free()


func test_duration_clamped() -> void:
	var se := _make_se()
	se.duration = -5.0
	assert_float(se.duration).is_equal(0.0)
	se.duration = 999.0
	assert_float(se.duration).is_equal(300.0)
	se.queue_free()


func test_max_stacks_clamped() -> void:
	var se := _make_se()
	se.max_stacks = 0
	assert_int(se.max_stacks).is_equal(1)
	se.max_stacks = 999
	assert_int(se.max_stacks).is_equal(99)
	se.queue_free()
