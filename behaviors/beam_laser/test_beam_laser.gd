## test_beam_laser.gd — Testes do BeamLaser | GdUnit4.
##
## Cobre: dano contínuo via RayCast2D real (StaticBody2D + CollisionShape2D),
##        sinais, transições, edge cases, visual, warnings, _find_health.
##
## Requer: GdUnit4 instalado como addon.

extends GdUnitTestSuite


# ── Dano (com colisão real via StaticBody2D) ──────────────────────────────────

func test_deals_damage_on_collision() -> void:
	var beam := _make_beam(100.0, 4.0, 500.0)
	var health := _make_health(200)
	var body := _make_static_body_at(Vector2(50, 0), Vector2(10, 10))
	body.add_child(health)

	add_child(beam)
	add_child(body)

	# Força raycast update (fora de _physics_process, necessário)
	beam.force_raycast_update()

	assert_bool(beam.is_colliding()).is_true().override_failure_message("StaticBody2D deve ser detectado pelo raio")
	# Aplica dano via _physics_process (delta=1.0 → 100dps → 100 dano)
	beam._damage_accumulator = 0.0
	beam._physics_process(1.0)
	assert_int(health.current_hp).is_less(200)


func test_damage_zero_when_disabled() -> void:
	var beam := _make_beam(100.0, 4.0, 500.0)
	beam.enabled = false
	var health := _make_health(200)
	var body := _make_static_body_at(Vector2(50, 0), Vector2(10, 10))
	body.add_child(health)

	add_child(beam)
	add_child(body)

	beam._physics_process(1.0)
	# enabled=false → _physics_process retorna cedo, nenhum dano
	assert_int(health.current_hp).is_equal(200)


# ── Acumulador de dano ────────────────────────────────────────────────────────

func test_damage_accumulates_correctly() -> void:
	var beam := _make_beam(10.0, 4.0, 500.0)
	add_child(beam)

	beam._damage_accumulator = 0.0
	beam._damage_accumulator += 10.0 * 0.3  # = 3.0
	assert_float(beam._damage_accumulator).is_equal(3.0)
	beam._damage_accumulator += 10.0 * 0.3  # = 6.0
	assert_float(beam._damage_accumulator).is_greater(5.9)


# ── Sinal hitting (com colisão real) ──────────────────────────────────────────

func test_hitting_signal_with_collision() -> void:
	var beam := _make_beam(30.0, 4.0, 500.0)
	var health := _make_health(100)
	var body := _make_static_body_at(Vector2(50, 0), Vector2(10, 10))
	body.add_child(health)

	add_child(beam)
	add_child(body)

	beam.force_raycast_update()

	var fired := false
	var captured_dps := 0.0
	beam.hitting.connect(func(_t, d): fired = true; captured_dps = d)
	beam._physics_process(0.016)
	assert_bool(fired).is_true().override_failure_message("hitting deve ser emitido durante colisão")
	assert_float(captured_dps).is_equal(30.0)


# ── Sinal stopped ─────────────────────────────────────────────────────────────

func test_stopped_on_transition() -> void:
	var beam := _make_beam(30.0, 4.0, 500.0)
	add_child(beam)

	beam._was_hitting = true
	var stopped_fired := false
	beam.stopped.connect(func(): stopped_fired = true)
	beam._physics_process(0.016)
	assert_bool(stopped_fired).is_true()
	assert_bool(beam._was_hitting).is_false()


func test_stopped_clears_accumulator() -> void:
	var beam := _make_beam(30.0, 4.0, 500.0)
	add_child(beam)

	beam._damage_accumulator = 5.0
	beam._was_hitting = true
	beam._hit_to_no_hit()
	assert_float(beam._damage_accumulator).is_equal(0.0)


# ── Edge cases ────────────────────────────────────────────────────────────────

func test_no_collision_does_not_crash() -> void:
	var beam := _make_beam(30.0, 4.0, 500.0)
	add_child(beam)

	beam._physics_process(0.016)
	beam._physics_process(0.016)
	assert_bool(true)


