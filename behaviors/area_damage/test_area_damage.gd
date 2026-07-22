## test_area_damage.gd — Testes do behavior AreaDamage | GdUnit4.

extends GdUnitTestSuite


func test_explode_damages_health_in_range() -> void:
	var ad := _make_ad(50, 200.0, 0.0, 0.0)
	var health := _make_health(100)
	var target := Node2D.new()
	target.global_position = Vector2(50, 0)
	target.add_child(health)
	add_child(ad)
	add_child(target)

	var hit := ad.explode()
	assert_int(hit).is_equal(1)
	assert_int(health.current_hp).is_equal(50)


func test_falloff_reduces_damage_at_edge() -> void:
	var ad := _make_ad(100, 100.0, 1.0, 0.0)
	var health := _make_health(100)
	var target := Node2D.new()
	target.global_position = Vector2(100, 0)  # na borda
	target.add_child(health)
	add_child(ad)
	add_child(target)

	ad.explode()
	# falloff=1.0, t=1.0: dmg = 100*(1-1*1) = 0
	assert_int(health.current_hp).is_equal(100)


func test_no_falloff_full_damage_at_edge() -> void:
	var ad := _make_ad(100, 100.0, 0.0, 0.0)
	var health := _make_health(100)
	var target := Node2D.new()
	target.global_position = Vector2(100, 0)
	target.add_child(health)
	add_child(ad)
	add_child(target)

	ad.explode()
	assert_int(health.current_hp).is_equal(0)


func test_exploded_signal() -> void:
	var ad := _make_ad(50, 200.0, 0.0, 0.0)
	var health := _make_health(100)
	var target := Node2D.new()
	target.global_position = Vector2(10, 0)
	target.add_child(health)
	add_child(ad)
	add_child(target)

	var signal_fired := false
	var captured_hits := 0
	ad.exploded.connect(func(h):
		signal_fired = true
		captured_hits = h
	)

	ad.explode()
	assert_bool(signal_fired).is_true()
	assert_int(captured_hits).is_equal(1)


func test_explode_no_targets_returns_zero() -> void:
	var ad := _make_ad(50, 100.0, 0.0, 0.0)
	add_child(ad)
	var hit := ad.explode()
	assert_int(hit).is_equal(0)


func test_knockback_applied() -> void:
	var ad := _make_ad(50, 200.0, 0.0, 300.0)
	var kb := Knockback.new()
	kb.force = 200.0
	var parent := CharacterBody2D.new()
	parent.global_position = Vector2(50, 0)
	parent.add_child(kb)
	add_child(ad)
	add_child(parent)

	ad.explode()
	assert_float(parent.velocity.length()).is_greater(0.0)


func test_no_knockback_when_force_zero() -> void:
	var ad := _make_ad(50, 200.0, 0.0, 0.0)  # force=0
	var kb := Knockback.new()
	kb.force = 200.0
	var parent := CharacterBody2D.new()
	parent.global_position = Vector2(50, 0)
	parent.add_child(kb)
	add_child(ad)
	add_child(parent)

	ad.explode()
	assert_float(parent.velocity.length()).is_equal(0.0)


# ── Setters ──────────────────────────────────────────────────────────────────

func test_damage_clamped() -> void:
	var ad := _make_ad(50, 100.0, 0.0, 0.0)
	ad.damage = 0
	assert_int(ad.damage).is_equal(1)


# ── Helpers ──────────────────────────────────────────────────────────────────

func _make_ad(dmg: int, rad: float, fall: float, force: float) -> AreaDamage:
	var ad := AreaDamage.new()
	ad.damage = dmg
	ad.radius = rad
	ad.falloff = fall
	ad.explosion_force = force
	return ad


func _make_health(hp: int) -> Health:
	var h := Health.new()
	h.max_hp = hp
	h.current_hp = hp
	return h
