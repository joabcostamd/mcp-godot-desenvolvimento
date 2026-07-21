## test_outline.gd — GdUnit4.

extends GdUnitTestSuite

func _make_ol() -> Outline: return Outline.new()

func test_defaults() -> void:
	var ol := _make_ol()
	assert_float(ol.outline_width).is_equal(2)
	var c: Color = ol.outline_color
	assert_float(c.r).is_equal(1); ol.queue_free()

func test_no_parent_does_not_crash() -> void:
	var ol := _make_ol()
	ol._setup_outline()  # sem parent CanvasItem
	assert_object(ol._material).is_null(); ol.queue_free()

func test_width_clamped() -> void:
	var ol := _make_ol()
	ol.outline_width = 0; assert_float(ol.outline_width).is_equal(1)
	ol.outline_width = 99; assert_float(ol.outline_width).is_equal(10); ol.queue_free()
