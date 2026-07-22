## test_outline_shader.gd — GdUnit4.
extends GdUnitTestSuite
func _make_os() -> OutlineShader: return OutlineShader.new()
func test_defaults() -> void:
	var o := _make_os(); assert_float(o.outline_width).is_equal(1); o.queue_free()
func test_width_clamped() -> void:
	var o := _make_os(); o.outline_width = -1; assert_float(o.outline_width).is_equal(0); o.outline_width = 99; assert_float(o.outline_width).is_equal(5); o.queue_free()
func test_color_setter() -> void:
	var o := _make_os(); o.outline_color = Color.YELLOW; assert_that(o.outline_color).is_equal(Color.YELLOW); o.queue_free()
func test_ready_without_canvas_item() -> void:
	var o := _make_os(); add_child(o)  # parent é GdUnitTestSuite (não CanvasItem)
	assert_object(o._material).is_null(); remove_child(o); o.queue_free()
