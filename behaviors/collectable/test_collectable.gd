## test_collectable.gd — Testes do behavior Collectable | GdUnit4.
##
## Cobre: auto_pickup, pickup manual, collected, pickup_failed (cheio,
##        sem inventory, item inválido), magnet_range, edge cases.
##
## Requer: GdUnit4 instalado como addon.
## Executar: GdUnit4 > Run Tests na cena behaviors/collectable/test_collectable.gd

extends GdUnitTestSuite


# ── Helpers ───────────────────────────────────────────────────────────────────

func _make_collectable(item_id := "sword", quantity := 1, auto := true) -> Collectable:
	var c := Collectable.new()
	c.item_id = item_id
	c.quantity = quantity
	c.auto_pickup = auto
	return c


func _make_inventory(slot_count := 10, max_stack := 99) -> Inventory:
	var inv := Inventory.new()
	inv.slot_count = slot_count
	inv.max_stack = max_stack
	return inv


func _make_player_with_inventory() -> Node2D:
	var player := Node2D.new()
	var inv := _make_inventory()
	player.add_child(inv)
	return player


# ── Auto-pickup ───────────────────────────────────────────────────────────────

func test_auto_pickup_collects_item() -> void:
	var player := _make_player_with_inventory()
	var col := _make_collectable("gem", 3)
	add_child(player)
	player.add_child(col)
	col._on_body_entered(player)
	# Verificar que o Inventory do player recebeu o item
	var inv := player.get_children()[0] as Inventory
	assert_int(inv.get_item_count("gem")).is_equal(3)


func test_auto_pickup_emits_collected() -> void:
	var player := _make_player_with_inventory()
	var col := _make_collectable("gem", 1)
	add_child(player)
	player.add_child(col)
	var emitted := false
	var captured_qty := 0
	col.collected.connect(func(_id, qty):
		emitted = true
		captured_qty = qty
	)
	col._on_body_entered(player)
	assert_bool(emitted).is_true()
	assert_int(captured_qty).is_equal(1)


func test_auto_pickup_disabled_does_nothing() -> void:
	var player := _make_player_with_inventory()
	var col := _make_collectable("gem", 1, false)  # auto_pickup = false
	add_child(player)
	player.add_child(col)
	col._on_body_entered(player)
	var inv := player.get_children()[0] as Inventory
	assert_int(inv.get_item_count("gem")).is_equal(0)


# ── Pickup manual ─────────────────────────────────────────────────────────────

func test_manual_pickup_collects_item() -> void:
	var player := _make_player_with_inventory()
	var col := _make_collectable("potion", 5)
	add_child(player)
	player.add_child(col)
	col.pickup(player)
	var inv := player.get_children()[0] as Inventory
	assert_int(inv.get_item_count("potion")).is_equal(5)


func test_manual_pickup_emits_collected() -> void:
	var player := _make_player_with_inventory()
	var col := _make_collectable("potion", 2)
	add_child(player)
	player.add_child(col)
	var emitted := false
	col.collected.connect(func(_id, _qty): emitted = true)
	col.pickup(player)
	assert_bool(emitted).is_true()


# ── pickup_failed — inventory full ────────────────────────────────────────────

func test_pickup_failed_inventory_full() -> void:
	var player := Node2D.new()
	var inv := _make_inventory(1, 1)  # 1 slot, stack 1
	player.add_child(inv)
	var col := _make_collectable("a", 1)
	add_child(player)
	player.add_child(col)
	inv.add_item("b", 1)  # lota o único slot
	var reason := ""
	col.pickup_failed.connect(func(r): reason = r)
	col.pickup(player)
	assert_str(reason).is_equal("inventory_full")


# ── pickup_failed — no inventory ──────────────────────────────────────────────

func test_pickup_failed_no_inventory() -> void:
	var player := Node2D.new()  # sem Inventory
	var col := _make_collectable("gem", 1)
	add_child(player)
	player.add_child(col)
	var reason := ""
	col.pickup_failed.connect(func(r): reason = r)
	col.pickup(player)
	assert_str(reason).is_equal("no_inventory")


# ── pickup_failed — invalid item ──────────────────────────────────────────────

func test_pickup_failed_empty_item_id() -> void:
	var player := _make_player_with_inventory()
	var col := _make_collectable("", 1)  # item_id vazio
	add_child(player)
	player.add_child(col)
	var reason := ""
	col.pickup_failed.connect(func(r): reason = r)
	col.pickup(player)
	assert_str(reason).is_equal("invalid_item")


