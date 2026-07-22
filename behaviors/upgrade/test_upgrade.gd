## test_upgrade.gd — Testes do behavior Upgrade | GdUnit4.

extends GdUnitTestSuite


func _make_upgrade(options := [], choices := 3) -> Upgrade:
	var u := Upgrade.new()
	u.upgrade_options = options.duplicate(true)
	u.choices_per_level = choices
	return u


func _make_xp_level() -> XPLevel:
	var x := XPLevel.new()
	x.xp_table = [0, 100]
	return x


func _sample_options() -> Array:
	return [
		{"id": "atk", "name": "Attack", "max_level": 5, "effects": [{"stat": "damage", "value": 10}]},
		{"id": "spd", "name": "Speed", "max_level": 3, "effects": [{"stat": "speed", "value": 5}]},
		{"id": "hp", "name": "Health", "max_level": 5, "effects": [{"stat": "max_hp", "value": 20}]},
	]


# ── Choices ───────────────────────────────────────────────────────────────────

func test_force_choices_generates_options() -> void:
	var u := _make_upgrade(_sample_options(), 2)
	add_child(u)
	u.force_choices()
	var choices := u.get_pending_choices()
	assert_int(choices.size()).is_equal(2)


func test_force_choices_respects_choices_per_level() -> void:
	var u := _make_upgrade(_sample_options(), 1)
	add_child(u)
	u.force_choices()
	assert_int(u.get_pending_choices().size()).is_equal(1)


func test_empty_options_no_choices() -> void:
	var u := _make_upgrade([], 3)
	add_child(u)
	u.force_choices()
	assert_int(u.get_pending_choices().size()).is_equal(0)


func test_choices_ready_signal() -> void:
	var u := _make_upgrade(_sample_options(), 2)
	add_child(u)
	var emitted := false
	u.choices_ready.connect(func(_o): emitted = true)
	u.force_choices()
	assert_bool(emitted).is_true()


# ── apply_upgrade ─────────────────────────────────────────────────────────────

func test_apply_upgrade_success() -> void:
	var u := _make_upgrade(_sample_options(), 3)
	add_child(u)
	u.force_choices()
	var result := u.apply_upgrade(0)
	assert_bool(result).is_true()
	var choices := u.get_pending_choices()
	assert_int(choices.size()).is_equal(0)  # limpa após aplicar


func test_apply_upgrade_increments_level() -> void:
	var u := _make_upgrade(_sample_options(), 3)
	add_child(u)
	u.force_choices()
	var choices := u.get_pending_choices()
	var chosen_id := (choices[0] as Dictionary).get("id", "") as String
	u.apply_upgrade(0)
	assert_int(u.get_upgrade_level(chosen_id)).is_equal(1)
	# Segundo level up — mesmo upgrade deve aparecer se não max
	u.force_choices()
	u.apply_upgrade(0)
	assert_int(u.get_upgrade_level(chosen_id)).is_equal(2)


func test_apply_upgrade_invalid_index() -> void:
	var u := _make_upgrade(_sample_options(), 2)
	add_child(u)
	u.force_choices()
	assert_bool(u.apply_upgrade(-1)).is_false()
	assert_bool(u.apply_upgrade(99)).is_false()


func test_apply_upgrade_emits_signal() -> void:
	var u := _make_upgrade(_sample_options(), 3)
	add_child(u)
	u.force_choices()
	var captured_id := ""
	var captured_lvl := 0
	u.upgrade_applied.connect(func(id, lvl):
		captured_id = id
		captured_lvl = lvl
	)
	u.apply_upgrade(0)
	assert_str(captured_id).is_not_equal("")
	assert_int(captured_lvl).is_equal(1)


# ── Max level ─────────────────────────────────────────────────────────────────

func test_max_level_not_in_choices() -> void:
	var opts := [{"id": "only", "name": "Only", "max_level": 1, "effects": []}]
	var u := _make_upgrade(opts, 3)
	add_child(u)
	u.force_choices()
	assert_int(u.get_pending_choices().size()).is_equal(1)
	u.apply_upgrade(0)
	u.force_choices()
	assert_int(u.get_pending_choices().size()).is_equal(0)  # maximizado


# ── XPLevel integration ───────────────────────────────────────────────────────

func test_connects_to_sibling_xp_level() -> void:
	var root := Node.new()
	add_child(root)
	var xp := _make_xp_level()
	var up := _make_upgrade(_sample_options(), 2)
	root.add_child(xp)
	root.add_child(up)
	var emitted := false
	up.choices_ready.connect(func(_o): emitted = true)
	xp.add_xp(100)
	assert_bool(emitted).is_true()
	root.queue_free()


func test_no_xp_level_no_crash() -> void:
	var u := _make_upgrade(_sample_options(), 2)
	add_child(u)
	u.force_choices()
	assert_int(u.get_pending_choices().size()).is_greater(0)
