## test_player_topdown.gd — Testes do behavior PlayerTopDown | GdUnit4.
##
## Testa movimento top-down: input, aceleração, fricção, normalização diagonal.
## Fonte: Godot 4.7 ClassDB — CharacterBody2D, Input, Vector2.move_toward.

extends GdUnitTestSuite


func _make_pt() -> PlayerTopDown:
	return PlayerTopDown.new()


func _make_body() -> CharacterBody2D:
	var body := CharacterBody2D.new()
	body.set_script(null)  # sem script — o behavior controla a velocidade
	return body


# ── Compilação e defaults ─────────────────────────────────────────────────────

func test_script_compiles() -> void:
	var pt := PlayerTopDown.new()
	assert_object(pt).is_not_null()
	pt.queue_free()


func test_default_parameters() -> void:
	var pt := _make_pt()
	assert_float(pt.speed).is_equal(200.0)
	assert_float(pt.acceleration).is_equal(1000.0)
	assert_float(pt.friction).is_equal(1000.0)
	pt.queue_free()


func test_initial_velocity_zero() -> void:
	var pt := _make_pt()
	assert_that(pt.get_velocity()).is_equal(Vector2.ZERO)
	pt.queue_free()


# ── Input vector ──────────────────────────────────────────────────────────────

func test_input_right() -> void:
	var pt := _make_pt()
	# Simula input: ui_right pressionado, outros não
	Input.action_press("ui_right")
	var v := pt._get_input_vector()
	assert_float(v.x).is_equal(1.0)
	assert_float(v.y).is_equal(0.0)
	Input.action_release("ui_right")
	pt.queue_free()


func test_input_up_left() -> void:
	var pt := _make_pt()
	Input.action_press("ui_up")
	Input.action_press("ui_left")
	var v := pt._get_input_vector()
	assert_float(v.x).is_equal(-1.0)
	assert_float(v.y).is_equal(-1.0)
	Input.action_release("ui_up")
	Input.action_release("ui_left")
	pt.queue_free()


func test_input_diagonal_magnitude() -> void:
	# Diagonal bruta deve ter magnitude > 1 (não normalizada aqui —
	# a normalização é feita no _physics_process)
	var pt := _make_pt()
	Input.action_press("ui_right")
	Input.action_press("ui_down")
	var v := pt._get_input_vector()
	assert_float(v.length()).is_greater(1.0)  # (1,1) → sqrt(2) ≈ 1.41
	Input.action_release("ui_right")
	Input.action_release("ui_down")
	pt.queue_free()


func test_input_none() -> void:
	var pt := _make_pt()
	var v := pt._get_input_vector()
	assert_that(v).is_equal(Vector2.ZERO)
	pt.queue_free()


# ── Physics process: aceleração ───────────────────────────────────────────────

func test_accelerates_toward_speed() -> void:
	var body := _make_body()
	add_child(body)
	var pt := _make_pt()
	body.add_child(pt)

	Input.action_press("ui_right")
	# Um frame de física com delta grande para ver aceleração
	pt._physics_process(0.5)
	Input.action_release("ui_right")

	var vel := pt.get_velocity()
	# Após 0.5s com accel=1000 e speed=200:
	# move_toward(200, 500) = 200 → chega no target em 0.2s
	# Então após 0.5s deve estar no máximo
	assert_float(vel.x).is_equal(200.0)
	assert_float(vel.y).is_equal(0.0)

	remove_child(body)
	body.queue_free()
	pt.queue_free()


func test_accelerates_gradually() -> void:
	var body := _make_body()
	add_child(body)
	var pt := _make_pt()
	body.add_child(pt)

	Input.action_press("ui_right")
	pt._physics_process(0.05)  # 50ms — 50 px/s ganho
	Input.action_release("ui_right")

	var vel := pt.get_velocity()
	# move_toward: step = 1000 * 0.05 = 50
	assert_float(vel.x).is_equal(50.0)

	remove_child(body)
	body.queue_free()
	pt.queue_free()


# ── Physics process: fricção ──────────────────────────────────────────────────

func test_decelerates_when_no_input() -> void:
	var body := _make_body()
	add_child(body)
	var pt := _make_pt()
	body.add_child(pt)

	# Primeiro acelera
	Input.action_press("ui_right")
	pt._physics_process(0.5)  # atinge speed=200
	Input.action_release("ui_right")
	assert_float(pt.get_velocity().x).is_equal(200.0)

	# Depois desacelera
	pt._physics_process(0.05)  # step = 1000 * 0.05 = 50 → vx = 150
	assert_float(pt.get_velocity().x).is_equal(150.0)

	remove_child(body)
	body.queue_free()
	pt.queue_free()


