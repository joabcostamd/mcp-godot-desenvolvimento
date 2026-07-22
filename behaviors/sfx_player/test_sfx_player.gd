## test_sfx_player.gd — Testes do behavior SfxPlayer | GdUnit4.

extends GdUnitTestSuite


func _make_sp() -> SfxPlayer:
	return SfxPlayer.new()


func test_script_compiles() -> void:
	var sp := SfxPlayer.new()
	assert_object(sp).is_not_null()
	sp.queue_free()


func test_default_parameters() -> void:
	var sp := SfxPlayer.new()
	assert_float(sp.volume_db).is_equal(0.0)
	assert_float(sp.pitch_scale).is_equal(1.0)
	assert_str(sp.bus).is_equal("SFX")
	assert_bool(sp.auto_play).is_false()
	sp.queue_free()


func test_play_null_stream_returns_null() -> void:
	var sp := _make_sp()
	add_child(sp)
	var p := sp.play()
	assert_object(p).is_null()
	remove_child(sp)
	sp.queue_free()


func test_play_stream_creates_player() -> void:
	var sp := _make_sp()
	add_child(sp)
	var player := sp.play_stream(null)
	assert_object(player).is_null()
	remove_child(sp)
	sp.queue_free()


func test_emits_played_signal() -> void:
	var sp := _make_sp()
	add_child(sp)
	var emitted := false
	sp.played.connect(func(): emitted = true)
	sp.played.emit()
	assert_bool(emitted).is_true()
	remove_child(sp)
	sp.queue_free()
