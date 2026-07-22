## test_dialogue.gd — Testes do behavior Dialogue | GdUnit4.

extends GdUnitTestSuite


func _make_dl() -> Dialogue:
	return Dialogue.new()


func _sample_lines() -> Array:
	return [
		{"text": "Hello!", "speaker": "NPC"},
		{"text": "Goodbye!", "speaker": "NPC"}
	]


func test_script_compiles() -> void:
	var dl := Dialogue.new()
	assert_object(dl).is_not_null()
	dl.queue_free()


func test_default_parameters() -> void:
	var dl := Dialogue.new()
	assert_bool(dl.auto_advance).is_false()
	assert_float(dl.auto_delay).is_equal(3.0)
	assert_str(dl.advance_input).is_equal("ui_accept")
	dl.queue_free()


func test_start_displays_first_line() -> void:
	var dl := _make_dl()
	add_child(dl)
	dl.start(_sample_lines())
	assert_bool(dl.is_active()).is_true()
	assert_int(dl._current_index).is_equal(0)
	remove_child(dl)
	dl.queue_free()


func test_next_advances() -> void:
	var dl := _make_dl()
	add_child(dl)
	dl.start(_sample_lines())
	dl.next()
	assert_int(dl._current_index).is_equal(1)
	remove_child(dl)
	dl.queue_free()


func test_skip_finishes() -> void:
	var dl := _make_dl()
	add_child(dl)
	dl.start(_sample_lines())
	dl.skip()
	assert_bool(dl.is_active()).is_false()
	remove_child(dl)
	dl.queue_free()


func test_start_empty_noop() -> void:
	var dl := _make_dl()
	dl.start([])
	assert_bool(dl.is_active()).is_false()
	dl.queue_free()
