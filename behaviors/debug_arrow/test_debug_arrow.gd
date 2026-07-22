## test_debug_arrow.gd — GdUnit4.
extends GdUnitTestSuite
func _make_da() -> DebugArrow: return DebugArrow.new()
func test_defaults() -> void:
	var da := _make_da(); assert_float(da.length).is_equal(64); assert_that(da.direction).is_equal(Vector2(1,0)); da.queue_free()
func test_length_clamped() -> void:
	var da := _make_da(); da.length = 1; assert_float(da.length).is_equal(8); da.length = 999; assert_float(da.length).is_equal(256); da.queue_free()
func test_direction_normalized() -> void:
	var da := _make_da(); da.direction = Vector2(10,0); assert_float(da.direction.length()).is_equal(1.0); da.queue_free()
func test_zero_direction_defaults() -> void:
	var da := _make_da(); da.direction = Vector2.ZERO; assert_that(da.direction).is_equal(Vector2(1,0)); da.queue_free()
func test_color_setter() -> void:
	var da := _make_da(); da.color = Color.BLUE; assert_that(da.color).is_equal(Color.BLUE); da.queue_free()
