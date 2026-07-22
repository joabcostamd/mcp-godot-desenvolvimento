## test_xp_level.gd — Testes do behavior XPLevel | GdUnit4.

extends GdUnitTestSuite


func _make_xp_level(xp_table := [0, 100, 300, 600], xp := 0, level := 1) -> XPLevel:
	var x := XPLevel.new()
	x.xp_table = xp_table.duplicate()
	x.current_xp = xp
	x.current_level = level
	return x


# ── add_xp ────────────────────────────────────────────────────────────────────

func test_add_xp_basic() -> void:
	var x := _make_xp_level()
	add_child(x)
	var gained := x.add_xp(50)
	assert_int(gained).is_equal(0)
	assert_int(x.current_xp).is_equal(50)
	assert_int(x.current_level).is_equal(1)


func test_add_xp_levels_up() -> void:
	var x := _make_xp_level()
	add_child(x)
	var gained := x.add_xp(100)
	assert_int(gained).is_equal(1)
	assert_int(x.current_level).is_equal(2)


func test_add_xp_multiple_levels() -> void:
	var x := _make_xp_level([0, 50, 150])
	add_child(x)
	var gained := x.add_xp(200)
	assert_int(gained).is_equal(2)
	assert_int(x.current_level).is_equal(3)


func test_add_xp_zero_noop() -> void:
	var x := _make_xp_level()
	add_child(x)
	var gained := x.add_xp(0)
	assert_int(gained).is_equal(0)
	assert_int(x.current_xp).is_equal(0)


func test_add_xp_negative_noop() -> void:
	var x := _make_xp_level()
	add_child(x)
	var gained := x.add_xp(-10)
	assert_int(gained).is_equal(0)


func test_add_xp_emits_xp_gained() -> void:
	var x := _make_xp_level()
	add_child(x)
	var val := 0
	x.xp_gained.connect(func(v, _t): val = v)
	x.add_xp(75)
	assert_int(val).is_equal(75)


func test_add_xp_emits_leveled_up() -> void:
	var x := _make_xp_level()
	add_child(x)
	var new_lvl := 0
	x.leveled_up.connect(func(l): new_lvl = l)
	x.add_xp(100)
	assert_int(new_lvl).is_equal(2)


func test_add_xp_multiple_leveled_up_signals() -> void:
	var x := _make_xp_level([0, 50, 150])
	add_child(x)
	var levels := []
	x.leveled_up.connect(func(l): levels.append(l))
	x.add_xp(200)
	assert_int(levels.size()).is_equal(2)
	assert_int(levels[0]).is_equal(2)
	assert_int(levels[1]).is_equal(3)


# ── get_xp_to_next ────────────────────────────────────────────────────────────

func test_get_xp_to_next() -> void:
	var x := _make_xp_level([0, 100, 300])
	add_child(x)
	assert_int(x.get_xp_to_next()).is_equal(100)
	x.add_xp(80)
	assert_int(x.get_xp_to_next()).is_equal(20)


func test_get_xp_to_next_max_level() -> void:
	var x := _make_xp_level([0, 50])
	add_child(x)
	x.add_xp(100)
	assert_int(x.get_xp_to_next()).is_equal(-1)


# ── is_max_level ──────────────────────────────────────────────────────────────

func test_is_max_level_false() -> void:
	var x := _make_xp_level([0, 100, 300])
	add_child(x)
	assert_bool(x.is_max_level()).is_false()


func test_is_max_level_true() -> void:
	var x := _make_xp_level([0, 50])
	add_child(x)
	x.add_xp(100)
	assert_bool(x.is_max_level()).is_true()


func test_is_max_level_empty_table() -> void:
	var x := _make_xp_level([])
	add_child(x)
	assert_bool(x.is_max_level()).is_true()
	assert_int(x.get_xp_to_next()).is_equal(-1)
	assert_int(x.add_xp(100)).is_equal(0)


# ── Edge cases ────────────────────────────────────────────────────────────────

func test_xp_exact_threshold() -> void:
	var x := _make_xp_level([0, 100])
	add_child(x)
	var gained := x.add_xp(100)
	assert_int(gained).is_equal(1)
	assert_int(x.current_level).is_equal(2)


func test_xp_between_thresholds() -> void:
	var x := _make_xp_level([0, 100, 300])
	add_child(x)
	x.add_xp(250)
	assert_int(x.current_level).is_equal(2)
	assert_int(x.get_xp_to_next()).is_equal(50)


func test_add_xp_at_max_level() -> void:
	var x := _make_xp_level([0, 50])
	add_child(x)
	x.add_xp(100)  # atinge max level
	var gained := x.add_xp(50)  # mais XP, mas já no máximo
	assert_int(gained).is_equal(0)
	assert_int(x.current_xp).is_equal(150)
