## test_achievement.gd — Testes do behavior Achievement | GdUnit4.

extends GdUnitTestSuite


func _make_ach(achievements := []) -> Achievement:
	var a := Achievement.new()
	a.achievements = achievements.duplicate(true)
	return a


func _make_inv() -> Inventory:
	var i := Inventory.new(); i.slot_count = 10; return i


func _make_cur() -> Currency:
	var c := Currency.new(); c.amount = 0; return c


func _make_xp() -> XPLevel:
	return XPLevel.new()


func _sample() -> Array:
	return [{"id": "coll3", "name": "Collect 3", "condition": {"type": "collect", "target_id": "gem", "required": 3}}]


# ── Collect ───────────────────────────────────────────────────────────────────

func test_collect_achievement_unlocks() -> void:
	var r := Node.new(); add_child(r)
	var inv := _make_inv(); var ach := _make_ach(_sample())
	r.add_child(inv); r.add_child(ach)
	var unlocked := ""; ach.unlocked.connect(func(id): unlocked = id)
	inv.add_item("gem", 3)
	assert_str(unlocked).is_equal("coll3")
	assert_bool(ach.is_unlocked("coll3")).is_true()
	r.queue_free()


func test_collect_progress_partial() -> void:
	var r := Node.new(); add_child(r)
	var inv := _make_inv(); var ach := _make_ach(_sample())
	r.add_child(inv); r.add_child(ach)
	inv.add_item("gem", 2)
	var p := ach.get_progress("coll3")
	assert_int(p.current).is_equal(2)
	r.queue_free()


# ── Currency ──────────────────────────────────────────────────────────────────

func test_currency_achievement() -> void:
	var r := Node.new(); add_child(r)
	var cur := _make_cur(); var ach := _make_ach([{"id": "rich", "name": "Rich", "condition": {"type": "currency", "target_id": "", "required": 100}}])
	r.add_child(cur); r.add_child(ach)
	var unlocked := ""; ach.unlocked.connect(func(id): unlocked = id)
	cur.add(100)
	assert_str(unlocked).is_equal("rich")
	r.queue_free()


# ── Level ─────────────────────────────────────────────────────────────────────

func test_level_achievement() -> void:
	var r := Node.new(); add_child(r)
	var xp := _make_xp(); xp.xp_table = [0, 50]
	var ach := _make_ach([{"id": "lvl2", "name": "Level 2", "condition": {"type": "level", "target_id": "", "required": 2}}])
	r.add_child(xp); r.add_child(ach)
	var unlocked := ""; ach.unlocked.connect(func(id): unlocked = id)
	xp.add_xp(100)
	assert_str(unlocked).is_equal("lvl2")
	r.queue_free()


# ── Edge cases ────────────────────────────────────────────────────────────────

func test_empty_achievements_no_crash() -> void:
	var ach := _make_ach([]); add_child(ach)
	assert_bool(ach.is_unlocked("x")).is_false()


func test_progress_updated_signal() -> void:
	var r := Node.new(); add_child(r)
	var inv := _make_inv(); var ach := _make_ach(_sample())
	r.add_child(inv); r.add_child(ach)
	var prog_current := 0; ach.progress_updated.connect(func(_id, c, _r): prog_current = c)
	inv.add_item("gem", 1)
	assert_int(prog_current).is_equal(1)
	r.queue_free()


func test_unlocked_only_once() -> void:
	var r := Node.new(); add_child(r)
	var inv := _make_inv(); var ach := _make_ach(_sample())
	r.add_child(inv); r.add_child(ach)
	var count := 0; ach.unlocked.connect(func(_id): count += 1)
	inv.add_item("gem", 3); inv.add_item("gem", 5)
	assert_int(count).is_equal(1)
	r.queue_free()
