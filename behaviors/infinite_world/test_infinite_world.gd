extends GdUnitTestSuite
func test_defaults() -> void: var o:=InfiniteWorld.new(); o.queue_free()

func test_edge_case_zero() -> void:
	var c := InfiniteWorld.new()
	c.chunk_size = 0
	# Nao deve crashar com valor zero
	c.queue_free()

func test_edge_case_extreme() -> void:
	var c := InfiniteWorld.new()
	c.chunk_size = 999999
	# Nao deve crashar com valor extremo
	c.queue_free()
