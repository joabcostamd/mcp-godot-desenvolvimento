extends GdUnitTestSuite
func test_register_and_fire() -> void:
	var eb:=EventBus.new()
	var fired:=false
	eb.register("test",func(_p): fired=true)
	eb.fire("test")
	assert_bool(fired).is_true(); eb.queue_free()
func test_clear() -> void:
	var eb:=EventBus.new()
	eb.register("x",func(_p): pass); eb.clear()
	assert_bool(eb.has_listeners("x")).is_false(); eb.queue_free()
