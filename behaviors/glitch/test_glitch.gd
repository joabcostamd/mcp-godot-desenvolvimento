## test_glitch.gd — Testes do behavior Glitch | GdUnit4.

extends GdUnitTestSuite


func _make_gl() -> Glitch:
	return Glitch.new()


func test_script_compiles() -> void:
	var gl := Glitch.new()
	assert_object(gl).is_not_null()
	gl.queue_free()


func test_default_parameters() -> void:
	var gl := Glitch.new()
	assert_float(gl.default_intensity).is_equal(0.5)
	assert_float(gl.default_duration).is_equal(0.3)
	assert_float(gl.max_offset).is_equal(10.0)
	gl.queue_free()


func test_trigger_activates() -> void:
	var node := Node2D.new()
	add_child(node)
	var gl := _make_gl()
	node.add_child(gl)
	gl.trigger(0.5, 0.1)
	assert_bool(gl.is_active()).is_true()
	remove_child(node); node.queue_free()


func test_trigger_emits_started() -> void:
	var node := Node2D.new()
	add_child(node)
	var gl := _make_gl()
	node.add_child(gl)
	var started := false
	gl.glitch_started.connect(func(): started = true)
	gl.trigger(0.5, 0.1)
	assert_bool(started).is_true()
	remove_child(node); node.queue_free()


func test_trigger_ignored_when_active() -> void:
	var node := Node2D.new()
	add_child(node)
	var gl := _make_gl()
	node.add_child(gl)
	gl.trigger(0.5, 0.5)
	gl.trigger(1.0, 0.1)
	assert_bool(gl.is_active()).is_true()
	remove_child(node); node.queue_free()


func test_trigger_no_parent_noop() -> void:
	var gl := _make_gl()
	add_child(gl)
	gl.trigger(0.5, 0.1)
	assert_bool(gl.is_active()).is_false()
	remove_child(gl); gl.queue_free()


func test_restores_position() -> void:
	var node := Node2D.new()
	node.position = Vector2(100, 50)
	add_child(node)
	var gl := _make_gl()
	gl.default_duration = 0.05
	gl.flicker_speed = 60.0
	node.add_child(gl)
	gl.trigger(0.5)
	await get_tree().create_timer(0.15).timeout
	assert_that(node.position).is_equal(Vector2(100, 50))
	remove_child(node); node.queue_free()
