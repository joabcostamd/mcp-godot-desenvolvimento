## test_dash.gd — Testes do behavior Dash | GdUnit4.
##
## Testa início/fim, cooldown, direção, cancelamento.
## Fonte: Godot 4.7 ClassDB — Timer, Input.get_vector.

extends GdUnitTestSuite


func _make_dash() -> Dash:
	return Dash.new()


func _make_body() -> CharacterBody2D:
	return CharacterBody2D.new()


# ── Compilação e defaults ─────────────────────────────────────────────────────

func test_script_compiles() -> void:
	var d := Dash.new()
	assert_object(d).is_not_null()
	d.queue_free()


func test_default_parameters() -> void:
	var d := _make_dash()
	assert_float(d.dash_speed).is_equal(800.0)
	assert_float(d.dash_duration).is_equal(0.15)
	assert_float(d.cooldown).is_equal(0.5)
	d.queue_free()


func test_can_dash_initially() -> void:
	var d := _make_dash()
	assert_bool(d.can_dash()).is_true()
	assert_bool(d.is_dashing()).is_false()
	d.queue_free()


# ── Direção ───────────────────────────────────────────────────────────────────

func test_direction_from_input() -> void:
	var d := _make_dash()
	Input.action_press("ui_right")
	var dir := d._get_dash_direction()
	assert_float(dir.x).is_equal(1.0)
	assert_float(dir.y).is_equal(0.0)
	Input.action_release("ui_right")
	d.queue_free()


func test_direction_fallback_right() -> void:
	var d := _make_dash()
	d._dash_direction = Vector2.ZERO
	var dir := d._get_dash_direction()
	assert_float(dir.x).is_equal(1.0)
	assert_float(dir.y).is_equal(0.0)
	d.queue_free()


func test_direction_remembers_last() -> void:
	var d := _make_dash()
	Input.action_press("ui_up")
	d._get_dash_direction()
	Input.action_release("ui_up")

	# Sem input, deve lembrar última direção
	var dir := d._get_dash_direction()
	assert_float(dir.y).is_equal(-1.0)
	d.queue_free()


# ── Início e fim do dash ─────────────────────────────────────────────────────

func test_start_dash_sets_state() -> void:
	var body := _make_body()
	add_child(body)
	var d := _make_dash()
	body.add_child(d)

	d._start_dash(Vector2.RIGHT)
	assert_bool(d.is_dashing()).is_true()
	assert_bool(d.can_dash()).is_false()

	remove_child(body)
	body.queue_free()
	d.queue_free()


func test_dash_applies_velocity() -> void:
	var body := _make_body()
	add_child(body)
	var d := _make_dash()
	d.dash_speed = 500.0
	body.add_child(d)

	d._start_dash(Vector2.RIGHT)
	d._physics_process(0.0)

	assert_float(body.velocity.x).is_equal(500.0)
	assert_float(body.velocity.y).is_equal(0.0)

	remove_child(body)
	body.queue_free()
	d.queue_free()


func test_end_dash_stops_dashing() -> void:
	var body := _make_body()
	add_child(body)
	var d := _make_dash()
	body.add_child(d)

	d._start_dash(Vector2.RIGHT)
	assert_bool(d.is_dashing()).is_true()

	d._end_dash()
	assert_bool(d.is_dashing()).is_false()

	remove_child(body)
	body.queue_free()
	d.queue_free()


# ── Sinais ────────────────────────────────────────────────────────────────────

func test_emits_dashed_signal() -> void:
	var body := _make_body()
	add_child(body)
	var d := _make_dash()
	body.add_child(d)

	var emitted := false
	d.dashed.connect(func(): emitted = true)

	d._start_dash(Vector2.LEFT)
	assert_bool(emitted).is_true()

	remove_child(body)
	body.queue_free()
	d.queue_free()


func test_emits_dash_ready_after_cooldown() -> void:
	var body := _make_body()
	add_child(body)
	var d := _make_dash()
	d.cooldown = 0.01
	body.add_child(d)

	var ready := false
	d.dash_ready.connect(func(): ready = true)

	d._start_dash(Vector2.RIGHT)
	# Cooldown timer vai disparar
	d._on_cooldown_ready()
	assert_bool(ready).is_true()
	assert_bool(d.can_dash()).is_true()

	remove_child(body)
	body.queue_free()
	d.queue_free()


# ── Cancelamento ──────────────────────────────────────────────────────────────

func test_cancel_dash() -> void:
	var body := _make_body()
	add_child(body)
	var d := _make_dash()
	body.add_child(d)

	d._start_dash(Vector2.RIGHT)
	assert_bool(d.is_dashing()).is_true()

	d.cancel_dash()
	assert_bool(d.is_dashing()).is_false()

	remove_child(body)
	body.queue_free()
	d.queue_free()


# ── Sem parent ────────────────────────────────────────────────────────────────

func test_no_parent_does_not_crash() -> void:
	var d := _make_dash()
	d._start_dash(Vector2.RIGHT)
	d._physics_process(0.0)  # sem parent — não crasha
	assert_bool(d.is_dashing()).is_true()
	d.queue_free()


# ── Clamp setters ─────────────────────────────────────────────────────────────

func test_dash_speed_clamped() -> void:
	var d := _make_dash()
	d.dash_speed = 50.0
	assert_float(d.dash_speed).is_equal(100.0)
	d.dash_speed = 9999.0
	assert_float(d.dash_speed).is_equal(5000.0)
	d.queue_free()


func test_dash_duration_clamped() -> void:
	var d := _make_dash()
	d.dash_duration = 0.01
	assert_float(d.dash_duration).is_equal(0.05)
	d.dash_duration = 5.0
	assert_float(d.dash_duration).is_equal(1.0)
	d.queue_free()
