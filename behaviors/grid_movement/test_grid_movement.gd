## test_grid_movement.gd — Testes do GridMovement | GdUnit4.
##
## Testa snap, movimento, bloqueio durante animação, sinais.
## Fonte: Godot 4.7 ClassDB — Tween.tween_property, Input.

extends GdUnitTestSuite


func _make_gm() -> GridMovement:
	return GridMovement.new()


func _make_parent() -> Node2D:
	var n := Node2D.new()
	n.position = Vector2(100, 200)
	return n


# ── Compilação e defaults ─────────────────────────────────────────────────────

func test_script_compiles() -> void:
	var gm := GridMovement.new()
	assert_object(gm).is_not_null()
	gm.queue_free()


func test_default_parameters() -> void:
	var gm := _make_gm()
	assert_that(gm.grid_size).is_equal(Vector2(32, 32))
	assert_float(gm.move_duration).is_equal(0.15)
	assert_bool(gm.snap_on_start).is_true()
	gm.queue_free()


func test_starts_not_moving() -> void:
	var gm := _make_gm()
	assert_bool(gm.is_moving()).is_false()
	gm.queue_free()


# ── Snap ──────────────────────────────────────────────────────────────────────

func test_snap_to_grid() -> void:
	var parent := _make_parent()
	parent.position = Vector2(50, 70)  # 50/32=1.56→2*32=64, 70/32=2.18→2*32=64
	add_child(parent)
	var gm := _make_gm()
	gm.snap_on_start = true
	parent.add_child(gm)

	# _ready já chamou _snap_to_grid
	assert_that(parent.position).is_equal(Vector2(64, 64))

	remove_child(parent)
	parent.queue_free()
	gm.queue_free()


func test_snap_off() -> void:
	var parent := _make_parent()
	parent.position = Vector2(50, 70)
	add_child(parent)
	var gm := _make_gm()
	gm.snap_on_start = false
	parent.add_child(gm)

	# Posição não alterada
	assert_that(parent.position).is_equal(Vector2(50, 70))

	remove_child(parent)
	parent.queue_free()
	gm.queue_free()


# ── Grid position ─────────────────────────────────────────────────────────────

func test_get_grid_position() -> void:
	var parent := _make_parent()
	parent.position = Vector2(64, 64)
	add_child(parent)
	var gm := _make_gm()
	gm.snap_on_start = false
	parent.add_child(gm)

	var gp := gm.get_grid_position()
	assert_float(gp.x).is_equal(2.0)  # 64/32
	assert_float(gp.y).is_equal(2.0)

	remove_child(parent)
	parent.queue_free()
	gm.queue_free()


# ── Movimento bloqueado durante animação ─────────────────────────────────────

func test_is_moving_during_tween() -> void:
	var parent := _make_parent()
	add_child(parent)
	var gm := _make_gm()
	gm.snap_on_start = false
	parent.add_child(gm)

	gm.move_to_grid(5, 5)
	assert_bool(gm.is_moving()).is_true()

	remove_child(parent)
	parent.queue_free()
	gm.queue_free()


func test_move_to_grid_ignored_while_moving() -> void:
	var parent := _make_parent()
	add_child(parent)
	var gm := _make_gm()
	gm.snap_on_start = false
	parent.add_child(gm)

	gm.move_to_grid(3, 3)
	var pos := parent.position
	gm.move_to_grid(9, 9)  # ignorado — ainda movendo
	# Posição não deve ser 9,9 (ainda está indo para 3,3)
	assert_that(parent.position).is_equal(pos)

	remove_child(parent)
	parent.queue_free()
	gm.queue_free()


# ── Disabled ──────────────────────────────────────────────────────────────────

func test_disabled_does_not_move() -> void:
	var parent := _make_parent()
	add_child(parent)
	var gm := _make_gm()
	gm.enabled = false
	gm.snap_on_start = false
	parent.add_child(gm)

	var pos := parent.position
	Input.action_press("ui_right")
	gm._physics_process(0.0)
	Input.action_release("ui_right")
	assert_that(parent.position).is_equal(pos)

	remove_child(parent)
	parent.queue_free()
	gm.queue_free()


# ── Sem parent ────────────────────────────────────────────────────────────────

func test_no_parent_does_not_crash() -> void:
	var gm := _make_gm()
	gm._physics_process(0.0)
	assert_bool(gm.is_moving()).is_false()
	gm.queue_free()


# ── Clamp setters ─────────────────────────────────────────────────────────────

func test_grid_size_clamped() -> void:
	var gm := _make_gm()
	gm.grid_size = Vector2(1, 1)
	assert_float(gm.grid_size.x).is_equal(4.0)
	assert_float(gm.grid_size.y).is_equal(4.0)
	gm.queue_free()


func test_move_duration_clamped() -> void:
	var gm := _make_gm()
	gm.move_duration = 0.001
	assert_float(gm.move_duration).is_equal(0.01)
	gm.move_duration = 5.0
	assert_float(gm.move_duration).is_equal(1.0)
	gm.queue_free()


# ── Sinais ────────────────────────────────────────────────────────────────────

func test_emits_moved_signal() -> void:
	var parent := _make_parent()
	add_child(parent)
	var gm := _make_gm()
	gm.snap_on_start = false
	parent.add_child(gm)

	var moved_emitted := false
	var dir := Vector2.ZERO
	gm.moved.connect(func(d): moved_emitted = true; dir = d)

	gm.move_to_grid(4, 4)
	assert_bool(moved_emitted).is_true()

	remove_child(parent)
	parent.queue_free()
	gm.queue_free()
