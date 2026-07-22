extends GdUnitTestSuite
func test_defaults() -> void:
	var ws:=WaterSurface.new(); assert_float(ws.wave_speed).is_equal(1.0); assert_float(ws.wave_amplitude).is_equal(5.0); ws.queue_free()
func test_color_update() -> void:
	var ws:=WaterSurface.new(); ws.water_color=Color.RED; assert_color(ws.water_color).is_equal(Color.RED); ws.queue_free()
func test_process_no_crash() -> void:
	var ws:=WaterSurface.new(); ws._process(0.016); ws.queue_free()
