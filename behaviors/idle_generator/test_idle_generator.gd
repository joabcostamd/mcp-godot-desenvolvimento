## test_idle_generator.gd — Testes do IdleGenerator | GdUnit4.

extends GdUnitTestSuite


func _make_gen() -> IdleGenerator:
	return IdleGenerator.new()


func _make_currency(initial_amount: int = 1000) -> Currency:
	var c := Currency.new()
	c.amount = initial_amount
	return c


# ---------------------------------------------------------------------------
# PRODUCTION
# ---------------------------------------------------------------------------

func test_initial_state() -> void:
	var gen := _make_gen()
	assert_int(gen.get_level()).is_equal(1)
	assert_float(gen.get_stored()).is_equal(0.0)
	assert_float(gen.get_current_rate()).is_equal(1.0)
	assert_float(gen.get_storage_ratio()).is_equal(0.0)
	gen.queue_free()


func test_collect_no_stored() -> void:
	var gen := _make_gen()
	assert_int(gen.collect()).is_equal(0)
	gen.queue_free()


func test_collect_with_currency() -> void:
	var parent := Node.new()
	var gen := _make_gen()
	var curr := _make_currency(0)
	parent.add_child(curr)
	parent.add_child(gen)

	# Simula acumulação manual
	gen._stored = 5.7
	var collected := gen.collect()
	assert_int(collected).is_equal(5)
	assert_int(curr.get_amount()).is_equal(5)
	assert_float(gen.get_stored()).is_equal(0.7)  # fração residual
	assert_bool(gen.get_stored() < 1.0).is_true()

	parent.queue_free()


func test_collect_without_currency() -> void:
	var gen := _make_gen()
	gen._stored = 10.0
	var collected := gen.collect()
	assert_int(collected).is_equal(10)  # coleta mesmo sem Currency
	assert_float(gen.get_stored()).is_equal(0.0)
	gen.queue_free()


func test_accumulation_over_time() -> void:
	var gen := _make_gen()
	gen.resource_per_second = 10.0
	gen._initialized = true  # simula _ready
	gen._physics_process(1.0)  # 1 segundo
	assert_float(gen.get_stored()).is_equal(10.0)
	gen.queue_free()


func test_accumulation_disabled() -> void:
	var gen := _make_gen()
	gen.enabled = false
	gen.resource_per_second = 10.0
	gen._initialized = true
	gen._physics_process(1.0)
	assert_float(gen.get_stored()).is_equal(0.0)
	gen.queue_free()


func test_accumulation_not_initialized() -> void:
	var gen := _make_gen()
	# _initialized = false (default)
	gen.resource_per_second = 10.0
	gen._physics_process(1.0)
	assert_float(gen.get_stored()).is_equal(0.0)
	gen.queue_free()


# ---------------------------------------------------------------------------
# STORAGE CAP
# ---------------------------------------------------------------------------

func test_storage_cap() -> void:
	var gen := _make_gen()
	gen.max_storage = 50.0
	gen.resource_per_second = 100.0
	gen._initialized = true
	gen._physics_process(1.0)
	assert_float(gen.get_stored()).is_equal(50.0)  # capped
	gen.queue_free()


func test_storage_full_signal() -> void:
	var gen := _make_gen()
	gen.max_storage = 10.0
	gen.resource_per_second = 100.0
	gen._initialized = true

	var emitted := false
	gen.storage_full.connect(func(): emitted = true)
	gen._physics_process(1.0)

	assert_bool(emitted).is_true()
	gen.queue_free()


func test_storage_ratio() -> void:
	var gen := _make_gen()
	gen.max_storage = 200.0
	gen._stored = 50.0
	assert_float(gen.get_storage_ratio()).is_equal(0.25)
	gen._stored = 200.0
	assert_float(gen.get_storage_ratio()).is_equal(1.0)
	gen.queue_free()


# ---------------------------------------------------------------------------
# UPGRADE
# ---------------------------------------------------------------------------