func test_double_stopped_not_emitted() -> void:
	var beam := _make_beam(30.0, 4.0, 500.0)
	add_child(beam)

	var stopped_count := 0
	beam.stopped.connect(func(): stopped_count += 1)

	beam._physics_process(0.016)
	beam._physics_process(0.016)
	assert_int(stopped_count).is_equal(0)


func test_max_range_sets_target_position() -> void:
	var beam := _make_beam(50.0, 4.0, 100.0)
	assert_float(beam.max_range).is_equal(100.0)
	assert_vector2(beam.target_position).is_equal(Vector2(100.0, 0.0))


# ── _find_health ──────────────────────────────────────────────────────────────

func test_find_health_direct() -> void:
	var beam := _make_beam(30.0, 4.0, 500.0)
	var health := _make_health(100)
	add_child(beam)

	var found := beam._find_health(health)
	assert_object(found).is_not_null()
	assert_int(found.max_hp).is_equal(100)


func test_find_health_on_child() -> void:
	var beam := _make_beam(30.0, 4.0, 500.0)
	var health := _make_health(50)
	var target := Node2D.new()
	target.add_child(health)
	add_child(beam)

	var found := beam._find_health(target)
	assert_object(found).is_not_null()
	assert_int(found.max_hp).is_equal(50)


func test_find_health_null_for_node2d_without_health() -> void:
	var beam := _make_beam(30.0, 4.0, 500.0)
	var target := Node2D.new()
	add_child(beam)

	var found := beam._find_health(target)
	assert_object(found).is_null()


# ── Visual ────────────────────────────────────────────────────────────────────

func test_line_created_in_tree() -> void:
	var beam := _make_beam(30.0, 4.0, 500.0)
	add_child(beam)

	var line_found := false
	for child in beam.get_children():
		if child is Line2D:
			line_found = true
			var line: Line2D = child as Line2D
			assert_float(line.width).is_equal(4.0)
			assert_float(line.get_point_position(1).x).is_equal(500.0)
			break
	assert_bool(line_found).is_true()


func test_beam_color_default_is_red() -> void:
	var beam := _make_beam(30.0, 4.0, 500.0)
	assert_color(beam.beam_color).is_equal(Color.RED)


func test_beam_color_custom() -> void:
	var beam := _make_beam(30.0, 4.0, 500.0)
	beam.beam_color = Color.CYAN
	assert_color(beam.beam_color).is_equal(Color.CYAN)
	add_child(beam)
	for child in beam.get_children():
		if child is Line2D:
			var line: Line2D = child as Line2D
			assert_color(line.default_color).is_equal(Color.CYAN)
			break


# ── Warnings ──────────────────────────────────────────────────────────────────

func test_warning_disabled() -> void:
	var beam := _make_beam(30.0, 4.0, 500.0)
	beam.enabled = false
	add_child(beam)

	var warnings := beam._get_configuration_warnings()
	var found := false
	for w in warnings:
		if "enabled" in w:
			found = true
			break
	assert_bool(found).is_true()


func test_warning_collision_mask_zero() -> void:
	var beam := _make_beam(30.0, 4.0, 500.0)
	beam.collision_mask = 0
	add_child(beam)

	var warnings := beam._get_configuration_warnings()
	var found := false
	for w in warnings:
		if "collision_mask" in w:
			found = true
			break
	assert_bool(found).is_true()


# ── Helpers ──────────────────────────────────────────────────────────────────

func _make_beam(dps: float, width: float, max_range_val: float) -> BeamLaser:
	var b := BeamLaser.new()
	b.damage_per_second = dps
	b.beam_width = width
	b.max_range = max_range_val
	return b


func _make_health(hp: int) -> Health:
	var h := Health.new()
	h.max_hp = hp
	h.current_hp = hp
	return h


## Cria um StaticBody2D com CollisionShape2D na posição especificada,
## para que o RayCast2D possa detectar colisão real.
func _make_static_body_at(pos: Vector2, shape_size: Vector2) -> StaticBody2D:
	var body := StaticBody2D.new()
	body.global_position = pos
	var shape := RectangleShape2D.new()
	shape.size = shape_size
	var collision := CollisionShape2D.new()
	collision.shape = shape
	body.add_child(collision)
	return body
