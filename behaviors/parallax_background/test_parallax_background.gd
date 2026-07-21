## test_parallax_bg.gd
extends GdUnitTestSuite
func test_defaults() -> void:
	var pb := ParallaxBackground.new()
	assert_that(pb.auto_scroll).is_equal(Vector2.ZERO); assert_bool(pb.follow_camera).is_true(); pb.queue_free()
func test_no_crash() -> void:
	var pb := ParallaxBackground.new(); add_child(pb); pb._process(0.1); remove_child(pb); pb.queue_free()
