## test_screen_shake.gd — Testes do behavior ScreenShake | GdUnit4.

extends GdUnitTestSuite


func _make_ss(intensity := 5.0, duration := 0.3, decay := 0.8) -> ScreenShake:
	var s := ScreenShake.new()
	s.intensity = intensity; s.duration = duration; s.decay = decay
	return s


func test_trigger_starts_shake() -> void:
	var ss := _make_ss(); add_child(ss)
	ss.trigger()
	assert_bool(ss.is_shaking()).is_true()


func test_trigger_emits_started() -> void:
	var ss := _make_ss(); add_child(ss)
	var emitted := false; ss.shake_started.connect(func(): emitted = true)
	ss.trigger()
	assert_bool(emitted).is_true()


func test_shake_ends_after_duration() -> void:
	var ss := _make_ss(5, 0.1, 0.0); add_child(ss)
	ss.trigger()
	ss._process(0.15)  # além da duração
	assert_bool(ss.is_shaking()).is_false()


func test_shake_emits_ended() -> void:
	var ss := _make_ss(5, 0.1, 0.0); add_child(ss)
	var emitted := false; ss.shake_ended.connect(func(): emitted = true)
	ss.trigger(); ss._process(0.15)
	assert_bool(emitted).is_true()


func test_trigger_during_shake_noop() -> void:
	var ss := _make_ss(5, 0.5, 0.0); add_child(ss)
	ss.trigger()
	var count := 0; ss.shake_started.connect(func(): count += 1)
	ss.trigger()
	assert_int(count).is_equal(0)


func test_is_shaking_initially_false() -> void:
	var ss := _make_ss(); add_child(ss)
	assert_bool(ss.is_shaking()).is_false()


func test_trigger_with_override() -> void:
	var ss := _make_ss(5, 0.5, 0.0); add_child(ss)
	ss.trigger(10.0)
	assert_bool(ss.is_shaking()).is_true()
