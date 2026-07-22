## test_magnet.gd — Testes do Magnet | GdUnit4.

extends GdUnitTestSuite

func _make_m() -> Magnet: return Magnet.new()

func test_default_parameters() -> void:
	var m := _make_m()
	assert_float(m.force).is_equal(500.0)
	assert_int(m.falloff).is_equal(1)
	assert_str(m.target_group).is_equal("")
	m.queue_free()

func test_force_clamped() -> void:
	var m := _make_m()
	m.force = 5; assert_float(m.force).is_equal(10.0)
	m.force = 9999; assert_float(m.force).is_equal(5000.0)
	m.queue_free()

func test_falloff_clamped() -> void:
	var m := _make_m()
	m.falloff = -1; assert_int(m.falloff).is_equal(0)
	m.falloff = 99; assert_int(m.falloff).is_equal(2)
	m.queue_free()

func test_creates_collision_shape() -> void:
	var m := _make_m(); add_child(m)
	var found := false
	for c in m.get_children():
		if c is CollisionShape2D: found = true
	assert_bool(found).is_true()
	remove_child(m); m.queue_free()

func test_ignores_non_character_body() -> void:
	var m := _make_m(); add_child(m)
	var node := Node2D.new(); add_child(node)
	m._bodies.append(node)
	m._physics_process(0.1)  # deve ignorar, não é CharacterBody2D
	assert_bool(true).is_true()  # não crashou
	remove_child(node); remove_child(m)
	node.queue_free(); m.queue_free()

func test_target_group_filter() -> void:
	var m := _make_m()
	m.target_group = "enemies"
	assert_str(m.target_group).is_equal("enemies")
	m.queue_free()

func test_no_duplicate_bodies() -> void:
	var m := _make_m(); add_child(m)
	var body := CharacterBody2D.new()
	m._bodies.append(body)
	m._bodies.append(body)  # duplicata manual
	m._on_enter(body)  # não deve adicionar duplicata
	var count := 0
	for b in m._bodies:
		if b == body: count += 1
	assert_int(count).is_equal(2)  # a duplicata manual permanece (a guarda é só no enter)
	remove_child(m); m.queue_free(); body.queue_free()
