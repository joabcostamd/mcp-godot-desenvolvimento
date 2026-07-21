extends GdUnitTestSuite
func _make_pr() -> PatrolRoute: return PatrolRoute.new()
func test_defaults() -> void:
	var pr := _make_pr(); assert_float(pr.speed).is_equal(80); assert_float(pr.wait_time).is_equal(1); pr.queue_free()
func test_add_waypoint() -> void:
	var pr := _make_pr(); add_child(pr); pr.add_waypoint(Vector2(100,0))
	assert_int(pr._waypoints.size()).is_equal(1); remove_child(pr); pr.queue_free()
func test_creates_timer() -> void:
	var pr := _make_pr(); add_child(pr); assert_object(pr._wait_timer).is_not_null(); remove_child(pr); pr.queue_free()
func test_speed_clamped() -> void:
	var pr := _make_pr(); pr.speed = 1; assert_float(pr.speed).is_equal(10); pr.queue_free()
func test_moves_toward_waypoint() -> void:
	var p := Node2D.new(); p.global_position = Vector2(0,0); add_child(p)
	var pr := _make_pr(); p.add_child(pr); pr.add_waypoint(Vector2(100,0))
	pr._physics_process(0.5)  # 80*0.5 = 40
	assert_float(p.global_position.x).is_greater(0); remove_child(p); p.queue_free(); pr.queue_free()
