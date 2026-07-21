extends GdUnitTestSuite
func test_set() -> void: var s:=SteamInput.new(); var e:=false; s.action_set_changed.connect(func(_n): e=true); s.set_action_set("menu"); assert_bool(e).is_true(); s.queue_free()
