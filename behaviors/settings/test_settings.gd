## test_settings.gd — Testes do behavior Settings | GdUnit4.

extends GdUnitTestSuite


func _make_st() -> Settings:
	return Settings.new()


func test_script_compiles() -> void:
	var st := Settings.new()
	assert_object(st).is_not_null()
	st.queue_free()


func test_default_parameters() -> void:
	var st := Settings.new()
	assert_float(st.default_master_vol).is_equal(0.0)
	assert_float(st.default_music_vol).is_equal(0.0)
	assert_float(st.default_sfx_vol).is_equal(0.0)
	assert_bool(st.show_fullscreen).is_true()
	st.queue_free()


func test_creates_ui() -> void:
	var st := _make_st()
	add_child(st)
	var container := st.get_node_or_null("SettingsContainer")
	assert_object(container).is_not_null()
	remove_child(st)
	st.queue_free()


func test_has_sliders() -> void:
	var st := _make_st()
	add_child(st)
	var container := st.get_node_or_null("SettingsContainer")
	var sliders := 0
	for child in container.get_children():
		if child is HBoxContainer:
			for c2 in child.get_children():
				if c2 is HSlider:
					sliders += 1
	assert_int(sliders).is_equal(3)
	remove_child(st)
	st.queue_free()


func test_show_fullscreen_false_hides() -> void:
	var st := _make_st()
	st.show_fullscreen = false
	add_child(st)
	var container := st.get_node_or_null("SettingsContainer")
	var found := false
	for child in container.get_children():
		if child is CheckButton:
			found = true; break
	assert_bool(found).is_false()
	remove_child(st)
	st.queue_free()
