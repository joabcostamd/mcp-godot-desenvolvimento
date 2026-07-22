extends GdUnitTestSuite
func test_defaults() -> void: var o:=ModularWeapon.new(); o.queue_free()

func test_edge_case_multiple_instances() -> void:
	var a := ModularWeapon.new()
	var b := ModularWeapon.new()
	assert_object(a).is_not_null()
	assert_object(b).is_not_null()
	a.queue_free()
	b.queue_free()
