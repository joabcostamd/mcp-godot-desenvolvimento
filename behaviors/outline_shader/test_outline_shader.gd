extends GdUnitTestSuite
func test_defaults() -> void: var o:=OutlineShader.new(); assert_float(o.outline_width).is_equal(1); o.queue_free()
