extends GdUnitTestSuite
func test_defaults() -> void: var o:=BlendSpace1D.new(); o.queue_free()

func test_edge_case_multiple_instances() -> void:
	var a := BlendSpace1d.new()
	var b := BlendSpace1d.new()
	assert_object(a).is_not_null()
	assert_object(b).is_not_null()
	a.queue_free()
	b.queue_free()
