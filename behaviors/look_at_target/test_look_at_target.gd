## test_look_at_target.gd — GdUnit4.

extends GdUnitTestSuite

func _make_la() -> LookAtTarget: return LookAtTarget.new()

func test_defaults() -> void:
	var la := _make_la()
	assert_float(la.rotation_speed).is_equal(5.0)
	assert_float(la.angle_offset).is_equal(0.0)
	assert_bool(la.has_target()).is_false(); la.queue_free()

func test_set_target() -> void:
	var la := _make_la(); add_child(la)
	var t := Node2D.new(); add_child(t)
	la.set_target(t)
	assert_bool(la.has_target()).is_true()
	la.clear_target()
	assert_bool(la.has_target()).is_false()
	remove_child(t); remove_child(la); t.queue_free(); la.queue_free()

func test_set_target_position() -> void:
	var la := _make_la(); add_child(la)
	la.set_target_position(Vector2(100,0))
	assert_bool(la.has_target()).is_true()
	remove_child(la); la.queue_free()

func test_rotates_toward_target() -> void:
	var p := Node2D.new(); add_child(p)
	var la := _make_la(); la.rotation_speed = 0.0  # instant
	p.add_child(la)
	var t := Node2D.new(); t.global_position = Vector2(100,0); add_child(t)
	la.set_target(t)
	la._physics_process(0.1)
	assert_float(p.rotation).is_equal(0.0)  # aponta para direita
	remove_child(t); remove_child(p); t.queue_free(); p.queue_free(); la.queue_free()

func test_clear_target_emits() -> void:
	var la := _make_la(); add_child(la)
	var t := Node2D.new(); la.set_target(t)
	var emitted := false
	la.target_lost.connect(func(): emitted = true)
	la.clear_target()
	assert_bool(emitted).is_true()
	t.queue_free(); remove_child(la); la.queue_free()

func test_target_acquired_signal() -> void:
	var la := _make_la(); add_child(la)
	var t := Node2D.new()
	var emitted := false
	la.target_acquired.connect(func(_n): emitted = true)
	la.set_target(t)
	assert_bool(emitted).is_true()
	t.queue_free(); remove_child(la); la.queue_free()