func test_pickup_failed_invalid_quantity() -> void:
	var player := _make_player_with_inventory()
	var col := _make_collectable("sword", 0)  # quantity = 0
	add_child(player)
	player.add_child(col)
	var reason := ""
	col.pickup_failed.connect(func(r): reason = r)
	col.pickup(player)
	assert_str(reason).is_equal("invalid_quantity")


# ── Pickup só acontece uma vez ────────────────────────────────────────────────

func test_pickup_only_once() -> void:
	var player := _make_player_with_inventory()
	var col := _make_collectable("gem", 1)
	add_child(player)
	player.add_child(col)
	var collected_count := 0
	col.collected.connect(func(_id, _qty): collected_count += 1)
	col.pickup(player)
	col.pickup(player)  # segunda tentativa — já coletado
	assert_int(collected_count).is_equal(1)


# ── Inventory como irmão (mesmo pai) ──────────────────────────────────────────

func test_finds_inventory_in_sibling() -> void:
	var root := Node.new()
	var inv := _make_inventory()
	var col := _make_collectable("key", 1)
	root.add_child(inv)
	root.add_child(col)
	add_child(root)
	var player := Node2D.new()
	col._try_collect(player)
	assert_int(inv.get_item_count("key")).is_equal(1)
	root.queue_free()


# ── Magnet range ──────────────────────────────────────────────────────────────

func test_magnet_starts_within_range() -> void:
	var player := _make_player_with_inventory()
	var col := _make_collectable("gem", 1)
	col.magnet_range = 100.0
	add_child(player)
	player.add_child(col)
	player.global_position = Vector2(50, 0)
	col.global_position = Vector2.ZERO
	col._start_magnet(player)
	assert_bool(col._magnet_target != null).is_true()


func test_magnet_does_not_start_outside_range() -> void:
	var player := _make_player_with_inventory()
	var col := _make_collectable("gem", 1)
	col.magnet_range = 10.0
	add_child(player)
	player.add_child(col)
	player.global_position = Vector2(200, 0)
	col.global_position = Vector2.ZERO
	col._start_magnet(player)
	assert_bool(col._magnet_target == null).is_true()


func test_magnet_zero_range_does_nothing() -> void:
	var player := _make_player_with_inventory()
	var col := _make_collectable("gem", 1)
	col.magnet_range = 0.0
	add_child(player)
	player.add_child(col)
	player.global_position = Vector2(5, 0)
	col.global_position = Vector2.ZERO
	col._start_magnet(player)
	assert_bool(col._magnet_target == null).is_true()


# ── Correções da auditoria ────────────────────────────────────────────────────

func test_auto_pickup_setter_reconnects_signal() -> void:
	var player := _make_player_with_inventory()
	var col := _make_collectable("gem", 1)
	add_child(player)
	player.add_child(col)
	# Desabilitar auto_pickup
	col.auto_pickup = false
	col._on_body_entered(player)  # não deve coletar
	var inv := player.get_children()[0] as Inventory
	assert_int(inv.get_item_count("gem")).is_equal(0)
	# Reabilitar auto_pickup
	col.auto_pickup = true
	col._on_body_entered(player)  # deve coletar agora
	assert_int(inv.get_item_count("gem")).is_equal(1)


func test_pickup_failed_cooldown_prevents_flood() -> void:
	var player := Node2D.new()
	var inv := _make_inventory(1, 1)
	player.add_child(inv)
	var col := _make_collectable("a", 1)
	add_child(player)
	player.add_child(col)
	inv.add_item("b", 1)  # lota
	var fail_count := 0
	col.pickup_failed.connect(func(_r): fail_count += 1)
	col.pickup(player)
	col.pickup(player)  # segunda tentativa — cooldown deve bloquear
	assert_int(fail_count).is_equal(1)  # apenas o primeiro emitido


func test_magnet_auto_detects_bodies_in_range() -> void:
	var col := _make_collectable("gem", 1)
	col.magnet_range = 100.0
	# Adicionar à árvore para get_overlapping_bodies funcionar
	var root := Node.new()
	add_child(root)
	root.add_child(col)
	# Criar um corpo dentro da área
	var body := StaticBody2D.new()
	var shape := CollisionShape2D.new()
	var rect := RectangleShape2D.new()
	rect.size = Vector2(10, 10)
	shape.shape = rect
	body.add_child(shape)
	root.add_child(body)
	body.global_position = Vector2(5, 0)
	col.global_position = Vector2.ZERO
	# Simular um frame de física
	col._physics_process(0.016)
	assert_bool(col._magnet_target != null).is_true()
	root.queue_free()


func test_warning_when_auto_pickup_disabled() -> void:
	var col := _make_collectable("gem", 1, false)  # auto_pickup = false
	col.item_id = "gem"
	var warnings := col._get_configuration_warnings()
	assert_bool(warnings.size() > 0).is_true()
