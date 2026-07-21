extends GdUnitTestSuite
func test_defaults() -> void:
	var d:=DebugArrow.new(); assert_float(d.length).is_equal(64); d.queue_free()
