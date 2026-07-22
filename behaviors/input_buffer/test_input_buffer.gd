extends GdUnitTestSuite
func test_push_consume() -> void: var ib:=InputBuffer.new(); ib.push_action("punch"); assert_bool(ib.consume_action("punch")).is_true(); ib.queue_free()
func test_buffer_expires() -> void: var ib:=InputBuffer.new(); ib.buffer_window=0.01; ib.push_action("kick"); ib._process(1.0); assert_bool(ib.consume_action("kick")).is_false(); ib.queue_free()

func test_edge_case_zero() -> void:
	var c := InputBuffer.new()
	c.buffer_window = 0.0
	# Nao deve crashar com valor zero
	c.queue_free()

func test_edge_case_extreme() -> void:
	var c := InputBuffer.new()
	c.buffer_window = 999999.0
	# Nao deve crashar com valor extremo
	c.queue_free()
