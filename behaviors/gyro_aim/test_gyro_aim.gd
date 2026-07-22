extends GdUnitTestSuite
func test_gyro() -> void: var g:=GyroAim.new(); var r:=g.process_gyro(Vector2(1,0)); assert_bool(r.length()>0).is_true(); g.queue_free()

func test_edge_case_zero() -> void:
	var c := GyroAim.new()
	c.sensitivity = 0.0
	# Nao deve crashar com valor zero
	c.queue_free()

func test_edge_case_extreme() -> void:
	var c := GyroAim.new()
	c.sensitivity = 999999.0
	# Nao deve crashar com valor extremo
	c.queue_free()
