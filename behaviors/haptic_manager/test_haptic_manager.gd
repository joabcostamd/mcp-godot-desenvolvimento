extends GdUnitTestSuite
func test_vibrate() -> void: var h:=HapticManager.new(); h.vibrate(); h.stop_vibration(); h.queue_free()

func test_edge_case_zero() -> void:
	var c := HapticManager.new()
	c.intensity = 0.0
	# Nao deve crashar com valor zero
	c.queue_free()

func test_edge_case_extreme() -> void:
	var c := HapticManager.new()
	c.intensity = 999999.0
	# Nao deve crashar com valor extremo
	c.queue_free()
