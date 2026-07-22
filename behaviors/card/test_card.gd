## test_card.gd — Testes do Card | GdUnit4.

extends GdUnitTestSuite

func _make_card() -> Card: return Card.new()

func test_default_face_up() -> void:
	var c := _make_card()
	assert_bool(c.face_up).is_true()
	c.queue_free()

func test_flip() -> void:
	var c := _make_card()
	c.flip()
	assert_bool(c.face_up).is_false()
	c.flip()
	assert_bool(c.face_up).is_true()
	c.queue_free()

func test_flipped_signal() -> void:
	var c := _make_card()
	var emitted := false
	c.flipped.connect(func(_f): emitted = true)
	c.flip()
	assert_bool(emitted).is_true()
	c.queue_free()

func test_played_signal() -> void:
	var c := _make_card()
	var emitted := false
	c.played.connect(func(): emitted = true)
	c.play()
	assert_bool(emitted).is_true()
	c.queue_free()

func test_drawn_signal() -> void:
	var c := _make_card()
	var emitted := false
	c.drawn.connect(func(): emitted = true)
	c.draw()
	assert_bool(emitted).is_true()
	c.queue_free()

func test_card_data() -> void:
	var c := _make_card()
	c.card_data = {"suit": "hearts", "value": 10}
	assert_str(c.card_data.suit).is_equal("hearts")
	assert_int(c.card_data.value).is_equal(10)
	c.queue_free()
