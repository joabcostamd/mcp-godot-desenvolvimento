## test_debug_position.gd — GdUnit4.
extends GdUnitTestSuite
func _make_dp() -> DebugPosition: return DebugPosition.new()
func test_defaults() -> void:
	var dp := _make_dp(); assert_float(dp.size).is_equal(16); assert_bool(dp.show_label).is_false(); dp.queue_free()
func test_color_setter() -> void:
	var dp := _make_dp(); dp.color = Color.RED; assert_that(dp.color).is_equal(Color.RED); dp.queue_free()
func test_size_clamped() -> void:
	var dp := _make_dp(); dp.size = 1; assert_float(dp.size).is_equal(4); dp.size = 999; assert_float(dp.size).is_equal(64); dp.queue_free()
func test_show_label_setter() -> void:
	var dp := _make_dp(); dp.show_label = true; assert_bool(dp.show_label).is_true(); dp.queue_free()
