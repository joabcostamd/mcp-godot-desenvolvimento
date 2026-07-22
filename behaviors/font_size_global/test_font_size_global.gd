extends GdUnitTestSuite
func test_defaults() -> void: var o:=FontSizeGlobal.new(); o.queue_free()

func test_edge_case_zero() -> void:
	var c := FontSizeGlobal.new()
	c.scale = 0.0
	# Nao deve crashar com valor zero
	c.queue_free()

func test_edge_case_extreme() -> void:
	var c := FontSizeGlobal.new()
	c.scale = 999999.0
	# Nao deve crashar com valor extremo
	c.queue_free()
