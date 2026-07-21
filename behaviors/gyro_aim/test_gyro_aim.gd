extends GdUnitTestSuite
func test_gyro() -> void: var g:=GyroAim.new(); var r:=g.process_gyro(Vector2(1,0)); assert_bool(r.length()>0).is_true(); g.queue_free()
