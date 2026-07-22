## test_chromatic_aberration.gd — Testes do behavior ChromaticAberration | GdUnit4.

extends GdUnitTestSuite


func _make_ca() -> ChromaticAberration:
	return ChromaticAberration.new()


func test_script_compiles() -> void:
	var ca := ChromaticAberration.new()
	assert_object(ca).is_not_null()
	ca.queue_free()


func test_default_parameters() -> void:
	var ca := ChromaticAberration.new()
	assert_float(ca.default_intensity).is_equal(0.5)
	assert_float(ca.default_duration).is_equal(0.3)
	assert_float(ca.flicker_speed).is_equal(20.0)
	ca.queue_free()


func test_trigger_activates() -> void:
	var sprite := Sprite2D.new()
	add_child(sprite)
	var ca := _make_ca()
	sprite.add_child(ca)
	ca.trigger(0.5, 0.1)
	assert_bool(ca.is_active()).is_true()
	remove_child(sprite)
	sprite.queue_free()


func test_trigger_emits_started() -> void:
	var sprite := Sprite2D.new()
	add_child(sprite)
	var ca := _make_ca()
	sprite.add_child(ca)
	var started := false
	ca.aberration_started.connect(func(): started = true)
	ca.trigger(0.5, 0.1)
	assert_bool(started).is_true()
	remove_child(sprite)
	sprite.queue_free()


func test_trigger_ignored_when_active() -> void:
	var sprite := Sprite2D.new()
	add_child(sprite)
	var ca := _make_ca()
	sprite.add_child(ca)
	ca.trigger(0.5, 0.5)
	ca.trigger(1.0, 0.1)
	assert_float(ca.default_intensity).is_equal(0.5)  # não mudou
	remove_child(sprite)
	sprite.queue_free()


func test_trigger_no_parent_noop() -> void:
	var ca := _make_ca()
	add_child(ca)
	ca.trigger(0.5, 0.1)
	assert_bool(ca.is_active()).is_false()
	remove_child(ca)
	ca.queue_free()


func test_restores_modulate_after_finish() -> void:
	var sprite := Sprite2D.new()
	sprite.modulate = Color.GREEN
	add_child(sprite)
	var ca := _make_ca()
	ca.default_duration = 0.05
	ca.flicker_speed = 60.0
	sprite.add_child(ca)
	ca.trigger(0.5)
	await get_tree().create_timer(0.15).timeout
	assert_that(sprite.modulate).is_equal(Color.GREEN)
	remove_child(sprite)
	sprite.queue_free()
