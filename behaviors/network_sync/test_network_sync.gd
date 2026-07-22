extends GdUnitTestSuite
func test_add_property() -> void:
	var ns:=NetworkSync.new(); ns.add_sync_property("position"); assert_int(ns.get_sync_properties().size()).is_equal(1); ns.queue_free()
func test_defaults() -> void:
	var ns:=NetworkSync.new(); assert_float(ns.sync_interval).is_equal(0.1); ns.queue_free()

func test_edge_case_zero() -> void:
	var c := NetworkSync.new()
	c.sync_interval = 0.0
	# Nao deve crashar com valor zero
	c.queue_free()

func test_edge_case_extreme() -> void:
	var c := NetworkSync.new()
	c.sync_interval = 999999.0
	# Nao deve crashar com valor extremo
	c.queue_free()
