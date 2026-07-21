extends GdUnitTestSuite
func test_defaults() -> void:
	var r:=RPCBridge.new(); assert_bool(r.reliable).is_true(); assert_int(r.channel).is_equal(0); r.queue_free()
func test_send_emits_signal() -> void:
	var r:=RPCBridge.new(); var e:=false; r.rpc_sent.connect(func(_m): e=true); r.send_rpc("test"); assert_bool(e).is_true(); r.queue_free()
