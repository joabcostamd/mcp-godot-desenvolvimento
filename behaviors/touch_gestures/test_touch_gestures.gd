extends GdUnitTestSuite
func test_defaults() -> void: var t:=TouchGestures.new(); assert_float(t.swipe_threshold).is_equal(50.0); t.queue_free()
func test_swipe_detected() -> void: var t:=TouchGestures.new(); var e:=false; t.swiped.connect(func(_d): e=true); t._input(create_touch_event(Vector2.ZERO,true)); t._input(create_touch_event(Vector2(100,0),false)); assert_bool(e).is_true(); t.queue_free()
func create_touch_event(pos: Vector2, pressed: bool) -> InputEventScreenTouch: var ev:=InputEventScreenTouch.new(); ev.position=pos; ev.pressed=pressed; return ev

func test_edge_case_zero() -> void:
	var c := TouchGestures.new()
	c.swipe_threshold = 0.0
	# Nao deve crashar com valor zero
	c.queue_free()

func test_edge_case_extreme() -> void:
	var c := TouchGestures.new()
	c.swipe_threshold = 999999.0
	# Nao deve crashar com valor extremo
	c.queue_free()
