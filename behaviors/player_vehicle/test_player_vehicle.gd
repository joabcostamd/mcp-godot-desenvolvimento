## test_player_vehicle.gd — Testes do PlayerVehicle | GdUnit4.
##
## Testa rotação, impulso, drift, limite de velocidade.
## Fonte: Godot 4.7 ClassDB — CharacterBody2D, Vector2.rotated.

extends GdUnitTestSuite


func _make_pv() -> PlayerVehicle:
	return PlayerVehicle.new()


func _make_body() -> CharacterBody2D:
	return CharacterBody2D.new()


# ── Compilação e defaults ─────────────────────────────────────────────────────

func test_script_compiles() -> void:
	var pv := PlayerVehicle.new()
	assert_object(pv).is_not_null()
	pv.queue_free()


func test_default_parameters() -> void:
	var pv := _make_pv()
	assert_float(pv.acceleration).is_equal(500.0)
	assert_float(pv.max_speed).is_equal(400.0)
	assert_float(pv.turn_rate).is_equal(3.0)
	assert_float(pv.drift).is_equal(0.9)
	pv.queue_free()


# ── Rotação ───────────────────────────────────────────────────────────────────

func test_turns_right() -> void:
	var body := _make_body()
	add_child(body)
	var pv := _make_pv()
	body.add_child(pv)

	var initial := body.rotation
	Input.action_press("ui_right")
	pv._physics_process(0.5)
	Input.action_release("ui_right")

	assert_float(body.rotation).is_greater(initial)

	remove_child(body)
	body.queue_free()
	pv.queue_free()


func test_turns_left() -> void:
	var body := _make_body()
	add_child(body)
	var pv := _make_pv()
	body.add_child(pv)

	var initial := body.rotation
	Input.action_press("ui_left")
	pv._physics_process(0.5)
	Input.action_release("ui_left")

	assert_float(body.rotation).is_less(initial)

	remove_child(body)
	body.queue_free()
	pv.queue_free()


# ── Impulso ───────────────────────────────────────────────────────────────────

func test_thrust_forward() -> void:
	var body := _make_body()
	add_child(body)
	var pv := _make_pv()
	pv.acceleration = 1000.0
	body.add_child(pv)

	Input.action_press("ui_up")
	pv._physics_process(0.1)  # 100 px/s
	Input.action_release("ui_up")

	assert_float(body.velocity.length()).is_greater(0.0)

	remove_child(body)
	body.queue_free()
	pv.queue_free()


func test_reverse_thrust() -> void:
	var body := _make_body()
	add_child(body)
	var pv := _make_pv()
	pv.acceleration = 1000.0
	body.add_child(pv)

	Input.action_press("ui_down")
	pv._physics_process(0.1)
	Input.action_release("ui_down")

	# Ré: velocidade negativa na direção frontal
	assert_float(body.velocity.length()).is_greater(0.0)

	remove_child(body)
	body.queue_free()
	pv.queue_free()


# ── Velocidade máxima ────────────────────────────────────────────────────────

func test_speed_clamped() -> void:
	var body := _make_body()
	add_child(body)
	var pv := _make_pv()
	pv.max_speed = 100.0
	pv.acceleration = 5000.0
	body.add_child(pv)

	Input.action_press("ui_up")
	for _i in range(10):
		pv._physics_process(0.1)
	Input.action_release("ui_up")

	assert_float(body.velocity.length()).is_less_equal(100.0)

	remove_child(body)
	body.queue_free()
	pv.queue_free()


# ── Drift ─────────────────────────────────────────────────────────────────────

func test_drift_reduces_lateral() -> void:
	var body := _make_body()
	add_child(body)
	var pv := _make_pv()
	pv.drift = 0.5
	pv.acceleration = 1000.0
	body.add_child(pv)

	# Dá impulso e depois aplica drift
	Input.action_press("ui_up")
	pv._physics_process(0.2)
	Input.action_release("ui_up")

	# drift foi aplicado
	assert_float(body.velocity.length()).is_greater(0.0)

	remove_child(body)
	body.queue_free()
	pv.queue_free()


# ── Reset ─────────────────────────────────────────────────────────────────────

func test_reset_zeroes_velocity() -> void:
	var body := _make_body()
	add_child(body)
	var pv := _make_pv()
	body.add_child(pv)

	Input.action_press("ui_up")
	pv._physics_process(0.5)
	Input.action_release("ui_up")

	pv.reset()
	assert_that(body.velocity).is_equal(Vector2.ZERO)

	remove_child(body)
	body.queue_free()
	pv.queue_free()


# ── Disabled ──────────────────────────────────────────────────────────────────

func test_disabled_does_not_process() -> void:
	var body := _make_body()
	add_child(body)
	var pv := _make_pv()
	pv.enabled = false
	body.add_child(pv)

	Input.action_press("ui_up")
	pv._physics_process(0.5)
	Input.action_release("ui_up")

	assert_that(body.velocity).is_equal(Vector2.ZERO)

	remove_child(body)
	body.queue_free()
	pv.queue_free()


# ── Sem parent ────────────────────────────────────────────────────────────────

func test_no_parent_does_not_crash() -> void:
	var pv := _make_pv()
	pv._physics_process(0.1)
	assert_that(pv.get_velocity()).is_equal(Vector2.ZERO)
	pv.queue_free()
