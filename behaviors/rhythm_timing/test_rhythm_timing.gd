extends GdUnitTestSuite
func test_bpm() -> void: var r:=RhythmTiming.new(); assert_float(r.bpm).is_equal(120); r.queue_free()
