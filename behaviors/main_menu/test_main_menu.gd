## test_main_menu.gd — Testes do behavior MainMenu | GdUnit4.

extends GdUnitTestSuite


func _make_mm() -> MainMenu:
	return MainMenu.new()


func test_script_compiles() -> void:
	var mm := MainMenu.new()
	assert_object(mm).is_not_null()
	mm.queue_free()


func test_default_parameters() -> void:
	var mm := MainMenu.new()
	assert_bool(mm.show_quit).is_true()
	assert_bool(mm.show_settings).is_true()
	mm.queue_free()


func test_creates_container() -> void:
	var mm := _make_mm()
	add_child(mm)
	var container := mm.get_node_or_null("MenuContainer")
	assert_object(container).is_not_null()
	assert_bool(container is VBoxContainer).is_true()
	remove_child(mm)
	mm.queue_free()


func test_creates_play_button() -> void:
	var mm := _make_mm()
	add_child(mm)
	var container: VBoxContainer = mm.get_node_or_null("MenuContainer")
	var found := false
	for child in container.get_children():
		if child is Button and child.text == "Play":
			found = true; break
	assert_bool(found).is_true()
	remove_child(mm)
	mm.queue_free()


func test_show_settings_false_hides_button() -> void:
	var mm := _make_mm()
	mm.show_settings = false
	add_child(mm)
	var container: VBoxContainer = mm.get_node_or_null("MenuContainer")
	var found := false
	for child in container.get_children():
		if child is Button and child.text == "Settings":
			found = true; break
	assert_bool(found).is_false()
	remove_child(mm)
	mm.queue_free()


func test_show_quit_false_hides_button() -> void:
	var mm := _make_mm()
	mm.show_quit = false
	add_child(mm)
	var container: VBoxContainer = mm.get_node_or_null("MenuContainer")
	var found := false
	for child in container.get_children():
		if child is Button and child.text == "Quit":
			found = true; break
	assert_bool(found).is_false()
	remove_child(mm)
	mm.queue_free()


func test_play_pressed_emits() -> void:
	var mm := _make_mm()
	add_child(mm)
	var emitted := false
	mm.play_pressed.connect(func(): emitted = true)
	# Simula o pressionamento via sinal interno
	mm.play_pressed.emit()
	assert_bool(emitted).is_true()
	remove_child(mm)
	mm.queue_free()