func test_upgrade_cost_formula() -> void:
	var gen := _make_gen()
	gen.upgrade_cost = 10
	gen.upgrade_cost_multiplier = 2.0

	assert_int(gen.get_upgrade_cost()).is_equal(10)  # level 1: 10 * 2^0
	gen._level = 2
	assert_int(gen.get_upgrade_cost()).is_equal(20)  # level 2: 10 * 2^1
	gen._level = 3
	assert_int(gen.get_upgrade_cost()).is_equal(40)  # level 3: 10 * 2^2
	gen.queue_free()


func test_upgrade_success() -> void:
	var parent := Node.new()
	var gen := _make_gen()
	var curr := _make_currency(100)
	parent.add_child(curr)
	parent.add_child(gen)

	assert_int(gen.get_level()).is_equal(1)
	assert_float(gen.get_current_rate()).is_equal(1.0)

	assert_bool(gen.upgrade()).is_true()
	assert_int(gen.get_level()).is_equal(2)
	assert_float(gen.get_current_rate()).is_equal(2.0)  # rate * 2^1

	parent.queue_free()


func test_upgrade_insufficient_funds() -> void:
	var parent := Node.new()
	var gen := _make_gen()
	var curr := _make_currency(5)  # precisa de 10
	parent.add_child(curr)
	parent.add_child(gen)

	assert_bool(gen.upgrade()).is_false()
	assert_int(gen.get_level()).is_equal(1)

	parent.queue_free()


func test_upgrade_no_currency() -> void:
	var gen := _make_gen()
	assert_bool(gen.upgrade()).is_false()
	gen.queue_free()


func test_upgrade_rate_scaling() -> void:
	var gen := _make_gen()
	gen.resource_per_second = 2.0
	gen.upgrade_rate_multiplier = 3.0

	assert_float(gen.get_current_rate()).is_equal(2.0)
	gen._level = 3
	assert_float(gen.get_current_rate()).is_equal(18.0)  # 2 * 3^2
	gen.queue_free()


# ---------------------------------------------------------------------------
# SIGNALS
# ---------------------------------------------------------------------------

func test_generated_signal() -> void:
	var parent := Node.new()
	var gen := _make_gen()
	var curr := _make_currency(0)
	parent.add_child(curr)
	parent.add_child(gen)

	var emitted := false
	var emitted_amount := 0
	gen.generated.connect(func(amt): emitted = true; emitted_amount = amt)

	gen._stored = 3.0
	gen.collect()

	assert_bool(emitted).is_true()
	assert_int(emitted_amount).is_equal(3)

	parent.queue_free()


func test_upgraded_signal() -> void:
	var parent := Node.new()
	var gen := _make_gen()
	var curr := _make_currency(100)
	parent.add_child(curr)
	parent.add_child(gen)

	var emitted := false
	var emitted_level := 0
	var emitted_rate := 0.0
	gen.upgraded.connect(func(lvl, rate): emitted = true; emitted_level = lvl; emitted_rate = rate)

	gen.upgrade()

	assert_bool(emitted).is_true()
	assert_int(emitted_level).is_equal(2)
	assert_float(emitted_rate).is_equal(2.0)

	parent.queue_free()


# ---------------------------------------------------------------------------
# EDGE CASES
# ---------------------------------------------------------------------------

func test_multiple_collects() -> void:
	var parent := Node.new()
	var gen := _make_gen()
	var curr := _make_currency(0)
	parent.add_child(curr)
	parent.add_child(gen)

	gen._stored = 15.7
	gen.collect()  # coleta 15, sobra 0.7
	assert_int(curr.get_amount()).is_equal(15)

	gen._stored += 4.3  # 0.7 + 4.3 = 5.0
	gen.collect()  # coleta 5
	assert_int(curr.get_amount()).is_equal(20)

	parent.queue_free()


func test_collect_fraction_only() -> void:
	var gen := _make_gen()
	gen._stored = 0.5
	assert_int(gen.collect()).is_equal(0)  # menos de 1, nada coletado
	assert_float(gen.get_stored()).is_equal(0.5)
	gen.queue_free()


func test_get_storage_ratio_zero_max() -> void:
	var gen := _make_gen()
	gen.max_storage = 0.0  # setter clampa pra 1.0 depois do export... mas vamos testar
	# O setter clampa, então max_storage nunca será 0
	assert_float(gen.get_storage_ratio()).is_equal(0.0)
	gen.queue_free()
