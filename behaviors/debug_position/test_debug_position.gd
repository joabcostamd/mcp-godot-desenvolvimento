extends GdUnitTestSuite
func test_defaults() -> void:
	var d:=DebugPosition.new(); assert_float(d.size).is_equal(16); d.queue_free()
