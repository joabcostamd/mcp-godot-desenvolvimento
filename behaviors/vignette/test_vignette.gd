## test_vignette.gd — Testes do behavior Vignette | GdUnit4.

extends GdUnitTestSuite


func _make_vg() -> Vignette:
	return Vignette.new()


func test_script_compiles() -> void:
	var vg := Vignette.new()
	assert_object(vg).is_not_null()
	vg.queue_free()


func test_default_parameters() -> void:
	var vg := Vignette.new()
	assert_float(vg.default_intensity).is_equal(0.5)
	assert_float(vg.default_duration).is_equal(0.5)
	assert_that(vg.vignette_color).is_equal(Color.BLACK)
	vg.queue_free()


func test_trigger_creates_rect() -> void:
	var vg := _make_vg()
	add_child(vg)
	vg.trigger(0.5, 0.3)
	var rect := vg.get_node_or_null("VignetteRect")
	assert_object(rect).is_not_null()
	remove_child(vg)
	vg.queue_free()


func test_trigger_emits_started() -> void:
	var vg := _make_vg()
	add_child(vg)
	var started := false
	vg.vignette_started.connect(func(): started = true)
	vg.trigger(0.5, 0.3)
	assert_bool(started).is_true()
	remove_child(vg)
	vg.queue_free()


func test_trigger_emits_finished() -> void:
	var vg := _make_vg()
	vg.default_duration = 0.1
	add_child(vg)
	var finished := false
	vg.vignette_finished.connect(func(): finished = true)
	vg.trigger(0.3)
	await get_tree().create_timer(0.3).timeout
	assert_bool(finished).is_true()
	remove_child(vg)
	vg.queue_free()


func test_rect_has_ignore_mouse() -> void:
	var vg := _make_vg()
	add_child(vg)
	vg.trigger(0.5, 0.5)
	var rect: ColorRect = vg.get_node_or_null("VignetteRect")
	if rect:
		assert_int(rect.mouse_filter).is_equal(Control.MOUSE_FILTER_IGNORE)
	remove_child(vg)
	vg.queue_free()
