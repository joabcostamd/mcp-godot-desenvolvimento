extends GdUnitTestSuite
func test_defaults() -> void:
	var dc:=DebugConsole.new(); assert_int(dc.max_lines).is_equal(200); dc.queue_free()
