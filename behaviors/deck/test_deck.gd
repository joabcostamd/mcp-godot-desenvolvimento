extends GdUnitTestSuite
func test_add_draw() -> void:
	var d:=Deck.new(); var c:=Card.new(); d.add_card(c)
	assert_int(d.get_remaining()).is_equal(1); var drawn:=d.draw()
	assert_object(drawn).is_not_null(); d.queue_free(); c.queue_free()
