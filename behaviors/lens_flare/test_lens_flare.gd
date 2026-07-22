extends GdUnitTestSuite
func test_defaults() -> void:
	var lf:=LensFlare.new(); assert_float(lf.flare_intensity).is_equal(1.0); lf.queue_free()
func test_zero_intensity_no_crash() -> void:
	var lf:=LensFlare.new(); lf.flare_intensity=0.0; lf._draw(); lf.queue_free()
func test_color() -> void:
	var lf:=LensFlare.new(); lf.flare_color=Color.RED; assert_color(lf.flare_color).is_equal(Color.RED); lf.queue_free()
