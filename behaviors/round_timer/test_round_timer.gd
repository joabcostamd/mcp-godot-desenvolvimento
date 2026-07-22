## test_round_timer.gd — Testes do behavior RoundTimer | GdUnit4.

extends GdUnitTestSuite


func _make_rt(dur := 3.0) -> RoundTimer:
	var rt := RoundTimer.new()
	rt.duration = dur
	return rt


func test_script_compiles() -> void:
	var rt := RoundTimer.new()
	assert_object(rt).is_not_null()
	rt.queue_free()


func test_default_parameters() -> void:
	var rt := RoundTimer.new()
	assert_float(rt.duration).is_equal(60.0)
	assert_bool(rt.countdown).is_true()
	assert_bool(rt.pause_on_end).is_false()
	rt.queue_free()


func test_start_activates() -> void:
	var rt := _make_rt()
	add_child(rt)
	rt.start()
	assert_bool(rt.is_active()).is_true()
	remove_child(rt)
	rt.queue_free()


func test_get_remaining_countdown() -> void:
	var rt := _make_rt(10.0)
	rt.countdown = true
	rt._elapsed = 3.0
	assert_float(rt.get_remaining()).is_equal(7.0)
	rt.queue_free()


func test_get_remaining_countup() -> void:
	var rt := _make_rt(10.0)
	rt.countdown = false
	rt._elapsed = 3.0
	assert_float(rt.get_remaining()).is_equal(3.0)
	rt.queue_free()


func test_stop_deactivates() -> void:
	var rt := _make_rt()
	add_child(rt)
	rt.start()
	rt.stop()
	assert_bool(rt.is_active()).is_false()
	remove_child(rt)
	rt.queue_free()
