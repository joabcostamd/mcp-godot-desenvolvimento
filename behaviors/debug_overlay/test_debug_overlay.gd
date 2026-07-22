extends GdUnitTestSuite
func test_defaults() -> void: var o:=DebugOverlay.new(); o.queue_free()

func test_edge_case_disabled() -> void:
	var c := DebugOverlay.new()
	c.show_fps = false
	# Nao deve crashar com disabled
	assert_bool(c.show_fps).is_false()
	c.queue_free()

func test_edge_case_multiple_instances() -> void:
	var a := DebugOverlay.new()
	var b := DebugOverlay.new()
	assert_object(a).is_not_null()
	assert_object(b).is_not_null()
	a.queue_free()
	b.queue_free()
