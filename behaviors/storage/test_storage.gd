extends GdUnitTestSuite
func test_defaults() -> void:
	var s:=Storage.new(); assert_str(s.file_path).is_equal("user://storage.cfg"); s.queue_free()
func test_set_get() -> void:
	var s:=Storage.new(); add_child(s); s.set_data("hp",100)
	assert_int(s.get_data("hp",0)).is_equal(100); remove_child(s); s.queue_free()
