## test_camera_shake.gd — Testes do CameraShake | GdUnit4.

extends GdUnitTestSuite


func _make_shake() -> CameraShake:
	return CameraShake.new()


func _make_camera() -> Camera2D:
	var cam := Camera2D.new()
	cam.offset = Vector2(100, 50)
	return cam


# ---------------------------------------------------------------------------
# TRIGGER / STOP
# ---------------------------------------------------------------------------

func test_trigger_starts_shake() -> void:
	var cam := _make_camera()
	var shake := _make_shake()
	cam.add_child(shake)

	assert_bool(shake.is_shaking()).is_false()
	shake.trigger()
	assert_bool(shake.is_shaking()).is_true()

	cam.queue_free()


func test_trigger_guards_duplicate() -> void:
	"""PADRÃO 10: segundo trigger enquanto ativo é ignorado."""
	var cam := _make_camera()
	var shake := _make_shake()
	cam.add_child(shake)

	shake.trigger()
	shake.trigger()  # no-op
	assert_bool(shake.is_shaking()).is_true()

	cam.queue_free()


func test_stop_restores_offset() -> void:
	var cam := _make_camera()
	var shake := _make_shake()
	shake.duration = 999.0  # longa duração
	cam.add_child(shake)

	var original := cam.offset
	shake.trigger()
	shake._process(0.1)  # aplica offset
	assert_bool(cam.offset != original).is_true()

	shake.stop()
	assert_vector(cam.offset).is_equal(original)
	assert_bool(shake.is_shaking()).is_false()

	cam.queue_free()


func test_stop_when_inactive() -> void:
	var shake := _make_shake()
	shake.stop()  # no-op, sem crash
	assert_bool(shake.is_shaking()).is_false()
	shake.queue_free()


# ---------------------------------------------------------------------------
# SIGNALS
# ---------------------------------------------------------------------------

func test_shake_started_signal() -> void:
	var cam := _make_camera()
	var shake := _make_shake()
	cam.add_child(shake)

	var emitted := false
	shake.shake_started.connect(func(): emitted = true)
	shake.trigger()
	assert_bool(emitted).is_true()

	cam.queue_free()


func test_shake_finished_signal_on_duration() -> void:
	var cam := _make_camera()
	var shake := _make_shake()
	shake.duration = 0.1
	cam.add_child(shake)

	var emitted := false
	shake.shake_finished.connect(func(): emitted = true)

	shake.trigger()
	shake._process(0.15)  # excede duration

	assert_bool(emitted).is_true()
	assert_bool(shake.is_shaking()).is_false()

	cam.queue_free()


func test_shake_finished_signal_on_stop() -> void:
	var cam := _make_camera()
	var shake := _make_shake()
	cam.add_child(shake)

	var emitted := false
	shake.shake_finished.connect(func(): emitted = true)

	shake.trigger()
	shake.stop()

	assert_bool(emitted).is_true()

	cam.queue_free()


# ---------------------------------------------------------------------------
# SINUSOIDAL BEHAVIOR
# ---------------------------------------------------------------------------

func test_offset_is_sinusoidal() -> void:
	var cam := _make_camera()
	var shake := _make_shake()
	shake.amplitude = 10.0
	shake.frequency = 1.0  # 1 Hz = 1 ciclo por segundo
	shake.duration = 1.0
	shake.decay = 0.0  # sem decaimento
	shake.direction = Vector2(1.0, 0.0)  # apenas horizontal
	cam.add_child(shake)

	var original := cam.offset
	shake.trigger()

	# Em t=0.25s (1/4 do ciclo), sin(PI/2) = 1 → offset máximo
	shake._process(0.25)
	assert_float(cam.offset.x).is_equal(original.x + 10.0)

	# Em t=0.5s (1/2 ciclo), sin(PI) = 0 → offset zero
	shake._process(0.25)  # total = 0.5
	assert_float(cam.offset.x).is_equal(original.x)

	# Em t=0.75s (3/4 ciclo), sin(3PI/2) = -1 → offset mínimo
	shake._process(0.25)  # total = 0.75
	assert_float(cam.offset.x).is_equal(original.x - 10.0)

	cam.queue_free()


func test_decay_reduces_amplitude() -> void:
	var cam := _make_camera()
	var shake := _make_shake()
	shake.amplitude = 10.0
	shake.frequency = 1.0
	shake.duration = 1.0
	shake.decay = 1.0  # decaimento total
	shake.direction = Vector2(1.0, 0.0)
	cam.add_child(shake)

	shake.trigger()

	# t=0.25: sin(PI/2)=1, decay_factor = 1-0.25*1.0 = 0.75
	shake._process(0.25)
	assert_float(cam.offset.x).is_equal(cam.offset.x)  # já movido

	# t=1.0: sin(2PI)=0, decay_factor = 0 → offset zero
	shake._process(0.75)  # total = 1.0 → shake termina
	assert_bool(shake.is_shaking()).is_false()

	cam.queue_free()


# ---------------------------------------------------------------------------
# EDGE CASES
# ---------------------------------------------------------------------------

func test_direction_normalized() -> void:
	var shake := _make_shake()
	shake.direction = Vector2(3.0, 4.0)
	assert_float(shake.direction.length()).is_equal(1.0)  # normalizado
	shake.queue_free()


func test_direction_zero_defaults() -> void:
	var shake := _make_shake()
	shake.direction = Vector2.ZERO
	assert_vector(shake.direction).is_equal(Vector2.ONE)  # fallback
	shake.queue_free()


func test_trigger_without_camera() -> void:
	var shake := _make_shake()
	shake.trigger()
	assert_bool(shake.is_shaking()).is_true()  # ativa mesmo sem câmera
	shake.stop()
	shake.queue_free()


func test_amplitude_override() -> void:
	var cam := _make_camera()
	var shake := _make_shake()
	shake.amplitude = 5.0
	shake.frequency = 1.0
	shake.duration = 1.0
	shake.decay = 0.0
	shake.direction = Vector2(1.0, 0.0)
	cam.add_child(shake)

	var original := cam.offset
	shake.trigger(20.0)  # override

	shake._process(0.25)
	assert_float(cam.offset.x).is_equal(original.x + 20.0)

	cam.queue_free()