func test_stops_completely() -> void:
	var body := _make_body()
	add_child(body)
	var pt := _make_pt()
	body.add_child(pt)

	Input.action_press("ui_right")
	pt._physics_process(0.5)
	Input.action_release("ui_right")

	# Vários frames sem input → deve parar
	for _i in range(10):
		pt._physics_process(0.05)

	assert_that(pt.get_velocity()).is_equal(Vector2.ZERO)

	remove_child(body)
	body.queue_free()
	pt.queue_free()


# ── Normalização diagonal ─────────────────────────────────────────────────────

func test_diagonal_not_faster() -> void:
	var body := _make_body()
	add_child(body)
	var pt := _make_pt()
	body.add_child(pt)

	Input.action_press("ui_right")
	Input.action_press("ui_down")
	pt._physics_process(0.5)  # tempo suficiente para atingir max
	Input.action_release("ui_right")
	Input.action_release("ui_down")

	var vel := pt.get_velocity()
	# Normalizado → magnitude deve ser speed, não speed * sqrt(2)
	assert_float(vel.length()).is_equal(200.0)

	remove_child(body)
	body.queue_free()
	pt.queue_free()


# ── Velocidade máxima ─────────────────────────────────────────────────────────

func test_does_not_exceed_speed() -> void:
	var body := _make_body()
	add_child(body)
	var pt := _make_pt()
	pt.speed = 100.0  # Reduz velocidade
	body.add_child(pt)

	Input.action_press("ui_right")
	pt._physics_process(0.5)
	Input.action_release("ui_right")

	var vel := pt.get_velocity()
	assert_float(vel.length()).is_less_equal(100.0)

	remove_child(body)
	body.queue_free()
	pt.queue_free()


# ── Reset ─────────────────────────────────────────────────────────────────────

func test_reset_zeroes_velocity() -> void:
	var body := _make_body()
	add_child(body)
	var pt := _make_pt()
	body.add_child(pt)

	Input.action_press("ui_right")
	pt._physics_process(0.5)
	Input.action_release("ui_right")
	assert_float(pt.get_velocity().x).is_greater(0.0)

	pt.reset()
	assert_that(pt.get_velocity()).is_equal(Vector2.ZERO)
	assert_that(body.velocity).is_equal(Vector2.ZERO)

	remove_child(body)
	body.queue_free()
	pt.queue_free()


# ── set_velocity ───────────────────────────────────────────────────────────────

func test_set_velocity_instant() -> void:
	var body := _make_body()
	add_child(body)
	var pt := _make_pt()
	body.add_child(pt)

	pt.set_velocity(Vector2(150, 0))
	assert_float(pt.get_velocity().x).is_equal(150.0)
	assert_float(body.velocity.x).is_equal(150.0)

	remove_child(body)
	body.queue_free()
	pt.queue_free()


func test_set_velocity_respects_speed_limit() -> void:
	var body := _make_body()
	add_child(body)
	var pt := _make_pt()
	pt.speed = 100.0
	body.add_child(pt)

	pt.set_velocity(Vector2(500, 0))
	assert_float(pt.get_velocity().length()).is_equal(100.0)

	remove_child(body)
	body.queue_free()
	pt.queue_free()


# ── Signal ────────────────────────────────────────────────────────────────────

func test_emits_velocity_changed() -> void:
	var body := _make_body()
	add_child(body)
	var pt := _make_pt()
	body.add_child(pt)

	var emitted := false
	var last_vel := Vector2.ZERO
	pt.velocity_changed.connect(func(v): emitted = true; last_vel = v)

	Input.action_press("ui_right")
	pt._physics_process(0.5)
	Input.action_release("ui_right")

	assert_bool(emitted).is_true()
	assert_float(last_vel.x).is_greater(0.0)

	remove_child(body)
	body.queue_free()
	pt.queue_free()


# ── Sem parent CharacterBody2D ────────────────────────────────────────────────

func test_no_parent_does_not_crash() -> void:
	var pt := _make_pt()
	# Sem add_child — sem parent
	Input.action_press("ui_right")
	pt._physics_process(0.5)
	Input.action_release("ui_right")
	# Não deve crashar
	assert_that(pt.get_velocity()).is_equal(Vector2.ZERO)
	pt.queue_free()


# ── Disabled ──────────────────────────────────────────────────────────────────

func test_disabled_does_not_move() -> void:
	var body := _make_body()
	add_child(body)
	var pt := _make_pt()
	body.add_child(pt)

	# Desabilita
	pt.enabled = false  # Node.enabled (herdado)

	Input.action_press("ui_right")
	pt._physics_process(0.5)
	Input.action_release("ui_right")

	assert_that(pt.get_velocity()).is_equal(Vector2.ZERO)

	remove_child(body)
	body.queue_free()
	pt.queue_free()
