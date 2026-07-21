## test_flocking.gd — Testes do Flocking | GdUnit4.
##
## Requer: GdUnit4 instalado como addon.

extends GdUnitTestSuite


func test_separation_pushes_apart() -> void:
	var f := _make_flock(1.5, 0.0, 0.0, 200.0, 150.0)
	var parent := CharacterBody2D.new()
	parent.add_child(f)
	add_child(parent)
	var n := CharacterBody2D.new()
	n.global_position = Vector2(10, 0)
	add_child(n)

	var force := f._separation(parent, [n])
	assert_float(force.x).is_less(0.0)


func test_alignment_averages_velocity() -> void:
	var f := _make_flock(0.0, 1.0, 0.0, 200.0, 150.0)
	add_child(f)
	var n := CharacterBody2D.new()
	n.velocity = Vector2(100, 0)
	add_child(n)

	var force := f._alignment([n])
	assert_float(force.x).is_greater(0.0)


func test_cohesion_toward_center() -> void:
	var f := _make_flock(0.0, 0.0, 1.0, 200.0, 150.0)
	var parent := CharacterBody2D.new()
	parent.add_child(f)
	add_child(parent)
	var n := CharacterBody2D.new()
	n.global_position = Vector2(50, 0)
	add_child(n)

	var force := f._cohesion(parent, [n])
	assert_float(force.x).is_greater(0.0)


func test_empty_neighbors_no_crash() -> void:
	var f := _make_flock(1.0, 1.0, 1.0, 100.0, 150.0)
	add_child(f)
	f._physics_process(0.016)
	assert_bool(true)


func test_no_parent_no_crash() -> void:
	var f := _make_flock(1.0, 1.0, 1.0, 100.0, 150.0)
	add_child(f)
	f._physics_process(0.016)
	assert_bool(true)


func test_parent_not_character_body() -> void:
	var f := _make_flock(1.0, 1.0, 1.0, 100.0, 150.0)
	var parent := Node2D.new()
	parent.add_child(f)
	add_child(parent)
	f._physics_process(0.016)
	assert_bool(true)


func test_weights_zero_no_force() -> void:
	var f := _make_flock(0.0, 0.0, 0.0, 100.0, 150.0)
	var parent := CharacterBody2D.new()
	parent.add_child(f)
	add_child(parent)
	var n := CharacterBody2D.new()
	n.global_position = Vector2(10, 0)
	n.add_to_group("flock")
	add_child(n)

	f._physics_process(0.016)
	assert_vector2(parent.velocity).is_equal(Vector2.ZERO)


func test_max_speed_clamped() -> void:
	var f := _make_flock(1.0, 1.0, 1.0, 100.0, 0.0)
	assert_float(f.max_speed).is_equal(10.0)


func test_warning_empty_group() -> void:
	var f := _make_flock(1.0, 1.0, 1.0, 100.0, 150.0)
	f.flock_group = ""
	add_child(f)
	var found := false
	for w in f._get_configuration_warnings():
		if "flock_group" in w:
			found = true
	assert_bool(found).is_true()


func _make_flock(sep: float, ali: float, coh: float, radius: float, speed: float) -> Flocking:
	var f := Flocking.new()
	f.separation_weight = sep
	f.alignment_weight = ali
	f.cohesion_weight = coh
	f.neighbor_radius = radius
	f.max_speed = speed
	return f
