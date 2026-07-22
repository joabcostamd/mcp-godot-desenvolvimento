## test_wind_zone.gd — GdUnit4.
extends GdUnitTestSuite
func _make_wz() -> WindZone: return WindZone.new()
func test_defaults() -> void:
	var wz := _make_wz(); assert_float(wz.wind_strength).is_equal(300); assert_float(wz.turbulence).is_equal(0); wz.queue_free()
func test_creates_shape() -> void:
	var wz := _make_wz(); add_child(wz)
	var found := false; for c in wz.get_children(): if c is CollisionShape2D: found=true
	assert_bool(found).is_true(); remove_child(wz); wz.queue_free()
func test_wind_pushes_body() -> void:
	var wz := _make_wz(); add_child(wz)
	var body := CharacterBody2D.new(); wz._bodies.append(body)
	wz._physics_process(0.1)  # 300 * 0.1 = 30
	assert_float(body.velocity.x).is_equal(30.0)
	remove_child(wz); wz.queue_free(); body.queue_free()
func test_direction_normalized() -> void:
	var wz := _make_wz(); wz.wind_direction = Vector2(5,5)
	assert_float(wz.wind_direction.length()).is_equal(1.0); wz.queue_free()
func test_turbulence_clamped() -> void:
	var wz := _make_wz(); wz.turbulence = -1; assert_float(wz.turbulence).is_equal(0)
	wz.turbulence = 2; assert_float(wz.turbulence).is_equal(1); wz.queue_free()
