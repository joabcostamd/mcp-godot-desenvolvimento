## test_gravity_zone.gd — GdUnit4.
extends GdUnitTestSuite
func _make_gz() -> GravityZone: return GravityZone.new()
func test_defaults() -> void:
	var gz := _make_gz(); assert_float(gz.gravity_strength).is_equal(980); assert_bool(gz.override).is_false(); gz.queue_free()
func test_creates_shape() -> void:
	var gz := _make_gz(); add_child(gz)
	var found := false; for c in gz.get_children(): if c is CollisionShape2D: found=true
	assert_bool(found).is_true(); remove_child(gz); gz.queue_free()
func test_direction_normalized() -> void:
	var gz := _make_gz(); gz.gravity_direction = Vector2(3,4)
	assert_float(gz.gravity_direction.length()).is_equal(1.0); gz.queue_free()
func test_zero_direction_defaults() -> void:
	var gz := _make_gz(); gz.gravity_direction = Vector2.ZERO
	assert_that(gz.gravity_direction).is_equal(Vector2(0,1)); gz.queue_free()
func test_override_applies() -> void:
	var gz := _make_gz(); gz.override = true; add_child(gz)
	var body := CharacterBody2D.new(); body.velocity = Vector2(100,50)
	gz._bodies.append(body); gz._physics_process(0.1)
	assert_float(body.velocity.x).is_equal(0.0)  # override zerou
	remove_child(gz); gz.queue_free(); body.queue_free()
func test_strength_clamped() -> void:
	var gz := _make_gz(); gz.gravity_strength = -10; assert_float(gz.gravity_strength).is_equal(0)
	gz.gravity_strength = 9999; assert_float(gz.gravity_strength).is_equal(5000); gz.queue_free()
