## test_tween_player.gd — Testes do behavior TweenPlayer | GdUnit4.
##
## Cobre: play, stop, delay, sinais, node inválido.

extends GdUnitTestSuite


func _make_tp() -> TweenPlayer:
	return TweenPlayer.new()


# ESTÁTICO
func test_script_compiles() -> void:
	var tp := TweenPlayer.new()
	assert_object(tp).is_not_null()
	tp.queue_free()


func test_default_parameters() -> void:
	var tp := TweenPlayer.new()
	assert_float(tp.default_duration).is_equal(0.5)
	assert_int(tp.default_easing).is_equal(1)
	assert_int(tp.default_transition).is_equal(2)
	tp.queue_free()


# UNITÁRIO
func test_play_animates_position() -> void:
	var node := Node2D.new()
	add_child(node)
	node.position = Vector2.ZERO
	var tp := _make_tp()
	add_child(tp)
	tp.play(node, "position", Vector2(100, 0), 0.1, 0.0)
	await get_tree().create_timer(0.2).timeout
	assert_that(node.position).is_equal(Vector2(100, 0))
	remove_child(node); remove_child(tp)
	node.queue_free(); tp.queue_free()


func test_play_emits_started() -> void:
	var node := Node2D.new()
	add_child(node)
	var tp := _make_tp()
	add_child(tp)
	var prop := ""
	tp.tween_started.connect(func(p: String): prop = p)
	tp.play(node, "position:x", 50.0, 0.1)
	assert_str(prop).is_equal("position:x")
	remove_child(node); remove_child(tp)
	node.queue_free(); tp.queue_free()


func test_play_emits_finished() -> void:
	var node := Node2D.new()
	add_child(node)
	var tp := _make_tp()
	add_child(tp)
	var prop := ""
	tp.tween_finished.connect(func(p: String): prop = p)
	tp.play(node, "position", Vector2(50, 0), 0.05)
	await get_tree().create_timer(0.15).timeout
	assert_str(prop).is_equal("position")
	remove_child(node); remove_child(tp)
	node.queue_free(); tp.queue_free()


func test_stop_cancels() -> void:
	var node := Node2D.new()
	add_child(node)
	node.position = Vector2.ZERO
	var tp := _make_tp()
	add_child(tp)
	tp.play(node, "position", Vector2(500, 0), 1.0)
	tp.stop()
	assert_bool(tp.is_playing()).is_false()
	remove_child(node); remove_child(tp)
	node.queue_free(); tp.queue_free()


func test_play_null_node_noop() -> void:
	var tp := _make_tp()
	add_child(tp)
	tp.play(null, "position", Vector2.ZERO, 0.1)
	# Não crasha
	remove_child(tp)
	tp.queue_free()
