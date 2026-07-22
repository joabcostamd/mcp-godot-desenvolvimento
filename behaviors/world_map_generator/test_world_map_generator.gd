extends GdUnitTestSuite
func test_defaults() -> void: var o:=WorldMapGenerator.new(); o.queue_free()

func test_edge_case_zero() -> void:
	var c := WorldMapGenerator.new()
	c.width = 0
	# Nao deve crashar com valor zero
	c.queue_free()

func test_edge_case_extreme() -> void:
	var c := WorldMapGenerator.new()
	c.width = 999999
	# Nao deve crashar com valor extremo
	c.queue_free()
