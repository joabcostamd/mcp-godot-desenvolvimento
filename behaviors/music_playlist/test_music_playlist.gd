## test_music_playlist.gd — Testes do behavior MusicPlaylist | GdUnit4.

extends GdUnitTestSuite


func _make_mp() -> MusicPlaylist:
	return MusicPlaylist.new()


func test_script_compiles() -> void:
	var mp := MusicPlaylist.new()
	assert_object(mp).is_not_null()
	mp.queue_free()


func test_default_parameters() -> void:
	var mp := MusicPlaylist.new()
	assert_bool(mp.shuffle).is_false()
	assert_float(mp.crossfade_duration).is_equal(0.0)
	assert_float(mp.volume_db).is_equal(0.0)
	assert_bool(mp.auto_play).is_false()
	mp.queue_free()


func test_play_empty_noop() -> void:
	var mp := _make_mp()
	add_child(mp)
	mp.play()
	assert_bool(mp.is_playing()).is_false()
	remove_child(mp)
	mp.queue_free()


func test_next_empty_noop() -> void:
	var mp := _make_mp()
	mp.next()
	assert_int(mp._current_index).is_equal(-1)
	mp.queue_free()


func test_stop_clears() -> void:
	var mp := _make_mp()
	add_child(mp)
	mp.stop()
	assert_bool(mp.is_playing()).is_false()
	remove_child(mp)
	mp.queue_free()
