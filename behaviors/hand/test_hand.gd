## test_hand.gd — Testes do Hand | GdUnit4.

extends GdUnitTestSuite


func _make_card(id: String = "test") -> Card:
	var c := Card.new()
	c.card_data = {"id": id, "name": id}
	return c


func _make_deck() -> Deck:
	var d := Deck.new()
	d.shuffle_on_init = false
	for i in range(10):
		d.add_card(_make_card("card_%d" % i))
	return d


func _make_hand() -> Hand:
	return Hand.new()


# ---------------------------------------------------------------------------
# ADD / REMOVE
# ---------------------------------------------------------------------------

func test_add_card() -> void:
	var hand := _make_hand()
	var card := _make_card()
	assert_bool(hand.add_card(card)).is_true()
	assert_int(hand.get_count()).is_equal(1)
	assert_bool(hand.get_cards().has(card)).is_true()
	hand.queue_free()


func test_add_card_full() -> void:
	var hand := _make_hand()
	hand.max_cards = 2
	assert_bool(hand.add_card(_make_card("a"))).is_true()
	assert_bool(hand.add_card(_make_card("b"))).is_true()
	assert_bool(hand.is_full()).is_true()
	assert_bool(hand.add_card(_make_card("c"))).is_false()
	assert_int(hand.get_count()).is_equal(2)
	hand.queue_free()


func test_add_duplicate_card() -> void:
	var hand := _make_hand()
	var card := _make_card()
	hand.add_card(card)
	assert_bool(hand.add_card(card)).is_false()
	assert_int(hand.get_count()).is_equal(1)
	hand.queue_free()


func test_remove_card() -> void:
	var hand := _make_hand()
	var card := _make_card()
	hand.add_card(card)
	assert_bool(hand.remove_card(card)).is_true()
	assert_int(hand.get_count()).is_equal(0)
	hand.queue_free()


func test_remove_nonexistent_card() -> void:
	var hand := _make_hand()
	hand.add_card(_make_card("a"))
	assert_bool(hand.remove_card(_make_card("b"))).is_false()
	assert_int(hand.get_count()).is_equal(1)
	hand.queue_free()


# ---------------------------------------------------------------------------
# DRAW FROM DECK
# ---------------------------------------------------------------------------

func test_draw_from_deck() -> void:
	var parent := Node.new()
	var hand := _make_hand()
	var deck := _make_deck()
	parent.add_child(deck)
	parent.add_child(hand)

	var initial_remaining := deck.get_remaining()
	var card := hand.draw_from_deck()
	assert_bool(card != null).is_true()
	assert_int(hand.get_count()).is_equal(1)
	assert_int(deck.get_remaining()).is_equal(initial_remaining - 1)

	parent.queue_free()


func test_draw_from_deck_full_hand() -> void:
	var parent := Node.new()
	var hand := _make_hand()
	var deck := _make_deck()
	parent.add_child(deck)
	parent.add_child(hand)

	hand.max_cards = 1
	hand.add_card(_make_card())
	assert_bool(hand.is_full()).is_true()

	var card := hand.draw_from_deck()
	assert_bool(card == null).is_true()

	parent.queue_free()


func test_draw_from_deck_no_deck() -> void:
	var hand := _make_hand()
	var card := hand.draw_from_deck()
	assert_bool(card == null).is_true()
	hand.queue_free()


# ---------------------------------------------------------------------------
# PLAY CARD
# ---------------------------------------------------------------------------

func test_play_card() -> void:
	var hand := _make_hand()
	var card := _make_card()
	hand.add_card(card)

	var played := false
	card.played.connect(func(): played = true)

	assert_bool(hand.play_card(0)).is_true()
	assert_int(hand.get_count()).is_equal(0)
	assert_bool(played).is_true()
	hand.queue_free()


func test_play_card_invalid_index() -> void:
	var hand := _make_hand()
	assert_bool(hand.play_card(0)).is_false()
	assert_bool(hand.play_card(-1)).is_false()
	hand.add_card(_make_card())
	assert_bool(hand.play_card(1)).is_false()
	hand.queue_free()


# ---------------------------------------------------------------------------
# DISCARD CARD
# ---------------------------------------------------------------------------

func test_discard_card() -> void:
	var parent := Node.new()
	var hand := _make_hand()
	var deck := _make_deck()
	parent.add_child(deck)
	parent.add_child(hand)

	var card := _make_card()
	hand.add_card(card)

	assert_bool(hand.discard_card(0)).is_true()
	assert_int(hand.get_count()).is_equal(0)
	assert_int(deck.get_discard_size()).is_equal(1)

	parent.queue_free()


