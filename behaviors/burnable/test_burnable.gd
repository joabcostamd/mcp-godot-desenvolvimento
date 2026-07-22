## test_burnable.gd — GdUnit4.

extends GdUnitTestSuite

func _make_b() -> Burnable: return Burnable.new()

func test_defaults() -> void:
	var b := _make_b()
	assert_float(b.ignition_time).is_equal(0.5)
	assert_float(b.burn_duration).is_equal(5)
	assert_float(b.burn_dps).is_equal(10)
	assert_float(b.spread_radius).is_equal(100); b.queue_free()

func test_not_burning_initially() -> void:
	var b := _make_b(); add_child(b)
	assert_bool(b.is_burning()).is_false()
	remove_child(b); b.queue_free()

func test_ignites_on_fire_damage() -> void:
	var p := Node2D.new(); add_child(p)
	var h := Health.new(); h.max_hp = 10; p.add_child(h)
	var b := _make_b(); p.add_child(b)
	b._on_damage(1, 9, "fire")
	assert_bool(b._igniting).is_true()
	remove_child(p); p.queue_free(); h.queue_free(); b.queue_free()

func test_ignores_non_fire() -> void:
	var p := Node2D.new(); add_child(p)
	var h := Health.new(); h.max_hp = 10; p.add_child(h)
	var b := _make_b(); p.add_child(b)
	b._on_damage(1, 9, "physical")
	assert_bool(b._igniting).is_false()
	remove_child(p); p.queue_free(); h.queue_free(); b.queue_free()

func test_extinguish() -> void:
	var b := _make_b(); add_child(b)
	b._burning = true; b._igniting = true
	b.extinguish()
	assert_bool(b.is_burning()).is_false()
	assert_bool(b._igniting).is_false()
	remove_child(b); b.queue_free()

func test_burn_deals_damage() -> void:
	var p := Node2D.new(); add_child(p)
	var h := Health.new(); h.max_hp = 100; p.add_child(h)
	var b := _make_b(); b.burn_dps = 50; p.add_child(b)
	var hp_before := h.current_hp
	b._burning = true
	b._physics_process(1.0)  # 1s de burn a 50 dps
	assert_int(h.current_hp).is_less(hp_before)
	remove_child(p); p.queue_free(); h.queue_free(); b.queue_free()

func test_setters() -> void:
	var b := _make_b()
	b.ignition_time = -1; assert_float(b.ignition_time).is_equal(0)
	b.burn_duration = 0.1; assert_float(b.burn_duration).is_equal(0.5)
	b.burn_dps = 0; assert_float(b.burn_dps).is_equal(1)
	b.spread_radius = -10; assert_float(b.spread_radius).is_equal(0); b.queue_free()
