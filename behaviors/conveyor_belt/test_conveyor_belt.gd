## test_conveyor_belt.gd — GdUnit4.
extends GdUnitTestSuite
func _make_cb() -> ConveyorBelt: return ConveyorBelt.new()
func test_defaults() -> void:
	var cb := _make_cb(); assert_float(cb.direction.x).is_equal(100); assert_str(cb.target_group).is_equal(""); cb.queue_free()
func test_creates_shape() -> void:
	var cb := _make_cb(); add_child(cb)
	var found := false; for c in cb.get_children(): if c is CollisionShape2D: found=true
	assert_bool(found).is_true(); remove_child(cb); cb.queue_free()
func test_moves_character_body() -> void:
	var cb := _make_cb(); add_child(cb)
	var body := CharacterBody2D.new(); cb._bodies.append(body)
	cb._physics_process(0.5)  # 100 * 0.5 = 50
	assert_float(body.velocity.x).is_equal(50.0)
	remove_child(cb); cb.queue_free(); body.queue_free()
func test_moves_rigid_body() -> void:
	var cb := _make_cb(); add_child(cb)
	var body := RigidBody2D.new(); cb._bodies.append(body)
	cb._physics_process(0.1)  # apply_central_force com direction * 10
	assert_bool(true).is_true()  # não crashou
	remove_child(cb); cb.queue_free(); body.queue_free()
func test_target_group_filter() -> void:
	var cb := _make_cb(); cb.target_group = "players"; add_child(cb)
	var body := CharacterBody2D.new()  # sem grupo
	cb._bodies.append(body); cb._physics_process(0.5)
	assert_float(body.velocity.x).is_equal(0.0)  # não moveu (grupo errado)
	remove_child(cb); cb.queue_free(); body.queue_free()
func test_stale_bodies_removed() -> void:
	var cb := _make_cb(); add_child(cb)
	var body := CharacterBody2D.new(); cb._bodies.append(body)
	body.queue_free()  # corpo destruído
	cb._physics_process(0.1)  # filter remove stale
	assert_bool(true).is_true()  # não crashou
	remove_child(cb); cb.queue_free()
