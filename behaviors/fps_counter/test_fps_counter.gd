## test_fps_counter.gd — Testes do FPSCounter | GdUnit4.

extends GdUnitTestSuite

func _make_fc() -> FPSCounter: return FPSCounter.new()

func test_default_parameters() -> void:
	var fc := _make_fc()
	assert_float(fc.update_interval).is_equal(0.5)
	assert_bool(fc.show_min_max).is_true()
	fc.queue_free()

func test_creates_label() -> void:
	var fc := _make_fc(); add_child(fc)
	assert_object(fc._label).is_not_null()
	assert_str(fc._label.text).is_equal("0 FPS | min:9999 max:0")
	remove_child(fc); fc.queue_free()

func test_process_accumulates_frames() -> void:
	var fc := _make_fc(); add_child(fc)
	fc._process(0.5)  # 0.5s = update_interval
	assert_int(fc._frames).is_equal(0)  # reset após atingir intervalo
	assert_float(fc._fps).is_equal(2.0)  # 1 frame / 0.5s
	remove_child(fc); fc.queue_free()

func test_update_interval_clamped() -> void:
	var fc := _make_fc()
	fc.update_interval = 0.01; assert_float(fc.update_interval).is_equal(0.1)
	fc.update_interval = 10.0; assert_float(fc.update_interval).is_equal(5.0)
	fc.queue_free()

func test_min_max_tracking() -> void:
	var fc := _make_fc(); add_child(fc)
	fc._process(0.5)  # fps = 2, min = 2
	assert_float(fc._min_fps).is_equal(2.0)
	fc._process(0.1)  # acumula frames sem update
	fc._process(0.4)  # total = 1s, frames = 3, fps = 3, min = 2
	assert_float(fc._min_fps).is_equal(2.0)
	remove_child(fc); fc.queue_free()

func test_show_min_max_false() -> void:
	var fc := _make_fc(); fc.show_min_max = false; add_child(fc)
	fc._process(0.5)
	assert_str(fc._label.text).is_equal("2 FPS")
	remove_child(fc); fc.queue_free()
