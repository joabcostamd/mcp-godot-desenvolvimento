extends GdUnitTestSuite
func test_defaults() -> void: var t:=TextSize.new(); assert_float(t.scale_multiplier).is_equal(1.0); t.queue_free()
