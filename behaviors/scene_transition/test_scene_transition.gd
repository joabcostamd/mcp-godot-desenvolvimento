## test_scene_transition.gd — Testes do behavior SceneTransition | GdUnit4.

extends GdUnitTestSuite


func _make_st() -> SceneTransition:
	return SceneTransition.new()


func test_script_compiles() -> void:
	var st := SceneTransition.new()
	assert_object(st).is_not_null()
	st.queue_free()


func test_default_parameters() -> void:
	var st := SceneTransition.new()
	assert_float(st.default_duration).is_equal(0.5)
	assert_that(st.fade_color).is_equal(Color.BLACK)
	st.queue_free()


func test_creates_rect() -> void:
	var st := _make_st()
	add_child(st)
	var rect := st.get_node_or_null("TransitionRect")
	assert_object(rect).is_not_null()
	if rect:
		assert_bool(rect is ColorRect).is_true()
		assert_int(rect.mouse_filter).is_equal(Control.MOUSE_FILTER_IGNORE)
	remove_child(st)
	st.queue_free()


func test_rect_starts_transparent() -> void:
	var st := _make_st()
	add_child(st)
	var rect: ColorRect = st.get_node_or_null("TransitionRect")
	if rect:
		assert_float(rect.modulate.a).is_equal(0.0)
	remove_child(st)
	st.queue_free()


func test_transition_emits_started() -> void:
	var st := _make_st()
	st.default_duration = 0.1
	add_child(st)
	var started := false
	st.transition_started.connect(func(): started = true)
	st.transition_to("res://example_project/scenes/main.tscn")
	assert_bool(started).is_true()
	remove_child(st)
	st.queue_free()
