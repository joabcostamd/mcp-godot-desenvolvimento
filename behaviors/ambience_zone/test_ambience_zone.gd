## test_ambience_zone.gd — Testes do behavior AmbienceZone | GdUnit4.

extends GdUnitTestSuite


func _make_az() -> AmbienceZone:
	return AmbienceZone.new()


func test_script_compiles() -> void:
	var az := AmbienceZone.new()
	assert_object(az).is_not_null()
	az.queue_free()


func test_default_parameters() -> void:
	var az := AmbienceZone.new()
	assert_float(az.volume_db).is_equal(0.0)
	assert_float(az.max_distance).is_equal(500.0)
	assert_float(az.attenuation).is_equal(0.5)
	assert_bool(az.auto_play).is_false()
	az.queue_free()


func test_creates_player() -> void:
	var az := _make_az()
	add_child(az)
	var player := az.get_node_or_null("AmbiencePlayer")
	assert_object(player).is_not_null()
	assert_bool(player is AudioStreamPlayer2D).is_true()
	remove_child(az)
	az.queue_free()


func test_creates_collision() -> void:
	var az := _make_az()
	add_child(az)
	var shape := az.get_node_or_null("AmbienceShape")
	assert_object(shape).is_not_null()
	remove_child(az)
	az.queue_free()


func test_not_playing_initially() -> void:
	var az := _make_az()
	assert_bool(az.is_playing()).is_false()
	az.queue_free()
