extends GdUnitTestSuite
func test_defaults() -> void:
	var f:=FPSCounter.new(); assert_float(f.update_interval).is_equal(0.5); f.queue_free()
