extends GdUnitTestSuite
func test_progress() -> void: var d:=Dissolve.new(); d.set_progress(0.5); assert_float(d._progress).is_equal(0.5); d.queue_free()
