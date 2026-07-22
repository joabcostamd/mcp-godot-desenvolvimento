extends GdUnitTestSuite
func test_defaults() -> void: var o:=NoiseGenerator.new(); o.queue_free()

func test_edge_case_zero() -> void:
	var c := NoiseGenerator.new()
	c.frequency = 0.0
	# Nao deve crashar com valor zero
	c.queue_free()

func test_edge_case_extreme() -> void:
	var c := NoiseGenerator.new()
	c.frequency = 999999.0
	# Nao deve crashar com valor extremo
	c.queue_free()
