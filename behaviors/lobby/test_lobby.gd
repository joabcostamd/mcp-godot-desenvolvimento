extends GdUnitTestSuite
func test_defaults() -> void:
	var l:=Lobby.new(); assert_int(l.max_players).is_equal(4); assert_str(l.game_mode).is_equal("default"); l.queue_free()
func test_player_count() -> void:
	var l:=Lobby.new(); assert_int(l.get_player_count()).is_equal(0); l.queue_free()
