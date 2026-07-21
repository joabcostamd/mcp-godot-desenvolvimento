extends GdUnitTestSuite
func test_assist() -> void: var a:=AimAssist.new(); var t:=Node2D.new(); t.global_position=Vector2(50,0); var r:=a.get_assisted_aim(Vector2.ZERO,[t]); assert_bool(r.x>0).is_true(); t.queue_free(); a.queue_free()
