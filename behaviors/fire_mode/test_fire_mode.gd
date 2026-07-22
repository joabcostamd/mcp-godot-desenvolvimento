extends GdUnitTestSuite
func _make_fm() -> FireMode: return FireMode.new()
func test_defaults() -> void:
	var fm := _make_fm(); assert_int(fm.mode).is_equal(0); assert_int(fm.burst_count).is_equal(3); fm.queue_free()
func test_mode_clamped() -> void:
	var fm := _make_fm(); fm.mode = -1; assert_int(fm.mode).is_equal(0)
	fm.mode = 99; assert_int(fm.mode).is_equal(2); fm.queue_free()
func test_semi_blocks_second_shot() -> void:
	var fm := _make_fm(); fm.mode = 2  # SEMI
	Input.action_press("ui_accept")
	assert_bool(fm.can_fire()).is_true()
	assert_bool(fm.can_fire()).is_false()  # bloqueado
	fm.reset_semi(); Input.action_release("ui_accept")
	assert_bool(fm.can_fire()).is_true()  # liberado
	fm.queue_free()
func test_burst_count() -> void:
	var fm := _make_fm(); fm.mode = 1  # BURST
	assert_int(fm.get_burst_count()).is_equal(3)
	fm.mode = 0  # AUTO
	assert_int(fm.get_burst_count()).is_equal(1); fm.queue_free()
func test_mode_changed_signal() -> void:
	var fm := _make_fm(); var emitted := false
	fm.mode_changed.connect(func(_m): emitted = true)
	fm.mode = 1; assert_bool(emitted).is_true(); fm.queue_free()
