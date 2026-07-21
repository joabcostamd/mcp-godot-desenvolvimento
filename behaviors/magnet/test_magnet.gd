## test_magnet.gd
extends GdUnitTestSuite
func _make_m() -> Magnet: return Magnet.new()
func test_defaults() -> void:
	var m := _make_m()
	assert_float(m.force).is_equal(500); assert_int(m.falloff).is_equal(1); m.queue_free()
func test_no_crash() -> void:
	var m := _make_m(); add_child(m); m._physics_process(0.1); remove_child(m); m.queue_free()
func test_setters() -> void:
	var m := _make_m(); m.force = 5; assert_float(m.force).is_equal(10)
	m.falloff = -1; assert_int(m.falloff).is_equal(0); m.queue_free()
