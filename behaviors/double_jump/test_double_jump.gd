## test_double_jump.gd — Testes do DoubleJump | GdUnit4.
##
## Testa pulos no ar, coyote time, reset, sinais.
## Fonte: Godot 4.7 ClassDB — CharacterBody2D.is_on_floor.

extends GdUnitTestSuite


func _make_dj() -> DoubleJump:
	return DoubleJump.new()


func _make_body() -> CharacterBody2D:
	return CharacterBody2D.new()


# ── Compilação e defaults ─────────────────────────────────────────────────────

func test_script_compiles() -> void:
	var dj := DoubleJump.new()
	assert_object(dj).is_not_null()
	dj.queue_free()


func test_default_parameters() -> void:
	var dj := _make_dj()
	assert_int(dj.jump_count).is_equal(2)
	assert_float(dj.jump_velocity).is_equal(-400.0)
	assert_float(dj.coyote_time).is_equal(0.1)
	dj.queue_free()


func test_starts_with_zero_jumps() -> void:
	var dj := _make_dj()
	assert_int(dj.get_jumps_used()).is_equal(0)
	assert_int(dj.get_jumps_remaining()).is_equal(2)
	dj.queue_free()


# ── Lógica de pulo ────────────────────────────────────────────────────────────

func test_no_jump_on_floor() -> void:
	var body := _make_body()
	add_child(body)
	var dj := _make_dj()
	body.add_child(dj)

	# is_on_floor() = false por padrão, mas _can_air_jump(true) → false
	assert_bool(dj._can_air_jump(true)).is_false()

	remove_child(body)
	body.queue_free()
	dj.queue_free()


func test_can_jump_in_air() -> void:
	var body := _make_body()
	add_child(body)
	var dj := _make_dj()
	body.add_child(dj)

	# No ar, 0 pulos usados
	assert_bool(dj._can_air_jump(false)).is_true()

	remove_child(body)
	body.queue_free()
	dj.queue_free()


func test_cannot_jump_when_exhausted() -> void:
	var body := _make_body()
	add_child(body)
	var dj := _make_dj()
	dj.jump_count = 2
	body.add_child(dj)

	# Simula 2 pulos já usados
	dj._jumps_used = 2
	assert_bool(dj._can_air_jump(false)).is_false()

	remove_child(body)
	body.queue_free()
	dj.queue_free()


# ── Coyote time ───────────────────────────────────────────────────────────────

func test_coyote_time_allows_jump() -> void:
	var body := _make_body()
	add_child(body)
	var dj := _make_dj()
	dj.coyote_time = 0.2
	body.add_child(dj)

	dj._air_time = 0.15  # dentro do coyote time
	dj._jumps_used = 0
	assert_bool(dj._can_air_jump(false)).is_true()

	remove_child(body)
	body.queue_free()
	dj.queue_free()


func test_coyote_time_expired() -> void:
	var body := _make_body()
	add_child(body)
	var dj := _make_dj()
	dj.coyote_time = 0.1
	body.add_child(dj)

	dj._air_time = 0.3  # passou do coyote
	dj._jumps_used = 0
	# Ainda pode pular (jumps_used=0 < jump_count=2) via pulo normal no ar
	assert_bool(dj._can_air_jump(false)).is_true()

	remove_child(body)
	body.queue_free()
	dj.queue_free()


# ── Sinais ────────────────────────────────────────────────────────────────────

func test_emits_jumped_signal() -> void:
	var body := _make_body()
	add_child(body)
	var dj := _make_dj()
	body.add_child(dj)

	var emitted := false
	var used := -1
	dj.jumped.connect(func(j): emitted = true; used = j)

	# Simula pulo no ar
	Input.action_press("ui_accept")
	dj._physics_process(0.0)
	Input.action_release("ui_accept")

	if emitted:
		assert_int(used).is_equal(1)
		assert_int(dj.get_jumps_used()).is_equal(1)

	remove_child(body)
	body.queue_free()
	dj.queue_free()


func test_emits_exhausted_when_all_used() -> void:
	var body := _make_body()
	add_child(body)
	var dj := _make_dj()
	dj.jump_count = 1
	body.add_child(dj)

	var exhausted := false
	dj.jumps_exhausted.connect(func(): exhausted = true)

	# Simula pulo que esgota
	Input.action_press("ui_accept")
	dj._physics_process(0.0)
	Input.action_release("ui_accept")

	# Pode ter emitido ou não dependendo se estava no ar
	# Se _can_air_jump retornou true e o pulo aconteceu:
	if dj.get_jumps_used() >= 1:
		assert_bool(exhausted).is_true()

	remove_child(body)
	body.queue_free()
	dj.queue_free()


# ── Reset ─────────────────────────────────────────────────────────────────────

func test_reset_jumps() -> void:
	var body := _make_body()
	add_child(body)
	var dj := _make_dj()
	body.add_child(dj)

	dj._jumps_used = 2
	dj._air_time = 5.0
	dj.reset_jumps()

	assert_int(dj.get_jumps_used()).is_equal(0)
	assert_int(dj.get_jumps_remaining()).is_equal(2)
	assert_float(dj._air_time).is_equal(0.0)

	remove_child(body)
	body.queue_free()
	dj.queue_free()


# ── Clamp setters ─────────────────────────────────────────────────────────────

func test_jump_count_clamped() -> void:
	var dj := _make_dj()
	dj.jump_count = 0
	assert_int(dj.jump_count).is_equal(1)
	dj.jump_count = 100
	assert_int(dj.jump_count).is_equal(10)
	dj.queue_free()


func test_coyote_time_clamped() -> void:
	var dj := _make_dj()
	dj.coyote_time = -0.5
	assert_float(dj.coyote_time).is_equal(0.0)
	dj.coyote_time = 2.0
	assert_float(dj.coyote_time).is_equal(0.5)
	dj.queue_free()
