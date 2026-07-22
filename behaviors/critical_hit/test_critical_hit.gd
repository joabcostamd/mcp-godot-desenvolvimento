## test_critical_hit.gd — Testes do behavior CriticalHit | GdUnit4.
##
## Cobre: try_critical, chance 0/1, sinais, is_critical, roll, warnings.

extends GdUnitTestSuite


# ── try_critical ─────────────────────────────────────────────────────────────

func test_never_crits_with_zero_chance() -> void:
	var ch := _make_crit(0.0, 2.0)
	for i in 100:
		var result := ch.try_critical(10)
		assert_int(result).is_equal(10)
		assert_bool(ch.is_critical()).is_false()


func test_always_crits_with_full_chance() -> void:
	var ch := _make_crit(1.0, 3.0)
	for i in 10:
		var result := ch.try_critical(10)
		assert_int(result).is_equal(30)  # 10 * 3
		assert_bool(ch.is_critical()).is_true()


func test_always_crits_with_multiplier_1_5() -> void:
	var ch := _make_crit(1.0, 1.5)
	var result := ch.try_critical(20)
	assert_int(result).is_equal(30)  # ceil(20 * 1.5) = 30


func test_damage_zero_does_not_crit() -> void:
	var ch := _make_crit(1.0, 5.0)
	var result := ch.try_critical(0)
	assert_int(result).is_equal(0)
	assert_bool(ch.is_critical()).is_false()


func test_damage_negative_does_not_crit() -> void:
	var ch := _make_crit(1.0, 5.0)
	var result := ch.try_critical(-10)
	assert_int(result).is_equal(-10)


# ── Sinais ───────────────────────────────────────────────────────────────────

func test_crit_landed_emitted() -> void:
	var ch := _make_crit(1.0, 2.0)
	var signal_fired := false
	var captured_damage := 0
	ch.crit_landed.connect(func(dmg):
		signal_fired = true
		captured_damage = dmg
	)

	ch.try_critical(25)
	assert_bool(signal_fired).is_true()
	assert_int(captured_damage).is_equal(50)


func test_crit_landed_not_emitted_without_crit() -> void:
	var ch := _make_crit(0.0, 2.0)
	var signal_fired := false
	ch.crit_landed.connect(func(_dmg): signal_fired = true)

	ch.try_critical(25)
	assert_bool(signal_fired).is_false()


# ── is_critical ──────────────────────────────────────────────────────────────

func test_is_critical_false_before_first_roll() -> void:
	var ch := _make_crit(0.5, 2.0)
	assert_bool(ch.is_critical()).is_false()


# ── roll ─────────────────────────────────────────────────────────────────────

func test_roll_with_full_chance() -> void:
	var ch := _make_crit(1.0, 2.0)
	var signal_fired := false
	ch.crit_landed.connect(func(_d): signal_fired = true)

	var result := ch.roll()
	assert_bool(result).is_true()
	assert_bool(ch.is_critical()).is_true()
	# roll() não deve emitir crit_landed
	assert_bool(signal_fired).is_false()


# ── Setters ──────────────────────────────────────────────────────────────────

func test_crit_chance_clamped() -> void:
	var ch := _make_crit(0.5, 2.0)
	ch.crit_chance = -1.0
	assert_float(ch.crit_chance).is_equal(0.0)
	ch.crit_chance = 999.0
	assert_float(ch.crit_chance).is_equal(1.0)


func test_crit_multiplier_clamped() -> void:
	var ch := _make_crit(0.5, 2.0)
	ch.crit_multiplier = 0.0
	assert_float(ch.crit_multiplier).is_equal(1.0)


# ── Warnings ─────────────────────────────────────────────────────────────────

func test_warning_chance_zero() -> void:
	var ch := _make_crit(0.0, 2.0)
	var warnings := ch._get_configuration_warnings()
	var found := false
	for w in warnings:
		if "crit_chance" in w:
			found = true
			break
	assert_bool(found).is_true()


func test_no_warning_when_valid() -> void:
	var ch := _make_crit(0.2, 2.5)
	var warnings := ch._get_configuration_warnings()
	assert_bool(warnings.size()).is_equal(0)


# ── Helpers ──────────────────────────────────────────────────────────────────

func _make_crit(chance: float, mult: float) -> CriticalHit:
	var ch := CriticalHit.new()
	ch.crit_chance = chance
	ch.crit_multiplier = mult
	return ch
