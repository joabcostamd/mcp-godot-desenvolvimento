extends GdUnitTestSuite
func test_dead_zone() -> void: var d:=DeadZoneConfig.new(); d.dead_zone=0.3; assert_vector(d.apply_dead_zone(Vector2(0.1,0))).is_equal(Vector2.ZERO); d.queue_free()
func test_passthrough() -> void: var d:=DeadZoneConfig.new(); d.dead_zone=0.0; assert_bool(d.apply_dead_zone(Vector2(0.5,0)).length()>0).is_true(); d.queue_free()
