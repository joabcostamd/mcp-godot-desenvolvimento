## test_parallax_bg.gd — GdUnit4.
extends GdUnitTestSuite
func _make_pb() -> ParallaxBackground: return ParallaxBackground.new()
func test_defaults() -> void:
	var pb := _make_pb(); assert_that(pb.auto_scroll).is_equal(Vector2.ZERO); assert_bool(pb.follow_camera).is_true(); pb.queue_free()
func test_add_layer() -> void:
	var pb := _make_pb(); add_child(pb)
	var tex := PlaceholderTexture2D.new(); tex.size = Vector2(64,64)
	pb.add_layer(tex, 0.5)
	assert_int(pb._layers.size()).is_equal(1)
	remove_child(pb); pb.queue_free()
func test_scan_layers() -> void:
	var pb := _make_pb(); add_child(pb)
	var s := Sprite2D.new(); s.set_meta("parallax_scale", 0.3); pb.add_child(s)
	pb._scan_layers()
	assert_int(pb._layers.size()).is_equal(1)
	remove_child(pb); pb.queue_free()
func test_process_no_camera() -> void:
	var pb := _make_pb(); add_child(pb); pb._process(0.1)
	assert_bool(true).is_true(); remove_child(pb); pb.queue_free()
