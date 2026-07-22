## test_currency.gd — Testes do behavior Currency | GdUnit4.
##
## Cobre: add, spend, can_afford, get_amount, sinais, edge cases.
##
## Requer: GdUnit4 instalado como addon.

extends GdUnitTestSuite


# ── Helpers ───────────────────────────────────────────────────────────────────

func _make_currency(currency_type := "gold", amount := 0) -> Currency:
	var c := Currency.new()
	c.currency_type = currency_type
	c.amount = amount
	return c


# ── add ───────────────────────────────────────────────────────────────────────

func test_add_increases_amount() -> void:
	var c := _make_currency("gold", 0)
	add_child(c)
	c.add(100)
	assert_int(c.get_amount()).is_equal(100)


func test_add_multiple_times() -> void:
	var c := _make_currency("gold", 0)
	add_child(c)
	c.add(50)
	c.add(30)
	assert_int(c.get_amount()).is_equal(80)


func test_add_zero_is_noop() -> void:
	var c := _make_currency("gold", 50)
	add_child(c)
	c.add(0)
	assert_int(c.get_amount()).is_equal(50)


func test_add_negative_is_noop() -> void:
	var c := _make_currency("gold", 50)
	add_child(c)
	c.add(-10)
	assert_int(c.get_amount()).is_equal(50)


func test_add_emits_gained() -> void:
	var c := _make_currency("gold", 0)
	add_child(c)
	var captured_value := 0
	var captured_total := 0
	c.gained.connect(func(v, t):
		captured_value = v
		captured_total = t
	)
	c.add(75)
	assert_int(captured_value).is_equal(75)
	assert_int(captured_total).is_equal(75)


func test_add_zero_does_not_emit() -> void:
	var c := _make_currency("gold", 50)
	add_child(c)
	var emitted := false
	c.gained.connect(func(_v, _t): emitted = true)
	c.add(0)
	assert_bool(emitted).is_false()


# ── spend ─────────────────────────────────────────────────────────────────────

func test_spend_decreases_amount() -> void:
	var c := _make_currency("gold", 100)
	add_child(c)
	var result := c.spend(40)
	assert_bool(result).is_true()
	assert_int(c.get_amount()).is_equal(60)


func test_spend_exact_amount() -> void:
	var c := _make_currency("gold", 50)
	add_child(c)
	var result := c.spend(50)
	assert_bool(result).is_true()
	assert_int(c.get_amount()).is_equal(0)


func test_spend_more_than_available() -> void:
	var c := _make_currency("gold", 30)
	add_child(c)
	var result := c.spend(100)
	assert_bool(result).is_false()
	assert_int(c.get_amount()).is_equal(30)  # não mudou


func test_spend_zero_returns_true() -> void:
	var c := _make_currency("gold", 50)
	add_child(c)
	var result := c.spend(0)
	assert_bool(result).is_true()
	assert_int(c.get_amount()).is_equal(50)


func test_spend_negative_returns_false() -> void:
	var c := _make_currency("gold", 50)
	add_child(c)
	var result := c.spend(-10)
	assert_bool(result).is_false()


func test_spend_emits_spent() -> void:
	var c := _make_currency("gold", 100)
	add_child(c)
	var captured_value := 0
	var captured_total := 0
	c.spent.connect(func(v, t):
		captured_value = v
		captured_total = t
	)
	c.spend(30)
	assert_int(captured_value).is_equal(30)
	assert_int(captured_total).is_equal(70)


func test_spend_emits_insufficient() -> void:
	var c := _make_currency("gold", 10)
	add_child(c)
	var requested := 0
	var available := 0
	c.insufficient.connect(func(r, a):
		requested = r
		available = a
	)
	c.spend(50)
	assert_int(requested).is_equal(50)
	assert_int(available).is_equal(10)


# ── can_afford ────────────────────────────────────────────────────────────────

func test_can_afford_true() -> void:
	var c := _make_currency("gold", 100)
	add_child(c)
	assert_bool(c.can_afford(50)).is_true()
	assert_bool(c.can_afford(100)).is_true()


func test_can_afford_false() -> void:
	var c := _make_currency("gold", 10)
	add_child(c)
	assert_bool(c.can_afford(50)).is_false()


func test_can_afford_zero_or_negative() -> void:
	var c := _make_currency("gold", 0)
	add_child(c)
	assert_bool(c.can_afford(0)).is_true()
	assert_bool(c.can_afford(-5)).is_true()


# ── amount clamping ───────────────────────────────────────────────────────────

func test_amount_clamped_to_zero() -> void:
	var c := _make_currency("gold", 0)
	add_child(c)
	c.amount = -50
	assert_int(c.get_amount()).is_equal(0)


func test_amount_clamped_to_max() -> void:
	var c := _make_currency("gold", 0)
	add_child(c)
	c.amount = 9999999
	assert_int(c.get_amount()).is_equal(999999)


# ── Multiple currency types ───────────────────────────────────────────────────

func test_multiple_currencies_independent() -> void:
	var gold := _make_currency("gold", 100)
	var gems := _make_currency("gems", 50)
	var root := Node.new()
	add_child(root)
	root.add_child(gold)
	root.add_child(gems)
	gold.add(20)
	gems.spend(10)
	assert_int(gold.get_amount()).is_equal(120)
	assert_int(gems.get_amount()).is_equal(40)
	root.queue_free()
