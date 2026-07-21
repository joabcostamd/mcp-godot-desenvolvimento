## test_rhythm_timing.gd — Testes do RhythmTiming | GdUnit4.

extends GdUnitTestSuite

func _make_rt() -> RhythmTiming: return RhythmTiming.new()

func test_default_parameters() -> void:
	var rt := _make_rt()
	assert_float(rt.bpm).is_equal(120.0)
	assert_float(rt.tolerance).is_equal(0.1)
	assert_str(rt.input_action).is_equal("ui_accept")
	rt.queue_free()

func test_beat_interval_calculated() -> void:
	var rt := _make_rt()
	add_child(rt)  # _ready calcula _beat_interval
	assert_float(rt._beat_interval).is_equal(0.5)  # 60/120
	remove_child(rt); rt.queue_free()

func test_beat_emitted() -> void:
	var rt := _make_rt()
	add_child(rt)
	var beat_count := 0
	rt.beat.connect(func(_n): beat_count += 1)
	# 60/120 = 0.5s por beat. 1s = 2 beats
	rt._physics_process(0.5)
	rt._physics_process(0.5)
	assert_int(beat_count).is_greater_equal(2)
	remove_child(rt); rt.queue_free()

func test_bpm_clamped() -> void:
	var rt := _make_rt()
	rt.bpm = 10.0; assert_float(rt.bpm).is_equal(30.0)
	rt.bpm = 500.0; assert_float(rt.bpm).is_equal(300.0)
	rt.queue_free()

func test_tolerance_clamped() -> void:
	var rt := _make_rt()
	rt.tolerance = 0.001; assert_float(rt.tolerance).is_equal(0.01)
	rt.tolerance = 2.0; assert_float(rt.tolerance).is_equal(0.5)
	rt.queue_free()

func test_check_hit_miss() -> void:
	var rt := _make_rt()
	add_child(rt)
	var miss_emitted := false
	rt.miss.connect(func(): miss_emitted = true)
	rt._timer = 999.0  # longe do beat
	rt._check_hit()
	assert_bool(miss_emitted).is_true()
	remove_child(rt); rt.queue_free()
