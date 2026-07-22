## test_save_load.gd — Testes do behavior SaveLoad | GdUnit4.

extends GdUnitTestSuite


func _make_save_load() -> SaveLoad:
	return SaveLoad.new()


func _make_inventory(slots := 10) -> Inventory:
	var inv := Inventory.new()
	inv.slot_count = slots
	return inv


func _make_currency(ctype := "gold", amount := 0) -> Currency:
	var c := Currency.new()
	c.currency_type = ctype
	c.amount = amount
	return c


func _make_xp_level() -> XPLevel:
	return XPLevel.new()


# ── Save/Load Inventory ───────────────────────────────────────────────────────

func test_save_load_inventory() -> void:
	var root := Node.new()
	add_child(root)
	var sl := _make_save_load()
	var inv := _make_inventory()
	root.add_child(inv)
	root.add_child(sl)
	inv.add_item("sword", 3)
	inv.add_item("potion", 5)
	assert_bool(sl.save("test_inv")).is_true()
	inv.clear()
	assert_int(inv.get_item_count("sword")).is_equal(0)
	assert_bool(sl.load("test_inv")).is_true()
	assert_int(inv.get_item_count("sword")).is_equal(3)
	assert_int(inv.get_item_count("potion")).is_equal(5)
	sl.delete_save("test_inv")
	root.queue_free()


# ── Save/Load Currency ────────────────────────────────────────────────────────

func test_save_load_currency() -> void:
	var root := Node.new()
	add_child(root)
	var sl := _make_save_load()
	var cur := _make_currency("gems", 500)
	root.add_child(cur)
	root.add_child(sl)
	assert_bool(sl.save("test_cur")).is_true()
	cur.amount = 0
	assert_bool(sl.load("test_cur")).is_true()
	assert_int(cur.get_amount()).is_equal(500)
	sl.delete_save("test_cur")
	root.queue_free()


# ── Save/Load XPLevel ─────────────────────────────────────────────────────────

func test_save_load_xp_level() -> void:
	var root := Node.new()
	add_child(root)
	var sl := _make_save_load()
	var xp := _make_xp_level()
	xp.xp_table = [0, 100, 300]
	root.add_child(xp)
	root.add_child(sl)
	xp.add_xp(150)
	assert_int(xp.current_level).is_equal(2)
	assert_bool(sl.save("test_xp")).is_true()
	xp.current_level = 1
	xp.current_xp = 0
	assert_bool(sl.load("test_xp")).is_true()
	assert_int(xp.current_level).is_equal(2)
	assert_int(xp.current_xp).is_equal(150)
	sl.delete_save("test_xp")
	root.queue_free()


# ── has_save / delete_save ────────────────────────────────────────────────────

func test_has_save() -> void:
	var sl := _make_save_load()
	add_child(sl)
	assert_bool(sl.has_save("nonexistent")).is_false()
	sl.save("test_has")
	assert_bool(sl.has_save("test_has")).is_true()
	sl.delete_save("test_has")


func test_delete_save() -> void:
	var sl := _make_save_load()
	add_child(sl)
	sl.save("test_del")
	assert_bool(sl.has_save("test_del")).is_true()
	assert_bool(sl.delete_save("test_del")).is_true()
	assert_bool(sl.has_save("test_del")).is_false()


func test_delete_nonexistent_returns_false() -> void:
	var sl := _make_save_load()
	add_child(sl)
	assert_bool(sl.delete_save("ghost")).is_false()


# ── Edge cases ────────────────────────────────────────────────────────────────

func test_load_nonexistent_returns_false() -> void:
	var sl := _make_save_load()
	add_child(sl)
	assert_bool(sl.load("ghost_slot")).is_false()


func test_save_empty_slot_returns_false() -> void:
	var sl := _make_save_load()
	add_child(sl)
	assert_bool(sl.save("")).is_false()


func test_saved_signal() -> void:
	var sl := _make_save_load()
	add_child(sl)
	var emitted := ""
	sl.saved.connect(func(s): emitted = s)
	sl.save("test_sig")
	assert_str(emitted).is_equal("test_sig")
	sl.delete_save("test_sig")


func test_loaded_signal() -> void:
	var root := Node.new()
	add_child(root)
	var sl := _make_save_load()
	var inv := _make_inventory()
	root.add_child(inv)
	root.add_child(sl)
	sl.save("test_ld_sig")
	var emitted := ""
	sl.loaded.connect(func(s): emitted = s)
	sl.load("test_ld_sig")
	assert_str(emitted).is_equal("test_ld_sig")
	sl.delete_save("test_ld_sig")
	root.queue_free()


func test_get_save_slots() -> void:
	var sl := _make_save_load()
	add_child(sl)
	sl.save("slot_a")
	sl.save("slot_b")
	var slots := sl.get_save_slots()
	assert_bool(slots.has("slot_a")).is_true()
	assert_bool(slots.has("slot_b")).is_true()
	sl.delete_save("slot_a")
	sl.delete_save("slot_b")
