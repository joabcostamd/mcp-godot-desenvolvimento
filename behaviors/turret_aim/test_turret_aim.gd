## test_turret_aim.gd — Testes do TurretAim | GdUnit4.
##
## Cobre: rotação, mira, sinais, spawn de projétil,
##        edge cases, warnings.
##
## Requer: GdUnit4 instalado como addon.

extends GdUnitTestSuite


# ── Rotação ───────────────────────────────────────────────────────────────────

func test_rotates_toward_target() -> void:
	var ta := _make_turret(3.0, 400.0, 5.0)
	var target := Node2D.new()
	target.add_to_group("player")
	target.global_position = Vector2(100, 0)
	add_child(ta)
	add_child(target)

	ta._physics_process(0.016)
	assert_float(ta.rotation).is_not_equal(0.0)


func test_ignores_out_of_range() -> void:
	var ta := _make_turret(3.0, 100.0, 5.0)
	var target := Node2D.new()
	target.add_to_group("player")
	target.global_position = Vector2(200, 0)
	add_child(ta)
	add_child(target)

	ta._physics_process(0.016)
	assert_float(ta.rotation).is_equal(0.0)


# ── Sinais ────────────────────────────────────────────────────────────────────

func test_target_locked_signal() -> void:
	var ta := _make_turret(10.0, 400.0, 45.0)
	var target := Node2D.new()
	target.add_to_group("player")
	target.global_position = Vector2(100, 0)
	add_child(ta)
	add_child(target)

	var locked := false
	ta.target_locked.connect(func(_t): locked = true)
	ta._physics_process(0.016)
	assert_bool(locked).is_true()


func test_target_lost_signal() -> void:
	var ta := _make_turret(3.0, 100.0, 5.0)
	var target := Node2D.new()
	target.add_to_group("player")
	target.global_position = Vector2(200, 0)
	add_child(ta)
	add_child(target)

	ta._target = target
	ta._was_locked = true
	var lost := false
	ta.target_lost.connect(func(): lost = true)
	ta._physics_process(0.016)
	assert_bool(lost).is_true()


# ── Disparo ───────────────────────────────────────────────────────────────────

func test_spawns_projectile() -> void:
	var ta := _make_turret(10.0, 400.0, 45.0)
	var parent := Node2D.new()
	parent.add_child(ta)
	add_child(parent)

	var target := Node2D.new()
	target.add_to_group("player")
	target.global_position = Vector2(100, 0)
	add_child(target)
	ta._physics_process(0.016)  # mira

	var proj_spawned := false
	ta.fired.connect(func(_p): proj_spawned = true)
	ta._spawn_projectile()
	assert_bool(proj_spawned).is_true()


# ── _shortest_angle ───────────────────────────────────────────────────────────

func test_shortest_angle() -> void:
	var ta := _make_turret(3.0, 400.0, 5.0)
	add_child(ta)

	assert_float(ta._shortest_angle(0.0, PI)).is_equal(PI)
	assert_float(ta._shortest_angle(PI, 0.0)).is_equal(-PI)
	assert_float(ta._shortest_angle(0.0, 0.1)).is_equal(0.1)


# ── Edge cases ────────────────────────────────────────────────────────────────

func test_no_target_no_crash() -> void:
	var ta := _make_turret(3.0, 400.0, 5.0)
	add_child(ta)
	ta._physics_process(0.016)
	assert_bool(true)


func test_target_freed_cleared() -> void:
	var ta := _make_turret(3.0, 400.0, 5.0)
	var target := Node2D.new()
	target.add_to_group("player")
	target.global_position = Vector2(100, 0)
	add_child(ta)
	add_child(target)
	ta.set_target(target)
	remove_child(target)
	target.free()
	ta._physics_process(0.016)
	assert_bool(true)


# ── Parâmetros ────────────────────────────────────────────────────────────────

func test_rotation_speed_clamped() -> void:
	var ta := _make_turret(0.0, 400.0, 5.0)
	assert_float(ta.rotation_speed).is_equal(0.1)


func test_aim_tolerance_clamped() -> void:
	var ta := _make_turret(3.0, 400.0, 0.0)
	assert_float(ta.aim_tolerance_deg).is_equal(0.5)


# ── Warnings ──────────────────────────────────────────────────────────────────

func test_warning_no_fire_rate() -> void:
	var ta := _make_turret(3.0, 400.0, 5.0)
	add_child(ta)
	var found := false
	for w in ta._get_configuration_warnings():
		if "FireRate" in w:
			found = true
	assert_bool(found).is_true()


# ── Helpers ──────────────────────────────────────────────────────────────────

func _make_turret(rot_spd: float, drange: float, tolerance: float) -> TurretAim:
	var ta := TurretAim.new()
	ta.rotation_speed = rot_spd
	ta.detection_range = drange
	ta.aim_tolerance_deg = tolerance
	return ta
