## test_day_night_cycle.gd — Testes do behavior DayNightCycle | GdUnit4.

extends GdUnitTestSuite


func _make_dn(dur := 10.0) -> DayNightCycle:
	var dn := DayNightCycle.new()
	dn.cycle_duration = dur
	dn.auto_start = false
	return dn


func test_script_compiles() -> void:
	var dn := DayNightCycle.new()
	assert_object(dn).is_not_null()
	dn.queue_free()


func test_default_parameters() -> void:
	var dn := DayNightCycle.new()
	assert_float(dn.cycle_duration).is_equal(300.0)
	assert_bool(dn.auto_start).is_true()
	dn.queue_free()


func test_start_activates() -> void:
	var dn := _make_dn()
	add_child(dn)
	dn.start()
	assert_bool(dn.is_active()).is_true()
	remove_child(dn)
	dn.queue_free()


func test_stop_deactivates() -> void:
	var dn := _make_dn()
	add_child(dn)
	dn.start()
	dn.stop()
	assert_bool(dn.is_active()).is_false()
	remove_child(dn)
	dn.queue_free()


func test_get_phase_day() -> void:
	var dn := _make_dn()
	dn._elapsed = 3.0  # 3/10 = 0.3 -> day
	assert_str(dn.get_phase()).is_equal("day")
	dn.queue_free()


func test_get_phase_night() -> void:
	var dn := _make_dn()
	dn._elapsed = 8.0  # 8/10 = 0.8 -> night
	assert_str(dn.get_phase()).is_equal("night")
	dn.queue_free()
