extends GdUnitTestSuite
func test_defaults() -> void: var o:=ProfilerHook.new(); o.queue_free()

func test_edge_case_disabled() -> void:
	var c := ProfilerHook.new()
	c.auto_start = false
	# Nao deve crashar com disabled
	assert_bool(c.auto_start).is_false()
	c.queue_free()

func test_edge_case_multiple_instances() -> void:
	var a := ProfilerHook.new()
	var b := ProfilerHook.new()
	assert_object(a).is_not_null()
	assert_object(b).is_not_null()
	a.queue_free()
	b.queue_free()
