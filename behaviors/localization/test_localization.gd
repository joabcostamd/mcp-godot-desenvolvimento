extends GdUnitTestSuite
func test_defaults() -> void: var l:=Localization.new(); assert_str(l.locale).is_equal("en"); l.queue_free()
func test_set_locale() -> void: var l:=Localization.new(); var e:=false; l.locale_changed.connect(func(_x): e=true); l.set_locale("pt"); assert_bool(e).is_true(); l.queue_free()

func test_edge_case_multiple_instances() -> void:
	var a := Localization.new()
	var b := Localization.new()
	assert_object(a).is_not_null()
	assert_object(b).is_not_null()
	a.queue_free()
	b.queue_free()
