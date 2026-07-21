extends GdUnitTestSuite
func test_vibrate() -> void: var h:=HapticManager.new(); h.vibrate(); h.stop_vibration(); h.queue_free()
