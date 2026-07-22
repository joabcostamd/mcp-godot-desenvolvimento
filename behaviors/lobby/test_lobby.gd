extends GdUnitTestSuite
func test_defaults() -> void:
	var l:=Lobby.new(); assert_int(l.max_players).is_equal(4); assert_str(l.game_mode).is_equal("default"); l.queue_free()
func test_player_count() -> void:
	var l:=Lobby.new(); assert_int(l.get_player_count()).is_equal(0); l.queue_free()

func test_edge_case_zero() -> void:
	var c := Lobby.new()
	c.max_players = 0
	# Nao deve crashar com valor zero
	c.queue_free()

func test_edge_case_extreme() -> void:
	var c := Lobby.new()
	c.max_players = 999999
	# Nao deve crashar com valor extremo
	c.queue_free()
