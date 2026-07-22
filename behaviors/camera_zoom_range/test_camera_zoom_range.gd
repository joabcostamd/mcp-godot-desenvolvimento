extends GdUnitTestSuite
func test_defaults() -> void: var c:=CameraZoomRange.new(); assert_vector(c.zoom_min).is_equal(Vector2(0.5,0.5)); c.queue_free()
func test_zoom_in() -> void: var cam:=Camera2D.new(); var czr:=CameraZoomRange.new(); cam.add_child(czr); czr.zoom_in(); assert_bool(cam.zoom.x>1.0).is_true(); cam.queue_free()
func test_zoom_clamped() -> void: var cam:=Camera2D.new(); var czr:=CameraZoomRange.new(); czr.zoom_max=Vector2(2,2); cam.add_child(czr); czr.zoom_speed=100.0; czr.zoom_in(); czr.zoom_in(); assert_float(cam.zoom.x).is_less_equal(2.0); cam.queue_free()
