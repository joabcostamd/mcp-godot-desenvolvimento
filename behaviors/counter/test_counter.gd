## test_counter.gd — Testes do Counter | GdUnit4.

extends GdUnitTestSuite

func _make_c() -> Counter:
	return Counter.new()

func test_defaults() -> void:
	var c := _make_c()
	assert_int(c.initial_value).is_equal(0)
	assert_int(c.min_value).is_equal(0)
	assert_int(c.max_value).is_equal(0)
	assert_int(c.step).is_equal(1)
	c.queue_free()

func test_initial_value() -> void:
	var c := _make_c()
	c.initial_value = 5
	add_child(c)  # _ready runs
	assert_int(c.get_value()).is_equal(5)
	remove_child(c); c.queue_free()

func test_increment() -> void:
	var c := _make_c(); add_child(c)
	c.increment()
	assert_int(c.get_value()).is_equal(1)
	remove_child(c); c.queue_free()

func test_decrement() -> void:
	var c := _make_c(); c.initial_value = 5; add_child(c)
	c.decrement()
	assert_int(c.get_value()).is_equal(4)
	remove_child(c); c.queue_free()

func test_add() -> void:
	var c := _make_c(); add_child(c)
	c.add(7)
	assert_int(c.get_value()).is_equal(7)
	remove_child(c); c.queue_free()

func test_clamp_max() -> void:
	var c := _make_c(); c.max_value = 10; add_child(c)
	c.add(20)
	assert_int(c.get_value()).is_equal(10)
	remove_child(c); c.queue_free()

func test_clamp_min() -> void:
	var c := _make_c(); c.min_value = -5; add_child(c)
	c.add(-20)
	assert_int(c.get_value()).is_equal(-5)
	remove_child(c); c.queue_free()

func test_no_max_limit() -> void:
	var c := _make_c(); c.max_value = 0; add_child(c)
	c.add(99999)
	assert_int(c.get_value()).is_equal(99999)
	remove_child(c); c.queue_free()

func test_is_at_min() -> void:
	var c := _make_c(); c.min_value = 0; add_child(c)
	assert_bool(c.is_at_min()).is_true()
	c.increment()
	assert_bool(c.is_at_min()).is_false()
	remove_child(c); c.queue_free()

func test_is_at_max() -> void:
	var c := _make_c(); c.max_value = 5; add_child(c)
	assert_bool(c.is_at_max()).is_false()
	c.add(10)
	assert_bool(c.is_at_max()).is_true()
	remove_child(c); c.queue_free()

func test_value_changed_signal() -> void:
	var c := _make_c(); add_child(c)
	var emitted := false
	c.value_changed.connect(func(_n, _o): emitted = true)
	c.increment()
	assert_bool(emitted).is_true()
	remove_child(c); c.queue_free()

func test_max_reached_signal() -> void:
	var c := _make_c(); c.max_value = 3; add_child(c)
	var emitted := false
	c.max_reached.connect(func(): emitted = true)
	c.add(10)
	assert_bool(emitted).is_true()
	remove_child(c); c.queue_free()

func test_min_reached_signal() -> void:
	var c := _make_c(); c.min_value = -2; c.initial_value = 0; add_child(c)
	var emitted := false
	c.min_reached.connect(func(): emitted = true)
	c.add(-10)
	assert_bool(emitted).is_true()
	remove_child(c); c.queue_free()

func test_reset() -> void:
	var c := _make_c(); c.initial_value = 5; add_child(c)
	c.add(100)
	c.reset()
	assert_int(c.get_value()).is_equal(5)
	remove_child(c); c.queue_free()

func test_set_value() -> void:
	var c := _make_c(); add_child(c)
	c.set_value(42)
	assert_int(c.get_value()).is_equal(42)
	remove_child(c); c.queue_free()

func test_step_setter() -> void:
	var c := _make_c()
	c.step = 0
	assert_int(c.step).is_equal(1)
	c.step = 9999
	assert_int(c.step).is_equal(1000)
	c.queue_free()
