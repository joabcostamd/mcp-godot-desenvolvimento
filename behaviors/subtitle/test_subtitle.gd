extends GdUnitTestSuite
func test_show() -> void: var s:=Subtitle.new(); s.show_subtitle("test"); assert_bool(s._label.visible).is_true(); s.queue_free()

func test_edge_case_zero() -> void:
	var c := Subtitle.new()
	c.duration = 0.0
	# Nao deve crashar com valor zero
	c.queue_free()

func test_edge_case_extreme() -> void:
	var c := Subtitle.new()
	c.duration = 999999.0
	# Nao deve crashar com valor extremo
	c.queue_free()
