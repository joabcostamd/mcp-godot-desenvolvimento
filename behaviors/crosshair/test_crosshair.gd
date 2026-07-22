extends GdUnitTestSuite
func _make_ch() -> Crosshair: return Crosshair.new()
func test_defaults() -> void:
	var ch := _make_ch(); assert_float(ch.crosshair_size).is_equal(16); assert_int(ch.crosshair_style).is_equal(0); ch.queue_free()
func test_style_clamped() -> void:
	var ch := _make_ch(); ch.crosshair_style = -1; assert_int(ch.crosshair_style).is_equal(0)
	ch.crosshair_style = 99; assert_int(ch.crosshair_style).is_equal(2); ch.queue_free()
func test_size_clamped() -> void:
	var ch := _make_ch(); ch.crosshair_size = 1; assert_float(ch.crosshair_size).is_equal(4)
	ch.crosshair_size = 999; assert_float(ch.crosshair_size).is_equal(64); ch.queue_free()
func test_gap_clamped() -> void:
	var ch := _make_ch(); ch.gap = -1; assert_float(ch.gap).is_equal(0)
	ch.gap = 999; assert_float(ch.gap).is_equal(32); ch.queue_free()
func test_color_setter() -> void:
	var ch := _make_ch(); ch.crosshair_color = Color.GREEN; assert_that(ch.crosshair_color).is_equal(Color.GREEN); ch.queue_free()
