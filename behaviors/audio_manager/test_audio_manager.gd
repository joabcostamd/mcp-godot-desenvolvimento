## test_audio_manager.gd — Testes do behavior AudioManager | GdUnit4.

extends GdUnitTestSuite


func _make_am() -> AudioManager:
	return AudioManager.new()


func test_script_compiles() -> void:
	var am := AudioManager.new()
	assert_object(am).is_not_null()
	am.queue_free()


func test_default_parameters() -> void:
	var am := AudioManager.new()
	assert_float(am.master_volume_db).is_equal(0.0)
	assert_float(am.music_volume_db).is_equal(0.0)
	assert_float(am.sfx_volume_db).is_equal(0.0)
	am.queue_free()


func test_set_bus_volume_clamps() -> void:
	var am := _make_am()
	add_child(am)
	am.set_bus_volume("Master", 100.0)
	assert_float(am.get_bus_volume("Master")).is_equal(24.0)
	am.set_bus_volume("Master", -999.0)
	assert_float(am.get_bus_volume("Master")).is_equal(-80.0)
	remove_child(am)
	am.queue_free()


func test_get_bus_volume_invalid_returns_zero() -> void:
	var am := _make_am()
	assert_float(am.get_bus_volume("NonExistent")).is_equal(0.0)
	am.queue_free()


func test_play_sfx_creates_player() -> void:
	var am := _make_am()
	add_child(am)
	var player := am.play_sfx(null)
	assert_object(player).is_not_null()
	assert_str(player.bus).is_equal("SFX")
	remove_child(am)
	am.queue_free()


func test_play_music_creates_player() -> void:
	var am := _make_am()
	add_child(am)
	var player := am.play_music(null)
	assert_object(player).is_not_null()
	assert_str(player.bus).is_equal("Music")
	remove_child(am)
	am.queue_free()
