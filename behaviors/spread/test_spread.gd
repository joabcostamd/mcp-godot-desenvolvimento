extends GdUnitTestSuite
func _make_s() -> Spread: return Spread.new()
func test_defaults() -> void:
	var s := _make_s(); assert_float(s.base_spread).is_equal(2); assert_float(s.max_spread).is_equal(15); s.queue_free()
func test_get_angle_returns_radians() -> void:
	var s := _make_s(); add_child(s); var a := s.get_angle()
	assert_float(abs(a)).is_less_equal(deg_to_rad(15)); remove_child(s); s.queue_free()
func test_spread_accumulates() -> void:
	var s := _make_s(); add_child(s)
	s.get_angle(); s.get_angle(); s.get_angle()
	assert_float(s._current_spread).is_greater(2); remove_child(s); s.queue_free()
func test_reset() -> void:
	var s := _make_s(); add_child(s); s.get_angle(); s.get_angle()
	s.reset_spread(); assert_float(s._current_spread).is_equal(2); remove_child(s); s.queue_free()
func test_clamped() -> void:
	var s := _make_s(); s.base_spread = -1; assert_float(s.base_spread).is_equal(0)
	s.max_spread = 999; assert_float(s.max_spread).is_equal(90); s.queue_free()
