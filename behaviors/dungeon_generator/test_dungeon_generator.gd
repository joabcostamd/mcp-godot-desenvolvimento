extends GdUnitTestSuite
func test_defaults() -> void: var o:=DungeonGenerator.new(); o.queue_free()

func test_edge_case_zero() -> void:
	var c := DungeonGenerator.new()
	c.room_count = 0
	# Nao deve crashar com valor zero
	c.queue_free()

func test_edge_case_extreme() -> void:
	var c := DungeonGenerator.new()
	c.room_count = 999999
	# Nao deve crashar com valor extremo
	c.queue_free()
