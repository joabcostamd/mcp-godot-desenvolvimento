## test_teleport.gd — Testes do behavior Teleport | GdUnit4.

extends GdUnitTestSuite


func _make_tp() -> Teleport: return Teleport.new()


func test_script_compiles() -> void:
	var tp := Teleport.new(); assert_object(tp).is_not_null(); tp.queue_free()


func test_default_parameters() -> void:
	var tp := Teleport.new()
	assert_that(tp.target_position).is_equal(Vector2.ZERO)
	assert_str(tp.target_scene).is_equal("")
	assert_str(tp.player_group).is_equal("players")
	tp.queue_free()


func test_teleports_player() -> void:
	var tp := _make_tp(); tp.target_position = Vector2(500, 300); add_child(tp)
	var player := CharacterBody2D.new(); player.add_to_group("players")
	player.global_position = Vector2.ZERO; add_child(player)
	tp._on_body_entered(player)
	assert_that(player.global_position).is_equal(Vector2(500, 300))
	remove_child(player); remove_child(tp)
	player.queue_free(); tp.queue_free()


func test_ignores_non_player() -> void:
	var tp := _make_tp(); add_child(tp)
	var enemy := CharacterBody2D.new(); enemy.global_position = Vector2.ZERO
	add_child(enemy)
	tp._on_body_entered(enemy)
	assert_that(enemy.global_position).is_equal(Vector2.ZERO)
	remove_child(enemy); remove_child(tp)
	enemy.queue_free(); tp.queue_free()
