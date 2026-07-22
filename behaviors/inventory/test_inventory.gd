## test_inventory.gd — Testes do behavior Inventory | GdUnit4.
##
## Cobre: add_item, remove_item, has_item, get_item_count, is_full, clear,
##        sinais, max_stack, slot_count, edge cases.
##
## Requer: GdUnit4 instalado como addon.
## Executar: GdUnit4 > Run Tests na cena behaviors/inventory/test_inventory.gd

extends GdUnitTestSuite


# ── Helpers ───────────────────────────────────────────────────────────────────

func _make_inventory(slot_count := 20, max_stack := 99) -> Inventory:
	var inv := Inventory.new()
	inv.slot_count = slot_count
	inv.max_stack = max_stack
	return inv


# ── add_item ──────────────────────────────────────────────────────────────────

func test_add_item_basic() -> void:
	var inv := _make_inventory()
	add_child(inv)
	var added := inv.add_item("sword", 1)
	assert_int(added).is_equal(1)
	assert_int(inv.get_item_count("sword")).is_equal(1)
	assert_bool(inv.has_item("sword")).is_true()


func test_add_item_multiple() -> void:
	var inv := _make_inventory()
	add_child(inv)
	var added := inv.add_item("potion", 5)
	assert_int(added).is_equal(5)
	assert_int(inv.get_item_count("potion")).is_equal(5)


func test_add_item_stacks_in_same_slot() -> void:
	var inv := _make_inventory(20, 99)
	add_child(inv)
	inv.add_item("arrow", 30)
	inv.add_item("arrow", 30)
	assert_int(inv.get_item_count("arrow")).is_equal(60)
	# Deve ocupar apenas 1 slot (max_stack=99)
	var slots := inv.get_slots()
	var arrow_slots := 0
	for s in slots:
		if s.id == "arrow":
			arrow_slots += 1
	assert_int(arrow_slots).is_equal(1)


func test_add_item_spills_to_new_slot_when_stack_full() -> void:
	var inv := _make_inventory(20, 10)
	add_child(inv)
	var added := inv.add_item("gem", 15)
	assert_int(added).is_equal(15)
	assert_int(inv.get_item_count("gem")).is_equal(15)
	# Deve ocupar 2 slots: 10 + 5
	var slots := inv.get_slots()
	var gem_slots := 0
	for s in slots:
		if s.id == "gem":
			gem_slots += 1
	assert_int(gem_slots).is_equal(2)


func test_add_item_zero_does_nothing() -> void:
	var inv := _make_inventory()
	add_child(inv)
	var added := inv.add_item("sword", 0)
	assert_int(added).is_equal(0)
	assert_int(inv.get_item_count("sword")).is_equal(0)


func test_add_item_negative_does_nothing() -> void:
	var inv := _make_inventory()
	add_child(inv)
	var added := inv.add_item("sword", -5)
	assert_int(added).is_equal(0)


func test_add_item_empty_id_does_nothing() -> void:
	var inv := _make_inventory()
	add_child(inv)
	var added := inv.add_item("", 10)
	assert_int(added).is_equal(0)


func test_add_item_fills_empty_slots_first() -> void:
	var inv := _make_inventory(5, 10)
	add_child(inv)
	inv.add_item("a", 10)  # slot 0: 10/10 (cheio)
	inv.add_item("b", 5)   # slot 1: 5/10
	inv.add_item("a", 3)   # deve ir para slot 2 (novo), não slot 1 (tem b)
	assert_int(inv.get_item_count("a")).is_equal(13)
	var slots := inv.get_slots()
	assert_int(slots[0].quantity).is_equal(10)
	assert_int(slots[2].quantity).is_equal(3)


# ── remove_item ───────────────────────────────────────────────────────────────

func test_remove_item_basic() -> void:
	var inv := _make_inventory()
	add_child(inv)
	inv.add_item("sword", 5)
	var removed := inv.remove_item("sword", 3)
	assert_int(removed).is_equal(3)
	assert_int(inv.get_item_count("sword")).is_equal(2)


func test_remove_item_more_than_available() -> void:
	var inv := _make_inventory()
	add_child(inv)
	inv.add_item("sword", 3)
	var removed := inv.remove_item("sword", 10)
	assert_int(removed).is_equal(3)
	assert_int(inv.get_item_count("sword")).is_equal(0)


