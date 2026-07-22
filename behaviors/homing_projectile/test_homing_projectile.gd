## test_homing_projectile.gd — Testes do HomingProjectile | GdUnit4.

extends GdUnitTestSuite


func test_moves_toward_target() -> void:
	var hp := _make_hp(300.0, 3.0, 20, 5.0)
	var target := Node2D.new()
	target.global_position = Vector2(100, 0)
	add_child(hp)
	add_child(target)
	hp.set_target(target)
	await get_tree().physics_frame
	assert_float(hp.global_position.x).is_greater(0.0)


func test_deals_damage() -> void:
	var hp := _make_hp(300.0, 3.0, 25, 5.0)
	var h := _make_health(100)
	var t := Node2D.new(); t.add_child(h)
	add_child(hp); add_child(t)
	hp._handle_hit(t)
	assert_int(h.current_hp).is_equal(75)


func test_hit_signal() -> void:
	var hp := _make_hp(300.0, 3.0, 30, 5.0)
	var h := _make_health(100)
	var t := Node2D.new(); t.add_child(h)
	add_child(hp); add_child(t)
	var fired := false; var dmg := 0
	hp.hit.connect(func(_t, d): fired = true; dmg = d)
	hp._handle_hit(t)
	assert_bool(fired).is_true(); assert_int(dmg).is_equal(30)


func test_target_null_does_not_crash() -> void:
	var hp := _make_hp(300.0, 3.0, 20, 5.0)
	add_child(hp)
	hp._physics_process(0.016)
	assert_bool(true)  # não crashou


func test_target_freed_cleared() -> void:
	var hp := _make_hp(300.0, 3.0, 20, 5.0)
	var t := Node2D.new()
	add_child(hp); add_child(t)
	hp.set_target(t)
	remove_child(t); t.free()
	hp._physics_process(0.016)  # P8: não deve crashar
	assert_bool(true)


func test_set_target() -> void:
	var hp := _make_hp(300.0, 3.0, 20, 5.0)
	var t := Node2D.new()
	hp.set_target(t)
	assert_object(hp._target).is_not_null()


# ── Helpers ──────────────────────────────────────────────────────────────────
func _make_hp(spd: float, tr: float, dmg: int, life: float) -> HomingProjectile:
	var p := HomingProjectile.new(); p.speed = spd; p.turn_rate = tr; p.damage = dmg; p.lifetime = life; return p

func _make_health(hp: int) -> Health:
	var h := Health.new(); h.max_hp = hp; h.current_hp = hp; return h
