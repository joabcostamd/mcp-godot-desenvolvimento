extends GdUnitTestSuite
func test_set() -> void: var s:=SteamInput.new(); var e:=false; s.action_set_changed.connect(func(_n): e=true); s.set_action_set("menu"); assert_bool(e).is_true(); s.queue_free()

func test_edge_case_multiple_instances() -> void:
	var a := SteamInput.new()
	var b := SteamInput.new()
	assert_object(a).is_not_null()
	assert_object(b).is_not_null()
	a.queue_free()
	b.queue_free()
