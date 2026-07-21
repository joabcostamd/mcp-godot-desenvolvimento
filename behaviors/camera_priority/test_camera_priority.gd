extends GdUnitTestSuite
func test_priority_default() -> void:
	var cp:=CameraPriority.new(); assert_int(cp.priority).is_equal(0); cp.queue_free()
func test_camera_activated_on_highest() -> void:
	var parent:=Node2D.new(); var cam1:=Camera2D.new(); var cam2:=Camera2D.new()
	var cp1:=CameraPriority.new(); cp1.priority=10; cam1.add_child(cp1)
	var cp2:=CameraPriority.new(); cp2.priority=5; cam2.add_child(cp2)
	cam2.enabled=true; cam1.enabled=false
	parent.add_child(cam1); parent.add_child(cam2)
	cp1._evaluate_priority()
	assert_bool(cam1.enabled).is_true()
	parent.queue_free()
func test_activate_sets_highest() -> void:
	var cp:=CameraPriority.new(); cp.priority=5; cp.activate()
	assert_int(cp.priority).is_equal(100); cp.queue_free()
