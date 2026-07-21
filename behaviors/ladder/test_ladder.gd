## test_ladder.gd — GdUnit4.

extends GdUnitTestSuite

func _make_l() -> Ladder: return Ladder.new()

func test_defaults() -> void:
	var l := _make_l()
	assert_float(l.climb_speed).is_equal(150)
	assert_str(l.player_group).is_equal("players"); l.queue_free()

func test_enter_adds_climber() -> void:
	var l := _make_l(); add_child(l)
	var b := Node2D.new(); b.add_to_group("players")
	l._on_enter(b)
	assert_bool(l._climbers.has(b)).is_true()
	b.queue_free(); remove_child(l); l.queue_free()

func test_exit_removes_climber() -> void:
	var l := _make_l(); add_child(l)
	var b := Node2D.new(); b.add_to_group("players")
	l._on_enter(b); l._on_exit(b)
	assert_bool(l._climbers.has(b)).is_false()
	b.queue_free(); remove_child(l); l.queue_free()

func test_climb_speed_clamped() -> void:
	var l := _make_l()
	l.climb_speed = 5; assert_float(l.climb_speed).is_equal(10)
	l.climb_speed = 9999; assert_float(l.climb_speed).is_equal(1000); l.queue_free()

func test_ignores_non_player() -> void:
	var l := _make_l(); add_child(l)
	var b := Node2D.new()  # sem grupo
	l._on_enter(b)
	assert_bool(l._climbers.has(b)).is_false()
	b.queue_free(); remove_child(l); l.queue_free()
