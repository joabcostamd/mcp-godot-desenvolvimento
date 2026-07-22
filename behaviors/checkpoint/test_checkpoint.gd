## test_checkpoint.gd — Testes do behavior Checkpoint | GdUnit4.

extends GdUnitTestSuite


func _make_cp() -> Checkpoint:
	return Checkpoint.new()


func test_script_compiles() -> void:
	var cp := Checkpoint.new()
	assert_object(cp).is_not_null()
	cp.queue_free()


func test_default_parameters() -> void:
	var cp := Checkpoint.new()
	assert_str(cp.checkpoint_id).is_equal("default")
	assert_that(cp.spawn_offset).is_equal(Vector2.ZERO)
	assert_bool(cp.is_activated()).is_false()
	cp.queue_free()


func test_creates_collision() -> void:
	var cp := _make_cp()
	add_child(cp)
	var shape := cp.get_node_or_null("CheckpointShape")
	assert_object(shape).is_not_null()
	remove_child(cp)
	cp.queue_free()


func test_activate_sets_activated() -> void:
	var cp := _make_cp()
	add_child(cp)
	cp._activated = false
	var player := CharacterBody2D.new()
	player.global_position = Vector2(100, 200)
	add_child(player)
	cp._on_body_entered(player)
	assert_bool(cp.is_activated()).is_true()
	remove_child(player); remove_child(cp)
	player.queue_free(); cp.queue_free()


func test_respawn_static() -> void:
	Checkpoint._last_checkpoint_data = {"position_x": 50.0, "position_y": 75.0}
	var player := CharacterBody2D.new()
	Checkpoint.respawn(player)
	assert_that(player.global_position).is_equal(Vector2(50, 75))
	player.queue_free()
