extends GdUnitTestSuite
func test_add_item() -> void:
	var s:=Shop.new(); add_child(s); s.add_item("sword",100)
	assert_int(s.get_items().size()).is_equal(1); remove_child(s); s.queue_free()