func test_discard_card_no_deck() -> void:
	var hand := _make_hand()
	var card := _make_card()
	hand.add_card(card)
	assert_bool(hand.discard_card(0)).is_true()  # descarta mesmo sem deck
	assert_int(hand.get_count()).is_equal(0)
	hand.queue_free()


# ---------------------------------------------------------------------------
# SIGNALS
# ---------------------------------------------------------------------------

func test_card_added_signal() -> void:
	var hand := _make_hand()
	var card := _make_card()
	var emitted := false
	var received: Card = null
	hand.card_added.connect(func(c): emitted = true; received = c)
	hand.add_card(card)
	assert_bool(emitted).is_true()
	assert_bool(received == card).is_true()
	hand.queue_free()


func test_card_removed_signal() -> void:
	var hand := _make_hand()
	var card := _make_card()
	hand.add_card(card)
	var emitted := false
	hand.card_removed.connect(func(_c): emitted = true)
	hand.remove_card(card)
	assert_bool(emitted).is_true()
	hand.queue_free()


func test_draw_emits_card_added() -> void:
	var parent := Node.new()
	var hand := _make_hand()
	var deck := _make_deck()
	parent.add_child(deck)
	parent.add_child(hand)

	var emitted := false
	hand.card_added.connect(func(_c): emitted = true)
	hand.draw_from_deck()
	assert_bool(emitted).is_true()

	parent.queue_free()


# ---------------------------------------------------------------------------
# LAYOUT
# ---------------------------------------------------------------------------

func test_get_card_position_single_card() -> void:
	var hand := _make_hand()
	hand.add_card(_make_card())
	var pos := hand.get_card_position(0)
	assert_vector(pos).is_equal(Vector2.ZERO)
	hand.queue_free()


func test_get_card_position_multiple() -> void:
	var hand := _make_hand()
	hand.fan_angle = 90.0
	hand.card_spacing = 100.0
	for _i in range(3):
		hand.add_card(_make_card())

	# Carta central (índice 1) deve estar em (0, y>0)
	var center := hand.get_card_position(1)
	assert_float(center.x).is_equal(0.0)
	assert_bool(center.y > 0.0).is_true()  # curvatura

	# Cartas das pontas devem ser simétricas em x
	var left := hand.get_card_position(0)
	var right := hand.get_card_position(2)
	assert_float(left.x).is_equal(-right.x)
	assert_float(left.y).is_equal(right.y)
	hand.queue_free()


func test_get_card_rotation() -> void:
	var hand := _make_hand()
	hand.fan_angle = 60.0
	for _i in range(3):
		hand.add_card(_make_card())

	var rot_center := hand.get_card_rotation(1)
	assert_float(rot_center).is_equal(0.0)

	var rot_left := hand.get_card_rotation(0)
	var rot_right := hand.get_card_rotation(2)
	assert_float(rot_left).is_equal(-rot_right)
	assert_bool(rot_left < 0.0).is_true()
	assert_bool(rot_right > 0.0).is_true()
	hand.queue_free()


func test_get_card_position_empty_hand() -> void:
	var hand := _make_hand()
	assert_vector(hand.get_card_position(0)).is_equal(Vector2.ZERO)
	assert_vector(hand.get_card_position(-1)).is_equal(Vector2.ZERO)
	hand.queue_free()


func test_get_card_rotation_single() -> void:
	var hand := _make_hand()
	hand.add_card(_make_card())
	assert_float(hand.get_card_rotation(0)).is_equal(0.0)
	hand.queue_free()


# ---------------------------------------------------------------------------
# EDGE CASES
# ---------------------------------------------------------------------------

func test_get_card_invalid_index() -> void:
	var hand := _make_hand()
	assert_bool(hand.get_card(0) == null).is_true()
	assert_bool(hand.get_card(-1) == null).is_true()
	hand.add_card(_make_card())
	assert_bool(hand.get_card(1) == null).is_true()
	hand.queue_free()


func test_is_full() -> void:
	var hand := _make_hand()
	hand.max_cards = 3
	assert_bool(hand.is_full()).is_false()
	hand.add_card(_make_card())
	hand.add_card(_make_card())
	hand.add_card(_make_card())
	assert_bool(hand.is_full()).is_true()
	hand.queue_free()


func test_add_null_card() -> void:
	var hand := _make_hand()
	assert_bool(hand.add_card(null)).is_false()
	assert_int(hand.get_count()).is_equal(0)
	hand.queue_free()


func test_remove_null_card() -> void:
	var hand := _make_hand()
	hand.add_card(_make_card())
	assert_bool(hand.remove_card(null)).is_false()
	assert_int(hand.get_count()).is_equal(1)
	hand.queue_free()
