extends GdUnitTestSuite
func test_defaults() -> void: var o:=HoldAlternative.new(); o.queue_free()

func test_edge_case_zero() -> void:
	var c := HoldAlternative.new()
	c.hold_threshold = 0.0
	# Nao deve crashar com valor zero
	c.queue_free()

func test_edge_case_extreme() -> void:
	var c := HoldAlternative.new()
	c.hold_threshold = 999999.0
	# Nao deve crashar com valor extremo
	c.queue_free()
