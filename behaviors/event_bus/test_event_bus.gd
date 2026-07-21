## test_event_bus.gd — Testes do EventBus | GdUnit4.

extends GdUnitTestSuite

func _make_eb() -> EventBus: return EventBus.new()

func test_register_and_fire() -> void:
	var eb := _make_eb()
	var fired := false
	eb.register("test", func(_p): fired = true)
	eb.fire("test")
	assert_bool(fired).is_true()
	eb.queue_free()

func test_fire_with_payload() -> void:
	var eb := _make_eb()
	var received: Dictionary = {}
	eb.register("damage", func(p): received = p)
	eb.fire("damage", {"amount": 10, "type": "fire"})
	assert_int(received.get("amount", 0)).is_equal(10)
	assert_str(received.get("type", "")).is_equal("fire")
	eb.queue_free()

func test_multiple_listeners() -> void:
	var eb := _make_eb()
	var count := 0
	eb.register("tick", func(_p): count += 1)
	eb.register("tick", func(_p): count += 1)
	eb.fire("tick")
	assert_int(count).is_equal(2)
	eb.queue_free()

func test_unregister() -> void:
	var eb := _make_eb()
	var count := 0
	var cb := func(_p): count += 1
	eb.register("test", cb)
	eb.fire("test")
	assert_int(count).is_equal(1)
	eb.unregister("test", cb)
	eb.fire("test")
	assert_int(count).is_equal(1)  # não incrementou
	eb.queue_free()

func test_clear() -> void:
	var eb := _make_eb()
	eb.register("x", func(_p): pass)
	eb.register("y", func(_p): pass)
	eb.clear()
	assert_bool(eb.has_listeners("x")).is_false()
	assert_bool(eb.has_listeners("y")).is_false()
	eb.queue_free()

func test_has_listeners() -> void:
	var eb := _make_eb()
	assert_bool(eb.has_listeners("test")).is_false()
	eb.register("test", func(_p): pass)
	assert_bool(eb.has_listeners("test")).is_true()
	eb.queue_free()

func test_fire_unknown_event() -> void:
	var eb := _make_eb()
	# Não crasha com evento sem listeners
	eb.fire("unknown")
	assert_bool(true).is_true()
	eb.queue_free()

func test_event_fired_signal() -> void:
	var eb := _make_eb()
	var emitted := false
	eb.event_fired.connect(func(_n, _p): emitted = true)
	eb.fire("alerta", {"msg": "hello"})
	assert_bool(emitted).is_true()
	eb.queue_free()
