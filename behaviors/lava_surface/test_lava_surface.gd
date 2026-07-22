extends GdUnitTestSuite
func test_defaults() -> void:
	var ls:=LavaSurface.new(); assert_float(ls.flow_speed).is_equal(0.5); assert_float(ls.glow_intensity).is_equal(1.5); ls.queue_free()
func test_color_update() -> void:
	var ls:=LavaSurface.new(); ls.lava_color=Color.BLUE; assert_color(ls.lava_color).is_equal(Color.BLUE); ls.queue_free()
func test_process_no_crash() -> void:
	var ls:=LavaSurface.new(); ls._process(0.016); ls.queue_free()
