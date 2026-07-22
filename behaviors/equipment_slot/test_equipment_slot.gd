## test_equipment_slot.gd — Testes do EquipmentSlot | GdUnit4.

extends GdUnitTestSuite

func _make_es() -> EquipmentSlot:
	return EquipmentSlot.new()


func test_default_parameters() -> void:
	var es := _make_es()
	assert_str(es.slot_type).is_equal("weapon")
	assert_float(es.slot_bonus).is_equal(1.0)
	assert_bool(es.has_equipped()).is_false()
	es.queue_free()


func test_equip_fails_without_inventory() -> void:
	var es := _make_es()
	assert_bool(es.equip("sword")).is_false()
	es.queue_free()


func test_unequip_empty_does_nothing() -> void:
	var es := _make_es()
	es.unequip()  # não crasha
	assert_bool(es.has_equipped()).is_false()
	es.queue_free()


func test_slot_bonus_clamped() -> void:
	var es := _make_es()
	es.slot_bonus = -1.0
	assert_float(es.slot_bonus).is_equal(0.0)
	es.slot_bonus = 99.0
	assert_float(es.slot_bonus).is_equal(5.0)
	es.queue_free()


func test_get_equipped_item_empty() -> void:
	var es := _make_es()
	assert_str(es.get_equipped_item()).is_equal("")
	es.queue_free()


func test_equipped_signal() -> void:
	var parent := Node2D.new()
	add_child(parent)
	var inv := Inventory.new()
	inv.slot_count = 10
	parent.add_child(inv)
	inv.add_item("sword", 1)
	var es := _make_es()
	parent.add_child(es)

	var emitted := false
	es.equipped.connect(func(_id): emitted = true)
	es.equip("sword")
	assert_bool(emitted).is_true()

	remove_child(parent)
	parent.queue_free()
	inv.queue_free()
	es.queue_free()


func test_unequipped_signal() -> void:
	var parent := Node2D.new()
	add_child(parent)
	var inv := Inventory.new()
	inv.slot_count = 10
	parent.add_child(inv)
	inv.add_item("sword", 1)
	var es := _make_es()
	parent.add_child(es)
	es.equip("sword")

	var emitted := false
	es.unequipped.connect(func(_id): emitted = true)
	es.unequip()
	assert_bool(emitted).is_true()

	remove_child(parent)
	parent.queue_free()
	inv.queue_free()
	es.queue_free()


func test_equip_returns_item_on_unequip() -> void:
	var parent := Node2D.new()
	add_child(parent)
	var inv := Inventory.new()
	inv.slot_count = 10
	parent.add_child(inv)
	inv.add_item("sword", 1)
	var es := _make_es()
	parent.add_child(es)

	es.equip("sword")  # tira do inventário
	assert_int(inv.get_item_count("sword")).is_equal(0)
	es.unequip()  # devolve
	assert_int(inv.get_item_count("sword")).is_equal(1)

	remove_child(parent)
	parent.queue_free()
	inv.queue_free()
	es.queue_free()
