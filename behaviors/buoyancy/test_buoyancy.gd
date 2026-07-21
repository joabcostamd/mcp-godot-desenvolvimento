## test_buoyancy.gd — GdUnit4.
extends GdUnitTestSuite
func _make_b() -> Buoyancy: return Buoyancy.new()
func test_defaults() -> void:
	var b := _make_b(); assert_float(b.fluid_density).is_equal(1); assert_float(b.drag_coefficient).is_equal(0.5); b.queue_free()
func test_creates_shape() -> void:
	var b := _make_b(); add_child(b)
	var found := false; for c in b.get_children(): if c is CollisionShape2D: found=true
	assert_bool(found).is_true(); remove_child(b); b.queue_free()
func test_buoyancy_lifts_body() -> void:
	var b := _make_b(); add_child(b)
	var body := CharacterBody2D.new(); body.global_position = Vector2(0,50); b.surface_y = 0
	b._bodies.append(body); b._physics_process(0.1)  # depth = 50 > 0, aplica empuxo
	assert_float(body.velocity.y).is_less(0.0)  # para cima (negativo)
	remove_child(b); b.queue_free(); body.queue_free()
func test_drag_slows_body() -> void:
	var b := _make_b(); add_child(b)
	var body := CharacterBody2D.new(); body.velocity = Vector2(100,0)
	b._bodies.append(body); b._physics_process(0.1)  # drag = 0.5
	assert_float(body.velocity.length()).is_less(100.0)
	remove_child(b); b.queue_free(); body.queue_free()
func test_density_clamped() -> void:
	var b := _make_b(); b.fluid_density = 0; assert_float(b.fluid_density).is_equal(0.1); b.queue_free()
func test_drag_clamped() -> void:
	var b := _make_b(); b.drag_coefficient = 3; assert_float(b.drag_coefficient).is_equal(2); b.queue_free()
