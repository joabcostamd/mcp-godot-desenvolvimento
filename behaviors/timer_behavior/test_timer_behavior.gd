## test_timer.gd — Testes do behavior TimerBehavior | GdUnit4.

extends GdUnitTestSuite


func _make_tb() -> TimerBehavior:
	return TimerBehavior.new()


func test_script_compiles() -> void:
	var tb := TimerBehavior.new()
	assert_object(tb).is_not_null()
	tb.queue_free()


func test_default_parameters() -> void:
	var tb := TimerBehavior.new()
	assert_float(tb.wait_time).is_equal(1.0)
	assert_bool(tb.one_shot).is_false()
	assert_bool(tb.auto_start).is_false()
	tb.queue_free()


func test_start_creates_timer() -> void:
	var tb := _make_tb()
	add_child(tb)
	tb.start()
	assert_bool(tb.is_running()).is_true()
	remove_child(tb)
	tb.queue_free()


func test_stop_stops() -> void:
	var tb := _make_tb()
	add_child(tb)
	tb.start()
	tb.stop()
	assert_bool(tb.is_running()).is_false()
	remove_child(tb)
	tb.queue_free()


func test_restart() -> void:
	var tb := _make_tb()
	add_child(tb)
	tb.start()
	tb.restart()
	assert_bool(tb.is_running()).is_true()
	remove_child(tb)
	tb.queue_free()


func test_one_shot_emits_timeout() -> void:
	var tb := _make_tb()
	tb.one_shot = true
	tb.wait_time = 0.02
	add_child(tb)
	var emitted := false
	tb.timeout.connect(func(): emitted = true)
	tb.start()
	await get_tree().create_timer(0.1).timeout
	assert_bool(emitted).is_true()
	remove_child(tb)
	tb.queue_free()
