extends GdUnitTestSuite
func test_defaults() -> void: var h:=HighContrast.new(); h.queue_free()

func test_edge_case_zero() -> void:
	var c := HighContrast.new()
	c.contrast_level = 0.0
	# Nao deve crashar com valor zero
	c.queue_free()

func test_edge_case_extreme() -> void:
	var c := HighContrast.new()
	c.contrast_level = 999999.0
	# Nao deve crashar com valor extremo
	c.queue_free()
