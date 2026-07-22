extends GdUnitTestSuite
func test_defaults() -> void: var o:=ScreenShakeToggle.new(); o.queue_free()

func test_edge_case_disabled() -> void:
	var c := ScreenShakeToggle.new()
	c.enabled = false
	# Nao deve crashar com disabled
	assert_bool(c.enabled).is_false()
	c.queue_free()

func test_edge_case_multiple_instances() -> void:
	var a := ScreenShakeToggle.new()
	var b := ScreenShakeToggle.new()
	assert_object(a).is_not_null()
	assert_object(b).is_not_null()
	a.queue_free()
	b.queue_free()
