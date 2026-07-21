## test_gravity_zone.gd
extends GdUnitTestSuite
func _make_gz() -> GravityZone: return GravityZone.new()
func test_defaults() -> void:
	var gz := _make_gz()
	assert_float(gz.gravity_strength).is_equal(980); assert_bool(gz.override).is_false(); gz.queue_free()
func test_no_crash() -> void:
	var gz := _make_gz(); add_child(gz); gz._physics_process(0.1); remove_child(gz); gz.queue_free()
