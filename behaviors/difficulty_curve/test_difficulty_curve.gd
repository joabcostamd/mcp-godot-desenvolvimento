extends GdUnitTestSuite
func _make_dc() -> DifficultyCurve: return DifficultyCurve.new()
func test_start_multiplier() -> void:
	var dc:=_make_dc(); dc._ready()
	assert_float(dc.get_multiplier()).is_equal(1.0); dc.queue_free()
func test_increases_over_time() -> void:
	var dc:=_make_dc(); dc.increase_per_minute=6.0; dc._ready()
	dc._process(30.0)  # 0.5 min
	assert_float(dc.get_multiplier()).is_greater(2.0); dc.queue_free()
func test_capped_at_max() -> void:
	var dc:=_make_dc(); dc.max_multiplier=3.0; dc.increase_per_minute=60.0; dc._ready()
	dc._process(999.0)
	assert_float(dc.get_multiplier()).is_equal(3.0); dc.queue_free()
func test_reset() -> void:
	var dc:=_make_dc(); dc._ready(); dc._process(120.0); dc.reset()
	assert_float(dc.get_multiplier()).is_equal(dc.start_multiplier); dc.queue_free()
