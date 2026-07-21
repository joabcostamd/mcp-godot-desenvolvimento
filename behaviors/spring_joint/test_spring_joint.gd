## test_spring_joint.gd
extends GdUnitTestSuite
func test_defaults() -> void:
	var sj := SpringJoint.new()
	assert_float(sj.stiffness).is_equal(100); assert_float(sj.rest_length).is_equal(100); sj.queue_free()
func test_no_crash() -> void:
	var sj := SpringJoint.new(); add_child(sj); sj._physics_process(0.1); remove_child(sj); sj.queue_free()
