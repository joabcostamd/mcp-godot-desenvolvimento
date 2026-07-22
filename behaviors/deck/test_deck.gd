## test_deck.gd — Testes do Deck | GdUnit4.

extends GdUnitTestSuite

func _make_deck() -> Deck: return Deck.new()
func _make_card() -> Card: return Card.new()

func test_add_and_draw() -> void:
	var d := _make_deck(); var c := _make_card()
	d.add_card(c)
	assert_int(d.get_remaining()).is_equal(1)
	var drawn := d.draw()
	assert_object(drawn).is_not_null()
	assert_int(d.get_remaining()).is_equal(0)
	d.queue_free(); c.queue_free()

func test_shuffle_does_not_crash() -> void:
	var d := _make_deck()
	for _i in range(5):
		d.add_card(_make_card())
	d.shuffle()
	assert_int(d.get_remaining()).is_equal(5)
	d.queue_free()

func test_draw_from_empty() -> void:
	var d := _make_deck()
	var empty_emitted := false
	d.empty.connect(func(): empty_emitted = true)
	var drawn := d.draw()
	assert_object(drawn).is_null()
	assert_bool(empty_emitted).is_true()
	d.queue_free()

func test_discard_and_reshuffle() -> void:
	var d := _make_deck()
	var c := _make_card()
	d.add_card(c)
	d.draw(); d.discard(c)  # descarta a carta
	assert_int(d.get_remaining()).is_equal(0)
	assert_int(d.get_discard_size()).is_equal(1)
	# Draw deve reshuffle do discard
	var redrawn := d.draw()
	assert_object(redrawn).is_not_null()
	d.queue_free(); c.queue_free()

func test_card_drawn_signal() -> void:
	var d := _make_deck(); var c := _make_card()
	d.add_card(c)
	var emitted := false
	d.card_drawn.connect(func(_card): emitted = true)
	d.draw()
	assert_bool(emitted).is_true()
	d.queue_free(); c.queue_free()

func test_shuffled_signal() -> void:
	var d := _make_deck()
	d.add_card(_make_card())
	var emitted := false
	d.shuffled.connect(func(): emitted = true)
	d.shuffle()
	assert_bool(emitted).is_true()
	d.queue_free()
