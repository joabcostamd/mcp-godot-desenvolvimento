## test_camera_framed.gd — Testes do CameraFramed | GdUnit4.

extends GdUnitTestSuite


func _make_framed() -> CameraFramed:
	return CameraFramed.new()


func _make_camera() -> Camera2D:
	var cam := Camera2D.new()
	cam.global_position = Vector2(500, 400)
	return cam


func _make_target(pos: Vector2 = Vector2.ZERO) -> Node2D:
	var t := Node2D.new()
	t.global_position = pos
	return t


# ---------------------------------------------------------------------------
# DEAD ZONE
# ---------------------------------------------------------------------------

func test_target_in_dead_zone_no_camera_movement() -> void:
	var cam := _make_camera()
	var framed := _make_framed()
	var t := _make_target(Vector2(520, 410))  # 20,10 de distância — dentro da dead zone 100x60
	cam.add_child(framed)
	framed.target = t

	var original := cam.global_position
	framed._process(0.016)

	assert_vector(cam.global_position).is_equal(original)  # câmera não mexeu

	cam.queue_free()


func test_target_outside_dead_zone_moves_camera() -> void:
	var cam := _make_camera()
	var framed := _make_framed()
	framed.damping = 1.0  # snap instantâneo
	var t := _make_target(Vector2(700, 400))  # 200px à direita — fora da dead zone 100x60
	cam.add_child(framed)
	framed.target = t

	framed._process(0.016)

	assert_bool(cam.global_position.x > 500.0).is_true()  # câmera moveu para direita

	cam.queue_free()


func test_is_target_in_dead_zone() -> void:
	var cam := _make_camera()
	var framed := _make_framed()
	cam.add_child(framed)

	# Dentro da dead zone
	var t_inside := _make_target(Vector2(520, 410))
	framed.target = t_inside
	assert_bool(framed.is_target_in_dead_zone()).is_true()

	# Fora da dead zone
	var t_outside := _make_target(Vector2(800, 400))
	framed.target = t_outside
	assert_bool(framed.is_target_in_dead_zone()).is_false()

	cam.queue_free()


# ---------------------------------------------------------------------------
# SIGNAL
# ---------------------------------------------------------------------------

func test_target_entered_dead_zone_signal() -> void:
	var cam := _make_camera()
	var framed := _make_framed()
	framed.dead_zone = Vector2(100, 60)
	framed.soft_zone = Vector2(0, 0)
	framed.damping = 1.0

	# Começa fora
	var t := _make_target(Vector2(800, 400))
	cam.add_child(framed)
	framed.target = t

	var emitted := false
	framed.target_entered_dead_zone.connect(func(): emitted = true)

	framed._process(0.016)  # move câmera para perto do target

	# Após o snap, o target deve estar dentro da dead zone
	# Vamos verificar manualmente — posiciona target dentro
	t.global_position = cam.global_position + Vector2(20, 10)
	framed._process(0.016)

	assert_bool(emitted).is_true()

	cam.queue_free()


# ---------------------------------------------------------------------------
# DAMPING
# ---------------------------------------------------------------------------

func test_damping_controls_speed() -> void:
	var cam := _make_camera()
	var framed_fast := _make_framed()
	var framed_slow := _make_framed()

	framed_fast.damping = 1.0
	framed_slow.damping = 0.01

	var t_fast := _make_target(Vector2(800, 400))
	var t_slow := _make_target(Vector2(800, 400))

	cam.add_child(framed_fast)
	framed_fast.target = t_fast

	var cam2 := _make_camera()
	cam2.add_child(framed_slow)
	framed_slow.target = t_slow

	var pos_fast_before := cam.global_position
	var pos_slow_before := cam2.global_position

	framed_fast._process(0.016)
	framed_slow._process(0.016)

	var move_fast := absf(cam.global_position.x - pos_fast_before.x)
	var move_slow := absf(cam2.global_position.x - pos_slow_before.x)

	assert_bool(move_fast > move_slow).is_true()  # damping=1 move mais que damping=0.01

	cam.queue_free()
	cam2.queue_free()


# ---------------------------------------------------------------------------
# EDGE CASES
# ---------------------------------------------------------------------------

func test_no_target_no_crash() -> void:
	var cam := _make_camera()
	var framed := _make_framed()
	cam.add_child(framed)
	framed._process(0.016)  # no-op, sem crash
	cam.queue_free()


func test_no_camera_no_crash() -> void:
	var framed := _make_framed()
	var t := _make_target(Vector2(100, 100))
	framed.target = t
	framed._process(0.016)  # no-op, sem crash
	framed.queue_free()
