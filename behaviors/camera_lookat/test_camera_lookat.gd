extends GdUnitTestSuite
func test_defaults() -> void:
	var cl:=CameraLookAt.new(); assert_float(cl.damping).is_equal(0.1); cl.queue_free()
func test_set_target() -> void:
	var cl:=CameraLookAt.new(); var t:=Node2D.new(); cl.set_target_node(t); assert_bool(cl._target_node==t).is_true(); cl.queue_free()
func test_camera_moves_toward_target() -> void:
	var cam:=Camera2D.new(); cam.global_position=Vector2.ZERO
	var cl:=CameraLookAt.new(); cl.damping=1.0; cam.add_child(cl)
	var t:=Node2D.new(); t.global_position=Vector2(100,0); cl.set_target_node(t)
	cl._process(0.016)
	assert_float(cam.global_position.x).is_equal(100.0)
	cam.queue_free()
