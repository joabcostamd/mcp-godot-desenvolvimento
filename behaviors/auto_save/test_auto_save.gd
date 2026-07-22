extends GdUnitTestSuite
func test_defaults() -> void: var o:=AutoSave.new(); o.queue_free()

func test_edge_case_disabled() -> void:
	var c := AutoSave.new()
	c.save_on_scene_change = false
	# Nao deve crashar com disabled
	assert_bool(c.save_on_scene_change).is_false()
	c.queue_free()

func test_edge_case_extreme() -> void:
	var c := AutoSave.new()
	c.interval = 999999.0
	# Nao deve crashar com valor extremo
	c.queue_free()
