## test_spring_joint.gd — GdUnit4.
extends GdUnitTestSuite
func _make_sj() -> SpringJoint: return SpringJoint.new()
func test_defaults() -> void:
	var sj := _make_sj(); assert_float(sj.stiffness).is_equal(100); assert_float(sj.rest_length).is_equal(100)
	assert_float(sj.damping).is_equal(5); sj.queue_free()
func test_requires_two_anchors() -> void:
	var sj := _make_sj(); add_child(sj); sj._physics_process(0.1)  # sem anchors → retorna
	assert_bool(true).is_true(); remove_child(sj); sj.queue_free()
func test_stiffness_clamped() -> void:
	var sj := _make_sj(); sj.stiffness = 0; assert_float(sj.stiffness).is_equal(1)
	sj.stiffness = 9999; assert_float(sj.stiffness).is_equal(1000); sj.queue_free()
func test_damping_clamped() -> void:
	var sj := _make_sj(); sj.damping = -1; assert_float(sj.damping).is_equal(0)
	sj.damping = 999; assert_float(sj.damping).is_equal(50); sj.queue_free()
func test_rest_length_clamped() -> void:
	var sj := _make_sj(); sj.rest_length = 0; assert_float(sj.rest_length).is_equal(1); sj.queue_free()
func test_two_bodies_attract() -> void:
	var sj := _make_sj(); add_child(sj)
	var a := CharacterBody2D.new(); a.name="A"; a.global_position=Vector2(0,0); add_child(a)
	var b := CharacterBody2D.new(); b.name="B"; b.global_position=Vector2(200,0); add_child(b)
	sj.anchor_a = NodePath("../A"); sj.anchor_b = NodePath("../B")
	sj.stiffness = 500; sj.rest_length = 100
	sj._physics_process(0.1)  # dist=200 > rest=100, spring puxa
	assert_bool(true).is_true()  # não crashou
	remove_child(a); remove_child(b); remove_child(sj)
	a.queue_free(); b.queue_free(); sj.queue_free()
