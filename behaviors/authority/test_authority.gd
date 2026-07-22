extends GdUnitTestSuite
func test_default_authority() -> void:
	var a:=Authority.new(); assert_int(a.get_authority()).is_equal(1); assert_bool(a.is_server()).is_true(); a.queue_free()
func test_transfer() -> void:
	var a:=Authority.new(); var e:=false; a.authority_changed.connect(func(_id): e=true)
	a.transfer(3); assert_int(a.get_authority()).is_equal(3); assert_bool(e).is_true(); a.queue_free()

func test_edge_case_multiple_instances() -> void:
	var a := Authority.new()
	var b := Authority.new()
	assert_object(a).is_not_null()
	assert_object(b).is_not_null()
	a.queue_free()
	b.queue_free()