func test_remove_item_not_found() -> void:
	var inv := _make_inventory()
	add_child(inv)
	var removed := inv.remove_item("nonexistent", 1)
	assert_int(removed).is_equal(0)


func test_remove_item_zero_does_nothing() -> void:
	var inv := _make_inventory()
	add_child(inv)
	inv.add_item("sword", 5)
	var removed := inv.remove_item("sword", 0)
	assert_int(removed).is_equal(0)
	assert_int(inv.get_item_count("sword")).is_equal(5)


func test_remove_item_clears_slot_when_empty() -> void:
	var inv := _make_inventory(5, 99)
	add_child(inv)
	inv.add_item("gem", 10)
	inv.remove_item("gem", 10)
	assert_int(inv.get_item_count("gem")).is_equal(0)
	assert_int(inv.get_free_slot()).is_equal(0)  # slot 0 ficou livre


# ── is_full / get_free_slot ───────────────────────────────────────────────────

func test_is_full_false_initially() -> void:
	var inv := _make_inventory(5, 99)
	add_child(inv)
	assert_bool(inv.is_full()).is_false()


func test_is_full_when_all_slots_occupied() -> void:
	var inv := _make_inventory(3, 1)
	add_child(inv)
	inv.add_item("a", 1)  # slot 0
	inv.add_item("b", 1)  # slot 1
	inv.add_item("c", 1)  # slot 2
	assert_bool(inv.is_full()).is_true()
	assert_int(inv.get_free_slot()).is_equal(-1)


func test_get_free_slot_returns_first_empty() -> void:
	var inv := _make_inventory(5, 99)
	add_child(inv)
	inv.add_item("a", 1)  # slot 0 ocupado
	inv.add_item("b", 1)  # slot 1 ocupado
	assert_int(inv.get_free_slot()).is_equal(2)


# ── Sinais ────────────────────────────────────────────────────────────────────

func test_item_added_signal() -> void:
	var inv := _make_inventory()
	add_child(inv)
	var captured_id := ""
	var captured_qty := 0
	var captured_slot := -1
	inv.item_added.connect(func(id, qty, slot):
		captured_id = id
		captured_qty = qty
		captured_slot = slot
	)
	inv.add_item("sword", 3)
	assert_str(captured_id).is_equal("sword")
	assert_int(captured_qty).is_equal(3)
	assert_int(captured_slot).is_equal(0)


func test_item_removed_signal() -> void:
	var inv := _make_inventory()
	add_child(inv)
	inv.add_item("sword", 5)
	var captured_id := ""
	var captured_qty := 0
	inv.item_removed.connect(func(id, qty, _slot):
		captured_id = id
		captured_qty = qty
	)
	inv.remove_item("sword", 2)
	assert_str(captured_id).is_equal("sword")
	assert_int(captured_qty).is_equal(2)


func test_inventory_full_signal() -> void:
	var inv := _make_inventory(1, 1)
	add_child(inv)
	inv.add_item("a", 1)  # lota o único slot
	var full_emitted := false
	inv.inventory_full.connect(func(): full_emitted = true)
	var added := inv.add_item("b", 1)
	assert_int(added).is_equal(0)
	assert_bool(full_emitted).is_true()


# ── clear ─────────────────────────────────────────────────────────────────────

func test_clear_empties_inventory() -> void:
	var inv := _make_inventory(5, 99)
	add_child(inv)
	inv.add_item("a", 10)
	inv.add_item("b", 20)
	inv.clear()
	assert_int(inv.get_item_count("a")).is_equal(0)
	assert_int(inv.get_item_count("b")).is_equal(0)
	assert_bool(inv.is_full()).is_false()


func test_clear_on_empty_inventory() -> void:
	var inv := _make_inventory()
	add_child(inv)
	inv.clear()  # não deve crashar
	assert_bool(inv.is_full()).is_false()


# ── has_item ──────────────────────────────────────────────────────────────────

func test_has_item_true() -> void:
	var inv := _make_inventory()
	add_child(inv)
	inv.add_item("key", 2)
	assert_bool(inv.has_item("key")).is_true()
	assert_bool(inv.has_item("key", 2)).is_true()
	assert_bool(inv.has_item("key", 3)).is_false()


func test_has_item_false_for_missing() -> void:
	var inv := _make_inventory()
	add_child(inv)
	assert_bool(inv.has_item("ghost")).is_false()


