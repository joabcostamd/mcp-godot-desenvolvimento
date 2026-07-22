## test_stealth.gd — Testes do Stealth | GdUnit4.

extends GdUnitTestSuite

func _make_s() -> Stealth: return Stealth.new()

func test_default_parameters() -> void:
	var s := _make_s()
	assert_float(s.visibility).is_equal(0.5)
	assert_float(s.noise_radius).is_equal(100.0)
	assert_float(s.detection_decay).is_equal(0.5)
	s.queue_free()

func test_add_detection() -> void:
	var s := _make_s()
	s.add_detection(0.6)
	assert_float(s.get_detection_level()).is_equal(0.6)
	s.queue_free()

func test_detection_clamped_to_one() -> void:
	var s := _make_s()
	s.add_detection(2.0)
	assert_float(s.get_detection_level()).is_equal(1.0)
	s.queue_free()

func test_detection_decays() -> void:
	var s := _make_s()
	s.add_detection(0.8)
	s._physics_process(1.0)  # decay = 0.5 * 1.0 = 0.5
	assert_float(s.get_detection_level()).is_equal(0.3)  # 0.8 - 0.5
	s.queue_free()

func test_detection_never_negative() -> void:
	var s := _make_s()
	s._physics_process(1.0)  # sem detecção, decay de 0
	assert_float(s.get_detection_level()).is_equal(0.0)
	s.queue_free()

func test_detected_at_full() -> void:
	var s := _make_s()
	var detected := false
	s.detected.connect(func(): detected = true)
	s.add_detection(1.0)
	assert_bool(detected).is_true()
	assert_bool(s.is_detected()).is_true()
	s.queue_free()

func test_alerted_at_half() -> void:
	var s := _make_s()
	var alerted := false
	s.alerted.connect(func(): alerted = true)
	s.add_detection(0.6)
	assert_bool(alerted).is_true()
	s.queue_free()

func test_hidden_after_decay() -> void:
	var s := _make_s()
	s.add_detection(1.0)  # detected
	assert_bool(s.is_detected()).is_true()
	var hidden := false
	s.hidden.connect(func(): hidden = true)
	# Decai até zero
	for _i in range(20):
		s._physics_process(0.1)
	assert_bool(hidden).is_true()
	assert_bool(s.is_detected()).is_false()
	s.queue_free()

func test_make_noise() -> void:
	var s := _make_s()
	s.visibility = 0.0  # totalmente visível → noise máximo
	s.make_noise()
	assert_float(s.get_detection_level()).is_equal(0.3)  # 0.3 * (1.0 - 0.0)
	s.queue_free()

func test_visibility_reduces_noise() -> void:
	var s := _make_s()
	s.visibility = 1.0  # invisível
	s.make_noise()
	assert_float(s.get_detection_level()).is_equal(0.0)  # 0.3 * (1.0 - 1.0)
	s.queue_free()

func test_visibility_clamped() -> void:
	var s := _make_s()
	s.visibility = -0.5; assert_float(s.visibility).is_equal(0.0)
	s.visibility = 2.0; assert_float(s.visibility).is_equal(1.0)
	s.queue_free()
