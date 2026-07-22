extends GdUnitTestSuite
func test_defaults() -> void:
	var r:=RPCBridge.new(); assert_bool(r.reliable).is_true(); assert_int(r.channel).is_equal(0); r.queue_free()
func test_send_emits_signal() -> void:
	var r:=RPCBridge.new(); var e:=false; r.rpc_sent.connect(func(_m): e=true); r.send_rpc("test"); assert_bool(e).is_true(); r.queue_free()

func test_edge_case_disabled() -> void:
	var c := RpcBridge.new()
	c.reliable = false
	# Nao deve crashar com disabled
	assert_bool(c.reliable).is_false()
	c.queue_free()

func test_edge_case_extreme() -> void:
	var c := RpcBridge.new()
	c.channel = 999999
	# Nao deve crashar com valor extremo
	c.queue_free()
