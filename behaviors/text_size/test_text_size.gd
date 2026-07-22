extends GdUnitTestSuite
func test_defaults() -> void: var t:=TextSize.new(); assert_float(t.scale_multiplier).is_equal(1.0); t.queue_free()

func test_edge_case_zero() -> void:
	var c := TextSize.new()
	c.scale_multiplier = 0.0
	# Nao deve crashar com valor zero
	c.queue_free()

func test_edge_case_extreme() -> void:
	var c := TextSize.new()
	c.scale_multiplier = 999999.0
	# Nao deve crashar com valor extremo
	c.queue_free()
