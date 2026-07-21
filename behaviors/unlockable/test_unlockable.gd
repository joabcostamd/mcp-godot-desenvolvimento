## test_unlockable.gd — Testes do behavior Unlockable | GdUnit4.

extends GdUnitTestSuite


func _make_unl(unlocks := []) -> Unlockable:
	var u := Unlockable.new(); u.unlocks = unlocks.duplicate(true); return u
func _make_ach() -> Achievement:
	var a := Achievement.new(); a.achievements = [{"id": "a1", "name": "", "condition": {"type": "collect", "target_id": "gem", "required": 1}}]; return a
func _make_inv() -> Inventory:
	var i := Inventory.new(); i.slot_count = 10; return i
func _make_xp() -> XPLevel:
	return XPLevel.new()
func _make_cur() -> Currency:
	return Currency.new()


# ── Achievement condition ─────────────────────────────────────────────────────

func test_unlock_by_achievement() -> void:
	var r := Node.new(); add_child(r)
	var ach := _make_ach(); var inv := _make_inv(); var unl := _make_unl([{"id": "u1", "name": "", "conditions": [{"type": "achievement", "target_id": "a1", "required": 1}]}])
	r.add_child(inv); r.add_child(ach); r.add_child(unl)
	var unlocked := ""; unl.unlocked.connect(func(id): unlocked = id)
	inv.add_item("gem", 1)
	assert_str(unlocked).is_equal("u1")
	r.queue_free()


# ── Level condition ───────────────────────────────────────────────────────────

func test_unlock_by_level() -> void:
	var r := Node.new(); add_child(r)
	var xp := _make_xp(); xp.xp_table = [0, 50]
	var unl := _make_unl([{"id": "u2", "name": "", "conditions": [{"type": "level", "target_id": "", "required": 2}]}])
	r.add_child(xp); r.add_child(unl)
	var unlocked := ""; unl.unlocked.connect(func(id): unlocked = id)
	xp.add_xp(100)
	assert_str(unlocked).is_equal("u2")
	r.queue_free()


# ── Currency condition ────────────────────────────────────────────────────────

func test_unlock_by_currency() -> void:
	var r := Node.new(); add_child(r)
	var cur := _make_cur(); cur.amount = 0
	var unl := _make_unl([{"id": "u3", "name": "", "conditions": [{"type": "currency", "target_id": "", "required": 200}]}])
	r.add_child(cur); r.add_child(unl)
	var unlocked := ""; unl.unlocked.connect(func(id): unlocked = id)
	cur.add(200)
	assert_str(unlocked).is_equal("u3")
	r.queue_free()


# ── Multiple conditions ───────────────────────────────────────────────────────

func test_unlock_all_conditions_required() -> void:
	var r := Node.new(); add_child(r)
	var xp := _make_xp(); xp.xp_table = [0, 50]; xp.add_xp(100)
	var cur := _make_cur(); cur.add(200)
	var unl := _make_unl([{"id": "u4", "name": "", "conditions": [{"type": "level", "target_id": "", "required": 2}, {"type": "currency", "target_id": "", "required": 100}]}])
	r.add_child(xp); r.add_child(cur); r.add_child(unl)
	assert_bool(unl.is_unlocked("u4")).is_true()
	r.queue_free()


# ── Edge cases ────────────────────────────────────────────────────────────────

func test_unlocked_only_once() -> void:
	var r := Node.new(); add_child(r)
	var xp := _make_xp(); xp.xp_table = [0, 10]
	var unl := _make_unl([{"id": "u5", "name": "", "conditions": [{"type": "level", "target_id": "", "required": 2}]}])
	r.add_child(xp); r.add_child(unl)
	var count := 0; unl.unlocked.connect(func(_id): count += 1)
	xp.add_xp(10); xp.add_xp(999)
	assert_int(count).is_equal(1)
	r.queue_free()


func test_empty_unlocks_no_crash() -> void:
	var u := _make_unl([]); add_child(u)
	assert_bool(u.is_unlocked("x")).is_false()
