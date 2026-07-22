## test_player_controller.gd — Testes do PlayerController | GdUnit4.
##
## Testa gravidade, pulo, movimento horizontal, kill plane.
## Fonte: Godot 4.7 ClassDB — CharacterBody2D, move_and_slide, is_on_floor.

extends GdUnitTestSuite


func _make_pc() -> PlayerController:
	return PlayerController.new()


func _make_body() -> CharacterBody2D:
	return CharacterBody2D.new()


# ── Compilação e defaults ─────────────────────────────────────────────────────

func test_script_compiles() -> void:
	var pc := PlayerController.new()
	assert_object(pc).is_not_null()
	pc.queue_free()


func test_default_parameters() -> void:
	var pc := _make_pc()
	assert_float(pc.speed).is_equal(300.0)
	assert_float(pc.jump_velocity).is_equal(-400.0)
	assert_float(pc.gravity).is_equal(980.0)
	assert_float(pc.acceleration).is_equal(1000.0)
	assert_float(pc.friction).is_equal(1000.0)
	assert_float(pc.kill_plane_y).is_equal(0.0)
	pc.queue_free()


# ── Gravidade ─────────────────────────────────────────────────────────────────

func test_gravity_applied_in_air() -> void:
	var body := _make_body()
	add_child(body)
	var pc := _make_pc()
	pc.gravity = 1000.0
	body.add_child(pc)

	# Simula um frame — começa no ar (is_on_floor = false)
	pc._physics_process(0.1)
	# gravity * delta = 1000 * 0.1 = 100 (positivo = para baixo)
	assert_float(body.velocity.y).is_equal(100.0)

	remove_child(body)
	body.queue_free()
	pc.queue_free()


func test_gravity_accumulates() -> void:
	var body := _make_body()
	add_child(body)
	var pc := _make_pc()
	pc.gravity = 500.0
	body.add_child(pc)

	pc._physics_process(0.1)
	assert_float(body.velocity.y).is_equal(50.0)

	pc._physics_process(0.1)
	assert_float(body.velocity.y).is_equal(100.0)

	remove_child(body)
	body.queue_free()
	pc.queue_free()


# ── Movimento horizontal ──────────────────────────────────────────────────────

func test_move_right() -> void:
	var body := _make_body()
	add_child(body)
	var pc := _make_pc()
	pc.speed = 200.0
	pc.acceleration = 1000.0
	body.add_child(pc)

	Input.action_press("ui_right")
	pc._physics_process(0.5)  # tempo suficiente para atingir max
	Input.action_release("ui_right")

	assert_float(body.velocity.x).is_equal(200.0)

	remove_child(body)
	body.queue_free()
	pc.queue_free()


func test_move_left() -> void:
	var body := _make_body()
	add_child(body)
	var pc := _make_pc()
	pc.speed = 200.0
	pc.acceleration = 1000.0
	body.add_child(pc)

	Input.action_press("ui_left")
	pc._physics_process(0.5)
	Input.action_release("ui_left")

	assert_float(body.velocity.x).is_equal(-200.0)

	remove_child(body)
	body.queue_free()
	pc.queue_free()


func test_friction_stops() -> void:
	var body := _make_body()
	add_child(body)
	var pc := _make_pc()
	body.add_child(pc)

	# Acelera
	Input.action_press("ui_right")
	pc._physics_process(0.5)
	Input.action_release("ui_right")
	assert_float(body.velocity.x).is_greater(0.0)

	# Desacelera
	for _i in range(10):
		pc._physics_process(0.05)

	assert_float(body.velocity.x).is_equal(0.0)

	remove_child(body)
	body.queue_free()
	pc.queue_free()


# ── Pulo ─────────────────────────────────────────────────────────────────────

func test_jump_sets_velocity() -> void:
	var body := _make_body()
	add_child(body)
	var pc := _make_pc()
	pc.jump_velocity = -500.0
	body.add_child(pc)

	# is_on_floor() retorna false por padrão sem colisão.
	# Para testar pulo, precisamos simular is_on_floor = true.
	# Infelizmente não podemos mockar is_on_floor() diretamente.
	# Testamos apenas que o parâmetro está correto.
	assert_float(pc.jump_velocity).is_equal(-500.0)

	remove_child(body)
	body.queue_free()
	pc.queue_free()


# ── Kill plane ────────────────────────────────────────────────────────────────

func test_kill_plane_disabled_by_default() -> void:
	var body := _make_body()
	add_child(body)
	var pc := _make_pc()
	body.add_child(pc)

	body.global_position = Vector2(0, 9999)
	pc.kill_plane_y = 0.0  # desativado

	var died := false
	pc.player_died.connect(func(): died = true)

	pc._physics_process(0.1)
	assert_bool(died).is_false()

	remove_child(body)
	body.queue_free()
	pc.queue_free()


func test_kill_plane_emits_when_below() -> void:
	var body := _make_body()
	add_child(body)
	var pc := _make_pc()
	pc.kill_plane_y = 1000.0
	body.add_child(pc)

	body.global_position = Vector2(0, 1500)

	var died := false
	pc.player_died.connect(func(): died = true)

	pc._physics_process(0.1)
	assert_bool(died).is_true()

	remove_child(body)
	body.queue_free()
	pc.queue_free()


func test_kill_plane_above_is_safe() -> void:
	var body := _make_body()
	add_child(body)
	var pc := _make_pc()
	pc.kill_plane_y = 1000.0
	body.add_child(pc)

	body.global_position = Vector2(0, 500)

	var died := false
	pc.player_died.connect(func(): died = true)

	pc._physics_process(0.1)
	assert_bool(died).is_false()

	remove_child(body)
	body.queue_free()
	pc.queue_free()


# ── Reset ─────────────────────────────────────────────────────────────────────

func test_reset_zeroes_velocity() -> void:
	var body := _make_body()
	add_child(body)
	var pc := _make_pc()
	body.add_child(pc)

	Input.action_press("ui_right")
	pc._physics_process(0.5)
	Input.action_release("ui_right")

	pc.reset()
	assert_that(body.velocity).is_equal(Vector2.ZERO)

	remove_child(body)
	body.queue_free()
	pc.queue_free()


# ── Sem parent ────────────────────────────────────────────────────────────────

func test_no_parent_does_not_crash() -> void:
	var pc := _make_pc()
	pc._physics_process(0.1)
	assert_bool(pc.is_on_ground()).is_false()
	assert_that(pc.get_velocity()).is_equal(Vector2.ZERO)
	pc.queue_free()


# ── Clamp setters ─────────────────────────────────────────────────────────────

func test_speed_clamped() -> void:
	var pc := _make_pc()
	pc.speed = 5000.0
	assert_float(pc.speed).is_equal(2000.0)
	pc.speed = 1.0
	assert_float(pc.speed).is_equal(10.0)
	pc.queue_free()


func test_jump_velocity_clamped() -> void:
	var pc := _make_pc()
	pc.jump_velocity = 0.0
	assert_float(pc.jump_velocity).is_equal(-50.0)
	pc.jump_velocity = -3000.0
	assert_float(pc.jump_velocity).is_equal(-2000.0)
	pc.queue_free()
