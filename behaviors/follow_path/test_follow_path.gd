## test_follow_path.gd — GdUnit4.

extends GdUnitTestSuite

func _make_fp() -> FollowPath: return FollowPath.new()

func test_defaults() -> void:
	var fp := _make_fp()
	assert_float(fp.speed).is_equal(100); assert_bool(fp.loop).is_true()
	fp.queue_free()

func test_moves_along_path() -> void:
	var p := Node2D.new(); add_child(p)
	var fp := _make_fp(); fp.speed = 100; p.add_child(fp)
	var path := Path2D.new(); var c := Curve2D.new()
	c.add_point(Vector2(0,0)); c.add_point(Vector2(100,0))
	path.curve = c; fp.add_child(path)
	fp._physics_process(0.5)
	assert_float(p.global_position.x).is_greater(0)
	remove_child(p); p.queue_free(); fp.queue_free()

func test_no_path_does_not_crash() -> void:
	var fp := _make_fp(); add_child(fp)
	fp._physics_process(0.1)
	assert_bool(true).is_true()
	remove_child(fp); fp.queue_free()

func test_reset() -> void:
	var fp := _make_fp(); fp._progress = 500; fp.reset()
	assert_float(fp._progress).is_equal(0); fp.queue_free()
