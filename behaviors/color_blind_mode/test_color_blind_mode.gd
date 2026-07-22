extends GdUnitTestSuite
func test_defaults() -> void: var c:=ColorBlindMode.new(); assert_int(c.mode).is_equal(0); assert_float(c.intensity).is_equal(0.8); c.queue_free()

func test_edge_case_zero() -> void:
	var c := ColorBlindMode.new()
	c.mode = 0
	# Nao deve crashar com valor zero
	c.queue_free()

func test_edge_case_extreme() -> void:
	var c := ColorBlindMode.new()
	c.mode = 999999
	# Nao deve crashar com valor extremo
	c.queue_free()
