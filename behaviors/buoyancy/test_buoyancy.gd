## test_buoyancy.gd
extends GdUnitTestSuite
func _make_b() -> Buoyancy: return Buoyancy.new()
func test_defaults() -> void:
	var b := _make_b(); assert_float(b.fluid_density).is_equal(1); b.queue_free()
func test_no_crash() -> void:
	var b := _make_b(); add_child(b); b._physics_process(0.1); remove_child(b); b.queue_free()
