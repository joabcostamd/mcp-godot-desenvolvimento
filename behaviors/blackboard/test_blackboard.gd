extends GdUnitTestSuite
func test_set_get() -> void:
	var bb:=Blackboard.new(); bb.set_var("score",42)
	assert_int(bb.get_var("score")).is_equal(42); bb.queue_free()
func test_trigger() -> void:
	var bb:=Blackboard.new(); var v=0
	bb.set_trigger("x",func(val): v=val)
	bb.set_var("x",99); assert_int(v).is_equal(99); bb.queue_free()
