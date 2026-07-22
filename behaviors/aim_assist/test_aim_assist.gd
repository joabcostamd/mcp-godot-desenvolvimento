extends GdUnitTestSuite
func test_assist() -> void: var a:=AimAssist.new(); var t:=Node2D.new(); t.global_position=Vector2(50,0); var r:=a.get_assisted_aim(Vector2.ZERO,[t]); assert_bool(r.x>0).is_true(); t.queue_free(); a.queue_free()

func test_edge_case_zero() -> void:
	var c := AimAssist.new()
	c.friction = 0.0
	# Nao deve crashar com valor zero
	c.queue_free()

func test_edge_case_extreme() -> void:
	var c := AimAssist.new()
	c.friction = 999999.0
	# Nao deve crashar com valor extremo
	c.queue_free()
