## test_conveyor_belt.gd
extends GdUnitTestSuite
func _make_cb() -> ConveyorBelt: return ConveyorBelt.new()
func test_defaults() -> void:
	var cb := _make_cb()
	assert_float(cb.direction.x).is_equal(100); assert_str(cb.target_group).is_equal(""); cb.queue_free()
func test_no_crash() -> void:
	var cb := _make_cb(); add_child(cb); cb._physics_process(0.1); remove_child(cb); cb.queue_free()