# ── Edge cases ────────────────────────────────────────────────────────────────

func test_add_item_to_full_inventory_returns_zero() -> void:
	var inv := _make_inventory(2, 1)
	add_child(inv)
	inv.add_item("a", 1)
	inv.add_item("b", 1)
	var added := inv.add_item("c", 1)
	assert_int(added).is_equal(0)


func test_add_item_partial_fill_when_near_full() -> void:
	var inv := _make_inventory(2, 5)
	add_child(inv)
	inv.add_item("a", 5)  # slot 0 cheio
	inv.add_item("b", 3)  # slot 1: 3/5
	var added := inv.add_item("c", 10)
	assert_int(added).is_equal(2)  # só cabem 2 no slot 1 (5-3=2)
	assert_int(inv.get_item_count("c")).is_equal(2)


func test_multiple_items_different_ids() -> void:
	var inv := _make_inventory(10, 99)
	add_child(inv)
	inv.add_item("sword", 1)
	inv.add_item("shield", 1)
	inv.add_item("potion", 5)
	assert_int(inv.get_item_count("sword")).is_equal(1)
	assert_int(inv.get_item_count("shield")).is_equal(1)
	assert_int(inv.get_item_count("potion")).is_equal(5)


func test_slot_count_change_preserves_items() -> void:
	var inv := _make_inventory(5, 99)
	add_child(inv)
	inv.add_item("gem", 30)
	inv.slot_count = 10  # expande
	assert_int(inv.get_item_count("gem")).is_equal(30)
	assert_int(inv.get_slots().size()).is_equal(10)
	inv.slot_count = 2  # encolhe — pode perder slots, mas gem está no slot 0
	assert_int(inv.get_slots().size()).is_equal(2)
	# slot 0 ainda deve ter gem
	assert_int(inv.get_item_count("gem")).is_greater(0)


# ── Correções da auditoria ────────────────────────────────────────────────────

func test_resize_emit_item_removed_for_truncated_slots() -> void:
	var inv := _make_inventory(3, 99)
	add_child(inv)
	inv.add_item("a", 1)  # slot 0
	inv.add_item("b", 1)  # slot 1
	inv.add_item("c", 1)  # slot 2
	var removed_ids := []
	inv.item_removed.connect(func(id, _qty, _slot): removed_ids.append(id))
	inv.slot_count = 1  # trunca slots 1 e 2
	assert_int(removed_ids.size()).is_equal(2)
	assert_bool(removed_ids.has("b")).is_true()
	assert_bool(removed_ids.has("c")).is_true()


func test_inventory_full_on_partial_fill() -> void:
	var inv := _make_inventory(1, 5)
	add_child(inv)
	var full_emitted := false
	inv.inventory_full.connect(func(): full_emitted = true)
	var added := inv.add_item("a", 10)  # só cabem 5
	assert_int(added).is_equal(5)
	assert_bool(full_emitted).is_true()


func test_has_item_quantity_zero_returns_false() -> void:
	var inv := _make_inventory()
	add_child(inv)
	inv.add_item("key", 5)
	assert_bool(inv.has_item("key", 0)).is_false()


func test_has_item_quantity_negative_returns_false() -> void:
	var inv := _make_inventory()
	add_child(inv)
	inv.add_item("key", 5)
	assert_bool(inv.has_item("key", -1)).is_false()


func test_has_item_empty_id_returns_false() -> void:
	var inv := _make_inventory()
	add_child(inv)
	assert_bool(inv.has_item("", 1)).is_false()


func test_same_item_stack_emits_delta_not_remove_add() -> void:
	var inv := _make_inventory()
	add_child(inv)
	inv.add_item("arrow", 10)
	var added_qty := 0
	var added_slot := -1
	var removed_emitted := false
	inv.item_added.connect(func(_id, qty, slot):
		added_qty += qty
		added_slot = slot
	)
	inv.item_removed.connect(func(_id, _qty, _slot): removed_emitted = true)
	# Adicionar mais do mesmo item → deve emitir só item_added com delta=5
	inv.add_item("arrow", 5)
	assert_int(added_qty).is_equal(5)  # apenas o delta da segunda adicao
	assert_int(added_slot).is_equal(0)
	# item_removed NÃO deve ter sido emitido (mesmo ID, só aumentou)
	assert_bool(removed_emitted).is_false()
