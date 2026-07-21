## test_shop.gd — Testes do Shop | GdUnit4.

extends GdUnitTestSuite

func _make_shop() -> Shop: return Shop.new()

func test_default_parameters() -> void:
	var s := _make_shop()
	assert_str(s.shop_name).is_equal("Loja")
	assert_float(s.discount).is_equal(0.0)
	s.queue_free()

func test_add_item() -> void:
	var s := _make_shop(); add_child(s)
	s.add_item("sword", 100)
	assert_int(s.get_items().size()).is_equal(1)
	remove_child(s); s.queue_free()

func test_add_item_with_quantity() -> void:
	var s := _make_shop(); add_child(s)
	s.add_item("potion", 50, 3)
	var items := s.get_items()
	assert_int((items[0] as Dictionary).quantity).is_equal(3)
	remove_child(s); s.queue_free()

func test_buy_fails_without_deps() -> void:
	var s := _make_shop(); add_child(s)
	s.add_item("sword", 100)
	assert_bool(s.buy("sword")).is_false()
	remove_child(s); s.queue_free()

func test_buy_nonexistent_item() -> void:
	var s := _make_shop(); add_child(s)
	assert_bool(s.buy("ghost")).is_false()
	remove_child(s); s.queue_free()

func test_discount_clamped() -> void:
	var s := _make_shop()
	s.discount = -0.5; assert_float(s.discount).is_equal(0.0)
	s.discount = 2.0; assert_float(s.discount).is_equal(1.0)
	s.queue_free()

func test_get_items_returns_copy() -> void:
	var s := _make_shop(); add_child(s)
	s.add_item("a", 10)
	var items := s.get_items(); items.clear()
	assert_int(s.get_items().size()).is_equal(1)
	remove_child(s); s.queue_free()

func test_sell_fails_without_inventory() -> void:
	var s := _make_shop(); add_child(s)
	s.add_item("sword", 100)
	assert_bool(s.sell("sword")).is_false()
	remove_child(s); s.queue_free()

func test_buy_price_auto() -> void:
	var s := _make_shop(); add_child(s)
	s.add_item("sword", 100)
	var item := s._find_item("sword")
	assert_int(item.buy_price).is_equal(50)  # price * 0.5
	remove_child(s); s.queue_free()

func test_buy_price_custom() -> void:
	var s := _make_shop(); add_child(s)
	s.add_item("sword", 100, -1, 70)
	var item := s._find_item("sword")
	assert_int(item.buy_price).is_equal(70)
	remove_child(s); s.queue_free()
