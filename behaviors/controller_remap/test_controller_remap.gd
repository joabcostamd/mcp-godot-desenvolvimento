extends GdUnitTestSuite
func test_defaults() -> void: var c:=ControllerRemap.new(); assert_array(c.actions).is_empty(); c.queue_free()

func test_edge_case_multiple_instances() -> void:
	var a := ControllerRemap.new()
	var b := ControllerRemap.new()
	assert_object(a).is_not_null()
	assert_object(b).is_not_null()
	a.queue_free()
	b.queue_free()
