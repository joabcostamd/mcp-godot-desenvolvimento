extends GdUnitTestSuite
func test_defaults() -> void: var c:=ControllerRemap.new(); assert_array(c.actions).is_empty(); c.queue_free()
