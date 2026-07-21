extends GdUnitTestSuite
func test_show() -> void: var s:=Subtitle.new(); s.show_subtitle("test"); assert_bool(s._label.visible).is_true(); s.queue_free()
