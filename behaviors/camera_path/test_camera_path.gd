extends GdUnitTestSuite
func test_defaults() -> void:
	var cp:=CameraPath.new(); assert_float(cp.speed).is_equal(100.0); assert_bool(cp.loop).is_false(); cp.queue_free()
func test_start_sets_moving() -> void:
	var cp:=CameraPath.new(); cp.start(); assert_bool(cp._moving).is_true(); cp.stop(); cp.queue_free()
func test_stop() -> void:
	var cp:=CameraPath.new(); cp.start(); cp.stop(); assert_bool(cp._moving).is_false(); cp.queue_free()
