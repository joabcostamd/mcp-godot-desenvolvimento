extends GdUnitTestSuite
func _make_av() -> Avoidance: return Avoidance.new()
func test_defaults() -> void:
	var av := _make_av(); assert_float(av.radius).is_equal(32); assert_float(av.priority).is_equal(1); av.queue_free()
func test_creates_agent() -> void:
	var av := _make_av(); add_child(av); assert_object(av._agent).is_not_null(); remove_child(av); av.queue_free()
func test_radius_clamped() -> void:
	var av := _make_av(); av.radius = 1; assert_float(av.radius).is_equal(4)
	av.radius = 999; assert_float(av.radius).is_equal(128); av.queue_free()
