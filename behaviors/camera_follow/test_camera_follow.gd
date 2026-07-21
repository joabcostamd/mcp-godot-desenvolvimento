## test_camera_follow.gd — Testes do CameraFollow | GdUnit4.

extends GdUnitTestSuite

func _make_cf() -> CameraFollow:
	return CameraFollow.new()


func test_default_parameters() -> void:
	var cf := _make_cf()
	assert_float(cf.damping).is_equal(0.1)
	assert_float(cf.look_ahead).is_equal(0.0)
	assert_that(cf.offset).is_equal(Vector2.ZERO)
	cf.queue_free()


func test_set_target() -> void:
	var cf := _make_cf()
	var target := Node2D.new()
	cf.set_target(target)
	assert_object(cf._target_node).is_not_null()
	target.queue_free()
	cf.queue_free()


func test_damping_clamped() -> void:
	var cf := _make_cf()
	cf.damping = -1.0
	assert_float(cf.damping).is_equal(0.0)
	cf.damping = 2.0
	assert_float(cf.damping).is_equal(1.0)
	cf.queue_free()


func test_look_ahead_clamped() -> void:
	var cf := _make_cf()
	cf.look_ahead = -10.0
	assert_float(cf.look_ahead).is_equal(0.0)
	cf.look_ahead = 999.0
	assert_float(cf.look_ahead).is_equal(200.0)
	cf.queue_free()


func test_process_without_camera() -> void:
	var cf := _make_cf()
	add_child(cf)
	cf._process(0.1)  # sem camera — nao crasha
	assert_bool(true).is_true()
	remove_child(cf)
	cf.queue_free()


func test_process_without_target() -> void:
	var camera := Camera2D.new()
	add_child(camera)
	var cf := _make_cf()
	camera.add_child(cf)
	cf._process(0.1)  # sem target — nao crasha
	assert_bool(true).is_true()
	remove_child(camera)
	camera.queue_free()
	cf.queue_free()


func test_camera_moves_toward_target() -> void:
	var camera := Camera2D.new()
	camera.global_position = Vector2(0, 0)
	camera.enabled = true
	add_child(camera)
	var target := Node2D.new()
	target.global_position = Vector2(100, 0)
	add_child(target)
	var cf := _make_cf()
	cf.damping = 0.0  # instantaneo
	camera.add_child(cf)
	cf.set_target(target)

	cf._process(0.1)
	assert_that(camera.global_position).is_equal(Vector2(100, 0))

	remove_child(camera)
	remove_child(target)
	camera.queue_free()
	target.queue_free()
	cf.queue_free()


func test_damping_smooths_movement() -> void:
	var camera := Camera2D.new()
	camera.global_position = Vector2(0, 0)
	camera.enabled = true
	add_child(camera)
	var target := Node2D.new()
	target.global_position = Vector2(100, 0)
	add_child(target)
	var cf := _make_cf()
	cf.damping = 0.5
	camera.add_child(cf)
	cf.set_target(target)

	cf._process(0.1)
	# Com damping 0.5: lerp(0, 100, 0.5) = 50
	assert_float(camera.global_position.x).is_equal(50.0)

	remove_child(camera)
	remove_child(target)
	camera.queue_free()
	target.queue_free()
	cf.queue_free()
