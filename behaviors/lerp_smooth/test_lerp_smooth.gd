## test_lerp_smooth.gd — GdUnit4.

extends GdUnitTestSuite

func _make_ls() -> LerpSmooth: return LerpSmooth.new()

func test_defaults() -> void:
	var ls := _make_ls()
	assert_float(ls.duration).is_equal(0.5); assert_int(ls.easing).is_equal(3)
	assert_bool(ls.is_running()).is_false(); ls.queue_free()

func test_starts_not_running() -> void:
	var ls := _make_ls(); add_child(ls)
	assert_bool(ls.is_running()).is_false()
	remove_child(ls); ls.queue_free()

func test_move_to_starts_tween() -> void:
	var p := Node2D.new(); add_child(p)
	var ls := _make_ls(); p.add_child(ls)
	ls.move_to(Vector2(100,0))
	assert_bool(ls.is_running()).is_true()
	remove_child(p); p.queue_free(); ls.queue_free()

func test_stop_kills_tween() -> void:
	var p := Node2D.new(); add_child(p)
	var ls := _make_ls(); p.add_child(ls)
	ls.move_to(Vector2(100,0))
	assert_bool(ls.is_running()).is_true()
	ls.stop()
	assert_bool(ls.is_running()).is_false()
	remove_child(p); p.queue_free(); ls.queue_free()

func test_no_parent_does_not_crash() -> void:
	var ls := _make_ls()
	ls.move_to(Vector2(100,0))  # sem parent — retorna cedo
	assert_bool(ls.is_running()).is_false(); ls.queue_free()

func test_rotate_to() -> void:
	var p := Node2D.new(); add_child(p)
	var ls := _make_ls(); p.add_child(ls)
	ls.rotate_to(3.14)
	assert_bool(ls.is_running()).is_true()
	remove_child(p); p.queue_free(); ls.queue_free()

func test_easing_setter() -> void:
	var ls := _make_ls()
	ls.easing = -1; assert_int(ls.easing).is_equal(0)
	ls.easing = 99; assert_int(ls.easing).is_equal(3); ls.queue_free()
