extends GdUnitTestSuite
func test_detection() -> void:
	var s:=Stealth.new(); s.add_detection(0.6); assert_float(s.get_detection_level()).is_equal(0.6); s.queue_free()
