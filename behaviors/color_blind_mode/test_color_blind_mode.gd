extends GdUnitTestSuite
func test_defaults() -> void: var c:=ColorBlindMode.new(); assert_int(c.mode).is_equal(0); assert_float(c.intensity).is_equal(0.8); c.queue_free()
