## test_hitscan.gd — Testes do Hitscan | GdUnit4.
##
## Cobre: dano, sinais, flash visual, edge cases, warnings.
## Usa StaticBody2D + CollisionShape2D para colisão real.
##
## Requer: GdUnit4 instalado como addon.

extends GdUnitTestSuite


# ── Dano ──────────────────────────────────────────────────────────────────────

func test_fire_deals_damage() -> void:
	var hs := _make_hitscan(50, 1000.0)
	var health := _make_health(200)
	var body := _make_static_body_at(Vector2(100, 0), Vector2(10, 10))
	body.add_child(health)
	add_child(hs)
	add_child(body)

	hs.fire()
	assert_int(health.current_hp).is_equal(150)


func test_fire_no_target_no_damage() -> void:
	var hs := _make_hitscan(50, 1000.0)
	add_child(hs)

	hs.fire()
	assert_bool(true)  # não crasha


func test_fire_disabled_ignored() -> void:
	var hs := _make_hitscan(50, 1000.0)
	hs.enabled = false
	var health := _make_health(200)
	var body := _make_static_body_at(Vector2(100, 0), Vector2(10, 10))
	body.add_child(health)
	add_child(hs)
	add_child(body)

	hs.fire()
	assert_int(health.current_hp).is_equal(200)


# ── Sinais ────────────────────────────────────────────────────────────────────

func test_hit_signal() -> void:
	var hs := _make_hitscan(30, 1000.0)
	var health := _make_health(100)
	var body := _make_static_body_at(Vector2(100, 0), Vector2(10, 10))
	body.add_child(health)
	add_child(hs)
	add_child(body)

	var hit_fired := false
	var hit_target: Node = null
	var hit_dmg := 0
	hs.hit.connect(func(t, d): hit_fired = true; hit_target = t; hit_dmg = d)
	hs.fire()

	assert_bool(hit_fired).is_true()
	assert_int(hit_dmg).is_equal(30)


func test_fired_signal_always() -> void:
	var hs := _make_hitscan(30, 1000.0)
	add_child(hs)

	var fired_count := 0
	hs.fired.connect(func(_t, _d): fired_count += 1)
	hs.fire()
	assert_int(fired_count).is_equal(1)


func test_fired_without_target_emits_null() -> void:
	var hs := _make_hitscan(30, 1000.0)
	add_child(hs)

	var fired_target: Node = hs  # dummy non-null
	var fired_dmg := -1
	hs.fired.connect(func(t, d): fired_target = t; fired_dmg = d)
	hs.fire()

	assert_object(fired_target).is_null()
	assert_int(fired_dmg).is_equal(0)


func test_fired_with_target_emits_correct() -> void:
	var hs := _make_hitscan(40, 1000.0)
	var health := _make_health(100)
	var body := _make_static_body_at(Vector2(100, 0), Vector2(10, 10))
	body.add_child(health)
	add_child(hs)
	add_child(body)

	var fired_dmg := 0
	hs.fired.connect(func(_t, d): fired_dmg = d)
	hs.fire()

	assert_int(fired_dmg).is_equal(40)


# ── Flash visual ──────────────────────────────────────────────────────────────

func test_flash_shows_on_fire() -> void:
	var hs := _make_hitscan(30, 1000.0)
	add_child(hs)

	hs.fire()
	assert_bool(hs._line.visible).is_true()


func test_flash_hides_after_timer() -> void:
	var hs := _make_hitscan(30, 1000.0)
	hs.flash_duration = 0.02
	add_child(hs)

	hs.fire()
	assert_bool(hs._line.visible).is_true()
	# Aguarda o timer expirar
	await get_tree().create_timer(0.03).timeout
	assert_bool(hs._line.visible).is_false()


# ── _find_health ──────────────────────────────────────────────────────────────

func test_find_health_direct() -> void:
	var hs := _make_hitscan(30, 1000.0)
	var health := _make_health(100)
	add_child(hs)
	assert_object(hs._find_health(health)).is_not_null()


func test_find_health_on_child() -> void:
	var hs := _make_hitscan(30, 1000.0)
	var health := _make_health(50)
	var target := Node2D.new()
	target.add_child(health)
	add_child(hs)
	assert_object(hs._find_health(target)).is_not_null()


func test_find_health_null() -> void:
	var hs := _make_hitscan(30, 1000.0)
	add_child(hs)
	assert_object(hs._find_health(Node2D.new())).is_null()


# ── Parâmetros ────────────────────────────────────────────────────────────────

func test_damage_clamped() -> void:
	var hs := _make_hitscan(0, 1000.0)
	assert_int(hs.damage).is_equal(1)  # clamped min


func test_max_range_sets_target_position() -> void:
	var hs := _make_hitscan(30, 500.0)
	assert_float(hs.max_range).is_equal(500.0)
	assert_vector2(hs.target_position).is_equal(Vector2(500.0, 0.0))


func test_beam_color_default() -> void:
	var hs := _make_hitscan(30, 1000.0)
	assert_color(hs.beam_color).is_equal(Color.YELLOW)


func test_beam_color_custom() -> void:
	var hs := _make_hitscan(30, 1000.0)
	hs.beam_color = Color.CYAN
	assert_color(hs.beam_color).is_equal(Color.CYAN)
	add_child(hs)
	for child in hs.get_children():
		if child is Line2D:
			assert_color((child as Line2D).default_color).is_equal(Color.CYAN)
			break


# ── Warnings ──────────────────────────────────────────────────────────────────

func test_warning_disabled() -> void:
	var hs := _make_hitscan(30, 1000.0)
	hs.enabled = false
	add_child(hs)
	var found := false
	for w in hs._get_configuration_warnings():
		if "enabled" in w:
			found = true
	assert_bool(found).is_true()


func test_warning_collision_mask_zero() -> void:
	var hs := _make_hitscan(30, 1000.0)
	hs.collision_mask = 0
	add_child(hs)
	var found := false
	for w in hs._get_configuration_warnings():
		if "collision_mask" in w:
			found = true
	assert_bool(found).is_true()


# ── Helpers ──────────────────────────────────────────────────────────────────

func _make_hitscan(dmg: int, max_range_val: float) -> Hitscan:
	var hs := Hitscan.new()
	hs.damage = dmg
	hs.max_range = max_range_val
	return hs


func _make_health(hp: int) -> Health:
	var h := Health.new()
	h.max_hp = hp
	h.current_hp = hp
	return h


func _make_static_body_at(pos: Vector2, shape_size: Vector2) -> StaticBody2D:
	var body := StaticBody2D.new()
	body.global_position = pos
	var shape := RectangleShape2D.new()
	shape.size = shape_size
	var collision := CollisionShape2D.new()
	collision.shape = shape
	body.add_child(collision)
	return body
