extends GdUnitTestSuite
func test_flip() -> void: var c:=Card.new(); c.face_up=false; assert_bool(c.face_up).is_false(); c.queue_free()
