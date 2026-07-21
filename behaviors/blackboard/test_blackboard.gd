## test_blackboard.gd — Testes do Blackboard | GdUnit4.

extends GdUnitTestSuite

func _make_bb() -> Blackboard: return Blackboard.new()

func test_set_get() -> void:
	var bb := _make_bb()
	bb.set_var("score", 42)
	assert_int(bb.get_var("score")).is_equal(42)
	bb.queue_free()

func test_default_value() -> void:
	var bb := _make_bb()
	assert_int(bb.get_var("missing", -1)).is_equal(-1)
	bb.queue_free()

func test_has_var() -> void:
	var bb := _make_bb()
	assert_bool(bb.has_var("x")).is_false()
	bb.set_var("x", 1)
	assert_bool(bb.has_var("x")).is_true()
	bb.queue_free()

func test_erase_var() -> void:
	var bb := _make_bb()
	bb.set_var("x", 10)
	bb.erase_var("x")
	assert_bool(bb.has_var("x")).is_false()
	bb.queue_free()

func test_clear() -> void:
	var bb := _make_bb()
	bb.set_var("a", 1); bb.set_var("b", 2)
	bb.clear()
	assert_bool(bb.has_var("a")).is_false()
	assert_bool(bb.has_var("b")).is_false()
	bb.queue_free()

func test_var_set_signal() -> void:
	var bb := _make_bb()
	var emitted := false
	bb.var_set.connect(func(_k): emitted = true)
	bb.set_var("hp", 100)
	assert_bool(emitted).is_true()
	bb.queue_free()

func test_trigger() -> void:
	var bb := _make_bb()
	var received = null
	bb.set_trigger("health", func(val): received = val)
	bb.set_var("health", 75)
	assert_int(received).is_equal(75)
	bb.queue_free()

func test_trigger_activated_signal() -> void:
	var bb := _make_bb()
	var emitted := false
	bb.trigger_activated.connect(func(_k): emitted = true)
	bb.set_trigger("alerta", func(_v): pass)
	bb.set_var("alerta", true)
	assert_bool(emitted).is_true()
	bb.queue_free()

func test_same_value_no_signal() -> void:
	var bb := _make_bb()
	var emitted := false
	bb.var_set.connect(func(_k): emitted = true)
	bb.set_var("x", 5)  # first set → emit
	assert_bool(emitted).is_true()
	emitted = false
	bb.set_var("x", 5)  # same value → no emit
	assert_bool(emitted).is_false()
	bb.queue_free()

func test_overwrite_value() -> void:
	var bb := _make_bb()
	bb.set_var("x", 1)
	bb.set_var("x", 2)
	assert_int(bb.get_var("x")).is_equal(2)
	bb.queue_free()
