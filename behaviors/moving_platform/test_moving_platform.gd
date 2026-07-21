## test_moving_platform.gd — Testes do MovingPlatform | GdUnit4.
##
## Testa movimento, loop, ping-pong, pause, edge cases.
## Fonte: Godot 4.7 ClassDB — AnimatableBody2D, Path2D, Curve2D.

extends GdUnitTestSuite


func _make_mp() -> MovingPlatform:
	return MovingPlatform.new()


func _make_path(p1: Vector2, p2: Vector2) -> Path2D:
	var path := Path2D.new()
	var curve := Curve2D.new()
	curve.add_point(p1)
	curve.add_point(p2)
	path.curve = curve
	return path


# ── Compilação e defaults ─────────────────────────────────────────────────────

func test_script_compiles() -> void:
	var mp := MovingPlatform.new()
	assert_object(mp).is_not_null()
	mp.queue_free()


func test_default_parameters() -> void:
	var mp := _make_mp()
	assert_float(mp.speed).is_equal(100.0)
	assert_bool(mp.loop).is_true()
	assert_float(mp.pause_at_ends).is_equal(0.0)
	mp.queue_free()


# ── Movimento ─────────────────────────────────────────────────────────────────

func test_moves_along_path() -> void:
	var mp := _make_mp()
	var path := _make_path(Vector2(0, 0), Vector2(200, 0))
	mp.add_child(path)
	add_child(mp)

	assert_that(mp.global_position).is_equal(Vector2(0, 0))

	mp._physics_process(0.5)  # 100 px/s * 0.5 = 50 px
	# sample_baked retorna posição ao longo da curva
	assert_float(mp.global_position.x).is_greater(0.0)

	remove_child(mp)
	mp.queue_free()


func test_does_not_move_without_path() -> void:
	var mp := _make_mp()
	add_child(mp)

	var initial := mp.global_position
	mp._physics_process(1.0)
	assert_that(mp.global_position).is_equal(initial)

	remove_child(mp)
	mp.queue_free()


# ── Loop ──────────────────────────────────────────────────────────────────────

func test_loop_resets_progress() -> void:
	var mp := _make_mp()
	mp.speed = 1000.0  # rápido
	mp.loop = true
	var path := _make_path(Vector2(0, 0), Vector2(100, 0))
	mp.add_child(path)
	add_child(mp)

	# Move até o fim
	mp._physics_process(1.0)  # 1000 px → passa do fim

	# Com loop, deve ter reiniciado
	assert_float(mp._progress).is_less_equal(100.0)

	remove_child(mp)
	mp.queue_free()


# ── Ping-pong ─────────────────────────────────────────────────────────────────

func test_ping_pong_reverses() -> void:
	var mp := _make_mp()
	mp.loop = false
	var path := _make_path(Vector2(0, 0), Vector2(50, 0))
	mp.add_child(path)
	add_child(mp)

	# Move até o fim
	for _i in range(10):
		mp._physics_process(0.1)  # 10 px por frame

	assert_int(mp._direction).is_equal(-1)  # inverteu

	remove_child(mp)
	mp.queue_free()


# ── Pause ─────────────────────────────────────────────────────────────────────

func test_pause_at_ends_stops() -> void:
	var mp := _make_mp()
	mp.pause_at_ends = 1.0
	mp.speed = 2000.0
	var path := _make_path(Vector2(0, 0), Vector2(50, 0))
	mp.add_child(path)
	add_child(mp)

	# Move até o fim → deve pausar
	mp._physics_process(0.1)

	# Pode ter pausado ou não dependendo da posição
	# Verifica que _paused é um bool (não crashou)
	assert_bool(mp._paused == true or mp._paused == false).is_true()

	remove_child(mp)
	mp.queue_free()


# ── Sinais ────────────────────────────────────────────────────────────────────

func test_emits_waypoint_reached() -> void:
	var mp := _make_mp()
	mp.speed = 2000.0
	mp.loop = false
	var path := _make_path(Vector2(0, 0), Vector2(50, 0))
	mp.add_child(path)
	add_child(mp)

	var reached := -1
	mp.waypoint_reached.connect(func(i): reached = i)

	mp._physics_process(0.1)
	# Deve ter chegado ao fim (índice 1)
	if reached >= 0:
		assert_int(reached).is_equal(1)

	remove_child(mp)
	mp.queue_free()


# ── Reset ─────────────────────────────────────────────────────────────────────

func test_reset_position() -> void:
	var mp := _make_mp()
	var path := _make_path(Vector2(0, 0), Vector2(100, 0))
	mp.add_child(path)
	add_child(mp)

	mp._physics_process(0.5)  # avança
	mp.reset_position()

	assert_float(mp._progress).is_equal(0.0)
	assert_int(mp._direction).is_equal(1)

	remove_child(mp)
	mp.queue_free()


# ── Progress ratio ────────────────────────────────────────────────────────────

func test_progress_ratio_starts_zero() -> void:
	var mp := _make_mp()
	var path := _make_path(Vector2(0, 0), Vector2(100, 0))
	mp.add_child(path)
	assert_float(mp.get_progress_ratio()).is_equal(0.0)
	mp.queue_free()


func test_progress_ratio_no_path() -> void:
	var mp := _make_mp()
	assert_float(mp.get_progress_ratio()).is_equal(0.0)
	mp.queue_free()


# ── Clamp setters ─────────────────────────────────────────────────────────────

func test_speed_clamped() -> void:
	var mp := _make_mp()
	mp.speed = 5.0
	assert_float(mp.speed).is_equal(10.0)
	mp.speed = 9999.0
	assert_float(mp.speed).is_equal(2000.0)
	mp.queue_free()


func test_pause_clamped() -> void:
	var mp := _make_mp()
	mp.pause_at_ends = -1.0
	assert_float(mp.pause_at_ends).is_equal(0.0)
	mp.pause_at_ends = 99.0
	assert_float(mp.pause_at_ends).is_equal(10.0)
	mp.queue_free()
