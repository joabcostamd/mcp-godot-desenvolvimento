extends GdUnitTestSuite
func _make_pf() -> Pathfinding: return Pathfinding.new()
func test_defaults() -> void:
	var pf := _make_pf(); assert_float(pf.speed).is_equal(150); assert_float(pf.arrival_distance).is_equal(8); pf.queue_free()
func test_creates_agent() -> void:
	var pf := _make_pf(); add_child(pf); assert_object(pf._agent).is_not_null(); remove_child(pf); pf.queue_free()
func test_set_clear_target() -> void:
	var pf := _make_pf(); add_child(pf); pf.set_target(Vector2(100,0))
	assert_bool(pf.is_navigating()).is_true(); pf.clear_target()
	assert_bool(pf.is_navigating()).is_false(); remove_child(pf); pf.queue_free()
func test_speed_clamped() -> void:
	var pf := _make_pf(); pf.speed = 5; assert_float(pf.speed).is_equal(10)
	pf.speed = 9999; assert_float(pf.speed).is_equal(2000); pf.queue_free()
